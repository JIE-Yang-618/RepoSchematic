from reposchematic.project import load_project_options

def test_config_options(tmp_path):
    (tmp_path / ".reposchematic.toml").write_text(
        'max_file_bytes = 12345\nuse_cache = false\nignore_dirs = ["vendor"]\n', encoding="utf-8"
    )
    opts = load_project_options(tmp_path)
    assert opts.max_file_bytes == 12345
    assert opts.use_cache is False
    assert "vendor" in opts.ignore_dirs
