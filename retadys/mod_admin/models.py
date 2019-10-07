from datetime import date, datetime
from flask_admin.contrib.peewee import ModelView
from flask_admin.model import typefmt
from playhouse.shortcuts import fn
from retadys.mod_root.models import Programacion, Trabajo


def datetime_format(view, value):
    return value.strftime('%d/%m/%Y %H:%M')

MY_DEFAULT_FORMATTERS = dict(typefmt.BASE_FORMATTERS)
MY_DEFAULT_FORMATTERS.update({
    datetime: datetime_format
})


class EditableModelView(ModelView):
    column_editable_list = ['codigo', 'descripcion']
    column_type_formatters = MY_DEFAULT_FORMATTERS


class ProgramacionModelView(EditableModelView):
    column_editable_list = ['codigo', 'descripcion', 'finalizada']
    # form_excluded_columns = ['prioridad']

    # form_args = dict(
    #     start=dict(format='%Y-%m-%d %I:%M %p')  # changes how the input is parsed by strptime (12 hour time)
    # )
    # form_widget_args = dict(
    #     start={'data-date-format': u'yyyy-mm-dd HH:ii P', 'data-show-meridian': 'True'}
    #     # changes how the DateTimeField displays the time
    # )

    def on_model_change(self, form, tarea, is_created):
        if is_created:
            trabajos_maquina = Trabajo.select().where(Trabajo.maquina == tarea.trabajo.maquina)
            max_prioridad = Programacion.select(fn.Max(Programacion.prioridad)).where(
                Programacion.trabajo << trabajos_maquina &
                Programacion.finalizada == False
            ).scalar()
            if not max_prioridad:
                max_prioridad = 0
            tarea.prioridad = max_prioridad + 1
