from datetime import datetime
from flask import Blueprint, render_template, flash, Markup, jsonify, redirect, url_for, request, current_app
from playhouse.shortcuts import model_to_dict, fn
from peewee import DoesNotExist
from webapp.db import db
from webapp.mod_root.models import Programacion, Trabajo, Maquina

listener_root = Blueprint('root', __name__)


def get_tareas(maquinas):
    tmaq = {}
    for maq in maquinas:
        trabajos = Trabajo.select().where(Trabajo.maquina == maq)
        tareas = Programacion.select().where((Programacion.finalizada == False) &
                                             (Programacion.trabajo << trabajos)).order_by(Programacion.prioridad.asc())
        tmaq[maq.codigo] = tareas
    return tmaq


@listener_root.route('/', methods=['GET'])
def index():
    mod = request.args.get('modificable')
    if not mod:
        mod = None
    maquinas = Maquina.select()
    tmaq = get_tareas(maquinas)
    return render_template('root/index.html',
                           maquinas=maquinas,
                           tmaq=tmaq,
                           # appname=current_app.config['APP_NAME'],
                           modificable=mod)


@listener_root.route('/seccion/<int:idseccion>', methods=['GET'])
def detalle_seccion(idseccion):
    mod = request.args.get('modificable')
    if not mod:
        mod = None
    maquinas = Maquina.select().where(Maquina.seccion == idseccion)
    tmaq = get_tareas(maquinas)
    return render_template('root/index.html',
                           maquinas=maquinas,
                           tmaq=tmaq,
                           modificable=mod,
                           refresh_url='/seccion/{}'.format(idseccion))


@listener_root.route('/aumentar-prioridad/<int:idtarea>', methods=['POST'])
def aumentar_prioridad(idtarea):
    conseguido = "False"
    tarea_aumentar = Programacion.get(Programacion.id == idtarea)
    trabajos = Trabajo.select().where(Trabajo.maquina == tarea_aumentar.trabajo.maquina)
    try:
        # tarea_disminuir = Programacion.get((Programacion.prioridad == (tarea_disminuir.prioridad - 1)) &
        #                                   (Programacion.trabajo << trabajos))
        tarea_disminuir = Programacion.select().where(
            (Programacion.finalizada == False) &
            (Programacion.prioridad < tarea_aumentar.prioridad) &
            (Programacion.trabajo << trabajos)
        ).order_by(
            Programacion.prioridad.desc()
        ).limit(1).get()
    except DoesNotExist:
        conseguido = "False"
    else:
        if tarea_disminuir:
            with db.atomic():
                # tarea_disminuir.prioridad += 1
                # tarea_aumentar.prioridad -= 1
                pri = tarea_disminuir.prioridad
                tarea_disminuir.prioridad = tarea_aumentar.prioridad
                tarea_aumentar.prioridad = pri
                tarea_disminuir.save()
                tarea_aumentar.save()
                conseguido = "True"
    return conseguido


@listener_root.route('/disminuir-prioridad/<int:idtarea>', methods=['POST'])
def disminuir_prioridad(idtarea):
    conseguido = "False"
    tarea_disminuir = Programacion.get(Programacion.id == idtarea)
    trabajos = Trabajo.select().where(Trabajo.maquina == tarea_disminuir.trabajo.maquina)
    try:
        # tarea_aumentar = Programacion.get((Programacion.prioridad == (tarea_disminuir.prioridad + 1)) &
        #                                   (Programacion.trabajo << trabajos))
        tarea_aumentar = Programacion.select().where(
            (Programacion.finalizada == False) &
            (Programacion.prioridad > tarea_disminuir.prioridad) &
            (Programacion.trabajo << trabajos)
        ).order_by(
            Programacion.prioridad.asc()
        ).limit(1).get()
    except DoesNotExist as e:
        conseguido = "False"
    else:
        if tarea_aumentar:
            with db.atomic():
                # tarea_disminuir.prioridad += 1
                # tarea_aumentar.prioridad -= 1
                pri = tarea_disminuir.prioridad
                tarea_disminuir.prioridad = tarea_aumentar.prioridad
                tarea_aumentar.prioridad = pri
                tarea_disminuir.save()
                tarea_aumentar.save()
                conseguido = "True"
    return conseguido


