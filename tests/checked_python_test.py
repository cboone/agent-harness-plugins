"""Exercise uv's interpreter selection for both shipped runner scripts."""

import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest


class PythonSelectionTests(unittest.TestCase):
    def test_python_selection(self):
        scripts = Path(os.environ["CHECKED_PLANT_BIN"]).parent
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".python-version").write_text("3.12\n")
            shutil.copy2(scripts / "checked_core.py", root)
            for name in ("checked-plant", "checked-gate"):
                with self.subTest(runner=name):
                    shutil.copy2(scripts / name, root)
                    result = subprocess.run(
                        ["uv", "run", "--verbose", "--script", name, "--help"],
                        cwd=root, capture_output=True, text=True, timeout=120,
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertIn(f"usage: {name}", result.stdout)
                    version = re.search(
                        r"Using Python (\d+)\.(\d+)\.(\d+) interpreter", result.stderr,
                    )
                    self.assertIsNotNone(version, result.stderr)
                    self.assertGreaterEqual(
                        tuple(map(int, version.groups())), (3, 13, 0),
                        f"{name}: selected Python below 3.13",
                    )
                    print(f"{name}: Python {version.group(0).split()[2]}; startup passed")


if __name__ == "__main__":
    unittest.main()
