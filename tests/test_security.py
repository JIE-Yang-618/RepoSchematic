from pathlib import Path
from reposchematic.security import contains_secret, is_sensitive_path

def test_sensitive_paths():
    assert is_sensitive_path(Path(".env"))
    assert is_sensitive_path(Path("keys/server.pem"))
    assert not is_sensitive_path(Path("src/config.py"))

def test_secret_detection():
    assert contains_secret("api_key = 'abcdefghijklmnop123456'")
    assert not contains_secret("api_key_name = 'development'")
