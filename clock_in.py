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

    # Only set up logging if debug is enabled
    logger = None
    if debug:
        log_path = os.path.join(script_dir, 'clock_in_schedule.log')
        logger = logging.getLogger('clock_in')
        if not logger.handlers:
            formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
            fh = logging.FileHandler(log_path, encoding='utf-8')
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(formatter)
            sh = logging.StreamHandler()
            sh.setLevel(logging.INFO)
            sh.setFormatter(formatter)
            logger.addHandler(fh)
            logger.addHandler(sh)
        logger.setLevel(logging.DEBUG)
    else:
        logger = logging.getLogger('clock_in')
        logger.setLevel(logging.CRITICAL)  # Suppress all logs below CRITICAL

    try:
        python_exe = sys.executable
        username = os.environ['USERNAME']
        
        # Use schtasks.exe which is more reliable for run-when-user-logs-out scenarios
        # Format: /ST HH:MM (24-hour, no date needed - schtasks defaults to today)
        scheduled_time = clock_out_time.strftime('%H:%M')
        
        if debug:
            logger.info('Scheduling task via schtasks.exe for %s', scheduled_time)
            logger.debug('Task name: %s', task_name)
            logger.debug('Python executable: %s', python_exe)
            logger.debug('Script: %s', clock_out_script)
            logger.debug('Working dir: %s', script_dir)
        
        # Create the scheduled task using schtasks which handles credentials better
        # Note: Omit /sd (start date) - schtasks defaults to today, avoiding locale date format issues
        cmd = [
            'schtasks', '/create', 
            '/tn', task_name,
            '/tr', f'"{python_exe}" "{clock_out_script}"',
            '/sc', 'once',
            '/st', scheduled_time,
            '/ru', username,
            '/rp', win_pwd,
            '/rl', 'limited',
            '/f',  # Force overwrite if exists
            '/du', '01:00'
        ]
        
        if debug:
            logger.debug('Running schtasks command: %s', ' '.join(cmd))
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        if debug:
            logger.debug('schtasks returncode=%s', result.returncode)
            logger.debug('schtasks stdout:\n%s', result.stdout)
            logger.debug('schtasks stderr:\n%s', result.stderr)
        
        if result.returncode != 0:
            if debug:
                ts = datetime.now().strftime('%Y%m%d_%H%M%S')
                out_file = os.path.join(script_dir, f'schtasks_stdout_{ts}.log')
                err_file = os.path.join(script_dir, f'schtasks_stderr_{ts}.log')
                with open(out_file, 'w', encoding='utf-8') as f:
                    f.write(result.stdout or '')
                with open(err_file, 'w', encoding='utf-8') as f:
                    f.write(result.stderr or '')
                logger.error('schtasks failed (code %s). Stdout: %s, Stderr: %s', result.returncode, out_file, err_file)
            return False

        if debug:
            logger.info("✓ SUCCESS: Task '%s' scheduled for today at %s", task_name, scheduled_time)
        return True

    except Exception as e:
        if debug:
            logger.exception('Task scheduling error: %s', e)
            tb_file = os.path.join(script_dir, f'schedule_exception_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
            with open(tb_file, 'w', encoding='utf-8') as f:
                f.write(traceback.format_exc())
            logger.error('Wrote traceback to %s', tb_file)
        return False