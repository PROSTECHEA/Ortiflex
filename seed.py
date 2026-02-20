from app import create_app, db
from app.models import Material, Project, User, ProjectMaterial
import bcrypt
import os

app = create_app()

def seed_data():
    # Remove database if exists to ensure clean slate
    # Note: we are using the app context which might have it open, 
    # but we will try to recreate tables first.
    with app.app_context():
        db.drop_all()
        db.create_all()
        
        # Create Admin
        hashed_pw = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        admin = User(username='admin', email='admin@ortiflex.com', password=hashed_pw, role='Admin', can_manage_users=True)
        db.session.add(admin)
        
        # Create Operativo
        operador_pw = bcrypt.hashpw('op123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        operador = User(username='operador', email='operador@ortiflex.com', password=operador_pw, role='Operativo', can_manage_users=False, can_view_reports=False)
        db.session.add(operador)
        
        # Materials
        m1 = Material(name='Tinta Flexográfica Cyan', quantity=15.5, unit='Litros', min_stock=5, supplier='Chimicolor')
        m2 = Material(name='Sustrato Autoadhesivo Mate', quantity=120, unit='Metros', min_stock=50, supplier='Sustratos Vzla')
        m3 = Material(name='Tinta Flexográfica Negra', quantity=2, unit='Litros', min_stock=10, supplier='Chimicolor')
        m4 = Material(name='Adhesivo Hotmelt', quantity=5, unit='Kg', min_stock=10, supplier='Químicos Sur')
        
        db.session.add_all([m1, m2, m3, m4])
        db.session.commit()
        
        from datetime import datetime, timedelta
        # Projects
        p1 = Project(name='Etiquetas Agua Minalba 500ml', description='Pedido de 50.000 unidades.', status='En ejecución', date_started=datetime.utcnow() - timedelta(days=1))
        p2 = Project(name='Etiquetas Alimentos Polar', description='Prueba de color.', status='Planificado')
        
        db.session.add_all([p1, p2])
        db.session.commit()
        
        # History for p1
        from app.models import ProjectHistory
        h1 = ProjectHistory(project_id=p1.id, user_id=admin.id, action='Proyecto Creado', details='Creación inicial', date=datetime.utcnow() - timedelta(days=2))
        h2 = ProjectHistory(project_id=p1.id, user_id=admin.id, action='Cambio de Estado', details='De Planificado a En ejecución', date=datetime.utcnow() - timedelta(days=1))
        db.session.add_all([h1, h2])
        db.session.commit()
        
        # Project Materials
        pm1 = ProjectMaterial(project_id=p1.id, material_id=m1.id, quantity_required=5.0)
        pm2 = ProjectMaterial(project_id=p2.id, material_id=m1.id, quantity_required=10.0)
        
        db.session.add_all([pm1, pm2])
        db.session.commit()
        
        print("Database re-initialized and seed data added successfully!")

if __name__ == '__main__':
    seed_data()
