import asyncio
from core.llm_router import router
from core.task_manager import task_manager
from tools.file_tool import list_files, read_file, write_file
from tools.git_tool import init_repo, commit

class AutoEngineer:
    async def run(self, task_id: str, model_name: str):
        task = task_manager.tasks.get(task_id)
        prompt = task["prompt"]

        try:
            # 1. 觀察環境
            task_manager.update(task_id, "🔍 [Observer] 正在掃描 Workspace...")
            files = list_files()
            context = ""
            if files:
                task_manager.update(task_id, f"📂 發現現有檔案: {', '.join(files)}，正在讀取上下文...")
                # 讀取第一個檔案作為參考內容（簡化版邏輯）
                context = read_file(files[0])

            # 2. 思考規劃
            task_manager.update(task_id, "🧠 [Planner] 正在構思代碼架構...")
            full_prompt = f"現有代碼：\n{context}\n\n使用者需求：{prompt}"
            plan = router.call("plan", full_prompt, model_name)
            
            # 3. 撰寫代碼
            task_manager.update(task_id, "💻 [Coder] 正在產出 Python 程式碼...")
            code = router.call("code", plan, model_name)
            
            # 4. 執行存檔與版本控制
            filename = f"solution_{task_id[:8]}.py"
            write_file(filename, code)
            task_manager.update(task_id, f"✅ 已存檔: {filename}", code=code)
            
            init_repo()
            commit(f"AI 生成代碼: {filename}")
            task_manager.update(task_id, "📦 [Git] 已自動提交變更。")
            
            task_manager.complete(task_id)

        except Exception as e:
            task_manager.update(task_id, f"❌ 系統崩潰: {str(e)}")

engine = AutoEngineer()
