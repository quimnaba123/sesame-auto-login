import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

def clock_out():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in background
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://app.sesametime.com")
    
    """Check if user is logged in by looking for logged-in indicators"""
    login_needed = True
    # Try multiple indicators of being logged in
    indicators = [
        (By.CSS_SELECTOR, "[test-id='el-768782d1']"),  # Clock in button
        (By.CSS_SELECTOR, "[test-id='button-click-sign-out']"),  # Clock out button
        (By.CSS_SELECTOR, ".dashboard, .user-profile"),  # Dashboard elements
        (By.CSS_SELECTOR, "button[data-testid='user-menu']"),  # User menu
        (By.XPATH, "//*[contains(text(), 'Welcome') or contains(text(), 'My Portal')]")
    ]
    
    for by, selector in indicators:
        element = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((by, selector))
        )
        if element.is_displayed():
            login_needed = False
            break

    if login_needed:
        login.login(driver)

    clock_out_button = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[test-id='button-click-sign-out']"))
    )
    clock_out_button.click()
    
    print(f"Successfully clocked out at: {datetime.now()}")
    
    # Clean up scheduled task
    if os.name == 'nt':
        import subprocess
        subprocess.run(['schtasks', '/delete', '/tn', 'SesametimeClockOut', '/f'])
        
    except Exception as e:
        print(f"Clock-out failed: {e}")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    clock_out()