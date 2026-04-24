/**
 * editor.js
 * 負責編輯器核心、分頁管理與檔案系統存取
 */
export function createEditorModule({ addLog }) {
    // 1. 產生全域 Session ID
    const sessionId = crypto.randomUUID();

    // 2. 內部狀態
    const state = {
        fileContents: {
            "main.py": "# 這是主程式入口 (main.py)\n",
            "utils.py": "# 放置工具函數 (utils.py)\n",
            "date_gen.py": "# 放置數據生成邏輯 (date_gen.py)\n",
            "analyzer.py": "# 放置數據分析邏輯 (analyzer.py)\n"
        },
        currentTab: "main.py"
    };

    // 3. 初始化 CodeMirror 編輯器
    const editor = CodeMirror.fromTextArea(
        document.getElementById('editor-content'),
        {
            mode: "python",
            theme: "material-darker",
            lineNumbers: true,
            lineWrapping: true,
            indentUnit: 4,
            smartIndent: true,
            matchBrackets: true,
            autoCloseBrackets: true,
            extraKeys: { "Ctrl-Space": "autocomplete" }
        }
    );

    // 設定初始內容
    editor.setValue(state.fileContents[state.currentTab]);

    // 4. 分頁 UI 更新邏輯
    const updateTabsUI = () => {
        const tabBar = document.getElementById('tab-bar');
        if (!tabBar) return;

        tabBar.innerHTML = '';

        Object.keys(state.fileContents).forEach(fname => {
            const div = document.createElement('div');
            div.className = `tab ${fname === state.currentTab ? 'active' : ''}`;
            div.dataset.filename = fname;
            div.innerText = fname;
            tabBar.appendChild(div);
        });
    };

    // 5. 分頁切換事件處理
    const onTabClick = (e) => {
        if (!e.target.classList.contains('tab')) return;

        // 切換前存檔當前內容
        state.fileContents[state.currentTab] = editor.getValue();
        
        // 更新狀態
        state.currentTab = e.target.dataset.filename;

        // UI 與編輯器內容同步
        updateTabsUI();
        editor.setValue(state.fileContents[state.currentTab] || "");
        
        // 確保 CodeMirror 正確刷新顯示
        setTimeout(() => editor.refresh(), 1);
    };

    // 6. 本機檔案系統存取 (Open/Save)
    const setupFileIO = () => {
        // 開啟本機檔案
        document.getElementById('btn-open')?.addEventListener('click', async () => {
            try {
                const [handle] = await window.showOpenFilePicker();
                const file = await handle.getFile();
                const text = await file.text();

                editor.setValue(text);
                state.fileContents[state.currentTab] = text;

                addLog(`📂 已從本機載入: ${file.name}`, "#58a6ff");
            } catch (err) {
                if (err.name !== 'AbortError') console.error(err);
            }
        });

        // 儲存至本機檔案
        document.getElementById('btn-save')?.addEventListener('click', async () => {
            try {
                const handle = await window.showSaveFilePicker({ 
                    suggestedName: state.currentTab,
                    types: [{
                        description: 'Python Files',
                        accept: { 'text/x-python': ['.py'] },
                    }]
                });
                const writable = await handle.createWritable();

                await writable.write(editor.getValue());
                await writable.close();

                addLog(`💾 檔案已儲存至本機`, "#3fb950");
            } catch (err) {
                if (err.name !== 'AbortError') console.error(err);
            }
        });
    };

    // 執行模組初始化
    updateTabsUI();
    document.getElementById('tab-bar')?.addEventListener('click', onTabClick);
    setupFileIO();

    // 🔥 對外 API：僅暴露必要方法，保護內部 state
    return {
        getSessionId: () => sessionId,
        getFiles: () => ({ ...state.fileContents }),
        setFiles: (newFiles) => {
            state.fileContents = { ...newFiles };
            // 如果當前分頁被移除，預設跳轉到第一個
            if (!state.fileContents[state.currentTab]) {
                state.currentTab = Object.keys(state.fileContents)[0];
            }
            updateTabsUI();
            editor.setValue(state.fileContents[state.currentTab] || "");
            editor.refresh();
        },
        getEditor: () => editor,
        getCurrentTab: () => state.currentTab,
        
        // 清理資源用
        destroy: () => {
            document.getElementById('tab-bar')?.removeEventListener('click', onTabClick);
        }
    };
}
