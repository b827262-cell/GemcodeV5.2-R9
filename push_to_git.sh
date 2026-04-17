#!/bin/bash
# Ultra IDE V5.2 - 一鍵推送到 GitHub 腳本

echo "🚀 準備將 V5.2 推送至 Git..."

# 1. 確保有 .gitignore，避免把虛擬環境和機密資料推上雲端
cat << 'IGNORE' > .gitignore
.venv/
__pycache__/
.env
workspace/
.DS_Store
IGNORE

# 2. 初始化 Git (如果尚未初始化)
if [ ! -d ".git" ]; then
    git init
    echo "✅ Git 初始化完成"
fi

# 3. 加入所有檔案並提交
git add .
read -p "請輸入 Commit 訊息 [預設: Update V5.2]: " commit_msg
commit_msg=${commit_msg:-Update V5.2}
git commit -m "$commit_msg"

echo "------------------------------------------------"
echo "請確保你已經在 GitHub 建立了一個空的 Repository。"
echo "如果你還沒設定遠端網址，請輸入 (例如: https://github.com/你的帳號/你的專案.git)"
echo "如果已經設定過，請直接按 Enter 跳過。"
read remote_url

if [ ! -z "$remote_url" ]; then
    git remote add origin $remote_url
    git branch -M main
fi

# 4. 推送上雲端
git push -u origin main

echo "✅ 成功推送至 GitHub！"
