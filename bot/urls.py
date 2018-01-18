from django.conf.urls import url

from bot import views

urlpatterns = [
    url(r'^train/imagination/', name='train_bot', view=views.training_view),
    url(r'^train/actions/', name='train_actions', view=views.training_action_view),
]
