from users import views
from django.conf.urls import url, include
from rest_framework import routers
from django.urls import path


'''
    This module prepared by @@ Rupam Hazra. Any kind of issues occurred, ask me first !!!
    Version - 2.0
'''


urlpatterns = [
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('login/', views.LoginAuthToken.as_view()),
    path('add_user/', views.UsersSignInListCreate.as_view()),
    path('edit_user/<pk>/', views.UsersSignInListCreate.as_view()),
    path('change_password/', views.ChangePasswordView.as_view()),
    path('change_password_with_username/', views.ChangePasswordWithUsernameView.as_view()),
    path('forgot_password/', views.ForgotPasswordView.as_view()),
    path('logout/', views.Logout.as_view()),
    # path('user_lock_unlock/<pk>/', views.ActiveInactiveUserView.as_view()),
    path('user_edit/<cu_user_id>/', views.EditUserView.as_view()),
    path('user_module_list/', views.ModuleUserList.as_view()),
    path('user_update_employee_code/', views.UserUpdateEmployeeCode.as_view()),

    ###################################################################
    ########################### new permission level API ##############
    ###################################################################

    path('user_permission_edit/<cu_user_id>/', views.UserPermissionEditView.as_view()), #EditUserNewView
    path('login_new/', views.LoginAuthTokenNew.as_view()),
    path('edit_user_new/<pk>/', views.EditUserNewView.as_view()), 
    path('edit_user_get_new/<pk>/', views.EditUserGetNewView.as_view()), 
    path('user_list_by_department/<department_id>/',views.UserListByDepartmentView.as_view()),
    path('user_list_under_login_user/',views.UserListUnderLoginUserView.as_view()),

    # Department HOD List
    path('hod_list_with_department/', views.HodListWithDepartmentView.as_view()),

    
    #New Token Authentication [knox]
    #path('login_knox/', views.LoginAPIView.as_view()),
    #END
]