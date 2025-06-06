# 從我們的模組中，匯入需要被呼叫的函式
from notion_test import update_page_title
# ⚠️ 已將匯入的檔案名稱從 web_scraper_selenium 改為 web_scraper
from web_scraper import run_selenium_login_test 

def main():
    """
    主程式進入點，作為任務的總指揮。
    """
    print("🚀 主程式 (main.py) 開始執行...")

    # =======================================================
    # 在這裡決定你要執行哪個任務，可以取消註解來啟用對應功能
    # =======================================================

    # --- 任務一：Notion API 測試 ---
    # print("\n--- 執行 Notion 任務 ---")
    # update_page_title()

    # --- 任務二：Selenium 登入測試 ---
    print("\n--- 執行 Selenium 任務 ---")
    run_selenium_login_test()

    print("\n🏁 主程式 (main.py) 執行完畢。")

if __name__ == '__main__':
    main()