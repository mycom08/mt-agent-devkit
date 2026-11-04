"""Copy marked common-skill parts into the generated blocks of the kept Common files.

A skill marks each copyable part with `<!-- part: <name> -->` ... `<!-- /part: <name> -->`;
the part body is the text between the markers without surrounding blank lines. BLOCKS is
the mapping table, one row per generated block: skill, part, layer, target file, block.
Internal targets take text only from the internal skill; Phase 2 targets take text only
from the Phase 2 skill template. COPIES names Phase 2 skill templates that are a
byte-for-byte copy of their internal skill (written first, then read as the Phase 2 source).

Without --check the blocks and copies are rewritten. With --check (CI) the script exits 1
when a block differs from its part, a block is missing or duplicated, a target holds a
generated block the table does not name, a mapped part is missing, a part is marked twice,
or a marked part has no target.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import re
from typing import NamedTuple

ROOT = Path(__file__).resolve().parents[2]
INTERNAL_SKILLS = ".mt-agent-devkit/skills"
PHASE2_SKILLS = ".mt-agent-devkit/distribution/phase2/templates/skills"
SOURCES = {
    "internal": INTERNAL_SKILLS + "/{skill}/SKILL.md",
    "phase2": PHASE2_SKILLS + "/{skill}/SKILL_template.md",
}
RULES = ".mt-agent-devkit/rules/"
TEMPLATES = ".mt-agent-devkit/distribution/phase2/templates/rules/"
# Layer-neutral skills (ST-000310): the Phase 2 template is the internal skill, byte for byte.
COPIES = ("agent-security", "shell-rules", "retro", "retro-contribution", "credential-gate")


class Block(NamedTuple):
    skill: str
    part: str
    layer: str
    target: str
    block: str


def row(skill: str, part: str, layer: str, target: str) -> Block:
    return Block(skill, part, layer, target, f"{skill} part {part}")


BLOCKS: tuple[Block, ...] = (
    # agent-security (ST-000287): internal and Phase 2 rows.
    row("agent-security", "A", "internal", RULES + "Agent_Common_Core.md"),
    row("agent-security", "B", "internal", RULES + "Agent_Common_Core.md"),
    row("agent-security", "A", "internal", RULES + "Agent_Common_Bootstrap.md"),
    row("agent-security", "B", "internal", RULES + "Agent_Common_Bootstrap.md"),
    row("agent-security", "A", "phase2", TEMPLATES + "Agent_Common_Core_template.md"),
    row("agent-security", "B", "phase2", TEMPLATES + "Agent_Common_Core_template.md"),
    row("agent-security", "A", "phase2", TEMPLATES + "Agent_Common_Bootstrap_template.md"),
    row("agent-security", "B", "phase2", TEMPLATES + "Agent_Common_Bootstrap_template.md"),
    # Common Bootstrap (design 7b).
    row("pre-work", "read-order", "internal", RULES + "Agent_Common_Bootstrap.md"),
    row("working-record", "format", "internal", RULES + "Agent_Common_Bootstrap.md"),
    row("pre-work", "resume", "internal", RULES + "Agent_Common_Bootstrap.md"),
    row("token-efficiency", "conventions", "internal", RULES + "Agent_Common_Bootstrap.md"),
    row("shell-rules", "rules", "internal", RULES + "Agent_Common_Bootstrap.md"),
    row("retro", "detection", "internal", RULES + "Agent_Common_Bootstrap.md"),
    row("retro-contribution", "orchestration", "internal", RULES + "Agent_Common_Bootstrap.md"),
    # Common On-Demand.
    row("agent-memory", "facts", "internal", RULES + "Agent_Common_Read_On_Demand.md"),
    row("troubleshooting", "format", "internal", RULES + "Agent_Common_Read_On_Demand.md"),
    row("troubleshooting", "protocol", "internal", RULES + "Agent_Common_Read_On_Demand.md"),
    row("retro-contribution", "writing", "internal", RULES + "Agent_Common_Read_On_Demand.md"),
    row("handoff", "state", "internal", RULES + "Agent_Common_Read_On_Demand.md"),
    row("credential-gate", "gate", "internal", RULES + "Agent_Common_Read_On_Demand.md"),
    row("agent-memory", "two-tier", "internal", RULES + "Agent_Common_Read_On_Demand.md"),
    # Live Common modules (B4) and the Core route.
    row("shell-rules", "safety", "internal", RULES + "Agent_Common_Shell_Safety.md"),
    row("working-record", "format", "internal", RULES + "Agent_Common_Working_Record.md"),
    row("token-efficiency", "conventions", "internal", RULES + "Agent_Common_Core.md"),
    row("retro", "detection", "internal", RULES + "Agent_Common_Core.md"),
    row("retro-contribution", "orchestration", "internal", RULES + "Agent_Common_Core.md"),
    row("agent-memory", "facts", "internal", RULES + "Agent_Common_Memory.md"),
    row("troubleshooting", "format", "internal", RULES + "Agent_Common_Memory.md"),
    row("agent-memory", "two-tier", "internal", RULES + "Agent_Common_Memory.md"),
    row("retro-contribution", "writing", "internal", RULES + "Agent_Common_Retro.md"),
    row("troubleshooting", "protocol", "internal", RULES + "Agent_Common_Troubleshooting.md"),
    row("credential-gate", "gate", "internal", RULES + "Agent_Common_Credential_Gate.md"),
    row("handoff", "state", "internal", RULES + "Agent_Common_Stage_Transition.md"),
)
# Phase 2 (ST-000310): every internal common-skill row, sourced from the Phase 2 skill
# templates into the Phase 2 rule templates. agent-security keeps its own rows above.
BLOCKS += tuple(
    row(item.skill, item.part, "phase2", TEMPLATES + item.target.removeprefix(RULES).replace(".md", "_template.md"))
    for item in BLOCKS if item.layer == "internal" and item.skill != "agent-security"
)

PART = re.compile(r"^<!-- part: ([a-zA-Z0-9-]+) -->\n(.*?)^<!-- /part: \1 -->$", re.M | re.S)
PART_OPEN = re.compile(r"^<!-- part: ([a-zA-Z0-9-]+) -->$", re.M)
GENERATED = re.compile(r"^<!-- BEGIN GENERATED (.+?): edit ", re.M)


def source(skill: str, layer: str) -> str:
    return SOURCES[layer].format(skill=skill)


def edit_path(item: Block) -> str:
    """The file a maintainer edits: the internal skill, also for byte-copied templates."""
    return source(item.skill, "internal" if item.skill in COPIES else item.layer)


def begin(item: Block) -> str:
    return f"<!-- BEGIN GENERATED {item.block}: edit {edit_path(item)}, then regenerate -->\n"


def end(item: Block) -> str:
    return f"<!-- END GENERATED {item.block} -->\n"


def parts(text: str) -> dict[str, str]:
    """Every marked part body; raise ValueError on a duplicated or unclosed part."""
    opened = PART_OPEN.findall(text)
    found = {}
    for name, body in PART.findall(text):
        found[name] = body.strip("\n") + "\n"
    duplicated = sorted({name for name in opened if opened.count(name) > 1})
    if duplicated:
        raise ValueError(f"part marked more than once: {', '.join(duplicated)}")
    unclosed = sorted(set(opened) - set(found))
    if unclosed:
        raise ValueError(f"part not closed: {', '.join(unclosed)}")
    return found


def render(text: str, items: list[Block], bodies: dict[tuple[str, str, str], str]) -> str:
    """Replace each mapped block once; raise ValueError when one is missing or duplicated."""
    for item in items:
        pattern = re.compile(re.escape(begin(item)) + r".*?" + re.escape(end(item)), re.S)
        count = len(pattern.findall(text))
        if count != 1:
            state = "missing" if count == 0 else "duplicated"
            raise ValueError(f"generated block {state}: {item.block}")
        body = bodies[(item.skill, item.layer, item.part)]
        text = pattern.sub(lambda _: begin(item) + body + end(item), text)
    return text


def skill_files(root: Path) -> list[tuple[str, str, Path]]:
    """(skill, layer, path) for every skill file in both layers."""
    found = []
    for layer in SOURCES:
        folder = root / (INTERNAL_SKILLS if layer == "internal" else PHASE2_SKILLS)
        pattern = "*/SKILL.md" if layer == "internal" else "*/SKILL_template.md"
        found.extend((path.parent.name, layer, path) for path in sorted(folder.glob(pattern)))
    return found


def findings(root: Path = ROOT, write: bool = False, blocks: tuple[Block, ...] = BLOCKS) -> list[str]:
    errors = []
    for skill in COPIES:
        internal, template = root / source(skill, "internal"), root / source(skill, "phase2")
        text = internal.read_text(encoding="utf-8")
        if write:
            template.parent.mkdir(parents=True, exist_ok=True)
            template.write_text(text, encoding="utf-8", newline="\n")
        elif not template.is_file() or template.read_text(encoding="utf-8") != text:
            errors.append(f"{source(skill, 'phase2')}: differs from {source(skill, 'internal')}")
    bodies = {}
    for skill, layer, path in skill_files(root):
        relative = path.relative_to(root).as_posix()
        try:
            marked = parts(path.read_text(encoding="utf-8"))
        except ValueError as error:
            errors.append(f"{relative}: {error}")
            continue
        for name, body in marked.items():
            bodies[(skill, layer, name)] = body
            if not any((b.skill, b.layer, b.part) == (skill, layer, name) for b in blocks):
                errors.append(f"{relative}: part {name} has no target")
    for item in blocks:
        if (item.skill, item.layer, item.part) not in bodies:
            errors.append(f"{source(item.skill, item.layer)}: mapped part {item.part} is missing")
    by_target: dict[str, list[Block]] = {}
    for item in blocks:
        by_target.setdefault(item.target, []).append(item)
    for target, items in by_target.items():
        path = root / target
        if not path.is_file():
            errors.append(f"{target}: target file missing")
            continue
        text = path.read_text(encoding="utf-8")
        mapped = {item.block for item in items}
        for name in sorted(set(GENERATED.findall(text)) - mapped):
            errors.append(f"{target}: generated block {name} is not in the mapping table")
        usable = [item for item in items if (item.skill, item.layer, item.part) in bodies]
        try:
            expected = render(text, usable, bodies)
        except ValueError as error:
            errors.append(f"{target}: {error}")
            continue
        if expected != text:
            if write:
                path.write_text(expected, encoding="utf-8", newline="\n")
            else:
                drifted = [item.block for item in usable if begin(item) + bodies[(item.skill, item.layer, item.part)] + end(item) not in text]
                errors.append(f"{target}: generated block differs from its part: {', '.join(drifted)}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    errors = findings(write=not args.check)
    for error in errors:
        print(f"[ERROR] {error}")
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
