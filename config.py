import os
from base64 import b64encode

APP_NAME = 'retadys'

SECRET_KEY = b64encode(os.urandom(64)).decode('utf-8')[:30]
WTF_CSRF_KEY = b64encode(os.urandom(64)).decode('utf-8')[:30]
WTF_CSRF_SECRET_KEY = b64encode(os.urandom(64)).decode('utf-8')[:30]

MAIL_SERVER = 'localhost'
MAIL_PORT = '25'
MAIL_USE_TLS = False
MAIL_USE_SSL = False
MAIL_DEFAULT_SENDER = 'info@{}.io'.format(APP_NAME)

ADMINS = ['someone@rareserver.net']
