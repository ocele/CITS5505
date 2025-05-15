# tests/unit/test_form_validation.py

from app.forms import LoginForm, RegisterForm
from flask import Flask
from flask_wtf.csrf import CSRFProtect

def create_app():
    app = Flask(__name__)
    app.config["WTF_CSRF_ENABLED"] = False  # 测试禁用 CSRF
    app.config["SECRET_KEY"] = "test"
    CSRFProtect(app)
    return app

def test_valid_login_form():
    app = create_app()
    with app.test_request_context():
        form = LoginForm(data={
            "emailLogin": "test@example.com",
            "passwordLogin": "testpass123",
            "remember_me": True
        })
        assert form.validate() is True

def test_invalid_login_form_missing_email():
    app = create_app()
    with app.test_request_context():
        form = LoginForm(data={
            "emailLogin": "",
            "passwordLogin": "testpass123"
        })
        assert form.validate() is False
        assert "This field is required." in str(form.emailLogin.errors)

def test_valid_register_form():
    app = create_app()
    with app.test_request_context():
        form = RegisterForm(data={
            "firstName": "John",
            "lastName": "Doe",
            "emailRegister": "john@example.com",
            "passwordRegister": "secret123",
            "passwordRegisterRepeat": "secret123",
            "subscription": True
        })
        assert form.validate() is True

def test_register_passwords_not_match():
    app = create_app()
    with app.test_request_context():
        form = RegisterForm(data={
            "firstName": "Jane",
            "lastName": "Smith",
            "emailRegister": "jane@example.com",
            "passwordRegister": "secret123",
            "passwordRegisterRepeat": "wrongpass",
            "subscription": False
        })
        assert form.validate() is False
        assert "Passwords must match" in str(form.passwordRegisterRepeat.errors)

def test_register_short_first_name():
    app = create_app()
    with app.test_request_context():
        form = RegisterForm(data={
            "firstName": "A",
            "lastName": "Smith",
            "emailRegister": "jane@example.com",
            "passwordRegister": "secret123",
            "passwordRegisterRepeat": "secret123",
            "subscription": False
        })
        assert form.validate() is False
        assert "Field must be between 3 and 64 characters long." in str(form.firstName.errors)
