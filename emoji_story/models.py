import json
from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from emoji_story.extensions import db


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    emoji = db.Column(db.String)
    name = db.Column(db.String)
    story = db.Column(db.Text)
    time = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    like = db.Column(db.Integer, default=0)
    #  定义外键
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'))
    #  定义双向关系
    user = db.relationship('Author', back_populates='post')
    comment = db.relationship('Comment')
    liker_list = db.relationship('Like', back_populates='liked', cascade='all')
    timeline = db.relationship('Timeline')


class Author(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True)
    username = db.Column(db.String, unique=True)
    confirmed = db.Column(db.Boolean, default=False)
    pwd_hash = db.Column(db.String(128))
    bio = db.Column(db.String(140), default='I am a very mysterious storyteller!')
    photo = db.Column(db.String, default='default.jpg')
    notification = db.Column(db.Integer, default=0)

    def set_password(self, password):
        self.pwd_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.pwd_hash, password)

    def is_like(self, post):
        return Like.query.with_parent(self).filter_by(liked_id=post.id).first() is not None

    def like(self, post):
        if not self.is_like(post):
            like = Like(liker=self, liked=post)
            post.like += 1
            db.session.add(like)
            db.session.commit()

    def unlike(self, post):
        like = Like.query.with_parent(self).filter_by(liked_id=post.id).first()
        if like:
            post.like -= 1
            db.session.delete(like)
            db.session.commit()

    #  定义关系
    post = db.relationship('Post', back_populates='user')
    comment = db.relationship('Comment', cascade='all')
    liked_list = db.relationship('Like', back_populates='liker', cascade='all')


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    time = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    author_name = db.Column(db.String, db.ForeignKey('author.username'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))


class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    liker_id = db.Column(db.Integer, db.ForeignKey('author.id'))
    liked_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    liker = db.relationship('Author', back_populates='liked_list', lazy='joined')
    liked = db.relationship('Post', back_populates='liker_list', lazy='joined')


class Timeline(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    type = db.Column(db.String, default='other')  # 'like' or 'comment'
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    username_1 = db.Column(db.String)
    username_2 = db.Column(db.String)
    post = db.relationship('Post', back_populates='timeline')
    comment = db.Column(db.Text)
