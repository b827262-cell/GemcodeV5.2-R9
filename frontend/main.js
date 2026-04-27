/**
 * GETCODE IDE V9.0 - 終極融合版 (V5 分頁架構 + 物理隔離解析 + 十字聯動)
 */

const terminal = document.getElementById('terminal-output');
const logs = document.getElementById('logs');
const aiBtn = document.getElementById('ai-btn');
const runBtn = document.getElementById('run-btn');
const tabBar = document.getElementById('tab-bar');
const fileList = document.getElementById('file-list');

// 🌟 1. 狀態與 Session 管理
const apiUrl = ''; // 讓它自動使用當前 Cloud Run 的網域
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
        logs.innerHTML += `<div><span style="color: #8b949e;">[${time}]</span> <span style="color: ${colors[type] || "#d1d5da"};">${msg}</span></div>`;
        logs.scrollTop = logs.scrollHeight;
    }
};

/**
 * 🏆 終極版解析引擎 - 四層防禦物理切分
 * 作用：透過強力清洗、寬鬆切分、容錯結尾與終極 Fallback，確保代碼解析 100% 成功。
 */
const runParsingEngine = (rawText) => {
    let parsedFiles = {};
    let foundAnyFile = false;

    console.log("🧪 [PARSER] RAW:", rawText);

    // ==========================================
    // 🥇 第1層：強力清洗
    // ==========================================
    let cleanText = rawText
        .replace(/```[a-zA-Z]*\n?/g, '') // 移除 Markdown 開頭
        .replace(/```/g, '')             // 移除 Markdown 結尾
        .replace(/\r/g, '')              // 移除換行符雜質
        .replace(/^[^\<]*/, '')          // 移除第一個 < 出現之前的廢話
        .trim();

    console.log("🧪 [PARSER] CLEAN:", cleanText);

    // ==========================================
    // 🥈 第2層：寬鬆切分 (支援 <file name="xxx"> 或 <file name='xxx'>)
    // ==========================================
    const segments = cleanText.split(/<file\s+name\s*=\s*["']/i);

    for (let i = 1; i < segments.length; i++) {
        const segment = segments[i];

        // 抓取檔名直到結束引號 ["']，接著跳過可能的空格與結束角括號 [>]
        const nameMatch = segment.match(/^([^"'>\n]+)["']\s*>/);
        if (!nameMatch) continue;

        const fileName = nameMatch[1].trim();
        let content = segment.substring(nameMatch[0].length);

        // ==========================================
        // 🥉 第3層：容錯結尾處理
        // ==========================================
        const closeTagIndex = content.search(/<\/file>/i);

        if (closeTagIndex !== -1) {
            // 如果有乖乖寫結尾，就切到結尾前
            content = content.substring(0, closeTagIndex);
        } else {
            // 如果沒寫結尾 (例如串流截斷)，則切到下一個 <file 標籤之前
            const nextFileIndex = content.search(/<file\s+name/i);
            if (nextFileIndex !== -1) {
                content = content.substring(0, nextFileIndex);
            }
        }

        content = content.trim();

        if (fileName && content.length > 0) {
            parsedFiles[fileName] = content;
            foundAnyFile = true;
            addLog(`📂 解析成功: ${fileName} (${content.length} 字元)`, "success");
        }
    }

    // ==========================================
    // 🏅 第4層：終極 Fallback (完全沒有 <file> 標籤時)
    // ==========================================
    if (!foundAnyFile) {
        // 移除所有可能是殘餘標籤的文字，剩下的當作 main.py
        let fallback = cleanText.replace(/<\/?[^>]+>/g, '').trim();

        if (fallback.length > 10) {
            addLog("⚠️ 未偵測到結構標籤，啟動 Fallback 模式...", "warning");
            parsedFiles["main.py"] = fallback;
            foundAnyFile = true;
        }
    }

    if (foundAnyFile) {
        return { type: "files", files: parsedFiles };
    }
    
    return { type: "raw", content: rawText };
};

// ==========================================
// 📡 AI 生成邏輯 (HTTP Streaming)
// ==========================================
aiBtn.onclick = async () => {
    const prompt = document.getElementById('task-input').value;
    const model = document.getElementById('model-select').value;
    if (!prompt) return addLog("請輸入任務需求", "warning");

    aiBtn.innerText = "🧠 思考中...";
    aiBtn.disabled = true;
    addLog("🚀 Agent 啟動，正在獲取串流...", "status");

    let fullTextAccumulator = "";
    isStreaming = true;

    try {
        // 利用 Vite Proxy 自動轉發 /api 請求
        const response = await fetch(`${apiUrl}/api/ask_ai_stream?prompt=${encodeURIComponent(prompt)}&model_id=${model}&session_id=${sessionId}`, {
            headers: HEADERS
        });

        if (!response.ok) throw new Error(`連線失敗 (${response.status})`);

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;
            fullTextAccumulator += decoder.decode(value);
            
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

            Object.entries(result.files).forEach(([fname, code]) => {
                if (!code || code.trim().length < 5) return;
                fileContents[fname] = code;
                validUpdates++;
            });

            if (validUpdates > 0) {
                if (!updatedFileNames.includes(currentActiveFile)) currentActiveFile = updatedFileNames[0];
                updateTabsUI();
                editor.setValue(fileContents[currentActiveFile]);
                addLog(`✅ 任務成功！安全更新了 ${validUpdates} 個檔案。`, "success");

                // 🌟 自動存檔邏輯
                Object.entries(result.files).forEach(([fileName, fileContent]) => {
                    if (!fileContent || fileContent.trim().length < 5) return;
                    fetch(`${apiUrl}/api/save_file`, {
                        method: 'POST',
                        headers: HEADERS,
                        body: JSON.stringify({
                            session_id: sessionId,
                            filename: fileName,
                            content: fileContent
                        })
                    }).then(() => refreshFileList());
                });
            }
        } else {
            addLog("📢 未偵測到有效結構化代碼，保留現有檔案內容。", "warning");
            editor.setValue(fileContents[currentActiveFile] || "");
        }
        await refreshFileList();

    } catch (e) {
        isStreaming = false;
        addLog(`❌ 錯誤: ${e.message}`, "error");
    } finally {
        aiBtn.disabled = false;
        aiBtn.innerText = "生成專案代碼 (多檔案)";
    }
};

// ==========================================
// 💾 本機檔案操作邏輯 (純前端，不需後端)
// ==========================================
document.getElementById('btn-open').onclick = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '*/*';
    input.onchange = (e) => {
        const file = e.target.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = (event) => {
            const content = event.target.result;
            const fileName = file.name;
            fileContents[fileName] = content;
            currentActiveFile = fileName;
            updateTabsUI();
            editor.setValue(content);
            addLog(`📂 成功從本機載入檔案: ${fileName}`, "success");
        };
        reader.readAsText(file);
    };
    input.click();
};

document.getElementById('btn-save').onclick = () => {
    const content = editor.getValue();
    if (!content) return addLog("❌ 編輯器內無內容可儲存", "warning");
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = currentActiveFile || 'main.py';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    addLog(`💾 已將 ${link.download} 下載至本機`, "success");
};

// ==========================================
// 💻 執行與工作區分頁管理
// ==========================================
const refreshFileList = async () => {
    try {
        const res = await fetch(`${apiUrl}/api/list_files?session_id=${sessionId}`, { headers: HEADERS });
        const data = await res.json();
        if (fileList && data.files) {
            fileList.innerHTML = data.files.length ? "" : "工作區暫無檔案";
            data.files.forEach(f => {
                const div = document.createElement('div');
                div.className = "file-item";
                div.style = "padding: 5px; cursor: pointer; border-bottom: 1px solid #30363d; font-size: 13px; display: flex; justify-content: space-between;";
                div.innerHTML = `<span>📄 ${f}</span><a style="color: #58a6ff; text-decoration: none;" href="${apiUrl}/api/download/${sessionId}/${f}" target="_blank">📥</a>`;
                fileList.appendChild(div);
            });
        }
    } catch (e) {}
};

const updateTabsUI = () => {
    if (!tabBar) return;
    tabBar.innerHTML = '';
    Object.keys(fileContents).forEach(fname => {
        const div = document.createElement('div');
        div.className = `tab ${fname === currentActiveFile ? 'active' : ''}`;
        div.innerText = fname;
        div.onclick = () => {
            if (isStreaming) return;
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

    // 🌟 網頁檔案檢查邏輯
    const ext = currentActiveFile.split('.').pop().toLowerCase();
    if (['html', 'css', 'js'].includes(ext)) {
        terminal.innerHTML = `
            <div style="color: #58a6ff; background: #161b22; padding: 10px; border-radius: 4px; border-left: 4px solid #58a6ff;">
                💡 <b>系統提示：前端網頁預覽說明</b><br>
                您目前正處於網頁檔案 (<code>${currentActiveFile}</code>)。<br>
                Python 沙盒主要負責後端運算，無法直接渲染網頁介面。<br>
                👉 <b>建議做法：</b> 請點擊左側 <b>「💾 儲存本機」</b> 下載專案檔案，並在您的電腦上直接開啟 HTML 檔案即可看到網頁效果！
            </div>
        `;
        return;
    }

    runBtn.disabled = true;
    terminal.innerHTML = '<span style="color: #8b949e;">正在啟動沙盒執行環境...</span>';

    try {
        const res = await fetch(`${apiUrl}/api/execute`, {
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
        
        // 🌟 GUI 程式偵測與提示邏輯
        if (data.error && data.error.includes("libtk8.6.so")) {
            terminal.innerHTML += `
                <div style="color: #ffa657; background: #341f00; padding: 10px; border-radius: 4px; margin-bottom: 10px; border-left: 4px solid #ffa657;">
                    ⚠️ <b>系統提示：偵測到桌面視窗程式 (Tkinter)</b><br>
                    雲端沙盒環境沒有顯示器，無法直接執行 GUI 視窗。<br>
                    👉 <b>建議做法：</b> 請點擊左側 <b>「💾 儲存本機」</b> 將檔案下載到您的電腦，並在您本機的 Python 環境中執行。
                </div>
            `;
            pre.textContent = data.error; // 依然保留原始錯誤訊息在下方供參考
        } else {
            pre.textContent = data.output || data.error || "執行完成 (無終端輸出)";
        }
        
        terminal.appendChild(pre);
    } catch (e) {
        terminal.innerHTML = `<span style="color:#f85149;">❌ 執行失敗: ${e.message}</span>`;
    }
    runBtn.disabled = false;
};

// ==========================================
// ✥ 十字網格縮放器 (神經系統)
// ==========================================
const layout = document.getElementById('main-layout');
const crossHandler = document.getElementById('cross-handler');
let isResizing = false;

if (crossHandler && layout) {
    crossHandler.addEventListener('mousedown', (e) => {
        isResizing = true;
        document.body.classList.add('no-select');
        document.body.style.cursor = 'move';
        e.preventDefault();
    });

    document.addEventListener('mousemove', (e) => {
        if (!isResizing) return;
        const xPercent = (e.clientX / window.innerWidth) * 100;
        const yPercent = (e.clientY / window.innerHeight) * 100;
        const cX = Math.min(Math.max(xPercent, 15), 85);
        const cY = Math.min(Math.max(yPercent, 15), 85);
        layout.style.gridTemplateColumns = `${cX}% 5px 1fr`;
        layout.style.gridTemplateRows = `${cY}% 5px 1fr`;
    });

    document.addEventListener('mouseup', () => {
        if (isResizing) {
            isResizing = false;
            document.body.classList.remove('no-select');
            document.body.style.cursor = 'default';
            if (typeof editor !== 'undefined' && editor) editor.refresh();
        }
    });
}

// ==========================================
// 🚀 系統初始化
// ==========================================
updateTabsUI();
refreshFileList();
addLog("GETCODE V9.0 核心解析引擎已就緒。", "system");
