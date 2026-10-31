"""Opt-in edit-mode acceptance evaluation using the existing Codex CLI."""

import argparse
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PLUGIN = ROOT / "plugins/review-anti-patterns"
SKILL = PLUGIN / "skills/review-anti-patterns/SKILL.md"
CHECK = SKILL.parent / "references/result-check.jq"
EXPECTED_PATHS = {"siblings.mjs", "new-count.mjs"}
FILES = {
    "package.json": '{"type":"module","scripts":{"test":"node --test"}}\n',
    "range.mjs": "export function isInRange(value, start, end) {\n"
    "  return value >= start && value < end;\n}\n",
    "siblings.mjs": "export function countInRange(values, start, end) {\n"
    "  return values.filter(value => value >= start && value < end).length;\n}\n",
    "README.md": "# Range helpers\n\nBoth helpers include the start and exclude the end.\n",
    "range.test.mjs": "import test from 'node:test';\n"
    "import assert from 'node:assert/strict';\n"
    "import { isInRange } from './range.mjs';\n"
    "import { countInRange } from './siblings.mjs';\n"
    "test('endpoints', () => {\n"
    "  assert.equal(isInRange(2, 0, 2), false);\n"
    "  assert.equal(countInRange([0, 1, 2], 0, 2), 2);\n});\n",
}


def environment():
    # Preserve configured signing; prevent inherited Git repository selectors.
    return {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}


def git(fixture, *args):
    return subprocess.check_output(
        ["git", "--no-pager", "-c", "core.fsmonitor=false", "-C", str(fixture), *args],
        env=environment(), text=True,
    ).strip()


def read_json(path):
    assert not path.is_symlink() and path.resolve() == path and path.is_file(), str(path)
    return json.loads(path.read_text())


def read_result(path):
    result = read_json(path)
    subprocess.run(["jq", "-e", "-f", str(CHECK), str(path)],
                   check=True, stdout=subprocess.DEVNULL)
    assert result["status"] == "success", f"{path.name}: review did not succeed"
    assert result["complete"], f"{path.name}: review is incomplete"
    assert not result["not_reviewed"], f"{path.name}: review has coverage gaps"
    assert not result["unverified"], f"{path.name}: validation remains unverified"
    return result


def baseline_control(out):
    assert "2 !== 3" in (out / "before-tests.log").read_text(), "baseline endpoint assertion did not fail"


def check(out):
    baseline_control(out)
    fixture = out / "fixture"
    assert not fixture.is_symlink() and fixture.resolve() == fixture, "fixture path changed"
    state = read_json(out / "initial-state.json")
    immutable = {"range.mjs", "README.md", "range.test.mjs", "package.json"}
    assert set(state["immutable"]) == immutable, "unexpected immutable paths"
    for name in set(FILES) | EXPECTED_PATHS:
        path = fixture / name
        assert not path.is_symlink() and path.resolve() == path and path.is_file(), name
    assert git(fixture, "rev-parse", "HEAD") == state["head"], "HEAD moved"
    assert git(fixture, "show-ref") == state["refs"], "refs moved"
    assert git(fixture, "ls-files", "--stage") == state["index"], "index changed"
    for name, digest in state["immutable"].items():
        assert hashlib.sha256((fixture / name).read_bytes()).hexdigest() == digest, name
    tracked = set(git(fixture, "diff", "--no-ext-diff", "--no-textconv", "--no-color", "--name-only").splitlines())
    untracked = set(git(fixture, "ls-files", "--others", "--exclude-standard").splitlines())
    assert tracked | untracked == EXPECTED_PATHS, "unexpected or missing fixes"
    assert untracked == {"new-count.mjs"}, "new sibling was not left untracked"
    aggregate = read_result(out / "reply.json")
    initial = read_result(out / "initial-review.json")
    final = read_result(out / "final-review.json")
    assert initial["findings"], "initial review did not exercise a finding"
    assert not aggregate["findings"] and not final["findings"], "unresolved findings"
    before = read_json(out / "before.json")
    after = read_json(out / "after.json")
    for capture in (before, after):
        assert re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", capture["raw_tree"])
    current = json.loads(subprocess.check_output(
        ["bash", str(ROOT / "plugins/review-until-clean/scripts/review-scope"), "--base", "origin/main"],
        cwd=fixture, env=environment(), text=True,
    ))
    assert current["snapshot"] == after["snapshot"], "final capture no longer describes the fixture"
    measured = set(git(fixture, "diff", "--no-ext-diff", "--no-textconv", "--no-color", "--name-only",
                       before["raw_tree"], after["raw_tree"], "--").splitlines())
    assert measured == EXPECTED_PATHS, "captured fix diff misses actual fixes"
    inputs = read_json(out / "final-inputs.json")
    assert set(inputs["paths"]) == measured, "final-review inputs omit measured fixes"
    for path in measured:
        assert path in final["report"] or path in final["reviewed"], "final coverage not evidenced"
    with (out / "verified-tests.log").open("w") as log:
        subprocess.run(["node", "--test", "--test-reporter=tap", "range.test.mjs"],
                       cwd=fixture, env=environment(), stdout=log,
                       stderr=subprocess.STDOUT, check=True)
    assert "# pass 1" in (out / "verified-tests.log").read_text(), "test did not run"
    print("PASS: measured tracked and new sibling fixes reached final review; tests, HEAD and index verified")


