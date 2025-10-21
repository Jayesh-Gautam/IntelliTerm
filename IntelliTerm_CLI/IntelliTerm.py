import platform
import subprocess
import os
import sys  # <-- ADDED THIS
from groq import Groq
import json

# --- Configuration ---
API_KEY = "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" # Your key
POWER_USER_MODE = True # Set to True to skip confirmation

if not API_KEY:
    print("------------------------------------------------------------------")
    print("Groq API Key not found!")
    print("Please paste your Groq API key in the script or set it as an environment variable.")
    print("------------------------------------------------------------------")
    exit()

client = Groq(api_key=API_KEY)

def handle_execution(command):
    """
    Handles the actual execution of a command, including the special case for 'cd'.
    Returns the new working directory if it changed, otherwise None.
    """
    if command.strip().lower().startswith("cd "):
        try:
            path = command.strip().split(" ", 1)[1]
            if platform.system() == "Windows" and path.lower().startswith("/d "):
                path = path[3:]
            os.chdir(path)
            # For this tool model, we just print the new directory.
            # The *real* terminal's directory won't change, as this is a sub-process.
            # This is a limitation of this model.
            # A more complex solution involves writing a 'cd' command back to a batch file for the parent shell to execute.
            # For now, we'll just execute it and inform the user.
            print(f"--> Directory changed to: {os.getcwd()} (within this script's process)")
            print(f"--> NOTE: Your main terminal is still in the old directory. Run the 'cd' command directly for a persistent change.")
            
        except FileNotFoundError:
            print(f"Error: Directory not found: {path}")
        except IndexError:
            print("Error: 'cd' command requires a directory path.")
    else:
        execute_command(command)
    
    return None

def confirm_and_execute(original_prompt, command, explanation):
    """
    Displays the command, asks for confirmation (Y/N/E), and handles AI-powered edits.
    """
    current_command = command
    current_explanation = explanation

    while True:
        print("\n┌─ AI-Powered Terminal " + "─" * 53)
        print(f"│\n│ Command:     {current_command}")
        print(f"│ Explanation: {current_explanation}\n│")
        print("└" + "─" * 74)

        choice = input("--> Execute? [Y]es, [N]o, [E]dit > ").lower()

        if choice in ['y', 'yes', '']:
            break

        elif choice in ['n', 'no']:
            print("--> Action cancelled.")
            return None

        elif choice in ['e', 'edit']:
            modification_request = input("--> Edit: ")
            if not modification_request:
                print("--> Edit cancelled, no change described.")
                continue

            edit_prompt = (
                f"The user's original request was: '{original_prompt}'.\n"
                f"The generated command was: `{current_command}`.\n"
                f"The user now wants to change something. Their change request is: '{modification_request}'\n\n"
                f"Generate a new command based on the original request and the change."
            )
            
            ai_response_str = get_ai_response(edit_prompt)
            
            try:
                ai_response = json.loads(ai_response_str)
                if ai_response.get("status") == "success":
                    current_command = ai_response.get("command")
                    current_explanation = ai_response.get("explanation")
                else:
                    print(f"--> AI could not process the edit: {ai_response.get('message', 'Unknown error')}")
            except json.JSONDecodeError:
                print(f"--> AI returned an invalid format for the edit. Raw Response: {ai_response_str}")
            
            continue

        else:
            print("--> Invalid choice. Please enter Y, N, or E.")

    print(f"--> Executing: `{current_command}`")
    return handle_execution(current_command)

