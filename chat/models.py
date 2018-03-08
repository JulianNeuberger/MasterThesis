from django.contrib.auth.models import User
from django.db import models


class Chat(models.Model):
    initiator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')
    name = models.CharField(max_length=64, null=True)


class Message(models.Model):
    sent_on = models.DateTimeField(auto_now_add=True)
    value = models.CharField(max_length=512)

    sent_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')
    sent_in = models.ForeignKey(Chat, on_delete=models.CASCADE)

    reward = models.DecimalField(max_digits=10, decimal_places=9, default=.6)


class Settings(models.Model):
    visits = models.IntegerField(default=0)
    show_tutorial = models.BooleanField(default=True)

    for_user = models.OneToOneField(User, on_delete=models.CASCADE)
