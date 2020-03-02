from core import views
from django.conf.urls import url, include
from rest_framework import routers
from django.urls import path
from rest_framework.authtoken import views as rest_framework_views

'''
    This module prepared by @@ Rupam Hazra. Any kind of issues occurred, ask me first !!!
    Version - 1.0
'''

urlpatterns = [
    path('permissions_list/', views.PermissionsListCreate.as_view()),
    path('add_application/', views.ModuleListCreate.as_view()),
    path('applications_list/', views.ModuleList.as_view()),
    path('edit_application/<pk>/', views.EditModuleById.as_view()),
    path('add_role/', views.RoleListCreate.as_view()), #add role and list of role
    path('edit_role/<pk>/', views.RoleRetrieveUpdateAPIView.as_view()), #add role and list of role
    path('unit_add/', views.UnitAddView.as_view()),
    
    #:::::::::::::::: OBJECTS :::::::::::::#
    path('other_add/', views.OtherAddView.as_view()),
    path('other_list/<module_id>/', views.OtherListView.as_view()),
    path('other_list_by_parent/<module_id>/<parent_id>/', views.OtherListByParentView.as_view()),
    path('other_edit/<pk>/', views.OtherEditView.as_view()),
    path('other_delete/<pk>/', views.OtherDeleteView.as_view()),

    # Objects List For Role
    path('other_list_for_role/<module_id>/', views.OtherListForRoleView.as_view()),
    
    #:::::::::::::::::::::: T CORE DEPARTMENT:::::::::::::::::::::::::::#
    path('t_core_department_add/', views.CoreDepartmentAddView.as_view()),
    path('t_core_department_add_with_child_dep/<parent_id>/', views.CoreDepartmentWithChildView.as_view()),
    path('t_core_department_edit/<pk>/', views.CoreDepartmentEditView.as_view()),
    path('t_core_department_delete/<pk>/', views.CoreDepartmentDeleteView.as_view()),
    #:::::::::::::::::::::: T CORE DESIGNATION:::::::::::::::::::::::::::#
    path('t_core_designation_add/', views.CoreDesignationAddView.as_view()),
    path('t_core_designation_edit/<pk>/', views.CoreDesignationEditView.as_view()),
    path('t_core_designation_delete/<pk>/', views.CoreDesignationDeleteView.as_view()),

    #:::::::::::::::::::::: T CORE COMPANY :::::::::::::::::::::::::::::#
    path('t_core_company_add/',views.CoreCompanyAddView.as_view()),
    path('t_core_company_edit/<pk>/',views.CoreCompanyEditView.as_view()),
    path('t_core_comapny_delete/<pk>/',views.CoreCompanyDeleteView.as_view()),


    ###################################################################
    ########################### new permission level API ##############
    ###################################################################

    #:::::::::::::::: OBJECTS :::::::::::::#

    path('other_add_new/', views.OtherAddNewView.as_view()),
    path('other_list_new_by_module_name/<module_name>/', views.OtherListNewView.as_view()),
    path('other_list_with_permission_by_role_module_name/<module_name>/<role_name>/',views.OtherListWithPermissionByRoleModuleNameView.as_view()),
    path('other_list_with_permission_by_user_module_name/<module_name>/<user_id>/',views.OtherListWithPermissionByUserModuleNameView.as_view()),
    path('other_edit_new/<pk>/', views.OtherEditNewView.as_view()),

    #::::::::::::::: T Core State ::::::::::::::::#
    path('states_list_add/',views.StatesListAddView.as_view()),
    path('states_list_edit/<pk>/',views.StatesListEditView.as_view()),
    path('states_list_delete/<pk>/',views.StatesListDeleteView.as_view()),
    #:::::::::::::::::::::: T CORE SALARY TYPE:::::::::::::::::::::::::::#
    path('t_core_salary_type_add/', views.CoreSalaryTypeAddView.as_view()),
    path('t_core_salary_type_edit/<pk>/', views.CoreSalaryTypeEditView.as_view()),
    path('t_core_salary_type_delete/<pk>/', views.CoreSalaryTypeDeleteView.as_view()),

    
]