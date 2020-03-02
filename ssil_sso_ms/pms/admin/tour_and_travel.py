from django.contrib import admin
from pms.models.module_tour_and_travel import *


@admin.register(PmsTourAndTravelExpenseMaster)
class PmsTourAndTravelExpenseMaster(admin.ModelAdmin):
    list_display = [field.name for field in PmsTourAndTravelExpenseMaster._meta.fields]

@admin.register(PmsTourAndTravelEmployeeDailyExpenses)
class PmsTourAndTravelEmployeeDailyExpenses(admin.ModelAdmin):
    list_display = [field.name for field in PmsTourAndTravelEmployeeDailyExpenses._meta.fields]

@admin.register(PmsTourAndTravelVendorOrEmployeeDetails)
class PmsTourAndTravelVendorOrEmployeeDetails(admin.ModelAdmin):
    list_display = [field.name for field in PmsTourAndTravelVendorOrEmployeeDetails._meta.fields]


@admin.register(PmsTourAndTravelBillReceived)
class PmsTourAndTravelBillReceived(admin.ModelAdmin):
    list_display = [field.name for field in PmsTourAndTravelBillReceived._meta.fields]

@admin.register(PmsTourAndTravelWorkSheetFlightBookingQuotation)
class PmsTourAndTravelWorkSheetFlightBookingQuotation(admin.ModelAdmin):
    list_display = [field.name for field in PmsTourAndTravelWorkSheetFlightBookingQuotation._meta.fields]

@admin.register(PmsTourAndTravelFinalBookingDetails)
class PmsTourAndTravelFinalBookingDetails(admin.ModelAdmin):
    list_display = [field.name for field in PmsTourAndTravelFinalBookingDetails._meta.fields]








