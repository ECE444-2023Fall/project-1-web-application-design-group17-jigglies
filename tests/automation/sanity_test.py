import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time


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
    driver.save_screenshot('error.png')
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

def test_create_event(browser, client):
    # Start the browser and open the login page
    browser.get('http://web-app:5000/login')

    assert "login" in browser.current_url

    # Find form elements
    username_input = browser.find_element(By.NAME, 'user_identifier')
    password_input = browser.find_element(By.NAME, 'password')
    submit_button = browser.find_element(By.XPATH, "//button[contains(text(), 'Login')]")

    # Login with credentials
    username_input.send_keys('harrypotter')
    password_input.send_keys('testpass1')
    submit_button.click()

    # Verify the login was successful
    assert browser.current_url == 'http://web-app:5000/', f'Login was unsuccessful, url was expected to be http://web-app:5000/ but is actually {browser.current_url}'

    # Go to Search Page
    search_link = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, 'Search')))
    search_link.click()

    browser.save_screenshot('screenshot_after_submission.png')

    # Verify the one already created event is seen
    event_titles = WebDriverWait(browser, 10).until(EC.presence_of_all_elements_located((By.ID, "event_name")))
    assert len(event_titles) == 1, "Less or more than one event titles found on the page."

    # Verify that the titles are displayed (non-empty text)
    assert event_titles[0].text == 'Duplicate Event Name', "Incorrect Event Name was found"

    # Wait for the 'Create Event' link to be present and clickable
    create_event_link = WebDriverWait(browser, 10).until(
        EC.element_to_be_clickable((By.LINK_TEXT, 'Create Event'))
    )

    # Click the 'Create Event' link
    create_event_link.click()

    # Verify the browser is now on the 'create_event' page
    assert '/create_event' in browser.current_url, f"Browser did not navigate to create_event page, current URL is {browser.current_url}"

    # Fill out the Event Name
    event_name_input = browser.find_element(By.ID, "event_name")
    event_name_input.send_keys("Sample Event Name")

    # Fill out the Organization
    organization_input = browser.find_element(By.ID, "organization")
    organization_input.send_keys("Sample Organization")

    # Fill out the Date
    date_input = browser.find_element(By.ID, "date")
    date_to_set = '2024-11-11'
    browser.execute_script(f"document.getElementById('date').value = '{date_to_set}';")

    # Select Start Time
    start_time_select = browser.find_element(By.ID, "start-time")
    start_time_select.click()
    start_time_select.find_element(By.XPATH, "./option[@value='13']").click() 

    # Select End Time
    end_time_select = browser.find_element(By.ID, "end-time")
    end_time_select.click()
    end_time_select.find_element(By.XPATH, "./option[@value='15']").click()  

    # Fill out the Address
    address_input = browser.find_element(By.ID, "location")
    address_input.send_keys('25 College Street, Toronto, ON, Canada')

    # Fill out the Room
    room_input = browser.find_element(By.ID, "room")
    room_input.send_keys("Room 101")

    # Select Comments option
    allow_comments_select = browser.find_element(By.ID, "allow_comments")
    allow_comments_select.click()
    allow_comments_select.find_element(By.XPATH, "./option[@value='Yes']").click()  

    # Fill out the Capacity
    capacity_input = browser.find_element(By.ID, "capacity")
    capacity_input.send_keys("100")  

    # Fill out the Event Information
    event_info_textarea = browser.find_element(By.ID, "event-information")
    event_info_textarea.send_keys("This is the event information.")

    # Click the Submit button
    submit_button = browser.find_element(By.XPATH, "//button[contains(text(), 'Pop Event!')]")
    submit_button.click()

    # Verify the browser is now on the 'create_event' page
    assert '/event_success' in browser.current_url, f"Browser did not navigate to create_event page, current URL is {browser.current_url}"

    # Click the button to go back to the homepage
    # Wait for the link to be clickable
    return_home_link = WebDriverWait(browser, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Click here')]"))
    )

    # Click the 'Click here' link
    return_home_link.click()

    # Verify the two events are now seen
    event_titles = browser.find_elements(By.ID, "event_name")
    assert len(event_titles) == 2, "Less or more than two event titles found on the page."

    # Verify that the titles are displayed (non-empty text)
    assert event_titles[0].text == 'Duplicate Event Name', "Incorrect Event Name was found"
    assert event_titles[1].text == 'Sample Event Name', "Incorrect Event Name was found"
