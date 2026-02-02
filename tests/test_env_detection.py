import pytest
from pathlib import Path
from pushguard.scanning.env_detector import detect_sensitive_env_files

def test_detect_sensitive_env_files(tmp_path):
    (tmp_path / ".env").touch()
    (tmp_path / ".env.production").touch()
    (tmp_path / ".env.example").touch()
    result = detect_sensitive_env_files(tmp_path, [".env", ".env.*"], [".env.example"])
    assert len(result) == 2
    assert (tmp_path / ".env") in result
    assert (tmp_path / ".env.production") in result