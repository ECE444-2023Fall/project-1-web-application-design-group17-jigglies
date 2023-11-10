'''
A File with All Form's used in the Databases
'''
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, FileField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from flask_login import current_user
from flask_wtf.file import FileAllowed

class CreateEventForm(FlaskForm):
    name = StringField('What is the name of the Event?', validators=[DataRequired()])
    organization = StringField('What is the name of the organization', validators=[DataRequired()])
    date = StringField('What is the date of the event', validators=[DataRequired()]) # Change this to Date time
    submit = SubmitField('Submit')

class ProfileForm(FlaskForm):
    username = StringField('Username')
    bio = StringField('Bio')
    password = PasswordField('New Password')
    submit = SubmitField('Update Profile')
    #profile_pic = FileField('Profile Image', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])

