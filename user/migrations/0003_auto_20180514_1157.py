# Generated by Django 2.0.2 on 2018-05-14 09:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_auto_20180514_1156'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='gender',
            field=models.CharField(choices=[('M', 'male'), ('F', 'female'), ('O', 'other')], max_length=1),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='occupation',
            field=models.CharField(choices=[('NS', 'natural sciences'), ('HS', 'health sciences'), ('CS', 'computer sciences'), ('LA', 'law'), ('EC', 'economics')], max_length=2),
        ),
    ]
