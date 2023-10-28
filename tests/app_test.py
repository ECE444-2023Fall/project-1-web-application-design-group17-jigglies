##Test cases written by Yousef Al Rawwash

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