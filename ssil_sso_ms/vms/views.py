from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from vms.models import *
from vms.serializers import *
from vms.vms_pagination import CSLimitOffestpagination,CSPageNumberVmsPagination
from rest_framework.views import APIView
from django.conf import settings
from rest_framework import filters
from datetime import datetime,timedelta
import collections
from rest_framework.exceptions import APIException
from pagination import *
from master.serializers import UserModuleWiseListSerializer
from master.models import TMasterModuleRole
from users.models import TCoreUserDetail
from rest_framework.response import Response
from custom_decorator import *
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend

import pandas as pd
import numpy as np
from datetime import datetime
import functools
import operator


#:::::::::::::::::::::: VMS FLOOR DETAILS MASTER:::::::::::::::::::::::::::#
class FloorDetailsMasterAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = VmsFloorDetailsMaster.objects.filter(is_deleted=False)
    serializer_class = FloorDetailsMasterAddSerializer

    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response

class FloorDetailsMasterEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = VmsFloorDetailsMaster.objects.all()
    serializer_class = FloorDetailsMasterEditSerializer

class FloorDetailsMasterDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = VmsFloorDetailsMaster.objects.all()
    serializer_class = FloorDetailsMasterDeleteSerializer

#:::::::::::::::::::::: VMS CARD DETAILS MASTER:::::::::::::::::::::::::::#
class CardDetailsMasterAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = VmsCardDetailsMaster.objects.filter(is_deleted=False)
    serializer_class = CardDetailsMasterAddSerializer
    pagination_class = CSPageNumberPagination
    # filter_backends = (DjangoFilterBackend,)
    # filterset_fields = ('card_no','card_friendly_no', 'card_current_status','status','report_arise',)
    #?report_arise=False&status=True&card_current_status=1#
    #only use in getting cards data in Visit add API#
    
    @response_modify_decorator_post
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_queryset(self):
        field_name = self.request.query_params.get('field_name', None)
        order_by = self.request.query_params.get('order_by', None)
        card_no = self.request.query_params.get('card_no', None)
        sort_field = 'card_no'
        
        if field_name and order_by:
            # if field_name == 'sort_card_no' and order_by == 'asc':
            #     queryset = self.queryset.filter(is_deleted=False).order_by('card_no')
            #     return queryset
            # elif field_name == 'sort_card_no' and order_by == 'desc':
            #     queryset = self.queryset.filter(is_deleted=False).order_by('-card_no')
            #     return queryset
            if field_name =='sort_card_no' and order_by=='asc':
                sort_field = 'card_no'
            elif field_name =='sort_card_no' and order_by=='desc':
                sort_field = '-card_no'
        if card_no:
            return self.queryset.filter(card_no__icontains=card_no).order_by(sort_field)
                 
        else:
            return self.queryset.order_by(sort_field)

    @response_modify_decorator_list_or_get_after_execution_for_pagination
    def get(self, request, *args, **kwargs):
        response=super(CardDetailsMasterAddView,self).get(self, request, args, kwargs)
        print("response.data['results']",response.data['results'])
        if response.data['results']:
            for data in response.data['results']:
                # print('data',data)
                card_floor_det=VmsCardAndFloorMapping.objects.filter(card_id=data['id'],status=True,is_deleted=False)
                print('card_floor_det',card_floor_det)
                card_floor_list=[]
                if card_floor_det:
                    for c_f in card_floor_det:
                        c_f_dict={
                            'id':c_f.id,
                            'card_id':c_f.card.id,
                            'floor_id':c_f.floor.id,
                        }
                        floor_det=VmsFloorDetailsMaster.objects.filter(id=c_f.floor.id,is_deleted=False)
                        if floor_det:
                            for f_d in floor_det:
                                c_f_dict[ 'floor_name']=f_d.floor_name
                        else:
                            c_f_dict[ 'floor_name']=None
                                        
                        card_floor_list.append(c_f_dict)
                    data['floor_details']=card_floor_list
                else:
                    data['floor_details']=[]
        return response
class CardDetailsMasterEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = VmsCardDetailsMaster.objects.all()
    serializer_class = CardDetailsMasterEditSerializer

class CardAndFloorEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = VmsCardDetailsMaster.objects.all()
    serializer_class = CardAndFloorEditSerializer

    @response_modify_decorator_update
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @response_modify_decorator_get_after_execution
    def get(self, request, *args, **kwargs):
        response=super(CardAndFloorEditView,self).get(self, request, args, kwargs)
        print('response',response.data)
        card_floor_det=VmsCardAndFloorMapping.objects.filter(card_id=response.data['id'],status=True,is_deleted=False)
        print('card_floor_det',card_floor_det)
        card_floor_list=[]
        for c_f in card_floor_det:
            floor_det=VmsFloorDetailsMaster.objects.only('floor_name').get(id=c_f.floor.id,is_deleted=False).floor_name
            c_f_dict={
                'id':c_f.id,
                'card_id':c_f.card.id,
                'floor_id':c_f.floor.id,
                'floor_name':floor_det
            }
            card_floor_list.append(c_f_dict)
        response.data['floor_details']=card_floor_list
        return response

class CardDetailsMasterDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = VmsCardDetailsMaster.objects.all()
    serializer_class = CardDetailsMasterDeleteSerializer

    @response_modify_decorator_update
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

class AvailableCardsListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = VmsCardDetailsMaster.objects.filter(report_arise=False,
                                                is_deleted=False,
                                                status=True,
                                                card_current_status=1)
    serializer_class = AvailableCardsListSerializer

    def get_queryset(self):
        card_filter={}
        floor=self.request.query_params.get('floor',None)
        search=self.request.query_params.get('search',None)
        field_name=self.request.query_params.get('field_name', None)
        order_by = self.request.query_params.get('order_by', None)
        sort_field = 'card_no'
        all_queryset=VmsCardDetailsMaster.objects.none()
        floor_queryset=VmsCardDetailsMaster.objects.none()


        if field_name and order_by:
            if field_name =='card_no' and order_by=='asc':
                sort_field = 'card_no'
            elif field_name =='card_no' and order_by=='desc':
                sort_field = '-card_no'
            
        if floor:
            floor_list=floor.split(',')
            

            # for floor_id in floor_list:
            #     flo = floor=floor_id+'&'

            available_cards=VmsCardAndFloorMapping.objects.filter(
                            (Q(floor__floor_name="All Floor") | Q(floor__in=floor_list)),
                            is_deleted=False).values('card')

            if available_cards:
                cards_list = [x['card'] for x in available_cards]
                card_filter['id__in'] = cards_list
            else:
                card_filter['id__in'] = []

            floor_queryset=self.queryset.filter(**card_filter)
            # return self.queryset.filter(**card_filter)
        if search:
            name=search.split(',')
            for i in name:

                queryset=self.queryset.filter(Q(card_no__icontains=i)|
                                            Q(card_friendly_no__icontains=i))
                all_queryset=(all_queryset|queryset)
            # return queryset
        all_queryset=(all_queryset|floor_queryset)
        
        if all_queryset:
            return all_queryset.order_by(sort_field)
        else:
            return self.queryset.order_by(sort_field)
           

    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response

            


#:::::::::::::::::::::: VMS VISITOR DETAILS:::::::::::::::::::::::::::#
class VisitorDetailsAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = VmsVisitorDetails.objects.filter(is_deleted=False)
    serializer_class = VisitorDetailsAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('phone_no',)
    def get(self, request, *args, **kwargs):
        data_dict = {}
        response = super(VisitorDetailsAddView, self).get(request, args, kwargs)
        data_dict['result'] = {}
        if response.data:
            data_dict['result'] = response.data[-1]
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

class VisitorDetailsListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = VmsVisitorDetails.objects.all()
    serializer_class = VisitorDetailsListSerializer
    pagination_class = CSPageNumberVmsPagination

    def get_queryset(self):
        visitor_filter = {}
        filter = {}
        aa = 0
        name_or_no = self.request.query_params.get('name_or_no', None)
        organization = self.request.query_params.get('organization', None)
        field_name = self.request.query_params.get('field_name', None)
        order_by = self.request.query_params.get('order_by', None)
        visit_type = self.request.query_params.get('visit_type', None)
        sort_field = "-id"

        if field_name and order_by:
            if field_name == 'sort_name' and order_by == 'asc':
                sort_field = 'name'
            elif field_name == 'sort_name' and order_by == 'desc':
                sort_field = '-name'

        if name_or_no:
            visitor_filter['name__icontains'] = name_or_no

        #:: On going = 1 :: Complited = 2 :: Drop-off = 3 ::#
        if visit_type:
            visit_type_list = visit_type.split(',')
            if len(visit_type_list)<3:
                if '3' in visit_type_list:
                    if '1' in visit_type_list:
                        print("if '1' in visit_type_list:")
                        filter['logout_time__isnull'] = True

                    elif '2' in visit_type_list:
                        aa = 1               #only conditions for running Complited and Drop-off
                    else:
                        filter['drop_off_time__isnull'] = False

                elif '2' in visit_type_list:
                    if '1' in visit_type_list:
                        filter['drop_off_time__isnull'] = True
                    else:
                        filter['logout_time__isnull'] = False
                        filter['drop_off_time__isnull'] = True

                elif '1' in visit_type_list:
                    filter['logout_time__isnull'] = True
                    filter['drop_off_time__isnull'] = True

        print("filter",filter, aa)
        if filter and aa ==1:
            visitor = VmsVisit.objects.filter(Q(is_deleted=False) & Q(logout_time__isnull=False) |
                                            Q(drop_off_time__isnull=False) & Q(**filter)).values('visitor')
        elif filter:
            visitor = VmsVisit.objects.filter(is_deleted=False,**filter).values('visitor')
        elif aa==1:
            visitor = VmsVisit.objects.filter(Q(is_deleted=False) & Q(logout_time__isnull=False) |
                                            Q(drop_off_time__isnull=False)).values('visitor')
        else:
            # print("field",field)
            visitor = VmsVisit.objects.filter(is_deleted=False).values('visitor')

        if visitor:
            visitor_list = [x['visitor'] for x in visitor]
            visitor_filter['id__in'] = visitor_list
        else:
            visitor_filter['id__in'] = []

        if organization:
            organization_list = organization.split(",")
            visitor_filter['organization__in'] = organization_list

        if visitor_filter:
            print("visitor_filter",visitor_filter)
            queryset = self.queryset.filter(is_deleted=False,**visitor_filter).order_by(sort_field)
            return queryset

        else:
            # queryset = self.queryset.filter(is_deleted=False).order_by(sort_field)
            queryset = VmsVisit.objects.none()
            return queryset

    def list(self, request, *args, **kwargs):
        response = super(VisitorDetailsListView, self).list(request,args,kwargs)

        if response.data['results']:
            response.data['request_status'] = 1
            response.data['msg'] = settings.MSG_SUCCESS
        elif len(response.data['results']) ==0:
            response.data['request_status'] = 1
            response.data['msg'] = settings.MSG_NO_DATA
        else:
            response.data['request_status'] = 0
            response.data['msg'] = settings.MSG_ERROR

        return response

class VisitorDetailsListForVisitorEntryView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = VmsVisitorDetails.objects.all()
    serializer_class = VisitorDetailsListForVisitorEntrySerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name', 'phone_no','email','address','picture','organization')

    @response_modify_decorator_list
    def list(self, request, *args, **kwargs):
        return response


class VisitorDetailsEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = VmsVisitorDetails.objects.all()
    serializer_class = VisitorDetailsEditSerializer

class VisitorDetailsDeactivateView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = VmsVisitorDetails.objects.all()
    serializer_class = VisitorDetailsDeactivateSerializer

class OrganizationListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = VmsVisitorDetails.objects.all()
    serializer_class = OrganizationListSerializer
    # @response_modify_decorator_get 
    def get(self, request, *args, **kwargs):
        respone=super(OrganizationListView, self).get(request, args, kwargs)
        # print('respone',respone.data)
        org_list=set([x['organization'] for x in respone.data])
        # print('org_list',org_list)
        
        return Response({"organization_list":org_list})

#:::::::::::::::::::: USER DETAILS :::::::::::::::::::::::::#
class UserDetailsListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = TCoreUserDetail.objects.filter(cu_is_deleted=False)
    serializer_class = UserDetailsListSerializer

#:::::::::::::::::::::: VMS VISITOR TYPE MASTER:::::::::::::::::::::::::::#
class VisitorTypeMasterAddView(generics.ListCreateAPIView):
	permission_classes = [IsAuthenticated]
	authentication_classes = [TokenAuthentication]
	queryset = VmsVisitorTypeMaster.objects.all()
	serializer_class = VisitorTypeMasterAddSerializer


class VisitorTypeMasterEditView(generics.RetrieveUpdateAPIView):
	permission_classes = [IsAuthenticated]
	authentication_classes = [TokenAuthentication]
	queryset = VmsVisitorTypeMaster.objects.all()
	serializer_class = VisitorTypeMasterEditSerializer


