# Generated by Django 3.2.6 on 2021-10-25 14:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sgp', '0004_incremento'),
    ]

    operations = [
        migrations.AddField(
            model_name='incremento',
            name='usuario',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]
