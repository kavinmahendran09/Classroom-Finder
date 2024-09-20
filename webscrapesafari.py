from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Set up the Safari WebDriver
driver = webdriver.Safari()

try:
    # Define the login URL
    login_url = 'https://academia-pro.vercel.app/auth/login'  # Replace with the actual login URL
    driver.get(login_url)

    # Enter login credentials
    username = driver.find_element(By.CSS_SELECTOR, 'input[placeholder="User ID"]')
    password = driver.find_element(By.CSS_SELECTOR, 'input[placeholder="Passw*rd"]')  # Assuming there's a similar placeholder for password

    username.send_keys('###')  # Replace with your actual username
    password.send_keys('###')  # Replace with your actual password
    password.send_keys(Keys.RETURN)  # Press Enter to submit the form

    # Wait for login to complete and redirect
    WebDriverWait(driver, 10).until(
        EC.url_to_be('https://academia-pro.vercel.app/academia')  # Adjust the URL if needed
    )

    # Additional wait to ensure the page fully loads
    time.sleep(10)  # Wait for 10 seconds for the page to load completely

    # Define the data URL (if you need to navigate separately, you can remove this line)
    data_url = 'https://academia-pro.vercel.app/academia'  # Replace with the URL of the page you want to scrape
    driver.get(data_url)

    # Wait for the element to be present
    day_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'span.text-sm.text-light-accent'))
    )
    print(day_element.text)

finally:
    # Close the browser
    driver.quit()
