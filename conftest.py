import pytest

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
