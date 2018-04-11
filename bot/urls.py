from django.conf.urls import url

from bot import views

urlpatterns = [
    url(r'^train/', name='train_bot', view=views.training_view),
    url(r'^save/', name='save_bot', view=views.save_model),
    url(r'^load/', name='load_bot', view=views.change_model),
    url(r'^start/', name='start_bot', view=views.start_bot),
    url(r'^list/models', name='list_models', view=views.list_models),
]
