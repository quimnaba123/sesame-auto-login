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
import subprocess
import traceback
from pathlib import Path

def clock_out(debug=False):
    # Prepare logging only if debug is enabled
    script_dir = os.path.dirname(os.path.abspath(__file__))
    logger = logging.getLogger('clock_out')
    
    if debug:
        log_path = os.path.join(script_dir, 'clock_out.log')
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
        logger.setLevel(logging.CRITICAL)  # Suppress all logs

    chrome_options = Options()
    # Run in headless mode so the scheduled task can run without an interactive session
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-infobars")  # Disable infobars
    chrome_options.add_argument("--disable-extensions")  # Disable extensions
    chrome_options.add_argument("--disable-notifications")  # Disable extensions
    chrome_options.add_argument("--log-level=3")  # Suppress logs
    chrome_options.add_argument("--disable-search-engine-choice-screen") #Disable Choose Search Engine
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    driver = None
    try:
        logger.info('Launching Chrome WebDriver (headless)')
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://app.sesametime.com/login")
        logger.info('Loaded page: %s (title=%s)', driver.current_url, driver.title)

        wait = WebDriverWait(driver, 20)
        with open('PrivateData.json') as f:
            pvdata = json.load(f)

        try:
            logger.debug('Waiting for email field')
            wait.until(EC.element_to_be_clickable((By.ID, "txt-email-login")))
            email_sesame = driver.find_element(By.ID, "txt-email-login")
            email_sesame.click()
            # Set value directly with JavaScript
            driver.execute_script(
                f"""
                var element = document.getElementById('txt-email-login');
                element.value = '{pvdata["user_email"]}';
                var events = ['input', 'change', 'blur', 'focus', 'keydown', 'keyup', 'keypress'];
                events.forEach(function(eventType) {{ element.dispatchEvent(new Event(eventType, {{ bubbles: true }})); }});
                if (element.__vue__) {{ element.__vue__.$emit('input', '{pvdata["user_email"]}'); }}
                """
            )
            logger.info('Email field populated')
        except Exception as e:
            logger.exception('Failed to populate email field: %s', e)
            # continue so we can capture more diagnostics below

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
        # Click Login Button
        try:
            wait.until(EC.element_to_be_clickable((By.ID, "btn-login-login")))
            driver.find_element(By.ID, "btn-login-login").click()
            logger.info('Clicked login button')
        except Exception as e:
            logger.exception('Failed to click login button: %s', e)
            raise

        # Logout button - debug version
        try:
            wait.until(EC.element_to_be_clickable((By.ID, "button-click-sign-out")))
            sign_out_button = driver.find_element(By.ID, "button-click-sign-out")
            
            # Try multiple click methods
            try:
                # Method 1: Regular click
                sign_out_button.click()
                logger.info('Clicked sign out button (method 1)')
            except Exception as e1:
                logger.warning('Regular click failed: %s', e1)
                
                try:
                    # Method 2: JavaScript click
                    driver.execute_script("arguments[0].click();", sign_out_button)
                    logger.info('Clicked sign out button (method 2 - JavaScript)')
                except Exception as e2:
                    logger.warning('JavaScript click failed: %s', e2)
                    
                    try:
                        # Method 3: ActionChains
                        from selenium.webdriver.common.action_chains import ActionChains
                        ActionChains(driver).move_to_element(sign_out_button).click().perform()
                        logger.info('Clicked sign out button (method 3 - ActionChains)')
                    except Exception as e3:
                        logger.warning('ActionChains click failed: %s', e3)
                        
                        try:
                            # Method 4: Click with offset (sometimes helps with overlays)
                            ActionChains(driver).move_to_element_with_offset(sign_out_button, 5, 5).click().perform()
                            logger.info('Clicked sign out button (method 4 - offset click)')
                        except Exception as e4:
                            logger.error('All click methods failed')
                            # Method 5: Try to find a different selector
                            try:
                                # Maybe there's a different selector we can use
                                alt_button = driver.find_element(By.CSS_SELECTOR, "[test-id='sign-out-button']")
                                alt_button.click()
                                logger.info('Clicked sign out button using alternative selector')
                            except:
                                raise e4
            
            # Wait a moment to verify if click worked
            time.sleep(2)
            
            # Check if we're still on the same page (if element still exists, click might not have worked)
            try:
                if driver.find_element(By.ID, "button-click-sign-out").is_displayed():
                    logger.warning('Sign out button still present after click - may not have worked')
            except:
                # Element not found - that's good! Means we probably navigated away
                logger.info('Sign out button no longer present - click successful')
            
            logger.info('Successfully clocked out at: %s', datetime.now())
            
        except Exception as e:
            logger.exception('Failed to locate/click sign-out button: %s', e)
            raise

    except Exception as exc:
        # log and capture diagnostic artifacts
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        logger.exception('Unhandled exception during clock_out: %s', exc)
        if driver:
            try:
                screenshot_path = os.path.join(script_dir, f'clock_out_error_{ts}.png')
                driver.save_screenshot(screenshot_path)
                logger.info('Saved screenshot to %s', screenshot_path)
            except Exception:
                logger.exception('Failed to save screenshot')
            try:
                page_source_path = os.path.join(script_dir, f'clock_out_source_{ts}.html')
                with open(page_source_path, 'w', encoding='utf-8') as f:
                    f.write(driver.page_source)
                logger.info('Saved page source to %s', page_source_path)
            except Exception:
                logger.exception('Failed to save page source')
        # re-raise so callers can see return code if needed
        raise
    finally:
        if driver:
            try:
                driver.quit()
                logger.debug('Driver quit')
            except Exception:
                logger.exception('Error while quitting driver')
    
    # Clean up scheduled task
    # Delete task with new naming pattern
    task_name_prefix = "SesameClockOut_"
    try:
        # Use /query with /v (verbose) to get more details and ensure we get the full task name
        result = subprocess.run(
            ['schtasks', '/query', '/fo', 'LIST'],  # Use LIST format which is easier to parse
            capture_output=True, text=True, encoding='utf-8', errors='ignore'
        )
        logger.debug('schtasks query returned code %s', result.returncode)

        if result.returncode == 0:
            tasks_found = False
            current_task = None
            
            # Parse LIST format
            for line in result.stdout.split('\n'):
                line = line.strip()
                
                # TaskName line in LIST format
                if line.startswith('TaskName:'):
                    current_task = line.split(':', 1)[1].strip()
                    logger.debug('Found task: %s', current_task)
                    
                    # Check if this is our task
                    if current_task and task_name_prefix in current_task:
                        tasks_found = True
                        logger.info('Deleting task: %s', current_task)
                        
                        # Delete the task
                        del_result = subprocess.run(
                            ['schtasks', '/delete', '/tn', current_task, '/f'], 
                            capture_output=True, text=True
                        )
                        
                        if del_result.returncode == 0:
                            logger.info('Successfully deleted task: %s', current_task)
                        else:
                            logger.error('Failed to delete task %s: %s', current_task, del_result.stderr)
            
            if not tasks_found:
                logger.info('No tasks found with prefix: %s', task_name_prefix)
                
                # Alternative: Try using where command to search
                logger.debug('Attempting alternative search method...')
                alt_result = subprocess.run(
                    ['schtasks', '/query', '/fo', 'CSV'],
                    capture_output=True, text=True, encoding='utf-8', errors='ignore'
                )
                if alt_result.returncode == 0:
                    for line in alt_result.stdout.split('\n'):
                        if task_name_prefix in line:
                            logger.debug('Found in CSV: %s', line)
        else:
            logger.error('Failed to query scheduled tasks. Stderr: %s', result.stderr)

    except Exception as e:
        logger.exception('Error cleaning up tasks: %s', e)

if __name__ == "__main__":
    clock_out()