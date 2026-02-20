from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from app import db
from app.models import Material, InventoryMovement
from app.utils.pdf_generator import generate_project_report # I'll add an inventory report function too
import os

inventory = Blueprint('inventory', __name__)

@inventory.route('/inventory')
@login_required
def list_materials():
    materials = Material.query.filter_by(is_deleted=False).all()
    return render_template('inventory/list.html', materials=materials)

@inventory.route('/inventory/add', methods=['GET', 'POST'])
@login_required
def add_material():
    if request.method == 'POST':
        name = request.form.get('name')
        quantity = float(request.form.get('quantity'))
        unit = request.form.get('unit')
        min_stock = float(request.form.get('min_stock'))
        supplier = request.form.get('supplier')
        
        material = Material(name=name, quantity=quantity, unit=unit, min_stock=min_stock, supplier=supplier)
        db.session.add(material)
        db.session.commit()
        
        movement = InventoryMovement(material_id=material.id, quantity=quantity, type='Entra', user_id=current_user.id, notes='Carga inicial')
        db.session.add(movement)
        db.session.commit()
        
        flash('Material registrado exitosamente.', 'success')
        return redirect(url_for('inventory.list_materials'))
    return render_template('inventory/add.html')

@inventory.route('/inventory/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_material(id):
    material = Material.query.get_or_404(id)
    if request.method == 'POST':
        new_qty = float(request.form.get('quantity'))
        
        # Log movement if quantity changed manually
        if new_qty != material.quantity:
            diff = new_qty - material.quantity
            m_type = 'Entra' if diff > 0 else 'Sale'
            movement = InventoryMovement(
                material_id=material.id, 
                quantity=abs(diff), 
                type=m_type, 
                user_id=current_user.id, 
                notes='Ajuste manual en edición'
            )
            db.session.add(movement)
            material.quantity = new_qty

        material.name = request.form.get('name')
        material.unit = request.form.get('unit')
        material.min_stock = float(request.form.get('min_stock'))
        material.supplier = request.form.get('supplier')
        
        db.session.commit()
        flash(f'Material "{material.name}" actualizado.', 'success')
        return redirect(url_for('inventory.list_materials'))
    return render_template('inventory/edit.html', material=material)

@inventory.route('/inventory/<int:id>/delete')
@login_required
def delete_material(id):
    material = Material.query.get_or_404(id)
    material.is_deleted = True
    db.session.commit()
    flash(f'Material "{material.name}" movido a la papelera.', 'info')
    return redirect(url_for('inventory.list_materials'))

@inventory.route('/inventory/trash')
@login_required
def trash():
    deleted_materials = Material.query.filter_by(is_deleted=True).all()
    return render_template('inventory/trash.html', materials=deleted_materials)

@inventory.route('/inventory/<int:id>/restore')
@login_required
def restore_material(id):
    material = Material.query.get_or_404(id)
    material.is_deleted = False
    db.session.commit()
    flash(f'Material "{material.name}" restaurado.', 'success')
    return redirect(url_for('inventory.trash'))

@inventory.route('/inventory/<int:id>/permanent_delete')
@login_required
def permanent_delete_material(id):
    material = Material.query.get_or_404(id)
    db.session.delete(material)
    db.session.commit()
    flash(f'Material "{material.name}" eliminado permanentemente.', 'danger')
    return redirect(url_for('inventory.trash'))
