#!/bin/bash
# Ultra Pro Max V5.2 - Frontend Starter (Port 3001)

# 1. 檢查前端目錄
if [ -d "frontend" ]; then
    echo "✅ 找到 frontend 目錄"
else
    echo "❌ 找不到 frontend 目錄，請確認 install_v52_full.sh 是否已執行"
    exit 1
fi

# 2. 啟動輕量級伺服器
echo "🚀 正在啟動前端介面於埠位 3001..."
echo "🔗 點擊開啟 URL: http://localhost:3001"

# 進入前端目錄並啟動伺服器
# 使用 3001 避開 Open WebUI 的 3000
cd frontend && python3 -m http.server 3001
