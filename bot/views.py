from django.http import HttpResponse

from bot.training import train_new_imagination_model, train_new_action_model


def training_view(request):
    model = train_new_imagination_model()
    return HttpResponse('model trained')


def training_action_view(request):
    model = train_new_action_model()
    return HttpResponse('action model trained')
