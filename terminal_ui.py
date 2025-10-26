# terminal_ui.py
# Put this file in the same folder as your original intelliterm.py (do NOT rename your original file).

import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox, filedialog
import contextlib
import io
import os
import platform
import json
import threading

# Import your original IntelliTerm module (leave it unchanged)
import intelliterm  # <-- your original file must be named intelliterm.py and in the same folder

# -------------------------
# Helper wrapper functions
# -------------------------
def call_get_ai_response(user_prompt, conversation_history):
    """
    Calls your get_ai_response from intelliterm and returns the raw JSON string.
    (Your function already returns a JSON-like string in your original file.)
    """
    try:
        return intelliterm.get_ai_response(user_prompt, conversation_history)
    except Exception as e:
        return json.dumps({"status": "error", "message": f"Error calling get_ai_response: {e}"})


def call_execute_command_capture(command):
    """
    Calls your intelliterm.execute_command(command) but captures anything it prints
    (stdout and stderr) and returns the captured text as a string.
    This lets us keep your original function unchanged.
    """
    buf_out = io.StringIO()
    buf_err = io.StringIO()
    try:
        # Redirect both stdout and stderr so prints inside your execute_command are captured
        with contextlib.redirect_stdout(buf_out), contextlib.redirect_stderr(buf_err):
            maybe_ret = intelliterm.execute_command(command)
            # Some implementations may return text; if so, include it too.
            if maybe_ret is not None:
                # If it returned a string, also include it
                try:
                    if isinstance(maybe_ret, str) and maybe_ret.strip():
                        # Write its returned text to buffer (to be consistent with CLI behavior)
                        buf_out.write(str(maybe_ret))
                except Exception:
                    pass
    except FileNotFoundError as fnf:
        buf_err.write(f"FileNotFoundError: {fnf}\n")
    except Exception as e:
        buf_err.write(f"Exception while executing command: {e}\n")

    out_text = buf_out.getvalue()
    err_text = buf_err.getvalue()
    combined = ""
    if out_text:
        combined += out_text
    if err_text:
        if combined and not combined.endswith("\n"):
            combined += "\n"
        combined += "[stderr]\n" + err_text
    if combined.strip() == "":
        combined = "(No output)\n"
    return combined

