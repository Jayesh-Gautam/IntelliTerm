import platform
import subprocess
import os
from groq import Groq
import json

# --- Configuration ---
# IMPORTANT: Hardcoding keys is okay for personal projects, but for shared
# or public code, using environment variables is more secure.
API_KEY = "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" # Your key is placed here directly
POWER_USER_MODE = True # Set to True to enable Power User Mode

# This check ensures the key is not empty
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
            return f"Current Directory: {os.getcwd()}"
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
    # Keep track of the current command and explanation as they might change
    current_command = command
    current_explanation = explanation

    while True:
        # STEP 1: Display the current suggestion
        print("\n┌─ AI-Powered Terminal " + "─" * 53)
        print(f"│\n│ Command:     {current_command}")
        print(f"│ Explanation: {current_explanation}\n│")
        print("└" + "─" * 74)

        choice = input("--> Execute? [Y]es, [N]o, [E]dit > ").lower()

        # STEP 2: Handle the user's choice
        if choice in ['y', 'yes', '']:
            # --- User chose YES ---
            break  # Exit the loop to proceed with execution

        elif choice in ['n', 'no']:
            # --- User chose NO ---
            print("--> Action cancelled.")
            return None # Exit the function entirely

        elif choice in ['e', 'edit']:
            # --- User chose EDIT (The new AI-powered logic) ---
            modification_request = input("--> Edit: ")
            if not modification_request:
                print("--> Edit cancelled, no change described.")
                continue # Ask for Y/N/E again for the same command

            # Create a new, more detailed prompt for the AI
            edit_prompt = (
                f"The user's original request was: '{original_prompt}'.\n"
                f"The generated command was: `{current_command}`.\n"
                f"The user now wants to change something. Their change request is: '{modification_request}'\n\n"
                f"Generate a new command based on the original request and the change."
            )
            
            # print("--> Asking AI to revise the command...")
            ai_response_str = get_ai_response(edit_prompt, "") # Send the new prompt to the AI
            
            try:
                ai_response = json.loads(ai_response_str)
                if ai_response.get("status") == "success":
                    # If AI succeeds, update the command and explanation for the next loop
                    current_command = ai_response.get("command")
                    current_explanation = ai_response.get("explanation")
                else:
                    # If AI fails, inform the user and keep the current command
                    print(f"--> AI could not process the edit: {ai_response.get('message', 'Unknown error')}")
            except json.JSONDecodeError:
                print(f"--> AI returned an invalid format for the edit. Raw Response: {ai_response_str}")
            
            # After the edit, the 'while' loop will automatically restart and show the NEW suggestion
            continue

        else:
            print("--> Invalid choice. Please enter Y, N, or E.")

    # STEP 3: Execute the final, confirmed command
    print(f"--> Executing: `{current_command}`")
    return handle_execution(current_command)

    if current_command.strip().lower().startswith("cd "):
        try:
            path = current_command.strip().split(" ", 1)[1]
            if platform.system() == "Windows" and path.lower().startswith("/d "):
                path = path[3:]
            os.chdir(path)
            return f"Current Directory: {os.getcwd()}"
        except FileNotFoundError:
            print(f"Error: Directory not found: {path}")
        except IndexError:
            print("Error: 'cd' command requires a directory path.")
    else:
        execute_command(current_command)
    
    return None

def get_system_prompt():
    """Determines the current OS and returns the appropriate system prompt for the AI."""
    os_name = platform.system()
    
    if os_name == "Windows":
        shell_type = "CMD (Command Prompt)"
    else: # Linux, macOS, etc.
        shell_type = "Bash"

    # This is the instruction for the AI. It's the most important part!
    # It tells the AI how to behave and what format to return the data in.
    prompt = f"""
    You are an expert command-line assistant. Your task is to convert a user's natural language request
    into a single, executable shell command for the {shell_type} shell.

    RULES:
    1.  First, analyze the user's request.
    2.  If the request is clear and contains all necessary information (like filenames, folder names, etc.),
        generate the command. The response MUST be a JSON object with three keys:
        - "status": "success"
        - "command": The generated command string.
        - "explanation": A brief, user-friendly explanation of what the command does.
        Example 1 (creating a folder): {{"status": "success", "command": "mkdir my_folder", "explanation": "This command creates a new directory named 'my_folder'."}}
        Example 2 (opening a file): {{"status": "success", "command": "code script.py", "explanation": "This command opens the file 'script.py' in Visual Studio Code."}}

    3.  If the request is ambiguous or missing information, you MUST request the missing information.
        The response must be formal, direct, and state what is needed.
        The response MUST be a JSON object with two keys:
        - "status": "incomplete"
        - "question": The information request for the user.
        # <<< START: Updated Rule #3 and Example >>>
        # OLD EXAMPLE: {{"status": "incomplete", "question": "What is the name of the folder you want to create?"}}
        # NEW, MORE FORMAL EXAMPLE:
        Example: {{"status": "incomplete", "question": "A folder name is required. Please provide the name for the new folder."}}
        # <<< END: Updated Rule #3 and Example >>>

    4.  Do not add any text or explanation outside of the JSON object. Your entire response must be only the raw JSON object.
    5.  The command should be for the current directory unless the user specifies a different path.
    6.  If the user asks to open, view, or edit a file, your primary tool is Visual Studio Code. Generate the command using `code [filename]`.
    7.  **Special rule for Windows directory changes:** When the user wants to change to a directory on a DIFFERENT drive, ALWAYS use the `cd /d` command. For example, to go to the 'projects' folder on the D: drive, generate `cd /d D:\\projects`.
    """
    return prompt

