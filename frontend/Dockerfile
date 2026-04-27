# 🌟 使用最新穩定版 Node.js 輕量映像檔
FROM node:20-alpine

WORKDIR /app

# 📦 預先安裝依賴，利用 Docker Layer Cache 縮短建構時間
COPY package*.json ./
RUN npm install

# 📂 複製所有前端原始碼 (包含 index.html, style.css, main.js)
COPY . .

# 🚪 開放主要埠號 (IDE 介面) 與 輔助埠號 (HMR)
EXPOSE 3001
EXPOSE 3005

# 🚀 啟動開發伺服器，並強制開啟主機監聽以利 Docker 存取
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
