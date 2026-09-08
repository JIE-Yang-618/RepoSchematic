from pathlib import Path
from reposchematic.config import ScanConfig
from reposchematic.discovery import discover

FIXTURE = Path(__file__).parent / "fixtures" / "sample_repo"

def test_discovers_source_and_skips_secret():
    result = discover(ScanConfig(root=FIXTURE))
    paths = {f.path for f in result.files}
    assert "src/sample/cli.py" in paths
    assert ".env" not in paths
    assert any("sensitive path" in x for x in result.skipped)

def test_categories():
    result = discover(ScanConfig(root=FIXTURE))
    cats = {f.path: f.category for f in result.files}
    assert cats["tests/test_service.py"] == "test"
    assert cats["pyproject.toml"] == "config"
    assert cats["README.md"] == "docs"