def get_system_prompt():
    """Determines the current OS and returns the appropriate system prompt for the AI."""
    os_name = platform.system()
    
    if os_name == "Windows":
        shell_type = "CMD (Command Prompt)"
    else: # Linux, macOS, etc.
        shell_type = "Bash"

    prompt = f"""
    You are an expert command-line assistant. Your task is to convert a user's natural language request
    into a single, executable shell command for the {shell_type} shell.
    The user's current working directory is: {os.getcwd()}

    RULES:
    1.  First, analyze the user's request.
    2.  If the request is clear, generate the command. The response MUST be a JSON object with three keys:
        - "status": "success"
        - "command": The generated command string.
        - "explanation": A brief, user-friendly explanation of what the command does.
        Example: {{"status": "success", "command": "mkdir my_folder", "explanation": "This command creates a new directory named 'my_folder'."}}

    3.  If the request is ambiguous or missing information, you MUST request the missing information.
        The response must be formal, direct, and state what is needed.
        The response MUST be a JSON object with two keys:
        - "status": "incomplete"
        - "question": The information request for the user.
        Example: {{"status": "incomplete", "question": "A folder name is required. Please provide the name for the new folder."}}

    4.  Do not add any text or explanation outside of the JSON object.
    5.  The command should be for the current directory unless the user specifies a different path.
    6.  If the user asks to open, view, or edit a file, use `code [filename]`.
    7.  **Special rule for Windows 'cd':** When changing to a DIFFERENT drive, ALWAYS use `cd /d`. Example: `cd /d D:\\projects`.
    """
    return prompt

def get_ai_response(user_prompt):
    """Sends the prompt to the Groq API and gets a response."""
    system_prompt = get_system_prompt()
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"User Request: \"{user_prompt}\""}
    ]
    
    try:
        completion = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=messages,
            temperature=0.2,
            max_tokens=1024,
            stream=False
        )
        response_text = completion.choices[0].message.content

        if '```json' in response_text:
            json_part = response_text.split('```json')[1].split('```')[0]
        elif '{' in response_text and '}' in response_text:
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            json_part = response_text[start:end]
        else:
            json_part = response_text

        return json_part.strip()
    except Exception as e:
        return f'{{"status": "error", "message": "An error occurred with the API: {e}"}}'


def execute_command(command):
    """Executes the given command and returns the output."""
    try:
        is_windows = platform.system() == "Windows"
        result = subprocess.run(
            command,
            shell=True, # Shell=True is needed to run commands like 'cd' or 'dir'
            text=True,
            capture_output=True,
            check=False,
            cwd=os.getcwd()
        )
        if result.stdout:
            print("\n--- Output ---\n", result.stdout)
        if result.stderr:
            print("\n--- Error ---\n", result.stderr)
    except FileNotFoundError:
        print(f"\nError: Command not found. Is '{command.split()[0]}' installed and in your PATH?")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

#
# --- NEW MAIN LOGIC ---
#
def main(args):
    """Main application logic for command-line tool."""
    
    # 1. Combine all arguments into one string
    prompt = " ".join(args)
    if not prompt:
        print("IntelliTerm: No query provided.")
        print("Usage: turn \"your natural language query\"")
        return

    # 2. Get the first response from the AI
    ai_response_str = get_ai_response(prompt)
    
    try:
        ai_response = json.loads(ai_response_str)
    except json.JSONDecodeError:
        print(f"AI returned an invalid format. Please try rephrasing.\nRaw Response: {ai_response_str}")
        return

    # 3. Handle 'incomplete' status by asking for clarification
    if ai_response.get("status") == "incomplete":
        question = ai_response.get('question')
        print("\n┌─ Clarification Needed " + "─" * 54)
        print(f"│\n│ {question}\n│")
        print("└" + "─" * 74)
        
        clarification_prompt = input("--> ")
        
        if not clarification_prompt:
            print("--> Action cancelled.")
            return

        # Create a new, combined prompt
        new_prompt = f"Original request was '{prompt}'. The user provided this missing info: '{clarification_prompt}'"
        
        print("--> Re-evaluating with new info...")
        ai_response_str = get_ai_response(new_prompt)
        try:
            ai_response = json.loads(ai_response_str)
        except json.JSONDecodeError:
            print(f"AI returned an invalid format on the second attempt. Please start over.\nRaw Response: {ai_response_str}")
            return

    # 4. Handle 'success' status
    if ai_response.get("status") == "success":
        command = ai_response.get("command")
        
        if POWER_USER_MODE:
            print(f"\n--> Power Mode: Executing...")
            print(f"    `{command}`")
            handle_execution(command)
        else:
            explanation = ai_response.get("explanation")
            confirm_and_execute(prompt, command, explanation)

    elif ai_response.get("status") == "error":
        print(f"An error occurred: {ai_response.get('message')}")

if __name__ == "__main__":
    # Get all arguments *after* the script name (e.g., "make folder name 'new files'")
    main(sys.argv[1:])