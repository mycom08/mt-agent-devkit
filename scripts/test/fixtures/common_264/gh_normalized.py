"""Explicit ST-000264 recording-only serialization amendment; no GitHub calls."""
import json
import sys
from pathlib import Path

with Path('gh-events.jsonl').open('a', encoding='utf-8', newline='\n') as stream:
    stream.write(json.dumps(sys.argv[1:]) + '\n')
print(json.dumps({'state': 'mocked'}))
