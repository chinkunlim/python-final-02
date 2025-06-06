import json
import time # 匯入 time 模組以供重試時等待
from web_scraper import login_and_get_page_source, read_config
from process_courses import process_source_and_create_files
from notion_test import update_page_title 

def main():
    """
    主程式進入點，作為任務的總指揮，並包含重試機制。
    """
    print("🚀 主程式 (main.py) 開始執行...")
    
    # 1. 讀取設定檔
    config = read_config()
    if not config: return
    
    login_url = config.get("LOGIN_URL")
    username = config.get("USERNAME")
    password = config.get("PASSWORD")
    if not all([login_url, username, password]):
        print("❌ config.txt 中缺少必要的登入資訊。")
        return
        
    # --- 核心修改：加入重試機制 ---
    page_source = None
    max_attempts = 3
    for attempt in range(max_attempts):
        print("\n" + "="*50)
        print(f"▶️  第 {attempt + 1}/{max_attempts} 次嘗試獲取網頁資源...")
        
        # 2. 呼叫爬蟲
        source = login_and_get_page_source(login_url, username, password)
        
        if source:
            print("✅ 成功獲取網頁資源！")
            page_source = source
            break # 成功後跳出重試循環
        else:
            print(f"⚠️ 第 {attempt + 1} 次嘗試失敗。")
            if attempt < max_attempts - 1:
                print("   將在 5 秒後重試...")
                time.sleep(5) # 重試前等待5秒

    # 3. 在所有重試結束後，檢查最終結果
    if not page_source:
        print("\n" + "☠️ "*20)
        print(f"錯誤：在嘗試 {max_attempts} 次後，依然無法獲取網頁資源。")
        print("請檢查網路連線或網站狀態，或查看 error_log 文件夾中的詳細資訊。")
        print("任務終止。")
        return # 結束程式
    # --- 重試機制結束 ---

    # 4. 如果成功獲取原始碼，就交給處理器
    print("\n▶️ main.py: 成功獲取 Page Source，準備交給處理模組...")
    final_courses_data = process_source_and_create_files(page_source)
    
    if final_courses_data:
        print("\n" + "="*50)
        print("✅ main.py: 已成功接收到處理後的課程 JSON 資料：")
        print(json.dumps(final_courses_data, indent=2, ensure_ascii=False))
        
        # 5. 在這裡呼叫 Notion 相關功能
        print("\n" + "="*50)
        print("▶️ main.py: 準備執行 Notion 相關任務...")
        update_page_title()

    else:
        print("☠️ main.py: 未能從 process_courses 模組獲取任何課程資料，任務終止。")

    print("\n🏁 主程式 (main.py) 執行完畢。")

if __name__ == '__main__':
    main()