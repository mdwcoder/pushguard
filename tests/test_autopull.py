import pytest
import subprocess
from pathlib import Path
from pushguard.checks.autopull_check import check_autopull

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

def test_autopull_no_autopull(cloned_repo):
    result = check_autopull(cloned_repo, "origin", "master", None, 0, 0)
    assert result.status == "OK"

def test_autopull_up_to_date(cloned_repo):
    result = check_autopull(cloned_repo, "origin", "master", "rebase", 0, 0)
    assert result.status == "OK"
    assert "already up-to-date" in " ".join(result.warnings)

def test_autopull_behind_rebase(tmp_path, remote_repo, cloned_repo):
    # Make a commit in remote
    other_clone = tmp_path / "other"
    subprocess.run(["git", "clone", str(remote_repo), str(other_clone)], check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=other_clone, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=other_clone, check=True)
    (other_clone / "file.txt").write_text("updated")
    subprocess.run(["git", "add", "file.txt"], cwd=other_clone, check=True)
    subprocess.run(["git", "commit", "-m", "update"], cwd=other_clone, check=True)
    subprocess.run(["git", "push"], cwd=other_clone, check=True)

    # Fetch in cloned_repo
    subprocess.run(["git", "fetch"], cwd=cloned_repo, check=True)

    result = check_autopull(cloned_repo, "origin", "master", "rebase", 0, 1)
    assert result.status == "OK"
    assert "successfully" in " ".join(result.warnings)

def test_autopull_dirty_working_tree(cloned_repo):
    # Make working tree dirty
    (cloned_repo / "dirty.txt").write_text("dirty")
    result = check_autopull(cloned_repo, "origin", "master", "rebase", 0, 1)
    assert result.status == "BLOCK"
    assert "not clean" in " ".join(result.blockers)