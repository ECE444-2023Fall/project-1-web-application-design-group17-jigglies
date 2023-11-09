import json
from io import BytesIO
from flask import url_for




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
        user_identifier="harrypotter",
        password="testpass1"
    ))

    assert response.status_code == 302
    assert '/' in response.headers['Location']


## ----------------------------- Bilal Ikram - Tests ----------------------------- ##

def test_correct_event_submission(client):
    """Test event submission with all valid event information."""
    
    with client as c:
        # Log in as user1 before trying to create an event
        login_response = c.post('/login', data=dict(
            user_identifier="harrypotter",
            password="testpass1"
        ), follow_redirects=True)
        
        # Ensure that the login was successful
        assert login_response.status_code == 200

        response = c.post('/create_event', data={
            'event_name': 'Unique Test Event',  # Make sure this is unique
            'organization': 'Test Org',
            'date': '2023-11-01',
            'start-time': '12',  # Ensure this is just an hour
            'end-time': '13',    # Ensure this is just an hour
            'location': '25 College Street, Toronto, ON, Canada',
            'room': 'A101',
            'allow_comments': 'Yes',
            'capacity': 50,  # Make sure this is an integer
            'event-information': 'Test Information',
            'tags': json.dumps([{'value': 'tag1'}, {'value': 'tag2'}]),  # Ensure tags are included
            'file-upload': (BytesIO(b'Test image data'), 'test-image.jpg'),
        })

        # Check for the expected redirect response
        assert response.status_code == 302
        assert url_for('event_success') in response.headers['Location']

def test_duplicate_event_name_submission(client):
    """Test event submission with duplicate Event Name"""

    with client as c: 
        login_response = c.post('/login', data=dict(
            user_identifier="harrypotter",  
            password="testpass1"
        ), follow_redirects=True)

        # Ensure that the login was successful
        assert login_response.status_code == 200

        response = client.post('/create_event', data={
            'event_name': 'Duplicate Event Name',
            'event_organization': 'Test Org',
            'date': '2023-11-01',
            'start_time': '12',
            'end_time': '13',
            'location': '25 College Street, Toronto, ON, Canada',
            'room': 'A101',
            'allow_comments': 'Yes',
            'capacity': '50',
            'event_information': 'Test Information',
            'cover_photo': (BytesIO(b'Test image data'), 'test-image.jpg'),
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'An event with the name already exists, please choose another name' in response.data

## ----------------------------- Yousef Al Rawwash - Tests ----------------------------- ##

def test_signup_with_existing_username(client):
    """Test signup with an existing username"""
    # First, signup a user using the client
    client.post('/signup', data=dict(
        username="testuser",
        email="test@utoronto.ca",
        password="password"
    ), follow_redirects=True)
    
    # Attempt to sign up again with the same username
    response = client.post('/signup', data=dict(
        username="testuser",
        email="newtest@utoronto.ca",
        password="password"
    ), follow_redirects=True)
    
    assert b"Username already exists. Please choose another one." in response.data