@listener_root.route('/mover-a-maquina', methods=['POST'])
def mover_a_maquina():
    idmaquina = request.form.get('idmaquina')
    idtarea = request.form.get('idtarea')
    with db.atomic():
        try:
            tarea_mover = Programacion.get(Programacion.id == idtarea)
            maquina_destino = Maquina.get(Maquina.id == idmaquina)
            maquina_origen = tarea_mover.trabajo.maquina
            tarea_mover.trabajo.maquina = maquina_destino
            tarea_mover.trabajo.save()
            # Para mover la tarea, le ponemos la minima prioridad en la siguiente maquina
            trabajos_maquina_destino = Trabajo.select().where(Trabajo.maquina == maquina_destino)
            menor_prioridad = Programacion.select(fn.Max(Programacion.prioridad)
                                                  ).where(Programacion.trabajo << trabajos_maquina_destino).scalar()
            prioridad_tarea_movida = tarea_mover.prioridad
            tarea_mover.prioridad = menor_prioridad + 1
            # Y le bajamos la prioridad a todos los trabajos que han quedado en esta maquina y estaban detras
            trabajos_maquina_origen = Trabajo.select().where(Trabajo.maquina == maquina_origen)
            Programacion.update(prioridad=(Programacion.prioridad-1)).where(
                    (Programacion.prioridad > prioridad_tarea_movida) &
                    (Programacion.trabajo << trabajos_maquina_origen)
            ).execute()
            tarea_mover.save()
        except DoesNotExist as e:
            flash(Markup("Se produjo un error:" + e.__cause__), 'error')
            conseguido = "False"
        except Exception as e:
            flash(Markup("Se produjo un error:" + e.__cause__), 'error')
            conseguido = "False"
        else:
            conseguido = "True"
    print(conseguido)
    return conseguido


@listener_root.route('/maquinas/<int:idmaquina>', methods=['GET'])
def maquina_detalle(idmaquina):
    maq = Maquina.get(Maquina.id == idmaquina)
    return jsonify(model_to_dict(maq, backrefs=True))


@listener_root.route('/tareas', methods=['GET'])
def tarea_nueva():
    idtrabajo = request.args.get('form-job-work')
    idmaquina = request.args.get('form-job-machine')
    orden_fabricacion = request.args.get('form-job-work-new')
    descripcion = request.args.get('form-job-work-desc-new')
    horas = request.args.get('form-job-work-hours-new')
    fecha_prev = request.args.get('form-job-work-date-new')
    with db.atomic():
        if idtrabajo:
            trabajo = Trabajo.get(Trabajo.id == idtrabajo)
        elif orden_fabricacion and descripcion:
            trabajo, created = Trabajo.get_or_create(orden_fabricacion=orden_fabricacion,
                                                     defaults={'maquina': Maquina.get(Maquina.id == idmaquina),
                                                               'descripcion': descripcion,
                                                               'horas_realizacion': horas})
        else:
            trabajo = None
            flash(Markup('Por favor, seleccione tarea o escriba Orden de Fabricación y Descripción'))
        if trabajo:
            tarea = Programacion()
            trabajos = Trabajo.select().where(Trabajo.maquina == trabajo.maquina)
            max_prioridad = Programacion.select(fn.Max(Programacion.prioridad)).where(
                (Programacion.trabajo << trabajos) &
                (Programacion.finalizada == False)
            ).scalar()
            if not max_prioridad:
                max_prioridad = 0
            tarea.prioridad = max_prioridad + 1
            tarea.fecha_entrega_prevista = datetime.strptime(fecha_prev, '%d/%m/%Y %H:%M')
            tarea.trabajo = trabajo
            tarea.finalizada = False
            tarea.save()
            flash(Markup('Se ha añadido la tarea'))
        else:
            flash(Markup('No se ha podido insertar la tarea'))
    return redirect(url_for('root.index', modificable=1))


@listener_root.route('/finalizar-tarea/<int:idtarea>', methods=['POST'])
def tarea_finalizar(idtarea):
    with db.atomic():
        tarea = Programacion.get(Programacion.id == idtarea)
        tarea.finalizada = True
        tarea.save()
        # Actualizar la prioridad de las tareas para esa maquina
        trabajos = Trabajo.select().where(Trabajo.maquina == tarea.trabajo.maquina)
        tareas = Programacion.select().where(Programacion.trabajo << trabajos)
        for t in tareas:
            if t.finalizada and t.prioridad > tarea.prioridad and t.id != tarea.id:
                t.prioridad -= 1
                t.save()
        finalizada = 'ok'
    return finalizada


@listener_root.route('/keep-alive', methods=['POST'])
def keep_alive():
    return ''
