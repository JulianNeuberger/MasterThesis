from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from events.listener import SlackEventManager, SlackMessageEvent

SLACK_VERIFICATION_TOKEN = getattr(settings, 'SLACK_VERIFICATION_TOKEN', None)
SLACK_BOT_USER_TOKEN = getattr(settings, 'SLACK_BOT_USER_TOKEN', None)


class SlackEventEndpoints(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.event_manager = SlackEventManager()

    def post(self, request):
        slack_message = request.data

        if slack_message.get('token') != SLACK_VERIFICATION_TOKEN:
            return Response(status=status.HTTP_403_FORBIDDEN)

        if slack_message.get('type') == 'url_verification':
            return Response(data=slack_message,
                            status=status.HTTP_200_OK)
        if 'event' in slack_message:
            event_message = slack_message.get('event')

            if event_message.get('subtype') == 'bot_message':
                return Response(status=status.HTTP_200_OK)

            user = event_message.get('user')
            text = event_message.get('text')
            channel = event_message.get('channel')
            if text is not None:
                # don't handle pure image/location/gif/audio/video messages
                self.event_manager.notify_listeners(SlackMessageEvent(user_name=user, channel=channel, message=text))
        return Response(status=status.HTTP_200_OK)
