import ast
import logging
import re
from typing import Any, Callable

from bs4 import BeautifulSoup
from requests import post

import dialogflow
from bot.config import SECONDS_FOR_TERMINAL, SECONDS_PER_DAY
from turns.models import Sentence, Parameter, Intent, IntentTemplate, Dialogue, UserProfile, Player, Team, \
    ParameterTemplate

logger = logging.getLogger('turns')


def update_sentiment_for_all_sentences(override=False, query_set=None):
    _update_sentence_generic(update_sentiment_for_single_sentence, 'sentiment', override, query_set)


def update_intents_for_all_sentences(override=False, query_set=None):
    _update_sentence_generic(update_intent_for_single_sentence, 'intent', override, query_set)


def update_reward_for_all_sentences(override=False, query_set=None):
    _update_sentence_generic(update_reward_for_single_sentence, 'reward', override, query_set)


def _update_sentence_generic(update_method: Callable[[Sentence, bool], Any],
                             field_name,
                             override=False,
                             query_set=None):
    """
    Updates the sentences' "field_name" in the given queryset with the given update method.
    Counts the number of sentences touched/skipped and logs these numbers.

    :param update_method: a callable that takes a sentence and a bool and returns the updated object
    :param field_name: name of field to update
    :param query_set: which sentences are considered? defaults to all
    :param override: override existing values?
    :return: Nothing
    """
    touched = 0
    skipped = 0
    query_set = query_set if query_set is not None else Sentence.objects.all()
    for sentence in query_set:
        if override or sentence.sentiment is None:
            new_val = update_method(sentence, override)
            logger.debug("New {} for sentence '{}' is {}".format(field_name,
                                                                 sentence.value,
                                                                 new_val))
            touched += 1
        else:
            skipped += 1
            logger.debug("Skipping sentence '{}'".format(sentence))
    logger.info(
        "Touched {} and skipped {} sentences while updating {}s for them.".format(touched,
                                                                                  skipped,
                                                                                  field_name))


def update_sentiment_for_single_sentence(sentence, override=False, save=True):
    if sentence.sentiment is None or override:
        sentiment = crawl_single_sentiment(sentence.value)
        sentence.sentiment = sentiment
        if save:
            sentence.save()
    return sentence.sentiment


def crawl_single_sentiment(text):
    response = post('http://text-processing.com/demo/sentiment/',
                    data={
                        'language': 'english',
                        'text': text
                    })
    parsed = BeautifulSoup(response.text, 'lxml')
    polarity = parsed.find_all('h5')
    if len(polarity) == 1:
        # neutral
        return 0
    else:
        parsed = polarity[1]
        parsed = parsed.find_next('ul')
        positive = str(parsed.find('li', attrs={'class': 'positive'}).contents[0])
        positive = re.findall('\d+\.\d+', positive)[0]
        negative = str(parsed.find('li', attrs={'class': 'negative'}).contents[0])
        negative = re.findall('\d+\.\d+', negative)[0]
        sentiment = float(positive) - float(negative)
        return sentiment


ACCESS_TOKEN = '91f867c85e574b7cb1021d21b9319c55'


def update_intent_for_single_sentence(sentence: Sentence, override=False, save=True):
    if sentence.intent is None or override:
        response = dialogflow.Query.from_text(sentence.value, ACCESS_TOKEN, lang='en', session_id=sentence.said_in_id)
        result = response['result']
        try:
            meta_data = result['metadata']
            intent_id = meta_data['intentId']
            logger.debug('Successfully read intent id from response.')
            intent_template = IntentTemplate.objects.get(dialog_flow_id=intent_id)
            intent = Intent.objects.create(template=intent_template)
            sentence.intent = intent
            parameters = result['parameters']
            logger.debug('Successfully read parameters from response.')
            expected_parameters = intent_template.parameters.all()
            for parameter_template in expected_parameters:
                try:
                    parameter_value = parameters[parameter_template.name]
                    parameter_value = _sanitize_parameter_value(parameter_value, parameter_template)
                    if parameter_value is not None:
                        Parameter.objects.create(template=parameter_template, intent=intent, value=parameter_value)
                    else:
                        raise KeyError()
                except KeyError:
                    logger.info(
                        'Expected intent "{}" to have parameter "{}", but found none in sentence "{}".'.format(
                            intent_template.name,
                            parameter_template.name,
                            sentence.value
                        ))
        except KeyError:
            logger.debug('Failed to read response, no intent available.')
            sentence.intent = None
        if save:
            sentence.save()
    return sentence.intent.template.name if sentence.intent is not None else 'commons.unknown'


