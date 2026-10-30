"""Opt-in live Codex checks; uses existing CLI authentication, never runs in CI."""

import argparse
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests/data/trim-text-default-scopes.json"
SKILL = ROOT / "plugins/trim-text/skills/trim-text/SKILL.md"
COMMENT_FIXTURE = ROOT / "tests/data/trim-scope.json"
COMMENT_SKILL = ROOT / "plugins/trim-comments/skills/trim-comments/SKILL.md"


def run(command, cwd):
    return subprocess.check_output(command, cwd=cwd, text=True).strip()


def evaluate(out, name, prompt, schema, cwd):
    schema_path = out / f"{name}-schema.json"
    reply = out / f"{name}-reply.json"
    schema_path.write_text(json.dumps(schema))
    with (out / f"{name}.log").open("w") as log:
        subprocess.run(
            [
                "codex", "exec", "--cd", str(cwd), "--skip-git-repo-check",
                "--sandbox", "read-only", "--config", 'approval_policy="never"',
                "--config", 'web_search="disabled"', "--ephemeral",
                "--model", "gpt-6.1-sol", "--config", 'model_reasoning_effort="low"',
                "--config", "model_context_window=872000",
                "--output-schema", str(schema_path), "--output-last-message", str(reply),
                prompt,
            ],
            input="", text=True, stdout=log, stderr=subprocess.STDOUT, check=True,
        )
    return json.loads(reply.read_text())


def object_schema(properties):
    return {"type": "object", "additionalProperties": False,
            "properties": properties, "required": list(properties)}


def check_scopes(cases, reply):
    actual = reply["cases"]
    assert len(actual) == len(cases), "Missing or extra case results"
    assert sorted(x["name"] for x in actual) == sorted(x["name"] for x in cases)
    for case in cases:
        result = next(x for x in actual if x["name"] == case["name"])
        assert result["choice"] == case["expected_choice"], (case["name"], result)
        assert result["base_ref"] == case["expected_base"], (case["name"], result)
        if "expected_options" in case:
            assert result["options"] == case["expected_options"], (case["name"], result)
        print(f'{case["name"]}: PASS')


def check_prose(cases, reply, base, note):
    assert reply["merge_base"] == base
    first, tail = cases[0]["working_text"].split("\n\n", 1)
    assert all(row["file"] == "notes.md" and row["before"] == first for row in reply["changes"]), reply
    assert len(reply["changes"]) == 1, reply
    change = reply["changes"][0]
    assert "must" in change["after"] and "Save" in change["after"]
    assert len(change["after"]) < len(first)
    rendered = cases[0]["working_text"].replace(first, change["after"], 1)
    assert rendered.split("\n\n", 1)[1] == tail
    assert note.read_text() == cases[0]["working_text"]


def check_comments(cases, replies):
    for variant in ("alias", "equivalent", "mixed"):
        selected = [case for case in cases if ("request" if variant == "mixed" else variant) in case]
        actual = replies[variant]["cases"]
        assert len(actual) == len(selected), (variant, "Missing or extra cases")
        for case, result in zip(selected, actual):
            request = case["request" if variant == "mixed" else variant]
            assert result["request"] == request, (variant, result)
            assert len({row["file"] for row in result["eligible"]}) == len(result["eligible"])
            eligible = {row["file"]: row["lines"] for row in result["eligible"]}
            profiles = {row["file"]: row["profile"] for row in result["eligible"]}
            expected_profiles = case.get("profiles", {path: "code-comments" for path in case["expected"]})
            assert eligible == case["expected"], (request, eligible, case["expected"])
            assert profiles == expected_profiles, (request, profiles)
            expected_flags = ["fresh.ts:1"] if "fresh.ts" in case["expected"] else []
            assert result["flags"] == expected_flags, (request, result["flags"])
            print(f"{request}: PASS")


def fixture_state(fixture):
    files = {str(path.relative_to(fixture)): path.read_bytes()
             for path in fixture.rglob("*")
             if path.is_file() and ".git" not in path.relative_to(fixture).parts}
    return (run(["git", "rev-parse", "HEAD"], fixture),
            run(["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"], fixture),
            (fixture / ".git/index").read_bytes(), files)


