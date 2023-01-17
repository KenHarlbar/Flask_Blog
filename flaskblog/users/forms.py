from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flaskblog.models import User
from flask_login import current_user


class RegistrationForm(FlaskForm):
    """ A class that defines a registration form for users """
    username = StringField('Username',
                           validators=[DataRequired(),
                                       Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(),
                                    Email()])
    password = PasswordField('Password',
                             validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(),
                                                 EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.get(username=username.data)
        if user:
            raise ValidationError('This username has \
                    already been taken, please choose \
                    another username')

    def validate_email(self, email):
        email = User.get(email=email.data)
        if email:
            raise ValidationError('This Email already \
                    exists, please log in instead')


class LoginForm(FlaskForm):
    """ A class that defines a registration form for users """
    email = StringField('Email',
                        validators=[DataRequired(),
                                    Email()])
    password = PasswordField('Password',
                             validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    """ A class that defines a registration form for users """
    username = StringField('Username',
                           validators=[DataRequired(),
                                       Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(),
                                    Email()])
    picture = FileField('Update Profile Picture',
                        validators=[FileAllowed(['png', 'jpg'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data == current_user.username:
            user = User.get(username=username.data)
            if user:
                raise ValidationError('This username has \
                        already been taken, please choose \
                        another username')

    def validate_email(self, email):
        if email.data == current_user.email:
            email = User.get(email=email.data)
            if email:
                raise ValidationError('This Email already \
                        exists, please log in instead')


class RequestResetForm(FlaskForm):
    """ A class for taking a user email and checking if it exists in the
    database """
    email = StringField('Email',
                        validators=[DataRequired(),
                                    Email()])
    submit = SubmitField('Request Reset Password')

    def validate_email(self, email):
        user = User.get(email=email.data)
        if not user:
            raise ValidationError('There is no account with that email, \
                                  Please create an account instead')


class ResetPasswordForm(FlaskForm):
    """ This class accepts a new password for a user and stores it's hash in the database """
    password = PasswordField('Password',
                             validators=[DataRequired()])
    confirm_password = PasswordField('Password',
                                     validators=[DataRequired(),
                                                 EqualTo('password')])
    submit = SubmitField('Reset Password')
