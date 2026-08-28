#!/usr/bin/env bash
# Computes real token usage + cost for one finished sub-agent, from its own
# Antigravity transcript file. See README.md in this folder for why the
# dedup step below is required — skipping it overcounts tokens.
#
# Usage:
#   token_cost.sh <agent-transcript.jsonl> [input_$_per_mtok] [output_$_per_mtok]
#
# Price args are optional — if omitted, the script looks up the model found
# in the transcript against the table below (standard API rate, $/MTok).
# This table WILL go stale — verify against shared/models.md in the
# claude-api skill (or platform.antigravity.com/docs/en/pricing) before trusting
# a cost figure for a model not listed, or after a pricing change.

set -euo pipefail

FILE="${1:?usage: token_cost.sh <agent-transcript.jsonl> [input_price_per_mtok] [output_price_per_mtok]}"

if ! command -v jq >/dev/null 2>&1; then
  echo "error: jq is required (https://jqlang.org)" >&2
  exit 1
fi
if [[ ! -f "$FILE" ]]; then
  echo "error: file not found: $FILE" >&2
  exit 1
fi

MODEL=$(jq -r 'select(.type=="assistant") | .message.model' "$FILE" | head -1)

case "$MODEL" in
  claude-fable-5)    DEFAULT_IN=10.00; DEFAULT_OUT=50.00 ;;
  claude-mythos-5)   DEFAULT_IN=10.00; DEFAULT_OUT=50.00 ;;
  claude-opus-5)     DEFAULT_IN=5.00;  DEFAULT_OUT=25.00 ;;
  claude-opus-4-8)   DEFAULT_IN=5.00;  DEFAULT_OUT=25.00 ;;
  claude-opus-4-7)   DEFAULT_IN=5.00;  DEFAULT_OUT=25.00 ;;
  claude-sonnet-5)   DEFAULT_IN=3.00;  DEFAULT_OUT=15.00 ;;
  claude-sonnet-4-6) DEFAULT_IN=3.00;  DEFAULT_OUT=15.00 ;;
  claude-haiku-4-5*) DEFAULT_IN=1.00;  DEFAULT_OUT=5.00  ;;
  *)                 DEFAULT_IN=0;     DEFAULT_OUT=0     ;;
esac

PRICE_IN="${2:-$DEFAULT_IN}"
PRICE_OUT="${3:-$DEFAULT_OUT}"

if [[ "$PRICE_IN" == "0" ]]; then
  echo "warning: unknown model '$MODEL' — cost will be 0. Pass price args explicitly:" >&2
  echo "  token_cost.sh $FILE <input_\$_per_mtok> <output_\$_per_mtok>" >&2
fi

# Dedup by message.id: one real API call can log as several JSONL lines
# (one per content block — thinking/text/tool_use). Grouping by id and taking
# one usage per group avoids counting the same call multiple times.
#
# Input-side fields (input_tokens, cache_creation*, cache_read) are identical
# on every line of a group, so .[0] is safe for those. output_tokens is NOT:
# on sub-agent transcripts the early lines of a streamed message carry a
# partial count (often 1-5) and only the LAST line carries the total. Taking
# .[0] there undercounts output — measured 5.9x low on a real sub-agent run,
# and output is the most expensive token class. Hence: .[0] for the input
# side, max across the group for output.
#
# Main-session transcripts happen to repeat the complete usage on every line,
# so this bug is invisible there and only bites on the sub-agent transcripts
# this script exists to measure. Verify with:
#   jq -s '[.[]|select(.type=="assistant")]|group_by(.message.id)
#          |{first:(map(.[0].message.usage.output_tokens//0)|add),
#            max:(map([.[].message.usage.output_tokens//0]|max)|add)}' <file>
jq -s \
  --arg model "$MODEL" \
  --argjson price_in "$PRICE_IN" \
  --argjson price_out "$PRICE_OUT" '
  [.[] | select(.type=="assistant")]
  | group_by(.message.id)
  | map(.[0].message.usage
        + { output_tokens: ([.[].message.usage.output_tokens // 0] | max) })
  | {
      model: $model,
      calls: length,
      input_tokens: (map(.input_tokens // 0) | add),
      cache_creation_input_tokens: (map(.cache_creation_input_tokens // 0) | add),
      cache_creation_1h_input_tokens: (map(.cache_creation.ephemeral_1h_input_tokens // 0) | add),
      cache_read_input_tokens: (map(.cache_read_input_tokens // 0) | add),
      output_tokens: (map(.output_tokens // 0) | add)
    }
  | . + { cache_creation_5m_input_tokens: (.cache_creation_input_tokens - .cache_creation_1h_input_tokens) }
  | . + {
      cost_usd: {
        input: (.input_tokens * $price_in / 1e6),
        cache_write: ((.cache_creation_5m_input_tokens * $price_in * 1.25
                        + .cache_creation_1h_input_tokens * $price_in * 2) / 1e6),
        cache_read: (.cache_read_input_tokens * $price_in * 0.1 / 1e6),
        output: (.output_tokens * $price_out / 1e6)
      }
    }
  | .cost_usd.total = (.cost_usd.input + .cost_usd.cache_write + .cost_usd.cache_read + .cost_usd.output)
' "$FILE"
