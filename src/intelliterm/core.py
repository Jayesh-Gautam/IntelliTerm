"""
AI interaction logic for IntelliTerm.

Handles communication with the Groq API, including prompt construction,
API calls, and response parsing. This module contains all AI-related
functionality shared between one-shot and interactive modes.
"""

import platform
import os
import json
from groq import Groq
from . import config


def _get_client():
    """
    Create and return a Groq API client.

    Returns None if no API key is configured, allowing callers
    to provide a helpful error message.
    """
    api_key = config.get_api_key()
    if not api_key:
        return None
    return Groq(api_key=api_key)


def get_system_prompt():
    """
    Build the system prompt for the AI based on the current OS
    and working directory.

    The prompt instructs the AI to behave as a command-line translator
    that outputs structured JSON responses. It includes OS-specific
    rules (CMD vs Bash) and formatting requirements.

    Returns:
        A string containing the full system prompt.
    """
    os_name = platform.system()
    shell_type = "CMD (Command Prompt)" if os_name == "Windows" else "Bash"
    cwd = os.getcwd()

    prompt = f"""
    You are an expert command-line assistant. Your task is to convert
    a user's natural language request into a single, executable shell
    command for the {shell_type} shell.

    The user's current working directory is: {cwd}

    RULES:
    1. If the request is clear and contains all necessary information,
       generate the command. The response MUST be a JSON object with
       three keys:
       - "status": "success"
       - "command": The generated command string.
       - "explanation": A brief, user-friendly explanation of what
         the command does.
       Example: {{"status": "success", "command": "mkdir my_folder",
       "explanation": "Creates a new directory named my_folder."}}

    2. If the request is ambiguous or missing information, request
       the missing information. The response MUST be a JSON object
       with two keys:
       - "status": "incomplete"
       - "question": A formal, direct statement of what information
         is needed.
       Example: {{"status": "incomplete", "question": "A folder name
       is required. Please provide the name for the new folder."}}

    3. Do not add any text or explanation outside of the JSON object.
       Your entire response must be only the raw JSON object.

    4. The command should be for the current directory unless the user
       specifies a different path.

    5. If the user asks to open, view, or edit a file, use
       `code [filename]`.

    6. Special rule for Windows directory changes: when changing to a
       directory on a DIFFERENT drive, always use `cd /d`.
       Example: `cd /d D:\\projects`.

    7. CRITICAL: In Windows CMD shell, do NOT use symbols like `>=`, `<=`,
       `>`, `<` for numeric comparisons in 'if' statements. These are
       interpreted as redirection operators. ALWAYS use the mnemonic
       operators: `GEQ` (Greater or Equal), `LEQ` (Less or Equal),
       `GTR` (Greater Than), `LSS` (Less Than), `EQU` (Equal),
       `NEQ` (Not Equal).
       Example: `if %~zx GEQ 100000000 echo %x`

    8. RECURSION: By default, file search or listing requests (e.g., "find
       all python files") should be performed RECURSIVELY (searching
       subdirectories) unless the user explicitly says "in this folder
       only".

    9. POWERSHELL ON WINDOWS: For complex Windows operations (like
       filtering files by size, date, or advanced patterns), prefer
       generating a `powershell` command over a complex CMD one-liner.
       PowerShell is more reliable and robust for these tasks.
       Example for files > 100MB: `powershell "Get-ChildItem -Recurse | Where-Object {$_.Length -gt 100mb} | Select-Object FullName"`
    """
    return prompt


def get_ai_response(user_prompt):
    """
    Send a natural language prompt to the Groq API and return the
    parsed response.

    This is the primary entry point for AI interaction. It constructs
    the full message array (system + user), calls the API, and parses
    the JSON response.

    Args:
        user_prompt: The user's natural language request string.

    Returns:
        A dictionary with at minimum a 'status' key. On success,
        includes 'command' and 'explanation'. On incomplete requests,
        includes 'question'. On failure, includes 'message'.
    """
    client = _get_client()
    if client is None:
        return {
            "status": "error",
            "message": (
                "API key not configured. "
                "Run: turn config set-key <your-key>"
            ),
        }

    system_prompt = get_system_prompt()
    model = config.get_model()

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f'User Request: "{user_prompt}"'},
    ]

    try:
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.2,
            max_tokens=1024,
            stream=False,
        )
        response_text = completion.choices[0].message.content
        return parse_ai_response(response_text)
    except Exception as e:
        return {"status": "error", "message": f"API request failed: {e}"}


def get_edit_response(original_prompt, current_command, edit_request):
    """
    Ask the AI to revise a previously generated command based on
    user feedback.

    Constructs a new prompt that includes the original request, the
    current command, and the user's edit description, then sends it
    through the standard AI pipeline.

    Args:
        original_prompt: The user's original natural language request.
        current_command: The command that was previously generated.
        edit_request: The user's description of what to change.

    Returns:
        A parsed response dictionary (same format as get_ai_response).
    """
    edit_prompt = (
        f"The user's original request was: '{original_prompt}'.\n"
        f"The generated command was: `{current_command}`.\n"
        f"The user wants to change something. "
        f"Their change request is: '{edit_request}'\n\n"
        f"Generate a new command based on the original request "
        f"and the change."
    )
    return get_ai_response(edit_prompt)


def parse_ai_response(raw_text):
    """
    Extract and parse a JSON object from the AI's raw response text.

    The AI sometimes wraps JSON in markdown code blocks or adds extra
    text around it. This function handles those cases by trying
    multiple extraction strategies:
    1. Direct JSON parse of the full text
    2. Extract from ```json ... ``` code blocks
    3. Find the first { to last } substring

    Args:
        raw_text: The raw string response from the AI.

    Returns:
        A parsed dictionary on success, or a dictionary with
        status 'error' and a 'message' key on failure.
    """
    # Strategy 1: Direct parse
    try:
        return json.loads(raw_text.strip())
    except json.JSONDecodeError:
        pass

    # Strategy 2: Extract from markdown code block
    if "```json" in raw_text:
        try:
            json_part = raw_text.split("```json")[1].split("```")[0]
            return json.loads(json_part.strip())
        except (json.JSONDecodeError, IndexError):
            pass

    # Strategy 3: Find raw JSON boundaries
    if "{" in raw_text and "}" in raw_text:
        try:
            start = raw_text.find("{")
            end = raw_text.rfind("}") + 1
            return json.loads(raw_text[start:end])
        except json.JSONDecodeError:
            pass

    return {
        "status": "error",
        "message": f"Failed to parse AI response: {raw_text[:200]}",
    }
