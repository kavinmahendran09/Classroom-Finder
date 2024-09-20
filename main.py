import pandas as pd
from datetime import datetime, timedelta
import pytz
import os
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

CACHE_FILE = 'day_order_cache.json'

# Function to round time to the next nearest 5 minutes
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

# Function to check if today is a weekday
def is_weekday(custom_day=None):
    if custom_day:
        date_obj = datetime.strptime(custom_day, "%d %B %Y")
    else:
        date_obj = datetime.now()

    # Monday is 0 and Sunday is 6, so check if it's a weekday (Monday to Friday)
    return date_obj.weekday() < 5

# Function to save the day order in the cache
def save_day_order_to_cache(day_order):
    current_date = datetime.now().strftime("%Y-%m-%d")
    cache_data = {
        "date": current_date,
        "day_order": day_order
    }
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache_data, f)

# Function to load the day order from the cache
def load_day_order_from_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            cache_data = json.load(f)
            return cache_data
    return None

# Function to get the day order by scraping the website using Selenium
def get_day_order_from_web():
    driver = webdriver.Safari()

    try:
        # Define the login URL
        login_url = 'https://academia-pro.vercel.app/auth/login'
        driver.get(login_url)

        # Enter login credentials
        username = driver.find_element(By.CSS_SELECTOR, 'input[placeholder="User ID"]')
        password = driver.find_element(By.CSS_SELECTOR, 'input[placeholder="Passw*rd"]')  # Replace with actual placeholder

        username.send_keys('kb7634')  # Replace with your actual username
        password.send_keys('srm@2004KB')  # Replace with your actual password
        password.send_keys(Keys.RETURN)  # Press Enter to submit the form

        # Wait for login to complete and redirect
        WebDriverWait(driver, 10).until(
            EC.url_to_be('https://academia-pro.vercel.app/academia')  # Adjust the URL if needed
        )

        # Additional wait to ensure the page fully loads
        time.sleep(10)  # Wait for 10 seconds for the page to load completely

        # Wait for the day order element to be present
        day_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'span.text-sm.text-light-accent'))
        )

        # Extract the day order from the text
        day_order_text = day_element.text
        return int(day_order_text.split(" ")[1])  # Assuming it returns "Day X"

    finally:
        # Close the browser
        driver.quit()

# Function to get the day order, either from cache or by scraping
def get_day_order():
    current_date = datetime.now().strftime("%Y-%m-%d")

    # Try to load from cache
    cache_data = load_day_order_from_cache()
    if cache_data:
        cached_date = cache_data["date"]
        if cached_date == current_date:
            # If cache is from today, use it
            return cache_data["day_order"]

    # If cache is outdated or doesn't exist, scrape it
    current_day_order = get_day_order_from_web()

    # Save the new day order to cache
    save_day_order_to_cache(current_day_order)

    return current_day_order

# Function to find free rooms
def find_free_rooms(custom_time=None, custom_day_order=None, custom_day=None):
    global global_current_day_order  # Declare the global variable inside the function

    # Load CSV files with updated paths
    unified_timetable_batch1 = pd.read_csv("batch 1/UNIFIED_TIME_TABLE.csv")
    detailed_timetable_batch1 = pd.read_csv("batch 1/detailed_timetable.csv")
    unified_timetable_batch2 = pd.read_csv("batch 2/NEW_UNIFIED_TIME_TABLE_24HR.csv")
    detailed_timetable_batch2 = pd.read_csv("batch 2/detailed_timetable_2.csv")

    # Combine the timetables and detailed timetables from both batches
    unified_timetable = pd.concat([unified_timetable_batch1, unified_timetable_batch2], ignore_index=True)
    detailed_timetable = pd.concat([detailed_timetable_batch1, detailed_timetable_batch2], ignore_index=True)

    # Define time slots
    time_slots = [
        ("08:00", "08:50"), ("08:50", "09:40"), ("09:45", "10:35"), ("10:40", "11:30"),
        ("11:35", "12:25"), ("12:30", "13:20"), ("13:25", "14:15"), ("14:20", "15:10"),
        ("15:10", "16:00"), ("16:00", "16:50"), ("16:50", "17:30"), ("17:30", "18:10")
    ]

    # Get current time in IST
    if custom_time:
        current_time = custom_time
    else:
        ist = pytz.timezone('Asia/Kolkata')
        current_time = datetime.now(ist).strftime("%H:%M")

    # Get current date
    if custom_day:
        current_date = datetime.strptime(custom_day, "%d %B %Y")
    else:
        current_date = datetime.now()

    # Get the current day order
    if custom_day_order is not None:
        current_day_order = custom_day_order
    else:
        current_day_order = get_day_order()

    # Update the global variable
    global_current_day_order = current_day_order

    # Check if the current time is before 8:00 AM or after 4:50 PM
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

    # Find the current time slot
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
    
    # Find occupied rooms from the unified timetable
    occupied_rooms = set()

    occupied_rooms.update(
        unified_timetable.loc[(unified_timetable['Day'] == f"Day {current_day_order}") &
                              (unified_timetable['Time Slot'] == current_time_slot),
                              'Room Number'].tolist()
    )

    # Filter out rows from the detailed timetable that match the current day order
    detailed_filtered_rows = detailed_timetable[detailed_timetable['DayOrder'] == current_day_order]

    # Append the occupied rooms from the detailed timetable
    occupied_rooms.update(detailed_filtered_rows['RoomNo.'].tolist())

    # Find all rooms
    all_rooms = set(unified_timetable['Room Number'].unique()).union(set(detailed_timetable['RoomNo.'].unique()))

    # Find free rooms by subtracting occupied rooms from all rooms
    free_rooms = list(all_rooms - occupied_rooms)

    return {
        "status": "success",
        "message": "Free rooms found.",
        "current_day_order": current_day_order,
        "current_time": current_time,
        "current_date": current_date.strftime("%d %B %Y"),
        "free_rooms": free_rooms
    }

# Example of using the process_data function in the main application
def process_data(day_order, time_table, building_name=None):
    details = find_free_rooms(custom_day_order=day_order)
    return details

# Example of how the final output could be printed
if __name__ == "__main__":
    result = find_free_rooms()
    print(result)
