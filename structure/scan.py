"""AST checks for structurally absent capabilities."""

from __future__ import annotations

import ast
from pathlib import Path

# node type -> (check id, severity, message)
BANNED_NODES = {
    "eval_call": ("no-eval", "critical", "eval() — arbitrary code execution"),
    "exec_call": ("no-exec", "critical", "exec() — arbitrary code execution"),
    "compile_call": ("no-compile", "high", "compile() — code object factory"),
    "os_system": ("no-os-system", "critical", "os.system() — shell injection surface"),
    "shell_true": ("no-shell-true", "high", "subprocess with shell=True"),
    "pickle_load": ("no-pickle", "high", "pickle deserialization attack surface"),
    "yaml_unsafe": ("no-yaml-unsafe", "high", "yaml.load without SafeLoader"),
}


def _call_name(node: ast.Call) -> str:
    f = node.func
    if isinstance(f, ast.Name):
        return f.id
    if isinstance(f, ast.Attribute):
        return f.attr
    return ""


def scan_file(path: str | Path) -> list[dict]:
    """Check one Python file. Returns findings."""
    path = Path(path)
    try:
        tree = ast.parse(path.read_text())
    except (SyntaxError, OSError) as e:
        return [{"file": str(path), "line": 0, "severity": "info",
                 "check": "unparseable", "detail": str(e)[:120]}]
    findings = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = _call_name(node)
        lineno = getattr(node, "lineno", 0)

        def hit(check, severity, detail):
            findings.append({"file": str(path), "line": lineno,
                             "severity": severity, "check": check,
                             "detail": detail})

        # Bare builtins only — re.compile and friends are fine.
        if isinstance(node.func, ast.Name) and node.func.id in ("eval", "exec", "compile"):
            key = {"eval": "eval_call", "exec": "exec_call", "compile": "compile_call"}[node.func.id]
            c, s, d = BANNED_NODES[key]
            hit(c, s, d)
        elif name == "system":
            c, s, d = BANNED_NODES["os_system"]
            hit(c, s, d)
        elif name in ("Popen", "run", "call", "check_output", "check_call"):
            for kw in node.keywords:
                if kw.arg == "shell" and getattr(kw.value, "value", False) is True:
                    c, s, d = BANNED_NODES["shell_true"]
                    hit(c, s, d)
        elif name in ("loads", "load") and not _is_yaml_load(node):
            c, s, d = BANNED_NODES["pickle_load"]
            hit(c, s, d + " — verify caller imports pickle, not json")
        elif _is_yaml_load(node):
            c, s, d = BANNED_NODES["yaml_unsafe"]
            hit(c, s, d)
    # filter pickle hits to actual pickle usage (name-based scan over-flags json)
    src = path.read_text()
    out = []
    for f in findings:
        if f["check"] == "no-pickle" and "import pickle" not in src and "from pickle" not in src:
            continue
        out.append(f)
    return out


def _is_yaml_load(node: ast.Call) -> bool:
    f = node.func
    return (isinstance(f, ast.Attribute) and f.attr == "load"
            and isinstance(f.value, ast.Name) and f.value.id == "yaml")


def scan_repo(root: str | Path,
              exclude: tuple[str, ...] = ("tests", "test_", "__pycache__")) -> dict:
    """Scan all Python files under root. Returns {clean, findings}."""
    findings = []
    files = 0
    for path in sorted(Path(root).rglob("*.py")):
        rel = str(path.relative_to(root))
        if any(e in rel for e in exclude):
            continue
        files += 1
        findings.extend(scan_file(path))
    return {"clean": not findings, "files": files, "findings": findings}
