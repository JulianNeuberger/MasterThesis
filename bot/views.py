from django.http import HttpResponse

from bot.bot import QueryableModel


def training_view(request):
    QueryableModel().train()
    return HttpResponse('model trained')
