import json
from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, logout_user,login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_mail import Mail, Message
import random
import base64
from base64 import b64encode
import urllib
import re
from project import helpers
from werkzeug.datastructures import FileStorage

from datetime import datetime, timedelta
from project.forms.forms import CreateEventForm, ProfileForm
from datetime import datetime, timedelta
import os

app = Flask(__name__, template_folder='project/templates', static_folder='project/static')
app.config['SECRET_KEY'] = 'mysecret'

url = os.getenv('DATABASE_URL', 'sqlite:///database.db')
if url.startswith("postgres://"):
    url = url.replace("postgres://", "postgresql://", 1)

SQLALCHEMY_DATABASE_URI = url

app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = '/imgs'

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'noreply.poppin@gmail.com'
app.config['MAIL_PASSWORD'] = 'pnjn bbtn ihqe spwm'
mail = Mail(app)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'signup'

bootstrap = Bootstrap(app)
moment = Moment(app)
migrate = Migrate(app, db)

GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
GOOGLE_PLACES_API_KEY = os.getenv('GOOGLE_PLACES_API_KEY')



## ----------------------------- Database Schemas ----------------------------- ##

class User(UserMixin, db.Model):
    #__bind_key__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)  # New email field
    password = db.Column(db.String(150), nullable=False)
    comments = db.relationship("Comment", backref="user", passive_deletes=True)
    likes = db.relationship("Like", backref="user", passive_deletes=True)
    rsvps = db.relationship("Rsvp", backref="user", passive_deletes=True)
    bio = db.Column(db.String(150), nullable=True)
    profile_pic = db.Column(db.LargeBinary, nullable=True)

    def update_username(self, new_username):
        self.username = new_username
        db.session.commit()

    def update_password(self, new_password):
        hashed_password = generate_password_hash(new_password, method='scrypt')
        self.password = hashed_password
        db.session.commit()

    def update_bio(self, new_bio):
        self.bio = new_bio
        db.session.commit()

    def update_profile_pic(self, pic):
        self.profile_pic = pic
        db.session.commit()
    
# Event Database
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(80), unique=True, nullable=False)
    event_organization = db.Column(db.String(80), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    location = db.Column(db.String(120), nullable=False)
    room = db.Column(db.String(50), nullable=False)
    allow_comments = db.Column(db.Boolean, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    event_information = db.Column(db.Text, nullable=False)
    tags = db.Column(db.String, nullable=True) # Retrive by using json.loads(tags) to put it back into list form
    cover_photo = db.Column(db.LargeBinary, nullable=True)
    comments = db.relationship("Comment", backref="event", passive_deletes=True)
    likes = db.relationship("Like", backref="event", passive_deletes=True)
    rsvps = db.relationship("Rsvp", backref="event", passive_deletes=True)
    
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    datetime_created = db.Column(db.DateTime(timezone=True), default=func.now())
    author = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey("event.id", ondelete="CASCADE"), nullable=False)
    
class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey("event.id", ondelete="CASCADE"), nullable=False)

class Rsvp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey("event.id", ondelete="CASCADE"), nullable=False)
## ---------------------------------------------------------------------------- ##



## ----------------------------------- Login ---------------------------------- ##
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@app.template_filter('b64encode')
def b64encode_filter(data):
    return b64encode(data).decode() if data else None


