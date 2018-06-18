import logging
import time

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpRequest, HttpResponseBadRequest
from django.template.response import TemplateResponse
from django.utils.dateparse import parse_datetime
from django.views.decorators.http import require_http_methods

from dialogflow import Intents
from turns.models import Sentence, Dialogue
from turns.services import persist_intent_templates
from turns.util import update_sentiment_for_all_sentences, update_intents_for_all_sentences, \
    update_user_profile_for_all_dialogues, update_reward_for_all_sentences, \
    update_all_for_single_sentence, update_terminals_for_all_dialogues, update_user_profile_for_single_dialogue

logger = logging.getLogger('turns')


def index(request):
    return TemplateResponse(request=request, context={}, template='turns/index.html')


@login_required
@require_http_methods(['POST', 'GET'])
def fake_conversations(request):
    if request.method == 'POST':
        user_sentence = request.POST.get('user')
        bot_sentence = request.POST.get('bot')
        dialogue = Dialogue.objects.get(with_user=request.user.username)

        user_sentence = Sentence.objects.create(value=user_sentence,
                                                reward=0,
                                                terminal=False,
                                                said_by=request.user.username,
                                                said_in=dialogue)
        time.sleep(1)
        bot_sentence = Sentence.objects.create(value=bot_sentence,
                                               reward=1,
                                               terminal=False,
                                               said_by='Chatbot',
                                               said_in=dialogue)

        update_all_for_single_sentence(user_sentence, override=False, save=True)
        update_all_for_single_sentence(bot_sentence, override=False, save=True)
        update_user_profile_for_single_dialogue(dialogue)

        return TemplateResponse(request=request, template='turns/fake.html')
    else:
        return TemplateResponse(request=request, template='turns/fake.html')


@require_http_methods(['POST'])
def update_sentiments(request):
    override = request.POST.get(key='override', default='')
    override = override.lower() in ('true', '1', 'on')
    update_sentiment_for_all_sentences(override=override)
    return HttpResponse('Updated all sentiments')


@require_http_methods(['POST'])
def update_intents(request):
    override = request.POST.get(key='override', default='')
    last = request.POST.get(key='last', default=False)
    override = override.lower() in ('true', '1', 'on')
    if last:
        query_set = Sentence.objects.all().order_by('-said_on')[:int(last)]
    else:
        query_set = None
    update_intents_for_all_sentences(override=override, query_set=query_set)
    return HttpResponse('Updated all intents')


@require_http_methods(['POST'])
def update_user_profiles(request):
    override = request.POST.get(key='override', default='')
    override = override.lower() in ('true', '1')
    update_user_profile_for_all_dialogues(override=override)
    return HttpResponse('Updated all user profiles')


@require_http_methods(['POST'])
def update_rewards(request):
    update_reward_for_all_sentences(override=True)
    return HttpResponse('Updated all rewards')


@require_http_methods(['POST'])
def update_terminals(request):
    update_terminals_for_all_dialogues(override=True)
    return HttpResponse('Updated terminal states for all sentences')


@require_http_methods(['POST'])
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


def evaluation(request: HttpRequest):
    if request.method == 'POST':
        all_dialogues = Dialogue.objects.all()
        dialogue_ids = [int(id) for id in request.POST.getlist('ids')]
        starts = request.POST.getlist('starts')
        stops = request.POST.getlist('stops')
        result = {}
        for dialogue, start, stop in zip(all_dialogues, starts, stops):
            if dialogue.id in dialogue_ids:
                start = parse_datetime(start)
                stop = parse_datetime(stop)
                sentences = Sentence.objects.exclude(reward=0.6).filter(said_in=dialogue,
                                                                        said_by='Chatbot',
                                                                        said_on__gte=start,
                                                                        said_on__lte=stop)
                if len(sentences) > 0:
                    reward_sum = 0
                    for sentence in sentences:
                        reward_sum += sentence.reward
                    result[dialogue] = reward_sum / len(sentences)
                else:
                    result[dialogue] = float('nan')
        return TemplateResponse(request=request, template='turns/evaluation_result.html', context={'values': result})
    elif request.method == 'GET':
        dialogues = Dialogue.objects.all()
        context = {
            'dialogues': dialogues
        }
        return TemplateResponse(request=request, template='turns/evaluation.html', context=context)
    else:
        return HttpResponseBadRequest(reason='Only GET and POST allowed.')
