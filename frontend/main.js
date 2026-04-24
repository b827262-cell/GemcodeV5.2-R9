/**
 * GETCODE IDE V9.0 - 核心解析與安全執行引擎
 * 採用物理切分法 (Format Control) 徹底解決標籤解析 BUG
 */

const terminal = document.getElementById('terminal-output');
const logs = document.getElementById('logs');
const aiBtn = document.getElementById('ai-btn');
const runBtn = document.getElementById('run-btn');
const tabBar = document.getElementById('tab-bar');
const fileList = document.getElementById('file-list');

// 🌟 1. 狀態與 Session 管理
const sessionId = typeof __session_id !== 'undefined' ? __session_id : Math.random().toString(36).substring(2, 15);
let fileContents = { "main.py": "# 系統已就緒，請輸入指令...\n" };
let currentActiveFile = "main.py";
let isStreaming = false;

const HEADERS = {
    'ngrok-skip-browser-warning': 'true',
    'Content-Type': 'application/json'
};

// 初始化 CodeMirror 編輯器
const editor = CodeMirror.fromTextArea(document.getElementById('editor-content'), {
    mode: "python",
    theme: "material-darker",
    lineNumbers: true,
    lineWrapping: true,
    matchBrackets: true,
    autoCloseBrackets: true,
    indentUnit: 4
});
editor.setValue(fileContents[currentActiveFile]);

const addLog = (msg, type = "status") => {
    const colors = { error: "#f85149", status: "#d2a8ff", success: "#3fb950", warning: "#ffa657", system: "#8b949e" };
    if (logs) {
        const time = new Date().toLocaleTimeString();
        logs.innerHTML += `<br><span style="color: #8b949e;">[${time}]</span> <span style="color: ${colors[type] || "#d1d5da"};">${msg}</span>`;
        logs.scrollTop = logs.scrollHeight;
    }
};

/**
 * 🏆 終極版解析引擎 - 採用物理切分策略 (Format Control)
 * 解決痛點：
 * 1. 巢狀標籤：<file><file></file></file> 不會互相污染。
 * 2. 標籤變體：處理 <file >, </ file>, <</file> 等 AI 亂碼。
 * 3. 內容保護：不依賴 Regex 抓取中間內容，確保程式碼一字不漏。
 */
const runParsingEngine = (rawText) => {
    let parsedFiles = {};
    let parsedAny = false;

    // 🧹 第一步：環境大掃除 (陣列過濾法)
    // 改用「純字串替換法」，不使用複雜的正則表達式，可讀性更高且不易出錯
    let cleanText = rawText;
    const markdownTagsToRemove = [
        "```python\n", "```python", 
        "```javascript\n", "```javascript",
        "```html\n", "```html",
        "```css\n", "```css",
        "```\n", "```"
    ];
    
    // 透過迴圈，利用 split().join("") 達到全域安全替換的效果
    markdownTagsToRemove.forEach(tag => {
        cleanText = cleanText.split(tag).join(""); 
    });

    // ✂️ 第二步：物理切分 (Physical Splitting)
    // 我們直接拿 "<file " 當作菜刀，把整坨字串強制切斷成數個區塊
    let parts = cleanText.split(/<\s*file\s+/i);

    // 迴圈從 1 開始，因為 parts[0] 是第一個 <file 出現之前的文字（通常是開場白廢話）
    for (let i = 1; i < parts.length; i++) {
        let part = parts[i];

        // 1. 提取檔名：在切開的區塊開頭尋找 name="xxx"
        let nameMatch = part.match(/^name\s*=\s*['"]([^'"]+)['"]/i);
        let fname = nameMatch ? nameMatch[1].trim() : `module_${i}.py`;

        // 2. 定位內容起點：尋找標籤結束的右角括號 '>'
        let contentStart = part.indexOf(">");
        if (contentStart === -1) continue; 

        // 程式碼內容從 '>' 之後開始
        let code = part.substring(contentStart + 1);

        // 3. 處理結尾與雜質：
        // 尋找此區塊內第一個出現的任何形式的 </file> (包含 <</file> 等變體) 並斬斷它
        let closeMatch = code.match(/<+?\/?\s*file[^>]*>/i);
        if (closeMatch) {
            code = code.substring(0, closeMatch.index);
        }

        // 4. 清理並儲存
        code = code.trim();
        if (code) {
            parsedFiles[fname] = code;
            parsedAny = true;
        }
    }

    // 🥉 第三步：回傳結果
    if (parsedAny) {
        return { type: "files", files: parsedFiles };
    }
    
    return { type: "raw", content: rawText };
};

