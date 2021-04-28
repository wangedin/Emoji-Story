from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

moment = Moment()
db = SQLAlchemy()
csrf = CSRFProtect()
mail = Mail()

#  初始化登陆管理对象
login_manager = LoginManager()
login_manager.login_view = 'user.login'
login_manager.login_message_category = 'warning'
login_manager.login_message = "Oops, You haven't logged in yet!"


@login_manager.user_loader
def load_user(user_id):
    from emoji_story.models import Author
    user = Author.query.get(int(user_id))
    return user


def load_post(post_id):
    from emoji_story.models import Post
    post = Post.query.get(int(post_id))
    return post
