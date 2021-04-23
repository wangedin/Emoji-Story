from functools import wraps

from flask import Markup, flash, url_for, redirect
from flask_login import current_user


#  过滤未确认用户
def confirm_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not current_user.confirmed:
            message = Markup('Please confirm your account first.<br>'
                             'Not receive the email? Go to SETTINGS to resend.')
            flash(message, 'warning')
            return redirect(url_for('main_page.index'))
        return func(*args, **kwargs)

    return decorated_function
