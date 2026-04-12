"""
Command history for IntelliTerm.

Stores executed commands with timestamps in a JSON file at
~/.intelliterm/history.json. Provides functions to save, retrieve,
and clear history entries. History is capped at 100 entries to
prevent unbounded growth.
"""

import json
from datetime import datetime
from . import config


def _load_history():
    """
    Load the history file and return its contents as a list.

    Returns an empty list if the file does not exist or cannot
    be parsed.
    """
    history_file = config.HISTORY_FILE
    if not history_file.exists():
        return []
    try:
        with open(history_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def _save_history(entries):
    """
    Write the history entries list to the history file.

    Creates the config directory if it does not exist.

    Args:
        entries: List of history entry dictionaries to write.
    """
    config._ensure_config_dir()
    with open(config.HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)


def save_entry(query, command):
    """
    Append a new entry to the command history.

    Each entry records the original query, the generated command,
    and the current timestamp. The history file is capped at 100
    entries; older entries are discarded when the limit is reached.

    Args:
        query: The natural language query the user typed.
        command: The shell command that was generated and executed.
    """
    entries = _load_history()
    entries.append({
        "query": query,
        "command": command,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    })
    # Keep only the last 100 entries
    entries = entries[-100:]
    _save_history(entries)


def get_entries(limit=20):
    """
    Return the most recent history entries.

    Args:
        limit: Maximum number of entries to return. Defaults to 20.

    Returns:
        A list of history entry dictionaries, each containing
        'query', 'command', and 'timestamp' keys.
    """
    entries = _load_history()
    return entries[-limit:]


def clear_history():
    """Delete all command history by writing an empty list."""
    _save_history([])
