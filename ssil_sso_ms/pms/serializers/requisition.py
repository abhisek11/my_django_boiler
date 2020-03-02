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
from pagination import CSLimitOffestpagination,CSPageNumberPagination
from rest_framework import filters
import calendar
from custom_exception_message import *
from datetime import datetime
from holidays.models import *
import collections
from rest_framework.exceptions import APIException
import pandas as pd
import numpy as np
from django_filters.rest_framework import DjangoFilterBackend
from master.serializers import UserModuleWiseListSerializer
from master.models import TMasterModuleRole
from users.models import TCoreUserDetail
from custom_decorator import *
from rest_framework.parsers import FileUploadParser
import os
from pms.custom_filter import *
from datetime import datetime
from django.db.models.functions import Concat
from django.db.models import Value

###############PLANNING AND REPORTING ########################
class ExecutionProjectPlaningAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    project_details_of_site = serializers.DictField(required=False)
    field_label_value = serializers.ListField(required=False)
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsExecutionProjectPlaningMaster
        fields = ('id', 'project', 'site_location', 'name_of_work',
                  'created_by', 'owned_by', 'updated_by', 'created_at',
                  'updated_at', 'project_details_of_site', 'field_label_value')

    def create(self, validated_data):
        try:
            with transaction.atomic():

                field_label_value = validated_data.pop(
                    'field_label_value') if 'field_label_value' in validated_data else ""
                site_details = PmsSiteProjectSiteManagement.objects.filter(pk=str(validated_data.get("site_location"))). \
                    values('name', 'company_name')
                project_duration = PmsProjects.objects.filter(pk=str(validated_data.get("project"))). \
                    values('start_date', 'end_date')
                project_details_of_site = {'site_details': site_details, 'project_duration': project_duration}
                id = ''
                existing_project_palnning = PmsExecutionProjectPlaningMaster.objects.filter(
                    project=validated_data.get('project'), site_location=validated_data.get('site_location'))
                print(existing_project_palnning)
                for i in existing_project_palnning:
                    id = i.id
                if existing_project_palnning:
                    PmsExecutionProjectPlaningMaster.objects.filter(
                        project=validated_data.get('project'),
                        site_location=validated_data.get('site_location')).delete()
                    PmsExecutionProjectPlaningFieldLabel.objects.filter(project_planning_id=id).delete()
                    PmsExecutionProjectPlaningFieldValue.objects.filter(project_planning_id=id).delete()

                    project_planning_data = PmsExecutionProjectPlaningMaster.objects.create(
                        **validated_data
                    )
                    print("project_planning_data::::::", project_planning_data)
                    for each_field_label_value in field_label_value:
                        project_planning_label = PmsExecutionProjectPlaningFieldLabel. \
                            objects.create(
                            project_planning=PmsExecutionProjectPlaningMaster.objects.get(pk=project_planning_data.id),
                            field_label=each_field_label_value['field_label'],
                            created_by=validated_data.get('created_by'),
                            owned_by=validated_data.get('owned_by')
                        )
                        for field_value in each_field_label_value['field_value']:
                            project_planning_label_value = PmsExecutionProjectPlaningFieldValue. \
                                objects.create(
                                project_planning=PmsExecutionProjectPlaningMaster.objects.get(
                                    pk=project_planning_data.id),
                                initial_field_label=project_planning_label,
                                field_value=field_value,
                                created_by=validated_data.get('created_by'),
                                owned_by=validated_data.get('owned_by')
                            )
                else:
                    print('validated_data', validated_data)
                    project_planning_data = PmsExecutionProjectPlaningMaster.objects.create(
                        **validated_data)

                    for each_field_label_value in field_label_value:
                        project_planning_label = PmsExecutionProjectPlaningFieldLabel. \
                            objects.create(
                            project_planning=PmsExecutionProjectPlaningMaster.objects.get(pk=project_planning_data.id),
                            field_label=each_field_label_value['field_label'],
                            created_by=validated_data.get('created_by'),
                            owned_by=validated_data.get('owned_by')
                        )
                        for field_value in each_field_label_value['field_value']:
                            project_planning_label_value = PmsExecutionProjectPlaningFieldValue. \
                                objects.create(
                                project_planning=PmsExecutionProjectPlaningMaster.objects.get(
                                    pk=project_planning_data.id),
                                initial_field_label=project_planning_label,
                                field_value=field_value,
                                created_by=validated_data.get('created_by'),
                                owned_by=validated_data.get('owned_by')
                            )
                response_data = {
                    'id': project_planning_data.id,
                    'project': project_planning_data.project,
                    'site_location': project_planning_data.site_location,
                    'project_details_of_site': project_details_of_site,
                    'name_of_work': project_planning_data.name_of_work,
                    'created_by': project_planning_data.created_by,
                    'owned_by': project_planning_data.owned_by,
                    'field_label_value': field_label_value
                }
                return response_data


        except Exception as e:
            raise e


class ExecutionProjectPlaningviewSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    #status = serializers.BooleanField(default=True)
    field_label_value = serializers.ListField(required=False)
    project_details_of_site = serializers.DictField(required=False)

    class Meta:
        model = PmsExecutionProjectPlaningMaster
        fields = ('id', 'project', 'site_location', 'name_of_work',
                  'created_by', 'owned_by', 'updated_by', 'created_at',
                  'updated_at', 'project_details_of_site', 'field_label_value')


class DailyReportProgressSerializeradd(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())

    progress_data = serializers.ListField(required=False)

    class Meta:
        model = PmsExecutionDailyProgress
        fields = ('__all__')
        extra_fields = ('progress_data')

    def create(self, validated_data):
        try:
            progress_data = validated_data.pop('progress_data') if 'progress_data' in validated_data else ""
            owned_by = validated_data.get('owned_by')
            created_by = validated_data.get('created_by')
            with transaction.atomic():
                date_entry = validated_data.get('date_entry')
                pmsExecutionDailyProgres_exist = PmsExecutionDailyProgress.objects.filter(
                    project_id = validated_data.get('project_id'), 
                    site_location = validated_data.get('site_location'), 
                    date_entry__year = date_entry.year,
                    date_entry__month = date_entry.month,
                    date_entry__day = date_entry.day,
                    type_of_report = validated_data.get('type_of_report')
                )
                print('pmsExecutionDailyProgres_exist',pmsExecutionDailyProgres_exist)

                if not pmsExecutionDailyProgres_exist: 
                    pedp_data = PmsExecutionDailyProgress.objects.create(**validated_data)

                else:
                    pedp_data = PmsExecutionDailyProgress.objects.get(
                        project_id = validated_data.get('project_id') , 
                        site_location = validated_data.get('site_location'), 
                        date_entry__year = date_entry.year,
                        date_entry__month = date_entry.month,
                        date_entry__day = date_entry.day,
                        type_of_report = validated_data.get('type_of_report')
                        )
                    #print('pedp_data',pedp_data)
                for pro_data in progress_data:
                    pedpp_data, created2 = PmsExecutionDailyProgressProgress.objects.get_or_create(
                        daily_progress=pedp_data,
                        created_by=created_by,
                        owned_by=owned_by,
                        **pro_data
                        )
                  
               
                return validated_data

        except Exception as e:
            raise e


class DailyReportlabourSerializeradd(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())

    labour_data = serializers.ListField(required=False)

    class Meta:
        model = PmsExecutionDailyProgress
        fields = ('__all__')
        extra_fields = ('labour_data')

    def create(self, validated_data):
        try:
            labour_data = validated_data.pop('labour_data') if 'labour_data' in validated_data else ""
            owned_by = validated_data.get('owned_by')
            created_by = validated_data.get('created_by')
            #print('validated_data',validated_data)
            with transaction.atomic():
                date_entry = validated_data.get('date_entry')
                pmsExecutionDailyProgres_exist = PmsExecutionDailyProgress.objects.filter(
                    project_id = validated_data.get('project_id'), 
                    site_location = validated_data.get('site_location'), 
                    date_entry__year = date_entry.year,
                    date_entry__month = date_entry.month,
                    date_entry__day = date_entry.day,
                    type_of_report = validated_data.get('type_of_report')
                )
                print('pmsExecutionDailyProgres_exist',pmsExecutionDailyProgres_exist)

                if not pmsExecutionDailyProgres_exist: 
                    pedl_data = PmsExecutionDailyProgress.objects.create(**validated_data)
                else:
                    pedl_data = PmsExecutionDailyProgress.objects.get(
                        project_id = validated_data.get('project_id') , 
                        site_location = validated_data.get('site_location'), 
                        date_entry__year = date_entry.year,
                        date_entry__month = date_entry.month,
                        date_entry__day = date_entry.day,
                        type_of_report = validated_data.get('type_of_report')
                        )
                
                for lab_data in labour_data:
                    #print('lab_data',type(lab_data['name_of_contractor']))
                    created2 = PmsExecutionDailyProgressLabourReport.objects.create(
                        labour_report=pedl_data,
                        created_by=created_by,
                        owned_by=owned_by,
                        **lab_data
                        )
                return validated_data
        except Exception as e:
            raise e


class DailyReportPandMSerializeradd(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())

    p_and_m_data = serializers.ListField(required=False)

    class Meta:
        model = PmsExecutionDailyProgress
        fields = ('__all__')
        extra_fields = ('p_and_m_data')

    def create(self, validated_data):
        try:
            p_and_m_data = validated_data.pop('p_and_m_data') if 'p_and_m_data' in validated_data else ""
            owned_by = validated_data.get('owned_by')
            created_by = validated_data.get('created_by')
            with transaction.atomic():
                date_entry = validated_data.get('date_entry')
                pmsExecutionDailyProgres_exist = PmsExecutionDailyProgress.objects.filter(
                    project_id = validated_data.get('project_id'), 
                    site_location = validated_data.get('site_location'), 
                    date_entry__year = date_entry.year,
                    date_entry__month = date_entry.month,
                    date_entry__day = date_entry.day,
                    type_of_report = validated_data.get('type_of_report')
                )
                if not pmsExecutionDailyProgres_exist: 
                    pedpnm_data = PmsExecutionDailyProgress.objects.create(**validated_data)
                else:
                    pedpnm_data = PmsExecutionDailyProgress.objects.get(
                        project_id = validated_data.get('project_id') , 
                        site_location = validated_data.get('site_location'), 
                        date_entry__year = date_entry.year,
                        date_entry__month = date_entry.month,
                        date_entry__day = date_entry.day,
                        type_of_report = validated_data.get('type_of_report')
                        )
                for pandm_data in p_and_m_data:
                    pedppnm_data, created2 = PmsExecutionDailyProgressPandM.objects.get_or_create(
                        plan_machine_report=pedpnm_data,
                        created_by=created_by,
                        owned_by=owned_by,
                        **pandm_data
                        )
                return validated_data
        except Exception as e:
            raise e


class DailyReportProgressSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    execution_daily_pro = serializers.SerializerMethodField()

    def get_execution_daily_pro(self, PmsExecutionDailyProgress):
        # total_data = list()
        pro_list=[]
        e_d_p = PmsExecutionDailyProgressProgress.objects.filter(daily_progress=PmsExecutionDailyProgress.id,is_deleted=False)
        for data in e_d_p:
            if data:
                data.__dict__.pop('_state') if "_state" in data.__dict__.keys() else data.__dict__

                data.__dict__["activity_details"]=[x for x in            PmsExecutionPurchasesRequisitionsActivitiesMaster.objects.filter(id=data.__dict__["activity_id"],is_deleted=False).values('id','code','description')][0]
                data.__dict__["contractor_details"]=[x for x in PmsExternalUsers.objects.filter(
                    id=data.__dict__["contractors_name_id"],is_deleted=False).values(
                        'id','code','contact_person_name')][0]
                data.__dict__["uom_details"]=[x for x in TCoreUnit.objects.filter(
                    id=data.__dict__["uom_id"],c_is_deleted=False).values('id','c_name')][0]
                data.__dict__["assigned_to_details"]=[x for x in User.objects.annotate(name=Concat('first_name',Value(' '),'last_name')).filter(
                    id=data.__dict__["assigned_to_id"]).values(
                    'id','username','name')][0]
                data.__dict__["date_entry"] = PmsExecutionDailyProgress.date_entry
                print("data::::::",data.__dict__)
                pro_list.append(data.__dict__)
            else:[]
        return pro_list

    class Meta:
        model = PmsExecutionDailyProgress
        fields = ('__all__')
        extra_fields = ('execution_daily_pro')





class DailyReportlabourSerializerview(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())

    execution_daily_lab = serializers.SerializerMethodField()

    def get_execution_daily_lab(self, PmsExecutionDailyProgress):
        # total_data = list()
        lab_list=[]
        e_d_l = PmsExecutionDailyProgressLabourReport.objects.filter(labour_report=PmsExecutionDailyProgress.id)
        #print('e_d_l',e_d_l)
        for data in e_d_l:
            data.__dict__.pop('_state') if "_state" in data.__dict__.keys() else data.__dict__
            data.__dict__["contractor_details"]=[x for x in PmsExternalUsers.objects.filter(
                    id=data.__dict__["name_of_contractor_id"],is_deleted=False).values(
                        'id','code','contact_person_name')][0]
            data.__dict__["date_entry"] = PmsExecutionDailyProgress.date_entry
            lab_list.append(data.__dict__)
        return lab_list

    class Meta:
        model = PmsExecutionDailyProgress
        fields = ('__all__')
        extra_fields = ('execution_daily_lab')


class DailyReportPandMSerializerview(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())

    execution_daily_pandm = serializers.SerializerMethodField()

    def get_execution_daily_pandm(self, PmsExecutionDailyProgress):
        # total_data = list()
        pandm_list=[]
        e_d_l = PmsExecutionDailyProgressPandM.objects.filter(plan_machine_report=PmsExecutionDailyProgress.id)
        print('e_d_l',e_d_l)
        for data in e_d_l:
            data.__dict__.pop('_state') if "_state" in data.__dict__.keys() else data.__dict__
            data.__dict__["machinery_used_details"]=[x for x in PmsMachineries.objects.filter(
                    id=data.__dict__["machinery_used_id"],is_deleted=False).values(
                        'id','code','equipment_name')][0]
            data.__dict__["uom_details"]=[x for x in TCoreUnit.objects.filter(
                    id=data.__dict__["unit_details_id"],c_is_deleted=False).values('id','c_name')][0]
            data.__dict__["date_entry"] = PmsExecutionDailyProgress.date_entry
            pandm_list.append(data.__dict__) 
        return pandm_list

    class Meta:
        model = PmsExecutionDailyProgress
        fields = ('__all__')
        extra_fields = ('execution_daily_pandm')



#::::::::::  PMS EXECUTION PURCHASES REQUISITIONS ACTIVITIES MASTER ADD ;::::::::#
class ExecutionPurchasesRequisitionsActivitiesMasterAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsExecutionPurchasesRequisitionsActivitiesMaster
        fields = ('__all__')

#::::::::::  PMS EXECUTION PURCHASES REQUISITIONS ACTIVITIES MASTER EDIT ;::::::::#
class ExecutionPurchasesRequisitionsActivitiesMasterEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsExecutionPurchasesRequisitionsActivitiesMaster
        fields = ('id','code','description','updated_by')

#::::::::::  PMS EXECUTION PURCHASES REQUISITIONS ACTIVITIES MASTER DELETE ;::::::::#
class ExecutionPurchasesRequisitionsActivitiesMasterDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsExecutionPurchasesRequisitionsActivitiesMaster
        fields = ('id','is_deleted','updated_by')

    def update(self, instance, validated_data):
        try:
            with transaction.atomic():
                instance.is_deleted = True
                instance.save()
                return instance
        except Exception as e:
            raise APIException({'request_status': 0, 'msg': e})

#::::::::::  PMS EXECUTION PURCHASES REQUISITIONS SITE TO PROJECT ID LIST;::::::::#
# class PurchaseRequisitionsSiteToProjectIDListSerializer(serializers.ModelSerializer):
#     created_by = serializers.CharField(default=serializers.CurrentUserDefault())
#     owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
#
#     class Meta:
#         model = PmsProjects
#         fields = ('__all__')

# #::::::::::  PMS EXECUTION PURCHASES REQUISITIONS ADD  :::::::::::#
class PurchaseRequisitionsAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    requisition_details = serializers.ListField(required=False)
    requisition_master = serializers.CharField(required=False)
    #requisitions_date = serializers.CharField(required=False)
    # item_description=
    #activity_list = serializers.ListField(required=False)
    class Meta:
        model = PmsExecutionPurchasesRequisitionsMaster
        fields = ('id', 'requisition_master', 'mr_date','site_location','project','type','status',
                  'requisition_details','created_by', 'owned_by')

    def create(self, validated_data):
        #requisition_list = list()
        # print('validated_data',validated_data)   
        created_by = validated_data.get('created_by')
        owned_by = validated_data.get('owned_by')
        requisition_details = validated_data.get('requisition_details')
        # print('requisition_details',requisition_date)
        data_dict = {}
        with transaction.atomic():
            re_date = PmsExecutionPurchasesRequisitionsMaster.objects.create(
                mr_date = validated_data.get('mr_date'),
                site_location= validated_data.get('site_location'),
                project= validated_data.get('project'),
                type= validated_data.get('type'),
                #status=validated_data.get('status'),
                created_by=created_by,
                owned_by = owned_by
            )
            # print('re_date',re_date)
            validated_data['requisition_master']=re_date.id

            for e_requisition_details in requisition_details:
                # print('uom',e_requisition_details['uom'])
                uom_id=e_requisition_details['uom'] if 'uom' in e_requisition_details else ""
                hsn_sac_code=e_requisition_details['hsn_sac_code'] if 'hsn_sac_code' in e_requisition_details else ""
                item_data= e_requisition_details['item'] if 'item' in e_requisition_details else custom_exception_message(self,None,"Please give Item for moving forward")
                current_stock = e_requisition_details['current_stock'] if 'current_stock' in e_requisition_details else 0.00
                quantity = e_requisition_details['quantity'] if 'quantity' in e_requisition_details else 0.00
                procurement_site = e_requisition_details['procurement_site'] if 'procurement_site' in e_requisition_details else 0.00
                procurement_ho = e_requisition_details['procurement_ho'] if 'procurement_ho' in e_requisition_details else 0.00
                # current_stock=PmsExecutionUpdatedStock.objects.filter(project=validated_data.get('project'),
                #                                                     site_location=validated_data.get('site_location'),
                #                                                     type=validated_data.get('type'),
                #                                                     item=e_requisition_details['item'],
                #                                                     uom=e_requisition_details['uom']).values('opening_stock')

                # current_stock_data=[x for x in current_stock][0]
                # print("current_stock",current_stock_data)
                # print('uom_id',uom_id)

                re_details = PmsExecutionPurchasesRequisitions.objects.create(
                    requisitions_master = re_date,
                    item=e_requisition_details['item'],
                    hsn_sac_code=hsn_sac_code,
                    uom_id= uom_id,
                    quantity= quantity,
                    current_stock= current_stock,
                    procurement_site= procurement_site,
                    procurement_ho= procurement_ho,
                    required_by=e_requisition_details['required_by'],
                    required_on=datetime.strptime(e_requisition_details['required_on'],"%Y-%m-%dT%H:%M:%S.%fZ"),
                    remarks=e_requisition_details['remarks'],
                    created_by = created_by,
                    owned_by = owned_by
                )
                # print('re_details',re_details)

                ac_details =e_requisition_details['activity_details']
                for e_ac_details in ac_details:
                    PmsExecutionPurchasesRequisitionsMapWithActivities.objects.create(
                        requisitions = re_details,
                        activity_id = e_ac_details['activity'],
                        created_by=created_by,
                        owned_by=owned_by
                    )
                    # print('e_ac_details',e_ac_details)

            return validated_data

class PurchaseRequisitionsForAndroidAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    requisition_details = serializers.DictField(required=False)
    requisition_master = serializers.CharField(required=False)
    class Meta:
        model = PmsExecutionPurchasesRequisitionsMaster
        fields = ('id', 'requisition_master', 'mr_date','site_location','project','type','status',
                  'requisition_details','created_by', 'owned_by')

    def create(self, validated_data):
        created_by = validated_data.get('created_by')
        owned_by = validated_data.get('owned_by')

        requisition_master = validated_data.get('requisition_master')
        requisition_details = validated_data.get('requisition_details')

        data_dict = {}

        # print("ReqData ",requisition_master)
        with transaction.atomic():
            if not PmsExecutionPurchasesRequisitionsMaster.objects.filter(id=requisition_master).exists():
                re_date = PmsExecutionPurchasesRequisitionsMaster.objects.create(
                    mr_date = validated_data.get('mr_date'),
                    site_location= validated_data.get('site_location'),
                    project= validated_data.get('project'),
                    type= validated_data.get('type'),
                    #status=validated_data.get('status'),
                    created_by=created_by,
                    owned_by = owned_by
                )
                # print('re_date',re_date)
                validated_data['requisition_master']=re_date.id
                req_data = str(re_date)
            else:
                # print("Exist")
                # validated_data['requisition_master']=requisition_master
                req_data = int(requisition_master)
                # print('re_date_else',req_data)

            uom_id=requisition_details['uom'] if 'uom' in requisition_details else ""
            hsn_sac_code=requisition_details['hsn_sac_code'] if 'hsn_sac_code' in requisition_details else ""
            current_stock = requisition_details['current_stock'] if 'current_stock' in requisition_details else 0.00

            re_details = PmsExecutionPurchasesRequisitions.objects.create(
                    requisitions_master_id = req_data,
                    item=requisition_details['item'],
                    hsn_sac_code=hsn_sac_code,
                    uom_id= uom_id,
                    quantity=requisition_details['quantity'],
                    current_stock=current_stock,
                    procurement_site=requisition_details['procurement_site'],
                    procurement_ho=requisition_details['procurement_ho'],
                    required_by=requisition_details['required_by'],
                    required_on=datetime.strptime(requisition_details['required_on'],"%Y-%m-%dT%H:%M:%S.%fZ"),
                    remarks=requisition_details['remarks'],
                    created_by = created_by,
                    owned_by = owned_by
                )
            # print('re_details',re_details)

            ac_details =requisition_details['activity_details']
            for e_ac_details in ac_details:
                PmsExecutionPurchasesRequisitionsMapWithActivities.objects.create(
                    requisitions = re_details,
                    activity_id = e_ac_details['activity'],
                    created_by=created_by,
                    owned_by=owned_by
                )
                # print('e_ac_details',e_ac_details)

            return validated_data
        
        

class PurchaseRequisitionsSumbmitApprovalSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    status = serializers.IntegerField(default=1)
    requisition_details = serializers.ListField(required=False)
    type= serializers.DictField(required=False)
    module_name = serializers.CharField(required=False)
    class Meta:
        model = PmsExecutionPurchasesRequisitionsMaster
        fields = ('id','site_location' ,'project','type','module_name','status',
                  'requisition_details','updated_by','completed_status')

    def update(self, instance, validated_data):
        try:
            #with transaction.atomic():
            update_status=0
            owned_by = validated_data.get('owned_by')
            created_by = validated_data.get('created_by')
            module_name = validated_data.get('module_name') if 'module_name' in validated_data else ''
            type = validated_data.get('type')
            
            requisition_details = validated_data.get('requisition_details')
            # print('validate data',validated_data)
            with transaction.atomic():
                requisitions_m_status = PmsExecutionPurchasesRequisitionsMaster.objects.only('status').get(
                    is_deleted=False,id=instance.id).status
                # print('requisitions_m_status',requisitions_m_status)
                if module_name == 'requisitions_tab':
                    if requisitions_m_status == 0:
                        # print("requisitions_m_status == None")
                        # print("status_id",instance.id)
                        update_status = PmsExecutionPurchasesRequisitionsMaster.objects.filter(
                            is_deleted=False,id=instance.id).update(status=1)

                        # print('update_status',update_status)

                    #pms_req_master=PmsExecutionPurchasesRequisitionsMaster.objects.filter(id=instance.id)
                    #req_data=PmsExecutionPurchasesRequisitions.objects.filter(requisitions_master=instance.id)
                    if update_status:
                        if requisition_details:
                            for e_item_d in requisition_details:
                                # print('e_item_d',e_item_d['current_stock'])
                                current_s = e_item_d['current_stock'] if 'current_stock' in e_item_d else 0.00
                                # print('current_s',current_s)
                                PmsExecutionStock.objects.create(
                                        which_requisition_tab="requisition",
                                        project=validated_data.get('project'),
                                        site_location=validated_data.get('site_location'),
                                        opening_stock=current_s,
                                        uom_id=e_item_d['uom'],
                                        item=e_item_d['id'],
                                        type_id=type['id'],
                                        requisition=instance,
                                        created_by = created_by,
                                        owned_by = owned_by
                                    )
                                # print('dsfdsfdfsdf')
                                exist_updated_stock_ck=PmsExecutionUpdatedStock.objects.filter(
                                        project=validated_data.get('project'),
                                        site_location=validated_data.get('site_location'),
                                        item=e_item_d['id'],
                                        type_id=type['id'],
                                        uom_id=e_item_d['uom'],
                                        )
                                # print('exist_updated_stock_ck',exist_updated_stock_ck)
                                if exist_updated_stock_ck:
                                    # print('current_s',current_s)
                                    for e_exist_updated_stock_ck in exist_updated_stock_ck:
                                        e_exist_updated_stock_ck.opening_stock = current_s
                                        e_exist_updated_stock_ck.issued_stock = 0.00
                                        e_exist_updated_stock_ck.recieved_stock = 0.00
                                        e_exist_updated_stock_ck.updated_by = owned_by
                                        e_exist_updated_stock_ck.save()
                                else:
                                    p=PmsExecutionUpdatedStock.objects.create(
                                    project=validated_data.get('project'),
                                    site_location=validated_data.get('site_location'),
                                    opening_stock=current_s,
                                    issued_stock = 0.00,
                                    recieved_stock = 0.00,
                                    uom_id=e_item_d['uom'],
                                    item=e_item_d['id'],
                                    type_id=type['id'],
                                    requisition=instance,
                                    created_by = created_by,
                                    owned_by = owned_by
                                    )

                            return validated_data

                    else:
                        instance.status = validated_data.get('status')
                        instance.save()
                        return instance
                else:
                    update_status = PmsExecutionPurchasesRequisitionsMaster.objects.filter(
                        is_deleted=False, id=instance.id).update(status=validated_data.get('status'),completed_status=validated_data.get('completed_status'))

                    return validated_data
        except Exception as e:
            raise e 


# #::::::::::  PMS EXECUTION PURCHASES REQUISITIONS LIST  :::::::::::#
class PurchaseRequisitionsListSerializer(serializers.ModelSerializer):

    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    # actual_consumption_approval = serializers.SerializerMethodField()
    # current_stock = serializers.SerializerMethodField()

    class Meta:
        model = PmsExecutionPurchasesRequisitionsMaster
        fields = ('__all__')
    
    # def get_current_stock(self, PmsExecutionPurchasesRequisitionsApproval):
    #     #print('self',self.context.get('view').kwargs.get('requisition_id'))
    #     #requisition_id = self.context.get('view').kwargs.get('requisition_id')
    #     project_id = self.context.get('view').kwargs.get('project_id')
    #     site_id = self.context.get('view').kwargs.get('site_id')
    #     stock_details = PmsExecutionUpdatedStock.objects.filter(
    #         project=project_id,
    #         site_location=site_id,
    #         item=PmsExecutionPurchasesRequisitionsApproval.item,
    #         type=PmsExecutionPurchasesRequisitionsApproval.type,
    #         uom=PmsExecutionPurchasesRequisitionsApproval.uom
    #     )
    #     #print('stock_details',stock_details)
    #     #current_stock = 0.0
    #     if stock_details:
    #         for e_stock_details in stock_details:
    #             if e_stock_details.issued_stock:
    #                 t_issued_stock = float(e_stock_details.issued_stock)
    #             else:
    #                 t_issued_stock = 0.0

    #             if e_stock_details.opening_stock:
    #                 t_opening_stock = float(e_stock_details.opening_stock)
    #             else:
    #                 t_opening_stock = 0.0

    #             if e_stock_details.recieved_stock:
    #                 t_recieved_stock = float(e_stock_details.recieved_stock)
    #             else:
    #                 t_recieved_stock = 0.0
    #             current_stock = (t_opening_stock + t_recieved_stock) - t_issued_stock
    #             #print('current_stock',current_stock)

    #     else:
    #         current_stock = 0.00
    #     return current_stock

    # def get_actual_consumption_approval(self, PmsExecutionPurchasesRequisitionsApproval):
    #     try:
    #         with transaction.atomic():
    #             from django.db.models import Sum
    #             print(PmsExecutionPurchasesRequisitionsApproval)
    #             item_d = Materials.objects.filter(id=PmsExecutionPurchasesRequisitionsApproval.item).values('id','name')
    #             # unit_d = PmsExecutionPurchasesRequisitions.objects. \
    #             #              filter(requisitions_master=PmsExecutionPurchasesRequisitionsApproval.requisitions_master,
    #             #                     item=PmsExecutionPurchasesRequisitionsApproval.uom).values('uom')[:1]
                
    #             #u = [x['uom'] for x in unit_d]
    #             unit_details = TCoreUnit.objects.filter(pk=PmsExecutionPurchasesRequisitionsApproval.uom.id).values('id', 'c_name')
    #             print("unit_details:::::",unit_details)
    #             if unit_details:
    #                 req_master_details = PmsExecutionPurchasesRequisitionsMaster.objects. \
    #                     filter(project=PmsExecutionPurchasesRequisitionsApproval.project,
    #                         site_location=PmsExecutionPurchasesRequisitionsApproval.site_location,
    #                         status=5, type=PmsExecutionPurchasesRequisitionsApproval.type).order_by('-id')
    #                 approval_list = []
    #                 query_list = []
    #                 totals = 0
    #                 c = 0
    #                 last_3_avg = 0
                    
    #                 for req_master in req_master_details:
    #                     if req_master:
    #                         qr_details = PmsExecutionPurchasesRequisitions.objects. \
    #                             filter(requisitions_master=req_master.id, item=PmsExecutionPurchasesRequisitionsApproval.item). \
    #                             aggregate(Sum('quantity'))['quantity__sum']
    #                         if qr_details is not None:
    #                             totals = totals + qr_details
    #                             if c < 3:
    #                                 last_3_avg = last_3_avg + qr_details
    #                                 c = c + 1
    #                 latest = PmsExecutionPurchasesRequisitions.objects. \
    #                     filter(requisitions_master=PmsExecutionPurchasesRequisitionsApproval.requisitions_master,
    #                         item=PmsExecutionPurchasesRequisitionsApproval.item). \
    #                     aggregate(Sum('quantity'))['quantity__sum']
    #                 remarks_details = PmsExecutionPurchasesRequisitions.objects. \
    #                     filter(requisitions_master=PmsExecutionPurchasesRequisitionsApproval.requisitions_master,
    #                         item=PmsExecutionPurchasesRequisitionsApproval.item).values("remarks").distinct()
    #                 print("remarks_details:::::::", remarks_details)
    #                 actual_consumption = {}
    #                 actual_consumption = {'total_previous_requisition': totals,
    #                                     'avg_of_last_three_requsition': last_3_avg,
    #                                     'new_requsition': latest,
    #                                     'item_name': [x for x in item_d][0]['name'],
    #                                     'unit_name': [x for x in unit_details][0]['c_name'],
    #                                     'remarks': [x for x in remarks_details][0]['remarks']

    #                                     }

    #                 return actual_consumption
    #             else:
    #                 req_master_details = PmsExecutionPurchasesRequisitionsMaster.objects. \
    #                     filter(project=PmsExecutionPurchasesRequisitionsApproval.project,
    #                         site_location=PmsExecutionPurchasesRequisitionsApproval.site_location,
    #                         status=5, type=PmsExecutionPurchasesRequisitionsApproval.type).order_by('-id')
    #                 approval_list = []
    #                 query_list = []
    #                 totals = 0
    #                 c = 0
    #                 last_3_avg = 0
                    
    #                 for req_master in req_master_details:
    #                     if req_master:
    #                         qr_details = PmsExecutionPurchasesRequisitions.objects. \
    #                             filter(requisitions_master=req_master.id, item=PmsExecutionPurchasesRequisitionsApproval.item). \
    #                             aggregate(Sum('quantity'))['quantity__sum']
    #                         if qr_details is not None:
    #                             totals = totals + qr_details
    #                             if c < 3:
    #                                 last_3_avg = last_3_avg + qr_details
    #                                 c = c + 1
    #                 latest = PmsExecutionPurchasesRequisitions.objects. \
    #                     filter(requisitions_master=PmsExecutionPurchasesRequisitionsApproval.requisitions_master,
    #                         item=PmsExecutionPurchasesRequisitionsApproval.item). \
    #                     aggregate(Sum('quantity'))['quantity__sum']
    #                 remarks_details = PmsExecutionPurchasesRequisitions.objects. \
    #                     filter(requisitions_master=PmsExecutionPurchasesRequisitionsApproval.requisitions_master,
    #                         item=PmsExecutionPurchasesRequisitionsApproval.item).values("remarks").distinct()
    #                 print("remarks_details:::::::", remarks_details)
    #                 actual_consumption = {}
    #                 actual_consumption = {'total_previous_requisition': totals,
    #                                     'avg_of_last_three_requsition': last_3_avg,
    #                                     'new_requsition': latest,
    #                                     'item_name': [x for x in item_d][0]['name'],
    #                                     'unit_name': None,
    #                                     'remarks': [x for x in remarks_details][0]['remarks']

    #                                     }

    #                 return actual_consumption
    
    #     except Exception as e:
    #         raise e

# #::::::::::  PMS EXECUTION PURCHASES REQUISITIONS TOTAL LIST  :::::::::::#
class PurchaseRequisitionsTotalListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PmsExecutionPurchasesRequisitionsMaster
        fields = ('id', 'mr_date', 'project', 'site_location', 'type','status','get_status_display')


#MOBILE LISTING FOR REQUISITION 
class PurchaseRequisitionsNotApprovalMobileListSerializer(serializers.ModelSerializer):
    requisition_details = serializers.SerializerMethodField(required=False)

    def get_requisition_details(self,PmsExecutionPurchasesRequisitionsMaster):
        print("PmsExecutionPurchasesRequisitionsMaster::",PmsExecutionPurchasesRequisitionsMaster.id)
        requisition_details=PmsExecutionPurchasesRequisitions.objects.filter(requisitions_master=PmsExecutionPurchasesRequisitionsMaster.id,is_deleted=False).values()
        if requisition_details:
            return requisition_details

    class Meta:
        model = PmsExecutionPurchasesRequisitionsMaster
        fields = ('__all__')
        extra_fields = ('requisition_details')


        

#:::::::::: PMS EXECUTION PURCHASES REQUISITIONS DATA EDIT :::::::::#
class PurchaseRequisitionsEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    requisition_list = serializers.ListField(required=False)
    activity_details = serializers.ListField(required=False)
    class Meta:
        model = PmsExecutionPurchasesRequisitionsMaster
        fields = ('id','updated_by','requisition_list','activity_details')

    def update(self,instance, validated_data):
        # print("instance",instance)
        try:
            requisition = validated_data.pop('requisition_list')if 'requisition_list' in validated_data else ""
            updated_by = validated_data.get('updated_by')
            with transaction.atomic():
                req_details = PmsExecutionPurchasesRequisitions.objects.filter(requisitions_master=instance, is_deleted=False)
                if req_details:
                    req_details.delete()
                requisition_details_list = list()
                for req in requisition:
                    activity_v_list = req['activity_details']
                    #print('activity_list',activity_v_list)
                    # unit_id = validated_data.get(req['uom_id']) if req['uom_id'] in validated_data else "",
                    # print("unit_id",req.keys())
                    if 'uom' in req.keys():
                        # print("requnvfhjcfwehj",req['uom_id'])
                        unit_id = req['uom']
                    #
                    else:
                        unit_id = ''
                    current_stock = req['current_stock'] if 'current_stock' in req else 0.00
                    quantity=req['quantity'] if 'quantity' in req else 0.00
                    procurement_site=req['procurement_site'] if 'procurement_site' in req else 0.00
                    procurement_ho=req['procurement_ho'] if 'procurement_ho' in req else 0.00
                    hsn_sac_code= req['hsn_sac_code'] if 'hsn_sac_code' in req else ""
                    requisition_details = PmsExecutionPurchasesRequisitions.objects.create(
                        requisitions_master=instance,
                        item=req['item'],
                        hsn_sac_code=hsn_sac_code,
                        quantity = quantity,
                        current_stock = current_stock,
                        procurement_site = procurement_site,
                        procurement_ho = procurement_ho,
                        required_by = req['required_by'],
                        required_on=datetime.strptime(req['required_on'], "%Y-%m-%dT%H:%M:%S.%fZ"),
                        uom_id = unit_id,
                        remarks = req['remarks'],
                        created_by=updated_by,
                        owned_by=updated_by
                    )

                    #print('requisition_details',requisition_details)
                    #print('requisition_id', requisition_details.__dict__)
                    requisition_details.__dict__.pop('_state') if '_state' in requisition_details.__dict__.keys() else requisition_details.__dict__

                    # delete and create activity
                    existing_activities=PmsExecutionPurchasesRequisitionsMapWithActivities.objects.filter(
                        requisitions=requisition_details,is_deleted=False)
                    if existing_activities:
                        #print('existing_activities',existing_activities)
                        existing_activities.delete()

                    activity_details_list=list()
                    for a_l in activity_v_list:
                        #print('a_l',a_l)
                        activity_details = PmsExecutionPurchasesRequisitionsMapWithActivities.objects.create(
                            requisitions_id=requisition_details.__dict__['id'],
                            activity_id=a_l['activity'],
                            created_by=updated_by,owned_by=updated_by)
                        #print('activity_details',activity_details.__dict__)
                        activity_details.__dict__.pop('_state') if '_state' in activity_details.__dict__.keys() else activity_details.__dict__
                        activity_details_list.append(activity_details.__dict__)
                    #print('activity_list',activity_details_list)
                    #instance.__dict__['requisition_list']['activity_list'] = activity_details_list
                    requisition_details.__dict__['activity_details']= activity_details_list
                    requisition_details_list.append(requisition_details.__dict__)
                instance.__dict__['requisition_list'] = requisition_details_list
                #print('instance',instance.__dict__['requisition_list'])

                return instance
        except Exception as e:
            raise e

class PurchaseRequisitionsForAndroidEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    # requisition_list = serializers.DictField(required=False)
    activity_details = serializers.ListField(required=False)
    class Meta:
        model = PmsExecutionPurchasesRequisitions
        fields = ('id','requisitions_master','item','hsn_sac_code','quantity','procurement_site','procurement_ho','required_by','uom','current_stock',
                    'updated_by','required_on','remarks','activity_details')

    def update(self,instance, validated_data):
        try:
            activity_details = validated_data.pop('activity_details')if 'activity_details' in validated_data else ""
            updated_by = validated_data.get('updated_by')
            with transaction.atomic():
                req_masterID = PmsExecutionPurchasesRequisitions.objects.only('requisitions_master').get(id=instance.id).requisitions_master
                # print("req_masterID-->",req_masterID)
                requisition_details_list = []

                if 'uom' in validated_data.keys():
                    print("uom",validated_data['uom'])
                    unit_id = str(validated_data['uom'])
                else:
                    unit_id = ''
                current_stock = validated_data['current_stock'] if 'current_stock' in validated_data.keys() else 0.00
                instance.item=validated_data['item']
                instance.hsn_sac_code=validated_data['hsn_sac_code']
                instance.quantity = validated_data['quantity']
                instance.current_stock = current_stock
                instance.procurement_site = validated_data['procurement_site']
                instance.procurement_ho = validated_data['procurement_ho']
                instance.required_by = validated_data['required_by']
                instance.required_on=validated_data['required_on']
                # required_on=datetime.strptime(validated_data['required_on'],"%Y-%m-%dT%H:%M:%S.%fZ"),
                instance.uom_id = unit_id
                instance.remarks = validated_data['remarks']
                updated_by=updated_by
                instance.save()

                existing_activities=PmsExecutionPurchasesRequisitionsMapWithActivities.objects.filter(
                        requisitions=instance.id,is_deleted=False)
                if existing_activities:
                    #print('existing_activities',existing_activities)
                    existing_activities.delete()

                activity_details_list = []
                for ac_details in activity_details:
                    activity_details = PmsExecutionPurchasesRequisitionsMapWithActivities.objects.create(
                            requisitions_id=instance.id,
                            activity_id=ac_details['activity'],
                            created_by=updated_by,
                            owned_by=updated_by)
                    activity_details.__dict__.pop('_state') if '_state' in activity_details.__dict__.keys() else activity_details.__dict__
                    activity_details_list.append(activity_details.__dict__)

                instance.__dict__['requisitions_master'] = req_masterID
                
                instance.__dict__['activity_details'] = activity_details_list
                return instance.__dict__
        except Exception as e:
            raise e

class PurchaseRequisitionsDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsExecutionPurchasesRequisitions
        fields = ('id','is_deleted','updated_by','requisitions_master')

    def update(self, instance, validated_data):
        
        try:
            with transaction.atomic():
                req_masterID = PmsExecutionPurchasesRequisitions.objects.only('requisitions_master').get(id=instance.id)
                activity_details = PmsExecutionPurchasesRequisitionsMapWithActivities.objects.filter(
                    requisitions=instance,
                    is_deleted=False)
                for activity in activity_details:
                    print('activity_PRE_Status',activity.is_deleted)
                    activity.is_deleted = True
                    activity.updated_by =  validated_data.get('updated_by')
                    print('activity_POST_Status', activity.is_deleted)
                    activity.save()
                instance.updated_by = validated_data.get('updated_by')
                instance.is_deleted = True
                instance.save()
                instance.__dict__['requisitions_master'] = req_masterID
                return instance
        except Exception as e:
            raise e

class PurchaseRequisitionsForAndroidEditItemSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsExecutionPurchasesRequisitions
        fields = ('__all__')

#::::::::::  PMS EXECUTION PURCHASES QUOTATIONS PAYMENT TERMS MASTER  ;::::::::#
class ExecutionPurchaseQuotationsPaymentTermsMasterAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsExecutionPurchasesQuotationsPaymentTermsMaster
        fields = ('__all__')

class ExecutionPurchaseQuotationsPaymentTermsMasterEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsExecutionPurchasesQuotationsPaymentTermsMaster
        fields = ('id', 'name','updated_by')

class ExecutionPurchaseQuotationsPaymentTermsMasterDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsExecutionPurchasesQuotationsPaymentTermsMaster
        fields = ('id', 'is_deleted','updated_by')

    def update(self, instance, validated_data):
        try:
            with transaction.atomic():
                instance.is_deleted = True
                instance.save()
                return instance
        except Exception as e:
            raise APIException({'request_status': 0, 'msg': e})

#::::::::::  PMS EXECUTION PURCHASES QUOTATIONS ADD VIEW  ;::::::::#
class ExecutionPurchaseQuotationsAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())

    def create(self,validated_data):
        vdetails = {}
        try:
            with transaction.atomic():
                quotation_data,created = PmsExecutionPurchasesQuotations.objects.get_or_create(**validated_data)
                quotation_data.__dict__.pop('_state') if "_state" in quotation_data.__dict__.keys() else quotation_data.__dict__

            return quotation_data
        except Exception as e:
            raise e

    class Meta:
        model = PmsExecutionPurchasesQuotations
        fields = ('id','created_by', 'owned_by','requisitions_master','vendor','item','payment_terms','quantity',
                  'unit','price','delivery_date','document','document_name')

class ExecutionPurchaseQuotationsEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsExecutionPurchasesQuotations
        fields = ('id', 'vendor','payment_terms', 'quantity', 'unit', 'price','remarks',
                      'delivery_date', 'document_name', 'document', 'updated_by')

class ExecutionPurchaseQuotationsDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsExecutionPurchasesQuotations
        fields = ('id','is_deleted','updated_by')

    def update(self, instance, validated_data):
        try:
            with transaction.atomic():
                instance.is_deleted = True
                instance.save()
                return instance
        except Exception as e:
            raise APIException({'request_status': 0, 'msg': e})

class PurchaseQuotationsForApprovedListSerializer(serializers.ModelSerializer):

    class Meta:
        model = PmsExecutionPurchasesRequisitionsMaster
        fields = '__all__'


#####################################################################################


class PurchaseRequisitionsItemTypeListViewSerializer(serializers.ModelSerializer):
    updated_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    type = serializers.CharField(required=False)
    item_details = serializers.SerializerMethodField()
    class Meta:
        model = PmsExecutionPurchasesRequisitions
        fields = ('id','item_details','updated_by')

    def get_item_details(self,PmsExecutionPurchasesRequisitions):
        if PmsExecutionPurchasesRequisitions.type == 1:
            item_d=Materials.objects.filter(id=PmsExecutionPurchasesRequisitions.item).values('id','name')
        elif PmsExecutionPurchasesRequisitions.type == 2:
            item_d=PmsMachineries.objects.filter(id=PmsExecutionPurchasesRequisitions.item).values('id','equipment_name')

        return item_d[0]


#::::::::::  PMS EXECUTION PURCHASES REQUISITIONS TYPE MASTER ADD ;::::::::#
class ExecutionPurchasesRequisitionstypeMasterAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsExecutionPurchasesRequisitionsTypeMaster
        fields = ('__all__')

class ExecutionPurchasesRequisitionsTypesMasterEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsExecutionPurchasesRequisitionsTypeMaster
        fields = ('__all__')

class ExecutionPurchasesRequisitionsTypesMasterDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsExecutionPurchasesRequisitionsTypeMaster
        fields = ('id', 'is_deleted','updated_by')

    def update(self, instance, validated_data):
        try:
            with transaction.atomic():
                instance.is_deleted = True
                instance.save()
                return instance
        except Exception as e:
            raise e

#:::::::::: PMS EXECUTION PURCHASES REQUISITIONS TYPE TO ITEM CODE LIST :::::::::#
class PurchasesRequisitionsTypeToItemCodeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PmsExecutionPurchasesRequisitionsTypeMaster
        fields = ('__all__')

class ExecutionPurchaseQuotationsApprovedListSerializer(serializers.ModelSerializer):
    updated_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsExecutionPurchasesQuotations
        fields = ('__all__')

class PurchaseQuotationApprovedSerializer(serializers.ModelSerializer):

    class Meta:
        model = PmsExecutionPurchasesRequisitionsApproval
        fields = ('id','quotation_approved')
    def update(self,instance,validated_data):
        instance.quotation_approved=True
        instance.save()
        return instance



#::::::::::  PMS EXECUTION PURCHASES QUOTATIONS ADD VIEW  ;::::::::#
class ExecutionPurchaseQuotationsAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())

    def create(self,validated_data):
        vdetails = {}
        try:
            with transaction.atomic():
                remarks=validated_data.pop('remarks') if 'remarks' in validated_data else None
                quotation_data,created = PmsExecutionPurchasesQuotations.objects.get_or_create(**validated_data,remarks=remarks)
                quotation_data.__dict__.pop('_state') if "_state" in quotation_data.__dict__.keys() else quotation_data.__dict__

                return quotation_data
        except Exception as e:
            raise e

    class Meta:
        model = PmsExecutionPurchasesQuotations
        fields = ('id','created_by', 'owned_by','requisitions_master','vendor','item','payment_terms','quantity',
                  'unit','price','delivery_date','document','document_name','remarks')

class ExecutionPurchaseQuotationsListSerializer(serializers.ModelSerializer):
    updated_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    quotation_details= serializers.SerializerMethodField()

    def get_quotation_details(self,PmsExecutionPurchasesQuotations):
        quotation_vendor_payment_term_details={}
        vendor = PmsExternalUsers.objects.filter(id=str(PmsExecutionPurchasesQuotations.vendor)).values('id','code', 'organisation_name',
        'contact_no','email','address','trade_licence_doc','gst_no','pan_no','bank_ac_no',
        'adhar_no','adhar_doc','contact_person_name')
        payment_terms = PmsExecutionPurchasesQuotationsPaymentTermsMaster.objects.\
                filter(id=str(PmsExecutionPurchasesQuotations.payment_terms)).values('id','name')
        unit=TCoreUnit.objects.filter(id=str(PmsExecutionPurchasesQuotations.unit)).values('id','c_name')
        print('sdfdsf')
        quotation_vendor_payment_term_details={'vendor':vendor[0],
                                                'payment_terms':payment_terms[0],
                                                'unit':unit[0]}

class ExecutionPurchaseQuotationsItemListSerializer(serializers.ModelSerializer):

    class Meta:
        model = PmsExecutionPurchasesQuotations()
        fields = ('__all__')

class ExecutionPurchaseQuotationsItemTotalListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PmsExecutionPurchasesQuotations
        fields = ('__all__')

# class ExecutionPurchasesComparitiveStatementAddSerializer(serializers.ModelSerializer):
#     created_by = serializers.CharField(default=serializers.CurrentUserDefault())
#     owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
#     item_details = serializers.ListField(required=False)
#
#     class Meta:
#         model = PmsExecutionPurchasesComparitiveStatement
#         fields = ('id', 'requisitions_master', 'vendor', 'price_basis', 'make', 'base_price', 'packaging_and_forwarding',
#                   'freight_up_to_site', 'cgst', 'sgst', 'igst', 'payment_terms', 'delivery_time', 'total_order_value',
#                   'net_landed_cost', 'inco_terms', 'warranty_guarantee', 'created_by', 'owned_by', 'item_details')
#
#     def create(self, validated_data):
#         try:
#             with transaction.atomic():
#                 # print("validated ",validated_data)
#                 item_details = validated_data.pop('item_details') if 'item_details' in validated_data else ""
#                 print("item",validated_data.get('item'))
#                 for item in item_details:
#                     quotations_data = PmsExecutionPurchasesQuotations.objects.filter(requisitions_master=validated_data.get(
#                         'requisitions_master'),vendor=validated_data.get('vendor'),item=item['item'],is_deleted=False).update(
#                         discount=item['discount'],final_price=item['final_price'])
#                     print("quotations_data",quotations_data)
#
#                 comparitive_statement, created1 = PmsExecutionPurchasesComparitiveStatement.objects.get_or_create(**validated_data)
#                 comparitive_statement.__dict__.pop('_state') if '_state' in comparitive_statement.__dict__.keys() else comparitive_statement.__dict__
#                 return comparitive_statement
#
#         except Exception as e:
#             return APIException({'request_status': 0,
#                                  'error': e,
#                                  'msg': settings.MSG_ERROR})
#
#
# class ExecutionPurchasesComparitiveStatementOrdListViewSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = PmsExecutionPurchasesComparitiveStatement
#         fields = ('__all__')
class ExecutionPurchasesComparitiveStatementItemSumbmitApprovalSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    is_approved = serializers.BooleanField(default=False)

    class Meta:
        model = PmsExecutionPurchasesRequisitions
        fields = ('id', 'is_approved', 'updated_by')





class ExecutionPurchasesComparitiveStatementAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    vendor_name = serializers.SerializerMethodField(required=False)
    item_details = serializers.SerializerMethodField(required=False)

    class Meta:
        model = PmsExecutionPurchasesComparitiveStatement
        fields = ('id', 'requisitions_master', 'item', 'uom', 'discount', 'final_price', 'vendor', 'price_basis', 'make', 'base_price', 'packaging_and_forwarding',
                  'freight_up_to_site', 'cgst', 'sgst', 'igst', 'payment_terms', 'delivery_time', 'total_order_value',
                  'net_landed_cost', 'inco_terms', 'warranty_guarantee', 'is_approved', 'vendor_name', 'item_details', 'created_by', 'owned_by')

    def create(self, validated_data):
        try:
            # with transaction.atomic():
                # print("validated ",validated_data)
                # item_details = validated_data.pop('item_details') if 'item_details' in validated_data else ""
                # print("item",validated_data.get('item'))
                # for item in item_details:
                # quotations_data = PmsExecutionPurchasesQuotations.objects.filter(requisitions_master=validated_data.get(
                #     'requisitions_master'),vendor=validated_data.get('vendor'),item=validated_data.get('item'),
                #     is_deleted=False).update(discount=validated_data.get('discount'),final_price=validated_data.get('final_price'))
                # print("quotations_data",quotations_data)

            comparitive_statement, created1 = PmsExecutionPurchasesComparitiveStatement.objects.get_or_create(**validated_data)
            # comparitive_statement.__dict__.pop('_state') if '_state' in comparitive_statement.__dict__.keys() else comparitive_statement.__dict__
            return comparitive_statement

        except Exception as e:
            return APIException({'request_status': 0,
                                 'error': e,
                                 'msg': settings.MSG_ERROR})


    def get_vendor_name(self, PmsExecutionPurchasesComparitiveStatement):
        v_name = PmsExternalUsers.objects.only('contact_person_name').get(
            is_deleted=False,id=PmsExecutionPurchasesComparitiveStatement.vendor.id).contact_person_name
        if v_name:
            vendor_name = v_name
        else:
            vendor_name=""
        return vendor_name

    def get_item_details(self, PmsExecutionPurchasesComparitiveStatement):
        item_details_dict = {}
        req_type = PmsExecutionPurchasesRequisitionsMaster.objects.only('type').get(id=PmsExecutionPurchasesComparitiveStatement.
                                                                                    requisitions_master.id).type

        if req_type.__dict__['type_name'] == 'Materials':
            # uom = MaterialsUnitMapping.objects.only('unit').get(id=req_type.__dict__['id']).unit.c_name
            # print("uom",uom)
            materials_details = Materials.objects.get(id=PmsExecutionPurchasesComparitiveStatement.item)
            # print("materials_details",materials_details.__dict__['id'])
            item_details_dict['id'] = materials_details.__dict__['id']
            item_details_dict['name'] = materials_details.__dict__['name']
            item_details_dict['uom'] = PmsExecutionPurchasesComparitiveStatement.uom.c_name
            item_details_dict['mat_code'] = materials_details.__dict__['mat_code']
            # print("item_details",item_details)
            return item_details_dict
        elif req_type.__dict__['type_name'] == 'Machinery':
            machinery_details = PmsMachineries.objects.get(id=PmsExecutionPurchasesComparitiveStatement.item)
            # print("machinery_details", machinery_details.__dict__)
            item_details_dict['id'] = machinery_details.__dict__['id']
            item_details_dict['name'] = machinery_details.__dict__['equipment_name']
            item_details_dict['uom']=""
            item_details_dict['mat_code'] = machinery_details.__dict__['equipment_model_no']
            return item_details_dict


class ExecutionPurchasesComparitiveStatementEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsExecutionPurchasesComparitiveStatement
        fields = ('id',  'requisitions_master', 'item', 'uom', 'vendor', 'discount', 'final_price', 'price_basis', 'make',
                  'base_price', 'packaging_and_forwarding', 'freight_up_to_site', 'cgst', 'sgst', 'igst',
                  'payment_terms', 'delivery_time', 'total_order_value', 'net_landed_cost', 'inco_terms',
                  'warranty_guarantee', 'is_approved', 'updated_by')
class ExecutionPurchasesComparitiveStatementOrdListViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = PmsExecutionPurchasesComparitiveStatement
        fields = ('__all__')

class ExecutionPurchasesComparitiveStatementApprovalSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsExecutionPurchasesComparitiveStatement
        fields ='__all__'
    def update(self,instance,validated_data):      
        try:
            with transaction.atomic():
                section_name = self.context['request'].query_params.get('section_name', None)
                # print("mmmmmmmmmmmmmmmmm",type(validated_data.get('approval_permission_user_level')))
                permission_num = PmsApprovalPermissonLavelMatser.objects.get(section=TCoreOther.objects.get(cot_name=section_name)).permission_level
                permission_level_data=PmsApprovalPermissonMatser.objects.get(id=str(validated_data.get('approval_permission_user_level'))).permission_level
                permission_level=re.sub("\D", "",permission_level_data)
                
                
                if permission_num == int(permission_level):
                    comparative_approval = PmsExecutionPurchasesComparitiveStatement.objects.filter(id=instance.id,
                    requisitions_master=instance.requisitions_master,item=instance.item,uom=instance.uom,
                    is_approved=False,is_deleted=False).update(is_approved=True,
                    approval_permission_user_level=validated_data.get('approval_permission_user_level'))

                else:
                    comparative_approval = PmsExecutionPurchasesComparitiveStatement.objects.filter(id=instance.id,
                    requisitions_master=instance.requisitions_master,item=instance.item,uom=instance.uom,
                    is_approved=False,is_deleted=False).update(
                    approval_permission_user_level=str(validated_data.get('approval_permission_user_level')))

        
                comparative_approval_log=PmsExecutionPurchasesComparitiveStatementLog.objects.create(
                    **validated_data,is_approved=True)
                
                approval_items_data=PmsExecutionPurchasesRequisitionsApproval.objects.filter(requisitions_master=instance.requisitions_master,arm_approval__gt=False).\
                    values('item')
                approval_item=[x['item'] for x in approval_items_data ]

                completed_status_approval_validation = PmsExecutionPurchasesComparitiveStatement.objects.filter(requisitions_master=instance.requisitions_master,is_approved=True).count()
                print("completed_status_approval_validation",completed_status_approval_validation, type(completed_status_approval_validation))
                    # if completed_status_approval_validation:
                    #     count=count+1
                # print("count",count)
                print("len(approval_item)",len(approval_item))
                if len(approval_item) == completed_status_approval_validation:
                    final=PmsExecutionPurchasesRequisitionsMaster.objects.filter(id=str(instance.requisitions_master)).\
                        update(completed_status=1)
                    print("final",final)
                return comparative_approval_log
        except Exception as e:
            raise e

        # return validated_data

