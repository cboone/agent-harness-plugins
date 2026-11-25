"""Content-based discovery shared by the plant compatibility checks."""

import json
import os
from pathlib import Path


def is_manifest(value):
    return isinstance(value, dict) and {"green", "check", "variants"} <= value.keys()


def discover_manifests(root):
    paths = set()
    for directory, children, files in os.walk(root):
        children[:] = [name for name in children if name not in ("node_modules", "dist", ".agents", ".git")]
        for name in files:
            if not name.endswith(".json"):
                continue
            path = Path(directory) / name
            try:
                manifest = json.loads(path.read_text())
            except (UnicodeError, ValueError):
                continue
            if is_manifest(manifest):
                paths.add(path.relative_to(root).as_posix())
    return paths
