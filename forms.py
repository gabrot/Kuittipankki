from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DecimalField, DateField, FileField, SelectField, SelectMultipleField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo, NumberRange, Optional
from flask_wtf.file import FileRequired, FileAllowed

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=50)])
    password = PasswordField('Password', validators=[DataRequired()])

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=255)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])

class VendorForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    address = StringField('Address')
    phone = StringField('Phone')

class ReceiptForm(FlaskForm):
    description = StringField('Description', validators=[DataRequired(), Length(max=255)])
    amount = DecimalField('Total Amount', validators=[DataRequired(), NumberRange(min=0)])
    receipt_date = DateField('Receipt Date', validators=[DataRequired()])
    file = FileField('Receipt File', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png', 'jpeg', 'pdf'], 'Images and PDFs only!')
    ])
    category = SelectField('Category', coerce=int, validators=[DataRequired()])
    vendor = SelectField('Vendor', coerce=int)
    payment_method = SelectField('Payment Method', coerce=int, validators=[DataRequired()])
    tags = SelectMultipleField('Tags', coerce=int)

class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=255)])

class TagForm(FlaskForm):
    name = StringField('Tag Name', validators=[DataRequired(), Length(max=50)])

class PaymentMethodForm(FlaskForm):
    name = StringField('Payment Method Name', validators=[DataRequired(), Length(max=50)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=255)])

class DateRangeForm(FlaskForm):
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])