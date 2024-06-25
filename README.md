# LinkedIn Auto-Messaging Bot

This Python script automates the process of messaging LinkedIn profiles who have interacted with your posts (liked or reacted). The script logs into LinkedIn, navigates to notifications, and sends a thank-you message to those profiles, ensuring each profile is only messaged once.

## Features

- **Automatic Login**: Logs into LinkedIn using provided credentials.
- **2FA & CAPTCHA Handling**: Waits for manual CAPTCHA or 2FA code entry.
- **Profile Messaging**: Sends a custom message to profiles who liked or reacted to your posts.
- **Duplicate Handling**: Ensures each profile is messaged only once by maintaining a list of messaged profiles.
- **Error Handling**: Handles common Selenium exceptions to ensure robust operation.

## Prerequisites

- Python 3.x
- `selenium` library
- `webdriver_manager` library

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/linkedin-auto-messaging-bot.git
   cd linkedin-auto-messaging-bot
   ```

2. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

   The `requirements.txt` file should contain:

   ```
   selenium
   webdriver_manager
   ```

## Configuration

1. **Set LinkedIn Credentials**

   Replace `<enter username>` and `<enter password>` with your LinkedIn username and password in the script.

   ```python
   LINKEDIN_USERNAME = '<enter username>'
   LINKEDIN_PASSWORD = '<enter password>'
   ```

2. **Create JSON File for Messaged Profiles**

   Create an empty JSON file named `messaged_profiles.json` in the script directory.

   ```bash
   echo "[]" > messaged_profiles.json
   ```

## Usage

Run the script:

```bash
python linkedin_auto_messaging_bot.py
```

## Script Overview

### Imports

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, NoSuchElementException, ElementClickInterceptedException, WebDriverException
import time, os, json
```

### Configuration and Setup

Replace the placeholders with your LinkedIn credentials. Setup Chrome WebDriver using `webdriver_manager`.

### Functions

- **`load_messaged_profiles()`**: Loads profiles from `messaged_profiles.json`.
- **`save_messaged_profiles(profiles)`**: Saves profiles to `messaged_profiles.json`.
- **`highlight(element)`**: Highlights a Selenium WebDriver element.
- **`safe_find_element(driver, by, value, retries=3)`**: Safely finds an element, handling common exceptions.
- **`close_and_return()`**: Closes the current tab and returns to the original window.
- **`enter_credentials()`**: Enters LinkedIn credentials and logs in.
- **`wait_for_2fa_verification(html_element, msg1, msg2, msg3)`**: Waits for 2FA or CAPTCHA verification.
- **`wait_for_verification()`**: Handles CAPTCHA and 2FA verification.
- **`login_to_linkedin()`**: Logs into LinkedIn.
- **`get_notifications()`**: Retrieves notifications from LinkedIn.

### Main Script

Logs into LinkedIn, navigates to notifications, and processes each notification to send a message to profiles who liked or reacted to your posts.

### Example Run

1. Logs into LinkedIn.
2. Navigates to the notifications page.
3. Processes each notification.
4. Sends a thank-you message to profiles.
5. Ensures each profile is only messaged once.

### Error Handling

Handles exceptions like `StaleElementReferenceException`, `TimeoutException`, and more to ensure the script runs smoothly.

## Contributing

Feel free to fork this repository, make improvements, and submit pull requests. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License.
