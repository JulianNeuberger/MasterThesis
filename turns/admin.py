from django.contrib import admin

from turns.models import *


@admin.register(Dialogue, Sentence, Intent, Parameter, IntentTemplate, ParameterTemplate)
class TurnAdmin(admin.ModelAdmin):
    pass
