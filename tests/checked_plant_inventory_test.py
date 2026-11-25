"""Check the full plant manifest inventory against verdict compatibility data."""

import json
from pathlib import Path
import unittest

from checked_manifest_discovery import discover_manifests, is_manifest


ROOT = Path(__file__).resolve().parents[1]


class InventoryTests(unittest.TestCase):
    def test_plant_inventory_matches_verdict_data(self):
        data = json.loads((ROOT / "tests/data/checked-verdict-compatibility.json").read_text())
        listed = {row["manifest"] for row in data["rows"]}
        discovered = discover_manifests(ROOT)
        problems = []
        for path in data["historical_records"]:
            try:
                record = json.loads((ROOT / path).read_text())
            except (OSError, ValueError) as error:
                problems.append(f"Invalid historical record: {path}: {error}")
                continue
            if is_manifest(record):
                problems.append(f"Runnable historical record: {path}")
        problems.extend(f"Unlisted plant manifest: {path}" for path in sorted(discovered - listed))
        problems.extend(f"Missing plant manifest: {path}" for path in sorted(listed - discovered))
        self.assertFalse(problems, "\n".join(problems))


if __name__ == "__main__":
    unittest.main()
