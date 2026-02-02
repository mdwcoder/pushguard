from pathlib import Path
from typing import List
from ..git import is_tracked, is_ignored
from ..scanning.env_detector import detect_sensitive_env_files
from . import CheckResult

def check_env_ignore(repo_root: Path, env_patterns: List[str], allowlist: List[str]) -> CheckResult:
    sensitive_files = detect_sensitive_env_files(repo_root, env_patterns, allowlist)
    blockers = []
    warnings = []
    recommendations = []
    findings = []

    for file in sensitive_files:
        if is_tracked(file, repo_root):
            blockers.append(f"File {file.name} is tracked. Sensitive files should not be committed.")
            recommendations.append(f"Run 'git rm --cached {file.name}' and add to .gitignore.")
        elif not is_ignored(file, repo_root):
            blockers.append(f"File {file.name} is not ignored. Add to .gitignore.")
            recommendations.append(f"Add '{file.name}' to .gitignore.")

    if not blockers:
        status = "OK"
    else:
        status = "BLOCK"

    return CheckResult(
        name="Env Ignore Check",
        status=status,
        blockers=blockers,
        warnings=warnings,
        recommendations=recommendations,
        findings=findings
    )