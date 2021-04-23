"""
    :author: Wang Wang (王望)
    :copyright: © 2021 Wang Wang <wangedin@hotmail.com>
    :license: MIT, see LICENSE for more details.
"""

import os

from flask import Flask

from emoji_story.blueprints.email import email_bp
from emoji_story.blueprints.main_page import main_page_bp
from emoji_story.blueprints.user import user_bp
from emoji_story.extensions import db, moment, login_manager, csrf, mail
from emoji_story.settings import config

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')
        print(config_name)

    app = Flask('emoji_story')
    app.config.from_object(config[config_name])

    register_extensions(app)
    register_blueprints(app)

    return app


def register_blueprints(app):
    app.register_blueprint(main_page_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(email_bp)


def register_extensions(app):
    db.init_app(app)
    moment.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
