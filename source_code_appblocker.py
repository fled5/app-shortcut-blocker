import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import os
import shutil
import sys
import winreg

class BlockerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("app & shortcut Blocker")
        self.file_path = tk.StringVar()
        self.block_method = tk.StringVar(value="permanent")

        tk.Button(root, text="What does this do?", command=self.show_info).pack(pady=5)
        
        tk.Label(root, text="Paste or browse a .exe / .url / .lnk to block:").pack(pady=5)
        self.path_entry = tk.Entry(root, textvariable=self.file_path, width=60)
        self.path_entry.pack()

        tk.Button(root, text="Browse", command=self.browse_file).pack(pady=5)

        tk.Label(root, text="Choose Blocking Method:").pack(pady=5)
        methods = [
            ("Simple Rename Block (.blocked suffix)", "simple"),
            ("Hidden Storage Move (stealth)", "moderate_hidden"),
            ("Permanent Block (secret folder with reason)", "permanent")
        ]
        for text, mode in methods:
            tk.Radiobutton(root, text=text, variable=self.block_method, value=mode).pack(anchor='w')

        tk.Button(root, text="Block", command=self.start_blocking).pack(pady=10)
        tk.Button(root, text="Enable Auto-Start on Boot", command=self.enable_autostart).pack(pady=5)

        # Create folders
        self.permanent_folder = os.path.join("C:\\ProgramData", "SystemEvents")
        os.makedirs(self.permanent_folder, exist_ok=True)
        os.system(f'attrib +h "{self.permanent_folder}"')

        self.moderate_hidden_folder = os.path.join("C:\\ProgramData", "ModerateBlocker")
        os.makedirs(self.moderate_hidden_folder, exist_ok=True)

    def browse_file(self):
        path = filedialog.askopenfilename(filetypes=[("Executable or Shortcut", "*.exe *.url *.lnk")])
        if path:
            self.file_path.set(path)

    def start_blocking(self):
        target = self.file_path.get().strip()
        target = target.strip('"')  # <-- Remove surrounding quotes if any

        if not os.path.exists(target):
            messagebox.showerror("Error", f"Invalid file path:\n{target}")
            return
        
        method = self.block_method.get()
        file_name = os.path.basename(target)

        if method == "permanent":
            reason = simpledialog.askstring("Reason", "Why are you blocking this?")
            if not reason:
                messagebox.showwarning("Required", "You must enter a reason.")
                return

            confirm = messagebox.askyesno(
                "Confirm",
                "⚠️ This will block the file by moving it to a secret folder.\n"
                "You won’t be able to unblock it through this app easily.\n\nContinue?"
            )
            if not confirm:
                return

            note_path = os.path.join(self.permanent_folder, file_name + "_reason.txt")
            with open(note_path, "w") as f:
                f.write(reason)

            new_path = os.path.join(self.permanent_folder, file_name + ".enc")
            shutil.move(target, new_path)
            self.remove_visual_triggers(file_name)

        elif method == "moderate_hidden":
            new_path = os.path.join(self.moderate_hidden_folder, file_name + ".mhid")
            shutil.move(target, new_path)

        elif method == "simple":
            new_path = target + ".blocked"
            os.rename(target, new_path)

        else:
            messagebox.showerror("Error", "Unknown blocking method selected.")
            return

        messagebox.showinfo("Blocked", f"{file_name} has been blocked using '{method}' method.")
        self.file_path.set("")

    def remove_visual_triggers(self, file_name):
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        for fname in os.listdir(desktop):
            if file_name.lower() in fname.lower():
                try:
                    os.remove(os.path.join(desktop, fname))
                except:
                    pass

        start_menu = os.path.join(os.getenv("APPDATA"), r"Microsoft\Windows\Start Menu\Programs")
        for root_dir, _, files in os.walk(start_menu):
            for fname in files:
                if file_name.lower() in fname.lower():
                    try:
                        os.remove(os.path.join(root_dir, fname))
                    except:
                        pass

    def show_info(self):
        msg = (
            "This tool blocks programs or shortcuts by renaming or moving them.\n\n"
            "- Simple Block: Adds '.blocked' suffix so it can't run.\n"
            "- Moderate Hidden: Moves to a hidden folder.\n"
            "- Permanent: Hides forever with your reason logged.\n\n"

            "There’s no background process. Just open this app, block what you want, and close it.\n\n"
            " Additionally, this tool auto-starts once you enable auto-start, if you don't want that don't press enable auto-start.\n "
        )
        messagebox.showinfo("How This Works", msg)

    def enable_autostart(self):
        try:
            exe_path = sys.executable
            script_path = os.path.abspath(__file__)

            run_key = r"Software\Microsoft\Windows\CurrentVersion\Run"
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, run_key, 0, winreg.KEY_SET_VALUE)

            if exe_path.lower().endswith("python.exe") or exe_path.lower().endswith("pythonw.exe"):
                pythonw = exe_path.replace("python.exe", "pythonw.exe").replace("Python.exe", "pythonw.exe")
                cmd = f'"{pythonw}" "{script_path}"'
            else:
                cmd = f'"{exe_path}"'

            winreg.SetValueEx(key, "AppBlocker", 0, winreg.REG_SZ, cmd)
            winreg.CloseKey(key)

            messagebox.showinfo("Auto-Start Enabled", "This app will start automatically when you log into Windows.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to enable auto-start:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = BlockerApp(root)
    root.mainloop()
