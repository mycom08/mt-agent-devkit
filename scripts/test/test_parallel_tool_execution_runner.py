"""Local oracle checks; these do not substitute for P01-P08 agent runs."""

import unittest

from scripts.test.run_parallel_tool_execution_cases import evaluate


STATE = {"sentence": "The sky is blue.\n", "deletion_target_exists": True,
         "new_note": "", "committed": False}


class ParallelRunnerOracleTests(unittest.TestCase):
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
