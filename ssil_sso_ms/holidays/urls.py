from django.urls import path
from holidays import views
from django.conf.urls import url, include
from rest_framework.authtoken import views as rest_framework_views


urlpatterns = [
    #:::::::::::::::::::::: HOLIDAYS LIST:::::::::::::::::::::::::::#
    path('holidays_list_add/', views.HolidaysListAddView.as_view()),
    path('holidays_list_edit/<pk>/', views.HolidaysListEditView.as_view()),
    path('holidays_list_delete/<pk>/', views.HolidaysListDeleteView.as_view()),

    # State Wise holiday
    path('holidays_list_state_wise_old/', views.HolidaysListStateWiseViewOld.as_view()),
    # State wise holiday get:list, post:add list of holiday
    path('holidays_list_state_wise/', views.HolidaysStateWiseListAddView.as_view()),
    # State wise holiday edit
    path('holiday_list_state_wise_edit/<pk>/', views.StateWiseHolidaysEditView.as_view()),
    # State wise holiday soft-delete
    path('holidays_list_state_wise_delete/<pk>/', views.StateWiseHolidaysDeleteView.as_view()),
    
    path('pdf_test/', views.PDFTestView.as_view()),

]