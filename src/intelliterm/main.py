"""
Entry point for IntelliTerm.

Routes the 'turn' command to the appropriate handler based on
the subcommand or arguments provided by the user.

Usage:
    turn <natural language query>    Translate and execute a command
    turn shell                       Launch interactive shell
    turn config set-key <key>        Set API key
    turn config show                 Show current configuration
    turn config set-model <model>    Change AI model
    turn config power-mode on|off    Toggle power user mode
    turn history                     Show command history
    turn history clear               Clear command history
    turn uninstall                   Remove IntelliTerm from this machine
    turn --help                      Show help
    turn --version                   Show version
"""

import sys
from . import __version__
from . import config
from . import core
from . import history
from . import safety
from . import ui


HELP_TEXT = """
IntelliTerm v{version} - Natural Language Terminal

Usage:
    turn <query>                   Translate English to a shell command
    turn shell                     Launch interactive shell mode

Configuration:
    turn config set-key <key>      Set your Groq API key
    turn config show               Show current configuration
    turn config set-model <model>  Change the AI model
    turn config power-mode on|off  Toggle power user mode

History:
    turn history                   Show recent command history
    turn history clear             Clear all command history

Other:
    turn uninstall                 Remove IntelliTerm from this machine
    turn --help                    Show this help message
    turn --version                 Show version

Examples:
    turn list all files larger than 100mb
    turn find all python files modified today
    turn create a zip of the src folder
    turn show disk usage
""".format(version=__version__)


def _handle_config(args):
    """
    Handle 'turn config' subcommands.

    Supported subcommands:
        show          Display current configuration
        set-key       Save a new API key
        set-model     Change the AI model
        power-mode    Toggle power user mode on or off
    """
    if not args:
        ui.print_config_table(config.get_all_config())
        return

    subcmd = args[0].lower()

    if subcmd == "show":
        ui.print_config_table(config.get_all_config())

    elif subcmd == "set-key":
        if len(args) < 2:
            ui.print_error("Usage: turn config set-key <your-api-key>")
            return
        config.set_api_key(args[1])
        ui.print_success("API key saved successfully.")

    elif subcmd == "set-model":
        if len(args) < 2:
            ui.print_error("Usage: turn config set-model <model-name>")
            return
        config.set_model(args[1])
        ui.print_success(f"Model set to: {args[1]}")

    elif subcmd == "power-mode":
        if len(args) < 2 or args[1].lower() not in ("on", "off"):
            ui.print_error("Usage: turn config power-mode on|off")
            return
        enabled = args[1].lower() == "on"
        config.set_power_mode(enabled)
        state = "on" if enabled else "off"
        ui.print_success(f"Power User Mode: {state}")

    else:
        ui.print_error(f"Unknown config command: {subcmd}")
        ui.print_info("Available: set-key, set-model, power-mode, show")


def _handle_history(args):
    """
    Handle 'turn history' subcommands.

    With no arguments, displays the last 20 commands.
    With 'clear', deletes all history.
    """
    if args and args[0].lower() == "clear":
        history.clear_history()
        ui.print_success("Command history cleared.")
        return

    entries = history.get_entries()
    ui.print_history_table(entries)


def _handle_uninstall():
    """
    Handle 'turn uninstall'.

    Removes all configuration files from ~/.intelliterm and then
    uninstalls the Python package via pip. Requires the user to
    type 'confirm' to proceed.
    """
    ui.print_warning(
        "This will remove IntelliTerm and all its configuration "
        "from this machine."
    )
    confirm = ui.prompt_input("Type 'confirm' to proceed:")

    if confirm.strip().lower() != "confirm":
        ui.print_info("Uninstall cancelled.")
        return

    # Remove config directory
    config.remove_config()
    ui.print_info("Configuration files removed.")

    # Uninstall the package
    ui.print_info("Uninstalling package...")
    import subprocess

    result = subprocess.run(
        [sys.executable, "-m", "pip", "uninstall", "intelliterm", "-y"],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        ui.print_success("IntelliTerm has been uninstalled successfully.")
    else:
        ui.print_error(f"Failed to uninstall package: {result.stderr}")
        ui.print_info("You can manually run: pip uninstall intelliterm")


def _handle_one_shot(args):
    """
    Handle one-shot mode: translate a single natural language query
    into a shell command and execute it.

    This is the default mode when 'turn' is called with arguments
    that do not match any subcommand.

    Args:
        args: List of argument strings forming the query.
    """
    prompt = " ".join(args)

    # Verify API key
    api_key = config.get_api_key()
    if not api_key:
        ui.print_error("API key not configured.")
        ui.print_info("Run: turn config set-key <your-groq-api-key>")
        return

    # Get AI response with loading spinner
    with ui.get_spinner():
        response = core.get_ai_response(prompt)

    if response.get("status") == "error":
        ui.print_error(response.get("message", "Unknown error"))
        return

    # Handle clarification
    if response.get("status") == "incomplete":
        question = response.get("question", "Please provide more details.")
        ui.print_clarification_box(question)
        clarification = ui.prompt_input(">>>")

        if not clarification.strip():
            ui.print_info("Action cancelled.")
            return

        combined_prompt = (
            f"Original request was '{prompt}'. "
            f"The user provided this missing info: '{clarification}'"
        )
        with ui.get_spinner():
            response = core.get_ai_response(combined_prompt)

        if response.get("status") != "success":
            msg = response.get(
                "message",
                response.get("question", "Could not process request."),
            )
            ui.print_error(msg)
            return

    if response.get("status") != "success":
        return

    command = response.get("command", "")
    explanation = response.get("explanation", "")
    power_mode = config.get_power_mode()

    # Display the suggestion
    ui.print_command_box(command, explanation)

    # Safety check always runs
    is_dangerous, danger_reason = safety.check_safety(command)
    if is_dangerous:
        ui.print_danger_warning(command, danger_reason)
        confirm = ui.prompt_input(
            "Type 'confirm' to proceed, or anything else to cancel:"
        )
        if confirm.strip().lower() != "confirm":
            ui.print_info("Action cancelled.")
            return
    elif not power_mode:
        # Normal mode: ask for confirmation
        choice = ui.prompt_confirm()
        if choice in ("n", "no"):
            ui.print_info("Action cancelled.")
            return
        if choice not in ("y", "yes", ""):
            ui.print_info("Action cancelled.")
            return

    # Execute
    from . import executor

    ui.print_executing(command)
    stdout, stderr = executor.handle_execution(command)
    ui.print_output(stdout, stderr)

    # Save to history
    history.save_entry(prompt, command)


def app():
    """
    Main entry point for the 'turn' command.

    Parses sys.argv and routes to the appropriate handler based
    on the first argument. If no arguments match a known subcommand,
    all arguments are treated as a natural language query.
    """
    args = sys.argv[1:]

    # No arguments: show help
    if not args:
        print(HELP_TEXT)
        return

    first = args[0].lower()

    # Flags
    if first in ("--help", "-h"):
        print(HELP_TEXT)
        return

    if first in ("--version", "-v"):
        print(f"IntelliTerm v{__version__}")
        return

    # Subcommands
    if first == "shell":
        from . import shell

        shell.run()
        return

    if first == "config":
        _handle_config(args[1:])
        return

    if first == "history":
        _handle_history(args[1:])
        return

    if first == "uninstall":
        _handle_uninstall()
        return

    # Default: treat everything as a natural language query
    _handle_one_shot(args)
