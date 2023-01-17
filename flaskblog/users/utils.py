from flask_mail import Message
from flaskblog import mail
from flask import url_for
import os
from PIL import Image
import secrets
from flaskblog import app


def send_email_token(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
    {url_for('users.reset_token', token=token, _external=True)}
    If you did not make this request the ignore this email and nothing will change.
    '''
    mail.send(msg)


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