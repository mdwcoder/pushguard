import sys
from pathlib import Path
from typing import Optional
import typer
import subprocess
from .config import Config
from .git import get_repo_root, is_git_repo, get_upstream_remote, remote_exists, get_current_branch, run_git
from .state import State
from .checks.gitignore_check import check_gitignore
from .checks.env_ignore_check import check_env_ignore
from .checks.env_value_leak_check import check_env_value_leak
from .checks.pattern_secrets_check import check_pattern_secrets
from .checks.sync_check import check_sync
from .checks.autopull_check import check_autopull
from .reporting.console import render_checks
from .reporting.report_txt import generate_report

app = typer.Typer()

@app.command()
def main(
    remote_pos: Optional[str] = typer.Argument(None),
    branch_pos: Optional[str] = typer.Argument(None),
    branch: Optional[str] = typer.Option(None, "--branch", help="Branch to push"),
    no_branch: bool = typer.Option(False, "--no-branch", help="Allow no branch specified"),
    remote: Optional[str] = typer.Option(None, "--remote", help="Remote to push"),
    short: bool = typer.Option(False, "--short", help="Enable positional args"),
    force: bool = typer.Option(False, "--force", help="Force push even with blocks"),
    no_gitignore_check: bool = typer.Option(False, "--no-gitignore-check", help="Skip gitignore check"),
    cd_root: bool = typer.Option(False, "--cd-root", help="Auto cd to repo root"),
    no_fetch: bool = typer.Option(False, "--no-fetch", help="Skip fetch before sync check"),
    no_sync_check: bool = typer.Option(False, "--no-sync-check", help="Skip sync check"),
    autopull: Optional[str] = typer.Option(None, "--autopull", help="Auto-pull mode: rebase or merge"),
):
    if autopull and autopull not in ["rebase", "merge"]:
        typer.echo("Error: --autopull must be 'rebase' or 'merge'.", err=True)
        sys.exit(2)
    cwd = Path.cwd()
    repo_root = get_repo_root(cwd)

    if not is_git_repo(cwd):
        typer.echo("Error: Not in a git repository.", err=True)
        sys.exit(2)

    if repo_root != cwd:
        if cd_root:
            import os
            os.chdir(repo_root)
            cwd = repo_root
        else:
            typer.echo(f"Error: Must be in repo root {repo_root}. Use --cd-root or cd there.", err=True)
            sys.exit(2)

    # Resolve remote
    if remote is None:
        remote = get_upstream_remote(cwd)
        if remote is None:
            if remote_exists("origin", cwd):
                remote = "origin"
            else:
                typer.echo("Error: No remote specified and no upstream or origin found.", err=True)
                sys.exit(2)

    # Resolve branch
    if branch is None:
        if no_branch:
            pass  # OK
        else:
            current = get_current_branch(cwd)
            if current:
                branch = current
            else:
                typer.echo("Error: No branch specified and no current branch.", err=True)
                sys.exit(2)

    config = Config(repo_root)
    state = State(repo_root)

    # Check for env example recommendation
    if not (repo_root / ".env.example").exists() and not state.get("recommended_env_example_shown"):
        typer.echo("Recommendation: Create .env.example for safe environment variable examples.")
        state.set("recommended_env_example_shown", True)

    # Run checks
    results = []
    sync_result = check_sync(repo_root, remote, branch, no_fetch, no_sync_check)
    results.append(sync_result)

    # Calculate ahead/behind for autopull
    from .git import rev_list_ahead_behind, get_upstream_ref
    upstream_ref = get_upstream_ref(repo_root)
    if upstream_ref:
        local_ref = f"refs/heads/{branch}"
        ahead, behind = rev_list_ahead_behind(local_ref, upstream_ref, repo_root)
    else:
        ahead, behind = 0, 0

    autopull_result = check_autopull(repo_root, remote, branch, autopull, ahead, behind)
    results.append(autopull_result)

    # If autopull succeeded, re-check sync
    if autopull_result.status == "OK" and autopull:
        sync_result = check_sync(repo_root, remote, branch, True, False)  # no fetch
        results[0] = sync_result  # Update sync result

    results.append(check_gitignore(repo_root, no_gitignore_check))
    results.append(check_env_ignore(repo_root, config.env_patterns, config.allowlist_env_templates))
    results.append(check_env_value_leak(repo_root, config.env_patterns, config.allowlist_env_templates, config.min_secret_length, config.exclude_dirs, config.scan_extensions))
    results.append(check_pattern_secrets(repo_root, config.secret_patterns, config.exclude_dirs, config.scan_extensions))

    render_checks(results, str(repo_root), remote, branch or "HEAD")

    has_blocks = any(r.status == "BLOCK" for r in results)

    if has_blocks:
        report_path = generate_report(results, repo_root, autopull)
        typer.echo(f"Report generated: {report_path}")
        if not force:
            typer.echo("Blocked: Fix issues or use --force.")
            sys.exit(1)
        else:
            typer.echo("Force enabled: Proceeding with push despite blocks.")

    # Execute git push
    push_args = ["push", remote]
    if branch:
        push_args.append(branch)

    try:
        result = run_git(push_args, repo_root, check=True)
        typer.echo("Push successful.")
        sys.exit(0)
    except subprocess.CalledProcessError as e:
        typer.echo(f"Git push failed with exit code {e.returncode}.", err=True)
        typer.echo(e.stdout)
        typer.echo(e.stderr, err=True)
        sys.exit(e.returncode)

if __name__ == "__main__":
    app()