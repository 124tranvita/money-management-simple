# __init__.py
from fileinput import filename
import os
from datetime import datetime
from flask import Flask, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_manager

### INIT FLASK APP ###
app = Flask(__name__)

### CONFIGURE SECRET KEY FOR FLASKFORM ###
app.config['SECRET_KEY'] = 'my_secret_key'

### CONFIGURE SQLACHEMY DATABASE ###
basedir = os.path.abspath(os.path.dirname(__file__))

# uri = os.getenv('DATABASE_URL')
# if uri.startswith('postgres://'):
#   uri = uri.replace("postgres://", "postgresql://", 1)
  
# app.config['SQLALCHEMY_DATABASE_URI'] = uri or 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
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

### APP CONTEXT PROCESSOR ###
@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}
