from flask import request, render_template,  Blueprint as BP
from pony.orm import desc
from flaskblog.models import Post
from math import ceil


main = BP('main', __name__)


@main.route('/')
@main.route('/home')
def home():
    page = request.args.get('page', 1, type=int)
    pagesize = 5
    total_number_of_posts = len(Post.select(lambda p: p)[:])
    no_of_pages = total_number_of_posts / pagesize
    no_of_pages = ceil(no_of_pages)
    posts = Post.select(lambda p: p).order_by(lambda p: desc(p.date_posted)).page(pagenum=page, pagesize=pagesize)
    return render_template('home.html', posts=posts, no_of_pages=no_of_pages, page=page)


@main.route('/about')
def about():
    return render_template('about.html', title='About')