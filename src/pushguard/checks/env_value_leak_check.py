from pathlib import Path
from typing import List
from ..scanning.env_parser import parse_env_file
from ..scanning.env_detector import detect_sensitive_env_files
from ..scanning.code_search import search_literals
from . import CheckResult

def check_env_value_leak(repo_root: Path, env_patterns: List[str], allowlist: List[str], min_secret_length: int, exclude_dirs: List[str], scan_extensions: List[str]) -> CheckResult:
    sensitive_files = detect_sensitive_env_files(repo_root, env_patterns, allowlist)
    candidates = []
    for file in sensitive_files:
        env_vars = parse_env_file(file)
        for key, value in env_vars.items():
            if len(value) >= min_secret_length and value not in ["true", "false", "localhost", "127.0.0.1", "0.0.0.0"]:
                candidates.append(value)

    findings_raw = search_literals(repo_root, candidates, exclude_dirs, scan_extensions)
    findings = [f"{path}:{lineno} - {masked}" for path, lineno, masked in findings_raw]

    blockers = []
    if findings:
        blockers.append("Potential secret leaks found in code.")
    recommendations = ["Review and remove hardcoded secrets."] if findings else []

    status = "BLOCK" if blockers else "OK"

    return CheckResult(
        name="Env Value Leak Check",
        status=status,
        blockers=blockers,
        warnings=[],
        recommendations=recommendations,
        findings=findings
    )