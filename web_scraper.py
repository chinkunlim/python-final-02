import time
import csv # 匯入 CSV 模組
from bs4 import BeautifulSoup # 匯入 BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, UnexpectedAlertPresentException, NoAlertPresentException

# ... read_config 函式維持不變 ...
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

def scrape_course_table(page_source):
    """
    使用 BeautifulSoup 解析頁面原始碼，抓取課表並存成 CSV。
    """
    print("\n▶️  開始解析頁面，抓取課程表格...")
    soup = BeautifulSoup(page_source, 'html.parser')
    
    # 1. 透過 ID 精準找到我們的目標表格
    table = soup.find('table', id='ContentPlaceHolder1_grd_selects')
    
    if not table:
        print("❌ 錯誤：在頁面中找不到指定的課程表格(ID: ContentPlaceHolder1_grd_selects)。")
        return

    # 2. 準備開啟一個 CSV 檔案來寫入
    #    使用 utf-8-sig 編碼可以確保 Excel 正確開啟中文，不會亂碼
    output_filename = 'course_schedule.csv'
    with open(output_filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
        csv_writer = csv.writer(csvfile)
        
        # 3. 尋找所有行 (tr)
        rows = table.find_all('tr')
        
        # 4. 處理表頭 (第一行)
        header_row = rows[0]
        headers = [th.get_text(strip=True) for th in header_row.find_all('th')]
        csv_writer.writerow(headers)
        print(f"   表頭已寫入: {headers}")

        # 5. 處理資料行 (從第二行開始)
        data_rows = rows[1:]
        for row in data_rows:
            # 找到該行的所有儲存格 (td)
            cols = row.find_all('td')
            # 提取每個儲存格的乾淨文字，並對內容做一些清理
            cleaned_cols = [col.get_text(strip=True).strip('/') for col in cols]
            csv_writer.writerow(cleaned_cols)
        
    print(f"✅ 課程資料已成功儲存至 {output_filename}")


def login_with_selenium(login_url, username, password):
    print("▶️  正在啟動 Chrome 瀏覽器...")
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 10)

    try:
        # ... (登入到清理循環的部分維持不變) ...
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
                print(f"✅ 自動偵測到原生對話框: {alert.text[:30]}...")
                alert.accept()
                print("   已自動點擊 '確定'。")
                continue 
            except NoAlertPresentException:
                pass
            
            try:
                div_modal_xpath = "//div[@aria-describedby='evalModal']"
                WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, div_modal_xpath)))
                print("✅ 偵測到 DIV 對話框，嘗試自動點擊「取消」...")
                cancel_button_xpath = "//div[@aria-describedby='evalModal']//button[text()='取消']"
                cancel_button = driver.find_element(By.XPATH, cancel_button_xpath)
                driver.execute_script("arguments[0].click();", cancel_button)
                print("   已自動點擊「取消」。")
                continue
            except TimeoutException:
                pass
            
            try:
                if "course_sele" in driver.current_url:
                    print("✅ 已確認進入主頁面，清理完畢。")
                    break
            except UnexpectedAlertPresentException:
                continue
            time.sleep(0.5)
        
        print("\n▶️  正在驗證最終登入狀態...")
        wait.until(EC.url_contains("course_sele"))
        print("🎉 登入成功！")

        # === 新增：呼叫爬蟲函式 ===
        # 取得登入後的頁面原始碼
        page_source = driver.page_source
        # 將原始碼交給爬蟲函式處理
        scrape_course_table(page_source)
        # === 爬蟲結束 ===
        
        print("\n▶️  所有任務完成，準備登出...")
        time.sleep(5) # 抓完資料後稍微等待一下

        print("▶️  準備執行登出...")
        logout_button_element = wait.until(EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_HyperLink5")))
        driver.execute_script("arguments[0].click();", logout_button_element)
        print("✅ 登出成功。")
        
        print("   等待 5 秒後關閉瀏覽器...")
        time.sleep(5)

    except Exception as e:
        print(f"☠️ 腳本執行期間發生未預期的錯誤: {type(e).__name__} - {e}")
        driver.save_screenshot("final_error_screenshot.png")
        print("   已將目前畫面截圖為 final_error_screenshot.png")
        print("   5 秒後關閉瀏覽器...")
        time.sleep(5)
        
    finally:
        print("▶️  正在關閉瀏覽器...")
        driver.quit()

# ... (底下程式碼不變)
def run_selenium_login_test():
    # ...
    config = read_config()
    if not config: return
    login_url = config.get("LOGIN_URL")
    username = config.get("USERNAME")
    password = config.get("PASSWORD")
    if not all([login_url, username, password]):
        print("❌ 錯誤：config.txt 中缺少 LOGIN_URL, USERNAME, 或 PASSWORD 其中一項。")
        return
    login_with_selenium(login_url, username, password)
if __name__ == '__main__':
    run_selenium_login_test()