from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError
import re

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Login')

# Custom YouTube URL Validator
def youtube_url_validator(form, field):
    youtube_regex = r'^https:\/\/www\.youtube\.com\/watch\?v=[\w-]{11}(&t=\d+s)?$'
    if not re.match(youtube_regex, field.data):
        raise ValidationError('Invalid YouTube URL.')

class URLForm(FlaskForm):
    youtube_url = StringField('YouTube URL', default='https://www.youtube.com/watch?v=iJZcjZD0fw0&t=1s', 
                              validators=[DataRequired(), youtube_url_validator])
    submit = SubmitField('Submit')