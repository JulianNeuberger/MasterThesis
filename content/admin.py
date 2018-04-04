from django.contrib import admin

from content.models import Content


@admin.register(Content)
class CcntentAdmin(admin.ModelAdmin):
    pass
