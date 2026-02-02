from pathlib import Path
from typing import List
from ..git import is_git_repo
from . import CheckResult

def check_gitignore(repo_root: Path, no_gitignore_check: bool) -> CheckResult:
    gitignore = repo_root / ".gitignore"
    blockers = []
    warnings = []
    recommendations = []
    findings = []

    if not gitignore.exists():
        if no_gitignore_check:
            warnings.append("No .gitignore found, but --no-gitignore-check enabled.")
            status = "WARN"
        else:
            blockers.append("No .gitignore file found. Create one to track ignored files.")
            recommendations.append("Run 'git init' or create .gitignore manually.")
            status = "BLOCK"
    else:
        # Ensure .pushguard/ is ignored
        with open(gitignore, "r") as f:
            content = f.read()
        if ".pushguard/" not in content:
            # Add it
            with open(gitignore, "a") as f:
                f.write("\n.pushguard/\n")
            recommendations.append("Added .pushguard/ to .gitignore.")
        status = "OK"

    return CheckResult(
        name="GitIgnore Check",
        status=status,
        blockers=blockers,
        warnings=warnings,
        recommendations=recommendations,
        findings=findings
    )