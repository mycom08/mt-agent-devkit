#!/usr/bin/env python3
"""Working mirror for the distributed telemetry collector.

The canonical implementation is the target-project template. Delegating keeps
the devkit's active Antigravity workflow executable without duplicating schema
logic that could drift from the script installed into target projects.
"""

from pathlib import Path
import runpy


runpy.run_path(str(Path(__file__).resolve().parents[4] / ".claude/agents/templates/scripts/telemetry.py"), run_name="__main__")
