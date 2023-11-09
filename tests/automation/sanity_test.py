import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from conftest import client


# Setup a fixture for the browser
@pytest.fixture(scope="module")
def browser():


    # Define Selenium remote URL
    selenium_remote_url = "http://selenium-chrome:4444/wd/hub"

    # Set Chrome options
    chrome_options = Options()
    chrome_options.headless = True  # Run in headless mode
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1280x1696')

    # Initialize the Remote WebDriver with the options we've set
    driver = webdriver.Remote(
        command_executor=selenium_remote_url,
        options=chrome_options  # Use 'options' instead of 'desired_capabilities'
    )
    yield driver
    driver.quit()


def test_login_user(browser, client):
    # Start the browser and open the login page
    browser.get('http://web-app:5000/login')

    assert "login" in browser.current_url

    # Find form elements
    username_input = browser.find_element(By.NAME, 'user_identifier')
    password_input = browser.find_element(By.NAME, 'password')
    submit_button = browser.find_element(By.XPATH, "//button[contains(text(), 'Login')]")

    # Input test credentials (replace with actual test account credentials)
    username_input.send_keys('harrypotter')
    password_input.send_keys('testpass1')
    submit_button.click()

    # Verify the login was successful
    assert browser.current_url == 'http://web-app:5000/', f'Login was unsuccessful, url was expected to be http://web-app:5000/ but is actually {browser.current_url}'

    # Click the user-profile the button by its ID
    user_menu_button = browser.find_element(By.ID, "user-menu-button")
    user_menu_button.click()

    # Retrieve the email that is displayed
    email = browser.find_element(By.XPATH, "//*[@id='user-dropdown']//span[contains(@class, 'text-gray-500')]").text

    # Retrieve the username that is displayed
    username = browser.find_element(By.XPATH, "//*[@id='user-dropdown']//span[contains(@class, 'text-gray-900')]").text

    # Verify that the email text is as expected
    assert email == 'harry.potter@mail.utoronto.ca', f"Expected email to be 'harry.potter@mail.utoronto.ca', but got {email}"

    # Verify that the username text is as expected
    assert username == 'harrypotter', f"Expected username to be 'harrypotter', but got {username}"

