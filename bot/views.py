from django.core.exceptions import SuspiciousOperation
from django.http import JsonResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.views.decorators.http import require_http_methods

from bot.bot import AbstractBot
from bot.listener import BotListener


def start_bot(request):
    return JsonResponse({
        'success': True,
        'errors': []
    })


def training_view(request):
    success = BotListener().bot.pre_train()
    response = {
        'success': success,
        'errors': []
    }
    return JsonResponse(response)


def save_model(request):
    success = BotListener().bot.save_weights()
    response = {
        'success': success,
        'errors': []
    }
    return JsonResponse(response)


@require_http_methods(['GET'])
def list_models(request):
    models = AbstractBot.list_available_models()
    if request.GET.get('json', default=False):
        response = {
            'models': models
        }
        return JsonResponse(response)
    else:
        context = {
            'models': models
        }
        return TemplateResponse(context=context, request=request, template='bot/list-available.html')


@require_http_methods(['POST'])
def change_model(request):
    try:
        model_name = request.POST['name']
    except KeyError:
        raise SuspiciousOperation('Change model view needs a name POST parameter (the model name), to change the model')
    BotListener().change_bot(model_name)
    return redirect('list_models')
