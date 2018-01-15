from django.conf.urls import url

from events.views import SlackEventEndpoints

urlpatterns = [url(r'^$', SlackEventEndpoints.as_view())]
