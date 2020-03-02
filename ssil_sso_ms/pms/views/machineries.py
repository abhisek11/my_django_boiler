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


#:::::::::::::::::  MECHINARY MASTER :::::::::::::::#
class MachineriesAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsMachineries.objects.filter(is_deleted=False).order_by('-id')
    serializer_class = MachineriesAddSerializer
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
    # def get(self, request, *args, **kwargs):
    #     response = super(MachineriesAddView, self).get(self, request, args, kwargs)
    #     print('response.data',response.data)
    #     for data in response.data:
    #         if data["owner_type"] == 1:
    #             machinary_rented_details_queryset = PmsMachinaryRentedDetails.objects.filter(
    #                 equipment=data["id"],is_deleted=False)
    #             rental_details = dict()
    #             for machinary_rent in machinary_rented_details_queryset:
    #                 rental_details['id'] = machinary_rent.id
    #                 rental_details['equipment'] = machinary_rent.equipment.id
    #                 rental_details['vendor'] = machinary_rent.vendor.id
    #                 rental_details['rent_amount'] = machinary_rent.rent_amount
    #                 rental_details['type_of_rent'] = machinary_rent.type_of_rent.id
    #             if rental_details:
    #                 data["rental_details"] = rental_details
    #         elif data["owner_type"] == 2:
    #             owner_queryset = PmsMachinaryOwnerDetails.objects.filter(equipment=data["id"], is_deleted=False)
    #             owner_dict = {}
    #             for owner in owner_queryset:
    #                 owner_dict['id'] = owner.id
    #                 owner_dict['equipment'] = owner.equipment.id
    #                 owner_dict['purchase_date'] = owner.purchase_date
    #                 owner_dict['price'] = owner.price
    #
    #                 if owner.is_emi_available:
    #                     emi_queryset = PmsMachinaryOwnerEmiDetails.objects.filter(equipment_owner_details=owner,
    #                                                                               equipment=data["id"],
    #                                                                               is_deleted=False)
    #                     emi_dict = {}
    #                     for emi in emi_queryset:
    #                         emi_dict['id'] = emi.id
    #                         emi_dict['equipment'] = emi.equipment
    #                         emi_dict['equipment_owner_details'] = emi.equipment_owner_details
    #                         emi_dict['amount'] = emi.amount
    #                         emi_dict['start_date'] = emi.start_date
    #                         emi_dict['no_of_total_installment'] = emi.no_of_total_installment
    #
    #                     if emi_dict:
    #                         owner_dict['owner_emi_details'] = emi_dict
    #             if owner_dict:
    #                 data['owner_details'] = owner_dict
    #         elif data["owner_type"] == 3:
    #             contract_queryset = PmsMachinaryContractDetails.objects.filter(equipment=data["id"], is_deleted=False)
    #             contract_dict = {}
    #             for contract in contract_queryset:
    #                 contract_dict['id'] = contract.id
    #                 contract_dict['equipment'] = contract.equipment.id
    #                 contract_dict['contractor'] = contract.contractor.id
    #             data['contract_details'] = contract_dict
    #         else:
    #             pass
    #     return response
class MachineriesEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsMachineries.objects.all()
    serializer_class = MachineriesEditSerializer
    def get(self, request, *args, **kwargs):
        response = super(MachineriesEditView, self).get(self, request, args, kwargs)
        #print('response', response.data)
        #print('equipment_category', type(response.data['equipment_category']))
        w_c_details = {}
        PmsMachineriesWorkingCategoryde = PmsMachineriesWorkingCategory.objects.filter(
            id=response.data['equipment_category'],is_deleted=False)
        #print('PmsMachineriesWorkingCategory',PmsMachineriesWorkingCategoryde)
        for e_PmsMachineriesWorkingCategoryde in PmsMachineriesWorkingCategoryde:
            w_c_details = { 'id':e_PmsMachineriesWorkingCategoryde.id,
                            'name':e_PmsMachineriesWorkingCategoryde.name,
                            'is_deleted': e_PmsMachineriesWorkingCategoryde.is_deleted,
                            }

        response.data['equipment_category_details'] = w_c_details
        PmsMachineriesDoc = PmsMachineriesDetailsDocument.objects.filter(
            equipment=response.data['id'],is_deleted=False)
        #print('PmsMachineriesDoc', PmsMachineriesDoc)
        m_d_details_list=[]
        #request = self.context.get('request')
        for e_PmsMachineriesDoc in PmsMachineriesDoc:
            m_d_details = { 'id':e_PmsMachineriesDoc.id,
                            'name':e_PmsMachineriesDoc.document_name,
                            'document': request.build_absolute_uri(e_PmsMachineriesDoc.document.url),
                            'is_deleted': e_PmsMachineriesDoc.is_deleted,
                            }
            m_d_details_list.append(m_d_details)
        #print('m_d_details_list',m_d_details_list)
        response.data['document_details'] = m_d_details_list
        if response.data["owner_type"] == 1:
            # print('xyz',gfsdsdf)
            machinary_rented_details_queryset = PmsMachinaryRentedDetails.objects.filter(equipment=response.data["id"],
                                                                                         is_deleted=False)
            #print('machinary_rented_details_queryset',machinary_rented_details_queryset)
            rental_details = dict()
            for machinary_rent in machinary_rented_details_queryset:
                rental_details['id'] = machinary_rent.id
                rental_details['equipment'] = machinary_rent.equipment.id
                rental_details['vendor'] = machinary_rent.vendor.id if machinary_rent.vendor else None
                rental_details['rent_amount'] = machinary_rent.rent_amount
                rental_details['type_of_rent'] = machinary_rent.type_of_rent.id if machinary_rent.type_of_rent else None
            if rental_details:
                response.data["rental_details"] = rental_details
                if machinary_rent.vendor:
                    m_rented_details_vendor = PmsExternalUsers.objects.filter(
                        pk=machinary_rent.vendor.id,is_deleted=False)
                    # print('m_rented_details_vendor',m_rented_details_vendor)
                    if m_rented_details_vendor:
                        for e_m_rented_details_vendor in m_rented_details_vendor:
                            m_v_details = {'id': e_m_rented_details_vendor.id,
                                        'name': e_m_rented_details_vendor.contact_person_name,
                                        'is_deleted': e_m_rented_details_vendor.is_deleted,
                                        }
                        response.data["rental_details"]['vendor_details']= m_v_details
                    else:
                        response.data["rental_details"]['vendor_details']= {}
                else:
                    response.data["rental_details"]['vendor_details']= {}
            else:
                response.data["rental_details"] = {}
        elif response.data["owner_type"] == 2:
            owner_queryset = PmsMachinaryOwnerDetails.objects.filter(equipment=response.data["id"], is_deleted=False)
            print('owner_queryset',owner_queryset)
            owner_dict = {}
            for owner in owner_queryset:
                owner_dict['id'] = owner.id
                owner_dict['equipment'] = owner.equipment.id
                owner_dict['purchase_date'] = owner.purchase_date
                owner_dict['price'] = owner.price
                owner_dict['is_emi_available'] = owner.is_emi_available

                if owner.is_emi_available:
                    emi_queryset = PmsMachinaryOwnerEmiDetails.objects.filter(equipment_owner_details=owner,
                                                                              equipment=response.data["id"],
                                                                              is_deleted=False)
                    #print('emi_queryset',emi_queryset)
                    emi_dict = {}
                    for emi in emi_queryset:
                        emi_dict['id'] = emi.id
                        emi_dict['equipment'] = emi.equipment.id
                        emi_dict['equipment_owner_details'] = emi.equipment_owner_details.id
                        emi_dict['amount'] = emi.amount
                        emi_dict['start_date'] = emi.start_date
                        emi_dict['no_of_total_installment'] = emi.no_of_total_installment

                    if emi_dict:
                        owner_dict['owner_emi_details'] = emi_dict
                        print('owner_dict',owner_dict)
                    else:
                        owner_dict['owner_emi_details'] ={}

            if owner_dict:
                response.data['owner_details'] = owner_dict
            else:
                response.data['owner_details'] = {}
        elif response.data["owner_type"] == 3:
            contract_queryset = PmsMachinaryContractDetails.objects.filter(equipment=response.data["id"],
                                                                           is_deleted=False)
            contract_dict = {}
            for contract in contract_queryset:
                contract_dict['id'] = contract.id
                contract_dict['equipment'] = contract.equipment.id
                contract_dict['contractor'] = contract.contractor.id if contract.contractor else None
            if contract_dict:
                response.data['contract_details'] = contract_dict
            else:
                response.data['contract_details'] = {}
        else:
            lease_details=PmsMachinaryLeaseDetails.objects.filter(equipment=response.data["id"],
                                                                           is_deleted=False)
            lease_dict={}
            for l_d in lease_details:
                lease_dict['id']=l_d.id
                lease_dict['vendor']=l_d.vendor.id if l_d.vendor else None
                lease_dict['lease_amount']=l_d.lease_amount
                lease_dict['start_date']=l_d.start_date
                lease_dict['lease_period']=l_d.lease_period
            if lease_dict:
                response.data['lease_details'] = lease_dict
            else:
                response.data['lease_details'] = {}
        return response
