# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-02-02

### Added
- Initial release of pushguard
- Sync check: Validates branch is up-to-date before push
- Autopull feature: Automatic rebase/merge when behind/diverged
- Security scans: Gitignore validation, env file checks, secret pattern detection
- Rich console output with actionable error messages
- Report generation with masked secrets
- Comprehensive test suite
- Local test repository setup for manual validation