"""The GitHub comment hook: rules, shell reading, provider envelopes and configs.

Every case feeds the hook input JSON; nothing is ever posted to GitHub.
"""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / ".mt-agent-devkit/scripts/check_gh_posts.py"
spec = importlib.util.spec_from_file_location("check_gh_posts", SCRIPT)
hook = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook)

CHECKS = "Layer-1 invariant check\tpass\t58s\thttps://github.com/o/r/actions/runs/1/job/2"
FENCE = "```"


def fenced(content, language=""):
    return FENCE + language + "\n" + content + "\n" + FENCE


class HookCase(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.cwd = Path(folder.name)

    def claude(self, command, tool="Bash"):
        payload = {"tool_name": tool, "tool_input": {"command": command}, "cwd": str(self.cwd)}
        return hook.respond("claude", json.dumps(payload))

    def body(self, text, command="gh issue comment 1"):
        (self.cwd / "body.md").write_text(text, encoding="utf-8")
        return self.claude(command + " --body-file body.md")

    def assertDenied(self, answer, fragment=""):
        self.assertIsNotNone(answer, "expected a denial, command passed")
        output = answer["hookSpecificOutput"]
        self.assertEqual(output.get("permissionDecision"), "deny", output)
        self.assertIn(fragment, output["permissionDecisionReason"])

    def assertWarned(self, answer, fragment):
        self.assertIsNotNone(answer, "expected a warning")
        output = answer["hookSpecificOutput"]
        self.assertNotIn("permissionDecision", output)
        self.assertIn(fragment, output["additionalContext"])


class BlockingRules(HookCase):
    def test_approve_is_blocked_in_every_spelling(self):
        for command in ("gh pr review 5 --approve", "gh pr review --approve 5 -b ok", "gh pr review 5 -a",
                        "gh -R o/r pr review 5 -a", "cd x && gh pr review 5 --approve",
                        "GH_TOKEN=x gh pr review 5 --approve", "echo y; (gh pr review 5 --approve)"):
            with self.subTest(command=command):
                self.assertDenied(self.claude(command), "--approve")

    def test_other_review_verdicts_and_commands_pass(self):
        for command in ("gh pr review 5 --comment -b fine", "gh pr review 5 --request-changes -b 'fix it'",
                        "gh pr view 5", "gh issue edit 5 --add-label x",
                        "gh pr create --title t --body 'Closes #5'",
                        "echo gh pr review 5 --approve", "git commit -m 'x; gh pr review 5 --approve'",
                        "# gh pr review 5 --approve", "grep 'gh pr review --approve' file"):
            with self.subTest(command=command):
                self.assertIsNone(self.claude(command))

    def test_mentions_and_bare_numbers_outside_code_are_blocked(self):
        for text, fragment in (("Ask @tl to check", "@tl"), ("Same as #12.", "#12"), ("(#7)", "#7")):
            for command in ("gh issue comment 1", "gh pr comment 1", "gh pr review 1 --comment"):
                with self.subTest(text=text, command=command):
                    self.assertDenied(self.body(text, command), fragment)

    def test_mentions_and_numbers_inside_code_links_and_words_pass(self):
        for text in ("Install `@types/node` and see `#12`.", fenced("@decorator\n# 1", "python"),
                     "Mail noreply@example.com", "See https://github.com/o/r/issues/1#issuecomment-2",
                     "ST-000012 and o/r#12", "## 2 Heading", "`a\nb @c`"):
            with self.subTest(text=text):
                self.assertIsNone(self.body(text))

    def test_fenced_command_or_test_output_is_blocked(self):
        for block in (fenced("$ git status\nnothing to commit"), fenced("Ran 116 tests in 3.2s\n\nOK"),
                      fenced("[PASS] inv1\nResults: 3 passed, 0 failed", "text"), fenced("anything", "console"),
                      fenced("===== 5 passed in 0.1s ====="), fenced("Traceback (most recent call last):\n x", "bash"),
                      "~~~\nPreflight: PASS\n~~~", "> " + FENCE + "\n> FAILED (failures=1)\n> " + FENCE):
            with self.subTest(block=block):
                self.assertDenied(self.body("Result:\n" + block), "output")

    def test_fenced_commands_code_and_templates_pass(self):
        for block in (fenced("git push origin main", "bash"), fenced("print('OK')", "python"),
                      fenced('{"status": "PASS"}', "json"), fenced("**Decision:** x\n**Next:** None", "markdown")):
            with self.subTest(block=block):
                self.assertIsNone(self.body(block))

    def test_script_code_is_not_output(self):
        for language, script in (
                ("bash", 'if [ -z "$x" ]; then\n  exit 1\nfi'), ("sh", "python3 hook.py || exit 0"),
                ("powershell", "if ($x) { exit 1 }"), ("", "exit 2"), ("", "git pull || exit 1"),
                ("bash", 'FAILED=0\nok "done"\nFAIL "no input"'), ("bash", "# exit code 2 blocks\n# 3 failed jobs retry"),
                ("bash", 'echo "1 failed"\necho "exit code 1"\necho "BUILD FAILED"')):
            with self.subTest(script=script):
                self.assertIsNone(self.body(fenced(script, language)))

    def test_exit_and_result_wording_is_still_output(self):
        for line in ("Error: exit code 1", "exit status 2", "Process exited with 3", "Exit code: 1",
                     "The command exited with code 127", 'Command "npm test" failed with exit code 1',
                     "FAILED tests/a.py::test_x - boom", "not ok 2 - merge", "ok  \texample.com/pkg\t0.31s",
                     "[INFO] BUILD SUCCESS", "3 passed, 1 failed"):
            with self.subTest(line=line):
                self.assertDenied(self.body(fenced(line)), "output")

    def test_checks_table_is_exempt_only_in_pr_comments(self):
        spaced = "Layer-1 invariant check  pass  58s  https://github.com/o/r/runs/1"
        terminal = "All checks were successful\n0 failing, 1 successful\n\n✓  Layer-1  58s  https://x"
        for table in (CHECKS, spaced, terminal, "$ gh pr checks 5\n" + CHECKS):
            for command in ("gh pr comment 5", "gh pr review 5 --comment"):
                with self.subTest(table=table, command=command):
                    self.assertIsNone(self.body("Approved.\n" + fenced(table), command))
        self.assertDenied(self.body(fenced(CHECKS), "gh issue comment 5"), "output")
        self.assertDenied(self.body(fenced(CHECKS + "\nRan 4 tests in 1s"), "gh pr comment 5"), "output")


class Warnings(HookCase):
    def test_long_comment_warns_unless_an_exception_is_stated(self):
        long_text = "word " * 230
        self.assertWarned(self.body(long_text), "words")
        for note in ("_Over 200 words by exception: one comment per story._",
                     "QA report, exempt from the word cap."):
            with self.subTest(note=note):
                self.assertIsNone(self.body(note + "\n" + long_text))
        self.assertIsNone(self.body("word " * 190))

    def test_checks_paste_does_not_count_toward_the_cap(self):
        table = "\n".join([CHECKS] * 40)
        self.assertIsNone(self.body("Approved.\n" + fenced(table), "gh pr comment 5"))

    def test_thread_status_without_decision_warns(self):
        self.assertWarned(self.body("**Thread Status:** Open\nHello"), "Decision")
        for decision in ("**Decision:** yes", "**Decision (user):** yes"):
            with self.subTest(decision=decision):
                self.assertIsNone(self.body("**Thread Status:** Open\n" + decision))

    def test_denial_reason_also_carries_warnings(self):
        answer = self.body("**Thread Status:** Open\nping @qa")
        self.assertDenied(answer, "@qa")
        self.assertDenied(answer, "Decision")


class BodySources(HookCase):
    def test_inline_forms(self):
        for command in ('gh issue comment 1 --body "ping @qa"', "gh issue comment 1 --body='ping @qa'",
                        "gh issue comment 1 -b 'ping @qa'", "gh pr comment 1 -b$'line\\nping @qa'",
                        'gh issue comment 1 --body "line one\nping @qa"',
                        "BODY='ping @qa'\ngh issue comment 1 --body \"$BODY\""):
            with self.subTest(command=command):
                self.assertDenied(self.claude(command), "@qa")

    def test_bash_heredocs(self):
        for command in (
                "gh issue comment 1 --body-file - <<'EOF'\nping @qa\nEOF",
                "gh issue comment 1 -F - <<EOF\nping @qa\nEOF\necho done",
                "gh issue comment 1 --body \"$(cat <<'EOF'\nit's (fine) @qa\nEOF\n)\"",
                "cat <<'EOF' | gh issue comment 1 --body-file -\nping @qa\nEOF",
                "cat > body.md <<'EOF'\nping @qa\nEOF\ngh issue comment 1 --body-file body.md",
                "gh issue comment 1 --body-file - <<< 'ping @qa'"):
            with self.subTest(command=command):
                self.assertDenied(self.claude(command), "@qa")

    def test_heredoc_content_is_not_read_as_a_command(self):
        self.assertIsNone(self.claude("cat > notes.md <<'EOF'\ngh pr review 1 --approve\nEOF"))

    def test_body_rewritten_in_the_same_command_ignores_the_stale_file(self):
        (self.cwd / "body.md").write_text("ping @qa", encoding="utf-8")
        self.assertIsNone(self.claude("python3 gen.py > body.md && gh issue comment 1 -F body.md"))
        self.assertIsNone(self.claude("cat > body.md <<'EOF'\nclean\nEOF\ngh issue comment 1 -F body.md"))

    def test_relative_paths_follow_cd_and_absolute_paths_are_read(self):
        (self.cwd / "sub").mkdir()
        (self.cwd / "sub/b.md").write_text("ping @qa", encoding="utf-8")
        self.assertDenied(self.claude("cd sub && gh issue comment 1 -F b.md"), "@qa")
        self.assertDenied(self.claude('gh issue comment 1 -F "%s"' % (self.cwd / "sub/b.md").as_posix()), "@qa")

    def test_windows_paths_keep_their_backslashes(self):
        for command in (r"gh issue comment 1 --body-file C:\Users\a\body.md",
                        r'gh issue comment 1 --body-file "C:\Users\a\body.md"'):
            for powershell in (False, True):
                with self.subTest(command=command, powershell=powershell):
                    words = hook.ShellReader(command, powershell).read()[0].words
                    self.assertEqual(words[-1].text, r"C:\Users\a\body.md")

    def test_powershell_forms(self):
        for command in ("gh issue comment 1 --body @'\nit's @qa\n'@",
                        "$body = @'\nping @qa\n'@\ngh issue comment 1 --body $body",
                        "@'\nping @qa\n'@ | gh issue comment 1 --body-file -",
                        "$body = @\"\r\nping @qa\r\n\"@\r\ngh pr comment 1 -F - <# note #>; $x = 1\r\n$body | gh pr comment 1 -F -",
                        "gh issue comment 1 `\n  --body 'ping @qa'",
                        "& gh pr review 1 --approve; Write-Host @qa"):
            with self.subTest(command=command):
                self.assertDenied(self.claude(command, "PowerShell"))
        self.assertIsNone(self.claude('gh issue comment 1 --body "use ``@types`` here"', "PowerShell"))

    def test_unparseable_or_unknown_input_passes(self):
        for command in ('gh issue comment 1 --body "@qa', "gh issue comment 1 -F - <<EOF\n@qa",
                        'gh issue comment 1 --body "$BODY"', 'gh issue comment 1 --body "$(make-body)"',
                        "gh issue comment 1 -F missing.md", 'gh issue comment 1 -F "$TMP/b.md"',
                        "gh issue comment 1", "gh issue comment 1 --body"):
            with self.subTest(command=command):
                self.assertIsNone(self.claude(command))
        for raw in ("", "not json", "{}", "[]", '{"tool_input": {"command": 5}}'):
            with self.subTest(raw=raw):
                self.assertIsNone(hook.respond("claude", raw))
                self.assertEqual(hook.respond("antigravity", raw), {"decision": "allow"})


class ProviderEnvelopes(HookCase):
    def antigravity(self, command):
        payload = {"toolCall": {"name": "run_command", "args": {"CommandLine": command, "Cwd": str(self.cwd)}}}
        return hook.respond("antigravity", json.dumps(payload))

    def test_antigravity_always_answers(self):
        self.assertEqual(self.antigravity("ls"), {"decision": "allow"})
        denied = self.antigravity("gh pr review 1 --approve")
        self.assertEqual(denied["decision"], "deny")
        self.assertIn("--approve", denied["reason"])
        warned = self.antigravity("gh issue comment 1 -b '**Thread Status:** Open'")
        self.assertEqual(warned["decision"], "allow")
        self.assertIn("Decision", warned["reason"])
        (self.cwd / "b.md").write_text("ping @qa", encoding="utf-8")
        self.assertEqual(self.antigravity("gh issue comment 1 -F b.md")["decision"], "deny")

    def test_script_runs_as_a_process_and_always_exits_zero(self):
        deny = {"tool_name": "Bash", "tool_input": {"command": "gh pr review 1 --approve"}, "cwd": str(self.cwd)}
        for arguments, raw, expected in ((["claude"], json.dumps(deny), "deny"), (["claude"], "broken", ""),
                                         (["antigravity"], "broken", "allow"), ([], json.dumps(deny), "deny")):
            with self.subTest(arguments=arguments, raw=raw[:10]):
                result = subprocess.run([sys.executable, str(SCRIPT), *arguments], input=raw.encode(), capture_output=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn(expected, result.stdout.decode())
                if not expected:
                    self.assertEqual(result.stdout, b"")


class InstalledConfigs(unittest.TestCase):
    """This repo's own hook configuration."""

    def commands(self):
        claude = json.loads((ROOT / ".claude/settings.json").read_text(encoding="utf-8"))
        agents = json.loads((ROOT / ".agents/hooks.json").read_text(encoding="utf-8"))
        return claude, agents["mt-agent-devkit-gh-posts"]

    def test_devkit_configs_run_the_shared_script_and_never_block_when_it_cannot_start(self):
        claude, agents = self.commands()
        self.assertEqual(set(claude), {"hooks"}, "no permission rules belong to the hook install")
        for events, matcher in ((claude["hooks"], "Bash|PowerShell"), (agents, "run_command")):
            group, = events["PreToolUse"]
            self.assertEqual(group["matcher"], matcher)
            command = group["hooks"][0]["command"]
            self.assertIn(".mt-agent-devkit/scripts/check_gh_posts.py", command)
            self.assertTrue(command.endswith("|| exit 0"), command)

    @unittest.skipUnless(shutil.which("bash") and sys.platform != "win32", "POSIX shell required")
    def test_missing_script_does_not_block(self):
        claude, agents = self.commands()
        with tempfile.TemporaryDirectory() as folder:
            (Path(folder) / ".agents").mkdir()
            for command, cwd in ((claude["hooks"]["PreToolUse"][0]["hooks"][0]["command"], Path(folder)),
                                 (agents["PreToolUse"][0]["hooks"][0]["command"], Path(folder) / ".agents")):
                result = subprocess.run(["bash", "-c", command], cwd=cwd, input=b"{}", capture_output=True,
                                        env={"PATH": "/usr/bin:/bin", "CLAUDE_PROJECT_DIR": folder})
                self.assertEqual((result.returncode, result.stdout), (0, b""))


def load_module(name, path):
    module_spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return module


class InstallAndSync(unittest.TestCase):
    """The hook reaches targets and a project's own hook settings survive."""

    # The last engine shipped before the hook: what an existing target syncs with.
    OLD_ENGINE_COMMIT = "4c5c46aabd598d4bcbc97676e7ecaae22c56f355"
    OWN = {"matcher": "Bash", "hooks": [{"type": "command", "command": "./project-hook.sh"}]}
    BOUND = {provider: {"PROVIDER_ROOT": "." + provider, "RUNTIME_ROOT": "." + provider + "/agents",
                        "COMMAND_ROOT": "." + provider + "/agents"} for provider in ("claude", "antigravity")}

    @classmethod
    def setUpClass(cls):
        folder = tempfile.TemporaryDirectory()
        cls.addClassCleanup(folder.cleanup)
        cls.scratch = Path(folder.name)
        phase2 = ROOT / ".mt-agent-devkit/distribution/phase2"
        builder = load_module("hook_builder", phase2 / "build_bundle.py")
        builder.build(ROOT, cls.scratch / "bundle")
        cls.manifest = cls.scratch / "bundle/deployment.json"
        cls.engine = load_module("hook_engine", phase2 / "deployment.py")

    def setUp(self):
        self.target = Path(tempfile.mkdtemp(dir=self.scratch))

    def put(self, relative, content):
        path = self.target / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content if isinstance(content, str) else json.dumps(content), encoding="utf-8")

    def read(self, relative):
        return json.loads((self.target / relative).read_text(encoding="utf-8"))

    def install(self, engine=None, profile="repo", extra=None):
        engine = engine or self.engine
        source = {"kind": "local", "tag": None, "commit": "0" * 40, "snapshot_version": "0.0.0",
                  "manifest_sha256": engine.digest(self.manifest.read_bytes())}
        adaptations = {name: "# Fixture\n**Mode:** github\n" for name in ("CLAUDE.md", "AGENTS.md")}
        adaptations.update({".mt-agent-devkit/context/Project_Priming.md": "# Context\n",
                            ".mt-agent-devkit/context/Document_Index.md": "# Docs\n", ".gitignore": "x\n", **(extra or {})})
        plan = engine.plan(self.target, self.manifest, source, "github", profile, self.BOUND, adaptations)
        engine.apply(self.target, plan)
        engine.verify(self.target)
        return plan

    def claude_commands(self):
        return [item["command"] for group in self.read(".claude/settings.json")["hooks"]["PreToolUse"] for item in group["hooks"]]

    def seed_project_hooks(self):
        self.put(".claude/settings.json", {"hooks": {"PreToolUse": [self.OWN]}, "custom": True})
        self.put(".agents/hooks.json", {"project-hook": {"PreToolUse": [self.OWN]}})

    def assertHookInstalled(self):
        self.assertEqual(self.claude_commands().count(self.read(".claude/settings.json")["hooks"]["PreToolUse"][-1]["hooks"][0]["command"]), 1)
        self.assertIn("check_gh_posts.py", self.claude_commands()[-1])
        self.assertIn("mt-agent-devkit-gh-posts", self.read(".agents/hooks.json"))
        self.assertTrue((self.target / ".mt-agent-devkit/scripts/check_gh_posts.py").is_file())

    def test_fresh_install_matches_this_repo_configuration(self):
        for profile in ("repo", "project_root"):
            with self.subTest(profile=profile):
                self.setUp()
                self.install(profile=profile)
                self.assertHookInstalled()
                self.assertEqual(self.read(".claude/settings.json")["hooks"]["PreToolUse"],
                                 json.loads((ROOT / ".claude/settings.json").read_text())["hooks"]["PreToolUse"])
                self.assertEqual(self.read(".agents/hooks.json"), json.loads((ROOT / ".agents/hooks.json").read_text()))

    def test_install_keeps_project_hooks_and_a_second_run_changes_nothing(self):
        self.seed_project_hooks()
        self.install()
        self.assertHookInstalled()
        self.assertIn("./project-hook.sh", self.claude_commands())
        self.assertTrue(self.read(".claude/settings.json")["custom"])
        self.assertEqual(self.read(".agents/hooks.json")["project-hook"], {"PreToolUse": [self.OWN]})
        again = self.install()
        self.assertEqual({op["action"] for op in again["operations"]}, {"preserve"})

    def devkit_entries(self):
        return [json.loads((ROOT / ".claude/settings.json").read_text())["hooks"]["PreToolUse"][0]["hooks"][0],
                json.loads((ROOT / ".agents/hooks.json").read_text())["mt-agent-devkit-gh-posts"]["PreToolUse"][0]["hooks"][0]]

    def test_every_shipped_command_is_one_the_merge_recognises(self):
        shipped = {entry["command"] for entry in self.devkit_entries()}
        self.assertEqual(shipped, set(self.engine.GH_POSTS_COMMANDS))

    def test_devkit_entries_are_replaced_and_enabled_choice_stays(self):
        claude, antigravity = self.devkit_entries()
        self.put(".claude/settings.json", {"hooks": {"PreToolUse": [
            {"matcher": "Bash", "hooks": [claude, *self.OWN["hooks"]]}, {"matcher": "Bash", "hooks": [claude]}]}})
        self.put(".agents/hooks.json", {"mine": {"PreToolUse": [{"matcher": "run_command", "hooks": [antigravity]}]},
                                        "mt-agent-devkit-gh-posts": {"enabled": False, "PreToolUse": []}})
        self.install()
        self.assertEqual(self.claude_commands(), ["./project-hook.sh", claude["command"]])
        hooks = self.read(".agents/hooks.json")
        self.assertEqual(list(hooks), ["mt-agent-devkit-gh-posts"])
        self.assertFalse(hooks["mt-agent-devkit-gh-posts"]["enabled"])
        self.assertTrue(hooks["mt-agent-devkit-gh-posts"]["PreToolUse"])

    def project_commands(self):
        """Commands naming the script that the devkit never wrote."""
        script = ".mt-agent-devkit/scripts/check_gh_posts.py"
        devkit = [entry["command"] for entry in self.devkit_entries()]
        mentions = ["echo see " + script, "cat " + script, "exit 0", "./wrap.sh " + script,
                    "python3 tools/audit.py ../" + script, "python3 tools/audit.py " + script + " || exit 0",
                    'python3 tools/audit.py "../' + script + '"', "node lint.js /srv/app/" + script,
                    "bash run.sh python3 " + script, "timeout 5 python3 " + script, "AUDIT=1 python3 " + script,
                    "python3 -m trace " + script, "python3 -X dev " + script, "python3 tools/check_gh_posts.py",
                    "python3 " + script + " && ./audit.sh", "./audit.sh; python3 " + script,
                    "python3 " + script + " | tee hook.log"]
        own_runs = ["python " + script, "python3 " + script + " --provider claude || exit 0",
                    'python3 "/home/my dir/' + script + '"',
                    'py -3 "C:\\work\\app\\.mt-agent-devkit\\scripts\\check_gh_posts.py"']
        edited = [change for command in devkit for change in (
            command.replace(" || exit 0", ""), command + " && ./audit.sh", command.replace("python3 ", "py -3 "))]
        return mentions + own_runs + edited

    def test_project_hooks_that_only_mention_the_script_are_kept(self):
        own = [{"type": "command", "command": command} for command in self.project_commands()]
        self.put(".claude/settings.json", {"hooks": {"PreToolUse": [{"matcher": "Bash", "hooks": own}]}})
        self.put(".agents/hooks.json", {"mine": {"PreToolUse": [{"matcher": "run_command", "hooks": own}]}})
        self.install()
        self.assertEqual(self.claude_commands()[:-1], [hook["command"] for hook in own])
        self.assertEqual(self.read(".agents/hooks.json")["mine"]["PreToolUse"][0]["hooks"], own)
        self.assertHookInstalled()

    def test_a_local_script_of_the_same_name_is_never_overwritten(self):
        self.put(".mt-agent-devkit/scripts/check_gh_posts.py", "# project's own\n")
        with self.assertRaisesRegex(self.engine.Conflict, "check_gh_posts"):
            self.install()

    def old_engine(self):
        old = self.scratch / "old_deployment.py"
        old.write_bytes(subprocess.run(["git", "show", self.OLD_ENGINE_COMMIT + ":.mt-agent-devkit/distribution/phase2/deployment.py"],
                                       cwd=ROOT, capture_output=True, check=True).stdout)
        return old

    def test_older_installed_engine_syncs_and_the_new_engine_adds_the_claude_hook(self):
        self.put(".claude/settings.json", {"hooks": {"PreToolUse": [self.OWN]}})
        self.install(load_module("old_hook_engine", self.old_engine()))
        self.assertEqual(self.claude_commands(), ["./project-hook.sh"])
        self.assertIn("mt-agent-devkit-gh-posts", self.read(".agents/hooks.json"))
        self.install()
        self.assertHookInstalled()
        self.assertIn("./project-hook.sh", self.claude_commands())

    def test_older_engine_stops_on_an_existing_hook_file_until_it_is_adapted(self):
        """The documented upgrade path for a target that already has `.agents/hooks.json`."""
        old = load_module("old_hook_engine_adapted", self.old_engine())
        own = json.dumps({"project-hook": {"PreToolUse": [self.OWN]}}, indent=4) + "\n"
        self.put(".agents/hooks.json", own)
        with self.assertRaisesRegex(old.Conflict, "divergent or unknown baseline: .agents/hooks.json"):
            self.install(old)
        self.install(old, extra={".agents/hooks.json": own})
        self.assertEqual((self.target / ".agents/hooks.json").read_text(encoding="utf-8"), own)
        self.install()
        self.assertHookInstalled()
        self.assertEqual(self.read(".agents/hooks.json")["project-hook"], {"PreToolUse": [self.OWN]})

    def test_strict_mode_ignores_the_antigravity_hook_file(self):
        sys.path.insert(0, str(ROOT / ".mt-agent-devkit/distribution/phase2"))
        self.addCleanup(sys.path.pop, 0)
        import lifecycle
        adaptations, _ = lifecycle.ignores(self.target, self.BOUND, "strict", {}, None)
        self.assertIn(".agents/hooks.json", adaptations[".gitignore"].splitlines())


if __name__ == "__main__":
    unittest.main()
