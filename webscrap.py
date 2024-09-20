from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)

# Set up the ChromeDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    # Define the login URL
    login_url = 'https://academia-pro.vercel.app/auth/login'  # Replace with the actual login URL
    driver.get(login_url)

    # Enter login credentials
    username = driver.find_element(By.CSS_SELECTOR, 'input[placeholder="User ID"]')  # Using CSS Selector
    password = driver.find_element(By.CSS_SELECTOR, 'input[placeholder="Passw*rd"]')  # Assuming there's a similar placeholder for password

    username.send_keys('kb7634')  # Replace with your actual username
    password.send_keys('srm@2004KB')  # Replace with your actual password
    password.send_keys(Keys.RETURN)  # Press Enter to submit the form

    # Wait for login to complete
    time.sleep(5)  # Adjust the sleep time as needed

    # Define the data URL
    data_url = 'https://academia-pro.vercel.app/academia'  # Replace with the URL of the page you want to scrape
    driver.get(data_url)

    # Scrape data from the page
    # Locate the span element using CSS Selector
    day_element = driver.find_element(By.CSS_SELECTOR, 'span.text-sm.text-light-accent')
    print(day_element.text)


finally:
    # Close the browser
    driver.quit()
