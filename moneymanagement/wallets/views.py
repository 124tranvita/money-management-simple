# wallets/views.py
from datetime import datetime
from flask import Blueprint, redirect, render_template, url_for, flash, request, abort
from flask_login import login_required, current_user
from sqlalchemy import extract
from moneymanagement import db
from moneymanagement.models import Item, Wallet, TrackBalance, MoneySaving
from moneymanagement.wallets.forms import CreateWalletForm, UpdateWalletForm, AddBalanceForm, UpdateBalanceForm 

wallets_blueprint = Blueprint('wallets', __name__)

# Tạo ví
@wallets_blueprint.route('/<int:user_id>/create_wallet', methods=['GET', 'POST'])
@login_required
def create(user_id):
  # Kiểm tra xem người dùng đã có ví hay chưa, nếu đã có -> warning
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
                            check=True,
                            wallet_id=wallet.id)
    db.session.add(new_track)
    db.session.commit()

    return redirect(url_for('users.wallet', user_id=user_id))
  return render_template('wallets/create.html', form=form, user_id=user_id)

# Xoá ví
@wallets_blueprint.route('/<int:wallet_id>/delete_wallet')
@login_required
def delete(wallet_id):
  # Lấy thông tin ví từ database
  wallet = Wallet.query.get_or_404(wallet_id)
  # Kiểm tra ví có thuộc người dùng hiện tại hay không, nếu không -> 403
  if current_user.id != wallet.user_id:
    abort(403)

  # Kiểm tra các danh mục được liên kết với ví, nếu vẫn còn danh mục liên kết -> warning
  if wallet.items.first():
    return redirect(url_for('errors.wallet_have_item'))

  # Load tất cả cách track balance thuộc ví
  track_wallets = TrackBalance.query.filter_by(wallet_id=wallet_id).all()
  # Xoá ví khỏi database
  db.session.delete(wallet)
  # Xoá tất cả các track balance của ví khỏi database khi ví được xoá
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

# Quản lý thông tin chi tiết về ví
@wallets_blueprint.route('/<int:user_id>/wallet-<int:wallet_id>/manage', methods=['GET', 'POST'])
@login_required
def manage(user_id, wallet_id):
  # Kiểm tra xem id của người dùng hiện tại có trùng với id nhận vào hay không, nếu không -> 403 error
  if current_user.id != user_id:
    abort(403)

  # Lấy thông tin ví của người dùng dựa vào current user id và wallet id của user
  wallet = Wallet.query.filter_by(user_id=user_id, id=wallet_id).first_or_404()
  # Khởi tạo giá trị 'date' và dùng hàm datetime để lấy thời gian hiện tại
  date = datetime.utcnow()
  # Khởi tạo giá trị page cho Track Balance table
  tb_page = request.args.get('tb_page', 1, type=int)
  # Lọc thông tin theo filter đã được chọn bởi user
  if wallet.filter == 1: # Theo tuần
    return redirect(url_for('errors.not_support'))

  if wallet.filter == 2: # Theo tháng
    date = date.strftime('%Y-%m')
    # Lọc các track balance theo tháng và năm
    track_info = TrackBalance.query.filter(TrackBalance.wallet_id == wallet_id).filter(extract('year', TrackBalance.date) == int(date[:4])).filter(extract('month', TrackBalance.date) == int(date[5:])).order_by(TrackBalance.date.desc()).paginate(page=tb_page, per_page=5)

  if wallet.filter == 3: # Theo năm
    date = date.strftime('%Y')
    # Lọc các track balance theo năm
    track_info = TrackBalance.query.filter(TrackBalance.wallet_id == wallet_id).filter(extract('year', TrackBalance.date) == int(date[:4])).order_by(TrackBalance.date.desc()).paginate(page=tb_page, per_page=5)

  # Lấy thông tin về các danh mục liên kết với ví
  item_info = Item.query.filter_by(user_id=user_id, wallet_id=wallet_id)
  
  return render_template('wallets/manage.html', wallet=wallet, track_info=track_info, item_info=item_info, date=date)

# Thêm ngân sách cho ví
@wallets_blueprint.route('/<int:user_id>/wallet-<int:wallet_id>/add_balance', methods=['GET', 'POST'])
@login_required
def add_balance(user_id, wallet_id):
  # Kiểm tra xem id của người dùng hiện tại có trùng với id nhận vào hay không, nếu không -> 403 error
  if current_user.id != user_id:
    abort(403)

  form = AddBalanceForm()

  if form.validate_on_submit():
    # Tạo record để theo dõi ngân sách đã được thêm vào
    new_track = TrackBalance(date=datetime.utcnow(),
                            balance=form.balance.data,
                            description=form.description.data,
                            check=False,
                            wallet_id=wallet_id)
    db.session.add(new_track)
    db.session.commit()
    flash('Cập nhật số dư thành công!')
    
    return redirect(url_for('wallets.manage', user_id=current_user.id, wallet_id=wallet_id))

  return render_template('wallets/add.html',form=form)

# Cập nhật ngân sách
@wallets_blueprint.route('/<int:user_id>/wallet-<int:wallet_id>/<int:track_id>/update_balance', methods=['GET', 'POST'])
def update_balance(user_id, wallet_id, track_id):
  # Kiểm tra xem id của người dùng hiện tại có trùng với id nhận vào hay không, nếu không -> 403 error
  if current_user.id != user_id:
    abort(403)

  # Lấy thông tin của track hiện tại
  track = TrackBalance.query.filter_by(wallet_id=wallet_id, id=track_id).first_or_404()

  form = UpdateBalanceForm()
  if form.validate_on_submit():
    track.balance = form.balance.data
    track.description = form.description.data
    db.session.commit()
    flash('Cập nhật ngân sách thành công!')

    return redirect(url_for('wallets.manage', user_id=user_id, wallet_id=wallet_id))

  elif request.method == 'GET':
    form.balance.data = track.balance
    form.description.data = track.description
  
  return render_template('wallets/add.html', form=form, user_id=user_id, wallet_id=wallet_id)

# Xoá ngân sách khỏi ví
@wallets_blueprint.route('/<int:user_id>/wallet-<int:wallet_id>/<int:track_id>/delete_balance')
def delete_balance(user_id, wallet_id, track_id):
  # Kiểm tra xem id của người dùng hiện tại có trùng với id nhận vào hay không, nếu không -> 403 error
  if current_user.id != user_id:
    abort(403)

  # Lấy thông tin về ngân sách
  track = TrackBalance.query.filter_by(id=track_id, wallet_id=wallet_id).first_or_404()
  # Xoá track đã được chọn
  if track.check: # Nếu track check = True -> Không thể xoá
    return redirect(url_for('errors.balance_delete_error'))

  db.session.delete(track)
  db.session.commit()

  return redirect(url_for('wallets.manage', user_id=user_id, wallet_id=wallet_id))

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

@wallets_blueprint.context_processor
def inject_wallet():
  return {'wallet': Wallet.query.filter_by(user_id=current_user.id).first()}