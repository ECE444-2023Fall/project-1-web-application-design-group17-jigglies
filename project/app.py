
from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user,login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_bootstrap import Bootstrap
from flask_moment import Moment

from project.forms import CreateEventForm, ProfileForm
from datetime import datetime


app = Flask(__name__)
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
    name = db.Column(db.String(150), nullable=True)

    def update_username(self, new_username):
        self.username = new_username
        db.session.commit()

    def update_password(self, new_password):
        hashed_password = generate_password_hash(new_password, method='scrypt')
        self.password = hashed_password
        db.session.commit()

    def update_name(self, new_name):
        self.name = new_name
        db.session.commit()

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


@app.route('/')
@login_required
def index():
    # events = Event.query.all()
    return render_template('index.html')


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

## ------------------------------- Profile ------------------------------- ##

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    if form.validate_on_submit():
        if form.old_password.data and current_user.verify_password(form.old_password.data):
            # Assuming the methods `update_username`, `update_password`, and `update_name` exist
            # and handle the updating logic including saving to the database.
            if form.username.data:
                current_user.update_username(form.username.data)
            if form.password.data:
                current_user.update_password(form.password.data)
            if form.name.data:
                current_user.update_name(form.name.data)
            flash('Your profile has been updated!', 'success')
            return redirect(url_for('profile'))
        else:
            flash('Old password is incorrect.', 'danger')
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.name.data = current_user.name
    return render_template('profile.html', title='Update Profile', form=form)

## ---------------------------------------------------------------------------- ##



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # if not Event.query.first():
        #    add_dummy_events()
    app.run(debug=True)

    