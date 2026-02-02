import pytest
import subprocess
from pathlib import Path
from pushguard.checks.sync_check import check_sync

@pytest.fixture
def git_repo(tmp_path):
    """Create a basic git repo."""
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo, check=True)
    # Create initial commit
    (repo / "file.txt").write_text("initial")
    subprocess.run(["git", "add", "file.txt"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=repo, check=True)
    return repo

@pytest.fixture
def remote_repo(tmp_path):
    """Create a bare remote repo with initial commit."""
    remote = tmp_path / "remote.git"
    remote.mkdir()
    subprocess.run(["git", "init", "--bare"], cwd=remote, check=True)
    # Create initial commit in a temp repo and push to bare
    temp_repo = tmp_path / "temp"
    temp_repo.mkdir()
    subprocess.run(["git", "init"], cwd=temp_repo, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=temp_repo, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=temp_repo, check=True)
    (temp_repo / "file.txt").write_text("initial")
    subprocess.run(["git", "add", "file.txt"], cwd=temp_repo, check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=temp_repo, check=True)
    subprocess.run(["git", "remote", "add", "origin", str(remote)], cwd=temp_repo, check=True)
    subprocess.run(["git", "push", "-u", "origin", "master"], cwd=temp_repo, check=True)
    return remote

@pytest.fixture
def cloned_repo(tmp_path, remote_repo):
    """Clone the remote repo."""
    clone = tmp_path / "clone"
    subprocess.run(["git", "clone", str(remote_repo), str(clone)], check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=clone, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=clone, check=True)
    return clone

def test_sync_check_up_to_date(cloned_repo):
    result = check_sync(cloned_repo, "origin", "master", False, False)
    assert result.status == "OK"

def test_sync_check_behind(tmp_path, remote_repo, cloned_repo):
    # Simulate push from another clone
    other_clone = tmp_path / "other"
    subprocess.run(["git", "clone", str(remote_repo), str(other_clone)], check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=other_clone, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=other_clone, check=True)
    (other_clone / "file.txt").write_text("updated")
    subprocess.run(["git", "add", "file.txt"], cwd=other_clone, check=True)
    subprocess.run(["git", "commit", "-m", "update"], cwd=other_clone, check=True)
    subprocess.run(["git", "push"], cwd=other_clone, check=True)

    # Now check in original clone
    result = check_sync(cloned_repo, "origin", "master", False, False)
    assert result.status == "BLOCK"
    assert "behind" in " ".join(result.blockers)

def test_sync_check_no_sync_check(cloned_repo):
    result = check_sync(cloned_repo, "origin", "master", False, True)
    assert result.status == "WARN"