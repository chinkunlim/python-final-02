import csv
import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

def remove_text_in_parentheses(text):
    """(通用函式) 移除文字中的括號及其內容"""
    return re.sub(r'\(.*?\)|（.*?）', '', text).strip()

def get_time_from_period(period):
    base_time = datetime.strptime("06:10", "%H:%M")
    delta_minutes = (int(period) - 1) * 60
    return base_time + timedelta(minutes=delta_minutes)

def format_class_time(time_str):
    if not time_str.strip(): return "未排定"
    parts = time_str.strip('/').split('/')
    day_map = {'一': '週一', '二': '週二', '三': '週三', '四': '週四', '五': '週五', '六': '週六', '日': '週日'}
    try:
        day_char = parts[0][0]
        day_chinese = day_map.get(day_char, "未知")
        periods = [int(p[1:]) for p in parts]
        start_period, end_period = min(periods), max(periods)
        start_time = get_time_from_period(start_period)
        end_time = get_time_from_period(end_period) + timedelta(minutes=50)
        return f"{day_chinese} {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}"
    except (ValueError, IndexError):
        return time_str

def process_source_and_create_files(page_source):
    """
    接收 page_source，解析資料，存成 CSV，並回傳結構化資料。
    """
    print("\n▶️  process_courses: 開始解析 HTML...")
    soup = BeautifulSoup(page_source, 'html.parser')
    table = soup.find('table', id='ContentPlaceHolder1_grd_selects')
    if not table:
        print("❌ process_courses: 錯誤，在 HTML 中找不到指定的課程表格。")
        return None

    processed_courses = []
    rows = table.find_all('tr')
    if len(rows) < 2: return []

    headers = [th.get_text(strip=True) for th in rows[0].find_all('th')]
    
    for row in rows[1:]:
        cols = row.find_all('td')
        if len(cols) < 12: continue

        # --- 核心修改：在處理「上課教室」時也進行清理 ---
        course_data = {
            headers[1]: cols[1].get_text(strip=True),
            headers[2]: remove_text_in_parentheses(cols[2].get_text()), # 清理課程名稱
            headers[3]: cols[3].get_text(strip=True),
            headers[4]: cols[4].get_text(strip=True).strip('/'),
            headers[5]: format_class_time(cols[5].get_text(strip=True)),
            headers[6]: remove_text_in_parentheses(cols[6].get_text(strip=True)), # 清理上課教室
            headers[7]: cols[7].get_text(strip=True),
        }
        processed_courses.append(course_data)
        
    output_filename = 'course_schedule.csv'
    with open(output_filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
        if processed_courses:
            writer = csv.DictWriter(csvfile, fieldnames=processed_courses[0].keys())
            writer.writeheader()
            writer.writerows(processed_courses)
    print(f"✅ process_courses: 已將使用者檢查用的課表儲存至 {output_filename}")

    print(f"✅ process_courses: 資料處理完成，共 {len(processed_courses)} 門課程。")
    return processed_courses