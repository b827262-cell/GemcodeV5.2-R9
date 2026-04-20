FROM nginx:alpine

# 將當前目錄(frontend)的所有檔案複製到 Nginx 的對外展示區
COPY . /usr/share/nginx/html

# 開放 80 Port 讓 Cloud Run 連接
EXPOSE 80

# 啟動 Nginx
CMD ["nginx", "-g", "daemon off;"]