class MachineriesListDetailsView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    pagination_class = CSPageNumberPagination
    queryset = PmsMachineries.objects.filter(is_deleted=False).order_by('-id')
    serializer_class = MachineriesListDetailsSerializer
    def get_queryset(self):
        project= self.request.query_params.get('project', None)
        owner_type=self.request.query_params.get('owner_type', None)
        if project and owner_type:
            project = project.split(',')
            owner_type=owner_type.split(',')
            print('owner_type',owner_type)
            machinery_map_data=PmsProjectsMachinaryMapping.objects.filter(project__in=project,is_deleted=False).values('machinary')
            mac_list=[]
            for machiney_id in machinery_map_data:
                mac_list.append(machiney_id['machinary'])
            sft= self.queryset.filter(id__in=mac_list,owner_type__in=owner_type)
            print('sft',sft)
            return sft
        elif project:
            project = project.split(',')
            machinery_map_data=PmsProjectsMachinaryMapping.objects.filter(project__in=project,is_deleted=False).values('machinary')
            mac_list=[]
            for machiney_id in machinery_map_data:
                mac_list.append(machiney_id['machinary'])
            return self.queryset.filter(id__in=mac_list)

        elif owner_type:
            owner_type=owner_type.split(',')
            return self.queryset.filter(owner_type__in=owner_type)
       
        else:
            return self.queryset
        # return queryset

    # def get(self,*args,**kwargs):
    #     project= self.request.query_params.get('project', None)
    #     machinery_map_data=PmsProjectsMachinaryMapping.objects.filter(project=project,is_deleted=False).values('machinary')
    #     for machiney_id in machinery_map_data:
    #         self.get_queryset(machiney_id['machinary'])



class MachineriesListWPDetailsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsMachineries.objects.filter(is_deleted=False).order_by('-id')
    serializer_class = MachineriesListDetailsSerializer
    # filter_backends = (filters.SearchFilter,)
    # search_fields = ('equipment_name', 'equipment_model_no', 'equipment_registration_no')
