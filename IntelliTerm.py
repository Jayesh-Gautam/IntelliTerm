import platform
import subprocess
import os
from groq import Groq
import json

# --- Configuration ---
# IMPORTANT: Hardcoding keys is okay for personal projects, but for shared
# or public code, using environment variables is more secure.
API_KEY = "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" # Your key is placed here directly

# This check ensures the key is not empty
if not API_KEY:
    print("------------------------------------------------------------------")
    print("Groq API Key not found!")
    print("Please paste your Groq API key in the script or set it as an environment variable.")
    print("------------------------------------------------------------------")
    exit()


client = Groq(api_key=API_KEY)

# --- Core Functions ---

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

    3.  If the request is ambiguous or missing information, you MUST ask a single, clear clarifying question.
        The response MUST be a JSON object with two keys:
        - "status": "incomplete"
        - "question": The question to ask the user.
        Example: {{"status": "incomplete", "question": "What is the name of the folder you want to create?"}}

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

            ai_response_str = get_ai_response(prompt, conversation_history)
            
            try:
                ai_response = json.loads(ai_response_str)
            except json.JSONDecodeError:
                print(f"AI returned an invalid format. Please try rephrasing your request.\nRaw Response: {ai_response_str}")
                continue

            if ai_response.get("status") == "incomplete":
                clarification_prompt = input(f"AI: {ai_response.get('question')} > ")
                # Update conversation history and retry
                conversation_history += f"\nUser: {prompt}\nAI: {ai_response.get('question')}\nUser: {clarification_prompt}"
                prompt = f"Original request was '{prompt}'. The user provided this missing info: '{clarification_prompt}'"
                
                # Retry with the complete information
                ai_response_str = get_ai_response(prompt, "") # Reset history for this turn
                try:
                    ai_response = json.loads(ai_response_str)
                except json.JSONDecodeError:
                    print(f"AI returned an invalid format on the second attempt. Please start over.\nRaw Response: {ai_response_str}")
                    continue


            if ai_response.get("status") == "success":
                command = ai_response.get("command")
                explanation = ai_response.get("explanation")

                print(f"\nCommand: `{command}`")
                print(f"What will happen: {explanation}")

                try:
                    # Pause for user to press Enter to confirm, or Ctrl+C to cancel.
                    input("\nPress Enter to execute, or Ctrl+C to cancel... ")
                    
                    if command.strip().lower().startswith("cd "):
                        try:
                            # Handle 'cd' separately as it's a shell built-in
                            path = command.strip().split(" ", 1)[1]
                            
                            # On Windows, the AI might add '/d '. We need to remove it for os.chdir
                            if platform.system() == "Windows" and path.lower().startswith("/d "):
                                path = path[3:] # Remove the '/d ' part

                            os.chdir(path)
                            conversation_history = f"Current Directory: {os.getcwd()}" # Update CWD for AI
                            print(f"Changed directory to: {os.getcwd()}")
                        except FileNotFoundError:
                            print(f"Error: Directory not found: {path}")
                        except IndexError:
                            print("Error: 'cd' command requires a directory path.")
                    else:
                        execute_command(command)
                except KeyboardInterrupt:
                    # This catches Ctrl+C to cancel the current command execution
                    print("\nExecution cancelled.")
                    continue

            elif ai_response.get("status") == "error":
                 print(f"An error occurred: {ai_response.get('message')}")


        except KeyboardInterrupt:
            # This catches Ctrl+C from the main prompt to exit the program
            print("\nExiting IntelliTerm.")
            break


if __name__ == "__main__":
    main()


