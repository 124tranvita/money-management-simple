# wallets/views.py
from datetime import datetime
from flask import Blueprint, redirect, render_template, url_for, flash, request, abort
from flask_login import login_required, current_user
from sqlalchemy import extract
from moneymanagement import db
from moneymanagement.models import Expenditure, Item, Wallet, TrackBalance, MoneySaving
from moneymanagement.wallets.forms import CreateWalletForm, AddWalletForm, FilterWalletForm, UpdateWalletForm

wallets_blueprint = Blueprint('wallets', __name__)

# Tạo ví
@wallets_blueprint.route('/<int:user_id>/wallet_create', methods=['GET', 'POST'])
@login_required
def create(user_id):
  if Wallet.query.filter_by(user_id = user_id).first():
    return redirect(url_for('errors.already_have_wallet'))

  form = CreateWalletForm()

  if form.validate_on_submit():
    new_wallet = Wallet(name=form.name.data,
                        balance=form.balance.data,
                        filter=form.filter.data,
                        user_id=user_id)
    db.session.add(new_wallet)
    db.session.commit()
    flash('Ví đã được tạo!')
    # Tạo TrackBalance table đồng thời khi có bất kỳ Wallet object nào được khởi tạo
    wallet = Wallet.query.order_by(Wallet.id.desc()).first()
    new_track = TrackBalance(date=datetime.utcnow(),
                            balance=wallet.balance,
                            description='Khởi tạo',
                            wallet_id=wallet.id)
    db.session.add(new_track)
    db.session.commit()

    return redirect(url_for('users.wallet', user_id=user_id))

  return render_template('wallets/create.html', form=form, user_id=user_id)

# Xoá ví
@wallets_blueprint.route('/<int:wallet_id>/delete')
@login_required
def delete(wallet_id):
  wallet = Wallet.query.get_or_404(wallet_id)
  if wallet.items.first():
    return redirect(url_for('errors.wallet_have_item'))

  track_wallets = TrackBalance.query.filter_by(wallet_id=wallet_id).all()

  if current_user.id != wallet.user_id:
    abort(403)

  db.session.delete(wallet)
  # Delete all track-wallet record belong to wallet
  for track_record in track_wallets:
    db.session.delete(track_record)

  db.session.commit()
  flash('Ví đã được xoá!')

  return redirect(url_for('users.wallet', user_id=current_user.id))

# Cập nhật thông tin ví
@wallets_blueprint.route('/<int:user_id>/<int:wallet_id>/update', methods=['GET', 'POST'])
@login_required
def update(user_id, wallet_id):
  # Lấy thông tin ví
  wallet = Wallet.query.get_or_404(wallet_id)
  # Kiểm tra liên kết ví với người dùng thông qua user id, nếu ví thuộc user -> next step, nếu không -> error
  if wallet.user_id != user_id:
    abort(403)

  form = UpdateWalletForm()

  if form.validate_on_submit():
    # Cập nhật thông tin cho ví
    wallet.name = form.name.data
    wallet.filter = form.filter.data

    db.session.commit()
    flash('Ví đã được cập nhật!')

    return redirect(url_for('wallets.manage', user_id=user_id, wallet_id=wallet_id))

  elif request.method == 'GET':
    form.name.data = wallet.name
    form.filter.data = wallet.filter

  return render_template('wallets/update.html', form=form, wallet=wallet)

# Cập nhật số dư cho ví
@wallets_blueprint.route('/<int:wallet_id>/add', methods=['GET', 'POST'])
@login_required
def add(wallet_id):
  form = AddWalletForm()
  wallet = Wallet.query.get_or_404(wallet_id)

  if form.validate_on_submit():
    wallet.balance += form.balance.data
    db.session.commit()
    flash('Cập nhật số dư thành công!')
    # Tạo record để theo dõi ngân sách đã được thêm vào
    new_track = TrackBalance(date=datetime.utcnow(),
                            balance=form.balance.data,
                            description=form.description.data,
                            wallet_id=wallet.id)
    db.session.add(new_track)
    db.session.commit()
    
    return redirect(url_for('wallets.manage', user_id=current_user.id, wallet_id=wallet_id))

  return render_template('wallets/add.html',form=form, wallet=wallet)

