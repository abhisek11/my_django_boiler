from django.contrib import admin
from holidays.models import *

# Register your models here.

@admin.register(HolidaysList)
class HolidaysList(admin.ModelAdmin):
    list_display = [field.name for field in HolidaysList._meta.fields]


@admin.register(HolidayStateMapping)
class HolidayStateMapping(admin.ModelAdmin):
    list_display = [field.name for field in HolidayStateMapping._meta.fields]
    