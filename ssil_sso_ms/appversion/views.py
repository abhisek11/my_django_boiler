from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import filters
# permission checking
from rest_framework.permissions import IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
#get_current_site
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from pagination import CSLimitOffestpagination,CSPageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
import collections
from rest_framework.views import APIView
from appversion.models import *

# Create your views here.
class GetAppVersionView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        #print('GetAppVersionView')
        app_name = self.request.GET.get('app_name', None)
        #print('app_name',app_name)
        app_prev_version = self.request.GET.get('current_app_version', None)
        app_current_version = float(AppVersion.objects.only('version').get(name=app_name).version)
        print('app_current_version',float(app_current_version))
        if app_current_version > float(app_prev_version):
            response_dict = {
                "result":{
                    "app_name":app_name,
                    "app_prev_version":app_prev_version,
                    "app_current_version":app_current_version,
                    "version_upgraded":True
                },
                "msg":"success"
            }
        else:
            response_dict = {
                "result":{
                    "app_name":app_name,
                    "app_prev_version":app_prev_version,
                    "app_current_version":app_current_version,
                    "version_upgraded":False
                },
                "msg":"success"
            }
        return Response(response_dict)
        