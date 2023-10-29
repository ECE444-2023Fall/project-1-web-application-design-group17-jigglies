from pathlib import Path
import pytest
<<<<<<< HEAD
from project.app import app, db, User
=======
from project.app import app, db, Event
from your_flask_app.forms import CreateEventForm
from datetime import datetime
>>>>>>> 02dfdfad59b05dce826043ac55d5addfcf99e599

TEST_DB = "test.db"

@pytest.fixture
def client():
    BASE_DIR = Path(__file__).resolve().parent.parent
    app.config["TESTING"] = True
    app.config["DATABASE"] = BASE_DIR.joinpath(TEST_DB)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{BASE_DIR.joinpath(TEST_DB)}"

    with app.app_context():
        db.create_all()  # setup
        
        # Populate test db.
        user1 = User(username="harrypotter", email="harry.potter@mail.utoronto.ca", password="testpass1")
        user2 = User(username="ronweasely", email="ron.weasely@mail.utoronto.ca", password="testpass2")
        db.session.add(user1)
        db.session.add(user2)
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
