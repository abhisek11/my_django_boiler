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
from master.models import TMasterModuleRole
from users.models import TCoreUserDetail
from custom_decorator import *
from rest_framework.parsers import FileUploadParser
import os
from pms.custom_filter import *
from django.db.models import Q
from itertools import chain
#::::::::::::::: TENDER AND TENDER DOCUMENTS :::::::::::::::#
class TendersAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsTenders.objects.filter(is_deleted=False)
    serializer_class = TendersAddSerializer
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
    
    # @response_modify_decorator_post
    # def post(self, request, *args, **kwargs):
    #     return super().post(request, *args, **kwargs)

class TenderDocsAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = TenderDocumentAddSerializer
    queryset = PmsTenderDocuments.objects.filter(is_deleted=False)
class TenderDocsByTenderIdView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = TenderDocumentAddSerializer
    def get_queryset(self):
        tender_id = self.kwargs['tender_id']
        if tender_id:
            queryset = PmsTenderDocuments.objects.filter(tender_id=tender_id,
                                                         is_deleted=False).order_by('-created_at')
            return queryset

    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response

class TenderEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsTenders.objects.all()
    serializer_class = TenderEditSerializer

    # @response_modify_decorator_update
    # def update(self, request, *args, **kwargs):
    #     return super().update(request, *args, **kwargs)
    
class TenderDocsEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsTenderDocuments.objects.all()
    serializer_class = TenderDocsEditSerializer

class TenderDeleteByIdView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsTenders.objects.all()
    serializer_class = TenderDeleteSerializer

class TenderDocsDeleteByIdView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsTenderDocuments.objects.all()
    serializer_class = TenderDocumentDeleteSerializer

class TendersListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsTenders.objects.filter(is_deleted=False).order_by('-id')
    serializer_class = TendersListSerializer
    pagination_class = CSPageNumberPagination
    def get_queryset(self):
        filter = {}
        eligibility_dict={}
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        from_cost = self.request.query_params.get('from_cost', None)
        to_cost = self.request.query_params.get('to_cost', None)
        bidder_type=self.request.query_params.get('bidder_type',None)
        eligibility=self.request.query_params.get('eligibility',None)
        search=self.request.query_params.get('search',None)

        field_name=self.request.query_params.get('field_name',None)
        order_by=self.request.query_params.get('order_by',None)

        if field_name and order_by:

            if field_name=='tender_g_id' and order_by == 'asc':
                return self.queryset.filter(status=True,is_deleted=False).order_by('tender_g_id')
            elif field_name=='tender_g_id' and order_by == 'desc':
                return self.queryset.filter(status=True, is_deleted=False).order_by('-tender_g_id')
            elif field_name == 'created_at' and order_by == 'asc':
                return self.queryset.filter(status=True, is_deleted=False).order_by('created_at')
            elif field_name == 'created_at' and order_by == 'desc':
                return self.queryset.filter(status=True, is_deleted=False).order_by('-created_at')

            elif field_name == 'costing' and order_by == 'asc':
                #cost_list = PmsTenderInitialCosting.objects.filter(status=True, is_deleted=False).order_by('difference_in_budget')
                cost_list = PmsTenderInitialCosting.objects.filter(status=True, is_deleted=False).order_by('quoted_rate')
                #print('cost_list',cost_list)
                tender_c_list = list()
                for e_cost in cost_list:
                    print('e_cost',e_cost.quoted_rate)
                    tender_c_list.append(e_cost.tender.id)
                clauses = ' '.join(['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(tender_c_list)])
                ordering = 'CASE %s END' % clauses
                #print('ordering',ordering)
                return self.queryset.filter(is_deleted=False, id__in=tender_c_list, status=True).extra(select={'ordering': ordering}, order_by=('ordering',))
            elif field_name == 'costing' and order_by == 'desc':
                #cost_list = PmsTenderInitialCosting.objects.filter(status=True, is_deleted=False).order_by('-difference_in_budget')
                cost_list = PmsTenderInitialCosting.objects.filter(status=True, is_deleted=False).order_by('-quoted_rate')
                
                tender_c_list = list()
                for e_cost in cost_list:
                    tender_c_list.append(e_cost.tender.id)
                    # filter['id__in'] = tender_c_list
                clauses = ' '.join(['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(tender_c_list)])
                ordering = 'CASE %s END' % clauses
                return self.queryset.filter(is_deleted=False, id__in=tender_c_list, status=True).extra(
                    select={'ordering': ordering}, order_by=('ordering',))
                tender_query = self.queryset.filter(~Q(id__in=costing_query))
                total = list(chain(costing_query, tender_query))
                return total
                #return self.queryset.filter(is_deleted=False,id__in=tender_c_list,status=True)


        if search:
            queryset= self.queryset.filter(is_deleted=False,tender_g_id=search,status=True)
            return queryset

        if start_date and end_date:
            start_object = datetime.strptime(start_date, '%Y-%m-%d')
            end_object = datetime.strptime(end_date, '%Y-%m-%d')
            filter['created_at__range'] = (start_object, end_object)

        if from_cost and to_cost:
            #cost_list=PmsTenderInitialCosting.objects.filter(difference_in_budget__range=(from_cost,to_cost),status=True,is_deleted=False)
            cost_list=PmsTenderInitialCosting.objects.filter(quoted_rate__range=(from_cost,to_cost),status=True,is_deleted=False)
            tender_c_list=list()
            # print('cost_list',cost_list)
            for e_cost in cost_list:
                tender_c_list.append(e_cost.tender.id)
                filter['id__in']=tender_c_list

        if bidder_type:
            pmstender_list = PmsTenderBidderType.objects.filter(bidder_type=bidder_type,status=True,is_deleted=False)
            # print('pmstender_list',pmstender_list)
            tender_f_id = list()
            for e_pmstender_list in pmstender_list:
                tender_f_id.append(e_pmstender_list.tender.id)
                # print('e_pmstender_list',e_pmstender_list.__dict__)
            filter['id__in']=tender_f_id

        if eligibility:
            eligibility_list = eligibility.split(',')
            # print('eligibility_list',eligibility_list)
            eligibility_dict['type__in']=eligibility_list
            eligibility_types_list=PmsTenderEligibility.objects.filter(**eligibility_dict,eligibility_status=True,status=True,is_deleted=False)
            # print('eligibility_types_list',eligibility_types_list)
            e_list=list()
            # e_types_list=list()
            for e_eligibility in eligibility_types_list:
                # print('e_eligibility',e_eligibility)
                e_list.append(e_eligibility.tender.id)
                filter['id__in']=e_list

        if filter:
            queryset = self.queryset.filter(is_deleted=False, **filter,status=True)
            # print('queryset',queryset.query)
            return queryset

        else:
            queryset = self.queryset.filter(is_deleted=False,status=True)
            return queryset

    @response_modify_decorator_list_or_get_after_execution_for_pagination
    def get(self, request, *args, **kwargs):
        #print('checkccccccccccccccc')
        response=super(TendersListView,self).get(self, request, args, kwargs)
        # print("response",response.data)
        for data in response.data['results']:
            document_details = list()
            tender_document = PmsTenderSurveySitePhotos.objects.filter(
                tender=int(data['id']),
                status=True, is_deleted=False)
            for document in tender_document:
                data1 = {
                    "id": int(document.id),
                    "tender": int(document.tender.id),
                    "latitude": document.latitude,
                    "longitude": document.longitude,
                    "address": document.address,
                    "document_name": document.document_name,
                    "document": request.build_absolute_uri(document.document.url),
                }
                document_details.append(data1)
            data['site_photos'] = document_details

            bidder_details=PmsTenderBidderType.objects.filter(tender=data['id']).count()
            # print('bidder_details',bidder_details)
            if bidder_details:
                bidder_type_details=PmsTenderBidderType.objects.only('bidder_type').get(tender=data['id']).bidder_type
                # print('bidder_type_details',bidder_type_details)
                data['bidder_type']=bidder_type_details

            initial_cost=PmsTenderInitialCosting.objects.filter(tender=data['id']).count()
            if initial_cost:
                #initial_cost_details=PmsTenderInitialCosting.objects.only('difference_in_budget').get(tender=data['id']).difference_in_budget
                initial_cost_details=PmsTenderInitialCosting.objects.only('quoted_rate').get(tender=data['id']).quoted_rate
                
                data['initial_costing']=initial_cost_details

            eligibility=PmsTenderEligibility.objects.filter(tender=data['id'])
            # print('eligibility',eligibility)
            if eligibility:
                flag=1
                for each_eligibility in eligibility:
                    # print('each_eligibility',each_eligibility.__dict__)
                    if each_eligibility.__dict__['eligibility_status'] == False:
                        flag=0
                    if each_eligibility.__dict__['type']== 'special' and  each_eligibility.__dict__['eligibility_status']== False:
                        flag=1

                if flag == 1:
                    data['eligibility']="Yes"
                else:
                    data['eligibility'] = "No"

            tender_approval=PmsTenderApproval.objects.filter(tender=data['id']).count()
            # print('tender_approval',tender_approval)
            if tender_approval:
                tender_app_details=PmsTenderApproval.objects.only('is_approved').get(tender=data['id']).is_approved
                # print('tender_app_details',tender_app_details)
                data["approval"]=tender_app_details
            tender_status=PmsTenderStatus.objects.filter(tender=data['id']).count()
            if tender_status:
                tender_satus_details=PmsTenderStatus.objects.only('is_awarded').get(tender=data['id']).is_awarded
                data['tender_status']=tender_satus_details

        return response

    

class TendersListCountView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsTenders.objects.filter(is_deleted=False)
    serializer_class = TendersListSerializer
    def get(self,request,*args,**kwargs):
        response=super(TendersListCountView,self).get(self, request, args, kwargs)
        # print('response',response.data)
        c=0
        dic = {}
        active_tender = PmsTenders.objects.filter(status=True, is_deleted=False).count()
        # print('active_tender',active_tender)
        total_tender=PmsTenders.objects.all().count()
        # print('total_tender',total_tender)
        for data in response.data:
            awarded_tender=PmsTenderStatus.objects.filter(tender=data['id'],is_awarded=True,is_deleted=False,status=True).count()
            if awarded_tender == 1:
                c=c+1
        # print('awarded_tender_count',c)


        dic={'awarded_tender_count':c,
             'active_tender_count':active_tender,
             'total_tender_count':total_tender}

        data_dict = {}
        data_dict['result'] = dic
        if response.data:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_SUCCESS
        elif len(response.data) == 0:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_NO_DATA
        else:
            data_dict['request_status'] = 0
            data_dict['msg'] = settings.MSG_ERROR
        dic = data_dict

        return Response(dic)

class ProjectsListWPView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsProjects.objects.filter(is_deleted=False).order_by('-id')
    serializer_class=ProjectsListSerializer
    def get_queryset(self):
        # print('sdgfsdfsd')
        filter = {}
        start_date = self.request.query_params.get('start_date', None)
        # print("start_date",start_date)
        end_date = self.request.query_params.get('end_date', None)
        site_location = self.request.query_params.get('site_location', None)

        field_name = self.request.query_params.get('field_name', None)
        order_by = self.request.query_params.get('order_by', None)

        search = self.request.query_params.get('search', None)

        if search:
            queryset= self.queryset.filter(is_deleted=False,project_g_id=search,status=True)
            return queryset

        if field_name and order_by:
            if field_name=='tender_g_id' and order_by == 'asc':
                return self.queryset.filter(status=True,is_deleted=False).order_by('tender__tender_g_id')
            elif field_name=='tender_g_id' and order_by == 'desc':
                return self.queryset.filter(status=True, is_deleted=False).order_by('-tender__tender_g_id')
            elif field_name == 'project_g_id' and order_by == 'asc':
                return self.queryset.filter(status=True, is_deleted=False).order_by('project_g_id')
            elif field_name == 'project_g_id' and order_by == 'desc':
                return self.queryset.filter(status=True, is_deleted=False).order_by('-project_g_id')
            elif field_name == 'start_date' and order_by == 'asc':
                return self.queryset.filter(status=True, is_deleted=False).order_by('start_date')
            elif field_name == 'start_date' and order_by == 'desc':
                return self.queryset.filter(status=True, is_deleted=False).order_by('-start_date')
            elif field_name == 'end_date' and order_by == 'asc':
                return self.queryset.filter(status=True, is_deleted=False).order_by('end_date')
            elif field_name == 'end_date' and order_by == 'desc':
                return self.queryset.filter(status=True, is_deleted=False).order_by('-end_date')

        if start_date and end_date:
            # print("hjvgfa")
            start_object = datetime.strptime(start_date, '%Y-%m-%d')
            end_object = datetime.strptime(end_date, '%Y-%m-%d')
            filter['start_date__range'] = (start_object, end_object)
        if site_location:
            site_location_list = site_location.split(',')
            # print('site_location_list',site_location_list)
            filter['site_location__in']=site_location_list

        if filter:
            queryset = self.queryset.filter(is_deleted=False, status=True, **filter)
            # print('queryset',queryset.query)
            return queryset

        else:
            queryset = self.queryset.filter(is_deleted=False, status=True)
            return queryset

    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response

class TendersArchiveView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsTenders.objects.all()
    serializer_class = TendersArchiveSerializer

class TendersArchiveListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsTenders.objects.filter(status=False).order_by('-id')
    serializer_class = TendersArchiveListSerializer
    pagination_class = CSPageNumberPagination
    def get_queryset(self):
        filter = {}
        eligibility_dict={}
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        from_cost = self.request.query_params.get('from_cost', None)
        to_cost = self.request.query_params.get('to_cost', None)
        bidder_type=self.request.query_params.get('bidder_type',None)
        eligibility=self.request.query_params.get('eligibility',None)
        search=self.request.query_params.get('search',None)

        field_name=self.request.query_params.get('field_name',None)
        order_by=self.request.query_params.get('order_by',None)

        if field_name and order_by:

            if field_name=='tender_g_id' and order_by == 'asc':
                return self.queryset.filter(status=False).order_by('tender_g_id')
            elif field_name=='tender_g_id' and order_by == 'desc':
                return self.queryset.filter(status=False).order_by('-tender_g_id')
            elif field_name == 'created_at' and order_by == 'asc':
                return self.queryset.filter(status=False).order_by('created_at')
            elif field_name == 'created_at' and order_by == 'desc':
                return self.queryset.filter(status=False).order_by('-created_at')

            elif field_name == 'costing' and order_by == 'asc':
                cost_list = PmsTenderInitialCosting.objects.filter(status=False).order_by('difference_in_budget')
                #print('cost_list',cost_list)
                tender_c_list = list()
                for e_cost in cost_list:
                    # print('e_cost',e_cost.difference_in_budget)
                    tender_c_list.append(e_cost.tender.id)
                clauses = ' '.join(['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(tender_c_list)])
                ordering = 'CASE %s END' % clauses
                #print('ordering',ordering)
                return self.queryset.filter(id__in=tender_c_list, status=False).extra(select={'ordering': ordering}, order_by=('ordering',))
            elif field_name == 'costing' and order_by == 'desc':
                cost_list = PmsTenderInitialCosting.objects.filter(status=False).order_by('-difference_in_budget')
                tender_c_list = list()
                for e_cost in cost_list:
                    tender_c_list.append(e_cost.tender.id)
                    # filter['id__in'] = tender_c_list
                clauses = ' '.join(['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(tender_c_list)])
                ordering = 'CASE %s END' % clauses
                return self.queryset.filter(id__in=tender_c_list, status=False).extra(
                    select={'ordering': ordering}, order_by=('ordering',))
                #return self.queryset.filter(is_deleted=False,id__in=tender_c_list,status=True)


        if search:
            queryset= self.queryset.filter(tender_g_id=search,status=False)
            return queryset

        if start_date and end_date:
            start_object = datetime.strptime(start_date, '%Y-%m-%d')
            end_object = datetime.strptime(end_date, '%Y-%m-%d')
            filter['created_at__range'] = (start_object, end_object)

        if from_cost and to_cost:
            cost_list=PmsTenderInitialCosting.objects.filter(difference_in_budget__range=(from_cost,to_cost),status=False)
            tender_c_list=list()
            # print('cost_list',cost_list)
            for e_cost in cost_list:
                tender_c_list.append(e_cost.tender.id)
                filter['id__in']=tender_c_list

        if bidder_type:
            pmstender_list = PmsTenderBidderType.objects.filter(bidder_type=bidder_type,status=False)
            # print('pmstender_list',pmstender_list)
            tender_f_id = list()
            for e_pmstender_list in pmstender_list:
                tender_f_id.append(e_pmstender_list.tender.id)
                # print('e_pmstender_list',e_pmstender_list.__dict__)
            filter['id__in']=tender_f_id

        if eligibility:
            eligibility_list = eligibility.split(',')
            # print('eligibility_list',eligibility_list)
            eligibility_dict['type__in']=eligibility_list
            eligibility_types_list=PmsTenderEligibility.objects.filter(**eligibility_dict,eligibility_status=True,status=False)
            # print('eligibility_types_list',eligibility_types_list)
            e_list=list()
            # e_types_list=list()
            for e_eligibility in eligibility_types_list:
                # print('e_eligibility',e_eligibility)
                e_list.append(e_eligibility.tender.id)
                filter['id__in']=e_list

        if filter:
            queryset = self.queryset.filter(**filter,status=False)
            # print('queryset',queryset.query)
            return queryset

        else:
            queryset = self.queryset.filter(status=False)
            return queryset
    def get(self, request, *args, **kwargs):
        response = super(TendersArchiveListView, self).get(self, request, args, kwargs)
        # print('response',response.data)
        for data in response.data['results']:
            document_details = list()
            tender_document = PmsTenderSurveySitePhotos.objects.filter(
                tender=int(data['id']),
                status=False)
            for document in tender_document:
                data1 = {
                    "id": int(document.id),
                    "tender": int(document.tender.id),
                    "latitude": document.latitude,
                    "longitude": document.longitude,
                    "address": document.address,
                    "document_name": document.document_name,
                    "document": request.build_absolute_uri(document.document.url),
                }
                document_details.append(data1)
            data['site_photos'] = document_details

            bidder_details = PmsTenderBidderType.objects.filter(tender=data['id'],status=False).count()
            # print('bidder_details',bidder_details)
            if bidder_details:
                bidder_type_details = PmsTenderBidderType.objects.only('bidder_type').get(tender=data['id'],status=False).bidder_type
                # print('bidder_type_details',bidder_type_details)
                data['bidder_type'] = bidder_type_details

            initial_cost = PmsTenderInitialCosting.objects.filter(tender=data['id'],status=False).count()
            if initial_cost:
                initial_cost_details = PmsTenderInitialCosting.objects.only('difference_in_budget').get(
                    tender=data['id'],status=False).difference_in_budget
                data['initial_costing'] = initial_cost_details

            eligibility = PmsTenderEligibility.objects.filter(tender=data['id'],status=False)
            # print('eligibility',eligibility)
            if eligibility:
                flag = 1
                for each_eligibility in eligibility:
                    # print('each_eligibility',each_eligibility.__dict__)
                    if each_eligibility.__dict__['eligibility_status'] == False:
                        flag = 0
                    if each_eligibility.__dict__['type'] == 'special' and each_eligibility.__dict__[
                        'eligibility_status'] == False:
                        flag = 1

                if flag == 1:
                    data['eligibility'] = "Yes"
                else:
                    data['eligibility'] = "No"

            tender_approval = PmsTenderApproval.objects.filter(tender=data['id'],status=False).count()
            # print('tender_approval',tender_approval)
            if tender_approval:
                tender_app_details = PmsTenderApproval.objects.only('is_approved').get(tender=data['id'],status=False).is_approved
                # print('tender_app_details',tender_app_details)
                data["approval"] = tender_app_details
            tender_status = PmsTenderStatus.objects.filter(tender=data['id'],status=False).count()
            if tender_status:
                tender_satus_details = PmsTenderStatus.objects.only('is_awarded').get(tender=data['id'],status=False).is_awarded
                data['tender_status'] = tender_satus_details

        return response


#::::::::::::::: TENDER  BIDDER TYPE :::::::::::::::#
class PartnersAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = PartnersAddSerializer
    queryset = PmsTenderPartners.objects.filter(is_deleted=False,status=True)
class PartnersEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = PartnersEditSerializer
    queryset = PmsTenderPartners.objects.all()
class PartnersDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = PartnersDeleteSerializer
    queryset = PmsTenderPartners.objects.all()
class TendorBidderTypeAddView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = TendorBidderTypeAddSerializer
class TendorBidderTypeByTenderIdView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    #serializer_class = TendorBidderTypeByTenderIdSerializer
    
    def get(self, request, *args, **kwargs):
        #print('self',self)
        tender_id = self.kwargs['tender_id']
        data_dict={}
        response = {}
        if tender_id:
            tender_bidder_data = PmsTenderBidderType.objects.filter(tender=tender_id)
            print('tender_bidder_data',tender_bidder_data)
            if tender_bidder_data:
                for each_tender_bidder_data in tender_bidder_data:
                    partners = []
                    partners_m_details = PmsTenderBidderTypePartnerMapping.objects.\
                        filter(tender_bidder_type=each_tender_bidder_data.id)
                    print('partners_m_details',partners_m_details)
                    if partners_m_details:
                        for e_partners_m_details in partners_m_details:
                            partner_d = {
                                "tendor_vendor_id":e_partners_m_details.tender_partner.id
                            }
                            partners.append(e_partners_m_details.tender_partner.id)
                    if each_tender_bidder_data.updated_by:
                        updated_by = each_tender_bidder_data.updated_by.id
                    else:
                        updated_by = ''

                    response = {
                        "id":each_tender_bidder_data.id,
                        "bidder_type":each_tender_bidder_data.bidder_type,
                        "type_of_partner": each_tender_bidder_data.type_of_partner,
                        "responsibility": each_tender_bidder_data.responsibility,
                        "profit_sharing_ratio_actual_amount": each_tender_bidder_data.profit_sharing_ratio_actual_amount,
                        "profit_sharing_ratio_tender_specific_amount": each_tender_bidder_data.profit_sharing_ratio_tender_specific_amount,
                        "updated_by":updated_by,
                        "partners":partners
                    }

            data_dict['result'] = response
            if response:
                data_dict['request_status'] = 1
                data_dict['msg'] = settings.MSG_SUCCESS
                data_dict['result'] = response
            elif len(response) == 0:
                data_dict['request_status'] = 1
                data_dict['msg'] = settings.MSG_NO_DATA
                data_dict['result'] = None
                
            else:
                data_dict['request_status'] = 0
                data_dict['msg'] = settings.MSG_ERROR
                data_dict['result'] = None
                
            response = data_dict
            return Response(response)

         
    def update(self, request, *args, **kwargs):
        tender_id = self.kwargs['tender_id']
        #print('request',request.data['bidder_type'])
        try:
            if tender_id:
                tender_bidder_type_partner_mapping_list = []
                pmsTenderBidderType = PmsTenderBidderType.objects.filter(tender=tender_id)
                print('pmsTenderBidderType', pmsTenderBidderType)
                if pmsTenderBidderType:
                    tender_bidder_data = PmsTenderBidderType.objects.get(tender=tender_id)
                    with transaction.atomic():
                        if request.data['bidder_type'] == "joint_venture":
                            tender_bidder_data.bidder_type = request.data['bidder_type']
                            tender_bidder_data.type_of_partner=request.data['type_of_partner']
                            tender_bidder_data.responsibility=request.data['responsibility']
                            tender_bidder_data.profit_sharing_ratio_actual_amount=request.data['profit_sharing_ratio_actual_amount']
                            tender_bidder_data.profit_sharing_ratio_tender_specific_amount=request.data['profit_sharing_ratio_tender_specific_amount']
                            tender_bidder_data.updated_by=self.request.user
                            tender_bidder_data.save()
                            xyz=PmsTenderBidderTypePartnerMapping.objects.filter(tender_bidder_type_id=tender_bidder_data.id).delete()
                            #print('xyz',xyz)
                            for partner in request.data['partners']:
                                #print('partner',partner)
                                request_dict = {
                                    "tender_bidder_type_id": str(tender_bidder_data.id),
                                    "tender_partner_id": int(partner),
                                    "status": True,
                                    "created_by": self.request.user,
                                    "owned_by": self.request.user
                                }
                                tender_bidder_type_partner_m = PmsTenderBidderTypePartnerMapping.objects.create(
                                    **request_dict)
                            response = {
                                'id': tender_bidder_data.id,
                                'tender': tender_bidder_data.tender.id,
                                'bidder_type': tender_bidder_data.bidder_type,
                                'type_of_partner':  tender_bidder_data.type_of_partner,
                                'responsibility': tender_bidder_data.responsibility,
                                'profit_sharing_ratio_actual_amount':  tender_bidder_data.profit_sharing_ratio_actual_amount,
                                'profit_sharing_ratio_tender_specific_amount':  tender_bidder_data.profit_sharing_ratio_tender_specific_amount,
                                'partners': request.data['partners']
                            }
                            return Response(response)
                        else:
                            tender_bidder_data.bidder_type = request.data['bidder_type']
                            tender_bidder_data.responsibility = request.data['responsibility']
                            tender_bidder_data.updated_by = self.request.user
                            tender_bidder_data.save()
                            response = {
                                'id': tender_bidder_data.id,
                                'tender': tender_bidder_data.tender.id,
                                'bidder_type': tender_bidder_data.bidder_type,
                                'responsibility': tender_bidder_data.responsibility,
                            }
                            return Response(response)
                else:
                    with transaction.atomic():
                        if request.data['bidder_type'] == "joint_venture":
                            bidder_type_details = PmsTenderBidderType.objects.create(
                                tender_id = request.data['tender'],
                                bidder_type = request.data['bidder_type'],
                                type_of_partner = request.data['type_of_partner'],
                                responsibility=request.data['responsibility'],
                                profit_sharing_ratio_actual_amount=request.data['profit_sharing_ratio_actual_amount'],
                                profit_sharing_ratio_tender_specific_amount=request.data['profit_sharing_ratio_tender_specific_amount'],
                                created_by = self.request.user,
                                owned_by = self.request.user,
                                status = True
                            )
                            for partner in request.data['partners']:
                                #print('partner',partner)
                                request_dict = {
                                    "tender_bidder_type_id": int(bidder_type_details.id),
                                    "tender_partner_id": int(partner),
                                    "status": True,
                                    "created_by": self.request.user,
                                    "owned_by": self.request.user
                                }
                                tender_bidder_type_partner_m = PmsTenderBidderTypePartnerMapping.objects.create(
                                    **request_dict)
                            response = {
                                'id': int(bidder_type_details.id),
                                'tender': int(bidder_type_details.tender.id),
                                'bidder_type': bidder_type_details.bidder_type,
                                'type_of_partner':  bidder_type_details.type_of_partner,
                                'responsibility': bidder_type_details.responsibility,
                                'profit_sharing_ratio_actual_amount':  bidder_type_details.profit_sharing_ratio_actual_amount,
                                'profit_sharing_ratio_tender_specific_amount':  bidder_type_details.profit_sharing_ratio_tender_specific_amount,
                                'partners': request.data['partners']
                            }
                            return Response(response)
                        else:

                            bidder_type_details = PmsTenderBidderType.objects.create(
                                tender_id = request.data['tender'],
                                bidder_type=request.data['bidder_type'],
                                responsibility=request.data['responsibility'],
                                created_by=self.request.user,
                                owned_by=self.request.user,
                                status = True
                            )
                            #print('bidder_type_details',bidder_type_details)
                            response = {
                                'id': int(bidder_type_details.id),
                                'tender': int(bidder_type_details.tender.id),
                                'bidder_type': bidder_type_details.bidder_type,
                                'responsibility': bidder_type_details.responsibility,
                            }
                            return Response(response)
        except Exception as e:
            raise e
class TendorBidderTypeEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsTenderBidderType.objects.all()
    serializer_class = TendorBidderTypeEditSerializer
class TendorBidderTypeDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsTenderBidderType.objects.all()
    serializer_class = TendorBidderTypeDeleteSerializer

#::::::::::::::: TENDER  ELIGIBILITY :::::::::::::::#
class PmsTenderEligibilityFieldsByTypeListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = PmsTenderEligibilityFieldsByTypeEditSerializer
    queryset = PmsTenderEligibilityFieldsByType.objects.all()
    def get_queryset(self):
        tender_id = self.kwargs['tender_id']
        eligibility_type = self.kwargs['eligibility_type']
        return self.queryset.filter(tender_id=tender_id, tender_eligibility__type=eligibility_type,
                                    status=True, is_deleted=False)

    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
class PmsTenderEligibilityAdd(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = PmsTenderEligibilityAddSerializer
    queryset = PmsTenderEligibility.objects.all()
class PmsTenderEligibilityFieldsByTypeEdit(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = PmsTenderEligibilityFieldsByTypeEditSerializer
    queryset = PmsTenderEligibilityFieldsByType.objects.all()
class PmsTenderNotEligibilityReasonAdd(MultipleFieldLookupMixin, generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = PmsTenderNotEligibilityReasonAddSerializer
    queryset = PmsTenderEligibility.objects.filter(status=True, is_deleted=False)
    lookup_fields = ("tender_id", "type")
    def get(self,request,*args,**kwargs):
        #print('get')
        tender_id = self.kwargs['tender_id']
        return Response({
                    "tender": int(tender_id),
                    "ineligibility_reason": "",
                    "eligibility_status": True
                })
#::::::::::::::: TENDER SURVEY SITE PHOTOS:::::::::::::::#
class TenderSurveySitePhotosAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsTenderSurveySitePhotos.objects.all()
    serializer_class =TenderSurveySitePhotosAddSerializer
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
class TenderSurveySitePhotosEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsTenderSurveySitePhotos.objects.all()
    serializer_class =TenderSurveySitePhotosEditSerializer
class TenderSurveySitePhotosListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsTenderSurveySitePhotos.objects.all()
    serializer_class =TenderSurveySitePhotosListSerializer
    def get_queryset(self):
        tender_id = self.kwargs['tender_id']
        queryset = PmsTenderSurveySitePhotos.objects.filter(tender_id=tender_id, status=True).order_by('-id')
        return queryset
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
class TenderSurveySitePhotosDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsTenderSurveySitePhotos.objects.all()
    serializer_class =TenderSurveySitePhotosDeleteSerializer

#::::::::::::::: TENDER SURVEY COORDINATE :::::::::::::::#
class TenderSurveyMaterialsExternalUserMappingAddView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsExternalUsersExtraDetailsTenderMapping.objects.filter(is_deleted=False)
    serializer_class = TenderSurveyMaterialsExternalUserMappingAddSerializer
class TenderSurveyMaterialsExternalUserMappingAddFAndroidView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsExternalUsersExtraDetailsTenderMapping.objects.filter(is_deleted=False)
    serializer_class = TenderSurveyMaterialsExternalUserMappingAddFAndroidSerializer
class TenderSurveyMaterialsExternalUserMappingListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsExternalUsersExtraDetailsTenderMapping.objects.filter(is_deleted=False)
    serializer_class = TenderSurveyMaterialsExternalUserMappingListSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('tender','external_user_type','tender_survey_material')
    @response_modify_decorator_list
    def list(self,request, *args, **kwargs):
        return response
class TenderSurveyMaterialsExternalUserMappingDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsExternalUsersExtraDetailsTenderMapping.objects.all()
    serializer_class =TenderSurveyMaterialsExternalUserMappingDeleteSerializer
class TenderSurveyMaterialsExternalUserMappingDocumentAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsExternalUsersExtraDetailsTenderMappingDocument.objects.filter(status=True,is_deleted=False)
    serializer_class =TenderSurveyMaterialsExternalUserMappingDocumentAddSerializer
class TenderSurveyLocationAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsTenderSurveyCoordinatesSiteCoordinate.objects.all()
    serializer_class =TenderSurveyLocationAddSerializer
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
class TenderSurveyLocationListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsTenderSurveyCoordinatesSiteCoordinate.objects.all()
    serializer_class =TenderSurveyLocationListSerializer
    def get_queryset(self):
        tender_id=self.kwargs['tender_id']
        queryset = PmsTenderSurveyCoordinatesSiteCoordinate.objects.filter(
            tender_id=tender_id,status=True,is_deleted=False)
        return queryset
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
class TenderSurveyLocationEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsTenderSurveyCoordinatesSiteCoordinate.objects.all()
    serializer_class =TenderSurveyLocationEditSerializer
class TenderSurveyLocationDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsTenderSurveyCoordinatesSiteCoordinate.objects.all()
    serializer_class =TenderSurveyLocationDeleteSerializer

#:::::::::::::::::::::: MATERIAL TYPE MASTER:::::::::::::::::::::::::::#
# class MaterialTypeMasterAddView(generics.ListCreateAPIView):
#     permission_classes = [IsAuthenticated]
#     authentication_classes = [TokenAuthentication]
#     queryset = MaterialTypeMaster.objects.all()
#     serializer_class = MaterialTypeMasterAddSerializer

#     @response_modify_decorator_get
#     def get(self, request, *args, **kwargs):
#         return response


# class MaterialTypeMasterEditView(generics.RetrieveUpdateAPIView):
# 	permission_classes = [IsAuthenticated]
# 	authentication_classes = [TokenAuthentication]
# 	queryset = MaterialTypeMaster.objects.all()
# 	serializer_class = MaterialTypeMasterEditSerializer


# class MaterialTypeMasterDeleteView(generics.RetrieveUpdateAPIView):
# 	permission_classes = [IsAuthenticated]
# 	authentication_classes = [TokenAuthentication]
# 	queryset = MaterialTypeMaster.objects.all()
# 	serializer_class = MaterialTypeMasterDeleteSerializer


#::::::::::: TENDER SURVEY METERIAL ::::::::::::::::::::#
class MaterialsAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = Materials.objects.filter(is_deleted=False)
    serializer_class=MaterialsAddSerializer
    '''
        Filter Added By Rupam Hazra on 20.01.2020 for tender servey
    '''
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_master', 'is_crusher']

class AssetsExcelFileAddView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    @response_modify_decorator_post  
    def post(self, request, format=None):
        try:
            document = request.data['document']
            # print('document',document)
            data=pd.read_excel(document,converters={'Material Code':str})
            data = data.replace(np.nan,'',regex=True) 
            # print('data',data)
            unit_filter={}
            logdin_user_id = self.request.user.id
            total_result={}
            blank_mat_code_list=[]
            with transaction.atomic():
                for index, row in data.iterrows():
                    # print('row',row['Material Name'])
                    if row['Material Code'] == '':
                        blank_mat_code_dict={
                            'material_name':row['Material Name'],
                            'material_code':row['Material Code'],
                            'description':row['Description'],
                            'unit':row['Unit']
                        }
                        blank_mat_code_list.append(blank_mat_code_dict)
                    else:
                        if row['Unit']:
                            unit_det=TCoreUnit.objects.filter(c_name=(row['Unit']).lower(),c_is_deleted=False)
                            if unit_det:
                                for det in unit_det:
                                    unit_filter['unit_id']=det.id
                                    # print('unit_filter',unit_filter)
                            else:
                                unit_entry,created=TCoreUnit.objects.get_or_create(c_name=row['Unit'],
                                                                                c_created_by_id=logdin_user_id,
                                                                                c_owned_by_id=logdin_user_id
                                                                                    )
                                # print('unit_entry',unit_entry)
                                unit_filter['unit_id']=unit_entry.__dict__['id']
                                # print('unit_filter',unit_filter)
                        else:
                            unit_filter['unit_id']=None

                        material_name=row['Material Name'] if row['Material Name'] else ''
                        description=row['Description'] if row['Description'] else ''
                        if row['Material Code']:
                            material_det=Materials.objects.filter(mat_code=row['Material Code'],is_deleted=False).update(type_code='MAT002')
                            # materialdet=Materials.objects.filter(mat_code=row['Material Code'],is_deleted=False).count()
                            # print('materialdet',materialdet)
                        #     if material_det:
                        #         for mat in material_det:
                        #             unit_filter['material_id']=mat.id
                        #     else:
                        #         material_entry,created=Materials.objects.get_or_create(mat_code=row['Material Code'],
                        #                                                             type_code='MAT002',
                        #                                                             name=material_name,
                        #                                                             description=description,
                        #                                                             created_by_id=logdin_user_id,
                        #                                                             owned_by_id=logdin_user_id
                        #                                                             )
                        #         # print('material_entry',material_entry)
                        #         unit_filter['material_id']=material_entry.__dict__['id']
                        #         # print('unit_filter',unit_filter)
                        # existing_mapping=MaterialsUnitMapping.objects.filter(**unit_filter).count()
                        # print('existing_mapping',existing_mapping)
                        # if existing_mapping == 0:
                        #     material_unit_mapping=MaterialsUnitMapping.objects.create(**unit_filter,
                        #                                                             created_by_id=logdin_user_id,
                        #                                                             owned_by_id=logdin_user_id
                        #                                                             )


                        total_result['blank_material_code_list']=blank_mat_code_list  

                return Response(total_result)
        except Exception as e:
            raise APIException({'msg':settings.MSG_ERROR,
                                'error':e,
                                "request_status": 0
                                })
class ConsumablesExcelFileAddView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    @response_modify_decorator_post  
    def post(self, request, format=None):
        try:
            document = request.data['document']
            # print('document',document)
            data=pd.read_excel(document,converters={'Material Code':str})
            data = data.replace(np.nan,'',regex=True) 
            # print('data',data)
            unit_filter={}
            logdin_user_id = self.request.user.id
            total_result={}
            blank_mat_code_list=[]
            with transaction.atomic():
                for index, row in data.iterrows():
                    # print('row',row['Material Name'])
                    if row['Material Code'] == '':
                        blank_mat_code_dict={
                            'material_name':row['Material Name'],
                            'material_code':row['Material Code'],
                            'description':row['Description'],
                            'unit':row['Unit']
                        }
                        blank_mat_code_list.append(blank_mat_code_dict)
                    else:
                        if row['Unit']:
                            unit_det=TCoreUnit.objects.filter(c_name=(row['Unit']).lower(),c_is_deleted=False)
                            if unit_det:
                                for det in unit_det:
                                    unit_filter['unit_id']=det.id
                                    # print('unit_filter',unit_filter)
                            else:
                                unit_entry,created=TCoreUnit.objects.get_or_create(c_name=row['Unit'],
                                                                                c_created_by_id=logdin_user_id,
                                                                                c_owned_by_id=logdin_user_id
                                                                                    )
                                # print('unit_entry',unit_entry)
                                unit_filter['unit_id']=unit_entry.__dict__['id']
                                # print('unit_filter',unit_filter)
                        else:
                            unit_filter['unit_id']=None

                        material_name=row['Material Name'] if row['Material Name'] else ''
                        description=row['Description'] if row['Description'] else ''
                        if row['Material Code']:
                            material_det=Materials.objects.filter(mat_code=row['Material Code'],is_deleted=False).update(type_code='MAT005')
                        #     materialdet=Materials.objects.filter(mat_code=row['Material Code'],is_deleted=False).count()
                        #     print('materialdet',materialdet)
                        #     if material_det:
                        #         for mat in material_det:
                        #             unit_filter['material_id']=mat.id
                        #     else:
                        #         material_entry,created=Materials.objects.get_or_create(mat_code=row['Material Code'],
                        #                                                             type_code='MAT005',
                        #                                                             name=material_name,
                        #                                                             description=description,
                        #                                                             created_by_id=logdin_user_id,
                        #                                                             owned_by_id=logdin_user_id
                        #                                                             )
                        #         # print('material_entry',material_entry)
                        #         unit_filter['material_id']=material_entry.__dict__['id']
                        #         # print('unit_filter',unit_filter)
                        # existing_mapping=MaterialsUnitMapping.objects.filter(**unit_filter).count()
                        # print('existing_mapping',existing_mapping)
                        # if existing_mapping == 0:
                        #     material_unit_mapping=MaterialsUnitMapping.objects.create(**unit_filter,
                        #                                                             created_by_id=logdin_user_id,
                        #                                                             owned_by_id=logdin_user_id
                        #                                                             )


                        total_result['blank_material_code_list']=blank_mat_code_list  

                return Response(total_result)
        except Exception as e:
            raise APIException({'msg':settings.MSG_ERROR,
                                'error':e,
                                "request_status": 0
                                })
class ElectricalExcelFileAddView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    @response_modify_decorator_post  
    def post(self, request, format=None):
        try:
            document = request.data['document']
            # print('document',document)
            data=pd.read_excel(document,converters={'Material Code':str})
            data = data.replace(np.nan,'',regex=True) 
            # print('data',data)
            unit_filter={}
            logdin_user_id = self.request.user.id
            total_result={}
            blank_mat_code_list=[]
            with transaction.atomic():
                for index, row in data.iterrows():
                    # print('row',row['Material Name'])
                    if row['Material Code'] == '':
                        blank_mat_code_dict={
                            'material_name':row['Material Name'],
                            'material_code':row['Material Code'],
                            'description':row['Description'],
                            'unit':row['Unit']
                        }
                        blank_mat_code_list.append(blank_mat_code_dict)
                    else:
                        if row['Unit']:
                            unit_det=TCoreUnit.objects.filter(c_name=(row['Unit']).lower(),c_is_deleted=False)
                            if unit_det:
                                for det in unit_det:
                                    unit_filter['unit_id']=det.id
                                    # print('unit_filter',unit_filter)
                            else:
                                unit_entry,created=TCoreUnit.objects.get_or_create(c_name=row['Unit'],
                                                                                c_created_by_id=logdin_user_id,
                                                                                c_owned_by_id=logdin_user_id
                                                                                    )
                                # print('unit_entry',unit_entry)
                                unit_filter['unit_id']=unit_entry.__dict__['id']
                                # print('unit_filter',unit_filter)
                        else:
                            unit_filter['unit_id']=None

                        material_name=row['Material Name'] if row['Material Name'] else ''
                        description=row['Description'] if row['Description'] else ''
                        if row['Material Code']:
                            material_det=Materials.objects.filter(mat_code=row['Material Code'],is_deleted=False).update(type_code='MAT007')
                        #     materialdet=Materials.objects.filter(mat_code=row['Material Code'],is_deleted=False).count()
                        #     print('materialdet',materialdet)
                        #     if material_det:
                        #         for mat in material_det:
                        #             unit_filter['material_id']=mat.id
                        #     else:
                        #         material_entry,created=Materials.objects.get_or_create(mat_code=row['Material Code'],
                        #                                                             type_code='MAT007',
                        #                                                             name=material_name,
                        #                                                             description=description,
                        #                                                             created_by_id=logdin_user_id,
                        #                                                             owned_by_id=logdin_user_id
                        #                                                             )
                        #         # print('material_entry',material_entry)
                        #         unit_filter['material_id']=material_entry.__dict__['id']
                        #         # print('unit_filter',unit_filter)
                        # existing_mapping=MaterialsUnitMapping.objects.filter(**unit_filter).count()
                        # print('existing_mapping',existing_mapping)
                        # if existing_mapping == 0:
                        #     material_unit_mapping=MaterialsUnitMapping.objects.create(**unit_filter,
                        #                                                             created_by_id=logdin_user_id,
                        #                                                             owned_by_id=logdin_user_id
                        #                                                             )


                        total_result['blank_material_code_list']=blank_mat_code_list  

                return Response(total_result)
        except Exception as e:
            raise APIException({'msg':settings.MSG_ERROR,
                                'error':e,
                                "request_status": 0
                                })
class SparesExcelFileAddView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    @response_modify_decorator_post  
    def post(self, request, format=None):
        try:
            document = request.data['document']
            # print('document',document)
            data=pd.read_excel(document,converters={'Material Code':str})
            data = data.replace(np.nan,'',regex=True) 
            # print('data',data)
            unit_filter={}
            logdin_user_id = self.request.user.id
            total_result={}
            blank_mat_code_list=[]
            with transaction.atomic():
                for index, row in data.iterrows():
                    # print('row',row['Material Name'])
                    if row['Material Code'] == '':
                        blank_mat_code_dict={
                            'material_name':row['Material Name'],
                            'material_code':row['Material Code'],
                            'description':row['Description'],
                            'unit':row['Unit']
                        }
                        blank_mat_code_list.append(blank_mat_code_dict)
                    else:
                        if row['Unit']:
                            unit_det=TCoreUnit.objects.filter(c_name=(row['Unit']).lower(),c_is_deleted=False)
                            if unit_det:
                                for det in unit_det:
                                    unit_filter['unit_id']=det.id
                                    # print('unit_filter',unit_filter)
                            else:
                                unit_entry,created=TCoreUnit.objects.get_or_create(c_name=row['Unit'],
                                                                                c_created_by_id=logdin_user_id,
                                                                                c_owned_by_id=logdin_user_id
                                                                                    )
                                # print('unit_entry',unit_entry)
                                unit_filter['unit_id']=unit_entry.__dict__['id']
                                # print('unit_filter',unit_filter)
                        else:
                            unit_filter['unit_id']=None

                        material_name=row['Material Name'] if row['Material Name'] else ''
                        description=row['Description'] if row['Description'] else ''
                        if row['Material Code']:
                            material_det=Materials.objects.filter(mat_code=row['Material Code'],is_deleted=False).update(type_code='MAT004')
                        #     materialdet=Materials.objects.filter(mat_code=row['Material Code'],is_deleted=False).count()
                        #     print('materialdet',materialdet)
                        #     if material_det:
                        #         for mat in material_det:
                        #             unit_filter['material_id']=mat.id
                        #     else:
                        #         material_entry,created=Materials.objects.get_or_create(mat_code=row['Material Code'],
                        #                                                             type_code='MAT004',
                        #                                                             name=material_name,
                        #                                                             description=description,
                        #                                                             created_by_id=logdin_user_id,
                        #                                                             owned_by_id=logdin_user_id
                        #                                                             )
                        #         # print('material_entry',material_entry)
                        #         unit_filter['material_id']=material_entry.__dict__['id']
                        #         # print('unit_filter',unit_filter)
                        # existing_mapping=MaterialsUnitMapping.objects.filter(**unit_filter).count()
                        # print('existing_mapping',existing_mapping)
                        # if existing_mapping == 0:
                        #     material_unit_mapping=MaterialsUnitMapping.objects.create(**unit_filter,
                        #                                                             created_by_id=logdin_user_id,
                        #                                                             owned_by_id=logdin_user_id
                        #                                                             )


                        total_result['blank_material_code_list']=blank_mat_code_list  

                return Response(total_result)
        except Exception as e:
            raise APIException({'msg':settings.MSG_ERROR,
                                'error':e,
                                "request_status": 0
                                })
class GeneralToolsExcelFileAddView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    @response_modify_decorator_post  
    def post(self, request, format=None):
        try:
            document = request.data['document']
            # print('document',document)
            data=pd.read_excel(document,converters={'Material Code':str})
            data = data.replace(np.nan,'',regex=True) 
            # print('data',data)
            unit_filter={}
            logdin_user_id = self.request.user.id
            total_result={}
            blank_mat_code_list=[]
            with transaction.atomic():
                for index, row in data.iterrows():
                    # print('row',row['Material Name'])
                    if row['Material Code'] == '':
                        blank_mat_code_dict={
                            'material_name':row['Material Name'],
                            'material_code':row['Material Code'],
                            'description':row['Description'],
                            'unit':row['Unit']
                        }
                        blank_mat_code_list.append(blank_mat_code_dict)
                    else:
                        if row['Unit']:
                            unit_det=TCoreUnit.objects.filter(c_name=(row['Unit']).lower(),c_is_deleted=False)
                            if unit_det:
                                for det in unit_det:
                                    unit_filter['unit_id']=det.id
                                    # print('unit_filter',unit_filter)
                            else:
                                unit_entry,created=TCoreUnit.objects.get_or_create(c_name=row['Unit'],
                                                                                c_created_by_id=logdin_user_id,
                                                                                c_owned_by_id=logdin_user_id
                                                                                    )
                                # print('unit_entry',unit_entry)
                                unit_filter['unit_id']=unit_entry.__dict__['id']
                                # print('unit_filter',unit_filter)
                        else:
                            unit_filter['unit_id']=None

                        material_name=row['Material Name'] if row['Material Name'] else ''
                        description=row['Description'] if row['Description'] else ''
                        if row['Material Code']:
                            material_det=Materials.objects.filter(mat_code=row['Material Code'],is_deleted=False).update(type_code='MAT003')
                        #     materialdet=Materials.objects.filter(mat_code=row['Material Code'],is_deleted=False).count()
                        #     print('materialdet',materialdet)
                        #     if material_det:
                        #         for mat in material_det:
                        #             unit_filter['material_id']=mat.id
                        #     else:
                        #         material_entry,created=Materials.objects.get_or_create(mat_code=row['Material Code'],
                        #                                                             type_code='MAT003',
                        #                                                             name=material_name,
                        #                                                             description=description,
                        #                                                             created_by_id=logdin_user_id,
                        #                                                             owned_by_id=logdin_user_id
                        #                                                             )
                        #         # print('material_entry',material_entry)
                        #         unit_filter['material_id']=material_entry.__dict__['id']
                        #         # print('unit_filter',unit_filter)
                        # existing_mapping=MaterialsUnitMapping.objects.filter(**unit_filter).count()
                        # print('existing_mapping',existing_mapping)
                        # if existing_mapping == 0:
                        #     material_unit_mapping=MaterialsUnitMapping.objects.create(**unit_filter,
                        #                                                             created_by_id=logdin_user_id,
                        #                                                             owned_by_id=logdin_user_id
                        #                                                             )


                        total_result['blank_material_code_list']=blank_mat_code_list  

                return Response(total_result)
        except Exception as e:
            raise APIException({'msg':settings.MSG_ERROR,
                                'error':e,
                                "request_status": 0
                                })
class SafetyExcelFileAddView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    @response_modify_decorator_post  
    def post(self, request, format=None):
        try:
            document = request.data['document']
            # print('document',document)
            data=pd.read_excel(document,converters={'Material Code':str})
            data = data.replace(np.nan,'',regex=True) 
            # print('data',data)
            unit_filter={}
            logdin_user_id = self.request.user.id
            total_result={}
            blank_mat_code_list=[]
            with transaction.atomic():
                for index, row in data.iterrows():
                    # print('row',row['Material Name'])
                    if row['Material Code'] == '':
                        blank_mat_code_dict={
                            'material_name':row['Material Name'],
                            'material_code':row['Material Code'],
                            'description':row['Description'],
                            'unit':row['Unit']
                        }
                        blank_mat_code_list.append(blank_mat_code_dict)
                    else:
                        if row['Unit']:
                            unit_det=TCoreUnit.objects.filter(c_name=(row['Unit']).lower(),c_is_deleted=False)
                            if unit_det:
                                for det in unit_det:
                                    unit_filter['unit_id']=det.id
                                    # print('unit_filter',unit_filter)
                            else:
                                unit_entry,created=TCoreUnit.objects.get_or_create(c_name=row['Unit'],
                                                                                c_created_by_id=logdin_user_id,
                                                                                c_owned_by_id=logdin_user_id
                                                                                    )
                                # print('unit_entry',unit_entry)
                                unit_filter['unit_id']=unit_entry.__dict__['id']
                                # print('unit_filter',unit_filter)
                        else:
                            unit_filter['unit_id']=None

                        material_name=row['Material Name'] if row['Material Name'] else ''
                        description=row['Description'] if row['Description'] else ''
                        if row['Material Code']:
                            material_det=Materials.objects.filter(mat_code=row['Material Code'],is_deleted=False).update(type_code='MAT008')
                        #     materialdet=Materials.objects.filter(mat_code=row['Material Code'],is_deleted=False).count()
                        #     print('materialdet',materialdet)
                        #     if material_det:
                        #         for mat in material_det:
                        #             unit_filter['material_id']=mat.id
                        #     else:
                        #         material_entry,created=Materials.objects.get_or_create(mat_code=row['Material Code'],
                        #                                                             type_code='MAT008',
                        #                                                             name=material_name,
                        #                                                             description=description,
                        #                                                             created_by_id=logdin_user_id,
                        #                                                             owned_by_id=logdin_user_id
                        #                                                             )
                        #         # print('material_entry',material_entry)
                        #         unit_filter['material_id']=material_entry.__dict__['id']
                        #         # print('unit_filter',unit_filter)
                        # existing_mapping=MaterialsUnitMapping.objects.filter(**unit_filter).count()
                        # print('existing_mapping',existing_mapping)
                        # if existing_mapping == 0:
                        #     material_unit_mapping=MaterialsUnitMapping.objects.create(**unit_filter,
                        #                                                             created_by_id=logdin_user_id,
                        #                                                             owned_by_id=logdin_user_id
                        #                                                             )


                        total_result['blank_material_code_list']=blank_mat_code_list  

                return Response(total_result)
        except Exception as e:
            raise APIException({'msg':settings.MSG_ERROR,
                                'error':e,
                                "request_status": 0
                                })
class FuelandLubExcelFileAddView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    @response_modify_decorator_post  
    def post(self, request, format=None):
        try:
            document = request.data['document']
            # print('document',document)
            data=pd.read_excel(document,converters={'Material Code':str})
            data = data.replace(np.nan,'',regex=True) 
            # print('data',data)
            unit_filter={}
            logdin_user_id = self.request.user.id
            total_result={}
            blank_mat_code_list=[]
            with transaction.atomic():
                for index, row in data.iterrows():
                    # print('row',row['Material Name'])
                    if row['Material Code'] == '':
                        blank_mat_code_dict={
                            'material_name':row['Material Name'],
                            'material_code':row['Material Code'],
                            'description':row['Description'],
                            'unit':row['Unit']
                        }
                        blank_mat_code_list.append(blank_mat_code_dict)
                    else:
                        if row['Unit']:
                            unit_det=TCoreUnit.objects.filter(c_name=(row['Unit']).lower(),c_is_deleted=False)
                            if unit_det:
                                for det in unit_det:
                                    unit_filter['unit_id']=det.id
                                    # print('unit_filter',unit_filter)
                            else:
                                unit_entry,created=TCoreUnit.objects.get_or_create(c_name=row['Unit'],
                                                                                c_created_by_id=logdin_user_id,
                                                                                c_owned_by_id=logdin_user_id
                                                                                    )
                                # print('unit_entry',unit_entry)
                                unit_filter['unit_id']=unit_entry.__dict__['id']
                                # print('unit_filter',unit_filter)
                        else:
                            unit_filter['unit_id']=None

                        material_name=row['Material Name'] if row['Material Name'] else ''
                        description=row['Description'] if row['Description'] else ''
                        if row['Material Code']:
                            material_det=Materials.objects.filter(mat_code=row['Material Code'],is_deleted=False).update(type_code='MAT006')
                        #     materialdet=Materials.objects.filter(mat_code=row['Material Code'],is_deleted=False).count()
                        #     print('materialdet',materialdet)
                        #     if material_det:
                        #         for mat in material_det:
                        #             unit_filter['material_id']=mat.id
                        #     else:
                        #         material_entry,created=Materials.objects.get_or_create(mat_code=row['Material Code'],
                        #                                                             type_code='MAT006',
                        #                                                             name=material_name,
                        #                                                             description=description,
                        #                                                             created_by_id=logdin_user_id,
                        #                                                             owned_by_id=logdin_user_id
                        #                                                             )
                        #         # print('material_entry',material_entry)
                        #         unit_filter['material_id']=material_entry.__dict__['id']
                        #         # print('unit_filter',unit_filter)
                        # existing_mapping=MaterialsUnitMapping.objects.filter(**unit_filter).count()
                        # print('existing_mapping',existing_mapping)
                        # if existing_mapping == 0:
                        #     material_unit_mapping=MaterialsUnitMapping.objects.create(**unit_filter,
                        #                                                             created_by_id=logdin_user_id,
                        #                                                             owned_by_id=logdin_user_id
                        #                                                             )


                        total_result['blank_material_code_list']=blank_mat_code_list  

                return Response(total_result)
        except Exception as e:
            raise APIException({'msg':settings.MSG_ERROR,
                                'error':e,
                                "request_status": 0
                                })
class RawMaterialExcelFileAddView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    @response_modify_decorator_post  
    def post(self, request, format=None):
        try:
            document = request.data['document']
            # print('document',document)
            data=pd.read_excel(document,converters={'Material Code':str})
            data = data.replace(np.nan,'',regex=True) 
            # print('data',data)
            unit_filter={}
            logdin_user_id = self.request.user.id
            total_result={}
            blank_mat_code_list=[]
            with transaction.atomic():
                for index, row in data.iterrows():
                    # print('row',row['Material Name'])
                    if row['Material Code'] == '':
                        blank_mat_code_dict={
                            'material_name':row['Material Name'],
                            'material_code':row['Material Code'],
                            'description':row['Description'],
                            'unit':row['Unit']
                        }
                        blank_mat_code_list.append(blank_mat_code_dict)
                    else:
                        if row['Unit']:
                            unit_det=TCoreUnit.objects.filter(c_name=(row['Unit']).lower(),c_is_deleted=False)
                            if unit_det:
                                for det in unit_det:
                                    unit_filter['unit_id']=det.id
                                    # print('unit_filter',unit_filter)
                            else:
                                unit_entry,created=TCoreUnit.objects.get_or_create(c_name=row['Unit'],
                                                                                c_created_by_id=logdin_user_id,
                                                                                c_owned_by_id=logdin_user_id
                                                                                    )
                                # print('unit_entry',unit_entry)
                                unit_filter['unit_id']=unit_entry.__dict__['id']
                                # print('unit_filter',unit_filter)
                        else:
                            unit_filter['unit_id']=None

                        material_name=row['Material Name'] if row['Material Name'] else ''
                        description=row['Description'] if row['Description'] else ''
                        if row['Material Code']:
                            material_det=Materials.objects.filter(mat_code=row['Material Code'],is_deleted=False)
                            # materialdet=Materials.objects.filter(mat_code=row['Material Code'],is_deleted=False).count()
                            # print('materialdet',materialdet)
                            if material_det:
                                for mat in material_det:
                                    unit_filter['material_id']=mat.id
                            else:
                                material_entry,created=Materials.objects.get_or_create(mat_code=row['Material Code'],
                                                                                    type_code='MAT001',
                                                                                    name=material_name,
                                                                                    description=description,
                                                                                    created_by_id=logdin_user_id,
                                                                                    owned_by_id=logdin_user_id
                                                                                    )
                                # print('material_entry',material_entry)
                                unit_filter['material_id']=material_entry.__dict__['id']
                                # print('unit_filter',unit_filter)
                        existing_mapping=MaterialsUnitMapping.objects.filter(**unit_filter).count()
                        # print('existing_mapping',existing_mapping)
                        if existing_mapping == 0:
                            material_unit_mapping=MaterialsUnitMapping.objects.create(**unit_filter,
                                                                                    created_by_id=logdin_user_id,
                                                                                    owned_by_id=logdin_user_id
                                                                                    )


                        total_result['blank_material_code_list']=blank_mat_code_list  

                return Response(total_result)
        except Exception as e:
            raise APIException({'msg':settings.MSG_ERROR,
                                'error':e,
                                "request_status": 0
                                })



class MaterialsEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = Materials.objects.all()
    serializer_class=MaterialsEditSerializer

    def get(self, request, *args, **kwargs):
        response=super(MaterialsEditView, self).get(self, request, args, kwargs)
        # print('response',response.data)
        unit_details=MaterialsUnitMapping.objects.filter(material=response.data['id'])
        # print('unit_details',unit_details)
        unit_list=list()
        for u_d in unit_details:
            data={
                'id':u_d.id,
                'material':u_d.material.id,
                'unit':u_d.unit.id,
                'unit_name':u_d.unit.c_name,
            }
            unit_list.append(data)
        # print('unit_list',unit_list)
        response.data['material_unit_details']=unit_list
        data_dict={}
        data_dict['result']=response.data
        if response.data:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_SUCCESS
        elif len(response.data) == 0:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_NO_DATA
        else:
            data_dict['request_status'] = 0
            data_dict['msg'] = settings.MSG_ERROR
        response.data = data_dict

        return response

class MaterialsDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = Materials.objects.filter(is_deleted=False)
    serializer_class = MaterialsDeleteSerializer

class MaterialsListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = Materials.objects.filter(is_deleted=False)
    serializer_class=MaterialsListSerializer
    filter_backends = (DjangoFilterBackend,)
    '''
        Added Filter parameters By Rupam Hazra on 20.01.2020 for tender servey
    '''
    filterset_fields = ('id','type_code','is_master','is_crusher')
    pagination_class = OnOffPagination

    def get_queryset(self):
        project = self.request.query_params.get('project', None)
        if project:
            project = project.split(',')
            PmsProjectsmaterialMapping_d = list(
                PmsTenderSurveyResourceMaterial.objects.filter(is_deleted=False, tender_id__in=project).values(
                    'tender_survey_material'))
            # print('PmsProjectsMachinaryMapping_d',PmsProjectsMachinaryMapping_d)
            mapping_ids = list()
            for e_PmsProjectsmaterialMapping_d in PmsProjectsmaterialMapping_d:
                mapping_ids.append(e_PmsProjectsmaterialMapping_d['tender_survey_material'])
            # print('mapping_ids',mapping_ids)
            queryset = Materials.objects.filter(pk__in=mapping_ids, is_deleted=False).order_by('-id')
            print('queryset', queryset)
        else:
            queryset = Materials.objects.filter(is_deleted=False).order_by('-id')
        return queryset

    @response_modify_decorator_list_or_get_before_execution_for_onoff_pagination
    def get(self, request, *args, **kwargs):

        return response

#:::::::::: TENDER SURVEY RESOURCE ESTABLISHMENT :::::::::::#
class TenderSurveyResourceEstablishmentAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsTenderSurveyResourceEstablishment.objects.filter(status=True,is_deleted=False)
    serializer_class = TenderSurveyResourceEstablishmentAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('tender',)
    def get(self, request, *args,**kwargs):
        response = super(TenderSurveyResourceEstablishmentAddView, self).get(self, request, args, kwargs)
        for data in response.data:
            #print('data',data)
            document_details = list()
            establishment_document = PmsTenderSurveyDocument.objects.filter(
                model_class="PmsTenderSurveyResourceEstablishment",
                module_id=int(data['id']),
                status=True, is_deleted=False)
            #print('establishment_document',establishment_document)
            for document in establishment_document:
                data1={
                    "id":int(document.id),
                    "tender":int(document.tender.id),
                    "module_id":document.module_id,
                    "document_name":document.document_name,
                    "document":request.build_absolute_uri(document.document.url),
                }
                document_details.append(data1)
            data['establishment_document_details']=document_details
        data_dict = {}
        data_dict['result'] = response.data
        if response.data:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_SUCCESS
        elif len(response.data) == 0:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_NO_DATA
        else:
            data_dict['request_status'] = 0
            data_dict['msg'] = settings.MSG_ERROR
        response.data = data_dict
        return response
class TenderSurveyResourceEstablishmentEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsTenderSurveyResourceEstablishment.objects.all()
    serializer_class = TenderSurveyResourceEstablishmentEditSerializer
class TenderSurveyResourceEstablishmentDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsTenderSurveyResourceEstablishment.objects.all()
    serializer_class = TenderSurveyResourceEstablishmentDeleteSerializer
class TenderSurveyResourceEstablishmentDocumentAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsTenderSurveyDocument.objects.filter(status=True,is_deleted=False)
    serializer_class =TenderSurveyResourceEstablishmentDocumentAddSerializer
class TenderSurveyResourceEstablishmentDocumentEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsTenderSurveyDocument.objects.all()
    serializer_class =TenderSurveyResourceEstablishmentDocumentEditSerializer
class TenderSurveyResourceEstablishmentDocumentDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsTenderSurveyDocument.objects.all()
    serializer_class =TenderSurveyResourceEstablishmentDocumentDeleteSerializer

#:::: TENDER SURVEY RESOURCE HYDROLOGICAL :::::::#
class TenderSurveyResourceHydrologicalAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = TenderSurveyResourceHydrologicalAddSerializer
    queryset = PmsTenderSurveyResourceHydrological.objects.filter(status=True, is_deleted=False)
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('tender',)
    def get(self, request, *args, **kwargs):
        response = super(TenderSurveyResourceHydrologicalAddView, self).get(self, request, args, kwargs)
        for data in response.data:
            # print('data',data)
            document_details = list()
            establishment_document = PmsTenderSurveyDocument.objects.filter(
                model_class="PmsTenderSurveyResourceHydrological",
                module_id=int(data['id']),
                status=True, is_deleted=False)
            # print('establishment_document',establishment_document)
            for document in establishment_document:
                data1 = {
                    "id": int(document.id),
                    "tender": int(document.tender.id),
                    "module_id": document.module_id,
                    "document_name": document.document_name,
                    "document": request.build_absolute_uri(document.document.url),
                }
                document_details.append(data1)
            data['hyderological_document_details'] = document_details
        data_dict = {}
        data_dict['result'] = response.data
        if response.data:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_SUCCESS
        elif len(response.data) == 0:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_NO_DATA
        else:
            data_dict['request_status'] = 0
            data_dict['msg'] = settings.MSG_ERROR
        response.data = data_dict
        return response
class TenderSurveyResourceHydrologicalEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = TenderSurveyResourceHydrologicalEditSerializer
    queryset = PmsTenderSurveyResourceHydrological.objects.filter(status=True, is_deleted=False)
class TenderSurveyResourceHydrologicalDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = TenderSurveyResourceHydrologicalDeleteSerializer
    queryset = PmsTenderSurveyResourceHydrological.objects.all()
class TenderSurveyResourceHydrologicalDocumentAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = TenderSurveyResourceHydrologicalDocumentAddSerializer
    queryset = PmsTenderSurveyDocument.objects.all()
class TenderSurveyResourceHydrologicalDocumentEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = TenderSurveyResourceHydrologicalDocumentEditSerializer
    queryset = PmsTenderSurveyDocument.objects.filter(status=True, is_deleted=False)
class TenderSurveyResourceHydrologicalDocumentDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = TenderSurveyResourceHydrologicalDocumentDeleteSerializer
    queryset = PmsTenderSurveyDocument.objects.all()

#:::: TENDER SURVEY RESOURCE CONTRACTORS / VENDORS  CONTRACTOR WORK TYPE:::::::#
class TenderSurveyResourceContractorsOVendorsContractorWTypeAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsTenderSurveyResourceContractorsOVendorsContractor.objects.all()
    serializer_class =TenderSurveyResourceContractorsOVendorsContractorWTypeAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('tender',)

    def get(self, request, *args, **kwargs):
        response = super(TenderSurveyResourceContractorsOVendorsContractorWTypeAddView, self).get(self, request, args, kwargs)
        for data in response.data:
            # print('data',data)
            document_details = list()
            establishment_document = PmsTenderSurveyDocument.objects.filter(
                model_class="PmsTenderSurveyResourceContractorsOVendorsContractor",
                module_id=int(data['id']),
                status=True, is_deleted=False)
            # print('establishment_document',establishment_document)
            for document in establishment_document:
                data1 = {
                    "id": int(document.id),
                    "tender": int(document.tender.id),
                    "module_id": document.module_id,
                    "document_name": document.document_name,
                    "document": request.build_absolute_uri(document.document.url),
                }
                document_details.append(data1)
            data['Contractor_document_details'] = document_details
        data_dict = {}
        data_dict['result'] = response.data
        if response.data:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_SUCCESS
        elif len(response.data) == 0:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_NO_DATA
        else:
            data_dict['request_status'] = 0
            data_dict['msg'] = settings.MSG_ERROR
        response.data = data_dict
        return response
class TenderSurveyResourceContractorsOVendorsContractorWTypeEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsTenderSurveyResourceContractorsOVendorsContractor.objects.all()
    serializer_class = TenderSurveyResourceContractorsOVendorsContractorWTypeEditSerializer
class TenderSurveyResourceContractorsOVendorsContractorWTypeDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsTenderSurveyResourceContractorsOVendorsContractor.objects.all()
    serializer_class = TenderSurveyResourceContractorsOVendorsContractorWTypeDeleteSerializer
class TenderSurveyResourceContractorsOVendorsContractorWTypeDocumentAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class =TenderSurveyResourceContractorsOVendorsContractorWTypeDocumentAddSerializer
    queryset = PmsTenderSurveyDocument.objects.filter(status=True, is_deleted=False)
class TenderSurveyResourceContractorsOVendorsContractorWTypeDocumentEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class =TenderSurveyResourceContractorsOVendorsContractorWTypeDocumentEditSerializer
    queryset = PmsTenderSurveyDocument.objects.filter(status=True, is_deleted=False)
class TenderSurveyResourceContractorsOVendorsContractorWTypeDocumentDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class =TenderSurveyResourceContractorsOVendorsContractorWTypeDocumentDeleteSerializer
    queryset = PmsTenderSurveyDocument.objects.filter(status=True, is_deleted=False)


 #:::::::::::::::::::::: Machinary Type :::::::::::::::::::::::::#

#:::::::::::::::::::::: Machinary Type :::::::::::::::::::::::::#
class MachineryTypeAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = MachineryTypeAddSerializer
    queryset = PmsMachineryType.objects.filter(is_deleted=False)
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('is_default',)
    def get(self, request, *args, **kwargs):
        response = super(self.__class__, self).get(self, request, *args,**kwargs)
        for data in response.data:
            # print('data',data)
            document_details = list()
            establishment_document = PmsTenderSurveyDocument.objects.filter(
                model_class="PmsTenderSurveyResourceContractorsOVendorsVendor",
                module_id=int(data['id']),
                status=True, is_deleted=False)
            # print('establishment_document',establishment_document)
            for document in establishment_document:
                data1 = {
                    "id": int(document.id),
                    "tender": int(document.tender.id),
                    "module_id": document.module_id,
                    "document_name": document.document_name,
                    "document": request.build_absolute_uri(document.document.url),
                }
                document_details.append(data1)
            data['document_details'] = document_details
        data_dict = {}
        data_dict['result'] = response.data
        if response.data:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_SUCCESS
        elif len(response.data) == 0:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_NO_DATA
        else:
            data_dict['request_status'] = 0
            data_dict['msg'] = settings.MSG_ERROR
        response.data = data_dict
        return response
class MachineryTypeEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = MachineryTypeEditSerializer
    queryset = PmsMachineryType.objects.filter(is_deleted=False)
class MachineryTypeDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = MachineryTypeDeleteSerializer
    queryset = PmsMachineryType.objects.all()

#:::: TENDER SURVEY RESOURCE CONTRACTORS / VENDORS  P & M:::::::#
class TenderSurveyResourceContractorsOVendorsMachineryTypeExDeAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = TenderSurveyResourceContractorsOVendorsMachineryTypeExDeAddSerializer
    queryset = PmsTenderMachineryTypeDetails.objects.filter(is_deleted=False)
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('tender',)
    def get(self, request, *args, **kwargs):
        response = super(self.__class__, self).get(self, request, *args,**kwargs)
        for data in response.data:
            # print('data',data)
            document_details = list()
            establishment_document = PmsTenderSurveyDocument.objects.filter(
                model_class="PmsTenderMachineryTypeDetails",
                module_id=int(data['id']),
                status=True, is_deleted=False)
            # print('establishment_document',establishment_document)
            for document in establishment_document:
                data1 = {
                    "id": int(document.id),
                    "tender": int(document.tender.id),
                    "module_id": document.module_id,
                    "document_name": document.document_name,
                    "document": request.build_absolute_uri(document.document.url),
                }
                document_details.append(data1)
            data['document_details'] = document_details
        data_dict = {}
        data_dict['result'] = response.data
        if response.data:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_SUCCESS
        elif len(response.data) == 0:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_NO_DATA
        else:
            data_dict['request_status'] = 0
            data_dict['msg'] = settings.MSG_ERROR
        response.data = data_dict
        return response

class TenderSurveyResourceContractorsOVendorsMachineryTypeDeAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = TenderSurveyResourceContractorsOVendorsMachineryTypeDeAddSerializer
    queryset = PmsTenderMachineryTypeDetails.objects.filter(is_deleted=False)
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('tender',)
    def get(self, request, *args, **kwargs):
        response = super(self.__class__, self).get(self, request, *args,**kwargs)
        for data in response.data:
            # print('data',data)
            document_details = list()
            establishment_document = PmsTenderSurveyDocument.objects.filter(
                model_class="PmsTenderMachineryTypeDetails",
                module_id=int(data['id']),
                status=True, is_deleted=False)
            # print('establishment_document',establishment_document)
            for document in establishment_document:
                data1 = {
                    "id": int(document.id),
                    "tender": int(document.tender.id),
                    "module_id": document.module_id,
                    "document_name": document.document_name,
                    "document": request.build_absolute_uri(document.document.url),
                }
                document_details.append(data1)
            data['document_details'] = document_details
        data_dict = {}
        data_dict['result'] = response.data
        if response.data:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_SUCCESS
        elif len(response.data) == 0:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_NO_DATA
        else:
            data_dict['request_status'] = 0
            data_dict['msg'] = settings.MSG_ERROR
        response.data = data_dict
        return response

class MachinaryTypeListByTenderView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    #pagination_class = CSPageNumberPagination
    serializer_class = MachinaryTypeListByTenderSerializer
    queryset = PmsTenderMachineryTypeDetails.objects.filter(is_deleted=False)
    def get_queryset(self):
        tender=self.kwargs.get('tender')
        return self.queryset.filter(tender=tender)
        
    @response_modify_decorator_get_after_execution
    def get(self, request,*args,**kwargs):
        response=super(self.__class__, self).get(self, request, *args,**kwargs)
        m_t_list_2 = list()
        machinary_type_w_default=PmsMachineryType.objects.filter(is_default=True,is_deleted=False)
        if machinary_type_w_default:
            for m_w in machinary_type_w_default:
                m_w_dict={
                    'machinary_type':m_w.id,
                    'id':m_w.id,
                    'name':m_w.name,
                    'description':m_w.description,
                    'is_default':m_w.is_default,
                    'make':None,
                    'hire':None,
                    'khoraki':None,
                    'latitude':None,
                    'longitude':None,
                    'address':None
                }
                m_t_list_2.append(m_w_dict)
        response.data = response.data + m_t_list_2
        return response
        

class TenderSurveyResourceContractorsOVendorsMachineryTypeDeEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = TenderSurveyResourceContractorsOVendorsMachineryTypeDeEditSerializer
    queryset = PmsTenderMachineryTypeDetails.objects.filter(is_deleted=False)

class TenderSurveyResourceContractorsOVendorsMachineryTypeDeDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = TenderSurveyResourceContractorsOVendorsMachineryTypeDeDeleteSerializer
    queryset = PmsTenderMachineryTypeDetails.objects.all()

class TenderSurveyResourceContractorsOVendorsMachineryTypeDeDocumentAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = TenderSurveyResourceContractorsOVendorsMachineryTypeDeDocumentAddSerializer
    queryset = PmsTenderSurveyDocument.objects.filter(status=True, is_deleted=False)

class TenderSurveyResourceContractorsOVendorsMachineryTypeDeDocumentEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = TenderSurveyResourceContractorsOVendorsMachineryTypeDeDocumentEditSerializer
    queryset = PmsTenderSurveyDocument.objects.filter(status=True, is_deleted=False)
class TenderSurveyResourceContractorsOVendorsMachineryTypeDeDocumentDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = TenderSurveyResourceContractorsOVendorsMachineryTypeDeDocumentDeleteSerializer
    queryset = PmsTenderSurveyDocument.objects.filter(status=True, is_deleted=False)

#:::: TENDER SURVEY RESOURCE CONTACT DETAILS AND DESIGNATION :::::::#
class TenderSurveyResourceContactDesignationAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsTenderSurveyResourceContactDesignation.objects.filter(status=True)
    serializer_class = TenderSurveyResourceContactDesignationAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('tender',)
    @response_modify_decorator_list
    def list(self, request, *args, **kwargs):
        return response
class TenderSurveyResourceContactDetailsAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsTenderSurveyResourceContactDetails.objects.filter(
        is_deleted=False,status=True)
    serializer_class =TenderSurveyResourceContactDetailsAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('tender','designation')
    def get(self, request, *args, **kwargs):
        response = super(TenderSurveyResourceContactDetailsAddView, self).get(self, request, *args, **kwargs)
        for data in response.data:
            details_queryset = PmsTenderSurveyResourceContactFieldDetails.objects.filter(
                contact=data["id"], is_deleted=False, status=True)
            field_details_l = list()
            if details_queryset:
                for e_details_queryset in details_queryset:
                    field_details_d = dict()
                    # field_details_d['id'] = e_details_queryset.id
                    # field_details_d['contact'] = e_details_queryset.contact.id
                    field_details_d['field_label'] = e_details_queryset.field_label
                    field_details_d['field_value'] = e_details_queryset.field_value
                    field_details_d['field_type'] = e_details_queryset.field_type
                    field_details_l.append(field_details_d)
                data['field_details'] = field_details_l
            else:
                field_details_l=list()
                data['field_details'] = field_details_l
        data_dict = {}
        data_dict['result'] = response.data
        if response.data:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_SUCCESS
        elif len(response.data) == 0:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_NO_DATA
        else:
            data_dict['request_status'] = 0
            data_dict['msg'] = settings.MSG_ERROR
        response.data = data_dict
        return response
class TenderSurveyResourceContactDetailsEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsTenderSurveyResourceContactDetails.objects.all()
    serializer_class =TenderSurveyResourceContactDetailsEditSerializer
class TenderSurveyResourceContactDetailsDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsTenderSurveyResourceContactDetails.objects.all()
    serializer_class =TenderSurveyResourceContactDetailsDeleteSerializer

#::::::::::: TENDER INITIAL COSTING ::::::::::::::::::::#
class TenderInitialCostingUploadFileView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    def post(self, request, format=None):
        try:
            document = request.data['document']
            print('document',type(document))
            # filename = document.name
            # print('filename', type(filename))
            # file_type = filename.split('.')
            # print('file_type', file_type)
            # if file_type != 'xlsx':
            #     print('document type',document)
            #     raise APIException(
            #         {
            #             'request_status': 0,
            #             'msg': 'Check your file type',
            #         }
            #     )

            field_label_value = []
            import xlrd
            df1 = pd.read_excel(document) #read excel
            df2 = df1.replace(np.nan,'',regex=True) # for replace blank value with nan
            df =df2.loc[:, ~df2.columns.str.contains('^Unnamed')] # for elmeminate the blank index
            for j in df.columns:
                #print(df[j])
                field_value = []
                # tender_initial_costing_label = PmsTenderInitialCostingExcelFieldLabel.\
                #     objects.create(
                #     tender_initial_costing=PmsTenderInitialCosting.objects.get(pk=1),
                #     field_label=j
                #
                # )
                for i in df.index:
                    # tender_initial_costing_field = PmsTenderInitialCostingExcelFieldValue. \
                    #     objects.create(
                    #     tender_initial_costing=PmsTenderInitialCosting.objects.get(pk=1),
                    #     initial_costing_field_label=tender_initial_costing_label,
                    #     field_value=df[j][i]
                    #
                    # )
                    field_value.append(df[j][i])
                field_label_val_dict = {
                        "field_label":j,
                        "field_value":field_value
                        }
                field_label_value.append(field_label_val_dict)
            #print('field_label_value',field_label_value)
            response_data={
                "tender":request.data['tender'],
                "field_label_value":field_label_value
            }
            return Response(response_data)
        except Exception as e:

            raise APIException(
                {
                    'request_status': 0,
                    'msg': 'Check your file type',
                    'orginal_error': e
                }
            )
class TenderInitialCostingAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsTenderInitialCosting.objects.all()
    serializer_class =TenderInitialCostingAddSerializer
class TenderInitialCostingDetailsView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class =TenderInitialCostingDetailsSerializer
    def get(self, request, *args, **kwargs):
        response = dict()
        tender_id = self.kwargs['tender_id']
        ini_d = PmsTenderInitialCosting.objects.filter(tender=tender_id).values(
            'id','client','tender_notice_no_bid_id_no','name_of_work','is_approved',
            'difference_in_budget','quoted_rate','received_estimate','is_deleted','tender','created_by','owned_by')
        #print('ini_d',ini_d)
        if ini_d :
            for d in ini_d:
                ini_id = d['id']
                response['id'] = d['id']
                response['client'] = d['client']
                response['tender_notice_no_bid_id_no'] = d['tender_notice_no_bid_id_no']
                response['name_of_work'] = d['name_of_work']
                response['is_approved'] = 1 if d['is_approved'] == 1 else 0
                response['difference_in_budget'] = d['difference_in_budget']
                response['quoted_rate'] = d['quoted_rate']
                response['received_estimate'] = d['received_estimate']
                response['is_deleted'] = d['is_deleted']
                response['tender'] = d['tender']
                response['created_by'] = d['created_by']
                response['owned_by'] = d['owned_by']
            field_label_value_d = PmsTenderInitialCostingExcelFieldLabel.objects.filter(
                tender_initial_costing = ini_id)
            field_label_value = []
            for j in field_label_value_d:
                field_value = []
                field_label_value_v = PmsTenderInitialCostingExcelFieldValue.objects.filter(
                tender_initial_costing = ini_id,
                    initial_costing_field_label = j.id)
                #print('field_label_value_v',field_label_value_v)
                for i in field_label_value_v:
                    #print('field_label_value_v[index_j][index_i]',i)
                    field_value.append(i.field_value)
                field_label_val_dict = {
                    "field_label": j.field_label,
                    "field_value": field_value
                }
                field_label_value.append(field_label_val_dict)
            response['field_label_value'] = field_label_value
        data_dict = {}
        data_dict['result'] = response
        if response:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_SUCCESS
            data_dict['result'] = response
        elif len(response) == 0:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_NO_DATA
            data_dict['result'] = None
        else:
            data_dict['request_status'] = 0
            data_dict['msg'] = settings.MSG_ERROR
            data_dict['result'] = None
        response = data_dict    

        return Response(response)

#::::::::::::::: PmsTenderTabDocuments :::::::::::::::::::::#
class TenderEligibilityFieldDocumentAdd(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = TenderEligibilityFieldDocumentAddSerializer
    queryset = PmsTenderEligibilityFieldsByType.objects.filter(is_deleted=False).order_by('-id')
class TenderCheckTabDocumentUploadAddView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsTenderTabDocuments.objects.filter(is_deleted=False).order_by('-id')
    serializer_class = TenderCheckTabDocumentUploadAddSerializer
    def get(self, request, *args, **kwargs):
        #response = dict()
        tender_id = self.kwargs['tender_id']
        tab_doc_d = PmsTenderTabDocuments.objects.filter(tender=tender_id).values(
            'id','tender','is_upload_document','reason_for_no_documentation',
            'created_by','owned_by','status')
        if tab_doc_d:
            for e_tab_doc in tab_doc_d:
                tab_doc = {
                    'id': e_tab_doc['id'],
                    'tender':e_tab_doc['tender'],
                    'is_upload_document': e_tab_doc['is_upload_document'],
                    'reason_for_no_documentation': e_tab_doc['reason_for_no_documentation'],
                    'created_by': e_tab_doc['created_by'],
                    'owned_by': e_tab_doc['owned_by'],
                }
        else:
            tab_doc = ""
        #print('tab_doc',tab_doc)
        return Response({"result":tab_doc})
class TenderTabDocumentDocumentsAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsTenderTabDocumentsDocuments.objects.filter(is_deleted=False).order_by('-id')
    serializer_class = TenderTabDocumentDocumentsAddSerializer
    def get(self, request, *args, **kwargs):
        response =list()
        tender_id = self.kwargs['tender_id']
        el_type = self.kwargs['eligibility_type']
        el_type_id_d = PmsTenderTabDocumentsDocuments.objects.filter(
            tender_eligibility__type=el_type,
            tender_eligibility__tender=tender_id,
            tender_eligibility__is_deleted=False,is_deleted=False)
        for el_type_id in el_type_id_d:
            response_d = {
                'id':el_type_id.id,
                'tender':el_type_id.tender.id,
                'tender_eligibility':el_type_id.tender_eligibility.id,
                'document_date_o_s':el_type_id.document_date_o_s,
                'document_name':el_type_id.document_name,
                'tab_document':request.build_absolute_uri(el_type_id.tab_document.url),
                'created_by':el_type_id.created_by.username,
                'owned_by': el_type_id.owned_by.username,
            }
            response.append(response_d)
        #print('el_type_id_d', el_type_id_d)
        return Response(response)
class TenderTabDocumentDocumentsListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsTenderTabDocumentsDocuments.objects.filter(is_deleted=False).order_by('-id')
    serializer_class = TenderTabDocumentDocumentsListSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('tender',)
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response

class TenderTabDocumentsListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsTenderTabDocumentsDocuments.objects.filter(is_deleted=False).order_by('-id')
    serializer_class = TenderTabDocumentsListSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('tender',)
    def get(self, request, *args, **kwargs):
        tender = self.request.GET.get('tender')
        response=super(self.__class__, self).get(self, request, *args,**kwargs)
        el_doc_list = list()
        type_list = set()
        for e_res in response.data:
            type_list.add(e_res['type'])

        type_list.add('price')
        print('type_list',type_list)
        for e_type_list in type_list:
            if e_type_list == 'price':
                e_res_d = {'type':'price',}
                tab_docs= PmsTenderTabDocumentsPrice.objects.filter(
                    is_deleted=False,tender_id=int(tender))
            else:
                e_res_d = {'type':e_type_list,}
                tab_docs= PmsTenderTabDocumentsDocuments.objects.filter(
                    is_deleted=False,tender_id=int(tender),tender_eligibility__type=e_type_list
                    )
            e_el_document_list =list()
            for e_tab_docs in tab_docs:
                e_el_document_d = {
                'id':e_tab_docs.id,
                #'type':e_tab_docs.tender_eligibility.type,
                'document_date_o_s':e_tab_docs.document_date_o_s,
                'document_name':e_tab_docs.document_name,
                'tab_document':request.build_absolute_uri(e_tab_docs.tab_document.url),
                'is_deleted':e_tab_docs.is_deleted,
                'tender':e_tab_docs.tender.id,
                #'tender_eligibility':e_tab_docs.tender_eligibility.id,
                }
                e_el_document_list.append(e_el_document_d)

            #print('tab_doc',tab_doc)
            e_res_d['documents'] = e_el_document_list
            

            el_doc_list.append(e_res_d)
        print('type_list',type_list)
        #price_documents = PmsTenderTabDocumentsPrice.objects.filter(tender_id=tender)
        #print('price_documents',price_documents)
        #el_doc_list['type'] = 'price'
            
        # price_documents_l = list()
        # for e_price_document in price_documents:
        #     e_price_document_d = {
        #         'id':e_price_document.id,
        #         'type':"price",
        #         'document_date_o_s':e_price_document.document_date_o_s,
        #         'document_name':e_price_document.document_name,
        #         'tab_document':request.build_absolute_uri(e_price_document.tab_document.url),
        #         'is_deleted':e_price_document.is_deleted,
        #         'tender':e_price_document.tender.id,
        #         'tender_eligibility':None,
        #     }
        #     price_documents_l.append(e_price_document_d)
        # price_type_d['documents'] = price_documents_l
        # total_doc_list = el_doc_list+price_type_d
        if el_doc_list: 
            return Response(
                {
                    "results":el_doc_list,
                    "request_status":1,
                    "msg":settings.MSG_SUCCESS
                }
                )
        else:
            return Response(
                {
                    "results":list(),
                    "request_status":1,
                    "msg":settings.MSG_NO_DATA
                }
                )
       

class TenderTabDocumentDocumentsEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsTenderTabDocumentsDocuments.objects.filter(is_deleted=False).order_by('-id')
    serializer_class = TenderTabDocumentDocumentsEditSerializer
class TenderTabDocumentDocumentsDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = TenderTabDocumentDocumentsDeleteSerializer
    queryset = PmsTenderTabDocumentsDocuments.objects.filter(is_deleted=False).order_by('-id')

#:::::::::::::::PmsTenderTabDocumentsPrice:::::::::::::::::::::#
class TenderTabDocumentPriceAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsTenderTabDocumentsPrice.objects.filter(is_deleted=False,status=True).order_by('-id')
    serializer_class = TenderTabDocumentPriceAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('tender',)
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
class TenderTabDocumentPriceEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsTenderTabDocumentsPrice.objects.filter(status=True, is_deleted=False)
    serializer_class = TenderTabDocumentPriceEditSerializer
class TenderTabDocumentPriceDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsTenderTabDocumentsPrice.objects.filter(status=True, is_deleted=False)
    serializer_class = TenderTabDocumentPriceDeleteSerializer

#::::::::::::::::::: TENDER APPROVAL :::::::::::::#
class TenderApprovalAddOrUpdateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsTenderTabDocumentsPrice.objects.filter(is_deleted=False).order_by('-id')
    serializer_class = TenderApprovalAddOrUpdateSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('tender',)
    def get(self, request, *args, **kwargs):
        #response = dict()
        tender_id = self.kwargs['tender_id']
        tender_app_d = PmsTenderApproval.objects.filter(tender=tender_id).values(
            'id','tender','is_approved','reject_reason','created_by','owned_by')
        if tender_app_d:
            for e_tender_app_d in tender_app_d:
                tab_approve = {
                    'id': e_tender_app_d['id'],
                    'tender':e_tender_app_d['tender'],
                    'is_approved': e_tender_app_d['is_approved'],
                    'reject_reason': e_tender_app_d['reject_reason'],
                    'created_by': e_tender_app_d['created_by'],
                    'owned_by': e_tender_app_d['owned_by'],
                }
        else:
            tab_approve = ""
        #print('tab_doc',tab_doc)
        return Response({"result":tab_approve})
class TenderDetailsForApprovalView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsTenderApproval.objects.filter(is_deleted=False).order_by('-id')
    serializer_class = TenderApprovalAddOrUpdateSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('tender',)
    def get(self, request, *args, **kwargs):
        tender_id = self.kwargs['tender_id']
        data_dict={}
        tab_approve={}
        tender_app_d = custom_filter(
            self,PmsTenderApproval,
            filter_columns={
                'tender': tender_id, 'is_deleted': False
            },
            fetch_columns=['id', 'tender', 'is_approved', 'reject_reason', 'created_by', 'owned_by'],
            )
        print('tender_app_d',tender_app_d)
        if tender_app_d:
            for e_tender_app_d in tender_app_d:
                tab_approve = {
                    'id': e_tender_app_d['id'],
                    'tender': e_tender_app_d['tender'],
                    'is_approved': e_tender_app_d['is_approved'],
                    'reject_reason': e_tender_app_d['reject_reason'],
                    'created_by': e_tender_app_d['created_by'],
                    'owned_by': e_tender_app_d['owned_by'],
                }

            #@@@ tender details  @@@#
            tender_details = custom_filter(
                self, PmsTenders,
                filter_columns = {
                    'pk': tender_id,'is_deleted':False
                },
                fetch_columns=['id','tender_opened_on','tender_received_on','tender_final_date',
                'tender_added_by','tender_aasigned_to','is_deleted'],
                single_row=True
            )
            if tender_details:
                tab_approve['tender_details'] = tender_details
            else:
                tab_approve['tender_details'] =dict()

            #@@@ tender document details  @@@#
            tender_doc_details = custom_filter(
                self, PmsTenderDocuments, filter_columns = {
                    'tender': tender_id,'is_deleted':False
                })
            #print('tender_doc_details',tender_doc_details)
            doc_list = list()
            if tender_doc_details:
                for e_tender_doc_details in tender_doc_details:
                    doc_list.append({
                        'id':e_tender_doc_details.id,
                        'document_name':e_tender_doc_details.document_name,
                        'tender_document': request.build_absolute_uri(e_tender_doc_details.tender_document.url),
                        'is_deleted':e_tender_doc_details.is_deleted
                    })
                tab_approve['tender_document_details'] = doc_list
            else:
                tab_approve['tender_document_details'] = doc_list

            #@@@ eligibility details  @@@#
            tender_elgi_details = custom_filter(self,PmsTenderEligibility,
                filter_columns = {
                    'tender': tender_id,'is_deleted':False
                },
                fetch_columns=['id','type','ineligibility_reason',
                               'eligibility_status','is_deleted'],)
            #print('tender_elgi_details',tender_elgi_details)
            if tender_elgi_details:
                tender_eligibility_details_list = list()
                for e_tender_elgi_details in tender_elgi_details:
                    #print('e_tender_elgi_details',e_tender_elgi_details)
                    tender_eligibility_details= {
                        'id' : e_tender_elgi_details['id'],
                        'type': e_tender_elgi_details['type'],
                        'ineligibility_reason': e_tender_elgi_details['ineligibility_reason'],
                        'eligibility_status': e_tender_elgi_details['eligibility_status'],
                        'is_deleted':  e_tender_elgi_details['is_deleted'],
                        }
                    tender_eligibility_details_list.append(tender_eligibility_details)
                    #@@@ eligibility field details  @@@#
                    tender_elgi_f_details = custom_filter(
                        self, PmsTenderEligibilityFieldsByType,
                        filter_columns = {'tender': tender_id,
                                          'tender_eligibility': e_tender_elgi_details['id'],
                                        'is_deleted':False},
                        fetch_columns=['id','tender','tender_eligibility','field_label',
                                       'field_value','eligible','document','is_deleted'],)
                    #print('tender_elgi_f_details',tender_elgi_f_details)
                    if tender_elgi_f_details:
                        tender_eligibility_details['field_details'] = tender_elgi_f_details
                    else:
                        tender_eligibility_details['field_details'] = list()
                tab_approve['tender_eligibility_details']=tender_eligibility_details_list

            else:
                tab_approve['tender_eligibility_details'] = list()

            #@@@ biddder type details  @@@#
            tender_bidder_details1 = custom_filter(
                self, PmsTenderBidderType,
                filter_columns={'tender': tender_id, 'is_deleted': False},
                fetch_columns=['id', 'type_of_partner','profit_sharing_ratio_actual_amount',
                               'bidder_type','responsibility',
                               'profit_sharing_ratio_tender_specific_amount','is_deleted'], single_row=True)
            #print('tender_bidder_details',tender_bidder_details1)
            tender_bidder_details = {
                'id': tender_bidder_details1['id'],
                'type_of_partner': 'Lead Partner' if tender_bidder_details1['type_of_partner'] == 1 else 'Other Partner',
                'profit_sharing_ratio_actual_amount': tender_bidder_details1['profit_sharing_ratio_actual_amount'],
                'bidder_type': tender_bidder_details1['bidder_type'],
                'responsibility': tender_bidder_details1['responsibility'].replace('_',' ').title(),
                'profit_sharing_ratio_tender_specific_amount': tender_bidder_details1['profit_sharing_ratio_tender_specific_amount'],
                'is_deleted': tender_bidder_details1['is_deleted'],
            }
            # @@@ biddder type vendor details  @@@#
            tender_bidder_partner_details = custom_filter(
                self, PmsTenderBidderTypePartnerMapping,
                filter_columns={
                    'tender_bidder_type': tender_bidder_details1['id'],'is_deleted': False
                },
                fetch_columns=['tender_partner__id','tender_partner__name','tender_partner__contact',
                               'tender_partner__address','is_deleted'],
            )
            #print('tender_bidder_vendor_details',tender_bidder_vendor_details.query)
            tender_bidder_details['partners'] = tender_bidder_partner_details
            tab_approve['tender_bidder_type_details'] = tender_bidder_details
            # @@@ tender initial costing details  @@@#
            tender_initial_costing_details=custom_filter(self,PmsTenderInitialCosting,
                filter_columns = {
                    'tender': tender_id,'is_deleted':False
                },
                fetch_columns=['id','client','tender_notice_no_bid_id_no','name_of_work','is_approved',
                               'received_estimate','quoted_rate','difference_in_budget','document','is_deleted'],)
            # print('tender_initial_costing_details',tender_initial_costing_details)
            if tender_initial_costing_details:
                for e_tender_int_cost in tender_initial_costing_details:
                    initial_costing_details={
                        'id':e_tender_int_cost['id'],
                        'client':e_tender_int_cost['client'],
                        'tender_notice_no_bid_id_no':e_tender_int_cost['tender_notice_no_bid_id_no'],
                        'name_of_work':e_tender_int_cost['name_of_work'],
                        'is_approved':e_tender_int_cost['is_approved'],
                        'received_estimate':e_tender_int_cost['received_estimate'],
                        'quoted_rate':e_tender_int_cost['quoted_rate'],
                        'difference_in_budget':e_tender_int_cost['difference_in_budget'],
                        'document':request.build_absolute_uri(e_tender_int_cost['document']),
                    }
                    # print('initial_costing_details',initial_costing_details)
                    initial_costing_field_label = custom_filter(
                        self, PmsTenderInitialCostingExcelFieldLabel,
                        filter_columns={
                                        'tender_initial_costing': e_tender_int_cost['id'],
                                        'is_deleted': False},
                        fetch_columns=['id',  'tender_initial_costing', 'field_label',
                                        'is_deleted'], )
                    # print('initial_costing_field_label',initial_costing_field_label)
                    if initial_costing_field_label:
                        initial_costing_details['field_label_value']=initial_costing_field_label
                    else:
                        initial_costing_details['field_label_value'] = list()
                    # print('initial_costing_details',initial_costing_details)
                    for e_field_label in initial_costing_field_label:
                        # print('e_field_label',e_field_label)
                        initial_costing_field_value = custom_filter(
                            self, PmsTenderInitialCostingExcelFieldValue,
                            filter_columns={
                                'tender_initial_costing': e_tender_int_cost['id'],
                                'initial_costing_field_label': e_field_label['id'],
                                'is_deleted': False},
                            fetch_columns=['id', 'tender_initial_costing','initial_costing_field_label','field_value',
                                           'is_deleted'], )
                        # print('initial_costing_field_value',initial_costing_field_value)

                        if initial_costing_field_value:
                            field_value_list = list()
                            # initial_costing_details['field_label_value'] = initial_costing_field_value
                            for e_field_value in initial_costing_field_value:
                                # print('e_field_value',e_field_value)
                                field_value_dict={
                                    'id':e_field_value['id'],
                                    'tender_initial_costing':e_field_value['tender_initial_costing'],
                                    'initial_costing_field_label':e_field_value['initial_costing_field_label'],
                                    'field_value':e_field_value['field_value']
                                }
                                field_value_list.append(field_value_dict)
                            # print('field_value_list',field_value_list)
                                e_field_label['field_values']=field_value_list

                        else:
                            initial_costing_details['field_label_value'] = list()
                        # print('initial_costing_details',initial_costing_details)
                tab_approve['tender_initial_costing_details'] = initial_costing_details
            else:
                tab_approve['tender_initial_costing_details'] = list()

        data_dict['result'] = tab_approve
        if tab_approve:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_SUCCESS
            data_dict['result'] = tab_approve
        elif len(tab_approve) == 0:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_NO_DATA
            data_dict['result'] = None
            
        else:
            data_dict['request_status'] = 0
            data_dict['msg'] = settings.MSG_ERROR
            data_dict['result'] = None
            
        tab_approve = data_dict
        return Response(tab_approve)
        
#:::::::::::::::::::Pms Tender Status :::::::::::::::::::::::::#
class TenderStatusAddOrUpdateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsTenderStatus.objects.filter(is_deleted=False)
    serializer_class = TenderStatusAddOrUpdateSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('tender',)
    # @response_modify_decorator_get_after_execution
    def get(self, request, *args, **kwargs):
        response = super(self.__class__, self).get(self, request, args, kwargs)
        data_dict = {}
        #print("response",response.data)
        for data in response.data:
            response_d_list = list()
            doc_d = custom_filter(
                self, PmsTenderStatusDocuments,
                filter_columns={'tender_status': data['id'], 'is_deleted': False},
            )
            if doc_d:
                for e_doc_d in doc_d:
                    #print('e_doc_d',e_doc_d)
                    response_d_list.append({
                        'id':e_doc_d.id,
                        'tender': e_doc_d.tender.id,
                        'tender_status':e_doc_d.tender_status.id,
                        'document_name':e_doc_d.document_name,
                        'document':request.build_absolute_uri(e_doc_d.document.url),}
                    )

            #print('doc_d',doc_d)
            data['document_details'] = response_d_list
            response_p_list=list()
            participents_fields_d = custom_filter(
                self, PmsTenderStatusParticipentsFieldLabel,
                filter_columns={'tender_status': data['id'], 'is_deleted': False},
            )
            #print('participents_fields_d',participents_fields_d)
            for e_pa_field_l_details in participents_fields_d:
                participents_f_l = dict()
                participents_f_l['id']= e_pa_field_l_details.id
                participents_f_l['tender_status'] = e_pa_field_l_details.tender_status.id
                participents_f_l['field_label'] = e_pa_field_l_details.field_label
                participents_f_l['created_by'] = e_pa_field_l_details.created_by.username
                participents_f_l['owned_by'] = e_pa_field_l_details.owned_by.username
                participents_f_v_d = PmsTenderStatusParticipentsFieldValue.objects.filter(
                    tender_status=data['id'],
                         participents_field_label=e_pa_field_l_details
                         ).values_list('field_value', flat=True)
                participents_f_l['field_value'] = participents_f_v_d
                response_p_list.append(participents_f_l)
            data['participents_field_label_value'] = response_p_list
            response_c_list = list()
            comparison_fields_d = custom_filter(
                self, PmsTenderStatusComparisonChartFieldLabel,
                filter_columns={'tender_status': data['id'], 'is_deleted': False},
            )
            # print('participents_fields_d',participents_fields_d)
            for e_co_field_l_details in comparison_fields_d:
                comparison_f_l = dict()
                comparison_f_l['id'] = e_co_field_l_details.id
                comparison_f_l['tender_status'] = e_co_field_l_details.tender_status.id
                comparison_f_l['field_label'] = e_co_field_l_details.field_label
                comparison_f_l['created_by'] = e_co_field_l_details.created_by.username
                comparison_f_l['owned_by'] = e_co_field_l_details.owned_by.username
                comparison_f_v_d = PmsTenderStatusComparisonChartFieldValue.objects.filter(
                    tender_status=data['id'],
                    status_comparison_field_label=e_co_field_l_details
                ).values_list('field_value', flat=True)
                comparison_f_l['field_value'] = comparison_f_v_d
                response_c_list.append(comparison_f_l)
            data['comparison_field_label_value'] = response_c_list

        # data_dict['result'] = response.data[0]
        if response.data:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_SUCCESS
            data_dict['result'] = response.data[0]
        elif len(response.data) == 0:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_NO_DATA
            data_dict['result'] = None
            
        else:
            data_dict['request_status'] = 0
            data_dict['msg'] = settings.MSG_ERROR
            data_dict['result'] = None
            
        response.data = data_dict
        return response

class TenderStatParticipentsUploadFView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    def post(self, request, format=None):
        try:
            document = request.data['participents_document']
            field_label_value = []
            import xlrd
            df1 = pd.read_excel(document) #read excel
            df2 = df1.replace(np.nan,'',regex=True) # for replace blank value with nan
            df =df2.loc[:, ~df2.columns.str.contains('^Unnamed')] # for elmeminate the blank index
            for j in df.columns:
                field_value = []
                for i in df.index:
                    field_value.append(df[j][i])
                field_label_val_dict = {
                        "field_label":j,
                        "field_value":field_value
                        }
                field_label_value.append(field_label_val_dict)
            response_data={
                "tender":request.data['tender'],
                "participents_field_label_value":field_label_value
            }
            return Response(response_data)
        except Exception as e:
            raise APIException(
                {
                    'request_status': 0,
                    'msg': 'Check your file type',
                    'orginal_error': e
                }
            )
class TenderStatComparisonUploadFView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    def post(self, request, format=None):
        try:
            document = request.data['comparison_document']
            field_label_value = []
            import xlrd
            df1 = pd.read_excel(document) #read excel
            df2 = df1.replace(np.nan,'',regex=True) # for replace blank value with nan
            df =df2.loc[:, ~df2.columns.str.contains('^Unnamed')] # for elmeminate the blank index
            for j in df.columns:
                field_value = []
                for i in df.index:
                    field_value.append(df[j][i])
                field_label_val_dict = {
                        "field_label":j,
                        "field_value":field_value
                        }
                field_label_value.append(field_label_val_dict)
            response_data={
                "tender":request.data['tender'],
                "comparison_field_label_value":field_label_value
                    }
            return Response(response_data)
        except Exception as e:
            raise APIException(
                {
                    'request_status': 0,
                    'msg': 'Check your file type',
                    'orginal_error': e
                }
            )
class TenderStatDocumentAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsTenderStatusDocuments.objects.all()
    serializer_class = TenderStatusDocumentAddSerializer
class TenderStatDocumentEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsTenderStatusDocuments.objects.all()
    serializer_class = TenderStatusDocumentEditSerializer
class TenderStatDocumentDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsTenderStatusDocuments.objects.all()
    serializer_class = TenderStatusDocumentDeleteSerializer

class TenderTpeMasterAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = TenderTpeMasterAddSerializer
    queryset = PmsTenderTypeMaster.objects.filter(is_deleted=False)