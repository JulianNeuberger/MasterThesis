from django.http import HttpResponse

from bot.bot import QueryableModel
from bot.training import train_new_imagination_model


def training_view(request):
    QueryableModel().train()
    return HttpResponse('model trained')
