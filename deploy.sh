#!/bin/bash

echo "========================================"
echo "🚀 Ultra IDE V5.2 智慧部署工具"
echo "========================================"

# 檢查是否有正在運行的相關容器
RUNNING=$(docker ps -q -f name=ultra-v5)

if [ ! -z "$RUNNING" ]; then
    echo "💡 系統狀態：容器目前正在運行中。"
else
    echo "💡 系統狀態：容器目前已停止。"
fi

echo "----------------------------------------"
echo "是否要強制『重新安裝與建構』Docker 映像檔？"
echo "👉 選擇 [Y]: 適用於你修改了 requirements.txt 或 Dockerfile 時 (較慢)"
echo "👉 選擇 [N]: 直接啟動現有容器，適用於只修改 Python/JS 程式碼時 (極快)"
echo "----------------------------------------"

read -p "請輸入您的選擇 (Y/N) [預設 N]: " choice
choice=${choice:-N}

if [[ "$choice" == [Yy]* ]]; then
    echo "⏳ 開始強制重新建構..."
    docker-compose up -d --build
else
    echo "⚡ 略過建構，快速啟動容器..."
    docker-compose up -d
fi

echo "========================================"
echo "✅ 部署指令執行完畢！"
echo "請執行 docker ps 檢查容器狀態。"
echo "========================================"