// 🌟 2. AI 生成邏輯 (HTTP Streaming)
aiBtn.onclick = async () => {
    const prompt = document.getElementById('task-input').value;
    const model = document.getElementById('model-select').value;
    if (!prompt) return;

    aiBtn.innerText = "🧠 思考中...";
    aiBtn.disabled = true;
    addLog("🚀 Agent 啟動，正在獲取串流...", "status");

    let fullTextAccumulator = "";
    isStreaming = true;

    try {
        const response = await fetch(`/api/ask_ai_stream?prompt=${encodeURIComponent(prompt)}&model_id=${model}&session_id=${sessionId}`, {
            headers: { 'ngrok-skip-browser-warning': 'true' }
        });

        if (!response.ok) throw new Error(`連線失敗 (${response.status})`);

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;
            const chunk = decoder.decode(value);
            fullTextAccumulator += chunk;
            
            // 串流期間：僅顯示原始內容作為視覺反饋
            if (currentActiveFile === "main.py") {
                editor.setValue(fullTextAccumulator);
                editor.setCursor(editor.lineCount(), 0);
            }
        }

        isStreaming = false;
        addLog("🏁 串流完成，執行安全解析與分配...", "status");
        
        const result = runParsingEngine(fullTextAccumulator);

        if (result.type === "files") {
            const updatedFileNames = Object.keys(result.files);
            let validUpdates = 0;

            // 🛡️ 多檔案覆蓋保護策略
            Object.entries(result.files).forEach(([fname, code]) => {
                if (!code || code.trim().length < 5) {
                    addLog(`⚠️ ${fname} 內容異常，已跳過覆蓋以保護原代碼`, "warning");
                    return;
                }
                fileContents[fname] = code;
                validUpdates++;
            });

            if (validUpdates > 0) {
                // 🧠 聰明切換：如果目前正在看的檔案沒有被更新，才切換到第一個被更新的檔案
                if (!updatedFileNames.includes(currentActiveFile)) {
                    currentActiveFile = updatedFileNames[0];
                }
                
                updateTabsUI();
                editor.setValue(fileContents[currentActiveFile]);
                addLog(`✅ 任務成功！安全更新了 ${validUpdates} 個檔案。`, "success");
            }
        } else {
            addLog("📢 未偵測到有效結構化代碼，保留現有檔案內容。", "warning");
            editor.setValue(fileContents[currentActiveFile] || "");
        }

        await refreshFileList();

    } catch (e) {
        isStreaming = false;
        addLog(`❌ 錯誤: ${e.message}`, "error");
        editor.setValue(fileContents[currentActiveFile] || "");
    } finally {
        aiBtn.disabled = false;
        aiBtn.innerText = "生成專案代碼";
    }
};

// 🌟 3. 執行與工作區管理
const refreshFileList = async () => {
    try {
        const res = await fetch(`/api/list_files?session_id=${sessionId}`, { headers: HEADERS });
        const data = await res.json();
        if (fileList) {
            fileList.innerHTML = data.files.length ? "" : "工作區暫無檔案";
            data.files.forEach(f => {
                const div = document.createElement('div');
                div.className = "file-item";
                div.innerHTML = `<span>📄 ${f}</span><a class="file-download-link" href="/api/download/${sessionId}/${f}" target="_blank">📥</a>`;
                fileList.appendChild(div);
            });
        }
    } catch (e) {}
};

const updateTabsUI = () => {
    tabBar.innerHTML = '';
    Object.keys(fileContents).forEach(fname => {
        const div = document.createElement('div');
        div.className = `tab ${fname === currentActiveFile ? 'active' : ''}`;
        div.innerText = fname;
        div.onclick = () => {
            if (isStreaming) return; // 串流中禁止手動切換
            fileContents[currentActiveFile] = editor.getValue();
            currentActiveFile = fname;
            updateTabsUI();
            editor.setValue(fileContents[currentActiveFile]);
        };
        tabBar.appendChild(div);
    });
};

runBtn.onclick = async () => {
    if (isStreaming) return;
    
    fileContents[currentActiveFile] = editor.getValue();
    const code = fileContents[currentActiveFile];
    if (!code || code.length < 5) return;

    runBtn.disabled = true;
    terminal.innerHTML = '<span style="color: #8b949e;">正在啟動沙盒執行環境...</span>';

    try {
        const res = await fetch('/api/execute', {
            method: 'POST',
            headers: HEADERS,
            body: JSON.stringify({ session_id: sessionId, code: code })
        });
        const data = await res.json();
        
        terminal.innerHTML = "";
        if (data.image) {
            terminal.innerHTML = `<img src="data:image/png;base64,${data.image}" style="max-width:100%; border-radius:4px; margin-bottom: 10px;">`;
        }
        
        const pre = document.createElement('pre');
        pre.style.color = data.status === "error" ? "#f85149" : "#d1d5da";
        pre.textContent = data.output || data.error || "執行完成 (無終端輸出)";
        terminal.appendChild(pre);
        
    } catch (e) {
        terminal.innerHTML = `<span style="color:#f85149;">❌ 執行失敗: ${e.message}</span>`;
    }
    runBtn.disabled = false;
};

// 初始化啟動
updateTabsUI();
refreshFileList();
addLog("GETCODE V9.0 物理隔離解析引擎已就緒。", "system");
