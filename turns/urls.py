from django.conf.urls import url

from turns import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^update/sentiments', name='update_sentiments', view=views.update_sentiments),
    url(r'^update/intents', name='update_intents', view=views.update_intents),
    url(r'^update/profiles', name='update_profiles', view=views.update_user_profiles),
    url(r'^update/rewards', name='update_rewards', view=views.update_rewards),
    url(r'^update/terminals', name='update_terminals', view=views.update_terminals),
    url(r'^intents/load-from/dialogflow/(?P<access_token>[0-9a-f]+)$',
        views.load_intents_from_dialogflow,
        name='load_intents_dialogflow'),
    url(r'^test/', name='test_data_crawler', view=views.direct_test),
    url(r'^fake/', name='fake_conversations', view=views.fake_conversations)
]
