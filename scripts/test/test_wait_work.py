"""Deterministic CI fixtures and real launch-once local command lifecycle."""
import importlib.util
import json
import os
import shutil
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("wait_work", ROOT / ".mt-agent-devkit/scripts/wait_work.py")
w = importlib.util.module_from_spec(spec)
spec.loader.exec_module(w)
SHA, OTHER = "a" * 40, "b" * 40


def run(name="CI", status="completed", conclusion="success", sha=SHA, identity=1):
    return dict(workflowName=name, status=status, conclusion=conclusion, headSha=sha, databaseId=identity)


class GitHubFixture:
    def __init__(self, runs=None, checks=None, required=(), heads=None, prior=None, external=None):
        self.runs = runs or []
        self.checks = checks or []
        self.required = required
        self.heads = heads or [SHA]
        self.prior = prior or []
        self.external = external or []
        self.calls = []

    def __call__(self, args, **kwargs):
        self.calls.append(args)
        if args[:2] == ["pr", "view"]:
            head = self.heads.pop(0) if len(self.heads) > 1 else self.heads[0]
            return dict(headRefOid=head, statusCheckRollup=self.checks, baseRefName="main", commits=[{"oid": OTHER}, {"oid": SHA}])
        if args[:2] == ["pr", "checks"]:
            return []
        if args[:2] == ["run", "list"]:
            return self.runs if args[args.index("--commit") + 1] == SHA else self.prior
        if args[:2] == ["api", "graphql"]:
            return {"data": {"repository": {"ref": {"branchProtectionRule": {"requiredStatusCheckContexts": list(self.required)}}}}}
        if "/rules/" in args[-1]:
            return [[]]
        if "/compare/" in args[-1]:
            return {"files": [{"filename": "docs/note.md"}]}
        if "/check-runs" in args[-1]:
            return [{"check_runs": self.external}]
        if "/statuses" in args[-1]:
            return [[]]
        raise AssertionError(args)