class MachineriesListForReportView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsMachineries.objects.filter(is_deleted=False).order_by('-id')
    serializer_class = MachineriesListDetailsSerializer

    def get(self, request, *args, **kwargs):

        '''
            Added By Rupam Hazra [264 - 274] on 2020-27-01 
            for filter by project id and date
        '''
        #print('request',self.request.query_params.get())
        project = self.request.query_params.get('project_id', None)
        #print('project',project)
        input_date = self.request.query_params.get('date', None)
        input_date = datetime.strptime(input_date,"%Y-%m-%d").date()
        #print('input_date',input_date)
        #time.sleep(10)
        response=list()
        todays_date = datetime.now()
        machineries_filter_list = PmsProjectsMachinaryMapping.objects.\
            filter(
            machinary_s_d_req__lte=input_date,
            machinary_e_d_req__gte=input_date,
            project_id = int(project)
        )

        # response=list()
        # todays_date = datetime.now()
        # machineries_filter_list = PmsProjectsMachinaryMapping.objects.\
        #     filter(
        #     machinary_s_d_req__lte=todays_date.date(),
        #     machinary_e_d_req__gte=todays_date.date()
        # )
        #print('machineries_filter_list_query',machineries_filter_list.query)
        #print('machineries_filter_list', machineries_filter_list)
        mech_list=list()
        for e_machine in machineries_filter_list:
            mech_list.append(e_machine.machinary.id)
        #print('mech_list',mech_list)
        mechine_details_list = PmsMachineries.objects.\
            filter(is_deleted=False,pk__in=mech_list)
        #print('mechine_details_list',mechine_details_list)
        for e_mechine_details in mechine_details_list:
             
            response_d = {
                'id': e_mechine_details.id,
                'equipment_name': e_mechine_details.equipment_name,
                'equipment_category': e_mechine_details.equipment_category.id if e_mechine_details.equipment_category else None,
                'equipment_type': e_mechine_details.equipment_type.name if e_mechine_details.equipment_type else None,
                'owner_type': e_mechine_details.owner_type,
                'equipment_make': e_mechine_details.equipment_make,
                'equipment_model_no': e_mechine_details.equipment_model_no,
                'equipment_registration_no': e_mechine_details.equipment_registration_no,
                'equipment_chassis_serial_no': e_mechine_details.equipment_chassis_serial_no,
                'equipment_engine_serial_no': e_mechine_details.equipment_engine_serial_no,
                'equipment_power': e_mechine_details.equipment_power,
                'measurement_by': e_mechine_details.measurement_by,
                'measurement_quantity': e_mechine_details.measurement_quantity,
                'fuel_consumption': e_mechine_details.fuel_consumption,
                'remarks': e_mechine_details.remarks
            }
            if e_mechine_details.equipment_category:
                PmsMachineriesWorkingCategoryde = PmsMachineriesWorkingCategory.objects.\
                    filter(id=e_mechine_details.equipment_category.id,is_deleted=False)
                #print('PmsMachineriesWorkingCategoryde',PmsMachineriesWorkingCategoryde)
                for e_PmsMachineriesWorkingCategoryde in PmsMachineriesWorkingCategoryde:
                    w_c_details = { 'id':e_PmsMachineriesWorkingCategoryde.id,
                                    'name':e_PmsMachineriesWorkingCategoryde.name,
                                    'is_deleted': e_PmsMachineriesWorkingCategoryde.is_deleted,
                                    }
                #print('w_c_details',w_c_details)
                response_d['equipment_category_details'] = w_c_details
            else:
                response_d['equipment_category_details'] = dict()


            PmsMachineriesDoc = PmsMachineriesDetailsDocument.objects.filter(
                equipment=e_mechine_details.id,is_deleted=False)
            #print('PmsMachineriesDoc', PmsMachineriesDoc)
            m_d_details_list=[]
            #request = self.context.get('request')
            for e_PmsMachineriesDoc in PmsMachineriesDoc:
                m_d_details = { 'id':e_PmsMachineriesDoc.id,
                                'name':e_PmsMachineriesDoc.document_name,
                                'document': request.build_absolute_uri(e_PmsMachineriesDoc.document.url),
                                'is_deleted': e_PmsMachineriesDoc.is_deleted,
                                }
                m_d_details_list.append(m_d_details)
            #print('m_d_details_list',m_d_details_list)
            response_d['document_details'] = m_d_details_list
            if e_mechine_details.owner_type == 1:
                # print('xyz',gfsdsdf)
                machinary_rented_details_queryset = PmsMachinaryRentedDetails.objects.filter(equipment=e_mechine_details.id,
                                                                                             is_deleted=False)
                #print('machinary_rented_details_queryset',machinary_rented_details_queryset)
                rental_details = dict()
                for machinary_rent in machinary_rented_details_queryset:
                    rental_details['id'] = machinary_rent.id
                    rental_details['equipment'] = machinary_rent.equipment.id
                    rental_details['vendor'] = machinary_rent.vendor.id
                    rental_details['rent_amount'] = machinary_rent.rent_amount
                    rental_details['type_of_rent'] = machinary_rent.type_of_rent.id
                if rental_details:
                    response_d["rental_details"] = rental_details
                    m_rented_details_vendor = PmsExternalUsers.objects.filter(
                        pk=machinary_rent.vendor.id,is_deleted=False)
                    #print('m_rented_details_vendor',m_rented_details_vendor)
                    for e_m_rented_details_vendor in m_rented_details_vendor:
                        m_v_details = {'id': e_m_rented_details_vendor.id,
                                       'name': e_m_rented_details_vendor.contact_person_name,
                                       'is_deleted': e_m_rented_details_vendor.is_deleted,
                                       }
                    response_d["rental_details"]['vendor_details']= m_v_details
            elif e_mechine_details.owner_type == 2:
                owner_queryset = PmsMachinaryOwnerDetails.objects.filter(equipment=e_mechine_details.id,
                                                                         is_deleted=False)
                #print('owner_queryset',owner_queryset)
                owner_dict = {}
                for owner in owner_queryset:
                    owner_dict['id'] = owner.id
                    owner_dict['equipment'] = owner.equipment.id
                    owner_dict['purchase_date'] = owner.purchase_date
                    owner_dict['price'] = owner.price
                    owner_dict['is_emi_available'] = owner.is_emi_available
                    if owner.is_emi_available:
                        emi_queryset = PmsMachinaryOwnerEmiDetails.objects.filter(equipment_owner_details=owner,
                                                                                  equipment=e_mechine_details.id,
                                                                                  is_deleted=False)
                        #print('emi_queryset',emi_queryset)
                        emi_dict = {}
                        for emi in emi_queryset:
                            emi_dict['id'] = emi.id
                            emi_dict['equipment'] = emi.equipment.id
                            emi_dict['equipment_owner_details'] = emi.equipment_owner_details.id
                            emi_dict['amount'] = emi.amount
                            emi_dict['start_date'] = emi.start_date
                            emi_dict['no_of_total_installment'] = emi.no_of_total_installment

                        if emi_dict:
                            owner_dict['owner_emi_details'] = emi_dict
                            #print('owner_dict',owner_dict)
                if owner_dict:
                    response_d['owner_details'] = owner_dict
            else:
                contract_queryset = PmsMachinaryContractDetails.objects.filter(equipment=e_mechine_details.id,
                                                                               is_deleted=False)
                contract_dict = {}
                for contract in contract_queryset:
                    contract_dict['id'] = contract.id
                    contract_dict['equipment'] = contract.equipment.id
                    contract_dict['contractor_id'] = contract.contractor.id
                    contract_dict['contractor'] = contract.contractor.contact_person_name
                response_d['contract_details'] = contract_dict
            response.append(response_d)
            #print('response',response)
        return Response(response)
