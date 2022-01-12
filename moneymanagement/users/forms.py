# users\forms.py
from os import error
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, IntegerField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length, Regexp
from moneymanagement.models import User

### LOGIN FORM ###
class LoginForm(FlaskForm):
  email = StringField('Email', validators=[DataRequired(), Email()])
  password = PasswordField('Password', validators=[DataRequired()])
  submit = SubmitField('Login')

  def validate_email(self, email) -> None:
    if not User.query.filter_by(email=self.email.data).first():
      raise ValidationError('Email chưa được đăng ký!')
  
  def validate_password(self, email) -> None:
    user = User.query.filter_by(email=self.email.data).first()
    if user is not None and not user.password_check(self.password.data):
      raise ValidationError('Mật khẩu không chính xác!')

### REGISTER FORM ###
class RegisterForm(FlaskForm):
  email = StringField('Email', validators=[DataRequired(), Email(), Length(max=64)])
  username = StringField('Username', validators=[DataRequired(), Length(min=1, max=25), Regexp('^\w+$', message='Không được sử dụng ký tự đặc biệt!')])
  password = PasswordField('Password', validators=[DataRequired(), EqualTo('password_confirm', message='Mật khẩu không khớp!')])
  password_confirm = PasswordField('Confirm Password', validators=[DataRequired()])
  submit = SubmitField('Register')

  def validate_email(self, email) -> None:
    if User.query.filter_by(email=self.email.data).first():
      raise ValidationError('Email đã được đăng ký!')

  def validate_username(self, username) -> None:
    if User.query.filter_by(username=self.username.data).first():
      raise ValidationError('Tên người dùng đã được đăng ký!')
