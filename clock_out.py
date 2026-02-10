import json
import time
import os
import sys
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import logging

def clock_out():
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Run in background
    chrome_options.add_argument("--disable-infobars")  # Disable infobars
    chrome_options.add_argument("--disable-extensions")  # Disable extensions
    chrome_options.add_argument("--disable-notifications")  # Disable extensions
    chrome_options.add_argument("--log-level=3")  # Suppress logs
    chrome_options.add_argument("--disable-search-engine-choice-screen") #Disable Choose Search Engine
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
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
    #Click Login Button
    wait.until(EC.element_to_be_clickable((By.ID, "btn-login-login")))
    clock_in_button=driver.find_element(By.ID, "btn-login-login").click()

    #Logout button
    clock_out_button = wait.until(
        EC.element_to_be_clickable((By.ID, "button-click-sign-out"))
    )
    clock_out_button.click()
    
    print(f"Successfully clocked out at: {datetime.now()}")
    
    # Clean up scheduled task
    # Delete task with new naming pattern
    task_name_pattern = "SesameClockOut_*"
    try:
        # Query tasks that match our pattern
        result = subprocess.run(
            ['schtasks', '/query', '/tn', task_name_pattern, '/fo', 'CSV'],
            capture_output=True, text=True, encoding='utf-8'
        )
        
        if result.returncode == 0:
            # Parse CSV output
            lines = result.stdout.strip().split('\n')
            for line in lines[1:]:  # Skip header
                if ',' in line:
                    task_name = line.split(',')[0].strip('"')
                    if 'SesameClockOut' in task_name:
                        print(f"Deleting task: {task_name}")
                        subprocess.run(['schtasks', '/delete', '/tn', task_name, '/f'], 
                                        capture_output=True, check=False)
        
    except Exception as e:
        print(f"Could not query tasks: {e}")

if __name__ == "__main__":
    clock_out()