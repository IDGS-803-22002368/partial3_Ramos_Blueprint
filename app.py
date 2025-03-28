from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, login_required, current_user
from config import DevelopmentConfig
from models import db, User, Venta, DetallePizza, IngredientePizza
from forms import PizzaForm, ClienteForm
from datetime import datetime
import calendar
from sqlalchemy import extract
from forms import LoginForm
from flask import Blueprint
from flask_login import login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

auth_bp = Blueprint('auth', __name__)


def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role != role:
                flash('No tienes permiso para acceder a esta página', 'danger')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    from forms import RegistrationForm

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            role=form.role.data
        )
        user.set_password(form.password.data)

        try:
            db.session.add(user)
            db.session.commit()
            flash('Registro exitoso. Por favor inicia sesión.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error en el registro: {str(e)}', 'danger')

    return render_template('register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')

            if user.role == 'proveedor':
                return redirect(url_for('proveedor.lista_proveedores'))

            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash(
                'Inicio de sesión fallido. Por favor verifica tu usuario y contraseña', 'danger')
    return render_template('login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión', 'info')
    return redirect(url_for('index'))


proveedor_bp = Blueprint('proveedor', __name__)


@proveedor_bp.route('/proveedores')
@login_required
@role_required('proveedor')
def lista_proveedores():
    from models import Proveedor
    proveedores = Proveedor.query.all()
    return render_template('lista_proveedores.html', proveedores=proveedores)


@proveedor_bp.route('/proveedores/nuevo', methods=['GET', 'POST'])
@login_required
@role_required('proveedor')
def nuevo_proveedor():
    from forms import ProveedorForm
    from models import Proveedor

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

    return render_template('nuevo_proveedor.html', form=form)


