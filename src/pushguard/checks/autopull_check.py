from pathlib import Path
from typing import Optional
from ..git import is_working_tree_clean, pull_rebase, pull_merge, in_rebase, in_merge
from . import CheckResult

def check_autopull(repo_root: Path, remote: str, branch: str, autopull: Optional[str], ahead: int, behind: int) -> CheckResult:
    if not autopull:
        return CheckResult(
            name="AutoPull Check",
            status="OK",
            blockers=[],
            warnings=[],
            recommendations=[],
            findings=[]
        )

    if ahead == 0 and behind == 0:
        # Already up-to-date
        return CheckResult(
            name="AutoPull Check",
            status="OK",
            blockers=[],
            warnings=["AutoPull requested but already up-to-date."],
            recommendations=[],
            findings=[]
        )

    if not is_working_tree_clean(repo_root):
        return CheckResult(
            name="AutoPull Check",
            status="BLOCK",
            blockers=["Working tree is not clean. Cannot auto-pull."],
            warnings=[],
            recommendations=["Stash or commit your changes before running pushguard with --autopull."],
            findings=[]
        )

    if autopull == "rebase":
        result = pull_rebase(remote, branch, repo_root)
    elif autopull == "merge":
        result = pull_merge(remote, branch, repo_root)
    else:
        return CheckResult(
            name="AutoPull Check",
            status="BLOCK",
            blockers=["Invalid autopull mode."],
            warnings=[],
            recommendations=[],
            findings=[]
        )

    if result.returncode == 0:
        return CheckResult(
            name="AutoPull Check",
            status="OK",
            blockers=[],
            warnings=[f"Auto-pulled with {autopull} successfully."],
            recommendations=[],
            findings=[]
        )
    else:
        # Check for conflicts
        if in_rebase(repo_root) or in_merge(repo_root):
            mode = "rebase" if in_rebase(repo_root) else "merge"
            return CheckResult(
                name="AutoPull Check",
                status="BLOCK",
                blockers=[f"Conflicts detected during {mode}."],
                warnings=[],
                recommendations=[
                    f"Resolve conflicts, then run 'git {mode} --continue' or 'git {mode} --abort'.",
                    "After resolving, run pushguard again."
                ],
                findings=[]
            )
        else:
            return CheckResult(
                name="AutoPull Check",
                status="BLOCK",
                blockers=[f"Auto-pull {autopull} failed."],
                warnings=[],
                recommendations=["Check git status and resolve issues."],
                findings=[]
            )