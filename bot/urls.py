from django.conf.urls import url

from bot import views

urlpatterns = [
    url(r'^train/imagination/', name='train_bot', view=views.training_view),
    url(r'^query/imagination/', name='test_query', view=views.query_bot_end_point)
]
