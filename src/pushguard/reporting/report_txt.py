from pathlib import Path
from datetime import datetime
from typing import List, Optional
from ..checks import CheckResult

def generate_report(results: List[CheckResult], repo_root: Path, autopull_mode: Optional[str] = None) -> Path:
    reports_dir = repo_root / ".pushguard" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = reports_dir / f"{timestamp}_report.txt"

    with open(report_file, "w") as f:
        f.write("pushguard Security Report\n")
        f.write(f"Generated: {datetime.now()}\n")
        if autopull_mode:
            f.write(f"AutoPull Mode: {autopull_mode}\n")
        f.write("\n")
        for result in results:
            f.write(f"Check: {result.name}\n")
            f.write(f"Status: {result.status}\n")
            if result.blockers:
                f.write("Blockers:\n")
                for b in result.blockers:
                    f.write(f"  - {b}\n")
            if result.warnings:
                f.write("Warnings:\n")
                for w in result.warnings:
                    f.write(f"  - {w}\n")
            if result.recommendations:
                f.write("Recommendations:\n")
                for r in result.recommendations:
                    f.write(f"  - {r}\n")
            if result.findings:
                f.write("Findings:\n")
                for find in result.findings:
                    f.write(f"  - {find}\n")
            f.write("\n")

    return report_file