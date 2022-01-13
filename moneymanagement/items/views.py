# items/views.py
from datetime import datetime
from flask import Blueprint, redirect, render_template, url_for, request, abort
from flask.helpers import flash
from flask_login import current_user, login_required
from moneymanagement import db
from moneymanagement.models import Item, Wallet, Expenditure
from moneymanagement.items.forms import AddItemForm, UpdateItemForm, FilterItemForm

items_blueprint = Blueprint('items', __name__)

# Thêm danh mục mới
@items_blueprint.route('/<int:user_id>/add_item', methods=['GET', 'POST'])
@login_required
def add(user_id):
  # Kiểm tra xem người dùng đã có ví hay chưa, nếu chưa -> warning yêu cầu tạo ví trước
  if not Wallet.query.filter_by(user_id = user_id).first():
    return redirect(url_for('errors.wallet_require'))

  form = AddItemForm()

  if form.validate_on_submit():
    item = Item(name=form.name.data, 
                user_id=user_id,
                wallet_id=form.wallet_id.data.id)
    db.session.add(item)
    db.session.commit()
    flash('Thêm danh mục thành công!')

    return redirect(url_for('users.item', user_id=user_id))
  return render_template('items/add.html', form=form, user_id=user_id)

# Cập nhật danh mục mới
@items_blueprint.route('/<int:user_id>/<int:item_id>/update_item', methods=['GET', 'POST'])
@login_required
def update(user_id, item_id):
  # Kiểm tra xem người dùng có item id này hay ko, nếu không -> 404 error
  if not Item.query.filter_by(user_id=current_user.id, id=item_id).first():
    abort(404)
  # Lấy thông tin item từ database
  item = Item.query.get(item_id)
  
  form = UpdateItemForm()

  if form.validate_on_submit():
    item.name = form.name.data
    db.session.commit()
    flash('Danh mục đã cập nhật!')

    return redirect(url_for('users.item', user_id=user_id))

  elif request.method == 'GET':
    form.name.data = item.name

  return render_template('items/update.html', form=form, user_id=user_id, item_id=item_id)

# Xoá từng danh mục
@items_blueprint.route('/<int:item_id>/delete_item')
@login_required
def delete(item_id):
  if Expenditure.query.filter_by(item_id=item_id).first():
    return redirect(url_for('errors.item_delete_error', item_id=item_id))

  item = Item.query.get_or_404(item_id)

  if current_user.id != item.user_id:
    abort(403)

  db.session.delete(item)
  db.session.commit()
  flash('Xoá danh mục thành công!')

  return redirect(url_for('users.item', user_id=current_user.id))

# Xoá toàn bộ danh mục
@items_blueprint.route('/<int:user_id>/delete_all_item')
@login_required
def delete_all(user_id):
  # Kiểm tra xem id của người dùng hiện tại có trùng với id nhận vào hay không, nếu không -> 403 error
  if current_user.id != user_id:
    abort(403)
  # Kiểm tra xem có khoản chi nào đang liêt kết với danh mục hay không, nếu có -> warning
  if Expenditure.query.filter_by(user_id=user_id).first():
    return redirect(url_for('errors.item_delete_error', user_id=user_id))

  items = Item.query.filter_by(user_id=user_id)

  for item in items:
    db.session.delete(item)

  db.session.commit()
  flash('Tất cả danh mục đã được xoá!')

  return redirect(url_for('users.item', user_id=current_user.id))

# Liệt kê tất cả các khoản chi thuộc về danh mục
@items_blueprint.route('/<int:item_id>/item_by_expense')
@login_required
def item_expenses(item_id):
  '''
  Hàm trả về tất cả các khoản chi thuộc về từng danh mục được chọn.
  Các khoản chi của danh mục sẽ được liệt kê theo tháng hiện tại.
  '''
  # Kiểm tra xem người dùng có item id này hay ko, nếu không -> 404 error
  if not Item.query.filter_by(user_id=current_user.id, id=item_id).first():
    abort(404)
    
  # Khởi tạo biến page cho pagination
  page = request.args.get('page', 1, type=int)
  # Khởi tạo biến date để lưu thông tin tháng năm hiện tại.
  date = datetime.utcnow().strftime('%Y-%m')
  item = Item.query.get(item_id)
  expenses = Expenditure.query.filter_by(item_id=item_id).order_by(Expenditure.date.desc()).paginate(page=page, per_page=10)

  return render_template('users/expense.html', date=date, expenses=expenses, item=item, expense_by_item=True)

# Lọc các khoản chi của danh mục theo khoản thời gian (tháng - năm)
@items_blueprint.route('/<int:user_id>/filter/item', methods=['GET', 'POST'])
@login_required
def filter(user_id):
  '''
  Hàm trả về giá trị bộ lọc mà user đã nhập cho và làm giá trị đầu vào cho hàm user.item_filter()
  '''
  # Kiểm tra xem id của người dùng hiện tại có trùng với id nhận vào hay không, nếu không -> 403 error
  if current_user.id != user_id:
    abort(403)

  form = FilterItemForm()

  if form.validate_on_submit():
    date = form.condition.data.strftime('%Y-%m')

    return redirect(url_for('users.item_filter', user_id=user_id, date=date))
  return render_template('filter.html', form=form, user_id=user_id, item_filter=True)