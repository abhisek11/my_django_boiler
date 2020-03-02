from pms import views
from django.conf.urls import url, include
from rest_framework import routers
from django.urls import path
from rest_framework.authtoken import views as rest_framework_views

urlpatterns = [
#:::::::::::::::::  PMS External Users Type ::::::::::::::::::::#
    path('external_users_type_add/', views.ExternalUsersTypeAddView.as_view()),
    path('external_users_type_edit/<pk>/', views.ExternalUsersTypeEditView.as_view()),
    path('external_users_type_delete/<pk>/', views.ExternalUsersTypeDeleteView.as_view()),

    #:::::::::::::::::  PmsExternalUsers ::::::::::::::::::::#
    path('external_users_add/', views.ExternalUsersAddView.as_view()),
    path('external_users_list/', views.ExternalUsersListView.as_view()),
    path('external_users_list_with_pagination/', views.ExternalUsersListWithPaginationView.as_view()),
    path('external_users_edit/<pk>/', views.ExternalUsersEditView.as_view()),
    path('external_users_delete/<pk>/', views.ExternalUsersDeleteView.as_view()),
    path('external_users_document_add/', views.ExternalUsersDocumentAddView.as_view()),
    path('external_users_document_edit/<pk>/', views.ExternalUsersDocumentEditView.as_view()),
    path('external_users_document_delete/<pk>/', views.ExternalUsersDocumentDeleteView.as_view()),
    path('external_users_document_list/<external_user_id>/', views.ExternalUsersDocumentListView.as_view()),
    path('vendor_details_excel_file_add/',views.VendorDetailsExcelFileAddView.as_view()),

]