# -*- coding: utf-8 -*-
import json
import os.path
from datetime import timedelta

from flask import flash, redirect, url_for, render_template, request, Blueprint, jsonify, \
    current_app
from flask_login import login_user, current_user, login_required, logout_user

from emoji_story.extensions import db
from emoji_story.forms import LoginForm, DeleteStoryForm, SignUpForm, \
    ChangePwdForm, ConfirmEmailForm, ForgetPwdForm, ResetPwdForm, ProfileForm, ProfilePhotoForm
from emoji_story.models import Post, Author
from emoji_story.utils import generate_token, Operations, \
    validate_token, \
    clipResizeImg, random_filename, redirect_back
from emoji_story.blueprints.email import send_confirm_email, send_reset_pwd_email

user_bp = Blueprint('user', __name__)


@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main_page.index'))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        remember = form.remember.data
        user = Author.query.filter_by(email=email).first()
        if user:
            #  验证用户名密码
            if email == user.email and user.validate_password(password):
                login_user(user, remember, timedelta(days=30))
                flash('Welcome back, {}!'.format(user.username), 'success')
                return redirect_back()
            else:
                flash('Wrong password!', 'warning')
        else:
            flash('User does not exist!', 'warning')

    return render_template('login.html', form=form)


@user_bp.route('/home')
@login_required
def home():
    form = DeleteStoryForm()

    if current_user.is_authenticated:
        like_list = json.loads(Author.query.get(current_user.get_id()).like)['like_post']
    else:
        like_list = []

    page = request.args.get('page', 1, type=int)
    per_page = 15  # 每页数量
    #  从数据库读取用户生成内容列表，并倒序
    pagination = Post.query.order_by(Post.time.desc()). \
        filter_by(delete=False).filter_by(author_id=current_user.get_id()). \
        paginate(page, per_page=per_page)
    posts = pagination.items

    return render_template('home.html',
                           pagination=pagination,
                           form=form,
                           posts=posts,
                           like_list=like_list,
                           )


@user_bp.route('/delete/<int:delete_id>', methods=['POST'])
@login_required
def delete_story(delete_id):
    form = DeleteStoryForm()
    if form.validate_on_submit():
        delet_post = Post.query.get(delete_id)
        delet_post.delete = True
        db.session.commit()
        flash('This story has been deleted.', 'success')
    return redirect(url_for('user.home'))


@user_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Log out successfully!', 'success')
    return redirect(url_for('main_page.index'))


@user_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        email = form.email.data.lower()
        username = form.username.data
        new_user = Author(email=email, username=username)
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        send_confirm_email(user=new_user, token=generate_token(user=new_user, operation=Operations.CONFIRM))
        flash('Well done, {}! Your account has been created! Please check your inbox to confirm your email.'.format(
            username),
              'success')
        login_user(new_user)
        return redirect(url_for('main_page.index'))
    return render_template('signup.html', form=form)


@user_bp.route('/like', methods=['POST'])
@login_required
def like():
    import json
    post_id = int(request.get_json()['post_id'])
    post = Post.query.get(post_id)
    user = Author.query.get(current_user.get_id())

    like_list = json.loads(user.like)['like_post']
    if post_id not in like_list:
        post.like += 1
        like_list.append(post_id)
        result = 'like'
    else:
        post.like -= 1
        like_list.remove(post_id)
        result = 'unlike'
    user.like = json.dumps({'like_post': like_list})
    db.session.commit()
    return jsonify(result=result)


@user_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    confirm_form = ConfirmEmailForm()
    profile_form = ProfileForm()
    profile_photo_form = ProfilePhotoForm()

    if profile_form.submit_profile.data and profile_form.validate_on_submit():
        current_user.bio = profile_form.bio.data
        db.session.commit()
        flash('Submit successfully', 'success')
        return redirect(url_for('user.settings'))

    if profile_photo_form.submit_profile_photo.data and profile_photo_form.validate_on_submit():

        old_filename = current_user.photo
        f = profile_photo_form.profile_photo.data
        filename = random_filename(f.filename)
        f.save(os.path.join(current_app.config['UPLOAD_PATH'], filename))
        current_user.photo = filename
        db.session.commit()
        flash('Upload Success.', 'success')

        # 头像图片处理
        clipResizeImg(filename=filename, dst_h=320, dst_w=320)

        # 清除旧图
        if old_filename != filename:
            os.remove(os.path.join(current_app.config['UPLOAD_PATH'], old_filename))

        return redirect(url_for('user.settings'))

    return render_template('settings.html',
                           confirm_form=confirm_form,
                           profile_form=profile_form,
                           profile_photo_form=profile_photo_form)


@user_bp.route('/settings/change_pwd', methods=['POST', 'GET'])
@login_required
def change_pwd():
    password_form = ChangePwdForm()
    if password_form.validate_on_submit():
        if current_user.validate_password(password_form.old_pwd.data):
            current_user.set_password(password_form.new_pwd.data)
            db.session.commit()
            flash('Success!', 'success')
        else:
            flash('Wrong Password', 'danger')
        return redirect_back()
    return render_template('change_pwd.html', password_form=password_form)


@user_bp.route('/forget_pwd', methods=['POST', 'GET'])
def forget_pwd():
    if current_user.is_authenticated:
        return redirect(url_for('main_page.index'))
    form = ForgetPwdForm()
    if form.validate_on_submit():
        user = Author.query.filter_by(email=form.email.data.lower()).first()
        if user:
            token = generate_token(user=user, operation=Operations.RESET_PASSWORD)
            send_reset_pwd_email(user=user, token=token)
            flash('Password reset email sent, check your inbox.', 'info')
            return redirect(url_for('user.login'))
        else:
            flash('Invalid email.', 'warning')
            return redirect(url_for('user.forget_pwd'))
    return render_template('forget_pwd.html', form=form)


@user_bp.route('/reset_pwd/<token>', methods=['POST', 'GET'])
def reset_pwd(token):
    if current_user.is_authenticated:
        return redirect(url_for('main_page.index'))

    form = ResetPwdForm()
    if form.validate_on_submit():
        user = Author.query.filter_by(email=form.email.data.lower()).first()
        if user is None:
            form.email.errors.append('Invalid Email')
        else:
            if validate_token(user=user,
                              token=token,
                              operation=Operations.RESET_PASSWORD,
                              new_password=form.new_pwd.data):
                flash('Password updated. Now you can log in with your new password!', 'success')
                return redirect(url_for('user.login'))
            else:
                flash('Invalid or expired token.', 'danger')
                return redirect(url_for('user.forget_pwd'))
    return render_template('reset_pwd.html', form=form)


@user_bp.route('/people/<username>')
def people(username):
    if current_user.is_authenticated:
        like_list = json.loads(Author.query.get(current_user.get_id()).like)['like_post']
        if current_user.username == username:
            return redirect(url_for('user.home'))
    else:
        like_list = []

    page = request.args.get('page', 1, type=int)
    per_page = 15  # 每页数量
    #  从数据库读取用户生成内容列表，并倒序
    user = Author.query.filter_by(username=username).first()
    pagination = Post.query.order_by(Post.time.desc()). \
        filter_by(delete=False).filter_by(author_id=user.get_id()). \
        paginate(page, per_page=per_page)
    posts = pagination.items

    return render_template('people.html',
                           pagination=pagination,
                           posts=posts,
                           like_list=like_list,
                           user=user
                           )
