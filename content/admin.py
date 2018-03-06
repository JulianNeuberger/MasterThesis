from django.contrib import admin

from content.models import Content


@admin.register(Content)
class TurnAdmin(admin.ModelAdmin):
    pass
