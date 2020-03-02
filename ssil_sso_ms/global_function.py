
from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from hrms.models import *
from hrms.serializers import *
from pagination import CSLimitOffestpagination,CSPageNumberPagination
from rest_framework.views import APIView
from django.conf import settings
from rest_framework import mixins
from rest_framework import filters
from datetime import datetime,timedelta
import collections
from rest_framework.parsers import FileUploadParser
from django_filters.rest_framework import DjangoFilterBackend
from custom_decorator import *
import os
from django.http import JsonResponse
from datetime import datetime
from decimal import Decimal
import pandas as pd
import xlrd
import numpy as np
from django.db.models import Q
from custom_exception_message import *
from decimal import *
import math
from django.contrib.auth.models import *
from django.db.models import F
from django.db.models import Count
from core.models import *
from pms.models import *
import re

def userdetails(user):
    # print(type(user))
    if isinstance(user,(int)):
        name = User.objects.filter(id =user)
        for i in name:
            # print("i",i)
            f_name_l_name = i.first_name +" "+ i.last_name
            # print("f_name_l_name",f_name_l_name)
    elif isinstance(user,(str)):
        # print(user ,"str")
        name = User.objects.filter(username=user)
        for i in name:
            # print("i",i)
            f_name_l_name = i.first_name +" "+ i.last_name
            # print("f_name_l_name",f_name_l_name)
    else:
        f_name_l_name = None

    return f_name_l_name

def designation(designation):
    if isinstance(designation,(str)):
        desg_data  = TCoreUserDetail.objects.filter(cu_user__username =designation)
        if desg_data:
            for desg in desg_data:
                return desg.designation.cod_name
        else:
            return None
    elif isinstance(designation,(int)):
        desg_data = TCoreUserDetail.objects.filter(cu_user =designation)
        if desg_data:
            for desg in desg_data:
                return desg.designation.cod_name
        else:
            return None


def department(department):
    if isinstance(department,(str)):
        desg_data  = TCoreUserDetail.objects.filter(cu_user__username =department)
        if desg_data:
            for desg in desg_data: 
                return desg.department.cd_name
        else:
            return None
    elif isinstance(department,(int)):
        desg_data = TCoreUserDetail.objects.filter(cu_user =department)
        if desg_data:
            for desg in desg_data:
                return desg.department.cd_name
        else:
            return None

def getHostWithPort(request):
    protocol = 'https://' if request.is_secure() else 'http://'
    url = protocol+request.get_host()+'/'
    #print('url',url)
    return url

def raw_query_extract(query):

    return query.query