"""Synthetic stream checks for the local FIX-02 pilot runner."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest
from unittest import mock


RUNNER = Path(__file__).with_name("run_fix02_benchmark.py")
spec = importlib.util.spec_from_file_location("run_fix02_benchmark", RUNNER)
assert spec and spec.loader
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


def assistant(request_id: str, tool_id: str, command: str, output_tokens: int,
              *, input_tokens: int = 10) -> dict:
    return {"type": "assistant", "message": {
        "id": request_id, "model": "claude-sonnet-5",
        "usage": {"input_tokens": input_tokens, "cache_creation_input_tokens": 2,
                  "cache_read_input_tokens": 3, "output_tokens": output_tokens},
        "content": [{"type": "tool_use", "id": tool_id, "name": "PowerShell",
                     "input": {"command": command}}],
    }}


def tool_result(tool_id: str, content: str, *, is_error: bool = False) -> dict:
    return {"type": "user", "message": {"content": [
        {"type": "tool_result", "tool_use_id": tool_id, "is_error": is_error,
         "content": content}]}}


def parse(events: list[dict]) -> dict:
    payload = "\n".join(json.dumps(event) for event in events) + "\n"
    with mock.patch.object(Path, "read_text", return_value=payload):
        return runner.parse_stream(Path("synthetic-stream.jsonl"))


class StreamTests(unittest.TestCase):
    def test_duplicate_assistant_events_and_reused_tool_id(self) -> None:
        events = [
            assistant("request-1", "tool-1", "python -m unittest discover -s tests -v", 1),
            assistant("request-1", "tool-1", "python -m unittest discover -s tests -v", 9),
            tool_result("tool-1", "Exit code: 0\nOutput:\nRan 6 tests in 0.003s\n\nOK"),
            assistant("request-2", "tool-1", "git diff", 4, input_tokens=20),
            tool_result("tool-1", "Exit code: 0\nOutput:\n-prior\n+current"),
            {"type": "result", "result": '{"outcome":"completed","evidence":"done","checks_run":[]}',
             "usage": {"input_tokens": 30, "output_tokens": 13,
                       "cache_creation_input_tokens": 4, "cache_read_input_tokens": 6}},
        ]
        measured = parse(events)
        self.assertEqual(measured["requests"], 2)
        self.assertEqual(measured["tool_invocations"], 2)
        self.assertEqual(measured["usage"]["output_tokens"], 13)
        self.assertEqual(measured["tools_by_name"], {"PowerShell": 2})
        self.assertTrue(measured["test_command_confirmed"])
        self.assertTrue(measured["git_diff_command_confirmed"])
        self.assertEqual(measured["powershell_results_unverified"], 0)

    def test_failed_or_unmatched_command_does_not_count_as_verification(self) -> None:
        first = assistant("request-1", "tool-1", "python -m unittest discover -s tests -v", 8)
        final = {"type": "result", "result": '{"outcome":"completed"}', "usage": {}}
        failed = parse([first, tool_result("tool-1", "Exit code: 1\nRan 6 tests\nFAILED"), final])
        self.assertFalse(failed["test_command_confirmed"])
        self.assertEqual(failed["powershell_results_unverified"], 1)
        unmatched = parse([first, tool_result("wrong-id", "Exit code: 0\nRan 6 tests\nOK"), final])
        self.assertFalse(unmatched["test_command_confirmed"])
        self.assertEqual(unmatched["powershell_results_unverified"], 1)

    def test_cli_success_without_exit_code_and_harness_state_transitions(self) -> None:
        events = [
            assistant("request-1", "tool-1", "python -m unittest discover -s tests -v", 2),
            tool_result("tool-1", "Ran 6 tests in 0.001s\n\nOK"),
            {"type": "result", "result": '{"outcome":"completed"}', "usage": {}},
        ]
        self.assertTrue(parse(events)["test_command_confirmed"])
        state = {
            "current_stage": "developer_implementation", "story_status": "ready",
            "technical_lead_verdict": "pending", "qa_verdict": "pending",
            "product_owner_closure": "pending"}
        repo = mock.MagicMock()
        state_file = repo.__truediv__.return_value
        state_file.read_text.side_effect = lambda **_: json.dumps(state)
        state_file.write_text.side_effect = lambda content, **_: state.update(json.loads(content))
        for role in runner.ROLES:
            runner.advance_state(repo, role)
        self.assertEqual(state["current_stage"], "complete")
        self.assertEqual(state["technical_lead_verdict"], "approved")
        self.assertEqual(state["qa_verdict"], "approved")
        self.assertEqual(state["product_owner_closure"], "closed")

    def test_request_usage_must_be_stable(self) -> None:
        first = assistant("request-1", "tool-1", "git diff", 1)
        second = assistant("request-1", "tool-1", "git diff", 2, input_tokens=11)
        with self.assertRaisesRegex(ValueError, "inconsistent usage.input_tokens"):
            parse([first, second, {"type": "result", "result": "done", "usage": {}}])


if __name__ == "__main__":
    unittest.main()
