from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
from app.models import Customer


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class SectionForm(FlaskForm):
    body = StringField('Body', validators=[DataRequired()])
    submit = SubmitField('Enter new section and note')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = Customer.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = Customer.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class LoadPartForm(FlaskForm):
    stocknumber = IntegerField('Stock No.',validators=[DataRequired()])
    brand = StringField('Brand',validators=[DataRequired()])
    category = StringField('Category',validators=[DataRequired()])
    price = IntegerField('Price',validators=[DataRequired()])
    submit = SubmitField('Load New Part')

class SearchByBrandForm(FlaskForm):
    brand = StringField('Brand',validators=[DataRequired()])
    submit = SubmitField('Search By Brand')

class SearchByStkNoForm(FlaskForm):
    stocknumber = IntegerField('Stock No.',validators=[DataRequired()])
    submit = SubmitField('Search By Stock Number')

class OrderForm(FlaskForm):
    stocknumber = IntegerField('Enter Stock Number to Order',validators=[DataRequired()])
    submit = SubmitField('Order by Stock Number')

