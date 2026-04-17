import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

class LLMRouter:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        # 如果在 Docker 內沒抓到 .env，這裡會回傳 None
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None

    def call(self, role, prompt, model_name):
        if not self.client: return "❌ 錯誤: API KEY 未設定"
        
        instructions = {
            "plan": "你是一位資深架構師，請根據需求拆解 Python 開發步驟。",
            "code": "你是一位精通 Python 的工程師，請直接輸出程式碼，不含任何 Markdown 標記或說明文字。",
        }
        
        try:
            res = self.client.models.generate_content(
                model=model_name,
                contents=f"{instructions.get(role, '')}\n需求：{prompt}"
            )
            return res.text
        except Exception as e:
            return f"❌ AI 呼叫失敗: {str(e)}"

router = LLMRouter()
