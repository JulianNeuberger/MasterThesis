from django.apps import AppConfig

from events.listener import SlackEventManager


class DataConfig(AppConfig):
    name = 'data'

    def ready(self):
        super().ready()
        from data.logger import Logger
        SlackEventManager().register_listener(Logger())
