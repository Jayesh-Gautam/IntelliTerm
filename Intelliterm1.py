import platform
import subprocess
import os
from groq import Groq
import json

# --- Configuration ---
API_KEY = "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"  # Your key here
POWER_USER_MODE = False  # Default state (can now be toggled with "toggle power")

# --- API Key Check ---
if not API_KEY:
    print("------------------------------------------------------------------")
    print("Groq API Key not found!")
    print("Please paste your Groq API key in the script or set it as an environment variable.")
    print("------------------------------------------------------------------")
    exit()

client = Groq(api_key=API_KEY)

def handle_execution(command):
    if command.strip().lower().startswith("cd "):
        try:
            path = command.strip().split(" ", 1)[1]
            if platform.system() == "Windows" and path.lower().startswith("/d "):
                path = path[3:]
            os.chdir(path)
            return f"Current Directory: {os.getcwd()}"
        except FileNotFoundError:
            print(f"Error: Directory not found: {path}")
        except IndexError:
            print("Error: 'cd' command requires a directory path.")
    else:
        execute_command(command)
    return None

def confirm_and_execute(original_prompt, command, explanation):
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
            ai_response_str = get_ai_response(edit_prompt, "")
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
    os_name = platform.system()
    if os_name == "Windows":
        shell_type = "CMD (Command Prompt)"
    else:
        shell_type = "Bash"
    prompt = f"""
    You are an expert command-line assistant. Your task is to convert a user's natural language request
    into a single, executable shell command for the {shell_type} shell.

    RULES:
    1.  Analyze the user's request.
    2.  If clear, return JSON with keys: status, command, explanation.
    3.  If unclear, return JSON with keys: status="incomplete", question="..."
    4.  Do not add text outside the JSON.
    5.  Default to current directory unless specified otherwise.
    6.  Use 'code [filename]' to open or edit files.
    7.  On Windows, use `cd /d` when changing drives.
    """
    return prompt

def get_ai_response(user_prompt, conversation_history):
    system_prompt = get_system_prompt()
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Conversation History:\n{conversation_history}\n\nUser Request: \"{user_prompt}\""}
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
    try:
        is_windows = platform.system() == "Windows"
        result = subprocess.run(
            command,
            shell=True if is_windows else False,
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

def is_direct_command(prompt):
    first_word = prompt.strip().split(' ')[0].lower()
    common_commands = {
        "cd", "dir", "ls", "mkdir", "rmdir", "del", "rm", "copy",
        "move", "ren", "mv", "cls", "clear", "echo", "pwd",
        "pip", "git", "python", "code", "gcc", "node"
    }
    return first_word in common_commands

def main():
    global POWER_USER_MODE
    intro_art = r"""
██╗███╗   ██╗████████╗███████╗██╗     ██╗     ████████╗███████╗██████╗ ███╗   ███╗
██║████╗  ██║╚══██╔══╝██╔════╝██║     ██║     ╚══██╔══╝██╔════╝██╔══██╗████╗ ████║
██║██╔██╗ ██║   ██║   █████╗  ██║     ██║        ██║   █████╗  ██████╔╝██╔████╔██║
██║██║╚██╗██║   ██║   ██╔══╝  ██║     ██║        ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║
██║██║ ╚████║   ██║   ███████╗███████╗███████╗   ██║   ███████╗██║  ██║██║ ╚═╝ ██║
╚═╝╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚══════╝╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝
    """
    print(intro_art)
    print("Welcome to the AI-Powered Natural Language Terminal.")
    print("You can type a command in plain English or a standard shell command.")
    print("Type 'exit' or 'quit' to close.")
    print("Type 'toggle power' to enable or disable Power User Mode ⚡")
    print("-" * 70)

    conversation_history = f"Current Directory: {os.getcwd()}"

    while True:
        try:
            prompt = input(f"\n{os.getcwd()}> ")

            # --- NEW FEATURE: Toggle Power User Mode dynamically ---
            if prompt.strip().lower() == "toggle power":
                POWER_USER_MODE = not POWER_USER_MODE
                status = "ENABLED ⚡" if POWER_USER_MODE else "DISABLED 💡"
                print(f"\n🔄 Power User Mode {status}.")
                continue
            # --------------------------------------------------------

            if prompt.lower() in ["exit", "quit"]:
                break

            if is_direct_command(prompt):
                print("--> Direct command detected. Executing...")
                if prompt.strip().lower().startswith("cd "):
                    try:
                        path = prompt.strip().split(" ", 1)[1]
                        os.chdir(path)
                        conversation_history = f"Current Directory: {os.getcwd()}"
                        print(f"Changed directory to: {os.getcwd()}")
                    except FileNotFoundError:
                        print(f"Error: Directory not found: {path}")
                    except IndexError:
                        print("Error: 'cd' command requires a directory path.")
                else:
                    execute_command(prompt)
                continue 

            ai_response_str = get_ai_response(prompt, conversation_history)
            try:
                ai_response = json.loads(ai_response_str)
            except json.JSONDecodeError:
                print(f"AI returned an invalid format. Please try rephrasing your request.\nRaw Response: {ai_response_str}")
                continue

            if ai_response.get("status") == "incomplete":
                question = ai_response.get('question')
                print("\n┌─ Clarification Needed " + "─" * 54)
                print(f"│\n│ {question}\n│")
                print("└" + "─" * 74)
                clarification_prompt = input("--> ")
                conversation_history += f"\nUser: {prompt}\nAI: {question}\nUser: {clarification_prompt}"
                prompt = f"Original request was '{prompt}'. The user provided this missing info: '{clarification_prompt}'"
                print("--> Re-evaluating with new info...")
                ai_response_str = get_ai_response(prompt, "")
                try:
                    ai_response = json.loads(ai_response_str)
                except json.JSONDecodeError:
                    print(f"AI returned an invalid format on the second attempt. Please start over.\nRaw Response: {ai_response_str}")
                    continue

            if ai_response.get("status") == "success":
                command = ai_response.get("command")
                if POWER_USER_MODE:
                    print(f"\n--> Power Mode: Executing...")
                    print(f"    `{command}`")
                    new_cwd = handle_execution(command)
                else:
                    explanation = ai_response.get("explanation")
                    new_cwd = confirm_and_execute(prompt, command, explanation)
                if new_cwd:
                    conversation_history = new_cwd
            elif ai_response.get("status") == "error":
                print(f"An error occurred: {ai_response.get('message')}")
        except KeyboardInterrupt:
            print("\nExiting IntelliTerm.")
            break

if __name__ == "__main__":
    main()
