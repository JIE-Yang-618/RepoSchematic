from __future__ import annotations

import json
import tomllib
from pathlib import Path

from .models import EntryPoint, Evidence


def detect_entry_points(root: Path) -> list[EntryPoint]:
    entries: list[EntryPoint] = []
    pyproject = root / "pyproject.toml"
    if pyproject.exists():
        try:
            data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
            scripts = data.get("project", {}).get("scripts", {})
            for command, target in scripts.items():
                module = str(target).split(":", 1)[0]
                path = module.replace(".", "/") + ".py"
                src_path = "src/" + path
                chosen = src_path if (root / src_path).exists() else path
                entries.append(EntryPoint(
                    path=chosen,
                    kind="console-script",
                    command=command,
                    confidence="high",
                    evidence=[Evidence("pyproject", f"[project.scripts] {command} = {target}", "pyproject.toml")],
                ))
        except (OSError, tomllib.TOMLDecodeError):
            pass

    package = root / "package.json"
    if package.exists():
        try:
            data = json.loads(package.read_text(encoding="utf-8"))
            if isinstance(data.get("main"), str):
                entries.append(EntryPoint(
                    path=data["main"], kind="package-main", command=None, confidence="high",
                    evidence=[Evidence("package.json", f"main = {data['main']}", "package.json")],
                ))
            scripts = data.get("scripts", {})
            for name in ("start", "dev", "serve"):
                if isinstance(scripts.get(name), str):
                    entries.append(EntryPoint(
                        path="package.json", kind="npm-script", command=f"npm run {name}", confidence="medium",
                        evidence=[Evidence("package.json", f"scripts.{name} = {scripts[name]}", "package.json")],
                    ))
        except (OSError, json.JSONDecodeError):
            pass

    for candidate, kind in [
        ("main.py", "convention"), ("app.py", "convention"), ("src/main.py", "convention"),
        ("src/app.py", "convention"), ("index.js", "convention"), ("src/index.js", "convention"),
        ("src/index.ts", "convention"),
    ]:
        if (root / candidate).exists() and not any(e.path == candidate for e in entries):
            entries.append(EntryPoint(
                path=candidate, kind=kind, command=None, confidence="medium",
                evidence=[Evidence("convention", "Common application entry-point filename", candidate)],
            ))
    return entries


def detect_dependencies(root: Path) -> set[str]:
    deps: set[str] = set()
    pyproject = root / "pyproject.toml"
    if pyproject.exists():
        try:
            data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
            project = data.get("project", {})
            for item in project.get("dependencies", []) or []:
                deps.add(_package_name(str(item)))
            for group in (project.get("optional-dependencies", {}) or {}).values():
                for item in group or []:
                    deps.add(_package_name(str(item)))
        except (OSError, tomllib.TOMLDecodeError):
            pass
    req = root / "requirements.txt"
    if req.exists():
        for line in req.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and not line.startswith("-"):
                deps.add(_package_name(line))
    package = root / "package.json"
    if package.exists():
        try:
            data = json.loads(package.read_text(encoding="utf-8"))
            for section in ("dependencies", "devDependencies", "peerDependencies"):
                deps.update((data.get(section) or {}).keys())
        except (OSError, json.JSONDecodeError):
            pass
    return {d for d in deps if d}


def _package_name(spec: str) -> str:
    for token in ("[", ">", "<", "=", "!", "~", ";", " "):
        spec = spec.split(token, 1)[0]
    return spec.strip()
