from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)  # New email field
    password = db.Column(db.String(150), nullable=False)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    organizer = db.Column(db.String(100), nullable=False)
    time = db.Column(db.String(100), nullable=False)

events = [
    {"name": "Meet the team", "organizer": "UTFR", "time": "10-19-23 18:00"},
    {"name": "Hackathon", "organizer": "UTRA", "time": "11-19-23 15:00"},
    {"name": "Nasdaq Lunch and Learn", "organizer": "NSBE", "time": "09-28-23 19:00"}
]

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):  
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Check username and password', 'danger')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

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
        flash('Registration successful. Please login.', 'success')  # A message to inform the user that the registration was successful
        return redirect(url_for('login'))

    return render_template('signup.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/home')
def home():
    # Fetch events from the database
    events = Event.query.all()

    # Convert the list of Event objects into a list of dictionaries
    events_data = [
        {
            'name': event.name,
            'organizer': event.organizer,
            'time': event.time
        }
        for event in events
    ]

    # Enumerate the events in Python and pass them to the template
    enumerated_events = list(enumerate(events_data))

    return render_template('home.html', events=enumerated_events)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')

    # Query the database to find events that match the query (excluding time)
    results = Event.query.filter(
        (Event.name.ilike(f'%{query}%')) |
        (Event.organizer.ilike(f'%{query}%'))
    ).all()

    return render_template('search_results.html', results=results, query=query)


@app.route('/event/<int:event_id>')
def event_details(event_id):
    # Assuming you have a database with events, fetch the event details by event_id
    # Replace this with your actual database query
    event = events[event_id]  # Replace events with your database query

    return render_template('event_details.html', event=event)


if __name__ == '__main__':
    app.run(debug=True)
