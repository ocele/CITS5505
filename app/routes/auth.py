# app/routes/auth.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.forms import LoginForm, RegisterForm
from app.models import User
from app import db
from werkzeug.security import generate_password_hash, check_password_hash

bp = Blueprint('auth', __name__)  # 不加 prefix，最终 URL 就是 /login

@bp.route('/login', methods=['GET', 'POST'], endpoint='login')
def login():
    form1 = LoginForm()
    form2 = RegisterForm()

    if request.method == 'POST':
        form_type = request.form.get('form_type')

        if form_type == 'login' and form1.validate_on_submit():
            email = form1.emailLogin.data
            password = form1.passwordLogin.data

            user = User.query.filter_by(email=email).first()
            if user and check_password_hash(user.password_hash, password):
                flash("Login successful!", "success")
                return redirect(url_for('login'))
            else:
                flash("Invalid email or password.", "danger")
                return redirect(url_for('login'))

        elif form_type == 'register' and form2.validate_on_submit():
            user = User(
                first_name=form2.firstName.data,
                last_name=form2.lastName.data,
                email=form2.emailRegister.data,
                password_hash=generate_password_hash(form2.passwordRegister.data)
            )
            db.session.add(user)
            db.session.commit()
            flash("Registration successful!", "success")
            return redirect(url_for('login'))

    return render_template('login.html', form1=form1, form2=form2)
