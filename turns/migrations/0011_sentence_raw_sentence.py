# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-02-02 13:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0004_auto_20180202_1429'),
        ('turns', '0010_sentence_terminal'),
    ]

    operations = [
        migrations.AddField(
            model_name='sentence',
            name='raw_sentence',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='chat.Message'),
        ),
    ]
