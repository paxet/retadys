#!/usr/bin/env python3
import importlib
import argparse

# from flask_debugtoolbar import DebugToolbarExtension

import retadys
from retadys import app, db
from retadys.mod_root.models import Maquina, Programacion, Trabajo, Seccion  # , Usuario
import config

db_tables = [Maquina, Trabajo, Programacion, Seccion]  # Usuario


def class_for_name(module_name, class_name):
    """Gracias a m.kocikowski --> http://stackoverflow.com/a/13808375"""
    # load the module, will raise ImportError if module cannot be loaded
    m = importlib.import_module(module_name)
    # get the class, will raise AttributeError if class cannot be found
    c = getattr(m, class_name)
    return c


def create_tables():
    if db.get_db().is_closed():
        db.get_db().connect()
    db.get_db().create_tables(db_tables)
    print('Tables created')


def drop_tables():
    if db.get_db().is_closed():
        db.get_db().connect()
    db.get_db().drop_tables(db_tables)
    print('Tables dropped')


def migrate_db():
    if db.get_db().is_closed():
        db.get_db().connect()
    db.migrate_lastversion()


def get_app():
    """Devuelve el objeto de aplicación. Este método sólo se gasta en desarrollo"""
    # app.config['SECRET_KEY'] = 'development_secret'
    # app.config['WTF_CSRF_KEY'] = 'development_csrf_key'
    # app.config['WTF_CSRF_SECRET_KEY'] = 'development_csrf_secret'
    # toolbar = DebugToolbarExtension(app)
    return app


def interpret_args(args):
    commands = []
    if args.create:
        commands.append(create_tables)
    if args.create_one:
        raise NotImplementedError
    if args.drop:
        commands.append(drop_tables)
    if args.migrate:
        commands.append(migrate_db)
    if args.webserver:
        commands.append(lambda: get_app().run(host="127.0.0.1", port=5000))  # host="127.0.0.1", port=5000, debug=True
    if len(commands) > 0:
        for command in commands:
            command()
    else:
        parser.print_help()


if __name__ == '__main__':
    desc = '{appname} web project: {description}'.format(appname=config.APP_NAME, description=retadys.__description__)
    vers = '%(prog)s de {appname} {version}'.format(appname=config.APP_NAME, version=retadys.__version__)
    parser = argparse.ArgumentParser(description=desc)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-c', '--create',
                       help='Crear tablas en la BBDD',
                       action='store_true')
    group.add_argument('-o', '--create_one',
                       help='Crear la tabla indicada en la BBDD')
    group.add_argument('-d', '--drop',
                       help='Eliminar las tablas de la Base de Datos',
                       action='store_true',)
    group.add_argument('-m', '--migrate',
                       help='Migrar la Base de Datos y aplicar cambios',
                       action='store_true',)
    group.add_argument('-w', '--webserver',
                       help='Arrancar el servidor web integrado',
                       action='store_true',)
    parser.add_argument('--version',
                        action='version', version=vers)

    interpret_args(parser.parse_args())
