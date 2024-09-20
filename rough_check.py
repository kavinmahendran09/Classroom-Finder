import pandas as pd
from datetime import datetime, timedelta
import pytz
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

CACHE_FILE = 'day_order_cache.json'

def is_weekday(custom_day=None):
    if custom_day:
        date_obj = datetime.strptime(custom_day, "%d %B %Y")
    else:
        date_obj = datetime.now()
    return date_obj.weekday() < 5

def save_day_order_to_cache(day_order):
    current_date = datetime.now().strftime("%Y-%m-%d")
    cache_data = {"date": current_date, "day_order": day_order}
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache_data, f)

def load_day_order_from_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    return None

def get_day_order_from_web():
    driver = webdriver.Safari()
    try:
        login_url = 'https://academia-pro.vercel.app/auth/login'
        driver.get(login_url)

        username = driver.find_element(By.CSS_SELECTOR, 'input[placeholder="User ID"]')
        password = driver.find_element(By.CSS_SELECTOR, 'input[placeholder="Passw*rd"]')
        
        username.send_keys('kb7634')
        password.send_keys('srm@2004KB')
        password.send_keys(Keys.RETURN)

        WebDriverWait(driver, 10).until(
            EC.url_to_be('https://academia-pro.vercel.app/academia')
        )

        time.sleep(10)  # Wait for the page to load completely
        day_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'span.text-sm.text-light-accent'))
        )
        
        day_order_text = day_element.text
        return int(day_order_text.split(" ")[1])  # Extract the day number
    finally:
        driver.quit()

def get_day_order():
    current_date = datetime.now().strftime("%Y-%m-%d")
    cache_data = load_day_order_from_cache()
    if cache_data and cache_data["date"] == current_date:
        return cache_data["day_order"]
    
    current_day_order = get_day_order_from_web()
    save_day_order_to_cache(current_day_order)
    return current_day_order

def round_time_to_nearest_five(current_time):
    time_obj = datetime.strptime(current_time, "%H:%M")
    minute = time_obj.minute
    remainder = minute % 5
    if remainder != 0:
        new_minute = minute + (5 - remainder)
        if new_minute == 60:
            time_obj += timedelta(hours=1)
            new_minute = 0
    else:
        new_minute = minute
    rounded_time = time_obj.replace(minute=new_minute, second=0).strftime("%H:%M")
    return rounded_time

def find_free_rooms(custom_time=None, custom_day_order=None, custom_day=None, building_name=None):
    response = {
        'status': 'success',
        'message': '',
        'current_day_order': None,
        'current_time': None,
        'current_date': None,
        'free_rooms': []
    }
    
    unified_timetable_batch1 = pd.read_csv("batch 1/UNIFIED_TIME_TABLE.csv")
    detailed_timetable_batch1 = pd.read_csv("batch 1/detailed_timetable.csv")
    unified_timetable_batch2 = pd.read_csv("batch 2/NEW_UNIFIED_TIME_TABLE_24HR.csv")
    detailed_timetable_batch2 = pd.read_csv("batch 2/detailed_timetable_2.csv")
    
    unified_timetable = pd.concat([unified_timetable_batch1, unified_timetable_batch2], ignore_index=True)
    detailed_timetable = pd.concat([detailed_timetable_batch1, detailed_timetable_batch2], ignore_index=True)

    time_slots = [
        ("08:00", "08:50"), ("08:50", "09:40"), ("09:45", "10:35"), ("10:40", "11:30"),
        ("11:35", "12:25"), ("12:30", "13:20"), ("13:25", "14:15"), ("14:20", "15:10"),
        ("15:10", "16:00"), ("16:00", "16:50"), ("16:50", "17:30"), ("17:30", "18:10")
    ]

    ist = pytz.timezone('Asia/Kolkata')
    current_time = custom_time or datetime.now(ist).strftime("%H:%M")
    current_date = datetime.strptime(custom_day, "%d %B %Y") if custom_day else datetime.now()

    response['current_time'] = current_time
    response['current_date'] = current_date.strftime("%d %B %Y")

    if not is_weekday(custom_day):
        return {
            "status": "error",
            "message": "College doesn't run today.",
            "current_day_order": None,
            "current_time": current_time,
            "current_date": current_date.strftime("%d %B %Y"),
            "free_rooms": []
        }

    try:
        current_day_order = get_day_order() if not custom_day_order else custom_day_order
        response['current_day_order'] = current_day_order
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to get day order: {e}",
            "current_day_order": None,
            "current_time": current_time,
            "current_date": current_date.strftime("%d %B %Y"),
            "free_rooms": []
        }

    # Check time boundaries
    if current_time < "08:00":
        return {
            "status": "error",
            "message": "College not yet started.",
            "current_day_order": current_day_order,
            "current_time": current_time,
            "current_date": current_date.strftime("%d %B %Y"),
            "free_rooms": []
        }
    elif current_time > "16:50":
        return {
            "status": "error",
            "message": "College over.",
            "current_day_order": current_day_order,
            "current_time": current_time,
            "current_date": current_date.strftime("%d %B %Y"),
            "free_rooms": []
        }

    current_time_slot = None
    for start, end in time_slots:
        if start <= current_time <= end:
            current_time_slot = f"{start} - {end}"
            break

    if current_time_slot is None:
        next_update_time = round_time_to_nearest_five(current_time)
        return {
            "status": "error",
            "message": f"Free rooms get updated at: {next_update_time}",
            "current_day_order": current_day_order,
            "current_time": current_time,
            "current_date": current_date.strftime("%d %B %Y"),
            "free_rooms": []
        }

    occupied_rooms = set(unified_timetable.loc[
        (unified_timetable['Day'] == f"Day {current_day_order}") & 
        (unified_timetable['Time Slot'] == current_time_slot),
        'Room Number'
    ].tolist())

    detailed_slots = detailed_timetable['Slot'].tolist()
    detailed_rooms = detailed_timetable['RoomNo.'].tolist()
    detailed_room_map = dict(zip(detailed_slots, detailed_rooms))

    for course_code in unified_timetable.loc[
        (unified_timetable['Day'] == f"Day {current_day_order}") & 
        (unified_timetable['Time Slot'] == current_time_slot),
        'Course Code'
    ]:
        slot = course_code.split('/')[0]
        room_number = detailed_room_map.get(slot, "Unknown")
        occupied_rooms.add(room_number)

    all_rooms = set(unified_timetable['Room Number'].unique()).union(set(detailed_timetable['RoomNo.'].unique()))
    free_rooms = [room for room in all_rooms - occupied_rooms if room != "Unknown"]

    response.update({
        "status": "success",
        "message": "Data processed successfully",
        "current_day_order": current_day_order,
        "free_rooms": free_rooms
    })

    return response

def process_data(day_order, time_table, building_name=None):
    details = find_free_rooms(custom_day_order=day_order)
    return details

if __name__ == '__main__':
    # Example call to process_data
    day_order = get_day_order()  # Assuming you fetch the day order
    time_table = None  # Replace with actual timetable if needed
    result = process_data(day_order, time_table)
    print(result)
