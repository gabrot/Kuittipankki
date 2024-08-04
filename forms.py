from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, DateField, FileField
from wtforms.validators import DataRequired

class ReceiptForm(FlaskForm):
    description = StringField('Description', validators=[DataRequired()])
    amount = FloatField('Amount', validators=[DataRequired()])
    receipt_date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    file = FileField('Receipt File', validators=[DataRequired()])
