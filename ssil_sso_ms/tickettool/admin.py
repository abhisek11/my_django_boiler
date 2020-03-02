from django.contrib import admin

from tickettool.models import *
# Register your models here.


@admin.register(SupportType)
class SupportType(admin.ModelAdmin):
    list_display = [field.name for field in SupportType._meta.fields]

@admin.register(Ticket)
class Ticket(admin.ModelAdmin):
    list_display = [field.name for field in Ticket._meta.fields]