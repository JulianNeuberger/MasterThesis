# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-01-09 12:40
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('turns', '0005_auto_20180108_1051'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='intent',
            name='value',
        ),
        migrations.RemoveField(
            model_name='slottemplate',
            name='is_list',
        ),
        migrations.RemoveField(
            model_name='slottemplate',
            name='value',
        ),
    ]
