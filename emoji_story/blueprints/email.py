from flask import Blueprint, flash, redirect, url_for, render_template, current_app
from flask_login import login_required, current_user

from emoji_story.extensions import mail
from emoji_story.settings import Operations
from emoji_story.utils import validate_token, generate_token, redirect_back
from flask_mail import Message
from threading import Thread

email_bp = Blueprint('email', __name__)


def _send_async_mail(app, message):
    with app.app_context():
        mail.send(message)


#  邮件发送函数
def send_mail(subject, to, template, **kwargs):
    message = Message(subject=subject, recipients=[to])
    message.body = render_template(template + '.txt', **kwargs)
    message.html = render_template(template + '.html', **kwargs)
    app = current_app._get_current_object()
    thr = Thread(target=_send_async_mail, args=[app, message])
    thr.start()
    return thr


#  发送确认邮件函数
def send_confirm_email(user, token, to=None):
    send_mail(subject='Email Confirm',
              to=to or user.email,
              template='emails/confirm',
              user=user,
              token=token)


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


#  发送重置密码邮件函数
def send_reset_pwd_email(user, token, to=None):
    send_mail(subject='Reset Your Password',
              to=to or user.email,
              template='emails/reset_pwd',
              user=user,
              token=token)