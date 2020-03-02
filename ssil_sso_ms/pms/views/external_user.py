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
from pagination import CSLimitOffestpagination,CSPageNumberPagination,OnOffPagination
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

from rest_framework.parsers import MultiPartParser
from django.core.files.storage import FileSystemStorage
import shutil

#:::::::::::::::::  PMS External Users Type ::::::::::::::::::::#
class ExternalUsersTypeAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsExternalUsersType.objects.filter(is_deleted=False).order_by('-id')
    serializer_class = ExternalUsersTypeAddSerializer
class ExternalUsersListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsExternalUsers.objects.filter(is_deleted=False).order_by('-id')
    serializer_class = ExternalUsersListSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('user_type','user_type__type_name')
    pagination_class = OnOffPagination
    ##Develop by Manas Paul 12Jul19
    def get_queryset(self):
        project_id=self.request.query_params.get('project_id', None)
        # user_type__type_name=self.request.query_params.get('user_type__type_name', None)
        if project_id:
            tender_id = PmsProjects.objects.only('tender').get(id=project_id,is_deleted=False).tender
            getTenderDetails = PmsExternalUsersExtraDetailsTenderMapping.objects.filter(tender_id=tender_id)
            exter_user_list = []
            for g_t_d in getTenderDetails:
                exter_user_list.append(g_t_d.external_user.id)
            # print("exter_user_list-->",exter_user_list)
            return self.queryset.filter(id__in = exter_user_list )
        else:
            return self.queryset

    @response_modify_decorator_list_or_get_before_execution_for_onoff_pagination
    def get(self, request, *args, **kwargs):
        return response

class ExternalUsersListWithPaginationView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    pagination_class = CSPageNumberPagination
    queryset = PmsExternalUsers.objects.filter(is_deleted=False).order_by('-id')
    serializer_class = ExternalUsersListWithPaginationSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('user_type','user_type__type_name')

    ##Develop by Manas Paul 12Jul19
    def get_queryset(self):
        project_id=self.request.query_params.get('project_id', None)
        # user_type__type_name=self.request.query_params.get('user_type__type_name', None)
        if project_id:
            tender_id = PmsProjects.objects.only('tender').get(id=project_id,is_deleted=False).tender
            getTenderDetails = PmsExternalUsersExtraDetailsTenderMapping.objects.filter(tender_id=tender_id)
            exter_user_list = []
            for g_t_d in getTenderDetails:
                exter_user_list.append(g_t_d.external_user.id)
            # print("exter_user_list-->",exter_user_list)
            return self.queryset.filter(id__in = exter_user_list )
        else:
            return self.queryset

class ExternalUsersTypeEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsExternalUsersType.objects.all()
    serializer_class = ExternalUsersTypeEditSerializer
class ExternalUsersTypeDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsExternalUsersType.objects.all()
    serializer_class = ExternalUsersTypeDeleteSerializer

#:::::::::::::::::  PmsExternalUsers ::::::::::::::::::::#
class ExternalUsersAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsExternalUsers.objects.filter(is_deleted=False).order_by('-id')
    serializer_class = ExternalUsersAddSerializer

class ExternalUsersEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsExternalUsers.objects.all()
    serializer_class = ExternalUsersEditSerializer
class ExternalUsersDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsExternalUsers.objects.all()
    serializer_class =  ExternalUsersDeleteSerializer
class ExternalUsersDocumentAddView(generics.ListCreateAPIView):
	permission_classes = [IsAuthenticated]
	authentication_classes = [TokenAuthentication]
	queryset = PmsExternalUsersDocument.objects.all()
	serializer_class = ExternalUsersDocumentAddSerializer
class ExternalUsersDocumentEditView(generics.RetrieveUpdateAPIView):
	permission_classes = [IsAuthenticated]
	authentication_classes = [TokenAuthentication]
	queryset = PmsExternalUsersDocument.objects.all()
	serializer_class = ExternalUsersDocumentEditSerializer
class ExternalUsersDocumentDeleteView(generics.RetrieveUpdateAPIView):
	permission_classes = [IsAuthenticated]
	authentication_classes = [TokenAuthentication]
	queryset = PmsExternalUsersDocument.objects.all()
	serializer_class = ExternalUsersDocumentDeleteSerializer
class ExternalUsersDocumentListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    # queryset = PmsExternalUsersDocument.objects.all()
    serializer_class = ExternalUsersDocumentListSerializer
    def get_queryset(self):
        external_user_id = self.kwargs['external_user_id']
        queryset = PmsExternalUsersDocument.objects.filter(external_user_id=external_user_id,is_deleted=False).order_by('-id')
        return queryset
