# -*- coding: utf-8 -*-
"""
    :author: Wang Wang (王望)
    :copyright: © 2021 Wang Wang <wangedin@hotmail.com>
    :license: MIT, see LICENSE for more details.
"""

import os
import sys

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# SQLite URI compatible
WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'


class BaseConfig(object):
    SECRET_KEY = os.getenv('SECRET_KEY')

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_USE_TLS = True
    MAIL_PORT = 587
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('SENDGRID_API_KEY')
    MAIL_DEFAULT_SENDER = ('Emoji Story', 'emojistory@hotmail.com')

    MAX_CONTENT_LENGTH = 3 * 1024 * 1024
    UPLOAD_PATH = os.path.join(basedir, 'profile_photo')


class Operations:
    CONFIRM = 'confirm'
    RESET_PASSWORD = 'reset-password'
    CHANGE_EMAIL = 'change-emails'


class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = prefix + os.path.join(basedir, 'data.db')


class TestingConfig(BaseConfig):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite:////Users/wangwang/Library/Application Support/Postgres/var-13/data.db"  # in-memory database


class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', prefix + os.path.join(basedir, 'data.db'))


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}

