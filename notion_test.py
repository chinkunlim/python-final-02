import requests
import json

def update_page_title():
    """
    從 config.txt 讀取設定，連接 Notion API 並更新指定頁面的標題。
    這個版本更強健，會忽略空白行和不符合 key=value 格式的行。
    """
    # --- 讀取設定檔 (優化版) ---
    config = {}
    try:
        with open('config.txt', 'r', encoding='utf-8') as f: # 建議加上 encoding='utf-8'
            for line in f:
                # 忽略空白行和不包含 '=' 的行 (例如註解)
                if '=' in line:
                    # 用 .split('=', 1) 只在第一個等號處分割
                    key, value = line.strip().split('=', 1)
                    # 存入字典，並去除鍵和值前後可能的多餘空白
                    config[key.strip()] = value.strip()

    except FileNotFoundError:
        print("❌ 錯誤：找不到 config.txt 檔案。")
        return

    # --- 從字典中安全地獲取需要的資料 ---
    notion_key = config.get("NOTION_KEY")
    page_id = config.get("PAGE_ID")

    if not notion_key or not page_id:
        print("❌ 錯誤：config.txt 中找不到必要的 NOTION_KEY 或 PAGE_ID。")
        return

    # --- API 請求部分 (維持不變) ---
    url = f"https://api.notion.com/v1/pages/{page_id}"
    headers = {
        "Authorization": f"Bearer {notion_key}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }
    
    new_title = "114-1 課程筆記"
    payload = {
        "properties": {
            "title": {
                "title": [
                    {
                        "text": {
                            "content": new_title
                        }
                    }
                ]
            }
        }
    }

    print("▶️  正在嘗試連接 Notion API 並更新頁面標題...")
    try:
        response = requests.patch(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        print(f"✅ 成功！頁面標題已更新為 '{new_title}'。")
        
    except requests.exceptions.HTTPError as err:
        print(f"❌ HTTP 錯誤：{err}")
        error_details = err.response.json()
        print(f"   Notion 回應: {error_details.get('message', '沒有提供額外訊息')}")
    except requests.exceptions.RequestException as err:
        print(f"❌ 網路連線錯誤：{err}")


# 這段程式碼允許你單獨執行 notion_test.py 進行測試
if __name__ == '__main__':
    update_page_title()