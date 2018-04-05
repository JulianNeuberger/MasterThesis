# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-03-01 10:44
from __future__ import unicode_literals

import content.models
from django.db import migrations, models
import django.db.models.deletion
import enumfields.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('turns', '0019_auto_20180301_1139'),
    ]

    operations = [
        migrations.CreateModel(
            name='Content',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=1024)),
                ('type', enumfields.fields.EnumField(enum=content.models.ContentType, max_length=3)),
                ('for_player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='turns.Player')),
            ],
        ),
    ]
