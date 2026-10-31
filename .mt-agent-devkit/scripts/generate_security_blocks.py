"""Copy agent-security parts A and B into the Common generated blocks.

The skill at .mt-agent-devkit/skills/agent-security/SKILL.md is the only owner.
Each Common target holds the part bodies between BEGIN/END markers; the Phase 2
skill template is a byte-for-byte copy of the canonical skill. Part C is never
inlined. Use --check in CI: any drift or missing marker exits 1.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
SKILL = ".mt-agent-devkit/skills/agent-security/SKILL.md"
SKILL_TEMPLATE = ".mt-agent-devkit/distribution/phase2/templates/skills/agent-security/SKILL_template.md"
TEMPLATES = ".mt-agent-devkit/distribution/phase2/templates/rules/"
TARGETS = (
    ".mt-agent-devkit/rules/Agent_Common_Core.md",
    ".mt-agent-devkit/rules/Agent_Common_Bootstrap.md",
    TEMPLATES + "Agent_Common_Core_template.md",
    TEMPLATES + "Agent_Common_Bootstrap_template.md",
)
PARTS = ("A", "B")


def begin(part: str) -> str:
    return f"<!-- BEGIN GENERATED agent-security part {part}: edit {SKILL}, then regenerate -->\n"


def end(part: str) -> str:
    return f"<!-- END GENERATED agent-security part {part} -->\n"


def part_body(skill: str, part: str) -> str:
    """Return one part's body without its heading or surrounding blank lines."""
    match = re.search(rf"^## {part}\. [^\n]*\n(.*?)(?=^## |\Z)", skill, re.M | re.S)
    if not match:
        raise ValueError(f"agent-security part {part} heading missing")
    return match.group(1).strip("\n") + "\n"


def render(text: str, skill: str) -> str:
    """Replace every part block in text; raise when a block is missing or duplicated."""
    for part in PARTS:
        pattern = re.compile(re.escape(begin(part)) + r".*?" + re.escape(end(part)), re.S)
        if len(pattern.findall(text)) != 1:
            raise ValueError(f"expected exactly one generated block for part {part}")
        text = pattern.sub(lambda _: begin(part) + part_body(skill, part) + end(part), text)
    return text


def findings(root: Path = ROOT, write: bool = False) -> list[str]:
    errors = []
    skill = (root / SKILL).read_text(encoding="utf-8")
    template = root / SKILL_TEMPLATE
    if write:
        template.parent.mkdir(parents=True, exist_ok=True)
        template.write_text(skill, encoding="utf-8", newline="\n")
    elif not template.is_file() or template.read_text(encoding="utf-8") != skill:
        errors.append(f"{SKILL_TEMPLATE}: differs from {SKILL}")
    for relative in TARGETS:
        path = root / relative
        text = path.read_text(encoding="utf-8")
        try:
            expected = render(text, skill)
        except ValueError as error:
            errors.append(f"{relative}: {error}")
            continue
        if expected != text:
            if write:
                path.write_text(expected, encoding="utf-8", newline="\n")
            else:
                errors.append(f"{relative}: generated agent-security block drift")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    errors = findings(write=not args.check)
    for error in errors:
        print(f"[ERROR] {error}")
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
