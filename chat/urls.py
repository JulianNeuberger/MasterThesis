from django.conf.urls import url, include
from rest_framework import routers

from chat import views

router = routers.DefaultRouter()
router.register(r'messages', views.MessageViewSet, 'Message')
router.register(r'chats', views.ChatViewSet)
router.register(r'user-detail', views.UserViewSet)

urlpatterns = [
    url(r'^$', views.index),
    url(r'^single/(?P<chat_id>[0-9]+)/$', views.single_chat, name='single'),

    url(r'^settings/tutorial$', views.show_tutorial),

    url(r'^api/', include(router.urls)),
]
