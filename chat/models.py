from django.contrib.auth.models import User
from django.db import models


class Chat(models.Model):
    initiator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')


class Message(models.Model):
    sent_on = models.DateTimeField(auto_now_add=True)
    value = models.CharField(max_length=512)

    sent_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')
    sent_in = models.ForeignKey(Chat, on_delete=models.CASCADE)
