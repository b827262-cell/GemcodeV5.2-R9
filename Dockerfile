# ==========================================
# 階段 1: 前端構建 (Vite Build)
# ==========================================
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend
# 複製前端設定並安裝依賴
COPY frontend/package*.json ./
RUN npm install
# 複製源碼並打包
COPY frontend/ ./
RUN npm run build

# ==========================================
# 階段 2: 後端運行 (FastAPI + Cloud Run)
# ==========================================
FROM python:3.10-slim
WORKDIR /app

# 安裝系統層級的依賴 (供沙盒執行程式碼使用)
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

# 複製後端依賴並安裝
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 複製後端 Python 源碼
COPY backend/ ./backend/

# 🌟 關鍵：將前端打包好的 dist 資料夾，複製到後端容器中
COPY --from=frontend-builder /app/frontend/dist ./frontend_dist

# Cloud Run 會動態分配 PORT 環境變數，預設通常是 8080
ENV PORT=8080

# 啟動 FastAPI 伺服器
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT}"]
