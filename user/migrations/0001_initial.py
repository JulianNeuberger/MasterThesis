# Generated by Django 2.0.2 on 2018-05-14 09:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('age', models.IntegerField()),
                ('occupation', models.CharField(choices=[('NS', 'natural sciences'), ('HS', 'health sciences'), ('CS', 'computer sciences'), ('LA', 'law'), ('EC', 'economics')], max_length=1)),
                ('gender', models.CharField(choices=[('M', 'male'), ('F', 'female'), ('O', 'other')], max_length=1)),
                ('user', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
