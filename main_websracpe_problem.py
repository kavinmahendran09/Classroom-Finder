import pandas as pd
from datetime import datetime
import json
import pytz
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

CACHE_FILE = 'day_order_cache.json'

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
def find_free_rooms(custom_time=None, custom_day=None):
    # Load the CSV file that checks if today is a weekday (if necessary)
    day_order_df = pd.read_csv("batch 1/2024_Day_order.csv")

    # Get the current date and time in IST
    ist = pytz.timezone('Asia/Kolkata')
    if custom_time:
        current_time = custom_time
    else:
        current_time = datetime.now(ist).strftime("%H:%M")

    if custom_day:
        current_date = datetime.strptime(custom_day, "%d %B %Y")
    else:
        current_date = datetime.now()

    # Check if today is a weekday
    if not is_weekday(custom_day=custom_day):
        return {
            "status": "error",
            "message": "College doesn't run today.",
            "current_day_order": None,
            "current_time": current_time,
            "current_date": current_date.strftime("%d %B %Y"),
            "free_rooms": []
        }

    # Get the day order (either from cache or by scraping)
    try:
        current_day_order = get_day_order()
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to get day order: {e}",
            "current_day_order": None,
            "current_time": current_time,
            "current_date": current_date.strftime("%d %B %Y"),
            "free_rooms": []
        }

    # Rest of the logic remains the same for finding free rooms based on day order
    # (Your existing code for timetable logic goes here)
    # ...

    return {
        "status": "success",
        "message": "Data processed successfully",
        "current_day_order": current_day_order,
        "current_time": current_time,
        "current_date": current_date.strftime("%d %B %Y"),
        "free_rooms": []  # Fill in with actual free room data from your logic
    }

if __name__ == '__main__':
    # Call the find_free_rooms function
    result = find_free_rooms()
    print(result)




# Code works perfectly need to check after 12:00 am