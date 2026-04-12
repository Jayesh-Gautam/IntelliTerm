# IntelliTerm

IntelliTerm is a productivity-first, open-source command-line tool designed to bridge the gap between natural language and terminal execution. Built for developers who want to spend less time searching for obscure shell syntax and more time writing code, IntelliTerm uses high-speed AI to translate your intent into precise, executable commands.

### The Philosophy
The terminal is the most powerful tool in a developer's arsenal, but its steep learning curve and inconsistent syntax across operating systems can be a bottleneck. IntelliTerm doesn't replace the shell; it augments it. By providing a hybrid interface that understands both standard shell commands and plain English, it empowers developers to master their environment without the cognitive load of memorizing every flag for every utility.

---

## Quick Start

### One-Command Install

**Windows:**
```
git clone https://github.com/Jayesh-Gautam/IntelliTerm.git
cd IntelliTerm
install.bat
```

**Linux / macOS:**
```
git clone https://github.com/Jayesh-Gautam/IntelliTerm.git
cd IntelliTerm
chmod +x install.sh && ./install.sh
```

### Set Your API Key

Get a free key from the [Groq Console](https://console.groq.com/keys),
then run:

```
turn config set-key YOUR_API_KEY
```

### Start Using It

```
turn list all files larger than 100mb
turn find all python files modified today
turn create a zip archive of the src folder
turn show disk usage by folder
```

---

## Features

**Natural Language Commands** --
Type what you want in plain English. IntelliTerm translates it into
the correct shell command for your OS (Windows CMD or Bash).

**Two Modes** --
Use `turn <query>` for quick one-shot commands, or `turn shell` for
a full interactive session.

**Command Review** --
Every AI-generated command is shown with an explanation before
execution. You choose: Yes, No, or Edit.

**AI-Powered Editing** --
Not happy with the suggestion? Choose Edit and describe what to
change in English. The AI revises the command.

**Dangerous Command Detection** --
Commands like `rm -rf`, `format`, or `del /s` trigger a red warning
and require explicit confirmation, even in Power User Mode.

**Command History** --
All executed commands are saved. View them with `turn history` or
clear them with `turn history clear`.

**Power User Mode** --
Skip the confirmation prompt and execute AI commands instantly.
Enable with: `turn config power-mode on`

**Direct Command Passthrough** --
Standard commands like `git`, `pip`, `ls`, `dir`, `cd` are detected
and executed immediately without AI translation.

**Cross-Platform** --
Automatically detects Windows, macOS, or Linux and generates the
appropriate commands.

**Easy Uninstall** --
Remove everything cleanly with: `turn uninstall`

---

## Command Reference

| Command | Description |
|---|---|
| `turn <query>` | Translate and execute a single command |
| `turn shell` | Launch interactive shell mode |
| `turn config set-key <key>` | Set your Groq API key |
| `turn config show` | Show current configuration |
| `turn config set-model <model>` | Change the AI model |
| `turn config power-mode on\|off` | Toggle power user mode |
| `turn history` | Show recent command history |
| `turn history clear` | Clear all history |
| `turn uninstall` | Remove IntelliTerm completely |
| `turn --help` | Show help |
| `turn --version` | Show version |

---

## Example: One-Shot Mode

```
C:\Users\You> turn create a new folder called docs

+-------------------------------------------------+
| Command Suggestion                              |
|                                                 |
| Command:     mkdir docs                         |
| Explanation: Creates a new directory named docs. |
+-------------------------------------------------+

>>> Execute? [Y]es [N]o [E]dit > y
>>> Executing: mkdir docs
```

## Example: Interactive Shell

```
C:\Users\You> turn shell

 ___ _  _ _____ ___ _    _    ___ _____ ___ ___ __  __
|_ _| \| |_   _| __| |  | |  |_ _|_   _| __| _ \  \/  |
 | || .` | | | | _|| |__| |__ | |  | | | _||   / |\/| |
|___|_|\_| |_| |___|____|____|___| |_| |___|_|_\_|  |_|

  Natural Language Terminal v2.0
  Type a command in plain English or use standard shell commands.
  Type 'exit' or 'quit' to close.

C:\Users\You> git status
>>> Direct command detected. Executing...

C:\Users\You> show me all jpg files larger than 5mb
>>> Thinking...
+-------------------------------------------------+
| Command Suggestion                              |
|                                                 |
| Command:     forfiles /S /M *.jpg ...           |
| Explanation: Searches for JPG files over 5MB.   |
+-------------------------------------------------+
>>> Execute? [Y]es [N]o [E]dit >
```

---

## Configuration

All configuration is stored in `~/.intelliterm/config.env`. You can
edit this file directly or use the `turn config` commands.

Available settings:

| Setting | Default | Description |
|---|---|---|
| GROQ_API_KEY | (none) | Your Groq API key |
| GROQ_MODEL | llama-3.3-70b-versatile | The AI model to use |
| POWER_USER_MODE | false | Skip confirmation prompts |

---

## Technologies

- **Python 3.8+**
- **Groq API** -- Fast LLM inference
- **Rich** -- Terminal colors, panels, spinners, and tables
- **python-dotenv** -- Environment file management

---

## Uninstall

To completely remove IntelliTerm and all its configuration:

```
turn uninstall
```

Or manually:

```
pip uninstall intelliterm
```

Then delete the config folder at `~/.intelliterm/`.

---

## License

MIT
