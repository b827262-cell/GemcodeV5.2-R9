import asyncio
import os
import subprocess
import re
from google import genai
from google.genai import types
from tools import file_tool
from core.rag_manager import RAGManager
from core.task_manager import task_manager

class AgentEngine:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None
        self.rag = RAGManager(self.client) if self.client else None
        self.ws_manager = None
        self.current_loop = None

    async def _log(self, task_id, msg, type="status"):
        if self.ws_manager:
            await self.ws_manager.broadcast({"task_id": task_id, "type": type, "content": msg})

    async def run(self, task_id: str, model: str, ws_manager=None):
        if not self.client: return
        self.ws_manager = ws_manager
        self.current_loop = asyncio.get_event_loop()
        
        try:
            task_data = task_manager.get_task(task_id)
            main_prompt = task_data.get("prompt", "")

            # --- 第一步：[Think] 深度思考與 RAG 分析 ---
            await self._log(task_id, "🧠 [Step 1: Think] 正在分析現有代碼與需求關聯性...", "status")
            await asyncio.to_thread(self.rag.update_index)
            context = self.rag.query(main_prompt)

            # --- 第二步：[Ask/Refine] 方案推演 ---
            await self._log(task_id, "🔍 [Step 2: Refine] 正在推演最佳實作路徑...", "status")
            refine_prompt = f"分析以下需求與上下文，並給出一個實作思路。上下文：\n{context}\n\n需求：{main_prompt}"
            refine_res = await asyncio.to_thread(self.client.models.generate_content, model=model, contents=refine_prompt)
            await self._log(task_id, refine_res.text, "thought")

            # --- 第三步：[Design] 定架構 (Minimal Design) ---
            await self._log(task_id, "📐 [Step 3: Design] 正在根據 Minimal Design 標準決定專案結構...", "status")
            arch_prompt = f"根據上述思路，決定複雜度等級 (Level 1-3) 與檔案清單。請只輸出步驟，嚴禁過度設計。需求：{main_prompt}"
            arch_res = await asyncio.to_thread(self.client.models.generate_content, model=model, contents=arch_prompt)
            sub_tasks = [s.strip() for s in arch_res.text.strip().split("\n") if s.strip()]
            await self._log(task_id, "✅ 架構已定：\n" + "\n".join(sub_tasks), "status")

            # --- 第四步：[Code] 精準編碼 ---
            await self._log(task_id, "💻 [Step 4: Code] 開始進入編碼階段...", "status")
            chat = self.client.chats.create(
                model=model,
                config=types.GenerateContentConfig(
                    tools=self._get_wrapped_tools(task_id),
                    system_instruction="你是一個極簡主義工程師。請按照設計好的架構精準編碼，使用 write_workspace_file 儲存。"
                )
            )

            for step in sub_tasks:
                await self._log(task_id, f"🚧 執行階段: {step}", "status")
                response = await asyncio.to_thread(chat.send_message, f"執行步驟: {step}")
                for part in response.candidates[0].content.parts:
                    if part.text: await self._log(task_id, part.text, "thought")
                    if part.function_call: await self._log(task_id, f"調用工具: {part.function_call.name}", "action")

            await self._log(task_id, "🎊 任務圓滿達成！代碼已依照最小化原則實作完畢。", "done")
            task_manager.complete(task_id)

        except Exception as e:
            await self._log(task_id, f"❌ 任務失敗: {str(e)}", "error")
            task_manager.complete(task_id)

    # ... (其餘輔助方法 _get_wrapped_tools, _broadcast_sync 保持不變)
    def _broadcast_sync(self, task_id, msg_type, content):
        if self.ws_manager and self.current_loop:
            self.current_loop.create_task(self.ws_manager.broadcast({"task_id": task_id, "type": msg_type, "content": content}))

    def _get_wrapped_tools(self, task_id):
        def list_workspace_files() -> list: return file_tool.list_files()
        def read_workspace_file(filename: str) -> str: return file_tool.read_file(filename)
        def write_workspace_file(filename: str, content: str) -> str:
            res = file_tool.write_file(filename, content)
            self._broadcast_sync(task_id, "file_update", {"filename": filename, "content": content})
            return res
        def execute_test_code(code: str) -> str:
            dangerous = [r"os\.system\(", r"subprocess\.", r"shutil\.rmtree\(", r"rm\s+-rf"]
            for p in dangerous:
                if re.search(p, code): return f"Security Blocked: {p}"
            try:
                import sys
                process = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=15)
                return (process.stdout + process.stderr) or "Execution Success."
            except Exception as e: return str(e)
        return [list_workspace_files, read_workspace_file, write_workspace_file, execute_test_code]

engine = AgentEngine()
