# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-02-28 11:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('turns', '0015_auto_20180228_1232'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parametertemplate',
            name='is_list',
            field=models.BooleanField(default=False),
        ),
    ]
