from django.contrib import admin
from etask.models import *

# Register your models here.
@admin.register(EtaskTask)
class EtaskTask(admin.ModelAdmin):
    list_display = [field.name for field in EtaskTask._meta.fields]

@admin.register(EtaskUserCC)
class EtaskUserCC(admin.ModelAdmin):
    list_display = [field.name for field in EtaskUserCC._meta.fields]

# @admin.register(EtaskAssignTo)
# class EtaskAssignTo(admin.ModelAdmin):
#     list_display = [field.name for field in EtaskAssignTo._meta.fields]

@admin.register(ETaskReportingDates)
class ETaskReportingDates(admin.ModelAdmin):
    list_display = [field.name for field in ETaskReportingDates._meta.fields]

@admin.register(ETaskReportingActionLog)
class ETaskReportingActionLog(admin.ModelAdmin):
    list_display = [field.name for field in ETaskReportingActionLog._meta.fields]

@admin.register(ETaskComments)
class ETaskComments(admin.ModelAdmin):
    list_display = [field.name for field in ETaskComments._meta.fields]

@admin.register(ETaskCommentsViewers)
class ETaskCommentsViewers(admin.ModelAdmin):
    list_display = [field.name for field in ETaskCommentsViewers._meta.fields]

@admin.register(EtaskIncludeAdvanceCommentsCostDetails)
class EtaskIncludeAdvanceCommentsCostDetails(admin.ModelAdmin):
    list_display = [field.name for field in EtaskIncludeAdvanceCommentsCostDetails._meta.fields]

@admin.register(EtaskIncludeAdvanceCommentsOtherDetails)
class EtaskIncludeAdvanceCommentsOtherDetails(admin.ModelAdmin):
    list_display = [field.name for field in EtaskIncludeAdvanceCommentsOtherDetails._meta.fields]

@admin.register(EtaskIncludeAdvanceCommentsDocuments)
class EtaskIncludeAdvanceCommentsDocuments(admin.ModelAdmin):
    list_display = [field.name for field in EtaskIncludeAdvanceCommentsDocuments._meta.fields]

@admin.register(EtaskFollowUP)
class EtaskFollowUP(admin.ModelAdmin):
    list_display = [field.name for field in EtaskFollowUP._meta.fields]

@admin.register(FollowupComments)
class FollowupComments(admin.ModelAdmin):
    list_display = [field.name for field in FollowupComments._meta.fields]

@admin.register(FollowupIncludeAdvanceCommentsCostDetails)
class FollowupIncludeAdvanceCommentsCostDetails(admin.ModelAdmin):
    list_display = [field.name for field in FollowupIncludeAdvanceCommentsCostDetails._meta.fields]

@admin.register(FollowupIncludeAdvanceCommentsOtherDetails)
class FollowupIncludeAdvanceCommentsOtherDetails(admin.ModelAdmin):
    list_display = [field.name for field in FollowupIncludeAdvanceCommentsOtherDetails._meta.fields]
@admin.register(EtaskAppointment)
class EtaskAppointment(admin.ModelAdmin):
    list_display = [field.name for field in EtaskAppointment._meta.fields]

@admin.register(EtaskInviteEmployee)
class EtaskInviteEmployee(admin.ModelAdmin):
    list_display = [field.name for field in EtaskInviteEmployee._meta.fields]

@admin.register(EtaskInviteExternalPeople)
class EtaskInviteExternalPeople(admin.ModelAdmin):
    list_display = [field.name for field in EtaskInviteExternalPeople._meta.fields]

@admin.register(FollowupIncludeAdvanceCommentsDocuments)
class FollowupIncludeAdvanceCommentsDocuments(admin.ModelAdmin):
    list_display = [field.name for field in FollowupIncludeAdvanceCommentsDocuments._meta.fields]

@admin.register(AppointmentComments)
class AppointmentComments(admin.ModelAdmin):
    list_display = [field.name for field in AppointmentComments._meta.fields]

@admin.register(AppointmentIncludeAdvanceCommentsCostDetails)
class AppointmentIncludeAdvanceCommentsCostDetails(admin.ModelAdmin):
    list_display = [field.name for field in AppointmentIncludeAdvanceCommentsCostDetails._meta.fields]

@admin.register(AppointmentIncludeAdvanceCommentsOtherDetails)
class AppointmentIncludeAdvanceCommentsOtherDetails(admin.ModelAdmin):
    list_display = [field.name for field in AppointmentIncludeAdvanceCommentsOtherDetails._meta.fields]

@admin.register(AppointmentIncludeAdvanceCommentsDocuments)
class AppointmentIncludeAdvanceCommentsDocuments(admin.ModelAdmin):
    list_display = [field.name for field in AppointmentIncludeAdvanceCommentsDocuments._meta.fields]


@admin.register(EtaskMonthlyReportingDate)
class EtaskMonthlyReportingDate(admin.ModelAdmin):
    list_display = [field.name for field in EtaskMonthlyReportingDate._meta.fields]

@admin.register(EtaskTaskEditLog)
class EtaskTaskEditLog(admin.ModelAdmin):
    list_display = [field.name for field in EtaskTaskEditLog._meta.fields]

@admin.register(EtaskTaskTransferLog)
class EtaskTaskTransferLog(admin.ModelAdmin):
    list_display = [field.name for field in EtaskTaskTransferLog._meta.fields]

@admin.register(EtaskTaskSubAssignLog)
class EtaskTaskSubAssignLog(admin.ModelAdmin):
    list_display = [field.name for field in EtaskTaskSubAssignLog._meta.fields]
