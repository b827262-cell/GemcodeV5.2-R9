FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/

# 🌟 關鍵修復：切換到 backend 目錄內，讓 Python 能順利找到 api, core 等資料夾
WORKDIR /app/backend

# 啟動指令改為直接呼叫 main:app
CMD exec uvicorn main:app --host 0.0.0.0 --port $PORT
