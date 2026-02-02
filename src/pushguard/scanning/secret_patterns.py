from typing import Dict

DEFAULT_SECRET_PATTERNS: Dict[str, str] = {
    "github_token": r"ghp_[A-Za-z0-9]{36}",
    "aws_access_key_id": r"AKIA[0-9A-Z]{16}",
    "aws_secret_access_key": r"(?i)aws.*secret.*key.*[A-Za-z0-9+/]{40}",
    "stripe_key": r"sk_live_[0-9a-zA-Z]{24}",
    "google_api_key": r"AIza[0-9A-Za-z-_]{35}"
}