"""Isolated version-notice regression; no network or full devkit installation.

VERSION_NOTICE_SOURCE can select an extracted revision for before/after evidence.
The cp1252 shim changes only omitted encodings so this regression also runs on
UTF-8-default hosts; the Windows case executes without that shim or UTF-8 flags.
"""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(os.environ.get("VERSION_NOTICE_SOURCE", str(
    ROOT / ".mt-agent-devkit/distribution/phase2/version_notice.py")))
EXPECTED = {"systemMessage": "Devkit update available: v0.1.52 -> v0.1.53. Run sync devkit."}
TAGS = "abc refs/tags/v0.1.52\nabc refs/tags/v0.1.53\n"
RUNNER = r'''
import contextlib
import json
from pathlib import Path
import runpy
import subprocess
import sys
from unittest.mock import patch

original_read = Path.read_text
def cp1252_read(path, encoding=None, errors=None, **kwargs):
    return original_read(path, encoding=encoding or "cp1252", errors=errors, **kwargs)

def release_lookup(command, **kwargs):
    assert command == ["git", "ls-remote", "--tags", "--refs",
                       "https://github.com/mycom08/mt-agent-devkit.git"], command
    if sys.argv[3] == "failure":
        raise subprocess.CalledProcessError(1, command)
    return subprocess.CompletedProcess(command, 0, stdout=sys.argv[3], stderr="")

shim = patch.object(Path, "read_text", cp1252_read) if sys.argv[2] == "cp1252" else contextlib.nullcontext()
with shim, patch("subprocess.run", side_effect=release_lookup) as lookup:
    runpy.run_path(sys.argv[1], run_name="__main__")
    print(json.dumps({"release_calls": lookup.call_count, "utf8_mode": sys.flags.utf8_mode}))
'''


class VersionNoticeTests(unittest.TestCase):
    def run_notice(self, entries=None, receipt=None, tags=TAGS, source=SOURCE,
                   encoding_mode="cp1252", missing_receipt=False):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            installed = root / ".mt-agent-devkit/scripts/version_notice.py"
            installed.parent.mkdir(parents=True)
            shutil.copyfile(source, installed)
            if not missing_receipt:
                content = receipt if receipt is not None else {
                    "source": {"kind": "release", "tag": "v0.1.52"}}
                text = content if isinstance(content, str) else json.dumps(content, ensure_ascii=False)
                (root / ".mt-agent-devkit/install-receipt.json").write_text(text, encoding="utf-8")
            for name, text in (entries or {}).items():
                (root / name).write_text(text, encoding="utf-8")
            runner = root / "run_notice.py"
            runner.write_text(RUNNER, encoding="utf-8")
            environment = dict(os.environ)
            environment.pop("PYTHONUTF8", None)
            result = subprocess.run([sys.executable, str(runner), str(installed),
                                     encoding_mode, tags], cwd=root, env=environment,
                                    capture_output=True, encoding="utf-8", timeout=20)
            self.assertEqual(result.returncode, 0, result.stderr)
            lines = result.stdout.splitlines()
            self.assertEqual(len(lines), 2, result.stdout)
            return json.loads(lines[0]), json.loads(lines[1])

    def entry(self, suffix=""):
        return "**Devkit source:** https://github.com/mycom08/mt-agent-devkit\n" + suffix

    def test_cp1252_utf8_entrypoints_report_update(self):
        for name in ("CLAUDE.md", "AGENTS.md"):
            with self.subTest(entrypoint=name):
                notice, metadata = self.run_notice({name: self.entry("\u201d")})
                self.assertEqual(notice, EXPECTED)
                self.assertEqual(metadata["release_calls"], 1)

    def test_cp1252_utf8_receipt_reports_update(self):
        notice, metadata = self.run_notice({"AGENTS.md": self.entry()}, receipt={
            "source": {"kind": "release", "tag": "v0.1.52"}, "annotation": "\u201d"})
        self.assertEqual(notice, EXPECTED)
        self.assertEqual(metadata["release_calls"], 1)

    @unittest.skipUnless(sys.platform == "win32", "ordinary Windows invocation")
    def test_windows_ordinary_python_reports_update(self):
        notice, metadata = self.run_notice({"AGENTS.md": self.entry("\u201d")},
                                          encoding_mode="ordinary")
        self.assertEqual(metadata["utf8_mode"], 0)
        self.assertEqual(notice, EXPECTED)
        self.assertEqual(metadata["release_calls"], 1)

    def test_ascii_and_both_entrypoints_remain_supported(self):
        for entries in ({"CLAUDE.md": self.entry()}, {"AGENTS.md": self.entry()},
                        {"CLAUDE.md": self.entry("\u201d"), "AGENTS.md": self.entry("\u201d")}):
            with self.subTest(entries=tuple(entries)):
                notice, metadata = self.run_notice(entries)
                self.assertEqual(notice, EXPECTED)
                self.assertEqual(metadata["release_calls"], 1)

    def test_current_release_and_empty_tag_list_remain_silent(self):
        for tags in ("abc refs/tags/v0.1.52\n", ""):
            with self.subTest(tags=tags):
                notice, metadata = self.run_notice({"AGENTS.md": self.entry()}, tags=tags)
                self.assertEqual(notice, {})
                self.assertEqual(metadata["release_calls"], 1)

    def test_missing_or_invalid_inputs_remain_silent(self):
        cases = [{"missing_receipt": True}, {"receipt": "{"}, {"receipt": {}},
                 {"receipt": {"source": {"kind": "local"}}},
                 {"entries": {}}, {"entries": {"AGENTS.md": "No source"}}]
        for case in cases:
            with self.subTest(case=case):
                options = {"entries": {"AGENTS.md": self.entry()}, **case}
                notice, metadata = self.run_notice(**options)
                self.assertEqual(notice, {})
                self.assertEqual(metadata["release_calls"], 0)

    def test_release_lookup_failure_remains_silent(self):
        notice, metadata = self.run_notice({"AGENTS.md": self.entry()}, tags="failure")
        self.assertEqual(notice, {})
        self.assertEqual(metadata["release_calls"], 1)

    def test_generated_installed_script_reports_update(self):
        spec = importlib.util.spec_from_file_location("notice_bundle_builder",
            ROOT / ".mt-agent-devkit/distribution/phase2/build_bundle.py")
        builder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(builder)
        with tempfile.TemporaryDirectory() as folder:
            bundle = Path(folder)
            manifest = builder.build(ROOT, bundle)
            entry = next(item for item in manifest["files"] if item["id"] == "version_notice.py")
            self.assertEqual(entry["destination"], ".mt-agent-devkit/scripts/version_notice.py")
            self.assertEqual(set(entry["providers"]), {"claude", "antigravity", "codex"})
            self.assertEqual(set(entry["profiles"]), {"repo", "project_root"})
            asset = next(item for item in manifest["assets"] if item["id"] == entry["sources"][0])
            notice, metadata = self.run_notice({"AGENTS.md": self.entry("\u201d")},
                                              source=bundle / asset["path"])
            self.assertEqual(notice, EXPECTED)
            self.assertEqual(metadata["release_calls"], 1)


if __name__ == "__main__":
    unittest.main()
