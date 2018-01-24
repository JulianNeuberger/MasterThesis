import os

INTENTS = [
    'common.unknown',
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
    'reaction.content.positive',
    'userprofile.response.active',
    'userprofile.response.age',
    'userprofile.response.fan',
    'userprofile.response.favorite_player',
    'userprofile.response.inactive',
    'userprofile.response.name'
]
NUM_INTENTS = len(INTENTS)
ACTIONS = [
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
CONTEXT_SHAPE = (CONTEXT_LENGTH,) + STATE_SHAPE

IMAGINATION_DEPTH = 3
BATCH_SIZE = 32
NUM_EPOCHS = 1000
TEST_RATIO = .3

DISCOUNT = .1
START_DISCOUNT = .1
END_DISCOUNT = .8
EPOCHS_UNTIL_FULL_DISCOUNT = int(NUM_EPOCHS / 2)

# time to wait for another message after an "commons.bye" before marking a message as terminal (ending conversation)
SECONDS_FOR_TERMINAL = 60
SECONDS_PER_DAY = 3600 * 24

WEIGHTS_DIR = "./weights"
IMAGINATION_MODEL_LATEST_WEIGHTS_FILE = os.path.join(WEIGHTS_DIR, 'imagination_latest.pkl')
