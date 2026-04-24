FROM python:3.12-slim

# 安裝 Xvfb, Tkinter, Ghostscript 以及 Graphviz 系統組件
RUN apt-get update && apt-get install -y \
    xvfb \
    python3-tk \
    ghostscript \
    graphviz \
    libgraphviz-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
