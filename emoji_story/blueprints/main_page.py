# -*- coding: utf-8 -*-

import json

from flask import flash, render_template, make_response, request, Blueprint, send_from_directory, jsonify, current_app
from flask_login import current_user

from emoji_story import db
from emoji_story.forms import StoryForm, CommentForm
from emoji_story.models import Post, Author, Comment
from emoji_story.utils import Emoji, redirect_back, submit_post

main_page_bp = Blueprint('main_page', __name__)


@main_page_bp.route('/', methods=['GET', 'POST'])
def index():
    #  初始化表格
    form = StoryForm()  # https://unicode.org/emoji/charts/emoji-ordering.txt

    tempstory = request.cookies.get('tempstory')
    if tempstory:
        form.story.data = tempstory

    if current_user.is_authenticated:
        like_list = json.loads(Author.query.get(current_user.get_id()).like)['like_post']
    else:
        like_list = []

    # 【内容展示】
    #  页码
    page = request.args.get('page', 1, type=int)
    per_page = 15  # 每页数量
    #  从数据库读取用户生成内容列表，并倒序
    pagination = Post.query.order_by(Post.time.desc()).filter_by(delete=False).paginate(page, per_page=per_page)
    posts = pagination.items

    # 【内容提交】
    #  判断用户是否登陆
    #  YES: 判断表单，生成flash，并写入数据库
    if form.validate_on_submit():
        return submit_post(form=form, emoji_str=request.cookies.get('emoji'))

    #  生成响应
    response = make_response(render_template('index.html',
                                             form=form,
                                             pagination=pagination,
                                             posts=posts,
                                             like_list=like_list))

    return response


@main_page_bp.route('/refresh', methods=['POST'])
def refresh():
    emoji_str = Emoji.get()
    return jsonify(emoji_str=emoji_str)


@main_page_bp.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post(post_id):
    post = Post.query.get(post_id)
    form = CommentForm()

    if current_user.is_authenticated:
        like_list = json.loads(Author.query.get(current_user.get_id()).like)['like_post']
    else:
        like_list = []

    if form.validate_on_submit():
        post_id = int(request.path[6:])
        user_comment = Comment(body=form.body.data, post_id=post_id)
        current_user.comment.append(user_comment)
        db.session.commit()
        flash('Your comment has been sent!', 'success')
        return redirect_back()

    return render_template('post.html', post=post, like_list=like_list, form=form)


@main_page_bp.route('/uploads/<path:filename>')
def get_image(filename):
    return send_from_directory(current_app.config['UPLOAD_PATH'], filename)
