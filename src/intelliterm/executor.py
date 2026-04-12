"""
Command execution for IntelliTerm.

Handles running shell commands via subprocess and special cases like
the 'cd' command which must be handled within the Python process.
Also provides direct command detection to bypass the AI for standard
shell commands.
"""

import platform
import subprocess
import os


# Commands that are executed directly without AI translation.
# These are common shell commands that users type out of habit.
# Add more entries here as needed.
DIRECT_COMMANDS = {
    # File system
    "cd", "dir", "ls", "mkdir", "rmdir", "del", "rm", "copy",
    "move", "ren", "mv", "cls", "clear", "echo", "pwd", "cat",
    "type", "touch", "find", "grep", "head", "tail", "chmod",
    "chown", "ln",
    # Package managers and dev tools
    "pip", "pip3", "git", "python", "python3", "code", "gcc",
    "node", "npm", "npx", "docker", "docker-compose",
    # Network and system
    "curl", "wget", "ssh", "scp", "ping", "ipconfig", "ifconfig",
    "netstat", "tar", "zip", "unzip", "make", "cmake",
}


def is_direct_command(prompt):
    """
    Check if the user's input starts with a known shell command.

    Direct commands are executed immediately without AI translation
    for maximum speed and familiar behavior. Only the first word
    of the input is checked against the known commands list.

    Args:
        prompt: The raw user input string.

    Returns:
        True if the first word is a recognized shell command.
    """
    first_word = prompt.strip().split(" ")[0].lower()
    return first_word in DIRECT_COMMANDS


def execute_command(command):
    """
    Run a shell command via subprocess and return its output.

    Uses shell=True on all platforms for consistency with how users
    expect commands to behave (pipe support, environment variable
    expansion, etc.).

    Args:
        command: The command string to execute.

    Returns:
        A tuple of (stdout, stderr) strings.
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            text=True,
            capture_output=True,
            check=False,
            cwd=os.getcwd(),
        )
        return result.stdout, result.stderr
    except FileNotFoundError:
        first_word = command.split()[0] if command.split() else command
        return "", (
            f"Command not found: '{first_word}'. "
            f"Make sure it is installed and in your PATH."
        )
    except Exception as e:
        return "", f"An unexpected error occurred: {e}"


def handle_cd(path):
    """
    Handle the 'cd' command by changing the Python process working
    directory.

    Standard subprocess execution cannot change the parent process
    directory, so 'cd' must be handled specially via os.chdir().
    On Windows, the '/d' flag is stripped automatically since
    os.chdir handles cross-drive changes natively.

    To support persistent directory changes in the parent shell,
    a successful 'cd' writes the target path to ~/.intelliterm/last_cd
    which can be picked up by a shell wrapper.

    Args:
        path: The target directory path.

    Returns:
        A tuple of (success: bool, message: str).
    """
    try:
        # On Windows, strip the '/d' flag if present
        if platform.system() == "Windows" and path.lower().startswith("/d "):
            path = path[3:]

        path = path.strip().strip('"').strip("'")
        os.chdir(path)

        # Write to last_cd hook for shell wrappers
        from pathlib import Path
        hook_dir = Path.home() / ".intelliterm"
        hook_dir.mkdir(parents=True, exist_ok=True)
        hook_path = hook_dir / "last_cd"
        with open(hook_path, "w", encoding="utf-8") as f:
            f.write(os.getcwd())

        return True, f"Changed directory to: {os.getcwd()}"
    except FileNotFoundError:
        return False, f"Directory not found: {path}"
    except PermissionError:
        return False, f"Permission denied: {path}"
    except Exception as e:
        return False, f"Failed to change directory: {e}"


def handle_execution(command):
    """
    Execute a command, routing 'cd' to the special handler and
    everything else to subprocess execution.

    This is the main entry point for command execution. It inspects
    the command to determine if it needs special handling (cd) or
    can be passed directly to the shell.

    Args:
        command: The command string to execute.

    Returns:
        A tuple of (stdout, stderr) strings. For cd commands,
        stdout contains the success message and stderr is empty
        on success.
    """
    stripped = command.strip()

    if stripped.lower().startswith("cd ") or stripped.lower() == "cd":
        parts = stripped.split(" ", 1)
        if len(parts) < 2:
            return "", "'cd' requires a directory path."
        success, message = handle_cd(parts[1])
        if success:
            return message, ""
        else:
            return "", message
    else:
        return execute_command(command)
