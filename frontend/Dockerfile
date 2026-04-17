FROM nginx:alpine
RUN rm -rf /usr/share/nginx/html/*
COPY frontend/ /usr/share/nginx/html/
# 確保 nginx 使用者有權限讀取這些檔案
RUN chmod -R 755 /usr/share/nginx/html
EXPOSE 80