def get_ai_response(user_prompt, conversation_history):
    """Sends the prompt to the Groq API and gets a response."""
    system_prompt = get_system_prompt()
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Conversation History:\n{conversation_history}\n\nUser Request: \"{user_prompt}\""}
    ]
    
    try:
        completion = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=messages,
            temperature=0.2, # Lower temperature for more predictable JSON
            max_tokens=1024,
            stream=False
        )
        response_text = completion.choices[0].message.content

        # Clean the response to extract only the JSON part, as models
        # sometimes add extra text or markdown formatting.
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
        # For Windows, use shell=True. For Linux/macOS, it's safer to split the command.
        is_windows = platform.system() == "Windows"
        result = subprocess.run(
            command,
            shell=True if is_windows else False, # More secure for non-Windows
            text=True,
            capture_output=True,
            check=False, # Don't raise an exception for non-zero exit codes
            cwd=os.getcwd() # Run command in the current working directory
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
    """
    Checks if the user's input is likely a direct command.
    Returns True if it is, False otherwise.
    """
    # Get the first word of the prompt, converted to lowercase
    first_word = prompt.strip().split(' ')[0].lower()

    # A set of common commands for faster lookups
    # You can easily add more commands to this list!
    common_commands = {
        # General
        "cd", "dir", "ls", "mkdir", "rmdir", "del", "rm", "copy",
        "move", "ren", "mv", "cls", "clear", "echo", "pwd",
        # Package managers & tools
        "pip", "git", "python", "code", "gcc", "node",
    }

    return first_word in common_commands


def main():
    """Main application loop."""
    print("IntelliTerm - The Natural Language Terminal")
    print("Type 'exit' or 'quit' to close.")
    print("-" * 40)
    
    conversation_history = f"Current Directory: {os.getcwd()}"

    while True:
        try:
            prompt = input(f"\n{os.getcwd()}> ")

            if prompt.lower() in ["exit", "quit"]:
                break

            # <<< START: New logic for direct command execution >>>
            if is_direct_command(prompt):
                print("--> Direct command detected. Executing...")
                # Handle 'cd' command separately because it's a shell built-in
                if prompt.strip().lower().startswith("cd "):
                    try:
                        path = prompt.strip().split(" ", 1)[1]
                        
                        # On Windows, 'cd /d D:\...' changes drive. os.chdir handles this.
                        # The AI might add '/d ', but for direct commands we don't need to parse it.
                        os.chdir(path)
                        conversation_history = f"Current Directory: {os.getcwd()}" # Update CWD for AI
                        print(f"Changed directory to: {os.getcwd()}")
                    except FileNotFoundError:
                        print(f"Error: Directory not found: {path}")
                    except IndexError:
                        print("Error: 'cd' command requires a directory path.")
                else:
                    # For all other direct commands, execute them right away
                    execute_command(prompt)
                
                # After executing, restart the loop for the next prompt
                continue 
            # <<< END: New logic for direct command execution >>>

            # If it's not a direct command, use the AI (this is your original logic)
            ai_response_str = get_ai_response(prompt, conversation_history)
            
            try:
                ai_response = json.loads(ai_response_str)
            except json.JSONDecodeError:
                print(f"AI returned an invalid format. Please try rephrasing your request.\nRaw Response: {ai_response_str}")
                continue

            if ai_response.get("status") == "incomplete":
                # --- This is the new, formatted UI block for questions ---
                question = ai_response.get('question')
                print("\n┌─ Clarification Needed " + "─" * 54)
                # This part is slightly different to better handle questions
                print(f"│\n│ {question}\n│")
                print("└" + "─" * 74)
                clarification_prompt = input("--> ")
                # --- End of new UI block ---
                
                # The rest of the logic remains the same
                conversation_history += f"\nUser: {prompt}\nAI: {question}\nUser: {clarification_prompt}"
                prompt = f"Original request was '{prompt}'. The user provided this missing info: '{clarification_prompt}'"
                
                print("--> Re-evaluating with new info...")
                ai_response_str = get_ai_response(prompt, "") # Reset history for this turn
                try:
                    ai_response = json.loads(ai_response_str)
                except json.JSONDecodeError:
                    print(f"AI returned an invalid format on the second attempt. Please start over.\nRaw Response: {ai_response_str}")
                    continue

            if ai_response.get("status") == "success":
                command = ai_response.get("command")
                
                if POWER_USER_MODE:
                    # In Power User Mode, execute directly without confirmation
                    print(f"\n--> Power Mode: Executing...")
                    print(f"    `{command}`")
                    new_cwd = handle_execution(command)
                else:
                    # In Normal Mode, ask for confirmation as before
                    explanation = ai_response.get("explanation")
                    new_cwd = confirm_and_execute(prompt, command, explanation)

                # Update conversation history if the directory changed
                if new_cwd:
                    conversation_history = new_cwd

            elif ai_response.get("status") == "error":
                    print(f"An error occurred: {ai_response.get('message')}")

        except KeyboardInterrupt:
            print("\nExiting IntelliTerm.")
            break



if __name__ == "__main__":
    main()
