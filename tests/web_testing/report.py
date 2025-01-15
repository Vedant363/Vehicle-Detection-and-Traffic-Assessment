import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

@pytest.fixture(scope="module")
def driver():
    # Set up Chrome options (optional)
    # chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Optional: Run headless if you don't want a browser window to open

    # Set up the chromedriver path using the Service class
    service = Service('D:\\Google Downloads\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe')

    # Start the driver
    driver = webdriver.Chrome(service=service)
    yield driver
    driver.quit()

def test_flask_app(driver):
    # 1. Navigate to the login page
    driver.get('http://localhost:8087')
    
    # 2. Find the login form fields and fill them in
    driver.find_element(By.NAME, 'username').send_keys('test')  # 'username' field
    driver.find_element(By.NAME, 'password').send_keys('test123')  # 'password' field
    
    # 3. Submit the login form (click the submit button)
    driver.find_element(By.XPATH, "//button[text()='Login']").click()
    
    # 4. Wait until redirection to '/enterurl' page (increase wait time)
    WebDriverWait(driver, 10).until(EC.url_contains("/enterrurl"))
    print("Redirected to /enterurl")

    # 5. On /enterurl, locate the submit button (using the type='submit' attribute)
    submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
    submit_button.click()
    
    # 6. Wait for the page to load (give it 2 minutes)
    print("Waiting for /index page to load...")
    time.sleep(20)  # 2 minutes wait
    
    # 7. Wait for the page to be fully loaded (total time: 5 minutes)
    print("Waiting for additional 5 minutes...")
    time.sleep(60)  # 5 more minutes
    
    # 8. Press "q" key to stop the execution (simulating key press)
    print("Pressing 'q' key to stop execution...")
    actions = ActionChains(driver)
    actions.send_keys('q').perform()
    time.sleep(30)
    
    print("Test completed.")