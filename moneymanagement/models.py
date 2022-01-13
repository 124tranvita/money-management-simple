# moneymanagement/models.py
from datetime import datetime
from moneymanagement import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

### CONFIGURE USER LOADER ###
@login_manager.user_loader
def load_user(user_id):
  return User.query.get(user_id)

### USER MODEL ###
class User(db.Model, UserMixin):
  __tablename__ = 'users'
  id = db.Column(db.Integer, primary_key=True)
  email = db.Column(db.String(64), nullable=False, unique=True, index=True)
  username = db.Column(db.String(64), nullable=False, unique=True, index=True)
  password_hash = db.Column(db.String(128))
  profile_image = db.Column(db.String(64), nullable=False, default='df_profile.png')
  # Make relationship to Wallet table
  wallets = db.relationship('Wallet', back_populates='owner', lazy='dynamic')
  # Make relationship to Item table
  items = db.relationship('Item', back_populates='users', lazy='dynamic')
  # Make a relationship to Expenditure table
  expenditures = db.relationship('Expenditure', back_populates='users', lazy=True)
  # Make a relationship to MoneySaving table
  money_saving = db.relationship('MoneySaving', back_populates='user', lazy='dynamic')
  

  def __init__(self, email, username, password) -> None:
    self.email = email
    self.username = username
    self.password_hash = generate_password_hash(password)
  
  def password_check(self, password) -> bool:
    return check_password_hash(self.password_hash, password)

  # Tât cả tổng chi của người dùng
  def expenses_amount_in_sum(self):
    amount = 0
    for expense in self.expenditures:
      amount += expense.amount
    return amount

  # Tổng chi của người dùng theo khoản thời gian (ngày/tháng/năm)
  def expenses_amount_in_period(self, date):
    amount = 0
    for expense in self.expenditures:
      if date in expense.date.strftime('%Y-%m-%d'):
        amount += expense.amount
    return amount

     # Hàm tính tổng ngân sách của ví
  def total_balance(self):
    total = 0
    for wallet in self.wallets:
      for track in wallet.track_balances:
        total += track.balance
    return total

  # Hàm tính tổng ngân sách của ví theo khoảng thời gian (tháng, năm)
  def total_balance_in_period(self, date):
    total = 0
    for wallet in self.wallets:
      for track in wallet.track_balances:
        if date in track.date.strftime('%Y-%m-%d'):
          total += track.balance
    return total

  # Hàm tính tổng số dư của ví
  def rest_balance(self):
    total_balance = 0
    total_expense = 0
    # Tính tổng ngân sách của ví
    for wallet in self.wallets:
      for track in wallet.track_balances:
        total_balance += track.balance
    # Tính tổng các khoản chi
    for expense in self.expenditures:
      total_expense += expense.amount
    return (total_balance - total_expense)

   # Hàm tính tổng số dư của ví theo thời gian (tháng, năm)
  def rest_balance_in_period(self, date):
    total_balance = 0
    total_expense = 0
    # Tính tổng ngân sách của ví
    for wallet in self.wallets:
      for track in wallet.track_balances:
        if date in track.date.strftime('%Y-%m-%d'):
          total_balance += track.balance
    # Tính tổng các khoản chi
    for expense in self.expenditures:
      if date in expense.date.strftime('%Y-%m-%d'):
        total_expense += expense.amount
    return (total_balance - total_expense)

### WALLET MODEL###
class Wallet(db.Model):
  __tablename__ = 'wallets'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(16), nullable=False)
  balance = db.Column(db.Integer, nullable=False, default=0)
  date = db.Column(db.DateTime, default=datetime.utcnow())
  filter = db.Column(db.Integer, nullable=False, default=2)
  # Make user id as foreign key
  user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
  # Make a relationship to User table
  owner = db.relationship('User', back_populates='wallets', uselist=False)
  # Make a relationship to Wallet table
  track_balances = db.relationship('TrackBalance', back_populates='wallet', lazy='dynamic')
  # Make a relationship to Wallet table
  items = db.relationship('Item', back_populates='wallet', lazy='dynamic')
  # Make a relationship to MoneySaving table
  money_saving = db.relationship('MoneySaving', back_populates='wallet', lazy='dynamic')

  def __init__(self, name,balance, filter, user_id) -> None:
    self.name = name
    self.balance = balance
    self.filter = filter
    self.user_id = user_id
  
  def __repr__(self) -> str:
    return f'Account owner:   {self.owner.username}\nAccount balance: ${self.balance}'

  # Hàm để nhập tiền vào ví
  def deposit(self, amount) -> int:
    self.balance += amount
    print('Deposit Accepted')

  # Hàm để rút tiền ra khỏi ví
  def withdraw(self, amount) -> int:
    self.balance -= amount
    print('Withdrawal Accepted')

  # Hàm để tính tổng ngân sách của ví
  def total_balance(self):
    total = 0
    for track in self.track_balances:
      total += track.balance
    return total

  # Hàm để tính tổng ngân sách của ví theo 1 thời gian nhất định (tháng/năm)
  def balance_in_period(self, date):
    total = 0
    for track in self.track_balances:
      if date in track.date.strftime('%Y-%m-%d'):
        total += track.balance
    return total

  
