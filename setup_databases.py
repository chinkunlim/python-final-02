import requests
import json
import time
import os

def test_notion_connection(api_key):
    """測試 Notion API 連線。"""
    print("▶️  正在測試 Notion API 連線...")
    headers = {"Authorization": f"Bearer {api_key}","Notion-Version": "2022-06-28"}
    test_url = "https://api.notion.com/v1/users/me"
    try:
        response = requests.get(test_url, headers=headers)
        response.raise_for_status()
        bot_info = response.json()
        bot_name = bot_info.get("name", "未命名機器人")
        print(f"✅ Notion 連線測試成功！API 金鑰有效，成功連接到機器人: '{bot_name}'。")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Notion 連線測試失敗: {e}")
        return False

def clear_all_blocks_on_page(api_key, page_id):
    """刪除指定頁面下的所有內容區塊。"""
    print(f"▶️  正在準備清空頁面 (ID: {page_id})...")
    headers = {"Authorization": f"Bearer {api_key}", "Notion-Version": "2022-06-28"}
    get_children_url = f"https://api.notion.com/v1/blocks/{page_id}/children?page_size=100"
    try:
        response = requests.get(get_children_url, headers=headers)
        response.raise_for_status()
        blocks = response.json().get("results", [])
        if not blocks:
            print("   ℹ️  頁面本身是空的，無需清空。")
            return
        print(f"   偵測到 {len(blocks)} 個區塊，準備刪除...")
        for block in blocks:
            requests.delete(f"https://api.notion.com/v1/blocks/{block['id']}", headers=headers)
            time.sleep(0.4)
        print("✅ 頁面內容已成功清空。")
    except requests.exceptions.RequestException as e:
        print(f"❌ 清空頁面時發生錯誤: {e.response.text}")

def create_database(api_key, parent_page_id, db_title, db_icon, db_properties):
    """通用的資料庫建立函式。"""
    print(f"▶️  正在嘗試建立資料庫: '{db_title}'...")
    headers = {"Authorization": f"Bearer {api_key}","Content-Type": "application/json","Notion-Version": "2022-06-28"}
    payload = {"parent": {"type": "page_id", "page_id": parent_page_id},"icon": {"type": "emoji", "emoji": db_icon},"title": [{"type": "text", "text": {"content": db_title}}],"properties": db_properties}
    url = "https://api.notion.com/v1/databases"
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        new_db = response.json()
        print(f"✅ 成功建立資料庫: '{db_title}', ID: {new_db['id']}")
        return new_db
    except requests.exceptions.RequestException as e:
        print(f"❌ 建立資料庫 '{db_title}' 失敗: {e.response.text}")
        return None

def update_config_file(key, value, filename="config.txt"):
    """安全地更新或新增 config.txt 中的一個鍵值對。"""
    print(f"▶️  正在自動更新設定檔 {filename}...")
    key_found = False
    lines = []
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    with open(filename, 'w', encoding='utf-8') as f:
        for line in lines:
            if line.strip().startswith(key + '='):
                f.write(f"{key}={value}\n")
                key_found = True
            else:
                f.write(line)
        if not key_found:
            if lines and not lines[-1].endswith('\n'):
                f.write('\n')
            f.write(f"{key}={value}\n")
    print(f"✅ 設定檔更新完畢: 已自動設定 {key}。")

def update_parent_page_title(api_key, page_id, new_title):
    """更新指定頁面的標題。"""
    print(f"▶️  正在嘗試更新父頁面標題為: '{new_title}'...")
    url = f"https://api.notion.com/v1/pages/{page_id}"
    headers = {"Authorization": f"Bearer {api_key}","Content-Type": "application/json","Notion-Version": "2022-06-28"}
    payload = {"properties": {"title": { "title": [{"type": "text", "text": {"content": new_title}}] }}}
    try:
        response = requests.patch(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        print(f"✅ 父頁面標題已成功更新！")
    except requests.exceptions.RequestException as e:
        print(f"❌ 更新父頁面標題失敗: {e.response.text}")

def build_dashboard_layout(api_key, page_id, db_objects):
    """在指定頁面上建立儀表板的基礎佈局 (繁體中文版)。"""
    print("\n▶️  正在建立儀表板基礎佈局 (繁體中文)...")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json", "Notion-Version": "2022-06-28"}
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    layout_payload = {
        "children": [
            {"type": "heading_1", "heading_1": {"rich_text": [{"text": {"content": "大學四年學習總部"}}]}},
            {"type": "divider", "divider": {}},
            {"type": "column_list", "column_list": {"children": [
                {"type": "column", "column": {"children": [
                    {"type": "heading_2", "heading_2": {"rich_text": [{"text": {"content": "⚡️ 快速紀錄"}}]}},
                    {"type": "callout", "callout": {"icon": {"emoji": "💡"},"rich_text": [{"type": "text", "text": {"content": "手動在此處建立「新增任務」、「新增筆記」等按鈕，加速日常操作。"}, "annotations": {"italic": True, "color": "gray"}}]}},
                    {"type": "divider", "divider": {}},
                    {"type": "heading_2", "heading_2": {"rich_text": [{"text": {"content": "🧭 導覽"}}]}},
                    {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": db_objects["courses"]["title"][0]["text"]["content"], "link": {"url": db_objects["courses"]["url"]}}}]}},
                    {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": db_objects["tasks"]["title"][0]["text"]["content"], "link": {"url": db_objects["tasks"]["url"]}}}]}},
                    {"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": db_objects["notes"]["title"][0]["text"]["content"], "link": {"url": db_objects["notes"]["url"]}}}]}},
                ]}},
                {"type": "column", "column": {"children": [
                    {"type": "heading_2", "heading_2": {"rich_text": [{"text": {"content": "📚 本學期課程"}}]}},
                    {"type": "callout", "callout": {"icon": {"emoji": "ℹ️"},"rich_text": [{"type": "text", "text": {"content": "手動在此處用 /linked view 建立課程的「畫廊視圖」，並篩選本學期。"}, "annotations": {"italic": True, "color": "gray"}}]}},
                    {"type": "divider", "divider": {}},
                    {"type": "heading_2", "heading_2": {"rich_text": [{"text": {"content": "🗓️ 行事曆"}}]}},
                    {"type": "callout", "callout": {"icon": {"emoji": "ℹ️"},"rich_text": [{"type": "text", "text": {"content": "手動在此處用 /linked view 建立課程的「日曆視圖」，並篩選本學期。"}, "annotations": {"italic": True, "color": "gray"}}]}},
                ]}},
            ]}}
        ]
    }
    try:
        response = requests.patch(url, headers=headers, data=json.dumps(layout_payload, ensure_ascii=False).encode('utf-8'))
        response.raise_for_status()
        print("✅ 儀表板基礎佈局已成功建立！")
    except requests.exceptions.RequestException as e:
        print(f"❌ 建立儀表板佈局失敗: {e.response.text}")


