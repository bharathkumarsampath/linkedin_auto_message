from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, NoSuchElementException,ElementClickInterceptedException, WebDriverException
import time,os,json

# Replace these with your LinkedIn credentials
LINKEDIN_USERNAME = '<enter username>'
LINKEDIN_PASSWORD = '<enter password>'

# Setup Chrome WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# Path to the JSON file
MESSAGED_PROFILES_FILE = 'messaged_profiles.json'

# Load messaged profiles
def load_messaged_profiles():
    if os.path.exists(MESSAGED_PROFILES_FILE):
        with open(MESSAGED_PROFILES_FILE, 'r') as file:
            return json.load(file)
    return []

# Save messaged profiles
def save_messaged_profiles(profiles):
    with open(MESSAGED_PROFILES_FILE, 'w') as file:
        json.dump(profiles, file)

# Initialize the list of messaged profiles
messaged_profiles = load_messaged_profiles()

def highlight(element):
    """Highlights (blinks) a Selenium Webdriver element"""
    driver = element._parent
    def apply_style(s):
        driver.execute_script("arguments[0].setAttribute('style', arguments[1]);", element, s)
    original_style = element.get_attribute('style')
    apply_style("border: 3px solid red;")
    time.sleep(1)
    apply_style(original_style)

def safe_find_element(driver, by, value, retries=3):
    for i in range(retries):
        try:
            element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((by, value)))
            return element
        except StaleElementReferenceException:
            print(f"StaleElementReferenceException occurred, retrying {i + 1}/{retries}")
            if i == retries - 1:
                raise
        except NoSuchElementException:
            print(f"NoSuchElementException occurred, element not found: {by} {value}")
            return None
        
def close_and_return():
    driver.close()  # Close the current tab
    driver.switch_to.window(original_window)

def enter_credentials():
    # Navigate to LinkedIn login page
    print("Navigating to LinkedIn login page")
    driver.get('https://www.linkedin.com/login')

    # Enter username
    print("Entering username")
    username_field = driver.find_element(By.ID, 'username')
    username_field.send_keys(LINKEDIN_USERNAME)

    # Enter password
    print("Entering password")
    password_field = driver.find_element(By.ID, 'password')
    password_field.send_keys(LINKEDIN_PASSWORD)
    password_field.send_keys(Keys.RETURN)

def wait_for_2fa_verification(html_element, msg1, msg2, msg3):
    # Check for CAPTCHA or 2FA prompt
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, html_element))
    )
    print(msg1)
    # Wait for the user to solve the CAPTCHA manually
    while True:
        try:
            # Check if the CAPTCHA has been solved and the user is redirected
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="global-nav"]/div'))
            )
            print(msg2)
            break
        except TimeoutException:
            print(msg3)
            time.sleep(5)

def wait_for_verification():
    try:
        wait_for_2fa_verification("home_children_button",
                                    "CAPTCHA detected. Please solve it manually.",
                                    "CAPTCHA solved and logged in.",
                                    "Waiting for CAPTCHA to be solved...")
    except TimeoutException:
        print("No CAPTCHA detected, checking for 2FA prompt...")
        try:
            wait_for_2fa_verification("try-another-way",
                                    "2FA prompt detected. Click 'Try another way'.",
                                    "2FA completed and logged in.",
                                    "Waiting for 2FA code entry...")
        except TimeoutException:
            print("Opted for OTP entry, waiting for OTP verification...")
            wait_for_2fa_verification("input__phone_verification_pin",
                                    "OTP input field detected. Please enter the code manually.",
                                    "OTP completed and logged in.",
                                    "Waiting for OTP code entry...")
        
def login_to_linkedin():
    try:
        enter_credentials()
        wait_for_verification()
    except Exception as e:
        print(f"An error occurred during login: {e}")

