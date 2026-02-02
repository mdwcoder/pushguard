from pathlib import Path
from typing import Dict, List
from ..scanning.code_search import search_patterns
from . import CheckResult

def check_pattern_secrets(repo_root: Path, secret_patterns: Dict[str, str], exclude_dirs: List[str], scan_extensions: List[str]) -> CheckResult:
    findings_raw = search_patterns(repo_root, secret_patterns, exclude_dirs, scan_extensions)
    findings = [f"{path}:{lineno} - {masked}" for path, lineno, masked in findings_raw]

    blockers = []
    if findings:
        blockers.append("Potential secret patterns found in code.")
    recommendations = ["Review and remove exposed secrets."] if findings else []

    status = "BLOCK" if blockers else "OK"

    return CheckResult(
        name="Pattern Secrets Check",
        status=status,
        blockers=blockers,
        warnings=[],
        recommendations=recommendations,
        findings=findings
    )