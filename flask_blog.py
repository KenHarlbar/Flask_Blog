from flask import Flask, render_template, url_for, flash, redirect
from pony.flask import Pony
from pony.orm import *
from forms import RegistrationForm, LoginForm
from datetime import datetime
from faker import Faker

fake = Faker()
app = Flask(__name__)
app.config.update(dict(
    DEBUG = False,
    SECRET_KEY = 'f03d7f578799cd79ac0bfa6db387418e',
    PONY = {
        'provider': 'mysql',
        'host': 'localhost',
        'user': 'hbnb_test',
        'passwd': 'Hbnb_test_pwd01#',
        'db': 'hbnb_test_db'
    }
))

db = Database()


class User(db.Entity):
    id = PrimaryKey(int, auto=True)
    username = Required(str, unique=True, size=20)
    email = Required(str, unique=True, size=120)
    image_file = Required(str, default='default.jpg', size=20)
    password = Required(str, size=60)
    posts = Set('Post')

    #def __repr__(self):
        #return f'User("{self.username}", "{self.email}", "{self.image_file}")'

class Post(db.Entity):
    id = PrimaryKey(int, auto=True)
    title = Required(str, size=100)
    date_posted = Required(datetime, default=lambda d: datetime.utcnow)
    content = Required(str)
    user_id = Required(User)

    #def __repr__(self):
        #return f"Post('{self.title}', '{self.date_posted}')"



db.bind(**app.config['PONY'])
db.generate_mapping(create_tables=True)

posts = [
    {
        'author': fake.name(),
        'title': 'Blog post 1',
        'content': fake.sentence(),
        'date_posted': fake.date() + ' ' + fake.time()
    },
    {
        'author': fake.name(),
        'title': 'Blog post 2',
        'content': fake.sentence(),
        'date_posted': fake.date() + ' ' + fake.time()
    },
    {
        'author': fake.name(),
        'title': 'Blog post 3',
        'content': fake.sentence(),
        'date_posted': fake.date() + ' ' + fake.time()
    }
]


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', posts=posts)

@app.route('/about')
def about():
    return render_template('about.html', title='About')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash('Account created for {{ form.username.data }}!', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@blog.com' and form.password.data == 'password':
            flash('you have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful, please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)


if __name__ == '__main__':
    app.run(debug=True)
