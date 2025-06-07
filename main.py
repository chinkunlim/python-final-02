import time
from datetime import datetime
from web_scraper import read_config
from setup_databases import setup_all_databases

def run_semester_task(config):
    """執行每學期一次的抓取與上傳任務，並回報結果。"""
    from web_scraper import login_and_get_page_source
    from process_courses import process_source_and_create_files
    from notion_uploader import upload_courses_to_notion

    print("\n--- 您選擇了【學期性功能】 ---")
    
    print("▶️  請依序輸入新學期的資訊...")
    semester_name = input("   - 學期名稱 (例如: 115上): ").strip()
    if not semester_name:
        print("❌ 未輸入學期名稱，任務中止。")
        return False

    start_date_str = input(f"   - 「{semester_name}」的開始日期 (格式YYYY-MM-DD): ").strip()
    end_date_str = input(f"   - 「{semester_name}」的結束日期 (格式YYYY-MM-DD): ").strip()

    try:
        datetime.strptime(start_date_str, "%Y-%m-%d")
        datetime.strptime(end_date_str, "%Y-%m-%d")
    except ValueError:
        print("❌ 日期格式錯誤，應為YYYY-MM-DD。任務中止。")
        return False
    
    print(f"ℹ️  好的，將為「{semester_name}」學期 ({start_date_str} 至 {end_date_str}) 進行排程...")
    
    login_url, username, password = config.get("LOGIN_URL"), config.get("USERNAME"), config.get("PASSWORD")
    api_key, database_id = config.get("NOTION_KEY"), config.get("COURSE_DATABASE_ID")
    if not all([login_url, username, password, api_key, database_id]):
        print("❌ config.txt 中缺少執行此任務所需的固定資訊。")
        return False

    page_source = None
    max_attempts = 3
    for attempt in range(max_attempts):
        print("\n" + "="*50)
        print(f"▶️  第 {attempt + 1}/{max_attempts} 次嘗試抓取課程網頁...")
        source = login_and_get_page_source(login_url, username, password)
        if source:
            print("✅ 網頁抓取成功！")
            page_source = source
            break
        else:
            print(f"⚠️ 第 {attempt + 1} 次抓取失敗。")
            if attempt < max_attempts - 1:
                print("   將在 5 秒後重試...")
                time.sleep(5)

    if not page_source:
        print("\n☠️ 抓取課程網頁失敗，已達重試上限。任務終止。")
        return False

    final_courses_data = process_source_and_create_files(page_source, start_date_str, end_date_str)
    
    if not final_courses_data:
        print("☠️ 資料處理後無有效課程，任務終止。")
        return False

    # === 核心修改：修正函式呼叫，傳入所有必要的參數 ===
    upload_courses_to_notion(api_key, database_id, final_courses_data, semester_name)
    return True

def run_initial_setup(config):
    """執行一次性的資料庫安裝任務，並回報結果"""
    print("\n--- 您選擇了【初始化設定】 ---")
    api_key = config.get("NOTION_KEY")
    parent_page_id = config.get("PARENT_PAGE_ID")
    if not all([api_key, parent_page_id]):
        print("❌ config.txt 中缺少 NOTION_KEY 或 PARENT_PAGE_ID。")
        return False
    return setup_all_databases(api_key, parent_page_id)

def run_reminder_task(config):
    """執行批次新增提醒的維護任務"""
    from add_reminders import add_reminders_for_upcoming_courses
    print("\n--- 您選擇了【日常維護】 ---")
    api_key = config.get("NOTION_KEY")
    database_id = config.get("COURSE_DATABASE_ID")
    if not all([api_key, database_id]):
        print("❌ config.txt 中缺少 NOTION_KEY 或 COURSE_DATABASE_ID。")
        return False
    return add_reminders_for_upcoming_courses(api_key, database_id)

def run_note_creation_task(config):
    """為指定學期批次建立筆記"""
    from create_notes import create_weekly_notes_for_semester
    print("\n--- 您選擇了【筆記建立】 ---")
    # 執行前，先互動式地詢問學期名稱
    semester_name = input("▶️  請輸入您要為哪個學期建立筆記 (例如: 115上): ").strip()
    if not semester_name:
        print("❌ 未輸入學期名稱，任務中止。")
        return False
        
    api_key = config.get("NOTION_KEY")
    course_db_id = config.get("COURSE_DATABASE_ID")
    notes_db_id = config.get("NOTE_DATABASE_ID")
    if not all([api_key, course_db_id, notes_db_id]):
        print("❌ config.txt 中缺少執行此任務所需的資料庫ID。")
        return False
    return create_weekly_notes_for_semester(api_key, course_db_id, notes_db_id, semester_name)

def main():
    """主程式進入點，提供任務選單並處理任務銜接。"""
    print("🚀 歡迎使用 Notion 自動化總管 🚀")
    print("="*50)
    print("請選擇要執行的任務：")
    print("  1. 【初始化設定】 首次使用，建立所有 Notion 資料庫")
    print("  2. 【學期性功能】 新學期開始，抓取課表並全自動排程")
    print("  3. 【筆記建立】   為指定學期批次建立所有課堂筆記")
    print("  4. 【日常維護】   為未來一個月的課程批次加上提醒")
    print("="*50)
    
    choice = input("請輸入選項 (1, 2, 3, 或 4): ")
    
    config = read_config()
    if not config:
        print("❌ 讀取設定檔失敗，無法繼續。")
        return

    if choice == '1':
        if run_initial_setup(config):
            print("\n" + "*"*50 + "\n✅ 初始化設定成功完成！您的 Notion 架構已準備就緒。")
            continue_choice = input("   是否要立刻接著執行【學期性功能】(任務2)？(y/N): ").lower()
            if continue_choice == 'y':
                choice = '2'
            else:
                print("   好的，您可以隨時重新執行本程式並選擇其他選項。")
                choice = None

    if choice == '2':
        if run_semester_task(config):
            print("\n" + "*"*50 + "\n✅ 學期性功能成功完成！")
            continue_choice_notes = input("   是否要為此學期預先建立所有筆記頁面(任務3)？(y/N): ").lower()
            if continue_choice_notes == 'y':
                choice = '3'
            else:
                choice = None
        else: # 如果任務2失敗，就不繼續
            choice = None

    if choice == '3':
        # 在執行任務3前，確保有學期名稱
        if not config.get("SEMESTER_NAME_FOR_NOTES"):
             # 從 run_semester_task 傳遞過來的學期名稱
            semester_name_for_notes = config.get("SEMESTER_NAME_FROM_TASK_2")
            if not semester_name_for_notes:
                 semester_name_for_notes = input("▶️  請輸入您要建立筆記的學期名稱 (例如: 115上): ").strip()
        else:
            semester_name_for_notes = config.get("SEMESTER_NAME_FOR_NOTES")

        if semester_name_for_notes:
            config["SEMESTER_NAME_FOR_NOTES"] = semester_name_for_notes # 儲存起來供後續使用
            if run_note_creation_task(config):
                print("\n" + "*"*50 + "\n✅ 筆記建立成功完成！")
                continue_choice_reminders = input("   是否要接著執行【日常維護】(任務4) 來加上近期提醒？(y/N): ").lower()
                if continue_choice_reminders == 'y':
                    choice = '4'
                else:
                    choice = None
        else:
            print("❌ 未提供學期名稱，無法建立筆記。")
            choice = None
    
    if choice == '4':
        run_reminder_task(config)
        
    elif choice not in ['1', '2', '3', '4']:
        print("❌ 無效的選項。")

    print("\n🏁 主程式 (main.py) 執行完畢。")

if __name__ == '__main__':
    main()