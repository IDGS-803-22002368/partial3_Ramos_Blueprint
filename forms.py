from wtforms import Form
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, RadioField, SelectMultipleField, widgets
from wtforms import validators
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from models import User


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(message='Username is required'),
        Length(min=4, max=50, message='Username must be between 4 and 50 characters')
    ])
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Invalid email address')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=6, message='Password must be at least 6 characters long')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message='Confirm password is required'),
        EqualTo('password', message='Passwords must match')
    ])
    role = SelectField('Role', choices=[
        ('empleado', 'Empleado'),
        ('proveedor', 'Proveedor')
    ], validators=[DataRequired(message='Role is required')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already exists')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(message='Username is required')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required')
    ])
    submit = SubmitField('Login')


class ProveedorForm(FlaskForm):
    nombre = StringField('Nombre', validators=[
        DataRequired(message='Nombre es requerido'),
        Length(min=4, max=100, message='Nombre debe tener entre 4 y 100 caracteres')
    ])
    empresa = StringField('Empresa', validators=[
        DataRequired(message='Empresa es requerida'),
        Length(min=2, max=100, message='Empresa debe tener entre 2 y 100 caracteres')
    ])
    telefono = StringField('Teléfono', validators=[
        DataRequired(message='Teléfono es requerido'),
        Length(min=7, max=20, message='Teléfono debe tener entre 7 y 20 caracteres')
    ])
    email = StringField('Email', validators=[
        DataRequired(message='Email es requerido'),
        Email(message='Email inválido')
    ])
    direccion = StringField('Dirección', validators=[
        Length(max=200, message='Dirección no puede exceder 200 caracteres')
    ])
    submit = SubmitField('Guardar')


class ClienteForm(FlaskForm):
    nombre = StringField('Nombre', [
        validators.DataRequired(message='El nombre es requerido'),
        validators.length(
            min=4, max=25, message='El nombre debe tener entre 4 y 25 caracteres')
    ])
    direccion = StringField('Dirección', [
        validators.DataRequired(message='La dirección es requerida'),
        validators.length(
            min=4, max=100, message='La dirección debe tener entre 4 y 100 caracteres')
    ])
    telefono = StringField('Teléfono', [
        validators.DataRequired(message='El teléfono es requerido'),
        validators.length(
            min=7, max=12, message='El teléfono debe tener entre 7 y 12 caracteres')
    ])


class PizzaForm(FlaskForm):
    tamano = RadioField(
        'Tamaño',
        choices=[('pequena', 'Pequeña ($40)'),
                 ('mediana', 'Mediana ($80)'),
                 ('grande', 'Grande ($120)')],
        default='mediana',
        validators=[validators.DataRequired(message='El tamaño es requerido')])

    ingredientes = SelectMultipleField(
        'Ingredientes ($10 cada uno)',
        choices=[
            ('jamon', 'Jamón'),
            ('pina', 'Piña'),
            ('champinones', 'Champiñones')
        ],
        option_widget=widgets.CheckboxInput(),
        widget=widgets.ListWidget(prefix_label=False)
    )

    numPizzas = IntegerField('Número de pizzas', [
        validators.DataRequired(message='El número de pizzas es requerido'),
        validators.NumberRange(
            min=1, max=100, message='El número de pizzas debe ser entre 1 y 100')
    ], default=1)
