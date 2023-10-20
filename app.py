from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'

app.config['SQLALCHEMY_BINDS'] = {
    'users': 'sqlite:///users.db',
    'events': 'sqlite:///events.db'
}

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin, db.Model):
    __bind_key__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)  # New email field
    password = db.Column(db.String(150), nullable=False)

class Event(db.Model):
    __bind_key__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    organizer = db.Column(db.String(100), nullable=False)
    time = db.Column(db.String(100), nullable=False)

def event_exists(name, organizer, time):
    return Event.query.filter_by(name=name, organizer=organizer, time=time).first() is not None

def add_dummy_events():
    events = [
        {"name": "Meet the team", "organizer": "UTFR", "time": "10-19-23 18:00"},
        {"name": "Hackathon", "organizer": "UTRA", "time": "11-19-23 15:00"},
        {"name": "Nasdaq Lunch and Learn", "organizer": "NSBE", "time": "09-28-23 19:00"}
    ]

    for event in events:
        name = event['name']
        organizer = event['organizer']
        time = event['time']
        
        if not event_exists(name, organizer, time):
            new_event = Event(name = event['name'], organizer = event['organizer'], time = datetime.strptime(event['time'], "%m-%d-%y %H:%M"))
            db.session.add(new_event)

    db.session.commit()

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

    return render_template('home.html', events=events)

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
    event = Event.query.get(event_id)

    if event is not None:
        return render_template('event_details.html', event = event)
    else:
        flash('Event not found', 'danger')
        return redirect(url_for('home'))
    
@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    query = request.args.get('query')
    results = Event.query.filter(
        (Event.name.ilike(f'%{query}%')) |
        (Event.organizer.ilike(f'%{query}%'))
    ).all()

    suggestions = [{"label": event.name, "value": event.name} for event in results]

    return jsonify(suggestions)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not Event.query.first():
            add_dummy_events()
    app.run(debug=False)

    