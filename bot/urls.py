from django.conf.urls import url

from bot import views

urlpatterns = [
    url(r'^train/', name='train_bot', view=views.training_view),
    url(r'^save/', name='save_bot', view=views.save_model),
    url(r'^status/', name='bot_status', view=views.bot_status),
]
