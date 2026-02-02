import pytest
from pathlib import Path
from pushguard.scanning.code_search import search_literals

def test_search_literals(tmp_path):
    code_file = tmp_path / "test.py"
    code_file.write_text("secret = 'abcd1234'\n")
    result = search_literals(tmp_path, ["abcd1234"], [], [".py"])
    assert len(result) == 1
    assert result[0][0] == code_file
    assert result[0][1] == 1
    assert "abcd..." in result[0][2]