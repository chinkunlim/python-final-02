import requests
import json
import time

def create_weekly_notes_for_semester(api_key, course_db_id, notes_db_id, semester_name):
    """
    為指定學期的所有課程，批次建立每週的筆記頁面。
    此版本已修復100筆資料限制，並會填入新欄位。
    """
    print(f"\n▶️  create_notes: 開始為「{semester_name}」學期建立筆記...")
    
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json", "Notion-Version": "2022-06-28"}
    
    # 處理分頁 (Pagination)，確保抓取所有課程
    all_course_pages = []
    start_cursor = None
    while True:
        print(f"   正在查詢課程資料庫 (已取得 {len(all_course_pages)} 筆)...")
        query_url = f"https://api.notion.com/v1/databases/{course_db_id}/query"
        payload = {"filter": {"property": "學期", "select": {"equals": semester_name}}}
        if start_cursor:
            payload["start_cursor"] = start_cursor
            
        try:
            response = requests.post(query_url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()
            data = response.json()
            
            all_course_pages.extend(data.get("results", []))
            
            if data.get("has_more"):
                start_cursor = data.get("next_cursor")
            else:
                break # 如果沒有下一頁了，就跳出迴圈
        except requests.exceptions.RequestException as e:
            print(f"❌ 查詢課程時發生錯誤: {e.response.text}")
            return False
    
    if not all_course_pages:
        print(f"   ℹ️  在「課程總資料庫」中找不到任何標記為「{semester_name}」的課程。")
        return True

    print(f"   查詢完畢，共找到 {len(all_course_pages)} 堂課，準備逐一建立筆記...")

    total_notes_created = 0
    for course_page in all_course_pages:
        course_page_id = course_page["id"]
        
        try:
            course_name = course_page["properties"]["課程名稱"]["title"][0]["text"]["content"]
            week_num = course_page["properties"]["週次"]["number"]
            course_date_obj = course_page["properties"]["課程日期與提醒"]["date"]
            
            note_title = f"{course_name} - 課堂筆記"
            
            new_note_payload = {
                "parent": {"database_id": notes_db_id},
                "properties": {
                    "筆記標題": {"title": [{"text": {"content": note_title}}]},
                    "關聯到課程": {"relation": [{"id": course_page_id}]},
                    "學期": {"select": {"name": semester_name}},
                    "週次": {"number": week_num},
                    "上課日期": {"date": {"start": course_date_obj["start"] if course_date_obj else None}},
                    "分類": {"select": {"name": "課堂筆記"}}
                }
            }

            create_url = "https://api.notion.com/v1/pages"
            create_response = requests.post(create_url, headers=headers, data=json.dumps(new_note_payload, ensure_ascii=False).encode('utf-8'))
            
            if create_response.status_code == 200:
                print(f"     ✅ 已建立筆記: {note_title} (第{week_num}週)")
                total_notes_created += 1
            else:
                print(f"     ❌ 建立筆記 '{note_title}' (第{week_num}週) 失敗: {create_response.text}")
            
            time.sleep(0.4)

        except (KeyError, IndexError) as e:
            print(f"     ⚠️  處理課程頁面 {course_page_id} 時缺少必要屬性 ({e})，已跳過。")
            continue

    print(f"\n✅ create_notes: 任務完成，共成功建立了 {total_notes_created} 則筆記。")
    return True