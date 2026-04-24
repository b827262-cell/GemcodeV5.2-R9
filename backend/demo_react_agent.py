import asyncio
import os
import sys

# 模擬 PYTHONPATH，確保能讀取到 tools
sys.path.append(os.getcwd())

# 1. 導入我們辛苦建立的引擎
from agent_core.loop import engine

async def main():
    print("=== 🤖 Gemcode ReAct Agent 自主研發測試 ===")
    
    # 定義一個極其複雜的任務
    task_id = "demo_001"
    prompt = """
    請自主執行以下步驟：
    1. 使用 list_files 查看工作區內容。
    2. 讀取 math_lib.py 並了解其功能。
    3. 寫一個測試程式 test_math.py，呼叫 math_lib.py 的 add 函數，並檢查 2+3 是否等於 5。
    4. 執行 test_math.py，如果失敗則修復它。
    5. 最後寫一份 summary.txt 告訴我最終結果。
    """
    
    # 模擬 task_manager (因為沒連 Firestore，我們 Mock 掉它)
    from unittest.mock import MagicMock
    import core.task_manager
    core.task_manager.task_manager = MagicMock()

    print(f"正在執行任務：{prompt}")
    await engine.run(task_id, "models/gemini-2.0-flash")
    
    print("\n=== 🎯 任務執行完畢，檢查成果 ===")
    for f in ["test_math.py", "summary.txt"]:
        path = os.path.join("workspace", f)
        if os.path.exists(path):
            with open(path, "r") as file:
                print(f"\n📄 {f} 內容：\n{file.read()}")
        else:
            print(f"\n❌ 找不到 {f}")

if __name__ == "__main__":
    asyncio.run(main())
