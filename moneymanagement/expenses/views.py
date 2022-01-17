# expenses/views.py
from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from flask_login import current_user, login_required
from moneymanagement import db
from moneymanagement.models import Expenditure, Item, Wallet
from moneymanagement.expenses.forms import AddExpenditureForm, UpdateExpenditureForm, FilterByTimeForm

# Tạo blueprint cho expense views
expenses_blueprint = Blueprint('expenses', __name__)

# Thêm khoản chi
@expenses_blueprint.route('/<int:user_id>/add_expense', methods=['GET', 'POST'])
@login_required
def add(user_id):
  # Kiểm tra id của người dùng hiện tại có trùng với id nhận vào hay không, nếu không -> 403 error
  if current_user.id != user_id:
    abort(403)

  # Kiểm tra người dùng đã tạo danh mục nào hay chưa, nếu chưa -> show warning
  if not Item.query.filter_by(user_id = user_id).first():
    return redirect(url_for('errors.item_required'))

  form = AddExpenditureForm()

  if form.validate_on_submit():
    expense = Expenditure(name=form.name.data,
                          date=form.date.data,
                          description=form.description.data,
                          amount=form.amount.data,
                          item_id=form.item_id.data.id,
                          user_id=user_id,
                          wallet_id=form.item_id.data.wallet_id)
    db.session.add(expense)
    db.session.commit()
    flash('Đã thêm khoản chi!')

    return redirect(url_for('users.expense', user_id=user_id))
  return render_template('expenses/add.html', form=form, user_id=user_id)

# Thêm khoản chi theo danh mục (người dùng sẽ thêm khoản chi này từ page danh mục)
@expenses_blueprint.route('/<int:user_id>/<int:item_id>/add_expense', methods=['GET', 'POST'])
@login_required
def add_by_item(user_id, item_id):
  # Kiểm tra id của người dùng hiện tại có trùng với id nhận vào hay không, nếu không -> 403 error
  if current_user.id != user_id:
    abort(403)

  form = AddExpenditureForm()

  if form.validate_on_submit():
    expense = Expenditure(name=form.name.data,
                          date=form.date.data,
                          description=form.description.data,
                          amount=form.amount.data,
                          item_id=form.item_id.data.id,
                          user_id=user_id,
                          wallet_id=form.item_id.data.wallet_id)
    db.session.add(expense)
    db.session.commit()
    flash('Đã thêm khoản chi!')

    return redirect(url_for('items.item_expenses', item_id=item_id))

  elif request.method == 'GET':
    form.item_id.data = Item.query.get(item_id)

  return render_template('expenses/add.html', form=form, user_id=user_id)

# Cập nhật khoản chi
@expenses_blueprint.route('/<int:user_id>/<int:expense_id>/update_expense', methods=['GET', 'POST'])
@login_required
def update(user_id, expense_id):
  # Kiểm tra id của người dùng hiện tại có trùng với id nhận vào hay không, nếu không -> 403 error
  if current_user.id != user_id:
    abort(403)

  # Lấy thông tin khoản chi từ database
  expense = Expenditure.query.filter_by(user_id=user_id, id=expense_id).first_or_404()

  form = UpdateExpenditureForm()

  if form.validate_on_submit():
    # Cập nhật khoản chi
    expense.name = form.name.data
    expense.date = form.date.data
    expense.description = form.description.data
    expense.amount = form.amount.data
    expense.item_id = form.item_id.data.id
    expense.wallet_id = form.item_id.data.wallet_id
    db.session.commit()
    flash('Khoản chi đã được cập nhật!')
    return redirect(url_for('users.expense', user_id=user_id))
  
  elif request.method == 'GET':
    form.name.data = expense.name 
    form.date.data = expense.date
    form.description.data = expense.description
    form.amount.data = expense.amount
    form.item_id.data = expense.item_id

  return render_template('expenses/update.html', form=form, user_id=user_id,expense_id=expense_id)

# Xoá từng khoản chi
@expenses_blueprint.route('/<int:expense_id>/delete_expense')
@login_required
def delete(expense_id):
  # Lấy thông tin khoản chi từ database
  expense = Expenditure.query.filter_by(user_id=current_user.id, id=expense_id).first_or_404()
  # Xoá khoản chi
  db.session.delete(expense)
  db.session.commit()
  flash('Khoản chi đã được xoá!')

  return redirect(url_for('users.expense', user_id=current_user.id))

# Xoá tất cả khoản chi
@expenses_blueprint.route('/<int:user_id>/delete_all_expense')
@login_required
def delete_all(user_id):
  # Kiểm tra id của người dùng hiện tại có trùng với id nhận vào hay không, nếu không -> 403 error
  if current_user.id != user_id:
    abort(403)

  # Lấy tất cả các khoản chi của người dùng
  expenses = Expenditure.query.filter_by(user_id=user_id)
  # Xoá tất cả các khoản chi
  for expense in expenses:
    db.session.delete(expense)

  db.session.commit()
  flash('Tất cả khoản chi đã được xoá!')

  return redirect(url_for('users.expense', user_id=user_id))

# Lọc khoản chi theo khoản thời gian
@expenses_blueprint.route('/<int:user_id>/filter/expense', methods=['GET', 'POST'])
@login_required
def filter(user_id):
  # Kiểm tra id của người dùng hiện tại có trùng với id nhận vào hay không, nếu không -> 403 error
  if current_user.id != user_id:
    abort(403)

  form = FilterByTimeForm()

  if form.validate_on_submit():
    date_from = form.date_from.data.strftime('%Y-%m-%d')
    date_to = form.date_to.data.strftime('%Y-%m-%d')
      
    return redirect(url_for('users.expense_filter', user_id=user_id, date_from=date_from, date_to=date_to))
  return render_template('filter.html', form=form, user_id=user_id)
  