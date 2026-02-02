import json
from pathlib import Path
from typing import Dict, Any

class State:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.state_dir = repo_root / ".pushguard"
        self.state_file = self.state_dir / "state.json"
        self.data = self._load_state()

    def _load_state(self) -> Dict[str, Any]:
        if self.state_file.exists():
            with open(self.state_file, "r") as f:
                return json.load(f)
        return {}

    def save(self):
        self.state_dir.mkdir(exist_ok=True)
        with open(self.state_file, "w") as f:
            json.dump(self.data, f, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def set(self, key: str, value: Any):
        self.data[key] = value
        self.save()