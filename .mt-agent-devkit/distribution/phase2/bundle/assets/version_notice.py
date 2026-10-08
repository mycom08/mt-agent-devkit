"""Best-effort release notice from verified shared receipt, never a migration."""
import json
from pathlib import Path
import re
import subprocess


def notice(root):
    root = Path(root)
    try:
        receipt = json.loads((root / ".mt-agent-devkit/install-receipt.json").read_text())
        if receipt["source"]["kind"] != "release":
            return {}
        current = receipt["source"]["tag"]
        sources = []
        for name in ("CLAUDE.md", "AGENTS.md"):
            if (root / name).exists():
                sources.extend(re.findall(r"\*\*Devkit source:\*\*\s+(https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)", (root / name).read_text()))
        if not sources:
            return {}
        result = subprocess.run(["git", "ls-remote", "--tags", "--refs", sources[0].rstrip("/") + ".git"], capture_output=True, text=True, timeout=10, check=True)
        tags = re.findall(r"refs/tags/(v\d+\.\d+\.\d+)\b", result.stdout)
        latest = max(tags, key=lambda tag: tuple(map(int, tag[1:].split("."))))
        return {"systemMessage": "Devkit update available: " + current + " -> " + latest + ". Run sync devkit."} if latest != current else {}
    except (OSError, ValueError, KeyError, subprocess.SubprocessError):
        return {}


if __name__ == "__main__":
    print(json.dumps(notice(Path.cwd())))
