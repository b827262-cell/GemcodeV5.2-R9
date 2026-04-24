def draw_pyramid(height, char="*"):
    """
    在終端機繪製一個指定高度的金字塔。
    
    :param height: 金字塔的高度（行數）
    :param char: 構成金字塔的字元
    """
    print(f"--- 繪製高度為 {height} 的金字塔 ---")
    
    for i in range(1, height + 1):
        # 計算前置空格：總高度 - 當前行數
        spaces = " " * (height - i)
        # 計算符號數量：(2 * 當前行數) - 1
        stars = char * (2 * i - 1)
        # 組合並列印
        print(f"{spaces}{stars}")

# 固定參數設定
DEFAULT_HEIGHT = 7
DEFAULT_CHAR = "#"

if __name__ == "__main__":
    # 執行繪製
    draw_pyramid(DEFAULT_HEIGHT, DEFAULT_CHAR)