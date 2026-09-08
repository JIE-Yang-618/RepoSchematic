from reposchematic.project import initialize_project

def test_init_creates_config_and_state(tmp_path):
    messages = initialize_project(tmp_path)
    assert (tmp_path / ".reposchematic.toml").exists()
    assert (tmp_path / ".reposchematic").is_dir()
    assert messages

def test_init_uses_git_local_exclude(tmp_path):
    (tmp_path / ".git" / "info").mkdir(parents=True)
    initialize_project(tmp_path)
    text = (tmp_path / ".git" / "info" / "exclude").read_text()
    assert ".reposchematic/" in text