# -------------------------
# Tkinter GUI
# -------------------------
class TerminalUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("IntelliTerm GUI")
        self.geometry("920x600")
        self.minsize(700, 350)
        self.configure(bg="#0b0b0b")

        # Conversation history text (keeps current directory info etc.)
        self.conversation_history = f"Current Directory: {os.getcwd()}"

        # Build UI
        self._build_widgets()

    def _build_widgets(self):
        # Top toolbar frame (optional: Save, Clear)
        top_frame = tk.Frame(self, bg="#0b0b0b")
        top_frame.pack(side="top", fill="x", padx=8, pady=(8, 0))

        save_btn = tk.Button(top_frame, text="Save Output", command=self._save_output, bg="#1f1f1f", fg="white")
        save_btn.pack(side="left", padx=(0,6))

        clear_btn = tk.Button(top_frame, text="Clear", command=self._clear_output, bg="#1f1f1f", fg="white")
        clear_btn.pack(side="left", padx=(0,6))

        # Output area
        self.output = scrolledtext.ScrolledText(
            self, wrap=tk.WORD, bg="#101010", fg="#d1f3d1", insertbackground="white", font=("Consolas", 12)
        )
        self.output.pack(fill="both", expand=True, padx=8, pady=(6,8))
        self.output.tag_config("meta", foreground="#9aa5ff", font=("Consolas", 11, "italic"))
        self.output.tag_config("cmd", foreground="#00e5a8", font=("Consolas", 11, "bold"))
        self.output.tag_config("out", foreground="#d1f3d1", font=("Consolas", 11))
        self.output.tag_config("err", foreground="#ff7a7a", font=("Consolas", 11))

        # Input frame
        bottom = tk.Frame(self, bg="#0b0b0b")
        bottom.pack(side="bottom", fill="x", padx=8, pady=8)

        lbl = tk.Label(bottom, text=">", fg="#00e5a8", bg="#0b0b0b", font=("Consolas", 12))
        lbl.pack(side="left", padx=(4,4))

        self.entry_var = tk.StringVar()
        self.entry = tk.Entry(bottom, textvariable=self.entry_var, bg="#111111", fg="white", insertbackground="white", font=("Consolas", 12))
        self.entry.pack(side="left", fill="x", expand=True, padx=(0,6))
        self.entry.bind("<Return>", lambda e: self._on_enter())
        self.entry.focus_set()

        # initial welcome text
        self._append_meta("IntelliTerm GUI — type a natural-language request and press Enter.\n")

    # helpers
    def _append_meta(self, text):
        self.output.insert("end", text, "meta")
        self.output.see("end")

    def _append_cmd(self, text):
        self.output.insert("end", text, "cmd")
        self.output.see("end")

    def _append_out(self, text):
        # Use out tag for normal output, err for stderr lines
        if not text:
            return
        # Split by lines and tag lines containing "[stderr]" or just tag all
        if "[stderr]" in text:
            parts = text.split("[stderr]")
            if parts[0].strip():
                self.output.insert("end", parts[0], "out")
            self.output.insert("end", "\n[stderr]\n", "err")
            self.output.insert("end", parts[1], "err")
        else:
            self.output.insert("end", text, "out")
        self.output.see("end")

    def _clear_output(self):
        self.output.delete("1.0", "end")

    def _save_output(self):
        txt = self.output.get("1.0", "end-1c")
        if not txt.strip():
            messagebox.showinfo("Save", "Nothing to save.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files","*.txt"),("All files","*.*")])
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(txt)
            messagebox.showinfo("Saved", f"Saved to:\n{path}")

    # main flow
    def _on_enter(self):
        user_text = self.entry_var.get().strip()
        if not user_text:
            return
        self.entry_var.set("")  # clear entry box

        # display what the user typed
        self._append_cmd(f"\n> {user_text}\n")

        # do network/API and heavy work in separate thread to keep UI responsive
        threading.Thread(target=self._process_user_request, args=(user_text,), daemon=True).start()

    def _process_user_request(self, user_text):
        # 1) ask AI for command JSON
        self._append_meta("[Sending request to AI...]\n")
        ai_raw = call_get_ai_response(user_text, self.conversation_history)

        # parse JSON safely
        try:
            ai_json = json.loads(ai_raw)
        except Exception:
            # If parsing fails, show raw response
            self._append_out(f"[AI returned invalid JSON]\n{ai_raw}\n")
            return

        # 2) handle incomplete -> ask clarifying question using a dialog on main thread
        if ai_json.get("status") == "incomplete":
            question = ai_json.get("question", "Please clarify:")
            # ask user on main thread
            clarification = None
            def ask_dialog():
                nonlocal clarification
                clarification = simpledialog.askstring("Clarify", question, parent=self)
            self._run_on_main_thread(ask_dialog)
            if clarification is None:
                self._append_meta("[Clarification cancelled]\n")
                return
            # update conversation history (like your original code did)
            self.conversation_history += f"\nUser: {user_text}\nAI: {question}\nUser: {clarification}"
            retry_prompt = f"Original request was '{user_text}'. The user provided this missing info: '{clarification}'"
            self._append_meta("[Retrying AI with clarification...]\n")
            ai_raw_retry = call_get_ai_response(retry_prompt, self.conversation_history)
            try:
                ai_json = json.loads(ai_raw_retry)
            except Exception:
                self._append_out(f"[AI returned invalid JSON on retry]\n{ai_raw_retry}\n")
                return

        # 3) handle success / error
        if ai_json.get("status") == "success":
            command = ai_json.get("command", "")
            explanation = ai_json.get("explanation", "")
            # show command and explanation
            self._append_meta(f"[AI produced command]\n{explanation}\nCommand: {command}\n")
            # ask user to confirm execution (on main thread)
            confirmed = None
            def ask_confirm():
                nonlocal confirmed
                confirmed = messagebox.askyesno("Execute command?", f"Command:\n{command}\n\n{explanation}\n\nExecute?")
            self._run_on_main_thread(ask_confirm)
            if not confirmed:
                self._append_meta("[Execution cancelled by user]\n")
                return

            # special-case cd: change UI process working directory
            cmd_strip = command.strip()
            if cmd_strip.lower().startswith("cd "):
                # handle Windows cd /d case if AI used it
                path = cmd_strip.split(" ", 1)[1]
                if platform.system().startswith("Windows") and path.lower().startswith("/d "):
                    path = path[3:]
                try:
                    os.chdir(path)
                    self.conversation_history = f"Current Directory: {os.getcwd()}"
                    self._append_meta(f"[Changed directory to: {os.getcwd()}]\n")
                except Exception as e:
                    self._append_out(f"[Error changing directory: {e}]\n")
                return

            # execute command using wrapper that captures prints
            self._append_meta(f"[Executing command]\n")
            out_text = call_execute_command_capture(command)
            self._append_out(out_text + "\n")

        elif ai_json.get("status") == "error":
            self._append_out(f"[AI error] {ai_json.get('message')}\n")
        else:
            self._append_out(f"[Unhandled AI response] {ai_json}\n")

    def _run_on_main_thread(self, fn):
        """
        Helper to run a function synchronously on Tkinter main thread.
        """
        event = threading.Event()
        def wrapper():
            try:
                fn()
            finally:
                event.set()
        self.after(0, wrapper)
        event.wait()


# -------------------------
# Run the UI
# -------------------------
if __name__ == "__main__":
    app = TerminalUI()
    app.mainloop()
