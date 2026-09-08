from pathlib import Path
import shutil
from reposchematic.config import ScanConfig
from reposchematic.discovery import discover
from reposchematic.renderers import write_outputs
from reposchematic.service import analyze_repository

FIXTURE = Path(__file__).parent / "fixtures" / "sample_repo"

def test_generated_outputs_do_not_pollute_next_scan(tmp_path):
    repo = tmp_path / "repo"
    shutil.copytree(FIXTURE, repo)
    model = analyze_repository(repo, use_cache=False)
    write_outputs(model, repo)
    result = discover(ScanConfig(root=repo))
    paths = {f.path for f in result.files}
    assert "REPO_MAP.md" not in paths
    assert "ARCHITECTURE.md" not in paths
    assert "AI_CONTEXT.md" not in paths
    assert not any(p.startswith(".reposchematic/") for p in paths)
