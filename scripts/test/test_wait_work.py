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
UPGRADE_403 = "gh: Upgrade to GitHub Pro or make this repository public to enable this feature. (HTTP 403)"
BAD_CREDENTIALS_401 = "gh: Bad credentials (HTTP 401)\nTry authenticating with:  gh auth login"
SCOPE_403 = 'gh: This API operation needs the "repo" scope. To request it, run:  gh auth refresh -h github.com -s repo (HTTP 403)'
FORBIDDEN_403 = "gh: Resource not accessible by personal access token (HTTP 403)"
RATE_LIMIT_403 = "gh: API rate limit exceeded for user ID 1. (HTTP 403)"
NOT_FOUND_404 = "gh: Branch not found (HTTP 404)"


def run(name="CI", status="completed", conclusion="success", sha=SHA, identity=1):
    return dict(workflowName=name, status=status, conclusion=conclusion, headSha=sha, databaseId=identity)


class GitHubFixture:
    def __init__(self, runs=None, checks=None, required=(), heads=None, prior=None, external=None, base_exists=True):
        self.runs = runs or []
        self.checks = checks or []
        self.required = required
        self.heads = heads or [SHA]
        self.prior = prior or []
        self.external = external or []
        self.base_exists = base_exists
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
        if args[:2] == ["api", "graphql"] and not self.base_exists:
            return {"data": {"repository": {"ref": None}}}
        if args[:2] == ["api", "graphql"]:
            rule = {"requiredStatusCheckContexts": list(self.required)} if self.required else None
            return {"data": {"repository": {"ref": {"branchProtectionRule": rule}}}}
        if "/rules/" in args[-1]:
            return [[]]
        if "/branches/" in args[-1]:
            return {"name": "main"}
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


def lookup_name(args):
    if args[:2] == ["api", "graphql"]:
        return "protection"
    if "/rules/" in args[-1]:
        return "rules"
    if args[:2] in (["pr", "view"], ["pr", "checks"], ["run", "list"]):
        return " ".join(args[:2])
    return "branch" if "/branches/" in args[-1] else "other"


class FailingGh:
    """Stands in for the gh process, so the real gh_json classifies real stderr."""

    def __init__(self, fixture, failures):
        self.fixture = fixture
        self.failures = failures

    def __call__(self, command, **kwargs):
        args = command[1:]
        stderr = self.failures.get(lookup_name(args))
        if stderr:
            return subprocess.CompletedProcess(command, 1, "", stderr)
        return subprocess.CompletedProcess(command, 0, json.dumps(self.fixture(args)), "")


