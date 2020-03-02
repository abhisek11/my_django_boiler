from tickettool import views
from rest_framework import routers
from django.urls import path
from rest_framework.authtoken import views as rest_framework_views


urlpatterns = [
    path('support_type_add/',views.SupportTypeAdd.as_view()),
    path('ticket_add/',views.TicketAdd.as_view()),
    path('ticket_list/',views.TicketList.as_view()),
]