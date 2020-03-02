from django.urls import path
from vms import views
from django.conf.urls import url, include
from rest_framework.authtoken import views as rest_framework_views


urlpatterns = [
    #::::::::::::::::::::::::::::: VMS FLOOR DETAILS MASTER:::::::::::::::::::::::::::#
    path('floor_details_master_add/', views.FloorDetailsMasterAddView.as_view()),
    path('floor_details_master_edit/<pk>/', views.FloorDetailsMasterEditView.as_view()),
    path('floor_details_master_delete/<pk>/', views.FloorDetailsMasterDeleteView.as_view()),

    #:::::::::::::::::::::: VMS CARD DETAILS MASTER:::::::::::::::::::::::::::#
    path('card_details_master_add/', views.CardDetailsMasterAddView.as_view()),
    path('card_details_master_edit/<pk>/', views.CardDetailsMasterEditView.as_view()),
    path('card_and_floor_edit/<pk>/',views.CardAndFloorEditView.as_view()),
    path('card_details_master_delete/<pk>/', views.CardDetailsMasterDeleteView.as_view()),
    path('available_cards_list/',views.AvailableCardsListView.as_view()),
    
    #:::::::::::::::::::::: VMS VISITOR DETAILS :::::::::::::::::::::::::::#
    path('visitor_details_add/', views.VisitorDetailsAddView.as_view()),
    path('visitor_details_list/', views.VisitorDetailsListView.as_view()),
    path('visitor_details_list_for_visitor_entry/', views.VisitorDetailsListForVisitorEntryView.as_view()),
    path('visitor_details_edit/<pk>/', views.VisitorDetailsEditView.as_view()),
    path('visitor_details_deactivate/<pk>/', views.VisitorDetailsDeactivateView.as_view()),
    path('organization_list/',views.OrganizationListView.as_view()),

    #:::::::::::::::::::::::::::::::: USER DETAILS ::::::::::::::::::::::::::::::::#
    path('user_details_list_wo_page/', views.UserDetailsListView.as_view()),

	#:::::::::::::::::::::: VMS VISITOR TYPE MASTER:::::::::::::::::::::::::::#
    path('vms_visitor_type_master_add/', views.VisitorTypeMasterAddView.as_view()),
    path('vms_visitor_type_master_edit/<pk>/', views.VisitorTypeMasterEditView.as_view()),
    path('vms_visitor_type_master_delete/<pk>/', views.VisitorTypeMasterDeleteView.as_view()),

    #:::::::::::::::::::::: VMS VISIT:::::::::::::::::::::::::::#
    path('vms_visit_add/', views.VisitAddView.as_view()),
    path('vms_visit_list/', views.VisitListView.as_view()),
    path('vms_visit_edit/<pk>/', views.VisitEditView.as_view()),
    path('vms_visit_logout/<pk>/', views.VisitLogoutView.as_view()),
    path('vms_visit_delete/<pk>/', views.VisitDeleteView.as_view()),
    path('vms_visit_list_by_visitor_id/<visitor_id>/', views.VisitListByVisitorIdView.as_view()),

    #::::::::::::::::::::::::::: DOCUMENTS UPLOAD::::::::::::::::::::::::::::#
    path('vms_xlsx_file_upload/', views.VmsFileUpload.as_view()),



]