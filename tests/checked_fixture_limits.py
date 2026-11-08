"""Compare plant checks with the waits declared by their actual detectors."""

import ast
import json
import math
import os
from pathlib import Path
import re
import shlex
from types import SimpleNamespace
from unittest import mock


# The notification shell clock waits only for readiness; its Python owner contains the whole invocation.
SHELL_DETECTOR_WAITS = {"tests/fixtures/notification-clock.bash": 120}


def execution_window(core, limit):
    journal = SimpleNamespace(path=Path("static-fixture-allocation"), append=lambda *args, **kwargs: None)
    runtime = core.SupervisionRuntime(journal, "static-fixture-allocation")
    with mock.patch.dict(os.environ):
        os.environ.pop("CHECKED_STEP_LIMIT", None)
        allocation = runtime.allocate(limit)
    return allocation["execution_deadline"] - allocation["started_at"]


def declared_waits(source, selectors, policy, cleanup_margin):
    tree = ast.parse(source)
    classes = {node.name: node for node in tree.body if isinstance(node, ast.ClassDef)}
    globals_ = {node.targets[0].id: node.value for node in tree.body if isinstance(node, ast.Assign)
                and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)}
    functions = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
    for name, node in classes.items():
        functions.update({name + "." + child.name: child for child in node.body if isinstance(child, ast.FunctionDef)})
    functions["<module>"] = ast.Module(body=[node for node in tree.body
                                           if not isinstance(node, (ast.FunctionDef, ast.ClassDef))], type_ignores=[])

    def evaluate(node, function, seen=()):
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.Attribute) and ast.unparse(node) == "core.CLEANUP_MARGIN":
            return cleanup_margin
        if isinstance(node, ast.Attribute) and ast.unparse(node) == "self.deadline":
            parent = next(name.rsplit(".", 1)[0] for name, value in functions.items() if value is function)
            returns = [part.value for part in functions[parent + ".deadline"].body if isinstance(part, ast.Return)]
            if len(returns) != 1:
                raise ValueError("ambiguous detector deadline property")
            return evaluate(returns[0], functions[parent + ".deadline"], seen)
        if isinstance(node, ast.Name):
            if node.id in seen:
                raise ValueError("recursive detector wait")
            definitions = [part.value for part in ast.walk(function) if isinstance(part, ast.Assign)
                           and any(isinstance(target, ast.Name) and target.id == node.id for target in part.targets)]
            if not definitions and node.id in globals_:
                definitions = [globals_[node.id]]
            values = [evaluate(value, function, (*seen, node.id)) for value in definitions
                      if not isinstance(value, ast.Constant) or value.value is not None]
            if values:
                return max(values) if all(type(value) in (int, float) for value in values) else values[-1]
        if isinstance(node, ast.Subscript):
            return evaluate(node.value, function, seen)[evaluate(node.slice, function, seen)]
        if isinstance(node, ast.Dict):
            return {evaluate(key, function, seen): evaluate(value, function, seen) for key, value in zip(node.keys, node.values)}
        if isinstance(node, ast.BinOp):
            left, right = evaluate(node.left, function, seen), evaluate(node.right, function, seen)
            operations = {ast.Add: lambda: left + right, ast.Sub: lambda: left - right,
                          ast.Mult: lambda: left * right, ast.Div: lambda: left / right}
            if type(node.op) in operations:
                return operations[type(node.op)]()
        if isinstance(node, ast.Call):
            name = ast.unparse(node.func)
            if name in ("core.deadline_after", "core.remaining", "core.phase_deadline"):
                return evaluate(node.args[0], function, seen)
            if name == "json.loads" and ast.unparse(node.args[0]) == "BUDGETS.read_text()":
                return policy
            if name == "dict":
                return {keyword.arg: evaluate(keyword.value, function, seen) for keyword in node.keywords}
            if name == "min":
                upper_bounds = []
                for argument in node.args:
                    try:
                        upper_bounds.append(evaluate(argument, function, seen))
                    except ValueError:
                        pass
                if upper_bounds:
                    return min(upper_bounds)
        raise ValueError("undeclared detector wait: " + ast.unparse(node))

    selected = set()
    for selector in selectors:
        if selector in functions:
            selected.add(selector)
        elif selector in classes:
            selected.update(name for name in functions if name.startswith(selector + ".test_"))
        else:
            raise ValueError("unknown detector selector: " + selector)
    if not selectors:
        selected = {name for name in functions if name.rsplit(".", 1)[-1].startswith("test_")}
        if not selected:
            selected = set(functions)
    selected.add("<module>")
    pending = list(selected)
    while pending:
        name = pending.pop()
        cls = name.rsplit(".", 1)[0] if "." in name else None
        for call in (node for node in ast.walk(functions[name]) if isinstance(node, ast.Call)):
            called = ast.unparse(call.func)
            linked = cls + "." + called[5:] if cls and called.startswith("self.") else called
            if linked in functions and linked not in selected:
                selected.add(linked)
                pending.append(linked)
    waits = []
    for name in sorted(selected):
        function = functions[name]
        for call in (node for node in ast.walk(function) if isinstance(node, ast.Call)):
            called = ast.unparse(call.func)
            expressions = [call.args[0]] if called == "core.deadline_after" else []
            if called.endswith((".communicate", ".wait", ".run")):
                expressions.extend(keyword.value for keyword in call.keywords if keyword.arg == "timeout")
            for expression in expressions:
                value = evaluate(expression, function)
                if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
                    raise ValueError("invalid detector wait")
                waits.append(dict(detector=name, line=call.lineno, seconds=value))
            if called.endswith(".write_text") and call.args:
                try:
                    embedded = evaluate(call.args[0], function)
                except (ValueError, TypeError):
                    continue
                if isinstance(embedded, str) and re.search(r"(?:core\.deadline_after|timeout\s*=)", embedded):
                    try:
                        nested = declared_waits(embedded, [], policy, cleanup_margin)
                    except SyntaxError:
                        continue
                    waits.extend(dict(row, detector=name + "/" + row["detector"]) for row in nested)
    return waits