class VendorDetailsExcelFileAddView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    @response_modify_decorator_post  
    def post(self, request, format=None):
        try:
            # import pandas as pd 
            import xlrd
            # document = request.data['document']
            # print("doc",document)
            # url = '/home/koushik/Desktop/zvend(3700).xlsx'
            ########
            print("request.FILES",request.FILES['document'])
            # to access data
            print("(request.data)",request.data)

            # file_obj = request.data['file']
            file_obj = request.FILES['document']
            print("file_obj",file_obj)
            fs = FileSystemStorage(location="media/vendor_excel")
            print("fs",fs)
            filename = fs.save(file_obj.name, file_obj)
            print("filename",filename)
            file_url = fs.url('vendor_excel/'+filename).replace('/media','media')
            print("file_url",file_url)

            ##########
            # url =document
            wb = xlrd.open_workbook(file_url)
            print("wb",wb)
            sh = wb.sheet_by_index(0)
            a=[]
            # data = pd.read_excel(url,index_col=1)
            # data.dropna(axis=0, how='any', thresh=None, subset=None, inplace=False)
            # print(data.head())
            for i in range(sh.nrows):
                for j in range(sh.ncols):
                    if sh.cell_value(i,j) == 'Vendor':
                        skip_row=i
                        for i in range(0,skip_row):
                            a.append(i)
                        data = pd.read_excel(file_url,skiprows=skip_row,usecols=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,27,37],converters={'Pan No.':str,'IFSC Code':str})
                        data=data.replace(np.nan,'',regex=True)
                        # print(data.head())
            # print('data',data)

            # document = request.data['document']
            # # print('document',document)
            # data=pd.read_excel(document,converters={'Vendor':str})
            # # print('data',data)
            # data.columns = data.columns.str.replace('Unnamed.*', '')
            # data = data.replace(np.nan,'',regex=True)           
            # print('data',data)

            logdin_user_id = self.request.user.id
            # print('logdin_user_id',logdin_user_id)
            blank_vendor_code_list=[]
            duplicate_vendor_code_list=[]
            total_result={}
            state_filter={}
            pan_filter={}
            ifsc_filter={}
            with transaction.atomic():
                for index, row in data.iterrows():
                    if row['Vendor'] == '':
                        blank_vendor_code_dict={
                            'vendor_code':row['Vendor'],
                            'organisation_name':row['Name'],
                            'gst_no':row['GSTIN No.'],
                            'pan_no':row['Pan No.'],
                            'bank_name':row['Bank Name'],
                            'bank_ac_no':row['Bank A/c No.'],
                            'ifsc_code':row['IFSC Code'],       
                        }
                        blank_vendor_code_list.append(blank_vendor_code_dict) 
                    else:
                        name=row['Name'] if row['Name'] else ''
                        email=row['Email Address'] if row['Email Address'] else ''
                        gst_no=row['GSTIN No.'] if row['GSTIN No.'] else ''

                        pan_no=row['Pan No.'] if row['Pan No.'] else ''
                        # print('pan_no',pan_no,len(pan_no))
                        if len(pan_no)== 10:
                            pan_filter['pan_no']=pan_no
                        else:
                            pan_filter['pan_no']=''

                        bank_name=row['Bank Name'] if row['Bank Name'] else ''
                        bank_ac_no=row['Bank A/c No.'] if row['Bank A/c No.'] else ''

                        ifsc_code=row['IFSC Code'] if row['IFSC Code'] else ''
                        # print('ifsc_code',ifsc_code,len(ifsc_code))
                        if len(ifsc_code) == 11:
                            ifsc_filter['ifsc_code']=ifsc_code
                        else:
                            ifsc_filter['ifsc_code']=''
                      
                        house_no=row['House No.'] if row['House No.'] else ''
                        street =row['Street'] if row['Street'] else ''
                        street_2 =row['Street2'] if row['Street2'] else ''
                        street_3 =row['Street3'] if row['Street3'] else ''
                        street_4 =row['Street4'] if row['Street4'] else ''
                        district=row['District'] if row['District'] else ''
                        city=row['City'] if row['City'] else ''
                        postal_code=row['Postal Code'] if row['Postal Code'] else ''
                        region=row['Region'] if row['Region'] else ''
                        vendor_classified_text=row['Vendor Classif. text'] if row['Vendor Classif. text'] else ''

                        state=row['State'] if row['State']  else ''
                        # print('state',state)
                        state_detail=TCoreState.objects.filter(cs_state_name=state.lower(),cs_is_deleted=False)
                        if state_detail:
                            for s_d in state_detail:
                                state_filter['state_id']=s_d.id
                        else:
                            state_filter['state_id']=None

                        address="House No:-"+str(house_no)+",Street:-"+str(street)+",Street2:-"+str(street_2)+",Street3:-"+str(street_3)+",Street4:-"+str(street_4)+",District:-"+str(district)+",City:-"+str(city)+",Postal Code-"+str(postal_code)       
                        # print('address',address)
                        
                        if PmsExternalUsers.objects.filter(code=row['Vendor'],is_deleted=False).count() == 0:
                            vendors_entry=PmsExternalUsers.objects.create(user_type_id=2,
                                                                          code=row['Vendor'],
                                                                          organisation_name=name,
                                                                          contact_person_name=name,
                                                                          email=email,
                                                                          gst_no=gst_no,
                                                                          **pan_filter,
                                                                          bank_name=bank_name,
                                                                          bank_ac_no=bank_ac_no,
                                                                          **ifsc_filter,
                                                                          address=str(address),
                                                                          created_by_id=logdin_user_id,
                                                                          owned_by_id=logdin_user_id,
                                                                          region=region,
                                                                          vendor_classified_text=vendor_classified_text,
                                                                          **state_filter
                                                                        )
                        else:
                            duplicate_vendor_code={
                                'vendor_code':row['Vendor'],
                                'organisation_name':row['Name'],
                                'gst_no':gst_no,
                                'pan_no':pan_no,
                                'bank_name':bank_name,
                                'bank_ac_no':bank_ac_no,
                                'ifsc_code':ifsc_code,
                            }
                            duplicate_vendor_code_list.append(duplicate_vendor_code)

                    total_result['blank_vendor_code_list']=blank_vendor_code_list
                    total_result['duplicate_vendor_code_list']=duplicate_vendor_code_list
                return Response(total_result)
        except Exception as e:
            raise APIException({'msg':settings.MSG_ERROR,
                                'error':e,
                                "request_status": 0
                                })
