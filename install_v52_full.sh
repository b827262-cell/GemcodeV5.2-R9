echo "🚀 Ultra Pro Max V5.2 FULL Installing (Target: Current Directory)..."

# 建立 V5.2 模組化架構所需的資料夾
mkdir -p backend/{core,agent_core,tools,api}
mkdir -p frontend
mkdir -p workspace

# ======================
# requirements.txt
# 說明：定義後端所需的套件，包含 FastAPI, Git 控制以及 Pydantic 資料驗證
# ======================
cat << 'REQ' > requirements.txt
fastapi
uvicorn
python-dotenv
google-genai
gitpython
pydantic
REQ

# ======================
# backend/tools/file_tool.py
# 演算法：封裝底層檔案讀寫邏輯。
# 增加安全檢查，確保 workspace 目錄存在，並只列出實體檔案。
# ======================
cat << 'PY' > backend/tools/file_tool.py
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
PY

# ======================
# backend/tools/git_tool.py
# 說明：利用 gitpython 套件，讓 AI 具備版本控制能力。
# ======================
cat << 'PY' > backend/tools/git_tool.py
import git, os

BASE="./workspace"

def init_repo():
    if not os.path.exists(BASE):
        os.makedirs(BASE)
    if not os.path.exists(BASE+"/.git"):
        git.Repo.init(BASE)
    return "ok"

def commit(msg="update"):
    try:
        repo = git.Repo(BASE)
        repo.git.add(A=True)
        repo.index.commit(msg)
        return "committed"
    except Exception as e:
        return str(e)
PY

# ======================
# backend/tools/diff_tool.py
# 邏輯：使用 Python 內建的 difflib 產生標準的 Unified Diff 格式。
# ======================
cat << 'PY' > backend/tools/diff_tool.py
import difflib

def make_diff(a, b):
    # 比對 a(舊) 與 b(新) 的差異
    diff = list(difflib.unified_diff(a.splitlines(), b.splitlines(), lineterm=""))
    return "\n".join(diff) if diff else "目前內容與儲存版本一致，無差異。"
PY

# ======================
# backend/api/routes_file.py
# 說明：檔案系統的 API 接口，負責與前端對接檔案列表、讀取與儲存。
# ======================
cat << 'PY' > backend/api/routes_file.py
from fastapi import APIRouter
from pydantic import BaseModel
from tools.file_tool import *

router = APIRouter()

class FileData(BaseModel):
    name: str
    content: str

@router.get("/files")
def files():
    return list_files()

@router.get("/file/{name}")
def get_file(name: str):
    return {"content": read_file(name)}

@router.post("/file")
def save(data: FileData):
    return {"status": write_file(data.name, data.content)}
PY

# ======================
# backend/main.py
# 核心：整合所有 API 路由，並開啟 CORS 權限讓前端可以連線。
# ======================
cat << 'PY' > backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes_file import router as file_router

app = FastAPI()

# 跨域修復：允許前端 Port 3000 的請求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(file_router)

@app.get("/")
def root():
    return {"status": "V5.2 Backend Active"}
PY

# ======================
# frontend/app.js
# 說明：IDE 前端邏輯。包含 Monaco Editor 初始化與 Fetch API 互動。
# ======================
cat << 'JS' > frontend/app.js
require.config({ paths:{vs:'https://cdn.jsdelivr.net/npm/monaco-editor@0.45.0/min/vs'} })

let editor, currentFile = ""

require(['vs/editor/editor.main'],()=>{
 editor=monaco.editor.create(document.getElementById('editor'),{
  value:'# 歡迎使用 Ultra IDE V5.2\n# 請點選左側檔案開始編輯',
  language:'python',
  theme:'vs-dark',
  automaticLayout: true
 })
 loadFiles()
})

async function loadFiles(){
 let res=await fetch("http://localhost:8000/files")
 let files=await res.json()
 let sb=document.getElementById("sidebar")
 sb.innerHTML='<div style="color:#888; font-size:12px; margin-bottom:10px;">WORKSPACE</div>'
 files.forEach(f=>{
  let d=document.createElement("div")
  d.className = "file-item"
  d.innerText="📄 " + f
  d.onclick=()=>openFile(f)
  sb.appendChild(d)
 })
}

async function openFile(name){
 currentFile=name
 document.getElementById("current-file-label").innerText = `正在編輯: ${name}`
 let res=await fetch("http://localhost:8000/file/"+name)
 let data=await res.json()
 editor.setValue(data.content)
}

async function save(){
 let content=editor.getValue()
 let targetName = currentFile || prompt("請輸入新檔案名稱:", "main.py")
 if (!targetName) return
 
 await fetch("http://localhost:8000/file",{
  method:"POST",
  headers:{'Content-Type':'application/json'},
  body:JSON.stringify({name:targetName, content:content})
 })
 currentFile = targetName
 document.getElementById("current-file-label").innerText = `正在編輯: ${targetName}`
 loadFiles()
}
JS

echo "✅ V5.2 結構部署完成！"
echo "👉 請確保您的 .env 已手動放置於 ~/project/ultra-pro-max-v5/.env"
