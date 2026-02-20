from flask import Blueprint, render_template, request, jsonify, url_for
from flask_login import login_required
from app.models import Project, ProjectHistory
from app import db

reports = Blueprint('reports', __name__)

@reports.route('/reports')
@login_required
def search():
    page = request.args.get('page', 1, type=int)
    query = request.args.get('q', '')
    status = request.args.get('status', '')
    
    projects_query = Project.query
    
    if query:
        projects_query = projects_query.filter(Project.name.contains(query))
    
    if status:
        projects_query = projects_query.filter_by(status=status)
    
    pagination = projects_query.order_by(Project.date_created.desc()).paginate(
        page=page, per_page=5, error_out=False
    )
    
    return render_template('reports/search.html', 
                           projects=pagination.items, 
                           pagination=pagination, 
                           query=query, 
                           status=status)

@reports.route('/reports/autocomplete')
@login_required
def autocomplete():
    query = request.args.get('q', '')
    projects = Project.query.filter(Project.name.contains(query)).limit(10).all()
    suggestions = [p.name for p in projects]
    return jsonify(suggestions)

@reports.route('/reports/project/<int:id>')
@login_required
def project_audit(id):
    project = Project.query.get_or_404(id)
    return render_template('reports/audit.html', project=project)
