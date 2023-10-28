##Test cases written by Yousef Al Rawwash

def test_signup_with_existing_username(client):
    """Test signup with an existing username"""
    user = User(username="testuser", email="test@utoronto.ca", password=generate_password_hash("password"))
    db.session.add(user)
    db.session.commit()
    
    response = client.post('/signup', data=dict(
        username="testuser",
        email="newtest@utoronto.ca",
        password="password"
    ), follow_redirects=True)
    
    assert b"Username already exists. Please choose another one." in response.data

def test_create_event(client):
    """Test event creation"""
    response = client.post('/create_event', data=dict(
        name="Sample Event",
        organization="Test Org",
        date="10-27-23 19:00"
    ), follow_redirects=True)
    
    assert b"Succesfully Created New Event" in response.data

    # Check if the event is actually added to the database
    event = Event.query.filter_by(name="Sample Event").first()
    assert event is not None