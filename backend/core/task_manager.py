import os
import json
from datetime import datetime

class TaskManager:
    def __init__(self):
        self.storage_file = "tasks_db.json"
        # 建立一個簡單的本地資料庫
        if not os.path.exists(self.storage_file):
            with open(self.storage_file, "w") as f:
                json.dump({}, f)

    def _read_db(self):
        with open(self.storage_file, "r") as f:
            return json.load(f)

    def _write_db(self, db):
        with open(self.storage_file, "w") as f:
            json.dump(db, f, indent=4)

    def get_task(self, task_id):
        db = self._read_db()
        return db.get(task_id, {"error": "not found"})

    def update(self, task_id, status_msg, code=None):
        db = self._read_db()
        if task_id not in db:
            db[task_id] = {"prompt": "", "logs": [], "status": "running"}
        
        db[task_id]["logs"].append({
            "time": datetime.now().isoformat(),
            "msg": status_msg
        })
        if code:
            db[task_id]["code"] = code
        
        self._write_db(db)
        print(f"📌 Task {task_id}: {status_msg}")

    def complete(self, task_id):
        db = self._read_db()
        if task_id in db:
            db[task_id]["status"] = "completed"
            self._write_db(db)

task_manager = TaskManager()
