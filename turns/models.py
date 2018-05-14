import random

from django.db import models

from chat.models import Message


class Dialogue(models.Model):
    held_on = models.DateTimeField(auto_now_add=True)
    with_user = models.CharField(max_length=64, null=False, unique=True)

    @staticmethod
    def sample_random_uniform():
        """
        Samples a random Dialogue, useful for training a DQN
        :return: a random Dialogue object
        """
        dialogues = Dialogue.objects.distinct('id')
        num_dialogues = len(dialogues)
        index = int(num_dialogues * random.random())
        return dialogues[index]

    def __str__(self):
        return 'Dialog in {}'.format(self.with_user)


class ParameterTemplate(models.Model):
    name = models.CharField(max_length=64, null=False)
    is_list = models.BooleanField(default=False)


class IntentTemplate(models.Model):
    dialog_flow_id = models.CharField(max_length=64, unique=True, null=False)
    name = models.CharField(max_length=64, unique=True, null=False)

    parameters = models.ManyToManyField(to=ParameterTemplate)

    def __str__(self):
        return self.name


class Intent(models.Model):
    template = models.ForeignKey(IntentTemplate, on_delete=models.CASCADE)

    def __str__(self):
        return 'template instance of "{}"'.format(self.template)


class Parameter(models.Model):
    value = models.CharField(max_length=128)

    template = models.ForeignKey(ParameterTemplate, on_delete=models.CASCADE)
    intent = models.ForeignKey(Intent, on_delete=models.CASCADE)

    def __str__(self):
        return self.value


class Shoe(models.Model):
    name = models.CharField(max_length=64, unique=True, null=False)

    url = models.CharField(max_length=1024, null=False)


class Team(models.Model):
    name = models.CharField(max_length=64, unique=True, null=False)


class Player(models.Model):
    name = models.CharField(max_length=64, unique=True, null=False)

    age = models.IntegerField(null=True)
    height = models.DecimalField(max_digits=3, decimal_places=2, null=True)
    goals = models.IntegerField(null=True)

    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True)
    shoes = models.ForeignKey(Shoe, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return '<Player: {}>'.format(self.name)


class UserProfile(models.Model):
    name = models.CharField(max_length=128, null=True)

    has_favourite_player = models.NullBooleanField()
    favourite_player = models.ForeignKey(Player, on_delete=models.CASCADE, null=True)

    has_favourite_team = models.NullBooleanField()
    favourite_team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True)

    is_active_player = models.NullBooleanField()

    age = models.DecimalField(max_digits=3, decimal_places=0, null=True)

    def __str__(self):
        return 'UserProfile(name: {}, age: {}, favorite player: {}, favorite team: {}, is an active player: {})'.format(
            self.name,
            self.age,
            self.favourite_player if self.has_favourite_player is not None else 'No favorite player',
            self.favourite_team if self.has_favourite_team is not None else 'No favorite team',
            self.is_active_player
        )


class Sentence(models.Model):
    value = models.CharField(max_length=1024)
    sentiment = models.DecimalField(max_digits=10, decimal_places=9, null=True)
    reward = models.DecimalField(max_digits=10, decimal_places=9, null=False, default=0.6)

    terminal = models.BooleanField(null=False, default=False)

    intent = models.ForeignKey(Intent, on_delete=models.CASCADE, null=True)

    raw_sentence = models.ForeignKey(Message, null=True, on_delete=models.SET_NULL)

    used_in_training = models.BooleanField(default=False)

    said_on = models.DateTimeField(auto_now_add=True, )
    said_by = models.CharField(max_length=64, null=False)
    said_in = models.ForeignKey(Dialogue, null=False, on_delete=models.CASCADE)

    user_profile = models.ForeignKey(UserProfile, on_delete=models.DO_NOTHING, null=True)

    created_by = models.CharField(max_length=128, null=True)

    def __str__(self):
        return '"{}"(id={})'.format(self.value, self.id)

    @staticmethod
    def sample_sentence(said_by_name: str):
        """
        samples a random sentence uniformly

        :parameter said_by_name: a string, representing the bot user name, only "actions" are valid

        :return: a random sentence object
        """
        num_sentences = Sentence.objects.filter(said_by=said_by_name).count()
        return Sentence.objects.all().filter(said_by=said_by_name)[random.randint(0, num_sentences - 1)]

    @staticmethod
    def sample_sentence_in_range(said_by_name: str, start: int, stop: int):
        """
        uniformly samples a random sentence said by the bot,
        :param said_by_name: name of the user to filter sentences by
        :param start: start index to sample from (inclusive)
        :param stop: stop index to sample to (exclusive)

        :return: a random sentence object
        """
        range_size = stop - start
        assert range_size > 0, 'stop index must be (>=) greater than start index.'
        episode = Sentence.get_episode(start, stop)
        episode = [sentence for sentence in episode if sentence.said_by == said_by_name]
        num_sentences = len(episode)
        assert num_sentences > 0, 'there are no sentences of {} said in the given range'.format(said_by_name)
        offset = random.randint(0, num_sentences - 1)
        return episode[offset]

    @staticmethod
    def get_episode(start, stop):
        """TODO: write me"""
        return [sentence for sentence in Sentence.objects.all()[start:stop]]

    @staticmethod
    def has_episode(start, stop):
        return len(Sentence.get_episode(start, stop)) > 0
