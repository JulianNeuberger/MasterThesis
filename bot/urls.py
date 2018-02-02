from django.conf.urls import url

from bot import views

urlpatterns = [
    url(r'^train/imagination/', name='train_bot', view=views.training_view),
]
