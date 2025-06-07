import requests, json, time

def upload_courses_to_notion(api_key, database_id, courses_data, semester_name):
    """將處理好的課程資料列表，上傳到指定的 Notion 資料庫。"""
    print(f"\n▶️  notion_uploader: 準備將「{semester_name}」學期的課程上傳到 Notion...")
    
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json", "Notion-Version": "2022-06-28"}
    
    total_created_count = 0
    for course in courses_data:
        # [核心修改] 直接使用純課程名稱
        course_name = course.get("課程名稱", "無標題課程")
        print(f"   正在處理課程: {course_name}")

        for i, date_info in enumerate(course.get("重複日期列表", [])):
            week_num = i + 1
            # 標題不再加上週次資訊
            page_title = course_name 
            
            date_payload = {"start": date_info["start"], "end": date_info["end"], "time_zone": "Asia/Taipei"}

            new_page_payload = {
                "parent": {"database_id": database_id},
                "properties": {
                    "課程名稱": {"title": [{"text": {"content": page_title}}]},
                    "課程日期與提醒": {"date": date_payload},
                    "學期": {"select": {"name": semester_name}},
                    "週次": {"number": week_num},
                    "課程代碼": {"rich_text": [{"text": {"content": course.get("課程代碼", "")}}]},
                    "授課教師": {"rich_text": [{"text": {"content": course.get("授課教師", "")}}]},
                    "上課教室": {"rich_text": [{"text": {"content": course.get("上課教室", "")}}]},
                    "學分": {"rich_text": [{"text": {"content": course.get("學分", "")}}]},
                    "必選修": {"select": {"name": course.get("必選修", "選")}},
                    "星期": {"rich_text": [{"text": {"content": course.get("星期", "")}}]},
                    "開始時間": {"rich_text": [{"text": {"content": course.get("開始時間", "")}}]},
                    "結束時間": {"rich_text": [{"text": {"content": course.get("結束時間", "")}}]},
                }
            }
            
            create_url = "https://api.notion.com/v1/pages"
            try:
                response = requests.post(create_url, headers=headers, data=json.dumps(new_page_payload, ensure_ascii=False).encode('utf-8'))
                if response.status_code == 200:
                    total_created_count += 1
                else:
                    # 在錯誤訊息中也使用純標題
                    print(f"   ❌ 新增 '{page_title}' (第{week_num}週) 失敗, 原因: {response.text}")
                time.sleep(0.4) 
            except requests.exceptions.RequestException as e:
                print(f"   ❌ 發生網路錯誤: {e}")

    print(f"\n✅ notion_uploader: 上傳完畢，共成功建立了 {total_created_count} 堂課。")