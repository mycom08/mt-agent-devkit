# Independent Token Efficiency Review

**Scope:** Independent review of `Agent_Harness_Token_Efficiency_Analysis.md` and `Token_Cost_Model_and_Priorities.md`.
**Date:** 2026-09-21

## 1. Verification of Reported Issues

The existing documents accurately diagnose the core issues in the agent harness. Direct inspection of the codebase confirms:

- **Template Drift:** `.claude/agents/templates/instructions/developer_instructions_template.md` incorrectly lists Sections 2 through 5 as mandatory, whereas the live `Agent_Common_Bootstrap.md` contains 6 sections.
- **Redundant Issue Context:** `Developer_Rules_Bootstrap.md` explicitly forces agents to read "All existing comments on the GitHub Issue," heavily inflating the prefix with resolved discussions.
- **Lack of Bounded Helpers:** `read-section` is the only shipped skill. The absence of bounded helpers for CI logs or PR diffs forces agents to dump massive text blobs into context.
- **Linear Tool Execution:** `Agent_Common_Bootstrap.md` encourages shell-level chaining (e.g., `cmd1 && cmd2`) rather than native parallel tool calling, validating the ~1.1 tool calls/request metric.

## 2. Missing Blind Spots & Additional Findings

While the existing analysis is strong, it misses key architectural and financial realities:

- **The Hidden Cost of `read-section`:** Sequential `read-section` calls compound transcript costs. Because the full context replays per request, 5 sequential reads replay the ~42k token prefix 5 times.
  - *Fix:* Enforce native parallel tool calling for file reads or create a `read-multiple-sections` skill.
- **Financial Asymmetry (Model Routing):** The analysis measures raw tokens but ignores actual financial cost. The Technical Lead (Opus) is significantly more expensive per token than the PO (Haiku).
  - *Fix:* Prioritize context reduction for the Technical Lead over roles using cheaper models.
- **Error & Retry Context Bloat:** When an agent writes a malformed shell command, the error and retry loop permanently append to the un-evicted transcript.
  - *Fix:* Add instructions for defensive shell execution (e.g., test complex `jq` filters on small snippets first).
- **Inefficient State Updates:** Agents often rewrite entire Working Records or Memory files to add a single line.
  - *Fix:* Use `sed`-style in-place appending for state files instead of full-file overwrites to save output tokens.
