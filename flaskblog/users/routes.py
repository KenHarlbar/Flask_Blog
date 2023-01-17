from flask import Blueprint as BP
from flask_login import current_user, login_user, logout_user, login_required
from flask import redirect, url_for, flash, render_template, request
from pony.orm import db_session
from forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm
from math import ceil
from flaskblog import bcrypt
from flaskblog.models import User, Post
from .utils import save_picture, send_email_token
from pony.orm import desc


users = BP('users', __name__)


@users.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).\
                decode('utf-8')
        with db_session:
            user = User(username=form.username.data,
                        password=hashed_password,
                        email=form.email.data)
        flash('Your account has been created, \
                you are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get(email=form.email.data)
        if user and bcrypt.check_password_hash(
                user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else \
                redirect(url_for('home'))
        else:
            flash('Login Unsuccessful, please check \
                    username and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@users.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            with db_session:
                current_user.image_file = picture_file
        with db_session:
            current_user.username = form.username.data
            current_user.email = form.email.data
        flash('Your account has been updated', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' +
                         current_user.image_file)
    return render_template('account.html', title='Account',
                           form=form, image_file=image_file)


@users.route('/user/<string:username>')
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    pagesize = 5
    user = User.get(username=username)
    total_number_of_posts = len(Post.select(lambda p: p.author == user)[:])
    no_of_pages = total_number_of_posts / pagesize
    no_of_pages = ceil(no_of_pages)
    posts = Post.select(lambda p: p.author == user).\
            order_by(lambda p: desc(p.date_posted)).\
            page(pagenum=page, pagesize=pagesize)[:]            
    return render_template('user_posts.html',
                            page=page,
                            posts=posts,
                            no_of_pages=no_of_pages,
                            title=user.username + '\'s posts',
                            user=user,
                            count=total_number_of_posts)


@users.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.get(email=form.email.data)
        send_email_token(user)
        flash('An email has been sent with instructions to reset your password', 'info')
        return redirect(url_for('login'))
    return render_template('reset_password.html',
                           title='Reset Password',
                           form=form)


@users.route('/reset_token/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if not user:
        flash('This is an invalid or expired token', 'warning')
        return redirect(url_for('reset_password'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).\
                decode('utf-8')
        with db_session:
            user.password = hashed_password
        flash('Your password has been updated, \
                you are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html',
                           title='Reset Password',
                           form=form)
