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
from users.models import TCoreUserDetail
from rest_framework.response import Response
from pms.custom_filter import custom_filter
import pandas as pd
import numpy as np
import xlrd
from pms.custom_delete import *
from django.db.models import Q
import re
from django.conf import settings

#::::::::::::PMS PRE EXECUTION GUEST HOUSE FINDING:::::::::#
class PreExecutionGuestHouseFindingAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model=PmsPreExcutionGuestHouseFinding
        fields=('id','project','cost','address','latitude','longitude','no_of_rooms','capacity','distence_from_site','checkin_date',
                'checkout_date','near_rail_station','near_bus_stand','created_by','owned_by')
class PreExecutionGuestHouseFindingEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model=PmsPreExcutionGuestHouseFinding
        fields=('id','project','cost','address','latitude','longitude','no_of_rooms','capacity','distence_from_site','checkin_date',
                'checkout_date','near_rail_station','near_bus_stand','updated_by')

#::::::::::::PMS PRE EXECUTION FURNITURE:::::::::#
class PreExecutionFurnitureAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model=PmsPreExcutionFurniture
        fields=('id','project','guest_house_type','transporation_cost','created_by','owned_by')
class PreExecutionFurnitureEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsPreExcutionFurniture
        fields = ( 'id','project','guest_house_type','transporation_cost','updated_by')
class PreExecutionFurnitureRequirementsAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsPreExcutionFurMFurRequirements
        fields = ('id', 'f_requirements', 'type', 'count','local_rate','document_name','document', 'created_by', 'owned_by')
class PreExecutionFurnitureRequirementsEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsPreExcutionFurMFurRequirements
        fields = ('id', 'f_requirements', 'type', 'count','local_rate','updated_by')
    # def update(self, instance, validated_data):
    #     instance.f_requirements=validated_data.get('f_requirements')
    #     instance.type=validated_data.get('type')
    #     instance.count=validated_data.get('count')
    #     instance.local_rate=validated_data.get('local_rate')
    #     instance.document_name=validated_data.get('document_name')
    #     instance.updated_by = validated_data.get('updated_by')
    #     existing_image = './media/' + str(instance.document)
    #     # print('existing_image', existing_image)
    #     if validated_data.get('document'):
    #         if os.path.isfile(existing_image):
    #             os.remove(existing_image)
    #         instance.document = validated_data.get('document')
    #     instance.save()
    #     return instance
class PreExecutionFurnitureRequirementsDocumentEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsPreExcutionFurMFurRequirements
        fields = ('id','document_name','updated_by')
class PreExecutionFurnitureRequirementsDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsPreExcutionFurMFurRequirements
        fields = '__all__'

    def update(self, instance, validated_data):
        instance.updated_by = validated_data.get('updated_by')
        instance.is_deleted = True
        instance.save()
        return instance

#::::::::::::PMS PRE EXCUTION UTILITIES ELECTRICAL::::::::#
class PreExcutionUtilitiesElectricalAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    document_details=serializers.SerializerMethodField()

    def get_document_details(self, PmsPreExcutionUtilitiesElectrical):
        document = PmsPreExcutionUtilitiesDocument.objects.filter(project=PmsPreExcutionUtilitiesElectrical.project.id,
                                                                    module_id=PmsPreExcutionUtilitiesElectrical.id,
                                                                  model_class="PmsPreExcutionUtilitiesElectrical",
                                                                  is_deleted=False)
        request = self.context.get('request')
        response_list = []
        for each_document in document:
            file_url = request.build_absolute_uri(each_document.document.url)
            owned_by = str(each_document.owned_by) if each_document.owned_by else ''
            created_by = str(each_document.created_by) if each_document.created_by else ''
            each_data = {
                "id": int(each_document.id),
                "project":int(each_document.project.id),
                "module_id": int(each_document.module_id),
                "model_class":each_document.model_class,
                "document_name": each_document.document_name,
                "document": file_url,
                "created_by": created_by,
                "owned_by": owned_by
            }
            response_list.append(each_data)
        return response_list

    class Meta:
        model = PmsPreExcutionUtilitiesElectrical
        fields = ('id', 'project', 'local_connection', 'option', 'n_electric_of_addr', 'latitude', 'longitude', 'contact_no',
                  'detailed_procedure', 'requirment_s_date', 'requirment_e_date', 'budgeted_cost', 'executed_cost', 'created_by', 'owned_by','document_details')
class PreExcutionUtilitiesElectricalEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsPreExcutionUtilitiesElectrical
        fields = ('id', 'project', 'local_connection', 'option', 'n_electric_of_addr', 'latitude', 'longitude', 'contact_no',
                  'detailed_procedure', 'requirment_s_date', 'requirment_e_date', 'budgeted_cost', 'executed_cost', 'updated_by')
class PreExcutionUtilitiesElectricalDocumentAddSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    owned_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    model_class = serializers.CharField(required=False)
    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = ('id', 'project', 'module_id', 'document_name', 'document', 'created_by', 'owned_by','model_class')

    def create(self,validated_data):
        try:
            electrical_data = PmsPreExcutionUtilitiesDocument.objects.create(**validated_data,
                                                                      model_class="PmsPreExcutionUtilitiesElectrical")
            return electrical_data
        except Exception as e:
            raise e
class PreExcutionUtilitiesElectricalDocumentEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = ("id", "document_name", "updated_by")
class PreExcutionUtilitiesElectricalDocumentDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = '__all__'

    def update(self, instance, validated_data):
        instance.updated_by = validated_data.get('updated_by')
        instance.is_deleted = True
        instance.save()
        return instance

#:::::::::::::::::::::: PMS PRE EXCUTION UTILITIES WATER:::::::::::::::::::::::::::#
class PreExcutionUtilitiesWaterAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    document_details=serializers.SerializerMethodField()
    def get_document_details(self, PmsPreExcutionUtilitiesWater):
        document = PmsPreExcutionUtilitiesDocument.objects.filter(project=PmsPreExcutionUtilitiesWater.project.id,
                                                                    module_id=PmsPreExcutionUtilitiesWater.id,
                                                                  model_class="PmsPreExcutionUtilitiesWater",
                                                                  is_deleted=False)
        request = self.context.get('request')
        response_list = []
        for each_document in document:
            file_url = request.build_absolute_uri(each_document.document.url)
            owned_by = str(each_document.owned_by) if each_document.owned_by else ''
            created_by = str(each_document.created_by) if each_document.created_by else ''
            each_data = {
                "id": int(each_document.id),
                "project":int(each_document.project.id),
                "module_id": int(each_document.module_id),
                "model_class":each_document.model_class,
                "document_name": each_document.document_name,
                "document": file_url,
                "created_by": created_by,
                "owned_by": owned_by
            }
            response_list.append(each_data)
        return response_list


    class Meta:
        model = PmsPreExcutionUtilitiesWater
        fields = ('id', 'project', 'submergible_pump','quantity', 'depth', 'con_name', 'con_conatct_no', 'con_email_id',
                  'con_address', 'latitude', 'longitude', 'requirment_s_date', 'requirment_e_date', 'budgeted_cost',
                  'executed_cost', 'created_by', 'owned_by','document_details')
class PreExcutionUtilitiesWaterEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsPreExcutionUtilitiesWater
        fields = ('id', 'project', 'submergible_pump', 'quantity', 'depth', 'con_name', 'con_conatct_no', 'con_email_id',
                  'con_address', 'latitude', 'longitude', 'requirment_s_date', 'requirment_e_date', 'budgeted_cost',
                  'executed_cost',  'updated_by')
class PreExcutionUtilitiesWaterDocumentAddSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    owned_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    model_class = serializers.CharField(required=False)
    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = ('id', 'project', 'module_id', 'document_name', 'document', 'created_by', 'owned_by','model_class')

    def create(self, validated_data):
        resource_establishment_data = PmsPreExcutionUtilitiesDocument.objects.create(**validated_data,
                                                                             model_class="PmsPreExcutionUtilitiesWater")
        return resource_establishment_data
class PreExcutionUtilitiesWaterDocumentEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = ("id", "document_name", "updated_by")
class PreExcutionUtilitiesWaterDocumentDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = '__all__'

    def update(self, instance, validated_data):
        instance.updated_by = validated_data.get('updated_by')
        instance.is_deleted = True
        instance.save()
        return instance
#:::::::::::::::::::::: PMS PRE EXCUTION UTILITIES FUEL:::::::::::::::::::::::::::#
class PreExcutionUtilitiesFuelAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    document_details=serializers.SerializerMethodField()
    def get_document_details(self, PmsPreExcutionUtilitiesFuel):
        document = PmsPreExcutionUtilitiesDocument.objects.filter(project=PmsPreExcutionUtilitiesFuel.project.id,
                                                                    module_id=PmsPreExcutionUtilitiesFuel.id,
                                                                  model_class="PmsPreExcutionUtilitiesFuel",
                                                                  is_deleted=False)
        request = self.context.get('request')
        response_list = []
        for each_document in document:
            file_url = request.build_absolute_uri(each_document.document.url)
            owned_by = str(each_document.owned_by) if each_document.owned_by else ''
            created_by = str(each_document.created_by) if each_document.created_by else ''
            each_data = {
                "id": int(each_document.id),
                "project":int(each_document.project.id),
                "module_id": int(each_document.module_id),
                "model_class":each_document.model_class,
                "document_name": each_document.document_name,
                "document": file_url,
                "created_by": created_by,
                "owned_by": owned_by
            }
            response_list.append(each_data)
        return response_list
    class Meta:
        model = PmsPreExcutionUtilitiesFuel
        fields = ('id', 'project', 'available', 'supplier_name', 'contact_no', 'supplier_address', 'latitude', 'longitude','type_of_fuel',
                 'volume_required', 'requirment_s_date', 'requirment_e_date', 'budgeted_cost', 'executed_cost', 'created_by', 'owned_by','document_details')
class PreExcutionUtilitiesFuelEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsPreExcutionUtilitiesFuel
        fields = ('id', 'project', 'available', 'supplier_name', 'contact_no', 'supplier_address', 'latitude', 'longitude','type_of_fuel',
                  'volume_required',
                  'requirment_s_date', 'requirment_e_date', 'budgeted_cost', 'executed_cost', 'updated_by')
class PreExcutionUtilitiesFuelDocumentAddSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    owned_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    model_class = serializers.CharField(required=False)
    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = ('id', 'project', 'module_id', 'document_name', 'document', 'created_by', 'owned_by','model_class')

    def create(self, validated_data):
        resource_establishment_data = PmsPreExcutionUtilitiesDocument.objects.create(**validated_data,
                                                                             model_class="PmsPreExcutionUtilitiesFuel")
        return resource_establishment_data
class PreExcutionUtilitiesFuelDocumentEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = ("id", "document_name", "updated_by")
class PreExcutionUtilitiesFuelDocumentDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = '__all__'

    def update(self, instance, validated_data):
        instance.updated_by = validated_data.get('updated_by')
        instance.is_deleted = True
        instance.save()
        return instance
#:::::::::::::: PMS PRE EXCUTION UTILITIES UTENSILS :::::::::::::#
class PreExcutionUtilitiesUtensilsAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    utensils_types=serializers.DictField(required=False)

    class Meta:
        model = PmsPreExcutionUtilitiesUtensils
        fields = (  'id', 'project', 'available', 'requirment_s_date','requirment_e_date' ,'budgeted_cost','executed_cost',
                    'created_by', 'owned_by', 'utensils_types')
    def create(self, validated_data):
        try:
            utensils=validated_data.pop('utensils_types') if 'utensils_types' in validated_data else ""
            owned_by = validated_data.get('owned_by')
            created_by = validated_data.get('created_by')
            with transaction.atomic():
                utilities_utensils=PmsPreExcutionUtilitiesUtensils.objects.create(**validated_data)
                response={
                    'id':utilities_utensils.id,
                    'project':utilities_utensils.project,
                    'available':utilities_utensils.available,
                    'requirment_s_date':utilities_utensils.requirment_s_date,
                    'requirment_e_date':utilities_utensils.requirment_e_date,
                    'budgeted_cost':utilities_utensils.budgeted_cost,
                    'executed_cost':utilities_utensils.executed_cost,
                    'created_by':utilities_utensils.created_by,
                    'owned_by':utilities_utensils.owned_by
                }
                utilities_utensils=PmsPreExcutionUtilitiesUtensilsTypes.objects.create(utensils=utilities_utensils,
                                                                                       project_id=utensils['project'],
                                                                                       type_of_utensils=utensils['type_of_utensils'],
                                                                                       quantity=utensils['quantity'],
                                                                                       rate=utensils['rate'],
                                                                                       created_by=created_by,
                                                                                       owned_by=owned_by
                                                                                       )
                utilities_utensils_dict={}
                utilities_utensils_dict['id']=utilities_utensils.id
                utilities_utensils_dict['utensils']=utilities_utensils.utensils.id
                utilities_utensils_dict['project']=utilities_utensils.project.id
                utilities_utensils_dict['type_of_utensils']=utilities_utensils.type_of_utensils
                utilities_utensils_dict['quantity']=utilities_utensils.quantity
                utilities_utensils_dict['rate']=utilities_utensils.rate
                utilities_utensils_dict['created_by']=utilities_utensils.created_by.username
                utilities_utensils_dict['owned_by']=utilities_utensils.owned_by.username
                response['utensils_types']=utilities_utensils_dict

                return response

        except Exception as e:
            return APIException ({'request_status':0,
                                'error':e,
                                'msg':settings.MSG_ERROR})
class PreExcutionUtilitiesUtensilsEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    utensils_types = serializers.DictField(required=False)
    class Meta:
        model = PmsPreExcutionUtilitiesUtensils
        fields = (
        'id', 'project', 'available', 'requirment_s_date', 'requirment_e_date', 'budgeted_cost', 'executed_cost',
        'updated_by','utensils_types')
    def update(self,instance,validated_data):
        try:
            with transaction.atomic():
                utensils = validated_data.pop('utensils_types') if 'utensils_types' in validated_data else ""

                instance.project=validated_data.get('project')
                instance.available=validated_data.get('available')
                instance.requirment_s_date=validated_data.get('requirment_s_date')
                instance.requirment_e_date=validated_data.get('requirment_e_date')
                instance.budgeted_cost=validated_data.get('budgeted_cost')
                instance.executed_cost=validated_data.get('executed_cost')
                instance.updated_by=validated_data.get('updated_by')
                instance.save()

                # PmsPreExcutionUtilitiesUtensilsTypes.objects.filter(utensils_id=instance.id).delete()

                utilities_utensils,created = PmsPreExcutionUtilitiesUtensilsTypes.objects.get_or_create(utensils_id=instance.id,
                                                                                         project_id=utensils['project'],
                                                                                         type_of_utensils=utensils[
                                                                                             'type_of_utensils'],
                                                                                         quantity=int(utensils['quantity']),
                                                                                         rate=float(utensils['rate']),
                                                                                         updated_by=instance.updated_by,

                                                                                         )
                print('created: ',created)
                print('utilities_utensils_id: ',utilities_utensils.id)
                # for utilities in utilities_utensils:
                utilities_utensils_dict = {}
                utilities_utensils_dict['id'] = utilities_utensils.id
                utilities_utensils_dict['utensils_id'] = utilities_utensils.utensils_id
                utilities_utensils_dict['project'] = utilities_utensils.project_id
                utilities_utensils_dict['type_of_utensils'] = utilities_utensils.type_of_utensils
                utilities_utensils_dict['quantity'] = utilities_utensils.quantity
                utilities_utensils_dict['rate'] = utilities_utensils.rate


                response = {
                    'id': instance.id,
                    'project': instance.project,
                    'available': instance.available,
                    'requirment_s_date': instance.requirment_s_date,
                    'requirment_e_date': instance.requirment_e_date,
                    'budgeted_cost': instance.budgeted_cost,
                    'executed_cost': instance.executed_cost,
                    'utensils_types': utilities_utensils_dict
                }
                return response

        except Exception as e:
            return APIException ({'request_status':0,
                                'error':e,
                                'msg':settings.MSG_ERROR})
class PreExcutionUtilitiesUtensilsDocumentAddSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    owned_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    model_class = serializers.CharField(required=False)

    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = ('id', 'project', 'module_id', 'document_name', 'document', 'created_by', 'owned_by','model_class')

    def create(self, validated_data):
        utensils_document = PmsPreExcutionUtilitiesDocument.objects.create(**validated_data,
                                                                                     model_class="PmsPreExcutionUtilitiesUtensilsTypes")
        return utensils_document
class PreExcutionUtilitiesUtensilsDocumentEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = ("id","document_name","updated_by")
class PreExcutionUtilitiesUtensilsDocumentDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = '__all__'

    def update(self, instance, validated_data):
        instance.updated_by = validated_data.get('updated_by')
        instance.is_deleted = True
        instance.save()
        return instance
class PreExcutionUtilitiesUtensilsTypesListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PmsPreExcutionUtilitiesUtensilsTypes
        fields = '__all__'