def fixture_checks(root, policy):
    root = Path(root)
    checks = []
    plant_path, gate_path = (root / "tests" / name for name in ("checked_plant_test.py", "checked_gate_test.py"))
    plant_tree, gate_tree = (ast.parse(path.read_text()) for path in (plant_path, gate_path))
    supplemental = next(ast.literal_eval(node.value) for node in plant_tree.body if isinstance(node, ast.Assign)
                        and any(isinstance(target, ast.Name) and target.id == "SUPPLEMENTAL_DETECTORS" for target in node.targets))
    for tree, key in ((plant_tree, "checks"), (gate_tree, "gate_checks")):
        declarations = [node.value for node in ast.walk(tree) if isinstance(node, ast.Assign)
                        and any(isinstance(target, ast.Name) and target.id == "changes" for target in node.targets)
                        and isinstance(node.value, ast.List)]
        names = set()
        for rows in declarations:
            for row in rows.elts:
                name, method = ast.literal_eval(row.elts[0]), ast.literal_eval(row.elts[-1])
                method = method.removeprefix("FAIL: ")
                if name not in policy[key]:
                    raise ValueError("undeclared plant fixture: " + name)
                names.add(name)
                methods = [method, *supplemental.get(name, [])] if key == "checks" else [method]
                for method in methods:
                    path = plant_path if key == "checks" or name == "duplicate-reader" else gate_path
                    cls = "RunnerTests" if path == plant_path else "GateTests"
                    checks.append(dict(fixture=key + "/" + name, timeout=policy[key][name], path=path,
                                       selectors=[cls + "." + method]))
        if names != set(policy[key]):
            raise ValueError("plant fixture inventory differs from execution")
    for directory, children, files in os.walk(root):
        children[:] = [name for name in children if name not in
                       ("node_modules", "dist", ".agents", ".git", ".claude", ".workmux", ".yarn")]
        for name in files:
            if not name.endswith(".json"):
                continue
            path = Path(directory) / name
            try:
                value = json.loads(path.read_text())
            except (ValueError, UnicodeError):
                continue
            if not isinstance(value, dict) or not all(key in value for key in ("green", "check", "variants")):
                continue
            for detector, seconds in SHELL_DETECTOR_WAITS.items():
                if detector in value.get("inputs", []):
                    checks.append(dict(fixture=str(path.relative_to(root)), timeout=value["timeout"],
                                       path=root / detector, selectors=[],
                                       shell_waits=[dict(detector=detector, line=None, seconds=seconds)]))
            script = path.parent / value["check"]
            if not script.is_file():
                raise ValueError("plant check script is unavailable: " + str(path.relative_to(root)))
            pending, seen = [script], set()
            while pending:
                script = pending.pop()
                if script in seen:
                    continue
                seen.add(script)
                text = script.read_text()
                if script.suffix == ".py":
                    checks.append(dict(fixture=str(path.relative_to(root)), timeout=value["timeout"], path=script, selectors=[]))
                    continue
                tokens = shlex.split(text.replace("\\\n", " "), comments=True)
                if any(token in ("timeout", "gtimeout", "wait") for token in tokens):
                    raise ValueError("shell detector wait requires an explicit Python declaration: " + str(script))
                shell_waits = []
                for index, token in enumerate(tokens):
                    if token == "sleep":
                        try:
                            duration = float(tokens[index + 1])
                        except (IndexError, ValueError) as error:
                            raise ValueError("undeclared shell detector wait") from error
                        if not math.isfinite(duration) or duration < 0:
                            raise ValueError("invalid shell detector wait")
                        shell_waits.append(dict(detector=str(script.relative_to(root)), line=None, seconds=duration))
                checks.append(dict(fixture=str(path.relative_to(root)), timeout=value["timeout"], path=script,
                                   selectors=[], shell_waits=shell_waits))
                for index, token in enumerate(tokens):
                    if not token.endswith(".py") and not (index and tokens[index - 1] in ("bash", "sh", "source", ".")):
                        continue
                    candidate = root / token
                    if not candidate.is_file():
                        continue
                    if token.endswith(".py"):
                        selectors = []
                        for following in tokens[index + 1:]:
                            if not re.fullmatch(r"[A-Z][A-Za-z0-9_]*(?:\.test_[A-Za-z0-9_]+)?", following):
                                break
                            selectors.append(following)
                        checks.append(dict(fixture=str(path.relative_to(root)), timeout=value["timeout"], path=candidate, selectors=selectors))
                    elif index and tokens[index - 1] in ("bash", "sh", "source", "."):
                        pending.append(candidate)
    return checks


def fixture_margins(root, policy, core):
    rows, violations = [], []
    for check in fixture_checks(root, policy):
        try:
            waits = (check["shell_waits"] if "shell_waits" in check else
                     declared_waits(check["path"].read_text(), check["selectors"], policy, core.CLEANUP_MARGIN))
            window = execution_window(core, check["timeout"])
            rows.append(dict(fixture=check["fixture"], path=str(check["path"].relative_to(root)),
                             execution=window, waits=waits))
            for wait in waits:
                row = dict(fixture=check["fixture"], path=str(check["path"].relative_to(root)),
                           execution=window, **wait)
                if window < 2 * wait["seconds"] and not math.isclose(window, 2 * wait["seconds"], abs_tol=1e-6):
                    violations.append(row)
        except (ValueError, KeyError, TypeError, StopIteration) as error:
            violations.append(dict(fixture=check["fixture"], cause=str(error)))
    return rows, violations
