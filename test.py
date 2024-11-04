import zipfile
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
        # Если аргумент для директории не указан, выводим содержимое корневой директории
        directory = "/" if not args else args[0]

        # Проверяем, что указанная директория существует
        if directory != "/" and directory not in self.vfs:
            return f"ls: cannot access '{directory}': No such directory"

        # Составляем список файлов и папок внутри указанной директории
        files = []
        for file_path in self.vfs.keys():
            # Проверяем, находится ли файл в указанной директории
            if file_path.startswith(directory):
                # Убираем префикс директории и добавляем к списку
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
        # Переход в указанную директорию
        if len(args) != 1:
            return "cd: missing argument"
        new_dir = args[0]
        if new_dir in self.vfs:
            self.current_dir = new_dir
            return ""
        return f"cd: no such file or directory: {new_dir}"