class ExecutionPurchasesComparitiveStatementDocumentAddSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    owned_by = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsExecutionPurchasesComparitiveStatementDocument
        fields = ('id', 'comparitive_statement', 'document_name', 'document', 'created_by', 'owned_by')

class ExecutionPurchasesComparitiveStatementApprovalListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PmsExecutionPurchasesComparitiveStatement
        fields = ('__all__')

# #:::::::::::::::::::::: PMS EXECUTION PURCHASES DELIVERY:::::::::::::::::::::::::::#
# class ExecutionPurchasesDeliveryAddSerializer(serializers.ModelSerializer):
#     created_by = serializers.CharField(default=serializers.CurrentUserDefault())
#     owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
#     document_details=serializers.SerializerMethodField()
#
#     def get_document_details(self, PmsExecutionPurchasesDelivery):
#         document = PmsExecutionPurchasesDeliveryDocument.objects.filter(delivery=PmsExecutionPurchasesDelivery.id,
#                                                                   is_deleted=False)
#         request = self.context.get('request')
#         response_list = []
#         for each_document in document:
#             file_url = request.build_absolute_uri(each_document.document.url)
#             owned_by = str(each_document.owned_by) if each_document.owned_by else ''
#             created_by = str(each_document.created_by) if each_document.created_by else ''
#             each_data = {
#                 "id": int(each_document.id),
#                 "delivery": int(each_document.delivery.id),
#                 "document_name": each_document.document_name,
#                 "document": file_url,
#                 "created_by": created_by,
#                 "owned_by": owned_by
#             }
#             response_list.append(each_data)
#         return response_list
#
#     class Meta:
#         model = PmsExecutionPurchasesDelivery
#         fields = ('id',  'requisitions_master', 'received_item', 'received_quantity', 'uom', 'date_of_delivery','vendor',
#                   'grn_no', 'e_way_bill_no', 'return_and_issue', 'return_cost', 'compensation', 'date_of_receipt',
#                   'created_by', 'owned_by','document_details')
# class ExecutionPurchasesDeliveryEditSerializer(serializers.ModelSerializer):
#     updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
#
#     class Meta:
#         model = PmsExecutionPurchasesDelivery
#         fields = (
#         'id', 'requisitions_master', 'received_item', 'received_quantity', 'uom', 'date_of_delivery', 'vendor',
#         'grn_no', 'e_way_bill_no', 'return_and_issue', 'return_cost', 'compensation', 'date_of_receipt',
#         'updated_by')
# class ExecutionPurchasesDeliveryDocumentAddSerializer(serializers.ModelSerializer):
#     created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
#     owned_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
#     class Meta:
#         model = PmsExecutionPurchasesDeliveryDocument
#         fields = ('id', 'delivery', 'document_name', 'document', 'created_by', 'owned_by')
# class ExecutionPurchasesDeliveryDocumentEditSerializer(serializers.ModelSerializer):
#     updated_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
#     class Meta:
#         model = PmsExecutionPurchasesDeliveryDocument
#         fields = ('id', 'document_name', 'updated_by')

#::::::::::::::::::::::::::::::::::::  PMS EXECUTION PURCHASES PO  ;::::::::::::::::::::::::::::::#
class ExecutionPurchasesPOListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PmsExecutionPurchasesComparitiveStatement
        fields = ('__all__')

class ExecutionPOTransportCostMasterAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsExecutionPurchasesPOTransportCostMaster
        fields = ('__all__')

class ExecutionPOTransportCostMasterEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsExecutionPurchasesPOTransportCostMaster
        fields = ('id','name','code','type_desc','updated_by')

class ExecutionPOTransportCostMasterDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsExecutionPurchasesPOTransportCostMaster
        fields = ('id', 'is_deleted','updated_by')

    def update(self, instance, validated_data):
        try:
            with transaction.atomic():
                instance.is_deleted = True
                instance.save()
                return instance
        except Exception as e:
            raise e

# class ExecutionPurchasesPOAddSerializer(serializers.ModelSerializer):
#     created_by = serializers.CharField(default=serializers.CurrentUserDefault())
#     owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
#     po_master= serializers.ListField(required=False)
#     poItemsMAP = serializers.ListField(required=False)
#     class Meta:
#         model = PmsExecutionPurchasesPO
#         fields = ('id','requisitions_master', 'po_master','created_by','owned_by','poItemsMAP')
#
#     def create(self, validated_data):
#         created_by = validated_data.get('created_by')
#         owned_by = validated_data.get('owned_by')
#
#         po_master = validated_data.pop('po_master') if 'po_master' in validated_data else ""
#         # pomapDict = {}
#         vendorList = []
#         vendorDict = {}
#         for poMasterDetails in po_master:
#             poItemsMAP = poMasterDetails['poItemsMAP']
#             re_details = PmsExecutionPurchasesPO.objects.create(
#                 requisitions_master=validated_data.get('requisitions_master'),
#                 vendor_id = poMasterDetails['vendor'],
#                 date_of_po= poMasterDetails['date_of_po'],
#                 # date_of_po=datetime.strptime(poMasterDetails['date_of_po'], "%Y-%m-%dT%H:%M:%S.%fZ"),
#                 po_no = poMasterDetails['po_no'],
#                 po_amount = poMasterDetails['po_amount'],
#                 transport_cost_type_id = poMasterDetails['transport_cost_type'],
#                 transport_cost = poMasterDetails['transport_cost'],
#                 created_by=created_by,
#                 owned_by=owned_by
#             )
#             pomapList = []
#             for po_map in poItemsMAP:
#                 # print('uom_id-->', po_map['uom_id'])
#                 uom_id = po_map['uom_id'] if 'uom_id' in po_map else ""
#                 poItemsMAPDetails = PmsExecutionPurchasesPOItemsMAP.objects.create(
#                     purchase_order=re_details,
#                     item=po_map['item'],
#                     quantity=po_map['quantity'],
#                     uom_id=uom_id,
#                     created_by=created_by,
#                     owned_by=owned_by
#                 )
#
#                 poItemsMAPDetails.__dict__.pop('_state') if "_state" in poItemsMAPDetails.__dict__.keys() else poItemsMAPDetails.__dict__
#                 # print("poItemsMAPDetails-->", poItemsMAPDetails.__dict__)
#                 pomapList.append(poItemsMAPDetails.__dict__)
#                 # print("pomapList --> ", pomapList)
#             re_details.__dict__['poItemsMAP'] = pomapList
#             re_details.__dict__.pop('_state') if "_state" in re_details.__dict__.keys() else re_details.__dict__
#
#             vendorList.append(re_details.__dict__)
#         vendorDict['requisitions_master'] = validated_data.get('requisitions_master')
#         vendorDict['po_master'] = vendorList
#             # print("re_details --> ",re_details.__dict__)
#             # re_details.__dict__.append(pomapDict)
#         # vendorDict['po_master'] = vendorList
#             # print("pomapDict----> ",pomapDict)
#             # pomapDict.pop('_state') if "_state" in pomapDict.keys() else pomapDict
#
#             # print("pomapDict----> ", pomapDict)
#
#
#         # print("validated_data", validated_data)
#
#         return vendorDict
class ExecutionPurchasesPOAddSerializer(serializers.ModelSerializer):
    '''
    AUTHOR:Abhisek Singh,

    DESCRIPTION: Here the PO is added and generating a status as "Processing" and 
    "PO_Completed" which is updated at status field and completed_status field respectevly

    Validation: Here a validation is implemented from front-end where they check approved_quantity 
    is == 0 if do so then request must be send with "completed_status=2" 

    '''
                 

    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    # completed_status = serializers.CharField(required=False)
    po_master= serializers.ListField(required=False)
    poItemsMAP = serializers.ListField(required=False)
    class Meta:
        model = PmsExecutionPurchasesPO
        fields = ('id','requisitions_master','po_master','created_by','owned_by','poItemsMAP')

    def create(self, validated_data):
        from decimal import Decimal
        created_by = validated_data.get('created_by')
        owned_by = validated_data.get('owned_by')
        requisitions_master_id = validated_data.get('requisitions_master')
        # completed_status = validated_data.pop('completed_status') if 'completed_status' in validated_data else ''
        po_master = validated_data.pop('po_master') if 'po_master' in validated_data else ""
        pomapDict = {}
        vendorList = []
        vendorDict = {}
        with transaction.atomic():
            # status = PmsExecutionPurchasesRequisitionsMaster.objects.filter(id=str(requisitions_master_id),status=9).update(status=3)
            status = PmsExecutionPurchasesRequisitionsMaster.objects.filter(id=str(requisitions_master_id),status=4).update(status=5)
            print("status",status)
            for poMasterDetails in po_master:
                poItemsMAP = poMasterDetails['poItemsMAP']
                if 'transport_cost' in poMasterDetails.keys():
                    re_details = PmsExecutionPurchasesPO.objects.create(
                        requisitions_master=validated_data.get('requisitions_master'),
                        vendor_id = poMasterDetails['vendor'],
                        date_of_po = datetime.strptime(poMasterDetails['date_of_po'], "%Y-%m-%dT%H:%M:%S.%fZ"),
                        po_no = poMasterDetails['po_no'],
                        po_amount = poMasterDetails['po_amount'],
                        transport_cost_type_id = poMasterDetails['transport_cost_type'],
                        transport_cost = poMasterDetails['transport_cost'],
                        created_by=created_by,
                        owned_by=owned_by
                    )
                    print("re_details",re_details)
                    transport_cost = PmsExecutionPurchasesTotalTransportCostPayable.objects.filter(is_deleted=False,
                                                                                            requisitions_master=requisitions_master_id)
                    if transport_cost:
                        # print("poMasterDetails['transport_cost']",type(poMasterDetails['transport_cost']))
                        # print("poMasterDetails['transport_cost']",poMasterDetails['transport_cost'])
                        last_transport_cost = transport_cost[0].__dict__['total_transport_cost']
                        last_transport_cost = last_transport_cost + int(poMasterDetails['transport_cost']) if poMasterDetails['transport_cost'] else 0
                        # print("last_transport_cost",last_transport_cost)
                        transport_cost_add = PmsExecutionPurchasesTotalTransportCostPayable.objects.filter(is_deleted=False,
                        requisitions_master=requisitions_master_id
                        ).update(total_transport_cost=last_transport_cost)

                    else:
                        transport_cost_add = PmsExecutionPurchasesTotalTransportCostPayable.objects.create(
                            requisitions_master=validated_data.get('requisitions_master'),
                            total_transport_cost=poMasterDetails['transport_cost'],
                            created_by=created_by,
                            owned_by=owned_by
                        )

                else:
                    re_details = PmsExecutionPurchasesPO.objects.create(
                        requisitions_master=validated_data.get('requisitions_master'),
                        vendor_id = poMasterDetails['vendor'],
                        date_of_po = datetime.strptime(poMasterDetails['date_of_po'], "%Y-%m-%dT%H:%M:%S.%fZ"),
                        po_no = poMasterDetails['po_no'],
                        po_amount = poMasterDetails['po_amount'],
                        transport_cost_type_id = poMasterDetails['transport_cost_type'],
                        created_by=created_by,
                        owned_by=owned_by
                    )
                pomapList = []
                print("re_details", re_details)
                for po_map in poItemsMAP:
                    uom_id = po_map['uom'] if 'uom' in po_map else ""
                    print("uom_id-->",uom_id)
                    poItemsMAPDetails = PmsExecutionPurchasesPOItemsMAP.objects.create(
                        purchase_order=re_details,
                        item=po_map['item'],
                        quantity=po_map['quantity'],
                        uom_id=uom_id,
                        created_by=created_by,
                        owned_by=owned_by
                    )
                    print("poItemsMAPDetails",poItemsMAPDetails.__dict__)
                    available_quantity = PmsExecutionPurchasesRequisitionsApproval.objects.only('available_quantity').get(
                        requisitions_master=requisitions_master_id.id,item=po_map['item'],uom=uom_id).available_quantity
                    print("available_quantity",available_quantity)
                    if int(po_map['quantity'])<=available_quantity:
                        print("if po_map['quantity']<=available_quantity:")
                        avl_qun = available_quantity - int(po_map['quantity'])
                        print("avl_qun",avl_qun)
                        latest_quantity = PmsExecutionPurchasesRequisitionsApproval.objects.filter(
                        requisitions_master=requisitions_master_id,item=po_map['item'],uom=uom_id).update(available_quantity=avl_qun)
                        print("latest_quantity",latest_quantity)

                    poItemsMAPDetails.__dict__.pop('_state') if "_state" in poItemsMAPDetails.__dict__.keys() else poItemsMAPDetails.__dict__
                    pomapList.append(poItemsMAPDetails.__dict__)
                re_details.__dict__['poItemsMAP'] = pomapList
                re_details.__dict__.pop('_state') if "_state" in re_details.__dict__.keys() else re_details.__dict__

                vendorList.append(re_details.__dict__)

            # if int(completed_status) == 2:
            #     status_update = PmsExecutionPurchasesRequisitionsMaster.objects.filter(id=str(requisitions_master_id)).update(
            #         completed_status=2)
            # else:
            approval_data = PmsExecutionPurchasesRequisitionsApproval.objects.filter(is_deleted=False,requisitions_master=requisitions_master_id).values_list('available_quantity')
            flag = 0
            for data in approval_data:
                if data[0] != Decimal('0.0'):
                    flag = 0
                    break
                else:
                    flag = 1

            if flag == 1:
                status_update = PmsExecutionPurchasesRequisitionsMaster.objects.filter(id=str(requisitions_master_id)).update(completed_status=2)

        vendorDict['requisitions_master'] = validated_data.get('requisitions_master')
        # vendorDict['completed_status'] = completed_status
        vendorDict['po_master'] = vendorList
        return vendorDict


class ExecutionPurchasesPOTotalListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PmsExecutionPurchasesPO
        fields = ('__all__')

# class ExecutionPurchasesPOQuantityCalSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = PmsExecutionPurchasesPO
#         fields = ('__all__')

class ExecutionPurchasesPODocumentAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsExecutionPurchasesPODocument
        fields = ('__all__')


class ExecutionPurchasesPODocumentEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsExecutionPurchasesPODocument
        fields = ('id','document_name','document','updated_by')


class ExecutionPurchasesPODocumentDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsExecutionPurchasesPODocument
        fields = ('id', 'is_deleted','updated_by')

    def update(self, instance, validated_data):
        try:
            with transaction.atomic():
                instance.is_deleted = True
                instance.save()
                return instance
        except Exception as e:
            raise e


class PurchaseRequisitionsApprovalSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    item_approval_details = serializers.ListField(required=False)

    def create(self, validated_data):

        try:
            with transaction.atomic():
                created_by = validated_data.get('created_by')
                owned_by = validated_data.get('owned_by')
                item_approval_details = validated_data.pop(
                    'item_approval_details') if 'item_approval_details' in validated_data else ""

                from django.db.models import Sum
                req_master_details = PmsExecutionPurchasesRequisitionsMaster.objects. \
                    filter(project=validated_data.get('project'), site_location=validated_data.get('site_location'),
                           status=8, type=validated_data.get('type')).order_by('-id')
                #UPDATE THE PERMISSION 
                existing_data = PmsExecutionPurchasesRequisitionsApproval.objects.\
                    filter(requisitions_master=validated_data.get('requisitions_master'))
                if existing_data:
                    # print('existing_data',existing_data)
                    approval_list = []
                    for item_approval in item_approval_details:
                        reqsition_update_approvals = PmsExecutionPurchasesRequisitionsApproval.objects.\
                            filter(requisitions_master=validated_data.get('requisitions_master'),type=validated_data.get('type'),
                            item=item_approval['item'],uom=item_approval['uom']).\
                                update(approval_permission_user_level=int(item_approval['permission_level']),
                                arm_approval=item_approval['arm_approval'])

                        reqsition_approvals_log_entry = PmsExecutionPurchasesRequisitionsApprovalLogTable.objects.create(
                            requisitions_master_id=str(validated_data.get('requisitions_master')),
                            project_id=str(validated_data.get('project')),
                            site_location_id=str(validated_data.get('site_location')),
                            item=item_approval['item'],
                            type_id=str(validated_data.get('type')),
                            uom_id = item_approval['uom'],
                            # initial_estimate=item_approval['initial_estimate'],
                            # as_per_drawing=item_approval['as_per_drawing'],
                            arm_approval= item_approval['arm_approval'],
                            approval_permission_user_level_id=int(item_approval['permission_level']),
                            approved_quantity=item_approval['approved_quantity'],
                            available_quantity=item_approval['approved_quantity'],
                            created_by=created_by,
                            owned_by=owned_by
                            )    
                        query_list = []
                        totals = 0
                        c = 0
                        last_3_avg = 0
                        for req_master in req_master_details:
                            qr_details = PmsExecutionPurchasesRequisitions.objects. \
                                filter(requisitions_master=req_master.id, item=item_approval['item']). \
                                aggregate(Sum('quantity'))['quantity__sum']
                            if qr_details is not None:
                                totals = totals + qr_details
                                if c < 3:
                                    last_3_avg = last_3_avg + qr_details
                                    c = c + 1
                        reqsition_approvals_log_entry.__dict__.pop(
                            '_state') if "_state" in reqsition_approvals_log_entry.__dict__.keys() else reqsition_approvals_log_entry.__dict__
                        approval_list.append(reqsition_approvals_log_entry.__dict__)
                        latest = PmsExecutionPurchasesRequisitions.objects. \
                            filter(requisitions_master=validated_data.get('requisitions_master'),
                                item=item_approval['item']).aggregate(Sum('quantity'))['quantity__sum']
                        reqsition_approvals_log_entry.__dict__['item_details'] = {'total_quantity': totals,
                                                                        'item': str(item_approval['item']),
                                                                        'last_3_avg': last_3_avg,
                                                                        'latest_quantity': latest}

                        validated_data['item_approval_details'] = approval_list 
                        id = validated_data.get('requisitions_master')
                        requisitions_master_id = str(id.__dict__['id'])
                        section_name = self.context['request'].query_params.get('section_name', None)
                        others_checking=TCoreOther.objects.only('id').get(cot_name=section_name,cot_is_deleted=False).id
                        approval_section=PmsApprovalPermissonLavelMatser.objects.only('permission_level').get(section=others_checking).permission_level
                        permission_level=PmsApprovalPermissonMatser.objects.only('permission_level').\
                            get(id=reqsition_approvals_log_entry.approval_permission_user_level_id,section=others_checking,is_deleted=False).permission_level
                        # print("permission_level",permission_level)
                        permission_level=re.sub("\D", "",permission_level)
                        # print("permission_level:::::::::::::::::",type(permission_level))
                        requisitions_m_status = PmsExecutionPurchasesRequisitionsMaster.objects.only('status').get(
                            is_deleted=False, id=requisitions_master_id).status
                        # print("requisitions_m_status", requisitions_m_status)
                        if int(requisitions_m_status) < 2 and int(permission_level) == int(approval_section):
                            if PmsExecutionPurchasesRequisitionsApproval.objects.filter(requisitions_master=requisitions_master_id,arm_approval__gt=0):
                                # print("requisitions_m_status == None")
                                update_status = PmsExecutionPurchasesRequisitionsMaster.objects.filter(is_deleted=False,id=requisitions_master_id).update(status=2)               
                        


                else: 
                # print(req_master_details)
                    approval_list = []
                    for item_approval in item_approval_details:
                        reqsition_approvals = PmsExecutionPurchasesRequisitionsApproval.objects.create(
                            requisitions_master_id=str(validated_data.get('requisitions_master')),
                            project_id=str(validated_data.get('project')),
                            site_location_id=str(validated_data.get('site_location')),
                            item=item_approval['item'],
                            # justification=item_approval['justification'],
                            type_id=str(validated_data.get('type')),
                            initial_estimate=item_approval['initial_estimate'],
                            as_per_drawing=item_approval['as_per_drawing'],
                            # modified by Rupam
                            #current_stock=item_approval['current_stock'], 
                            uom_id = item_approval['uom'],
                            arm_approval= item_approval['arm_approval'],
                            approval_permission_user_level_id=int(item_approval['permission_level']),
                            approved_quantity=item_approval['approved_quantity'],
                            available_quantity=item_approval['approved_quantity'],
                            created_by=created_by,
                            owned_by=owned_by
                        )
                        reqsition_approvals_log_entry = PmsExecutionPurchasesRequisitionsApprovalLogTable.objects.create(
                            requisitions_master_id=str(validated_data.get('requisitions_master')),
                            project_id=str(validated_data.get('project')),
                            site_location_id=str(validated_data.get('site_location')),
                            item=item_approval['item'],
                            type_id=str(validated_data.get('type')),
                            uom_id = item_approval['uom'],
                            arm_approval= item_approval['arm_approval'],
                            approval_permission_user_level_id=int(item_approval['permission_level']),
                            approved_quantity=item_approval['approved_quantity'],
                            available_quantity=item_approval['approved_quantity'],
                            created_by=created_by,
                            owned_by=owned_by
                        )                    

                        query_list = []
                        totals = 0
                        c = 0
                        last_3_avg = 0
                        for req_master in req_master_details:
                            qr_details = PmsExecutionPurchasesRequisitions.objects. \
                                filter(requisitions_master=req_master.id, item=item_approval['item']). \
                                aggregate(Sum('quantity'))['quantity__sum']
                            if qr_details is not None:
                                totals = totals + qr_details
                                if c < 3:
                                    last_3_avg = last_3_avg + qr_details
                                    c = c + 1
                        reqsition_approvals.__dict__.pop(
                            '_state') if "_state" in reqsition_approvals.__dict__.keys() else reqsition_approvals.__dict__
                        approval_list.append(reqsition_approvals.__dict__)
                        latest = PmsExecutionPurchasesRequisitions.objects. \
                            filter(requisitions_master=validated_data.get('requisitions_master'),
                                item=item_approval['item']).aggregate(Sum('quantity'))['quantity__sum']
                        reqsition_approvals.__dict__['item_details'] = {'total_quantity': totals,
                                                                        'item': str(item_approval['item']),
                                                                        'last_3_avg': last_3_avg,
                                                                        'latest_quantity': latest}

                        validated_data['item_approval_details'] = approval_list
                        id = validated_data.get('requisitions_master')
                        requisitions_master_id = str(id.__dict__['id'])
                        section_name = self.context['request'].query_params.get('section_name', None)
                        #print("section_name",section_name)
                        others_checking=TCoreOther.objects.only('id').get(cot_name=section_name,cot_is_deleted=False).id
                        #print("others_checking",validated_data.get('item_approval_details'))
                        approval_section=PmsApprovalPermissonLavelMatser.objects.only('permission_level').get(section=others_checking).permission_level
                        #print("approval_section",type(approval_section))
                        permission_level=PmsApprovalPermissonMatser.objects.only('permission_level').\
                            get(id=reqsition_approvals_log_entry.approval_permission_user_level_id,section=others_checking,is_deleted=False).permission_level
                        # print("permission_level",permission_level)
                        permission_level=re.sub("\D", "",permission_level)
                        # print("permission_level:::::::::::::::::",type(permission_level))
                        requisitions_m_status = PmsExecutionPurchasesRequisitionsMaster.objects.only('status').get(
                            is_deleted=False, id=requisitions_master_id).status
                        # print("requisitions_m_status", requisitions_m_status)
                        if int(requisitions_m_status) < 2 and int(permission_level) == int(approval_section):
                            if PmsExecutionPurchasesRequisitionsApproval.objects.filter(arm_approval__gt=0,requisitions_master=requisitions_master_id):
                                # print("requisitions_m_status == None")
                                update_status = PmsExecutionPurchasesRequisitionsMaster.objects.filter(is_deleted=False,id=requisitions_master_id).update(status=2)               
                    
                return validated_data
        except Exception as e:
            raise e

    class Meta:
        model = PmsExecutionPurchasesRequisitionsApproval
        fields = (
        'id', 'created_by', 'owned_by', 'item_approval_details', 'project', 'site_location', 'type',
        'requisitions_master')


# class PurchaseRequisitionsApprovalListSerializer(serializers.ModelSerializer):
class PurchaseRequisitionsApprovalListSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    actual_consumption_approval = serializers.SerializerMethodField()
    permission_details = serializers.SerializerMethodField()
    current_stock = serializers.SerializerMethodField()
    class Meta:
        model = PmsExecutionPurchasesRequisitionsApproval
        fields = ('__all__')
    def get_current_stock(self, PmsExecutionPurchasesRequisitionsApproval):
        #print('self',self.context.get('view').kwargs.get('requisition_id'))
        #requisition_id = self.context.get('view').kwargs.get('requisition_id')
        project_id = self.context.get('view').kwargs.get('project_id')
        site_id = self.context.get('view').kwargs.get('site_id')
        stock_details = PmsExecutionUpdatedStock.objects.filter(
            project=project_id,
            site_location=site_id,
            item=PmsExecutionPurchasesRequisitionsApproval.item,
            type=PmsExecutionPurchasesRequisitionsApproval.type,
            uom=PmsExecutionPurchasesRequisitionsApproval.uom
        )
        #print('stock_details',stock_details)
        #current_stock = 0.0
        if stock_details:
            for e_stock_details in stock_details:
                if e_stock_details.issued_stock:
                    t_issued_stock = float(e_stock_details.issued_stock)
                else:
                    t_issued_stock = 0.0

                if e_stock_details.opening_stock:
                    t_opening_stock = float(e_stock_details.opening_stock)
                else:
                    t_opening_stock = 0.0

                if e_stock_details.recieved_stock:
                    t_recieved_stock = float(e_stock_details.recieved_stock)
                else:
                    t_recieved_stock = 0.0
                current_stock = (t_opening_stock + t_recieved_stock) - t_issued_stock
                #print('current_stock',current_stock)

        else:
            current_stock = 0.00
        return current_stock

    def get_actual_consumption_approval(self, PmsExecutionPurchasesRequisitionsApproval):
        try:
            with transaction.atomic():
                from django.db.models import Sum
                print(PmsExecutionPurchasesRequisitionsApproval)
                item_d = Materials.objects.filter(id=PmsExecutionPurchasesRequisitionsApproval.item).values('id',
                                                                                                            'name')
                # unit_d = PmsExecutionPurchasesRequisitions.objects. \
                #              filter(requisitions_master=PmsExecutionPurchasesRequisitionsApproval.requisitions_master,
                #                     item=PmsExecutionPurchasesRequisitionsApproval.uom).values('uom')[:1]
                
                #u = [x['uom'] for x in unit_d]
                unit_details = TCoreUnit.objects.filter(pk=PmsExecutionPurchasesRequisitionsApproval.uom.id).values('id', 'c_name')
                print("unit_details:::::",unit_details)
                if unit_details:
                    req_master_details = PmsExecutionPurchasesRequisitionsMaster.objects. \
                        filter(project=PmsExecutionPurchasesRequisitionsApproval.project,
                            site_location=PmsExecutionPurchasesRequisitionsApproval.site_location,
                            status=5, type=PmsExecutionPurchasesRequisitionsApproval.type).order_by('-id')
                    approval_list = []
                    query_list = []
                    totals = 0
                    c = 0
                    last_3_avg = 0
                    
                    for req_master in req_master_details:
                        if req_master:
                            qr_details = PmsExecutionPurchasesRequisitions.objects. \
                                filter(requisitions_master=req_master.id, item=PmsExecutionPurchasesRequisitionsApproval.item). \
                                aggregate(Sum('quantity'))['quantity__sum']
                            if qr_details is not None:
                                totals = totals + qr_details
                                if c < 3:
                                    last_3_avg = last_3_avg + qr_details
                                    c = c + 1
                    latest = PmsExecutionPurchasesRequisitions.objects. \
                        filter(requisitions_master=PmsExecutionPurchasesRequisitionsApproval.requisitions_master,
                            item=PmsExecutionPurchasesRequisitionsApproval.item). \
                        aggregate(Sum('quantity'))['quantity__sum']
                    remarks_details = PmsExecutionPurchasesRequisitions.objects. \
                        filter(requisitions_master=PmsExecutionPurchasesRequisitionsApproval.requisitions_master,
                            item=PmsExecutionPurchasesRequisitionsApproval.item).values("remarks").distinct()
                    print("remarks_details:::::::", remarks_details)
                    actual_consumption = {}
                    actual_consumption = {'total_previous_requisition': totals,
                                        'avg_of_last_three_requsition': last_3_avg,
                                        'new_requsition': latest,
                                        'item_name': [x for x in item_d][0]['name'],
                                        'unit_name': [x for x in unit_details][0]['c_name'],
                                        'remarks': [x for x in remarks_details][0]['remarks']

                                        }

                    return actual_consumption
                else:
                    req_master_details = PmsExecutionPurchasesRequisitionsMaster.objects. \
                        filter(project=PmsExecutionPurchasesRequisitionsApproval.project,
                            site_location=PmsExecutionPurchasesRequisitionsApproval.site_location,
                            status=8, type=PmsExecutionPurchasesRequisitionsApproval.type).order_by('-id')
                    approval_list = []
                    query_list = []
                    totals = 0
                    c = 0
                    last_3_avg = 0
                    
                    for req_master in req_master_details:
                        if req_master:
                            qr_details = PmsExecutionPurchasesRequisitions.objects. \
                                filter(requisitions_master=req_master.id, item=PmsExecutionPurchasesRequisitionsApproval.item). \
                                aggregate(Sum('quantity'))['quantity__sum']
                            if qr_details is not None:
                                totals = totals + qr_details
                                if c < 3:
                                    last_3_avg = last_3_avg + qr_details
                                    c = c + 1
                    latest = PmsExecutionPurchasesRequisitions.objects. \
                        filter(requisitions_master=PmsExecutionPurchasesRequisitionsApproval.requisitions_master,
                            item=PmsExecutionPurchasesRequisitionsApproval.item). \
                        aggregate(Sum('quantity'))['quantity__sum']
                    remarks_details = PmsExecutionPurchasesRequisitions.objects. \
                        filter(requisitions_master=PmsExecutionPurchasesRequisitionsApproval.requisitions_master,
                            item=PmsExecutionPurchasesRequisitionsApproval.item).values("remarks").distinct()
                    print("remarks_details:::::::", remarks_details)
                    actual_consumption = {}
                    actual_consumption = {'total_previous_requisition': totals,
                                        'avg_of_last_three_requsition': last_3_avg,
                                        'new_requsition': latest,
                                        'item_name': [x for x in item_d][0]['name'],
                                        'unit_name': None,
                                        'remarks': [x for x in remarks_details][0]['remarks']

                                        }

                    return actual_consumption
    
        except Exception as e:
            raise e
    def get_permission_details(self, PmsExecutionPurchasesRequisitionsApproval):

        #level of approvals list 
        permission_details=[]
        section_details=TCoreOther.objects.get(cot_name__iexact='requisition')
        approval_master_details = PmsApprovalPermissonMatser.objects.filter(section=section_details.id)
        print("approval_master_details",approval_master_details)
        log_details=PmsExecutionPurchasesRequisitionsApprovalLogTable.objects.\
                filter(requisitions_master=PmsExecutionPurchasesRequisitionsApproval.requisitions_master,
                type=PmsExecutionPurchasesRequisitionsApproval.type,
                uom=PmsExecutionPurchasesRequisitionsApproval.uom,item=PmsExecutionPurchasesRequisitionsApproval.item).\
                    values('id','arm_approval','approval_permission_user_level','approved_quantity')
        # print(log_details) 
        amd_list=[]
        l_d_list=[]
        for l_d in log_details:
            l_d_list.append(l_d['approval_permission_user_level'])

        for a_m_d in approval_master_details:
            if l_d_list:
                    if a_m_d.id in l_d_list:
                        l_d=log_details.get(approval_permission_user_level=a_m_d.id)
                        f_name = a_m_d.approval_user.first_name if a_m_d.approval_user else '' 
                        l_name = a_m_d.approval_user.last_name if a_m_d.approval_user else '' 
                        var=a_m_d.permission_level
                        res = re.sub("\D", "", var)
                        permission_dict={
                                "user_level":a_m_d.permission_level,
                                "approval":l_d['arm_approval'],
                                "permission_num":int(res),
                                "approved_quantity":l_d['approved_quantity'],
                                "user_details":{
                                    "id":a_m_d.approval_user.id if a_m_d.approval_user else None,
                                    "email":a_m_d.approval_user.email if a_m_d.approval_user else None,
                                    "name":  f_name +' '+l_name,
                                    "username":a_m_d.approval_user.username
                                    }
                            }
                                

                    else:
                        var=a_m_d.permission_level
                        res = re.sub("\D", "", var)
                        permission_dict={
                            "user_level":a_m_d.permission_level,
                            "permission_num":int(res),
                            "approval":None,
                        }


                    permission_details.append(permission_dict)
        return permission_details



class PurchaseRequisitionsApprovalTotalListSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    status=serializers.CharField(required=False)
    class Meta:
        model = PmsExecutionPurchasesRequisitions
        fields = ('__all__')
        extra_fields=('status')

#:::::::::::::::::::::: PMS EXECUTION PURCHASES DISPATCH:::::::::::::::::::::::::::#
class ExecutionPurchasesDispatchAddSerializer(serializers.ModelSerializer):
    '''
    AUTHOR:Abhisek Singh,
    DESCRIPTION: Here Dispatch is made against PO and generating a status "Dispatch_Completed"
    which is further updated in field "completed_status" of requisition master table 
    '''
                    
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    # document_details=serializers.SerializerMethodField()
    # completed_status = serializers.CharField(required=False)


    class Meta:
        model = PmsExecutionPurchasesDispatch
        fields = ('id', 'requisitions_master', 'dispatch_item', 'quantity', 'uom', 'vendor', 'po_no',
                  'date_of_dispatch', 'dispatch_cost', 'created_by', 'owned_by')


    def create(self, validated_data):
        requisitions_master_id = validated_data.get('requisitions_master')
        print("validated_data",validated_data)
        # completed_status = validated_data.pop('completed_status') if 'completed_status' in validated_data else ''
        # print("completed_status",type(completed_status))
        with transaction.atomic():
            dispatch_add,created = PmsExecutionPurchasesDispatch.objects.get_or_create(**validated_data)
            # print("dispatch_add",dispatch_add)
            # print("created",created)

            requisitions_m_status = PmsExecutionPurchasesRequisitionsMaster.objects.get(
                            is_deleted=False,
                            id=str(requisitions_master_id)).status
            if requisitions_m_status <6:
                        print("requisitions_m_status == None")
                        update_status = PmsExecutionPurchasesRequisitionsMaster.objects.filter(is_deleted=False,
                                                                                                id=str(requisitions_master_id)
                                                                                                ).update(status=6)

            # #["THIS PORTION IS DEGREDED AS ITS NOT REQUIRED AS PER FUTURE PROSPECTIVE"]

            # if int(completed_status) == 2:
            #     status_update = PmsExecutionPurchasesRequisitionsMaster.objects.filter(id=str(requisitions_master_id)).update(
            #         completed_status=2)
            #     print("status_update",status_update)
            # else: 

            com_stat = PmsExecutionPurchasesRequisitionsMaster.objects.get(id=str(requisitions_master_id))
            # print("com_stat",com_stat)
            if com_stat:
                item_list = []
                item_len = 0
                po_details = PmsExecutionPurchasesPO.objects.filter(requisitions_master=requisitions_master_id).values("id")
                # print("po_details",po_details)
                for i in po_details:
                    po_item = PmsExecutionPurchasesPOItemsMAP.objects.filter(purchase_order=i['id'],is_deleted=False).values("id")
                    # print("item",len(po_item))
                    item_len = item_len+len(po_item)
                    # print("item_len",item_len)
                dispatch_list = PmsExecutionPurchasesDispatch.objects.filter(requisitions_master=requisitions_master_id).values("id")
                # print("dispatch_list",len(dispatch_list))
                completed_status = PmsExecutionPurchasesRequisitionsMaster.objects.get(
                    is_deleted=False,
                    id=str(requisitions_master_id)).completed_status

                if len(dispatch_list) == item_len and completed_status==2:
                    status_update = PmsExecutionPurchasesRequisitionsMaster.objects.filter(id=str(requisitions_master_id)).update(completed_status=3)
                else:
                    status_update=0


            # validated_data['completed_status']=status_update
            validated_data['id']=dispatch_add.id
            return validated_data
class ExecutionPurchasesDispatchEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsExecutionPurchasesDispatch
        fields = ('id', 'requisitions_master', 'dispatch_item', 'quantity', 'uom', 'date_of_dispatch', 'dispatch_cost', 'updated_by')
class ExecutionPurchasesDispatchDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsExecutionPurchasesDispatch
        fields = ('id','is_deleted','updated_by')
    def update(self, instance, validated_data):
        try:
            with transaction.atomic():
                instance.is_deleted=True
                instance.updated_by=validated_data.get('updated_by')
                instance.save()

                dispatch_document=PmsExecutionPurchasesDispatchDocument.objects.filter(dispatch=instance,
                                                                                       is_deleted=False).update(is_deleted=True)
                # print("dispatch_document",dispatch_document)
                return instance

        except Exception as e:
            raise e
class ExecutionPurchasesDispatchListSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    document_details = serializers.SerializerMethodField(required=False)
    item_details = serializers.SerializerMethodField(required=False)
    vendor_name = serializers.SerializerMethodField(required=False)
    is_delivered = serializers.SerializerMethodField(required=False)

    class Meta:
        model = PmsExecutionPurchasesDispatch
        fields = ('id', 'requisitions_master', 'dispatch_item', 'quantity', 'uom', 'vendor', 'po_no', 'date_of_dispatch',
                  'dispatch_cost', 'created_by', 'owned_by', 'item_details', 'vendor_name', 'document_details', 'is_delivered')

    def get_is_delivered(self, PmsExecutionPurchasesDispatch):
        delivery = PmsExecutionPurchasesDelivery.objects.filter(is_deleted=False,requisitions_master=PmsExecutionPurchasesDispatch.requisitions_master.id,
        received_item=PmsExecutionPurchasesDispatch.dispatch_item,uom=PmsExecutionPurchasesDispatch.uom.id,po_no=PmsExecutionPurchasesDispatch.po_no,
        vendor=PmsExecutionPurchasesDispatch.vendor.id).values()
        if delivery:
            return True
        else:
            return False       

    def get_item_details(self, PmsExecutionPurchasesDispatch):
        item_details_dict = {}
        req_type = PmsExecutionPurchasesRequisitionsMaster.objects.only('type').get(id=PmsExecutionPurchasesDispatch.
                                                                                    requisitions_master.id).type
            
        if req_type.__dict__['type_name'] == 'Machinery':
            machinery_details = PmsMachineries.objects.get(id=PmsExecutionPurchasesDispatch.dispatch_item)
            # print("machinery_details", machinery_details.__dict__)
            item_details_dict['id'] = machinery_details.__dict__['id']
            item_details_dict['equipment_engine_serial_no'] = machinery_details.__dict__['equipment_engine_serial_no']
            item_details_dict['equipment_power'] = machinery_details.__dict__['equipment_power']
            item_details_dict['equipment_category_id'] = machinery_details.__dict__['equipment_category_id']
            item_details_dict['equipment_name'] = machinery_details.__dict__['equipment_name']
            item_details_dict['measurement_quantity'] = machinery_details.__dict__['measurement_quantity']
            item_details_dict['equipment_chassis_serial_no'] = machinery_details.__dict__['equipment_chassis_serial_no']
            item_details_dict['equipment_make'] = machinery_details.__dict__['equipment_make']
            item_details_dict['equipment_registration_no'] = machinery_details.__dict__['equipment_registration_no']
            item_details_dict['equipment_type_id'] = machinery_details.__dict__['equipment_type_id']
            item_details_dict['fuel_consumption'] = machinery_details.__dict__['fuel_consumption']
            item_details_dict['equipment_model_no'] = machinery_details.__dict__['equipment_model_no']
            return item_details_dict
        else:
            # uom = MaterialsUnitMapping.objects.only('unit').get(id=req_type.__dict__['id']).unit.c_name
            # print("uom",uom)
            materials_details = Materials.objects.get(id=PmsExecutionPurchasesDispatch.dispatch_item)
            # print("materials_details",materials_details.__dict__['id'])
            item_details_dict['id'] = materials_details.__dict__['id']
            item_details_dict['name'] = materials_details.__dict__['name']
            item_details_dict['uom'] = PmsExecutionPurchasesDispatch.uom.c_name
            item_details_dict['mat_code'] = materials_details.__dict__['mat_code']
            # print("item_details",item_details)
            return item_details_dict

    def get_vendor_name(self, PmsExecutionPurchasesDelivery):

        v_name = PmsExternalUsers.objects.only('contact_person_name').get(
            is_deleted=False,id=PmsExecutionPurchasesDelivery.vendor.id).contact_person_name
        if v_name:
            vendor_name = v_name
        else:
            vendor_name=""
        return vendor_name
    def get_document_details(self, PmsExecutionPurchasesDispatch):
        # print("PmsExecutionPurchasesDelivery",PmsExecutionPurchasesDelivery.id)
        document_details = PmsExecutionPurchasesDispatchDocument.objects.filter(dispatch=PmsExecutionPurchasesDispatch.id,
                                                                  is_deleted=False)
        print('document_details',document_details)
        request = self.context.get('request')
        response_list = []
        for each_document in document_details:
            file_url = request.build_absolute_uri(each_document.document.url) if each_document.document else ""
            owned_by = str(each_document.owned_by) if each_document.owned_by else ''
            created_by = str(each_document.created_by) if each_document.created_by else ''
            each_data = {
                "id": int(each_document.id),
                "dispatch": int(each_document.dispatch.id),
                "document_name": each_document.document_name,
                "document": file_url,
                "created_by": created_by,
                "owned_by": owned_by
            }
            response_list.append(each_data)
        return response_list
class ExecutionPurchasesDispatchDocumentAddSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    owned_by = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsExecutionPurchasesDispatchDocument
        fields = ('id', 'dispatch', 'document_name', 'document', 'created_by', 'owned_by')
class ExecutionPurchasesDispatchDocumentEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsExecutionPurchasesDispatchDocument
        fields = ("id","document_name","updated_by")

#:::::::::::::::::::::: PMS EXECUTION PURCHASES DELIVERY:::::::::::::::::::::::::::#
class ExecutionPurchasesDeliveryAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    # completed_status = serializers.CharField(required=False)

    # document_details = serializers.SerializerMethodField()

    class Meta:
        model = PmsExecutionPurchasesDelivery
        fields = ('id', 'requisitions_master', 'received_item', 'received_quantity', 'uom',
                  'date_of_delivery', 'vendor', 'po_no', 'grn_no', 'e_way_bill_no', 'return_and_issue',
                  'return_cost', 'compensation', 'date_of_receipt', 'created_by', 'owned_by')

    def create(self, validated_data):        
        with transaction.atomic():
            try:
                # master_update = {}
                filter = {}
                created_by = validated_data.get('created_by')
                owned_by = validated_data.get('owned_by')
                requisitions_master_id = validated_data.get('requisitions_master').id
                item = validated_data.get('received_item')
                vendor_id = validated_data.get('vendor').id
                po_no = validated_data.get('po_no')
                delivery_quantity = validated_data.get('received_quantity')
                uom = validated_data.get('uom')
                # completed_status = validated_data.pop(
                #     'completed_status') if 'completed_status' in validated_data else ''

                #############################
                # for stock entry
                # print("validated_data", validated_data)
                requisition_master_data = PmsExecutionPurchasesRequisitionsMaster.objects.filter(
                    id=requisitions_master_id)
                for x in requisition_master_data:
                    # print("::::::::::::::::::::::", x.id)
                    p = PmsExecutionStock.objects.create(
                        which_requisition_tab="delivery",
                        project=x.project,
                        site_location=x.site_location,
                        recieved_stock=delivery_quantity,
                        uom=uom,
                        item=item,
                        type=x.type,
                        requisition_id=x.id,
                        created_by=created_by,
                        owned_by=owned_by
                    )
                    print(":::::::::::::::::::", p)
                    exist_updated_stock_ck = PmsExecutionUpdatedStock.objects.filter(
                        project=x.project, site_location=x.site_location,
                        item=item, type=x.type,
                        uom=uom)
                    print("exist_updated_stock_ck",exist_updated_stock_ck)
                    if exist_updated_stock_ck:
                        for e_exist_updated_stock_ck in exist_updated_stock_ck:
                            e_exist_updated_stock_ck.recieved_stock = delivery_quantity
                            e_exist_updated_stock_ck.updated_by = owned_by
                            e_exist_updated_stock_ck.save()
                            # PmsExecutionUpdatedStock.objects.update(
                            #     opening_stock=e_requisition_details['current_stock'],
                            #     updated_by=owned_by,
                            #     )
                            print("e_exist_updated_stock_ck", e_exist_updated_stock_ck)
                    else:

                        PmsExecutionUpdatedStock.objects.create(
                            project=x.project,
                            site_location=x.site_location,
                            recieved_stock=delivery_quantity,
                            uom=uom,
                            item=item,
                            type=x.type,
                            requisition_id=x.id,
                            created_by=created_by,
                            owned_by=owned_by
                        )
                        print("PmsExecutionUpdatedStock", PmsExecutionUpdatedStock)

                        #############################

                # print("completed_status", type(completed_status))
                # if int(completed_status) == 3:
                #     print("int(completed_status) == 3")
                #     status_update = PmsExecutionPurchasesRequisitionsMaster.objects.filter(
                #         id=str(requisitions_master_id)
                #         ).update(completed_status=3)
                #     print("status_update", status_update)
                po_details = PmsExecutionPurchasesPO.objects.get(is_deleted=False,
                                                                 requisitions_master=requisitions_master_id,
                                                                 po_no=po_no, vendor=vendor_id)
                print("po_details", po_details)
                dispatch_details = PmsExecutionPurchasesDispatch.objects.get(is_deleted=False,
                                                                             requisitions_master=requisitions_master_id,
                                                                             po_no=po_no, vendor=vendor_id,
                                                                             dispatch_item=item,uom=uom)
                print("dispatch_details", dispatch_details)
                payment_terms = PmsExecutionPurchasesQuotations.objects.only('payment_terms').get(is_deleted=False,
                                                                                                  requisitions_master=requisitions_master_id,
                                                                                                  vendor=vendor_id,
                                                                                                  item=item,unit=uom).payment_terms
                print("payment_terms", payment_terms)
                filter['requisitions_master'] = validated_data.get('requisitions_master')
                filter['vendor'] = validated_data.get('vendor')
                filter['item'] = item
                filter['payment_terms'] = payment_terms
                filter['po_no'] = po_no
                filter['created_by'] = created_by
                filter['owned_by'] = owned_by
                print("filter",filter)
                if dispatch_details and payment_terms:
                    print("dispatch_details and payment_terms:", po_details.transport_cost_type.id)
                    if po_details.transport_cost_type.id == 2:
                        print("po_details.transport_cost.id==2:")
                        filter['quantity'] = dispatch_details.quantity
                        filter['uom'] = dispatch_details.uom
                        filter['price'] = dispatch_details.dispatch_cost

                    else:
                        if dispatch_details.quantity > delivery_quantity:
                            print("dispatch_details.quantity>delivery_quantity:")
                            delivery_cost = (
                                            dispatch_details.dispatch_cost / dispatch_details.quantity) * delivery_quantity  # Cost Calculation
                            filter['quantity'] = delivery_quantity
                            filter['uom'] = uom
                            filter['price'] = delivery_cost
                        else:
                            print("else")
                            filter['quantity'] = dispatch_details.quantity
                            filter['uom'] = dispatch_details.uom
                            filter['price'] = dispatch_details.dispatch_cost
                            print("gkdf", filter)
                print("filter", filter)
                if filter['price']:
                    delivery_add, created1 = PmsExecutionPurchasesDelivery.objects.get_or_create(**validated_data)
                    print("delivery_add", delivery_add)
                    payable_amount, created2 = PmsExecutionPurchasesTotalAmountPayable.objects.get_or_create(
                        **filter)
                    print("payable_amount", payable_amount)
                    delivery_add.__dict__.pop(
                        '_state') if '_state' in delivery_add.__dict__.keys() else delivery_add
                    requisitions_m_status = PmsExecutionPurchasesRequisitionsMaster.objects.only('status').get(
                        is_deleted=False,
                        id=requisitions_master_id).status
                    print("requisitions_m_status", requisitions_m_status)

                    if requisitions_m_status <7:
                        print("requisitions_m_status == None")
                        update_status = PmsExecutionPurchasesRequisitionsMaster.objects.filter(is_deleted=False,
                                                                                               id=requisitions_master_id
                                                                                               ).update(status=7)
                        print("requisitions_m_status == None",update_status)
                    else:
                        print("not update")

                # if int(completed_status) == 4:
                #     status_update = PmsExecutionPurchasesRequisitionsMaster.objects.filter(
                #         id=str(requisitions_master_id)
                #         ).update(completed_status=4)
                #     print("status_update", status_update)
                # else:
                status_update = PmsExecutionPurchasesRequisitionsMaster.objects.filter(id=str(requisitions_master_id),completed_status=3)
                if status_update:
                    dispatch_list = PmsExecutionPurchasesDispatch.objects.filter(requisitions_master=requisitions_master_id).values("id")
                    print("length_disp",len(dispatch_list))
                    delivery_list = PmsExecutionPurchasesDelivery.objects.filter(requisitions_master=requisitions_master_id).values("id")
                    print("length_disp",len(delivery_list))
                    if len(dispatch_list) == len(delivery_list):
                        status_update = PmsExecutionPurchasesRequisitionsMaster.objects.filter(id=str(requisitions_master_id)).update(completed_status=4)
                        print("status_update",status_update)
                    else:
                        status_update = 0
                else:
                    status_update = 0

                return delivery_add
            except Exception as e:
                return APIException({'request_status': 0,
                                    'error': e,
                                    'msg': settings.MSG_ERROR})
class ExecutionPurchasesDeliveryEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsExecutionPurchasesDelivery
        fields = ('id', 'return_and_issue', 'return_cost', 'compensation', 'date_of_receipt', 'updated_by')

class ExecutionPurchasesDeliveryListSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    document_details = serializers.SerializerMethodField(required=False)
    item_details = serializers.SerializerMethodField(required=False)
    vendor_name = serializers.SerializerMethodField(required=False)

    class Meta:
        model = PmsExecutionPurchasesDelivery
        fields = ('id', 'requisitions_master', 'received_item', 'received_quantity', 'uom', 'date_of_delivery','vendor',
                  'grn_no', 'e_way_bill_no', 'return_and_issue', 'return_cost', 'compensation', 'date_of_receipt', 'po_no',
                  'created_by', 'owned_by','document_details', 'item_details', 'vendor_name')

    def get_vendor_name(self, PmsExecutionPurchasesDelivery):

        v_name = PmsExternalUsers.objects.only('contact_person_name').get(
            is_deleted=False,id=PmsExecutionPurchasesDelivery.vendor.id).contact_person_name
        print("v_name",v_name)
        if v_name:
            vendor_name = v_name
        else:
            vendor_name=""

        print("kjsdgj",vendor_name)
        return vendor_name

    def get_item_details(self, PmsExecutionPurchasesDelivery):
        item_details_dict = {}
        req_type = PmsExecutionPurchasesRequisitionsMaster.objects.only('type').get(
            id=PmsExecutionPurchasesDelivery.requisitions_master.id).type

        # print("type",req_type.__dict__)

        if req_type.__dict__['type_name'] == 'Machinery':
            machinery_details = PmsMachineries.objects.get(id=PmsExecutionPurchasesDelivery.received_item)
            print("machinery_details",machinery_details.__dict__)
            item_details_dict['id']=machinery_details.__dict__['id']
            item_details_dict['equipment_engine_serial_no']=machinery_details.__dict__['equipment_engine_serial_no']
            item_details_dict['equipment_power']=machinery_details.__dict__['equipment_power']
            item_details_dict['equipment_category_id']=machinery_details.__dict__['equipment_category_id']
            item_details_dict['equipment_name']=machinery_details.__dict__['equipment_name']
            item_details_dict['measurement_quantity']=machinery_details.__dict__['measurement_quantity']
            item_details_dict['equipment_chassis_serial_no']=machinery_details.__dict__['equipment_chassis_serial_no']
            item_details_dict['equipment_make']=machinery_details.__dict__['equipment_make']
            item_details_dict['equipment_registration_no']=machinery_details.__dict__['equipment_registration_no']
            item_details_dict['equipment_type_id']=machinery_details.__dict__['equipment_type_id']
            item_details_dict['fuel_consumption']=machinery_details.__dict__['fuel_consumption']
            item_details_dict['equipment_model_no']=machinery_details.__dict__['equipment_model_no']
            return item_details_dict
        else:
            materials_details = Materials.objects.get(id=PmsExecutionPurchasesDelivery.received_item)
            # print("materials_details",materials_details.__dict__['id'])
            item_details_dict['id']=materials_details.__dict__['id']
            item_details_dict['name']=materials_details.__dict__['name']
            item_details_dict['uom']=PmsExecutionPurchasesDelivery.uom.c_name
            item_details_dict['mat_code']=materials_details.__dict__['mat_code']
            # print("item_details",item_details)
            return item_details_dict


    def get_document_details(self, PmsExecutionPurchasesDelivery):
        # print("PmsExecutionPurchasesDelivery",PmsExecutionPurchasesDelivery.id)
        document_details = PmsExecutionPurchasesDeliveryDocument.objects.filter(delivery=PmsExecutionPurchasesDelivery.id,
                                                                  is_deleted=False)
        print('document_details',document_details)
        request = self.context.get('request')
        response_list = []
        for each_document in document_details:
            file_url = request.build_absolute_uri(each_document.document.url) if each_document.document else ""
            owned_by = str(each_document.owned_by) if each_document.owned_by else ''
            created_by = str(each_document.created_by) if each_document.created_by else ''
            each_data = {
                "id": int(each_document.id),
                "delivery": int(each_document.delivery.id),
                "document_name": each_document.document_name,
                "document": file_url,
                "created_by": created_by,
                "owned_by": owned_by
            }
            response_list.append(each_data)
        return response_list

class ExecutionPurchasesDeliveryDocumentAddSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    owned_by = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsExecutionPurchasesDeliveryDocument
        fields = ('id', 'delivery', 'document_name', 'document', 'created_by', 'owned_by')
class ExecutionPurchasesDeliveryDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsExecutionPurchasesDelivery
        fields = ('id', 'is_deleted', 'updated_by')

    def update(self, instance, validated_data):
        try:
            with transaction.atomic():
                # print("instance",instance.requisitions_master)
                # master_status = PmsExecutionPurchasesRequisitionsMaster.objects.only('completed_status').get(
                #     id=instance.requisitions_master.id
                # ).completed_status
                # print("master_status",master_status)
                instance.is_deleted = True
                instance.updated_by = validated_data.get('updated_by')
                instance.save()

                dispatch_document = PmsExecutionPurchasesDeliveryDocument.objects.filter(delivery=instance,
                                                                                         is_deleted=False).update(
                    is_deleted=True)
                # print("dispatch_document",dispatch_document)
                return instance

        except Exception as e:
            raise e

class PurchaseRequisitionsTotalDeliveryMaterialRecievedListSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    # status=serializers.CharField(required=False)
    class Meta:
        model = PmsExecutionPurchasesDelivery
        fields = ('requisitions_master','received_item','received_quantity','uom','vendor','date_of_delivery','created_by',
        'owned_by','created_at','updated_at','updated_by','id')

#:::::::::::::::::::::::::::::::::PMS EXECUTION PURCHASES PAYMENT PLAN::::::::::::::::::::::::::::::::::::::::::::::::::::#
class ExecutionPurchasesPaymentPlanAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    vendor_name = serializers.SerializerMethodField(required=False)

    class Meta:
        model = PmsExecutionPurchasesPaymentPlan
        fields = ('id', 'requisitions_master', 'due_amount', 'due_date', 'vendor', 'created_by', 'owned_by', 'vendor_name')

    def get_vendor_name(self, PmsExecutionPurchasesPaymentPlan):
        v_name = PmsExternalUsers.objects.only('contact_person_name').get(
            is_deleted=False,id=PmsExecutionPurchasesPaymentPlan.vendor.id).contact_person_name
        print("v_name",v_name)
        if v_name:
            vendor_name = v_name
        else:
            vendor_name=""

        print("kjsdgj",vendor_name)
        return vendor_name

#:::::::::::::::::::::: PMS EXECUTION PURCHASES PAYMENTS MADE:::::::::::::::::::::::::::#
class ExecutionPurchasesPaymentsMadeAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    completed_status = serializers.CharField(required=True)

    class Meta:
        model = PmsExecutionPurchasesPaymentsMade
        fields = ('id',  'requisitions_master', 'payment_amount', 'payment_date', 'invoice_number', 'transaction_id',
                  'vendor', 'po_no', 'created_by', 'owned_by', 'completed_status')

    def create(self, validated_data):
        requisitions_master_id = str(validated_data.get('requisitions_master'))
        completed_status = validated_data.pop('completed_status') if 'completed_status' in validated_data else ''
        with transaction.atomic():
            payments_add,created = PmsExecutionPurchasesPaymentsMade.objects.get_or_create(**validated_data)
            # print("payments_add",payments_add)
            # print("created",created)
            if int(completed_status) == 5:
                status_update = PmsExecutionPurchasesRequisitionsMaster.objects.filter(id=requisitions_master_id).update(
                    completed_status=5,status=9)
                # print("status_update",status_update)
            else:
                requisitions_m_status = PmsExecutionPurchasesRequisitionsMaster.objects.only('status').get(is_deleted=False,
                                                                                                        id=requisitions_master_id).status
                # print("requisitions_m_status", type(requisitions_m_status))

                if requisitions_m_status < 8 or requisitions_m_status == None:
                    update_status = PmsExecutionPurchasesRequisitionsMaster.objects.filter(is_deleted=False,
                                                                                        id=requisitions_master_id
                                                                                        ).update(status=8)
                status_update=completed_status

            validated_data['completed_status']=status_update
            validated_data['id']=payments_add.id
            return validated_data

class ExecutionPurchasesPaymentsMadeEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsExecutionPurchasesPaymentsMade
        fields = (
        'id', 'requisitions_master', 'payment_amount', 'payment_date', 'invoice_number', 'transaction_id',
        'vendor', 'po_no', 'updated_by')
class ExecutionPurchasesPaymentsMadeDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsExecutionPurchasesPaymentsMade
        fields = ('id', 'is_deleted', 'updated_by')

    def update(self, instance, validated_data):
        instance.is_deleted = True
        instance.updated_by = validated_data.get('updated_by')
        instance.save()
        return instance
class ExecutionPurchasesPaymentsMadeDocumentAddSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    owned_by = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsExecutionPurchasesPaymentsMadeDocument
        fields = ('id', 'purchases_made', 'document_name', 'document', 'created_by', 'owned_by')
class ExecutionPurchasesPaymentsMadeDocumentEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsExecutionPurchasesPaymentsMadeDocument
        fields = ("id", "document_name", "updated_by")
class ExecutionPurchasesPaymentsMadeDocumentDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsExecutionPurchasesPaymentsMadeDocument
        fields = ("id", "is_deleted", "updated_by")

    def update(self, instance, validated_data):
        instance.is_deleted = True
        instance.updated_by = validated_data.get('updated_by')
        instance.save()
        return instance
class ExecutionPurchasesPaymentsMadeListSerializer(serializers.ModelSerializer):
    vendor_name = serializers.SerializerMethodField(required=False)
    paid_by = serializers.SerializerMethodField(required=False)

    class Meta:
        model = PmsExecutionPurchasesPaymentsMade
        fields = ('id', 'requisitions_master', 'payment_amount', 'payment_date', 'invoice_number', 'transaction_id',
                  'vendor', 'po_no', 'vendor_name', 'paid_by')

    def get_vendor_name(self, PmsExecutionPurchasesDelivery):
        return PmsExternalUsers.objects.only('contact_person_name').get(
            is_deleted=False,id=PmsExecutionPurchasesDelivery.vendor.id).contact_person_name

    def get_paid_by(self, PmsExecutionPurchasesDelivery):
        company_name = PmsExecutionPurchasesRequisitionsMaster.objects.only('site_location').get(
            id=PmsExecutionPurchasesDelivery.requisitions_master.id).site_location
        return company_name.__dict__['company_name']



class ExecutionPurchasesTotalAmountPayableListSerializer(serializers.ModelSerializer):
    item_details = serializers.SerializerMethodField(required=False)
    vendor_name = serializers.SerializerMethodField(required=False)
    payment_terms_details = serializers.SerializerMethodField(required=False)

    class Meta:
        model = PmsExecutionPurchasesTotalAmountPayable
        fields = ('id', 'requisitions_master', 'vendor', 'item', 'quantity', 'uom', 'price', 'payment_terms', 'po_no',
                  'item_details', 'vendor_name', 'payment_terms_details')

    def get_vendor_name(self, PmsExecutionPurchasesTotalAmountPayable):

        print("PmsExecutionPurchasesTotalAmountPayable.vendor.id",PmsExecutionPurchasesTotalAmountPayable.vendor.id)
        # v_name = PmsExternalUsers.objects.filter( is_deleted=False,id=PmsExecutionPurchasesTotalAmountPayable.vendor.id)
        v_name = PmsExternalUsers.objects.only('contact_person_name').get(
            is_deleted=False,id=PmsExecutionPurchasesTotalAmountPayable.vendor.id).contact_person_name
        print("v_name",v_name)
        if v_name:
            vendor_name = v_name
        else:
            vendor_name=""

        print("kjsdgj",vendor_name)
        return vendor_name

    def get_payment_terms_details(self, PmsExecutionPurchasesTotalAmountPayable):
        # payment = PmsExecutionPurchasesQuotationsPaymentTermsMaster.
        payment = PmsExecutionPurchasesQuotationsPaymentTermsMaster.objects.only('name').get(
            is_deleted=False,id=PmsExecutionPurchasesTotalAmountPayable.payment_terms.id).name
        print("payment",payment)
        return payment

    def get_item_details(self, PmsExecutionPurchasesTotalAmountPayable):
        item_details_dict = {}
        req_type = PmsExecutionPurchasesRequisitionsMaster.objects.only('type').get(id=PmsExecutionPurchasesTotalAmountPayable.
                                                                                    requisitions_master.id).type

        # print("type",req_type.__dict__['type_name'])
           
        if req_type.__dict__['type_name'] == 'Machinery':
            machinery_details = PmsMachineries.objects.get(id=PmsExecutionPurchasesTotalAmountPayable.item)
            print("machinery_details",machinery_details.__dict__)
            item_details_dict['id']=machinery_details.__dict__['id']
            item_details_dict['equipment_engine_serial_no']=machinery_details.__dict__['equipment_engine_serial_no']
            item_details_dict['equipment_power']=machinery_details.__dict__['equipment_power']
            item_details_dict['equipment_category_id']=machinery_details.__dict__['equipment_category_id']
            item_details_dict['equipment_name']=machinery_details.__dict__['equipment_name']
            item_details_dict['measurement_quantity']=machinery_details.__dict__['measurement_quantity']
            item_details_dict['equipment_chassis_serial_no']=machinery_details.__dict__['equipment_chassis_serial_no']
            item_details_dict['equipment_make']=machinery_details.__dict__['equipment_make']
            item_details_dict['equipment_registration_no']=machinery_details.__dict__['equipment_registration_no']
            item_details_dict['equipment_type_id']=machinery_details.__dict__['equipment_type_id']
            item_details_dict['fuel_consumption']=machinery_details.__dict__['fuel_consumption']
            item_details_dict['equipment_model_no']=machinery_details.__dict__['equipment_model_no']
            return item_details_dict
        else:
            if MaterialsUnitMapping.objects.filter(id=req_type.__dict__['id']).count():
                uom = MaterialsUnitMapping.objects.only('unit').get(id=req_type.__dict__['id']).unit.c_name
            else:
                uom = ''
            # print("uom",uom)
            materials_details = Materials.objects.get(id=PmsExecutionPurchasesTotalAmountPayable.item)
            # print("materials_details",materials_details.__dict__['id'])
            item_details_dict['id']=materials_details.__dict__['id']
            item_details_dict['name']=materials_details.__dict__['name']
            item_details_dict['uom']=uom
            item_details_dict['mat_code']=materials_details.__dict__['mat_code']
            # print("item_details",item_details)
            return item_details_dict




