import os
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
ACTIONS = [
    'common.what',
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
    'common.you_too', # maybe comment out this one for demoing?
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
    'common.what': 'Sorry, I didn\'t get that',
    'common.bad': 'That\'s bad...',
    'common.bye': 'Bye!',
    'common.good': 'That is good!',
    'common.have_fun': 'Have fun!',
    'common.hi': 'Hello!',
    'common.how_are_you': 'How are you?',
    'common.im_fine': 'I am fine, thank you!',
    'common.no': 'No.',
    'common.thanks': 'Thank you!',
    'common.yes': 'Yes.',
    'common.you_are_welcome': 'You are welcome!',
    'commons.more': 'Can I do anything else for you?',
    'commons.nice_to_meet_you': 'Nice to meet you!',
    'commons.sorry': 'Sorry!',
    'offer.player.news': 'I can show you news about this player!',
    'reaction.bad_you_didnt_like': 'Too bad you didn\'t like that...',
    'reaction.glad_you_liked_it': 'I am glad you liked it!',
    'response.abilities': 'I can show you news about your favorite players and answer questions about them!',
    'response.bot': 'I am a bot, but I am not planning on taking over the world',
    'response.list.jerseys': 'I know about all kinds of jerseys of Bayern, Juventus and Barca',
    'response.list.players': 'I know about Thomas Müller, Cristiano Ronaldo and many more',
    'response.player.information.age': 'Thomas Müller is 28 years old.',
    'response.player.information.goals': 'Thomas Müller scored 35 times in total last season.',
    'response.player.information.height': 'Thomas Müller is 1.86m tall.',
    'response.player.information.shoe': 'Thomas Müller wears the Adidas X 17.1',
    'response.player.news': 'Have you seen this video of Thomas Müller?',
    'userprofile.query.active': 'Are you an active soccer player?',
    'userprofile.query.age': 'How old are you?',
    'userprofile.query.fan': 'Are you a soccer fan?',
    'userprofile.query.name': 'What\'s your name?',
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

EPISODE_SIZE = 150
STEPS_PER_EPISODE = 15

# time to wait for another message after an "commons.bye" before marking a message as terminal (ending conversation)
SECONDS_FOR_TERMINAL = 60
SECONDS_PER_DAY = 3600 * 24

# noinspection PyUnresolvedReferences
WEIGHTS_DIR = os.path.join(".", "bot", "weights")
# noinspection PyUnresolvedReferences
LOG_DIR = os.path.join(".", "bot", "logs")