@proveedor_bp.route('/proveedores/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('proveedor')
def editar_proveedor(id):
    from forms import ProveedorForm
    from models import Proveedor

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

    return render_template('editar_proveedor.html', form=form, proveedor=proveedor)


@proveedor_bp.route('/proveedores/eliminar/<int:id>', methods=['POST'])
@login_required
@role_required('proveedor')
def eliminar_proveedor(id):
    from models import Proveedor

    proveedor = Proveedor.query.get_or_404(id)
    try:
        db.session.delete(proveedor)
        db.session.commit()
        flash('Proveedor eliminado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar proveedor: {str(e)}', 'danger')

    return redirect(url_for('proveedor.lista_proveedores'))

PRECIOS = {
    'pequena': 40,
    'mediana': 80,
    'grande': 120
}

COSTO_INGREDIENTE = 10

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
csrf = CSRFProtect()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(proveedor_bp)

def agregarPizza(tamano, cantidad, ingredientes):
    ingredientes_lista = ",".join(ingredientes)
    with open("pedidos.txt", "a", encoding="utf-8") as archivo:
        archivo.write(f"{tamano}|{cantidad}|{ingredientes_lista}\n")


def cargarCarrito():
    carrito = []
    try:
        with open("pedidos.txt", "r", encoding="utf-8") as archivo:
            for linea in archivo:
                datos = linea.strip().split("|")
                if len(datos) >= 3:
                    carrito.append({
                        "tamano": datos[0],
                        "cantidad": datos[1],
                        "ingredientes": datos[2].split(",") if datos[2] else []
                    })
    except FileNotFoundError:
        with open("pedidos.txt", "w", encoding="utf-8") as archivo:
            pass
    return carrito


def eliminarPizzaEspecifica(indice):
    carrito = cargarCarrito()
    if 0 <= indice < len(carrito):
        carrito.pop(indice)
        with open("pedidos.txt", "w", encoding="utf-8") as archivo:
            for pizza in carrito:
                ingredientes_lista = ",".join(pizza["ingredientes"])
                archivo.write(
                    f"{pizza['tamano']}|{pizza['cantidad']}|{ingredientes_lista}\n")
        return True
    return False


def vaciarCarrito():
    open("pedidos.txt", "w").close()

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(401)
def unauthorized(error):
    flash('Por favor inicia sesión para acceder a esta página', 'warning')
    return redirect(url_for('auth.login'))

@app.route("/", methods=['GET', 'POST'])
@login_required
@role_required('empleado')
def index():
    from forms import PizzaForm, ClienteForm

    pizza_form = PizzaForm()
    cliente_form = ClienteForm()

    fecha_seleccionada = request.args.get('fecha')
    if fecha_seleccionada:
        try:
            fecha_filtrada = datetime.strptime(
                fecha_seleccionada, '%Y-%m-%d').date()
        except ValueError:
            flash("Formato de fecha inválido", "danger")
            return redirect(url_for('index'))
    else:
        fecha_filtrada = datetime.today().date()
        
    ventas = Venta.query.filter(db.func.date(
        Venta.fecha) == fecha_filtrada).all()

    titulo_ventas = f"Ventas del Día ({fecha_filtrada.strftime('%d/%m/%Y')})"
    total_ventas = sum(venta.total_venta for venta in ventas)

    return render_template('index.html',
                           pizza_form=pizza_form,
                           cliente_form=cliente_form,
                           ventas=ventas,
                           titulo_ventas=titulo_ventas,
                           total_ventas=total_ventas,
                           fecha_seleccionada=fecha_seleccionada)


@app.route('/finalizarPedido', methods=['GET', 'POST'])
@login_required
@role_required('empleado')
def finalizarPedido():
    from forms import ClienteForm

    cliente_form = ClienteForm()
    pizzas = cargarCarrito()

    if not pizzas:
        flash("No hay pizzas en el carrito", "danger")
        return redirect(url_for('index'))

    if request.method == 'POST':
        if cliente_form.validate_on_submit():
            nombre = cliente_form.nombre.data
            direccion = cliente_form.direccion.data
            telefono = cliente_form.telefono.data

            session['cliente_data'] = {
                'nombre': nombre,
                'direccion': direccion,
                'telefono': telefono
            }
        elif 'cliente_data' in session:
            nombre = session['cliente_data'].get('nombre')
            direccion = session['cliente_data'].get('direccion')
            telefono = session['cliente_data'].get('telefono')
        else:
            flash("Por favor complete los datos del cliente", "danger")
            return redirect(url_for('index'))

        if not nombre or not direccion or not telefono:
            flash("Por favor complete todos los datos del cliente", "danger")
            return redirect(url_for('index'))

        subtotal_total = 0
        for pizza in pizzas:
            precio_inicial = PRECIOS[pizza["tamano"]]
            precio_ingredientes = len(
                pizza["ingredientes"]) * COSTO_INGREDIENTE
            subtotal_pieza = precio_inicial + precio_ingredientes
            subtotal_total += subtotal_pieza * int(pizza["cantidad"])

        nueva_venta = Venta(
            nombre_cliente=nombre,
            direccion_cliente=direccion,
            telefono_cliente=telefono,
            total_venta=subtotal_total
        )

        db.session.add(nueva_venta)
        db.session.flush()

        for pizza in pizzas:
            precio_inicial = PRECIOS[pizza["tamano"]]
            precio_ingredientes = len(
                pizza["ingredientes"]) * COSTO_INGREDIENTE
            subtotal_pieza = precio_inicial + precio_ingredientes
            subtotal_total_pizza = subtotal_pieza * int(pizza["cantidad"])

            detalle = DetallePizza(
                venta_id=nueva_venta.id,
                tamano=pizza["tamano"],
                cantidad=pizza["cantidad"],
                subtotal=subtotal_total_pizza
            )

            db.session.add(detalle)
            db.session.flush()

            for ingrediente in pizza["ingredientes"]:
                ing = IngredientePizza(
                    detalle_pizza_id=detalle.id,
                    nombre_ingrediente=ingrediente
                )
                db.session.add(ing)

        try:
            db.session.commit()
            vaciarCarrito()
            session.pop('cliente_data', None)
            flash("Pedido finalizado correctamente", "success")
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error al procesar el pedido: {str(e)}", "danger")
            return redirect(url_for('index'))

    return redirect(url_for('index'))


@app.route('/eliminar_pizza/<int:indice>', methods=['POST'])
@login_required
@role_required('empleado')
def eliminar_pizza(indice):
    if eliminarPizzaEspecifica(indice):
        flash("Pizza eliminada del carrito", "success")
    else:
        flash("No se pudo eliminar la pizza", "danger")
    return redirect(url_for('index'))


@app.route('/eliminar_carrito', methods=['POST'])
@login_required
@role_required('empleado')
def eliminar_carrito():
    vaciarCarrito()
    flash("Carrito vaciado correctamente", "info")
    return redirect(url_for('index'))


if __name__ == '__main__':
    csrf.init_app(app)
    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.run()
