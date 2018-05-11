"""

THIS FILE IS DEPRECATED

I ONLY LEFT IT IN FOR REFERENCE

USE THE CONFIGURATION MODULE 'config'

"""


import os

from content.template import Template

print('#####################################################################################')
print('# You are using the deprecated config.py, use the configuration object in database! #')
print('#####################################################################################')

UNKNOWN_INTENT = 'common.unknown'
INTENTS = [
    UNKNOWN_INTENT,
    'common.what',
    'common.bad',
    'common.bye',
    'common.good',
    'common.hi',
    'common.how_are_you',
    'common.im_fine',
    'common.no',
    'common.thanks',
    'common.well_done',
    'common.yes',
    'common.you_are_welcome',
    'common.you_too',
    'commons.more',
    'commons.nice_to_meet_you',
    'commons.no_problem',
    'query.abilities',
    'query.bot',
    'query.list.jerseys',
    'query.list.players',
    'query.player.height',
    'query.player.information.age',
    'query.player.information.goals',
    'query.player.information.shoe',
    'query.player.news',
    'query.player.news.more',
    'reaction.content.known',
    'reaction.content.later',
    'reaction.content.negative',
    'reaction.content.not_interested',
    'reaction.content.positive',
    'reaction.dumb',
    'userprofile.response.active',
    'userprofile.response.age',
    'userprofile.response.fan',
    'userprofile.response.favorite_player',
    'userprofile.response.inactive',
    'userprofile.response.name'
]

NUM_INTENTS = len(INTENTS)
DIDNT_UNDERSTAND_INTENT_ACTION = 'common.what'
ACTIONS = [
    DIDNT_UNDERSTAND_INTENT_ACTION,
    'common.bad',
    'common.bye',
    'common.good',
    'common.have_fun',
    'common.hi',
    'common.how_are_you',
    'common.im_fine',
    'common.no',
    'common.thanks',
    'common.yes',
    'common.you_are_welcome',
    'commons.more',
    'commons.nice_to_meet_you',
    'commons.sorry',
    'common.you_too',
    'offer.player.news',
    'reaction.bad_you_didnt_like',
    'reaction.glad_you_liked_it',
    'response.abilities',
    'response.bot',
    'response.list.jerseys',
    'response.list.players',
    'response.player.information.age',
    'response.player.information.goals',
    'response.player.information.height',
    'response.player.information.shoe',
    'response.player.news',
    'userprofile.query.active',
    'userprofile.query.age',
    'userprofile.query.fan',
    'userprofile.query.name',
]
NUM_ACTIONS = len(ACTIONS)