@app.route('/')
@login_required
def index():
    today = datetime.today().date()
    events_today = Event.query.filter_by(date=today).all()
    user_events = Event.query.filter_by(created_by=current_user.id).all()
    
    top_upcoming_rsvps = Event.query \
        .join(Rsvp, Event.id == Rsvp.event_id) \
        .filter(Rsvp.author == current_user.id, Event.date >= today) \
        .order_by(Event.date.asc()) \
        .limit(5) \
        .all()
        
    top_liked_events = Event.query \
        .join(Like, isouter=True) \
        .group_by(Event.id) \
        .order_by(func.count(Like.id).desc()) \
        .limit(5) \
        .all()
    
    events = Event.query.all()
    return render_template('index.html', events = events, events_today=events_today, user_events=user_events, top_upcoming_rsvps=top_upcoming_rsvps, top_liked_events=top_liked_events)


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
            flash('Login Unsuccessful. Check your details and try again.', 'alert')

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        user_verification_code = request.form.get('verificationCode')

        # Add this block to validate the email domain
        if not email.endswith('utoronto.ca'):
            flash('Please sign up with a uoft email.', 'alert')
            return render_template('signup.html')

        user_by_username = User.query.filter_by(username=username).first()
        user_by_email = User.query.filter_by(email=email).first()

        if user_by_username:
            flash('Username already exists. Please choose another one.', 'alert')
            return render_template('signup.html', username=username, email=email)

        if user_by_email:
            flash('Email already registered. Please use another email or login.', 'alert')
            return render_template('signup.html', username=username, email=email)
        
        if len(password) < 6 or not re.search("[a-z]", password) or not re.search("[A-Z]", password) or not re.search("[0-9]", password) or not re.search("[!@#$%^&*(),.?\":{}|<>]", password):
            flash('Password too weak. It must be at least 6 characters long and include uppercase and lowercase letters, and special characters.', 'alert')
            return render_template('signup.html', username=username, email=email)


        
        # Check if the verification code matches
        stored_codes = session.get('verification_codes', {})
        if email in stored_codes and str(stored_codes[email]) == user_verification_code:
            # Proceed with registration
            hashed_password = generate_password_hash(password, method='scrypt')
            new_user = User(username=username, email=email, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful. Please login.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Invalid verification code.', 'alert')
            #return render_template('signup.html')
        
    return render_template('signup.html')


@app.route('/send_verification_code', methods=['POST'])
def send_verification_code():
    email = request.json.get('email')

    # Validate email or other logic here
    if not email:
        return jsonify({'status': 'error', 'message': 'Please first enter your uoft email'})
    user_by_email = User.query.filter_by(email=email).first()
    if not email.endswith('utoronto.ca'):
        return jsonify({'status': 'error', 'message': 'Please sign up with a uoft email.'})

    if user_by_email:
        return jsonify({'status': 'error', 'message': 'Email already registered. Please use another email or login'})

    verification_code = random.randint(100000, 999999)

    # Store the code in the session or database
    if 'verification_codes' not in session:
        session['verification_codes'] = {}

    session['verification_codes'][email] = verification_code
    session.modified = True  # Ensure the session is marked as modified

    # Send the code via email
    msg = Message("Your Verification Code", sender="your-email@example.com", recipients=[email])
    msg.body = f"Your verification code is {verification_code}"
    mail.send(msg)
    
    return jsonify({'message': 'Verification code sent! (Please check SPAM folder)'})

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

## ----------------------------------Search----------------------------------- ##

@app.route('/search', methods=['GET'])
@login_required
def search():
    query = request.args.get('search_query')
   
    # Query the database
    if(query):
        results = Event.query.filter(
            (Event.event_name.ilike(f'%{query}%')) |
            (Event.event_organization.ilike(f'%{query}%'))
        ).all()
        description = "Search Results: " + query
    else:
        description = "Explore all events:"
        results = Event.query.all()

    # Prepare data for JSON serialization
    events_data = []
    for event in results:
        event_dict = {
            'id': event.id,
            'event_name': event.event_name,
            'event_organization': event.event_organization,
            'date': event.date,  
            'date': event.date.strftime('%Y-%m-%d'),
            'start_time': event.start_time.strftime('%H:%M:%S'),
            'end_time': event.end_time.strftime('%H:%M:%S'),
            'room': event.room,
            'allow_comments': event.allow_comments,
            'capacity': event.capacity,
            'event_information': event.event_information,
            'tags': json.loads(event.tags) if event.tags else [],
            # Convert binary data to base64 string for image
            'cover_photo': b64encode(event.cover_photo).decode() if event.cover_photo else None
        }
        events_data.append(event_dict)

    organizers = {event.event_organization for event in results}
    tags = set()
    for event in results:
        if event.tags:
            event_tags = json.loads(event.tags)
            tags.update(event_tags)

    return render_template('search_results.html', events=events_data, query=query, organizers=list(organizers), tags=list(tags), description=description)


@app.route('/autocomplete', methods=['GET'])
@login_required
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


@app.route('/event/<int:event_id>')
@login_required
def event_details(event_id):
    event = Event.query.filter_by(id=event_id).first()

    if event is not None:
        comments = event.comments

        if event.location is not None:
            google_maps_url = "https://www.google.com/maps/embed/v1/place?key=" + GOOGLE_MAPS_API_KEY + "&q=" + urllib.parse.quote_plus(event.location)
        else:
            google_maps_url = None

        parsedDateTime = helpers.parseDateTime(event.date, event.start_time, event.end_time)

        # Check if tags are not None before trying to load JSON
        if event.tags is not None:
            tags = json.loads(event.tags)
        else:
            tags = []

        return render_template('event_details.html', event=event, urllib=urllib, google_maps_url=google_maps_url, parsedDateTime=parsedDateTime, comments=comments, GOOGLE_MAPS_API_KEY=GOOGLE_MAPS_API_KEY, tags=tags)
    else:
        flash("Sorry, that event doesn't exist!", 'danger')
        return redirect(url_for('index'))



@app.route('/create_comment/<int:event_id>', methods=["POST"])
@login_required
def create_comment(event_id):
    comment_text = request.json.get("comment")
    event = Event.query.filter_by(id=event_id).first()
    
    if event:
        comment = Comment(text=comment_text, author=current_user.id, event_id=event_id)
        db.session.add(comment)
        db.session.commit()
        profile_pic = b64encode(current_user.profile_pic).decode() if current_user.profile_pic else None
        
        return jsonify({
            "comment": {
                "text": comment.text,
                "author": comment.user.username,
                "datetime_created": comment.datetime_created
            },
            "profile_pic": profile_pic
        })
    else:
        flash("Event does not exist!", "error")
        return redirect(url_for("home"))
    
@app.route('/like_event/<int:event_id>', methods=["POST"])
@login_required
def like_event(event_id):
    event = Event.query.filter_by(id=event_id).first()
    like = Like.query.filter_by(author=current_user.id, event_id=event_id).first()
    
    if not event:
        return jsonify({"error": "Event does not exist."}, 400)
    elif like: # If user has already liked the event, remove the like from db.
        db.session.delete(like)
        db.session.commit()
    else:
        like = Like(author=current_user.id, event_id=event_id)
        db.session.add(like)
        db.session.commit()
    return jsonify({"like_count": len(event.likes), "user_has_liked": current_user.id in map(lambda like: like.author, event.likes )})
    
@app.route('/rsvp_event/<int:event_id>', methods=["POST"])
@login_required
def rsvp_event(event_id):
    event = Event.query.filter_by(id=event_id).first()
    rsvp = Rsvp.query.filter_by(author=current_user.id, event_id=event_id).first()

    if not event:
        return jsonify({"error": "Event does not exist."}, 400)
    elif rsvp: # If user has already rsvp'd for the event, remove the rsvp from db.
        db.session.delete(rsvp)
        db.session.commit()
    else:
        rsvp = Rsvp(author=current_user.id, event_id=event_id)
        db.session.add(rsvp)
        db.session.commit()
    return jsonify({"rsvp_count": len(event.rsvps),"user_has_rsvp": current_user.id in map(lambda rsvp: rsvp.author, event.rsvps )})

## ---------------------------------------------------------------------------- ##


## ------------------------------- Create Event ------------------------------- ##

@app.route('/event_success', methods=['GET', 'POST'])
def event_success():
    return render_template('event_success.html')


@app.route('/create_event', methods=['GET', 'POST'])
@login_required 
def create_event():
    tomorrow = (datetime.utcnow() + timedelta(days=1)).date()
    if request.method == 'GET':
        return render_template('create_event.html', tomorrow=tomorrow, key=GOOGLE_PLACES_API_KEY)
    
    if request.method == 'POST':
        # Extract event name
        event_name = request.form['event_name']

        # Check if event name already exists
        if Event.query.filter_by(event_name=event_name).first():
            flash('An event with the name already exists, please choose another name', 'danger')
            return render_template('create_event.html', tomorrow=tomorrow, key=GOOGLE_PLACES_API_KEY)
        
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
            return render_template('create_event.html', tomorrow=tomorrow, key=GOOGLE_PLACES_API_KEY)

        tag_info = request.form['tags']
        tags = [tag['value'] for tag in json.loads(tag_info)]
        tag_db = json.dumps(tags)
        location = request.form['location']
        room = request.form['room']
        allow_comments = True if request.form['allow_comments'] == 'Yes' else False
        capacity = int(request.form['capacity'])
        event_information = request.form['event-information']
        

        image_file = request.files['file-upload']
        image_data = None
        if image_file:
            image_data = image_file.read()
        
        new_event = Event(
            event_name=event_name,
            event_organization=event_organization,
            created_by=current_user.id,
            date=event_date,
            start_time=start_time_obj,
            end_time=end_time_obj,
            location=location,
            room=room,
            allow_comments=allow_comments,
            capacity=capacity,
            event_information=event_information,
            tags=tag_db,
            cover_photo=image_data 
        )
        db.session.add(new_event)
        db.session.commit()
        return redirect(url_for('event_success'))

    return render_template(url_for('create_event'), tomorrow=tomorrow, key=GOOGLE_PLACES_API_KEY) 


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

## ------------------------------- Profile ------------------------------- ##

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    name = current_user.username
    bio = current_user.bio
    return render_template('profile.html', title='View Profile', name=name, bio=bio)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = ProfileForm()
    status = None
    if form.validate_on_submit():
        has_changes = False
        # Check if username needs to be updated
        if 'username' in request.form:
            new_username = form.username.data
            if new_username and new_username != current_user.username:
                current_user.update_username(new_username)
                has_changes = True
        # Check if password needs to be updated
        if 'password' in request.form:
            new_password = form.password.data
            if new_password:
                current_user.update_password(new_password)
                has_changes = True
        # Check if bio needs to be updated
        if 'bio' in request.form:
            new_bio = form.bio.data
            if new_bio and new_bio != current_user.bio:
                current_user.update_bio(new_bio)
                has_changes = True
        if form.profile_pic.data:
            image_file = request.files['profile_pic']
            image_data = None
            if image_file:
                image_data = image_file.read()
            profile_pic = image_data
            current_user.update_profile_pic(profile_pic)
            has_changes = True
        # Set status based on whether changes were made
        if has_changes:
            db.session.commit()
            status = 'success'
        else:
            status = 'no_changes'
    elif request.method == 'GET':
        # Pre-fill the form with the current user's data
        form.username.data = current_user.username
        form.bio.data = current_user.bio

    return render_template('edit_profile.html', title='Update Profile', form=form, status=status)


## ---------------------------------------------------------------------------- ##

## ----------------------- Liked Events --------------------------------------- ##

@app.route('/liked_events')
@login_required
def liked_events():
    liked_events = Event.query.join(Like).filter(Like.author == current_user.id).all()
    return render_template('liked_events.html', liked_events=liked_events)

## -------------------------------------------------------------------------------- ##

@app.errorhandler(404)
def page_not_found(e):
    if not current_user.is_authenticated:
        # If the user is not logged in, redirect them to login page.
        return redirect(url_for('login'))
    else:
        # For an authenticated user, display custom 404 page.
        return render_template('404.html'), 404

if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()
        if not User.query.first() and not Event.query.first():
            populate_database()
        # if not Event.query.first():
        #    add_dummy_events()
    app.run(debug=True)

