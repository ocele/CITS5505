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
        return redirect(url_for('main.index')) 

    form = LoginForm()
    form2 = RegisterForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.emailLogin.data).first() 
        if user is None or not user.check_password(form.passwordLogin.data):
            flash('Invalid email or password', 'danger')
            return redirect(url_for('auth.login'))

        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('main.index')
        flash('Login successful!', 'success')
        return redirect(next_page)

    return render_template('login.html', title='Sign In', form1=form, form2=form2)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegisterForm()
    form1 = LoginForm()
    if form.validate_on_submit():
        user = User(firstName=form.firstName.data, lastName=form.lastName.data, email=form.emailRegister.data)
        user.set_password(form.passwordRegister.data) 
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!', 'success')
        return redirect(url_for('auth.login')) 
    # register page requires both login and register forms
    return render_template('login.html', title='Register', form2=form, form1 = form1)

@bp.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))