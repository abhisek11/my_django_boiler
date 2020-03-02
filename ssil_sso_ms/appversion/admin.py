from django.contrib import admin
from appversion.models import *

@admin.register(AppVersion)
class AppVersion(admin.ModelAdmin):
    list_display = [field.name for field in AppVersion._meta.fields]