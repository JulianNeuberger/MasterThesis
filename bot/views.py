from django.http import HttpResponse

from bot.model import QueryableModel
from bot.training import train_new_imagination_model
from turns.util import update_all_for_single_sentence


def training_view(request):
    model = train_new_imagination_model()
    return HttpResponse('model trained')


def query_bot_end_point(request):
    sentence = request.GET.get('sentence')
    sentence = update_all_for_single_sentence(sentence)
    QueryableModel().query()