def get_notifications():
    notification_xpath = "//article[contains(@class, 'nt-card')]"
     # Get the list of liked notifications
    print("Retrieving  notifications...")
    try:
        notifications = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.XPATH, notification_xpath))
        )
        return notifications
    except TimeoutException:
        print("Timeout while waiting for liked notifications. Printing page source for debugging:")
        with open("page_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("Page source saved to page_source.html")
        raise

try:

     # Navigate to LinkedIn login page
    login_to_linkedin()

    driver.get('https://www.linkedin.com/notifications/')

    # Wait for notifications page to load
    time.sleep(5)

    notifications = get_notifications()

    # Store the original window handle
    original_window = driver.current_window_handle

    # Process each notification
    for notification in notifications:
        try:
            if 'liked your post' in notification.text or 'loved your post' in notification.text:
                
                print("Processing a liked notification...")
                highlight(notification)

                # Click on the profile link within the notification
                profile_link = notification.find_element(By.XPATH, ".//a[contains(@href, '/in/')]")
                profile_url = profile_link.get_attribute('href')
                print(f"Profile URL: {profile_url}")

                # Check if this profile has already been messaged
                if profile_url in messaged_profiles:
                    print(f"Already messaged: {profile_url}")
                    continue

                highlight(profile_link)
                 # Open the profile in a new tab
                print("Opening profile in a new tab")
                driver.execute_script("window.open(arguments[0], '_blank');", profile_url)
                
                # Switch to the new tab
                driver.switch_to.window(driver.window_handles[-1])
                time.sleep(5)  # Wait for the profile page to load


                # Locate the user profile section uniquely (adjust the XPath according to your page structure)
                profile_section_xpath = "//div[@class='ph5 pb5']"  # Adjust this based on your actual structure
                profile_section = safe_find_element(driver,By.XPATH, profile_section_xpath)
                highlight(profile_section)

                # Extract the name of the person
                name_xpath = ".//h1[@class='text-heading-xlarge inline t-24 v-align-middle break-words']"
                name_element = profile_section.find_element(By.XPATH, name_xpath)
                highlight(name_element)
                person_name = name_element.text
                print(f"Person's name: {person_name}")

                # Within the profile section, find the specific message button
                message_button_xpath = ".//button[contains(@class, 'artdeco-button--primary') and contains(@aria-label, 'Message')]"
                message_button = profile_section.find_element(By.XPATH, message_button_xpath)
                highlight(message_button)
                print("Message button found")


                # Click on the message button
                try:
                    print("Clicking on the message button...")
                    message_button.click()
                    time.sleep(5)  # Wait for message window to load

                    # Check if the message box appears
                    message_box_xpath = "//div[contains(@class, 'msg-overlay-conversation-bubble')]"
                    try:
                        message_box = safe_find_element(driver,By.XPATH, message_box_xpath)
                        highlight(message_box)
                        print("Message box appeared.")
                    except TimeoutException:
                        print("Message box did not appear, skipping this profile.")
                        close_and_return()
                        continue
                except (ElementClickInterceptedException, StaleElementReferenceException, WebDriverException) as e:
                    print(f"ElementClickInterceptedException while clicking message button: {e}")
                    close_and_return()
                    continue
                except Exception as e:
                    print(f"Exception while clicking message button: {e}")
                    close_and_return()
                    continue

                # Enter the message
                print("Entering the thank you message...")
                message_box_xpath = "//div[contains(@class, 'msg-form__contenteditable')]"
                message_box = safe_find_element(driver,By.XPATH, message_box_xpath)
                highlight(message_box)
                message_box.clear()
                #custom_message = f"Hi {person_name}, \n\nThank you for liking and loving my post!"
                custom_message = f"Hi {person_name}, \n\nThank you for the wonderful post and am interested in learning more!"
                message_box.send_keys(custom_message)
                time.sleep(2)

                # Click the send button
                send_button_xpath = "//button[contains(@class, 'msg-form__send-button')]"
                send_button = safe_find_element(driver,By.XPATH, send_button_xpath)
                highlight(send_button)
                #send_button.click()
                print("Message sent.")
                time.sleep(2)  # Wait for message to send

                # Add the profile to the list of messaged profiles
                messaged_profiles.append(profile_url)
                save_messaged_profiles(messaged_profiles)
                close_and_return()
                
        
        except StaleElementReferenceException as e:
            print(f"Stale element reference exception occurred: {e}")
            # Attempt to re-process the notification
            print("Re-trying to process the notification...")
            time.sleep(600)

        except Exception as e:
            print(f"An error occurred while processing a notification: {e}")
            # Go back to notifications page in case of an error
            time.sleep(600)


finally:
    # Close the browser window
    # Keep the browser open
    print("Script completed. Browser will remain open.")
    driver.quit()  # Keep the browser open for 10 minutes to inspect manually