class PreExcutionUtilitiesUtensilsTypesEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    utensils_details=serializers.DictField(required=False)

    class Meta:
        model = PmsPreExcutionUtilitiesUtensilsTypes
        fields = ('id','project','utensils','type_of_utensils','quantity','rate','updated_by', 'utensils_details')

    def update(self, instance, validated_data):
        try:
            utensils = validated_data.pop('utensils_details') if 'utensils_details' in validated_data else ""
            with transaction.atomic():
                instance.project = validated_data.get('project')
                instance.type_of_utensils = validated_data.get('type_of_utensils')
                instance.quantity = validated_data.get('quantity')
                instance.rate = validated_data.get('rate')
                instance.updated_by = validated_data.get('updated_by')
                instance.utensils = validated_data.get('utensils')
                instance.save()

                utensils_details = PmsPreExcutionUtilitiesUtensils.objects.filter(id=instance.utensils_id,
                                                                                 project_id=instance.project_id) \

                for data in utensils_details:
                    print('project_id: ', data.project_id)
                    data.available = utensils['available']
                    data.requirment_s_date = datetime.datetime.strptime(utensils['requirment_s_date'], "%Y-%m-%dT%H:%M:%S.%fZ")
                    data.requirment_e_date = datetime.datetime.strptime(utensils['requirment_e_date'], "%Y-%m-%dT%H:%M:%S.%fZ")
                    data.budgeted_cost = utensils['budgeted_cost']
                    data.executed_cost = utensils['executed_cost']
                    data.save()
                    #
                    utensils_details_dict = {'id': data.id,
                                               'project': data.project_id,
                                               'available': data.available,
                                               'requirment_s_date': data.requirment_s_date,
                                               'requirment_e_date': data.requirment_e_date,
                                               'budgeted_cost': data.budgeted_cost,
                                               'executed_cost': data.executed_cost}

                response = {
                    'id': instance.id,
                    'project': instance.project,
                    'type_of_utensils': instance.type_of_utensils,
                    'quantity': instance.quantity,
                    'rate': instance.rate,
                    'utensils': instance.utensils,
                    'update_by': instance.updated_by,
                    'utensils_details': utensils_details_dict
                }

            return response
        except Exception as e:
            raise e
class PreExcutionUtilitiesUtensilsTypesDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsPreExcutionUtilitiesUtensilsTypes
        fields='__all__'

    def update(self, instance, validated_data):
        instance.updated_by = validated_data.get('updated_by')
        instance.is_deleted = True
        instance.save()
        PmsPreExcutionUtilitiesDocument.objects.filter(project=instance.project.id,
                                                       module_id=instance.id,
                                                       model_class="PmsPreExcutionUtilitiesUtensilsTypes"
                                                       ).update(is_deleted=True)
        return instance

#:::::::::::::: PMS PRE EXCUTION UTILITIES TIFFIN BOX :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::#
class  PreExcutionUtilitiesTiffinBoxAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    tiffin_box_types=serializers.DictField(required=False)
    class Meta:
        model = PmsPreExcutionUtilitiesTiffinBox
        fields = ( 'id', 'project', 'available', 'requirment_s_date', 'requirment_e_date', 'budgeted_cost', 'executed_cost',
        'created_by', 'owned_by', 'tiffin_box_types')
    def create(self, validated_data):
        try:
            tiffin = validated_data.pop('tiffin_box_types') if 'tiffin_box_types' in validated_data else ""
            owned_by = validated_data.get('owned_by')
            created_by = validated_data.get('created_by')
            with transaction.atomic():
                utilities_tiffin_box = PmsPreExcutionUtilitiesTiffinBox.objects.create(**validated_data)
                print('utilities_tiffin_box',utilities_tiffin_box)

                # print('response',response)
                utilities_box_types =PmsPreExcutionUtilitiesTiffinBoxTypes.objects.create(tiffin_box=utilities_tiffin_box,
                                                                                         project_id=tiffin['project'],
                                                                                         make_of_tiffin_box=tiffin[
                                                                                             'make_of_tiffin_box'],
                                                                                         quantity=tiffin['quantity'],
                                                                                         rate=tiffin['rate'],
                                                                                         created_by=created_by,
                                                                                         owned_by=owned_by
                                                                                         )
                print('utilities_box_types',utilities_box_types)
                utilities_tiffin_box_dict = {}
                utilities_tiffin_box_dict['id'] = utilities_box_types.id
                utilities_tiffin_box_dict['tiffin_box'] = utilities_box_types.tiffin_box_id
                utilities_tiffin_box_dict['project'] = utilities_box_types.project_id
                utilities_tiffin_box_dict['make_of_tiffin_box'] = utilities_box_types.make_of_tiffin_box
                utilities_tiffin_box_dict['quantity'] = utilities_box_types.quantity
                utilities_tiffin_box_dict['rate'] = utilities_box_types.rate
                # utilities_tiffin_box_dict['created_by'] = utilities_box_types.created_by.username
                # utilities_tiffin_box_dict['owned_by'] = utilities_box_types.owned_by.username
                # response['tiffin_box_types'] = utilities_tiffin_box_dict
                response = {
                    'id': utilities_tiffin_box.id,
                    'project': utilities_tiffin_box.project,
                    'available': utilities_tiffin_box.available,
                    'requirment_s_date': utilities_tiffin_box.requirment_s_date,
                    'requirment_e_date': utilities_tiffin_box.requirment_e_date,
                    'budgeted_cost': utilities_tiffin_box.budgeted_cost,
                    'executed_cost': utilities_tiffin_box.executed_cost,
                    'tiffin_box_types': utilities_tiffin_box_dict
                }
                return response

        except Exception as e:
            # raise e
            raise APIException({'request_status':0,
                                'error':e,
                                'msg':settings.MSG_ERROR})
class PreExcutionUtilitiesTiffinBoxEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    tiffin_box_types = serializers.DictField(required=False)

    class Meta:
        model = PmsPreExcutionUtilitiesTiffinBox
        fields = ( 'id', 'project', 'available', 'requirment_s_date', 'requirment_e_date', 'budgeted_cost', 'executed_cost',
        'updated_by', 'tiffin_box_types')

    def update(self, instance, validated_data):
        try:
            with transaction.atomic():
                tiffin = validated_data.pop('tiffin_box_types') if 'tiffin_box_types' in validated_data else ""

                instance.project = validated_data.get('project')
                instance.available = validated_data.get('available')
                instance.requirment_s_date = validated_data.get('requirment_s_date')
                instance.requirment_e_date = validated_data.get('requirment_e_date')
                instance.budgeted_cost = validated_data.get('budgeted_cost')
                instance.executed_cost = validated_data.get('executed_cost')
                instance.updated_by = validated_data.get('updated_by')
                instance.save()


                # PmsPreExcutionUtilitiesTiffinBoxTypes.objects.filter(tiffin_box_id=instance.id).delete()

                utilities_tiffin, created = PmsPreExcutionUtilitiesTiffinBoxTypes.objects.get_or_create(
                    tiffin_box_id=instance.id,
                    project_id=tiffin['project'],
                    make_of_tiffin_box=tiffin[
                        'make_of_tiffin_box'],
                    quantity=int(tiffin['quantity']),
                    rate=float(tiffin['rate']),
                    updated_by=instance.updated_by,

                    )
                print('created: ', created)
                print('utilities_tiffin_id: ', utilities_tiffin.id)
                # for utilities in utilities_utensils:
                utilities_tiffin_box_dict = {}
                utilities_tiffin_box_dict['id'] = utilities_tiffin.id
                utilities_tiffin_box_dict['tiffin_box_id'] = utilities_tiffin.tiffin_box_id
                utilities_tiffin_box_dict['project'] = utilities_tiffin.project_id
                utilities_tiffin_box_dict['make_of_tiffin_box'] = utilities_tiffin.make_of_tiffin_box
                utilities_tiffin_box_dict['quantity'] = utilities_tiffin.quantity
                utilities_tiffin_box_dict['rate'] = utilities_tiffin.rate

                response = {
                    'id': instance.id,
                    'project': instance.project,
                    'available': instance.available,
                    'requirment_s_date': instance.requirment_s_date,
                    'requirment_e_date': instance.requirment_e_date,
                    'budgeted_cost': instance.budgeted_cost,
                    'executed_cost': instance.executed_cost,
                    'tiffin_box_types': utilities_tiffin_box_dict
                }
                return response

        except Exception as e:
            return APIException({'request_status': 0,
                                 'error': e,
                                 'msg': settings.MSG_ERROR})
class PreExcutionUtilitiesTiffinBoxDocumentAddSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    owned_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    model_class = serializers.CharField(required=False)
    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = ('id', 'project', 'module_id', 'document_name', 'document', 'created_by', 'owned_by','model_class')

    def create(self, validated_data):
        tiffin_box_document = PmsPreExcutionUtilitiesDocument.objects.create(**validated_data,
                                                                                     model_class="PmsPreExcutionUtilitiesTiffinBoxTypes")
        return tiffin_box_document
class PreExcutionUtilitiesTiffinBoxDocumentEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = ("id","document_name","updated_by")
class PreExcutionUtilitiesTiffinBoxDocumentDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = '__all__'

    def update(self, instance, validated_data):
        instance.updated_by = validated_data.get('updated_by')
        instance.is_deleted = True
        instance.save()
        return instance
class PreExcutionUtilitiesTiffinBoxTypesListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PmsPreExcutionUtilitiesTiffinBoxTypes
        fields = '__all__'
class PreExcutionUtilitiesTiffinBoxTypesEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    tiffin_box_details = serializers.DictField(required=False)

    class Meta:
        model = PmsPreExcutionUtilitiesTiffinBoxTypes
        fields = ('id','project','tiffin_box','make_of_tiffin_box','quantity','rate','updated_by', 'tiffin_box_details')
    def update(self,instance,validated_data):
        try:
            tiffin = validated_data.pop('tiffin_box_details') if 'tiffin_box_details' in validated_data else ""
            with transaction.atomic():
                instance.project=validated_data.get('project')
                instance.make_of_tiffin_box=validated_data.get('make_of_tiffin_box')
                instance.quantity=validated_data.get('quantity')
                instance.rate=validated_data.get('rate')
                instance.updated_by=validated_data.get('updated_by')
                instance.tiffin_box=validated_data.get('tiffin_box')
                instance.save()


                tiffin_details=PmsPreExcutionUtilitiesTiffinBox.objects.filter(id=instance.tiffin_box_id,project_id=instance.project_id)\
                                                                        # .update(available=tiffin['available'],
                                                                        #         requirment_s_date=tiffin['requirment_s_date'],
                                                                        #         requirment_e_date=tiffin['requirment_e_date'],
                                                                        #         budgeted_cost=tiffin['budgeted_cost'],
                                                                        #         executed_cost=tiffin['executed_cost']
                                                                        #         ).values('available')
                # print('available:::::', type(tiffin_details['available']))
                for data in tiffin_details:
                    print('project_id: ',data.project_id)
                    data.available=tiffin['available']
                    data.requirment_s_date= datetime.datetime.strptime(tiffin['requirment_s_date'], "%Y-%m-%dT%H:%M:%S.%fZ")
                    data.requirment_e_date= datetime.datetime.strptime(tiffin['requirment_e_date'], "%Y-%m-%dT%H:%M:%S.%fZ")
                    data.budgeted_cost=tiffin['budgeted_cost']
                    data.executed_cost=tiffin['executed_cost']
                    data.save()
                #
                    tiffin_box_details_dict = {'id':data.id,
                    'project':data.project_id,
                    'available':data.available,
                    'requirment_s_date':data.requirment_s_date,
                    'requirment_e_date':data.requirment_e_date,
                    'budgeted_cost':data.budgeted_cost,
                    'executed_cost':data.executed_cost}

                response={
                    'id':instance.id,
                    'project':instance.project,
                    'make_of_tiffin_box':instance.make_of_tiffin_box,
                    'quantity':instance.quantity,
                    'rate':instance.rate,
                    'tiffin_box': instance.tiffin_box,
                    'update_by':instance.updated_by,
                    'tiffin_box_details':tiffin_box_details_dict
                }

            return response
        except Exception as e:
            raise e
class PreExcutionUtilitiesTiffinBoxTypesDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsPreExcutionUtilitiesTiffinBoxTypes
        fields='__all__'

    def update(self, instance, validated_data):
        instance.updated_by = validated_data.get('updated_by')
        instance.is_deleted = True
        instance.save()
        PmsPreExcutionUtilitiesDocument.objects.filter(project=instance.project.id,
                                                       module_id=instance.id,
                                                       model_class="PmsPreExcutionUtilitiesTiffinBoxTypes"
                                                       ).update(is_deleted=True)
        return instance

#:::::::::::::::::::::: PMS PRE EXCUTION UTILITIES COOK::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::#
class PreExcutionUtilitiesCookAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsPreExcutionUtilitiesCook
        fields = ('id', "project", "available", "cook_name", "cook_conatct_no", "chargs", "name_of_agency",
                  "agency_contact_no", "agency_addr", "latitude", "longitude", "requirment_s_date",
                  "requirment_e_date", "budgeted_cost", "executed_cost", 'created_by', 'owned_by')
class PreExcutionUtilitiesCookEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsPreExcutionUtilitiesCook
        fields = ('id', "project", "available", "cook_name", "cook_conatct_no", "chargs", "name_of_agency",
                  "agency_contact_no", "agency_addr", "latitude", "longitude", "requirment_s_date",
                  "requirment_e_date", "budgeted_cost", "executed_cost", 'updated_by')
#:::::::::::::::::::::: PMS PRE EXECUTION OFFICE SETUP MASTER:::::::::::::::::::::::::::::::::::::::::::::::::::::::#
# class PreExecutionOfficeSetupMasterAddSerializer(serializers.ModelSerializer):
#     created_by = serializers.CharField(default=serializers.CurrentUserDefault())
#     owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
#     class Meta:
#         model = PmsPreExecutionOfficeSetupMaster
#         fields = ('id', 'project', 'name', 'created_by', 'owned_by')
# class PreExecutionOfficeSetupMasterEditSerializer(serializers.ModelSerializer):
#     updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

#     class Meta:
#         model = PmsPreExecutionOfficeSetupMaster
#         fields = ('id', 'project', 'name', 'updated_by')
# class PreExecutionOfficeSetupMasterDeleteSerializer(serializers.ModelSerializer):
#     updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

#     class Meta:
#         model = PmsPreExecutionOfficeSetupMaster
#         fields = '__all__'
#     def update(self, instance, validated_data):
#         instance.is_deleted=True
#         instance.updated_by = validated_data.get('updated_by')
#         instance.save()
#         return instance

#::::::::::::PMS PRE EXCUTION OFFICE STRUCTURE:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::#
class PreExecutionOfficeStructureAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    document_details=serializers.SerializerMethodField()

    def get_document_details(self, PmsPreExecutionOfficeStructure):
        document = PmsPreExcutionUtilitiesDocument.objects.filter(project=PmsPreExecutionOfficeStructure.project.id,
                                                                  module_id=PmsPreExecutionOfficeStructure.id,
                                                                  model_class="PmsPreExecutionOfficeStructure",
                                                                  is_deleted=False)
        request = self.context.get('request')
        response_list = []
        for each_document in document:
            file_url = request.build_absolute_uri(each_document.document.url)
            owned_by = str(each_document.owned_by) if each_document.owned_by else ''
            created_by = str(each_document.created_by) if each_document.created_by else ''
            each_data = {
                "id": int(each_document.id),
                "project": int(each_document.project.id),
                "module_id": int(each_document.module_id),
                "model_class": each_document.model_class,
                "document_name": each_document.document_name,
                "document": file_url,
                "created_by": created_by,
                "owned_by": owned_by
            }
            response_list.append(each_data)
        return response_list


    class Meta:
        model = PmsPreExecutionOfficeStructure
        fields = ('id','project', 'structure_type', 'size', 'rate', 'agency_name', 'agency_contact_no',
                  'transportation_cost', 'requirment_s_date', 'requirment_e_date', 'budgeted_cost', 'executed_cost',
                  'created_by', 'owned_by','document_details')
class PreExecutionOfficeStructureEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsPreExecutionOfficeStructure
        fields = ('id','project', 'structure_type', 'size', 'rate', 'agency_name', 'agency_contact_no',
                  'transportation_cost', 'requirment_s_date', 'requirment_e_date', 'budgeted_cost', 'executed_cost',
                  'updated_by')
class PreExecutionOfficeStructureDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsPreExecutionOfficeStructure
        fields = '__all__'

    def update(self, instance, validated_data):
        try:
            with transaction.atomic():
                instance.updated_by = validated_data.get('updated_by')
                instance.is_deleted = True
                instance.save()
                return instance
        except Exception as e:
            raise e
class PreExecutionOfficeStructureDocumentAddSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    owned_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    model_class = serializers.CharField(required=False)
    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = ('id', 'project', 'module_id', 'document_name', 'document', 'created_by', 'owned_by','model_class')

    def create(self, validated_data):
        office_structure_document = PmsPreExcutionUtilitiesDocument.objects.create(**validated_data,
                                                                                     model_class="PmsPreExecutionOfficeStructure")
        return office_structure_document
class PreExecutionOfficeStructureDocumentEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = ("id","document_name","updated_by")
class PreExecutionOfficeStructureDocumentDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = '__all__'

    def update(self, instance, validated_data):
        instance.updated_by = validated_data.get('updated_by')
        instance.is_deleted = True
        instance.save()
        return instance

