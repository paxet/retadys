from peewee import CharField, TextField, BooleanField, IntegerField, ForeignKeyField, DateTimeField, Check
from playhouse.shortcuts import fn
from retadys import worktime
from retadys.db import BaseModel


class Seccion(BaseModel):
    codigo = CharField(null=False, unique=True, max_length=20)
    descripcion = TextField(null=True)

    class Meta:
        order_by = ('codigo',)

    def __str__(self):
        return '{}: {}'.format(self.codigo, self.descripcion)


class Maquina(BaseModel):
    codigo = CharField(null=False, unique=True, max_length=20)
    descripcion = TextField(null=True)
    anotaciones = TextField(null=True)
    seccion = ForeignKeyField(Seccion, related_name='maquinas')
    horas_trabajo_diario = IntegerField(default=8,
                                        db_column='horas_trabajo_diario',
                                        constraints=[Check('horas_trabajo_diario <= 24')])

    # @property
    # def horas_trabajo_diario(self):
    #     return self.__horas_trabajo_diario
    #
    # @horas_trabajo_diario.setter
    # def horas_trabajo_diario(self, horas):
    #     self.__horas_trabajo_diario = horas

    class Meta:
        order_by = ('seccion', 'codigo',)

    def __str__(self):
        return '{} -> {}'.format(self.codigo, self.seccion.codigo)


class Trabajo(BaseModel):
    maquina = ForeignKeyField(Maquina, related_name='trabajos')
    orden_fabricacion = CharField(null=False, unique=True, max_length=20)
    horas_realizacion = IntegerField(default=1)
    descripcion = TextField(null=True)

    class Meta:
        order_by = ('maquina', 'orden_fabricacion', 'horas_realizacion',)

    def __str__(self):
        return '{} -> {}'.format(self.orden_fabricacion, self.maquina)


# class Usuario(BaseModel):
#     nombre = CharField(max_length=60)
#     apellidos = CharField(max_length=60)
#     anotaciones = TextField(null=True)
#     usuario = CharField(null=False, unique=True, max_length=60)
#     contrasenya = CharField(null=False, max_length=60)
#
#     class Meta:
#         order_by = ('apellidos',)
#
#     def __str__(self):
#        return '{}: {}'.format(self.apellidos, self.nombre)


class Programacion(BaseModel):
    trabajo = ForeignKeyField(Trabajo, related_name='programacion')
    # usuario = ForeignKeyField(Usuario, related_name='tareas')
    prioridad = IntegerField(default=5)
    finalizada = BooleanField(default=False)
    fecha_entrega_prevista = DateTimeField(null=True)

    @property
    def cumple_entrega(self):
        if self.fecha_entrega_prevista:
            # print(self.fecha_entrega_prevista)
            horas_trabajo_maquina = self.get_horas_trabajo()
            ###
            # progs = Programacion.select().join(Trabajo).where(
            #     (Trabajo.maquina == self.trabajo.maquina) &
            #     (Programacion.prioridad <= self.prioridad) &
            #     (Programacion.finalizada == False))
            # for p in progs:
            #     print(p)
            ###
            # print(horas_trabajo_maquina)
            horas_laborales = worktime.workhours_until_date(self.fecha_entrega_prevista,
                                                            self.trabajo.maquina.horas_trabajo_diario)
            # print(horas_laborales)
            cumple = horas_trabajo_maquina <= horas_laborales
            # print(cumple)
        else:
            cumple = False
        return cumple

    @property
    def fecha_entrega_calculada(self):
        horas_trabajo_maquina = self.get_horas_trabajo()
        return worktime.finish_datetime(horas_trabajo_maquina, self.trabajo.maquina.horas_trabajo_diario)

    class Meta:
        order_by = ('finalizada', 'trabajo', 'prioridad',)

    def __str__(self):
        return '^{prioridad}^ {orden_fabricacion}: {seccion} -> {maquina}'.format(
            prioridad=self.prioridad,
            orden_fabricacion=self.trabajo.orden_fabricacion,
            seccion=self.trabajo.maquina.seccion.codigo,
            maquina=self.trabajo.maquina.codigo)

    def get_horas_trabajo(self):
        return Programacion.select(fn.Sum(Trabajo.horas_realizacion)).join(Trabajo).where(
            (Trabajo.maquina == self.trabajo.maquina) &
            (Programacion.prioridad <= self.prioridad) &
            (Programacion.finalizada == False)).scalar()
