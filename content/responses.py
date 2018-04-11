import logging
from random import randint

from config.models import Configuration
from content.content import SimpleContentInterface

logger = logging.getLogger('content')


class ResponseFactory:
    def __init__(self):
        self._base_sentences = Configuration.get_active().response_templates.all()
        for template in self._base_sentences:
            template.prepare()
        self._context = {}
        self._tracking_table = {
            'query.player.height': ['player'],
            'query.player.information.age': ['player'],
            'query.player.information.goals': ['player'],
            'query.player.information.shoe': ['player'],
            'query.player.news': ['content-type', 'player'],
            'query.player.news.more': ['player', 'content-type'],
            'userprofile.response.name': ['given-name'],
            'userprofile.response.favorite_player': ['player'],
            'userprofile.response.age': ['age']
        }
        self._response_builders = {
            'common.hi': self._greeting,
            'common.thanks': self._thanks,
            'common.how_are_you': self._how_are_you,
            'response.player.news': self._content,
            'response.player.information.age': self._player_age,
            'response.player.information.height': self._player_height,
            'response.player.information.goals': self._player_goals,
            'response.player.information.shoe': self._player_shoe,
            'offer.player.news': self._offer_content,
        }
        self._content_interface = SimpleContentInterface()

    def create_response(self, action_name):
        try:
            return self._response_builders[action_name]()
        except KeyError:
            return self._default(action_name)

    def update(self, intent):
        intent_name = intent.template.name
        if intent_name in self._tracking_table.keys():
            tracked_params = self._tracking_table[intent_name]
            parameters = intent.parameter_set.all()
            for parameter in parameters:
                if parameter.template.name in tracked_params:
                    if parameter.value is not None and len(parameter.value) > 0:
                        key = parameter.template.name
                        self._context[key] = parameter.value

    def _default(self, action_name):
        template = self._get_template(action_name)
        return template.substitute()

    def _greeting(self):
        template = self._get_template('common.hi')
        return template.substitute({'user_name': self._get_user_name()})

    def _thanks(self):
        template = self._get_template('common.thanks')
        return template.substitute({'user_name': self._get_user_name()})

    def _how_are_you(self):
        template = self._get_template('common.how_are_you')
        return template.substitute({'user_name': self._get_user_name()})

    def _content(self):
        template = self._get_template('response.player.news')
        player_name = self._get_requested_player_name()
        content_type = self._get_requested_content_type()
        content = self._content_interface.content_for_player_name(player_name, content_type)
        return template.substitute({
            'player_name': player_name,
            'content_type': content_type,
            'content': content.url
        })

    def _offer_content(self):
        template = self._get_template('offer.player.news')
        player_name = self._get_requested_player_name()
        content_type = self._get_requested_content_type()
        return template.substitute({
            'player_name': player_name,
            'content_type': content_type
        })

    def _player_age(self):
        template = self._get_template('response.player.information.age')
        return template.substitute({
            'player_name': self._get_requested_player_name(),
            'player_age': '## PLACEHOLDER: 28'
        })

    def _player_goals(self):
        template = self._get_template('response.player.information.goals')
        return template.substitute({
            'player_name': self._get_requested_player_name(),
            'player_goals': '## PLACEHOLDER: 10'
        })

    def _player_height(self):
        template = self._get_template('response.player.information.height')
        return template.substitute({
            'player_name': self._get_requested_player_name(),
            'player_height': '## PLACEHOLDER: 1,80m ##'
        })

    def _player_shoe(self):
        template = self._get_template('response.player.information.shoe')
        return template.substitute({
            'player_name': self._get_requested_player_name(),
            'player_shoe': '## PLACEHOLDER: X17 ##'
        })

    def _get_template(self, intent_name):
        base_sentences = [base_sentence for base_sentence in self._base_sentences if
                          base_sentence.for_action.name == intent_name]
        assert len(base_sentences) > 0, 'No template for action {}, add one!'.format(intent_name)
        if len(base_sentences) > 1:
            return base_sentences[randint(0, len(base_sentences) - 1)]
        return base_sentences[0]

    def _get_user_name(self):
        return self._context.get('given-name', None)

    def _get_requested_player_name(self):
        return self._context.get('player', None)

    def _get_requested_content_type(self):
        return self._context.get('content-type', None)

    def _get_user_age(self):
        return self._context.get('age', None)
