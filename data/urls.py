from django.conf.urls import url

from data import views

urlpatterns = [
    url(r'process', name='data_processing', view=views.pre_process_data_view)
]
