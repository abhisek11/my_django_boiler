from django.contrib import admin
from attendance.models import *

# Register your models here.
@admin.register(DeviceMaster)
class DeviceMaster(admin.ModelAdmin):
    list_display = [field.name for field in DeviceMaster._meta.fields]

@admin.register(AttendenceMonthMaster)
class AttendenceMonthMaster(admin.ModelAdmin):
    list_display = [field.name for field in AttendenceMonthMaster._meta.fields]

@admin.register(JoiningApprovedLeave)
class JoiningApprovedLeave(admin.ModelAdmin):
    list_display = [field.name for field in JoiningApprovedLeave._meta.fields]
    search_fields = ('employee__username',)

@admin.register(Attendance)
class Attendance(admin.ModelAdmin):
    list_display = [field.name for field in Attendance._meta.fields]
    search_fields = ('employee__username',)

@admin.register(AttendanceLog)
class AttendanceLog(admin.ModelAdmin):
    list_display = [field.name for field in AttendanceLog._meta.fields]

@admin.register(AttendanceApprovalRequest)
class AttendanceApprovalRequest(admin.ModelAdmin):
    list_display = [field.name for field in AttendanceApprovalRequest._meta.fields]
    search_fields = ('attendance__id',)

@admin.register(AttandanceApprovalDocuments)
class AttandanceApprovalDocuments(admin.ModelAdmin):
    list_display = [field.name for field in AttandanceApprovalDocuments._meta.fields]

@admin.register(EmployeeAdvanceLeaves)
class EmployeeAdvanceLeaves(admin.ModelAdmin):
    list_display = [field.name for field in EmployeeAdvanceLeaves._meta.fields]
    search_fields = ('employee__username',)

@admin.register(AttandancePerDayDocuments)
class AttandancePerDayDocuments(admin.ModelAdmin):
    list_display = [field.name for field in AttandancePerDayDocuments._meta.fields]

@admin.register(VehicleTypeMaster)
class VehicleTypeMaster(admin.ModelAdmin):
    list_display = [field.name for field in VehicleTypeMaster._meta.fields]

@admin.register(AttendenceSaturdayOffMaster)
class AttendenceSaturdayOffMaster(admin.ModelAdmin):
    list_display = [field.name for field in AttendenceSaturdayOffMaster._meta.fields]
    search_fields = ('employee__username',)

@admin.register(AttendenceSaturdayOffLogMaster)
class AttendenceSaturdayOffLogMaster(admin.ModelAdmin):
    list_display = [field.name for field in AttendenceSaturdayOffLogMaster._meta.fields]
    search_fields = ('employee__username',)

@admin.register(AttendanceSpecialdayMaster)
class AttendanceSpecialdayMaster(admin.ModelAdmin):
    list_display = [field.name for field in AttendanceSpecialdayMaster._meta.fields]

@admin.register(AttendenceAction)
class AttendenceAction(admin.ModelAdmin):
    list_display = [field.name for field in AttendenceAction._meta.fields]

