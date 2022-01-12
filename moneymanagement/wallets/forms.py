# wallets/forms.py
from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, IntegerField, SubmitField, TextAreaField, SelectField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Length, ValidationError
from moneymanagement.models import Wallet

class CreateWalletForm(FlaskForm):
  name = StringField('Wallet Name', validators=[DataRequired(), Length(min=1, max=16)])
  balance = IntegerField('Balance', default=0)
  filter = SelectField('Filter', choices=[(1, 'Tuần'), (2, 'Tháng'), (3, 'Năm')], default=2, validators=[DataRequired()])
  submit = SubmitField('Create')

  def validate_name(self, name) -> None:
    if Wallet.query.filter_by(user_id=current_user.id, name=self.name.data).first():
      raise ValidationError('Tên ví đã tồn tại!')

class UpdateWalletForm(FlaskForm):
  name = StringField('Wallet Name', validators=[DataRequired(), Length(min=1, max=16)])
  filter = SelectField('Filter', choices=[(1, 'Tuần'), (2, 'Tháng'), (3, 'Năm')], default=2, validators=[DataRequired()])
  submit = SubmitField('Create')
  # Thêm vào validate cho field name nếu người dùng cập nhật tên ví trùng với tên ví khác (in-progress)

class AddWalletForm(FlaskForm):
  description = TextAreaField('Description', validators=[DataRequired()])
  balance = IntegerField('Balance', default=0)
  submit = SubmitField('Update')

class FilterWalletForm(FlaskForm):
  condition = SelectField('Condition', choices=[(1, 'Tuần'), (2, 'Tháng'), (3, 'Năm')], validators=[DataRequired()])
  value = DateField('Value', format='%Y-%m-%d', validators=[DataRequired()])
  submit = SubmitField('Submit')