class VisitorTypeMasterDeleteView(generics.RetrieveUpdateAPIView):
	permission_classes = [IsAuthenticated]
	authentication_classes = [TokenAuthentication]
	queryset = VmsVisitorTypeMaster.objects.all()
	serializer_class = VisitorTypeMasterDeleteSerializer

#:::::::::::::::::::::: VMS VISIT:::::::::::::::::::::::::::#
class VisitAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = VmsVisit.objects.all()
    serializer_class = VisitAddSerializer

class VisitListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = VmsVisit.objects.all()
    serializer_class = VisitListSerializer
    pagination_class = CSPageNumberVmsPagination

    def get_queryset(self):
        filter = {}
        new_filter = {}
        or_filter = []
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        search = self.request.query_params.get('search', None)
        visit_type = self.request.query_params.get('visit_type', None)
        floor = self.request.query_params.get('floor', None)
        field_name = self.request.query_params.get('field_name', None)
        order_by = self.request.query_params.get('order_by', None)
        visitor_id = self.request.query_params.get('visitor_id', None)
        aa = 0
        sort_field = '-id'

        new_filter['visitor__status'] = True

        if visitor_id:
            new_filter['visitor__id']=visitor_id

        if field_name and order_by:
            if field_name == 'sort_name' and order_by == 'asc':
                sort_field = 'visitor__name'
            elif field_name == 'sort_name' and order_by == 'desc':
                sort_field = '-visitor__name'
            elif field_name == 'sort_date' and order_by == 'asc':
                sort_field = 'created_at'
            elif field_name == 'sort_date' and order_by == 'desc':
                sort_field = '-created_at'

        if start_date and end_date:
            start_object = datetime.strptime(start_date, '%Y-%m-%d')
            end_object = datetime.strptime(end_date, '%Y-%m-%d')
            new_filter['created_at__date__gte']= start_object
            new_filter['created_at__date__lte']= end_object
        if search:
            if '@' in search:
                new_filter['visitor__email__icontains'] = search
                search = ''
                or_filter = [Q(**{'visitor__name__icontains':search}),Q(**{'visitor__organization__icontains':search}),
                            Q(**{'visitor__address__icontains':search})]
            elif search.isdigit():
                new_filter['visitor__phone_no__icontains'] = search
                search = ''
                or_filter = [Q(**{'visitor__name__icontains':search}),Q(**{'visitor__organization__icontains':search}),
                            Q(**{'visitor__address__icontains':search})]
            else:
                or_filter = [Q(**{'visitor__name__icontains':search}),Q(**{'visitor__organization__icontains':search}),
                            Q(**{'visitor__address__icontains':search})]
                # or_filter = [Q(**{'visitor__name__icontains':search}),Q(**{'visitor__address__icontains':search})]
                print("or_filter",or_filter)
                # or_filter['visitor__name__icontains'] = search
                # or_filter['visitor__organization__icontains'] = search
        else:
            or_filter = [Q(**{'visitor__name__icontains':''}),Q(**{'visitor__organization__icontains':''}),
                            Q(**{'visitor__address__icontains':''})]


        if floor:
            floor_list = floor.split(",")
            visit_floor = VmsFloorVisitor.objects.filter(floor__in=floor_list).values('visit')
            if visit_floor:
                visit_floor_list = [x['visit'] for x in visit_floor]
                new_filter['id__in'] = visit_floor_list
            else:
                new_filter['id__in'] = [0]

        #:: On going = 1 :: Complited = 2 :: Drop-off = 3 ::#
        if visit_type:
            visit_type_list = visit_type.split(',')
            if len(visit_type_list)<3:
                if '3' in visit_type_list:
                    if '1' in visit_type_list:
                        filter['logout_time__isnull'] = True

                    elif '2' in visit_type_list:
                        aa = 1               #only conditions for running Complited and Drop-off
                    else:
                        filter['drop_off_time__isnull'] = False

                elif '2' in visit_type_list:
                    if '1' in visit_type_list:
                        filter['drop_off_time__isnull'] = True
                    else:
                        filter['logout_time__isnull'] = False
                        filter['drop_off_time__isnull'] = True

                elif '1' in visit_type_list:
                    filter['logout_time__isnull'] = True
                    filter['drop_off_time__isnull'] = True

        # print('filter',filter)
        print("new_filter",new_filter)
        print("or_filter",or_filter)

        if filter and aa ==1:
            queryset = self.queryset.filter(functools.reduce(operator.or_,or_filter),Q(is_deleted=False) & Q(logout_time__isnull=False) |
                                            Q(drop_off_time__isnull=False) & Q(**filter) & Q(**new_filter)).order_by(sort_field)
            return queryset
        elif filter:
            queryset = self.queryset.filter(functools.reduce(operator.or_,or_filter),is_deleted=False,**filter,**new_filter).order_by(sort_field)
            return queryset
        elif aa==1:
            queryset = self.queryset.filter(functools.reduce(operator.or_,or_filter),(Q(is_deleted=False) & Q(logout_time__isnull=False) |
                                            Q(drop_off_time__isnull=False) & Q(**new_filter))).order_by(sort_field)
            return queryset
        else:
            queryset = self.queryset.filter(functools.reduce(operator.or_,or_filter),is_deleted=False,**new_filter).order_by(sort_field)
            return queryset

    def list(self, request, *args, **kwargs):
        response = super(VisitListView, self).list(request,args,kwargs)

        if response.data['results']:
            response.data['request_status'] = 1
            response.data['msg'] = settings.MSG_SUCCESS
        elif len(response.data['results']) ==0:
            response.data['request_status'] = 1
            response.data['msg'] = settings.MSG_NO_DATA
        else:
            response.data['request_status'] = 0
            response.data['msg'] = settings.MSG_ERROR

        return response

class VisitEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = VmsVisit.objects.all()
    serializer_class = VisitEditSerializer

class VisitLogoutView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = VmsVisit.objects.all()
    serializer_class = VisitLogoutSerializer

class VisitDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = VmsVisit.objects.all()
    serializer_class = VisitDeleteSerializer

class VisitListByVisitorIdView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = VmsVisit.objects.all()
    serializer_class = VisitListSerializer
    pagination_class = CSPageNumberVmsPagination

    def get_queryset(self):
        visitor_id = self.kwargs['visitor_id']
        # parent_id = self.kwargs['parent_id']
        return VmsVisit.objects.filter(visitor_id=visitor_id, is_deleted=False).order_by('-id')


#:::::::::::::::::: DOCUMENTS UPLOAD ::::::::::::::::::::::::#
class VmsFileUpload(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    def post(self, request):
        # import openpyxl

        # print("lhblbh")
        # path = "/home/nooralam/Desktop/book.xlsx"

        import pandas as pd 
        import xlrd
        # url = '/home/nooralam/Desktop/book.xlsx'
        url = '/home/nooralam/Desktop/attend_08_07_19_new.xlsx'
        print("url",url)
        # try:
        #     wb = xlrd.open_workbook(url)
        #     print("wb",wb)
        # except xlrd.biffh.XLRDError:
        #     print("XLRDError occure")
        wb = xlrd.open_workbook(url)
        print("wb",wb)
        if wb:
            sh = wb.sheet_by_index(0)
            print("sh",sh)
        else:
            print("exit")
            exit()
        a=[]
        for i in range(sh.nrows):
            for j in range(sh.ncols):
                if sh.cell_value(i,j) == 'Date':
                    skip_row=i
                    for i in range(0,skip_row):
                        a.append(i)
                    data = pd.read_excel(url,skiprows=skip_row)
                    # print(data.head())
        data1 = pd.DataFrame(data)
        total_punch = []
        for index, row in data.iterrows():
            if row['Department'] == 'Visitor':
                print("Gate",row['Gate'])
                # print(row['Date'])
                # print(row['Time'])
                date_time = row['Date']+'T'+row['Time']
                date_time_format = datetime.strptime(date_time, "%d/%m/%YT%H:%M:%S")
                print("date_time",date_time_format)
                visit_details = VmsVisit.objects.filter(visitor_type=1,card__card_no=str(row['Cardid']),login_time__lte=date_time_format,logout_time__gte=date_time_format)
                # print("visit", type(visit[0].__dict__['card_id']))
                # print("visit", visit_details)
                if visit_details:
                    for visit in visit_details:
                        print("visit", visit.id)
                        visit_punch, created = VmsVisitorPunching.objects.get_or_create(visit=visit,gate=row['Gate'],time=date_time_format)
                        print("visit_punch",visit_punch)
                        total_punch.append(visit_punch.id)
        print("total_punch",total_punch)
        return Response(total_punch)


