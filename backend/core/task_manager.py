import uuid
from google.cloud import firestore
import os

class TaskManager:
    def __init__(self):
        # 建立 Firestore Client
        # 在 Cloud Run 環境中，它會自動抓取專案權限
        self.db = firestore.Client()
        self.collection = self.db.collection("gemcode_tasks")

    def create(self, prompt, model):
        task_id = str(uuid.uuid4())
        task_data = {
            "id": task_id,
            "prompt": prompt,
            "model": model,
            "status": "processing",
            "logs": ["✨ 任務已在雲端資料庫初始化..."],
            "code": ""
        }
        # 寫入 Firestore
        self.collection.document(task_id).set(task_data)
        return task_id

    def update(self, task_id, log_msg, code=None):
        doc_ref = self.collection.document(task_id)
        # 使用 ArrayUnion 確保 Logs 是累加的，不會覆蓋
        updates = {
            "logs": firestore.ArrayUnion([log_msg])
        }
        if code:
            updates["code"] = code
        
        doc_ref.update(updates)

    def complete(self, task_id):
        self.collection.document(task_id).update({"status": "done"})

    def get_task(self, task_id):
        # 從 Firestore 讀取
        doc = self.collection.document(task_id).get()
        if doc.exists:
            return doc.to_dict()
        return {"error": "任務不存在"}

task_manager = TaskManager()
