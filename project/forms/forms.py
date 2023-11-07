'''
A File with All Form's used in the Databases
'''
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class CreateEventForm(FlaskForm):
    name = StringField('What is the name of the Event?', validators=[DataRequired()])
    organization = StringField('What is the name of the organization', validators=[DataRequired()])
    date = StringField('What is the date of the event', validators=[DataRequired()]) # Change this to Date time
    submit = SubmitField('Submit')

class ProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    name = StringField('Name', validators=[Length(max=150)])
    password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Update Profile')

