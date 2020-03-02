from pms import views
from django.conf.urls import url, include
from rest_framework import routers
from django.urls import path

from rest_framework.authtoken import views as rest_framework_views


urlpatterns = [
    #:::::::::::::::::::  Manpower :::::::::::::::::::::::::#
    path('manpower_list_wo_pagination/<module_id>/', views.ManPowerListWOView.as_view()),
    path('manpower_list/<module_id>/', views.ManPowerListView.as_view()),
    path('manpower_designation_list/', views.ManPowerDesignationListView.as_view()), # not used
    path('manpower_designation_list_wo_pagination/', views.ManPowerDesignationListWOPaginationView.as_view()),
    path('manpower_list_by_designation_id/<module_id>/<designation_id>/', views.ManPowerListByDesignationIdView.as_view()),
    path('manpower_list_by_designation_id_wo_pagination/<module_id>/<designation_id>/', views.ManPowerListByDesignationIdWOPaginationView.as_view()),
]