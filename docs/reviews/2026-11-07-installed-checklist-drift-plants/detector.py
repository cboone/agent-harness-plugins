"""Declare the Bash detector's wait and preserve its streams for the runner."""

from pathlib import Path
import subprocess


raise SystemExit(
    subprocess.run(
        ["bash", "-euo", "pipefail", str(Path(__file__).with_suffix(".bash"))],
        timeout=30,
        check=False,
    ).returncode
)
