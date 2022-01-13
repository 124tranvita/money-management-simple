# core/views.py
from datetime import datetime
from flask.helpers import url_for
from sqlalchemy import extract
from flask import Blueprint, render_template, abort, session
from flask_login import login_required, current_user
from werkzeug.utils import redirect
from moneymanagement.models import Expenditure, TrackBalance, Wallet, Item
from moneymanagement.handler.chart import month_report, month_report_in_percent

# Create blueprint for core views
core_blueprint = Blueprint('core', __name__)

# Index View
@core_blueprint.route('/')
def index():
  return render_template('index.html')

# Home View (trang thống kê)
@core_blueprint.route('/<int:user_id>/home')
@login_required
def home(user_id):
  '''
  Thông tin trên Dashboard sẽ là thông tin thống kê theo từng tháng hiện tại
  dựa vào biến 'date' và hàm datetime.utcnow()
  '''
  # Nếu id của người dùng hiện tại không trùng với id nhập vào -> abort(403)
  if user_id != current_user.id:
    abort(403)

  # Nếu người dùng hiện tại chưa có ví -> show warning message yêu cầu tạo ví
  if not Wallet.query.filter_by(user_id=user_id).first():
    return redirect(url_for('errors.wallet_require'))

  # Khởi tạo biến 'date' và dùng hàm datetime.utcnow() để lưu thời gian hiện tại
  date = datetime.utcnow().strftime('%Y-%m')
  # Lấy danh sách ví của người dùng dựa vào user id
  wallet = Wallet.query.filter_by(user_id=user_id).first()
  # Lấy các danh mục chi của người dùng dưak vào user id
  items = Item.query.filter_by(user_id=user_id)
  # Lấy bản thống kê các khoản thu nhập từ ví dựa vào wallet id
  tracks = TrackBalance.query.filter_by(wallet_id=wallet.id)
  
  # Lấy danh sách các khoản chi từ database và lọc theo tháng hiện tại, sắp xếp theo thời gian mới nhất
  expenses_date = Expenditure.query.filter(Expenditure.user_id == user_id).filter(extract('year', Expenditure.date) == int(date[:4])).filter(extract('month', Expenditure.date) == int(date[5:])).order_by(Expenditure.date.desc())
  
  # Dùng hàm report để trả về dict{'ngày':'tổng khoản chi'} của tháng hiện tại
  report = month_report(user_id)
  # Dùng hàm month_report_in_percent để trả về dict{'ngày':['tổng khoản chi', '% trên tồng khoản chi]} của tháng hiện tại
  report_in_percent = month_report_in_percent(report)

  return render_template('home.html', expenses_date=expenses_date, wallet=wallet, tracks=tracks, items=items, user_id=user_id, date=date, report=report, report_in_percent=report_in_percent)

# About View
@core_blueprint.route('/about')
def about():
  return render_template('about.html')