def update_user_profile_for_single_dialogue(dialogue: Dialogue, override=False, save=True):
    last_profile = None
    for sentence in dialogue.sentence_set.order_by('said_on').all():
        if sentence.user_profile is None or override:
            if last_profile is None:
                last_profile = UserProfile.objects.create()
                logger.debug("No user profile is existent for dialogue {}, created one".format(sentence.said_in))
            sentence.user_profile = get_user_profile_for_sentence(sentence, last_profile)
            if save:
                sentence.save()

        last_profile = sentence.user_profile


def update_user_profile_for_all_dialogues(override=False, save=True):
    for dialogue in Dialogue.objects.all():
        update_user_profile_for_single_dialogue(dialogue, override, save)


def get_user_profile_for_sentence(sentence: Sentence, previous: UserProfile, save=True):
    intent = sentence.intent
    assert previous is not None
    if intent is not None:
        if intent.template.name.startswith('userprofile.response'):
            updated_profile = duplicate_user_profile_no_save(previous)
            dispatch_profile_changing_intent(updated_profile, intent)
            logger.debug('User profile updated after seeing sentence "{}" ({}) to {}'
                         .format(sentence,
                                 sentence.intent.template.name,
                                 updated_profile))
            if save:
                updated_profile.save()
            return updated_profile
    return previous


def dispatch_profile_changing_intent(user_profile: UserProfile, intent: Intent):
    # FIXME: defaults to doing nothing in case of intent not being listed, is this smart?
    {
        'userprofile.response.inactive': set_user_profile_active_player,
        'userprofile.response.active': set_user_profile_active_player,
        'userprofile.response.name': update_user_profile_name,
        'userprofile.response.favorite_player': update_user_profile_favorite_player,
        'userprofile.response.no_favorite_player': update_user_profile_favorite_player,
        'userprofile.response.favorite_team': update_user_profile_favorite_team,
        'userprofile.response.no_favorite_team': update_user_profile_favorite_team,
        'userprofile.response.age': update_user_profile_age
    }.get(intent.template.name, lambda *args: None)(user_profile, intent)


def set_user_profile_active_player(user_profile: UserProfile, intent: Intent):
    user_profile.is_active_player = intent.template.name == 'userprofile.response.active'


def update_user_profile_age(user_profile: UserProfile, intent: Intent):
    user_profile.age = get_object_from_intent('age', 'userprofile.response.age', get_age_from_slot, intent)


def get_age_from_slot(slot: Parameter):
    return int(ast.literal_eval(slot.value)['amount'])


def update_user_profile_name(user_profile: UserProfile, intent: Intent):
    user_profile.name = get_user_name_from_intent(intent)


def update_user_profile_favorite_team(user_profile: UserProfile, intent: Intent):
    if intent.template.name == 'userprofile.response.favorite_team':
        user_profile.has_favourite_team = True
        user_profile.favourite_team = get_team_from_intent(intent)
    else:
        user_profile.has_favourite_team = False


def update_user_profile_favorite_player(user_profile: UserProfile, intent: Intent):
    if intent.template.name == 'userprofile.response.favorite_player':
        user_profile.has_favourite_player = True
        user_profile.favourite_player = get_player_from_intent(intent)
    else:
        user_profile.has_favourite_player = False


