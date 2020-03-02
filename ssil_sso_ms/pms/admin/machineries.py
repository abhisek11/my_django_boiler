from django.contrib import admin
from pms.models.module_machineries import *
from pms.models.module_project import *


@admin.register(PmsMachineriesWorkingCategory)
class PmsMachineriesWorkingCategory(admin.ModelAdmin):
    list_display = [field.name for field in PmsMachineriesWorkingCategory._meta.fields]


@admin.register(PmsMachineryType)
class PmsMachineryType(admin.ModelAdmin):
    list_display = [field.name for field in PmsMachineryType._meta.fields]

@admin.register(PmsMachineries)
class PmsMachineries(admin.ModelAdmin):
    list_display = [field.name for field in PmsMachineries._meta.fields]

@admin.register(PmsMachineriesDetailsDocument)
class PmsMachineriesDetailsDocument(admin.ModelAdmin):
    list_display = [field.name for field in PmsMachineriesDetailsDocument._meta.fields]

@admin.register(PmsMachinaryRentedTypeMaster)
class PmsMachinaryRentedTypeMaster(admin.ModelAdmin):
    list_display = [field.name for field in PmsMachinaryRentedTypeMaster._meta.fields]

@admin.register(PmsMachinaryRentedDetails)
class PmsMachinaryRentedDetails(admin.ModelAdmin):
    list_display = [field.name for field in PmsMachinaryRentedDetails._meta.fields]

@admin.register(PmsMachinaryOwnerDetails)
class PmsMachinaryOwnerDetails(admin.ModelAdmin):
    list_display = [field.name for field in PmsMachinaryOwnerDetails._meta.fields]

@admin.register(PmsMachinaryOwnerEmiDetails)
class PmsMachinaryOwnerEmiDetails(admin.ModelAdmin):
    list_display = [field.name for field in PmsMachinaryOwnerEmiDetails._meta.fields]

@admin.register(PmsMachinaryContractDetails)
class PmsMachinaryContractDetails(admin.ModelAdmin):
    list_display = [field.name for field in PmsMachinaryContractDetails._meta.fields]


@admin.register(PmsMachinaryLeaseDetails)
class PmsMachinaryLeaseDetails(admin.ModelAdmin):
    list_display = [field.name for field in PmsMachinaryLeaseDetails._meta.fields]


@admin.register(PmsProjectsMachinaryMapping)
class PmsProjectsMachinaryMapping(admin.ModelAdmin):
    list_display = [field.name for field in PmsProjectsMachinaryMapping._meta.fields]

@admin.register(PmsProjectsMachinaryReport)
class PmsProjectsMachinaryReport(admin.ModelAdmin):
    list_display = [field.name for field in PmsProjectsMachinaryReport._meta.fields]