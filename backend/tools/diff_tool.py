import difflib

def make_diff(a, b):
    # 比對 a(舊) 與 b(新) 的差異
    diff = list(difflib.unified_diff(a.splitlines(), b.splitlines(), lineterm=""))
    return "\n".join(diff) if diff else "目前內容與儲存版本一致，無差異。"
