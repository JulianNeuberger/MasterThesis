from django.contrib import admin

from turns.models import Dialogue, Sentence, Intent, Parameter, IntentTemplate, ParameterTemplate


@admin.register(Dialogue, Sentence, Intent, Parameter, IntentTemplate, ParameterTemplate)
class TurnAdmin(admin.ModelAdmin):
    pass
