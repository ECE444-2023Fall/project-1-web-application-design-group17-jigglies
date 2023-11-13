from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys


def test_3_test_search(browser, client):
    # Start the browser and open the login page
    browser.get('http://web-app:5000/login')

    assert "login" in browser.current_url

    # Find form elements
    username_input = browser.find_element(By.NAME, 'user_identifier')
    password_input = browser.find_element(By.NAME, 'password')
    submit_button = browser.find_element(By.XPATH, "//button[contains(text(), 'Sign in')]")

    # Login with credentials
    username_input.send_keys('harrypotter')
    password_input.send_keys('testpass1')
    submit_button.click()

    # Verify the login was successful
    assert browser.current_url == 'http://web-app:5000/', f'Login was unsuccessful, url was expected to be http://web-app:5000/ but is actually {browser.current_url}'

    # Go to Search Page
    search_link = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, 'Explore')))
    search_link.click()

    # Verify the one already created event is seen
    event_titles = WebDriverWait(browser, 10).until(EC.presence_of_all_elements_located((By.ID, "event_name")))
    assert len(event_titles) == 1, "Less or more than one event titles found on the page."

    # Verify that the titles are displayed (non-empty text)
    assert event_titles[0].text == 'Duplicate Event Name', "Incorrect Event Name was found"

    # Find the search input using its ID.
    search_input = browser.find_element(By.ID, "search_query_2")

    # Click the search input field.
    search_input.click()

    # Type 'X' into the search field and press Enter.
    search_input.send_keys("X" + Keys.RETURN)

    # Verify no events are seen
    event_titles = browser.find_elements(By.ID, "event_name")
    assert len(event_titles) == 0, "An event was seen when none should have been seen"

    # Click the search input field.
    search_input = browser.find_element(By.ID, "search_query_2")
    search_input.click()

    # Type 'Duplicate' into the search field and press Enter.
    search_input.send_keys("Duplicate" + Keys.RETURN)

    # Verify the one already created event is seen
    event_titles = WebDriverWait(browser, 10).until(EC.presence_of_all_elements_located((By.ID, "event_name")))
    assert len(event_titles) == 1, "Less or more than one event titles found on the page."

    # Verify that the titles are displayed (non-empty text)
    assert event_titles[0].text == 'Duplicate Event Name', "Incorrect Event Name was found"