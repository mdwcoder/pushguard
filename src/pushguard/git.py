import subprocess
from pathlib import Path
from typing import List, Optional

def run_git(args: List[str], cwd: Path, check: bool = False) -> subprocess.CompletedProcess:
    cmd = ["git"] + args
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=check)

def get_repo_root(cwd: Path) -> Optional[Path]:
    try:
        result = run_git(["rev-parse", "--show-toplevel"], cwd, check=True)
        return Path(result.stdout.strip())
    except subprocess.CalledProcessError:
        return None

def is_git_repo(cwd: Path) -> bool:
    try:
        run_git(["rev-parse", "--git-dir"], cwd, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def get_upstream_remote(cwd: Path) -> Optional[str]:
    try:
        result = run_git(["rev-parse", "--symbolic-full-name", "@{upstream}"], cwd, check=True)
        upstream = result.stdout.strip()
        parts = upstream.split("/")
        if len(parts) >= 3 and parts[0] == "refs" and parts[1] == "remotes":
            return parts[2]
        return None
    except subprocess.CalledProcessError:
        return None

def remote_exists(name: str, cwd: Path) -> bool:
    try:
        run_git(["remote"], cwd, check=True)
        result = run_git(["remote"], cwd, check=True)
        remotes = result.stdout.strip().split("\n")
        return name in remotes
    except subprocess.CalledProcessError:
        return False

def is_tracked(path: Path, cwd: Path) -> bool:
    try:
        run_git(["ls-files", "--error-unmatch", str(path)], cwd, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def is_ignored(path: Path, cwd: Path) -> bool:
    try:
        run_git(["check-ignore", "-q", str(path)], cwd, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def get_current_branch(cwd: Path) -> Optional[str]:
    try:
        result = run_git(["rev-parse", "--abbrev-ref", "HEAD"], cwd, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None

def fetch(remote: str, cwd: Path) -> None:
    run_git(["fetch", remote], cwd, check=True)

def get_upstream_ref(cwd: Path) -> Optional[str]:
    try:
        result = run_git(["rev-parse", "--symbolic-full-name", "@{upstream}"], cwd, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None

def rev_list_ahead_behind(local_ref: str, upstream_ref: str, cwd: Path) -> tuple[int, int]:
    try:
        result = run_git(["rev-list", "--left-right", "--count", f"{local_ref}...{upstream_ref}"], cwd, check=True)
        ahead, behind = result.stdout.strip().split()
        return int(ahead), int(behind)
    except subprocess.CalledProcessError:
        return 0, 0

def is_working_tree_clean(cwd: Path) -> bool:
    try:
        result = run_git(["status", "--porcelain"], cwd, check=True)
        return not result.stdout.strip()
    except subprocess.CalledProcessError:
        return False

def pull_rebase(remote: str, branch: str, cwd: Path) -> subprocess.CompletedProcess:
    return run_git(["pull", "--rebase", remote, branch], cwd, check=False)

def pull_merge(remote: str, branch: str, cwd: Path) -> subprocess.CompletedProcess:
    return run_git(["pull", "--no-rebase", remote, branch], cwd, check=False)

def in_rebase(cwd: Path) -> bool:
    try:
        git_dir = run_git(["rev-parse", "--git-dir"], cwd, check=True).stdout.strip()
        git_dir_path = Path(cwd) / git_dir
        return (git_dir_path / "rebase-apply").exists() or (git_dir_path / "rebase-merge").exists()
    except subprocess.CalledProcessError:
        return False

def in_merge(cwd: Path) -> bool:
    try:
        git_dir = run_git(["rev-parse", "--git-dir"], cwd, check=True).stdout.strip()
        git_dir_path = Path(cwd) / git_dir
        return (git_dir_path / "MERGE_HEAD").exists()
    except subprocess.CalledProcessError:
        return False