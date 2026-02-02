# pushguard

Pre-flight security checks for git push. Ensures your code is safe and up-to-date before pushing to remote repositories.

## Installation

### Recommended: pipx (isolated environment)
```bash
pipx install pushguard
```

### Alternative: pip
```bash
pip install --user pushguard
```

### Windows
Use Git Bash or WSL for best compatibility. PowerShell may work but Git Bash is recommended.

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
