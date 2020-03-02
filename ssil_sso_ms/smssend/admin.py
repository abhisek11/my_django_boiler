from django.contrib import admin

from smssend.models import *

@admin.register(SmsContain)
class SmsContain(admin.ModelAdmin):
    list_display = [field.name for field in SmsContain._meta.fields]
