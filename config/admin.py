from django.contrib import admin

from config.models import Configuration, ResponseTemplate, UserProfileVariable
from turns.models import IntentTemplate


@admin.register(Configuration, ResponseTemplate, UserProfileVariable)
class ConfigurationAdmin(admin.ModelAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in ('didnt_understand_intent', 'unknown_intent', 'for_action'):
            kwargs['queryset'] = IntentTemplate.objects.order_by('name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name in ('action_intents', 'state_intents'):
            kwargs['queryset'] = IntentTemplate.objects.order_by('name')
        return super().formfield_for_manytomany(db_field, request, **kwargs)
