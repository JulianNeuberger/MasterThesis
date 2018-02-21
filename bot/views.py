from django.http import HttpResponse, JsonResponse

from bot.bot import DeepMindModel

model = DeepMindModel.instance


def training_view(request):
    model.train()
    return HttpResponse('model trained')


def save_model(request):
    model.save_weights()
    return HttpResponse('saved weights')


def bot_status(request):
    return JsonResponse({
        'training': model.is_training(),
    })
