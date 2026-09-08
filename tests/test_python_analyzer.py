from pathlib import Path
from reposchematic.analyzers.python import PythonAnalyzer
from reposchematic.models import FileRecord

FIXTURE = Path(__file__).parent / "fixtures" / "sample_repo"

def test_extracts_symbols_and_imports():
    rec = FileRecord("src/sample/service.py", "Python", 1, "x")
    PythonAnalyzer().analyze(FIXTURE, rec)
    assert any(s.name == "UserService" and s.kind == "class" for s in rec.symbols)
    assert any(i.target == ".repository" for i in rec.imports)
    assert rec.parse_status == "ok"

def test_parse_error_is_nonfatal(tmp_path):
    (tmp_path / "bad.py").write_text("def nope(:", encoding="utf-8")
    rec = FileRecord("bad.py", "Python", 1, "x")
    PythonAnalyzer().analyze(tmp_path, rec)
    assert rec.parse_status == "error"
