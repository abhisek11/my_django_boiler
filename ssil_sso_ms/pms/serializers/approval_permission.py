from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from pms.models import *
from django.contrib.auth.models import *
import time
from django.db import transaction, IntegrityError
from drf_extra_fields.fields import Base64ImageField
import os
from rest_framework.exceptions import APIException
import datetime
from core.models import TCoreUnit
from master.models import TMasterModuleRoleUser
from rest_framework.response import Response
from pms.custom_filter import custom_filter
import pandas as pd
import numpy as np
import xlrd
from pms.custom_delete import *
from django.db.models import Q
import re

#::::: PMS SECTION PERMISSION LEVEL MASTER:::::::::::::::#
class ApprovalPermissonLavelMatserAddSerializer(serializers.ModelSerializer):
    created_by=serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by=serializers.CharField(default=serializers.CurrentUserDefault())
    section_name = serializers.SerializerMethodField()
    def get_section_name(self, PmsApprovalPermissonLavelMatser): return PmsApprovalPermissonLavelMatser.section.cot_name
    class Meta:
        model = PmsApprovalPermissonLavelMatser
        fields = ('id','section','section_name','permission_level','created_by','owned_by')

class ApprovalPermissonLavelMatserEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsApprovalPermissonLavelMatser
        fields = ('id','updated_by','section','permission_level')

#::::: PMS SECTION PERMISSION MASTER:::::::::::::::#
class ApprovalPermissonMatserAddSerializer(serializers.ModelSerializer):
    created_by=serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by=serializers.CharField(default=serializers.CurrentUserDefault())
    section_name = serializers.CharField(required=False)
    user_details = serializers.DictField(required=False)
    user_approve_details = serializers.ListField(required=False)
    action = serializers.CharField(required=False)
    class Meta:
        model = PmsApprovalPermissonMatser
        fields = ('id','section','section_name','user_approve_details','user_details','created_by','owned_by','action')

    def create(self,validated_data):
        try:
            with transaction.atomic():
                user_approve_details = validated_data.get('user_approve_details')
                print('user_approve_details',user_approve_details)
                if validated_data.get('action') == 'edit':
                    PmsApprovalPermissonMatser.objects.filter(section = validated_data.get('section')).update(is_deleted=True)
                    for index,e_user_approve_details in enumerate(user_approve_details):
                        result = PmsApprovalPermissonMatser.objects.create(
                            section = validated_data.get('section'),
                            permission_level = e_user_approve_details['permission_level'],
                            approval_user_id = e_user_approve_details['approval_user'],
                            created_by = validated_data.get('created_by'),
                            owned_by = validated_data.get('owned_by')
                            )
                elif validated_data.get('action') == 'add':
                    for index,e_user_approve_details in enumerate(user_approve_details):
                        result = PmsApprovalPermissonMatser.objects.create(
                            section = validated_data.get('section'),
                            permission_level = e_user_approve_details['permission_level'],
                            approval_user_id = e_user_approve_details['approval_user'],
                            created_by = validated_data.get('created_by'),
                            owned_by = validated_data.get('owned_by')
                            )
                validated_data['section_name'] = validated_data.get('section').cot_name
                return validated_data
        except Exception as e:
            raise APIException(
                {"msg": e, "request_status": 0}
            )
class ApprovalPermissonListSerializer(serializers.ModelSerializer):
    created_by=serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by=serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsApprovalPermissonMatser
        fields = ('__all__')

class ApprovalPermissonMatserEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    section_name = serializers.SerializerMethodField()
    user_details = serializers.SerializerMethodField()
    def get_section_name(self,PmsApprovalPermissonMatser): return PmsApprovalPermissonMatser.section.section_name
    def get_user_details(self,PmsApprovalPermissonMatser): 
        user_dict = {
            'id': PmsApprovalPermissonMatser.approval_user.id,
            'email':PmsApprovalPermissonMatser.approval_user.email,
        }
        return user_dict
    class Meta:
        model = PmsApprovalPermissonMatser
        fields = ('id','updated_by','section','section_name','approval_user','user_details','permission_level')



class ApprovalUserListByPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TMasterModuleRoleUser
        fields = '__all__'