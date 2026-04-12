"""
Dangerous command detection for IntelliTerm.

Scans commands against a list of known destructive patterns and
warns the user before execution. Even in Power User Mode, dangerous
commands require explicit confirmation to prevent accidental damage.
"""

import re


# Each entry is a tuple of (compiled_regex, human-readable reason).
# Patterns are checked case-insensitively against the full command
# string. To add new dangerous patterns, append a tuple to this list.
DANGEROUS_PATTERNS = [
    (
        re.compile(r"\brm\s+(-[a-z]*r[a-z]*\s+|-[a-z]*f[a-z]*\s+)", re.IGNORECASE),
        "Recursive or forced file deletion can permanently destroy data.",
    ),
    (
        re.compile(r"\brm\s+-rf\s+[/\\]", re.IGNORECASE),
        "This will recursively delete from the root directory.",
    ),
    (
        re.compile(r"\bdel\s+/[sq]", re.IGNORECASE),
        "Quiet or recursive deletion on Windows can permanently destroy data.",
    ),
    (
        re.compile(r"\brmdir\s+/s", re.IGNORECASE),
        "Recursive directory removal can permanently destroy data.",
    ),
    (
        re.compile(r"\bformat\s+[a-z]:", re.IGNORECASE),
        "Formatting a drive will erase all data on it.",
    ),
    (
        re.compile(r"\bmkfs\b", re.IGNORECASE),
        "Creating a filesystem will erase all data on the target device.",
    ),
    (
        re.compile(r"\bdd\s+", re.IGNORECASE),
        "The dd command writes raw data to devices and can overwrite entire disks.",
    ),
    (
        re.compile(r">\s*/dev/sda", re.IGNORECASE),
        "Writing directly to a block device can destroy the filesystem.",
    ),
    (
        re.compile(r"\bdrop\s+(table|database)\b", re.IGNORECASE),
        "This SQL command will permanently delete database objects.",
    ),
    (
        re.compile(r":\(\)\{\s*:\|:&\s*\};:", re.IGNORECASE),
        "This is a fork bomb that will crash the system.",
    ),
    (
        re.compile(r"\bshutdown\b", re.IGNORECASE),
        "This will shut down or restart the computer.",
    ),
    (
        re.compile(r"\breboot\b", re.IGNORECASE),
        "This will restart the computer.",
    ),
    (
        re.compile(r"\breg\s+delete\b", re.IGNORECASE),
        "Deleting registry keys can break the operating system.",
    ),
]


def check_safety(command):
    """
    Check a command against known dangerous patterns.

    Iterates through all patterns in DANGEROUS_PATTERNS and returns
    on the first match. Commands that do not match any pattern are
    considered safe.

    Args:
        command: The command string to check.

    Returns:
        A tuple of (is_dangerous: bool, reason: str).
        If not dangerous, reason is an empty string.
    """
    for pattern, reason in DANGEROUS_PATTERNS:
        if pattern.search(command):
            return True, reason
    return False, ""
