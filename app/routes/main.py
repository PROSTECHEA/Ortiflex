from flask import Blueprint, render_template, send_file
from flask_login import login_required
from app.models import Material, Project
from app.utils.pdf_generator import generate_inventory_report, generate_project_report
import os

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/dashboard')
@login_required
def dashboard():
    materials_count = Material.query.count()
    projects_count = Project.query.count()
    low_stock = Material.query.filter(Material.quantity <= Material.min_stock).all()
    active_projects = Project.query.filter_by(status='En ejecución').all()
    return render_template('dashboard.html', materials_count=materials_count, 
                           projects_count=projects_count, low_stock=low_stock,
                           active_projects=active_projects)

@main.route('/report/inventory')
@login_required
def inventory_report():
    materials = Material.query.all()
    filename = generate_inventory_report(materials)
    path = os.path.join(os.getcwd(), "app", "static", "reports", filename)
    return send_file(path, mimetype='application/pdf')

@main.route('/report/project/<int:id>')
@login_required
def project_report(id):
    project = Project.query.get_or_404(id)
    filename = generate_project_report(project)
    path = os.path.join(os.getcwd(), "app", "static", "reports", filename)
    return send_file(path, mimetype='application/pdf')
