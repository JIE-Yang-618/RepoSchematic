from pathlib import Path
import shutil
from reposchematic.cli import main

FIXTURE = Path(__file__).parent / "fixtures" / "sample_repo"

def test_cli_analyze_generates_files(tmp_path, capsys):
    repo = tmp_path / "repo"
    shutil.copytree(FIXTURE, repo)
    code = main(["analyze", str(repo), "--no-cache"])
    assert code == 0
    assert (repo / "REPO_MAP.md").exists()
    assert "RepoSchematic analyzed" in capsys.readouterr().out

def test_cli_explain(tmp_path, capsys):
    repo = tmp_path / "repo"
    shutil.copytree(FIXTURE, repo)
    code = main(["explain", "src/sample/service.py", "--repo", str(repo)])
    assert code == 0
    out = capsys.readouterr().out
    assert "UserService" in out
    assert "src/sample/repository.py" in out

def test_cli_doctor(tmp_path, capsys):
    repo = tmp_path / "repo"
    shutil.copytree(FIXTURE, repo)
    assert main(["doctor", str(repo)]) == 0
    assert "[OK" in capsys.readouterr().out
