# Generated by Django 3.2.6 on 2021-09-26 15:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sgp', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='proyecto',
            options={'default_permissions': (), 'permissions': [('administrar_equipo', 'administración de equipo'), ('gestionar_proyecto', 'gestión de proyecto'), ('pila_producto', 'gestión de pila de producto'), ('desarrollo', 'desarrollo'), ('vista', 'acceso al proyecto')]},
        ),
        migrations.CreateModel(
            name='UserStory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=200)),
                ('descripcion', models.TextField(blank=True, default='')),
                ('estado', models.CharField(choices=[('P', 'Pendiente'), ('I', 'Iniciado'), ('F', 'Finalizado')], default='P', max_length=50)),
                ('horas_estimadas', models.IntegerField()),
                ('horas_trabajadas', models.IntegerField(blank=True, default=0)),
                ('proyecto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_backlog', to='sgp.proyecto')),
            ],
        ),
        migrations.CreateModel(
            name='Sprint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=200)),
                ('descripcion', models.TextField(blank=True, default='')),
                ('fecha_inicio', models.DateField(verbose_name='Fecha de inicio')),
                ('fecha_fin', models.DateField(verbose_name='Fecha de fin')),
                ('estado', models.CharField(choices=[('P', 'Pendiente'), ('I', 'Iniciado'), ('F', 'Finalizado')], default='P', max_length=50)),
                ('equipo', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
                ('proyecto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sgp.proyecto')),
            ],
        ),
        migrations.CreateModel(
            name='Comentario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('texto', models.TextField()),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('autor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('user_story', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sgp.userstory')),
            ],
        ),
    ]
