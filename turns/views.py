from django.http import HttpResponse

from dialogflow import Intents
from turns.services import persist_intent_templates
from turns.util import update_sentiment_for_all_sentences, update_intents_for_all_sentences, \
    update_user_profile_for_all_dialogues


def index(request):
    return HttpResponse('Index')


def update_sentiments(request):
    update_sentiment_for_all_sentences(override=False)
    return HttpResponse('Updated all sentiments')


def update_intents(request):
    update_intents_for_all_sentences(override=True)
    return HttpResponse('Updated all intents')


def update_user_profiles(request):
    update_user_profile_for_all_dialogues(override=True)
    return HttpResponse('Updated all user profiles')


def load_intents_from_dialogflow(request, access_token):
    print(access_token)
    intents = Intents.get_all(access_token)
    persist_intent_templates(intents)
    return HttpResponse('Successfully synchronized all intents in database with dialogflow')
