
from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user,login_required 
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, TimeField, IntegerField
from wtforms.validators import DataRequired, Email, NumberRange
from datetime import datetime

from forms import CreateEventForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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


# Create User Event Form
class CreateEventForm(FlaskForm):
    name = StringField('Name of the Event', validators=[DataRequired()])
    organization = StringField('Name of the organization', validators=[DataRequired()])
    description = StringField('Description of the event', validators=[DataRequired()])
    contact = StringField('Contact information of the organizer', validators=[DataRequired()])
    date = DateField('Date of the event', format='%Y-%m-%d', validators=[DataRequired()])
    timing = TimeField('Time of the event', format='%H:%M', validators=[DataRequired()])
    capacity = IntegerField('Capacity of the event', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Submit')

# Event Database
class Event(db.Model):
    __tablename__ = 'events'

    name = db.Column(db.String(150), primary_key=True)
    organization = db.Column(db.String(150), nullable=False) # Organization can have multiple events but not with the same name
    description = db.Column(db.String(150), nullable=False)
    contact = db.Column(db.String(150), nullable=False)
    date = db.Column(db.Date, nullable=False)  # Date, store as a string for now, Change to Datetime
    timing = db.Column(db.Time, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)


    def repr(self):
        return '<Event %r>' % self.name

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

## ---------------------------------------------------------------------------- ##



## ----------------------------------- Login ---------------------------------- ##
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@app.route('/')
@login_required
def index():
    events = Event.query.all()
    return render_template('index.html', events=events)

@app.route('/successful')
def successful():
    return render_template('successful.html')


@app.route('/create_event', methods=['GET', 'POST'])
def create_event():
    form = CreateEventForm()
    if form.validate_on_submit(): 
        name = form.name.data
        organization = form.organization.data
        date = form.date.data
        description = form.description.data
        timing = form.timing.data
        contact = form.contact.data
        capacity = form.capacity.data

        name_exists = Event.query.filter_by(name =name).first()
        if name_exists:
            flash('Event name already exists. Please choose another one.', 'danger')
            return render_template('create_event.html', form=form)
        
        # Check if the event date is in the past
        current_date = datetime.now().date()
        if date <= current_date:
            flash('Event date is in the past. Please choose a future date.', 'danger')
            return render_template('create_event.html', form=form)
        
        new_event = Event(name=name, organization=organization, date=date, description=description, timing=timing, contact=contact, capacity=capacity)
        db.session.add(new_event)
        db.session.commit()
        flash('Succesfully Created New Event', 'success')
        return redirect(url_for('successful'))
    
        # return redirect(url_for('create_event'))
    return render_template('create_event.html', form=form)


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




@app.route('/create_event', methods=['GET', 'POST'])
def create_event():
    form = CreateEventForm()
    if form.validate_on_submit(): 
        name = form.name.data
        organizer = form.organization.data
        time = form.date.data

        name_exists = Event.query.filter_by(name =name).first()
        if name_exists:
            flash('Event name already exists. Please choose another one.', 'danger')
            return render_template('create_event.html', form=form)
        
        new_event = Event(name=name, organizer=organizer, time=time)
        db.session.add(new_event)
        db.session.commit()
        flash('Succesfully Created New Event', 'success')
    
        # return redirect(url_for('create_event'))
    return render_template('create_event.html', form=form)

## ---------------------------------------------------------------------------- ##


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not Event.query.first():
            add_dummy_events()
    app.run(debug=False)

    