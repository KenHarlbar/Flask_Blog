from os import getenv


class Config:
    DEBUG = False
    SECRET_KEY = 'f03d7f578799cd79ac0bfa6db387418e'
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = getenv('EMAIL_USER')
    MAIL_PASSWORD = getenv('EMAIL_PASS')
    PONY = {
        'provider': 'sqlite',
        'filename': 'site.db',
        'create_db': True
    }