import json
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
# Check if something is covering the input
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains
import time

def clock_login():
    chrome_options = Options()
    chrome_options.add_argument("--disable-infobars")  # Disable infobars
    chrome_options.add_argument("--disable-extensions")  # Disable extensions
    chrome_options.add_argument("--disable-notifications")  # Disable extensions
    chrome_options.add_argument("--log-level=3")  # Suppress logs
    chrome_options.add_argument("--disable-search-engine-choice-screen") #Disable Choose Search Engine
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    # Add headless mode

    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://app.sesametime.com/login")

    wait = WebDriverWait(driver, 20)
    with open('PrivateData.json') as f:
        pvdata = json.load(f)

    try:
        wait.until(EC.element_to_be_clickable((By.ID, "txt-email-login")))
        email_sesame = driver.find_element(By.ID, "txt-email-login")
        email_sesame.click()
        
        # Set value directly with JavaScript
        driver.execute_script(
            f"""
            var element = document.getElementById('txt-email-login');
            
            // Set the value
            element.value = '{pvdata["user_email"]}';
            
            // Trigger ALL possible events
            var events = ['input', 'change', 'blur', 'focus', 'keydown', 'keyup', 'keypress'];
            events.forEach(function(eventType) {{
                element.dispatchEvent(new Event(eventType, {{ bubbles: true }}));
            }});
            
            // For Vue.js (based on your data-v- attribute)
            if (element.__vue__) {{
                // Update Vue's internal model
                element.__vue__.$emit('input', '{pvdata["user_email"]}');
            }}
            """
        )
                   
    except Exception as e:
        print(f"Error: {e}")

    driver.find_element(By.ID, "btn-next-login").click()
    wait.until(EC.element_to_be_clickable((By.ID, "txt-pw-login")))
    pwd_sesame = driver.find_element(By.ID, "txt-pw-login")
    driver.execute_script(
            f"""
            var element = document.getElementById('txt-pw-login');
            
            // Set the value
            element.value = '{pvdata["pwd"]}';
            
            // Trigger ALL possible events
            var events = ['input', 'change', 'blur', 'focus', 'keydown', 'keyup', 'keypress'];
            events.forEach(function(eventType) {{
                element.dispatchEvent(new Event(eventType, {{ bubbles: true }}));
            }});
            
            // For Vue.js (based on your data-v- attribute)
            if (element.__vue__) {{
                // Update Vue's internal model
                element.__vue__.$emit('input', '{pvdata["pwd"]}');
            }}
            """
        )
    driver.find_element(By.ID, "btn-login-login").click()

    #Start timer
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[test-id='el-768782d1']")))
    clock_in_button = driver.find_element(By.CSS_SELECTOR, "[test-id='el-768782d1']")
    clock_in_button.click() 

    #Clockout button id button-click-sign-out
    


