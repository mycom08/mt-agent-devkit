#!/usr/bin/env python3
"""Working mirror for the distributed project-settings resolver.

The canonical implementation is the active shared distribution. Delegating keeps
the devkit's own orchestrator on the same resolution rules as target projects.
"""

from pathlib import Path
import runpy


runpy.run_path(str(Path(__file__).resolve().parents[1] / "distribution/phase2/templates/scripts/project_settings.py"), run_name="__main__")
