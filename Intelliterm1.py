import platform
import subprocess
import os
from groq import Groq
import json

# ============================================================
# --- Configuration ---
# ============================================================

# Read or ask for API key automatically
def get_api_key():
    key_file = "api_key.txt"
    if os.path.exists(key_file):
        with open(key_file, "r") as f:
            saved_key = f.read().strip()
            if saved_key:
                return saved_key

    print("🔑 Groq API key not found or expired.")
    new_key = input("Please enter your new Groq API key: ").strip()
    with open(key_file, "w") as f:
        f.write(new_key)
    return new_key


API_KEY = get_api_key()
POWER_USER_MODE = False  # Default mode

# Create client
try:
    client = Groq(api_key=API_KEY)
except Exception as e:
    print(f"Error initializing API client: {e}")
    exit()


# ============================================================
# --- Helper Functions ---
# ============================================================

def handle_execution(command):
    """Handles directory change or executes normal command."""
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


def execute_command(command):
    """Executes shell command and prints output."""
    try:
        is_windows = platform.system() == "Windows"
        result = subprocess.run(
            command,
            shell=True if is_windows else False,
            text=True,
            capture_output=True,
            cwd=os.getcwd()
        )
        if result.stdout:
            print("\n--- Output ---\n", result.stdout)
        if result.stderr:
            print("\n--- Error ---\n", result.stderr)
    except Exception as e:
        print(f"\nUnexpected error: {e}")


def is_direct_command(prompt):
    """Detects if user entered a raw command."""
    first_word = prompt.strip().split(' ')[0].lower()
    common = {"cd", "dir", "ls", "mkdir", "rmdir", "del", "rm", "copy", "move",
              "ren", "mv", "cls", "clear", "echo", "pwd", "pip", "git", "python", "code", "gcc", "node"}
    return first_word in common


def get_system_prompt():
    os_name = platform.system()
    shell_type = "CMD" if os_name == "Windows" else "Bash"
    return f"""
You are an expert command-line assistant.
Convert the user's natural language request into a {shell_type} shell command.

Rules:
- Return only JSON: {{"status":"success","command":"...","explanation":"..."}}
- If missing info: {{"status":"incomplete","question":"..."}}
- Do not include any text outside JSON.
- Always generate safe, clear commands.
"""


def get_ai_response(user_prompt, history):
    """Send query to Groq API safely with key check."""
    try:
        completion = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": get_system_prompt()},
                {"role": "user", "content": f"{history}\nUser: {user_prompt}"}
            ],
            temperature=0.2,
            max_tokens=1024
        )
        response = completion.choices[0].message.content
        if '```json' in response:
            response = response.split('```json')[1].split('```')[0]
        return response.strip()
    except Exception as e:
        print(f"⚠️ API Error: {e}")
        print("→ Try updating your API key.")
        os.remove("api_key.txt")
        return '{"status":"error","message":"API key expired. Restart IntelliTerm and provide a new key."}'


def confirm_and_execute(original_prompt, command, explanation):
    """Ask before executing command."""
    while True:
        print("\n┌─ AI-Powered Command ─────────────────────────────────────────────")
        print(f"│ Command: {command}")
        print(f"│ Explanation: {explanation}")
        print("└─────────────────────────────────────────────────────────────────")
        choice = input("--> Execute? [Y]es / [N]o / [E]dit > ").lower()
        if choice in ['y', 'yes', '']:
            return handle_execution(command)
        elif choice in ['n', 'no']:
            print("--> Cancelled.")
            return None
        elif choice in ['e', 'edit']:
            mod = input("--> Describe edit: ")
            if mod:
                ai_response_str = get_ai_response(
                    f"Original: '{original_prompt}', edit: '{mod}'", "")
                try:
                    ai_resp = json.loads(ai_response_str)
                    if ai_resp.get("status") == "success":
                        command = ai_resp["command"]
                        explanation = ai_resp["explanation"]
                        continue
                except:
                    print("--> Edit failed.")
            continue
        else:
            print("--> Invalid input.")


# ============================================================
# --- Main Loop ---
# ============================================================

def main():
    global POWER_USER_MODE
    print(r"""
██╗███╗   ██╗████████╗███████╗██╗     ██╗     ████████╗███████╗██████╗ ███╗   ███╗
██║████╗  ██║╚══██╔══╝██╔════╝██║     ██║     ╚══██╔══╝██╔════╝██╔══██╗████╗ ████║
██║██╔██╗ ██║   ██║   █████╗  ██║     ██║        ██║   █████╗  ██████╔╝██╔████╔██║
██║██║╚██╗██║   ██║   ██╔══╝  ██║     ██║        ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║
██║██║ ╚████║   ██║   ███████╗███████╗███████╗   ██║   ███████╗██║  ██║██║ ╚═╝ ██║
╚═╝╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚══════╝╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝
    """)
    print("🤖 Welcome to IntelliTerm — Your AI-powered Terminal Assistant.")
    print("Type natural commands, 'exit' to quit, or press 'P' to toggle Power Mode.")
    print("-" * 70)

    history = f"Current Directory: {os.getcwd()}"

    while True:
        try:
            mode_text = "⚡ POWER MODE ON" if POWER_USER_MODE else "💡 NORMAL MODE"
            prompt = input(f"\n[{mode_text}] {os.getcwd()}> ").strip()

            if prompt.lower() in ["exit", "quit"]:
                print("👋 Exiting IntelliTerm.")
                break

            if prompt.lower() == "p":
                POWER_USER_MODE = not POWER_USER_MODE
                print(f"→ Power Mode {'Enabled ⚡' if POWER_USER_MODE else 'Disabled 💡'}")
                continue

            if is_direct_command(prompt):
                print("--> Direct command detected.")
                handle_execution(prompt)
                continue

            ai_response_str = get_ai_response(prompt, history)
            try:
                ai_response = json.loads(ai_response_str)
            except:
                print("⚠️ Invalid AI format:", ai_response_str)
                continue

            if ai_response.get("status") == "success":
                command = ai_response["command"]
                if POWER_USER_MODE:
                    print(f"⚡ Executing: {command}")
                    handle_execution(command)
                else:
                    explanation = ai_response["explanation"]
                    confirm_and_execute(prompt, command, explanation)
            elif ai_response.get("status") == "incomplete":
                question = ai_response["question"]
                print(f"❓ {question}")
                more = input("--> ")
                new_prompt = f"{prompt}. Missing info: {more}"
                ai_response_str = get_ai_response(new_prompt, "")
                ai_response = json.loads(ai_response_str)
                if ai_response.get("status") == "success":
                    command = ai_response["command"]
                    confirm_and_execute(prompt, command, ai_response["explanation"])
            elif ai_response.get("status") == "error":
                print(f"⚠️ {ai_response.get('message')}")
        except KeyboardInterrupt:
            print("\n🛑 Interrupted. Exiting IntelliTerm.")
            break


if __name__ == "__main__":
    main()
