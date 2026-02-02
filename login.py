def login(driver):
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