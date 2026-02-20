from datetime import datetime
from flask_login import UserMixin
from app import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='Usuario') # Admin, Soporte, Operativo
    
    # Granular Permissions
    can_manage_inventory = db.Column(db.Boolean, default=True)
    can_manage_projects = db.Column(db.Boolean, default=True)
    can_view_reports = db.Column(db.Boolean, default=True)
    can_manage_users = db.Column(db.Boolean, default=False)
    
    activity = db.relationship('UserActivity', backref='user', lazy=True)

class Material(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Float, nullable=False, default=0)
    min_stock = db.Column(db.Float, nullable=False, default=10)
    unit = db.Column(db.String(20), nullable=False) # kg, m, units, etc.
    supplier = db.Column(db.String(100))
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    movements = db.relationship('InventoryMovement', backref='material', lazy=True)

class ProjectMaterial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey('material.id'), nullable=False)
    quantity_required = db.Column(db.Float, nullable=False)
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    
    project = db.relationship('Project', back_populates='materials')
    material = db.relationship('Material')

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), nullable=False, default='Planificado') # Planificado, En ejecución, Finalizado, Cancelado
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    date_started = db.Column(db.DateTime)
    date_ended = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    materials = db.relationship('ProjectMaterial', back_populates='project', cascade="all, delete-orphan")
    history = db.relationship('ProjectHistory', backref='project', lazy=True, cascade="all, delete-orphan")

class ProjectHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False) # e.g., 'Material Agregado', 'Estado Cambiado'
    details = db.Column(db.Text)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user = db.relationship('User')
    
class InventoryMovement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    material_id = db.Column(db.Integer, db.ForeignKey('material.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(10), nullable=False) # Entra, Sale
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True) # Optional link to project
    notes = db.Column(db.String(200))

class UserActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    login_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    logout_time = db.Column(db.DateTime)
    duration = db.Column(db.String(50)) # e.g. "2h 15m"
    ip_address = db.Column(db.String(50))
