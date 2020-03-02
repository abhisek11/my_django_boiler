from django.contrib import admin
from pms.models.module_approval_permission import *

@admin.register(PmsApprovalPermissonLavelMatser)
class PmsApprovalPermissonLavelMatser(admin.ModelAdmin):
    list_display = [field.name for field in PmsApprovalPermissonLavelMatser._meta.fields]

@admin.register(PmsApprovalPermissonMatser)
class PmsApprovalPermissonMatser(admin.ModelAdmin):
    list_display = [field.name for field in PmsApprovalPermissonMatser._meta.fields]



