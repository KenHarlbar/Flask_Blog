from os import getenv
from flask import Flask
from pony.flask import Pony
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail


app = Flask(__name__)
app.config.update(dict(
    DEBUG=False,
    SECRET_KEY='f03d7f578799cd79ac0bfa6db387418e',
    MAIL_SERVER='smtp.googlemail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME=getenv('EMAIL_USER'),
    MAIL_PASSWORD=getenv('EMAIL_PASS'),
    PONY={
        'provider': 'sqlite',
        'filename': 'site.db',
        'create_db': True
    }
))

Pony(app)
bcrypt = Bcrypt()
login_manager = LoginManager(app)
mail = Mail(app)
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'


from .users.routes import users
from .posts.routes import posts
from .main.routes import main

app.register_blueprint(users)
app.register_blueprint(posts)
app.register_blueprint(main)
