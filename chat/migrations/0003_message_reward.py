# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-01-30 09:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_chat_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='reward',
            field=models.IntegerField(default=6),
        ),
    ]
