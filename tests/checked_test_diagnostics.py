"""Keep captured runner output out of restart assertion diagnostics."""

import json
import os
from pathlib import Path
import tempfile


def restart_diagnostic(result, *, retain=False, fixture=None):
    if not isinstance(result, dict):
        return type(result).__name__
    metadata = {key: value for key in ("exit_code", "timed_out", "reaped", "output_truncated")
                if (value := result.get(key)) is None or type(value) in (bool, int)}
    if retain:
        base = os.environ.get("CHECKED_PLANT_DIAGNOSTICS_DIR")
        if base is not None:
            Path(base).mkdir(parents=True, exist_ok=True)
        directory = Path(tempfile.mkdtemp(prefix="checked-plant-diagnostic-", dir=base))
        destination = directory / "result.json"
        destination.write_text(json.dumps(dict(fixture=fixture, result=result), indent=2) + "\n")
        metadata["result_file"] = str(destination)
    return repr(metadata)