class MachineriesListFilterForReportView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    pagination_class = CSPageNumberPagination

    serializer_class = MachineriesListDetailsSerializer
    filter_backends = (DjangoFilterBackend,filters.OrderingFilter)
    filterset_fields = ('equipment_name','owner_type')
    ordering_fields = '__all__'
    def get_queryset(self):
        project = self.request.query_params.get('project', None)
        if project:
            PmsProjectsMachinaryMapping_d = PmsProjectsMachinaryMapping.objects.filter(is_deleted=False,project_id=int(project))
            print('PmsProjectsMachinaryMapping_d',PmsProjectsMachinaryMapping_d)
            mapping_ids = list()
            for e_PmsProjectsMachinaryMapping_d in PmsProjectsMachinaryMapping_d:
                mapping_ids.append(e_PmsProjectsMachinaryMapping_d.machinary.id)
            print('mapping_ids',mapping_ids)

            queryset = PmsMachineries.objects.filter(pk__in=mapping_ids,is_deleted=False).order_by('-id')
            print('queryset',queryset)

        else:
            queryset = PmsMachineries.objects.filter(is_deleted=False).order_by('-id')
        return queryset

    def list(self, request, *args, **kwargs):
        response = super(MachineriesListFilterForReportView, self).list(request, args, kwargs)
        for data in response.data['results']:
            PmsMachineriesWorkingCategoryde = PmsMachineriesWorkingCategory.objects.filter(
                id=data['equipment_category'],is_deleted=False)
            for e_PmsMachineriesWorkingCategoryde in PmsMachineriesWorkingCategoryde:
                w_c_details = { 'id':e_PmsMachineriesWorkingCategoryde.id,
                                'name':e_PmsMachineriesWorkingCategoryde.name,
                                'is_deleted': e_PmsMachineriesWorkingCategoryde.is_deleted,
                                }
            data['equipment_category_details'] = w_c_details
            PmsMachineriesDoc = PmsMachineriesDetailsDocument.objects.filter(
                equipment=data['id'],is_deleted=False)
            m_d_details_list=[]
            for e_PmsMachineriesDoc in PmsMachineriesDoc:
                m_d_details = { 'id':e_PmsMachineriesDoc.id,
                                'name':e_PmsMachineriesDoc.document_name,
                                'document': request.build_absolute_uri(e_PmsMachineriesDoc.document.url),
                                'is_deleted': e_PmsMachineriesDoc.is_deleted,
                                }
                m_d_details_list.append(m_d_details)
            data['document_details'] = m_d_details_list
            if data['owner_type'] == 1:
                machinary_rented_details_queryset = PmsMachinaryRentedDetails.objects.filter(
                    equipment=data['id'],is_deleted=False)
                #print('machinary_rented_details_queryset',machinary_rented_details_queryset)
                rental_details = dict()
                if machinary_rented_details_queryset:
                    for machinary_rent in machinary_rented_details_queryset:
                        equipment=machinary_rent.equipment.id if machinary_rent.equipment else None
                        vendor=machinary_rent.vendor.id if machinary_rent.vendor else None
                        type_of_rent=machinary_rent.type_of_rent.id if machinary_rent.type_of_rent else None
                        rental_details['id'] = machinary_rent.id
                        rental_details['equipment'] = equipment
                        rental_details['vendor'] = vendor
                        rental_details['rent_amount'] = machinary_rent.rent_amount
                        rental_details['type_of_rent'] = type_of_rent
                    if rental_details:
                        data["rental_details"] = rental_details
                        if machinary_rent.vendor:
                            m_rented_details_vendor = PmsExternalUsers.objects.filter(
                                pk=machinary_rent.vendor.id,is_deleted=False)
                            #print('m_rented_details_vendor',m_rented_details_vendor)
                            if m_rented_details_vendor:
                                for e_m_rented_details_vendor in m_rented_details_vendor:
                                    m_v_details = {'id': e_m_rented_details_vendor.id,
                                                'name': e_m_rented_details_vendor.contact_person_name,
                                                'is_deleted': e_m_rented_details_vendor.is_deleted,
                                                }
                                data["rental_details"]['vendor_details']= m_v_details
                            else:
                                data["rental_details"]['vendor_details']= None
                else:
                    data['rental_details']=None
            elif data['owner_type'] == 2:
                owner_queryset = PmsMachinaryOwnerDetails.objects.filter(
                    equipment=data['id'],is_deleted=False)
                #print('owner_queryset',owner_queryset)
                owner_dict = {}
                for owner in owner_queryset:
                    owner_dict['id'] = owner.id
                    owner_dict['equipment'] = owner.equipment.id
                    owner_dict['purchase_date'] = owner.purchase_date
                    owner_dict['price'] = owner.price
                    owner_dict['is_emi_available'] = owner.is_emi_available
                    if owner.is_emi_available:
                        emi_queryset = PmsMachinaryOwnerEmiDetails.objects.filter(
                            equipment_owner_details=owner,
                              equipment=data['id'],
                              is_deleted=False
                        )
                        #print('emi_queryset',emi_queryset)
                        emi_dict = {}
                        for emi in emi_queryset:
                            emi_dict['id'] = emi.id
                            emi_dict['equipment'] = emi.equipment.id
                            emi_dict['equipment_owner_details'] = emi.equipment_owner_details.id
                            emi_dict['amount'] = emi.amount
                            emi_dict['start_date'] = emi.start_date
                            emi_dict['no_of_total_installment'] = emi.no_of_total_installment

                        if emi_dict:
                            data['owner_emi_details'] = emi_dict
                            #print('owner_dict',owner_dict)
                if owner_dict:
                    data['owner_details'] = owner_dict
            else:
                contract_queryset = PmsMachinaryContractDetails.objects.filter(
                    equipment=data['id'],is_deleted=False)
                contract_dict = {}
                for contract in contract_queryset:
                    contract_dict['id'] = contract.id
                    contract_dict['equipment'] = contract.equipment.id
                    contract_dict['contractor_id'] = contract.contractor.id
                    contract_dict['contractor'] = contract.contractor.contact_person_name
                data['contract_details'] = contract_dict
        return response
class MachineriesDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsMachineries.objects.all()
    serializer_class = MachineriesDeleteSerializer

#::::::::::::::::: MECHINARY WORKING CATEGORY  :::::::::::::::#
class MachineriesWorkingCategoryAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsMachineriesWorkingCategory.objects.filter(is_deleted=False).order_by('-id')
    serializer_class= MachineriesWorkingCategoryAddSerializer
class MachineriesWorkingCategoryEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsMachineriesWorkingCategory.objects.all()
    serializer_class = MachineriesWorkingCategoryEditSerializer
class MachineriesWorkingCategoryDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsMachineriesWorkingCategory.objects.all()
    serializer_class = MachineriesWorkingCategoryDeleteSerializer

#::::::::::::::::: MECHINARY DETAILS DOCUMENT  :::::::::::::::#
class MachineriesDetailsDocumentAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsMachineriesDetailsDocument.objects.all()
    serializer_class = MachineriesDetailsDocumentAddSerializer
class MachineriesDetailsDocumentEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsMachineriesDetailsDocument.objects.all()
    serializer_class = MachineriesDetailsDocumentEditSerializer
class MachineriesDetailsDocumentDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsMachineriesDetailsDocument.objects.all()
    serializer_class = MachineriesDetailsDocumentDeleteSerializer
class MachineriesDetailsDocumentListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = MachineriesDetailsDocumentListSerializer
    def get_queryset(self):
        equipment_id = self.kwargs['equipment_id']
        queryset = PmsMachineriesDetailsDocument.objects.filter(equipment_id=equipment_id,is_deleted=False).order_by('-id')
        return queryset

#::::::::::::::: Pms Machinary Rented Type Master:::::::::::::::::::::#
class MachinaryRentedTypeMasterAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsMachinaryRentedTypeMaster.objects.filter(is_deleted=False).order_by('-id')
    serializer_class = MachinaryRentedTypeMasterAddSerializer
class MachinaryRentedTypeMasterEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsMachinaryRentedTypeMaster.objects.all()
    serializer_class = MachinaryRentedTypeMasterEditSerializer
class MachinaryRentedTypeMasterDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsMachinaryRentedTypeMaster.objects.all()
    serializer_class = MachinaryRentedTypeMasterDeleteSerializer

#:::::::::::: MECHINARY REPORTS ::::::::::::::::::::::::::::#
class MachineriesReportAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsProjectsMachinaryReport.objects.filter(is_deleted=False)
    serializer_class = MachineriesReportAddSerializer
    @response_modify_decorator_get_after_execution
    def get(self ,request, *args, **kwargs):
        project=self.request.query_params.get('project', None)
        machinary_list=[]
        if project:
            machinary=PmsProjectsMachinaryMapping.objects.filter(project=project)
            for e_machinary in machinary:
                machinary_report=PmsProjectsMachinaryReport.objects.filter(machine=e_machinary.machinary.id)
                for m_r in machinary_report:
                    machine_dict={
                        'id':m_r.id,
                        'machine':m_r.machine.id,
                        'date':m_r.date,
                        'opening_balance':m_r.opening_balance,
                        'cash_purchase':m_r.cash_purchase,
                        'diesel_transfer_from_other_site':m_r.diesel_transfer_from_other_site,
                        'total_diesel_available':m_r.total_diesel_available,
                        'total_diesel_consumed':m_r.total_diesel_consumed,
                        'diesel_balance':m_r.diesel_balance,
                        'diesel_consumption_by_equipment':m_r.diesel_consumption_by_equipment,
                        'other_consumption':m_r.other_consumption,
                        'miscellaneous_consumption':m_r.miscellaneous_consumption,
                        'opening_meter_reading':m_r.opening_meter_reading,
                        'closing_meter_reading':m_r.closing_meter_reading,
                        'running_km':m_r.running_km,
                        'running_hours':m_r.running_hours,
                        'purpose':m_r.purpose,
                        'last_pm_date':m_r.last_pm_date,
                        'next_pm_schedule':m_r.next_pm_schedule,
                        'difference_in_reading':m_r.difference_in_reading,
                        'hsd_average':m_r.hsd_average,
                        'standard_avg_of_hours':m_r.standard_avg_of_hours
                    }
                
                    machinary_list.append(machine_dict)
            return Response(machinary_list)
        else:
            response=super(MachineriesReportAddView, self).list(request, args, kwargs)
            return response
            

        

class MachineriesReportEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsProjectsMachinaryReport.objects.all()
    serializer_class = MachineriesReportEditSerializer