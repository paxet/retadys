from peewee import SqliteDatabase, Model, DateTimeField, IntegerField, Check
from playhouse.migrate import SqliteMigrator, migrate

db = None


def init_db(db_name='datos_retadys.sqlite'):
    return SqliteDatabase(db_name)


def get_db():
    global db
    if not db:
        db = init_db()
    return db


def remove_accents(text):
    """
    Replaced accented vowels from text with plain vowels
    :param text: The original string
    :return:
    """
    vowels = {'à': 'a', 'á': 'a', 'â': 'a', 'ã': 'a', 'ä': 'a', 'å': 'a', 'ā': 'a', 'ă': 'a', 'ą': 'a',
              'À': 'A', 'Á': 'A', 'Â': 'A', 'Ã': 'A', 'Ä': 'A', 'Å': 'A', 'Ā': 'A', 'Ă': 'A', 'Ą': 'A',
              'è': 'e', 'é': 'e', 'ê': 'e', 'ë': 'e', 'ē': 'e', 'ĕ': 'e', 'ė': 'e', 'ę': 'e', 'ě': 'e',
              'È': 'E', 'É': 'E', 'Ê': 'E', 'Ë': 'E', 'Ē': 'E', 'Ĕ': 'E', 'Ė': 'E', 'Ę': 'E', 'Ě': 'E',
              'ì': 'i', 'í': 'i', 'î': 'i', 'ï': 'i', 'ĩ': 'i', 'ī': 'i', 'ĭ': 'i',
              'Ì': 'I', 'Í': 'I', 'Î': 'I', 'Ï': 'I', 'Ĩ': 'I', 'Ī': 'I', 'Ĭ': 'I',
              'ò': 'o', 'ó': 'o', 'ô': 'o', 'õ': 'o', 'ö': 'o', 'ō': 'o', 'ŏ': 'o', 'ő': 'o',
              'Ò': 'O', 'Ó': 'O', 'Ô': 'O', 'Õ': 'O', 'Ö': 'O', 'Ō': 'O', 'Ŏ': 'O', 'Ő': 'O',
              'ù': 'u', 'ú': 'u', 'û': 'u', 'ü': 'u', 'ũ': 'u', 'ū': 'u', 'ŭ': 'u', 'ů': 'u',
              'Ù': 'U', 'Ú': 'U', 'Û': 'U', 'Ü': 'U', 'Ũ': 'U', 'Ū': 'U', 'Ŭ': 'U', 'Ů': 'U'}
    return "".join(vowels.get(k, k) for k in text)


def migrate_lastversion():
    return migrate_v1()


def migrate_v1():
    ddbb = get_db()
    migrator = SqliteMigrator(ddbb)
    fecha_entrega_prevista = DateTimeField(formats='%d-%m-%Y %H:%M:%S', null=True)
    horas_trabajo_diario = IntegerField(default=8,
                                        db_column='horas_trabajo_diario',
                                        constraints=[Check('horas_trabajo_diario <= 24')])
    with ddbb.transaction():
        migrate(
            migrator.add_column('programacion', 'fecha_entrega_prevista', fecha_entrega_prevista),
            migrator.add_column('maquina', 'horas_trabajo_diario', horas_trabajo_diario),
        )
        actulizado = True
    return actulizado


class BaseModel(Model):
    class Meta:
        database = get_db()
