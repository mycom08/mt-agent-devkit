"""Check the boundary of the unattended benchmark permission policy."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("permissions", Path(__file__).with_name("headless_permissions.py"))
permissions = importlib.util.module_from_spec(spec)
spec.loader.exec_module(permissions)


class PermissionTests(unittest.TestCase):
    def test_cleanup_allows_only_exact_nonrecursive_fixture_files(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder).resolve()
            command = permissions.cleanup_command(root)
            event = {"hook_event_name": "PermissionRequest", "tool_name": "Bash",
                     "tool_input": {"command": command}}
            self.assertEqual(permissions.decision(event, root), "allow")
            for other in (command + ' && git status', command.replace('rm --', 'rm -rf --'),
                          'rm -- "' + (root / '.claude/settings.json').as_posix() + '"'):
                event["tool_input"]["command"] = other
                self.assertEqual(permissions.decision(event, root), "deny")
            event["tool_input"]["command"] = command
            directory = root / '.claude/agents/tmp/pipeline_state.md'
            directory.mkdir(parents=True)
            self.assertEqual(permissions.decision(event, root), "deny")

    def event(self, root, path, tool="Write"):
        return {"hook_event_name": "PermissionRequest", "tool_name": tool,
                "cwd": str(root), "tool_input": {"file_path": str(path)}}

    def test_file_tools_can_write_target_configuration(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder).resolve()
            for tool in ("Write", "Edit"):
                for name in (".claude/agents/tmp/state.json", ".claude/settings.json",
                             ".claude/skills/read-section/SKILL.md"):
                    self.assertEqual(permissions.decision(self.event(root, name, tool), root), "allow")

    def test_other_paths_and_tools_are_denied(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder).resolve()
            for name in ("pricing.py", ".git/config", ".claude/../outside.txt",
                         ".claude", root.parent / "escape.txt", ".claude-other/file"):
                self.assertEqual(permissions.decision(self.event(root, name), root), "deny")
            for tool in ("Bash", "PowerShell", "Read", "Agent"):
                self.assertEqual(permissions.decision(self.event(root, ".claude/a", tool), root), "deny")
            self.assertEqual(permissions.decision({}, root), "deny")
            self.assertEqual(permissions.decision([], root), "deny")
            self.assertEqual(permissions.decision({"tool_input": None}, root), "deny")

    def test_existing_redirect_cannot_escape_target(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder).resolve()
            (root / ".claude").mkdir()
            outside = root / "outside"
            outside.mkdir()
            link = root / ".claude" / "linked"
            try:
                link.symlink_to(outside, target_is_directory=True)
            except OSError:
                self.skipTest("Host does not permit directory symlinks")
            self.assertEqual(permissions.decision(self.event(root, link / "file"), root), "deny")


if __name__ == "__main__":
    unittest.main()
