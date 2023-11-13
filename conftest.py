import pytest

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from pathlib import Path
from app import app, db, User, Event
from werkzeug.security import generate_password_hash
from io import BytesIO
from datetime import datetime


TEST_DB = "test.db"

@pytest.fixture
def client():
    BASE_DIR = Path(__file__).resolve().parent.parent
    app.config["TESTING"] = True
    app.config["DATABASE"] = BASE_DIR.joinpath(TEST_DB)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{BASE_DIR.joinpath(TEST_DB)}"
    


    with app.app_context():

        db.drop_all()
        db.create_all()  # setup
        
        # Add User Entries
        user1 = User(username="harrypotter", email="harry.potter@mail.utoronto.ca", password=generate_password_hash("testpass1", method='scrypt'))
        user2 = User(username="ronweasely", email="ron.weasely@mail.utoronto.ca", password=generate_password_hash("testpass1", method='scrypt'))
        db.session.add(user1)
        db.session.add(user2)

        db.session.commit()
        

        # Add Event Entry
        event_entry = Event(
            event_name='Duplicate Event Name',
            event_organization='UofT',
            created_by=user1.id,
            date= datetime.strptime('2024-11-11', '%Y-%m-%d').date(),
            start_time=datetime.strptime('9', '%H').time(),
            end_time=datetime.strptime('10', '%H').time(),
            location='25 College Street, Toronto, ON, Canada',
            room="A540",
            allow_comments=True,
            capacity=123,
            event_information="This is a test event to avoid duplicate Event Name entries",
            cover_photo=BytesIO(b'Test image data').read()
        )
        db.session.add(event_entry)

        # Commit all changes to DB
        db.session.commit()
        
        yield app.test_client() # tests run here
        db.drop_all()
        db.create_all()  # teardown
    

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

