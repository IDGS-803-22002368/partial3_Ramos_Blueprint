from flask_sqlalchemy import SQLAlchemy
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Proveedor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    empresa = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    direccion = db.Column(db.String(200))


class Venta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, default=datetime.datetime.now)
    nombre_cliente = db.Column(db.String(100))
    direccion_cliente = db.Column(db.String(100))
    telefono_cliente = db.Column(db.String(100))
    total_venta = db.Column(db.Float, default=0.0)
    detalles = db.relationship('DetallePizza', backref='venta')


class DetallePizza(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    venta_id = db.Column(db.Integer, db.ForeignKey('venta.id'))
    tamano = db.Column(db.String(20))
    cantidad = db.Column(db.Integer, default=1)
    subtotal = db.Column(db.Float)
    ingredientes = db.relationship(
        'IngredientePizza', backref='detalle_pizza')


class IngredientePizza(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    detalle_pizza_id = db.Column(db.Integer, db.ForeignKey('detalle_pizza.id'))
    nombre_ingrediente = db.Column(db.String(50))
