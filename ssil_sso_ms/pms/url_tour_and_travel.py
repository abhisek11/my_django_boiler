from pms import views
from django.conf.urls import url, include
from rest_framework import routers
from django.urls import path
from rest_framework.authtoken import views as rest_framework_views


urlpatterns = [
    path('tour_and_travel_expense_add/', views.TourAndTravelExpenseAddView.as_view()),
    path('tour_and_travel_vendor_or_employee_details_approval/',views.TourAndTravelVendorOrEmployeeDetailsApprovalView.as_view()),
    path('tour_and_travel_bill_received_approval/',views.TourAndTravelBillReceivedApprovalView.as_view()),
    path('tour_and_travel_final_booking_details_approval/',views.TourAndTravelFinalBookingDetailsApprovalView.as_view()),
    path('tour_and_travel_expense_master_approval/<pk>/',views.TourAndTravelExpenseMasterApprovalView.as_view()),
    path('tour_and_travel_expense_approval_list/', views.TourAndTravelExpenseApprovalList.as_view())
]







