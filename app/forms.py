from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from app.models import User 

class LoginForm(FlaskForm):
    emailLogin = EmailField('Email', validators=[DataRequired(), Email()]) 
    passwordLogin = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField("Remember me")
    submit = SubmitField('Sign In')

class RegisterForm(FlaskForm):
    firstName = StringField('First Name', validators=[DataRequired(), Length(min=3, max=64)])
    lastName = StringField('Last Name', validators=[DataRequired(), Length(min=3, max=64)])
    # username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    emailRegister = EmailField('Email', validators=[DataRequired(), Email(), Length(max=120)]) 
    passwordRegister = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    passwordRegisterRepeat = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match.')])
    subscription = BooleanField('Subscribe for Sales & New Themes')
    submit = SubmitField('Register')