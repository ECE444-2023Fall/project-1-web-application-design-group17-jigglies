from datetime import datetime
from flask import Flask, render_template, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email

app = Flask(__name__)
app.config['SECRET_KEY'] = 'lnlk;jdvsnd;jkvbsd'


bootstrap = Bootstrap(app)
moment = Moment(app)



class CreateEventForm(FlaskForm):
    name = StringField('What is the name of the Event?', validators=[DataRequired()])
    organization = StringField('What is the name of the organization', validators=[DataRequired()])
    date = StringField('What is the date of the event', validators=[DataRequired()])



@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit(): 
        session['name'] = form.name.data
        session['organization'] = form.organization.data
        return redirect(url_for('create_event'))
    return render_template('create_event.html', 
                           form=form, 
                           name=session.get('name'), 
                           organization=session.get('organization'),
                           rsvp_limit = session.get('rsvp_limt'))