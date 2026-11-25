"""Check that verdict compatibility data accounts for every tracked plant file."""

import json
import os
from pathlib import Path
import subprocess
import sys


def main():
    data = json.loads(Path("tests/data/checked-verdict-compatibility.json").read_text())
    listed = {row["manifest"] for row in data["rows"]} | set(data["historical_records"])
    paths = subprocess.check_output(["git", "ls-files", "-z", "--", "*-plants.json"])
    tracked = set(os.fsdecode(paths).split("\0")) - {""}
    for path in sorted(tracked - listed):
        print(f"Unlisted plant manifest: {path}", file=sys.stderr)
    for path in sorted(listed - tracked):
        print(f"Missing tracked plant manifest: {path}", file=sys.stderr)
    if tracked != listed:
        return 1
    print("Plant inventory matches verdict compatibility data")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
