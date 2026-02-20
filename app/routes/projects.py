from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Project, Material, ProjectMaterial, InventoryMovement, ProjectHistory

projects = Blueprint('projects', __name__)

@projects.route('/projects')
@login_required
def list_projects():
    projects_list = Project.query.all()
    return render_template('projects/list.html', projects=projects_list)

@projects.route('/projects/new', methods=['GET', 'POST'])
@login_required
def new_project():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        project = Project(name=name, description=description)
        db.session.add(project)
        db.session.commit()
        flash('Proyecto planificado. Ahora asigne los materiales necesarios.', 'success')
        return redirect(url_for('projects.manage_materials', id=project.id))
    return render_template('projects/new.html')

@projects.route('/projects/<int:id>/materials', methods=['GET', 'POST'])
@login_required
def manage_materials(id):
    project = Project.query.get_or_404(id)
    all_materials = Material.query.filter_by(is_deleted=False).all()
    
    if request.method == 'POST':
        mat_id = request.form.get('material_id')
        qty = float(request.form.get('quantity'))
        
        # Check stock for warning
        material = Material.query.get(mat_id)
        if material.quantity < qty:
            flash(f'¡Atención! Stock insuficiente para {material.name}. Cantidad disponible: {material.quantity}', 'warning')
        
        # Check if already added (even if deleted)
        existing = ProjectMaterial.query.filter_by(project_id=id, material_id=mat_id).first()
        if existing:
            action = "Material Actualizado" if not existing.is_deleted else "Material Restaurado"
            existing.quantity_required = qty # Update with new quantity
            existing.is_deleted = False # Restore if it was deleted
        else:
            action = "Material Agregado"
            pm = ProjectMaterial(project_id=id, material_id=mat_id, quantity_required=qty)
            db.session.add(pm)
        
        # Log history
        history = ProjectHistory(
            project_id=id, 
            user_id=current_user.id, 
            action=action, 
            details=f"Material: {material.name}, Cantidad: {qty} {material.unit}"
        )
        db.session.add(history)
        
        db.session.commit()
        flash('Material asignado al proyecto.', 'success')
        return redirect(url_for('projects.manage_materials', id=id))
    
    return render_template('projects/manage_materials.html', project=project, materials=all_materials)

@projects.route('/projects/material/<int:pm_id>/remove')
@login_required
def remove_project_material(pm_id):
    pm = ProjectMaterial.query.get_or_404(pm_id)
    project_id = pm.project_id
    pm.is_deleted = True
    
    history = ProjectHistory(
        project_id=project_id, 
        user_id=current_user.id, 
        action="Material Eliminado", 
        details=f"Material: {pm.material.name}"
    )
    db.session.add(history)
    
    db.session.commit()
    flash(f'Material {pm.material.name} removido del proyecto.', 'info')
    return redirect(url_for('projects.manage_materials', id=project_id))

@projects.route('/projects/material/<int:pm_id>/restore')
@login_required
def restore_project_material(pm_id):
    pm = ProjectMaterial.query.get_or_404(pm_id)
    project_id = pm.project_id
    pm.is_deleted = False
    
    history = ProjectHistory(
        project_id=project_id, 
        user_id=current_user.id, 
        action="Material Restaurado", 
        details=f"Material: {pm.material.name}"
    )
    db.session.add(history)
    
    db.session.commit()
    flash(f'Material {pm.material.name} restaurado al proyecto.', 'success')
    return redirect(url_for('projects.manage_materials', id=project_id))

@projects.route('/projects/<int:id>/status/<string:status>')
@login_required
def change_status(id, status):
    project = Project.query.get_or_404(id)
    
    if status == 'En ejecución' and project.status != 'En ejecución':
        # Auto-deduct stock
        for pm in project.materials:
            if pm.is_deleted: continue
            if pm.material.quantity < pm.quantity_required:
                flash(f'Error: Stock insuficiente para {pm.material.name}. Faltan {pm.quantity_required - pm.material.quantity} {pm.material.unit}', 'danger')
                return redirect(url_for('projects.list_projects'))
            
            pm.material.quantity -= pm.quantity_required
            movement = InventoryMovement(
                material_id=pm.material_id,
                quantity=pm.quantity_required,
                type='Sale',
                user_id=current_user.id,
                project_id=id,
                notes=f'Consumo automático: Proyecto {project.name}'
            )
            db.session.add(movement)
        
        project.date_started = datetime.utcnow()

    if status == 'Finalizado' or status == 'Cancelado':
        project.date_ended = datetime.utcnow()
            
    # Log history
    history = ProjectHistory(
        project_id=id, 
        user_id=current_user.id, 
        action="Cambio de Estado", 
        details=f"De {project.status} a {status}"
    )
    db.session.add(history)

    project.status = status
    db.session.commit()
    flash(f'Estado del proyecto actualizado a {status}', 'info')
    return redirect(url_for('projects.list_projects'))

@projects.route('/projects/<int:id>/notes', methods=['POST'])
@login_required
def update_notes(id):
    project = Project.query.get_or_404(id)
    project.notes = request.form.get('notes')
    
    history = ProjectHistory(
        project_id=id, 
        user_id=current_user.id, 
        action="Notas Actualizadas", 
        details="Se modificaron las notas generales del proyecto"
    )
    db.session.add(history)
    
    db.session.commit()
    flash('Notas del proyecto actualizadas.', 'success')
    return redirect(request.referrer or url_for('projects.list_projects'))
