from django.contrib.auth.models import User
from django.db import models


class Settings(models.Model):
    chat_bot_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')
    """
    Set this, to answer questions manually, not by chat bot.
    """
    manual_override = models.BooleanField(default=False)
    added_on = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def get_latest():
        try:
            return Settings.objects.order_by('-added_on')[0]
        except models.ObjectDoesNotExist:
            return None

    @staticmethod
    def get_latest_or_create():
        return Settings.get_latest() or Settings.objects.create()
