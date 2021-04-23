from flask import Blueprint, flash, redirect, url_for
from flask_login import login_required, current_user

from emoji_story.settings import Operations
from emoji_story.utils import validate_token, send_confirm_email, generate_token, redirect_back

email_bp = Blueprint('email', __name__)


#  确认邮件链接
@email_bp.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main_page.index'))

    if validate_token(user=current_user, token=token, operation=Operations.CONFIRM):
        flash('Account confirmed.', 'success')
        return redirect(url_for('main_page.index'))

    else:
        flash('Invalid or expired token.', 'danger')
        return redirect(url_for('.resend_confirm_email'))


#  重新发送确认邮件
@email_bp.route('/resend_confirm_email', methods=['POST'])
@login_required
def resend_confirm_email():
    if current_user.confirmed:
        return redirect(url_for('main_page.index'))
    token = generate_token(user=current_user, operation=Operations.CONFIRM)
    send_confirm_email(user=current_user, token=token)
    flash('New email sent, check your inbox.', 'info')
    return redirect_back()
