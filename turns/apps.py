from django.apps import AppConfig


class TurnsConfig(AppConfig):
    name = 'turns'

    def ready(self):
        from chat.events import ListenerManager
        from turns.listener import ChatMessageListener
        super().ready()
        ListenerManager().add_listener(ChatMessageListener())
