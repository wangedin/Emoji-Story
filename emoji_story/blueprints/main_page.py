# -*- coding: utf-8 -*-

import json
from flask import flash, render_template, make_response, request, Blueprint, send_from_directory, jsonify, current_app
from flask_login import current_user

from emoji_story.extensions import db
from emoji_story.forms import StoryForm, CommentForm
from emoji_story.models import Post, Author, Comment, Timeline
from emoji_story.utils import Emoji, redirect_back, submit_post
from urllib.parse import unquote

main_page_bp = Blueprint('main_page', __name__)


@main_page_bp.route('/', methods=['GET', 'POST'])
def index():
    #  初始化表格
    form = StoryForm()  # https://unicode.org/emoji/charts/emoji-ordering.txt

    tempstory = request.cookies.get('tempstory')
    if tempstory:
        form.story.data = unquote(tempstory)
        print(form.story.data)

    # 【内容展示】
    #  页码
    page = request.args.get('page', 1, type=int)
    per_page = 15  # 每页数量
    #  从数据库读取用户生成内容列表，并倒序
    pagination = Post.query.order_by(Post.time.desc()).paginate(page, per_page=per_page)
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
                                             )
                             )

    return response


@main_page_bp.route('/refresh', methods=['POST'])
def refresh():
    emoji_str = Emoji.get()
    return jsonify(emoji_str=emoji_str)


@main_page_bp.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post(post_id):
    post = Post.query.get(post_id)
    form = CommentForm()

    if form.validate_on_submit():
        # 提交评论
        post_id = int(request.path[6:])
        user_comment = Comment(body=form.body.data, post_id=post_id)
        db.session.add(user_comment)
        current_user.comment.append(user_comment)
        # 生成timeline
        comment_timeline = Timeline(type='comment',
                                    post_id=post_id,
                                    username_1=current_user.username,
                                    username_2=post.name,
                                    comment=form.body.data
                                    )
        # 提醒post owner
        post.user.notification += 1

        db.session.add(comment_timeline)
        db.session.commit()
        flash('Your comment has been sent!', 'success')
        return redirect_back()

    return render_template('post.html', post=post, form=form)


@main_page_bp.route('/uploads/<path:filename>')
def get_image(filename):
    return send_from_directory(current_app.config['UPLOAD_PATH'], filename)
