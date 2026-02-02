from pathlib import Path
from typing import List, Dict, Tuple, Union
import re
from .exclusions import should_exclude

Finding = Tuple[Path, int, str]  # path, lineno, masked_match

def search_literals(repo_root: Path, literals: List[str], exclude_dirs: List[str], scan_extensions: List[str]) -> List[Finding]:
    findings = []
    for file_path in repo_root.rglob("*"):
        if not file_path.is_file() or should_exclude(file_path, exclude_dirs, scan_extensions):
            continue
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                for lineno, line in enumerate(f, 1):
                    for literal in literals:
                        if literal in line:
                            masked = mask_secret(literal)
                            findings.append((file_path, lineno, masked))
        except Exception:
            pass  # Skip unreadable files
    return findings

def search_patterns(repo_root: Path, patterns: Dict[str, str], exclude_dirs: List[str], scan_extensions: List[str]) -> List[Finding]:
    findings = []
    compiled_patterns = {name: re.compile(pattern) for name, pattern in patterns.items()}
    for file_path in repo_root.rglob("*"):
        if not file_path.is_file() or should_exclude(file_path, exclude_dirs, scan_extensions):
            continue
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                for lineno, line in enumerate(f, 1):
                    for name, regex in compiled_patterns.items():
                        for match in regex.finditer(line):
                            masked = mask_secret(match.group(0))
                            findings.append((file_path, lineno, masked))
        except Exception:
            pass
    return findings

def mask_secret(secret: str) -> str:
    if len(secret) <= 4:
        return "****"
    return secret[:4] + "..." + secret[-4:]