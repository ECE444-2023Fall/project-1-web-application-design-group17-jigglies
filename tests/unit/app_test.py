import json
from app import app, db, User, Event, Rsvp, Comment, Like
from io import BytesIO
from flask import url_for

## ----------------------------- Jason Wang - Tests ----------------------------- ##
def test_unsuccessful_signup_with_non_uoft_email(client):
    """Test unsuccessful signup with a non-UofT email."""
    response = client.post('/signup', data=dict(
        username="testUserNonUofT",
        email="test@gmail.com",
        password="Password1!"
    ), follow_redirects=True)
    assert b"Please sign up with a uoft email." in response.data

def test_successful_signup(client):
    """Test successful signup"""
    # Set up the session to include a mocked verification code
    with client.session_transaction() as sess:
        sess['verification_codes'] = {'test@utoronto.ca': '123456'}

    # Send the POST request with the verification code
    response = client.post('/signup', data={
        'username': "testUser2",
        'email': "test@utoronto.ca",
        'password': "Password1!",
        'verificationCode': "123456"  # Correct mock verification code
    }, follow_redirects=True)

    # Check the response for the successful registration message
    assert b"Registration successful. Please login" in response.data

## ----------------------------- Taeuk Kang - Tests ----------------------------- ##
def test_incorrect_login(client):
    """Test login with an incorrect email/password."""
    login_response = client.post('/login', data=dict(
            user_identifier="falseusername",
            password="wrongpass"
    ), follow_redirects=True)
    assert b"Login Unsuccessful. Check your details and try again." in login_response.data

def test_correct_login(client):
    """Test login with a correct email/password."""
    login_response = client.post('/login', data=dict(
            user_identifier="harrypotter",
            password="testpass1"
    ), follow_redirects=True)
    assert login_response.status_code == 200
    
def test_rsvp_event(client):
    """Test RSVP'ing for an event."""
    login_response = client.post('/login', data=dict(
            user_identifier="harrypotter",
            password="testpass1"
    ), follow_redirects=True)
    
    assert login_response.status_code == 200
    
    user1 = User.query.filter_by(username="harrypotter").first()
    event1 = Event.query.filter_by(event_name='Duplicate Event Name').first()
    
    # Test RSVP'ing for an event.
    rsvp_resp = client.post(f"/rsvp_event/{event1.id}")
    data = rsvp_resp.get_json()
    assert rsvp_resp.status_code == 200
    assert data['rsvp_count'] == 1
    assert data['user_has_rsvp'] is True
    
    # Check DB if it's populated with new RSVP entry.
    rsvp = Rsvp.query.filter_by(author=user1.id, event_id=event1.id).first()
    assert rsvp is not None
    
    # Test unRSVP'ing for an event.
    rsvp_resp = client.post(f"/rsvp_event/{event1.id}")
    data = rsvp_resp.get_json()
    assert rsvp_resp.status_code == 200
    assert data['rsvp_count'] == 0
    assert data['user_has_rsvp'] is False
    
    rsvp = Rsvp.query.filter_by(author=user1.id, event_id=event1.id).first()
    assert rsvp is None
    
def test_like_event(client):
    """Test liking/unliking an event."""
    login_response = client.post('/login', data=dict(
            user_identifier="harrypotter",
            password="testpass1"
    ), follow_redirects=True)
    
    assert login_response.status_code == 200
    
    user1 = User.query.filter_by(username="harrypotter").first()
    event1 = Event.query.filter_by(event_name='Duplicate Event Name').first()
    
    # Test liking an event.
    like_resp = client.post(f"/like_event/{event1.id}")
    data = like_resp.get_json()
    assert like_resp.status_code == 200
    assert data['like_count'] == 1
    assert data['user_has_liked'] is True
    
    like = Like.query.filter_by(author=user1.id, event_id=event1.id).first()
    assert like is not None
    
    # Test unliking an event.
    like_resp = client.post(f"/like_event/{event1.id}")
    data = like_resp.get_json()
    assert like_resp.status_code == 200
    assert data['like_count'] == 0
    assert data['user_has_liked'] is False
    
    like = Like.query.filter_by(author=user1.id, event_id=event1.id).first()
    assert like is None
    
def test_comment(client):
    """Test commenting on an event."""
    login_response = client.post('/login', data=dict(
            user_identifier="harrypotter",
            password="testpass1"
    ), follow_redirects=True)
    
    assert login_response.status_code == 200
    
    user1 = User.query.filter_by(username="harrypotter").first()
    event1 = Event.query.filter_by(event_name='Duplicate Event Name').first()
    
    # Test commenting on an event.
    comment_data = json.dumps({"comment": "Test comment!"})
    headers = {
        'Content-Type': 'application/json',
    }
    comment_resp = client.post(f'/create_comment/{event1.id}', data=comment_data, headers=headers)
    data = comment_resp.get_json()
    
    assert comment_resp.status_code == 200
    assert data['comment']['text'] == "Test comment!"
    assert data['comment']['author'] == user1.username
    
    # Check if DB is populated with new comment.
    comment = Comment.query.filter_by(event_id=event1.id, author=user1.id).first()
    assert comment is not None
    assert comment.text == "Test comment!"
    

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


# Test the search function
def test_search_with_query(client):
    with client as c: 
        login_response = c.post('/login', data=dict(
            user_identifier="harrypotter",  
            password="testpass1"
        ), follow_redirects=True)

        # Ensure that the login was successful
        assert login_response.status_code == 200

        # Perform a search query
        response = c.get('/search?search_query=Duplicate')
        data = response.get_json()

        assert response.status_code == 200
        assert b"Search Results: Duplicate" in response.data
        assert b"Duplicate Event Name" in response.data

def test_search_no_query(client):
    with client as c: 
        login_response = c.post('/login', data=dict(
            user_identifier="harrypotter",  
            password="testpass1"
        ), follow_redirects=True)

        # Ensure that the login was successful
        assert login_response.status_code == 200

        # Perform a search without a query
        response = c.get('/search')

        assert response.status_code == 200
        assert b"Explore all events:" in response.data

## ----------------------------- Yousef Al Rawwash - Tests ----------------------------- ##

def test_signup_with_existing_username(client):
    """Test signup with an existing username"""
    
    # Attempt to sign up again with the same username
    response = client.post('/signup', data=dict(
        username="harrypotter",
        email="newtest@utoronto.ca",
        password="Password",
        verificationCode="0000"
    ), follow_redirects=True)
    
    assert b"Username already exists. Please choose another one." in response.data