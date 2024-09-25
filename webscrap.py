import json
import os
import time
import pytz
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

# Path to the day order cache file
CACHE_FILE = "day_order_cache.json"

# Function to load the day order cache
def load_day_order_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {}

# Function to save the day order cache
def save_day_order_cache(day_order_cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(day_order_cache, f)

# Function to configure headless Chrome
def get_headless_browser():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")  # Optional: to speed up headless mode
    chrome_options.add_argument("--no-sandbox")   # Optional: to avoid some environment issues
    chrome_options.add_argument("--disable-dev-shm-usage")  # Optional: for memory issues
    chrome_options.add_argument("window-size=1920x1080")  # Optional: set window size for screenshots
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

# Function to get the current day order from the cache or website
def get_current_day_order():
    print("Loading day order from cache...")
    day_order_cache = load_day_order_cache()
    
    # Get today's date in the format 'YYYY-MM-DD'
    today = datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d")
    
    # Check if today's date exists in the cache
    if today in day_order_cache:
        print(f"Day order found in cache for {today}.")
        return day_order_cache[today]
    
    print(f"Day order not found in cache for {today}. Scraping from the web...")
    
    # If today's date is not in the cache, login to the website to get the day order
    current_day_order = login_and_get_day_order_from_website()
    
    # Update the cache with today's date and the day order
    day_order_cache[today] = current_day_order
    save_day_order_cache(day_order_cache)
    
    return current_day_order

# Function to login and get the day order from the website
def login_and_get_day_order_from_website():
    print("Starting headless browser for web scraping...")
    
    # Start the headless Selenium WebDriver
    driver = get_headless_browser()
    login_url = 'https://academia-pro.vercel.app/auth/login'
    
    try:
        driver.get(login_url)
        print("Navigated to login page.")
        
        # Take screenshot of login page
        driver.save_screenshot("login_page.png")
        print("Screenshot saved for login page.")
        
        # Enter login credentials
        username = driver.find_element(By.CSS_SELECTOR, 'input[placeholder="User ID"]')
        password = driver.find_element(By.CSS_SELECTOR, 'input[placeholder="Passw*rd"]')
        
        username.send_keys('kb7634')  # Replace with your actual username
        password.send_keys('srm@2004KB')  # Replace with your actual password
        
        print("Entered login credentials.")
        password.send_keys(Keys.RETURN)  # Press Enter to submit the form
        print("Login form submitted.")
        
        # Wait for the redirect after login
        WebDriverWait(driver, 15).until(EC.url_to_be('https://academia-pro.vercel.app/academia'))
        print("Login successful, redirected to academia page.")
        
        # Take screenshot after login
        driver.save_screenshot("post_login_page.png")
        print("Screenshot saved for post-login page.")
        
        # Wait for the day order element to be present
        day_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'span.text-sm.text-light-accent'))
        )
        print("Day order element found.")
        
        # Take screenshot of the page showing day order
        driver.save_screenshot("day_order_page.png")
        print("Screenshot saved for day order page.")

        # Extract the day order or holiday status from the text
        day_order_text = day_element.text
        print(f"Extracted day order text: {day_order_text}")

        if "Holiday" in day_order_text:
            print("Today is a holiday.")
            driver.quit()
            return "Holiday"
        
        # Extract the day order number (e.g., 'Day 4' -> 4)
        day_order = int(day_order_text.split()[1])
        print(f"Day order number extracted: Day {day_order}")
        
        driver.quit()
        return day_order
    
    except Exception as e:
        print(f"An error occurred during web scraping: {e}")
        driver.quit()
        raise e

# Example usage
if __name__ == "__main__":
    try:
        current_day_order = get_current_day_order()
        print(f"Current day order: {current_day_order}")
    except Exception as e:
        print(f"Failed to get the day order: {e}")
