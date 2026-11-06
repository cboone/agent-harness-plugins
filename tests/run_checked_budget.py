"""Enforce the declared document deadline, reserving the shared cleanup margin."""

import json
import os
from pathlib import Path
import sys
import subprocess

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(os.environ["CHECKED_PLANT_BIN"]).parent))
import checked_core as core

policy = json.loads((Path(__file__).parent / "data/checked-timeout-budgets.json").read_text())
document, *argv = sys.argv[1:]
row = policy["documents"][document]
if row.get("behavior"):
    os.environ["CHECKED_PLANT_BEHAVIOR_ONLY"] = "1"
elif "variants" in row:
    os.environ["CHECKED_PLANT_GUARD_PART"] = str(row["partition"])
elif "gate_variants" in row:
    os.environ["CHECKED_GATE_GUARD_PART"] = str(row["partition"])
result, code = None, 1
try:
    with core.root_supervision():
        result = core.command(argv, Path.cwd(), row.get("limit", policy["limit"]))
        sys.stdout.write(result["stdout"])
        sys.stderr.write(result["stderr"])
        if not core.valid_step(result):
            print("Document supervision failed: " + repr(result), file=sys.stderr)
        code = 0 if core.valid_step(result) and result["exit_code"] == 0 else 1
except (OSError, ValueError, subprocess.SubprocessError) as error:
    phase = "execution" if result is None else "finalization"
    print("Document " + phase + " failed: " + core.failure_cause(error), file=sys.stderr)
    code = 1
raise SystemExit(code)
