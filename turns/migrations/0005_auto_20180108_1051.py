# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-01-08 09:51
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('turns', '0004_auto_20180108_1041'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sentence',
            name='topic',
        ),
        migrations.DeleteModel(
            name='Topic',
        ),
    ]