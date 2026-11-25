"""Check the full plant manifest inventory against verdict compatibility data."""

import json
from pathlib import Path
import sys

from checked_manifest_discovery import discover_manifests, is_manifest


def main():
    root = Path.cwd()
    data = json.loads((root / "tests/data/checked-verdict-compatibility.json").read_text())
    listed = {row["manifest"] for row in data["rows"]}
    discovered = discover_manifests(root)
    invalid_history = False
    for path in data["historical_records"]:
        try:
            record = json.loads((root / path).read_text())
        except (OSError, ValueError) as error:
            print(f"Invalid historical record: {path}: {error}", file=sys.stderr)
            invalid_history = True
            continue
        if is_manifest(record):
            print(f"Runnable historical record: {path}", file=sys.stderr)
            invalid_history = True
    for path in sorted(discovered - listed):
        print(f"Unlisted plant manifest: {path}", file=sys.stderr)
    for path in sorted(listed - discovered):
        print(f"Missing plant manifest: {path}", file=sys.stderr)
    if discovered != listed or invalid_history:
        return 1
    print("Plant inventory matches verdict compatibility data")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
