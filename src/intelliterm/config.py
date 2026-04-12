"""
Configuration management for IntelliTerm.

Handles loading and saving configuration from multiple sources:
1. Project-local .env file (for development)
2. User-level config at ~/.intelliterm/config.env (for global installs)
3. Environment variables (as fallback)

Priority order: .env > ~/.intelliterm/config.env > environment variables.
"""

import os
import shutil
from pathlib import Path
from dotenv import load_dotenv, set_key


# User-level config directory
CONFIG_DIR = Path.home() / ".intelliterm"
CONFIG_FILE = CONFIG_DIR / "config.env"
HISTORY_FILE = CONFIG_DIR / "history.json"

# Defaults
DEFAULT_MODEL = "llama-3.3-70b-versatile"
DEFAULT_POWER_MODE = False


def _ensure_config_dir():
    """Create the config directory if it does not exist."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def _load_env():
    """
    Load environment variables from .env files in priority order.

    Checks the project-local .env first (overrides everything), then
    falls back to the user-level config file. System environment
    variables act as the final fallback.
    """
    # User-level config (loaded first so local .env can override)
    if CONFIG_FILE.exists():
        load_dotenv(CONFIG_FILE, override=False)

    # Project-local .env (highest priority, overrides user config)
    local_env = Path.cwd() / ".env"
    if local_env.exists():
        load_dotenv(local_env, override=True)


def get_api_key():
    """Return the Groq API key from configuration."""
    _load_env()
    return os.getenv("GROQ_API_KEY", "")


def get_model():
    """Return the AI model name from configuration."""
    _load_env()
    return os.getenv("GROQ_MODEL", DEFAULT_MODEL)


def get_power_mode():
    """Return whether power user mode is enabled."""
    _load_env()
    value = os.getenv("POWER_USER_MODE", "false")
    return value.lower() in ("true", "1", "yes")


def set_api_key(key):
    """Save the API key to the user-level config file."""
    _ensure_config_dir()
    if not CONFIG_FILE.exists():
        CONFIG_FILE.touch()
    set_key(str(CONFIG_FILE), "GROQ_API_KEY", key)


def set_model(model):
    """Save the model name to the user-level config file."""
    _ensure_config_dir()
    if not CONFIG_FILE.exists():
        CONFIG_FILE.touch()
    set_key(str(CONFIG_FILE), "GROQ_MODEL", model)


def set_power_mode(enabled):
    """Save the power mode setting to the user-level config file."""
    _ensure_config_dir()
    if not CONFIG_FILE.exists():
        CONFIG_FILE.touch()
    set_key(str(CONFIG_FILE), "POWER_USER_MODE", str(enabled).lower())


def get_all_config():
    """
    Return a dictionary of all current configuration values.

    The API key is partially masked for display safety.
    """
    api_key = get_api_key()
    masked_key = ""
    if api_key:
        if len(api_key) > 12:
            masked_key = api_key[:8] + "..." + api_key[-4:]
        else:
            masked_key = "***"

    return {
        "API Key": masked_key or "(not set)",
        "Model": get_model(),
        "Power User Mode": "on" if get_power_mode() else "off",
        "Config Location": str(CONFIG_FILE),
    }


def remove_config():
    """
    Remove all IntelliTerm configuration files.

    Deletes the entire ~/.intelliterm directory, including config
    and history files. Used by the uninstall command.
    """
    if CONFIG_DIR.exists():
        shutil.rmtree(CONFIG_DIR)
