from pathlib import Path
from reposchematic.analyzers.javascript import JavaScriptAnalyzer
from reposchematic.models import FileRecord

FIXTURE = Path(__file__).parent / "fixtures" / "sample_repo"

def test_extracts_js_ts_imports_and_exports():
    rec = FileRecord("src/web.ts", "TypeScript", 1, "x")
    JavaScriptAnalyzer().analyze(FIXTURE, rec)
    assert any(i.target == "express" for i in rec.imports)
    assert any(i.target == "./helper" for i in rec.imports)
    assert any(s.name == "createApp" and s.exported for s in rec.symbols)
    assert "Express" in rec.frameworks
