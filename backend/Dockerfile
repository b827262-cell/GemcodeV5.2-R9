FROM python:3.12-slim

WORKDIR /app

# 安裝系統依賴 (git 是 gitpython 必備的)
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# 複製依賴清單並安裝
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製後端程式碼與 .env
COPY backend/ ./backend/
COPY .env .

# 重要：設定 Python 路徑，解決 api/tools 模組找不到的問題
ENV PYTHONPATH=/app/backend

# 啟動指令
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
