# Token Cost from Sub-Agent Transcripts

Computes real token usage and $ cost for one finished sub-agent, from Claude Code's own transcript file — not an estimate, not the live terminal counter.

## Where the data lives

Every sub-agent spawn writes its own transcript, separate from the parent session:

```
~/.antigravity/projects/<project-slug>/<parentSessionId>/subagents/agent-<id>.jsonl
~/.antigravity/projects/<project-slug>/<parentSessionId>/subagents/agent-<id>.meta.json
```

`.meta.json` has `agentType`, `description`, `toolUseId` (links back to the parent's `Task` call), `spawnDepth`. To find the right file for a specific sub-agent run, check `.meta.json` files under the parent session's `subagents/` folder, or just take the most recently modified `.jsonl` there.

Each line in the `.jsonl` is one logged event. Only `"type":"assistant"` lines carry `message.usage`.

## The gotcha: dedup before summing

One real API call is often logged as **multiple JSONL lines** — one per content block (`thinking`, `text`, `tool_use`) — and every one of those lines repeats the same `usage` object for that call. Summing `usage` across all `"assistant"` lines overcounts, sometimes 2–3x.

**Fix:** group by `message.id` first (one id = one real API call), take one `usage` per group, then sum. `token_cost.sh` does this.

## The second gotcha: `output_tokens` is only complete on the last line

Deduping is necessary but not sufficient. Within one `message.id` group the **input-side** fields (`input_tokens`, `cache_creation*`, `cache_read_input_tokens`) really are identical on every line — but `output_tokens` is not. Early lines of a streamed message carry a **partial** count (often `1`–`5`); only the last line carries the total.

So `map(.[0].message.usage)` — take the first line of each group — silently undercounts output. Measured on a real sub-agent run: **10,822 vs 64,365, a 5.9x undercount**, and output is the most expensive token class at 5x the input rate.

**Fix:** `.[0]` for the input side, `max` across the group for output. The script does this now.

> **This bug is invisible on main-session transcripts** — those repeat the complete `usage` on every line, so first-line and max agree exactly. It bites only on the sub-agent transcripts this script exists to measure. Don't validate a change to the dedup logic against a main-session file.

Check any transcript for the discrepancy:

```sh
jq -s '[.[]|select(.type=="assistant")]|group_by(.message.id)
       |{first:(map(.[0].message.usage.output_tokens//0)|add),
         max:(map([.[].message.usage.output_tokens//0]|max)|add)}' <file>
```

## The reported `subagent_tokens` is not a usage total

When a sub-agent completes, the harness reports a `subagent_tokens` figure. **It is not cumulative usage** — it is the footprint of the agent's **final API call** (cache_write + cache_read + input + output for that one call), which approximates peak context size.

Verified on a real run: reported `148912` matched exactly one call — the last one — while cumulative billed input for the whole run was ~6.96M tokens, **47x larger**.

Use it as a peak-context signal. Never as a cost proxy, and never as the "actual total" against which an agent's own step estimates are compared — that comparison is off by roughly the call count.

## Usage

```sh
./token_cost.sh <agent-transcript.jsonl>
# or with explicit pricing (\$/MTok):
./token_cost.sh <agent-transcript.jsonl> <input_price> <output_price>
```

Requires `jq`. No `jq`? Ask a fresh agent to port the `jq` filter in the script to `node` — same dedup-by-`message.id` logic, just a different runtime.

## Output fields

| Field | Meaning |
|---|---|
| `calls` | Real API calls in this sub-agent's run (after dedup) |
| `input_tokens` | Fresh tokens, not cached — full price |
| `cache_creation_input_tokens` | Tokens newly written to cache this run — costs 1.25x (5-min TTL) or 2x (1-hour TTL) |
| `cache_read_input_tokens` | Tokens served from cache — costs 0.1x |
| `output_tokens` | Generated tokens — full output price |
| `cost_usd.total` | Sum of all four, at the model's per-token rate |

## Pricing caveat

The script has a small hardcoded price table (`$/MTok` by model), current as of when this was written. It **will** go stale. Before trusting a cost figure:
- Check the `model` field in the output matches what you expect.
- Cross-check the rate against `shared/models.md` in the `claude-api` skill, or platform.claude.com/docs/en/pricing.
- If the model isn't in the table, `cost_usd` comes back all zero with a warning — pass the two price args explicitly.

## Why this exists, not the terminal counter

The live number Claude Code shows while a sub-agent runs is a rough running total for that agent's context — useful as a progress signal, not a billing figure. It doesn't break out cache-read vs cache-write vs fresh tokens, and isn't reliable for cost math. This script uses the same `usage` object the API actually bills from.