# :::::::::::::::::::::::::STOCK:::::::::::::::::::::::::::::::::::::#
class StockIssueModeSerializeradd(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsExecutionIssueMode
        fields = ('__all__')
class StockIssueModeSerializeredit(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsExecutionIssueMode
        fields = ('id', 'name', 'updated_by')

class StockIssueMobileSerializeredit(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsExecutionStockIssue
        fields = ('__all__')


class StockMobileIssueSerializerdelete(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    is_deleted = serializers.BooleanField(default=True)

    class Meta:
        model = PmsExecutionStockIssue
        fields = ('id','issue_master', 'is_deleted', 'updated_by')

    # def update(self, instance, validated_data):
    #     try:
    #         with transaction.atomic():
    #             instance.is_deleted = True
    #             instance.save()
    #             return instance
    #     except Exception as e:
    #         raise APIException({'request_status': 0, 'msg': e})
class StockIssueModeSerializerdelete(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsExecutionIssueMode
        fields = ('id', 'is_deleted', 'updated_by')

    def update(self, instance, validated_data):
        try:
            with transaction.atomic():
                instance.is_deleted = True
                instance.save()
                return instance
        except Exception as e:
            raise APIException({'request_status': 0, 'msg': e})
class StockIssueAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    requested_by = serializers.CharField(default=serializers.CurrentUserDefault())
    authorized_by = serializers.CharField(default=serializers.CurrentUserDefault())
    recieved_by = serializers.CharField(default=serializers.CurrentUserDefault())
    store_keeper = serializers.CharField(default=serializers.CurrentUserDefault())
    issue_items = serializers.ListField(required=False)

    class Meta:
        model = PmsExecutionStockIssueMaster
        fields = ('__all__')
        extra_fields = ('progress_data')

    def create(self, validated_data):
        try:
            issue_items = validated_data.pop('issue_items') if 'issue_items' in validated_data else ""
            owned_by = validated_data.get('owned_by')
            created_by = validated_data.get('created_by')
            with transaction.atomic():
                issue_master_data, created1 = PmsExecutionStockIssueMaster.objects.get_or_create(**validated_data)
                issue_list = []
                
                for issue_data in issue_items:
                    # issue_data.pop('unit_id')
                    # print("date_of_completion::::::::",pro_data['date_of_completion'],type(pro_data['date_of_completion']))
                    issue_items_data, created2 = PmsExecutionStockIssue.objects.get_or_create(
                        issue_master=issue_master_data,
                        created_by=created_by,
                        owned_by=owned_by,
                        **issue_data
                    )
                    issue_items_data.__dict__.pop(
                        '_state') if "_state" in issue_items_data.__dict__.keys() else issue_items_data.__dict__
                    issue_list.append(issue_items_data.__dict__)
                    # print("progress_list:::::", type(progress_list[0]['planned_start_date']))
                    issue_master_data.__dict__["issue_items"] = issue_list

                return issue_master_data

        except Exception as e:
            raise e

class StockIssueMobileAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    requested_by = serializers.CharField(default=serializers.CurrentUserDefault())
    authorized_by = serializers.CharField(default=serializers.CurrentUserDefault())
    recieved_by = serializers.CharField(default=serializers.CurrentUserDefault())
    store_keeper = serializers.CharField(default=serializers.CurrentUserDefault())
    issue_master = serializers.IntegerField(required=False)
    issue_items = serializers.DictField(required=False)
    class Meta:
        model = PmsExecutionStockIssueMaster
        fields = ('__all__')
        
    def create(self, validated_data):
        try:
            issue_items = validated_data.pop('issue_items') if 'issue_items' in validated_data else ""
            issue_master = validated_data.get('issue_master')
            owned_by = validated_data.get('owned_by')
            created_by = validated_data.get('created_by')
            with transaction.atomic():
                existing=PmsExecutionStockIssueMaster.objects.filter(id=issue_master)
                print('existing:::::::',existing)
                if existing:
                    issue_dict={}
                    issue_master_data=int(issue_master)
                    print(type(issue_master_data))
                    issue_items_data= PmsExecutionStockIssue.objects.create(
                        issue_master_id=issue_master_data,
                        type_item_id=issue_items['type_item_id'],
                        description=issue_items['description'],
                        wbs_number=issue_items['wbs_number'],
                        unit_id=issue_items['unit'],
                        quantity=issue_items['quantity'],
                        mode_id=issue_items['mode'],
                        remarks=issue_items['remarks'],
                        created_by=created_by,
                        owned_by=owned_by,
                    )
                    issue_items_data.__dict__.pop(
                        '_state') if "_state" in issue_items_data.__dict__.keys() else issue_items_data.__dict__
                    validated_data["issue_master"]=issue_master
                    validated_data["issue_items"]=issue_items_data.__dict__
                    return validated_data
                else:
                    issue_master_data= PmsExecutionStockIssueMaster.objects.create(
                        project_id=validated_data.get('project_id'),
                        site_location=validated_data.get('site_location'),
                        issue_date=validated_data.get('issue_date'),
                        issue_slip_no=validated_data.get('issue_slip_no'),
                        name_of_contractor=validated_data.get('name_of_contractor'),
                        type=validated_data.get('type'),
                        requested_by=validated_data.get('requested_by'),
                        authorized_by=validated_data.get('authorized_by'),
                        recieved_by=validated_data.get('recieved_by'),
                        store_keeper=validated_data.get('store_keeper'),
                        created_by=validated_data.get('created_by'),
                        owned_by=validated_data.get('owned_by'),
                        created_at=validated_data.get('created_at'),
                    )

                    issue_items_data= PmsExecutionStockIssue.objects.create(
                        issue_master=issue_master_data,
                        type_item_id=issue_items['type_item_id'],
                        description=issue_items['description'],
                        wbs_number=issue_items['wbs_number'],
                        unit_id=issue_items['unit'],
                        quantity=issue_items['quantity'],
                        mode_id=issue_items['mode'],
                        remarks=issue_items['remarks'],
                        created_by=created_by,
                        owned_by=owned_by,
                    )
                    print('issue_items_data',issue_items_data)
                    issue_items_data.__dict__.pop(
                        '_state') if "_state" in issue_items_data.__dict__.keys() else issue_items_data.__dict__
                    issue_master_data.__dict__["issue_items"] = issue_items_data.__dict__

                    return issue_master_data

        except Exception as e:
            raise e

class StockIssueSerializeredit(serializers.ModelSerializer):
    updated_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    is_approved = serializers.BooleanField(default=False)
    class Meta:
        model = PmsExecutionStockIssueMaster
        fields= ('__all__')



    def update(self, instance, validated_data):
        try:
            with transaction.atomic():

                section_name = self.context['request'].query_params.get('section_name', None)
                # issue_master_id=validated_data.pop('issue_master')
                owned_by = validated_data.get('owned_by')
                created_by = validated_data.get('created_by')
                others_checking=TCoreOther.objects.only('id').get(cot_name=section_name,cot_is_deleted=False).id

                approval_section=PmsApprovalPermissonLavelMatser.objects.only('permission_level').get(section=others_checking).permission_level

                permission_level=PmsApprovalPermissonMatser.objects.only('permission_level').\
                    get(id= str(validated_data.get('approval_permission_user_level')),section=others_checking,is_deleted=False).permission_level
                permission_level=re.sub("\D", "",permission_level)
                if int(permission_level) < int(approval_section):
                    instance.issue_stage_status = 2
                    instance.issue_approval=validated_data.get('issue_approval')
                    instance.approval_permission_user_level=validated_data.get('approval_permission_user_level')
                    instance.updated_by = validated_data.get('updated_by')
                    instance.save()
                    log_table_entry=PmsExecutionStockIssueMasterLogTable.objects.create(
                        issue_master_id=instance.id,
                        issue_stage_status=instance.issue_stage_status,
                        project_id=instance.project_id,
                        site_location=instance.site_location,
                        issue_date=instance.issue_date,
                        issue_slip_no=instance.issue_slip_no,
                        name_of_contractor=instance.name_of_contractor,
                        type=instance.type,
                        no_of_items=instance.no_of_items,
                        requested_by=instance.requested_by,
                        authorized_by=instance.authorized_by,
                        recieved_by=instance.recieved_by,
                        store_keeper=instance.store_keeper,
                        is_approved=False,
                        issue_approval=validated_data.get('issue_approval'),
                        approval_permission_user_level=validated_data.get('approval_permission_user_level'),
                        updated_by = validated_data.get('updated_by')
                        )

              
                elif int(permission_level)== int(approval_section):
                    instance.issue_stage_status = 3
                    instance.updated_by = validated_data.get('updated_by')
                    instance.is_approved = True
                    instance.issue_approval=validated_data.get('issue_approval')
                    instance.approval_permission_user_level=validated_data.get('approval_permission_user_level')
                    instance.save()
                    log_table_entry=PmsExecutionStockIssueMasterLogTable.objects.create(
                        issue_master_id=instance.id,
                        issue_stage_status=instance.issue_stage_status,
                        project_id=instance.project_id,
                        site_location=instance.site_location,
                        issue_date=instance.issue_date,
                        issue_slip_no=instance.issue_slip_no,
                        name_of_contractor=instance.name_of_contractor,
                        type=instance.type,
                        no_of_items=instance.no_of_items,
                        requested_by=instance.requested_by,
                        authorized_by=instance.authorized_by,
                        recieved_by=instance.recieved_by,
                        store_keeper=instance.store_keeper,
                        is_approved=True,
                        issue_approval=validated_data.get('issue_approval'),
                        approval_permission_user_level=validated_data.get('approval_permission_user_level'),
                        updated_by = validated_data.get('updated_by')
                        )
                    stock_issue=PmsExecutionStockIssue.objects.filter(issue_master=instance.id,is_deleted=False)
                    for stock_data in stock_issue:
                        p=PmsExecutionStock.objects.create(
                            which_requisition_tab="issue",
                            project=validated_data.get('project_id'),
                            site_location=validated_data.get('site_location'),
                            issued_stock=stock_data.quantity,
                            uom_id=stock_data.unit.id,
                            item=int(stock_data.type_item_id),
                            type=validated_data.get('type'),
                            purpose=stock_data.remarks,
                            created_by = created_by,
                            owned_by = owned_by
                        )

                        exist_updated_stock_ck=PmsExecutionUpdatedStock.objects.filter(
                            project=validated_data.get('project_id'),site_location=validated_data.get('site_location'),
                            item=p.item,type=validated_data.get('type'),
                            uom_id=p.uom_id,)
                        if exist_updated_stock_ck:
                            for e_exist_updated_stock_ck in exist_updated_stock_ck:
                                e_exist_updated_stock_ck.issued_stock = stock_data.quantity
                                e_exist_updated_stock_ck.purpose=stock_data.remarks
                                e_exist_updated_stock_ck.updated_by = owned_by
                                e_exist_updated_stock_ck.save()

                        else:

                            PmsExecutionUpdatedStock.objects.create(
                                project=validated_data.get('project_id'),
                                site_location=validated_data.get('site_location'),
                                issued_stock=stock_data.quantity,
                                uom_id=stock_data.unit.id,
                                item=int(stock_data.type_item_id),
                                type=validated_data.get('type'),
                                purpose=stock_data.remarks,
                                created_by = created_by,
                                owned_by = owned_by,
                                )
                else:
                    instance.issue_stage_status = 3
                    instance.is_approved = validated_data.get('is_approved')
                    instance.updated_by = validated_data.get('updated_by')
                    instance.save()         
                # print(validated_data)
                return log_table_entry

        except Exception as e:
            raise e

    




class StockIssueListSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    issue_data = serializers.SerializerMethodField()
    project_details = serializers.SerializerMethodField()
    site_location_details = serializers.SerializerMethodField()
    contractor_details = serializers.SerializerMethodField()
    requested_by = serializers.CharField(default=serializers.CurrentUserDefault())
    authorized_details = serializers.SerializerMethodField()
    recieved_details = serializers.SerializerMethodField()
    store_keeper_details = serializers.SerializerMethodField()
    no_of_items = serializers.SerializerMethodField()
    permission_details = serializers.SerializerMethodField()
    def get_issue_data(self, PmsExecutionStockIssueMaster):
        issue_list = []
        issue_list_details = []
        issue_d = PmsExecutionStockIssue.objects.filter(issue_master=PmsExecutionStockIssueMaster.id)
        # print("issue_d::::::::", issue_d)
        for data in issue_d:
            data.__dict__.pop('_state') if "_state" in data.__dict__.keys() else data.__dict__
            #print('data.__dict__',data.__dict__)
            issue_list.append(data.__dict__)
        for il in issue_list:
            # print("il:::::::::::::::",il)
            material_name = Materials.objects.filter(id=il['type_item_id']).values('id', 'name','mat_code')
            unit_details = TCoreUnit.objects.filter(id=il['unit_id']).values('id', 'c_name')
            mode_details = PmsExecutionIssueMode.objects.filter(id=il['mode_id']).values('id', 'name')
            # print("material_name:::::::::::::",material_name)
            il['type_item_id'] = [x for x in material_name][0]
            il['unit_id'] = [x for x in unit_details][0]
            il['mode_id'] = [x for x in mode_details][0]
            issue_list_details.append(il)
            #print(issue_list_details)

        # print("issue_list_details", issue_list_details)
        return issue_list_details
    def get_project_details(self,PmsExecutionStockIssueMaster):
        return [x for x in PmsProjects.objects.filter(id=str(PmsExecutionStockIssueMaster.project_id)).values('id', 'name','project_g_id')][0]
    def get_site_location_details(self, PmsExecutionStockIssueMaster):
        return [x for x in PmsSiteProjectSiteManagement.objects.filter(id=str(PmsExecutionStockIssueMaster.site_location)).values('id', 'name')][0]
    def get_contractor_details(self, PmsExecutionStockIssueMaster):
        return [x for x in PmsExternalUsers.objects.filter(id=str(PmsExecutionStockIssueMaster.name_of_contractor)).values('id','contact_person_name')][0]
    def get_authorized_details(self,PmsExecutionStockIssueMaster):
        print('PmsExecutionStockIssueMaster.authorized_by',PmsExecutionStockIssueMaster.authorized_by)
        if PmsExecutionStockIssueMaster.authorized_by:
            return [x for x in User.objects.filter(id=str(PmsExecutionStockIssueMaster.authorized_by.id)).values('id','username')][0]
    def get_recieved_details(self,PmsExecutionStockIssueMaster):
        if PmsExecutionStockIssueMaster.recieved_by:
            return [x for x in User.objects.filter(id=str(PmsExecutionStockIssueMaster.recieved_by.id)).values('id','username')][0]
    def get_store_keeper_details(self,PmsExecutionStockIssueMaster):
        if PmsExecutionStockIssueMaster.store_keeper:
            return [x for x in User.objects.filter(id=str(PmsExecutionStockIssueMaster.store_keeper.id)).values('id','username')][0]
    def get_no_of_items(self,PmsExecutionStockIssueMaster):
        return PmsExecutionStockIssue.objects.filter(issue_master=PmsExecutionStockIssueMaster.id).count()
    def get_permission_details(self,PmsExecutionStockIssueMaster):
        #level of approvals list 

        section_name = self.context['request'].query_params.get('section_name', None)
        permission_details=[]
        if section_name:
            
            section_details=TCoreOther.objects.get(cot_name__iexact=section_name)
            approval_master_details = PmsApprovalPermissonMatser.objects.filter(section=section_details.id)
            print("approval_master_details",approval_master_details)
            log_details=PmsExecutionStockIssueMasterLogTable.objects.\
                    filter(issue_master=PmsExecutionStockIssueMaster.id).\
                        values('id','issue_approval','approval_permission_user_level')
            # print(log_details) 
            amd_list=[]
            l_d_list=[]
            for l_d in log_details:
                l_d_list.append(l_d['approval_permission_user_level'])

            for a_m_d in approval_master_details:
                if l_d_list:
                    if a_m_d.id in l_d_list:
                        l_d=log_details.get(approval_permission_user_level=a_m_d.id)
                        f_name = a_m_d.approval_user.first_name if a_m_d.approval_user else '' 
                        l_name = a_m_d.approval_user.last_name if a_m_d.approval_user else '' 
                        var=a_m_d.permission_level
                        res = re.sub("\D", "", var)
                        permission_dict={
                            "user_level":a_m_d.permission_level,
                            "approval":l_d['issue_approval'],
                            "permission_num":int(res),
                            "user_details":{
                                "id":a_m_d.approval_user.id if a_m_d.approval_user else None,
                                "email":a_m_d.approval_user.email if a_m_d.approval_user else None,
                                "name":  f_name +' '+l_name,
                                "username":a_m_d.approval_user.username
                            }
                        }
                            

                    else:
                        f_name = a_m_d.approval_user.first_name if a_m_d.approval_user else '' 
                        l_name = a_m_d.approval_user.last_name if a_m_d.approval_user else '' 
                        var=a_m_d.permission_level
                        res = re.sub("\D", "", var)
                        permission_dict={
                            "user_level":a_m_d.permission_level,
                            "permission_num":int(res),
                            "approval":None,
                            "user_details":{
                                "id":a_m_d.approval_user.id if a_m_d.approval_user else None,
                                "email":a_m_d.approval_user.email if a_m_d.approval_user else None,
                                "name":  f_name +' '+l_name,
                                "username":a_m_d.approval_user.username
                            }
                        }

                    permission_details.append(permission_dict)
                else:
                    f_name = a_m_d.approval_user.first_name if a_m_d.approval_user else '' 
                    l_name = a_m_d.approval_user.last_name if a_m_d.approval_user else '' 
                    var=a_m_d.permission_level
                    res = re.sub("\D", "", var)
                    permission_dict={
                            "user_level":a_m_d.permission_level,
                            "permission_num":int(res),
                            "approval":None,
                            "user_details":{
                                "id":a_m_d.approval_user.id if a_m_d.approval_user else None,
                                "email":a_m_d.approval_user.email if a_m_d.approval_user else None,
                                "name":  f_name +' '+l_name,
                                "username":a_m_d.approval_user.username
                            }
                        }
                    permission_details.append(permission_dict)
        
            
        return permission_details
    class Meta:
        model = PmsExecutionStockIssueMaster
        fields = ('__all__')

class StockIssueMobileEachListSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    item_details = serializers.SerializerMethodField()
    unit_details = serializers.SerializerMethodField()
    mode_details = serializers.SerializerMethodField()
    data_dict=serializers.DictField(required=False)
    def get_item_details(self, PmsExecutionStockIssue):
        data_dict={}
        material_name = Materials.objects.filter(id=PmsExecutionStockIssue.type_item_id).values('id', 'name','mat_code')
        type_item_id = [x for x in material_name][0]
        return type_item_id
    def get_unit_details(self, PmsExecutionStockIssue):
        unit_details = TCoreUnit.objects.filter(id=PmsExecutionStockIssue.unit.id).values('id', 'c_name')
        return [x for x in unit_details][0]
    def get_mode_details(self, PmsExecutionStockIssue):
        mode_details = PmsExecutionIssueMode.objects.filter(id=PmsExecutionStockIssue.mode.id).values('id', 'name')
        return [x for x in mode_details][0]
       
    class Meta:
        model = PmsExecutionStockIssue
        fields = ('__all__')  
        extra_fields=('issue_data','unit_details','mode_details') 

class StockIssueApprovedListSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    issue_data = serializers.SerializerMethodField()
    project_details = serializers.SerializerMethodField()
    site_location_details = serializers.SerializerMethodField()
    contractor_details = serializers.SerializerMethodField()
    requested_by = serializers.CharField(default=serializers.CurrentUserDefault())
    authorized_details = serializers.SerializerMethodField()
    recieved_details = serializers.SerializerMethodField()
    store_keeper_details = serializers.SerializerMethodField()
    no_of_items = serializers.SerializerMethodField()
    def get_issue_data(self, PmsExecutionStockIssueMaster):
        issue_list = []
        issue_list_details = []
        issue_d = PmsExecutionStockIssue.objects.filter(issue_master=PmsExecutionStockIssueMaster.id)
        # print("issue_d::::::::", issue_d)
        for data in issue_d:
            data.__dict__.pop('_state') if "_state" in data.__dict__.keys() else data.__dict__
            #print('data.__dict__',data.__dict__)
            issue_list.append(data.__dict__)
        for il in issue_list:
            # print("il:::::::::::::::",il)
            material_name = Materials.objects.filter(id=il['type_item_id']).values('id', 'name','mat_code')
            unit_details = TCoreUnit.objects.filter(id=il['unit_id']).values('id', 'c_name')
            mode_details = PmsExecutionIssueMode.objects.filter(id=il['mode_id']).values('id', 'name')
            # print("material_name:::::::::::::",material_name)
            il['type_item_id'] = [x for x in material_name][0]
            il['unit_id'] = [x for x in unit_details][0]
            il['mode_id'] = [x for x in mode_details][0]
            issue_list_details.append(il)
            #print(issue_list_details)

        # print("issue_list_details", issue_list_details)
        return issue_list_details
    def get_project_details(self,PmsExecutionStockIssueMaster):
        return [x for x in PmsProjects.objects.filter(id=str(PmsExecutionStockIssueMaster.project_id)).values('id', 'name','project_g_id')][0]
    def get_site_location_details(self, PmsExecutionStockIssueMaster):
        return [x for x in PmsSiteProjectSiteManagement.objects.filter(id=str(PmsExecutionStockIssueMaster.site_location)).values('id', 'name')][0]
    def get_contractor_details(self, PmsExecutionStockIssueMaster):
        if PmsExecutionStockIssueMaster.name_of_contractor:
            return [x for x in PmsExternalUsers.objects.filter(id=str(PmsExecutionStockIssueMaster.name_of_contractor)).values('id','contact_person_name')][0]
    def get_authorized_details(self,PmsExecutionStockIssueMaster):
        if PmsExecutionStockIssueMaster.authorized_by:
            return [x for x in User.objects.filter(id=str(PmsExecutionStockIssueMaster.authorized_by.id)).values('id','username')][0]
    def get_recieved_details(self,PmsExecutionStockIssueMaster):
        if PmsExecutionStockIssueMaster.recieved_by:
            return [x for x in User.objects.filter(id=str(PmsExecutionStockIssueMaster.recieved_by.id)).values('id','username')][0]
    def get_store_keeper_details(self,PmsExecutionStockIssueMaster):
        if PmsExecutionStockIssueMaster.store_keeper:
            return [x for x in User.objects.filter(id=str(PmsExecutionStockIssueMaster.store_keeper.id)).values('id','username')][0]
    def get_no_of_items(self,PmsExecutionStockIssueMaster):
        return PmsExecutionStockIssue.objects.filter(issue_master=PmsExecutionStockIssueMaster.id).count()
    class Meta:
        model = PmsExecutionStockIssueMaster
        fields = ('__all__')

class StockIssueNonApprovedListSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    issue_data = serializers.SerializerMethodField()
    type_data = serializers.SerializerMethodField()
    project_details = serializers.SerializerMethodField()
    site_location_details = serializers.SerializerMethodField()
    contractor_details = serializers.SerializerMethodField()
    requested_by = serializers.CharField(default=serializers.CurrentUserDefault())
    authorized_details = serializers.SerializerMethodField()
    recieved_details = serializers.SerializerMethodField()
    store_keeper_details = serializers.SerializerMethodField()
    no_of_items = serializers.SerializerMethodField()
    def get_issue_data(self, PmsExecutionStockIssueMaster):
        issue_list = []
        issue_list_details = []
        issue_d = PmsExecutionStockIssue.objects.filter(issue_master=PmsExecutionStockIssueMaster.id)
        # print("issue_d::::::::", issue_d)
        for data in issue_d:
            data.__dict__.pop('_state') if "_state" in data.__dict__.keys() else data.__dict__
            #print('data.__dict__',data.__dict__)
            issue_list.append(data.__dict__)
        for il in issue_list:
            # print("il:::::::::::::::",il)
            material_name = Materials.objects.filter(id=il['type_item_id']).values('id', 'name','mat_code')
            unit_details = TCoreUnit.objects.filter(id=il['unit_id']).values('id', 'c_name')
            mode_details = PmsExecutionIssueMode.objects.filter(id=il['mode_id']).values('id', 'name')
            # print("material_name:::::::::::::",material_name)
            il['type_item_id'] = [x for x in material_name][0]
            il['unit_id'] = [x for x in unit_details][0]
            il['mode_id'] = [x for x in mode_details][0]
            issue_list_details.append(il)
            #print(issue_list_details)

        # print("issue_list_details", issue_list_details)
        return issue_list_details
    def get_type_data(self,PmsExecutionStockIssueMaster):
        return [x for x in PmsExecutionPurchasesRequisitionsTypeMaster.objects.filter(id=str(PmsExecutionStockIssueMaster.type)).values('id', 'type_name','code')][0]
    def get_project_details(self,PmsExecutionStockIssueMaster):
        return [x for x in PmsProjects.objects.filter(id=str(PmsExecutionStockIssueMaster.project_id)).values('id', 'name','project_g_id')][0]
    def get_site_location_details(self, PmsExecutionStockIssueMaster):
        return [x for x in PmsSiteProjectSiteManagement.objects.filter(id=str(PmsExecutionStockIssueMaster.site_location)).values('id', 'name')][0]
    def get_contractor_details(self, PmsExecutionStockIssueMaster):
        return [x for x in PmsExternalUsers.objects.filter(id=str(PmsExecutionStockIssueMaster.name_of_contractor)).values('id','contact_person_name') if x is not None][0]
    def get_authorized_details(self,PmsExecutionStockIssueMaster):
        if PmsExecutionStockIssueMaster.authorized_by:
            return [x for x in User.objects.filter(id=str(PmsExecutionStockIssueMaster.authorized_by.id)).values('id','username')][0]
    def get_recieved_details(self,PmsExecutionStockIssueMaster):
        if PmsExecutionStockIssueMaster.recieved_by:
            return [x for x in User.objects.filter(id=str(PmsExecutionStockIssueMaster.recieved_by.id)).values('id','username') ][0]
    def get_store_keeper_details(self,PmsExecutionStockIssueMaster):
        if PmsExecutionStockIssueMaster.store_keeper:
            return [x for x in User.objects.filter(id=str(PmsExecutionStockIssueMaster.store_keeper.id)).values('id','username')][0]
    def get_no_of_items(self,PmsExecutionStockIssueMaster):
        return PmsExecutionStockIssue.objects.filter(issue_master=PmsExecutionStockIssueMaster.id).count()
    class Meta:
        model = PmsExecutionStockIssueMaster
        fields = ('__all__')


class StocMonthlyReportListSerializer(serializers.ModelSerializer):
    month_stock_list_details = serializers.ListField(required=False)


    class Meta:
        model = PmsExecutionUpdatedStock
        fields = ('item','uom','month_stock_list_details')


class ExecutionStockIssueItemListByIssueIdSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    unit_details = serializers.SerializerMethodField()
    item_code_details = serializers.SerializerMethodField()
    mode_details = serializers.SerializerMethodField()
    item_details = serializers.SerializerMethodField()

    def get_unit_details(self, PmsExecutionStockIssue):
        unit_details=[]
        if PmsExecutionStockIssue.unit:
            unit_details = TCoreUnit.objects.filter(pk=PmsExecutionStockIssue.unit.id)
        if unit_details:
            for each_unit_details in unit_details:
                # print()
                unit_details = {
                    'id': each_unit_details.id,
                    'name': each_unit_details.c_name,
                }
            return unit_details
        else:
            return dict()


    def get_item_details(self, PmsExecutionStockIssue):
        master_id=PmsExecutionStockIssue.issue_master.id
        stock_master_type=PmsExecutionStockIssueMaster.objects.filter(id=master_id).values('type__type_name')
        print("stock_master_type:::",stock_master_type)
        type_name_name=[x['type__type_name'] for x in stock_master_type]
        if type_name_name[0].lower() == 'materials':
            material_details=Materials.objects.filter(is_deleted=False,id=PmsExecutionStockIssue.type_item_id)
            if material_details:
                print(material_details)
                for each_mat in material_details:
                    # print()
                    mat_details={
                        'id':each_mat.id,
                        'code':each_mat.mat_code,
                        'name':each_mat.name,
                        'description':each_mat.description
                    }
                return mat_details
            else:{}

        elif type_name_name[0].lower() == 'machinery':
            machinery_details=PmsMachineries.objects.filter(is_deleted=False,id=PmsExecutionStockIssue.type_item_id)
            if machinery_details:
                # print(material_details)
                for each_mach in machinery_details:
                    # print()
                    mach_details={
                        'id':each_mach.id,
                        'code':each_mach.code,
                        'name':each_mach.equipment_name,
                        'description':None
                    }
                return mach_details
            else:{}

            # return PmsExecutionPurchasesRequisitionsTypeMaster.objects.filter(
            #     pk=PmsExecutionStockIssue.type_item_id,).values('id', 'type_name', 'code')
    
    def get_item_code_details(self, PmsExecutionStockIssue):
        type_details = PmsExecutionPurchasesRequisitionsTypeMaster.objects.filter(pk=PmsExecutionStockIssue.issue_master.type.id)
        print('type_details',type_details)
        if type_details:
            for each_type_details in type_details:
                # print()
                type_details = {
                    'id': each_type_details.id,
                    'type_name':each_type_details.type_name,
                    'code': each_type_details.code,
                }
            return type_details
        else:
            return dict()


    def get_mode_details(self,PmsExecutionStockIssue):
        mode_details=[]
        if PmsExecutionStockIssue.mode:
            mode_details = PmsExecutionIssueMode.objects.filter(pk=PmsExecutionStockIssue.mode.id)
        if mode_details:
            for each_mode_details in mode_details:
                # print()
                mode_details = {
                    'id': each_mode_details.id,
                    'name': each_mode_details.name,
                }
            return mode_details
        else:
            return dict()

    class Meta:
        model = PmsExecutionStockIssue
        fields = ('__all__')
class ExecutionStockIssueSubmitForApprovalSerializer(serializers.ModelSerializer):
    updated_by = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsExecutionStockIssueMaster
        fields = ('id', 'issue_stage_status', 'updated_by')
class ExecutionCurrentStockReportSerializer(serializers.ModelSerializer):

    class Meta:
        model = PmsExecutionStock
        fields = ('id','project','site_location','closing_stock','stock_date','uom','type','item')
class ExecutionMaterialStockStatementReportSerializer(serializers.ModelSerializer):
    class Meta:
        model=PmsExecutionStock
        fields='__all__'

#::::::::::::::::::::::::::::::::::::  PMS EXECUTION ACTIVE PROJECTS LIST AND REPORTS  ;::::::::::::::::::::::::::::::#
class ExecutionActiveListAndReportForExternalUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = PmsExternalUsersExtraDetailsTenderMapping
        # fields = ('id','name','project_g_id','state','start_date','end_date','status','tender','site_location')
        # fields = ('id','project_g_id')
        fields = ('__all__')
class ExecutionActiveListAndReportOfPartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = PmsTenderPartners
        # fields = ('id','name','project_g_id','state','start_date','end_date','status','tender','site_location')
        # fields = ('id','project_g_id','tender')
        fields = ('__all__')

class ExecutionCurrentStockNewReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = PmsExecutionUpdatedStock
        fields = '__all__'
