from django.db import models

from chat.models import Message


class Dialogue(models.Model):
    held_on = models.DateTimeField(auto_now_add=True)
    with_user = models.CharField(max_length=64, null=False, unique=True)

    def __str__(self):
        return 'Dialog in {}'.format(self.with_user)


class IntentTemplate(models.Model):
    dialog_flow_id = models.CharField(max_length=64, unique=True, null=False)
    name = models.CharField(max_length=64, unique=True, null=False)

    def __str__(self):
        return self.name


class SlotType(models.Model):
    name = models.CharField(max_length=64, unique=True, null=False)

    def __str__(self):
        return self.name


class SlotTemplate(models.Model):
    dialog_flow_id = models.CharField(max_length=64, unique=True, null=False)
    name = models.CharField(max_length=64, null=False)

    type = models.ForeignKey(SlotType)
    intent_template = models.ForeignKey(IntentTemplate, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Intent(models.Model):
    template = models.ForeignKey(IntentTemplate, on_delete=models.CASCADE)

    def __str__(self):
        return 'template instance of "{}"'.format(self.template)


class Slot(models.Model):
    value = models.CharField(max_length=128)

    template = models.ForeignKey(SlotTemplate, on_delete=models.CASCADE)
    intent = models.ForeignKey(Intent, on_delete=models.CASCADE)

    def __str__(self):
        return self.value


class Player(models.Model):
    name = models.CharField(max_length=64, unique=True, null=False)


class Team(models.Model):
    name = models.CharField(max_length=64, unique=True, null=False)


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
    reward = models.DecimalField(max_digits=10, decimal_places=9, null=False, default=0)

    terminal = models.BooleanField(null=False, default=False)

    intent = models.ForeignKey(Intent, on_delete=models.CASCADE, null=True)

    raw_sentence = models.ForeignKey(Message, null=True)

    used_in_training = models.BooleanField(default=False)

    said_on = models.DateTimeField(auto_now_add=True)
    said_by = models.CharField(max_length=64, null=False)
    said_in = models.ForeignKey(Dialogue, null=False)

    user_profile = models.ForeignKey(UserProfile, on_delete=models.DO_NOTHING, null=True)

    def __str__(self):
        return self.value
