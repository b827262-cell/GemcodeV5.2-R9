echo "🐳 Generating Docker configurations for Ultra Pro Max V5.2..."

# 1. 後端 Dockerfile
cat << 'DOCKER' > backend/Dockerfile
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
DOCKER

# 2. 前端 Dockerfile
cat << 'DOCKER' > frontend/Dockerfile
FROM nginx:alpine
# 將前端程式碼複製到 Nginx 預設網頁目錄
COPY frontend/ /usr/share/nginx/html/
EXPOSE 80
DOCKER

# 3. Docker Compose 整合配置
cat << 'YML' > docker-compose.yml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: backend/Dockerfile
    container_name: ultra-v5-backend
    ports:
      - "8000:8000"
    volumes:
      - ./workspace:/app/workspace
    restart: always

  frontend:
    build:
      context: .
      dockerfile: frontend/Dockerfile
    container_name: ultra-v5-frontend
    ports:
      - "3001:80"
    depends_on:
      - backend
    restart: always

networks:
  default:
    name: ultra-net
YML

echo "✅ Docker 配置文件生成完畢！"
