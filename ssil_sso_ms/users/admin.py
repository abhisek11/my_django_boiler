from django.contrib import admin
from users.models import *
from core.models import *
# Register your models here.

@admin.register(TCoreUserDetail)
class TCoreUserDetail(admin.ModelAdmin):
    list_display = ('id','cu_user','cu_phone_no','cu_alt_email_id','company','department',
    'cu_punch_id','cu_emp_code','sap_personnel_no','joining_date','hod','reporting_head')
    search_fields = ('cu_user__username','cu_phone_no','cu_alt_email_id','cu_punch_id','cu_emp_code',
    'company__coc_name')
    



@admin.register(LoginLogoutLoggedTable)
class LoginLogoutLoggedTable(admin.ModelAdmin):
    list_display = [field.name for field in LoginLogoutLoggedTable._meta.fields]
    search_fields = ('user__username', 'ip_address', 'browser_name','os_name')