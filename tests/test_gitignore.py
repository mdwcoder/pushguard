import pytest
from pathlib import Path
from pushguard.checks.gitignore_check import check_gitignore

def test_check_gitignore_exists(tmp_path):
    gitignore = tmp_path / ".gitignore"
    gitignore.write_text("*.log\n")
    result = check_gitignore(tmp_path, False)
    assert result.status == "OK"

def test_check_gitignore_missing(tmp_path):
    result = check_gitignore(tmp_path, False)
    assert result.status == "BLOCK"