from django.urls import path
from etask import views
from django.conf.urls import url, include
from rest_framework.authtoken import views as rest_framework_views

urlpatterns = [
    #::::::::::::::::::::::::: TASK ADD :::::::::::::::::::::::::::#
    # path('etask_type_add/',views.EtaskTypeAddView.as_view()),
    path('etask_task_add/',views.EtaskTaskAddView.as_view()),
    path('etask_task_details/<pk>/',views.EtaskTaskRepostView.as_view()),
    path('etask_task_edit/<pk>/',views.EtaskTaskEditView.as_view()),
    path('etask_task_delete/<pk>/',views.EtaskTaskDeleteView.as_view()),
    path('etask_parent_task_list/',views.EtaskParentTaskListView.as_view()),
    path('etask_my_task_list/',views.EtaskMyTaskListView.as_view()),  ## Modified by manas ##
    path('etask_completed_task_list/',views.EtaskCompletedTaskListView.as_view()), ## Modified by manas ##
    path('etask_closed_task_list/',views.EtaskClosedTaskListView.as_view()),  ## Modified by manas ##
    path('etask_overdue_task_list/',views.EtaskOverdueTaskListView.as_view()), ## Modified by manas ##
    path('etask_task_list/',views.EtasktaskListView.as_view()),
    path('etask_task_status_list/',views.EtaskTaskStatusListView.as_view()),
    path('e_task_all_task_list/',views.ETaskAllTasklist.as_view()),#Modified by koushik##
    path('e_task_upcoming_completion_list/',views.ETaskUpcomingCompletionListView.as_view()), ## Created by manas ##
    path('etask_task_cc_list/',views.EtaskTaskCCListview.as_view()), ## Created by manas ##
    path('etask_task_transffered_list/',views.EtaskTaskTransferredListview.as_view()), ## Created by manas ##
    path('e_task_task_complete/<pk>/',views.EtaskTaskCompleteView.as_view()), ## Created by manas ##
    path('etask_my_task_todays_planner_list/',views.EtaskMyTaskTodaysPlannerListView.as_view()),  ## Modified by manas ##   
    path('etask_end_date_extension_request/<pk>/',views.EtaskEndDateExtensionRequestView.as_view()),
    path('etask_extensions_list_for_rh_or_hod/',views.EtaskExtensionsListView.as_view()),   
    path('etask_extensions_reject/<pk>/',views.EtaskExtensionsRejectView.as_view()),  
    path('etask_task_date_extended/<pk>/',views.EtaskTaskDateExtendedView.as_view()),  ## Modified by manas ##        
    path('etask_task_date_extended_with_delay/<pk>/',views.EtaskTaskDateExtendedWithDelayView.as_view()),  ## Modified by manas ##    
    path('etask_task_reopen_and_extend_with_delay/<pk>/',views.EtaskTaskReopenAndExtendWithDelayView.as_view()),
    path('etask_task_start_date_shift/<pk>/',views.EtaskTaskStartDateShiftView.as_view()),    
    path('etask_all_type_task_count/',views.EtaskAllTypeTaskCountView.as_view()),  ## Modified by manas ##        
    path('etask_getdetails_list/',views.ETaskGetDetailForCommentListView.as_view()),

    #::::::::::::::::::::::::: TASK COMMENTS:::::::::::::::::::::::::::#
    path('e_task_comments/',views.ETaskCommentsView.as_view()), ## Created by manas ##
    path('e_task_comments_viewers/',views.ETaskCommentsViewersView.as_view()),
    path('e_task_unread_comments/<user_id>/',views.ETaskUnreadCommentsView.as_view()),
    path('e_task_comments_advance_attachment_add/',views.ETaskCommentsAdvanceAttachmentAddView.as_view()), ## Created by manas ##
    path('e_task_comments_list/',views.EtasCommentsListView.as_view()), ## Created by manas ##
      
    #::::::::::::::::::::::::: Followup COMMENTS:::::::::::::::::::::::::::#
    path('e_task_followup_comments/',views.ETaskFollowupCommentsView.as_view()), ## Created by manas ##
    path('e_task_followup_comments_advance_attachment_add/',views.ETaskFollowupCommentsAdvanceAttachmentAddView.as_view()), ## Created by manas ##
    path('e_task_followup_comments_list/',views.EtasFollowupCommentsListView.as_view()), ## Created by manas ##

    #::::::::::::::::::::::::: TASK SUB ASSIGN:::::::::::::::::::::::::::#
    path('e_task_sub_assign/<pk>/',views.ETaskSubAssignView.as_view()), ## Modified by manas ##
    
    #::::::::::::::::::::::::: Follow UP:::::::::::::::::::::::::::#
    path('e_task_add_new_follow_up/',views.EtaskAddFollowUpView.as_view()),
    path('e_task_follow_up_list/<user_id>/',views.EtaskFollowUpListView.as_view()),
    path('e_task_todays_follow_up_list/<user_id>/',views.EtaskTodaysFollowUpListView.as_view()),
    path('e_task_upcoming_follow_up_list/<user_id>/',views.EtaskUpcomingFollowUpListView.as_view()),
    path('e_task_overdue_follow_up_list/<user_id>/',views.EtaskOverdueFollowUpListView.as_view()),
    path('e_task_follow_up_complete/<pk>/',views.EtaskFollowUpCompleteView.as_view()),
    path('e_task_follow_up_delete/<pk>/',views.EtaskFollowUpDeleteView.as_view()),
    path('e_task_follow_up_edit/<pk>/',views.EtaskFollowUpEditView.as_view()),
    path('e_task_follow_up_reschedule/<pk>/',views.EtaskFollowUpRescheduleView.as_view()),
    path('e_task_assign_to_list/',views.ETaskAssignToListView.as_view()),
    path('e_task_sub_assign_to_list/',views.ETaskSubAssignToListView.as_view()),

    #:::::::::::::::::::::::: Send Mail For ETask Comments ::::::::::::::::::::::::::#
    # path('e_task_all_mail_one_time_send/',views.ETaskAllMailOneTimeSendView.as_view()),

    #::::::::::::::::::::::::: APPOINTMENTS COMMENTS:::::::::::::::::::::::::::#
    path('e_task_appointment_add/',views.ETaskAppointmentAddView.as_view()),
    path('e_task_appointment_edit/<pk>/',views.ETaskAppointmentUpdateView.as_view()),
    path('e_task_appointment_comments/',views.ETaskAppointmentCommentsView.as_view()), ## Created by manas ##
    path('e_task_appointment_comments_advance_attachment_add/',views.ETaskAppointmentCommentsAdvanceAttachmentAddView.as_view()), ## Created by manas ##
    path('e_task_appointment_comments_list/',views.EtaskAppointmentCommentsListView.as_view()), ## Created by manas ##
    path('e_task_appointment_calander/',views.ETaskAppointmentCalanderView.as_view()),
    path('e_task_appointment_calander_weekly/',views.ETaskAppointmentCalanderWeeklyView.as_view()),
    path('e_task_allcomment/',views.ETaskAllCommentListView.as_view()),
    path('e_task_allcomment_documents/',views.ETaskAllCommentDocumentListView.as_view()),
    path('e_task_appointment_cancel/<pk>/',views.ETaskAppointmentCancelView.as_view()),

    #::::::::::::::::::::::::: REPORTING :::::::::::::::::::::::::::#
    path('e_task_reports/',views.ETaskReportsView.as_view()),#::Created by koushik::#
    path('etask_upcoming_reporting_list/',views.EtaskUpcommingReportingListView.as_view()), ## Created by manas ##
    path('etask_reporting_date_reported/<pk>/',views.EtaskReportingDateReportedView.as_view()), ## Created by manas ##
    path('etask_reporting_date_shift/',views.EtaskReportingDateShiftView.as_view()), ## Created by manas ##
    
    #::::::::::::::::::::::::: ADMIN REPORT :::::::::::::::::::::::::::#
    path('e_task_admin_task_report/',views.ETaskAdminTaskReportView.as_view()), #Created by koushik##
    path('e_task_admin_appointment_report/',views.ETaskAdminAppointmentReportView.as_view()), #Created by koushik##

    #::::::::::::::::::::::::: TEAM :::::::::::::::::::::::::::#
    path('e_task_team_ongoing_task/',views.ETaskTeamOngoingTaskView.as_view()),#Created by koushik## ## Modfied By Manas Paul##
    path('e_task_team_completed_task/',views.ETaskTeamCompletedTaskView.as_view()),#Created by koushik##
    path('e_task_team_closed_task/',views.ETaskTeamClosedTaskView.as_view()),#Created by koushik##
    path('e_task_closures_task_list/',views.ETaskClosuresTaskListView.as_view()),
    path('e_task_team_overdue_task/',views.ETaskTeamOverdueTaskView.as_view()),#Created by koushik##
    path('e_task_task_close/<pk>/',views.EtaskTaskCloseView.as_view()), ## Created by koushik ##
    path('e_task_mass_task_close/',views.ETaskMassTaskCloseView.as_view()),

    path('employee_list_without_details_for_e_task/',views.EmployeeListWithoutDetailsForETaskView.as_view()),

    #::::::::::::::::::::::: TODAYS PLANNING :::::::::::::::::::::::#
    path('e_task_today_appointment_list/',views.EtaskTodayAppointmentListView.as_view()),
    path('e_task_upcoming_appointment_list/',views.EtaskUpcomingAppointmentListView.as_view()),

    #::::::::::::::::UPCOMING TASK ALONG WITH TEAM:::::::::::::::::::::::::::::::::::::#
    path('upcoming_task_along_with_team/',views.UpcomingTaskAlongWithTeamView.as_view()),
    path('upcoming_task_per_user/<user_id>/',views.UpcomingTaskPerUserView.as_view()),

    path('upcoming_task_reporting_along_with_team/',views.UpcomingTaskReportingAlongWithTeamView.as_view()),
    path('upcoming_task_reporting_per_user/<user_id>/',views.UpcomingTaskReportingPerUserView.as_view()),
    
    #::::::::::::::::TODAYS TASK ALONG WITH TEAM:::::::::::::::::::::::::::::::::::::#
    path('todays_task_along_with_team/',views.TodaysTaskAlongWithTeamView.as_view()),
    path('todays_task_reporting_along_with_team/',views.TodaysTaskReportingAlongWithTeamView.as_view()),

    #::::::::::::::::DEFAULT REPORTING DATES:::::::::::::::::::::::::::::::::::::#
    path('e_task_default_reporting_dates_add/',views.ETaskDefaultReportingDatesView.as_view()),
    path('e_task_another_default_reporting_dates_add/',views.ETaskAnotherDefaultReportingDatesView.as_view()),
    path('e_task_default_reporting_dates_update/<pk>/',views.ETaskDefaultReportingDatesUpdateView.as_view()),
    path('e_task_default_reporting_dates_delete/<pk>/',views.ETaskDefaultReportingDatesDeleteView.as_view()),

    #:::::::::::::::::::::::::::::::::::::::::::  N E W  ::::::::::::::::::::::::::::::::::::::::::::#
    #================================================================================================#
    #:::::::::::::::::::::::::::::::::::::: TASK LIST -NEW ::::::::::::::::::::::::::::::::::::::::::::#
    path('today_task_details_per_user/<user_id>/',views.TodayTaskDetailsPerUserView.as_view()),
    path('upcoming_task_details_per_user/<user_id>/',views.UpcomingTaskDetailsPerUserView.as_view()),
    path('overdue_task_details_per_user/<user_id>/',views.OverdueTaskDetailsPerUserView.as_view()),
    path('closed_task_details_per_user/<user_id>/',views.ClosedTaskDetailsPerUserView.as_view()),
    path('e_task_todays_planner_count/<user_id>/',views.ETaskTodaysPlannerCountView.as_view()),

    #:::::::::::::::::::::::::::::::::::::: REPORTING ::::::::::::::::::::::::::::::::::::::::::::::::#
    path('today_reporting_details_per_user/<user_id>/',views.TodayReportingDetailsPerUserView.as_view()),
    path('upcoming_reporting_details_per_user/<user_id>/',views.UpcomingReportingDetailsPerUserView.as_view()),
    path('overdue_reporting_details_per_user/<user_id>/',views.OverdueReportingDetailsPerUserView.as_view()),
    path('today_reporting_mark_date_reported/<pk>/',views.TodayReportingMarkDateReportedView.as_view()),

    #:::::::::::::::::::::::::::::::::::::: APPOINMENT ::::::::::::::::::::::::::::::::::::::::::::::::#
    path('today_appointment_details_per_user/<user_id>/',views.TodayAppointmenDetailsPerUserView.as_view()),
    path('upcoming_appointment_details_per_user/<user_id>/',views.UpcomingAppointmenDetailsPerUserView.as_view()),
    path('overdue_appointment_details_per_user/<user_id>/',views.OverdueAppointmenDetailsPerUserView.as_view()),
    path('closed_appointment_details_per_user/<user_id>/',views.ClosedAppointmenDetailsPerUserView.as_view()),
    path('today_appoinment_mark_completed/<pk>/',views.TodayAppoinmentMarkCompletedView.as_view()),

    #:::::::::::::::::::::::::::::::::::::: TASK TRANSFER ::::::::::::::::::::::::::::::::::::::::::::::::#
    path('e_task_mass_task_transfer/',views.ETaskMassTaskTransferView.as_view()),
    path('e_task_team_transfer_tasks_list/<user_id>/',views.ETaskTeamTransferTasksListView.as_view()),
    path('e_task_team_tasks_transferred_list/',views.ETaskTeamTasksTransferredListView.as_view()),

    #::::::::::::::::::::::::::::::::::::::::::::: COUNT ::::::::::::::::::::::::::::::::::::::::::::::::::::::#
    path('today_count_details_per_user/<user_id>/',views.TodayCountDetailsPerUserView.as_view()),
    path('upcoming_count_details_per_user/<user_id>/',views.UpcomingCountDetailsPerUserView.as_view()),
    path('overdue_count_details_per_user/<user_id>/',views.OverDueCountDetailsPerUserView.as_view()),
    path('closed_count_details_per_user/<user_id>/',views.ClosedCountDetailsPerUserView.as_view()),
    path('dashboard_count_details/',views.DashboardCountDetailsView.as_view()),

    #::::::::::::::::::::::::::::::::::::::::::::: PRINT PLANNER ::::::::::::::::::::::::::::::::::::::::::::::::::::::#
    path('today_tomorrow_upcoming_planner/',views.TodayTomorrowUpcomingPlannerView.as_view())

]