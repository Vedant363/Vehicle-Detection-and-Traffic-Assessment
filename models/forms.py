from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError
import re

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Login')

# Custom validator to support both YouTube and IP stream URLs
def input_url_validator(form, field):
    youtube_regex = r'^https?://(www\.)?(youtube\.com/(watch\?v=|live/)|youtu\.be/)[\w-]{11}(&t=\d+s)?$'
    ip_stream_regex = r'^(http:\/\/|rtsp:\/\/).+'

    if not (re.match(youtube_regex, field.data) or re.match(ip_stream_regex, field.data)):
        raise ValidationError('Invalid URL. Must be a valid YouTube or IP stream URL.')

class URLForm(FlaskForm):
    youtube_url = StringField(
        'Input URL',
        default='https://www.youtube.com/watch?v=iJZcjZD0fw0&t=1s',
        validators=[DataRequired(), input_url_validator]
    )
    submit = SubmitField('Submit')