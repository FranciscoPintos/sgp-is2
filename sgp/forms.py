"""
Los formularios son un método de intercambio de información entre la aplicación
y el usuario. Cada formulario corresponde a un modelo, por lo que un formulario
en blanco permite instanciarlo mientras que uno ya ligado a una instancia
permite modificarla.

Para todos los formularios, los argumentos de los constructores son los mismos
que para su clase base.
"""

import datetime

from django import forms
from django.forms import ModelForm
from django.utils import timezone
from guardian.shortcuts import assign_perm, remove_perm, get_perms_for_model

from .models import User, Proyecto, Role, Sprint, UserStory


class UserForm(ModelForm):
    """
    Corresponde al modelo User. Se muestra un formulario por cada usuario
    dentro de la página de administración, donde se pueden modificar
    propiedades o permisos.

    Posee campos correspondientes a los atributos de nombre, apellido, y correo
    electrónico. Además, posee tres campos adicionales para los permisos de
    creación de proyecto, administración de usuarios, y auditación del sistema.

    **Fecha:** 24/08/21

    **Artefacto:** módulo de seguridad

    |
    """
    email = forms.CharField(disabled=True)
    crear_proyecto = forms.BooleanField(required=False)
    administrar = forms.BooleanField(required=False)
    auditar = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for permiso in self.Meta.fields:
            self.fields[permiso].initial = self.instance.has_perm('sgp.' + permiso)

    def save(self, commit=True):
        for permiso in ['crear_proyecto', 'administrar', 'auditar']:
            if self.cleaned_data[permiso]:
                assign_perm('sgp.' + permiso, self.instance)
            else:
                remove_perm('sgp.' + permiso, self.instance)
        super(UserForm, self).save(commit)

    class Meta:
        model = User
        fields = ['nombre', 'apellido', 'email', 'crear_proyecto', 'administrar', 'auditar']


class ProyectoForm(ModelForm):
    """
    Corresponde al modelo Proyecto. Este formulario se muestra en las páginas
    de creación y de edición de proyectos.

    Posee campos correspondientes a los atributos de nombre, descripción, fecha
    de inicio, fecha de fin, y duración predeterminada de los sprints.

    **Fecha:** 06/09/21

    **Artefacto:** módulo de proyecto
    """
    fecha_inicio = forms.DateField(label="Fecha de inicio",
                                   error_messages={'invalid': 'La fecha debe estar en formato dd/mm/aaaa.'})
    fecha_fin = forms.DateField(label="Fecha de fin",
                                error_messages={'invalid': 'La fecha debe estar en formato dd/mm/aaaa.'})
    duracion_sprint = forms.IntegerField(label="Duración de los sprints (en días)", min_value=0)

    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            if self.instance.estado == Proyecto.Estado.INICIADO:
                self.fields['fecha_inicio'].initial = self.instance.fecha_inicio
                self.fields['fecha_inicio'].disabled = True

    def clean(self):
        """
        Valida las fechas y la duración predeterminada del sprint.

        Para que el formulario sea válido, las fechas no pueden haber ocurrido
        en el pasado y la duración del sprint debe ser positiva. Además, debe
        haber suficiente tiempo entre la fecha de inicio la fecha de fin para
        realizar al menos un sprint.

        |
        """
        cleaned_data = super(ModelForm, self).clean()

        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')
        duracion_sprint = cleaned_data.get('duracion_sprint')

        if fecha_inicio and fecha_inicio < timezone.localdate():
            self.add_error('fecha_inicio', 'La fecha de inicio no puede ser en el pasado.')
            fecha_inicio = None
        if fecha_fin and fecha_fin < timezone.localdate():
            self.add_error('fecha_fin', 'La fecha de fin no puede ser en el pasado.')
            fecha_fin = None
        if fecha_inicio and fecha_fin and fecha_inicio > fecha_fin:
            self.add_error('fecha_fin', 'La fecha de fin debe ser después de la fecha de inicio.')
            fecha_inicio = None
            fecha_fin = None
        if fecha_inicio and fecha_fin and duracion_sprint and \
                fecha_inicio+datetime.timedelta(days=duracion_sprint) > fecha_fin:
            self.add_error('duracion_sprint', 'El proyecto debe tener tiempo para al menos un sprint.')

        return cleaned_data

    class Meta:
        model = Proyecto
        fields = ('nombre', 'descripcion', 'fecha_inicio', 'fecha_fin', 'duracion_sprint')


