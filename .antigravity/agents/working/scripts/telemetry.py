"""Generated compatibility wrapper; edit the canonical source instead."""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).resolve().parents[4] / ".mt-agent-devkit/scripts/telemetry.py"), run_name="__main__")
