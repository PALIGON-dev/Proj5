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