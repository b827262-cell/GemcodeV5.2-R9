import os

BASE = "./workspace"

def list_files():
    if not os.path.exists(BASE): return []
    # 僅列出檔案，排除資料夾（如 .git）
    return [f for f in os.listdir(BASE) if os.path.isfile(os.path.join(BASE, f))]

def read_file(name):
    path = os.path.join(BASE, name)
    if not os.path.exists(path): return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def write_file(name, content):
    if not os.path.exists(BASE): os.makedirs(BASE)
    path = os.path.join(BASE, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return "saved"