#:::::::::::::::::::::: PMS PRE EXECUTION ELECTRICAL CONNECTION:::::::::::::::::::::::::::#
class PreExecutionElectricalConnectionAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    document_details=serializers.SerializerMethodField(required=False)

    def get_document_details(self, PmsPreExecutionElectricalConnection):
        document = PmsPreExcutionUtilitiesDocument.objects.filter(project_id=PmsPreExecutionElectricalConnection.project.id,
                                                                  module_id=PmsPreExecutionElectricalConnection.id,
                                                                  model_class="PmsPreExecutionElectricalConnection",
                                                                  is_deleted=False)
        request = self.context.get('request')
        response_list = []
        for each_document in document:
            file_url = request.build_absolute_uri(each_document.document.url)
            owned_by = str(each_document.owned_by) if each_document.owned_by else ''
            created_by = str(each_document.created_by) if each_document.created_by else ''
            each_data = {
                "id": int(each_document.id),
                "project": int(each_document.project.id),
                "module_id": int(each_document.module_id),
                "model_class": each_document.model_class,
                "document_name": each_document.document_name,
                "document": file_url,
                "created_by": created_by,
                "owned_by": owned_by
            }
            response_list.append(each_data)
        return response_list

    class Meta:
        model = PmsPreExecutionElectricalConnection
        fields = ('id',  'project','connection_type', 'option', 'nearby_elec_off_address', 'latitude', 'longitude',
                  'contact_no', 'detailed_procedure', 'requirment_s_date', 'requirment_e_date', 'budgeted_cost', 'executed_cost',
                  'created_by', 'owned_by','document_details')
class PreExecutionElectricalConnectionEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsPreExecutionElectricalConnection
        fields = ('id',  'project','connection_type', 'option', 'nearby_elec_off_address', 'latitude', 'longitude', 'contact_no', 'detailed_procedure', 'requirment_s_date', 'requirment_e_date', 'budgeted_cost', 'executed_cost', 'updated_by')
class PreExecutionElectricalConnectionDocumentAddSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    owned_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    model_class = serializers.CharField(required=False)
    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = ('id', 'project', 'module_id', 'document_name', 'document', 'created_by', 'owned_by','model_class')

    def create(self, validated_data):
        PreExecutionElectricalConnection_document = PmsPreExcutionUtilitiesDocument.objects.create(**validated_data,
                                                                                     model_class="PmsPreExecutionElectricalConnection")
        return PreExecutionElectricalConnection_document
class PreExecutionElectricalConnectionDocumentEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = ("id","document_name","updated_by")
class PreExecutionElectricalConnectionDocumentDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = '__all__'

    def update(self, instance, validated_data):
        instance.updated_by = validated_data.get('updated_by')
        instance.is_deleted = True
        instance.save()
        return instance
#:::::::::::::::::::::: PMS PRE EXECUTION WATER CONNECTION:::::::::::::::::::::::::::#
class PreExecutionWaterConnectionAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    document_details=serializers.SerializerMethodField()

    def get_document_details(self, PmsPreExecutionWaterConnection):
        document = PmsPreExcutionUtilitiesDocument.objects.filter(project=PmsPreExecutionWaterConnection.project.id,
                                                                  module_id=PmsPreExecutionWaterConnection.id,
                                                                  model_class="PmsPreExecutionWaterConnection",
                                                                  is_deleted=False)
        request = self.context.get('request')
        response_list = []
        for each_document in document:
            file_url = request.build_absolute_uri(each_document.document.url)
            owned_by = str(each_document.owned_by) if each_document.owned_by else ''
            created_by = str(each_document.created_by) if each_document.created_by else ''
            each_data = {
                "id": int(each_document.id),
                "project": int(each_document.project.id),
                "module_id": int(each_document.module_id),
                "model_class": each_document.model_class,
                "document_name": each_document.document_name,
                "document": file_url,
                "created_by": created_by,
                "owned_by": owned_by
            }
            response_list.append(each_data)
        return response_list

    class Meta:
        model = PmsPreExecutionWaterConnection
        fields = ('id',  'project','submergible_pump_types', 'quantity', 'depth', 'contractor_name', 'con_contact_number', 'con_address', 'latitude', 'longitude', 'email_id', 'requirment_s_date', 'requirment_e_date', 'budgeted_cost', 'executed_cost', 'created_by', 'owned_by','document_details')
class PreExecutionWaterConnectionEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsPreExecutionWaterConnection
        fields = ('id',  'project','submergible_pump_types', 'quantity', 'depth', 'contractor_name', 'con_contact_number', 'con_address', 'latitude', 'longitude', 'email_id', 'requirment_s_date', 'requirment_e_date', 'budgeted_cost', 'executed_cost', 'updated_by')
class PreExecutionWaterConnectionDocumentAddSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    owned_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    model_class = serializers.CharField(required=False)
    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = ('id', 'project', 'module_id', 'document_name', 'document', 'created_by', 'owned_by','model_class')

    def create(self, validated_data):
        PreExecutionWaterConnection_document = PmsPreExcutionUtilitiesDocument.objects.create(**validated_data,
                                                                                     model_class="PmsPreExecutionWaterConnection")
        return PreExecutionWaterConnection_document
class PreExecutionWaterConnectionDocumentEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = ("id","document_name","updated_by")
class PreExecutionWaterConnectionDocumentDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = '__all__'

    def update(self, instance, validated_data):
        instance.updated_by = validated_data.get('updated_by')
        instance.is_deleted = True
        instance.save()
        return instance
#:::::::::::::::::::::: PMS PRE EXECUTION INTERNET CONNECTION:::::::::::::::::::::::::::#
class PreExecutionInternetConnectionAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    document_details=serializers.SerializerMethodField()

    def get_document_details(self, PmsPreExecutionInternetConnection):
        document = PmsPreExcutionUtilitiesDocument.objects.filter(project=PmsPreExecutionInternetConnection.project.id,
                                                                  module_id=PmsPreExecutionInternetConnection.id,
                                                                  model_class="PmsPreExecutionInternetConnection",
                                                                  is_deleted=False)
        request = self.context.get('request')
        response_list = []
        for each_document in document:
            file_url = request.build_absolute_uri(each_document.document.url)
            owned_by = str(each_document.owned_by) if each_document.owned_by else ''
            created_by = str(each_document.created_by) if each_document.created_by else ''
            each_data = {
                "id": int(each_document.id),
                "project": int(each_document.project.id),
                "module_id": int(each_document.module_id),
                "model_class": each_document.model_class,
                "document_name": each_document.document_name,
                "document": file_url,
                "created_by": created_by,
                "owned_by": owned_by
            }
            response_list.append(each_data)
        return response_list

    class Meta:
        model = PmsPreExecutionInternetConnection
        fields = ('id',  'project','connection_type', 'quantity', 'model', 'package_availed', 'price_limit', 'supplier_name', 'supplier_ph_no', 'supplier_address', 'service', 'initial_installation_charges', 'requirment_s_date', 'requirment_e_date', 'budgeted_cost', 'executed_cost', 'created_by', 'owned_by','document_details')
class PreExecutionInternetConnectionEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsPreExecutionInternetConnection
        fields = ('id',  'project','connection_type', 'quantity', 'model', 'package_availed', 'price_limit', 'supplier_name', 'supplier_ph_no', 'supplier_address', 'service', 'initial_installation_charges', 'requirment_s_date', 'requirment_e_date', 'budgeted_cost', 'executed_cost', 'updated_by')
class PreExecutionInternetConnectionDocumentAddSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    owned_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    model_class = serializers.CharField(required=False)
    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = ('id', 'project', 'module_id', 'document_name', 'document', 'created_by', 'owned_by','model_class')

    def create(self, validated_data):
        PreExecutionInternetConnection_document = PmsPreExcutionUtilitiesDocument.objects.create(**validated_data,
                                                                                     model_class="PmsPreExecutionInternetConnection")
        return PreExecutionInternetConnection_document
class PreExecutionInternetConnectionDocumentEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = ("id","document_name","updated_by")
class PreExecutionInternetConnectionDocumentDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = '__all__'

    def update(self, instance, validated_data):
        instance.updated_by = validated_data.get('updated_by')
        instance.is_deleted = True
        instance.save()
        return instance
#:::::::::::::::::::::: PMS PRE EXCUTION OFFICE SETUP FURNITURE:::::::::::::::::::::::::::#
class PreExcutionOfficeSetupFurnitureAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    document_details=serializers.SerializerMethodField()

    def get_document_details(self, PmsPreExcutionOfficeSetupFurniture):
        document = PmsPreExcutionUtilitiesDocument.objects.filter(project=PmsPreExcutionOfficeSetupFurniture.project.id,
                                                                  module_id=PmsPreExcutionOfficeSetupFurniture.id,
                                                                  model_class="PmsPreExcutionOfficeSetupFurniture",
                                                                  is_deleted=False)
        request = self.context.get('request')
        response_list = []
        for each_document in document:
            file_url = request.build_absolute_uri(each_document.document.url)
            owned_by = str(each_document.owned_by) if each_document.owned_by else ''
            created_by = str(each_document.created_by) if each_document.created_by else ''
            each_data = {
                "id": int(each_document.id),
                "project": int(each_document.project.id),
                "module_id": int(each_document.module_id),
                "model_class": each_document.model_class,
                "document_name": each_document.document_name,
                "document": file_url,
                "created_by": created_by,
                "owned_by": owned_by
            }
            response_list.append(each_data)
        return response_list

    class Meta:
        model = PmsPreExcutionOfficeSetupFurniture
        fields = ('id',  'project','furniture_type', 'brand', 'quantity', 'rate', 'supplier_name', 'supplier_ph_no', 'supplier_address', 'latitude', 'longitude', 'requirment_s_date', 'requirment_e_date', 'budgeted_cost', 'executed_cost', 'created_by', 'owned_by','document_details')
class PreExcutionOfficeSetupFurnitureEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsPreExcutionOfficeSetupFurniture
        fields = ('id',  'project','furniture_type', 'brand', 'quantity', 'rate', 'supplier_name', 'supplier_ph_no', 'supplier_address', 'latitude', 'longitude', 'requirment_s_date', 'requirment_e_date', 'budgeted_cost', 'executed_cost', 'updated_by')
class PreExcutionOfficeSetupFurnitureDocumentAddSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    owned_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    model_class = serializers.CharField(required=False)
    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = ('id', 'project', 'module_id', 'document_name', 'document', 'created_by', 'owned_by','model_class')

    def create(self, validated_data):
        PreExcutionOfficeSetupFurniture_document = PmsPreExcutionUtilitiesDocument.objects.create(**validated_data,
                                                                                     model_class="PmsPreExcutionOfficeSetupFurniture")
        return PreExcutionOfficeSetupFurniture_document
class PreExcutionOfficeSetupFurnitureDocumentEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = ("id","document_name","updated_by")
class PreExcutionOfficeSetupFurnitureDocumentDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = '__all__'

    def update(self, instance, validated_data):
        instance.updated_by = validated_data.get('updated_by')
        instance.is_deleted = True
        instance.save()
        return instance
#:::::::::::::::::::::: PMS PRE EXCUTION OFFICE SETUP COMPUTER:::::::::::::::::::::::::::#
class PreExcutionOfficeSetupComputerAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    document_details=serializers.SerializerMethodField()

    def get_document_details(self, PmsPreExcutionOfficeSetupComputer):
        document = PmsPreExcutionUtilitiesDocument.objects.filter(project=PmsPreExcutionOfficeSetupComputer.project.id,
                                                                  module_id=PmsPreExcutionOfficeSetupComputer.id,
                                                                  model_class="PmsPreExcutionOfficeSetupComputer",
                                                                  is_deleted=False)
        request = self.context.get('request')
        response_list = []
        for each_document in document:
            file_url = request.build_absolute_uri(each_document.document.url)
            owned_by = str(each_document.owned_by) if each_document.owned_by else ''
            created_by = str(each_document.created_by) if each_document.created_by else ''
            each_data = {
                "id": int(each_document.id),
                "project": int(each_document.project.id),
                "module_id": int(each_document.module_id),
                "model_class": each_document.model_class,
                "document_name": each_document.document_name,
                "document": file_url,
                "created_by": created_by,
                "owned_by": owned_by
            }
            response_list.append(each_data)
        return response_list

    class Meta:
        model = PmsPreExcutionOfficeSetupComputer
        fields = ('id',  'project','computer_type', 'brand', 'quantity', 'rate', 'supplier_name', 'supplier_ph_no', 'supplier_address', 'latitude', 'longitude', 'requirment_s_date', 'requirment_e_date', 'budgeted_cost', 'executed_cost', 'created_by', 'owned_by','document_details')
class PreExcutionOfficeSetupComputerEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsPreExcutionOfficeSetupComputer
        fields = ('id',  'project','computer_type', 'brand', 'quantity', 'rate', 'supplier_name', 'supplier_ph_no', 'supplier_address', 'latitude', 'longitude', 'requirment_s_date', 'requirment_e_date', 'budgeted_cost', 'executed_cost', 'updated_by')
class PreExcutionOfficeSetupComputerDocumentAddSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    owned_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    model_class = serializers.CharField(required=False)
    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = ('id', 'project', 'module_id', 'document_name', 'document', 'created_by', 'owned_by','model_class')

    def create(self, validated_data):
        PreExcutionOfficeSetupComputer_document = PmsPreExcutionUtilitiesDocument.objects.create(**validated_data,
                                                                                     model_class="PmsPreExcutionOfficeSetupComputer")
        return PreExcutionOfficeSetupComputer_document
class PreExcutionOfficeSetupComputerDocumentEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = ("id","document_name","updated_by")
class PreExcutionOfficeSetupComputerDocumentDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = '__all__'

    def update(self, instance, validated_data):
        instance.updated_by = validated_data.get('updated_by')
        instance.is_deleted = True
        instance.save()
        return instance

#:::::::::::::::::::::::::::::PMS PRE EXCUTION OFFICE SETUP STATIONARY::::::::::::::::::::::::::::::::::::::::::::::::::#
class PreExecutionOfficeSetupStationaryAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    stationary_details = serializers.DictField(required=False)
    class Meta:
        model=PmsPreExcutionOfficeSetupStationary
        fields=('id','project','requirment_s_date','requirment_e_date','budgeted_cost','executed_cost','created_by',
                'owned_by','stationary_details')
    def create(self, validated_data):
        try:
            stationary = validated_data.pop('stationary_details') if 'stationary_details' in validated_data else ""
            owned_by = validated_data.get('owned_by')
            created_by = validated_data.get('created_by')
            with transaction.atomic():
                office_setup_stationary = PmsPreExcutionOfficeSetupStationary.objects.create(**validated_data)
                # print('office_setup_stationary: ', office_setup_stationary)

                # print('response',response)
                stationary_types = PmsPreExcutionOfficeSetupStationaryMStnRequirements.objects.create(
                    stn_requirements=office_setup_stationary,
                    project_id=stationary['project'],
                    item=stationary['item'],
                    quantity=stationary['quantity'],
                    rate=stationary['rate'],
                    supplier_name=stationary['supplier_name'],
                    supplier_ph_no=stationary['supplier_ph_no'],
                    created_by=created_by,
                    owned_by=owned_by
                    )
                print('stationary_types', stationary_types)
                stationary_types_dict = {}
                stationary_types_dict['id'] = stationary_types.id
                stationary_types_dict['stn_requirements'] = stationary_types.stn_requirements_id
                stationary_types_dict['project'] = stationary_types.project_id
                stationary_types_dict['item'] = stationary_types.item
                stationary_types_dict['quantity'] = stationary_types.quantity
                stationary_types_dict['rate'] = stationary_types.rate
                stationary_types_dict['supplier_name'] = stationary_types.supplier_name
                stationary_types_dict['supplier_ph_no'] = stationary_types.supplier_ph_no

                response = {
                    'id': office_setup_stationary.id,
                    'project': office_setup_stationary.project,
                    'requirment_s_date': office_setup_stationary.requirment_s_date,
                    'requirment_e_date': office_setup_stationary.requirment_e_date,
                    'budgeted_cost': office_setup_stationary.budgeted_cost,
                    'executed_cost': office_setup_stationary.executed_cost,
                    'stationary_details': stationary_types_dict
                }
                return response

        except Exception as e:
            # raise e
            return APIException({'request_status': 0,
                                'error': e,
                                'msg': settings.MSG_ERROR})
class PreExecutionOfficeSetupStationaryEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    stationary_details = serializers.DictField(required=False)
    class Meta:
        model = PmsPreExcutionOfficeSetupStationary
        fields = ('id', 'project','requirment_s_date', 'requirment_e_date', 'budgeted_cost', 'executed_cost',
        'updated_by','stationary_details')

    def update(self,instance,validated_data):
        # print("validated_data: ", validated_data)
        try:
            stationary = validated_data.pop('stationary_details') if 'stationary_details' in validated_data else ""
            updated_by = validated_data.get('updated_by')
            with transaction.atomic():
                instance.project = validated_data.get('project')
                instance.requirment_s_date = validated_data.get('requirment_s_date')
                instance.requirment_e_date = validated_data.get('requirment_e_date')
                instance.budgeted_cost = validated_data.get('budgeted_cost')
                instance.executed_cost = validated_data.get('executed_cost')
                instance.updated_by = updated_by
                instance.save()

                stationary_requirements = PmsPreExcutionOfficeSetupStationaryMStnRequirements.objects.create(
                                                                                            stn_requirements =instance,
                                                                                            **stationary,
                                                                                            created_by=updated_by
                                                                                            )

                stationary_types_dict = {}
                stationary_types_dict['id'] = stationary_requirements.id
                stationary_types_dict['stn_requirements'] = stationary_requirements.stn_requirements_id
                stationary_types_dict['project'] = stationary_requirements.project_id
                stationary_types_dict['item'] = stationary_requirements.item
                stationary_types_dict['quantity'] = stationary_requirements.quantity
                stationary_types_dict['rate'] = stationary_requirements.rate
                stationary_types_dict['supplier_name'] = stationary_requirements.supplier_name
                stationary_types_dict['supplier_ph_no'] = stationary_requirements.supplier_ph_no

                instance.__dict__["stationary_details"] = stationary_types_dict

                return instance

        except Exception as e:
            raise e
            # return APIException({'request_status': 0,
            #                      'error': e,
            #                      'msg': settings.MSG_ERROR})
