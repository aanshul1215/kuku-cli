"""
Console helpers (UI layer)
- centered rules
- compact command panels
- consistent number alignment
"""
from typing import Iterable, Optional, Sequence
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt


class ConsoleUI:
    def __init__(self, console: Optional[Console] = None) -> None:
        self.console = console or Console()

    # ---- framing / chrome -------------------------------------------------

    def title(self, text: str) -> None:
        # centered, with a subtle accent
        self.console.rule(f"[bold white]{text}[/bold white]", characters="─")

    def palette(self, heading: str, body: str) -> None:
        # "Command palette" feel
        self.console.print(
            Panel.fit(
                body,
                title=f"[bold]{heading}[/bold]",
                border_style="bright_black",
                padding=(0, 2),
            )
        )

    # ---- messaging ---------------------------------------------------------

    def info(self, msg: str) -> None:
        self.console.print(f"[cyan]{msg}[/cyan]")

    def ok(self, msg: str) -> None:
        self.console.print(f"[green]✓ {msg}[/green]")

    def warn(self, msg: str) -> None:
        self.console.print(f"[yellow]! {msg}[/yellow]")

    def error(self, msg: str) -> None:
        self.console.print(f"[red]✗ {msg}[/red]")

    # ---- tables ------------------------------------------------------------

    def table(
        self,
        title: str,
        columns: Sequence[str],
        rows: Iterable[Iterable[object]],
        right_align: Iterable[str] = ("qty", "quantity", "price", "cost", "balance", "total"),
    ) -> None:
        t = Table(title=title, show_lines=False, border_style="bright_black")
        for c in columns:
            justify = "right" if c.lower() in right_align else "left"
            t.add_column(c, justify=justify)
        for r in rows:
            t.add_row(*[str(x) for x in r])
        self.console.print(t)

    # ---- prompts -----------------------------------------------------------

    def ask(self, prompt: str) -> str:
        return Prompt.ask(prompt).strip()

    def ask_password(self, prompt: str) -> str:
        return Prompt.ask(prompt, password=True).strip()

    def pause(self) -> None:
        Prompt.ask("Press [Enter] to continue", default="")
