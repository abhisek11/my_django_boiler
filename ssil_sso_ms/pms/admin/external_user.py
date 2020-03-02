from django.contrib import admin
from pms.models.module_tender import *
from pms.models.module_external_user import *


@admin.register(PmsExternalUsersType)
class PmsExternalUsersType(admin.ModelAdmin):
    list_display = [field.name for field in PmsExternalUsersType._meta.fields]

@admin.register(PmsExternalUsers)
class PmsExternalUsers(admin.ModelAdmin):
    list_display = [field.name for field in PmsExternalUsers._meta.fields]
    search_fields = ('code',)

@admin.register(PmsExternalUsersDocument)
class PmsExternalUsersDocument(admin.ModelAdmin):
    list_display = [field.name for field in PmsExternalUsersDocument._meta.fields]

@admin.register(PmsExternalUsersExtraDetailsTenderMapping)
class PmsExternalUsersExtraDetailsTenderMapping(admin.ModelAdmin):
    list_display = [field.name for field in PmsExternalUsersExtraDetailsTenderMapping._meta.fields]

@admin.register(PmsExternalUsersExtraDetailsTenderMappingDocument)
class PmsExternalUsersExtraDetailsTenderMappingDocument(admin.ModelAdmin):
    list_display = [field.name for field in PmsExternalUsersExtraDetailsTenderMappingDocument._meta.fields]