from dataclasses import dataclass
from typing import List

@dataclass
class CheckResult:
    name: str
    status: str  # OK, WARN, BLOCK
    blockers: List[str]
    warnings: List[str]
    recommendations: List[str]
    findings: List[str]