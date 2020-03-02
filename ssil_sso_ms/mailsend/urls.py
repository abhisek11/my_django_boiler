from mailsend import views
from django.conf.urls import url, include
from rest_framework import routers
from django.urls import path
from rest_framework.authtoken import views as rest_framework_views

'''
    This module prepared by @@ Rupam Hazra. Any kind of issues occurred, ask me first !!!
    Version - 1.0
'''

urlpatterns = [
    path('mail_send/', views.MailSendApiView.as_view()),
]