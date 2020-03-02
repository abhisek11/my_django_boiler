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
from rest_framework.response import Response
from pms.custom_filter import custom_filter
import pandas as pd
import numpy as np
import xlrd
from pms.custom_delete import *
from django.db.models import Q
import re

#:::::::::::::::::  PMS External Users ::::::::::::::::::::#
class ExternalUsersTypeAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    type_name = serializers.CharField(required=True)

    class Meta:
        model = PmsExternalUsersType
        fields = ('id', 'type_name', 'type_desc', 'created_by', 'owned_by')
class ExternalUsersTypeEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    type_name = serializers.CharField(read_only=True)

    class Meta:
        model = PmsExternalUsersType
        fields = ('id', 'type_name', 'type_desc', 'updated_by')
class ExternalUsersTypeDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = PmsExternalUsersType
        fields = '__all__'

    def update(self, instance, validated_data):
        instance.is_deleted = True
        instance.save()
        return instance

#:::::::::::::::::  PMS External Users Type ::::::::::::::::::::#
class ExternalUsersAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    document_details=serializers.SerializerMethodField(required=False)
    user_type_name = serializers.SerializerMethodField(required=False)
    class Meta:
        model = PmsExternalUsers
        fields = '__all__'
        extra_fields = ['document_details','user_type_name']

    def get_document_details(self, PmsExternalUsers):
        document = PmsExternalUsersDocument.objects.filter(external_user=PmsExternalUsers.id,is_deleted=False)
        request = self.context.get('request')
        response_list = []
        for each_document in document:
            file_url = request.build_absolute_uri(each_document.document.url)
            owned_by = str(each_document.owned_by) if each_document.owned_by else ''
            created_by = str(each_document.created_by) if each_document.created_by else ''
            each_data = {
                "id": int(each_document.id),
                "external_user": each_document.external_user.id,
                "document_name": each_document.document_name,
                "document": file_url,
                "created_by": created_by,
                "owned_by": owned_by
            }
            response_list.append(each_data)
        return response_list
    def get_user_type_name(self, PmsExternalUsers):
        return PmsExternalUsersType.objects.only('type_name').get(pk=PmsExternalUsers.user_type.id).type_name

class ExternalUsersListSerializer(serializers.ModelSerializer):
    document_details = serializers.SerializerMethodField(required=False)
    user_type_name = serializers.SerializerMethodField(required=False)
    def get_document_details(self, PmsExternalUsers):
        document = PmsExternalUsersDocument.objects.filter(external_user=PmsExternalUsers.id, is_deleted=False)
        # print('document',document)
        request = self.context.get('request')
        response_list = []
        for each_document in document:
            file_url = request.build_absolute_uri(each_document.document.url)
            owned_by = str(each_document.owned_by) if each_document.owned_by else ''
            created_by = str(each_document.created_by) if each_document.created_by else ''
            each_data = {
                "id": int(each_document.id),
                "external_user": each_document.external_user.id,
                "document_name": each_document.document_name,
                "document": file_url,
                "created_by": created_by,
                "owned_by": owned_by
            }
            response_list.append(each_data)
        return response_list

    def get_user_type_name(self, PmsExternalUsers):
        return PmsExternalUsersType.objects.only('type_name').get(pk=PmsExternalUsers.user_type.id).type_name

    class Meta:
        model = PmsExternalUsers
        fields = '__all__'
        extra_fields = ('document_details','user_type_name')

class ExternalUsersListWithPaginationSerializer(serializers.ModelSerializer):
    document_details = serializers.SerializerMethodField(required=False)
    user_type_name = serializers.SerializerMethodField(required=False)
    def get_document_details(self, PmsExternalUsers):
        document = PmsExternalUsersDocument.objects.filter(external_user=PmsExternalUsers.id, is_deleted=False)
        print('document',document)
        request = self.context.get('request')
        response_list = []
        for each_document in document:
            file_url = request.build_absolute_uri(each_document.document.url)
            owned_by = str(each_document.owned_by) if each_document.owned_by else ''
            created_by = str(each_document.created_by) if each_document.created_by else ''
            each_data = {
                "id": int(each_document.id),
                "external_user": each_document.external_user.id,
                "document_name": each_document.document_name,
                "document": file_url,
                "created_by": created_by,
                "owned_by": owned_by
            }
            response_list.append(each_data)
        return response_list

    def get_user_type_name(self, PmsExternalUsers):
        return PmsExternalUsersType.objects.only('type_name').get(pk=PmsExternalUsers.user_type.id).type_name

    class Meta:
        model = PmsExternalUsers
        fields = '__all__'
        extra_fields = ('document_details','user_type_name')

class ExternalUsersEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    document_details = serializers.SerializerMethodField(required=False)
    user_type_name = serializers.SerializerMethodField(required=False)
    gst_no = serializers.CharField(required=False)
    code = serializers.CharField(required=False)
    salary = serializers.CharField(required=False)
    pan_no = serializers.CharField(required=False)
    bank_ac_no = serializers.CharField(required=False)
    adhar_no = serializers.CharField(required=False)
    class Meta:
        model = PmsExternalUsers
        fields = '__all__'
        extra_fields = ['document_details', 'user_type_name']
    def get_document_details(self, PmsExternalUsers):
        document = PmsExternalUsersDocument.objects.filter(external_user=PmsExternalUsers.id,is_deleted=False)
        request = self.context.get('request')
        response_list = []
        for each_document in document:
            file_url = request.build_absolute_uri(each_document.document.url)
            owned_by = str(each_document.owned_by) if each_document.owned_by else ''
            created_by = str(each_document.created_by) if each_document.created_by else ''
            each_data = {
                "id": int(each_document.id),
                "external_user": each_document.external_user.id,
                "document_name": each_document.document_name,
                "document": file_url,
                "created_by": created_by,
                "owned_by": owned_by
            }
            response_list.append(each_data)
        return response_list
    def get_user_type_name(self, PmsExternalUsers):
        return PmsExternalUsersType.objects.only('type_name').get(pk=PmsExternalUsers.user_type.id).type_name
class ExternalUsersDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    is_deleted = serializers.BooleanField(default=True)
    class Meta:
        model=PmsExternalUsers
        fields=('id','is_deleted','updated_by','organisation_name','email')
        read_only_fields = ('organisation_name','email')
    def update(self, instance, validated_data):
        delete_details  = custom_delete(
            self, instance, validated_data,
            update_extra_columns=['status'],
            extra_model_with_fields = [
                {
                'model': PmsExternalUsersDocument,
                'filter_columns' : {
                    'external_user': instance, 'is_deleted': False
                 },
                'update_extra_columns':['status']
                },
            ]
        )
        return delete_details
class ExternalUsersDocumentAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsExternalUsersDocument
        fields = '__all__'
class ExternalUsersDocumentEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsExternalUsersDocument
        fields = '__all__'
class ExternalUsersDocumentDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsExternalUsersDocument
        fields = ('id', 'is_deleted', 'updated_by', 'document', 'document_name','external_user')
        read_only_fields = ('document', 'document_name','external_user')
class ExternalUsersDocumentListSerializer(serializers.ModelSerializer):
    class Meta:
        model=PmsExternalUsersDocument
        fields='__all__'