def evaluate_comments(out):
    data = json.loads(COMMENT_FIXTURE.read_text())
    fixture = out / "comment-fixture"
    fixture.mkdir()
    run(["git", "init", "-q", "--template=", "-b", "main", "."], fixture)
    for path, text in data["base_files"].items():
        (fixture / path).write_text(text)
    run(["git", "add", "."], fixture)
    run(["git", "commit", "-S", "-qm", "test: prepare comment scope fixture"], fixture)
    run(["git", "remote", "add", "origin", "https://github.com/cboone/agent-harness-plugins.git"], fixture)
    run(["git", "update-ref", "refs/remotes/origin/main", "HEAD"], fixture)
    run(["git", "symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/main"], fixture)
    run(["git", "checkout", "-q", "-b", "feature/comments"], fixture)
    for group in ("working_files", "untracked_files"):
        for path, text in data[group].items():
            (fixture / path).write_text(text)
    before = fixture_state(fixture)
    row_schema = object_schema({
        "file": {"type": "string"},
        "lines": {"type": "array", "items": {"type": "integer"}},
        "profile": {"type": "string"},
    })
    result_schema = object_schema({
        "request": {"type": "string"},
        "eligible": {"type": "array", "items": row_schema},
        "flags": {"type": "array", "items": {"type": "string"}},
    })
    schema = object_schema({"cases": {"type": "array", "items": result_schema}})
    replies = {}
    for variant in ("alias", "equivalent", "mixed"):
        key = "request" if variant == "mixed" else variant
        requests = [case[key] for case in data["cases"] if key in case]
        skill = COMMENT_SKILL if variant == "alias" else SKILL
        prompt = (
            f"Follow the skill at {skill} to resolve each request independently. "
            f"Its trim-text dependency, if needed, is at {SKILL}. "
            "Every request also has --no-codex. Run it yourself without delegation. "
            "Stop after scope resolution and classification, before proposing edits. "
            "No writes, commits, linters or network. origin/main is the verified remote default "
            "ref in this user's non-fork, non-archived fixture; no PR matches the branch. "
            "Return eligible comment-start lines or prose-unit start lines and their profiles. "
            "Include protected comments even when kept or flagged. Flags lists only file:line "
            "locations whose action is flag. Preserve request order and exact request text. "
            "Requests: " + json.dumps(requests)
        )
        replies[variant] = evaluate(out, f"comments-{variant}", prompt, schema, fixture)
        assert fixture_state(fixture) == before, (variant, "Dry run changed the fixture")
    check_comments(data["cases"], replies)
    print("comments: PASS; independent alias/direct scope, mixed profiles, TODO flags and unchanged state")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path)
    parser.add_argument("--scope-reply", type=Path, help="Check an existing scope reply without model calls")
    parser.add_argument("--prose-only", action="store_true", help="Run only the Git prose boundary check")
    parser.add_argument("--comments-only", action="store_true", help="Run alias/direct and mixed-file scope checks")
    parser.add_argument("--comment-replies", type=Path, help="Check existing comments-*-reply.json files without model calls")
    args = parser.parse_args()
    cases = json.loads(FIXTURE.read_text())
    if args.comment_replies:
        data = json.loads(COMMENT_FIXTURE.read_text())
        replies = {variant: json.loads((args.comment_replies / f"comments-{variant}-reply.json").read_text())
                   for variant in ("alias", "equivalent", "mixed")}
        check_comments(data["cases"], replies)
        return
    if args.scope_reply:
        check_scopes(cases, json.loads(args.scope_reply.read_text()))
        return
    if args.out_dir is None:
        parser.error("--out-dir is required for live evaluation")
    out = args.out_dir.resolve()
    if out == ROOT or ROOT in out.parents:
        parser.error("--out-dir must be outside the repository")
    out.mkdir(exist_ok=True)
    if any(out.iterdir()):
        parser.error("--out-dir must be empty")
    print(f"Evaluation output: {out}", flush=True)
    if args.comments_only:
        evaluate_comments(out)
        return
    inputs = [{k: v for k, v in case.items()
               if not k.startswith("expected_") and not k.endswith("_text")}
              for case in cases]
    result_schema = object_schema({
        "name": {"type": "string"},
        "choice": {"type": "string", "enum": ["branch", "pr", "question", "none"]},
        "options": {"type": "array", "items": {"type": "string"}},
        "base_ref": {"type": ["string", "null"]},
    })
    schema = object_schema({"cases": {
        "type": "array", "minItems": len(cases), "maxItems": len(cases), "items": result_schema,
    }})
    prompt = (
        "Apply the supplied skill literally to every scenario. Do not invent scope choices. "
        "Snapshots are hypothetical lookup results, not live GitHub state. Refs resolve and share history. "
        "No tools, commands, edits, network or delegation. Stop after scope resolution; record any "
        "required question instead of asking it. Return every case name, choice, options (default first), "
        "and base_ref only when branch scope is selected, otherwise null.\nSKILL:\n"
        + SKILL.read_text() + "\nSCENARIOS:\n" + json.dumps(inputs)
    )
    if not args.prose_only:
        check_scopes(cases, evaluate(out, "scopes", prompt, schema, out))

    fixture = out / "prose-fixture"
    fixture.mkdir()
    run(["git", "init", "-q", "--template=", "."], fixture)
    run(["git", "checkout", "-q", "-b", "main"], fixture)
    note = fixture / "notes.md"
    note.write_text(cases[0]["baseline_text"])
    run(["git", "add", "notes.md"], fixture)
    run(["git", "commit", "-S", "-qm", "test: prepare branch prose fixture"], fixture)
    base = run(["git", "rev-parse", "HEAD"], fixture)
    run(["git", "checkout", "-q", "-b", "feature/prose"], fixture)
    note.write_text(cases[0]["working_text"])
    schema = object_schema({
        "merge_base": {"type": "string"},
        "changes": {"type": "array", "items": object_schema({
            "file": {"type": "string"}, "before": {"type": "string"}, "after": {"type": "string"},
        })},
    })
    prompt = (
        f"Follow the skill at {SKILL} with branch --base main --dry-run --no-codex. "
        "Run it yourself without delegation or another Codex process in this Git fixture. "
        "Do not edit, commit, run linters or make network requests. Apply scope and preservation rules. "
        "Encode proposed rows as JSON instead of Markdown, with the resolved merge-base SHA "
        "and repository-relative file names."
    )
    reply = evaluate(out, "prose", prompt, schema, fixture)
    check_prose(cases, reply, base, note)
    print("prose: PASS; unchanged units, requirement, link and code preserved")


if __name__ == "__main__":
    main()
