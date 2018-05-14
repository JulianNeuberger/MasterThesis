from django.contrib import admin

from turns.models import Dialogue, Sentence, Intent, Parameter, IntentTemplate, ParameterTemplate, Player


@admin.register(Dialogue, Sentence, Intent, Parameter, IntentTemplate, ParameterTemplate, Player)
class TurnAdmin(admin.ModelAdmin):
    pass
