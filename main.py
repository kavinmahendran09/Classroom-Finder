import pandas as pd
from datetime import datetime, timedelta
import pytz
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

# Define a global variable for the current day order
global_current_day_order = None

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

# Function to scrape the day order from the web
def get_day_order_from_web():
    # Set up Chrome options for headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.binary_location = "/opt/render/project/src/chrome/opt/google/chrome/google-chrome"

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager(driver_version="114.0.5735.90").install()), 
        options=chrome_options
    )
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        # Define the login URL
        login_url = 'https://academia-pro.vercel.app/auth/login'
        driver.get(login_url)
        
        # Enter login credentials
        username = driver.find_element(By.CSS_SELECTOR, 'input[placeholder="User ID"]')
        password = driver.find_element(By.CSS_SELECTOR, 'input[placeholder="Passw*rd"]')

        username.send_keys('kb7634')  # Replace with your actual username
        password.send_keys('srm@2004KB')  # Replace with your actual password
        password.send_keys(Keys.RETURN)  # Press Enter to submit the form

        print("Submitted login credentials.")
        
        # Wait for login to complete and redirect
        WebDriverWait(driver, 15).until(
            EC.url_to_be('https://academia-pro.vercel.app/academia')
        )
            
        # Wait for the day order element to be present
        day_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'span.text-sm.text-light-accent'))
        )

        # Extract the day order or holiday status from the text
        day_order_text = day_element.text

        # Check if the page indicates a "Holiday"
        if "Holiday" in day_order_text:
            return None  # Return None for holiday
        
        # Extract and return the day order (assuming the format is "Day X")
        return int(day_order_text.split(" ")[1])

    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    finally:
        # Close the browser
        driver.quit()

# Function to find free rooms
def find_free_rooms(custom_time=None, custom_day_order=None, custom_day=None):
    global global_current_day_order  # Declare the global variable inside the function

    # Load CSV files with updated paths
    unified_timetable_batch1 = pd.read_csv("batch 1/UNIFIED_TIME_TABLE.csv")
    detailed_timetable_batch1 = pd.read_csv("batch 1/detailed_timetable.csv")
    unified_timetable_batch2 = pd.read_csv("batch 2/NEW_UNIFIED_TIME_TABLE_24HR.csv")
    detailed_timetable_batch2 = pd.read_csv("batch 2/detailed_timetable_2.csv")
    day_order_df = pd.read_csv("batch 1/2024_Day_order.csv")

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

    # Adjust the date format to match the CSV file
    current_day = current_date.strftime("%d").lstrip("0")  # Remove leading zeros from the day
    current_month = current_date.strftime("%B")
    
    # Check for today's information in the CSV file
    day_order_row = day_order_df[(day_order_df['Date'].astype(str) == current_day) &
                                 (day_order_df['Month'].str.lower() == current_month.lower())]

    # If today's information is not in the CSV, scrape it from the web
    if day_order_row.empty:
        day_order = get_day_order_from_web()
        if day_order is None:
            day_order = "NULL"  # Use 'NULL' for holidays
        else:
            day_order = int(day_order)
        
        # Update the CSV file with new data only
        new_entry = pd.DataFrame({
            'Date': [current_day],
            'Day': [datetime.now().strftime("%A")],
            'Month': [current_month],
            'Day_order': [day_order]
        }, columns=day_order_df.columns)  # Keep the same columns to avoid mismatch

        # Append the new entry to the CSV file without altering existing data
        day_order_df = pd.concat([day_order_df, new_entry], ignore_index=True)
        day_order_df.to_csv("batch 1/2024_Day_order.csv", index=False, float_format='%.0f')  # Ensure no float conversion
    else:
        day_order = day_order_row['Day_order'].values[0]
        if pd.isnull(day_order):  # If it is NULL in CSV, set it as None
            day_order = None

    # Check if the day order is NULL
    if day_order == "NULL" or day_order is None:
        return {
            "status": "error",
            "message": "College doesn't run today.",
            "current_day_order": None,
            "current_time": current_time,
            "current_date": current_date.strftime("%d %B %Y"),
            "free_rooms": []
        }
    
    # Update the global variable
    global_current_day_order = int(day_order)

    # Check if the current time is before 8:00 AM or after 4:50 PM
    if current_time < "08:00":
        return {
            "status": "error",
            "message": "College not yet started.",
            "current_day_order": global_current_day_order,
            "current_time": current_time,
            "current_date": current_date.strftime("%d %B %Y"),
            "free_rooms": []
        }
    elif current_time > "16:50":
        return {
            "status": "error",
            "message": "College over.",
            "current_day_order": global_current_day_order,
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
            "current_day_order": global_current_day_order,
            "current_time": current_time,
            "current_date": current_date.strftime("%d %B %Y"),
            "free_rooms": []
        }
    
    # Find occupied rooms from the unified timetable
    occupied_rooms = set()

    occupied_rooms.update(
        unified_timetable.loc[
            (unified_timetable['Day'] == f"Day {global_current_day_order}") & 
            (unified_timetable['Time Slot'] == current_time_slot),
            'Room Number'
        ]
    )
    
    # Identify occupied rooms in the detailed timetable
    for course_code in unified_timetable.loc[
        (unified_timetable['Day'] == f"Day {global_current_day_order}") & 
        (unified_timetable['Time Slot'] == current_time_slot),
        'Course Code'
    ]:
        slot = course_code.split('/')[0]
        room_number_series = detailed_timetable.loc[detailed_timetable['Slot'] == slot, 'RoomNo.']
        
        # Check if room_number_series is not empty before accessing
        if not room_number_series.empty:
            room_number = room_number_series.values[0]
            occupied_rooms.add(room_number)

    # List all possible rooms
    all_rooms = set(unified_timetable['Room Number'].unique()).union(set(detailed_timetable['RoomNo.'].unique()))

    # Find free rooms and remove 'Unknown'
    free_rooms = [room for room in list(all_rooms - occupied_rooms) if room != "Unknown"]

    return {
        "status": "success",
        "message": "Data processed successfully",
        "current_day_order": global_current_day_order,
        "current_time": current_time,
        "current_date": current_date.strftime("%d %B %Y"),
        "free_rooms": free_rooms
    }


# Example of using the process_data function in the main application
def process_data(day_order_df, time_table):
    details = find_free_rooms()
    return details

if __name__ == '__main__':
    # Load the day order and timetable files
    day_order_df = pd.read_csv('batch 1/2024_Day_order.csv')

    # Call process_data with the current date and time
    result = process_data(day_order_df, None)
    print(result)
