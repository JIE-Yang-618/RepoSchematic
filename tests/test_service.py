from pathlib import Path
from reposchematic.service import analyze_repository

FIXTURE = Path(__file__).parent / "fixtures" / "sample_repo"

def test_end_to_end_model(tmp_path):
    # copy to isolate cache state
    import shutil
    repo = tmp_path / "repo"
    shutil.copytree(FIXTURE, repo)
    model = analyze_repository(repo, use_cache=False)
    assert model.stats["files"] >= 8
    assert model.stats["entry_points"] >= 1
    assert any(e.source == "src/sample/service.py" and e.target == "src/sample/repository.py" for e in model.edges)
    assert any(e.source == "src/web.ts" and e.target == "src/helper.ts" for e in model.edges)
    assert "FastAPI" in model.tech_stack
    assert model.ranked_files[0].path == "src/sample/cli.py"

def test_cache_reuses_unchanged_files(tmp_path):
    import shutil
    repo = tmp_path / "repo"
    shutil.copytree(FIXTURE, repo)
    first = analyze_repository(repo)
    second = analyze_repository(repo)
    assert first.stats["reanalyzed_files"] > 0
    assert second.stats["cached_files"] == second.stats["files"]
    assert second.stats["reanalyzed_files"] == 0
