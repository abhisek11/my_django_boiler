from django.contrib import admin
from eticket.models import *

# Register your models here.

@admin.register(ETICKETReportingHead)
class ETICKETReportingHead(admin.ModelAdmin):
    list_display = [field.name for field in ETICKETReportingHead._meta.fields]

@admin.register(ETICKETSubjectOfDepartment)
class ETICKETSubjectOfDepartment(admin.ModelAdmin):
    list_display = [field.name for field in ETICKETSubjectOfDepartment._meta.fields]

@admin.register(ETICKETTicket)
class ETICKETTicket(admin.ModelAdmin):
    list_display = [field.name for field in ETICKETTicket._meta.fields]

@admin.register(ETICKETTicketDoc)
class ETICKETTicketDoc(admin.ModelAdmin):
    list_display = [field.name for field in ETICKETTicketDoc._meta.fields]

@admin.register(ETICKETTicketComment)
class ETICKETTicketComment(admin.ModelAdmin):
    list_display = [field.name for field in ETICKETTicketComment._meta.fields]


