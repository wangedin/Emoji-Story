import linecache
import os.path
import random
import uuid
from threading import Thread

from PIL import Image
from flask import render_template, make_response, flash, request, redirect, url_for, current_app
from flask_login import current_user, login_required
from flask_mail import Message
from itsdangerous import BadSignature, SignatureExpired
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from emoji_story.decorators import confirm_required
from emoji_story.extensions import mail, db
from emoji_story.models import Post
from emoji_story.settings import Operations

try:
    from urlparse import urlparse, urljoin
except ImportError:
    from urllib.parse import urlparse, urljoin


class Emoji:
    @staticmethod
    def get(amount=7):
        emoji_list = []
        while amount > 0:
            num = random.randint(1, 3521)
            emoji_list.append(
                linecache.getline('emoji_story/static/emoji_list.csv', num))
            amount -= 1
        emoji_str = ''
        for emoji in emoji_list:
            emoji = emoji.strip().replace('U+', "&#x")
            emoji_str += emoji.replace(' ', '')
        return emoji_str


@login_required
@confirm_required
def submit_post(form, emoji_str):
    story = form.story.data
    name = current_user.username
    user_content = Post(name=name, story=story, emoji=emoji_str)
    current_user.post.append(user_content)
    db.session.add(user_content)
    db.session.commit()
    response = make_response(redirect(url_for('main_page.index')))
    response.delete_cookie('tempstory')
    response.delete_cookie('emoji')
    flash('Well done, {}! Your story has been summit!'.format(current_user.username), 'success')
    return response


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def redirect_back(default='main_page.index', **kwargs):
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
    return redirect(url_for(default, **kwargs))


#  邮件发送函数
def send_mail(subject, to, template, **kwargs):
    message = Message(subject, recipients=[to])
    message.body = render_template(template + '.txt', **kwargs)
    message.html = render_template(template + '.html', **kwargs)
    mail.send(message)


#  生成令牌函数
def generate_token(user, operation, expire_in=None, **kwargs):
    s = Serializer(current_app.config['SECRET_KEY'], expire_in)
    data = {'id': user.id, 'operation': operation}
    data.update(**kwargs)
    return s.dumps(data)


#  发送确认邮件函数
def send_confirm_email(user, token, to=None):
    send_mail(subject='Email Confirm',
              to=to or user.email,
              template='emails/confirm',
              user=user,
              token=token)


#  验证和解析令牌函数
def validate_token(user, token, operation, new_password=None):
    s = Serializer(current_app.config['SECRET_KEY'])

    try:
        data = s.loads(token)
    except (SignatureExpired, BadSignature):
        return False

    if operation != data.get('operation') or user.id != data.get('id'):
        return False

    if operation == Operations.CONFIRM:
        user.confirmed = True
    elif operation == Operations.RESET_PASSWORD:
        user.set_password(new_password)
    else:
        return False
    db.session.commit()
    return True


#  发送重置密码邮件函数
def send_reset_pwd_email(user, token, to=None):
    send_mail(subject='Reset Your Password',
              to=to or user.email,
              template='emails/reset_pwd',
              user=user,
              token=token)


#  头像图片处理
def clipResizeImg(filename, dst_w, dst_h, qua=95):
    """
    先按照一个比例对图片剪裁，然后在压缩到指定尺寸
    一个图片 16:5 ，压缩为 2:1 并且宽为200，就要先把图片裁剪成 10:5,然后在等比压缩
    """

    img = Image.open(os.path.join(current_app.config['UPLOAD_PATH'], filename))

    ori_w, ori_h = img.size

    dst_scale = float(dst_w) / dst_h  # 目标高宽比
    ori_scale = float(ori_w) / ori_h  # 原高宽比

    if ori_scale <= dst_scale:
        # 过高
        width = ori_w
        height = int(width / dst_scale)

        x = 0
        y = (ori_h - height) / 2

    else:
        # 过宽
        height = ori_h
        width = int(height * dst_scale)

        x = (ori_w - width) / 2
        y = 0

    # 裁剪
    box = (x, y, width + x, height + y)
    # 这里的参数可以这么认为：从某图的(x,y)坐标开始截，截到(width+x,height+y)坐标
    newIm = img.crop(box)
    img = None

    # 压缩
    ratio = float(dst_w) / width
    newWidth = int(width * ratio)
    newHeight = int(height * ratio)
    newIm.resize((newWidth, newHeight), Image.ANTIALIAS).save(os.path.join(current_app.config['UPLOAD_PATH'], filename),
                                                              optimize=True,
                                                              quality=qua)
    return


# 重命名文件函数
def random_filename(filename):
    ext = os.path.splitext(filename)[1]
    return uuid.uuid4().hex + ext
