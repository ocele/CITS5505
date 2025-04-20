from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from app.models import User 

class LoginForm(FlaskForm):
    emailLogin = EmailField('Email', validators=[DataRequired(), Email()]) 
    passwordLogin = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)]) 
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match.')])
    submit = SubmitField('Register')