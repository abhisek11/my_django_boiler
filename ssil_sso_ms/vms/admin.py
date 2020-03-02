from django.contrib import admin
from vms.models import *

# Register your models here.

@admin.register(VmsFloorDetailsMaster)
class VmsFloorDetailsMaster(admin.ModelAdmin):
    list_display = [field.name for field in VmsFloorDetailsMaster._meta.fields]

@admin.register(VmsCardDetailsMaster)
class VmsCardDetailsMaster(admin.ModelAdmin):
    list_display = [field.name for field in VmsCardDetailsMaster._meta.fields]

@admin.register(VmsVisitorDetails)
class VmsVisitorDetails(admin.ModelAdmin):
    list_display = [field.name for field in VmsVisitorDetails._meta.fields]

@admin.register(VmsVisit)
class VmsVisit(admin.ModelAdmin):
    list_display = [field.name for field in VmsVisit._meta.fields]

# @admin.register(VmsEmployeeDetailsMaster)
# class VmsEmployeeDetailsMaster(admin.ModelAdmin):
#     list_display = [field.name for field in VmsEmployeeDetailsMaster._meta.fields]

@admin.register(VmsVisitorPunching)
class VmsVisitorPunching(admin.ModelAdmin):
    list_display = [field.name for field in VmsVisitorPunching._meta.fields]

@admin.register(VmsEmployeeVisitor)
class VmsEmployeeVisitor(admin.ModelAdmin):
    list_display = [field.name for field in VmsEmployeeVisitor._meta.fields]

@admin.register(VmsVisitorTypeMaster)
class VmsVisitorTypeMaster(admin.ModelAdmin):
    list_display = [field.name for field in VmsVisitorTypeMaster._meta.fields]

@admin.register(VmsFloorVisitor)
class VmsFloorVisitor(admin.ModelAdmin):
    list_display = [field.name for field in VmsFloorVisitor._meta.fields]

@admin.register(VmsCardAndFloorMapping)
class VmsCardAndFloorMapping(admin.ModelAdmin):
    list_display = [field.name for field in VmsCardAndFloorMapping._meta.fields]