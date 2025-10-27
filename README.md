# IntelliTerm: The Natural Language Terminal 🚀



**IntelliTerm** is an intelligent, hybrid command-line interface that allows you to execute shell commands by typing in plain English. Powered by the Groq API for high-speed inference, it translates your natural language requests into executable commands for both Windows (CMD) and Unix-like systems (Bash).

This project goes beyond a simple translator by creating a rich, interactive shell experience. It intelligently decides when to use AI and when to act as a traditional shell, giving you the best of both worlds.

---

## 🌟 Features

* **Natural Language Processing**: Simply type what you want to do, like *"create a new folder called 'docs'"* or *"find all text files in this directory"*.

* **Polished Interactive UI**: All interactions, from command suggestions to clarification questions, are presented in a clean, professional, and consistent interface.

* **Direct Command Execution**: IntelliTerm is a **hybrid shell**. It recognizes standard commands (like `dir`, `ls`, `git`, `pip`) and executes them immediately, bypassing the AI for maximum speed and familiar control.

* **AI-Powered Editing**: Made a typo or changed your mind? The 'Edit' feature allows you to provide a correction in plain English (e.g., *"change the name to 'final_report'"*), and the AI will intelligently revise the command for you.

* **Power User Mode**: For advanced users who prioritize speed, a special **Power User Mode** can be enabled. This mode executes all AI-generated commands instantly without requiring confirmation.

* **Cross-Platform Support**: Automatically detects your OS (Windows, macOS, or Linux) and generates the appropriate command.

* **Contextual Clarification**: If your request is ambiguous, the AI will ask for the necessary information in a structured prompt to ensure it gets the command right.

---

## 🛠️ Technologies Used

* **Python 3**
* **Groq API** for fast Language Model inference.
* **Standard Libraries**: `os`, `platform`, `subprocess`, `json`

---

## ⚙️ Setup and Installation

Follow these steps to get IntelliTerm running on your local machine.

### 1. Clone the Repository
```bash
git clone https://github.com/Jayesh-Gautam/IntelliTerm.git
cd IntelliTerm
````

### 2\. Install Dependencies

It's recommended to use a virtual environment.

```bash
# Create a virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install the required packages
pip install groq
```

### 3\. Configure API Key

You need a Groq API key to use the service.

1.  Get your free API key from the **[Groq Console](https://console.groq.com/keys)**.
2.  Open the script and paste your key into the `API_KEY` variable.

-----

### 🔧 Configuration

#### ⚡ Power User Mode (Toggle Feature)

IntelliTerm includes a **Power User Mode** that can be **enabled or disabled directly through the terminal** 🖥️

When **Power User Mode** is **enabled**, commands execute instantly ⚡ — no confirmation required — perfect for advanced users.
When it’s **disabled**, IntelliTerm adds a confirmation step 🛡️ for safer command execution.

You can toggle this mode anytime using the built-in command:

```bash
> toggle power
Power User Mode: ENABLED ✅
```

and to turn it off again:

```bash
> toggle power
Power User Mode: DISABLED ❌
```

This simple toggle lets you switch between **safe mode** and **instant execution** without editing any code 🚀


-----

## ▶️ How to Run

Once you have completed the setup, run the script from your terminal:

```bash
python IntelliTerm.py
```

The application will start, and you can begin typing commands.

-----

## 📝 Example Usage

### Example 1: Creating a File

The AI suggests a command and waits for your confirmation.

```
C:\Users\You> create a new empty file called report.docx

┌─ AI-Powered Terminal ─────────────────────────────────────────────────────
│
│ Command:     type nul > report.docx
│ Explanation: This command creates an empty file named 'report.docx'.
│
└──────────────────────────────────────────────────────────────────────────
--> Execute? [Y]es, [N]o, [E]dit >
```

### Example 2: AI-Powered Editing

After getting a suggestion, you can ask the AI to modify it.

```
C:\Users\You> make a folder for my new project

┌─ AI-Powered Terminal ─────────────────────────────────────────────────────
│
│ Command:     mkdir "new project"
│ Explanation: This command creates a new directory named 'new project'.
│
└──────────────────────────────────────────────────────────────────────────
--> Execute? [Y]es, [N]o, [E]dit > e
--> Describe your change: actually, name it "Project Alpha"

--> Asking AI to revise the command...

┌─ AI-Powered Terminal ─────────────────────────────────────────────────────
│
│ Command:     mkdir "Project Alpha"
│ Explanation: This command creates a new directory named 'Project Alpha'.
│
└──────────────────────────────────────────────────────────────────────────
--> Execute? [Y]es, [N]o, [E]dit >
```

### Example 3: Handling Ambiguity

The AI asks for more information in a clean, structured way.
cl
```
C:\Users\You> I need to make a new item

┌─ Clarification Needed ────────────────────────────────────────────────────
│
│ Please clarify whether you want to create a file or a folder.
│
└──────────────────────────────────────────────────────────────────────────
--> Response: a file named 'config'
```

-----

## 💡 Future Improvements

  * **Command History**: Implement up/down arrow functionality to cycle through previous commands.
  * **Alias Support**: Allow users to define their own custom shortcuts.
  * **Tab Completion**: Add auto-completion for file and directory names.

<!-- end list -->

