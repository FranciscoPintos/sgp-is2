# Generated by Django 3.2.6 on 2021-09-28 07:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sgp', '0002_auto_20210926_1103'),
    ]

    operations = [
        migrations.AddField(
            model_name='userstory',
            name='numero',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]