### ITEM MODEL ###
class Item(db.Model):
  __tablename__ = 'items'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(32), nullable=False)
  # Use user id as the foreign key
  user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
  # Use wallet id as the foreign key
  wallet_id = db.Column(db.Integer, db.ForeignKey('wallets.id'))
  # Make a relationship to User table
  users = db.relationship('User', back_populates='items',uselist=False)
  # Make a relationship to Expenditure table
  expenditures = db.relationship('Expenditure', back_populates='items', lazy=True)
  # Make a relationship to Wallet table
  wallet = db.relationship('Wallet', back_populates='items', uselist=False)

  def __init__(self, name, user_id, wallet_id) -> None:
    self.name = name
    self.user_id = user_id
    self.wallet_id = wallet_id

  # Tính tổng chi của từng danh mục (tất cả)
  def amount_in_sum(self, user_id):
    amount = 0
    for expense in self.expenditures:
      if expense.user_id == user_id:
        amount += expense.amount
    return amount

  # Tính tổng chi của từng danh mục (theo khoảng thời gian cố định (tháng, năm))
  def amount_in_period(self, user_id, date):
    amount = 0
    for expense in self.expenditures:
      if expense.user_id == user_id:
        if date in expense.date.strftime('%Y-%m-%d'):
          amount += expense.amount
    return amount

  # Đếm các khoản chi thuộc từng danh mục theo tháng
  def expense_count_in_period(self, user_id, item_id, date):
    total = 0
    for expense in self.expenditures:
      if expense.user_id == user_id and expense.item_id == item_id:
        if date in expense.date.strftime('%Y-%m-%d'):
          total += 1
    return total

  # Đếm tất cả các khoản chi thuộc từng danh mục
  def expense_count(self, user_id, item_id):
    total = 0
    for expense in self.expenditures:
      if expense.user_id == user_id and expense.item_id == item_id:
        total += 1
    return total
    
### Expenditure Model ###
class Expenditure(db.Model):
  __tablename__ = 'expenditures'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(32), nullable=False)
  date = db.Column(db.Date, nullable=False, default=datetime.utcnow().strftime('%Y-%m-%d'))
  description = db.Column(db.String(128), nullable=False, default='Không có miêu tả nào')
  amount = db.Column(db.Integer, nullable=False, default=0)
  # Use Item id as the foreign key
  item_id = db.Column(db.Integer, db.ForeignKey('items.id'))
  # Make a relationship to Item table
  items = db.relationship('Item', back_populates='expenditures', uselist=False)
  # Use User id as the foreign key
  user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
  # Make a relationship to User table
  users = db.relationship('User', back_populates='expenditures', uselist=False)

  def __init__(self, name, date, description, amount, item_id, user_id) -> None:
    self.name = name
    self.date = date
    self.description = description
    self.amount = amount
    self.item_id = item_id
    self.user_id = user_id
  
### TRACK THE BALANCE IN THE WALLET MODEL ###
class TrackBalance(db.Model):
  __tablename__ = 'trackbalances'
  id = db.Column(db.Integer, primary_key=True)
  date = db.Column(db.DateTime, nullable=False, unique=True, index=True)
  balance = db.Column(db.Integer, nullable=False, default=0)
  description = db.Column(db.String(128))
  # Use Wallet id as the foreign key
  wallet_id = db.Column(db.Integer, db.ForeignKey('wallets.id'))
  # Make a relationship to Wallet table
  wallet = db.relationship('Wallet', back_populates='track_balances', uselist=False)

  def __init__(self, date, balance, description, wallet_id) -> None:
    self.date = date
    self.balance = balance
    self.description = description
    self.wallet_id = wallet_id

### MONEY SAVING MODEL ###
class MoneySaving(db.Model):
  __tablename__ = 'moneysaving'
  id = db.Column(db.Integer, primary_key=True)
  date = db.Column(db.DateTime, nullable=False, unique=True, index=True)
  saving = db.Column(db.Integer, nullable=False, default=0)
  description = db.Column(db.String(128))
  # Use user id as the foreign key
  user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
  # Use Wallet id as the foreign key
  wallet_id = db.Column(db.Integer, db.ForeignKey('wallets.id'))
  # Make a relationship to User table
  user = db.relationship('User', back_populates='money_saving', uselist=False)
  # Make a relationship to Wallet table
  wallet = db.relationship('Wallet', back_populates='money_saving', uselist=False)

  def __init__(self, date, saving, description, user_id, wallet_id) -> None:
    self.date =date
    self.saving = saving
    self.description = description
    self.user_id = user_id
    self.wallet_id =wallet_id
