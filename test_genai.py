import os
from google import genai
from dotenv import load_dotenv

# 載入 .env 檔案
load_dotenv()

def validate_environment():
    # 新版 SDK 預設吃 GEMINI_API_KEY，我們直接檢查它是否存在
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ 錯誤: 未偵測到 GEMINI_API_KEY 環境變數。")
        return False, None
    
    try:
        # 初始化 2026 最新 Client
        client = genai.Client(api_key=api_key)
        print("✅ API 連線成功！正在驗證可用模型...")
        
        # 取得模型清單 (新版語法)
        models = client.models.list()
        for m in models:
            # 這裡簡單列出幾個代表性的模型，避免畫面洗版
            if "gemini" in m.name or "gemma" in m.name:
                print(f"- {m.name}")
        return True, client
    except Exception as e:
        print(f"❌ 驗證失敗: {e}")
        return False, None

def get_gemini_response(client, prompt):
    try:
        # 使用你指定的模型，或預設使用 2.5-flash
        model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        print(f"🧠 使用模型: {model_name}")
        
        # 新版生成語法
        response = client.models.generate_content(
            model=model_name,
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"❌ 調用失敗: {str(e)}"

if __name__ == "__main__":
    is_valid, client = validate_environment()
    if is_valid:
        print("\n🚀 開始執行需求任務...")
        result = get_gemini_response(client, "請計算 1 + 100 等於多少？")
        print(f"\n🤖 AI 回覆:\n{result.strip()}")
    else:
        print("\n⚠️ 環境設定無效，請檢查 .env 檔案中的 GEMINI_API_KEY。")
