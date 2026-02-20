from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from app.models import User
import bcrypt

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            login_user(user)
            # Log Activity
            from app.models import UserActivity
            from app import db
            activity = UserActivity(user_id=user.id, ip_address=request.remote_addr)
            db.session.add(activity)
            db.session.commit()
            return redirect(url_for('main.dashboard'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('auth/login.html')

@auth.route('/logout')
def logout():
    if current_user.is_authenticated:
        from app.models import UserActivity
        from app import db
        from datetime import datetime
        # Update last session
        last_session = UserActivity.query.filter_by(user_id=current_user.id).order_by(UserActivity.login_time.desc()).first()
        if last_session and not last_session.logout_time:
            last_session.logout_time = datetime.utcnow()
            diff = last_session.logout_time - last_session.login_time
            seconds = int(diff.total_seconds())
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            last_session.duration = f"{hours}h {minutes}m"
            db.session.commit()
            
    logout_user()
    return redirect(url_for('auth.login'))
