from flask_admin import Admin
from webapp.mod_root.models import Maquina, Trabajo, Programacion, Seccion  # , Usuario
from webapp.mod_admin.models import EditableModelView, ProgramacionModelView


admin = Admin()
admin.add_view(EditableModelView(Seccion))
admin.add_view(EditableModelView(Maquina))
admin.add_view(EditableModelView(Trabajo))
# admin.add_view(EditableModelView(Usuario))
admin.add_view(ProgramacionModelView(Programacion))
