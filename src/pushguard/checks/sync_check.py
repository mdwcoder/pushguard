from pathlib import Path
from typing import Optional
from ..git import get_current_branch, fetch, get_upstream_ref, rev_list_ahead_behind, remote_exists
from . import CheckResult

def check_sync(repo_root: Path, remote: str, branch: str, no_fetch: bool, no_sync_check: bool) -> CheckResult:
    if no_sync_check:
        return CheckResult(
            name="Sync Check",
            status="WARN",
            blockers=[],
            warnings=["Sync check disabled with --no-sync-check."],
            recommendations=[],
            findings=[]
        )

    if not no_fetch:
        try:
            fetch(remote, repo_root)
        except Exception:
            # If fetch fails, continue with existing refs
            pass

    upstream_ref = get_upstream_ref(repo_root)
    if upstream_ref is None:
        # Try origin/branch if exists
        if remote_exists(remote, repo_root):
            upstream_ref = f"refs/remotes/{remote}/{branch}"
        else:
            return CheckResult(
                name="Sync Check",
                status="WARN",
                blockers=[],
                warnings=["No upstream configured for branch."],
                recommendations=["Set upstream with: git branch --set-upstream-to=<remote>/<branch>"],
                findings=[]
            )

    local_ref = f"refs/heads/{branch}"
    ahead, behind = rev_list_ahead_behind(local_ref, upstream_ref, repo_root)

    if behind > 0 and ahead > 0:
        status = "BLOCK"
        blockers = [f"Branch is diverged: {ahead} commits ahead, {behind} commits behind."]
        recommendations = ["Resolve with: git pull --rebase (recommended) or git pull"]
    elif behind > 0:
        status = "BLOCK"
        blockers = [f"Branch is behind by {behind} commits."]
        recommendations = ["Update with: git pull --rebase (recommended) or git pull"]
    elif ahead > 0:
        status = "OK"
        blockers = []
        recommendations = []
    else:
        status = "OK"
        blockers = []
        recommendations = []

    return CheckResult(
        name="Sync Check",
        status=status,
        blockers=blockers,
        warnings=[],
        recommendations=recommendations,
        findings=[]
    )