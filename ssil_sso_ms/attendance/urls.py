from django.urls import path
from attendance import views
from django.conf.urls import url, include
from rest_framework.authtoken import views as rest_framework_views

'''
    attendance_file_upload ::- Daily upload from Excel File 
    attendance_file_upload_for_new_user ::- This is for new user attendence from Postman Hit with excel file
    attendance_file_upload_check_by_punch_from_old_data_base ::- This is for user attendence from 
    old database using Postman hit with date range,punch_ids
    attendance_user_attendance_upload_by_log_data ::- this is used to correct
    attendence using attendence log table with empids,last_date
'''


urlpatterns = [
    #:::::::::::::::::::::: DEVICE MASTER:::::::::::::::::::::::::::#
    path('punch_device_master_add/', views.DeviceMasterAddView.as_view()),
    path('punch_device_master_edit/<pk>/', views.DeviceMasterEditView.as_view()),
    path('punch_device_master_delete/<pk>/', views.DeviceMasterDeleteView.as_view()),

	#:::::::::::::::::::::: ATTENDENCE MONTH MASTER:::::::::::::::::::::::::::#
    path('attendence_month_master_add/', views.AttendenceMonthMasterAddView.as_view()),
    path('attendence_month_master_edit/<pk>/', views.AttendenceMonthMasterEditView.as_view()),
    path('attendence_month_master_delete/<pk>/', views.AttendenceMonthMasterDeleteView.as_view()),
    
    path('attendence_approval_request/<pk>/',views.AttendenceApprovalRequestView.as_view()),

    #:::::::::::::::::::::::::::ATTENDANCE DOCUMENTS UPLOAD::::::::::::::::::::::::::::#
    
    path('attendance_file_upload/', views.AttendanceFileUpload.as_view()), #After modifications
    path('attendance_file_upload_for_new_user/', views.AttendanceFileUploadForNewUser.as_view()),
    
    path('attendance_file_upload_check_by_punch_from_old_data_base/', views.AttendanceFileUploadCheckPunchOldData.as_view()),
    path('attendance_user_attendance_upload_by_log_data/', views.AttendanceUserAttendanceUploadByLogData.as_view()),

    path('attendance_file_upload_old_version/', views.AttendanceFileUploadOldVersion.as_view()),
    path('attendance_file_upload_check/', views.AttendanceFileUploadCheck.as_view()),

    path('attendence_per_day_document/',views.AttendencePerDayDocumentAddView.as_view()),
    # path('attendence_per_day_document/',views.AttendencePerDayDocumentAddView.as_view()),
    # path('attendence_joining_approved_leave_add/',views.AttendenceJoiningApprovedLeaveAddView.as_view()),
    path('attendance_grace_leave_list_first/',views.AttendanceGraceLeaveListView.as_view()),
    path('attendance_grace_leave_list_first_modified/',views.AttendanceGraceLeaveListModifiedView.as_view()),

    path('attendance_late_conveyance_apply/<pk>/',views.AttendanceLateConveyanceApplyView.as_view()),
    path('attendance_conveyance_approval_list/',views.AttendanceConveyanceApprovalListView.as_view()),
    path('attendance_conveyance_report_list/',views.AttendanceConveyanceAfterApprovalListView.as_view()),
    path('attendance_summary_list/',views.AttendanceSummaryListView.as_view()),
    path('attendance_daily_list/',views.AttendanceDailyListView.as_view()),

    #:::::::::::::::::::::::::::ATTENDANCE ADVANCE LEAVE::::::::::::::::::::::::::::#
    path('attendance_advance_leave_list/',views.AttendanceAdvanceLeaveListView.as_view()),
    path('attendance_advance_leave_report/',views.AttendanceAdvanceLeaveReportView.as_view()),
    path('attendance_advance_leave_add/',views.AttendanceAdvanceLeaveAddView.as_view()),
    path('admin_attendance_advance_leave_pending_list/',views.AdminAttendanceAdvanceLeavePendingListView.as_view()),
    path('admin_attendance_advance_leave_approval/',views.AdminAttendanceAdvanceLeaveApprovalView.as_view()), 


    path('e_task_attendance_approval_list/',views.ETaskAttendanceApprovalList.as_view()),
    path('e_task_attendance_approval_grace_list/',views.ETaskAttendanceApprovaGracelList.as_view()),
    path('e_task_attendance_approval_withoout_grace_list/',views.ETaskAttendanceApprovaWithoutGracelList.as_view()),
    path('e_task_attendance_approval/',views.ETaskAttendanceApprovalView.as_view()),
    path('e_task_attendance_approval_modify/',views.ETaskAttendanceApprovalModifyView.as_view()),
    path('attendance_approval_report/',views.AttendanceApprovalReportView.as_view()),
    
    path('attendance_vehicle_type_master_add/',views.AttendanceVehicleTypeMasterAddView.as_view()),
    path('attendance_vehicle_type_master_edit/<pk>/',views.AttendanceVehicleTypeMasterEditView.as_view()),
    path('attendance_vehicle_type_master_delete/<pk>/',views.AttendanceVehicleTypeMasterDeleteView.as_view()),

    path('attendance_admin_summary_list/',views.AttendanceAdminSummaryListView.as_view()),

    path('attendance_admin_daily_list/',views.AttendanceAdminDailyListView.as_view()),

    path('attendance_leave_approval_list/',views.AttendanceLeaveApprovalList.as_view()),

    path('attendance_admin_mispunch_checker/',views.AttendanceAdminMispunchCheckerView.as_view()),#F-Complete
    path('attendance_admin_mispunch_checker_csv_report/',views.AttendanceAdminMispunchCheckerCSVReportView.as_view()),

    
    path('attendance_request_free_by_hr_list/',views.AttandanceRequestFreeByHRListView.as_view()),
    path('attendance_monthly_hr_list/',views.AttendanceMonthlyHRListView.as_view()),
    path('attendance_monthly_hr_summary_list/',views.AttendanceMonthlyHRSummaryListView.as_view()),#F-Complete
    path('attendance_grace_leave_list_for_hr_modified/',views.AttendanceGraceLeaveListForHRModifiedView.as_view()),#F-Complete
    #:::::::::::::::::::::::::::ATTENDANCE SPECIALDAY MASTER::::::::::::::::::::::::::::#
    path('attendence_special_day_master_add/', views.AttendanceSpecialdayMasterAddView.as_view()),
    path('attendence_special_day_master_edit/<pk>/', views.AttendanceSpecialdayMasterEditView.as_view()),
    path('attendence_special_day_master_delete/<pk>/', views.AttendanceSpecialdayMasterDeleteView.as_view()),
    path('attendance_employee_report/',views.AttendanceEmployeeReportView.as_view()),

    path('attendence_logs/',views.logListView.as_view()),

    #::::::::::::::::::::::::::::::::::::::: Report :::::::::::::::::::::::::::::::::::::::#
    path('attendance_admin_od_mis_report/',views.AttandanceAdminOdMsiReportView.as_view()),
    path('attendance_admin_od_mis_report_details/',views.AttandanceAdminOdMsiReportDetailsView.as_view()),
    path('attendance_admin_sap_report/',views.AttandanceAdminSAPReportView.as_view()),

    path('attendance_user_leave_report_till_date/',views.AttandanceUserLeaveReportTillDateView.as_view()),

    path('attendance_new_users_joining_leave_calculate_update/', views.AttendanceNewUsersJoiningLeaveCalculation.as_view()),

    ################################## cron testing api ##########################################
    path('attendance_user_cron_mail_for_pending_testapi/', views.AttendanceUserCronMailForPending.as_view()),
    path('attendance_user_cron_mail_for_pending_roh_testapi/', views.AttendanceUserCronMailForPendingRoh.as_view()),
    
    # Corn API
    path('attendance_user_cron_lock_testapi/', views.AttendanceUserCronLock.as_view()),
    
    path('attendance_user_six_day_leave_checking/', views.AttendanceUserSixDayLeaveCheck.as_view()),

    # Dependent on celery and ($ celery -A SSIL_SSO_MS worker -l info) need to be executed
    path('email_sms_alert_for_request_approval/', views.EmailSMSAlertForRequestApproval.as_view()),
    
    
    #query print api 
    path('query_print/',views.QueryPrint.as_view()),

    # Added By Rupam For get user length or users for testing purpose (attendence cron)
    path('attendance_users/', views.AttendanceUsers.as_view()),

]