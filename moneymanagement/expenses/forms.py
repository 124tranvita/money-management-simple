# expenses/forms.py
from datetime import datetime
from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, TextAreaField, IntegerField, SubmitField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Length, ValidationError
from wtforms_alchemy.fields import QuerySelectField
from moneymanagement.models import Item

class AddExpenditureForm(FlaskForm):
  name = StringField('Name', validators=[DataRequired(), Length(min=1, max=32)])
  date = DateField('Date', validators=[DataRequired()], default=datetime.today(), format='%Y-%m-%d')
  description = TextAreaField('Description', validators=[Length(max=128)])
  amount = IntegerField('Amount', validators=[DataRequired()])
  item_id = QuerySelectField('Item', query_factory=lambda: Item.query.filter(Item.user_id == current_user.id), get_label='name', validators=[DataRequired()])
  submit = SubmitField('Submit')

  def validate_date(self, date):
    if self.date.data.strftime('%Y-%m-%d') > datetime.today().strftime('%Y-%m-%d'):
      raise ValidationError('Khoản chi nằm ngoài thời gian!')
    pass

class UpdateExpenditureForm(FlaskForm):
  name = StringField('Name', validators=[DataRequired(), Length(min=1, max=32)])
  date = DateField('Date', validators=[DataRequired()])
  description = TextAreaField('Description', validators=[Length(max=128)])
  amount = IntegerField('Amount', validators=[DataRequired()])
  item_id = QuerySelectField('Item', query_factory=lambda: Item.query.filter(Item.user_id == current_user.id), get_label='name', validators=[DataRequired()])
  submit = SubmitField('Submit')

### FILTER FORM ###
class FilterByTimeForm(FlaskForm):
  date_from = DateField('Amount', validators=[DataRequired()], format='%Y-%m-%d')
  date_to = DateField('Amount', validators=[DataRequired()], format='%Y-%m-%d')
  submit = SubmitField('Submit', )