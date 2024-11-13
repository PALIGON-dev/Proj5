import json
import datetime
import zipfile
import sys
import os
import shutil
from tkinter import Tk, Text, END
import tempfile

class ShellEmulatorGUI:
    def __init__(self, vfs_path, log_path, startup_script=None, username="user"):
        self.vfs_path = vfs_path
        self.log_path = log_path
        self.username = username
        self.current_dir = "/Folder"
        self.command_log = []
        self.root = Tk()
        self.root.title("Shell Emulator")
        self.text = Text(self.root, wrap="word")
        self.text.pack(expand=True, fill="both")
        self.text.bind("<Return>", self.execute_command)
        self.vfs = self.load_vfs(vfs_path)
        self.insert_prompt()
        if startup_script:
            self.execute_startup_script(startup_script)

    def load_vfs(self, vfs_path):
        vfs = {}
        with zipfile.ZipFile(vfs_path, 'r') as zip_ref:
            for file_info in zip_ref.infolist():
                vfs[file_info.filename] = None if file_info.is_dir() else zip_ref.read(file_info.filename).decode(
                    "utf-8")
        return vfs

    def insert_prompt(self):
        prompt = f"{self.username}@Shell:{self.current_dir}$ "
        self.text.insert(END, prompt)
        self.text.see(END)

    def normalize_path(self, path):
        if not path:
            return self.current_dir
        if path.startswith("/"):
            absolute_path = path
        else:
            absolute_path = self.current_dir.rstrip("/") + "/" + path
        parts = []
        for part in absolute_path.split("/"):
            if part == "..":
                if parts:
                    parts.pop()
            elif part and part != ".":
                parts.append(part)

        return "/" + "/".join(parts)

    def ls(self, args):
        directory = self.current_dir if not args else self.normalize_path(args[0])
        if directory != "/" and not any(key.startswith(directory.lstrip("/") + "/") for key in self.vfs):
            return f"ls: cannot access '{directory}': No such directory"
        dirs = set()
        files = []
        prefix = directory.lstrip("/") + "/"
        for file_path in self.vfs:
            if file_path.startswith(prefix):
                relative_path = file_path[len(prefix):]
                first_part = relative_path.split("/", 1)[0]
                if "/" in relative_path:
                    dirs.add(first_part + "/")
                else:
                    files.append(first_part)
        output = sorted(dirs) + sorted(files)
        return "\n".join(output) if output else "Empty directory"

    def run_command(self, command):
        parts = command.split()
        if not parts:
            return
        cmd = parts[0]
        args = parts[1:]
        if cmd == "ls":
            output = self.ls(args)
        elif cmd == "cd":
            output = self.cd(args)
        elif cmd == "exit":
            self.root.quit()
            return
        elif cmd == "echo":
            output = self.echo(args)
        elif cmd == "cp":
            output = self.cp(args)
        elif cmd == "uname":
            output = self.uname()
        else:
            output = f"Unknown command: {cmd}"
        self.text.insert(END, '\n' + output + '\n')
        self.log_command(command)
        self.insert_prompt()

    def cd(self, args):
        if len(args) != 1:
            return "cd: missing argument"
        new_dir = self.normalize_path(args[0])
        if new_dir in self.vfs or any(key.startswith(new_dir.lstrip("/") + "/") for key in self.vfs):
            self.current_dir = new_dir
            return ""
        return f"cd: no such file or directory: {new_dir}"

    def echo(self, args):
        return " ".join(args)

    def cp(self, args):
        if len(args) != 2:
            return "cp: missing source or destination"
        src, dst = args
        src = self.normalize_path(src)
        dst = self.normalize_path(dst)
        if src not in self.vfs:
            return f"cp: {src}: No such file in virtual filesystem"
        if dst not in self.vfs and not any(f.startswith(dst + "/") for f in self.vfs.keys()):
            return f"cp: {dst}: No such directory in virtual filesystem"
        if dst.endswith("/"):
            dst = dst.rstrip("/") + "/" + os.path.basename(src)
        else:
            dst = dst.rstrip("/")
        self.vfs[dst] = self.vfs[src]
        return f"Copied {src} to {dst}"

    def uname(self):
        return "Shell"

    def execute_command(self, event):
        command = self.text.get("end-2c linestart", "end-1c").strip()
        command = command[len(f"{self.username}@Shell:{self.current_dir}$ "):]
        self.run_command(command)
        return "break"

    def log_command(self, command):
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "command": command
        }
        self.command_log.append(entry)
        with open(self.log_path, "w") as f:
            json.dump(self.command_log, f, indent=4)

    def execute_startup_script(self, script_path):
        with open(script_path, "r") as f:
            commands = f.readlines()
            for command in commands:
                self.run_command(command.strip())


def main():
    if len(sys.argv) < 3:
        print("Usage: emulator.py <vfs_path> <log_path> [<startup_script>] [<username>]")
        sys.exit(1)
    vfs_path = sys.argv[1]
    log_path = sys.argv[2]
    startup_script = sys.argv[3] if len(sys.argv) > 3 else None
    username = sys.argv[4] if len(sys.argv) > 4 else "user"

    emulator = ShellEmulatorGUI(vfs_path, log_path, startup_script, username)
    emulator.root.mainloop()

if __name__ == "__main__":
    main()