# ==========================================
# 檔案名稱: utils.py
# 說明: GETCODE IDE 專用數據處理與輔助工具箱
# ==========================================

import csv
import random
import os

def generate_mock_sales_data(filename="sales.csv", num_rows=30):
    """
    生成一份模擬的銷售數據 CSV 檔案。
    包含：日期、產品類別、銷售額、利潤。
    """
    categories = ["Electronics", "Clothing", "Home & Garden", "Books", "Toys"]
    
    header = ["Day", "Category", "Revenue", "Profit"]
    data = []
    
    for day in range(1, num_rows + 1):
        cat = random.choice(categories)
        revenue = round(random.uniform(1000, 5000), 2)
        profit = round(revenue * random.uniform(0.1, 0.4), 2)
        data.append([day, cat, revenue, profit])
        
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(data)
        
    print(f"✅ [Utils] 成功生成 {num_rows} 筆模擬銷售數據至 '{filename}'")
    return filename

def clean_and_read_csv(filename):
    """
    讀取 CSV 檔案並回傳字典格式的資料。
    """
    if not os.path.exists(filename):
        print(f"❌ [Utils] 找不到檔案 '{filename}'")
        return None
        
    results = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                results.append(row)
        print(f"✅ [Utils] 成功讀取 '{filename}'，共 {len(results)} 筆資料。")
        return results
    except Exception as e:
        print(f"❌ [Utils] 讀取失敗: {e}")
        return None
