from flask import flash, redirect, url_for, abort, render_template, Blueprint as BP
from flask_login import login_required, current_user
from forms import PostForm
from pony.orm import db_session
from flaskblog.models import Post


posts = BP('posts', __name__)


@posts.route('/post/new', methods=['GET', 'POST'])
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


@posts.route('/post/<int:post_id>')
def post(post_id):
    try:
        post = Post[post_id]
    except:
        abort(404)
    if post:
        return render_template('post.html', title=post.title, post=post)
    abort(404)


@posts.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
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


@posts.route('/post/<int:post_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_post(post_id):
    post = Post[post_id]
    if not post:
        abort(404)
    if post.author != current_user:
        abort(403)
    with db_session:
        Post.delete(post)
    flash('Your post has been deleted', 'success')
    return redirect(url_for('home'))