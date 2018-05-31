import os
from typing import Tuple

from django.db import models
from django.db.utils import OperationalError

from content.template import Template
from turns.models import IntentTemplate


class UserProfileVariable(models.Model):
    name = models.CharField(max_length=64)


class ResponseTemplate(models.Model):
    for_action = models.ForeignKey(IntentTemplate, related_name='+', on_delete=models.CASCADE)
    value = models.CharField(max_length=256)

    _prepared = None

    def prepare(self):
        self._prepared = Template(self.value)

    def substitute(self, replacements=None):
        """
        Replaces the occurrences of placeholders by their corresponding values given in key word arguments.
        If the corresponding value in kwargs is empty, it will replace the placeholder with the empty string
        and move on.

        :param replacements: dictionary of values to replace the placeholders with
        :return: the string "pattern" given in __init__ with replaced placeholders
        """
        assert self._prepared is not None
        return self._prepared.substitute(replacements)

    def __str__(self):
        return '<ResponseTemplate(for="{}")(value="{}")>'.format(self.for_action.name, self.value)


# noinspection PyUnresolvedReferences
class Configuration(models.Model):
    active_calls = 0
    total_time = 0

    state_intents = models.ManyToManyField(IntentTemplate, related_name='+')
    action_intents = models.ManyToManyField(IntentTemplate, related_name='+')
    unknown_intent = models.ForeignKey(IntentTemplate, related_name='+', null=True, on_delete=models.CASCADE)
    didnt_understand_intent = models.ForeignKey(IntentTemplate, related_name='+', null=True, on_delete=models.CASCADE)
    response_templates = models.ManyToManyField(ResponseTemplate)

    sentiment_length = models.IntegerField(default=1)
    quality_length = models.IntegerField(default=1)
    user_profile_variable_names = models.ManyToManyField(UserProfileVariable, related_name='+')

    context_length = models.IntegerField(default=5)

    discount = models.DecimalField(max_digits=10, decimal_places=9, default='0.99')
    epsilon = models.DecimalField(max_digits=10, decimal_places=9, default=0)

    batch_size = models.IntegerField(default=10)
    episode_size = models.IntegerField(default=50)
    test_ratio = models.DecimalField(max_digits=10, decimal_places=9, default=.1)
    steps_per_episode = models.IntegerField(default=5)

    seconds_for_terminal = models.IntegerField(default=60)

    created_on = models.DateTimeField(auto_now_add=True)

    @property
    def number_of_user_intents(self) -> int:
        return self.number_state_intents

    @property
    def number_state_intents(self) -> int:
        return self.state_intents.count()

    @property
    def number_actions(self) -> int:
        return self.number_action_intents

    @property
    def number_action_intents(self) -> int:
        return self.action_intents.count()

    @property
    def number_of_user_profile_variables(self) -> int:
        return self.user_profile_variable_names.count()

    @property
    def state_shape(self) -> Tuple[int]:
        return self.number_state_intents + self.sentiment_length + self.number_of_user_profile_variables,

    @property
    def context_shape(self) -> Tuple[int, int]:
        return (self.context_length,) + (self.state_shape[0] + self.number_actions,)

    @property
    def seconds_per_day(self):
        return 3600 * 24

    @property
    def weights_dir(self):
        return os.path.join(".", "bot", "weights")

    @property
    def log_dir(self):
        return os.path.join(".", "bot", "logs")

    def action_index_for_name(self, name):
        action = IntentTemplate.objects.get(name=name)
        return list(self.action_intents.all()).index(action)

    def state_index_for_name(self, name):
        intent = IntentTemplate.objects.get(name=name)
        return list(self.state_intents.all()).index(intent)

    def is_action_intent(self, name):
        action = IntentTemplate.objects.get(name=name)
        return action in self.action_intents.all()

    def is_state_intent(self, name):
        intent = IntentTemplate.objects.get(name=name)
        return intent in self.state_intents.all()

    @staticmethod
    def get_active():
        """
        Get the latest configuration.

        Will create a new persisted one, if none exists.
        If database is not accessible (or table does not exist) returns an empty
        Configuration object, which will not be persisted

        :return: a Configuration object
        """
        try:
            config = Configuration.objects.order_by('-created_on')[0]
        except IndexError:
            # no configurations exist, create default one and persist it
            config = Configuration.objects.create()
        except OperationalError:
            # cannot access db or table does not exist
            # happens, if you install app for the first time and want to migrate
            # in this case config isn't needed, create empty object, don't persist it
            config = Configuration(id=0)
        return config
