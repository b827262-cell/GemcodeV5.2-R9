require.config({ paths:{vs:'https://cdn.jsdelivr.net/npm/monaco-editor@0.45.0/min/vs'} })
let editor, currentFile = ""

const API_BASE = "https://ultra-backend-569094769218.asia-east1.run.app";

require(['vs/editor/editor.main'],()=>{
 editor=monaco.editor.create(document.getElementById('editor'),{
  value:'# 歡迎來到 GEMCODE IDE\n# 選擇一個檔案或輸入任務開始...',
  language:'python', theme:'vs-dark', automaticLayout: true, fontSize: 14
 })
 loadFiles()
})

async function loadFiles(){
 try {
  // 🌟 修正：確保加上 /files 獲取清單
  let res=await fetch(`${API_BASE}/files`)
  let files=await res.json()
  let sb=document.getElementById("file-list-container")
  sb.innerHTML='<div style="color:#484f58; font-size:11px; margin-bottom:10px; letter-spacing:1px;">WORKSPACE</div>'
  files.forEach(f=>{
   let d=document.createElement("div")
   d.className = "file-item"
   d.innerText="📄 " + f
   d.onclick=()=>openFile(f)
   sb.appendChild(d)
  })
 } catch (e) { console.error("無法載入檔案清單", e) }
}

async function openFile(name){
 currentFile=name
 document.getElementById("current-file-label").innerText = `EDITING: ${name}`
 let res=await fetch(`${API_BASE}/file/`+name)
 let data=await res.json()
 editor.setValue(data.content)
}

async function save(){
 let content=editor.getValue()
 let targetName = currentFile || prompt("請輸入新檔案名稱:", "main.py")
 if (!targetName) return
 await fetch(`${API_BASE}/file`,{
  method:"POST", headers:{'Content-Type':'application/json'},
  body:JSON.stringify({name:targetName, content:content})
 })
 currentFile = targetName
 document.getElementById("current-file-label").innerText = `EDITING: ${targetName}`
 loadFiles()
 alert("✅ 檔案儲存成功")
}

async function submitTask() {
    const promptValue = document.getElementById('prompt-input').value;
    const model = document.getElementById('model-name').value;
    if(!promptValue) return alert("請輸入開發目標！");

    document.getElementById('logs').innerHTML = '<div class="log-entry">🚀 任務已提交...</div>';
    
    try {
        // 🌟 修正：任務提交必須去 /task
        const res = await fetch(`${API_BASE}/task`, {
            method: "POST",
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ prompt: promptValue, model: model })
        });
        const data = await res.json();
        startPolling(data.task_id);
    } catch (e) { alert("後端連線失敗！"); }
}

function startPolling(taskId) {
    const timer = setInterval(async () => {
        // 🌟 修正：輪詢狀態必須去 /task/${taskId}
        const res = await fetch(`${API_BASE}/task/${taskId}`);
        const data = await res.json();
        
        const logHtml = data.logs.map(log => `<div class="log-entry">${log}</div>`).join('');
        document.getElementById('logs').innerHTML = logHtml;
        
        if(data.code) editor.setValue(data.code);

        if(data.status === 'done' || data.status === 'error') {
            clearInterval(timer);
            loadFiles();
        }
    }, 1000);
}
