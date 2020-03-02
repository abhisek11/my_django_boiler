from django.contrib import admin
from pms.models.module_project import *
from pms.models.module_tender import *

@admin.register(PmsSiteTypeProjectSiteManagement)
class PmsSiteTypeProjectSiteManagement(admin.ModelAdmin):
    list_display = [field.name for field in PmsSiteTypeProjectSiteManagement._meta.fields]

@admin.register(PmsSiteProjectSiteManagement)
class PmsSiteProjectSiteManagement(admin.ModelAdmin):
    list_display = [field.name for field in PmsSiteProjectSiteManagement._meta.fields]

@admin.register(PmsProjects)
class PmsProjects(admin.ModelAdmin):
    list_display = [field.name for field in PmsProjects._meta.fields]
    search_fields = ('name', 'project_g_id', 'start_date','end_date')

@admin.register(PmsProjectUserMapping)
class PmsProjectUserMapping(admin.ModelAdmin):
    list_display = [field.name for field in PmsProjectUserMapping._meta.fields]
