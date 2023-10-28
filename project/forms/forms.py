'''
A File with All Form's used in the Databases
'''
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email

class CreateEventForm(FlaskForm):
    name = StringField('What is the name of the Event?', validators=[DataRequired()])
    organization = StringField('What is the name of the organization', validators=[DataRequired()])
    date = StringField('What is the date of the event', validators=[DataRequired()]) # Change this to Date time
    submit = SubmitField('Submit')
