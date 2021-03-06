import linecache
import os.path
import random
import uuid
from boto3.session import Session

from PIL import Image
from flask import render_template, make_response, flash, request, redirect, url_for, current_app
from flask_login import current_user, login_required
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
    story = form.story.data.replace('\n', '<br>')
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


#  ??????????????????
def generate_token(user, operation, expire_in=None, **kwargs):
    s = Serializer(current_app.config['SECRET_KEY'], expire_in)
    data = {'id': user.id, 'operation': operation}
    data.update(**kwargs)
    return s.dumps(data)


#  ???????????????????????????
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


#  ??????????????????
def clipResizeImg(filename, dst_w, dst_h, qua=95):
    """
    ?????????????????????????????????????????????????????????????????????
    ???????????? 16:5 ???????????? 2:1 ????????????200?????????????????????????????? 10:5,?????????????????????
    """

    img = Image.open(os.path.join(current_app.config['UPLOAD_PATH'], filename))

    ori_w, ori_h = img.size

    dst_scale = float(dst_w) / dst_h  # ???????????????
    ori_scale = float(ori_w) / ori_h  # ????????????

    if ori_scale <= dst_scale:
        # ??????
        width = ori_w
        height = int(width / dst_scale)

        x = 0
        y = (ori_h - height) / 2

    else:
        # ??????
        height = ori_h
        width = int(height * dst_scale)

        x = (ori_w - width) / 2
        y = 0

    # ??????
    box = (x, y, width + x, height + y)
    # ????????????????????????????????????????????????(x,y)????????????????????????(width+x,height+y)??????
    newIm = img.crop(box)
    img = None

    # ??????
    ratio = float(dst_w) / width
    newWidth = int(width * ratio)
    newHeight = int(height * ratio)

    # ????????????????????????
    newIm.resize((newWidth, newHeight), Image.ANTIALIAS).save(os.path.join(current_app.config['UPLOAD_PATH'], filename),
                                                              optimize=True,
                                                              quality=qua)

    # ?????????AWS
    session = Session(aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                      aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                      region_name='eu-west-2')
    s3 = session.client("s3")
    s3.upload_file(Filename=os.path.join(current_app.config['UPLOAD_PATH'], filename),
                   Key=filename, Bucket='emoji-story')

    return


# ??????upload????????????????????????????????????????????????????????????aws??????
def get_img_from_aws(user):
    bucket_name = 'emoji-story'
    file_name = user.photo
    local_file_name = os.path.join(current_app.config['UPLOAD_PATH'], user.photo)
    session = Session(aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                      aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                      region_name='eu-west-2')
    s3 = session.client("s3")
    s3.download_file(Bucket=bucket_name,
                     Key=file_name,
                     Filename=local_file_name)


# ?????????????????????
def random_filename(filename):
    ext = os.path.splitext(filename)[1]
    return uuid.uuid4().hex + ext
