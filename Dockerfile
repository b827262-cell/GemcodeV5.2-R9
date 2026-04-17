FROM python:3.12-slim

WORKDIR /app

# 複製依賴清單並安裝
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製程式碼與環境變數檔
COPY test_genai.py .
COPY .env .

# 預設執行測試腳本
CMD ["python", "test_genai.py"]
