import pytest
from pathlib import Path
from pushguard.scanning.env_parser import parse_env_file

def test_parse_env_file(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("""# Comment
KEY1=value1
KEY2="quoted value"
KEY3='single quoted'
""")
    result = parse_env_file(env_file)
    assert result == {"KEY1": "value1", "KEY2": "quoted value", "KEY3": "single quoted"}