from pathlib import Path
from typing import List
import fnmatch

def detect_sensitive_env_files(repo_root: Path, env_patterns: List[str], allowlist: List[str]) -> List[Path]:
    sensitive = []
    for pattern in env_patterns:
        for file in repo_root.glob(pattern):
            if file.is_file():
                # Check if in allowlist
                if not any(fnmatch.fnmatch(file.name, allowed) for allowed in allowlist):
                    sensitive.append(file)
    return sensitive