from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_change_user_profile(browser, client):
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
    assert browser.current_url == 'http://web-app:5000/', "Login was unsuccessful"

    # Navigate to the profile edit page
    edit_profile_link = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, 'Edit Profile')))
    edit_profile_link.click()

    # Update the username
    new_username = 'newusername'
    username_field = browser.find_element(By.NAME, 'username')
    username_field.clear()
    username_field.send_keys(new_username)

    # Update the password
    new_password = 'newpassword123'
    password_field = browser.find_element(By.NAME, 'password')
    password_field.clear()
    password_field.send_keys(new_password)

    # Update the bio
    new_bio = 'Updated bio text'
    bio_input = browser.find_element(By.NAME, 'bio')
    bio_input.clear()
    bio_input.send_keys(new_bio)

    # Submit the form
    save_button = browser.find_element(By.XPATH, "//button[contains(text(), 'Save Changes')]")
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
    assert browser.current_url == 'http://web-app:5000/', "Login was unsuccessful with new credentials"

    # Navigate to the profile page to verify bio update
    profile_link = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, 'Profile')))
    profile_link.click()

    # Check if the bio has been updated
    updated_bio = browser.find_element(By.ID, 'user-bio').text
    assert updated_bio == new_bio, "Bio update was unsuccessful"
