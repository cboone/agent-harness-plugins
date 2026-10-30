"""Manual regression: uv run --no-project tests/fixtures/plant-defects-bytecode.py."""

import os
from pathlib import Path
import subprocess
import sys
import tempfile


with tempfile.TemporaryDirectory(prefix="plant-bytecode-") as directory:
    root = Path(directory)
    source = root / "subject.py"
    cache = root / "__pycache__"
    env = dict(os.environ)
    for key in ("PYTHONDONTWRITEBYTECODE", "PYTHONPYCACHEPREFIX", "PYTHONPATH"):
        env.pop(key, None)

    def write(value):
        source.write_text(f"value = {value}\n", encoding="utf-8")
        os.utime(source, (1700000000, 1700000000))

    def read(**settings):
        return subprocess.check_output(
            [sys.executable, "-S", "-c", "import subject; print(subject.value)"],
            cwd=root, env=env | settings, text=True,
        ).strip()

    def clear():
        for bytecode in cache.iterdir():
            bytecode.unlink()
        cache.rmdir()

    write(1)
    planted_stat = source.stat()
    assert read() == "1"
    write(0)
    assert source.stat().st_size == planted_stat.st_size
    assert source.stat().st_mtime == planted_stat.st_mtime
    assert read(PYTHONDONTWRITEBYTECODE="1") == "1", "control must load stale code"
    clear()
    assert read(PYTHONDONTWRITEBYTECODE="1") == "0"
    assert not cache.exists()
    for settings in ({"PYTHONDONTWRITEBYTECODE": "1"},
                     {"PYTHONPYCACHEPREFIX": str(root / "isolated")}):
        write(1)
        assert read(**settings) == "1"
        write(0)
        assert not cache.exists()
        assert read(PYTHONDONTWRITEBYTECODE="1") == "0"
        if "PYTHONPYCACHEPREFIX" in settings:
            assert read(**settings) == "1", "reusing the plant prefix must be stale"
            assert read(PYTHONPYCACHEPREFIX=str(root / "restored")) == "0"
    print("stale-bytecode control, cleanup and both prevention options passed")
