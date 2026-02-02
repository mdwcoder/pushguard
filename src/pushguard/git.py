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
        if "/" in upstream:
            return upstream.split("/")[0]
    except subprocess.CalledProcessError:
        pass
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