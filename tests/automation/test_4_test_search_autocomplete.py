from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys


def test_4_test_search_autocomplete(browser, client):
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

    # Clear all events off the page by searching for non-existent element
    search_input = browser.find_element(By.ID, "search_query_2")
    search_input.click()
    search_input.send_keys("X" + Keys.RETURN)

    # Verify no events are seen
    event_titles = browser.find_elements(By.ID, "event_name")
    assert len(event_titles) == 0, "An event was seen when none should have been seen"

    # Find the search input using its ID.
    search_input = browser.find_element(By.ID, "search_query_2")

    # Click the search input field.
    search_input.click()

    # Type 'X' into the search field
    search_input.send_keys("X")

    # Verify nothing is seen in the suggestions box drop down
    suggestions_list = browser.find_elements(By.CSS_SELECTOR, "#suggestions_2 ul")
    assert len(suggestions_list) == 0, "There are autocomplete suggestions present."

    # Clear the Search input and send the letter "D"
    search_input.clear()
    search_input.send_keys("D")

    # Verify there is now one element seen in the autocomplete and it is the already existing event
    suggestions_list = browser.find_elements(By.CSS_SELECTOR, "#suggestions_2 ul")
    assert len(suggestions_list) == 1, "There are no autocomplete suggestions present."

    # Verify the correct text is seen in the drop down
    suggestions = suggestions_list[0].find_elements(By.TAG_NAME, "li")
    assert suggestions[0].text == 'Duplicate Event Name', "Incorrect Event Name was found"
    assert len(suggestions) == 1

    # Click the drop-down element and verify it searches
    suggestions[0].click()
    event_titles = browser.find_elements(By.ID, "event_name")
    assert event_titles[0].text == 'Duplicate Event Name', "Incorrect Event Name was found"