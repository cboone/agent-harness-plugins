# /// script
# requires-python = ">=3.13"
# ///
"""Run the fixture detectors with a declared supervised wait."""
import os
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "plugins/plant-defects/scripts"))
import checked_core as core

DETECTOR_SECONDS = 60
MODES = {
    "main": ("check", "relative", "supervisor-error", "cancel", "final-drain",
             "follower-error", "final-reader-error", "escaped-message"),
    "startup": ("follow", "partial-startup"),
}


def run_mode(mode):
    deadline = core.deadline_after(DETECTOR_SECONDS)
    result = core.command(
        ["bash", "tests/fixtures/measure-codex-failure-launches", mode],
        ROOT, core.remaining(deadline, "notify fixture detector"))
    return relay_result(result)


def relay_result(result):
    if (not isinstance(result, dict)
            or type(result.get("exit_code")) is not int
            or not all(isinstance(result.get(stream), str) for stream in ("stdout", "stderr"))):
        raise ValueError("invalid notify detector capture")
    sys.stdout.write(result["stdout"])
    sys.stdout.flush()
    sys.stderr.write(result["stderr"])
    sys.stderr.flush()
    if not core.valid_step(result):
        raise ValueError("incomplete notify detector capture: " + repr(result))
    return result["exit_code"] if result["exit_code"] in (0, 1) else 2


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in MODES:
        return 2
    group = sys.argv[1]
    os.environ["REPO_ROOT"] = str(ROOT)
    os.environ["CODEX_FAILURE_WATCHER_BIN"] = str(ROOT / "plugins/notify/scripts/watch-codex-failures")
    print("launch instrument started" if group == "main" else "startup boundary instrument started", flush=True)
    try:
        with core.root_supervision():
            for mode in MODES[group]:
                code = run_mode(mode)
                if code:
                    return code
        return 0
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print("Notify detector supervision failed: " + core.failure_cause(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
