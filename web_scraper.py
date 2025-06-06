import time
import os # 匯入 os 模組來操作文件夾
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, UnexpectedAlertPresentException, NoAlertPresentException

# (read_config 函式維持不變)
def read_config(filename='config.txt'):
    print("▶️  正在讀取設定檔 config.txt...")
    config = {}
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    config[key.strip()] = value.strip()
        print("✅ 設定檔讀取成功。")
        return config
    except FileNotFoundError:
        print(f"❌ 錯誤：找不到設定檔 {filename}。")
        return None

def login_and_get_page_source(login_url, username, password):
    """
    登入、處理對話框，最終回傳登入成功後的頁面原始碼。
    """
    print("▶️  正在啟動 Chrome 瀏覽器...")
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 10)
    page_source = None

    try:
        # ... (登入到抓取原始碼的邏輯維持不變) ...
        print(f"▶️  正在前往登入頁面: {login_url}")
        driver.get(login_url)
        username_field = wait.until(EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_ed_StudNo")))
        username_field.send_keys(username)
        password_field = wait.until(EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_ed_pass")))
        password_field.send_keys(password)
        login_button = wait.until(EC.element_to_be_clickable((By.ID, "ContentPlaceHolder1_BtnLoginNew")))
        login_button.click()

        print("\n▶️  登入後，啟動「全自動對話框清理循環」(最多等待10秒)...")
        end_time = time.time() + 10
        while time.time() < end_time:
            try:
                alert = driver.switch_to.alert
                alert.accept()
                continue 
            except NoAlertPresentException: pass
            try:
                div_modal_xpath = "//div[@aria-describedby='evalModal']//button[text()='取消']"
                cancel_button = WebDriverWait(driver, 1).until(EC.element_to_be_clickable((By.XPATH, div_modal_xpath)))
                driver.execute_script("arguments[0].click();", cancel_button)
                continue
            except TimeoutException: pass
            try:
                if "course_sele" in driver.current_url:
                    print("✅ 已確認進入主頁面，清理完畢。")
                    break
            except UnexpectedAlertPresentException: continue
            time.sleep(0.5)

        wait.until(EC.url_contains("course_sele"))
        print("🎉 登入成功！準備抓取頁面原始碼...")
        
        page_source = driver.page_source
        
        print("✅ 頁面原始碼抓取成功。")
        time.sleep(2)
        
        logout_button_element = wait.until(EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_HyperLink5")))
        driver.execute_script("arguments[0].click();", logout_button_element)
        print("✅ 已登出。")

    except Exception as e:
        print(f"☠️ web_scraper 執行期間發生錯誤: {type(e).__name__} - {e}")
        
        # === 核心修改：將除錯檔案儲存到指定文件夾 ===
        print("   正在儲存除錯檔案至 'error_log/' 文件夾...")
        try:
            # 1. 定義文件夾名稱
            error_log_dir = "error_log"
            
            # 2. 檢查文件夾是否存在，若否，則建立
            if not os.path.exists(error_log_dir):
                os.makedirs(error_log_dir)
                print(f"   ℹ️  已自動建立 '{error_log_dir}' 文件夾。")
            
            # 3. 組合檔案的完整路徑
            screenshot_path = os.path.join(error_log_dir, "error_page_screenshot.png")
            html_path = os.path.join(error_log_dir, "error_page_source.html")

            # 4. 儲存截圖和HTML
            driver.save_screenshot(screenshot_path)
            print(f"   ✅ 已將畫面截圖儲存至 {screenshot_path}")

            with open(html_path, "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print(f"   ✅ 已將頁面HTML儲存至 {html_path}")
            
        except Exception as save_e:
            print(f"   ⚠️ 儲存除錯檔案時發生額外錯誤: {save_e}")
        # ==========================================================
    
    finally:
        print("▶️  正在關閉瀏覽器...")
        driver.quit()
        return page_source