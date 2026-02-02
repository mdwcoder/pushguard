import sys
from pathlib import Path
from typing import Dict, List, Any

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

class Config:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.config_file = repo_root / ".pushguard" / "config.toml"
        self.data = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        defaults = {
            "env_patterns": [".env", ".env.*", ".env.*.local"],
            "allowlist_env_templates": [".env.example", ".env.sample"],
            "min_secret_length": 12,
            "scan_extensions": [".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".java", ".rb", ".php", ".cs", ".env", ".toml", ".yaml", ".yml", ".json", ".ini", ".cfg", ".conf", ".md"],
            "exclude_dirs": [".git", ".pushguard", "node_modules", "venv", ".venv", "dist", "build"],
            "secret_patterns": {
                "github_token": r"ghp_[A-Za-z0-9]{36}",
                "aws_access_key_id": r"AKIA[0-9A-Z]{16}",
                "aws_secret_access_key": r"(?i)aws.*secret.*key.*[A-Za-z0-9+/]{40}",
                "stripe_key": r"sk_live_[0-9a-zA-Z]{24}",
                "google_api_key": r"AIza[0-9A-Za-z-_]{35}"
            }
        }
        if self.config_file.exists():
            with open(self.config_file, "rb") as f:
                user_config = tomllib.load(f)
            defaults.update(user_config)
        return defaults

    @property
    def env_patterns(self) -> List[str]:
        return self.data["env_patterns"]

    @property
    def allowlist_env_templates(self) -> List[str]:
        return self.data["allowlist_env_templates"]

    @property
    def min_secret_length(self) -> int:
        return self.data["min_secret_length"]

    @property
    def scan_extensions(self) -> List[str]:
        return self.data["scan_extensions"]

    @property
    def exclude_dirs(self) -> List[str]:
        return self.data["exclude_dirs"]

    @property
    def secret_patterns(self) -> Dict[str, str]:
        return self.data["secret_patterns"]