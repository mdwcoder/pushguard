# pushguard

Pre-flight security checks for git push. Ensures your code is safe and up-to-date before pushing to remote repositories.

## Quickstart

```bash
git clone https://github.com/mdwcoder/pushguard.git
cd pushguard
bash init.sh
pushguard --help
```

If `init.sh` is not executable: `chmod +x init.sh && ./init.sh`.

`init.sh` will try to install `pushguard` using `pipx` (preferred). If `pipx` is not available it creates a per-user virtualenv at `~/.local/pushguard/venv`, installs the package, and links the `pushguard` CLI into `~/.local/bin`.

By default `init.sh` can add a short shell alias `pushg` that points to `pushguard`. We deliberately avoid the historical `pg` alias because `pg` may collide with the system pager on some platforms.

## Installation

Recommended (from source)

```bash
git clone https://github.com/mdwcoder/pushguard.git
cd pushguard
bash init.sh
```

If you prefer manual/development installs, use one of the alternatives below.

Alternative (development with pipx)

```bash
# for local editable install via pipx
pipx install -e .
```

Alternative (pip)

```bash
# editable local install for development
pip install -e .
# or, if published to PyPI:
# pip install --user pushguard
```

Platform notes

Linux / macOS: recommended. Windows: use Git Bash or WSL for compatibility.

## Basic Usage

By default, pushguard infers the remote (upstream or origin) and current branch, performs security checks, and blocks the push if issues are found.

```bash
pushguard
```

This runs:
- Fetch from remote
- Sync check (ensures branch is not behind/diverged)
- Security scans (gitignore, env files, secret patterns)
- If all OK, executes `git push`

## Autopull (when behind or diverged)

If your branch is behind or diverged, use `--autopull` to let pushguard handle the pull automatically:

```bash
pushguard --autopull rebase  # Recommended: rebase on top of remote
pushguard --autopull merge   # Alternative: merge remote changes
```

If conflicts occur during autopull, pushguard stops and provides instructions to resolve them.

## Security Features

### Environment Files
- Blocks pushes if `.env` files are tracked (not ignored)
- Scans for leaked values in code
- Recommends creating `.env.example` for safe examples

### Secret Patterns
- Detects common secret patterns (API keys, tokens, etc.)
- Masks findings in reports
- Scans code files for hardcoded secrets

Reports are saved to `.pushguard/reports/` with masked secrets.

## Local Test Repos

For manual testing, pushguard creates isolated test repositories in `.pushguard_testrepos/` (ignored by git).

To run the full test suite:

```bash
cd .pushguard_testrepos
# Scenarios include:
# - env not ignored
# - pattern secrets
# - diverged conflicts
# Run pushguard in each scenario repo to validate blocking behavior
```

## Options

- `--force`: Push despite blocks
- `--no-sync-check`: Skip sync validation
- `--no-fetch`: Skip fetch before sync check
- `--remote <name>`: Specify remote explicitly
- `--branch <name>`: Specify branch explicitly

## Exit Codes

- 0: Success
- 1: Blocked (fix issues or use --force)
- 2: Usage error