class PlanLimitTests(unittest.TestCase):
    LOOKUP_SETS = (("protection",), ("rules",), ("protection", "rules"))

    def snapshot(self, fixture, failures, required=()):
        with patch.object(w.subprocess, "run", side_effect=FailingGh(fixture, failures)):
            return w.ci_snapshot("owner/repo", 1, SHA, w.gh_json, required)

    def upgrade(self, lookups):
        return dict.fromkeys(lookups, UPGRADE_403)

    def assert_error(self, fixture, failures, expected_class):
        with self.assertRaises(w.WaitError) as caught:
            self.snapshot(fixture, failures)
        self.assertEqual(str(caught.exception), "GitHub " + expected_class + " error; recover then retry same identity")

    def test_error_classes(self):
        for stderr, expected in (
            (BAD_CREDENTIALS_401, "authentication"),
            ("HTTP 401", "authentication"),
            ("gh: bad credentials", "authentication"),
            ("To get started with GitHub CLI, please run:  gh auth login", "authentication"),
            (RATE_LIMIT_403, "rate limit"),
            ("gh: You have exceeded a secondary rate limit. (HTTP 403)", "rate limit"),
            (UPGRADE_403, "feature unavailable"),
            (SCOPE_403, "permission"),
            (FORBIDDEN_403, "permission"),
            ("gh: Upgrade your plan (HTTP 403)", "permission"),
            (NOT_FOUND_404, "network/API"),
            ("connection reset", "network/API"),
        ):
            self.assertEqual(w.error_class(stderr), expected, stderr)

    def test_upgrade_403_on_either_or_both_lookups_reports_check_outcomes(self):
        for lookups in self.LOOKUP_SETS:
            for runs, checks, expected in (
                ([run()], [{"name": "external", "state": "SUCCESS"}], "PASS"),
                ([run(conclusion="failure")], [], "FAIL"),
                ([run()], [{"name": "external", "state": "FAILURE"}], "FAIL"),
                ([run(status="in_progress", conclusion=None)], [], "PENDING"),
                ([run()], [{"name": "external", "status": "IN_PROGRESS"}], "PENDING"),
            ):
                evidence = self.snapshot(GitHubFixture(runs, checks), self.upgrade(lookups))
                self.assertEqual(evidence["outcome"], expected, lookups)
                self.assertTrue(evidence["discovery_skipped"])
                self.assertEqual(evidence["inspected_sha"], SHA)

    def test_free_plan_shape_null_protection_rule_with_rules_upgrade(self):
        fixture = GitHubFixture([run()])
        evidence = self.snapshot(fixture, self.upgrade(["rules"]))
        self.assertEqual(evidence["outcome"], "PASS")
        self.assertFalse(any(call[:2] == ["api", "repos/owner/repo/branches/main"] for call in fixture.calls))

    def test_upgrade_403_keeps_no_run_and_stale(self):
        for lookups in self.LOOKUP_SETS:
            self.assertEqual(self.snapshot(GitHubFixture(), self.upgrade(lookups))["outcome"], "NO RUN")
            evidence = self.snapshot(GitHubFixture(prior=[run(sha=OTHER)]), self.upgrade(lookups))
            self.assertEqual((evidence["outcome"], evidence["zero_check_gate"]), ("NO RUN", "required"))
            self.assertEqual(self.snapshot(GitHubFixture(heads=[OTHER]), self.upgrade(lookups))["outcome"], "STALE")
            self.assertEqual(self.snapshot(GitHubFixture([run()], heads=[SHA, OTHER]), self.upgrade(lookups))["outcome"], "STALE")

    def test_required_check_supplies_required_names_when_skipped(self):
        for lookups in self.LOOKUP_SETS:
            evidence = self.snapshot(GitHubFixture([run()]), self.upgrade(lookups), ["security"])
            self.assertEqual((evidence["outcome"], evidence["missing_checks"]), ("PENDING", ["security"]))
            evidence = self.snapshot(GitHubFixture([run()], [{"name": "security", "state": "SUCCESS"}]), self.upgrade(lookups), ["security"])
            self.assertEqual((evidence["outcome"], evidence["missing_checks"]), ("PASS", []))
            fixture = GitHubFixture([run()])
            self.snapshot(fixture, self.upgrade(lookups))
            self.assertFalse(any(call[:2] == ["pr", "checks"] for call in fixture.calls))

    def test_contexts_from_the_answering_lookup_stay_required(self):
        evidence = self.snapshot(GitHubFixture([run()], required=("security",)), self.upgrade(["rules"]))
        self.assertEqual((evidence["outcome"], evidence["missing_checks"]), ("PENDING", ["security"]))

    def test_missing_base_still_errors(self):
        with self.assertRaises(w.WaitError) as caught:
            self.snapshot(GitHubFixture([run()], base_exists=False), self.upgrade(["rules"]))
        self.assertEqual(str(caught.exception), "base branch protection scope unavailable")
        self.assert_error(GitHubFixture([run()]), {"protection": UPGRADE_403, "rules": UPGRADE_403, "branch": NOT_FOUND_404}, "network/API")

    def test_other_errors_on_either_lookup_still_error(self):
        for lookup in ("protection", "rules"):
            for stderr, expected in ((BAD_CREDENTIALS_401, "authentication"), (SCOPE_403, "permission"), (FORBIDDEN_403, "permission"), (RATE_LIMIT_403, "rate limit")):
                self.assert_error(GitHubFixture([run()]), {lookup: stderr}, expected)

    def test_upgrade_403_on_any_other_lookup_still_errors(self):
        for failures in (
            {"pr view": UPGRADE_403},
            {"run list": UPGRADE_403},
            {"pr checks": UPGRADE_403},
            {"protection": UPGRADE_403, "branch": UPGRADE_403},
        ):
            self.assert_error(GitHubFixture([run()]), failures, "feature unavailable")

    def test_real_error_on_one_lookup_is_not_masked_by_upgrade_on_the_other(self):
        self.assert_error(GitHubFixture([run()]), {"protection": UPGRADE_403, "rules": BAD_CREDENTIALS_401}, "authentication")
        self.assert_error(GitHubFixture([run()]), {"protection": SCOPE_403, "rules": UPGRADE_403}, "permission")

    def test_error_text_excludes_gh_output(self):
        with self.assertRaises(w.WaitError) as caught:
            self.snapshot(GitHubFixture([run()]), {"rules": "gh: Bad credentials secret-token (HTTP 401)"})
        self.assertNotIn("secret-token", str(caught.exception))

    def test_available_discovery_is_unchanged(self):
        fixture = GitHubFixture([run()], required=("security",))
        evidence = self.snapshot(fixture, {})
        self.assertEqual((evidence["outcome"], evidence["missing_checks"]), ("PENDING", ["security"]))
        self.assertNotIn("discovery_skipped", evidence)
        self.assertTrue(any(call[:2] == ["pr", "checks"] for call in fixture.calls))

    def test_only_the_upgrade_403_skips_discovery(self):
        for rule in (None, {}, {"requiredStatusCheckContexts": None}, {"requiredStatusCheckContexts": []}):
            fixture = GitHubFixture([run()])
            calls = []
            def request(args, **kwargs):
                calls.append(args)
                if lookup_name(args) == "protection":
                    return {"data": {"repository": {"ref": {"branchProtectionRule": rule}}}}
                if lookup_name(args) == "pr checks":
                    return [{"name": "security", "bucket": "fail"}]
                return fixture(args, **kwargs)
            evidence = w.ci_snapshot("owner/repo", 1, SHA, request)
            self.assertEqual(evidence["outcome"], "FAIL", rule)
            self.assertNotIn("discovery_skipped", evidence)
            self.assertTrue(any(lookup_name(call) == "pr checks" for call in calls), rule)

    def test_null_lookup_answers_error_rather_than_skip(self):
        fixture = GitHubFixture([run()])
        for lookup, answer in (("protection", None), ("rules", None), ("rules", [None])):
            def request(args, **kwargs):
                return answer if lookup_name(args) == lookup else fixture(args, **kwargs)
            with self.assertRaises((TypeError, AttributeError)):
                w.ci_snapshot("owner/repo", 1, SHA, request)

    def test_required_workflow_ruleset_errors_when_protection_is_plan_limited(self):
        fixture = GitHubFixture([run()])
        def request(args, **kwargs):
            if lookup_name(args) == "protection":
                raise w.FeatureUnavailable("GitHub feature unavailable error; recover then retry same identity")
            return [[{"type": "workflows"}]] if "/rules/" in args[-1] else fixture(args, **kwargs)
        with self.assertRaises(w.WaitError) as caught:
            w.ci_snapshot("owner/repo", 1, SHA, request)
        self.assertIn("required workflow rule", str(caught.exception))

    def test_wait_polls_to_completion_and_binds_head_when_skipped(self):
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder) / "ci"
            fixture = GitHubFixture([run(status="in_progress", conclusion=None)])
            now = [0.0]
            def sleep(seconds):
                now[0] += seconds
                fixture.runs = [run()]
            with patch.object(w.subprocess, "run", side_effect=FailingGh(fixture, self.upgrade(["rules"]))):
                evidence = w.ci_wait(directory, "owner/repo", 1, None, [], 5, 1, w.gh_json, lambda: now[0], sleep)
                self.assertEqual((evidence["outcome"], evidence["inspected_sha"]), ("PASS", SHA))
                self.assertEqual(json.loads((directory / "identity.json").read_text())["expected_sha"], SHA)
                fixture.heads = [OTHER]
                self.assertEqual(w.ci_wait(directory, "owner/repo", 1, None, [], 0, 1, w.gh_json, lambda: now[0], sleep)["outcome"], "STALE")

    def test_command_exit_codes(self):
        with tempfile.TemporaryDirectory() as folder:
            harness = Path(folder) / ".claude/harness"
            harness.mkdir(parents=True)
            (harness / "state-paths.json").write_text(json.dumps({"PROVIDER_ROOT": ".claude", "RUNTIME_ROOT": ".claude/agents"}))
            for identity, failures, expected in (
                ("plan-limit", self.upgrade(["rules"]), 0),
                ("unauthorized", {"rules": BAD_CREDENTIALS_401}, 3),
                ("scope", {"rules": SCOPE_403}, 3),
                ("rate-limit", {"protection": RATE_LIMIT_403}, 3),
            ):
                with patch.object(w.subprocess, "run", side_effect=FailingGh(GitHubFixture([run()]), failures)):
                    code = w.main(["ci", "--provider", "claude", "--runtime-root", ".claude/agents", "--root", folder, "--id", identity, "--mode", "github", "--repo", "owner/repo", "--pr", "1", "--window", "0"])
                self.assertEqual(code, expected, identity)


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
            # A forwarding shim, not a symlink: Windows refuses symlinks without elevated rights.
            forward = bin_dir / "dirname"
            forward.write_text('#!/bin/sh\nexec "' + Path(shutil.which("dirname")).as_posix() + '" "$@"\n')
            forward.chmod(0o755)
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
