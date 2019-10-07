import os
import locale
from datetime import datetime
from flask import Flask, g, request, url_for, render_template
from werkzeug.contrib.fixers import ProxyFix
from retadys import db
from retadys.mail import mailer
from retadys.mod_root.controllers import listener_root
from retadys.mod_admin.controllers import admin

__author__ = 'paxet'
__version__ = '0.1.0.dev1'
__description__ = 'Aplicación para gestionar qué tareas debe realizar un trabajador y en qué máquinas'


if os.name == 'nt':
    locale.setlocale(locale.LC_ALL, 'Spanish')  # Windows
else:
    locale.setlocale(locale.LC_ALL, 'es_ES.utf8')  # other (unix)

app = Flask(__name__)
app.config.from_object('config')

if not app.debug:
    # Production runs behind a proxy
    app.wsgi_app = ProxyFix(app.wsgi_app)
    # Send a mail in case of errors
    import logging
    from logging import Formatter
    from logging.handlers import SMTPHandler
    mail_handler = SMTPHandler(app.config['MAIL_SERVER'],
                               app.config['MAIL_DEFAULT_SENDER'],
                               app.config['ADMINS'],
                               '[{app_name}] Error happened'.format(app_name=app.config['APP_NAME']))
    mail_handler.setFormatter(Formatter('''
    Message type:       %(levelname)s
    Location:           %(pathname)s:%(lineno)d
    Module:             %(module)s
    Function:           %(funcName)s
    Time:               %(asctime)s

    Message:
    --------

    %(message)s
    '''))
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)

# Setup DataBase
database = db.get_db()
# database.create_tables([Resource])

# Setup Flask-Mail
mailer.init_app(app)

# Setup Flask-Admin
admin.init_app(app)

# Loading blueprints
app.register_blueprint(listener_root)


# Filtros para las Jinja Templates
@app.template_filter()
def floathumanreadable(numero: float) -> str:
    result = locale.format("%.2f", numero, True, True)
    return result

# TODO Aqui ceo que falta anyadir el floatnumber... a los filtros


def format_datetime(fecha: datetime, formato='completo') -> str:
    if formato == 'completo':
        formato = "%d/%m/%Y %H:%M"
    elif formato == 'abreviado':
        formato = "%d/%m/%Y"
    return fecha.strftime(formato)

app.jinja_env.filters['datetime'] = format_datetime


def url_for_other_page(page):
    """
    Este método se gasta para la paginación
    :param page: The page to return
    """
    args = request.view_args.copy()
    args['page'] = page
    return url_for(request.endpoint, **args)

app.jinja_env.globals['url_for_other_page'] = url_for_other_page


@app.errorhandler(401)
def forbidden_401(exception):
    return render_template('errors/401.html', exception=exception), 401


@app.errorhandler(403)
def forbidden_403(exception):
    return render_template('errors/403.html', exception=exception), 403


@app.errorhandler(404)
def forbidden_404(exception):
    return render_template('errors/404.html', exception=exception), 404


@app.before_request
def before_request():
    g.db = database
    g.db.connect()


@app.after_request
def after_request(response):
    g.db.close()
    return response
