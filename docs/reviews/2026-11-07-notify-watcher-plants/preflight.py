"""Validate owned plant copies before consuming a checked-plant gate."""
import hashlib
import ast
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import sys

FIXTURES = {'tests/fixtures/measure-codex-failure-launches': 'db92781b828ee37c03d9f35067980c71b68955c56ca4f343472c0b1b74235189', 'tests/fixtures/notify-rollout/sleep': '749ef0aca998c275ae88a32fd5846ccf1cf8794a6cbe507697c7708a14b601ef', 'tests/fixtures/notify-rollout/jq': '6a8db9b8574260110fe58077f50ab9b5cee5684b03010bf2a14cad46407e6cee', 'tests/fixtures/notify-rollout/tail': 'fbd51ab6755913e83e9bdf3f03b1cc45910138f3561fa441eb68038752b705a9', 'docs/reviews/2026-11-07-notify-watcher-plants/check.bash': 'ce09be8dc4b33f27d68c58ee262643a973efbe5f7a292390eafaa76135115b28', 'tests/fixtures/notify-rollout/mktemp': '13c1a913f026b8de0ba65a774406ca106c70874eb580e0136a4343ad77564735', 'tests/fixtures/notify-rollout/alerter': '73b45b58775de9662a01a054993f6521d4d19b9aa25e1301a52c99fdc1163e06', 'tests/fixtures/notify-rollout/tmux': '59f62ea762ae33e6217562cdb28a6403d4332c2ba3e3ce21dfcb3bb874ff5d5f', 'bin/lib/capture-child.bash': '29a0347c179df50079988e3314cc90f09ddfbf41caf9bdb7c0cf8a33a8b8cff5', 'docs/reviews/2026-11-07-notify-watcher-plants/startup-check.bash': '11735ca85144a76af75af2a2fcab2f456fd878e8dcab51132e81821d5bc0d1b7', 'bin/lib/git-environment.bash': '5f2cb5000fe3d05cc65705347c62c4a2975e0795e5b47c003d4260371279c054'}
PYTHON_FIXTURES = {'docs/reviews/2026-11-07-notify-watcher-plants/detector.py': 'd350d240d60e9f39ffcd2075c3b88ff69c97ea287acc34a984a65a08502442b9', 'plugins/plant-defects/scripts/checked_core.py': '5df16673e84af61c9729913d89fc74ce6c335070ed2e51356b4206e8002ae543'}


def main():
    root = Path.cwd()
    manifest = json.loads((root / (sys.argv[1] if len(sys.argv) > 1 else "2026-11-07-notify-watcher-plants.json")).read_text())
    for name, digest in PYTHON_FIXTURES.items():
        text = (root / name).read_text()
        assert "DEBUG" not in text and "BASH_COMMAND" not in text, name
        assert hashlib.sha256((root / name).read_bytes()).hexdigest() == digest, name
    detector = (root / "docs/reviews/2026-11-07-notify-watcher-plants/detector.py").read_text()
    for function in ast.parse(detector).body:
        if isinstance(function, ast.FunctionDef) and function.name != "relay_result":
            assert not any(isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name)
                           and node.value.id == "result" for node in ast.walk(function)), function.name
    assert 'isinstance(result, dict)' in detector and 'result.get("exit_code")' in detector
    for name, digest in FIXTURES.items():
        text = (root / name).read_text()
        assert "DEBUG" not in text and "BASH_COMMAND" not in text, name
        assert hashlib.sha256((root / name).read_bytes()).hexdigest() == digest, name
    judge = (root / "tests/fixtures/measure-codex-failure-launches").read_text()
    guard = judge[judge.index("function count_launches()"):judge.index("function main()")]
    assert judge.count("awk ") == guard.count("awk ") == 1
    # All artifact readers are reviewed helper bodies; main only writes records
    # or passes them to these helpers. Pinning the fixture rejects added readers.
    main_body = judge[judge.index("function main()"):]
    assert 'cat "${' not in main_body
    assert 'read -r ' not in main_body
    for helper in ("pid_record", "timer_record", "directory_record", "drain_record", "alert_count", "diagnostics", "supervisor_failure", "wait_watcher", "has_alert_message", "startup_messages"):
        start = judge.index("function " + helper + "()")
        end = judge.find("\nfunction ", start + 1)
        body = judge[start:end if end != -1 else len(judge)]
        assert '[[ -f ' in body and '! -L ' in body, helper
    assert 'all(.[]; type == "array"' in judge
    assert 'owner supervisor exited with status 1' in judge
    sleep = (root / "tests/fixtures/notify-rollout/sleep").read_text()
    assert sleep.count("exit ") == 1 and "exit 1" in sleep
    assert "exec /bin/sleep 120" in sleep
    assert '[[ -f "${ROLLOUT_LAUNCHES:?}"' in guard
    assert 'if (invalid) exit 1' in guard
    for tool, command in (("sleep", '/bin/sleep'), ("tail", '/usr/bin/tail')):
        assert f'exec {command} "$@"' in (root / f"tests/fixtures/notify-rollout/{tool}").read_text()
    assert 'exec "${ROLLOUT_REAL_JQ}" "$@"' in (root / "tests/fixtures/notify-rollout/jq").read_text()
    for variant in manifest.get("variants", []) + manifest.get("controls", []):
        with tempfile.TemporaryDirectory(prefix="notify-plant-preflight-") as temp:
            copy = Path(temp)
            for name in manifest["inputs"]:
                target = copy / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(root / name, target)
            git_env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
            git_env.update(GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_SYSTEM="/dev/null", GIT_CONFIG_NOSYSTEM="1")
            subprocess.run(["git", "apply", "--check", variant["patch"]], cwd=copy, check=True, env=git_env)
            scripts = ["plugins/notify/scripts/watch-codex-failures", "plugins/notify/scripts/notify", *FIXTURES]
            for name in scripts:
                text = (copy / name).read_text()
                loads = [line.strip() for line in text.splitlines() if line.lstrip().startswith("source ")]
                expected = ['source "${REPO_ROOT:?REPO_ROOT is required}/bin/lib/git-environment.bash"', 'source "${REPO_ROOT}/bin/lib/capture-child.bash"'] if name == "tests/fixtures/measure-codex-failure-launches" else []
                assert loads == expected, name
                subprocess.run(["bash", "-n", name], cwd=copy, check=True)
            subprocess.run(["bash", "-euo", "pipefail", "-c", 'source "$1"\nsource "$2"', "_", "bin/lib/git-environment.bash", "bin/lib/capture-child.bash"], cwd=copy, check=True)
            subprocess.run([sys.executable, "-c",
                            "import runpy; runpy.run_path('docs/reviews/2026-11-07-notify-watcher-plants/detector.py', run_name='notify_preflight'); import checked_core; from pathlib import Path; assert Path(checked_core.__file__).resolve() == Path('plugins/plant-defects/scripts/checked_core.py').resolve()"],
                           cwd=copy, check=True, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
            subprocess.run(["jq", "-n", "--arg", "identity", "", "-f",
                            "plugins/notify/scripts/codex-failure.jq"], cwd=copy, check=True)
            subprocess.run(["bash", manifest["check"]], cwd=copy, check=True, timeout=180,
                           env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
            print(f"preflight: {variant['name']} copy loads and unchanged baseline complete", flush=True)


if __name__ == "__main__":
    main()
