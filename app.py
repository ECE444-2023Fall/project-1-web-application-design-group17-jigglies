
from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

bootstrap = Bootstrap(app)
moment = Moment(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)  # New email field
    password = db.Column(db.String(150), nullable=False)


# Create User Event Form
class CreateEventForm(FlaskForm):
    name = StringField('What is the name of the Event?', validators=[DataRequired()])
    organization = StringField('What is the name of the organization', validators=[DataRequired()])
    date = StringField('What is the date of the event', validators=[DataRequired()]) # Change this to Date time
    submit = SubmitField('Submit')

# Event Database
class Event(db.Model):
    __tablename__ = 'events'

    name = db.Column(db.String(150), primary_key=True)
    organization = db.Column(db.String(150), nullable=False) # Organization can have multiple events but not with the same name
    date = db.Column(db.String(150), unique=True, nullable=False)  # Date, store as a string for now, Change to Datetime

    def repr(self):
        return '<Event %r>' % self.name

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_event', methods=['GET', 'POST'])
def create_event():
    form = CreateEventForm()
    if form.validate_on_submit(): 
        name = form.name.data
        organization = form.organization.data
        date = form.date.data

        name_exists = Event.query.filter_by(name = name).first()
        if name_exists:
            flash('Event name already exists. Please choose another one.', 'danger')
            return render_template('create_event.html')
        
        new_event = Event(name=name, organization=organization, date=date)
        db.session.add(new_event)
        db.session.commit()
        flash('Succesfully Created New Event', 'success')
    
        return redirect(url_for('create_event'))
    return render_template('create_event.html', 
                           form=form,
                           name=session.get('name'), 
                           organization=session.get('organization'),
                           rsvp_limit = session.get('rsvp_limt'))

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

if __name__ == '__main__':
    app.run(debug=True)