class RoleForm(ModelForm):
    """
    Corresponde al modelo Role. Se muestra un formulario por cada rol dentro
    de la página de administración de roles, donde se pueden crear nuevos
    roles, modificar sus permisos, o eliminarlos.

    Posee un campo correspondiente al nombre. Además, posee un campo adicional
    para cada permiso posible dentro de un proyecto. Estos son cuatro:
    administración de equipo, gestión de proyecto, modificación de la pila de
    producto, y desarrollo.

    Posee un parámetro para el rol actual del usuario. Este rol no podrá ser
    eliminado ni se le podrá revocar el permiso de administración de equipo,
    para evitar una situación en la que no se pueda modificar la configuración
    del proyecto.

    **Fecha:** 02/09/21

    **Artefacto:** módulo de proyecto

    :param rol_actual: El rol actual del usuario.
    :type rol_actual: Role

    |
    """
    administrar_equipo = forms.BooleanField(required=False)
    gestionar_proyecto = forms.BooleanField(required=False)
    pila_producto = forms.BooleanField(required=False)
    desarrollo = forms.BooleanField(required=False)

    def __init__(self, *args, rol_actual, **kwargs):
        super(RoleForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            permisos = get_perms_for_model(Proyecto).exclude(codename='vista')
            for perm in permisos:
                self.fields[perm.codename].initial = self.instance.permisos.filter(id=perm.id).exists()
            self.rol_actual = rol_actual
            if self.instance == rol_actual:
                self.fields['administrar_equipo'].disabled = True

    def save(self, commit=True):
        permisos = get_perms_for_model(Proyecto).exclude(codename='vista')
        if self.instance.pk:
            print(self.instance, '==', self.rol_actual)
            if self.instance == self.rol_actual:
                self.cleaned_data['administrar_equipo'] = True
            for perm in permisos:
                if self.cleaned_data[perm.codename]:
                    self.instance.asignar_permiso(perm)
                else:
                    self.instance.quitar_permiso(perm)
            super(RoleForm, self).save(commit)
        else:
            super(RoleForm, self).save(commit)
            for perm in permisos:
                if self.cleaned_data[perm.codename]:
                    self.instance.permisos.add(perm)

    class Meta:
        model = Role
        fields = ['nombre', 'administrar_equipo', 'gestionar_proyecto', 'pila_producto', 'desarrollo']


class UserRoleForm(ModelForm):
    """
    Corresponde al modelo User. Se muestra un formulario por cada usuario
    dentro de la página de administrar equipo, donde muestra la información
    principal y se puede asignar un rol a cada usuario.

    Posee campos desactivados correspondientes a los atributos de nombre,
    apellido, y correo electrónico. Además, posee un campo activado para
    seleccionar el rol del usuario.

    Posee un parámetro para el usuario actual. Este usuario no se podrá asignar
    un rol sin el permiso de administración de equipo para evitar una situación
    donde no pueda acceder a la vista de administración de equipo.

    **Fecha:** 18/09/21

    **Artefacto:** módulo de proyecto

    :param proyecto_actual: El proyecto cuyos roles se muestran.
    :param usuario_actual: El usuario accediendo a la vista.
    :type proyecto_actual: Proyecto
    :type usuario_actual: User
    """

    borrar = forms.BooleanField(required=False)

    def __init__(self, *args, usuario_actual, proyecto_actual, **kwargs):
        super(UserRoleForm, self).__init__(*args, **kwargs)

        if self.instance == usuario_actual:
            perm = get_perms_for_model(Proyecto).get(codename='administrar_equipo')
            queryset = Role.objects.filter(proyecto=proyecto_actual, permisos__in=[perm])
        else:
            queryset = Role.objects.filter(proyecto=proyecto_actual)

        self.fields['rol'] = forms.ModelChoiceField(
            queryset=queryset,
            initial=self.instance.participa_set.get(proyecto=proyecto_actual).rol
        )
        self.fields['nombre'].disabled = True
        self.fields['apellido'].disabled = True
        self.fields['email'].disabled = True

        self.usuario_actual = usuario_actual
        self.proyecto_actual = proyecto_actual

    def clean(self):
        """
        Además de validar los datos, se asegura de que al marcar un formulario
        para borrarlo, esto quite al usuario del equipo en vez de eliminarlo.

        |
        """
        cleaned_data = super(ModelForm, self).clean()
        if cleaned_data.get('borrar'):
            self.proyecto_actual.quitar_rol(self.instance)
        return cleaned_data

    def save(self, commit=True):
        if self.cleaned_data.get('rol'):
            self.proyecto_actual.asignar_rol(self.instance, self.cleaned_data['rol'].nombre)
        super(UserRoleForm, self).save(commit)

    class Meta:
        model = User
        fields = ['nombre', 'apellido', 'email', 'borrar']


class AgregarMiembroForm(forms.Form):
    """
    Permite seleccionar un usuario que no forma parte del equipo del proyecto y
    un rol existente dentro del proyecto. Agrega al usuario al equipo con ese
    rol.

    **Fecha:** 18/09/21

    **Artefacto:** módulo de proyecto

    :param proyecto_id: El proyecto al que se le agrega un usuario.
    :type proyecto_id: Proyecto

    |
    """

    def __init__(self, *args, proyecto_id, **kwargs):
        self.proyecto = proyecto_id
        super().__init__(*args, **kwargs)
        self.fields['usuarios'] = \
            forms.ModelChoiceField(queryset=User.objects.exclude(participa__proyecto=proyecto_id)
                                   .exclude(pk='AnonymousUser'))
        self.fields['roles'] = \
            forms.ModelChoiceField(queryset=Role.objects.filter(proyecto=proyecto_id))

    def save(self):
        self.proyecto.asignar_rol(self.cleaned_data['usuarios'], self.cleaned_data['roles'].nombre)


class UploadFileForm(forms.Form):
    """
    Permite enviar archivos al servidor.

    **Fecha:** 07/09/21

    |
    """
    archivo = forms.FileField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class UserStoryForm(ModelForm):
    """
    """
    horas_estimadas = forms.IntegerField(label="Costo estimado del user story (en horas)", min_value=0)

    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)

    class Meta:
        model = UserStory
        fields = ('nombre', 'descripcion', 'horas_estimadas')


class SprintForm(ModelForm):
    """
    """
    fecha_inicio = forms.DateField(label="Fecha de inicio",
                                   error_messages={'invalid': 'La fecha debe estar en formato dd/mm/aaaa.'})
    fecha_fin = forms.DateField(label="Fecha de fin",
                                error_messages={'invalid': 'La fecha debe estar en formato dd/mm/aaaa.'})

    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)

    def clean(self):
        """
        """
        cleaned_data = super(ModelForm, self).clean()

        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')

        if fecha_inicio and fecha_inicio < timezone.localdate():
            self.add_error('fecha_inicio', 'La fecha de inicio no puede ser en el pasado.')
            fecha_inicio = None
        if fecha_fin and fecha_fin < timezone.localdate():
            self.add_error('fecha_fin', 'La fecha de fin no puede ser en el pasado.')
            fecha_fin = None
        if fecha_inicio and fecha_fin and fecha_inicio > fecha_fin:
            self.add_error('fecha_fin', 'La fecha de fin debe ser después de la fecha de inicio.')

        return cleaned_data

    class Meta:
        model = Sprint
        fields = ('nombre', 'descripcion', 'fecha_inicio', 'fecha_fin')
