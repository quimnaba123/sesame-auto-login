import json
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains
import time
import login as login
import subprocess
import schedule
from datetime import datetime, timedelta
import os
import sys
import logging
import traceback
from datetime import datetime, timedelta
from pathlib import Path

def clock_in(debug):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    log_path = os.path.join(script_dir, 'clock_in_schedule.log')
    logger = logging.getLogger('clock_in')
    chrome_options = Options()
    if not debug:
        chrome_options.add_argument("--headless=new")
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

    #Click Login Button
    wait.until(EC.element_to_be_clickable((By.ID, "btn-login-login")))
    clock_in_button=driver.find_element(By.ID, "btn-login-login").click()
    
    # Start Sesame timer
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[test-id='el-768782d1']")))
    clock_in_button = driver.find_element(By.CSS_SELECTOR, "[test-id='el-768782d1']")
    # Wait a moment to verify
    time.sleep(1)
    # Try multiple click methods
    try:
        # Method 1: Regular click
        clock_in_button.click()
        logger.info('Clicked clock-in button (method 1)')
    except Exception as e1:
        logger.warning('Regular click failed: %s', e1)
        try:
            # Method 2: JavaScript click
            driver.execute_script("arguments[0].click();", clock_in_button)
            logger.info('Clicked clock-in button (method 2 - JavaScript)')
        except Exception as e2:
            logger.warning('JavaScript click failed: %s', e2)
            
            try:
                # Method 3: ActionChains
                from selenium.webdriver.common.action_chains import ActionChains
                ActionChains(driver).move_to_element(clock_in_button).click().perform()
                logger.info('Clicked clock-in button (method 3 - ActionChains)')
            except Exception as e3:
                logger.warning('ActionChains click failed: %s', e3)
                
                try:
                    # Method 4: Click with offset (sometimes helps with overlays)
                    ActionChains(driver).move_to_element_with_offset(clock_in_button, 5, 5).click().perform()
                    logger.info('Clicked clock-in button (method 4 - offset click)')
                except Exception as e4:
                    logger.error('All click methods failed for clock-in button')
                    raise e4

    schedule_clock_out(debug)

def schedule_clock_out(debug):
    """Schedule clock-out task for 8 hours later"""
    # Schedule clock-out for 8 hours later
    clock_out_time = datetime.now() + timedelta(hours=8)
    with open('PrivateData.json') as f:
        pvdata = json.load(f)
    win_pwd = pvdata["windows_pwd"]
    task_name = f"SesameClockOut_{datetime.now().strftime('%Y%m%d_%H%M')}"
    # Build paths and logger
    script_dir = os.path.dirname(os.path.abspath(__file__))
    clock_out_script = os.path.join(script_dir, "clock_out.py")
    python_exe = sys.executable
    username = os.environ['USERNAME']
    scheduled_time = clock_out_time.strftime('%H:%M')

    # Only set up logging if debug is enabled
    logger = None
    if debug:
        log_path = os.path.join(script_dir, 'clock_in_schedule.log')
        logger = logging.getLogger('clock_in')        

    # Use PowerShell to create the task with all the settings you want
    ps_command = f"""
        $action = New-ScheduledTaskAction -Execute '{python_exe}' -Argument '{clock_out_script}' -WorkingDirectory '{script_dir}'
        $trigger = New-ScheduledTaskTrigger -Once -At "{scheduled_time}"
        $principal = New-ScheduledTaskPrincipal -UserId '{username}' -LogonType Interactive -RunLevel Limited
        
        # Settings that give us what we want:
        # - Start when possible if missed (StartWhenAvailable)
        # - Run regardless of AC power (both battery options)
        # - Stop after 1 hour if not started (ExecutionTimeLimit)
        # - Wake the computer to run (WakeToRun)
        # - If task fails, retry up to 3 times (RestartOnFailure)
        $settings = New-ScheduledTaskSettingsSet `
            -AllowStartIfOnBatteries `
            -DontStopIfGoingOnBatteries `
            -StartWhenAvailable `
            -WakeToRun `
            -ExecutionTimeLimit (New-TimeSpan -Hours 1) `
            -RestartInterval (New-TimeSpan -Minutes 5) `
            -RestartCount 3 `
            -MultipleInstances IgnoreNew `
            -Priority 7
        
        # Register the task
        Register-ScheduledTask -TaskName '{task_name}' `
            -Action $action `
            -Trigger $trigger `
            -Principal $principal `
            -Settings $settings `
            -Force
        
        # Display the settings for verification
        $task = Get-ScheduledTask -TaskName '{task_name}'
        Write-Host "Task '{task_name}' scheduled for today at {scheduled_time}"
        Write-Host "Start when available (if missed): $($task.Settings.StartWhenAvailable)"
        Write-Host "Run on battery: $($task.Settings.DisallowStartIfOnBatteries -eq $false)"
        Write-Host "Execution time limit: $($task.Settings.ExecutionTimeLimit)"
        Write-Host "Wake to run: $($task.Settings.WakeToRun)"
    """

    # Execute PowerShell command
    if debug:
        logger.info('Scheduling task via PowerShell for %s with advanced settings', scheduled_time)
        logger.debug('PowerShell command: %s', ps_command)

    result = subprocess.run(
        ['powershell', '-Command', ps_command],
        capture_output=True, text=True, encoding='utf-8', errors='ignore'
    )