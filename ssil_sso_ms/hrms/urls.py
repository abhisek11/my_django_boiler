from django.urls import path
from hrms import views
from django.conf.urls import url, include
from rest_framework.authtoken import views as rest_framework_views


urlpatterns = [

#:::::::::::::::::::::: HRMS BENEFITS PROVIDED:::::::::::::::::::::::::::#
path('hrms_benefits_provided_add/', views.BenefitsProvidedAddView.as_view()),
path('hrms_benefits_provided_edit/<pk>/', views.BenefitsProvidedEditView.as_view()),
path('hrms_benefits_provided_delete/<pk>/', views.BenefitsProvidedDeleteView.as_view()),

#:::::::::::::::::::::: HRMS QUALIFICATION MASTER:::::::::::::::::::::::::::#
path('qualification_master_add/', views.QualificationMasterAddView.as_view()),
path('qualification_master_edit/<pk>/', views.QualificationMasterEditView.as_view()),
path('qualification_master_delete/<pk>/', views.QualificationMasterDeleteView.as_view()),

#:::::::::::::::::::::: HRMS EMPLOYEE:::::::::::::::::::::::::::#
path('employee_add/',views.EmployeeAddView.as_view()),
path('employee_edit/<pk>/',views.EmployeeEditView.as_view()),
path('employee_list/',views.EmployeeListView.as_view()),
path('employee_list_without_details/',views.EmployeeListWithoutDetailsView.as_view()),
path('employee_list_wo_pagination/',views.EmployeeListWOPaginationView.as_view()),
path('employee_list_for_hr/',views.EmployeeListForHrView.as_view()),
path('employee_lock_unlock/<pk>/', views.EmployeeActiveInactiveUserView.as_view()),

path('hrms_employee_document_add/',views.DocumentAddView.as_view()),
path('hrms_employee_document_delete/<pk>/',views.DocumentDeleteView.as_view()),

path('hrms_employee_profile_document_add/',views.HrmsEmployeeProfileDocumentAddView.as_view()),
path('hrms_employee_profile_document_delete/<pk>/',views.HrmsEmployeeProfileDocumentDeleteView.as_view()),

path('hrms_employee_academic_qualification_add/',views.HrmsEmployeeAcademicQualificationAddView.as_view()),
path('hrms_employee_academic_qualification_delete/<pk>/',views.HrmsEmployeeAcademicQualificationDeleteView.as_view()),

path('hrms_employee_academic_qualification_document_add/',views.HrmsEmployeeAcademicQualificationDocumentAddView.as_view()),
path('hrms_employee_academic_qualification_document_delete/<pk>/',views.HrmsEmployeeAcademicQualificationDocumentDeleteView.as_view()),

path('employee_add_by_csv_or_excel/',views.EmployeeAddByCSVorExcelView.as_view()),

#:::::::::::::::::::::: HRMS NEW REQUIREMENT:::::::::::::::::::::::::::#
path('hrms_new_requirement/',views.HrmsNewRequirementAddView.as_view()),

#:::::::::::::::::::::: HRMS INTERVIEW TYPE:::::::::::::::::::::::::::#
path('hrms_interview_type_add/', views.InterviewTypeAddView.as_view()),
path('hrms_interview_type_edit/<pk>/', views.InterviewTypeEditView.as_view()),
path('hrms_interview_type_delete/<pk>/', views.InterviewTypeDeleteView.as_view()),

#:::::::::::::::::::::: HRMS INTERVIEW LEVEL:::::::::::::::::::::::::::#
path('hrms_interview_level_add/', views.InterviewLevelAddView.as_view()),
path('hrms_interview_level_edit/<pk>/', views.InterviewLevelEditView.as_view()),
path('hrms_interview_level_delete/<pk>/', views.InterviewLevelDeleteView.as_view()),

#:::::::::::::::::::::: HRMS SCHEDULE INTERVIEW :::::::::::::::::::::::::::#
path('schedule_interview_add/',views.ScheduleInterviewAddView.as_view()),
path('reschedule_interview_add/',views.RescheduleInterviewAddView.as_view()),
path('interview_status_add/<pk>/',views.InterviewStatusAddView.as_view()),
path('interview_status_list/',views.InterviewStatusListView.as_view()),
path('candidature_update_data_edit/<pk>/', views.CandidatureUpdateEditView.as_view()),
path('candidature_level_approval/<pk>/', views.CandidatureApproveEditView.as_view()),
path('open_and_closed_requirement_list/',views.OpenAndClosedRequirementListView.as_view()),
path('upcoming_and_interview_history_list/',views.UpcomingAndInterviewHistoryListView.as_view()),

]