from pms import views
from django.conf.urls import url, include
from rest_framework import routers
from django.urls import path
from rest_framework.authtoken import views as rest_framework_views

urlpatterns = [
    #::::: PMS SECTION MASTER:::::::::::::::#
    # path('section_add/', views.SectionAddView.as_view()),
    # path('section_edit/<pk>/', views.SectionEditView.as_view()),

    #::::: PMS SECTION PERMISSION LEVEL MASTER:::::::::::::::#
    path('approval_permission_lavel_master_add/', views.ApprovalPermissonLavelMatserAddView.as_view()),
    path('approval_permission_lavel_master_edit/<pk>/', views.ApprovalPermissonLavelMatserEditView.as_view()),

    #::::: PMS SECTION PERMISSION MASTER:::::::::::::::#
    path('approval_permission_master_add/', views.ApprovalPermissonMatserAddView.as_view()),
    path('approval_permission_master_edit/<pk>/', views.ApprovalPermissonMatserEditView.as_view()),
    path('approval_permission_list/', views.ApprovalPermissonListView.as_view()),

    #::::: PMS APPROVAL USER LIST BY PERMISSION :::::::::::::::#
    path('approval_user_list_by_permission/<module_id>/<section_id>/<permission_id>/', views.ApprovalUserListByPermissionView.as_view()),


]
