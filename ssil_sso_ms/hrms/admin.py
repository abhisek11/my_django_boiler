from django.contrib import admin
from hrms.models import *

# Register your models here.
@admin.register(HrmsBenefitsProvided)
class HrmsBenefitsProvided(admin.ModelAdmin):
    list_display = [field.name for field in HrmsBenefitsProvided._meta.fields]

@admin.register(HrmsUsersBenefits)
class HrmsUsersBenefits(admin.ModelAdmin):
    list_display = [field.name for field in HrmsUsersBenefits._meta.fields]

@admin.register(HrmsUsersOtherFacilities)
class HrmsUsersOtherFacilities(admin.ModelAdmin):
    list_display = [field.name for field in HrmsUsersOtherFacilities._meta.fields]

@admin.register(HrmsDocument)
class HrmsDocument(admin.ModelAdmin):
    list_display = [field.name for field in HrmsDocument._meta.fields]

@admin.register(HrmsDynamicSectionFieldLabelDetailsWithDoc)
class HrmsDynamicSectionFieldLabelDetailsWithDoc(admin.ModelAdmin):
    list_display = [field.name for field in HrmsDynamicSectionFieldLabelDetailsWithDoc._meta.fields]

@admin.register(HrmsNewRequirement)
class HrmsNewRequirement(admin.ModelAdmin):
    list_display = [field.name for field in HrmsNewRequirement._meta.fields]

@admin.register(HrmsInterviewType)
class HrmsInterviewType(admin.ModelAdmin):
    list_display = [field.name for field in HrmsInterviewType._meta.fields]

@admin.register(HrmsInterviewLevel)
class HrmsInterviewLevel(admin.ModelAdmin):
    list_display = [field.name for field in HrmsInterviewLevel._meta.fields]

@admin.register(HrmsScheduleInterview)
class HrmsScheduleInterview(admin.ModelAdmin):
    list_display = [field.name for field in HrmsScheduleInterview._meta.fields]

@admin.register(HrmsScheduleAnotherRoundInterview)
class HrmsScheduleAnotherRoundInterview(admin.ModelAdmin):
    list_display = [field.name for field in HrmsScheduleAnotherRoundInterview._meta.fields]

@admin.register(HrmsScheduleInterviewWith)
class HrmsScheduleInterviewWith(admin.ModelAdmin):
    list_display = [field.name for field in HrmsScheduleInterviewWith._meta.fields]

@admin.register(HrmsScheduleInterviewFeedback)
class HrmsScheduleInterviewFeedback(admin.ModelAdmin):
    list_display = [field.name for field in HrmsScheduleInterviewFeedback._meta.fields]

@admin.register(HrmsNewRequirementLog)
class HrmsNewRequirementLog(admin.ModelAdmin):
    list_display = [field.name for field in HrmsNewRequirementLog._meta.fields]


@admin.register(HrmsScheduleInterviewLog)
class HrmsScheduleInterviewLog(admin.ModelAdmin):
    list_display = [field.name for field in HrmsScheduleInterviewLog._meta.fields]


@admin.register(HrmsQualificationMaster)
class HrmsQualificationMaster(admin.ModelAdmin):
    list_display = [field.name for field in HrmsQualificationMaster._meta.fields]

@admin.register(HrmsUserQualification)
class HrmsUserQualification(admin.ModelAdmin):
    list_display = [field.name for field in HrmsUserQualification._meta.fields]

@admin.register(HrmsUserQualificationDocument)
class HrmsUserQualificationDocument(admin.ModelAdmin):
    list_display = [field.name for field in HrmsUserQualificationDocument._meta.fields]