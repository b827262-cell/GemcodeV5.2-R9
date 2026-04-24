import os
import json
import numpy as np
from google import genai
from dotenv import load_dotenv

load_dotenv()

class RAGManager:
    def __init__(self, client=None, storage_path="vector_store.json"):
        # 優先使用傳入的 client，否則自行初始化
        self.client = client
        if not self.client:
            self.api_key = os.getenv("GEMINI_API_KEY")
            self.client = genai.Client(api_key=self.api_key) if self.api_key else None
            
        self.storage_path = storage_path
        # 🌟 更新為正確的模型名稱
        self.embedding_model = "models/gemini-embedding-2"
        self.index = []  # [{"text": str, "vector": list, "metadata": dict}]
        self.load_index()

    def load_index(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    self.index = json.load(f)
            except Exception:
                self.index = []

    def save_index(self):
        try:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(self.index, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _get_embedding(self, text):
        if not text or not text.strip() or not self.client:
            return None
        try:
            res = self.client.models.embed_content(
                model=self.embedding_model,
                contents=text.strip()
            )
            return res.embeddings[0].values
        except Exception as e:
            print(f"Embedding API 錯誤: {e}")
            return None

    def update_index(self, workspace_dir="workspace"):
        if not self.client: return
        
        new_index = []
        if not os.path.exists(workspace_dir):
            os.makedirs(workspace_dir)

        for root, _, files in os.walk(workspace_dir):
            for file in files:
                if file.endswith(('.py', '.js', '.html', '.css', '.md', '.json')):
                    path = os.path.join(root, file)
                    try:
                        with open(path, "r", encoding="utf-8") as f:
                            content = f.read()
                        if not content.strip(): continue

                        chunks = self._chunk_text(content)
                        for i, chunk in enumerate(chunks):
                            vector = self._get_embedding(chunk)
                            if vector:
                                new_index.append({
                                    "text": chunk,
                                    "vector": vector,
                                    "metadata": {"file": file, "path": path, "chunk": i}
                                })
                    except Exception:
                        pass
        self.index = new_index
        self.save_index()

    def _chunk_text(self, text, size=500, overlap=100):
        chunks = []
        for i in range(0, len(text), size - overlap):
            chunk = text[i:i + size].strip()
            if len(chunk) > 10:
                chunks.append(chunk)
        return chunks

    def query(self, prompt, top_k=3):
        if not self.index or not self.client: return ""
        
        query_vector = self._get_embedding(prompt)
        if not query_vector: return ""

        scored_chunks = []
        v1 = np.array(query_vector)
        for item in self.index:
            v2 = np.array(item["vector"])
            score = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
            scored_chunks.append((score, item))

        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        results = scored_chunks[:top_k]

        context = "\n--- 相關代碼上下文 ---\n"
        for score, item in results:
            context += f"檔案: {item['metadata']['path']} (相似度: {score:.2f})\n"
            context += f"內容: {item['text']}\n\n"
        return context
