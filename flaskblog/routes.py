from math import ceil
import secrets
import os
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from .forms import (RegistrationForm, LoginForm, UpdateAccountForm, PostForm,
                    RequestResetForm, ResetPasswordForm)
from . import bcrypt, app, mail
from .models import User, Post
from pony.orm import db_session, desc
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message


@app.route('/')
@app.route('/home')
def home():
    page = request.args.get('page', 1, type=int)
    pagesize = 5
    with db_session:
        total_number_of_posts = len(Post.select(lambda p: p)[:])
    no_of_pages = total_number_of_posts / pagesize
    no_of_pages = ceil(no_of_pages)
    with db_session:
        posts = Post.select(lambda p: p).order_by(lambda p: desc(p.date_posted)).page(pagenum=page, pagesize=pagesize)
    return render_template('home.html', posts=posts, no_of_pages=no_of_pages, page=page)


@app.route('/about')
def about():
    return render_template('about.html', title='About')


@app.route('/register', methods=['GET', 'POST'])
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


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        with db_session:
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


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    """ Creates a new file then saves the picture in the new file """
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics',
                                picture_fn)
    # resize the image
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route('/account', methods=['GET', 'POST'])
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


@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        with db_session:
            post = Post(title=form.title.data, content=form.content.data, author=current_user)
        flash('Your post has been created', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post',
                           form=form, legend='Update Post')


@app.route('/post/<int:post_id>')
def post(post_id):
    import pony
    with db_session:
        try:
            post = Post[post_id]
        except:
            abort(404)
    if post:
        return render_template('post.html', title=post.title, post=post)
    abort(404)


@app.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    with db_session:
        post = Post[post_id]
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        with db_session:
            post.title = form.title.data
            post.content = form.content.data
        flash('Your Post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    form.title.data = post.title
    form.content.data = post.content
    return render_template('create_post.html', title='Update Post',
                           form=form, legend='Update Post')


@app.route('/post/<int:post_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_post(post_id):
    with db_session:
        post = Post[post_id]
    if not post:
        abort(404)
    if post.author != current_user:
        abort(403)
    with db_session:
        Post.delete(post)
    flash('Your post has been deleted', 'success')
    return redirect(url_for('home'))


@app.route('/user/<string:username>')
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    pagesize = 5
    # with db_session:
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


def send_email_token(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
    {url_for('reset_token', token=token, _external=True)}
    If you did not make this request the ignore this email and nothing will change.
    '''
    mail.send(msg)


@app.route('/reset_password', methods=['GET', 'POST'])
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


@app.route('/reset_token/<token>', methods=['GET', 'POST'])
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
