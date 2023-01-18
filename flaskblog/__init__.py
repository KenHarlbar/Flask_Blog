from flask import Flask
from pony.flask import Pony
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from .config import Config



pony = Pony()
bcrypt = Bcrypt()
login_manager = LoginManager()
mail = Mail()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'





def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    pony.init_app()
    bcrypt.init_app()
    login_manager.init_app()
    mail.init_app()

    from .users.routes import users
    from .posts.routes import posts
    from .main.routes import main

    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(main)

    return app
