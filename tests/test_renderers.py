from pathlib import Path
import shutil
from reposchematic.renderers import render_ai_context, render_architecture, render_repo_map, write_outputs
from reposchematic.service import analyze_repository

FIXTURE = Path(__file__).parent / "fixtures" / "sample_repo"

def test_documents_contain_evidence(tmp_path):
    repo = tmp_path / "repo"
    shutil.copytree(FIXTURE, repo)
    model = analyze_repository(repo, use_cache=False)
    repo_map = render_repo_map(model)
    architecture = render_architecture(model)
    context = render_ai_context(model)
    assert "Where to start" in repo_map
    assert "high confidence" in repo_map
    assert "mermaid" in architecture
    assert "Safe modification guidance" in context

def test_write_outputs(tmp_path):
    repo = tmp_path / "repo"
    shutil.copytree(FIXTURE, repo)
    model = analyze_repository(repo, use_cache=False)
    outputs = write_outputs(model, repo)
    assert (repo / "REPO_MAP.md") in outputs
    assert (repo / ".reposchematic" / "repo.json").exists()
    assert (repo / ".reposchematic" / "graph.json").exists()
