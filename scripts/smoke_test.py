from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from reposchematic.cli import main

SOURCE = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "sample_repo"


def run() -> int:
    with tempfile.TemporaryDirectory(prefix="reposchematic-smoke-") as raw:
        repo = Path(raw) / "repo"
        shutil.copytree(SOURCE, repo)
        assert main(["doctor", str(repo)]) == 0
        assert main(["init", str(repo)]) == 0
        assert (repo / "REPO_MAP.md").exists()
        assert (repo / "ARCHITECTURE.md").exists()
        assert (repo / "AI_CONTEXT.md").exists()
        assert (repo / ".reposchematic" / "repo.json").exists()
        assert main(["explain", "src/sample/service.py", "--repo", str(repo)]) == 0
        assert main(["deps", "src/sample/service.py", "--repo", str(repo)]) == 0
    print("RepoSchematic smoke test: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
