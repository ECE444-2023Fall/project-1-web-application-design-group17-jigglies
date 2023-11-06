'''
A File with All Form's used in the Databases
'''
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from flask_login import current_user

class CreateEventForm(FlaskForm):
    name = StringField('What is the name of the Event?', validators=[DataRequired()])
    organization = StringField('What is the name of the organization', validators=[DataRequired()])
    date = StringField('What is the date of the event', validators=[DataRequired()]) # Change this to Date time
    submit = SubmitField('Submit')

class ProfileForm(FlaskForm):
    old_password = PasswordField('Old Password', validators=[DataRequired()])
    username = StringField('Username')
    password = PasswordField('New Password')
    confirm_password = PasswordField('Confirm Password', validators=[EqualTo('password')])
    name = StringField('Name')
    submit = SubmitField('Update Profile')

    def validate_old_password(self, old_password):
        if not current_user.verify_password(old_password.data):
            raise ValidationError('Old password is incorrect.')

