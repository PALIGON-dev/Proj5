import zipfile

def load_vfs(self, vfs_path):
    # Загружаем виртуальную файловую систему из zip-архива
    vfs = {}
    with zipfile.ZipFile(vfs_path, 'r') as zip_ref:
        for file_info in zip_ref.infolist():
            if not file_info.is_dir():
                # Сохраняем относительные пути файлов в vfs без извлечения на диск
                vfs[file_info.filename] = zip_ref.read(file_info.filename).decode("utf-8")
    return vfs
