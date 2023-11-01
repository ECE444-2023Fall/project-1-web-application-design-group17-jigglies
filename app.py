
from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user,login_required 
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_bootstrap import Bootstrap
from flask_moment import Moment
import base64

from datetime import datetime

app = Flask(__name__, template_folder='project/templates', static_folder='project/static')
app.config['SECRET_KEY'] = 'mysecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = '/imgs'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'signup'

bootstrap = Bootstrap(app)
moment = Moment(app)

## ----------------------------- Database Schemas ----------------------------- ##

class User(UserMixin, db.Model):
    #__bind_key__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)  # New email field
    password = db.Column(db.String(150), nullable=False)

# Event Database
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(80), unique=True, nullable=False)
    event_organization = db.Column(db.String(80), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    location = db.Column(db.String(120), nullable=False)
    room = db.Column(db.String(50), nullable=False)
    allow_comments = db.Column(db.Boolean, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    event_information = db.Column(db.Text, nullable=False)
    cover_photo = db.Column(db.LargeBinary, nullable=True)

## ---------------------------------------------------------------------------- ##



## ----------------------------------- Login ---------------------------------- ##
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@app.template_filter('b64encode')
def b64encode_filter(data):
    return base64.b64encode(data).decode() if data else None


@app.route('/')
@login_required
def index():
    events = Event.query.all()
    return render_template('index.html', events = events)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_identifier = request.form.get('user_identifier')
        password = request.form.get('password')
        
        # First, try to get the user by username
        user = User.query.filter_by(username=user_identifier).first()
        
        # If not found by username, try email
        if not user:
            user = User.query.filter_by(email=user_identifier).first()

        if user and check_password_hash(user.password, password):  
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Check your details and try again.', 'danger')

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Add this block to validate the email domain
        if not email.endswith('utoronto.ca'):
            flash('Please sign up with a uoft email.', 'danger')
            return render_template('signup.html')

        user_by_username = User.query.filter_by(username=username).first()
        user_by_email = User.query.filter_by(email=email).first()

        if user_by_username:
            flash('Username already exists. Please choose another one.', 'danger')
            return render_template('signup.html')

        if user_by_email:
            flash('Email already registered. Please use another email or login.', 'danger')
            return render_template('signup.html')

        hashed_password = generate_password_hash(password, method='scrypt')
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful. Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

## ----------------------------------Search----------------------------------- ##

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('search_query')

    # Query the database to find events that match the query
    results = Event.query.filter(
        (Event.event_name.ilike(f'%{query}%')) |
        (Event.event_organization.ilike(f'%{query}%'))
    ).all()

    return render_template('search_results.html', events=results, query=query)

@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    query = request.args.get('search_query')
    print(f"Received query: {query}")

    # Query the database to find events that match the query
    results = Event.query.filter(
        (Event.event_name.ilike(f'%{query}%'))
    ).all()

    # Transform results into a format suitable for the frontend
    results_list = [{'name': result.event_name} for result in results]

    return jsonify(results_list)



@app.route('/all_events')
def all_events():
    events = Event.query.all()
    return render_template('all_events.html', events=events)

@app.route('/event/<int:event_id>')
def event_details(event_id):
    event = Event.query.get(event_id)

    if event is not None:
        return render_template('event_details.html', event = event)
    else:
        flash('Event not found', 'danger')
        return redirect(url_for('home'))
    
## ---------------------------------------------------------------------------- ##


## ------------------------------- Create Event ------------------------------- ##

@app.route('/event_success', methods=['GET', 'POST'])
def event_success():
    return render_template('event_success.html')


@app.route('/create_event', methods=['GET', 'POST'])
def create_event():
    if request.method == 'GET':
        return render_template('create_event.html')
    
    if request.method == 'POST':
        # Extract event name
        event_name = request.form['event_name']

        # Check if event name already exists
        if Event.query.filter_by(event_name=event_name).first():
            flash('An event with the name already exists, please choose another name', 'danger')
            return render_template('create_event.html')
        
        # Extract event organization name
        event_organization = request.form['organization']

        date_str = request.form['date']
        event_date = datetime.strptime(date_str, '%Y-%m-%d').date()

        # Retrieve dropdown values for start and end time
        start_hour = request.form['start-time']
        start_time_obj = datetime.strptime(start_hour, '%H').time()

        end_hour = request.form['end-time'] 
        end_time_obj = datetime.strptime(end_hour, '%H').time()

        # If end time is before start time, return error as it is an invalid input
        if end_time_obj <= start_time_obj:
            flash('Invalid Time inputs, please check and resubmit', 'danger')
            return render_template('create_event.html')

        location = request.form['location']
        room = request.form['room']
        allow_comments = True if request.form['allow-comments'] == 'yes' else False
        capacity = int(request.form['capacity'])
        event_information = request.form['event-information']

        image_file = request.files['file-upload']
        image_data = None
        if image_file:
            image_data = image_file.read()
        
        new_event = Event(
            event_name=event_name,
            event_organization=event_organization,
            date=event_date,
            start_time=start_time_obj,
            end_time=end_time_obj,
            location=location,
            room=room,
            allow_comments=allow_comments,
            capacity=capacity,
            event_information=event_information,
            cover_photo=image_data 
        )
        db.session.add(new_event)
        db.session.commit()
        return redirect(url_for('event_success'))

    return render_template(url_for('create_event')) 


## ---------------------------------------------------------------------------- ##
def populate_database():
    # Add dummy users
    users = [
        {"username": "john", "email": "john@utoronto.ca", "password": "password123"},
        {"username": "jane", "email": "jane@utoronto.ca", "password": "password123"}
    ]
    
    for user in users:
        hashed_password = generate_password_hash(user["password"], method='scrypt')
        new_user = User(username=user["username"], email=user["email"], password=hashed_password)
        db.session.add(new_user)
    
    # Add dummy events
    events = [
        {
            "event_name": "Math 101 Class",
            "event_organization": "UofT",
            "date": datetime.today().date(),
            "start_time": (datetime.now() + timedelta(hours=1)).time(),
            "end_time": (datetime.now() + timedelta(hours=2)).time(),
            "location": "UofT Campus",
            "room": "Room 101",
            "allow_comments": True,
            "capacity": 50,
            "event_information": "This is a Math 101 class."
        },
        {
            "event_name": "Physics Lecture",
            "event_organization": "UofT",
            "date": datetime.today().date(),
            "start_time": (datetime.now() + timedelta(hours=3)).time(),
            "end_time": (datetime.now() + timedelta(hours=4)).time(),
            "location": "UofT Science Building",
            "room": "Room 201",
            "allow_comments": False,
            "capacity": 40,
            "event_information": "Advanced physics lecture."
        },
        {
            "event_name": "Computer Science Workshop",
            "event_organization": "UofT TechHub",
            "date": datetime.today().date(),
            "start_time": (datetime.now() + timedelta(hours=5)).time(),
            "end_time": (datetime.now() + timedelta(hours=6)).time(),
            "location": "UofT Tech Center",
            "room": "Room 10",
            "allow_comments": True,
            "capacity": 30,
            "event_information": "A workshop on the latest trends in computer science."
        }
    ]
    for event in events:
        new_event = Event(**event)
        db.session.add(new_event)

    db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()
        if not User.query.first() and not Event.query.first():
            populate_database()
    app.run(debug=True)