def get_team_from_intent(intent: Intent):
    return get_object_from_intent('team', 'userprofile.response.favorite_team',
                                  lambda slot: Team.objects.get(name=slot.value), intent)


def get_player_from_intent(intent: Intent):
    return get_object_from_intent('player', 'userprofile.response.favorite_player',
                                  lambda slot: Player.objects.get(name=slot.value), intent)


def get_object_from_intent(slot_name: str, intent_name: str, retrieval_method, intent: Intent):
    assert intent.template.name == intent_name
    obj = None
    for slot in intent.parameter_set.all():
        logger.debug('Searching for "{}", considering "{}"'.format(slot_name, slot.template.name))
        if slot.template.name == slot_name:
            logger.debug(
                'Found slot "{}" in intent "{}", retrieving object from raw "{}"...'.format(slot_name, intent_name,
                                                                                            slot.value))
            obj = retrieval_method(slot)
            logger.debug('Object is {}'.format(obj))
            break
    assert obj is not None
    return obj


def get_user_name_from_intent(intent: Intent):
    return get_object_from_intent('given-name', 'userprofile.response.name', lambda slot: slot.value, intent)


def duplicate_user_profile_no_save(user_profile: UserProfile):
    user_profile.id = None
    return user_profile


def update_reward_for_single_sentence(sentence: Sentence, override=False, save=True):
    if override or sentence.reward is None:
        intent_name = sentence.intent.template.name if sentence.intent is not None else 'common.unknown'
        sentence.reward = reward_for_reaction(intent_name)
        if save:
            sentence.save()
    return sentence.reward


def reward_for_reaction(intent_name):
    return {
        'reaction.content.positive': .5,
        'reaction.content.negative': -.25,
        'common.thanks': .25,
        'reaction.content.not_interested': -.75
    }.get(intent_name, .0)


def update_terminals_for_all_dialogues(override=False, save=True):
    dialogues = Dialogue.objects.all()
    for dialogue in dialogues:
        update_terminals_for_single_dialogue(dialogue, override, save)


def update_terminals_for_single_dialogue(dialogue: Dialogue, override=False, save=True):
    sentences = dialogue.sentence_set.all()
    num_sentences = len(sentences)
    for i, sentence in enumerate(sentences):
        if sentence.intent is not None and sentence.intent.template.name == 'common.bye' and override:
            logger.debug('Considering sentence "{}" to be terminal.'.format(sentence))
            next_i = i + 1
            if next_i < num_sentences:
                next_sentence = sentences[next_i]
                if next_sentence.intent is not None:
                    duration_to_next = next_sentence.said_on - sentence.said_on
                    seconds_between_sentences = duration_to_next.seconds + duration_to_next.days * SECONDS_PER_DAY
                    if seconds_between_sentences > SECONDS_FOR_TERMINAL:
                        logger.debug('Got no other message for {} seconds, sentence is terminal!'.format(
                            seconds_between_sentences
                        ))
                        sentence.terminal = True
                    else:
                        logger.debug('Got message "{}" after {} seconds, so sentence is not terminal!'.format(
                            next_sentence,
                            seconds_between_sentences
                        ))
                        sentence.terminal = False
                    if save:
                        sentence.save()
            else:
                logger.debug('There was no other message in this dialogue, setting "{}" to terminal'.format(sentence))


def update_all_for_single_sentence(sentence: Sentence, save=True):
    update_intent_for_single_sentence(sentence, True, save)
    update_sentiment_for_single_sentence(sentence, True, save)
    return sentence


def _sanitize_parameter_value(parameter_value, parameter_template: ParameterTemplate):
    if not parameter_template.is_list and isinstance(parameter_value, list):
        # simply take the first value
        if len(parameter_value) > 0:
            parameter_value = parameter_value[0]
        else:
            return None
    if isinstance(parameter_value, str) and len(parameter_value) == 0:
        return None
    return parameter_value
