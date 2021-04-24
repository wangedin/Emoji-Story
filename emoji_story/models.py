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
    delete = db.Column(db.Boolean, default=False)
    like = db.Column(db.Integer, default=0)
    #  定义外键
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'))
    #  定义双向关系
    user = db.relationship('Author', back_populates='post')
    comment = db.relationship('Comment')


class Author(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True)
    username = db.Column(db.String, unique=True)
    confirmed = db.Column(db.Boolean, default=False)
    pwd_hash = db.Column(db.String(128))
    like = db.Column(db.String, default=json.dumps({'like_post': []}))
    bio = db.Column(db.String(140), default='I am a very mysterious storyteller!')
    photo = db.Column(db.String, default='default.png')

    def set_password(self, password):
        self.pwd_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.pwd_hash, password)

    #  定义关系
    post = db.relationship('Post')
    comment = db.relationship('Comment')


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    time = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    author_name = db.Column(db.String, db.ForeignKey('author.username'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
