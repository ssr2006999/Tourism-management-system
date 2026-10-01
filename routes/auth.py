import re
from flask import render_template, request, redirect, url_for, session, flash
from routes import auth_bp
from database import query_db
from routes.utils import is_safe_url, validate_csrf_token


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    next_url = request.args.get('next')

    if request.method == 'POST':
        if not validate_csrf_token(request.form.get('csrf_token')):
            flash('Invalid form submission. Please try again.')
            return redirect(url_for('auth.login', next=next_url))

        email = request.form.get('email', '')
        password = request.form.get('password', '')

        if not email or not password:
            flash('Please enter both email and password.')
            return redirect(url_for('auth.login', next=next_url))

        users = query_db("select * from users where email = %s", (email,), fetch=True)

        if not users:
            flash('Invalid email or password.')
            return redirect(url_for('auth.login', next=next_url))

        user = users[0]

        if user['password'] != password:
            flash('Invalid email or password.')
            return redirect(url_for('auth.login', next=next_url))

        session['user_id'] = user['id']
        session['role'] = user['role']

        if next_url and is_safe_url(next_url):
            return redirect(next_url)

        if user['role'] == 'admin':
            return redirect(url_for('admin.admin_dashboard'))
        return redirect(url_for('main.home'))

    return render_template('auth.html', next_url=next_url, active_tab='login')


@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    flash('You have been logged out.')
    return redirect(url_for('main.home'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if not validate_csrf_token(request.form.get('csrf_token')):
            flash('Invalid form submission. Please try again.')
            return redirect(url_for('auth.register'))

        name = request.form.get('name', '')
        email = request.form.get('email', '')
        password = request.form.get('password', '')
        phone = request.form.get('phone', '')

        if not name or not email or not password:
            flash('Name, email, and password are required.')
            return redirect(url_for('auth.register'))

        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            flash('Invalid email format.')
            return redirect(url_for('auth.register'))

        existing = query_db("select * from users where email = %s", (email,), fetch=True)
        if existing:
            flash('Email is already registered.')
            return redirect(url_for('auth.register'))

        role = 'user'

        query_db(
            "insert into users (name, email, password, phone, role) values (%s, %s, %s, %s, %s)",
            (name, email, password, phone, role)
        )

        flash('Registration successful! Please log in.')
        return redirect(url_for('auth.login'))

    return render_template('auth.html', active_tab='register')