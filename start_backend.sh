#!/bin/bash
# Ultra Pro Max V5.2 - Backend Starter

# 1. 檢查並啟用虛擬環境
if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo "✅ 虛擬環境 (.venv) 已成功啟用"
else
    echo "❌ 找不到 .venv 資料夾，請先執行: python3 -m venv .venv"
    exit 1
fi

# 2. 設定 Python 模組搜尋路徑
# 讓系統知道 backend 資料夾內包含 api, tools 等模組
export PYTHONPATH="$PWD/backend"

# 3. 啟動 Uvicorn 伺服器
echo "🚀 正在啟動後端伺服器於 http://127.0.0.1:8000"
echo "📂 當前專案路徑: $PWD"

uvicorn backend.main:app --reload --port 8000
