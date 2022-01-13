# items/forms.py
from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, SubmitField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, ValidationError, Length
from wtforms_alchemy.fields import QuerySelectField
from moneymanagement.models import Item, Wallet

class AddItemForm(FlaskForm):
  name = StringField('Name', validators=[DataRequired(), Length(min=1, max=32)])
  wallet_id = QuerySelectField('Item', query_factory=lambda: Wallet.query.filter(Wallet.user_id == current_user.id), get_label='name', validators=[DataRequired()])
  submit = SubmitField('Submit')

  def validate_name(self, name) -> None:
    if Item.query.filter_by(user_id=current_user.id, name=self.name.data).first():
      raise ValidationError('Tên danh mục đã được tạo!')

class UpdateItemForm(FlaskForm):
  name = StringField('Name', validators=[DataRequired(), Length(min=1, max=32)])
  submit = SubmitField('Submit')

  def validate_name(self, name) -> None:
    if Item.query.filter_by(user_id=current_user.id, name=self.name.data).first():
      raise ValidationError('Tên danh mục đã được tạo!')

class FilterItemForm(FlaskForm):
  condition = DateField('Condition', validators=[DataRequired()], format='%Y-%m-%d')
  submit = SubmitField('Submit')