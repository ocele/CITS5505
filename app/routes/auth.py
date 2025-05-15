# app/routes/auth.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from urllib.parse import urlsplit
from app import db
from app.models import User
from app.forms import LoginForm, RegisterForm 

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = LoginForm()

    if form.validate_on_submit():
        submitted_email_original = form.emailLogin.data
        submitted_email_normalized = submitted_email_original.lower()
        user = User.query.filter_by(email=submitted_email_normalized).first()

        if user is None or not user.check_password(form.passwordLogin.data):
            flash('Invalid email or password.', 'danger')
            return redirect(url_for('auth.login'))

        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('main.dashboard')
        flash('Login successful!', 'success')
        return redirect(next_page)

    return render_template('login.html', title='Sign In', form=form)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(first_name=form.firstName.data,
                    last_name=form.lastName.data,
                    email=form.emailRegister.data,)
        user.set_password(form.passwordRegister.data)

        try:
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash('Congratulations, you are now registered!', 'success')
            return redirect(url_for('main.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('Registration failed due to a server error.', 'danger')
            print(f"DB Error on Registration: {e}")
            return render_template('register.html', title='Register Failed', form=form)
    else:
        if request.method == 'POST':
            flash('Please correct the errors in the registration form.', 'warning')
        return render_template('register.html', title='Register', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))