# Quản lý thông tin chi tiết về ví
@wallets_blueprint.route('/<int:user_id>/<int:wallet_id>/manage_wallet', methods=['GET', 'POST'])
@login_required
def manage(user_id, wallet_id):
  # Lấy thông tin ví của người dùng dựa vào current user id và wallet id của user
  wallet = Wallet.query.filter_by(user_id=user_id, id=wallet_id).first_or_404()
  # Khởi tạo giá trị và gán tháng và năm hiện tại cho biến (không gán ngày)
  date = datetime.utcnow()
  # Khởi tạo giá trị page cho Track Balance table
  tb_page = request.args.get('tb_page', 1, type=int)
  # Lọc date theo filter đã được chọn bởi user
  if wallet.filter == 1:
    return redirect(url_for('errors.not_support'))

  if wallet.filter == 2:
    date = date.strftime('%Y-%m')
    # Lọc thông track balance theo tháng và năm trong trường hợp bộ lọc tháng được chọn
    track_info = TrackBalance.query.filter(TrackBalance.wallet_id == wallet_id).filter(extract('year', TrackBalance.date) == int(date[:4])).filter(extract('month', TrackBalance.date) == int(date[5:])).order_by(TrackBalance.date.desc()).paginate(page=tb_page, per_page=5)

  if wallet.filter == 3:
    date = date.strftime('%Y')
    # Lọc thông track balance theo năm trong trường hợp bộ lọc năm được chọn
    track_info = TrackBalance.query.filter(TrackBalance.wallet_id == wallet_id).filter(extract('year', TrackBalance.date) == int(date[:4])).order_by(TrackBalance.date.desc()).paginate(page=tb_page, per_page=5)

  # Lấy thông tin về các khoản chi của người dùng (sử dụng danh mục chi)
  item_info = Item.query.filter_by(user_id=user_id)

  # Lọc thông tin các khoản chi dụa vào biến date và điều kiện filter
  # expense_info = [] # Khởi tạo danh sách chứa các object được query từ Expenditure table dựa theo date condition
  # expenses = Expenditure.query.filter_by(user_id=user_id)
  # for expense in expenses:
  #   if date in expense.date.strftime('%Y-%m-%d'):
  #     expense_info.append(expense)
  
  return render_template('wallets/manage.html', wallet=wallet, track_info=track_info, item_info=item_info, date=date,tb_page=tb_page)

# # Tạo bộ lọc theo thời gian (tuần, tháng, năm) cho ví
# @wallets_blueprint.route('/<int:user_id>/<int:wallet_id>/filter', methods=['GET', 'POST'])
# @login_required
# def filter(user_id, wallet_id):
#   # Lấy thông tin ví của người dùng dựa vào current user id và wallet id của user
#   wallet = Wallet.query.filter_by(user_id=user_id, id=wallet_id).first_or_404()
#   form = FilterWalletForm()

#   if form.validate_on_submit():
#     condition = form.condition.data
#     value = form.value.data.strftime('%Y-%m-%d')

#     return redirect(url_for('wallets.manage_filter', user_id=user_id, wallet_id=wallet_id, condition=condition, value=value))

#   return render_template('filter.html', form=form, wallet=wallet, wallet_filter=True)

# # Quản lý ví theo thời gian đã đươc xác nhận bởi bộ lọc
# @wallets_blueprint.route('/<int:user_id>/<int:wallet_id>/filter/<int:condition>/<value>')
# @login_required
# def manage_filter(user_id, wallet_id, condition, value):
#   # Lấy thông tin ví của người dùng dựa vào current user id và wallet id của user
#   wallet = Wallet.query.filter_by(user_id=user_id, id=wallet_id).first_or_404()
  
#   if condition == 1:
#     pass
#   if condition == 2:
#     date =value[:7]
#   if condition == 3:
#     date =value[:4]

#   # Lọc thông tin các khoản thu dụa vào biến current_datetime
#   track_info = [] # Khởi tạo danh sách chứa các object được query từ TrackBalance table dựa theo date condition
#   track_balances = TrackBalance.query.filter(TrackBalance.wallet_id == wallet_id)
#   for track in track_balances:
#     if date in track.date.strftime('%Y-%m-%d'):
#       track_info.append(track)

#   # Lọc thông tin các khoản chi dụa vào biến current_datetime
#   expense_info = [] # Khởi tạo danh sách chứa các object được query từ Expenditure table dựa theo date condition
#   expenses = Expenditure.query.filter_by(user_id=user_id)
#   for expense in expenses:
#     if date in expense.date.strftime('%Y-%m-%d'):
#       expense_info.append(expense)
  
#   return render_template('wallets/manage.html', wallet=wallet, track_info=track_info, expense_info=expense_info, date=date)

# Tất toán ví để bắt đầu chu kỳ mới
@wallets_blueprint.route('/<int:user_id>/<int:wallet_id>/settlement')
@login_required
def settlement(user_id, wallet_id):
  '''
  Tất toán ví để bắt đầu một chu kỳ mới.
  Số dư sẽ được cập nhật vào table MoneySaving.
  Ngân sách sẽ được đưa trở về 0.
  Các khoản chi liên quan đến ví cũng sẽ được loại bỏ.
  '''
  # Lấy thông tin hiện tại của ví
  wallet = Wallet.query.filter_by(user_id=user_id, id=wallet_id).first_or_404()
  # Lấy thông tin tất cả các khoản chi từ ví
  items = Item.query.filter_by(user_id=user_id, wallet_id=wallet_id)
  # Xoá tất cả các khoản chi đã được chi bới ví và người dùng
  for item in items:
    for expense in item.expenditures:
      db.session.delete(expense)
  # Cập nhật số dư hiện tại vào MoneySaving table
  saving = MoneySaving(date = datetime.utcnow(),
                        saving=wallet.balance,
                        description='Tiết kiệm tháng {}'.format(datetime.utcnow().strftime('%Y-%m')),
                        user_id=user_id,
                        wallet_id=wallet_id)
  db.session.add(saving)
  # Đưa số dư trong ví trở về 0
  wallet.balance = 0
  # Cập nhật thông tin về database
  db.session.commit()
  flash('Tất toán thành công!')

  return redirect(url_for('wallets.manage', user_id=user_id, wallet_id=wallet_id))