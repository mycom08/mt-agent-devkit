"""Open release-owned change metadata without losing shared deployment support."""
import argparse
import json
from pathlib import Path


def next_snapshot(data, snapshot):
    latest = next(iter(data.values()))
    entry = {"new": [], "modified": [], "removed": [], "descriptions": {}}
    if isinstance(latest, dict) and "deployment" in latest:
        bridges = list(latest.get("files", []))
        entry.update(deployment=latest["deployment"], files=bridges, modified=bridges,
                     descriptions={path: "Compatible legacy sync bridge; shared payload declared separately." for path in bridges},
                     checksums={path: latest["checksums"][path] for path in bridges})
    return {snapshot: entry, **data}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot")
    parser.add_argument("--changes", default="changes.json")
    args = parser.parse_args()
    path = Path(args.changes)
    path.write_text(json.dumps(next_snapshot(json.loads(path.read_text(encoding="utf-8")), args.snapshot), indent=2) + "\n", encoding="utf-8", newline="\n")
