import pytest
from pathlib import Path
from pushguard.scanning.code_search import search_patterns

def test_search_patterns(tmp_path):
    code_file = tmp_path / "test.py"
    code_file.write_text("token = 'ghp_1234567890abcdef'\n")
    patterns = {"github_token": r"ghp_[A-Za-z0-9]{16}"}
    result = search_patterns(tmp_path, patterns, [], [".py"])
    assert len(result) == 1