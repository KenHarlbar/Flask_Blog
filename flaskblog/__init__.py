from flask import Flask
from pony.flask import Pony
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from .config import Config


app = Flask(__name__)
app.config.from_object(Config)
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
