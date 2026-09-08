from reposchematic.graph import resolve_import

def test_python_src_layout_absolute():
    known = {"src/sample/service.py", "src/sample/repository.py"}
    assert resolve_import("tests/test_service.py", "sample.service", known) == "src/sample/service.py"

def test_python_relative_import():
    known = {"src/sample/service.py", "src/sample/repository.py"}
    assert resolve_import("src/sample/service.py", ".repository", known) == "src/sample/repository.py"

def test_typescript_relative_import():
    known = {"src/web.ts", "src/helper.ts"}
    assert resolve_import("src/web.ts", "./helper", known) == "src/helper.ts"
