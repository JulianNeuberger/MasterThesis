# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-02-28 13:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('turns', '0017_auto_20180228_1437'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='parametertemplate',
            name='intent_template',
        ),
        migrations.AddField(
            model_name='intenttemplate',
            name='parameters',
            field=models.ManyToManyField(to='turns.ParameterTemplate'),
        ),
    ]