class EvidenceTests(unittest.TestCase):
    def snapshot(self, fixture, pr=1, required=()):
        return w.ci_snapshot("owner/repo", pr, SHA, fixture, required)

    def test_pass_accounts_for_multiple_workflows(self):
        evidence = self.snapshot(GitHubFixture([run(), run("lint", identity=2)]))
        self.assertEqual(evidence["outcome"], "PASS")
        self.assertEqual([r["databaseId"] for r in evidence["runs"]], [2, 1])
        self.assertEqual(evidence["inspected_sha"], SHA)

    def test_failed_external_check_cannot_hide_behind_passing_action(self):
        for pr in (1, None):
            fixture = GitHubFixture([run()], [{"name": "external", "state": "FAILURE"}], external=[{"name": "external", "status": "completed", "conclusion": "failure"}])
            self.assertEqual(self.snapshot(fixture, pr)["outcome"], "FAIL")

    def test_fail_cancel_timeout_and_unknown_fail_closed(self):
        for conclusion in ("failure", "cancelled", "timed_out", "action_required", "unknown"):
            self.assertEqual(self.snapshot(GitHubFixture([run(conclusion=conclusion)]))["outcome"], "FAIL")

    def test_pending_required_context_missing_even_with_single_success(self):
        for fixture, required in ((GitHubFixture([run()], required=("security",)), ()), (GitHubFixture([run()]), ("security",))):
            evidence = self.snapshot(fixture, required=required)
            self.assertEqual(evidence["outcome"], "PENDING")
            self.assertEqual(evidence["missing_checks"], ["security"])

    def test_expected_context_is_pending(self):
        self.assertEqual(self.snapshot(GitHubFixture(checks=[{"context": "security", "state": "EXPECTED"}]))["outcome"], "PENDING")

    def test_second_required_run_pending_blocks(self):
        self.assertEqual(self.snapshot(GitHubFixture([run(), run("security", "queued", None, identity=2)]))["outcome"], "PENDING")

    def test_no_run_prior_candidate_stays_no_run_with_scope(self):
        evidence = self.snapshot(GitHubFixture(prior=[run(sha=OTHER)]))
        self.assertEqual(evidence["outcome"], "NO RUN")
        self.assertEqual(evidence["prior_outcome"], "PASS")
        self.assertEqual(evidence["changed_files"], ["docs/note.md"])
        self.assertEqual(evidence["zero_check_gate"], "required")

    def test_no_run_without_candidate(self):
        self.assertEqual(self.snapshot(GitHubFixture())["outcome"], "NO RUN")

    def test_head_change_during_snapshot_is_stale(self):
        evidence = self.snapshot(GitHubFixture([run()], heads=[SHA, OTHER]))
        self.assertEqual(evidence["outcome"], "STALE")
        self.assertEqual(evidence["current_sha"], OTHER)

    def test_latest_attempt_supersedes_previous_workflow_run(self):
        self.assertEqual(self.snapshot(GitHubFixture([run(conclusion="failure"), run(identity=2)]))["outcome"], "PASS")

    def test_same_display_name_different_workflows_cannot_hide_failure(self):
        first, second = run(conclusion="failure"), run(identity=2)
        first["workflowDatabaseId"], second["workflowDatabaseId"] = 10, 20
        self.assertEqual(self.snapshot(GitHubFixture([first,second]))["outcome"], "FAIL")

    def test_saturated_result_limit_is_not_pass(self):
        with self.assertRaises(w.WaitError):
            self.snapshot(GitHubFixture([run(identity=i) for i in range(100)]))

    def test_foreign_run_sha_is_error(self):
        with self.assertRaises(w.WaitError):
            self.snapshot(GitHubFixture([run(sha=OTHER)]))

    def test_ruleset_missing_context_and_unsupported_workflow_gate(self):
        fixture = GitHubFixture([run()])
        def request(args, **kwargs):
            if "/rules/" in args[-1]:
                return [[{"type": "required_status_checks", "parameters": {"required_status_checks": [{"context": "absent"}]}}]]
            return fixture(args, **kwargs)
        self.assertEqual(self.snapshot(request)["outcome"], "PENDING")
        def unsupported(args, **kwargs):
            return [[{"type": "workflows"}]] if "/rules/" in args[-1] else fixture(args, **kwargs)
        with self.assertRaises(w.WaitError):
            self.snapshot(unsupported)

    def test_repeated_waits_preserve_head_and_rediscover_delayed_run(self):
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder) / "ci"
            fixture = GitHubFixture()
            first = w.ci_wait(directory, "owner/repo", 1, None, [], 0, .01, fixture)
            self.assertEqual(first["outcome"], "NO RUN")
            fixture.runs = [run()]
            second = w.ci_wait(directory, "owner/repo", 1, None, [], 0, .01, fixture)
            self.assertEqual(second["outcome"], "PASS")
            fixture.heads = [OTHER]
            self.assertEqual(w.ci_wait(directory, "owner/repo", 1, None, [], 0, .01, fixture)["outcome"], "STALE")
            with self.assertRaises(w.WaitError):
                w.ci_wait(directory, "owner/other", 1, None, [], 0, .01, fixture)

    def test_window_expiry_then_completion_does_not_relaunch(self):
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder) / "ci"
            fixture = GitHubFixture([run(status="queued", conclusion=None)])
            # Disk persistence can exceed 25ms on Windows. Drive the polling
            # deadline explicitly; filesystem latency must not choose poll count.
            now, sleeps = [0.0], []
            def sleep(seconds):
                sleeps.append(seconds)
                now[0] += seconds
            self.assertEqual(w.ci_wait(directory, "owner/repo", 1, SHA, [], .025, .01, fixture, lambda: now[0], sleep)["outcome"], "PENDING")
            self.assertEqual(sum(c[:2] == ["run", "list"] for c in fixture.calls), 3)
            self.assertEqual(len(sleeps), 3)
            self.assertAlmostEqual(sum(sleeps), .025)
            self.assertEqual(json.loads((directory / "identity.json").read_text())["expected_sha"], SHA)
            fixture.runs = [run()]
            self.assertEqual(w.ci_wait(directory, "owner/repo", 1, SHA, [], 0, .01, fixture, lambda: now[0], sleep)["outcome"], "PASS")
            self.assertEqual(sum(c[:2] == ["run", "list"] for c in fixture.calls), 4)
            self.assertFalse(any("rerun" in c for c in fixture.calls))

    def test_delayed_discovery_within_window(self):
        with tempfile.TemporaryDirectory() as folder:
            fixture = GitHubFixture()
            def request(args, **kwargs):
                if args[:2] == ["run", "list"] and len(fixture.calls) > 5:
                    fixture.runs = [run()]
                return fixture(args, **kwargs)
            now = [0.0]
            def sleep(seconds):
                now[0] += seconds
            self.assertEqual(w.ci_wait(Path(folder)/"ci", "owner/repo", 1, SHA, [], .1, .01, request, lambda: now[0], sleep)["outcome"], "PASS")
            self.assertGreater(sum(c[:2] == ["run", "list"] for c in fixture.calls), 1)
            self.assertLess(now[0], .1)

    def test_nonzero_window_preserves_complete_no_run_on_repeated_waits(self):
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder) / "ci"
            fixture = GitHubFixture(prior=[run(sha=OTHER)])
            for _ in range(2):
                now = [0.0]
                def request(args, **kwargs):
                    self.assertLess(now[0], 2, "request started after deadline")
                    return fixture(args, **kwargs)
                def sleep(seconds):
                    now[0] += seconds
                evidence = w.ci_wait(directory, "owner/repo", 1, None, [], 2, 1, request, lambda: now[0], sleep)
                self.assertEqual(evidence["outcome"], "NO RUN")
                self.assertEqual(evidence["inspected_sha"], SHA)
                self.assertEqual(evidence["prior_sha"], OTHER)
                self.assertEqual(evidence["prior_run_ids"], [1])
                self.assertEqual(evidence["prior_outcome"], "PASS")
                self.assertEqual(evidence["changed_files"], ["docs/note.md"])
                self.assertEqual(evidence["zero_check_gate"], "required")
                self.assertEqual(json.loads((directory / "evidence.json").read_text()), evidence)

    def test_incomplete_request_timeout_remains_pending(self):
        with tempfile.TemporaryDirectory() as folder:
            now = [0.0]
            fixture = GitHubFixture(prior=[run(sha=OTHER)])
            def request(args, **kwargs):
                if now[0] == 1:
                    now[0] = 2
                    raise w.WaitError("GitHub request timed out; retry same identity")
                return fixture(args, **kwargs)
            def sleep(seconds):
                now[0] += seconds
            evidence = w.ci_wait(Path(folder)/"ci", "owner/repo", 1, None, [], 2, 1, request, lambda: now[0], sleep)
            self.assertEqual(evidence["outcome"], "PENDING")
            self.assertEqual(evidence["inspected_sha"], SHA)

    def test_transport_auth_malformed_and_timeout_are_sanitized(self):
        for code, output, error in ((1, "", "HTTP 401 secret-token"), (1, "", "network secret-token"), (0, "not json", ""), (1, "", "network")):
            response = subprocess.CompletedProcess([], code, output, error)
            with patch.object(w.subprocess, "run", return_value=response), self.assertRaises(w.WaitError) as caught:
                w.gh_json(["pr", "checks"], allowed=(0,1,8))
            self.assertNotIn("secret-token", str(caught.exception))
        with patch.object(w.subprocess, "run", side_effect=subprocess.TimeoutExpired("gh", 1)), self.assertRaises(w.WaitError):
            w.gh_json([])
        with patch.object(w.subprocess, "run", side_effect=FileNotFoundError), self.assertRaises(w.WaitError):
            w.gh_json([])

    def test_empty_aggregate_has_no_success(self):
        self.assertEqual(w.aggregate([], []), ("NO RUN", []))
        self.assertEqual(w.aggregate([], [], ["missing"]), ("PENDING", ["missing"]))


