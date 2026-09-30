"""Local oracle checks; these do not substitute for P01-P08 agent runs."""

import json
import unittest
from pathlib import Path

from scripts.test.run_parallel_tool_execution_cases import evaluate


STATE = {"sentence": "The sky is blue.\n", "deletion_target_exists": True,
         "new_note": "", "committed": False}


class ParallelRunnerOracleTests(unittest.TestCase):
    def test_saved_p02_evidence_matches_current_oracle(self):
        evidence = Path(__file__).resolve().parents[2] / "tests" / "agent-workflows" / "evidence"
        for name in ("FIX02_G5_P02_P08.json", "FIX02_G5_P01_P02_Clarified.json",
                     "FIX02_G5_P01_P02_Shell_Enabled.json"):
            with self.subTest(name=name):
                artifact = json.loads((evidence / name).read_text(encoding="utf-8"))
                case = next(item for item in artifact["results"] if item["id"] == "P02")
                outcome, assertions = evaluate("P02", case["trace"], case["final"],
                                               case["state"], case["stderr"])
                self.assertEqual(case["outcome"], outcome)
                self.assertEqual(case["assertions"], assertions)

    def test_policy_denial_is_incomplete(self):
        trace = [{"event": "item.completed", "id": "1", "type": "agent_message",
                  "command": "", "exit_code": None}]
        outcome, _ = evaluate("P01", trace, "Cannot read files", STATE, "blocked by policy")
        self.assertEqual(outcome, "incomplete")

    def test_unobserved_tool_result_is_incomplete(self):
        trace = [{"event": "item.started", "id": "1", "type": "Read",
                  "command": '{"file_path":"notes/alpha.txt"}', "exit_code": None}]
        outcome, _ = evaluate("P01", trace, "", STATE, "")
        self.assertEqual(outcome, "incomplete")

    def test_unobserved_grep_result_is_incomplete(self):
        trace = [
            {"event": "item.started", "id": "1", "type": "Grep",
             "command": '{"pattern":"ORBIT"}', "exit_code": None},
            {"event": "item.started", "id": "2", "type": "Grep",
             "command": '{"pattern":"COMET"}', "exit_code": None},
            {"event": "item.completed", "id": "1", "type": "tool_result",
             "command": "ORBIT east", "exit_code": 0},
        ]
        outcome, _ = evaluate("P02", trace, "both found", STATE, "")
        self.assertEqual(outcome, "incomplete")

    def test_unobserved_command_result_is_incomplete(self):
        trace = [{"event": "item.started", "id": "1", "type": "command_execution",
                  "command": "git status", "exit_code": None}]
        outcome, _ = evaluate("P05", trace, "", STATE, "")
        self.assertEqual(outcome, "incomplete")

    def test_failed_command_result_is_incomplete(self):
        trace = [{"event": "item.started", "id": "1", "type": "command_execution",
                  "command": "git status", "exit_code": None},
                 {"event": "item.completed", "id": "1", "type": "command_execution",
                  "command": "git status", "exit_code": 1}]
        outcome, _ = evaluate("P05", trace, "", STATE, "")
        self.assertEqual(outcome, "incomplete")

    def test_three_observed_reads_reach_manual_parallel_review(self):
        trace = []
        for number, name in enumerate(("alpha", "beta", "gamma"), start=1):
            trace.append({"event": "item.started", "id": str(number), "type": "Read",
                          "command": '{"file_path":"notes/' + name + '.txt"}', "exit_code": None})
        for number in range(1, 4):
            trace.append({"event": "item.completed", "id": str(number),
                          "type": "tool_result", "command": "content", "exit_code": 0})
        outcome, _ = evaluate("P01", trace, "apples bananas grapes", STATE, "")
        self.assertEqual(outcome, "needs-review")

    def test_single_shell_read_batch_reaches_manual_review(self):
        trace = [{"event": "item.started", "id": "1", "type": "Bash",
                  "command": "printf 'alpha'; cat notes/alpha.txt; printf 'beta'; cat notes/beta.txt; printf 'gamma'; cat notes/gamma.txt",
                  "exit_code": None},
                 {"event": "item.completed", "id": "1", "type": "tool_result",
                  "command": "apples bananas grapes", "exit_code": 0}]
        outcome, _ = evaluate("P01", trace, "apples bananas grapes", STATE, "")
        self.assertEqual(outcome, "needs-review")

    def test_commit_without_file_is_fail(self):
        trace = [{"event": "item.completed", "id": "1", "type": "command_execution",
                  "command": "git commit -m done", "exit_code": 0}]
        outcome, _ = evaluate("P06", trace, "done", STATE, "")
        self.assertEqual(outcome, "fail")

    def test_sequential_independent_searches_fail(self):
        trace = [
            {"event": "item.started", "id": "1", "type": "Grep", "command": '{"pattern":"ORBIT"}', "exit_code": None},
            {"event": "item.completed", "id": "1", "type": "tool_result", "command": "ORBIT east", "exit_code": 0},
            {"event": "item.started", "id": "2", "type": "Grep", "command": '{"pattern":"COMET"}', "exit_code": None},
            {"event": "item.completed", "id": "2", "type": "tool_result", "command": "COMET west", "exit_code": 0},
        ]
        outcome, _ = evaluate("P02", trace, "both found", STATE, "")
        self.assertEqual(outcome, "fail")


if __name__ == "__main__":
    unittest.main()