class PreExecutionOfficeSetupStationaryRequirementsDocumentAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    model_class = serializers.CharField(required=False)
    class Meta:
        model=PmsPreExcutionUtilitiesDocument
        fields=('id','project','module_id','document_name','document','created_by','owned_by','model_class')
    def create(self, validated_data):
        stationary_requirements_document = PmsPreExcutionUtilitiesDocument.objects.create(**validated_data,
                                                                             model_class="PmsPreExcutionOfficeSetupStationaryMStnRequirements")
        return stationary_requirements_document
class PreExecutionOfficeSetupStationaryRequirementsDocumentEditSerializer(serializers.ModelSerializer):
    updated_by=serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model=PmsPreExcutionUtilitiesDocument
        fields=('id','document_name','updated_by')
class PreExecutionOfficeSetupStationaryRequirementsDocumentDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model=PmsPreExcutionUtilitiesDocument
        fields='__all__'
    def update(self,instance,validated_data):
        instance.is_deleted=True
        instance.updated_by=validated_data.get('updated_by')
        instance.save()
        return instance
class PreExecutionOfficeSetupStationaryRequirementsListSerializer(serializers.ModelSerializer):
    class Meta:
        model=PmsPreExcutionOfficeSetupStationaryMStnRequirements
        fields='__all__'
class PreExecutionOfficeSetupStationaryRequirementsEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    stationary_details=serializers.DictField(required=False)
    class Meta:
        model=PmsPreExcutionOfficeSetupStationaryMStnRequirements
        fields=('id','stn_requirements','project','item','quantity','rate','supplier_name','supplier_ph_no','updated_by',
                'stationary_details')
    def update(self,instance,validated_data):
        try:
            stationary=validated_data.pop('stationary_details') if 'stationary_details' in validated_data else ""
            updated_by=validated_data.get('updated_by')
            with transaction.atomic():
                instance.stn_requirements=validated_data.get('stn_requirements')
                instance.project=validated_data.get('project')
                instance.item=validated_data.get('item')
                instance.quantity=validated_data.get('quantity')
                instance.rate=validated_data.get('rate')
                instance.supplier_name=validated_data.get('supplier_name')
                instance.supplier_ph_no=validated_data.get('supplier_ph_no')
                instance.updated_by=updated_by
                instance.save()

                # print('instance',instance)

                stationary_details=PmsPreExcutionOfficeSetupStationary.objects.filter(id=instance.stn_requirements_id,
                                                                                      project=instance.project)
                # print("stationary: ", stationary)
                # print('stationary_details',stationary_details)
                for data in stationary_details:
                    #print('requirment_s_date',data.requirment_s_date)
                    data.requirment_s_date=datetime.datetime.strptime(stationary['requirment_s_date'], "%Y-%m-%dT%H:%M:%S.%fZ")
                    data.requirment_e_date=datetime.datetime.strptime(stationary['requirment_e_date'], "%Y-%m-%dT%H:%M:%S.%fZ")
                    data.budgeted_cost=stationary['budgeted_cost']
                    data.executed_cost=stationary['executed_cost']
                    data.save()
                    stationary_details_dict = {'id': data.id,
                                               'project': data.project_id,
                                               'requirment_s_date': data.requirment_s_date,
                                               'requirment_e_date': data.requirment_e_date,
                                               'budgeted_cost': data.budgeted_cost,
                                               'executed_cost': data.executed_cost
                                               }

                instance.__dict__['stationary_details']=stationary_details_dict

                return instance
        except Exception as e:
            raise APIException({'request_status':0,
                                'msg':settings.MSG_ERROR,
                                'error':e})
class PreExecutionOfficeSetupStationaryRequirementsDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsPreExcutionOfficeSetupStationaryMStnRequirements
        fields = '__all__'

    def update(self, instance, validated_data):
        instance.updated_by = validated_data.get('updated_by')
        instance.is_deleted = True
        instance.save()
        PmsPreExcutionUtilitiesDocument.objects.filter(project=instance.project.id,
                                                       module_id=instance.id,
                                                       model_class="PmsPreExcutionOfficeSetupStationaryMStnRequirements"
                                                       ).update(is_deleted=True)
        return instance

#::::::::::::::::::::PMS PRE EXCUTION OFFICE SETUP TOILET::::::::::::::::::::::::::::::::::::::::::::#
class PreExcutionOfficeSetupToiletAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    document_details=serializers.SerializerMethodField()

    def get_document_details(self, PmsPreExcutionOfficeSetupToilet):
        document = PmsPreExcutionUtilitiesDocument.objects.filter(project=PmsPreExcutionOfficeSetupToilet.project.id,
                                                                  module_id=PmsPreExcutionOfficeSetupToilet.id,
                                                                  model_class="PmsPreExcutionOfficeSetupToilet",
                                                                  is_deleted=False)
        request = self.context.get('request')
        response_list = []
        for each_document in document:
            file_url = request.build_absolute_uri(each_document.document.url)
            owned_by = str(each_document.owned_by) if each_document.owned_by else ''
            created_by = str(each_document.created_by) if each_document.created_by else ''
            each_data = {
                "id": int(each_document.id),
                "project": int(each_document.project.id),
                "module_id": int(each_document.module_id),
                "model_class": each_document.model_class,
                "document_name": each_document.document_name,
                "document": file_url,
                "created_by": created_by,
                "owned_by": owned_by
            }
            response_list.append(each_data)
        return response_list

    class Meta:
        model = PmsPreExcutionOfficeSetupToilet
        fields = ('id',  'project','toi_available', 'existing_arrangement', 'details','rate', 'requirment_s_date', 'requirment_e_date', 'budgeted_cost', 'executed_cost', 'created_by', 'owned_by','document_details')
class PreExcutionOfficeSetupToiletEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsPreExcutionOfficeSetupToilet
        fields = ('id',  'project','toi_available', 'existing_arrangement', 'details','rate', 'requirment_s_date', 'requirment_e_date', 'budgeted_cost', 'executed_cost', 'updated_by')
class PreExcutionOfficeSetupToiletDocumentAddSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    owned_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    model_class = serializers.CharField(required=False)
    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = ('id', 'project', 'module_id', 'document_name', 'document', 'created_by', 'owned_by','model_class')

    def create(self, validated_data):
        PreExcutionOfficeSetupToilet_document = PmsPreExcutionUtilitiesDocument.objects.create(**validated_data,
                                                                                     model_class="PmsPreExcutionOfficeSetupToilet")
        return PreExcutionOfficeSetupToilet_document
class PreExcutionOfficeSetupToiletDocumentEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = ("id","document_name","updated_by")
class PreExcutionOfficeSetupToiletDocumentDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = '__all__'

    def update(self, instance, validated_data):
        instance.updated_by = validated_data.get('updated_by')
        instance.is_deleted = True
        instance.save()
        return instance
#:::::::::::::::::::::: PMS PRE EXCUTION OFFICE SETUP VEHICLE:::::::::::::::::::::::::::#
class  PreExcutionOfficeSetupVehicleAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    vehicle_driver = serializers.ListField(required=False)
    document_details = serializers.SerializerMethodField(required=False)

    def get_document_details(self,PmsPreExcutionOfficeSetupVehicle):
        document = PmsPreExcutionUtilitiesDocument.objects.filter(project=PmsPreExcutionOfficeSetupVehicle.project.id,
                                                                  module_id=PmsPreExcutionOfficeSetupVehicle.id,
                                                                  model_class="PmsPreExcutionOfficeSetupVehicle",
                                                                  is_deleted=False)
        request = self.context.get('request')
        response_list = []
        for each_document in document:
            file_url = request.build_absolute_uri(each_document.document.url)
            owned_by = str(each_document.owned_by) if each_document.owned_by else ''
            created_by = str(each_document.created_by) if each_document.created_by else ''
            each_data = {
                "id": int(each_document.id),
                "project": int(each_document.project.id),
                "module_id": int(each_document.module_id),
                "model_class": each_document.model_class,
                "document_name": each_document.document_name,
                "document": file_url,
                "created_by": created_by,
                "owned_by": owned_by
            }
            response_list.append(each_data)
        return response_list

    class Meta:
        model = PmsPreExcutionOfficeSetupVehicle
        fields = ( 'id', 'project','vehicle_type', 'vehicle_model', 'vehicle_details','vehicle_cost','Rate_per_day',
                   'quantity', 'owner_name', 'owner_contact_details', 'requirment_s_date', 'requirment_e_date',
                   'budgeted_cost', 'executed_cost', 'created_by', 'owned_by', 'vehicle_driver','document_details')
    def create(self, validated_data):

        try:
            driver = validated_data.pop('vehicle_driver') if 'vehicle_driver' in validated_data else ""
            owned_by = validated_data.get('owned_by')
            created_by = validated_data.get('created_by')
            driver_list=list()
            # print("driver ",driver)
            with transaction.atomic():
                vehicle_data, created1 = PmsPreExcutionOfficeSetupVehicle.objects.get_or_create(**validated_data)

                for v_d in driver:
                    driver_data, created2 = PmsPreExcutionOfficeSetupVehicleDriver.objects.get_or_create(
                        vehicle_driver=vehicle_data,
                        created_by=created_by,
                        owned_by=owned_by,
                        **v_d
                        )
                    # print('created2:: ',created2)
                    # print('driver_data::',driver_data.__dict__)
                    driver_data.__dict__.pop('_state') if "_state" in driver_data.__dict__.keys() else driver_data.__dict__

                    # print('driver_data222::', driver_data.__dict__)
                    driver_list.append(driver_data.__dict__)
                # print('driver_list',driver_list)

                vehicle_data.__dict__["vehicle_driver"] = driver_list

                return vehicle_data

        except Exception as e:
            # raise e
            raise APIException({'request_status':0,
                                'error':e,
                                'msg':settings.MSG_ERROR})
class PreExcutionOfficeSetupVehicleEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    vehicle_driver = serializers.ListField(required=False)

    class Meta:
        model = PmsPreExcutionOfficeSetupVehicle
        fields = ('id', 'project','vehicle_type', 'vehicle_model', 'vehicle_details','vehicle_cost','Rate_per_day',
                  'quantity', 'owner_name', 'owner_contact_details', 'requirment_s_date', 'requirment_e_date',
                  'budgeted_cost', 'executed_cost', 'updated_by', 'vehicle_driver')

    def update(self, instance, validated_data):
        print("validated_data ", validated_data)
        try:
            driver_list=list()
            with transaction.atomic():
                driver = validated_data.pop('vehicle_driver') if 'vehicle_driver' in validated_data else ""

                instance.project = validated_data.get('project')
                instance.vehicle_type = validated_data.get('vehicle_type')
                instance.vehicle_model = validated_data.get('vehicle_model')
                instance.vehicle_details = validated_data.get('vehicle_details')
                instance.vehicle_cost = validated_data.get('vehicle_cost')
                instance.Rate_per_day = validated_data.get('Rate_per_day')
                instance.quantity = validated_data.get('quantity')
                instance.owner_name = validated_data.get('owner_name')
                instance.owner_contact_details = validated_data.get('owner_contact_details')
                instance.requirment_s_date = validated_data.get('requirment_s_date')
                instance.requirment_e_date = validated_data.get('requirment_e_date')
                instance.budgeted_cost = validated_data.get('budgeted_cost')
                instance.executed_cost = validated_data.get('executed_cost')
                instance.updated_by = validated_data.get('updated_by')
                instance.save()
                for v_d in driver:
                    driver_data, created = PmsPreExcutionOfficeSetupVehicleDriver.objects.get_or_create(
                                                                                                vehicle_driver=instance,
                                                                                                **v_d,
                                                                                                created_by=instance.updated_by,
                                                                                                owned_by=instance.updated_by
                                                                                                )
                    driver_data.__dict__.pop('_state') if "_state" in driver_data.__dict__.keys() else driver_data.__dict__

                    driver_list.append(driver_data.__dict__)

                instance.__dict__["vehicle_driver"] = driver_list
                return instance

        except Exception as e:
            # raise e
            return APIException({'request_status': 0,
                                 'error': e,
                                 'msg': settings.MSG_ERROR})
class PreExcutionOfficeSetupVehicleDocumentAddSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    owned_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    model_class = serializers.CharField(required=False)
    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = ('id', 'project', 'module_id', 'document_name', 'document', 'created_by', 'owned_by','model_class')

    def create(self, validated_data):
        PreExcutionOfficeSetupVehicle_document = PmsPreExcutionUtilitiesDocument.objects.create(**validated_data,
                                                                                     model_class="PmsPreExcutionOfficeSetupVehicle")
        return PreExcutionOfficeSetupVehicle_document
class PreExcutionOfficeSetupVehicleDocumentEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = ("id","document_name","updated_by")
class PreExcutionOfficeSetupVehicleDocumentDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = '__all__'

    def update(self, instance, validated_data):
        instance.updated_by = validated_data.get('updated_by')
        instance.is_deleted = True
        instance.save()
        return instance
class PreExcutionOfficeSetupVehicleDriverListSerializer(serializers.ModelSerializer):
    class Meta:
        model=PmsPreExcutionOfficeSetupVehicleDriver
        fields='__all__'
class PreExcutionOfficeSetupVehicleDriverEditSerializer(serializers.ModelSerializer):
    updated_by=serializers.CharField(default=serializers.CurrentUserDefault())
    vehicle_details=serializers.DictField(required=False)
    class Meta:
        model=PmsPreExcutionOfficeSetupVehicleDriver
        fields='__all__'
        extra_fields=('vehicle_details')
    def update(self, instance, validated_data):
        try:
            vehicle = validated_data.pop('vehicle_details') if 'vehicle_details' in validated_data else ""
            updated_by = validated_data.get('updated_by')
            with transaction.atomic():
                instance.vehicle_driver=validated_data.get('vehicle_driver')
                # print('vehicle_driver',instance.vehicle_driver)
                instance.project=validated_data.get('project')
                instance.driver_name=validated_data.get('driver_name')
                instance.driver_contact_details=validated_data.get('driver_contact_details')
                instance.vehicle_numberplate=validated_data.get('vehicle_numberplate')
                instance.updated_by=updated_by
                instance.save()

                vehicle_data =PmsPreExcutionOfficeSetupVehicle.objects.filter(id=instance.vehicle_driver_id,
                                                                              project=instance.project)
                # print('vehicle_data',vehicle_data)
                for data in vehicle_data:
                    # print('data', data.vehicle_model)
                    data.vehicle_type=vehicle['vehicle_type']
                    data.vehicle_model=vehicle['vehicle_model']
                    data.vehicle_details=vehicle['vehicle_details']
                    data.vehicle_cost=vehicle['vehicle_cost']
                    data.Rate_per_day=vehicle['Rate_per_day']
                    data.quantity=vehicle['quantity']
                    data.owner_name=vehicle['owner_name']
                    data.owner_contact_details=vehicle['owner_contact_details']
                    data.requirment_s_date= datetime.datetime.strptime(vehicle['requirment_s_date'], "%Y-%m-%dT%H:%M:%S.%fZ")
                    data.requirment_e_date= datetime.datetime.strptime(vehicle['requirment_e_date'], "%Y-%m-%dT%H:%M:%S.%fZ")
                    data.budgeted_cost=vehicle['budgeted_cost']
                    data.executed_cost=vehicle['executed_cost']
                    data.updated_by=updated_by
                    data.save()
                    # print('dta',data.__dict__)

                    data.__dict__.pop('_state') if '_state' in data.__dict__.keys() else data
                    # print('data.__dict__',data.__dict__)

                instance.__dict__['vehicle_details']=data.__dict__

                return instance

        except Exception as e:
            # raise e
            return APIException({'request_status': 0,
                                 'error': e,
                                 'msg': settings.MSG_ERROR})
class PreExcutionOfficeSetupVehicleDriverDeleteSerializer(serializers.ModelSerializer):
    updated_by=serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model=PmsPreExcutionOfficeSetupVehicleDriver
        fields='__all__'

    def update(self, instance, validated_data):
        instance.updated_by = validated_data.get('updated_by')
        instance.is_deleted = True
        instance.save()
        return instance
