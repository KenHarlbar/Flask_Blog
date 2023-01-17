from datetime import datetime
from flask_login import UserMixin
from pony.orm import *
# from . import login_manager

# @login_manager.user_loader
# def load_user(user_id):
#     with db_session:
#         return User.get(id=int(user_id))


db = Database()


class User(db.Entity, UserMixin):
    _table_ = 'users'
    id = PrimaryKey(int, auto=True)
    username = Required(str, unique=True)
    email = Required(str, unique=True)
    image_file = Required(str, default='default.jpg')
    password = Required(str)
    posts = Set('Post')

    def __repr__(self):
        return f'User("{self.username}", "{self.email}", "{self.image_file}")'

class Post(db.Entity):
    _table_ = 'posts'
    id = PrimaryKey(int, auto=True)
    title = Required(str)
    date_posted = Required(datetime, default=datetime.utcnow)
    content = Required(str)
    author = Required(User)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"


# from . import app
db.bind(provider='sqlite', filename='site.db', create_db=True)
db.generate_mapping(create_tables=True)
