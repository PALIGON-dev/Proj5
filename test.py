import json
import datetime
import zipfile
import sys
from tkinter import Tk, Text, END

class ShellEmulatorGUI:
    def __init__(self, vfs_path, log_path, startup_script=None, username="user"):
        self.vfs_path = vfs_path
        self.log_path = log_path
        self.username = username  # Имя пользователя
        self.current_dir = "/"  # Текущая директория в файловой системе
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

    def run_command(self, command):
        # Разбиваем команду на основную часть и аргументы
        parts = command.split()
        if not parts:
            return

        cmd = parts[0]
        args = parts[1:]

        # Проверяем, какая команда введена
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

        # Записываем результат выполнения команды в GUI и логируем
        self.text.insert(END, '\n' + output + '\n')  # Добавляем пустую строку для новой строки после команды
        self.log_command(command)
        self.insert_prompt()

    def load_vfs(self, vfs_path):
        vfs = {}
        with zipfile.ZipFile(vfs_path, 'r') as zip_ref:
            for file_info in zip_ref.infolist():
                if not file_info.is_dir():
                    vfs[file_info.filename] = zip_ref.read(file_info.filename).decode("utf-8")
        return vfs

    def insert_prompt(self):
        prompt = f"{self.username}@ShellEmulator:{self.current_dir}$ "
        self.text.insert(END, prompt)
        self.text.see(END)

    def ls(self, args):
        directory = "/" if not args else args[0]
        if directory != "/" and directory not in self.vfs:
            return f"ls: cannot access '{directory}': No such directory"
        files = []
        for file_path in self.vfs.keys():
            if file_path.startswith(directory):
                relative_path = file_path[len(directory):].strip("/")
                files.append(relative_path)

        return "\n".join(files) if files else "Empty directory"

    def echo(self, args):
        return " ".join(args)

    def uname(self):
        return "ShellEmulator"

    def execute_command(self, event):
        command = self.text.get("end-2c linestart", "end-1c").strip()
        command = command[len(f"{self.username}@ShellEmulator:{self.current_dir}$ "):]
        self.run_command(command)
        return "break"

    def cd(self, args):
        if len(args) != 1:
            return "cd: missing argument"
        new_dir = args[0]
        if new_dir in self.vfs:
            self.current_dir = new_dir
            return ""
        return f"cd: no such file or directory: {new_dir}"

    def log_command(self, command):
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "command": command
        }
        self.command_log.append(entry)
        with open(self.log_path, "w") as f:
            json.dump(self.command_log, f, indent=4)

    def execute_startup_script(self, script_path):
        # Выполняем команды из стартового скрипта
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