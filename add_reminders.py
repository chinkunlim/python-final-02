import requests
import json
import time
from datetime import datetime, timedelta

def add_reminders_for_upcoming_courses(api_key, database_id):
    """查詢未來一個月內、尚未設定提醒的課程，並批次為它們加上提醒。"""
    print("\n▶️  add_reminders: 開始執行提醒新增任務...")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }
    
    query_url = f"https://api.notion.com/v1/databases/{database_id}/query"

    one_month_later = (datetime.now() + timedelta(days=30)).isoformat()

    query_payload = {
        "filter": {
            "and": [
                {"property": "課程日期與提醒", "date": {"on_or_after": datetime.now().isoformat()}},
                {"property": "課程日期與提醒", "date": {"on_or_before": one_month_later}},
                {"property": "課程日期與提醒", "date": {"is_not_empty": True}}
            ]
        }
    }
    
    try:
        print("   正在查詢未來一個月內的課程...")
        response = requests.post(query_url, headers=headers, data=json.dumps(query_payload))
        response.raise_for_status()
        pages_to_update = response.json().get("results", [])

        if not pages_to_update:
            print("   ✅ 檢查完畢，未來一個月內沒有需要新增提醒的課程。")
            return

        print(f"   偵測到 {len(pages_to_update)} 堂課需要更新提醒，開始處理...")

        for page in pages_to_update:
            page_id = page["id"]
            page_title = page["properties"]["課程名稱"]["title"][0]["text"]["content"]
            original_date = page["properties"]["課程日期與提醒"]["date"]
            
            # 如果已經有提醒，就跳過，避免重複設定
            if original_date and original_date.get("reminder"):
                print(f"     ℹ️  '{page_title}' 已有提醒，跳過。")
                continue

            original_date["reminder"] = {"unit": "minute", "value": 20}
            
            update_payload = {"properties": {"課程日期與提醒": {"date": original_date}}}
            
            update_url = f"https://api.notion.com/v1/pages/{page_id}"
            update_response = requests.patch(update_url, headers=headers, data=json.dumps(update_payload))
            
            if update_response.status_code == 200:
                print(f"     ✅ 已為 '{page_title}' 加上提醒。")
            else:
                print(f"     ❌ 更新 '{page_title}' 失敗: {update_response.text}")
            
            time.sleep(0.4)

        print("\n✅ 所有近期課程的提醒已設定完畢！")

    except requests.exceptions.RequestException as e:
        print(f"❌ 執行提醒新增任務時發生錯誤: {e.response.text}")