# users/views.py
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy import extract
from moneymanagement import db
from moneymanagement.users.forms import LoginForm, RegisterForm
from moneymanagement.models import User, Wallet, Expenditure, Item
# import expenses logic handler

# Create blueprint for users
users_blueprint = Blueprint('users', __name__)

# Đăng ký user
@users_blueprint.route('/register', methods=['GET', 'POST'])
def register():
  form = RegisterForm()
  if form.validate_on_submit():
    new_user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
    db.session.add(new_user)
    db.session.commit()
    flash('Đăng ký thành công!')

    return redirect(url_for('users.login'))
  return render_template('users/register.html', form=form)

# Login user
@users_blueprint.route('/login', methods=['GET', 'POST'])
def login():
  form = LoginForm()
  if form.validate_on_submit():
    user = User.query.filter_by(email=form.email.data).first()
    login_user(user)
    flash(f'"{user.username}" đã đăng nhập thành công!')
    next = request.args.get('next')

    if next is None or not next.startswith('/'):
      next = url_for('core.home', user_id=current_user.id)

    return redirect(next)
  return render_template('users/login.html', form=form)

# Logout user
@users_blueprint.route('/logout')
@login_required
def logout():
  logout_user()
  return redirect(url_for('core.index'))

# Danh sách ví của user
@users_blueprint.route('/<int:user_id>/wallet')
@login_required
def wallet(user_id):
  if current_user.id != user_id:
    abort(403)

  wallets = Wallet.query.filter_by(user_id=user_id)

  return render_template('users/wallet.html', wallets=wallets)

# Danh sách các danh mục của user
@users_blueprint.route('/<int:user_id>/item')
@login_required
def item(user_id):
  '''
  Lấy danh sách các danh mục chi của người dùng theo từng tháng hiện tại.
  Sử dụng datetime.utcnow() để lấy thông tin ngày tháng hiện tại.
  Sử dụng tháng và năm hiện tại để làm điều kiện lấy dữ liệu từ database.
  '''
  if current_user.id != user_id:
    abort(403)
  # Khởi tạo giá trị date để chứa thời gian hiện tại
  date = datetime.utcnow().strftime('%Y-%m')
  # Khởi tạo biến page dùng cho pagination
  page = request.args.get('page', 1, type=int)
  # Lấy thông tin danh mục từ người dùng
  items = Item.query.filter_by(user_id=user_id).paginate(page=page, per_page=10)

  return render_template('users/item.html', items=items, date=date)

# Lọc các khoản chi của từng danh mục trong 1 khoản thời gian nhất định
@users_blueprint.route('/<int:user_id>/filter/<date>')
@login_required
def item_filter(user_id, date):
  '''
  Giống như hàm item(), nhưng nhận giá trị date từ user input và lọc theo khoảng
  thời gian người dùng đã chọn
  '''
  if current_user.id != user_id:
    abort(403)
  # Khởi tạo biến page dùng cho pagination
  page = request.args.get('page', 1, type=int)
  # Lấy thông tin danh mục từ người dùng
  items = Item.query.filter_by(user_id=user_id).paginate(page=page, per_page=5)

  return render_template('users/item.html', items=items, date=date, item_filter=True)

# Danh sách các khoản chi của user
@users_blueprint.route('/<int:user_id>/expenses')
@login_required
def expense(user_id):
  '''
  Lấy danh sách các khoản chi của người dùng theo từng tháng hiện tại.
  Sử dụng datetime.utcnow() để lấy thông tin ngày tháng hiện tại.
  Sử dụng tháng và năm hiện tại để làm điều kiện lấy dữ liệu từ database.
  '''
  if current_user.id != user_id:
    abort(403)
  
  # Khởi tạo biến date để lưu thông tin tháng năm hiện tại.
  date = datetime.utcnow().strftime('%Y-%m')
  # Khởi tạo biến page để chứa thông tin pagination.
  page = request.args.get('page', 1, type=int)
  # Lấy thông tin khoản chi của user dựa vào tháng và năm hiện tại.
  expenses = Expenditure.query.filter(Expenditure.user_id == user_id).filter(extract('year', Expenditure.date) == int(date[:4])).filter(extract('month', Expenditure.date) == int(date[5:])).order_by(Expenditure.date.desc()).paginate(page=page, per_page=10)

  return render_template('users/expense.html', expenses=expenses, date=date)

# Lọc các khoản chi của người dùng trong 1 khoản thời gian nhất định
@users_blueprint.route('/<int:user_id>/filter/<date_from>/<date_to>')
@login_required
def expense_filter(user_id, date_from, date_to):
  if current_user.id != user_id:
    abort(403)

  page = request.args.get('page', 1, type=int)
  expenses = Expenditure.query.filter(Expenditure.user_id == user_id).filter(Expenditure.date >= date_from).filter(Expenditure.date <= date_to).order_by(Expenditure.date.desc()).paginate(page=page, per_page=5)

  return render_template('users/expense.html', expenses=expenses)
