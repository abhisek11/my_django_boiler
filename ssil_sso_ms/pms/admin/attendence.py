from django.contrib import admin
from pms.models.module_attendence import *

@admin.register(PmsAttendance)
class PmsAttendance(admin.ModelAdmin):
    list_display = [field.name for field in PmsAttendance._meta.fields]
    search_fields = ('employee__username','id','login_time','logout_time')

@admin.register(PmsAttandanceLog)
class PmsAttandanceLog(admin.ModelAdmin):
    list_display = [field.name for field in PmsAttandanceLog._meta.fields]
    search_fields = ('attandance__id',)

@admin.register(PmsAttandanceDeviation)
class PmsAttandanceDeviation(admin.ModelAdmin):
    list_display = [field.name for field in PmsAttandanceDeviation._meta.fields]

@admin.register(PmsEmployeeConveyance)
class PmsEmployeeConveyance(admin.ModelAdmin):
    list_display = [field.name for field in PmsEmployeeConveyance._meta.fields]

@admin.register(PmsEmployeeFooding)
class PmsEmployeeFooding(admin.ModelAdmin):
    list_display = [field.name for field in PmsEmployeeFooding._meta.fields]

@admin.register(PmsEmployeeLeaves)
class PmsEmployeeLeaves(admin.ModelAdmin):
    list_display = [field.name for field in PmsEmployeeLeaves._meta.fields]