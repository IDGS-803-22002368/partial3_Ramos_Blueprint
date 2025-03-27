from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required
from auth_blueprint import role_required
from models import db, Proveedor
from forms import ProveedorForm

proveedor_bp = Blueprint('proveedor', __name__)


@proveedor_bp.route('/proveedores')
@login_required
@role_required('proveedor')
def lista_proveedores():
    proveedores = Proveedor.query.all()
    return render_template('proveedor/lista_proveedores.html', proveedores=proveedores)


@proveedor_bp.route('/proveedores/nuevo', methods=['GET', 'POST'])
@login_required
@role_required('proveedor')
def nuevo_proveedor():
    form = ProveedorForm()
    if form.validate_on_submit():
        proveedor = Proveedor(
            nombre=form.nombre.data,
            empresa=form.empresa.data,
            telefono=form.telefono.data,
            email=form.email.data,
            direccion=form.direccion.data
        )
        try:
            db.session.add(proveedor)
            db.session.commit()
            flash('Proveedor creado exitosamente', 'success')
            return redirect(url_for('proveedor.lista_proveedores'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear proveedor: {str(e)}', 'danger')

    return render_template('proveedor/nuevo_proveedor.html', form=form)


@proveedor_bp.route('/proveedores/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('proveedor')
def editar_proveedor(id):
    proveedor = Proveedor.query.get_or_404(id)
    form = ProveedorForm(obj=proveedor)

    if form.validate_on_submit():
        try:
            form.populate_obj(proveedor)
            db.session.commit()
            flash('Proveedor actualizado exitosamente', 'success')
            return redirect(url_for('proveedor.lista_proveedores'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar proveedor: {str(e)}', 'danger')

    return render_template('proveedor/editar_proveedor.html', form=form, proveedor=proveedor)

