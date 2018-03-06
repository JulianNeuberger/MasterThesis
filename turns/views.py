import logging

from django.http import HttpResponse, HttpRequest, HttpResponseBadRequest
from django.template.response import TemplateResponse

from dialogflow import Intents
from turns.models import Sentence, Dialogue
from turns.services import persist_intent_templates
from turns.util import update_sentiment_for_all_sentences, update_intents_for_all_sentences, \
    update_user_profile_for_all_dialogues, update_reward_for_all_sentences, \
    update_all_for_single_sentence, update_terminals_for_all_dialogues

logger = logging.getLogger('turns')


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


def update_rewards(request):
    update_reward_for_all_sentences(override=True)
    return HttpResponse('Updated all rewards')


def update_terminals(request):
    update_terminals_for_all_dialogues(override=True)
    return HttpResponse('Updated terminal states for all sentences')


def load_intents_from_dialogflow(request, access_token):
    logger.info('Loading intents from dialogflow.')
    intents = Intents.get_all(access_token)
    num_intents = len(intents)
    intents_created, parameters_created = persist_intent_templates(intents)
    return HttpResponse(
        'Successfully synchronized {} intents with dialogflow. '
        'Created {} new intents with a total of {} new parameters'.format(
            num_intents,
            intents_created,
            parameters_created
        ))


def direct_test(request: HttpRequest):
    if request.method == 'POST':
        sentence = Sentence()
        # FIXME: save test sentences?
        dialogue = Dialogue.objects.first()
        sentence.said_in = dialogue
        sentence.value = request.POST.get(key='message', default='')
        update_all_for_single_sentence(sentence, False)
        context = {
            'sentence': sentence
        }
        return TemplateResponse(request=request, template='turns/breakdown.html', context=context)
    elif request.method == 'GET':
        return TemplateResponse(request=request, template='turns/breakdown.html', context={})
    else:
        return HttpResponseBadRequest(reason='Only GET and POST allowed.')
