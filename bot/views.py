from django.contrib.auth.models import User
from django.core.exceptions import SuspiciousOperation
from django.http import JsonResponse

from bot.bot import QueryableModelInterface, DeepMindModel
from bot.listener import BotListener

bot_user = User.objects.get(username='Chatbot')
bot_listener = BotListener(bot_user)


def training_view(request):
    success = bot_listener.model.pre_train()
    response = {
        'success': success,
        'errors': []
    }
    return JsonResponse(response)


def save_model(request):
    success = bot_listener.model.save_weights()
    response = {
        'success': success,
        'errors': []
    }
    return JsonResponse(response)


def list_models(request):
    models = QueryableModelInterface.list_available_models()
    response = {
        'models': models
    }
    return JsonResponse(response)


def change_model(request):
    try:
        model_name = request.POST['name']
    except KeyError:
        raise SuspiciousOperation("Change model view needs a name POST parameter (the model name), to change the model")
    bot_listener.model = QueryableModelInterface()
