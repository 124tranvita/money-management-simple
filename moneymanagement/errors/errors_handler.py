#errors/error_handler.py
from flask import Blueprint, render_template, abort
from moneymanagement.models import Item

errors_page = Blueprint('errors', __name__)

@errors_page.app_errorhandler(404)
def page_not_found(error):
    '''
    Error for page not found
    '''
    return render_template('errors/404.html'), 404

@errors_page.app_errorhandler(403)
def forbidden(error):
    '''
    The HTTP 403 Forbidden client error status response code indicates 
    that the server understands the request but refuses to authorize it.
    '''
    return render_template('errors/403.html'), 403

@errors_page.route('/errors/already_have_wallet')
def already_have_wallet():
    '''
    Cảnh báo xảy ra khi người dùng tạo ví thứ 2 trở lên
    '''
    return render_template('errors/errors.html', wallet_error_1=True)

@errors_page.route('/errors/wallet_have_item')
def wallet_have_item():
    '''
    Lỗi xảy ra khi người dùng xoá ví nhưng vẫn còn cách danh mục khoản chi vẫn đang liên kết với ví
    '''
    return render_template('errors/errors.html', wallet_error_2=True)

@errors_page.route('/errors/wallet_required')
def wallet_require():
    '''
    Cảnh báo xảy ra khi người dùng tạo danh mục khi chưa có ví
    '''
    return render_template('errors/errors.html', item_error_1=True)

@errors_page.route('/errors/item_delete_error')
def item_delete_error():
    '''
    Lỗi xảy ra khi người dùng xoá các danh mục đang có một hoặc nhiều hơn các khoản chi
    '''
    return render_template('errors/errors.html', item_error_2=True)

@errors_page.route('/errors/item_required')
def item_required():
    '''
    Cảnh báo xảy ra khi người dùng tạo khoản chi nhưng chưa tạo danh mục cho khoản chi
    '''
    return render_template('errors/errors.html', expense_error_1=True)