def setup_all_databases(api_key, parent_page_id):
    """主功能：依序驗證、清空、建立所有核心資料庫，並自動更新設定檔。"""
    print("\n--- 開始執行資料庫初始化設定 ---")
    
    print("\n步驟 1/5: 測試 Notion API 連線...");
    if not test_notion_connection(api_key): return False
    
    print("\n步驟 2/5: 清理環境...")
    choice = input("   連線成功！是否要清空父頁面上的所有現有內容？(y/N): ").lower()
    if choice == 'y':
        confirm = input("   ⚠️  警告：這將永久刪除父頁面內所有區塊！確定要繼續嗎？(y/N): ").lower()
        if confirm == 'y': clear_all_blocks_on_page(api_key, parent_page_id)
        else: print("   ℹ️  已取消清空操作。")
    else: print("   ℹ️  已跳過清空頁面步驟。")

    print("\n步驟 3/5: 建立所有核心資料庫...")
    db_objects = {}
    
    # 課程資料庫的最終結構
    courses_props = {
        "課程名稱": {"title": {}}, "學期": {"select": {"options": [{"name": "114上"}]}},
        "週次": {"number": {"format": "number"}}, "課程日期與提醒": {"date": {}},
        "課程代碼": {"rich_text": {}}, "授課教師": {"rich_text": {}},
        "上課教室": {"rich_text": {}}, "學分": {"rich_text": {}}, 
        "必選修": {"select": {"options": [{"name": "學程"}, {"name": "選"}]}},
        "星期": {"rich_text": {}}, "開始時間": {"rich_text": {}}, "結束時間": {"rich_text": {}}
    }
    courses_db = create_database(api_key, parent_page_id, "📚 課程總資料庫", "📚", courses_props)
    if not courses_db: return False
    db_objects["courses"] = courses_db; update_config_file("COURSE_DATABASE_ID", courses_db['id'].replace('-', '')); time.sleep(1)

    # 任務資料庫的最終結構
    tasks_props = {"任務名稱": {"title": {}},"關聯到課程": {"relation": {"database_id": courses_db['id'], "single_property": {}}},"截止日期": {"date": {}}, "類型": {"select": {"options": [{"name": "作業"}, {"name": "考試"}]}},"狀態": {"status": {}}, "學期": {"select": {"options": [{"name": "114上"}]}}}
    tasks_db = create_database(api_key, parent_page_id, "✅ 任務總資料庫", "✅", tasks_props)
    if not tasks_db: return False
    db_objects["tasks"] = tasks_db; update_config_file("TASK_DATABASE_ID", tasks_db['id'].replace('-', '')); time.sleep(1)
    
    # 筆記資料庫的最終結構
    notes_props = {
        "筆記標題": {"title": {}},
        "關聯到課程": {"relation": {"database_id": courses_db['id'], "single_property": {}}},
        "上課日期": {"date": {}},
        "學期": {"select": {"options": [{"name": "114上"}]}},
        "週次": {"number": {"format": "number"}},
        "分類": {"select": {"options": [{"name": "課堂筆記"}, {"name": "補充資料"}]}},
        "建立時間": {"created_time": {}},
        "最後修改時間": {"last_edited_time": {}}
    }
    notes_db = create_database(api_key, parent_page_id, "📝 學習筆記總資料庫", "📝", notes_props)
    if not notes_db: return False
    db_objects["notes"] = notes_db; update_config_file("NOTE_DATABASE_ID", notes_db['id'].replace('-', ''))

    print("\n步驟 4/5: 建立儀表板佈局...")
    build_dashboard_layout(api_key, parent_page_id, db_objects)

    print("\n步驟 5/5: 更新父頁面標題...")
    update_parent_page_title(api_key, parent_page_id, "大學四年學習總部")
    
    print("\n" + "="*50)
    print("🎉 所有初始化設定任務已成功執行完畢！")
    print("   ✅ 所有資料庫 ID (無橫線格式) 已自動寫入 config.txt。")
    print("   現在，請手動進行儀表板的最後微調（拖曳欄寬、建立按鈕與連結視圖）。")
    print("="*50)
    return True