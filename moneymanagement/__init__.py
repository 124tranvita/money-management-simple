# __init__.py
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_manager

### INIT FLASK APP ###
app = Flask(__name__)

### CONFIGURE SECRET KEY FOR FLASKFORM ###
app.config['SECRET_KEY'] = 'my_secret_key'

### CONFIGURE SQLACHEMY DATABASE ###
basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

### CONFIGURE MIGRATE ###
Migrate(app, db)

### CONFIGURE LOGIN MANAGER ###
login_manager = LoginManager()
# Pass in app to the login manager
login_manager.init_app(app)
# Tell users what view to go to when they need to login
login_manager.login_view ='users.login'

### REGISTER BLUEPRINT ###
from moneymanagement.core.views import core_blueprint
from moneymanagement.users.views import users_blueprint
from moneymanagement.wallets.views import wallets_blueprint
from moneymanagement.items.views import items_blueprint
from moneymanagement.expenses.views import expenses_blueprint
from moneymanagement.errors.errors_handler import errors_page

app.register_blueprint(core_blueprint)
app.register_blueprint(users_blueprint)
app.register_blueprint(wallets_blueprint)
app.register_blueprint(items_blueprint)
app.register_blueprint(expenses_blueprint)
app.register_blueprint(errors_page)