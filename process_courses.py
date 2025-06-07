import csv
import re
import os
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

# ... (remove_text_in_parentheses, get_time_from_period, format_class_time_to_dict, generate_recurring_dates 函式維持不變) ...
def remove_text_in_parentheses(text):
    return re.sub(r'\(.*?\)|（.*?）', '', text).strip()
def get_time_from_period(period):
    base_time = datetime.strptime("06:10", "%H:%M")
    delta_minutes = (int(period) - 1) * 60
    return base_time + timedelta(minutes=delta_minutes)
def format_class_time_to_dict(time_str):
    if not time_str.strip(): return {"weekday": "未排定", "start_time": "", "end_time": ""}
    parts = time_str.strip('/').split('/')
    day_map = {'一': '週一', '二': '週二', '三': '週三', '四': '週四', '五': '週五', '六': '週六', '日': '週日'}
    try:
        day_char = parts[0][0]; day_chinese = day_map.get(day_char, "未知")
        periods = [int(p[1:]) for p in parts]; start_period, end_period = min(periods), max(periods)
        start_time = get_time_from_period(start_period); end_time = get_time_from_period(end_period) + timedelta(minutes=50)
        return {"weekday": day_chinese, "start_time": start_time.strftime('%H:%M'), "end_time": end_time.strftime('%H:%M')}
    except (ValueError, IndexError): return {"weekday": time_str, "start_time": "", "end_time": ""}
def generate_recurring_dates(time_str, semester_start_str, semester_end_str):
    if not time_str.strip(): return []
    try:
        semester_start = datetime.strptime(semester_start_str, "%Y-%m-%d"); semester_end = datetime.strptime(semester_end_str, "%Y-%m-%d")
    except ValueError: print("❌ 錯誤：學期起訖日期格式不正確。"); return []
    parts = time_str.strip('/').split('/'); day_map_index = {'一': 0, '二': 1, '三': 2, '四': 3, '五': 4, '六': 5, '日': 6}
    try:
        target_weekday = day_map_index.get(parts[0][0]);
        if target_weekday is None: return []
        periods = [int(p[1:]) for p in parts]; start_period, end_period = min(periods), max(periods)
        start_time = get_time_from_period(start_period); end_time = get_time_from_period(end_period) + timedelta(minutes=50)
        recurring_dates = []; current_date = semester_start; days_ahead = target_weekday - current_date.weekday()
        if days_ahead < 0: days_ahead += 7
        current_date += timedelta(days=days_ahead)
        while current_date <= semester_end:
            start_iso = f"{current_date.strftime('%Y-%m-%d')}T{start_time.strftime('%H:%M:%S')}"
            end_iso = f"{current_date.strftime('%Y-%m-%d')}T{end_time.strftime('%H:%M:%S')}"
            recurring_dates.append({"start": start_iso, "end": end_iso}); current_date += timedelta(days=7)
        return recurring_dates
    except (ValueError, IndexError): return []


def process_source_and_create_files(page_source, semester_start, semester_end):
    """接收 page_source，解析資料，存成 CSV，並回傳結構化資料。"""
    print("\n▶️  process_courses: 開始解析 HTML 並產生所有學期內課程...")
    soup = BeautifulSoup(page_source, 'html.parser')
    table = soup.find('table', id='ContentPlaceHolder1_grd_selects')
    if not table:
        print("❌ process_courses: 錯誤，在 HTML 中找不到指定的課程表格。")
        return None

    processed_courses = []
    rows = table.find_all('tr')[1:]
    if not rows:
        print("ℹ️  課程表格中沒有資料。")
        return []

    final_headers = ["課程代碼", "課程名稱", "必選修", "授課教師", "星期", "開始時間", "結束時間", "上課教室", "學分"]
    
    for row in rows:
        cols = row.find_all('td')
        if len(cols) < 8:
            continue
        
        original_time_str = cols[5].get_text(strip=True)
        time_details = format_class_time_to_dict(original_time_str)
        
        # [核心修改] 將 "星期幾" 改為 "星期"，以匹配 uploader
        course_data = {
            "課程代碼": cols[1].get_text(strip=True),
            "課程名稱": remove_text_in_parentheses(cols[2].get_text()),
            "必選修": cols[3].get_text(strip=True),
            "授課教師": cols[4].get_text(strip=True).strip('/'),
            "星期": time_details.get("weekday"), # 使用正確的鍵名 "星期"
            "開始時間": time_details.get("start_time"),
            "結束時間": time_details.get("end_time"),
            "重複日期列表": generate_recurring_dates(original_time_str, semester_start, semester_end),
            "上課教室": remove_text_in_parentheses(cols[6].get_text(strip=True)).strip('/'),
            "學分": cols[7].get_text(strip=True),
        }
        processed_courses.append(course_data)
        
    if not processed_courses:
        print("ℹ️  未處理任何課程資料。")
        return []

    # ... (儲存CSV的部分維持不變) ...
    output_dir = "course_schedule"
    if not os.path.exists(output_dir): os.makedirs(output_dir)
    output_filename = os.path.join(output_dir, f"{semester_start}_course_schedule.csv")
    try:
        with open(output_filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=final_headers)
            writer.writeheader()
            for course in processed_courses:
                row_to_write = {key: course.get(key, '') for key in final_headers}
                writer.writerow(row_to_write)
        print(f"✅ process_courses: 已將使用者檢查用的課表儲存至 {output_filename}")
    except IOError as e: print(f"❌ 寫入 CSV 檔案時發生錯誤: {e}")

    print(f"✅ process_courses: 資料處理完成。")
    return processed_courses