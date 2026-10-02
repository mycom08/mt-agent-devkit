"""Offline checks for an experimental G5 fallback; no agent/model invocation."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.test import explicit_read_batch as batch


class ExplicitBatchTests(unittest.TestCase):
    def setup_fixture(self, root):
        for name, content in {"notes/alpha.txt": "apples\n", "notes/beta.txt": "bananas\n",
            "notes/gamma.txt": "grapes\n", "data/east.txt": "ORBIT east\n",
            "notes/west.txt": "COMET west\n"}.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content.encode("utf-8"))

    def snapshot(self, root):
        return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*") if p.is_file()}

    def test_both_groups_return_exact_labelled_results_without_mutation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.setup_fixture(root)
            before = self.snapshot(root)
            p01, p02 = batch.execute("P01", root), batch.execute("P02", root)
            self.assertEqual([r["content"] for r in p01["results"]], ["apples\n", "bananas\n", "grapes\n"])
            self.assertEqual([r["label"] for r in p01["results"]], ["alpha", "beta", "gamma"])
            self.assertEqual(p02["results"][0]["matches"], [{"line": 1, "text": "ORBIT east"}])
            self.assertEqual(p02["results"][1]["matches"], [{"line": 1, "text": "COMET west"}])
            self.assertEqual(before, self.snapshot(root))
            self.assertNotIn(str(root), json.dumps(p01))

    def test_all_jobs_are_submitted_before_waiting_on_any_result(self):
        events = []
        class Future:
            def result(self):
                events.append("result")
                return {}
        class Executor:
            def __init__(self, **kwargs): pass
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def submit(self, *args):
                events.append("submit")
                return Future()
        with patch.object(batch, "ThreadPoolExecutor", Executor):
            batch.execute("P01", Path.cwd())
        self.assertEqual(events, ["submit"] * 3 + ["result"] * 3)

    def test_missing_large_invalid_text_and_excess_matches_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.setup_fixture(root)
            path = root / "notes/alpha.txt"
            for content in (b"x" * (batch.MAX_FILE_BYTES + 1), b"\xff"):
                path.write_bytes(content)
                with self.assertRaises((ValueError, UnicodeError)):
                    batch.execute("P01", root)
            path.unlink()
            with self.assertRaises(ValueError):
                batch.execute("P01", root)
            (root / "data/east.txt").write_text("ORBIT\n" * 33, encoding="utf-8")
            with self.assertRaises(ValueError):
                batch.execute("P02", root)

    def test_output_bound_and_unsupported_operation_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.setup_fixture(root)
            with patch.object(batch, "MAX_RESULT_BYTES", 10), self.assertRaises(ValueError):
                batch.execute("P01", root)
            for case in ("P03", "delete", "../outside", "P01; git commit"):
                with self.assertRaises(ValueError):
                    batch.execute(case, root)

    def test_redirected_inputs_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.setup_fixture(root)
            with patch.object(Path, "is_symlink", return_value=True), self.assertRaises(ValueError):
                batch.execute("P01", root)


if __name__ == "__main__":
    unittest.main()
