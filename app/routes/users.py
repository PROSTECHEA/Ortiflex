from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import User
import bcrypt
from functools import wraps

users = Blueprint('users', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != 'Admin':
            flash('Acceso denegado. Se requieren permisos de administrador.', 'danger')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@users.route('/users')
@login_required
@admin_required
def list_users():
    all_users = User.query.all()
    return render_template('users/list.html', users=all_users)

@users.route('/users/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        
        # Permissions
        can_inv = 'can_manage_inventory' in request.form
        can_proj = 'can_manage_projects' in request.form
        can_rep = 'can_view_reports' in request.form
        can_users = 'can_manage_users' in request.form
        
        if User.query.filter_by(username=username).first():
            flash('El nombre de usuario ya existe.', 'danger')
            return redirect(url_for('users.add_user'))
            
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user = User(
            username=username, email=email, password=hashed_pw, role=role,
            can_manage_inventory=can_inv,
            can_manage_projects=can_proj,
            can_view_reports=can_rep,
            can_manage_users=can_users
        )
        db.session.add(user)
        db.session.commit()
        flash('Usuario creado exitosamente.', 'success')
        return redirect(url_for('users.list_users'))
    return render_template('users/add.html')

@users.route('/users/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(id):
    user = User.query.get_or_404(id)
    if request.method == 'POST':
        user.username = request.form.get('username')
        user.email = request.form.get('email')
        if request.form.get('password'):
            user.password = bcrypt.hashpw(request.form.get('password').encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user.role = request.form.get('role')
        user.can_manage_inventory = 'can_manage_inventory' in request.form
        user.can_manage_projects = 'can_manage_projects' in request.form
        user.can_view_reports = 'can_view_reports' in request.form
        user.can_manage_users = 'can_manage_users' in request.form
        db.session.commit()
        flash('Usuario actualizado.', 'success')
        return redirect(url_for('users.list_users'))
    return render_template('users/edit.html', user=user)

@users.route('/users/activity')
@login_required
@admin_required
def activity_log():
    from app.models import UserActivity
    activities = UserActivity.query.order_by(UserActivity.login_time.desc()).all()
    return render_template('users/activity_log.html', activities=activities)

@users.route('/users/verify-admin', methods=['POST'])
@login_required
def verify_admin_password():
    password = request.json.get('password')
    # Find any admin user to verify
    admins = User.query.filter_by(role='Admin').all()
    for admin in admins:
        if bcrypt.checkpw(password.encode('utf-8'), admin.password.encode('utf-8')):
            return {"success": True}
    return {"success": False}, 401

@users.route('/users/<int:id>/delete')
@login_required
@admin_required
def delete_user(id):
    user = User.query.get_or_404(id)
    if user.username == 'admin':
        flash('No se puede eliminar el usuario administrador principal.', 'danger')
    else:
        db.session.delete(user)
        db.session.commit()
        flash('Usuario eliminado.', 'info')
    return redirect(url_for('users.list_users'))
