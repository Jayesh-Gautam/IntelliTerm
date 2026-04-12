"""
Terminal UI rendering for IntelliTerm.

Uses the Rich library to provide colored output, bordered panels,
loading spinners, and formatted tables. All terminal output should
go through this module for visual consistency.
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box


console = Console()


def print_banner():
    """Print the IntelliTerm startup banner with styled ASCII art."""
    banner = r"""
 ___ _  _ _____ ___ _    _    ___ _____ ___ ___ __  __
|_ _| \| |_   _| __| |  | |  |_ _|_   _| __| _ \  \/  |
 | || .` | | | | _|| |__| |__ | |  | | | _||   / |\/| |
|___|_|\_| |_| |___|____|____|___| |_| |___|_|_\_|  |_|
    """
    console.print(banner, style="bold cyan")
    console.print("  Natural Language Terminal v2.0", style="dim")
    console.print(
        "  Type a command in plain English or use standard shell commands.",
        style="dim",
    )
    console.print("  Type 'exit' or 'quit' to close.\n", style="dim")


def print_command_box(command, explanation):
    """
    Display a command suggestion inside a bordered green panel.

    Args:
        command: The shell command string to display.
        explanation: A short description of what the command does.
    """
    content = Text()
    content.append("Command:     ", style="bold white")
    content.append(command, style="bold green")
    content.append("\n")
    content.append("Explanation: ", style="bold white")
    content.append(explanation, style="dim white")

    panel = Panel(
        content,
        title="[bold]Command Suggestion[/bold]",
        border_style="green",
        box=box.ROUNDED,
        padding=(1, 2),
    )
    console.print(panel)


def print_clarification_box(question):
    """
    Display a clarification request inside a bordered yellow panel.

    Args:
        question: The clarification question from the AI.
    """
    panel = Panel(
        question,
        title="[bold]Clarification Needed[/bold]",
        border_style="yellow",
        box=box.ROUNDED,
        padding=(1, 2),
    )
    console.print(panel)


def print_error(message):
    """Print an error message in red."""
    console.print(f"[bold red]Error:[/bold red] {message}")


def print_success(message):
    """Print a success message in green."""
    console.print(f"[bold green]{message}[/bold green]")


def print_warning(message):
    """Print a warning message in yellow."""
    console.print(f"[bold yellow]Warning:[/bold yellow] {message}")


def print_info(message):
    """Print an informational message in dim/muted style."""
    console.print(f"[dim]{message}[/dim]")


def print_executing(command):
    """Print the execution indicator showing which command is about to run."""
    console.print(
        f"[bold cyan]>>>[/bold cyan] Executing: [bold]{command}[/bold]"
    )


def print_output(stdout, stderr):
    """
    Print command output and error streams in styled panels.

    Args:
        stdout: Standard output text from the command.
        stderr: Standard error text from the command.
    """
    if stdout and stdout.strip():
        console.print(
            Panel(
                stdout.strip(),
                title="Output",
                border_style="blue",
                box=box.SIMPLE,
            )
        )
    if stderr and stderr.strip():
        console.print(
            Panel(
                stderr.strip(),
                title="Error Output",
                border_style="red",
                box=box.SIMPLE,
            )
        )


def print_config_table(config_dict):
    """
    Print configuration values as a formatted table.

    Args:
        config_dict: Dictionary of setting names to their values.
    """
    table = Table(
        title="IntelliTerm Configuration",
        box=box.ROUNDED,
        border_style="cyan",
    )
    table.add_column("Setting", style="bold white")
    table.add_column("Value", style="green")

    for key, value in config_dict.items():
        table.add_row(key, str(value))

    console.print(table)


def print_history_table(entries):
    """
    Print command history as a formatted table.

    Args:
        entries: List of history entry dictionaries with keys
                 'query', 'command', and 'timestamp'.
    """
    if not entries:
        print_info("No command history found.")
        return

    table = Table(
        title="Command History",
        box=box.ROUNDED,
        border_style="cyan",
    )
    table.add_column("#", style="dim", width=4)
    table.add_column("Query", style="white")
    table.add_column("Command", style="green")
    table.add_column("Time", style="dim")

    for i, entry in enumerate(entries, 1):
        table.add_row(
            str(i),
            entry.get("query", ""),
            entry.get("command", ""),
            entry.get("timestamp", ""),
        )

    console.print(table)


def print_danger_warning(command, reason):
    """
    Print a prominent red warning panel for potentially destructive commands.

    Args:
        command: The dangerous command string.
        reason: Explanation of why the command is flagged as dangerous.
    """
    content = Text()
    content.append("DANGEROUS COMMAND DETECTED\n\n", style="bold red")
    content.append("Command: ", style="bold white")
    content.append(command, style="bold red")
    content.append("\n")
    content.append("Reason:  ", style="bold white")
    content.append(reason, style="yellow")

    panel = Panel(
        content,
        title="[bold red]WARNING[/bold red]",
        border_style="red",
        box=box.HEAVY,
        padding=(1, 2),
    )
    console.print(panel)


def get_spinner():
    """
    Return a Rich status spinner context manager for loading states.

    Usage:
        with ui.get_spinner():
            # do work
    """
    return console.status(
        "[bold cyan]Thinking...[/bold cyan]", spinner="dots"
    )


def prompt_input(prompt_text):
    """
    Get input from the user with a styled prompt.

    Args:
        prompt_text: The text to display before the cursor.

    Returns:
        The user's input string.
    """
    return console.input(f"[bold cyan]{prompt_text}[/bold cyan] ")


def prompt_confirm():
    """
    Ask the user to confirm, edit, or cancel a command.

    Returns:
        The user's choice as a lowercase string.
    """
    return console.input(
        "[bold]>>>[/bold] Execute? "
        "[green][Y]es[/green] "
        "[red][N]o[/red] "
        "[yellow][E]dit[/yellow] > "
    ).lower()
