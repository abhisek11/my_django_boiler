from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from pms.models import *
from pms.serializers import *
import time
from multiplelookupfields import MultipleFieldLookupMixin
from rest_framework.views import APIView
from django.conf import settings
from pagination import *
from rest_framework import filters
import calendar
from datetime import datetime
from holidays.models import *
import collections
from rest_framework.exceptions import APIException
import pandas as pd
import numpy as np
from django_filters.rest_framework import DjangoFilterBackend
from master.serializers import UserModuleWiseListSerializer
from master.models import TMasterModuleRoleUser, TMasterOtherRole
from users.models import TCoreUserDetail
from custom_decorator import *
from rest_framework.parsers import FileUploadParser
import os
from pms.custom_filter import *
from django.db.models import Q
from itertools import chain

#::::: PMS SECTION PERMISSION LEVEL MASTER:::::::::::::::#
class ApprovalPermissonLavelMatserAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsApprovalPermissonLavelMatser.objects.filter(is_deleted=False)
    serializer_class = ApprovalPermissonLavelMatserAddSerializer
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
    
    @response_modify_decorator_post
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class ApprovalPermissonLavelMatserEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsApprovalPermissonLavelMatser.objects.all()
    serializer_class = ApprovalPermissonLavelMatserEditSerializer

    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response

    @response_modify_decorator_update
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)


#::::: PMS SECTION PERMISSION MASTER:::::::::::::::#

class ApprovalPermissonMatserAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsApprovalPermissonMatser.objects.filter(is_deleted=False)
    serializer_class = ApprovalPermissonMatserAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('section',)

    def get(self, request, *args, **kwargs):
        section = self.request.GET.get('section', None)
        response = super(self.__class__, self).get(request, args, kwargs)
        response_s= list()
        section_name = ''
        section_id = set()
        for data in response.data: section_id.add(data['section'])
        for e_section_id in section_id:
            section_name = TCoreOther.objects.only('cot_name').get(pk=e_section_id).cot_name if TCoreOther.objects.filter(pk=e_section_id).count() else None
            total_dict = {
                "id":e_section_id,
                "section_name":section_name,
            }
            approval_master_details = PmsApprovalPermissonMatser.objects.filter(
                section=e_section_id,is_deleted=False)
            #print('approval_master_details',approval_master_details)
            approval_master = list()
            for e_approval_master_details in approval_master_details:

                f_name = e_approval_master_details.approval_user.first_name if e_approval_master_details.approval_user else '' 
                l_name = e_approval_master_details.approval_user.last_name if e_approval_master_details.approval_user else '' 
                approval_master_dict = {
                    "id":e_approval_master_details.id,
                    "approval_user":e_approval_master_details.approval_user.id,
                    "permission_level":e_approval_master_details.permission_level,
                    "user_details":{
                        "id":e_approval_master_details.approval_user.id if e_approval_master_details.approval_user else None,
                        "email":e_approval_master_details.approval_user.email if e_approval_master_details.approval_user else None,
                        "name":  f_name +' '+l_name
                    }
                }
                approval_master.append(approval_master_dict)
            total_dict['user_approve_details'] = approval_master
            response_s.append(total_dict)
            
        data_dict = dict()
        if section:
            data_dict['result'] = total_dict
            if total_dict:
                data_dict['request_status'] = 1
                data_dict['msg'] = settings.MSG_SUCCESS
            elif len(total_dict) == 0:
                data_dict['request_status'] = 1
                data_dict['msg'] = settings.MSG_NO_DATA
            else:
                data_dict['request_status'] = 0
                data_dict['msg'] = settings.MSG_ERROR
        else:
            data_dict['result'] = response_s
            if response_s:
                data_dict['request_status'] = 1
                data_dict['msg'] = settings.MSG_SUCCESS
            elif len(response_s) == 0:
                data_dict['request_status'] = 1
                data_dict['msg'] = settings.MSG_NO_DATA
            else:
                data_dict['request_status'] = 0
                data_dict['msg'] = settings.MSG_ERROR
        return Response(data_dict)
    
    @response_modify_decorator_post
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class ApprovalPermissonListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsApprovalPermissonMatser.objects.filter(is_deleted=False)
    serializer_class = ApprovalPermissonListSerializer

    def get(self, request, *args, **kwargs):
        section = self.request.query_params.get('section', None)
        print("section",section.lower())
        response = super(self.__class__, self).get(request, args, kwargs)
        response_s= list()
        section_name = ''
        section_id = set()
        section_details= TCoreOther.objects.get(cot_name=section.lower())
        total_dict = {
            "id":section_details.id,
            "section_name":section_details.cot_name,
        }
        approval_master_details = PmsApprovalPermissonMatser.objects.filter(
            section=section_details.id,is_deleted=False)
        print('approval_master_details',approval_master_details)
        approval_master = list()
        for e_approval_master_details in approval_master_details:

            f_name = e_approval_master_details.approval_user.first_name if e_approval_master_details.approval_user else '' 
            l_name = e_approval_master_details.approval_user.last_name if e_approval_master_details.approval_user else '' 
            var=e_approval_master_details.permission_level
            if len(var) == 2:
                var=int(var[1:])
            approval_master_dict = {
                "id":e_approval_master_details.id,
                "approval_user":e_approval_master_details.approval_user.id,
                "permission_level":e_approval_master_details.permission_level,
                "permission_num":var,
                "user_details":{
                    "id":e_approval_master_details.approval_user.id if e_approval_master_details.approval_user else None,
                    "email":e_approval_master_details.approval_user.email if e_approval_master_details.approval_user else None,
                    "name":  f_name +' '+l_name,
                    "username":e_approval_master_details.approval_user.username
                }
            }
            approval_master.append(approval_master_dict)
        total_dict['user_approve_details'] = approval_master
        response_s.append(total_dict)
            
        data_dict = dict()
        if section:
            data_dict['result'] = total_dict
            if total_dict:
                data_dict['request_status'] = 1
                data_dict['msg'] = settings.MSG_SUCCESS
            elif len(total_dict) == 0:
                data_dict['request_status'] = 1
                data_dict['msg'] = settings.MSG_NO_DATA
            else:
                data_dict['request_status'] = 0
                data_dict['msg'] = settings.MSG_ERROR
        else:
            data_dict['result'] = response_s
            if response_s:
                data_dict['request_status'] = 1
                data_dict['msg'] = settings.MSG_SUCCESS
            elif len(response_s) == 0:
                data_dict['request_status'] = 1
                data_dict['msg'] = settings.MSG_NO_DATA
            else:
                data_dict['request_status'] = 0
                data_dict['msg'] = settings.MSG_ERROR
        return Response(data_dict)
    



class ApprovalPermissonMatserEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsApprovalPermissonMatser.objects.all()
    serializer_class = ApprovalPermissonMatserEditSerializer

    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response

    @response_modify_decorator_update
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

#::::: PMS APPROVAL USER LIST BY PERMISSION :::::::::::::::#

class ApprovalUserListByPermissionView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = TMasterModuleRoleUser.objects.filter(mmr_user__isnull=False)
    serializer_class = ApprovalUserListByPermissionSerializer

    def get_queryset(self):
        module_id=self.kwargs['module_id']
        section_id = self.kwargs['section_id']
        permission_id = self.kwargs['permission_id']

        other_details = TMasterOtherRole.objects.filter(
            mor_other_id=section_id,
            mor_module = module_id,
            mor_permissions = permission_id
            )
        print('other_details',other_details)
        mmr_user = list()
        mmr_user_role = list()
        if other_details:
            for e_other_details in other_details:
                mmr_user_role.append(e_other_details.mor_role)
            
            queryset = TMasterModuleRoleUser.objects.filter(
                (Q(
                mmr_is_deleted=False,
                mmr_role__in=mmr_user_role,
                mmr_module_id=module_id
                ) | Q(mmr_is_deleted=False,mmr_module_id=module_id,mmr_type=1))
            )
            print('queryset',queryset)
            return queryset

        

    @response_modify_decorator_get_after_execution
    def get(self,request,*args,**kwargs):
        response = super(self.__class__, self).get(self, request, args, kwargs)
        #print('response',response.data)
        module_id=self.kwargs['module_id']
        section_id = self.kwargs['section_id']
        permission_id = self.kwargs['permission_id']
        for data in response.data:
            if data['mmr_user']:
                #print('data:',data)
                employee_details = TCoreUserDetail.objects.filter(cu_user=data['mmr_user']).order_by('cu_user__first_name')
                print('employee_details',employee_details)
                for employee in employee_details:
                    manpower_dict = {}
                    #print("employee: ", employee.cu_user_id)
                    manpower_dict['employee_id']=employee.cu_user_id
                    manpower_dict['employee_code'] = employee.cu_emp_code
                    name = employee.cu_user.first_name + ' ' +employee.cu_user.last_name
                    manpower_dict['employee_name']=name.strip()
                    manpower_dict['email_id']=employee.cu_user.email
                    manpower_dict['contact_no']=employee.cu_phone_no
                

                designation_details = TMasterModuleRoleUser.objects.filter(
                    mmr_user=data['mmr_user'],mmr_module=module_id)
                #print('designation_details',designation_details)
                if designation_details:
                    for designation in designation_details:
                        if designation.mmr_designation:
                            data['designation'] =designation.mmr_designation.cod_name
                        else:
                            data['designation'] = ""

                data['mmr_user'] = manpower_dict
        return response

