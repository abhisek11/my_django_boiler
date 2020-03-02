from pms import views
from django.conf.urls import url, include
from rest_framework import routers
from django.urls import path
from rest_framework.authtoken import views as rest_framework_views

urlpatterns = [
    #----------Pms Site Type Project Site Management---------#
    path('project_site_management_site_type_add/', views.SiteTypeProjectSiteManagementAddView.as_view()),
    path('project_site_management_site_type_edit/<pk>/', views.SiteTypeProjectSiteManagementEditView.as_view()),
    path('project_site_management_site_type_delete/<pk>/', views.SiteTypeProjectSiteManagementDeleteView.as_view()),

    #--------- Pms Site Project Site Management---------------#
    path('project_site_management_site_add/', views.ProjectSiteManagementSiteAddView.as_view()),
    path('project_site_management_site_edit/<pk>/', views.ProjectSiteManagementSiteEditView.as_view()),
    path('project_site_management_site_delete/<pk>/', views.ProjectSiteManagementSiteDeleteView.as_view()),
    #path('project_site_management_site_wp_list/', views.ProjectSiteManagementSiteListWPView.as_view()),

    #::::::::::::::: PMS PROJECTS ::::::::::::::::::::::::::::#
    path('projects_add/', views.ProjectsAddView.as_view()),
    path('projects_list/', views.ProjectsListView.as_view()),
    path('closed_projects_list/', views.ClosedProjectsListView.as_view()),
    path('projects_list_count/', views.ProjectsListCountView.as_view()),
    path('projects_list_wp/', views.ProjectsListWPView.as_view()),
    path('projects_edit/<pk>/', views.ProjectsEditView.as_view()),
    path('projects_delete/<pk>/', views.ProjectsDeleteView.as_view()),
    path('projects_details_by_project_site_id/',views.ProjectsDetailsByProjectSiteIdView.as_view()),
    path('projects_list_with_lat_long/',views.ProjectsListWithLatLongView.as_view()),
    
]
