from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, BooleanField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    emailLogin = EmailField(validators=DataRequired())
    passwordLogin = PasswordField(validators=DataRequired())

class RegisterForm(FlaskForm):
    firstName = StringField(validators=DataRequired())
    lastName = StringField(validators=DataRequired())
    emailRegister = EmailField(validators=DataRequired())
    passwordRegister = PasswordField(validators=DataRequired())
    subscription = BooleanField()



# TODO: More validators might be useful