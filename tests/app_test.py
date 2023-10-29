from pathlib import Path
import pytest
from project.app import app, db, Event
from your_flask_app.forms import CreateEventForm
from datetime import datetime

TEST_DB = "test.db"

@pytest.fixture
def client():
    BASE_DIR = Path(__file__).resolve().parent.parent
    app.config["TESTING"] = True
    app.config["DATABASE"] = BASE_DIR.joinpath(TEST_DB)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{BASE_DIR.joinpath(TEST_DB)}"

    with app.app_context():
        db.create_all()  # setup
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

# TODO 
def test_incorrect_login(client):
    pass 

# TODO 
def test_correct_login(client):
    pass 

## ----------------------------- Alexander Hwang - Tests ----------------------------- ##

def test_create_event(client):
    # Test creating a new event
    form_data = {
        'name': 'Test Event',
        'organization': 'Test Org',
        'date': datetime(2023, 10, 28, 18, 0)
    }
    form = CreateEventForm(data=form_data)
    assert form.validate()
    response = client.post('/create_event', data=form_data, follow_redirects=True)
    assert response.status_code == 200
    event = Event.query.filter_by(name='Test Event').first()
    assert event is not None
    assert event.organizer == 'Test Org'

def test_create_event_existing_name(client):
    # Test creating an event with an existing name
    event = Event(name='Existing Event', organizer='Existing Org', time=datetime.now())
    db.session.add(event)
    db.session.commit()

    form_data = {
        'name': 'Existing Event',
        'organization': 'New Org',
        'date': datetime(2023, 10, 28, 18, 0)
    }
    form = CreateEventForm(data=form_data)
    assert form.validate()
    response = client.post('/create_event', data=form_data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Event name already exists. Please choose another one.' in response.data