from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db, User, Employee
from datetime import datetime
import random, string

auth_bp = Blueprint('auth', __name__)

def gen_code():
    return 'EMP' + ''.join(random.choices(string.digits, k=5))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # An already-authenticated session hitting /login must never render the
    # login form. base.html's layout branches purely on session.user_id —
    # if a session is still active, that branch shows the full sidebar
    # shell, and login.html only ever fills the auth_content block, not
    # content. The result without this check is a broken page: the
    # authenticated chrome rendering around a blank body, at the /login URL.
    # This isn't a styling issue (it happens in light mode too) — it's a
    # routing gap that a normal "click back, or revisit a bookmark while
    # still logged in" flow runs into for any real user. Redirecting
    # straight to the dashboard is also just the correct UX regardless —
    # a signed-in person shouldn't be shown a sign-in form at all.
    if session.get('user_id'):
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        email    = request.form.get('email')
        password = request.form.get('password')
        user     = User.query.filter_by(email=email, is_active=True).first()
        if user and user.check_password(password):
            session['user_id']   = user.id
            session['user_name'] = user.name
            session['user_role'] = user.role
            flash(f'Welcome back, {user.name}!', 'success')
            return redirect(url_for('dashboard.index'))
        flash('Invalid email or password.', 'danger')
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # Same reasoning as login() above — an authenticated session must never
    # see the registration form's broken empty-shell rendering.
    if session.get('user_id'):
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        name     = request.form.get('name')
        email    = request.form.get('email')
        password = request.form.get('password')
        confirm  = request.form.get('confirm')
        role     = request.form.get('role', 'employee')
        if password != confirm:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html')
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('auth/register.html')
        user = User(name=name, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()
        emp = Employee(user_id=user.id, employee_code=gen_code(),
                        date_of_joining=datetime.utcnow().date())
        db.session.add(emp)
        db.session.commit()
        flash('Registered! Please login.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