ACTION_SENTENCES = {
    'common.what': [Template('Sorry, I didn\'t get that'),
                    Template('Uhm, I did not understand that...')],

    'common.bad': [Template('That\'s bad...'),
                   Template('Too bad!')],

    'common.bye': [Template('Bye!'),
                   Template('Good bye!'),
                   Template('See you soon!'),
                   Template('See you around!'),
                   Template('See you later!'),
                   Template('See you!'),
                   Template('Ciao!')],

    'common.good': [Template('That is good!'),
                    Template('Nice!'),
                    Template('Very good'),
                    Template('Good!')],

    'common.have_fun': [Template('Have fun!')],
    'common.hi': [Template('Hello{ ${user_name}}!'),
                  Template('Hey{ ${user_name}}!'),
                  Template('Hi{ ${user_name}}'),
                  Template('Hello there{ ${user_name}}!')],

    'common.how_are_you': [Template('How are you{ ${user_name}}?'),
                           Template('How is it going{ ${user_name}}?'),
                           Template('What\'s up{ ${user_name}}?')],

    'common.im_fine': [Template('I am fine, thank you{ ${user_name}}!'),
                       Template('I am doing great, thanks for asking!'),
                       Template('I am well, thanks!')],

    'common.no': [Template('No.'),
                  Template('Nope')],

    'common.thanks': [Template('Thank you{ ${user_name}}!'),
                      Template('Thanks{ ${user_name}}'),
                      Template('Thanks a lot')],

    'common.yes': [Template('Yes.'),
                   Template('OK'),
                   Template('Yeah sure!'),
                   Template('Yep')],

    'common.you_are_welcome': [Template('You are welcome!'),
                               Template('No problem at all'),
                               Template('Glad to help')],

    'commons.more': [Template('Can I do anything else for you?'),
                     Template('Anything else?'),
                     Template('Anything else I can help you with?')],

    'commons.nice_to_meet_you': [Template('Nice to meet you!'),
                                 Template('Pleased to meet you')],

    'commons.sorry': [Template('Sorry!'),
                      Template('Excuse me..'),
                      Template('Pardon me.')],

    'common.you_too': [Template('You too!')],

    'offer.player.news': [Template('I can show you news{ about ${player_name}}!'),
                          Template('Do you want to see news{ about ${player_name}}?'),
                          Template('How about some news{ about ${player_name}}?')],

    'reaction.bad_you_didnt_like': [Template('Too bad you didn\'t like that...')],

    'reaction.glad_you_liked_it': [Template('I am glad you liked it!'),
                                   Template('It is great to liked it!'),
                                   Template('It is really nice you liked it')],

    'response.abilities':
        [Template('I can show you news about your favorite players and answer questions about them!')],

    'response.bot': [Template('I am a bot, but I am not planning on taking over the world'),
                     Template('Yes I am a bot!')],

    'response.list.jerseys': [Template('I know about all kinds of jerseys of Bayern, Juventus and Barca')],

    'response.list.players': [Template('I know about Thomas Müller, Cristiano Ronaldo and many more!')],

    'response.player.information.age': [Template('{${player_name} }is 28 years old.')],

    'response.player.information.goals': [Template('{${player_name} }scored 35 times.')],

    'response.player.information.height': [Template('{${player_name} }is 1.86m tall.')],

    'response.player.information.shoe': [Template('{${player_name} }wears the Adidas X 17.1'),
                                         Template('{${player_name} }uses the Adidas X 17.1')],

    'response.player.news': [Template('Have you seen this{ ${content_type}}{ of ${player_name}}? {${content}}'),
                             Template('Do you know this{ ${content_type}}{ of ${player_name}} already? {${content}}')],

    'userprofile.query.active': [Template('Are you an active soccer player?'),
                                 Template('Do you play soccer actively yourself?')],

    'userprofile.query.age': [Template('How old are you?')],

    'userprofile.query.fan': [Template('Are you a soccer fan?'),
                              Template('Do you like soccer?')],

    'userprofile.query.name': [Template('What\'s your name?'),
                               Template('How can I call you?')],
}

# currently scalar
SENTIMENT_LEN = 1

QUALITY_LEN = 1

# only depicts whether the variable in question is known or not
USER_PROFILE_VARIABLES = [
    'name',
    'age',
    'favorite_player',
    'favorite_team',
    'active_player'
]
USER_PROFILE_LEN = len(USER_PROFILE_VARIABLES)

STATE_SHAPE = (NUM_INTENTS + SENTIMENT_LEN + USER_PROFILE_LEN,)
CONTEXT_LENGTH = 5
CONTEXT_SHAPE = (CONTEXT_LENGTH,) + (STATE_SHAPE[0] + NUM_ACTIONS,)

IMAGINATION_DEPTH = 3
BATCH_SIZE = 10
NUM_EPOCHS = 10
TEST_RATIO = .1

START_DISCOUNT = .99
END_DISCOUNT = .75
END_DISCOUNT_BATCHES = 5000

START_EPSILON = .5
EPSILON_DECAY = 1.0001

EPISODE_SIZE = 50
STEPS_PER_EPISODE = int(EPISODE_SIZE / BATCH_SIZE)

# time to wait for another message before marking a message as terminal (ending conversation)
SECONDS_FOR_TERMINAL = 60
SECONDS_PER_DAY = 3600 * 24

# noinspection PyUnresolvedReferences
WEIGHTS_DIR = os.path.join(".", "bot", "weights")
# noinspection PyUnresolvedReferences
LOG_DIR = os.path.join(".", "bot", "logs")
