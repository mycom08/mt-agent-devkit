#!/usr/bin/env python3
"""Build isolated target-layout prototype assets without editing legacy sources."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import shutil
import tempfile
import subprocess


def neutral(text):
    text = text.replace("{{AGENT_DIR_PREFIX}}/agents/templates/", ".claude/agents/templates/")
    for folder in ("memory", "working-record", "retros", "tmp", "internal", "docs"):
        text = text.replace("{{AGENT_DIR_PREFIX}}/agents/" + folder, "{RUNTIME_ROOT}/" + folder)
        text = text.replace(".claude/agents/" + folder, "{RUNTIME_ROOT}/" + folder)
    for folder in ("rules", "workflows", "context", "instructions", "scripts"):
        text = text.replace("{{AGENT_DIR_PREFIX}}/agents/" + folder, ".mt-agent-devkit/" + folder)
    text = re.sub(r"\{\{AGENT_DIR_PREFIX\}\}/agents/([a-z_]+_instructions\.md)", r".mt-agent-devkit/instructions/\1", text)
    text = text.replace("{{AGENT_DIR_PREFIX}}/agents/orchestrator_instructions.md", ".mt-agent-devkit/instructions/orchestrator_instructions.md")
    text = text.replace("{{AGENT_DIR_PREFIX}}/agents/", "{RUNTIME_ROOT}/")
    text = text.replace("{{AGENT_DIR_PREFIX}}", "{PROVIDER_ROOT}")
    text = text.replace("{{ROOT_FILE}}", "{ENTRYPOINT}").replace("{{AGENT_CLI_NAME}}", "selected provider")
    # Generation examples contain project inputs resolved by their own workflow,
    # rather than installation tokens. Keep them explicit as runtime inputs.
    text = re.sub(r"\{\{(PROJECT_NAME|PROJECT_DESCRIPTION|DEVKIT_SOURCE_URL|DEVKIT_VERSION)\}\}", r"{\1}", text)
    text = text.replace("`SendMessage`", "the selected adapter's resume operation").replace("SendMessage", "the selected adapter's resume operation").replace("agentId", "session_handle")
    text = re.sub(r"## 6\. Shell Command Rules.*?(?=\n## Version)", "## 6. Shell Command Rules — Permissions and Tool Choice\n\nBefore the first command, read the selected provider adapter from the worker packet. Follow its actual shell/tool/permission/completion procedure; another provider's allow-list never applies. Use temporary body files for multiline GitHub text and remove them after completion. Missing adapter/bindings block state access.\n\n---\n", text, flags=re.S)
    text = re.sub(r"\*\*model: (sonnet|opus|haiku)\*\*", lambda m: "**policy: " + {"sonnet": "standard", "opus": "design-review", "haiku": "closure"}[m[1]] + "**", text)
    lines = []
    for line in text.splitlines():
        if "For a fresh Claude Code `Agent` result" in line:
            line = "- Collect sanitized stage telemetry through the selected provider adapter; unavailable usage remains null. Do not estimate usage or import another provider's transcripts."
        lines.append(line)
    return "\n".join(lines) + "\n"


def build(root, destination):
    root, destination = Path(root), Path(destination)
    implementation = root / ".mt-agent-devkit/distribution/phase2"
    destination.mkdir(parents=True, exist_ok=True)
    assets, files = [], []

    def asset(identifier, content, kind="template"):
        # Distribution text bytes are canonical UTF-8/LF so checked-in blob
        # bytes and release hashes agree across Windows and Linux checkouts.
        content = ("\n".join(line.rstrip() for line in content.decode("utf-8-sig").replace("\r\n", "\n").splitlines()) + "\n").encode("utf-8")
        path = "assets/" + identifier.replace(":", "_").replace("/", "_")
        (destination / path).parent.mkdir(parents=True, exist_ok=True)
        (destination / path).write_bytes(content)
        assets.append({"id": identifier, "path": path, "sha256": hashlib.sha256(content).hexdigest(), "bytes": len(content), "kind": kind})
        return identifier

    def entry(identifier, source_ids, target, profiles=("repo",), owner="shared", ownership="managed", renderer="copy", modes=("github", "strict"), providers=("claude", "antigravity", "codex"), phase="content"):
        files.append({"id": identifier, "sources": source_ids, "destination": target, "owner": owner, "ownership": ownership, "profiles": list(profiles), "modes": list(modes), "providers": list(providers), "renderer": renderer, "legacy_paths": [], "phase": phase, "required": True})

    templates = root / ".claude/agents/templates"
    for folder in ("rules", "instructions"):
        for source in sorted((templates / folder).glob("*_template.md")):
            name = source.name.replace("_template", "")
            identifier = folder + "/" + name
            content = neutral(source.read_text(encoding="utf-8-sig"))
            if name == "Agent_Common_Bootstrap.md":
                content = content.replace("## 1. Pre-Work Sequence", "## 1. Pre-Work Sequence\n\nBefore state access require concrete selected PROVIDER_ROOT, RUNTIME_ROOT and COMMAND_ROOT plus adapter path. Missing or foreign bindings block; never search another provider's records.")
            if folder == "instructions":
                content += "\nBefore state access, require the selected adapter path and concrete PROVIDER_ROOT/RUNTIME_ROOT/COMMAND_ROOT from the orchestrator packet. Never discover another provider's state.\n"
            aid = asset(identifier, content.encode())
            entry(identifier, [aid], ".mt-agent-devkit/" + identifier, ownership="project_adapted" if folder == "instructions" else "managed")
    for source in sorted((templates / "shared/workflows").glob("*_Shared_template.md")):
        name = source.name.replace("_Shared_template", "")
        common = asset("workflow_shared/" + name, neutral(source.read_text(encoding="utf-8-sig")).encode())
        for mode in ("github", "strict"):
            variant = templates / mode / "workflows" / name.replace(".md", "_template.md")
            aid = asset("workflow_" + mode + "/" + name, neutral(variant.read_text(encoding="utf-8-sig")).encode())
            entry("workflow_" + mode + "/" + name, [common, aid], ".mt-agent-devkit/workflows/" + name, modes=(mode,), renderer="shared_mode")
    common = asset("orchestrator_shared", neutral((templates / "shared/orchestrator_instructions_shared_template.md").read_text(encoding="utf-8-sig")).encode())
    for mode in ("github", "strict"):
        aid = asset("orchestrator_" + mode, neutral((templates / mode / "orchestrator_instructions_template.md").read_text(encoding="utf-8-sig")).encode())
        entry("orchestrator_" + mode, [common, aid], ".mt-agent-devkit/instructions/orchestrator_instructions.md", renderer="shared_mode", modes=(mode,))
    for source in sorted((templates / "scripts").iterdir()):
        if source.is_file():
            content = source.read_bytes()
            if source.name == "check_devkit_version.sh":
                content = b'#!/usr/bin/env bash\npython3 "$(dirname -- "$0")/version_notice.py"\n'
            elif source.name == "check_devkit_version.ps1":
                content = b"& python (Join-Path $PSScriptRoot 'version_notice.py')\n"
            elif source.name == "branch_preflight.py":
                text = content.decode("utf-8-sig").replace("RUNTIME_PREFIXES = (", "RUNTIME_PREFIXES = (\n" + "".join('    \".codex/agents/' + folder + '/\",\n' for folder in ("memory", "working-record", "retros", "tmp", "internal")))
                content = text.encode()
            aid = asset("scripts/" + source.name, content, "script")
            entry("scripts/" + source.name, [aid], ".mt-agent-devkit/scripts/" + source.name, profiles=("repo", "project_root"))
    # Repo/root adaptive inputs are exclusive; existing project content is preserved.
    for profile, source in (("repo", "context/Project_Priming_template.md"), ("project_root", "context/Project_Root_Priming_template.md")):
        aid = asset("priming_" + profile, neutral((templates / source).read_text(encoding="utf-8-sig")).encode())
        entry("priming_" + profile, [aid], ".mt-agent-devkit/context/Project_Priming.md", profiles=(profile,), ownership="project_owned", renderer="approved_adaptation")
    index = asset("document_index", neutral((templates / "context/Document_Index_template.md").read_text(encoding="utf-8-sig")).encode())
    entry("document_index", [index], ".mt-agent-devkit/context/Document_Index.md", ownership="project_owned", renderer="approved_adaptation")
    for name in ("Build_Software_Project_Workflow", "Sync_Devkit_Project_Workflow"):
        source = implementation / "Sync_Devkit_Workflow_template.md" if name.startswith("Sync") else templates / "workflows" / (name + "_template.md")
        aid = asset(name, neutral(source.read_text(encoding="utf-8-sig")).encode())
        entry(name, [aid], ".mt-agent-devkit/workflows/" + name + ".md", profiles=("project_root",))
    for profile in ("repo", "project_root"):
        source = templates / ("shared/Repo_Root_Shared_template.md" if profile == "repo" else "Project_Root_template.md")
        aid = asset("root_" + profile, neutral(source.read_text(encoding="utf-8-sig")).encode())
        for entrypoint, providers in (("CLAUDE.md", ("claude",)), ("AGENTS.md", ("antigravity", "codex"))):
            # One AGENTS owner even when both consumers are selected; provider list is descriptive.
            entry("root_" + profile + "/" + entrypoint, [aid], entrypoint, profiles=(profile,), owner="project", ownership="project_adapted", renderer="managed_sections", providers=providers, phase="discovery")
    for provider in ("claude", "antigravity", "codex"):
        for name in ("Provider_Adapter.md", "capabilities.json"):
            aid = asset(provider + "/" + name, (root / ("." + provider) / "harness" / name).read_bytes(), "adapter")
            entry(provider + "/" + name, [aid], "." + provider + "/harness/" + name, profiles=("repo", "project_root"), owner="selected_provider", providers=(provider,))
        bound = {"PROVIDER_ROOT": "." + provider, "RUNTIME_ROOT": "." + provider + "/agents", "COMMAND_ROOT": "." + provider + "/agents"}
        aid = asset(provider + "/state-paths.json", (json.dumps(bound, indent=2) + "\n").encode(), "contract")
        entry(provider + "/state-paths.json", [aid], "." + provider + "/harness/state-paths.json", profiles=("repo", "project_root"), owner="selected_provider", providers=(provider,))
        for role in ("Developer", "Technical_Lead", "QA", "Product_Owner", "Business_Analyst", "UI_UX_Designer"):
            for folder, suffix in (("memory", "Memory"), ("working-record", "Working_Record")):
                content = "# " + role + " " + suffix + "\n\nNo entries yet.\n"
                if suffix == "Memory" and role in ("Developer", "Technical_Lead", "QA"):
                    content = "# " + role + " Memory\n\n## Standing Checks\n\nNone yet.\n\n## Keyword Index\n\nNone yet.\n\n## Troubleshooting Facts\n\nNone yet.\n"
                aid = asset(provider + "/" + role + suffix, content.encode())
                entry(provider + "/" + role + suffix, [aid], "." + provider + "/agents/" + folder + "/" + role + "_" + suffix + ".md", owner="selected_provider", ownership="runtime_seed", renderer="create_if_absent", providers=(provider,))
            if role in ("Developer", "Technical_Lead", "QA"):
                aid = asset(provider + "/" + role + "Archive", ("# " + role + " Memory Archive\n\n## Stored Facts\n\nNone yet.\n").encode())
                entry(provider + "/" + role + "Archive", [aid], "." + provider + "/agents/memory/" + role + "_Memory_Archive.md", owner="selected_provider", ownership="runtime_seed", renderer="create_if_absent", providers=(provider,))
            if provider == "claude":
                slug = role.lower()
                content = "---\nname: " + slug + "\ndescription: Shared " + role + " role\n---\n\nRead .mt-agent-devkit/instructions/" + slug + "_instructions.md before work. Read the selected adapter supplied by the orchestrator and preserve concrete .claude/agents runtime bindings.\n"
                aid = asset(provider + "/wrapper/" + slug, content.encode(), "adapter")
                entry(provider + "/wrapper/" + slug, [aid], ".claude/agents/" + slug + ".md", owner="selected_provider", providers=(provider,), phase="discovery")
        aid = asset(provider + "/story_counter", b"0\n")
        entry(provider + "/story_counter", [aid], "." + provider + "/agents/docs/story_counter.txt", owner="selected_provider", ownership="runtime_seed", renderer="create_if_absent", providers=(provider,), modes=("strict",))
    for name in ("deployment.py", "provider_context.py", "version_notice.py", "migration.py", "sync.py", "lifecycle.py", "lifecycle.sh", "lifecycle.ps1", "build_bundle.py"):
        aid = asset(name, (implementation / name).read_bytes(), "script")
        entry(name, [aid], ".mt-agent-devkit/scripts/" + name, profiles=("repo", "project_root"))
    aid = asset("Sync_Devkit_Workflow", (implementation / "Sync_Devkit_Workflow_template.md").read_bytes())
    entry("Sync_Devkit_Workflow", [aid], ".mt-agent-devkit/workflows/Sync_Devkit_Workflow.md")
    aid = asset("Workflow_Guide", neutral((templates / "workflows/Workflow_Guide_template.md").read_text(encoding="utf-8-sig")).encode())
    entry("Workflow_Guide", [aid], ".mt-agent-devkit/workflows/Workflow_Guide.md")
    aid = asset("Gitignore", b"# Managed runtime ignores\n")
    entry("Gitignore", [aid], ".gitignore", profiles=("repo", "project_root"), owner="project", ownership="project_adapted", renderer="approved_adaptation")
    for name in ("read_section.py",):
        aid = asset(name, (root / ".mt-agent-devkit/scripts" / name).read_bytes(), "script")
        entry(name, [aid], ".mt-agent-devkit/scripts/" + name, profiles=("repo", "project_root"))
    aid = asset("Read_Section.md", (root / ".mt-agent-devkit/contracts/Read_Section.md").read_bytes(), "contract")
    entry("Read_Section", [aid], ".mt-agent-devkit/contracts/Read_Section.md", profiles=("repo", "project_root"))
    contract = b"# Target Provider Contract\n\nRead project priming for neutral tasks. Before workflows inspect actual enabled tools and call provider_context.select_provider with target root and explicit tool identities. Load exactly its selected adapter; missing/ambiguous mappings block before state writes or spawning. Pass concrete preserved state bindings to every role. Independent implementer, TL review, QA and PO gates remain mandatory. Provider directories never prove native discovery. Runtime remains provider-local, never merged. One shared mode/version; mixed modes/nonterminal legacy workflows block migration. Follow selected adapter for lifecycle, permissions, CI completion and unavailable telemetry.\n"
    aid = asset("Provider_Contract.md", contract, "contract")
    entry("Provider_Contract", [aid], ".mt-agent-devkit/contracts/Provider_Contract.md", profiles=("repo", "project_root"))
    aid = asset("Compatibility_Version", b"{{DEVKIT_VERSION}}\n")
    entry("Compatibility_Version", [aid], "{{RUNTIME_ROOT}}/devkit_version.txt", profiles=("repo", "project_root"), owner="selected_provider", ownership="provider_config", renderer="tokens", phase="compatibility")
    retirements = []
    for existing in list(files):
        target = existing["destination"]
        if not target.startswith((".mt-agent-devkit/rules/", ".mt-agent-devkit/workflows/")):
            continue
        for provider in ("claude", "antigravity"):
            for profile in existing["profiles"]:
                if profile not in ("repo", "project_root"): continue
                for mode in existing["modes"]:
                    legacy = "." + provider + "/agents/" + target.removeprefix(".mt-agent-devkit/")
                    identifier = "retire/" + provider + "/" + profile + "/" + mode + "/" + existing["id"]
                    root_id = "root_" + profile + "/" + ("CLAUDE.md" if provider == "claude" else "AGENTS.md")
                    entry(identifier, [], legacy, profiles=(profile,), owner="selected_provider", providers=(provider,), modes=(mode,), phase="retirement")
                    files[-1]["required"] = False
                    retirements.append({"logical_id": identifier, "path": legacy, "after_verified_ids": [existing["id"], root_id]})
    manifest = {"schema_version": 1, "layout_version": 2, "minimum_python": "3.10", "profiles": ["repo", "project_root"], "assets": assets, "files": files, "legacy_support": {"versions": ["0.1.48", "0.1.49", "0.1.50"], "providers": ["claude", "antigravity"], "modes": ["github", "strict"], "retirements": retirements}}
    (destination / "deployment.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--check", action="store_true", help="Rebuild in isolation and reject committed artifact drift")
    args = parser.parse_args()
    if args.check:
        with tempfile.TemporaryDirectory() as folder:
            value = build(args.root, folder)
            expected = {p.relative_to(folder).as_posix(): p.read_bytes() for p in Path(folder).rglob("*") if p.is_file()}
            actual = {p.relative_to(args.output).as_posix(): p.read_bytes() for p in Path(args.output).rglob("*") if p.is_file()}
            if actual != expected: parser.exit(2, "distribution artifact drift; regenerate before packaging\n")
    else:
        value = build(args.root, args.output)
    print(json.dumps({"assets": len(value["assets"]), "files": len(value["files"]), "status": "mechanical artifact; native support remains evidence gated"}))
