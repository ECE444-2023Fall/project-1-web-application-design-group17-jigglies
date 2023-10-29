from pathlib import Path
import pytest
from project.app import app, db, User, EventDB
from io import BytesIO
from datetime import datetime, date, time

TEST_DB = "test.db"

@pytest.fixture
def client():
    BASE_DIR = Path(__file__).resolve().parent.parent
    app.config["TESTING"] = True
    app.config["DATABASE"] = BASE_DIR.joinpath(TEST_DB)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{BASE_DIR.joinpath(TEST_DB)}"

    with app.app_context():
        db.create_all()  # setup
        
        # Add User Entries
        user1 = User(username="harrypotter", email="harry.potter@mail.utoronto.ca", password="testpass1")
        user2 = User(username="ronweasely", email="ron.weasely@mail.utoronto.ca", password="testpass2")
        db.session.add(user1)
        db.session.add(user2)
        

        # Add Event Entry
        event_entry = EventDB(
            event_name='Duplicate Event Name',
            event_organization='UofT',
            date= datetime.strptime('2024-11-11', '%Y-%m-%d').date(),
            start_time=datetime.strptime('9', '%H').time(),
            end_time=datetime.strptime('10', '%H').time(),
            location='123 Happy Street',
            room="A540",
            allow_comments=True,
            capacity=123,
            event_information="This is a test event to avoid duplicate Event Name entries",
            cover_photo=BytesIO(b'Test image data').read()
        )
        db.session.add(event_entry)

        # Commit all changes to DB
        db.session.commit()
        
        yield app.test_client()  # tests run here
        db.drop_all()  # teardown


## ----------------------------- Jason Wang - Tests ----------------------------- ##
def test_unsuccessful_signup_with_non_uoft_email(client):
    """Test unsuccessful signup with a non-UofT email."""
    response = client.post('/signup', data=dict(
        username="testUserNonUofT",
        email="test@gmail.com",
        password="password"
    ), follow_redirects=True)

    assert b"Please sign up with a uoft email." in response.data

def test_successful_signup(client):
    """Test successful signup"""
    response = client.post('/signup', data=dict(
        username="testUser2",
        email="test@utoronto.ca",
        password="password"
    ), follow_redirects=True)

    assert b"Registration successful. Please login" in response.data

## ----------------------------- Taeuk Kang - Tests ----------------------------- ##
def test_incorrect_login(client):
    """Test login with an incorrect email/password."""
    response = client.post('/login', data=dict(
        username="falseusername",
        email="false.user@mail.utoronto.ca",
        password="wrongpass"
    ), follow_redirects=True)

    assert b"Login Unsuccessful. Check your details and try again." in response.data

def test_correct_login(client):
    """Test login with a correct email/password."""
    response = client.post('/login', data=dict(
        username="harrypotter",
        email="harry.potter@mail.utoronto.ca",
        password="testpass1"
    ), follow_redirects=True)

    assert b"Welcome" in response.data


## ----------------------------- Bilal Ikram - Tests ----------------------------- ##

def test_correct_event_submission(client):
    """Test event submission with all valid event information."""
    response = client.post('/create_event', data={
        'event_name': 'Test Event',
        'organization': 'Test Org',
        'date': '2023-11-01',
        'start-time': '12',
        'end-time': '13',
        'location': 'Test Location',
        'room': 'A101',
        'allow-comments': 'yes',
        'capacity': '50',
        'event-information': 'Test Information',
        'file-upload': (BytesIO(b'Test image data'), 'test-image.jpg'),
    })

    assert response.status_code == 302
    assert b'event_success' in response.data

    event = EventDB.query.filter_by(event_name='Test Event').first()
    assert event is not None
    assert event.event_organization == 'Test Org'

def test_duplicate_event_name_submission(client):
    """Test event submission with duplicate Event Name"""
    response = client.post('/create_event', data={
        'event_name': 'Duplicate Event Name',
        'organization': 'Test Org',
        'date': '2023-11-01',
        'start-time': '12',
        'end-time': '13',
        'location': 'Test Location',
        'room': 'A101',
        'allow-comments': 'yes',
        'capacity': '50',
        'event-information': 'Test Information',
        'file-upload': (BytesIO(b'Test image data'), 'test-image.jpg'),
    })

    assert b'An event with the name already exists, please choose another name' in response.data