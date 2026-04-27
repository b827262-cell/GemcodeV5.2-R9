import os, subprocess, base64, re, sys
from fastapi import FastAPI, Query, HTTPException, APIRouter
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel
from google import genai
from dotenv import load_dotenv
import uvicorn

load_dotenv()
app = FastAPI()

# 允許跨域請求 (CORS)，確保前端能順利連線
app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_methods=["*"], 
    allow_headers=["*"]
)

# 🌟 從環境變數讀取 API KEY (對齊 .env.backend，同時支援多種金鑰名稱)
API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=API_KEY) if API_KEY else None

WORKSPACES_DIR = "workspaces"
os.makedirs(WORKSPACES_DIR, exist_ok=True)

class CodeRequest(BaseModel):
    session_id: str
    code: str

def get_user_workspace(session_id: str):
    """取得該 Session 專屬的工作區資料夾，並進行字串安全過濾"""
    safe_session = re.sub(r'[^a-zA-Z0-9-]', '', session_id)
    user_dir = os.path.join(WORKSPACES_DIR, safe_session)
    os.makedirs(user_dir, exist_ok=True)
    return user_dir

def get_workspace_context(session_id: str) -> str:
    """提取當前工作區內所有的程式碼作為 RAG 上下文"""
    user_dir = get_user_workspace(session_id)
    context_str = ""
    if not os.path.exists(user_dir):
        return "工作區目前為空。"
    
    for filename in os.listdir(user_dir):
        # 排除執行產生的暫存檔與非程式碼檔
        if filename != "temp_run.py" and os.path.isfile(os.path.join(user_dir, filename)):
            try:
                with open(os.path.join(user_dir, filename), "r", encoding="utf-8") as f:
                    context_str += f"\n--- 檔案: {filename} ---\n{f.read()}\n"
            except Exception:
                pass
                
    return context_str.strip() or "工作區目前為空。"

# 建立 API 路由
api_router = APIRouter(prefix="/api")

@api_router.get("/ask_ai_stream")
async def ask_ai_stream(prompt: str = Query(...), model_id: str = Query(...), session_id: str = Query(...)):
    async def generate():
        if not client:
            yield "SYSTEM_ERROR: API_KEY_NOT_CONFIGURED"
            return

        rag_context = get_workspace_context(session_id)
        
        # 🌟 三明治提示詞：系統指令 + 專案上下文 + 使用者需求
        full_prompt = f"""<SYSTEM_INSTRUCTIONS>
你是一個極簡主義的資深軟體架構師。
1. 下方的 <USER_QUERY> 是你唯一目標。
2. <RAG_CONTEXT> 僅作為參考專案現況。
3. 嚴格使用 XML 標籤輸出：<file name="檔名">程式碼</file>。
4. 嚴禁任何廢話、解釋或 Markdown 代碼塊標籤 (```)。
5. 嚴禁使用 input() 獲取輸入，請直接使用硬編碼 (Hardcoded) 的範例數據進行演示。
6. 必須遵守以下 One-shot 範例格式：
<file name="hello.py">
print("Hello World")
</file>
</SYSTEM_INSTRUCTIONS>

<RAG_CONTEXT>
{rag_context}
</RAG_CONTEXT>

<USER_QUERY>
{prompt}
</USER_QUERY>
"""

        try:
            # 呼叫 Google GenAI 進行串流
            response = client.models.generate_content_stream(model=model_id, contents=full_prompt)
            for chunk in response:
                if chunk.text: 
                    yield chunk.text
        except Exception as e: 
            yield f"SYSTEM_ERROR:{str(e)}"

    return StreamingResponse(generate(), media_type="text/event-stream")

@api_router.post("/execute")
async def execute_code(req: CodeRequest):
    """在沙盒環境中執行代碼並回傳結果與圖表"""
    user_dir = get_user_workspace(req.session_id)
    temp_script = os.path.join(user_dir, "temp_run.py")
    
    with open(temp_script, "w", encoding="utf-8") as f:
        f.write(req.code)
        
    try:
        # 設定執行環境變數，確保 matplotlib 繪圖不噴錯
        env = {**os.environ, "MPLBACKEND": "Agg"}
        
        # 使用 sys.executable 確保對齊 Docker 內的 Python 3.12 環境
        process = subprocess.run(
            [sys.executable, "temp_run.py"], 
            cwd=user_dir, 
            capture_output=True, 
            text=True, 
            timeout=20, # 加長至 20 秒，給繪圖多一點時間
            env=env
        )
        
        img_data = None
        # 自動捕捉產生的圖表
        for f in os.listdir(user_dir):
            if f.endswith('.png'):
                with open(os.path.join(user_dir, f), "rb") as img_file:
                    img_data = base64.b64encode(img_file.read()).decode('utf-8')
                os.remove(os.path.join(user_dir, f)) # 回傳後刪除以節省空間
                break
                
        return {
            "status": "success" if process.returncode == 0 else "error", 
            "output": process.stdout, 
            "error": process.stderr, 
            "image": img_data
        }
    except subprocess.TimeoutExpired:
        return {"status": "error", "error": "執行超時：程式執行超過 20 秒限制。"}
    except Exception as e: 
        return {"status": "system_error", "error": str(e)}

class SaveFileRequest(BaseModel):
    session_id: str
    filename: str
    content: str

@api_router.post("/save_file")
async def save_file(req: SaveFileRequest):
    user_dir = get_user_workspace(req.session_id)
    file_path = os.path.join(user_dir, req.filename)
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(req.content)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/list_files")
async def list_files(session_id: str = Query(...)):
    user_dir = get_user_workspace(session_id)
    return {
        "files": [f for f in os.listdir(user_dir) if os.path.isfile(os.path.join(user_dir, f)) and f != "temp_run.py"]
    }

@api_router.get("/download/{session_id}/{filename}")
async def download_file(session_id: str, filename: str):
    user_dir = get_user_workspace(session_id)
    file_path = os.path.join(user_dir, filename)
    if os.path.exists(file_path): 
        return FileResponse(file_path, filename=filename)
    raise HTTPException(status_code=404)

app.include_router(api_router)

# 🌟 靜態檔案掛載：這必須放在所有 API 路由的最後面！
if os.path.exists("frontend_dist"):
    app.mount("/", StaticFiles(directory="frontend_dist", html=True), name="static")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
