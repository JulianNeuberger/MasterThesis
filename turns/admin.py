from django.contrib import admin

from turns.models import *


@admin.register(Dialogue, Sentence, Intent, Slot, IntentTemplate, SlotTemplate)
class TurnAdmin(admin.ModelAdmin):
    pass