def prepare(out):
    fixture = out / "fixture"
    fixture.mkdir()
    (out / "empty-hooks").mkdir()
    git(fixture, "init", "-q", "--template=")
    git(fixture, "checkout", "-q", "-b", "main")
    git(fixture, "config", "core.hooksPath", str(out / "empty-hooks"))
    git(fixture, "config", "user.name", "Edit-mode fixture")
    git(fixture, "config", "user.email", "fixture@example.invalid")
    for name, content in FILES.items():
        (fixture / name).write_text(content)
    git(fixture, "add", *FILES)
    git(fixture, "commit", "-S", "-qm", "test: establish edit-mode evaluation fixture")
    base = git(fixture, "rev-parse", "HEAD")
    git(fixture, "update-ref", "refs/remotes/origin/main", base)
    git(fixture, "symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/main")
    git(fixture, "remote", "add", "origin", "https://github.com/cboone/agent-harness-plugins.git")
    git(fixture, "checkout", "-q", "-b", "fixture-624-inclusive-end")
    (fixture / "range.mjs").write_text(FILES["range.mjs"].replace("value < end", "value <= end")
                                     + "\nexport async function newCount(values, start, end) {\n"
                                     "  const { countInRange } = await import('./new-count.mjs');\n"
                                     "  return countInRange(values, start, end);\n}\n")
    (fixture / "README.md").write_text(
        "# Range helpers\n\nBoth helpers now include both endpoints.\n\n"
        "The newCount entry point loads new-count.mjs, which delegates to countInRange.\n")
    (fixture / "range.test.mjs").write_text(
        FILES["range.test.mjs"].replace("test('endpoints'", "import { newCount } from './range.mjs';\n"
                                     "test('endpoints'")
        .replace("test('endpoints', () =>", "test('endpoints', async () =>")
        .replace("0, 2), false", "0, 2), true")
        .replace("0, 2), 2", "0, 2), 3")
        .replace("\n});", "\n  assert.equal(await newCount([0, 1, 2], 0, 2), 3);\n});"))
    git(fixture, "add", "range.mjs", "README.md", "range.test.mjs")
    git(fixture, "commit", "-S", "-qm", "feat: include endpoints and expose count entry point")
    state = {"base": base, "head": git(fixture, "rev-parse", "HEAD"),
             "refs": git(fixture, "show-ref"), "index": git(fixture, "ls-files", "--stage"),
             "immutable": {name: hashlib.sha256((fixture / name).read_bytes()).hexdigest()
                           for name in ("range.mjs", "README.md", "range.test.mjs", "package.json")}}
    (out / "initial-state.json").write_text(json.dumps(state, indent=2) + "\n")
    with (out / "before-tests.log").open("w") as log:
        result = subprocess.run(["node", "--test", "range.test.mjs"], cwd=fixture,
                                env=environment(), stdout=log, stderr=subprocess.STDOUT)
    assert result.returncode != 0, "fixture did not expose the intended missing implementation"
    baseline_control(out)
    return fixture, base


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--check-only", action="store_true", help="Validate saved artifacts without model calls")
    args = parser.parse_args()
    out = args.out_dir.resolve()
    if out == ROOT or ROOT in out.parents:
        parser.error("--out-dir must be outside the repository")
    if args.check_only:
        check(out)
        return
    out.mkdir(exist_ok=True)
    if any(out.iterdir()):
        parser.error("--out-dir must be empty; previous attempts are never overwritten")
    print(f"Evaluation output: {out}", flush=True)
    fixture, base = prepare(out)
    captures = out / "captures"
    captures.mkdir()
    prompt = f"""Execute one bounded edit workflow in this disposable Git fixture.
Follow {SKILL} with --edit --run-checks --range {base}..HEAD --files range.mjs
--severity important --no-codex. This is an opt-in acceptance evaluation, not a new workstream.
The inclusive-end feature and its new count entry point are intended. Leave range.mjs,
README.md, package.json and range.test.mjs unchanged; use the existing assertions.
Apply supported fixes to necessary existing and new sibling sites, validate, and review once.
Do not commit, stage, stash, push, install, authenticate, modify live configuration or use network.
Writes are allowed only in the fixture and {out}. The source repository is read-only.
Read no credentials, memory or unrelated workspace files. No delegation or other agent processes.
Use the documented current-session fallback for report-only phases, stating that access is
read-only by instruction. This entire run explicitly requests edit mode.
Parent lookup: origin is github.com/cboone/agent-harness-plugins; this synthetic branch has no PR.
Use origin/main for capture, not to replace the supplied range. No gh calls are needed.
The precondition helper is {PLUGIN}/scripts/check-edit-worktree. Load only the helper section of
{ROOT}/plugins/review-until-clean/skills/review-until-clean/SKILL.md; its review-scope is at
{ROOT}/plugins/review-until-clean/scripts/review-scope. Do not start its loop.
For evaluation, copy exact schema-shaped phase results to {out}/initial-review.json and
{out}/final-review.json, and state captures to {out}/before.json and {out}/after.json.
Before the final review, save its actual literal input path manifest as {out}/final-inputs.json
with shape {{"paths":["repository-relative paths"]}}. These audit copies add no public result keys.
Keep all phase evidence even on failure. Do not substitute the original scope for the final
review's actual chosen inputs in the audit. End with only the existing aggregate JSON including
its report field. Missing checks or coverage must remain incomplete, never invented as clean.
"""
    (out / "prompt.md").write_text(prompt)
    env = environment()
    env["TMPDIR"] = str(captures)
    with (out / "codex.log").open("w") as log:
        subprocess.run(["codex", "exec", "--cd", str(fixture), "--ephemeral",
                        "--model", "gpt-6.1-sol", "--config", 'model_reasoning_effort="medium"',
                        "--output-schema", str(SKILL.parent / "references/result-schema.json"),
                        "--output-last-message", str(out / "reply.json"), prompt],
                       input="", text=True, env=env, stdout=log, stderr=subprocess.STDOUT, check=True)
    check(out)


if __name__ == "__main__":
    if not __debug__:
        raise SystemExit("Evaluation requires Python assertions; disable optimization")
    main()
