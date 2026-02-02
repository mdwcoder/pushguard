from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from typing import List
from ..checks import CheckResult
from .. import __version__

console = Console()

def render_checks(results: List[CheckResult], repo_path: str, remote: str, branch: str):
    console.print(Panel.fit(f"[bold blue]pushguard v{__version__}[/bold blue] - {repo_path} -> {remote}/{branch}"))

    table = Table(title="Security Checks")
    table.add_column("Check", style="cyan")
    table.add_column("Status", justify="center")
    table.add_column("Details")

    for result in results:
        status_color = {"OK": "green", "WARN": "yellow", "BLOCK": "red"}.get(result.status, "white")
        details = []
        if result.blockers:
            details.extend([f"[red]BLOCK: {b}[/red]" for b in result.blockers])
        if result.warnings:
            details.extend([f"[yellow]WARN: {w}[/yellow]" for w in result.warnings])
        if result.recommendations:
            details.extend([f"[blue]RECOMMEND: {r}[/blue]" for r in result.recommendations])
        if result.findings:
            details.extend([f"[magenta]FINDING: {f}[/magenta]" for f in result.findings])
        table.add_row(result.name, f"[{status_color}]{result.status}[/{status_color}]", "\n".join(details))

    console.print(table)