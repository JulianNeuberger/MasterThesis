from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)

    GENDER_CHOICES = (
        ('M', 'male'),
        ('F', 'female'),
        ('O', 'other')
    )

    OCCUPATION_CHOICES = (
        ('NS', 'natural sciences'),
        ('HS', 'health sciences'),
        ('CS', 'computer sciences'),
        ('LA', 'law'),
        ('EC', 'economics'),
    )

    age = models.IntegerField()
    occupation = models.CharField(max_length=2, choices=OCCUPATION_CHOICES)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