class LocalTests(unittest.TestCase):
    def test_real_foreground_run_success_and_failure_true_exit(self):
        with tempfile.TemporaryDirectory() as folder:
            for code in (0, 7, 124):
                directory = Path(folder)/str(code)
                evidence = w.local_run(directory, [sys.executable, "-c", "print('Tests 3 passed'); print('FAIL fixture'); raise SystemExit(" + str(code) + ")"], folder)
                self.assertEqual(evidence["process_exit_code"], code)
                self.assertEqual(evidence["outcome"], "PASS" if not code else "FAIL")
                self.assertEqual(w.local_wait(directory, 0, .01), evidence)
                with self.assertRaises(w.WaitError):
                    w.local_run(directory, [sys.executable, "-c", "raise SystemExit(0)"], folder)

    def test_wait_pending_then_success_launches_once(self):
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)/"once"
            counter = Path(folder)/"counter"
            command = [sys.executable, "-c", "from pathlib import Path; import time; Path('counter').write_text('one'); time.sleep(.15); print('Tests 1 passed')"]
            worker = threading.Thread(target=w.local_run, args=(directory, command, folder))
            worker.start()
            deadline = time.monotonic() + 2
            while not (directory/"identity.json").exists() and time.monotonic() < deadline:
                time.sleep(.01)
            self.assertEqual(w.local_wait(directory, .02, .01)["outcome"], "PENDING")
            with self.assertRaises(w.WaitError): w.local_run(directory, command, folder)
            worker.join(3)
            self.assertEqual(w.local_wait(directory, 0, .01)["outcome"], "PASS")
            self.assertEqual(counter.read_text(), "one")

    def test_missing_identity_empty_command_and_launch_failure(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(w.WaitError): w.local_wait(Path(folder)/"absent", 0, .01)
            with self.assertRaises(w.WaitError): w.local_run(Path(folder)/"empty", [], folder)
            self.assertEqual(w.local_run(Path(folder)/"bad", ["nonexistent-executable-217"], folder)["process_exit_code"], 127)

    def test_redacted_private_logs_and_bounded_summary(self):
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ, {"FIXTURE_SECRET": "sensitive-fixture-217"}):
            directory = Path(folder)/"private"
            evidence = w.local_run(directory, [sys.executable, "-c", "import os; print('x'*4090 + os.environ['FIXTURE_SECRET']); print('https://user:pass@example.com'); [print('Tests 1 passed') for _ in range(100)]"], folder)
            self.assertNotIn("sensitive-fixture-217", (directory/"output.log").read_text())
            self.assertNotIn("user:pass", (directory/"output.log").read_text())
            self.assertEqual(len(evidence["totals"]), 10)
            self.assertNotIn("command", json.loads((directory/"identity.json").read_text()))

    def test_confinement_and_all_provider_bindings(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for provider in w.PROVIDERS:
                harness = root/("." + provider)/"harness"
                harness.mkdir(parents=True)
                runtime = "." + provider + "/agents"
                (harness/"state-paths.json").write_text(json.dumps({"PROVIDER_ROOT": "."+provider, "RUNTIME_ROOT": runtime}))
                self.assertEqual(w.run_directory(root, provider, runtime, "checks", "local"), root/runtime/"tmp/waits/local/checks")
                for wrong in ("../escape", ".codex/agents/other", ""):
                    with self.assertRaises(w.WaitError): w.run_directory(root, provider, wrong, "checks", "local")
                with self.assertRaises(w.WaitError): w.run_directory(root, provider, runtime, "../escape", "local")
            for value in ("", "../escape", "a//b", "C:/outside", "a\\b"):
                with self.assertRaises(w.WaitError): w.safe(root, value)

    def test_strict_ci_does_not_invoke_github(self):
        with patch.object(w, "gh_json", side_effect=AssertionError("gh invoked")):
            self.assertEqual(w.main(["ci", "--provider", "codex", "--runtime-root", ".codex/agents", "--id", "strict", "--mode", "strict"]), 3)

    def test_invalid_inputs_and_redactor_empty(self):
        for extra in (["--window", "-1"], ["--window", "541"], ["--interval", "0"]):
            self.assertEqual(w.main(["local-wait", "--provider", "codex", "--runtime-root", ".codex/agents", "--id", "x", "--mode", "strict", *extra]), 3)
        self.assertEqual(w.redactor({})("plain"), "plain")


@unittest.skipUnless(shutil.which("bash") and shutil.which("dirname"), "bash and dirname required")
class ShellWrapperInterpreterTests(unittest.TestCase):
    """wait_work.sh prefers PYTHON_COMMAND, then python3, then python."""

    SCRIPT = ROOT / ".mt-agent-devkit/scripts/wait_work.sh"

    def invoke(self, shims, **env):
        with tempfile.TemporaryDirectory() as scratch:
            bin_dir = Path(scratch)
            (bin_dir / "dirname").symlink_to(shutil.which("dirname"))
            for name in shims:
                shim = bin_dir / name
                shim.write_text("#!/bin/sh\necho shim:" + name + "\n")
                shim.chmod(0o755)
            environment = {"PATH": str(bin_dir), **env}
            return subprocess.run([shutil.which("bash"), str(self.SCRIPT), "--help"], env=environment, capture_output=True, text=True)

    def test_prefers_python3_over_python(self):
        result = self.invoke(["python3", "python"])
        self.assertEqual(result.stdout.strip(), "shim:python3")

    def test_falls_back_to_python(self):
        result = self.invoke(["python"])
        self.assertEqual(result.stdout.strip(), "shim:python")

    def test_python_command_overrides_discovery(self):
        with tempfile.TemporaryDirectory() as scratch:
            custom = Path(scratch) / "custom-python"
            custom.write_text("#!/bin/sh\necho shim:custom\n")
            custom.chmod(0o755)
            result = self.invoke(["python3", "python"], PYTHON_COMMAND=str(custom))
        self.assertEqual(result.stdout.strip(), "shim:custom")

    def test_no_interpreter_exits_2_with_message(self):
        result = self.invoke([])
        self.assertEqual(result.returncode, 2)
        self.assertIn("Python 3 is required", result.stderr)


if __name__ == "__main__": unittest.main()
