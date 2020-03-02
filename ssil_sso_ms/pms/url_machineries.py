from pms import views
from django.conf.urls import url, include
from rest_framework import routers
from django.urls import path
from rest_framework.authtoken import views as rest_framework_views

urlpatterns = [

    #:::::::::::::::::  MECHINARY WORKING CATEGORY ::::::::::::::::::::#
    path('machineries_working_category_add/', views.MachineriesWorkingCategoryAddView.as_view()),
    path('machineries_working_category_edit/<pk>/', views.MachineriesWorkingCategoryEditView.as_view()),
    path('machineries_working_category_delete/<pk>/', views.MachineriesWorkingCategoryDeleteView.as_view()),

    #:::::::::::::::::  MECHINARY ::::::::::::::::::::#
    path('machineries_add/', views.MachineriesAddView.as_view()),
    path('machineries_edit/<pk>/', views.MachineriesEditView.as_view()),
    path('machineries_list/', views.MachineriesListDetailsView.as_view()),
    path('machineries_wp_list/', views.MachineriesListWPDetailsView.as_view()),
    path('machineries_list_for_report/', views.MachineriesListForReportView.as_view()),
    path('machineries_list_filter_for_report/', views.MachineriesListFilterForReportView.as_view()),
    path('machineries_delete/<pk>/', views.MachineriesDeleteView.as_view()),
    path('machineries_details_document_add/', views.MachineriesDetailsDocumentAddView.as_view()),
    path('machineries_details_document_edit/<pk>/', views.MachineriesDetailsDocumentEditView.as_view()),
    path('machineries_details_document_delete/<pk>/', views.MachineriesDetailsDocumentDeleteView.as_view()),
    path('machineries_details_document_list/<equipment_id>/', views.MachineriesDetailsDocumentListView.as_view()),
    path('machinary_rented_type_master_add/', views.MachinaryRentedTypeMasterAddView.as_view()),
    path('machinary_rented_type_master_edit/<pk>/', views.MachinaryRentedTypeMasterEditView.as_view()),
    path('machinary_rented_type_master_delete/<pk>/', views.MachinaryRentedTypeMasterDeleteView.as_view()),
    #:::::::::::::::::  MECHINARY REPORTS ::::::::::::::::::::#
    path('machineries_report_add/', views.MachineriesReportAddView.as_view()),
    path('machineries_report_edit/<pk>/', views.MachineriesReportEditView.as_view()),
]