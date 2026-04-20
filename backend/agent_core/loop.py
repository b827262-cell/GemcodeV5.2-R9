import asyncio
import os
from google import genai
from core.task_manager import task_manager

class AgentEngine:
    def __init__(self):
        # 初始化 Google GenAI (會自動抓取 .env 的 GEMINI_API_KEY)
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None

    async def run(self, task_id: str, model: str):
        try:
            # 🌟 關鍵修復 1：改用 Firestore 讀取方法 (不再用 .tasks)
            task = task_manager.get_task(task_id)
            if "error" in task:
                return

            prompt = task.get("prompt", "")
            
            # 🌟 關鍵修復 2：改用 task_manager.update() 來即時更新雲端 Log
            task_manager.update(task_id, "🔍 [Observer] 已讀取任務，準備分析需求...")
            await asyncio.sleep(1) # 讓前端有時間感受跳動
            
            if not self.client:
                task_manager.update(task_id, "❌ [系統錯誤] 找不到 GEMINI_API_KEY，請檢查 .env 檔案！")
                task_manager.complete(task_id)
                return

            task_manager.update(task_id, f"🧠 [Planner] 正在與 {model} 構思架構...")
            
            # 清理模型名稱以符合 SDK 格式
            clean_model_name = model.replace("models/", "")
            
            # 呼叫 Gemini AI
            response = self.client.models.generate_content(
                model=clean_model_name,
                contents=f"你是一個資深工程師。請根據以下需求寫出 Python 程式碼。\n請只提供程式碼，不要加上 Markdown 語法 (```python) 或任何解釋：\n\n{prompt}"
            )
            
            # 清理 AI 偶爾會亂加的 Markdown 標記
            generated_code = response.text.strip()
            if generated_code.startswith("```python"):
                generated_code = generated_code[9:-3].strip()
            elif generated_code.startswith("```"):
                generated_code = generated_code[3:-3].strip()

            task_manager.update(task_id, "💻 [Coder] 程式碼撰寫完畢，正在同步至雲端...")
            await asyncio.sleep(1)
            
            # 🌟 關鍵修復 3：將產生的代碼與完成狀態寫入 Firestore
            task_manager.update(task_id, "✅ 任務大功告成！", code=generated_code)
            task_manager.complete(task_id)

        except Exception as e:
            # 如果發生任何問題，把錯誤原因直接噴在網頁上方便 Debug
            task_manager.update(task_id, f"❌ [系統崩潰] 執行發生例外錯誤: {str(e)}")
            task_manager.complete(task_id)

engine = AgentEngine()
