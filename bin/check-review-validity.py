#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# ///
"""Check shared validity includes and reject ref-valued scope comparisons."""

import argparse
import json
from pathlib import Path
import re
import stat
import subprocess
import sys

REFERENCE = "skills/review-pr-with-codex/references/scope-validity.md"
SOURCE = f"plugins/review-pr-with-codex/{REFERENCE}"
COPIES = (
    "plugins/review-until-clean/skills/review-until-clean/references/scope-validity.md",
    "plugins/review-anti-patterns/skills/review-anti-patterns/references/scope-validity.md",
)
KEY_WORDING = (
    "Compare captured review inputs only.",
    "Ref names and tip movement never decide validity.",
    "Equal captured inputs preserve the round;",
    "changed captured inputs invalidate it.",
    "Do not substitute a comparison of ref names or remote-ref inventories,",
)
LEGACY_WORDING = (
    "a remote ref moved",
    "the base tip and merge base",
    "Anything that touched the tree since, including another session, invalidates the result.",
    "A local edit appearing after the precondition check invalidates the run",
    "Unexpected changes invalidate the result",
    "Staging, unstaging and intent-to-add move it.",
    "The base ref and its tip are informational; unrelated tip advances do not move it.",
    "The index is review input, so git add -N moves the snapshot.",
    "Any snapshot movement resets the pair",
    "Any edit after the review invalidates",
    "the snapshot covers disk and index content",
    "The snapshot covers HEAD, the merge base",
    "A separate snapshot comparison invalidates results",
    "a change after it returned invalidates the round",
    "A snapshot that moved after step 5 invalidates the findings",
    "The snapshot taken as the reviewer returned is the one the round started from",
)


def normalize(text: str) -> str:
    return " ".join(text.replace("`", "").split()).casefold()


def nodes(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from nodes(child)
    elif isinstance(value, list):
        for child in value:
            yield from nodes(child)


def literal_word(node):
    kind = node.get("Type", "Word" if "Parts" in node else None)
    if kind in ("Lit", "SglQuoted"):
        return node["Value"]
    if kind in ("Word", "DblQuoted"):
        parts = [literal_word(part) for part in node.get("Parts", [])]
        return None if None in parts else "".join(parts)
    return None


def ref_parameters(value) -> bool:
    return any(
        node.get("Type") == "ParamExp"
        and re.search(r"(?:ref|branch|tip|requested_base)", node["Param"]["Value"])
        for node in nodes(value)
    )


def raise_walk_error(error):
    raise error


def active_paths(root):
    for directory, names, files in (root / "plugins").walk(on_error=raise_walk_error, follow_symlinks=False):
        names.sort()
        for name in sorted(files):
            path = directory / name
            if stat.S_ISREG(path.lstat().st_mode):
                yield path


def check(root: Path) -> list[str]:
    errors = []
    source = (root / SOURCE).read_bytes()
    phrases = tuple(normalize(phrase) for phrase in KEY_WORDING)
    try:
        canonical = normalize(source.decode("utf-8"))
    except UnicodeDecodeError as error:
        raise ValueError(f"{SOURCE}: invalid UTF-8 policy source: {error}") from error
    if not all(phrase in canonical for phrase in phrases):
        errors.append(f"{SOURCE}: missing canonical key wording")
    for name in COPIES:
        path = root / name
        if not path.is_file() or path.read_bytes() != source:
            errors.append(f"{name}: validity copy differs from source")
    phrases += tuple(normalize(phrase) for phrase in LEGACY_WORDING)
    allowed = {SOURCE, *COPIES}
    for path in active_paths(root):
        active_prose = path.suffix == ".md" and (path.name in ("SKILL.md", "README.md") or "references" in path.parts)
        if not active_prose and "scripts" not in path.parts:
            continue
        relative = path.relative_to(root).as_posix()
        if relative in allowed:
            continue
        try:
            prose = normalize(path.read_text(encoding="utf-8"))
        except UnicodeDecodeError as error:
            raise ValueError(f"{relative}: invalid UTF-8 policy source: {error}") from error
        if any(phrase in prose for phrase in phrases):
            errors.append(f"{relative}: validity key wording outside shared reference")
    for plugin in ("review-until-clean", "review-pr-with-codex"):
        path = root / "plugins" / plugin / "scripts/review-scope"
        text = path.read_text()
        parsed = subprocess.run(
            ["shfmt", "--to-json", "-ln", "bash"],
            input=text, text=True, encoding="utf-8", stdout=subprocess.PIPE, check=True,
        )
        for node in nodes(json.loads(parsed.stdout)):
            comparison = node.get("Type") == "BinaryTest" and node.get("Op") in ("==", "=", "!=", "=~", "<", ">")
            if node.get("Type") == "CallExpr":
                args = node.get("Args", [])
                comparison = bool(args) and literal_word(args[0]) in ("test", "[")
            if comparison and ref_parameters(node):
                errors.append(f"{path.relative_to(root)}: ref-based scope comparison")
        digest = re.search(r'digest="\$\(jq\b.*?\| [^\n]*hash-object[^\n]*\)', text, re.S)
        if digest is None:
            errors.append(f"{path.relative_to(root)}: missing snapshot record")
        elif re.search(r"\b(?:base_ref|base_tip|requested_base)\b", digest[0]):
            errors.append(f"{path.relative_to(root)}: informational ref in snapshot record")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()
    try:
        errors = check(args.root.resolve())
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"review validity policy: check failed: {error}", file=sys.stderr)
        return 1
    if errors:
        for error in errors:
            print(f"review validity policy: {error}", file=sys.stderr)
        return 1
    print("Review validity policy passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