#:::::::::::::::::::::: PMS PRE EXECUTION OFFICE SETUP BIKE:::::::::::::::::::::::::::#
class PreExecutionOfficeSetupBikeAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    document_details=serializers.SerializerMethodField()

    def get_document_details(self, PmsPreExecutionOfficeSetupBike):
        document = PmsPreExcutionUtilitiesDocument.objects.filter(project=PmsPreExecutionOfficeSetupBike.project.id,
                                                                  module_id=PmsPreExecutionOfficeSetupBike.id,
                                                                  model_class="PmsPreExecutionOfficeSetupBike",
                                                                  is_deleted=False)
        request = self.context.get('request')
        response_list = []
        for each_document in document:
            file_url = request.build_absolute_uri(each_document.document.url)
            owned_by = str(each_document.owned_by) if each_document.owned_by else ''
            created_by = str(each_document.created_by) if each_document.created_by else ''
            each_data = {
                "id": int(each_document.id),
                "project": int(each_document.project.id),
                "module_id": int(each_document.module_id),
                "model_class": each_document.model_class,
                "document_name": each_document.document_name,
                "document": file_url,
                "created_by": created_by,
                "owned_by": owned_by
            }
            response_list.append(each_data)
        return response_list

    class Meta:
        model = PmsPreExecutionOfficeSetupBike
        fields = ('id',  'project','bike_model', 'bike_details', 'bike_cost', 'quantity', 'requirment_s_date', 'requirment_e_date', 'budgeted_cost', 'executed_cost', 'created_by', 'owned_by','document_details')
class PreExecutionOfficeSetupBikeEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsPreExecutionOfficeSetupBike
        fields = ('id',  'project','bike_model', 'bike_details', 'bike_cost', 'quantity', 'requirment_s_date', 'requirment_e_date', 'budgeted_cost', 'executed_cost', 'updated_by')
class PreExecutionOfficeSetupBikeDocumentAddSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    owned_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    model_class = serializers.CharField(required=False)
    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = ('id', 'project', 'module_id', 'document_name', 'document', 'created_by', 'owned_by','model_class')

    def create(self, validated_data):
        PreExecutionOfficeSetupBike_document = PmsPreExcutionUtilitiesDocument.objects.create(**validated_data,
                                                                                     model_class="PmsPreExecutionOfficeSetupBike")
        return PreExecutionOfficeSetupBike_document
class PreExecutionOfficeSetupBikeDocumentEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = ("id","document_name","updated_by")
class PreExecutionOfficeSetupBikeDocumentDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = '__all__'

    def update(self, instance, validated_data):
        instance.updated_by = validated_data.get('updated_by')
        instance.is_deleted = True
        instance.save()
        return instance
#:::::::::::::::::::::: PMS PRE EXECUTION OFFICE SETUP LABOUR LABOUR HUTMENT:::::::::::::::::::::::::::#
class PreExecutionOfficeSetupLabourLabourHutmentAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    document_details=serializers.SerializerMethodField()

    def get_document_details(self, PmsPreExecutionOfficeSetupLabourLabourHutment):
        document = PmsPreExcutionUtilitiesDocument.objects.filter(project=PmsPreExecutionOfficeSetupLabourLabourHutment.project.id,
                                                                  module_id=PmsPreExecutionOfficeSetupLabourLabourHutment.id,
                                                                  model_class="PmsPreExecutionOfficeSetupLabourLabourHutment",
                                                                  is_deleted=False)
        request = self.context.get('request')
        response_list = []
        for each_document in document:
            file_url = request.build_absolute_uri(each_document.document.url)
            owned_by = str(each_document.owned_by) if each_document.owned_by else ''
            created_by = str(each_document.created_by) if each_document.created_by else ''
            each_data = {
                "id": int(each_document.id),
                "project": int(each_document.project.id),
                "module_id": int(each_document.module_id),
                "model_class": each_document.model_class,
                "document_name": each_document.document_name,
                "document": file_url,
                "created_by": created_by,
                "owned_by": owned_by
            }
            response_list.append(each_data)
        return response_list

    class Meta:
        model = PmsPreExecutionOfficeSetupLabourLabourHutment
        fields = ('id',  'project', 'hut_type', 'area_of_hut', 'capacity_of_manpower', 'total_cost', 'contractor_name', 'phone_no', 'address', 'latitude', 'longitude', 'requirment_s_date', 'requirment_e_date', 'budgeted_cost', 'executed_cost', 'created_by', 'owned_by','document_details')
class PreExecutionOfficeSetupLabourLabourHutmentEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsPreExecutionOfficeSetupLabourLabourHutment
        fields = ('id',  'project','hut_type', 'area_of_hut', 'capacity_of_manpower', 'total_cost', 'contractor_name', 'phone_no', 'address', 'latitude', 'longitude', 'requirment_s_date', 'requirment_e_date', 'budgeted_cost', 'executed_cost', 'updated_by')
class PreExecutionOfficeSetupLabourLabourHutmentDocumentAddSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    owned_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    model_class = serializers.CharField(required=False)
    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = ('id', 'project', 'module_id', 'document_name', 'document', 'created_by', 'owned_by','model_class')

    def create(self, validated_data):
        PreExecutionOfficeSetupLabourLabourHutment_document = PmsPreExcutionUtilitiesDocument.objects.create(**validated_data,
                                                                                     model_class="PmsPreExecutionOfficeSetupLabourLabourHutment")
        return PreExecutionOfficeSetupLabourLabourHutment_document
class PreExecutionOfficeSetupLabourLabourHutmentDocumentEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = ("id","document_name","updated_by")
class PreExecutionOfficeSetupLabourLabourHutmentDocumentDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = '__all__'

    def update(self, instance, validated_data):
        instance.updated_by = validated_data.get('updated_by')
        instance.is_deleted = True
        instance.save()
        return instance
#:::::::::::::::::::::: PMS PRE EXECUTION OFFICE SETUP LABOUR TOILET:::::::::::::::::::::::::::#
class PreExecutionOfficeSetupLabourToiletAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    document_details=serializers.SerializerMethodField()

    def get_document_details(self, PmsPreExecutionOfficeSetupLabourToilet):
        document = PmsPreExcutionUtilitiesDocument.objects.filter(project=PmsPreExecutionOfficeSetupLabourToilet.project.id,
                                                                  module_id=PmsPreExecutionOfficeSetupLabourToilet.id,
                                                                  model_class="PmsPreExecutionOfficeSetupLabourToilet",
                                                                  is_deleted=False)
        request = self.context.get('request')
        response_list = []
        for each_document in document:
            file_url = request.build_absolute_uri(each_document.document.url)
            owned_by = str(each_document.owned_by) if each_document.owned_by else ''
            created_by = str(each_document.created_by) if each_document.created_by else ''
            each_data = {
                "id": int(each_document.id),
                "project": int(each_document.project.id),
                "module_id": int(each_document.module_id),
                "model_class": each_document.model_class,
                "document_name": each_document.document_name,
                "document": file_url,
                "created_by": created_by,
                "owned_by": owned_by
            }
            response_list.append(each_data)
        return response_list

    class Meta:
        model = PmsPreExecutionOfficeSetupLabourToilet
        fields = ('id',  'project','toi_available', 'existing_arrangement', 'details','rate' ,'requirment_s_date', 'requirment_e_date', 'budgeted_cost', 'executed_cost', 'created_by', 'owned_by','document_details')
class PreExecutionOfficeSetupLabourToiletEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsPreExecutionOfficeSetupLabourToilet
        fields = ('id',  'project','toi_available', 'existing_arrangement', 'details','rate', 'requirment_s_date', 'requirment_e_date', 'budgeted_cost', 'executed_cost', 'updated_by')
class PreExecutionOfficeSetupLabourToiletDocumentAddSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    owned_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    model_class = serializers.CharField(required=False)
    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = ('id', 'project', 'module_id', 'document_name', 'document', 'created_by', 'owned_by','model_class')

    def create(self, validated_data):
        PreExecutionOfficeSetupLabourToilet_document = PmsPreExcutionUtilitiesDocument.objects.create(**validated_data,
                                                                                     model_class="PmsPreExecutionOfficeSetupLabourToilet")
        return PreExecutionOfficeSetupLabourToilet_document
class PreExecutionOfficeSetupLabourToiletDocumentEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = ("id","document_name","updated_by")
class PreExecutionOfficeSetupLabourToiletDocumentDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = '__all__'

    def update(self, instance, validated_data):
        instance.updated_by = validated_data.get('updated_by')
        instance.is_deleted = True
        instance.save()
        return instance
#:::::::::::::::::::::: PMS PRE EXECUTION OFFICE SETUP LABOUR WATER CONNECTION:::::::::::::::::::::::::::#
class PreExecutionOfficeSetupLabourWaterConnectionAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    document_details=serializers.SerializerMethodField()

    def get_document_details(self, PmsPreExecutionOfficeSetupLabourWaterConnection):
        document = PmsPreExcutionUtilitiesDocument.objects.filter(project=PmsPreExecutionOfficeSetupLabourWaterConnection.project.id,
                                                                  module_id=PmsPreExecutionOfficeSetupLabourWaterConnection.id,
                                                                  model_class="PmsPreExecutionOfficeSetupLabourWaterConnection",
                                                                  is_deleted=False)
        request = self.context.get('request')
        response_list = []
        for each_document in document:
            file_url = request.build_absolute_uri(each_document.document.url)
            owned_by = str(each_document.owned_by) if each_document.owned_by else ''
            created_by = str(each_document.created_by) if each_document.created_by else ''
            each_data = {
                "id": int(each_document.id),
                "project": int(each_document.project.id),
                "module_id": int(each_document.module_id),
                "model_class": each_document.model_class,
                "document_name": each_document.document_name,
                "document": file_url,
                "created_by": created_by,
                "owned_by": owned_by
            }
            response_list.append(each_data)
        return response_list

    class Meta:
        model = PmsPreExecutionOfficeSetupLabourWaterConnection
        fields = ('id',  'project','borewell_for_drinking_water', 'quantity', 'depth', 'contractor_name', 'con_contact_number', 'con_address', 'latitude', 'longitude', 'email_id', 'requirment_s_date', 'requirment_e_date', 'budgeted_cost', 'executed_cost', 'created_by', 'owned_by','document_details')
class PreExecutionOfficeSetupLabourWaterConnectionEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsPreExecutionOfficeSetupLabourWaterConnection
        fields = ('id',  'project','borewell_for_drinking_water', 'quantity', 'depth', 'contractor_name', 'con_contact_number', 'con_address', 'latitude', 'longitude', 'email_id', 'requirment_s_date', 'requirment_e_date', 'budgeted_cost', 'executed_cost', 'updated_by')
class PreExecutionOfficeSetupLabourWaterConnectionDocumentAddSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    owned_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    model_class = serializers.CharField(required=False)
    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = ('id', 'project', 'module_id', 'document_name', 'document', 'created_by', 'owned_by','model_class')

    def create(self, validated_data):
        PreExecutionOfficeSetupLabourWaterConnection_document = PmsPreExcutionUtilitiesDocument.objects.create(**validated_data,
                                                                                     model_class="PmsPreExecutionOfficeSetupLabourWaterConnection")
        return PreExecutionOfficeSetupLabourWaterConnection_document
class PreExecutionOfficeSetupLabourWaterConnectionDocumentEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = ("id","document_name","updated_by")
class PreExecutionOfficeSetupLabourWaterConnectionDocumentDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = '__all__'

    def update(self, instance, validated_data):
        instance.updated_by = validated_data.get('updated_by')
        instance.is_deleted = True
        instance.save()
        return instance
#:::::::::::::::::::::: PMS PRE EXECUTION OFFICE SETUP LABOUR ELECTRICAL CONNECTION:::::::::::::::::::::::::::#
class PreExecutionOfficeSetupLabourElectricalConnectionAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    document_details=serializers.SerializerMethodField()

    def get_document_details(self, PmsPreExecutionOfficeSetupLabourElectricalConnection):
        document = PmsPreExcutionUtilitiesDocument.objects.filter(project=PmsPreExecutionOfficeSetupLabourElectricalConnection.project.id,
                                                                  module_id=PmsPreExecutionOfficeSetupLabourElectricalConnection.id,
                                                                  model_class="PmsPreExecutionOfficeSetupLabourElectricalConnection",
                                                                  is_deleted=False)
        request = self.context.get('request')
        response_list = []
        for each_document in document:
            file_url = request.build_absolute_uri(each_document.document.url)
            owned_by = str(each_document.owned_by) if each_document.owned_by else ''
            created_by = str(each_document.created_by) if each_document.created_by else ''
            each_data = {
                "id": int(each_document.id),
                "project": int(each_document.project.id),
                "module_id": int(each_document.module_id),
                "model_class": each_document.model_class,
                "document_name": each_document.document_name,
                "document": file_url,
                "created_by": created_by,
                "owned_by": owned_by
            }
            response_list.append(each_data)
        return response_list

    class Meta:
        model = PmsPreExecutionOfficeSetupLabourElectricalConnection
        fields = ('id',  'project','local_connection', 'option', 'nearby_elec_off_address', 'latitude', 'longitude', 'contact_no', 'detailed_procedure', 'requirment_s_date', 'requirment_e_date', 'budgeted_cost', 'executed_cost', 'created_by', 'owned_by','document_details')
class PreExecutionOfficeSetupLabourElectricalConnectionEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsPreExecutionOfficeSetupLabourElectricalConnection
        fields = ('id',  'project','local_connection', 'option', 'nearby_elec_off_address', 'latitude', 'longitude', 'contact_no', 'detailed_procedure', 'requirment_s_date', 'requirment_e_date', 'budgeted_cost', 'executed_cost', 'updated_by')
class PreExecutionOfficeSetupLabourElectricalConnectionDocumentAddSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    owned_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    model_class = serializers.CharField(required=False)
    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = ('id', 'project', 'module_id', 'document_name', 'document', 'created_by', 'owned_by','model_class')

    def create(self, validated_data):
        PreExecutionOfficeSetupLabourElectricalConnection_document = PmsPreExcutionUtilitiesDocument.objects.create(**validated_data,
                                                                                     model_class="PmsPreExecutionOfficeSetupLabourElectricalConnection")
        return PreExecutionOfficeSetupLabourElectricalConnection_document
class PreExecutionOfficeSetupLabourElectricalConnectionDocumentEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = ("id","document_name","updated_by")
class PreExecutionOfficeSetupLabourElectricalConnectionDocumentDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = '__all__'

    def update(self, instance, validated_data):
        instance.updated_by = validated_data.get('updated_by')
        instance.is_deleted = True
        instance.save()
        return instance

#:::::::::::::::::::::: PMS PRE EXECUTION OFFICE SETUP RAW MATERIAL YARD:::::::::::::::::::::::::::#
class PreExecutionOfficeSetupRawMaterialYardAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    document_details=serializers.SerializerMethodField()

    def get_document_details(self, PmsPreExecutionOfficeSetupRawMaterialYard):
        document = PmsPreExcutionUtilitiesDocument.objects.filter(project=PmsPreExecutionOfficeSetupRawMaterialYard.project.id,
                                                                  module_id=PmsPreExecutionOfficeSetupRawMaterialYard.id,
                                                                  model_class="PmsPreExecutionOfficeSetupRawMaterialYard",
                                                                  is_deleted=False)
        request = self.context.get('request')
        response_list = []
        for each_document in document:
            file_url = request.build_absolute_uri(each_document.document.url)
            owned_by = str(each_document.owned_by) if each_document.owned_by else ''
            created_by = str(each_document.created_by) if each_document.created_by else ''
            each_data = {
                "id": int(each_document.id),
                "project": int(each_document.project.id),
                "module_id": int(each_document.module_id),
                "model_class": each_document.model_class,
                "document_name": each_document.document_name,
                "document": file_url,
                "created_by": created_by,
                "owned_by": owned_by
            }
            response_list.append(each_data)
        return response_list

    class Meta:
        model = PmsPreExecutionOfficeSetupRawMaterialYard
        fields = ('id',  'project','land_type', 'protection_type', 'area_of_yard', 'rental_charge', 'area_owner_name', 'area_owner_phone_no', 'area_owner_address', 'latitude', 'longitude', 'requirment_s_date', 'requirment_e_date', 'budgeted_cost', 'executed_cost', 'created_by', 'owned_by','document_details')
class PreExecutionOfficeSetupRawMaterialYardEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsPreExecutionOfficeSetupRawMaterialYard
        fields = ('id',  'project','land_type', 'protection_type', 'area_of_yard', 'rental_charge', 'area_owner_name', 'area_owner_phone_no', 'area_owner_address', 'latitude', 'longitude', 'requirment_s_date', 'requirment_e_date', 'budgeted_cost', 'executed_cost', 'updated_by')
class PreExecutionOfficeSetupRawMaterialYardDocumentAddSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    owned_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    model_class = serializers.CharField(required=False)
    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = ('id', 'project', 'module_id', 'document_name', 'document', 'created_by', 'owned_by','model_class')

    def create(self, validated_data):
        PreExecutionOfficeSetupRawMaterialYard_document = PmsPreExcutionUtilitiesDocument.objects.create(**validated_data,
                                                                                     model_class="PmsPreExecutionOfficeSetupRawMaterialYard")
        return PreExecutionOfficeSetupRawMaterialYard_document
class PreExecutionOfficeSetupRawMaterialYardDocumentEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = ("id","document_name","updated_by")
class PreExecutionOfficeSetupRawMaterialYardDocumentDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = '__all__'

    def update(self, instance, validated_data):
        instance.updated_by = validated_data.get('updated_by')
        instance.is_deleted = True
        instance.save()
        return instance
