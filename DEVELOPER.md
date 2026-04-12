# Developer Documentation

This document explains the architecture, module responsibilities,
and data flow of IntelliTerm to help future contributors understand
and extend the codebase.

---

## Project Structure

```
IntelliTerm/
    pyproject.toml          -- Package config, registers 'turn' command
    requirements.txt        -- Python dependencies
    .env.example            -- Template for user configuration
    .gitignore              -- Git ignore rules
    install.bat             -- Windows one-click installer
    install.sh              -- Linux/macOS one-click installer
    README.md               -- User-facing documentation
    DEVELOPER.md            -- This file

    src/
        intelliterm/
            __init__.py     -- Package version
            main.py         -- Entry point and command routing
            core.py         -- AI interaction (Groq API, prompts)
            executor.py     -- Shell command execution
            shell.py        -- Interactive REPL mode
            config.py       -- Configuration management
            ui.py           -- Terminal output (Rich library)
            safety.py       -- Dangerous command detection
            history.py      -- Command history storage
```

---

## Architecture Overview

IntelliTerm is an installable Python package. When installed via
`pip install .`, the `turn` command is registered globally through
the `[project.scripts]` entry in `pyproject.toml`. This maps the
`turn` command to the `app()` function in `main.py`.

The package follows a modular design where each file has a single
responsibility. No module directly prints to the terminal; all
output goes through `ui.py` for consistent styling.

---

## Module Responsibilities

### main.py -- Entry Point

The `app()` function is called whenever the user runs `turn`.
It parses `sys.argv` and routes to the correct handler:

- No arguments -> show help text
- `--help`, `--version` -> print info and exit
- `shell` -> launch `shell.run()`
- `config` -> delegate to `_handle_config()`
- `history` -> delegate to `_handle_history()`
- `uninstall` -> delegate to `_handle_uninstall()`
- Anything else -> treat as a natural language query

The one-shot handler (`_handle_one_shot`) follows this flow:
1. Call `core.get_ai_response()` with a spinner
2. Handle clarification if status is "incomplete"
3. Display the command suggestion via `ui.print_command_box()`
4. Check safety via `safety.check_safety()`
5. Ask for user confirmation (unless Power User Mode)
6. Execute via `executor.handle_execution()`
7. Save to `history.save_entry()`

### core.py -- AI Logic

Contains all Groq API interaction:

- `get_system_prompt()` -- Builds the instruction prompt that tells
  the AI to return structured JSON. Includes the current OS type
  and working directory.
- `get_ai_response(prompt)` -- Sends user input to the Groq API
  and returns a parsed dictionary.
- `get_edit_response(original, current, edit)` -- Constructs a
  revision prompt when the user chooses "Edit".
- `parse_ai_response(raw_text)` -- Extracts JSON from the AI
  response using three fallback strategies: direct parse, markdown
  code block extraction, and raw brace matching.

The AI is instructed to return JSON in one of two formats:
- Success: `{"status": "success", "command": "...", "explanation": "..."}`
- Incomplete: `{"status": "incomplete", "question": "..."}`

### executor.py -- Command Execution

Handles running commands and detecting direct shell commands:

- `is_direct_command(prompt)` -- Checks the first word against a
  set of known commands (git, pip, ls, etc.). If matched, the
  command runs without AI translation.
- `execute_command(command)` -- Runs via `subprocess.run()` with
  `shell=True` and returns (stdout, stderr).
- `handle_cd(path)` -- Special handler for `cd` since subprocess
  cannot change the parent process directory. Uses `os.chdir()`.
- `handle_execution(command)` -- Routes to `handle_cd()` or
  `execute_command()` based on the command.

### shell.py -- Interactive Mode

The REPL (Read-Eval-Print Loop) launched by `turn shell`:

- `run()` -- Main loop. Displays the banner, reads input, and
  decides whether to run directly or send to the AI.
- `_handle_ai_query(prompt)` -- Full AI pipeline including
  clarification handling.
- `_confirm_and_execute(prompt, command, explanation)` -- The
  Y/N/E confirmation loop with AI-powered editing.

