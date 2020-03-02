from eticket import views
from django.conf.urls import url, include
from rest_framework import routers
from django.urls import path
from rest_framework.authtoken import views as rest_framework_views

'''
    This module prepared by @@ Rupam Hazra. Any kind of issues occurred, ask me first !!!
    Version - 1.0
'''


urlpatterns = [

    

    # Reporting Head of Eticket 
    path('eticket_reporting_head_add/', views.EticketReportingHeadAddView.as_view()),
    path('eticket_reporting_head_edit/<pk>/', views.EticketReportingHeadEditView.as_view()),

    

    # Ticket Section
    path('eticket_ticket_subject_list_by_department_add/', views.EticketTicketSubjectListByDepartmentAddView.as_view()),
    path('eticket_ticket_add/', views.EticketTicketAddView.as_view()),
    path('eticket_ticket_document_add/', views.EticketTicketDocumentAddView.as_view()),
    path('eticket_ticket_raised_by_me_list/', views.EticketTicketRaisedByMeListView.as_view()),
    path('eticket_ticket_assigned_to_me_list/', views.EticketTicketAssignedToMeListView.as_view()),

    # Ticket Change status
    path('eticket_ticket_change_status/<pk>/', views.EticketTicketChangeStatusView.as_view()),

    # Ticket Change Person Responsible
    path('eticket_ticket_change_person_responsible/<pk>/', views.EticketTicketChangePersonResponsibleView.as_view()),
    
    # Ticket Comment Section
    path('eticket_ticket_comment_add/', views.EticketTicketCommentAddView.as_view()),

    # Ticket List according to status
    path('eticket_ticket_list/<status>/', views.EticketTicketListByStatusView.as_view()),

    # Ticket subject wise department
    path('eticket_ticket_subject_list_by_department/<department_id>/', views.EticketTicketSubjectListByDepartmentView.as_view()),

    path('eticket_user_list_under_login_user/',views.EticketUserListUnderLoginUserView.as_view()),


]