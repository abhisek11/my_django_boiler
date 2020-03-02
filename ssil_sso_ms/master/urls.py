from master import views
from django.conf.urls import url, include
from rest_framework import routers
from django.urls import path
from rest_framework.authtoken import views as rest_framework_views

'''
    This module prepared by @@ Rupam Hazra. Any kind of issues occurred, ask me first !!!
    Version - 2.0
'''

urlpatterns = [
    path('user-module-role_list/', views.UserModuleRoleListCreate.as_view()),
    path('module-role_create/', views.ModuleRoleCreate.as_view()),
    path('module-role_relation-mapping/<mmro_module_id>/', views.ModuleRoleRelationMapping.as_view()),
    path('role-module_list/<mmro_module_id>/', views.ModuleRoleList.as_view()),
    path('user_list_by_module_id/<mmr_module_id>/', views.UserList.as_view()),
    path('clone_module-roles/<clone_from>/<clone_to>/', views.CloneModuleRole.as_view()),

    # Assign Permisson to Object List
    path('assign_permission_to_role_add_or_update/', views.AssignPermissonToRoleAdd.as_view()),

    # Get immediate position of a role
    # path('get_immidiate_position_by_role/<pk>/', views.GetImmidiatePositionByRoleView.as_view()),

    path('grade_add/',views.GradeAddView.as_view()),


    ##################################################################
    ########################### new permisson level API ##############
    ##################################################################

    path('all_module_role_relation_mapping/', views.AllModuleRoleRelationMapping.as_view()),
    path('roles_by_module_name/<mmro_module_name>/', views.RolesByModuleName.as_view()),

    # Assign Permisson to Object List by role
    path('assign_permission_to_role_add_or_update_new/', views.AssignPermissonToRoleAddNewView.as_view()),

    path('module_role_create_new/', views.ModuleRoleCreateNewView.as_view()),

    # Assign Permisson to Object List by user
    path('assign_permission_to_user_add_or_update_new/', views.AssignPermissonToUserAddNewView.as_view()),

    #::::::::::: Permission Block :::::::::#
    
    path('object_top_lavel_permission_by_module/<module_name>/',views.ObjectTopLavelPermissionByModuleView.as_view()),


]