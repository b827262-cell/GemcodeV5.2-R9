import uuid

class TaskManager:
    def __init__(self):
        self.tasks = {}

    def create(self, prompt, model):
        task_id = str(uuid.uuid4())
        self.tasks[task_id] = {
            "id": task_id,
            "prompt": prompt,
            "model": model,
            "status": "processing",
            "logs": [],
            "code": ""
        }
        return task_id

    def update(self, task_id, log_msg, code=None):
        if task_id in self.tasks:
            self.tasks[task_id]["logs"].append(log_msg)
            if code: self.tasks[task_id]["code"] = code

    def complete(self, task_id):
        if task_id in self.tasks:
            self.tasks[task_id]["status"] = "done"

task_manager = TaskManager()
