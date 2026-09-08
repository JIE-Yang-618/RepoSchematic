import pytest
from pathlib import Path
from reposchematic.analyzers.treesitter import TreeSitterJavaScriptAnalyzer, available
from reposchematic.models import FileRecord

FIXTURE = Path(__file__).parent / "fixtures" / "sample_repo"

def test_optional_tree_sitter_parser_when_installed():
    if not available():
        pytest.skip("tree-sitter extra not installed")
    rec = FileRecord("src/web.ts", "TypeScript", 1, "x")
    TreeSitterJavaScriptAnalyzer().analyze(FIXTURE, rec)
    assert rec.parse_status == "ok-tree-sitter"
    assert any(i.target == "./helper" for i in rec.imports)
    assert any(s.name == "createApp" for s in rec.symbols)
