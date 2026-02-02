from pathlib import Path
from typing import List

def should_exclude(path: Path, exclude_dirs: List[str], scan_extensions: List[str]) -> bool:
    # Check if in excluded dir
    for part in path.parts:
        if part in exclude_dirs:
            return True
    # Check extension
    if path.suffix not in scan_extensions:
        return True
    return False