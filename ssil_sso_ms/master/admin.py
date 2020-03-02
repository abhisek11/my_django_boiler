from django.contrib import admin

from master.models import *

@admin.register(TMasterModuleRoleUser)
class TMasterModuleRoleUser(admin.ModelAdmin):
    list_display = [field.name for field in TMasterModuleRoleUser._meta.fields]
    search_fields = ('mmr_module__cm_name', 'mmr_user__username','mmr_role__cr_name')

@admin.register(TMasterModuleRole)
class TMasterModuleRole(admin.ModelAdmin):
    list_display = [field.name for field in TMasterModuleRole._meta.fields]
    search_fields = ('mmro_module__cm_name','mmro_role__cr_name')

@admin.register(TMasterModuleOther)
class TMasterModuleOther(admin.ModelAdmin):
    list_display = [field.name for field in TMasterModuleOther._meta.fields]

@admin.register(TMasterOtherRole)
class TMasterOtherRole(admin.ModelAdmin):
    list_display = [field.name for field in TMasterOtherRole._meta.fields]
    search_fields = ('mor_role__id',)

@admin.register(TMasterOtherUser)
class TMasterOtherUser(admin.ModelAdmin):
    list_display = [field.name for field in TMasterOtherUser._meta.fields]
    search_fields = ('mou_user__id',)

@admin.register(TMasterModulePermissonBlock)
class TMasterModulePermissonBlock(admin.ModelAdmin):
    list_display = [field.name for field in TMasterModulePermissonBlock._meta.fields]
    search_fields = ('mmpb_module__cm_name',)


