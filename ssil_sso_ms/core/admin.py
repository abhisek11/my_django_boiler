from django.contrib import admin
from core.models import *

@admin.register(TCorePermissions)
class TCorePermissions(admin.ModelAdmin):
    list_display = [field.name for field in TCorePermissions._meta.fields]

@admin.register(TCoreModule)
class TCoreModule(admin.ModelAdmin):
    list_display = [field.name for field in TCoreModule._meta.fields]

@admin.register(TCoreOther)
class TCoreOther(admin.ModelAdmin):
    list_display = [field.name for field in TCoreOther._meta.fields]
    search_fields = ('cot_name',)

@admin.register(TCoreUnit)
class TCoreUnit(admin.ModelAdmin):
    list_display = [field.name for field in TCoreUnit._meta.fields]

@admin.register(TCoreRole)
class TCoreRole(admin.ModelAdmin):
    list_display = [field.name for field in TCoreRole._meta.fields]

@admin.register(TCoreDepartment)
class TCoreDepartment(admin.ModelAdmin):
    list_display = [field.name for field in TCoreDepartment._meta.fields]


@admin.register(TCoreDesignation)
class TCoreDesignation(admin.ModelAdmin):
    list_display = [field.name for field in TCoreDesignation._meta.fields]
    search_fields = ('cod_name',)


@admin.register(TCoreCompany)
class TCoreCompany(admin.ModelAdmin):
    list_display = [field.name for field in TCoreCompany._meta.fields]

@admin.register(TCoreGrade)
class TCoreGrade(admin.ModelAdmin):
    list_display = [field.name for field in TCoreGrade._meta.fields]
    search_fields = ('cg_name',)

@admin.register(TCoreState)
class TCoreState(admin.ModelAdmin):
    list_display = [field.name for field in TCoreState._meta.fields]
    search_fields = ('cg_name',)

@admin.register(TCoreSalaryType)
class TCoreSalaryType(admin.ModelAdmin):
    list_display = [field.name for field in TCoreSalaryType._meta.fields]
    search_fields = ('st_name',)