#:::::::::::::::::::::: PMS PRE EXECUTION OFFICE SETUP CEMENT GODOWN:::::::::::::::::::::::::::#
class PreExecutionOfficeSetupCementGodownAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    document_details=serializers.SerializerMethodField()

    def get_document_details(self, PmsPreExecutionOfficeSetupCementGodown):
        document = PmsPreExcutionUtilitiesDocument.objects.filter(project=PmsPreExecutionOfficeSetupCementGodown.project.id,
                                                                  module_id=PmsPreExecutionOfficeSetupCementGodown.id,
                                                                  model_class="PmsPreExecutionOfficeSetupCementGodown",
                                                                  is_deleted=False)
        request = self.context.get('request')
        response_list = []
        for each_document in document:
            file_url = request.build_absolute_uri(each_document.document.url)
            owned_by = str(each_document.owned_by) if each_document.owned_by else ''
            created_by = str(each_document.created_by) if each_document.created_by else ''
            each_data = {
                "id": int(each_document.id),
                "project": int(each_document.project.id),
                "module_id": int(each_document.module_id),
                "model_class": each_document.model_class,
                "document_name": each_document.document_name,
                "document": file_url,
                "created_by": created_by,
                "owned_by": owned_by
            }
            response_list.append(each_data)
        return response_list

    class Meta:
        model = PmsPreExecutionOfficeSetupCementGodown
        fields = ('id',  'project','protection_type', 'area_of_go_down', 'rental_cost', 'capacity', 'protection_cost', 'requirment_s_date', 'requirment_e_date', 'budgeted_cost', 'executed_cost', 'created_by', 'owned_by','document_details')
class PreExecutionOfficeSetupCementGodownEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsPreExecutionOfficeSetupCementGodown
        fields = ('id',  'project','protection_type', 'area_of_go_down', 'rental_cost', 'capacity', 'protection_cost', 'requirment_s_date', 'requirment_e_date', 'budgeted_cost', 'executed_cost', 'updated_by')
class PreExecutionOfficeSetupCementGodownDocumentAddSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    owned_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    model_class = serializers.CharField(required=False)
    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = ('id', 'project', 'module_id', 'document_name', 'document', 'created_by', 'owned_by','model_class')

    def create(self, validated_data):
        PreExecutionOfficeSetupCementGodown_document = PmsPreExcutionUtilitiesDocument.objects.create(**validated_data,
                                                                                     model_class="PmsPreExecutionOfficeSetupCementGodown")
        return PreExecutionOfficeSetupCementGodown_document
class PreExecutionOfficeSetupCementGodownDocumentEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = ("id","document_name","updated_by")
class PreExecutionOfficeSetupCementGodownDocumentDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = '__all__'

    def update(self, instance, validated_data):
        instance.updated_by = validated_data.get('updated_by')
        instance.is_deleted = True
        instance.save()
        return instance
#:::::::::::::::::::::: PMS PRE EXECUTION OFFICE SETUP LAB:::::::::::::::::::::::::::#
class PreExecutionOfficeSetupLabAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    document_details=serializers.SerializerMethodField()

    def get_document_details(self, PmsPreExecutionOfficeSetupLab):
        document = PmsPreExcutionUtilitiesDocument.objects.filter(project=PmsPreExecutionOfficeSetupLab.project.id,
                                                                  module_id=PmsPreExecutionOfficeSetupLab.id,
                                                                  model_class="PmsPreExecutionOfficeSetupLab",
                                                                  is_deleted=False)
        request = self.context.get('request')
        response_list = []
        for each_document in document:
            file_url = request.build_absolute_uri(each_document.document.url)
            owned_by = str(each_document.owned_by) if each_document.owned_by else ''
            created_by = str(each_document.created_by) if each_document.created_by else ''
            each_data = {
                "id": int(each_document.id),
                "project": int(each_document.project.id),
                "module_id": int(each_document.module_id),
                "model_class": each_document.model_class,
                "document_name": each_document.document_name,
                "document": file_url,
                "created_by": created_by,
                "owned_by": owned_by
            }
            response_list.append(each_data)
        return response_list

    class Meta:
        model = PmsPreExecutionOfficeSetupLab
        fields = ('id',  'project','protection_type', 'area_of_lab', 'rental_cost', 'capacity', 'protection_cost', 'requirment_s_date', 'requirment_e_date', 'budgeted_cost', 'executed_cost', 'created_by', 'owned_by','document_details')
class PreExecutionOfficeSetupLabEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsPreExecutionOfficeSetupLab
        fields = ('id',  'project','protection_type', 'area_of_lab', 'rental_cost', 'capacity', 'protection_cost', 'requirment_s_date', 'requirment_e_date', 'budgeted_cost', 'executed_cost', 'updated_by')
class PreExecutionOfficeSetupLabDocumentAddSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    owned_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    model_class = serializers.CharField(required=False)
    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = ('id', 'project', 'module_id', 'document_name', 'document', 'created_by', 'owned_by','model_class')

    def create(self, validated_data):
        PreExecutionOfficeSetupLab_document = PmsPreExcutionUtilitiesDocument.objects.create(**validated_data,
                                                                                     model_class="PmsPreExecutionOfficeSetupLab")
        return PreExecutionOfficeSetupLab_document
class PreExecutionOfficeSetupLabDocumentEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = ("id","document_name","updated_by")
class PreExecutionOfficeSetupLabDocumentDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = '__all__'

    def update(self, instance, validated_data):
        instance.updated_by = validated_data.get('updated_by')
        instance.is_deleted = True
        instance.save()
        return instance
# ::::::::::::PMS PRE EXECUTION OFFICE SETUP SURVEY INSTRUMENT:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::#
class PreExecutionOfficeSetupSurveyInstrumentAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    instrument_types=serializers.DictField(required=False)
    instrument_details = serializers.SerializerMethodField(required=False)

    def get_instrument_details(self, PmsPreExecutionOfficeSetupSurveyInstruments):
        instrument_details = PmsPreExecutionOfficeSetupSurveyInstrumentsType.objects.filter(
            survey_instrument_id=PmsPreExecutionOfficeSetupSurveyInstruments.id,is_deleted=False)

        instrument_list = []

        request = self.context.get('request')
        for instrument in instrument_details:
            instrument_document = PmsPreExcutionUtilitiesDocument.objects.filter(
                model_class="PmsPreExecutionOfficeSetupSurveyInstrumentsType",
                module_id=instrument.id,
                project_id=instrument.project.id,
                is_deleted=False)
            document_list = list()
            for i_d in instrument_document:
                data1 = {
                    "id": int(i_d.id),
                    "project": int(i_d.project.id),
                    "module_id": i_d.module_id,
                    "model_class": i_d.model_class,
                    "document_name": i_d.document_name,
                    "document": request.build_absolute_uri(i_d.document.url),
                    'is_deleted': i_d.is_deleted
                }
                document_list.append(data1)
            # return document_list
            survey_instrument = {
                'id': instrument.id,
                'survey_instrument': instrument.survey_instrument.id,
                'project': instrument.project.id,
                'type_of_instrument': instrument.type_of_instrument,
                'quantity': instrument.quantity,
                'total_cost': instrument.total_cost,
                'document_details': document_list
            }
            instrument_list.append(survey_instrument)

        return instrument_list

    class Meta:
        model=PmsPreExecutionOfficeSetupSurveyInstruments
        fields='__all__'
        extra_fields=('instrument_types','instrument_details')
    def create(self, validated_data):
        try:
            instrument_types=validated_data.pop('instrument_types') if 'instrument_types' in validated_data else ""
            created_by=validated_data.get('created_by')
            owned_by=validated_data.get('owned_by')
            with transaction.atomic():
                survey_instrument,created=PmsPreExecutionOfficeSetupSurveyInstruments.objects.get_or_create(**validated_data)
                # print('survey_instrument',type(survey_instrument))
                # print('created',created)
                survey_instrument_types,types_created=PmsPreExecutionOfficeSetupSurveyInstrumentsType.objects.get_or_create(survey_instrument=survey_instrument,
                                                                                                                            **instrument_types,
                                                                                                                            created_by=created_by,
                                                                                                                            owned_by=owned_by)
                # print('survey_instrument_types',survey_instrument_types.__dict__)
                # print('types_created',types_created)
                survey_instrument_types.__dict__.pop('_state') if '_state' in survey_instrument_types.__dict__.keys() else survey_instrument_types.__dict__
                survey_instrument.__dict__['instrument_types']=survey_instrument_types.__dict__

                return  survey_instrument
        except Exception as e:
            # raise e
            return ({'request_status':0,
                                'error':e,
                                'msg':settings.MSG_ERROR})
class PreExecutionOfficeSetupSurveyInstrumentEditSerializer(serializers.ModelSerializer):
    updated_by=serializers.CharField(default=serializers.CurrentUserDefault())
    instrument_types = serializers.DictField(required=False)
    class Meta:
        model = PmsPreExecutionOfficeSetupSurveyInstruments
        fields = '__all__'
        extra_fields = ('instrument_types')
    def update(self,instance,validated_data):
        try:
            instrument_types=validated_data.pop('instrument_types')if 'instrument_types' in validated_data else ""
            updated_by=validated_data.get('updated_by')
            with transaction.atomic():
                instance.project=validated_data.get('project')
                instance.survey_instrument_type_tab=validated_data.get('survey_instrument_type_tab')
                instance.requirment_s_date=validated_data.get('requirment_s_date')
                instance.requirment_e_date=validated_data.get('requirment_e_date')
                instance.budgeted_cost=validated_data.get('budgeted_cost')
                instance.executed_cost=validated_data.get('executed_cost')
                instance.updated_by=updated_by
                instance.save()

                survey_instrument_types,created=PmsPreExecutionOfficeSetupSurveyInstrumentsType.objects.get_or_create(survey_instrument=instance,
                                                                                                                      **instrument_types,
                                                                                                                      created_by=updated_by,
                                                                                                                      owned_by=updated_by
                                                                                                                      )
                survey_instrument_types.__dict__.pop('_state') if '_state' in survey_instrument_types.__dict__.keys() else survey_instrument_types.__dict__

                instance.__dict__['instrument_types']=survey_instrument_types.__dict__

                return instance

        except Exception as e:
            return ({'request_status':0,
                                'error':e,
                                'msg':settings.MSG_ERROR})
class PreExecutionOfficeSetupSurveyInstrumentTypesDocumentAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    model_class = serializers.CharField(required=False)
    class Meta:
        model=PmsPreExcutionUtilitiesDocument
        fields=('id','project','module_id','document_name','document','created_by','owned_by','model_class')
    def create(self, validated_data):
        document_details = PmsPreExcutionUtilitiesDocument.objects.create(**validated_data,
                                                                             model_class="PmsPreExecutionOfficeSetupSurveyInstrumentsType")
        return document_details
class PreExecutionOfficeSetupSurveyInstrumentTypesDocumentEditSerializer(serializers.ModelSerializer):
    updated_by=serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model=PmsPreExcutionUtilitiesDocument
        fields=('id','document_name','updated_by')
class PreExecutionOfficeSetupSurveyInstrumentTypesDocumentDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model=PmsPreExcutionUtilitiesDocument
        fields='__all__'
    def update(self,instance,validated_data):
        instance.is_deleted=True
        instance.updated_by=validated_data.get('updated_by')
        instance.save()
        return instance
class PreExecutionOfficeSetupSurveyInstrumentTypesListSerializer(serializers.ModelSerializer):
    class Meta:
        model=PmsPreExecutionOfficeSetupSurveyInstrumentsType
        fields='__all__'
class PreExecutionOfficeSetupSurveyInstrumentTypesEditSerializer(serializers.ModelSerializer):
    updated_by=serializers.CharField(default=serializers.CurrentUserDefault())
    survey_instruments=serializers.DictField(required=False)
    class Meta:
        model=PmsPreExecutionOfficeSetupSurveyInstrumentsType
        fields='__all__'
        extra_fields=('survey_instruments')
    def update(self, instance, validated_data):
        try:
            #print('validate', validated_data)
            survey_instruments=validated_data.pop('survey_instruments') if 'survey_instruments' in validated_data else ""
            updated_by=validated_data.get('updated_by')

            with transaction.atomic():
                instance.survey_instrument=validated_data.get('survey_instrument')
                instance.project=validated_data.get('project')
                instance.type_of_instrument=validated_data.get('type_of_instrument')
                instance.quantity=validated_data.get('quantity')
                instance.total_cost=validated_data.get('total_cost')
                instance.updated_by=updated_by
                instance.save()

                survey_data=PmsPreExecutionOfficeSetupSurveyInstruments.objects.filter(
                    id= instance.survey_instrument_id,project=instance.project)
                #print('survey_data', survey_data)
                for data in survey_data:

                    data.survey_instrument_type_tab=survey_instruments['survey_instrument_type_tab']
                    data.requirment_s_date=datetime.datetime.strptime(survey_instruments['requirment_s_date'], "%Y-%m-%dT%H:%M:%S.%fZ")
                    data.requirment_e_date=datetime.datetime.strptime(survey_instruments['requirment_e_date'], "%Y-%m-%dT%H:%M:%S.%fZ")
                    data.budgeted_cost=survey_instruments['budgeted_cost']
                    data.executed_cost=survey_instruments['executed_cost']
                    data.save()

                    data.__dict__.pop('_state') if '_state' in data.__dict__.keys() else data

                instance.__dict__['survey_instruments']=data.__dict__
                # print('instance',instance)

                return instance

        except Exception as e:
            return ({'request_status':0,
                                'error':e,
                                'msg':settings.MSG_ERROR})
class PreExecutionOfficeSetupSurveyInstrumentTypesDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsPreExecutionOfficeSetupSurveyInstrumentsType
        fields = '__all__'

    def update(self, instance, validated_data):
        delete_details = custom_delete(
            self, instance, validated_data,
            update_extra_columns=[],
            extra_model_with_fields=[
                {
                    'model': PmsPreExcutionUtilitiesDocument,
                    'filter_columns': {
                        'project': instance.project.id,
                        'module_id' :instance.id,
                       'model_class':"PmsPreExecutionOfficeSetupSurveyInstrumentsType"
                    },
                    'update_extra_columns': []

                },
            ]
        )
        return delete_details

#:::::::::::::PMS PRE EXECUTION OFFICE SETUP SAFTEY PPE's:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::#
class  PreExecutionOfficeSetupSafetyPPEsAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    ppes_accessory = serializers.DictField(required=False)
    accessory_details = serializers.SerializerMethodField(required=False)

    def get_accessory_details(self, PmsPreExecutionOfficeSetupSafetyPPEs):
        accessory_data = PmsPreExecutionOfficeSetupSafetyPPEsAccessory.objects. \
            filter(safety_ppe_id=PmsPreExecutionOfficeSetupSafetyPPEs.id, is_deleted=False)
        accessory_list = list()
        request = self.context.get('request')
        for accessory in accessory_data:
            document_list = list()
            accessory_document = PmsPreExcutionUtilitiesDocument.objects. \
                filter(model_class="PmsPreExecutionOfficeSetupSafetyPPEsAccessory",
                       project_id=accessory.project.id,
                       module_id=accessory.id,
                       is_deleted=False)

            for document in accessory_document:
                data_1 = {
                    "id": int(document.id),
                    "project": int(document.project.id),
                    "module_id": document.module_id,
                    "model_class": document.model_class,
                    "document_name": document.document_name,
                    "document": request.build_absolute_uri(document.document.url),
                    'is_deleted': document.is_deleted
                }
                document_list.append(data_1)

            data = {
                'id': accessory.id,
                'safety_ppe': accessory.safety_ppe.id,
                'project': accessory.project.id,
                'safety_accessory': accessory.safety_accessory,
                'quantity': accessory.quantity,
                'total_cost': accessory.total_cost,
                'safety_accessory_document': document_list

            }

            accessory_list.append(data)
        return accessory_list

    class Meta:
        model = PmsPreExecutionOfficeSetupSafetyPPEs
        fields = ( 'id', 'project','requirment_s_date', 'requirment_e_date', 'budgeted_cost', 'executed_cost',
        'created_by', 'owned_by', 'ppes_accessory','accessory_details')
    def create(self, validated_data):
        try:
            ppes_accessory = validated_data.pop('ppes_accessory') if 'ppes_accessory' in validated_data else ""
            owned_by = validated_data.get('owned_by')
            created_by = validated_data.get('created_by')
            with transaction.atomic():
                ppes_data, created1 = PmsPreExecutionOfficeSetupSafetyPPEs.objects.get_or_create(**validated_data)
                # print("ppes_data ", ppes_data)
                ppes_accessory_data, created2 = PmsPreExecutionOfficeSetupSafetyPPEsAccessory.objects.get_or_create(safety_ppe=ppes_data,
                                                                                                   created_by=created_by,
                                                                                                   owned_by=owned_by,
                                                                                                   **ppes_accessory
                                                                                                   )
                ppes_accessory_data.__dict__.pop('_state') if "_state" in ppes_accessory_data.__dict__.keys() else ppes_accessory_data.__dict__
                ppes_data.__dict__["ppes_accessory"] = ppes_accessory_data.__dict__

                return ppes_data

        except Exception as e:
            # raise e
            raise APIException({'request_status':0,
                                'error':e,
                                'msg':settings.MSG_ERROR})
class PreExecutionOfficeSetupSafetyPPEsEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    ppes_accessory = serializers.DictField(required=False)

    class Meta:
        model = PmsPreExecutionOfficeSetupSafetyPPEs
        fields = ('id', 'project','requirment_s_date', 'requirment_e_date', 'budgeted_cost', 'executed_cost',
        'updated_by', 'ppes_accessory')

    def update(self, instance, validated_data):
        try:
            with transaction.atomic():
                ppes_accessory = validated_data.pop('ppes_accessory') if 'ppes_accessory' in validated_data else ""

                instance.project = validated_data.get('project')
                instance.requirment_s_date = validated_data.get('requirment_s_date')
                instance.requirment_e_date = validated_data.get('requirment_e_date')
                instance.budgeted_cost = validated_data.get('budgeted_cost')
                instance.executed_cost = validated_data.get('executed_cost')
                instance.updated_by = validated_data.get('updated_by')
                instance.save()
                print("instance",ppes_accessory)
                ppes_accessory_data = PmsPreExecutionOfficeSetupSafetyPPEsAccessory.objects.create(
                    safety_ppe=instance,
                    project=validated_data.get('project'),
                    created_by=validated_data.get('updated_by'),
                    owned_by=validated_data.get('updated_by'),
                    **ppes_accessory
                    )
                ppes_accessory_data.__dict__.pop('_state') if "_state" in ppes_accessory_data.__dict__.keys() else ppes_accessory_data.__dict__
                instance.__dict__["ppes_accessory"] = ppes_accessory_data.__dict__
                return instance

        except Exception as e:
            # print(e)
            return APIException({'request_status': 0,
                                 'error': e,
                                 'msg': settings.MSG_ERROR})
class PreExecutionOfficeSetupSafetyPPEsDocumentAddSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    owned_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    model_class = serializers.CharField(required=False)
    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = ('id', 'project', 'module_id', 'document_name', 'document', 'created_by', 'owned_by','model_class')

    def create(self, validated_data):
        ppes_accessory_document = PmsPreExcutionUtilitiesDocument.objects.create(**validated_data,
                                                                                     model_class="PmsPreExecutionOfficeSetupSafetyPPEsAccessory")
        return ppes_accessory_document
class PreExecutionOfficeSetupSafetyPPEsDocumentEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = ("id","document_name","updated_by")
class PreExecutionOfficeSetupSafetyPPEsDocumentDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = ("id","is_deleted","updated_by")

    def update(self, instance, validated_data):
        instance.updated_by = validated_data.get('updated_by')
        instance.is_deleted = True
        instance.save()
        return instance
class PreExecutionOfficeSetupSafetyPPEsAccessoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PmsPreExecutionOfficeSetupSafetyPPEsAccessory
        fields = '__all__'
class PreExecutionOfficeSetupSafetyPPEsAccessoryEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    ppes_details = serializers.DictField(required=False)

    class Meta:
        model = PmsPreExecutionOfficeSetupSafetyPPEsAccessory
        fields = '__all__'
        extra_fields = ('ppes_details')
    def update(self,instance,validated_data):
        try:
            ppes_details = validated_data.pop('ppes_details') if 'ppes_details' in validated_data else ""
            with transaction.atomic():
                instance.project=validated_data.get('project')
                instance.safety_accessory=validated_data.get('safety_accessory')
                instance.quantity=validated_data.get('quantity')
                instance.total_cost=validated_data.get('total_cost')
                instance.updated_by=validated_data.get('updated_by')
                instance.save()

                ppes_data = PmsPreExecutionOfficeSetupSafetyPPEs.objects.filter(id=instance.safety_ppe_id,project_id=instance.project_id)

                print("ppes_data",ppes_data)
                for data in ppes_data:
                    # data.office_set_up=ppes_details['office_set_up']

                    data.requirment_s_date=datetime.datetime.strptime(ppes_details['requirment_s_date'], "%Y-%m-%dT%H:%M:%S.%fZ")
                    data.requirment_e_date=datetime.datetime.strptime(ppes_details['requirment_e_date'], "%Y-%m-%dT%H:%M:%S.%fZ")
                    data.budgeted_cost=ppes_details['budgeted_cost']
                    data.executed_cost=ppes_details['executed_cost']
                    data.updated_by = validated_data.get('updated_by')
                    data.save()

                    data.__dict__.pop('_state') if '_state' in data.__dict__.keys() else data

                instance.__dict__['ppes_details'] = data.__dict__


            return instance
        except Exception as e:
            raise e
class PreExecutionOfficeSetupSafetyPPEsAccessoryDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsPreExecutionOfficeSetupSafetyPPEsAccessory
        fields = '__all__'

    def update(self, instance, validated_data):
        delete_details = custom_delete(
            self, instance, validated_data,
            update_extra_columns=[],
            extra_model_with_fields=[
                {
                    'model': PmsPreExcutionUtilitiesDocument,
                    'filter_columns': {
                        'project': instance.project.id,
                        'module_id' :instance.id,
                       'model_class':"PmsPreExecutionOfficeSetupSafetyPPEsAccessory"
                    },
                    'update_extra_columns': []

                },
            ]
        )
        return delete_details

#:::::::::::::::::::::: PMS PRE EXECUTION OFFICE SETUP SECURITY ROOM:::::::::::::::::::::::::::#
class PreExecutionOfficeSetupSecurityRoomAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    document_details=serializers.SerializerMethodField()

    def get_document_details(self, PmsPreExecutionOfficeSetupSecurityRoom):
        document = PmsPreExcutionUtilitiesDocument.objects.filter(project=PmsPreExecutionOfficeSetupSecurityRoom.project.id,
                                                                  module_id=PmsPreExecutionOfficeSetupSecurityRoom.id,
                                                                  model_class="PmsPreExecutionOfficeSetupSecurityRoom",
                                                                  is_deleted=False)
        request = self.context.get('request')
        response_list = []
        for each_document in document:
            file_url = request.build_absolute_uri(each_document.document.url)
            owned_by = str(each_document.owned_by) if each_document.owned_by else ''
            created_by = str(each_document.created_by) if each_document.created_by else ''
            each_data = {
                "id": int(each_document.id),
                "project": int(each_document.project.id),
                "module_id": int(each_document.module_id),
                "model_class": each_document.model_class,
                "document_name": each_document.document_name,
                "document": file_url,
                "created_by": created_by,
                "owned_by": owned_by
            }
            response_list.append(each_data)
        return response_list

    class Meta:
        model = PmsPreExecutionOfficeSetupSecurityRoom
        fields = ('id',  'project','security_room_type', 'size', 'rate', 'agency_name', 'agency_contact_no', 'transportation_cost', 'requirment_s_date', 'requirment_e_date', 'budgeted_cost', 'executed_cost', 'created_by', 'owned_by','document_details')
class PreExecutionOfficeSetupSecurityRoomEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsPreExecutionOfficeSetupSecurityRoom
        fields = ('id',  'project','security_room_type', 'size', 'rate', 'agency_name', 'agency_contact_no', 'transportation_cost', 'requirment_s_date', 'requirment_e_date', 'budgeted_cost', 'executed_cost', 'updated_by')
class PreExecutionOfficeSetupSecurityRoomDocumentAddSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    owned_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    model_class = serializers.CharField(required=False)
    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = ('id', 'project', 'module_id', 'document_name', 'document', 'created_by', 'owned_by','model_class')

    def create(self, validated_data):
        PreExecutionOfficeSetupSecurityRoom_document = PmsPreExcutionUtilitiesDocument.objects.create(**validated_data,
                                                                                     model_class="PmsPreExecutionOfficeSetupSecurityRoom")
        return PreExecutionOfficeSetupSecurityRoom_document
class PreExecutionOfficeSetupSecurityRoomDocumentEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = ("id","document_name","updated_by")
class PreExecutionOfficeSetupSecurityRoomDocumentDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = '__all__'

    def update(self, instance, validated_data):
        instance.updated_by = validated_data.get('updated_by')
        instance.is_deleted = True
        instance.save()
        return instance

#:::::::::::::::::::::: PMS PRE EXECUTION P AND M DETAILS::::::::::::::::::::::::::::::::::::::::::::::::::::::::#
class PreExecutionPAndMMachineryTypeExDetailsAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    document_details=serializers.SerializerMethodField(required=False)
    class Meta:
        model = PmsPreExecutionMachineryTypeDetails
        fields = ('id','project','machinary_type','types',
         'model_of_machinery','fuel_consumption','quantity', 
         'capacity', 'rate_per_product', 'operator_required', 'operator_name', 
         'operator_contact_no', 'operator_salary', 'requirment_s_date', 'requirment_e_date', 
         'budgeted_cost', 'executed_cost', 'created_by', 'owned_by','updated_by','document_details')
       
    def get_document_details(self, PmsPreExecutionMachineryTypeDetails):
        print("PmsPreExecutionMachineryTypeDetails::::::;",type(PmsPreExecutionMachineryTypeDetails))
        if type(PmsPreExecutionMachineryTypeDetails) is dict:
            document = PmsPreExcutionUtilitiesDocument.objects.filter(
                project=PmsPreExecutionMachineryTypeDetails['project'],
                module_id=PmsPreExecutionMachineryTypeDetails['id'],
                model_class="PmsPreExecutionMachineryTypeDetails",is_deleted=False)
            request = self.context.get('request')
            response_list = []
            for each_document in document:
                file_url = request.build_absolute_uri(each_document.document.url)
                owned_by = str(each_document.owned_by) if each_document.owned_by else ''
                created_by = str(each_document.created_by) if each_document.created_by else ''
                each_data = {
                    "id": int(each_document.id),
                    "project": int(each_document.project.id),
                    "module_id": int(each_document.module_id),
                    "model_class": each_document.model_class,
                    "document_name": each_document.document_name,
                    "document": file_url,
                    "created_by": created_by,
                    "owned_by": owned_by
                }
                response_list.append(each_data)
            return response_list
        else:
            document = PmsPreExcutionUtilitiesDocument.objects.filter(
                project=PmsPreExecutionMachineryTypeDetails.project.id,
                module_id=PmsPreExecutionMachineryTypeDetails.id,
                model_class="PmsPreExecutionMachineryTypeDetails",is_deleted=False)
            request = self.context.get('request')
            response_list = []
            for each_document in document:
                file_url = request.build_absolute_uri(each_document.document.url)
                owned_by = str(each_document.owned_by) if each_document.owned_by else ''
                created_by = str(each_document.created_by) if each_document.created_by else ''
                each_data = {
                    "id": int(each_document.id),
                    "project": int(each_document.project.id),
                    "module_id": int(each_document.module_id),
                    "model_class": each_document.model_class,
                    "document_name": each_document.document_name,
                    "document": file_url,
                    "created_by": created_by,
                    "owned_by": owned_by
                }
                response_list.append(each_data)
            return response_list

    def create(self,validated_data):
        try:
            response= dict()
            # print(validated_data)
            pre_ex_machinary_type_details=PmsPreExecutionMachineryTypeDetails.objects.filter(project_id=validated_data.get('project'),machinary_type_id=validated_data.get('machinary_type'))
            # for x in pre_ex_machinary_type_details:
                # print(x.project)
            
            if pre_ex_machinary_type_details:
                for e_m_type_details in pre_ex_machinary_type_details:
                    e_m_type_details.types=validated_data.get('types')
                    e_m_type_details.model_of_machinery=validated_data.get('model_of_machinery')
                    e_m_type_details.fuel_consumption=validated_data.get('fuel_consumption')
                    e_m_type_details.quantity=validated_data.get('quantity')
                    e_m_type_details.capacity=validated_data.get('capacity')
                    e_m_type_details.rate_per_product=validated_data.get('rate_per_product')
                    e_m_type_details.operator_required=validated_data.get('operator_required')
                    e_m_type_details.operator_name=validated_data.get('operator_name')
                    e_m_type_details.operator_contact_no=validated_data.get('operator_contact_no')
                    e_m_type_details.operator_salary=validated_data.get('operator_salary')
                    e_m_type_details.requirment_s_date=validated_data.get('requirment_s_date')
                    e_m_type_details.requirment_e_date=validated_data.get('requirment_e_date')
                    e_m_type_details.budgeted_cost=validated_data.get('budgeted_cost')
                    e_m_type_details.executed_cost=validated_data.get('executed_cost')
                    e_m_type_details.updated_by=validated_data.get('updated_by')
                    e_m_type_details.save()
                    response['id']=e_m_type_details.id
                    response['project']=e_m_type_details.project
                    response['machinary_type']=e_m_type_details.machinary_type
                    response['types']=e_m_type_details.types
                    response['model_of_machinery']=e_m_type_details.model_of_machinery
                    response['fuel_consumption']=e_m_type_details.fuel_consumption
                    response['quantity']=e_m_type_details.quantity
                    response['capacity']=e_m_type_details.capacity
                    response['rate_per_product']=e_m_type_details.rate_per_product
                    response['operator_required']=e_m_type_details.operator_required
                    response['operator_name']=e_m_type_details.operator_name
                    response['operator_contact_no']=e_m_type_details.operator_contact_no
                    response['operator_salary']=e_m_type_details.operator_salary
                    response['requirment_s_date']=e_m_type_details.requirment_s_date
                    response['requirment_e_date']=e_m_type_details.requirment_e_date
                    response['budgeted_cost']=e_m_type_details.budgeted_cost
                    response['executed_cost']=e_m_type_details.executed_cost
                    return response
            else:
                pre_execution_machinary_type_details=PmsPreExecutionMachineryTypeDetails.objects.create(project=validated_data.get('project'),
                        machinary_type=validated_data.get('machinary_type'),
                        types=validated_data.get('types'),
                        model_of_machinery=validated_data.get('model_of_machinery'),
                        fuel_consumption=validated_data.get('fuel_consumption'),
                        quantity=validated_data.get('quantity'),
                        capacity=validated_data.get('capacity'),
                        rate_per_product=validated_data.get('rate_per_product'),
                        operator_required=validated_data.get('operator_required'),
                        operator_name=validated_data.get('operator_name'),
                        operator_contact_no=validated_data.get('operator_contact_no'),
                        operator_salary=validated_data.get('operator_salary'),
                        requirment_s_date=validated_data.get('requirment_s_date'),
                        requirment_e_date=validated_data.get('requirment_e_date'),
                        budgeted_cost=validated_data.get('budgeted_cost'),
                        executed_cost=validated_data.get('executed_cost'),
                        created_by=validated_data.get('created_by'),
                        owned_by=validated_data.get('owned_by')
                )
                
                return pre_execution_machinary_type_details
                      
        except Exception as e:
            raise e
class PreExecutionPAndMMachineryTypeDetailsAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    is_default = serializers.BooleanField(default=False)
    name = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
    machinary_name = serializers.SerializerMethodField()
    machinary_description = serializers.SerializerMethodField()
    document_details=serializers.SerializerMethodField()
    def get_document_details(self, PmsPreExecutionMachineryTypeDetails):
        document = PmsPreExcutionUtilitiesDocument.objects.filter(
            project=PmsPreExecutionMachineryTypeDetails.project.id,
            module_id=PmsPreExecutionMachineryTypeDetails.id,
            model_class="PmsPreExecutionMachineryTypeDetails",is_deleted=False)
        request = self.context.get('request')
        response_list = []
        for each_document in document:
            file_url = request.build_absolute_uri(each_document.document.url)
            owned_by = str(each_document.owned_by) if each_document.owned_by else ''
            created_by = str(each_document.created_by) if each_document.created_by else ''
            each_data = {
                "id": int(each_document.id),
                "project": int(each_document.project.id),
                "module_id": int(each_document.module_id),
                "model_class": each_document.model_class,
                "document_name": each_document.document_name,
                "document": file_url,
                "created_by": created_by,
                "owned_by": owned_by
            }
            response_list.append(each_data)
        return response_list

    def get_machinary_name(self,PmsPreExecutionMachineryTypeDetails):
        machineryTypeDetails = PmsMachineryType.objects.filter(
            pk=PmsPreExecutionMachineryTypeDetails.machinary_type.id)
        if machineryTypeDetails:
            return PmsMachineryType.objects.only('name').get(
            pk=PmsPreExecutionMachineryTypeDetails.machinary_type.id).name
        else:
            return None   
    def get_machinary_description(self,PmsPreExecutionMachineryTypeDetails):
        machineryTypeDetails = PmsMachineryType.objects.filter(
            pk=PmsPreExecutionMachineryTypeDetails.machinary_type.id)
        if machineryTypeDetails:
            return PmsMachineryType.objects.only('description').get(
            pk=PmsPreExecutionMachineryTypeDetails.machinary_type.id).description
        else:
            return None

    class Meta:
        model = PmsPreExecutionMachineryTypeDetails
        fields = ('id',  'project', 'machinary_type', 'types',
         'model_of_machinery', 'fuel_consumption', 'quantity', 
         'capacity', 'rate_per_product', 'operator_required', 'operator_name', 
         'operator_contact_no', 'operator_salary', 'requirment_s_date', 'requirment_e_date', 
         'budgeted_cost', 'executed_cost', 'created_by', 'owned_by','name',
         'description','is_default','machinary_name','machinary_description','document_details')

    def create(self,validated_data):
        try:
            with transaction.atomic():
                machinery_type_data= PmsMachineryType.objects.create(
                        name=validated_data.get('name'), 
                        description=validated_data.get('description'), 
                        is_default = validated_data.get('is_default'),
                        created_by = validated_data.get('created_by'),
                        owned_by = validated_data.get('owned_by')
                        )
                # print("machinery_type_data::::::::",machinery_type_data)
                pre_ex_machinery_type_details=PmsPreExecutionMachineryTypeDetails.objects.create(
                    project=validated_data.get('project'),
                    machinary_type_id=machinery_type_data.id,
                    types=validated_data.get('types'),
                    model_of_machinery=validated_data.get('model_of_machinery'),
                    fuel_consumption=validated_data.get('fuel_consumption'),
                    quantity=validated_data.get('quantity'),
                    capacity=validated_data.get('capacity'),
                    rate_per_product=validated_data.get('rate_per_product'),
                    operator_required=validated_data.get('operator_required'),
                    operator_name=validated_data.get('operator_name'),
                    operator_contact_no=validated_data.get('operator_contact_no'),
                    operator_salary=validated_data.get('operator_salary'),
                    requirment_s_date=validated_data.get('requirment_s_date'),
                    requirment_e_date=validated_data.get('requirment_e_date'),
                    budgeted_cost=validated_data.get('budgeted_cost'),
                    executed_cost=validated_data.get('executed_cost'),
                    created_by = validated_data.get('created_by'),
                    owned_by = validated_data.get('owned_by')
                    )
                # print('pre_ex_machinery_type_details',pre_ex_machinery_type_details)
                return pre_ex_machinery_type_details
        
        except Exception as e:
            # print('response.status_code',e.args[0])
            if e.args[0] == 1062:
                 raise APIException({
                'request_status': 0, 
                'msg': "Duplicate entry machinary for name"
                })         
            else:
                raise APIException({
                    'request_status': 0,
                    'msg': e.args[1]
                })

