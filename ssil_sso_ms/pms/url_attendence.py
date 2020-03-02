from pms import views
from django.conf.urls import url, include
from rest_framework import routers
from django.urls import path
from rest_framework.authtoken import views as rest_framework_views

urlpatterns = [
#   :::::::::::::::::  ATTENDENCE ::::::::::::::::::::#
    # path('attandance_login/', views.AttendanceLoginView.as_view()),
    path('attandance_logout/<pk>/', views.AttendanceLogOutView.as_view()),
    path('attandance_add/', views.AttendanceAddView.as_view()),
    # path('attandance_add_new/', views.AttendanceNewAddView.as_view()),
    #modification 09/09/2019
    # path('attandance_offline_add/', views.AttendanceOfflineAddView.as_view()),
    path('attandance_list_by_employee/<employee_id>/', views.AttendanceListByEmployeeView.as_view()),
    path('attandance_edit/<pk>/', views.AttendanceEditView.as_view()),
    path('attandance_approval_list/', views.AttendanceApprovalList.as_view()),
    path('attandance_approval_log_list/', views.AttandanceAllDetailsListView.as_view()),

    # for permisson label added by @Rupam
    path('attandance_approval_log_list_by_permisson/', views.AttandanceAllDetailsListByPermissonView.as_view()),

    # for permisson label added by @Rupam
    path('attandance_approval_list_with_only_deviation_by_permisson/', views.AttandanceListWithOnlyDeviationByPermissonView.as_view()),

    #::::::::::::::::: PmsAttandanceLog ::::::::::::::::::::#
    path('attandance_log_add/', views.AttandanceLogAddView.as_view()),
    path('attandance_log_multiple_add/', views.AttandanceLogMultipleAddView.as_view()),
    path('attandance_log_edit/<pk>/', views.AttendanceLogEditView.as_view()),
    path('attandance_log_approval_edit/<pk>/', views.AttandanceLogApprovalEditView.as_view()),

    #:::::::::::::::::  PmsLeaves ::::::::::::::::::::#
    path('advance_leave_apply/', views.AdvanceLeaveAddView.as_view()),
    path('advance_leave_apply_edit/<pk>/', views.AdvanceLeaveEditView.as_view()),
    path('leave_list_by_employee/<employee_id>/', views.LeaveListByEmployeeView.as_view()),

    # --------------------------- Pms Attandance Deviation------------------------------------
    path('attandance_deviation_justification/<pk>/', views.AttandanceDeviationJustificationEditView.as_view()),
    path('attandance_deviation_approval/<pk>/', views.AttandanceDeviationApprovaEditView.as_view()),
    path('attandance_deviation_by_attandance_list/', views.AttandanceDeviationByAttandanceListView.as_view()),

    #:::::::::::::::::::::: PMS EMPLOYEE CONVEYANCE:::::::::::::::::::::::::::#
    path('employee_conveyance_add/', views.EmployeeConveyanceAddView.as_view()),
    path('employee_conveyance_edit/<pk>/', views.EmployeeConveyanceEditView.as_view()),
    path('employee_conveyance_list/', views.EmployeeConveyanceListView.as_view()),

    #:::::::::::::::::::::::::::::::::::PMS EMPLOYEE FOODING:::::::::::::::::::::::::::::::#
    path('employee_fooding_add/', views.EmployeeFoodingAddView.as_view()),
    path('attandance_approval_log_list_with_fooding/', views.AttandanceAllDetailsListWithFoodingView.as_view()),

    #:::::::::::::::::::::::::::::::: ATTENDENCE LIST EXPORT ::::::::::::::::::::::::::::::#
    path('attandance_list_export/', views.AttandanceListExportView.as_view()),

    
    #Added By Rupam Hazra on [10-01-2020] line number 58
    
    path('attandance_update_logout_time_failed_on_logout/<pk>/', views.AttendanceUpdateLogOutTimeFailedOnLogoutView.as_view()),
    path('attandance_log_multiple_by_thread_add/', views.AttandanceLogMultipleByThreadAddView.as_view()),
]
