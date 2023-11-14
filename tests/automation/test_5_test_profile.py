from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_5_test_profile(browser, client):
    # Start the browser and open the login page
    browser.get('http://web-app:5000/login')
    assert "login" in browser.current_url

    # Find form elements for login
    username_input = browser.find_element(By.NAME, 'user_identifier')
    password_input = browser.find_element(By.NAME, 'password')
    submit_button = browser.find_element(By.XPATH, "//button[contains(text(), 'Sign in')]")

    # Login with credentials
    username_input.send_keys('harrypotter')
    password_input.send_keys('testpass1')
    submit_button.click()

    # Verify the login was successful
    assert browser.current_url == 'http://web-app:5000/', f'Login was unsuccessful, url was expected to be http://web-app:5000/ but is actually {browser.current_url}'

    # Navigate to the profile edit page using the URL
    edit_profile_url = "http://web-app:5000/edit-profile"
    browser.get(edit_profile_url)

    # Update the username
    new_username = 'newusername'
    username_input = browser.find_element(By.ID, 'username')
    username_input.clear()
    username_input.send_keys(new_username)

    # Update the password
    new_password = 'newpassword123'
    password_input = browser.find_element(By.ID, 'password')
    password_input.clear()
    password_input.send_keys(new_password)

    # Update the bio
    new_bio = 'Updated bio text'
    bio_input = browser.find_element(By.ID, 'bio')
    bio_input.clear()
    bio_input.send_keys(new_bio)

    # Submit the form
    save_button = browser.find_element(By.XPATH, "//input[@value='Update Profile']")
    save_button.click()

    # Log out
    logout_link = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, 'Logout')))
    logout_link.click()

    # Log in with the new credentials
    browser.get('http://web-app:5000/login')
    username_input = browser.find_element(By.NAME, 'user_identifier')
    password_input = browser.find_element(By.NAME, 'password')
    submit_button = browser.find_element(By.XPATH, "//button[contains(text(), 'Sign in')]")

    username_input.send_keys(new_username)
    password_input.send_keys(new_password)
    submit_button.click()

    # Verify the login was successful with new credentials
    assert browser.current_url == 'http://web-app:5000/', f'Login was unsuccessful, url was expected to be http://web-app:5000/ but is actually {browser.current_url}'

    # Navigate to the profile page to verify bio update
    profile_link = "http://web-app:5000/edit-profile"
    browser.get(edit_profile_url)

    # Check if the bio has been updated
    updated_bio = browser.find_element(By.ID, 'user-bio').text
    assert updated_bio == new_bio, "Bio update was unsuccessful"
