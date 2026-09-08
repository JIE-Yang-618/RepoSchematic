from pathlib import Path
from reposchematic.metadata import detect_dependencies, detect_entry_points

FIXTURE = Path(__file__).parent / "fixtures" / "sample_repo"

def test_pyproject_entrypoint():
    entries = detect_entry_points(FIXTURE)
    console = next(e for e in entries if e.kind == "console-script")
    assert console.command == "sample"
    assert console.path == "src/sample/cli.py"
    assert console.confidence == "high"

def test_dependencies():
    deps = detect_dependencies(FIXTURE)
    assert {"fastapi", "sqlalchemy"}.issubset(deps)
