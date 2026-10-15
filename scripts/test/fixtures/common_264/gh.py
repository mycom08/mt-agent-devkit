import json,sys
from pathlib import Path
p=Path("gh-events.jsonl")
with p.open("a",encoding="utf-8") as f:f.write(json.dumps(sys.argv[1:])+"\n")
print("{\"state\":\"mocked\"}")