class MachinaryTypeListByProjectSerializer(serializers.ModelSerializer):
    # name=serializers.SerializerMethodField()
    # description=serializers.SerializerMethodField()
    # def get_name(self,PmsTenderMachineryTypeDetails):
    #     return PmsMachineryType.objects.only('name').get(id=PmsTenderMachineryTypeDetails.machinary_type.id).name
    # def get_description(self,PmsTenderMachineryTypeDetails):
    #     return PmsMachineryType.objects.only('description').get(id=PmsTenderMachineryTypeDetails.machinary_type.id).description
    class Meta:
        model = PmsMachineryType
        fields= '__all__'
        # extra_fields = ('name','description')
        
class PreExecutionPAndMDetailsEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsPreExecutionMachineryTypeDetails
        fields = ('id',  'project', 'machinary_type', 'types', 'model_of_machinery', 'fuel_consumption', 'quantity', 'capacity', 'rate_per_product', 'operator_required', 'operator_name', 'operator_contact_no', 'operator_salary', 'requirment_s_date', 'requirment_e_date', 'budgeted_cost', 'executed_cost', 'updated_by')
class PreExecutionPAndMDetailsDocumentAddSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    owned_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    model_class = serializers.CharField(required=False)
    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = ('id', 'project', 'module_id', 'document_name', 'document', 'created_by', 'owned_by','model_class')

    def create(self, validated_data):
        PreExecutionPAndMDetails_document = PmsPreExcutionUtilitiesDocument.objects.create(**validated_data,
                                                                                     model_class="PmsPreExecutionMachineryTypeDetails")
        return PreExecutionPAndMDetails_document
class PreExecutionPAndMDetailsDocumentEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = ("id","document_name","updated_by")
class PreExecutionPAndMDetailsDocumentDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = '__all__'

    def update(self, instance, validated_data):
        instance.updated_by = validated_data.get('updated_by')
        instance.is_deleted = True
        instance.save()
        return instance

#:::::::::::::::::::::::::::::::::: PMS PRE EXECUTION MANPOWER::::::::::::::::::::::::::::::::::::::::::::::#

class PreExecutionManpowerRequirementAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    name = serializers.SerializerMethodField()
    contact_no = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    document_details=serializers.SerializerMethodField()
    def get_name(self, PmsPreExecutionManpowerDetails):
        # print('dfsfs',PmsPreExecutionManpowerDetails.manpower.id)
        if PmsPreExecutionManpowerDetails.manpower:
            user_details = User.objects.filter(pk=PmsPreExecutionManpowerDetails.manpower.id)
            if user_details:
                for e_user_details in user_details:
                    return e_user_details.first_name +' '+e_user_details.last_name    
    
    def get_contact_no(self, PmsPreExecutionManpowerDetails):
        if PmsPreExecutionManpowerDetails.manpower:
            user_details = TCoreUserDetail.objects.filter(cu_user_id=PmsPreExecutionManpowerDetails.manpower.id)
            if user_details:
                return TCoreUserDetail.objects.only('cu_phone_no').get(cu_user_id=PmsPreExecutionManpowerDetails.manpower.id).cu_phone_no
            
    def get_email(self, PmsPreExecutionManpowerDetails):
        if PmsPreExecutionManpowerDetails.manpower:
            user_details = User.objects.filter(pk=PmsPreExecutionManpowerDetails.manpower.id)
            if user_details:
                return User.objects.only('email').get(pk=PmsPreExecutionManpowerDetails.manpower.id).email
    
    def get_document_details(self,PmsPreExecutionManpowerDetails):
        if PmsPreExecutionManpowerDetails.manpower:
            doc_details=PmsPreExcutionUtilitiesDocument.objects.filter(
                module_id=PmsPreExecutionManpowerDetails.id,
                project=PmsPreExecutionManpowerDetails.project.id,
                model_class = 'User',is_deleted=False)
            print('doc_details',doc_details)
            request = self.context.get('request')
            response_list = []
            for each_document in doc_details:
                file_url = request.build_absolute_uri(each_document.document.url)
                owned_by = str(each_document.owned_by) if each_document.owned_by else ''
                created_by = str(each_document.created_by) if each_document.created_by else ''
                each_data = {
                    "id": int(each_document.id),
                    "document": file_url,
                    "created_by": created_by,
                    "owned_by": owned_by
                }
                response_list.append(each_data)
            return response_list
    
    class Meta:
        model = PmsPreExecutionManpowerDetails
        fields = '__all__'
        extra_fields = ('name','contact_no','email','document_details')
    
class PreExecutionManpowerRequirementEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    manpower_details = serializers.DictField(required=False)
    
    def get_name(self, PmsPreExecutionManpowerDetails):
        user_details = User.objects.filter(pk=PmsPreExecutionManpowerDetails.manpower.id)
        if user_details:
            for e_user_details in user_details:
                return e_user_details.first_name +' '+e_user_details.last_name    
    
    def get_contact_no(self, PmsPreExecutionManpowerDetails):
        user_details = TCoreUserDetail.objects.filter(cu_user_id=PmsPreExecutionManpowerDetails.manpower.id)
        if user_details:
            return TCoreUserDetail.objects.only('cu_phone_no').get(cu_user_id=PmsPreExecutionManpowerDetails.manpower.id).cu_phone_no
            
    def get_email(self, PmsPreExecutionManpowerDetails):
        user_details = User.objects.filter(pk=PmsPreExecutionManpowerDetails.manpower.id)
        if user_details:
            return User.objects.only('email').get(pk=PmsPreExecutionManpowerDetails.manpower.id).email
     
    class Meta:
        model = PmsPreExecutionManpowerDetails
        fields = '__all__'
        extra_fields = ('name','contact_no','email')

class PreExecutionManpowerRequirementDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    is_deleted = serializers.BooleanField(default=True)

    class Meta:
        model = PmsPreExecutionManpowerDetails
        fields = ("id","is_deleted","updated_by")
    def update(self, instance, validated_data):
        delete_details = custom_delete(
            self, instance, validated_data,
            update_extra_columns=[],
            extra_model_with_fields=[
                {
                    'model': PmsPreExcutionUtilitiesDocument,
                    'filter_columns': {
                        'project': instance.project.id,
                        'module_id' :instance.id,
                        'model_class':"User"
                    },
                    'update_extra_columns': []

                },
            ]
        )
        return delete_details

class PreExecutionManpowerDetailsDocumentAddSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    owned_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    model_class = serializers.CharField(required=False)
    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = ('id', 'project', 'module_id', 'document_name', 'document', 'created_by', 'owned_by','model_class')

    def create(self, validated_data):
        manpower_details_document = PmsPreExcutionUtilitiesDocument.objects.create(
            **validated_data,model_class="User")
        return manpower_details_document

class PreExecutionManpowerDetailsDocumentEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = ("id","document_name","updated_by")

class PreExecutionManpowerDetailsDocumentDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    is_deleted = serializers.BooleanField(default=True)

    class Meta:
        model = PmsPreExcutionUtilitiesDocument
        fields = ("id","is_deleted","updated_by")
    def update(self, instance, validated_data):
        instance.updated_by = validated_data.get('updated_by')
        instance.is_deleted = True
        instance.save()
        return instance

#::::::::::::::::::::::::::::::::::::::PMS PRE EXECUTION COST ANALYSIS:::::::::::::::::::::::::::::::::#
class PreExecutionCostAnalysisAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    document=serializers.FileField(required=False)
    date=serializers.DateTimeField(required=False)
    document_details=serializers.SerializerMethodField(required=False)

    def get_document_details(self,PmsPreExecutionCostAnalysis):
        doc_details=PmsPreExecutionCostAnalysisDocument.objects.filter(cost_analysis=PmsPreExecutionCostAnalysis.id,is_deleted=False)
        request = self.context.get('request')
        response_list = []
        for each_document in doc_details:
            file_url = request.build_absolute_uri(each_document.document.url)
            owned_by = str(each_document.owned_by) if each_document.owned_by else ''
            created_by = str(each_document.created_by) if each_document.created_by else ''
            each_data = {
                "id": int(each_document.id),
                "cost_analysis": int(each_document.cost_analysis.id),
                "document": file_url,
                "version":each_document.version,
                "date":each_document.date,
                "created_by": created_by,
                "owned_by": owned_by
            }
            response_list.append(each_data)
        return response_list

    class Meta:
        model = PmsPreExecutionCostAnalysis
        fields = ('id', 'project', 'analysis_type', 'document_name','created_by', 'owned_by','document','date','document_details')

    def create(self, validated_data):
        try:

            last_v = PmsPreExecutionCostAnalysisDocument.objects.filter(cost_analysis__analysis_type=validated_data.get('analysis_type')).values_list('version', flat=True)
            print('last_v', last_v)
            code = ''
            if last_v:
                for lv in last_v:
                    last_v_l = lv.split(' ')
                    next_val = int(last_v_l[1]) + 1
                    code =  "version " + str(next_val)
            else:
                code = "version 1"

            document=validated_data.pop('document')
            date=validated_data.pop('date')

            owned_by = validated_data.get('owned_by')
            created_by = validated_data.get('created_by')
            with transaction.atomic():
                if not PmsPreExecutionCostAnalysis.objects.filter(document_name=validated_data.get('document_name'),
                                                                  analysis_type=validated_data.get('analysis_type')).exists():
                    cost_analysis_add = PmsPreExecutionCostAnalysis.objects.create(**validated_data)


                    analysis_doc,created_1=PmsPreExecutionCostAnalysisDocument.objects.get_or_create(cost_analysis=cost_analysis_add,
                                                                                                   created_by=created_by,
                                                                                                     date=date,
                                                                                                     version=code,
                                                                                           owned_by=owned_by,
                                                                                                  document=document)




                else:
                    cost_analysis_add=PmsPreExecutionCostAnalysis.objects.get(document_name=validated_data.get('document_name'),analysis_type=validated_data.get('analysis_type'))

                    analysis_doc, created_2 = PmsPreExecutionCostAnalysisDocument.objects.get_or_create(
                        cost_analysis=cost_analysis_add,date=date,
                        version=code,
                        created_by=created_by,
                        owned_by=owned_by,
                    document=document)

                cost_analysis_add.__dict__.pop('_state') if '_state' in cost_analysis_add.__dict__.keys() else cost_analysis_add

                analysis_doc.__dict__.pop('_state') if '_state' in analysis_doc.__dict__.keys() else analysis_doc


                return cost_analysis_add



        except Exception as e:
            raise e

#:::::::::::::::::::::: PMS PRE EXECUTION CONTRACTOR FINALIZATION::::::::::::::::::::::::::::::::::::#
class PreExecutionContractorFinalizationAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    machinery_details=serializers.SerializerMethodField(required=False)
    contractor_details=serializers.SerializerMethodField(required=False)
    def get_machinery_details(self,PmsPreExecutionContractorFinalization):
        machinery_details=PmsMachineries.objects.filter(id=PmsPreExecutionContractorFinalization.machinery.id)
        for machinery in machinery_details:
            machinery_data={
                'id':int(machinery.id),
                'equipment_name':machinery.equipment_name,
                'equipment_category':machinery.equipment_category.id,
                'equipment_type':int(machinery.equipment_type.id),
                'owner_type':int(machinery.owner_type),
                'equipment_make':machinery.equipment_make,
                'equipment_model_no':machinery.equipment_model_no,
                'equipment_chassis_serial_no':machinery.equipment_chassis_serial_no,
                'equipment_engine_serial_no':machinery.equipment_engine_serial_no,
                'equipment_registration_no':machinery.equipment_registration_no,
                'equipment_power':machinery.equipment_power,
                'measurement_by':int(machinery.measurement_by),
                'measurement_quantity':machinery.measurement_quantity,
                'fuel_consumption':machinery.fuel_consumption,
                'remarks':machinery.remarks,
            }
        return machinery_data

    def get_contractor_details(self,PmsPreExecutionContractorFinalization):
        contractor_details=PmsExternalUsers.objects.filter(id=PmsPreExecutionContractorFinalization.contractor.id)
        request = self.context.get('request')
        if contractor_details:
            for contractor in contractor_details:
                contractor_data={
                    'id':int(contractor.id),
                    'user_type':int(contractor.user_type.id),
                    'code':contractor.code,
                    'organisation_name':contractor.organisation_name,
                    'contact_no':contractor.contact_no,
                    'email':contractor.email,
                    'address':contractor.address,
                    'trade_licence_doc': request.build_absolute_uri(contractor.trade_licence_doc.url) if contractor.trade_licence_doc else '',
                    'gst_no': contractor.gst_no,
                    'gst_doc': request.build_absolute_uri(contractor.gst_doc.url) if contractor.gst_doc else '',
                    'pan_no': contractor.pan_no,
                    'pan_doc': request.build_absolute_uri(contractor.pan_doc.url) if contractor.pan_doc else '',
                    'bank_ac_no': contractor.bank_ac_no,
                    'cancelled_cheque_doc': request.build_absolute_uri(contractor.cancelled_cheque_doc.url) if contractor.cancelled_cheque_doc else '',
                    'adhar_no': contractor.adhar_no,
                    'adhar_doc': request.build_absolute_uri(contractor.adhar_doc.url) if contractor.adhar_doc else '',
                    'contact_person_name': contractor.contact_person_name,
                    'salary': contractor.salary,
                }
        else:
            contractor_data = dict()
        return contractor_data

    class Meta:
        model = PmsPreExecutionContractorFinalization
        fields = ('id',  'project', 'machinery', 'contractor', 'created_by', 'owned_by','machinery_details','contractor_details')
class PreExecutionContractorFinalizationEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsPreExecutionContractorFinalization
        fields = ('id',  'project', 'machinery', 'contractor','updated_by')
class PreExecutionContractorFinalizationDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsPreExecutionContractorFinalization
        fields = '__all__'
    def update(self, instance, validated_data):
        instance.updated_by = validated_data.get('updated_by')
        instance.is_deleted = True
        instance.save()
        return instance
class PreExecutionContractorFinalizationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PmsPreExecutionContractorFinalization
        fields = '__all__'

#:::::::::::::::::::::::::::::::::: PMS PRE EXECUTION SITE PUJA::::::::::::::::::::::::::::::::::::::::::::::#
class PreExecutionSitePujaAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsPreExecutionSitePuja
        fields = ('id', 'project', 'location', 'latitude', 'longitude', 'date', 'budget', 'created_by', 'owned_by')
class PreExecutionSitePujaEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsPreExecutionSitePuja
        fields = ('id', 'project', 'location', 'latitude', 'longitude', 'date', 'budget', 'updated_by')
class PreExecutionSitePujaDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsPreExecutionSitePuja
        fields = '__all__'
    def update(self, instance, validated_data):
        instance.is_deleted=True
        instance.updated_by = validated_data.get('updated_by')
        instance.save()
        return instance

#::::::::::::::::::::::::PMS PRE EXECUTION APPROVAL:::::::::::::::#
class PreExecutionApprovalEditSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    request_modification=serializers.CharField(required=False)
    class Meta:
        model = PmsPreExecutionApproval
        fields = '__all__'
    def create(self, validated_data):
        try:
            existing_pre_ex_approval=PmsPreExecutionApproval.objects.filter(project=validated_data.get('project'),
                                                                            pre_execution_tabs=validated_data.get('pre_execution_tabs'))

            if existing_pre_ex_approval:

                for pre_ex_approval in existing_pre_ex_approval:
                    pre_ex_approval.project=validated_data.get('project')
                    pre_ex_approval.pre_execution_tabs=validated_data.get('pre_execution_tabs')
                    pre_ex_approval.approved_status=validated_data.get('approved_status')
                    pre_ex_approval.request_modification=validated_data.get('request_modification')
                    pre_ex_approval.updated_by=validated_data.get('created_by')
                    pre_ex_approval.save()

                    response={
                        'id':pre_ex_approval.id,
                        'project':pre_ex_approval.project,
                        'pre_execution_tabs':pre_ex_approval.pre_execution_tabs,
                        'approved_status':pre_ex_approval.approved_status,
                        'request_modification':pre_ex_approval.request_modification,
                        'updated_by':pre_ex_approval.updated_by,
                    }

                return response
            else:
                return PmsPreExecutionApproval.objects.create(**validated_data)


        except Exception as e:
            raise e