### config.py -- Configuration

Manages settings from multiple sources with this priority:
1. `.env` file in the current directory (highest priority)
2. `~/.intelliterm/config.env` (user-level config)
3. System environment variables (fallback)

The `turn config` commands write to `~/.intelliterm/config.env`.

Key functions:
- `get_api_key()`, `get_model()`, `get_power_mode()` -- Readers
- `set_api_key()`, `set_model()`, `set_power_mode()` -- Writers
- `get_all_config()` -- Returns all settings with masked API key
- `remove_config()` -- Deletes `~/.intelliterm/` (for uninstall)

### ui.py -- Terminal UI

All terminal output is centralized here using the Rich library:

- `print_banner()` -- ASCII art header for interactive mode
- `print_command_box()` -- Green-bordered panel for suggestions
- `print_clarification_box()` -- Yellow panel for AI questions
- `print_danger_warning()` -- Red panel for dangerous commands
- `print_output()` -- Styled panels for command stdout/stderr
- `print_config_table()` -- Formatted table for settings
- `print_history_table()` -- Formatted table for past commands
- `get_spinner()` -- Context manager for loading animation
- `prompt_input()` -- Styled input prompt
- `prompt_confirm()` -- Y/N/E choice prompt

### safety.py -- Danger Detection

Contains a list of compiled regex patterns that match destructive
commands (rm -rf, format, del /s, dd, DROP TABLE, etc.). Each
pattern has a human-readable explanation.

- `check_safety(command)` -- Returns (is_dangerous, reason).
  Dangerous commands force explicit confirmation even in Power
  User Mode.

To add new dangerous patterns, append a tuple to
`DANGEROUS_PATTERNS`:

```python
(re.compile(r"\byour_pattern\b", re.IGNORECASE),
 "Explanation of why this is dangerous."),
```

### history.py -- Command History

Stores entries in `~/.intelliterm/history.json` as a JSON array.
Each entry has three fields: query, command, timestamp.

- `save_entry(query, command)` -- Appends and caps at 100 entries.
- `get_entries(limit=20)` -- Returns the most recent entries.
- `clear_history()` -- Writes an empty list.

---

## Data Flow Diagram

One-shot mode (`turn list large files`):

```
User Input
    |
    v
main.app()  -->  parse sys.argv
    |
    v
core.get_ai_response()  -->  Groq API
    |
    v
core.parse_ai_response()  -->  extract JSON
    |
    v
safety.check_safety()  -->  regex scan
    |
    v
ui.print_command_box()  -->  show suggestion
    |
    v
ui.prompt_confirm()  -->  Y / N / E
    |
    v
executor.handle_execution()  -->  subprocess.run()
    |
    v
ui.print_output()  -->  display results
    |
    v
history.save_entry()  -->  write to JSON
```

---

## Development Setup

Clone the repository and install in editable mode:

```
git clone https://github.com/Jayesh-Gautam/IntelliTerm.git
cd IntelliTerm
pip install -e .
```

Editable mode means the `turn` command reflects code changes
immediately without reinstalling.

Create a `.env` file from the template:

```
copy .env.example .env
```

Edit `.env` and add your Groq API key.

---

## Adding a New Subcommand

1. Add a handler function `_handle_<name>(args)` in `main.py`.
2. Add a routing check in the `app()` function.
3. Update the `HELP_TEXT` string in `main.py`.
4. Update the command reference table in `README.md`.

---

## Adding a New Direct Command

To make IntelliTerm recognize a new command for direct execution
(bypassing AI), add it to the `DIRECT_COMMANDS` set in
`executor.py`.

---

## Testing

After making changes, verify the following:

```
turn --help              # Help text displays correctly
turn --version           # Version number displays
turn config show         # Configuration table renders
turn config set-key test # Key is saved
turn history             # History table renders
turn shell               # Interactive mode starts
```

For AI-dependent features, ensure your API key is configured and
test with simple queries like:

```
turn create an empty file called test.txt
turn list files in the current directory
```
