from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed
from wtforms import StringField, SubmitField, TextAreaField, PasswordField, BooleanField, FileField
from wtforms import ValidationError
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo

from emoji_story.models import Author


class StoryForm(FlaskForm):
    story = TextAreaField('Your story goes like this:',
                          validators=[DataRequired(),
                                      Length(10, 500, message="Your story should be 10-500 letters.")],
                          render_kw={'placeholder': "No clue? Try refresh to get another topic!"})
    submit = SubmitField()


class LoginForm(FlaskForm):
    email = EmailField('Email',
                       validators=[Email(),
                                   DataRequired(message='Please input a valid emails')],
                       render_kw={'placeholder': 'emails@example.com'})
    password = PasswordField('Password',
                             validators=[DataRequired('Please input password')],
                             render_kw={'placeholder': '**********'})
    remember = BooleanField('Remember me (30-Day)')
    submit = SubmitField('Go!')


class SignUpForm(FlaskForm):
    email = EmailField('Email',
                       validators=[Email(),
                                   DataRequired(),
                                   Length(1, 64)],
                       render_kw={'placeholder': 'emails@example.com'})
    username = StringField('Name',
                           validators=[DataRequired(),
                                       Length(1, 20),
                                       Regexp('^[a-zA-Z0-9]*$',
                                              message='The name should contain only a-z, A-Z and 0-9')],
                           render_kw={'placeholder': 'Emoji'})
    password = PasswordField('Password',
                             validators=[DataRequired(),
                                         Length(8, 128),
                                         EqualTo('confirm_password', message="Passwords don't match")],
                             render_kw={'placeholder': '********'})
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired()],
                                     render_kw={'placeholder': '********'})

    # 验证邮箱是否重复
    def validate_email(self, field):
        if Author.query.filter_by(email=field.data.lower()).first():
            raise ValidationError("The emails is already in use.")

    # 验证用户名是否重复
    def validate_username(self, field):
        if Author.query.filter_by(username=field.data).first():
            raise ValidationError('The name is already in use.')

    submit = SubmitField('OK!')


class DeleteStoryForm(FlaskForm):
    submit = SubmitField('Delete')


class LikeForm(FlaskForm):
    submit = SubmitField('Like')


class CommentForm(FlaskForm):
    body = TextAreaField('Write down your comment:',
                         validators=[DataRequired(),
                                     Length(1, 500, message="Your commnet should be 1-500 letters.")],
                         render_kw={'placeholder': "Be nice :)"})
    submit = SubmitField('Send')


class ChangePwdForm(FlaskForm):
    old_pwd = PasswordField('Old Password:',
                            validators=[DataRequired()],
                            render_kw={'placeholder': '********'})
    new_pwd = PasswordField('New Password',
                            validators=[DataRequired(),
                                        Length(8, 128),
                                        EqualTo('confirm_pwd', message="Passwords don't match")],
                            render_kw={'placeholder': '********'})
    confirm_pwd = PasswordField('Confirm Password',
                                validators=[DataRequired()],
                                render_kw={'placeholder': '********'})
    submit = SubmitField('OK')


class ConfirmEmailForm(FlaskForm):
    submit = SubmitField('Confirm')


class ForgetPwdForm(FlaskForm):
    email = EmailField('Email',
                       validators=[DataRequired()],
                       render_kw={'placeholder': 'input your email'})
    submit = SubmitField('OK')


class ResetPwdForm(FlaskForm):
    email = EmailField('Email',
                       validators=[DataRequired()],
                       render_kw={'placeholder': 'input your email'})
    new_pwd = PasswordField('New Password',
                            validators=[DataRequired(),
                                        Length(8, 128),
                                        EqualTo('confirm_pwd', message="Passwords don't match")],
                            render_kw={'placeholder': '********'})
    confirm_pwd = PasswordField('Confirm Password',
                                validators=[DataRequired()],
                                render_kw={'placeholder': '********'})
    submit = SubmitField('OK')


class ProfileForm(FlaskForm):
    bio = TextAreaField('bio',
                        validators=[Length(0, 140)],
                        )
    submit_profile = SubmitField('Submit', )


class ProfilePhotoForm(FlaskForm):
    profile_photo = FileField(validators=[FileRequired(),
                                          FileAllowed(['jpg', 'jpeg', 'gif', 'png'])])
    submit_profile_photo = SubmitField('Upload')
