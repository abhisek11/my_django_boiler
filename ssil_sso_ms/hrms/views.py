from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from hrms.models import *
from hrms.serializers import *
from pagination import CSLimitOffestpagination,CSPageNumberPagination,OnOffPagination
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
from custom_exception_message import *
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
from global_function import userdetails,department,designation
from django.contrib.admin.models import LogEntry
from global_function import userdetails
import time
# Create your views here.

#:::::::::::::::::::::: HRMS BENEFITS PROVIDED:::::::::::::::::::::::::::#
class BenefitsProvidedAddView(generics.ListCreateAPIView):
	permission_classes = [IsAuthenticated]
	authentication_classes = [TokenAuthentication]
	queryset = HrmsBenefitsProvided.objects.all()
	serializer_class = BenefitsProvidedAddSerializer


class BenefitsProvidedEditView(generics.RetrieveUpdateAPIView):
	permission_classes = [IsAuthenticated]
	authentication_classes = [TokenAuthentication]
	queryset = HrmsBenefitsProvided.objects.all()
	serializer_class = BenefitsProvidedEditSerializer


class BenefitsProvidedDeleteView(generics.RetrieveUpdateAPIView):
	permission_classes = [IsAuthenticated]
	authentication_classes = [TokenAuthentication]
	queryset = HrmsBenefitsProvided.objects.all()
	serializer_class = BenefitsProvidedDeleteSerializer

#:::::::::::::::::::::: HRMS QUALIFICATION MASTER:::::::::::::::::::::::::::#
class QualificationMasterAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = HrmsQualificationMaster.objects.filter(is_deleted=False)
    serializer_class = QualificationMasterAddSerializer
    @response_modify_decorator_get
    def get(self,request,*args,**kwargs):
        return response

class QualificationMasterEditView(generics.RetrieveUpdateAPIView):
	permission_classes = [IsAuthenticated]
	authentication_classes = [TokenAuthentication]
	queryset = HrmsQualificationMaster.objects.all()
	serializer_class = QualificationMasterEditSerializer


class QualificationMasterDeleteView(generics.RetrieveUpdateAPIView):
	permission_classes = [IsAuthenticated]
	authentication_classes = [TokenAuthentication]
	queryset = HrmsQualificationMaster.objects.all()
	serializer_class = QualificationMasterDeleteSerializer

#:::::::::::::::::::::: HRMS EMPLOYEE:::::::::::::::::::::::::::#
class EmployeeAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = User.objects.all()
    serializer_class = EmployeeAddSerializer

    def post(self, request, *args, **kwargs):
        #print('check post...',request.data)
        # username = request.data['username']
        # if User.objects.filter(username=username).count() > 0:
        #     custom_exception_message(self,'Employee Login ID')
            
        cu_emp_code = request.data['cu_emp_code']
        if TCoreUserDetail.objects.filter(cu_emp_code=cu_emp_code).count() > 0:
            custom_exception_message(self,'Employee Code')

        cu_phone_no = request.data['cu_phone_no']
        if TCoreUserDetail.objects.filter(cu_phone_no=cu_phone_no).count() > 0:
            custom_exception_message(self,'Personal Contact No. ')

        sap_personnel_no = request.data['sap_personnel_no']
        #print('sap_personnel_no',sap_personnel_no,type(sap_personnel_no))
        # Added By RUpam Hazra request in form data type
        if sap_personnel_no != 'null':
            if TCoreUserDetail.objects.filter(sap_personnel_no=sap_personnel_no).count() > 0:
                custom_exception_message(self,'SAP Personnel ID')
        
        
        cu_punch_id = request.data['cu_punch_id'] if request.data['cu_punch_id'] else None
        if TCoreUserDetail.objects.filter(cu_punch_id=cu_punch_id).count() > 0:
            custom_exception_message(self,'Punching Machine Id')
    
        return super().post(request, *args, **kwargs)

class EmployeeEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = User.objects.all()
    serializer_class = EmployeeEditSerializer
    
    @response_modify_decorator_update
    def put(self, request,*args, **kwargs):

        #print('request',request.data)
        
        user_id=self.kwargs['pk']
        #print('user_id',type(user_id))
        list_type = self.request.query_params.get('list_type', None)

        cu_emp_code = request.data['cu_emp_code']     
        if TCoreUserDetail.objects.filter(~Q(cu_user=user_id),cu_emp_code=cu_emp_code).count() > 0:
            custom_exception_message(self,'Employee Code')

        if list_type == "professional":
            sap_personnel_no = request.data['sap_personnel_no']
            if sap_personnel_no !='null':
                if TCoreUserDetail.objects.filter(~Q(cu_user=user_id),sap_personnel_no=sap_personnel_no).count() > 0:
                    custom_exception_message(self,'SAP Personnel ID')

            cu_punch_id = request.data['cu_punch_id'] if request.data['cu_punch_id'] else None
            if TCoreUserDetail.objects.filter(~Q(cu_user=user_id),cu_punch_id=cu_punch_id).count() > 0:
                custom_exception_message(self,'Punching Machine Id')

        if list_type == "personal":
            cu_phone_no = request.data['cu_phone_no']
            if TCoreUserDetail.objects.filter(~Q(cu_user=user_id),cu_phone_no=cu_phone_no).count() > 0:         
                custom_exception_message(self,'Personal Contact No. ')

            email = request.data['email']
            if User.objects.filter(~Q(id=user_id),email=email).count() > 0:
                custom_exception_message(self,'Personal Email ID')
        
        if list_type == "role":
            pass
            # cu_alt_phone_no = request.data['cu_alt_phone_no']
            # if TCoreUserDetail.objects.filter(~Q(cu_user=user_id),cu_alt_phone_no=cu_alt_phone_no).count() > 0:
            #     custom_exception_message(self,'Official Contact No.')

            # cu_alt_email_id = request.data['cu_alt_email_id']
            # if TCoreUserDetail.objects.filter(~Q(cu_user=user_id),cu_alt_email_id=cu_alt_email_id).count() > 0:
            #     custom_exception_message(self,'Official Email ID')
    
        return super().put(request, *args, **kwargs)


    def get(self, request, *args, **kwargs):
        get_id = self.kwargs['pk']
        list_type = self.request.query_params.get('list_type', None)
        module_id = self.request.query_params.get('module_id', None)
        response = User.objects.filter(id=get_id)
        data = {}
        data_dict = {}
        p_doc_dict = {}
        for user_data in response:
            data['first_name']= user_data.first_name
            data['last_name']= user_data.last_name
            if list_type == "professional":
                professional_details=TCoreUserDetail.objects.filter(
                    cu_user=user_data.id,cu_is_deleted=False
                ).values(
                    'cu_emp_code','daily_loginTime','joining_date',
                    'sap_personnel_no','daily_logoutTime','cu_punch_id',
                    'initial_ctc','current_ctc','lunch_start','lunch_end','salary_type__st_name',
                    'cost_centre','granted_cl','granted_sl','granted_el','salary_type','is_confirm','job_location_state','cu_alt_email_id')
                if professional_details:
                    data['emp_code']=professional_details[0]['cu_emp_code'] if professional_details[0]['cu_emp_code'] else None
                    data['cu_punch_id']=professional_details[0]['cu_punch_id'] if professional_details[0]['cu_punch_id'] else None
                    data['sap_personnel_no']=professional_details[0]['sap_personnel_no'] if professional_details[0]['sap_personnel_no'] else None
                    data['initial_ctc']=professional_details[0]['initial_ctc'] if professional_details[0]['initial_ctc'] else None
                    data['current_ctc']=professional_details[0]['current_ctc'] if professional_details[0]['current_ctc'] else None
                    data['cost_centre']=professional_details[0]['cost_centre'] if professional_details[0]['cost_centre'] else None
                    data['granted_cl']=professional_details[0]['granted_cl'] if professional_details[0]['granted_cl'] else None
                    data['granted_sl']=professional_details[0]['granted_sl'] if professional_details[0]['granted_sl'] else None
                    data['granted_el']=professional_details[0]['granted_el'] if professional_details[0]['granted_el'] else None
                    data['daily_loginTime']=professional_details[0]['daily_loginTime'] if professional_details[0]['daily_loginTime'] else None
                    data['daily_logoutTime']=professional_details[0]['daily_logoutTime'] if professional_details[0]['daily_logoutTime'] else None
                    data['lunch_start']=professional_details[0]['lunch_start'] if professional_details[0]['lunch_start'] else None
                    data['lunch_end']=professional_details[0]['lunch_end'] if professional_details[0]['lunch_end'] else None
                    data['joining_date']=professional_details[0]['joining_date'] if professional_details[0]['joining_date'] else None
                    data['salary_type']=professional_details[0]['salary_type'] if professional_details[0]['salary_type'] else None
                    data['salary_type_name']=professional_details[0]['salary_type__st_name'] if professional_details[0]['salary_type__st_name'] else None
                    data['is_confirm']=professional_details[0]['is_confirm'] 
                    data['job_location_state']=professional_details[0]['job_location_state'] if professional_details[0]['job_location_state'] else None
                    data['official_email_id']=professional_details[0]['cu_alt_email_id'] if professional_details[0]['cu_alt_email_id'] else None

                saturday_off=AttendenceSaturdayOffMaster.objects.filter(employee=user_data.id,is_deleted=False)
                #print('saturday_off',saturday_off)
                if saturday_off:
                    for s_o in saturday_off:
                        sat_data={
                            'id':s_o.id,
                            'first':s_o.first,
                            'second':s_o.second,
                            'third':s_o.third,
                            'fourth':s_o.fourth,
                            'all_s_day':s_o.all_s_day
                        }
                    data['saturday_off']=sat_data
                else:
                     data['saturday_off']=None       

                user_benefits=HrmsUsersBenefits.objects.filter(user=user_data.id,is_deleted=False)
                benefits_list=[]
                if user_benefits:
                    for u_b in user_benefits:
                        benefits={
                            'id':u_b.id,
                            'benefits':u_b.benefits.id,
                            'benefits_name':u_b.benefits.benefits_name,
                            'allowance':u_b.allowance
                        }
                        benefits_list.append(benefits)
                    data['benefits_provided']=benefits_list
                else:
                    data['benefits_provided'] = []
                other_facilities=HrmsUsersOtherFacilities.objects.filter(user=user_data.id,is_deleted=False)
                facilities_list=[]
                if other_facilities:
                    for o_f in other_facilities:
                        facility={
                            'id':o_f.id,
                            'other_facilities':o_f.other_facilities       
                        }
                        facilities_list.append(facility)
                    data['other_facilities']=facilities_list
                else:
                    data['other_facilities']= []
                
                initial_ctc_dict = {}                
                upload_files_dict = {}
                current_ctc_dict = {}
                professional_documents = HrmsDocument.objects.filter(user=user_data.id,is_deleted=False)
                if professional_documents:
                    upload_files_list = []
                    for doc_details in professional_documents: 
                        if (doc_details.tab_name).lower() == "professional" :
                            if doc_details.__dict__['document'] == "":
                                file_url = ''
                            else:
                                file_url = request.build_absolute_uri(doc_details.document.url)
                            if doc_details.__dict__['document_name'] == "":
                                doc_name = ''   
                            else:
                                doc_name = doc_details.document_name
                            if doc_details.field_label == "Initial CTC":
                                initial_ctc_dict = {
                                'id' : doc_details.id,
                                'document_name' : doc_name,
                                'document' : file_url
                                }
                            if doc_details.field_label == "Upload Files":
                                upload_files_dict = {
                                'id' : doc_details.id,
                                'document_name' : doc_name,
                                'document' : file_url
                                }
                                upload_files_list.append(upload_files_dict)
                            if doc_details.field_label == "Current CTC":
                                current_ctc_dict = {
                                'id' : doc_details.id,
                                'document_name' : doc_name,
                                'document' : file_url
                                }
                    data['initial_ctc_doc'] = initial_ctc_dict if initial_ctc_dict else None 
                    data['upload_files_doc'] = upload_files_list if  upload_files_list else None
                    data['current_ctc_doc'] = current_ctc_dict if current_ctc_dict else None
                    
                else:
                    data['initial_ctc_doc'] = None
                    data['upload_files_doc'] = []
                    data['current_ctc_doc'] = None
            if list_type == "role":
                role_details=TCoreUserDetail.objects.filter(cu_user=user_data.id,cu_is_deleted=False).values(
                    'cu_emp_code','cu_alt_phone_no','cu_alt_email_id','company__id','company__coc_name','job_description','hod__id','hod__first_name','hod__last_name','joining_date','termination_date',
                    'designation__id','designation__cod_name','department__id','department__cd_name','resignation_date','job_location_state','reporting_head__id','reporting_head__first_name','reporting_head__last_name','employee_grade__cg_name','employee_grade__id')
                if role_details:
                    data['emp_code']=role_details[0]['cu_emp_code'] if role_details[0]['cu_emp_code'] else None
                    data['joining_date']=role_details[0]['joining_date'] if role_details[0]['joining_date'] else None
                    data['official_contact_no']=role_details[0]['cu_alt_phone_no'] if role_details[0]['cu_alt_phone_no'] else None
                    data['official_email_id']=role_details[0]['cu_alt_email_id'] if role_details[0]['cu_alt_email_id'] else None
                    data['company']=role_details[0]['company__id'] if role_details[0]['company__id'] else None
                    data['company_name']=role_details[0]['company__coc_name'] if role_details[0]['company__coc_name'] else None
                    data['job_description']=role_details[0]['job_description'] if role_details[0]['job_description'] else None
                    data['hod_id']=role_details[0]['hod__id'] if role_details[0]['hod__id'] else None
                    hod__first_name = role_details[0]['hod__first_name'] if role_details[0]['hod__first_name'] else ''
                    hod__last_name = role_details[0]['hod__last_name'] if role_details[0]['hod__last_name'] else ''

                    data['hod']=hod__first_name+" " +hod__last_name

                    data['designation_id']=role_details[0]['designation__id'] if role_details[0]['designation__id'] else None
                    data['designation_name']=role_details[0]['designation__cod_name'] if role_details[0]['designation__cod_name'] else None
                    data['department_id']=role_details[0]['department__id'] if role_details[0]['department__id'] else None
                    data['department_name']=role_details[0]['department__cd_name'] if role_details[0]['department__cd_name'] else None

                    data['reporting_head_id']=role_details[0]['reporting_head__id'] if role_details[0]['reporting_head__id'] else None

                    reporting_head__first_name = role_details[0]['reporting_head__first_name'] if role_details[0]['reporting_head__first_name'] else ''
                    reporting_head__last_name = role_details[0]['reporting_head__last_name'] if role_details[0]['reporting_head__last_name'] else ''
                    data['reporting_head_name']= reporting_head__first_name  +" "+ reporting_head__last_name
                    # data['employee_grade_name']=role_details[0]['employee_grade__cg_name'] if role_details[0]['employee_grade__cg_name'] else None
                    # data['employee_grade_id']=role_details[0]['employee_grade__id'] if role_details[0]['employee_grade__id'] else None
                    data['termination_date']=role_details[0]['termination_date'] if role_details[0]['termination_date'] else None
                    data['resignation_date']=role_details[0]['resignation_date'] if role_details[0]['resignation_date'] else None
                    data['job_location_state']=role_details[0]['job_location_state'] if role_details[0]['job_location_state'] else None
        
                    grade_details=TCoreGrade.objects.filter(id=role_details[0]['employee_grade__id'],cg_is_deleted=False)
                    
                    if grade_details:
                        grade_details=TCoreGrade.objects.filter(id=role_details[0]['employee_grade__id'],cg_is_deleted=False)[0]
                        grade_dict = dict()
                        #print('grade_details',grade_details.id)
                        if grade_details.cg_parent_id!=0:
                            parent = TCoreGrade.objects.filter(id=grade_details.cg_parent_id,cg_is_deleted=False)
                            for p_d in parent:
                                grade_dict['id']=p_d.id
                                grade_dict['cg_name']=p_d.cg_name
                                
                            grade_dict['child'] = {
                                "id":grade_details.id,
                                "cg_name":grade_details.cg_name
                                }
                        else:
                            grade_dict['id']=grade_details.id
                            grade_dict['cg_name']=grade_details.cg_name
                            grade_dict['child'] = None

                        #print('grade_dict',grade_dict)
                          
                        data['grade_details']=grade_dict
                    else:
                        data['grade_details']=None   
            if list_type == "personal":
                personal_details=TCoreUserDetail.objects.filter(cu_user=user_data.id,cu_is_deleted=False)
                print('personal_details',personal_details)
                if personal_details:
                    for p_d in personal_details:
                        data['emp_code']=p_d.cu_emp_code
                        data['cu_phone_no']=p_d.cu_phone_no if p_d.cu_phone_no else ""
                        data['email']=p_d.cu_user.email
                        data['address']=p_d.address
                        data['joining_date']=p_d.joining_date
                        data['blood_group']=p_d.blood_group if p_d.blood_group else ''
                        data['photo']=request.build_absolute_uri(p_d.cu_profile_img.url) if p_d.cu_profile_img else None
                        data['total_experience']=p_d.total_experience
                        data['job_location_state']=p_d.job_location_state.id if p_d.job_location_state else None
                        data['job_location_state_name']=p_d.job_location_state.cs_state_name if p_d.job_location_state else None
                        data['official_email_id']=p_d.cu_alt_email_id
                                                    
                licenses_and_certifications_dict = {}
                work_experience_dict = {}
                add_more_files_dict = {}
                personal_documents = HrmsDynamicSectionFieldLabelDetailsWithDoc.objects.filter(user=user_data.id,is_deleted=False)
                print("personal_documents",personal_documents)
                if personal_documents:
                    licenses_and_certifications_list = []
                    add_more_files_list = []
                    work_experience_list = []
                    for doc_details in personal_documents: 
                        if (doc_details.tab_name).lower() == "personal" :
                            if doc_details.__dict__['document'] == "":
                                file_url = ''
                            else:
                                file_url = request.build_absolute_uri(doc_details.document.url)
                                
                            if doc_details.__dict__['document_name'] == "":
                                doc_name = ""
                            else:
                                doc_name = doc_details.document_name
                            
                            if doc_details.field_label == "Licenses and Certifications":
                                licenses_and_certifications_dict = {
                                'id' : doc_details.id,
                                'field_label_value' : doc_details.field_label_value if doc_details.field_label_value else None,
                                'document_name' : doc_name,
                                'document' : file_url
                                }
                                licenses_and_certifications_list.append(licenses_and_certifications_dict)
                            
                            if doc_details.field_label == "Work Experience":
                                work_experience_dict = {                            
                                'id' : doc_details.id,
                                'field_label_value' : doc_details.field_label_value if doc_details.field_label_value else None,
                                'document_name' : doc_name,                            
                                'document' : file_url                            
                                }                            
                                work_experience_list.append(work_experience_dict)
                    data['licenses_and_certifications_doc'] = licenses_and_certifications_list if licenses_and_certifications_list else []
                    data['work_experience_doc'] = work_experience_list if work_experience_list else []
                else:
                    data['licenses_and_certifications_doc'] = []
                    data['work_experience_doc'] = []
                academic_qualification=HrmsUserQualification.objects.filter(user=user_data.id,is_deleted=False)
                print('academic_qualification',academic_qualification)
                if academic_qualification:
                    academic_qualification_list = []
                    academic_qualification_dict = {} 
                    for a_q in academic_qualification:
                        academic_qualification_dict={
                            'id':a_q.id,
                            'qualification':a_q.qualification.id,
                            'qualification_name':a_q.qualification.name,
                            'details':a_q.details
                        }
                        academic_doc=HrmsUserQualificationDocument.objects.filter(user_qualification=a_q.id,is_deleted=False)
                        print('academic_doc',academic_doc)          
                        if academic_doc:
                            academic_doc_dict={}
                            academic_doc_list=[]
                            for a_d in academic_doc:
                                academic_doc_dict={
                                    'id':a_d.id,
                                    'document':request.build_absolute_uri(a_d.document.url)
                                }
                                academic_doc_list.append(academic_doc_dict)
                            academic_qualification_dict['qualification_doc']=academic_doc_list
                        else:
                            academic_qualification_dict['qualification_doc']=[]
                        academic_qualification_list.append(academic_qualification_dict)
                    data['academic_qualification']=academic_qualification_list
                else:
                    data['academic_qualification']=[]
                        

        data_dict['result'] = data
        if data:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_SUCCESS
        elif len(data) == 0:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_NO_DATA
        else:
            data_dict['request_status'] = 0
            data_dict['msg'] = settings.MSG_ERROR
        data = data_dict
        return Response(data)

class EmployeeListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = User.objects.filter(is_superuser=False,is_active=True).order_by('-id')
    serializer_class =EmployeeListSerializer
    pagination_class = CSPageNumberPagination
    
    

    def get_queryset(self):
        '''
            eleminate login user on employee list added by Rupam Hazra Line number 458 - 459
        '''
        login_user = self.request.user.id
        # self.queryset = self.queryset.filter(
        #     ~Q(pk=login_user),
        #     pk__in=(TMasterModuleRoleUser.objects.filter(mmr_type='3')))
        self.queryset = self.queryset.filter(
            ~Q(pk=login_user),is_active=True)
        filter = {}
        #name = self.request.query_params.get('name', None)
        field_name = self.request.query_params.get('field_name', None)
        order_by = self.request.query_params.get('order_by', None)
        search_keyword = self.request.query_params.get('search_keyword', None)

        '''
            Reason : Fetch Resignation employee list
            Author : Rupam Hazra 
            Line number:  494 - 503
            Date : 19/02/2020
        '''
        list_type = self.request.query_params.get('list_type', None)
        if list_type == 'resignation':
            cur_month = self.request.query_params.get('month', None)
            cur_year = self.request.query_params.get('year', None)
            self.queryset = self.queryset.filter(
            ~Q(pk=login_user),is_active=True,id__in=(
                TCoreUserDetail.objects.filter(
                    termination_date__year=cur_year,
                    termination_date__month=cur_month,cu_is_deleted=False
                    ).values_list('cu_user',flat=True)))

        
        if field_name and order_by:
            #print('sfsffsfsfff')
            if field_name == 'email' and order_by == 'asc':
                return self.queryset.all().order_by('email')

            if field_name == 'email' and order_by == 'desc':
                return self.queryset.all().order_by('-email')

            if field_name =='name' and order_by=='asc':
                return self.queryset.all().order_by('first_name')

            if field_name =='name' and order_by=='desc':
                return self.queryset.all().order_by('-first_name')
            
            if field_name =='grade' and order_by =='asc':
                #print('user_grade_asc',order_by)
                user_grade = TCoreUserDetail.objects.filter(
                    cu_is_deleted=False).order_by('employee_grade__cg_name')
                #print('user_grade',user_grade)
                grade_list=[]
                for u_g in user_grade:
                    grade_id= u_g.employee_grade.id if u_g.employee_grade else None
                    grade_list.append(grade_id)
                #print('grade_list',grade_list)
                clauses = ' '.join(['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(grade_list)])
                ordering = 'CASE %s END' % clauses
                queryset =  self.queryset.filter(pk__in=grade_list).extra(
                    select={'ordering': ordering}, order_by=('ordering',)
                )
                #print('queryset',queryset)
                return queryset

            if field_name =='grade' and order_by =='desc':
                #print('user_grade',order_by)
                user_grade = TCoreUserDetail.objects.filter(
                    cu_is_deleted=False).order_by('-employee_grade__cg_name')
                #print('user_grade_desc',user_grade)
                grade_list=[]
                for u_g in user_grade:
                    grade_id= u_g.employee_grade.id if u_g.employee_grade else None
                    grade_list.append(grade_id)
                #print('grade_list',grade_list)
                clauses = ' '.join(['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(grade_list)])
                ordering = 'CASE %s END' % clauses
                queryset =  self.queryset.filter(pk__in=grade_list).extra(select={'ordering': ordering}, order_by=('ordering',))
                #print('queryset',queryset)
                return queryset

            if field_name =='designation' and order_by =='desc':
                #print('user_grade',order_by)
                user_designation = TCoreUserDetail.objects.filter(
                    cu_is_deleted=False).order_by('-designation__cod_name')
                #print('user_designation_desc',user_designation)
                designation_list=[]
                for u_g in user_designation:
                    designation_id=u_g.cu_user.id
                    designation_list.append(designation_id)
                #print('designation_list',designation_list)
                clauses = ' '.join(['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(designation_list)])
                ordering = 'CASE %s END' % clauses
                queryset =  self.queryset.filter(pk__in=designation_list).extra(select={'ordering': ordering}, order_by=('ordering',))
                #print('queryset',queryset)
                return queryset
            
            if field_name =='designation' and order_by =='asc':
                #print('user_grade',order_by)
                user_designation = TCoreUserDetail.objects.filter(
                    cu_is_deleted=False).order_by('designation__cod_name')
                #print('user_designation_desc',user_designation)
                designation_list=[]
                for u_g in user_designation:
                    designation_id=u_g.cu_user.id
                    designation_list.append(designation_id)
                #print('designation_list',designation_list)
                clauses = ' '.join(['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(designation_list)])
                ordering = 'CASE %s END' % clauses
                queryset =  self.queryset.filter(pk__in=designation_list).extra(select={'ordering': ordering}, order_by=('ordering',))
                #print('queryset',queryset)
                return queryset
            
            if field_name =='department' and order_by =='asc':
                #print('user_department',order_by)
                user_department = TCoreUserDetail.objects.filter(
                    cu_is_deleted=False).order_by('department__cd_name')
                #print('user_department_asc',user_department)
                department_list=[]
                for u_g in user_department:
                    department_id=u_g.cu_user.id
                    department_list.append(department_id)
                #print('department_list',department_list)
                clauses = ' '.join(['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(department_list)])
                ordering = 'CASE %s END' % clauses
                queryset =  self.queryset.filter(pk__in=department_list).extra(select={'ordering': ordering}, order_by=('ordering',))
                #print('queryset',queryset)
                return queryset

            if field_name =='department' and order_by =='desc':
                #print('user_department',order_by)
                user_department = TCoreUserDetail.objects.filter(
                    cu_is_deleted=False).order_by('-department__cd_name')
                #print('user_department_asc',user_department)
                department_list=[]
                for u_g in user_department:
                    department_id=u_g.cu_user.id
                    department_list.append(department_id)
                #print('department_list',department_list)
                clauses = ' '.join(['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(department_list)])
                ordering = 'CASE %s END' % clauses
                queryset =  self.queryset.filter(pk__in=department_list).extra(select={'ordering': ordering}, order_by=('ordering',))
                #print('queryset',queryset)
                return queryset

            if field_name =='company' and order_by =='desc':
                #print('user_department',order_by)
                user_company = TCoreUserDetail.objects.filter(
                    cu_is_deleted=False).order_by('-company__coc_name')
                #print('user_company_asc',user_company)
                company_list=[]
                for u_g in user_company:
                    company_id=u_g.cu_user.id
                    company_list.append(company_id)
                #print('company_list',company_list)
                clauses = ' '.join(['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(company_list)])
                ordering = 'CASE %s END' % clauses 
                queryset =  self.queryset.filter(pk__in=company_list).extra(select={'ordering': ordering}, order_by=('ordering',))
                #print('queryset',queryset)
                return queryset
            
            if field_name =='company' and order_by =='asc':
                #print('user_department',order_by)
                user_company = TCoreUserDetail.objects.filter(
                    cu_is_deleted=False).order_by('company__coc_name')
                #print('user_company_asc',user_company)
                company_list=[]
                for u_g in user_company:
                    company_id=u_g.cu_user.id
                    company_list.append(company_id)
                #print('company_list',company_list)
                clauses = ' '.join(['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(company_list)])
                ordering = 'CASE %s END' % clauses
                queryset =  self.queryset.filter(pk__in=company_list).extra(select={'ordering': ordering}, order_by=('ordering',))
                #print('queryset',queryset)
                return queryset
            
            if field_name =='sap_no' and order_by =='asc':
                #print('user_department',order_by)
                user_sap_no_details = TCoreUserDetail.objects.filter(
                    cu_is_deleted=False).order_by('sap_personnel_no')
                #print('user_sap_no_details_asc',user_sap_no_details)
                sap_no_details_list=[]
                for u_g in user_sap_no_details:
                    sap_no_details_id=u_g.cu_user.id
                    sap_no_details_list.append(sap_no_details_id)
                #print('sap_no_details_list',sap_no_details_list)
                clauses = ' '.join(['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(sap_no_details_list)])
                ordering = 'CASE %s END' % clauses
                queryset =  self.queryset.filter(pk__in=sap_no_details_list).extra(select={'ordering': ordering}, order_by=('ordering',))
                #print('queryset',queryset)
                return queryset
            
            if field_name =='sap_no' and order_by =='desc':
                #print('user_department',order_by)
                user_sap_no_details = TCoreUserDetail.objects.filter(
                    cu_is_deleted=False).order_by('-sap_personnel_no')
                #print('user_sap_no_details_asc',user_sap_no_details)
                sap_no_details_list=[]
                for u_g in user_sap_no_details:
                    sap_no_details_id=u_g.cu_user.id
                    sap_no_details_list.append(sap_no_details_id)
                #print('sap_no_details_list',sap_no_details_list)
                clauses = ' '.join(['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(sap_no_details_list)])
                ordering = 'CASE %s END' % clauses
                queryset =  self.queryset.filter(pk__in=sap_no_details_list).extra(select={'ordering': ordering}, order_by=('ordering',))
                #print('queryset',queryset)
                return queryset

            if field_name =='initial_ctc' and order_by =='desc':
                #print('user_department',order_by)
                user_initial_ctc_details = TCoreUserDetail.objects.filter(
                    cu_is_deleted=False).order_by('-initial_ctc')
                #print('user_initial_ctc_details_asc',user_initial_ctc_details)
                initial_ctc_details_list=[]
                for u_g in user_initial_ctc_details:
                    initial_ctc_details_id=u_g.cu_user.id
                    initial_ctc_details_list.append(initial_ctc_details_id)
                #print('initial_ctc_details_list',initial_ctc_details_list)
                clauses = ' '.join(['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(initial_ctc_details_list)])
                ordering = 'CASE %s END' % clauses 
                queryset =  self.queryset.filter(pk__in=initial_ctc_details_list).extra(select={'ordering': ordering}, order_by=('ordering',))
                #print('queryset',queryset)
                return queryset
             
            if field_name =='initial_ctc' and order_by =='asc':
                #print('user_department',order_by) 
                user_initial_ctc_details = TCoreUserDetail.objects.filter(
                    cu_is_deleted=False).order_by('initial_ctc')
                #print('user_initial_ctc_details_asc',user_initial_ctc_details)
                initial_ctc_details_list=[]
                for u_g in user_initial_ctc_details:
                    initial_ctc_details_id=u_g.cu_user.id
                    initial_ctc_details_list.append(initial_ctc_details_id)
                #print('initial_ctc_details_list',initial_ctc_details_list)
                clauses = ' '.join(['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(initial_ctc_details_list)])
                ordering = 'CASE %s END' % clauses
                queryset =  self.queryset.filter(pk__in=initial_ctc_details_list).extra(select={'ordering': ordering}, order_by=('ordering',))
                #print('queryset',queryset)
                return queryset
            
            if field_name =='current_ctc' and order_by =='desc':
                #print('user_department',order_by)
                user_current_ctc_details = TCoreUserDetail.objects.filter(
                    cu_is_deleted=False).order_by('-current_ctc')
                #print('user_current_ctc_details_asc',user_current_ctc_details)
                current_ctc_details_list=[]
                for u_g in user_current_ctc_details:
                    current_ctc_details_id=u_g.cu_user.id
                    current_ctc_details_list.append(current_ctc_details_id)
                #print('current_ctc_details_list',current_ctc_details_list)
                clauses = ' '.join(['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(current_ctc_details_list)])
                ordering = 'CASE %s END' % clauses
                queryset =  self.queryset.filter(pk__in=current_ctc_details_list).extra(select={'ordering': ordering}, order_by=('ordering',))
                #print('queryset',queryset)
                return queryset
            
            if field_name =='current_ctc' and order_by =='asc':
                #print('user_department',order_by)
                user_current_ctc_details = TCoreUserDetail.objects.filter(
                    cu_is_deleted=False).order_by('current_ctc')
                #print('user_current_ctc_details_asc',user_current_ctc_details)
                current_ctc_details_list=[]
                for u_g in user_current_ctc_details:
                    current_ctc_details_id=u_g.cu_user.id
                    current_ctc_details_list.append(current_ctc_details_id)
                #print('current_ctc_details_list',current_ctc_details_list)
                clauses = ' '.join(['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(current_ctc_details_list)])
                ordering = 'CASE %s END' % clauses
                queryset =  self.queryset.filter(pk__in=current_ctc_details_list).extra(select={'ordering': ordering}, order_by=('ordering',))
                #print('queryset',queryset)
                return queryset

            if field_name =='granted_cl' and order_by =='asc':
                #print('user_department',order_by)
                user_granted_cl_details = TCoreUserDetail.objects.filter(
                    cu_is_deleted=False).order_by('current_ctc')
                #print('user_current_ctc_details_asc',user_granted_cl_details)
                granted_cl_details_list=[]
                for u_g in user_granted_cl_details:
                    granted_cl_details_id=u_g.cu_user.id
                    granted_cl_details_list.append(granted_cl_details_id)
                #print('current_ctc_details_list',granted_cl_details_list)
                clauses = ' '.join(['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(granted_cl_details_list)])
                ordering = 'CASE %s END' % clauses
                queryset =  self.queryset.filter(pk__in=granted_cl_details_list).extra(select={'ordering': ordering}, order_by=('ordering',))
                #print('queryset',queryset)
                return queryset

            if field_name =='granted_cl' and order_by =='desc':
                #print('user_department',order_by)
                user_granted_cl_details = TCoreUserDetail.objects.filter(
                    cu_is_deleted=False).order_by('-granted_cl')
                #print('user_current_ctc_details_asc',user_granted_cl_details)
                granted_cl_details_list=[]
                for u_g in user_granted_cl_details:
                    granted_cl_details_id=u_g.cu_user.id
                    granted_cl_details_list.append(granted_cl_details_id)
                #print('current_ctc_details_list',granted_cl_details_list)
                clauses = ' '.join(['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(granted_cl_details_list)])
                ordering = 'CASE %s END' % clauses
                queryset =  self.queryset.filter(pk__in=granted_cl_details_list).extra(select={'ordering': ordering}, order_by=('ordering',))
                #print('queryset',queryset)
                return queryset

            if field_name == 'granted_sl' and order_by == 'desc':
                # print('user_department',order_by)
                user_granted_sl_details = TCoreUserDetail.objects.filter(
                    cu_is_deleted=False).order_by('-granted_sl')
                #print('user_current_ctc_details_asc', user_granted_sl_details)
                granted_sl_details_list = []
                for u_g in user_granted_sl_details:
                    granted_sl_details_id = u_g.cu_user.id
                    granted_sl_details_list.append(granted_sl_details_id)
                #print('current_ctc_details_list', granted_sl_details_list)
                clauses = ' '.join(['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(granted_sl_details_list)])
                ordering = 'CASE %s END' % clauses
                queryset = self.queryset.filter(pk__in=granted_sl_details_list).extra(select={'ordering': ordering},
                                                                                      order_by=('ordering',))
                #print('queryset', queryset)
                return queryset

            if field_name == 'granted_sl' and order_by == 'asc':
                # print('user_department',order_by)
                user_granted_sl_details = TCoreUserDetail.objects.filter(
                    cu_is_deleted=False).order_by('granted_sl')
                #print('user_current_ctc_details_asc', user_granted_sl_details)
                granted_sl_details_list = []
                for u_g in user_granted_sl_details:
                    granted_sl_details_id = u_g.cu_user.id
                    granted_sl_details_list.append(granted_sl_details_id)
                #print('current_ctc_details_list', granted_sl_details_list)
                clauses = ' '.join(['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(granted_sl_details_list)])
                ordering = 'CASE %s END' % clauses
                queryset = self.queryset.filter(pk__in=granted_sl_details_list).extra(select={'ordering': ordering},
                                                                                      order_by=('ordering',))
                #print('queryset', queryset)
                return queryset

            if field_name == 'granted_el' and order_by == 'desc':
                # print('user_department',order_by)
                user_granted_el_details = TCoreUserDetail.objects.filter(
                    cu_is_deleted=False).order_by('-granted_el')
                #print('user_current_ctc_details_asc', user_granted_el_details)
                granted_el_details_list = []
                for u_g in user_granted_el_details:
                    granted_el_details_id = u_g.cu_user.id
                    granted_el_details_list.append(granted_el_details_id)
                #print('current_ctc_details_list', granted_el_details_list)
                clauses = ' '.join(['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(granted_el_details_list)])
                ordering = 'CASE %s END' % clauses
                queryset = self.queryset.filter(pk__in=granted_el_details_list).extra(select={'ordering': ordering},
                                                                                      order_by=('ordering',))
                #print('queryset', queryset)
                return queryset

            if field_name == 'granted_el' and order_by == 'asc':
                # print('user_department',order_by)
                user_granted_el_details = TCoreUserDetail.objects.filter(
                    cu_is_deleted=False).order_by('granted_el')
                #print('user_current_ctc_details_asc', user_granted_el_details)
                granted_el_details_list = []
                for u_g in user_granted_el_details:
                    granted_el_details_id = u_g.cu_user.id
                    granted_el_details_list.append(granted_el_details_id)
                #print('current_ctc_details_list', granted_el_details_list)
                clauses = ' '.join(['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(granted_el_details_list)])
                ordering = 'CASE %s END' % clauses
                queryset = self.queryset.filter(pk__in=granted_el_details_list).extra(select={'ordering': ordering},
                                                                                      order_by=('ordering',))
                #print('queryset', queryset)
                return queryset

            if field_name == 'total_experience' and order_by == 'desc':
                # print('user_department',order_by)
                user_total_experience_details = TCoreUserDetail.objects.filter(
                    cu_is_deleted=False).order_by('-total_experience')
                #print('user_current_ctc_details_asc', user_total_experience_details)
                total_experience_details_list = []
                for u_g in user_total_experience_details:
                    total_experience_details_id = u_g.cu_user.id
                    total_experience_details_list.append(total_experience_details_id)
                #print('current_ctc_details_list', total_experience_details_list)
                clauses = ' '.join(
                    ['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(total_experience_details_list)])
                ordering = 'CASE %s END' % clauses
                queryset = self.queryset.filter(pk__in=total_experience_details_list).extra(
                    select={'ordering': ordering}, order_by=('ordering',))
                #print('queryset', queryset)
                return queryset

            if field_name == 'total_experience' and order_by == 'asc':
                # print('user_department',order_by)
                user_total_experience_details = TCoreUserDetail.objects.filter(
                    cu_is_deleted=False).order_by('total_experience')
                #print('user_current_ctc_details_asc', user_total_experience_details)
                total_experience_details_list = []
                for u_g in user_total_experience_details:
                    total_experience_details_id = u_g.cu_user.id
                    total_experience_details_list.append(total_experience_details_id)
                #print('current_ctc_details_list', total_experience_details_list)
                clauses = ' '.join(
                    ['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(total_experience_details_list)])
                ordering = 'CASE %s END' % clauses
                queryset = self.queryset.filter(pk__in=total_experience_details_list).extra(
                    select={'ordering': ordering}, order_by=('ordering',))
                #print('queryset', queryset)
                return queryset
            
            if field_name == 'cu_emp_code' and order_by == 'asc':
                # print('user_department',order_by)
                user_total_experience_details = TCoreUserDetail.objects.filter(
                    cu_is_deleted=False).order_by('cu_emp_code')
                #print('user_current_ctc_details_asc', user_total_experience_details)
                total_experience_details_list = []
                for u_g in user_total_experience_details:
                    total_experience_details_id = u_g.cu_user.id
                    total_experience_details_list.append(total_experience_details_id)
                #print('current_ctc_details_list', total_experience_details_list)
                clauses = ' '.join(
                    ['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(total_experience_details_list)])
                ordering = 'CASE %s END' % clauses
                queryset = self.queryset.filter(pk__in=total_experience_details_list).extra(
                    select={'ordering': ordering}, order_by=('ordering',))
                #print('queryset', queryset)
                return queryset
            
            if field_name == 'cu_emp_code' and order_by == 'desc':
                # print('user_department',order_by)
                user_total_experience_details = TCoreUserDetail.objects.filter(
                    cu_is_deleted=False).order_by('-cu_emp_code')
                #print('user_current_ctc_details_asc', user_total_experience_details)
                total_experience_details_list = []
                for u_g in user_total_experience_details:
                    total_experience_details_id = u_g.cu_user.id
                    total_experience_details_list.append(total_experience_details_id)
                #print('current_ctc_details_list', total_experience_details_list)
                clauses = ' '.join(
                    ['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(total_experience_details_list)])
                ordering = 'CASE %s END' % clauses
                queryset = self.queryset.filter(pk__in=total_experience_details_list).extra(
                    select={'ordering': ordering}, order_by=('ordering',))
                #print('queryset', queryset)
                return queryset
            
            if field_name == 'cu_alt_email_id' and order_by == 'asc':
                # print('user_department',order_by)
                user_total_experience_details = TCoreUserDetail.objects.filter(
                    cu_is_deleted=False).order_by('cu_alt_email_id')
                #print('user_current_ctc_details_asc', user_total_experience_details)
                total_experience_details_list = []
                for u_g in user_total_experience_details:
                    total_experience_details_id = u_g.cu_user.id
                    total_experience_details_list.append(total_experience_details_id)
                #print('current_ctc_details_list', total_experience_details_list)
                clauses = ' '.join(
                    ['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(total_experience_details_list)])
                ordering = 'CASE %s END' % clauses
                queryset = self.queryset.filter(pk__in=total_experience_details_list).extra(
                    select={'ordering': ordering}, order_by=('ordering',))
                #print('queryset', queryset)
                return queryset
            
            if field_name == 'cu_alt_email_id' and order_by == 'desc':
                # print('user_department',order_by)
                user_total_experience_details = TCoreUserDetail.objects.filter(
                    cu_is_deleted=False).order_by('-cu_alt_email_id')
                #print('user_current_ctc_details_asc', user_total_experience_details)
                total_experience_details_list = []
                for u_g in user_total_experience_details:
                    total_experience_details_id = u_g.cu_user.id
                    total_experience_details_list.append(total_experience_details_id)
                #print('current_ctc_details_list', total_experience_details_list)
                clauses = ' '.join(
                    ['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(total_experience_details_list)])
                ordering = 'CASE %s END' % clauses
                queryset = self.queryset.filter(pk__in=total_experience_details_list).extra(
                    select={'ordering': ordering}, order_by=('ordering',))
                #print('queryset', queryset)
                return queryset
        elif search_keyword:
            self.queryset = TCoreUserDetail.objects.filter(cu_is_deleted=False,cu_user__is_superuser=False)
            #print('self.queryset',self.queryset)
            f_name = search_keyword.split(' ')[0]
            l_name = ' '.join(search_keyword.split(' ')[1:])
            #print(l_name)
            
            if l_name:
                queryset = self.queryset.filter(
                    Q(cu_user__first_name__icontains = f_name) | 
                    Q(cu_user__last_name__icontains = l_name) |
                    Q(cu_user__email__icontains = search_keyword) | 
                    Q(cu_alt_email_id__icontains=search_keyword)
                    )
            else:
                queryset = self.queryset.filter(
                    Q(cu_user__first_name__icontains = f_name) |
                    Q(cu_user__email__icontains = search_keyword) | 
                    Q(cu_alt_email_id__icontains=search_keyword)
                )
            #print('queryset',queryset.query)
            return queryset
             
        else:
            queryset = self.queryset.all()
            return queryset


    @response_modify_decorator_list_or_get_after_execution_for_pagination
    def get(self, request, *args, **kwargs):
        response=super(EmployeeListView,self).get(self, request, args, kwargs)
        
        if 'results' in response.data:
            response_s = response.data['results']
        else:
            response_s = response.data

        print('response check::::::::::::::',response_s)
        list_type = self.request.query_params.get('list_type', None)
        module_id = self.request.query_params.get('module_id', None)
        search_keyword = self.request.query_params.get('search_keyword', None)
        # print('module_id',module_id)
        p_doc_dict = {}

        for data in response_s:
            if list_type == "professional":
                professional_details=TCoreUserDetail.objects.filter(cu_user=data['id'],cu_is_deleted=False).values(
                    'cu_emp_code','sap_personnel_no','initial_ctc','current_ctc','cu_punch_id',
                    'cost_centre','granted_cl','granted_sl','granted_el')

                if search_keyword:
                    professional_details=TCoreUserDetail.objects.filter(pk=data['id'],cu_is_deleted=False).values(
                    'cu_emp_code','sap_personnel_no','initial_ctc','current_ctc','cu_punch_id',
                    'cost_centre','granted_cl','granted_sl','granted_el','cu_user__first_name','cu_user__last_name','cu_user__id')
                    data['first_name'] = professional_details[0]['cu_user__first_name'] if professional_details[0]['cu_user__first_name'] else ''
                    data['last_name'] = professional_details[0]['cu_user__last_name'] if professional_details[0]['cu_user__last_name'] else ''
                    data['name'] = data['first_name'] +' '+data['last_name']
                    data['id'] = User.objects.only('id').get(pk=professional_details[0]['cu_user__id']).id

                #print('professional_details',professional_details)

                if professional_details:
                    data['emp_code']=professional_details[0]['cu_emp_code'] if professional_details[0]['cu_emp_code'] else None
                    data['cu_punch_id']=professional_details[0]['cu_punch_id'] if professional_details[0]['cu_punch_id'] else None
                    data['sap_personnel_no']=professional_details[0]['sap_personnel_no'] if professional_details[0]['sap_personnel_no'] else None
                    data['initial_ctc']=professional_details[0]['initial_ctc'] if professional_details[0]['initial_ctc'] else None
                    data['current_ctc']=professional_details[0]['current_ctc'] if professional_details[0]['current_ctc'] else None
                    data['cost_centre']=professional_details[0]['cost_centre'] if professional_details[0]['cost_centre'] else None
                    data['granted_cl']=professional_details[0]['granted_cl'] if professional_details[0]['granted_cl'] else None
                    data['granted_sl']=professional_details[0]['granted_sl'] if professional_details[0]['granted_sl'] else None
                    data['granted_el']=professional_details[0]['granted_el'] if professional_details[0]['granted_el'] else None
                

                user_benefits=HrmsUsersBenefits.objects.filter(user=data['id'],is_deleted=False)
                benefits_list=[]
                if user_benefits:
                    for u_b in user_benefits:
                        benefits={
                            'id':u_b.id,
                            'benefits':u_b.benefits.id,
                            'benefits_name':u_b.benefits.benefits_name,
                            'allowance':u_b.allowance
                        }
                        benefits_list.append(benefits)
                    data['benefits_provided']=benefits_list
                else:
                    data['benefits_provided']= []
                other_facilities=HrmsUsersOtherFacilities.objects.filter(user=data['id'],is_deleted=False)
                facilities_list=[]
                if other_facilities:
                    for o_f in other_facilities:
                        facility={
                            'id':o_f.id,
                            'other_facilities':o_f.other_facilities,                       
                        }
                        facilities_list.append(facility)
                    data['other_facilities']=facilities_list
                else:
                    data['other_facilities'] = []
                p_doc_list = []
                professional_documents = HrmsDocument.objects.filter(user=data['id'],is_deleted=False)
                if professional_documents:
                    for doc_details in professional_documents:
                        if (doc_details.tab_name).lower() == "professional" :
                            if doc_details.__dict__['document'] == "":
                                file_url = ''
                            else:
                                file_url = request.build_absolute_uri(doc_details.document.url)
                            if doc_details.__dict__['document_name'] == "":
                                doc_name = ""                
                            else:
                                doc_name = doc_details.document_name

                            p_doc_dict = {
                                'tab_name' : doc_details.tab_name if doc_details.tab_name else None,
                                'field_label' : doc_details.field_label if doc_details.field_label else None,
                                'document_name' : doc_name,
                                'document' : file_url
                            }
                            p_doc_list.append(p_doc_dict)
                    data['documents'] = p_doc_list
                else:
                    data['documents'] = []
            if list_type == "role":
                role_details=TCoreUserDetail.objects.filter(cu_user=data['id'],cu_is_deleted=False).values('cu_user__username','cu_user__first_name','cu_user__last_name',
                    'cu_emp_code','cu_alt_phone_no','cu_alt_email_id','company__id','company__coc_name','job_description','hod__id','hod__first_name','hod__last_name',
                    'designation__id','cu_user__id','designation__cod_name','department__id','department__cd_name','reporting_head__id','reporting_head__first_name','reporting_head__last_name',
                    'employee_grade__id','employee_grade__cg_name')
                
                if search_keyword:
                    role_details=TCoreUserDetail.objects.filter(pk=data['id'],cu_is_deleted=False).values('cu_user__username',
                    'cu_user__first_name','cu_user__last_name','cu_emp_code','cu_user__id','cu_alt_phone_no','cu_alt_email_id','company__id','company__coc_name','job_description','hod__id',
                    'hod__first_name','hod__last_name', 'designation__id','designation__cod_name','department__id','employee_grade__id',
                    'department__cd_name','reporting_head__id','reporting_head__first_name','reporting_head__last_name','employee_grade__cg_name')

                
                if role_details:
                    first_name = role_details[0]['cu_user__first_name'] if role_details[0]['cu_user__first_name'] else ''
                    last_name = role_details[0]['cu_user__last_name'] if role_details[0]['cu_user__last_name'] else ''
                    data['id'] = role_details[0]['cu_user__id']  
                    data['name']= first_name + " " + last_name
                    data['first_name']=first_name
                    data['last_name']=last_name
                    data['username'] = role_details[0]['cu_user__username'] if role_details[0]['cu_user__username'] else None
                    data['emp_code']=role_details[0]['cu_emp_code'] if role_details[0]['cu_emp_code'] else None
                    data['official_contact_no']=role_details[0]['cu_alt_phone_no'] if role_details[0]['cu_alt_phone_no'] else None
                    data['official_email_id']=role_details[0]['cu_alt_email_id'] if role_details[0]['cu_alt_email_id'] else None
                    data['company']=role_details[0]['company__id'] if role_details[0]['company__id'] else None
                    data['company_name']=role_details[0]['company__coc_name'] if role_details[0]['company__coc_name'] else None
                    data['job_description']=role_details[0]['job_description'] if role_details[0]['job_description'] else None
                    data['hod_id']=role_details[0]['hod__id'] if role_details[0]['hod__id'] else None
                    
                    hod__first_name = role_details[0]['hod__first_name'] if role_details[0]['hod__first_name'] else ''
                    hod__last_name = role_details[0]['hod__last_name'] if role_details[0]['hod__last_name'] else ''

                    data['hod']= hod__first_name + " " + hod__last_name

                    data['designation_id']=role_details[0]['designation__id'] if role_details[0]['designation__id'] else None
                    data['designation_name']=role_details[0]['designation__cod_name'] if role_details[0]['designation__cod_name'] else None
                    data['department_id']=role_details[0]['department__id'] if role_details[0]['department__id'] else None
                    data['department_name']=role_details[0]['department__cd_name'] if role_details[0]['department__cd_name'] else None

                    data['reporting_head_id']=role_details[0]['reporting_head__id'] if role_details[0]['reporting_head__id'] else None

                    reporting_head__first_name = role_details[0]['reporting_head__first_name'] if role_details[0]['reporting_head__first_name'] else '' 
                    reporting_head__last_name = role_details[0]['reporting_head__last_name'] if role_details[0]['reporting_head__last_name'] else ''

                    data['reporting_head_name'] = reporting_head__first_name + " " + reporting_head__last_name 
                    # data['employee_grade_name']=role_details[0]['employee_grade__cg_name'] if role_details[0]['employee_grade__id'] else None
                    # data['employee_grade_id']=role_details[0]['employee_grade__id'] if role_details[0]['employee_grade__id'] else None   
                    grade_details=TCoreGrade.objects.filter(id=role_details[0]['employee_grade__id'],cg_is_deleted=False)
                    if grade_details:
                        grade_details=TCoreGrade.objects.filter(id=role_details[0]['employee_grade__id'],cg_is_deleted=False)[0]
                        if grade_details:
                            grade_dict = dict()
                            print('grade_details',grade_details.id)
                            if grade_details.cg_parent_id!=0:
                                parent = TCoreGrade.objects.filter(id=grade_details.cg_parent_id,cg_is_deleted=False)
                                for p_d in parent:
                                    grade_dict['id']=p_d.id
                                    grade_dict['cg_name']=p_d.cg_name
                                    
                                grade_dict['child'] = {
                                    "id":grade_details.id,
                                    "cg_name":grade_details.cg_name
                                    }
                            else:
                                grade_dict['id']=grade_details.id
                                grade_dict['cg_name']=grade_details.cg_name
                                grade_dict['child'] = None

                            print('grade_dict',grade_dict)
                            
                            data['grade_details']=grade_dict
                        else:
                            data['grade_details']=None
                    else:
                        data['grade_details']=None 
            if list_type == "personal":
                personal_details=TCoreUserDetail.objects.filter(cu_user=data['id'],cu_is_deleted=False)
                if search_keyword:
                    personal_details=TCoreUserDetail.objects.filter(pk=data['id'],cu_is_deleted=False)
                    
                if personal_details:
                    for p_d in personal_details:
                        data['id'] = p_d.cu_user.id
                        data['first_name'] = p_d.cu_user.first_name if p_d.cu_user.first_name else ''
                        data['last_name'] = p_d.cu_user.last_name if p_d.cu_user.last_name else ''
                        data['name'] = data['first_name'] +' '+data['last_name']
                        data['emp_code']=p_d.cu_emp_code
                        data['personal_contact_no']=p_d.cu_phone_no
                        data['personal_email_id']=p_d.cu_user.email
                        data['address']=p_d.address
                        data['blood_group']=p_d.blood_group
                        data['photo']=request.build_absolute_uri(p_d.cu_profile_img.url) if p_d.cu_profile_img else None
                        data['total_experience']=p_d.total_experience
                
                licenses_and_certifications_dict = {}
                work_experience_dict = {}
                add_more_files_dict = {}
                personal_documents = HrmsDynamicSectionFieldLabelDetailsWithDoc.objects.filter(user=data['id'],is_deleted=False)
                print("personal_documents",personal_documents)
                if personal_documents:
                    licenses_and_certifications_list = []
                    add_more_files_list = []
                    work_experience_list = []
                    for doc_details in personal_documents: 
                        if (doc_details.tab_name).lower() == "personal" :
                            if doc_details.__dict__['document'] == "":
                                file_url = ''
                            else:
                                file_url = request.build_absolute_uri(doc_details.document.url)
                                
                            if doc_details.__dict__['document_name'] == "":
                                doc_name = ""
                            else:
                                doc_name = doc_details.document_name
                                
                            if doc_details.field_label == "Licenses and Certifications":
                                licenses_and_certifications_dict = {
                                'id' : doc_details.id,
                                'field_label_value' : doc_details.field_label_value if doc_details.field_label_value else None,
                                'document_name' : doc_name,
                                'document' : file_url
                                }
                                licenses_and_certifications_list.append(licenses_and_certifications_dict)
                            
                            if doc_details.field_label == "Work Experience":
                                work_experience_dict = {                            
                                'id' : doc_details.id,
                                'field_label_value' : doc_details.field_label_value if doc_details.field_label_value else None,
                                'document_name' : doc_name,                            
                                'document' : file_url                            
                                }                            
                                work_experience_list.append(work_experience_dict)

                    data['licenses_and_certifications_doc'] = licenses_and_certifications_list if licenses_and_certifications_list else []
                    data['work_experience_doc'] = work_experience_list if work_experience_list else []
                   
                else:
                    data['licenses_and_certifications_doc'] = []
                    data['work_experience_doc'] = []
                academic_qualification=HrmsUserQualification.objects.filter(user=data['id'],is_deleted=False)
                print('academic_qualification',academic_qualification)
                if academic_qualification:
                    academic_qualification_list = []
                    academic_qualification_dict = {} 
                    for a_q in academic_qualification:
                        academic_qualification_dict={
                            'id':a_q.id,
                            'qualification':a_q.qualification.id,
                            'qualification_name':a_q.qualification.name,
                            'details':a_q.details
                        }
                        academic_doc=HrmsUserQualificationDocument.objects.filter(user_qualification=a_q.id,is_deleted=False)
                        print('academic_doc',academic_doc)          
                        if academic_doc:
                            academic_doc_dict={}
                            academic_doc_list=[]
                            for a_d in academic_doc:
                                academic_doc_dict={
                                    'id':a_d.id,
                                    'document':request.build_absolute_uri(a_d.document.url)
                                }
                                academic_doc_list.append(academic_doc_dict)
                            academic_qualification_dict['qualification_doc']=academic_doc_list
                        else:
                            academic_qualification_dict['qualification_doc']=[]
                        academic_qualification_list.append(academic_qualification_dict)
                    data['academic_qualification']=academic_qualification_list
                else:
                    data['academic_qualification']=[]
            if list_type == 'resignation':
                '''
                    Reason : Fetch Resignation employee list
                    Author : Rupam Hazra 
                    Line number:  1245 - 1337
                    Date : 19/02/2020
                '''
                #time.sleep(10)
                role_details=TCoreUserDetail.objects.filter(
                    cu_user=data['id'],cu_is_deleted=False
                    ).values(
                    'cu_user__username','cu_user__first_name','cu_user__last_name',
                    'cu_emp_code','cu_alt_phone_no','cu_alt_email_id','company__id','company__coc_name',
                    'job_description','hod__id','hod__first_name','hod__last_name','designation__id','cu_user__id',
                    'designation__cod_name','department__id','department__cd_name','reporting_head__id',
                    'reporting_head__first_name','reporting_head__last_name',
                    'employee_grade__id','employee_grade__cg_name','sap_personnel_no','cu_punch_id','termination_date','resignation_date')
                
                if search_keyword:
                    role_details=TCoreUserDetail.objects.filter(pk=data['id'],cu_is_deleted=False).values('cu_user__username',
                    'cu_user__first_name','cu_user__last_name','cu_emp_code','cu_user__id','cu_alt_phone_no',
                    'cu_alt_email_id','company__id','company__coc_name','job_description','hod__id',
                    'hod__first_name','hod__last_name', 'designation__id','designation__cod_name',
                    'department__id','employee_grade__id','department__cd_name','reporting_head__id',
                    'reporting_head__first_name','reporting_head__last_name','employee_grade__cg_name',
                    'sap_personnel_no','cu_punch_id','termination_date','resignation_date')

                
                if role_details:
                    first_name = role_details[0]['cu_user__first_name'] if role_details[0]['cu_user__first_name'] else ''
                    last_name = role_details[0]['cu_user__last_name'] if role_details[0]['cu_user__last_name'] else ''
                    data['id'] = role_details[0]['cu_user__id']  
                    data['name']= first_name + " " + last_name
                    data['first_name']=first_name
                    data['last_name']=last_name
                    data['username'] = role_details[0]['cu_user__username'] if role_details[0]['cu_user__username'] else None
                    data['emp_code']=role_details[0]['cu_emp_code'] if role_details[0]['cu_emp_code'] else None
                    data['official_contact_no']=role_details[0]['cu_alt_phone_no'] if role_details[0]['cu_alt_phone_no'] else None
                    data['official_email_id']=role_details[0]['cu_alt_email_id'] if role_details[0]['cu_alt_email_id'] else None
                    data['company']=role_details[0]['company__id'] if role_details[0]['company__id'] else None
                    data['company_name']=role_details[0]['company__coc_name'] if role_details[0]['company__coc_name'] else None
                    data['job_description']=role_details[0]['job_description'] if role_details[0]['job_description'] else None
                    data['hod_id']=role_details[0]['hod__id'] if role_details[0]['hod__id'] else None
                    data['sap_personnel_no']=role_details[0]['sap_personnel_no'] if role_details[0]['sap_personnel_no'] else None
                    data['cu_punch_id']=role_details[0]['cu_punch_id'] if role_details[0]['cu_punch_id'] else None
                    data['termination_date']=role_details[0]['termination_date'] if role_details[0]['termination_date'] else None
                    data['resignation_date']=role_details[0]['resignation_date'] if role_details[0]['resignation_date'] else None
                    
                    hod__first_name = role_details[0]['hod__first_name'] if role_details[0]['hod__first_name'] else ''
                    hod__last_name = role_details[0]['hod__last_name'] if role_details[0]['hod__last_name'] else ''

                    data['hod']= hod__first_name + " " + hod__last_name

                    data['designation_id']=role_details[0]['designation__id'] if role_details[0]['designation__id'] else None
                    data['designation_name']=role_details[0]['designation__cod_name'] if role_details[0]['designation__cod_name'] else None
                    data['department_id']=role_details[0]['department__id'] if role_details[0]['department__id'] else None
                    data['department_name']=role_details[0]['department__cd_name'] if role_details[0]['department__cd_name'] else None

                    data['reporting_head_id']=role_details[0]['reporting_head__id'] if role_details[0]['reporting_head__id'] else None

                    reporting_head__first_name = role_details[0]['reporting_head__first_name'] if role_details[0]['reporting_head__first_name'] else '' 
                    reporting_head__last_name = role_details[0]['reporting_head__last_name'] if role_details[0]['reporting_head__last_name'] else ''

                    data['reporting_head_name'] = reporting_head__first_name + " " + reporting_head__last_name 
                    # data['employee_grade_name']=role_details[0]['employee_grade__cg_name'] if role_details[0]['employee_grade__id'] else None
                    # data['employee_grade_id']=role_details[0]['employee_grade__id'] if role_details[0]['employee_grade__id'] else None   
                    grade_details=TCoreGrade.objects.filter(id=role_details[0]['employee_grade__id'],cg_is_deleted=False)
                    if grade_details:
                        grade_details=TCoreGrade.objects.filter(id=role_details[0]['employee_grade__id'],cg_is_deleted=False)[0]
                        if grade_details:
                            grade_dict = dict()
                            print('grade_details',grade_details.id)
                            if grade_details.cg_parent_id!=0:
                                parent = TCoreGrade.objects.filter(id=grade_details.cg_parent_id,cg_is_deleted=False)
                                for p_d in parent:
                                    grade_dict['id']=p_d.id
                                    grade_dict['cg_name']=p_d.cg_name
                                    
                                grade_dict['child'] = {
                                    "id":grade_details.id,
                                    "cg_name":grade_details.cg_name
                                    }
                            else:
                                grade_dict['id']=grade_details.id
                                grade_dict['cg_name']=grade_details.cg_name
                                grade_dict['child'] = None

                            print('grade_dict',grade_dict)
                            
                            data['grade_details']=grade_dict
                        else:
                            data['grade_details']=None
                    else:
                        data['grade_details']=None       

        return response  

class EmployeeListWithoutDetailsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = User.objects.filter(is_superuser=False,is_active=True)
    serializer_class = EmployeeListWithoutDetailsSerializer
    pagination_class = OnOffPagination

    def get_queryset(self):
        search_key = self.request.query_params.get('search_key', None)
        module= self.request.query_params.get('module', None)
        team_approval_flag = self.request.query_params.get('team_approval_flag', None)
        login_user_details = self.request.user
        
        print('login_user_details',login_user_details,login_user_details.id)

        if login_user_details.is_superuser == False:
            if module == 'hrms':
                module = 'ATTENDANCE & HRMS'
            if module == 'ETASK' or module == 'etask':
                module = 'e-task'
            
            if team_approval_flag == '1' and module is not None:
                
                if search_key:
                    queryset = User.objects.filter(
                        (Q(first_name__icontains=search_key) | Q(last_name__icontains=search_key)),
                        pk__in=(
                        TMasterModuleRoleUser.objects.filter(
                            mmr_type__in=('3'),
                            mmr_module__cm_name=module,
                            mmr_is_deleted=False,
                            mmr_user_id__in=TCoreUserDetail.objects.filter(reporting_head_id=login_user_details,cu_is_deleted=False).values_list('cu_user_id',flat=True)).values_list('mmr_user_id',flat=True)
                        ),
                        is_active=True,
                        is_superuser=False
                    )
                else:
                    queryset = User.objects.filter(
                        pk__in=(TMasterModuleRoleUser.objects.filter(
                            mmr_type__in=('3'),
                            mmr_module__cm_name=module,
                            mmr_is_deleted=False,
                            mmr_user_id__in=TCoreUserDetail.objects.filter(
                                reporting_head_id=login_user_details,cu_is_deleted=False).values_list('cu_user_id',flat=True)).values_list('mmr_user_id',flat=True)
                        ),
                        is_active=True,
                        is_superuser=False
                    )
                #print('queryset',queryset.query)
                return queryset
               
            elif team_approval_flag == '1' and module is None:
                if search_key:
                    queryset = User.objects.filter((Q(first_name__icontains=search_key) | Q(last_name__icontains=search_key)),pk__in=(TCoreUserDetail.objects.filter(reporting_head_id=login_user_details,cu_is_deleted=False).values_list('cu_user_id',flat=True)))
                else:
                    queryset = User.objects.filter(pk__in=(TCoreUserDetail.objects.filter(reporting_head_id=login_user_details,cu_is_deleted=False).values_list('cu_user_id',flat=True)))
                return queryset
                
            elif team_approval_flag is None and module is not None:
                #print('modulekkkkkkkkkkkkkkkkkkkkkkkkkk',module)
                #time.sleep(5)
                if module.lower() == "vms":
                    if search_key:
                        return self.queryset.filter(Q(first_name__icontains=search_key) | Q(last_name__icontains=search_key))                       
                    else:
                        return self.queryset.all()
                
                elif module == "e-task":
                    #print('checdkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk')
                    #time.sleep(10)
                    '''
                        Reason : 
                        1) on_behalf_of :According to changing function doc to show list of user highier level
                        2) assign_to / sub_assign_to : According to changing function doc to show list of user lower level or hod
                        Author : Rupam Hazra
                        Date : 21/02/2020
                        Line Number : 582
                    '''
                    mode_for = self.request.query_params.get('mode_for', None)
                    if mode_for == 'on_behalf_of':
                        hi_user_list_details = TCoreUserDetail.objects.filter(
                            cu_user = login_user_details,cu_is_deleted=False,reporting_head__isnull=False).values_list('reporting_head',flat=True)
                        #print('hi_user_list_details',hi_user_list_details)
                        if hi_user_list_details.count() > 0 :
                            hi_user_details  = hi_user_list_details[0]
                            #print('hi_user_details_up',hi_user_details,type(hi_user_details))
                            hi_user_details_l = self.getHighierLevelUserList(str(hi_user_details))
                            print('hi_user_details_l',hi_user_details_l,type(hi_user_details_l))
                            hi_user_details_l = [int(x) for x in hi_user_details_l.split(",")]
                            if search_key:
                                return self.queryset.filter((Q(first_name__icontains=search_key) | Q(last_name__icontains=search_key)),pk__in=hi_user_details_l)
                            else:
                                return self.queryset.filter(pk__in=hi_user_details_l)

                    elif mode_for == 'assign_to' or mode_for == 'sub_assign_to' :
                        is_hod = TCoreUserDetail.objects.filter(
                            hod = login_user_details,cu_is_deleted=False,cu_user__isnull=False).values('hod').distinct()
                        #print('is_hodlllllllllllllllllllllllllll',is_hod)
                        #time.sleep(15)
                        if is_hod:
                            department_d = TCoreUserDetail.objects.filter(
                                cu_user = login_user_details,cu_is_deleted=False,cu_user__isnull=False).values_list('department',flat=True)
                            #print('department_d',department_d)
                            if department_d:
                                hi_user_list_details = TCoreUserDetail.objects.filter(~Q(cu_user=login_user_details),department__in=department_d).values_list('cu_user',flat=True)
                                #print('hi_user_list_details',hi_user_list_details)
                                if search_key:
                                    return self.queryset.filter((Q(first_name__icontains=search_key) | Q(last_name__icontains=search_key)),pk__in=hi_user_list_details)
                                else:
                                    return self.queryset.filter(pk__in=hi_user_list_details)   
                        else:

                            hi_user_list_details = TCoreUserDetail.objects.filter(
                                reporting_head = login_user_details,cu_is_deleted=False,cu_user__isnull=False).values_list('cu_user',flat=True)
                            #print('hi_user_list_details',list(hi_user_list_details))
                            hi_user_details1 = ''
                            if hi_user_list_details.count() > 0 :
                                for hi_user_details in hi_user_list_details:
                                    hi_user_list_details = self.getLowerLevelUserList(str(hi_user_details),list(hi_user_list_details))
                                #print('hi_user_details1',hi_user_list_details)
                                if search_key:
                                    return self.queryset.filter((Q(first_name__icontains=search_key) | Q(last_name__icontains=search_key)),pk__in=hi_user_list_details)
                                else:
                                    return self.queryset.filter(pk__in=hi_user_list_details)   
                                               
                    else:
                        if search_key:
                            return self.queryset.filter(~Q(id=self.request.user.id),(Q(first_name__icontains=search_key) | Q(last_name__icontains=search_key)))
                        else:
                            # return self.queryset.all()
                            return self.queryset.filter(~Q(id=self.request.user.id))
                
                elif module.lower() == "hrms":
                    if search_key:
                        return self.queryset.filter(Q(first_name__icontains=search_key) | Q(last_name__icontains=search_key))                       
                    else:
                        return self.queryset.all(~Q(cu_punch_id__in=('#N/A')))
                else:
                    if search_key:
                        queryset = User.objects.filter(
                        (Q(first_name__icontains=search_key) | Q(last_name__icontains=search_key)),
                        pk__in=(
                        TMasterModuleRoleUser.objects.filter(mmr_type__in=('3'),mmr_module__cm_name=module).values_list('mmr_user_id',flat=True)
                        )
                        )
                    else:
                        queryset = User.objects.filter(
                        pk__in=(
                        TMasterModuleRoleUser.objects.filter(mmr_module__cm_name=module,mmr_type__in=('3')).values_list('mmr_user_id',flat=True)
                        )
                        )
                    print('queryset',queryset.query)
                    return queryset
        else:
            if search_key:
                queryset=self.queryset.filter((Q(first_name__icontains=search_key) | Q(last_name__icontains=search_key)))
            else:
                queryset=self.queryset.all()                                

            return queryset

    def getHighierLevelUserList(self, user_id='') -> list:
        try:
            hi_user_list = user_id
            hi_user_list_d =TCoreUserDetail.objects.filter(cu_user_id = str(user_id),cu_is_deleted=False,reporting_head__isnull=False).values_list(
                'reporting_head',flat=True)
            if hi_user_list_d.count() > 0:
                hi_user_list1 = str(hi_user_list_d[0])
                hi_user_list = hi_user_list +','+ str(self.getHighierLevelUserList(hi_user_list1))
            return hi_user_list.replace(',None','')
        except Exception as e:
            raise e   
    
    def getLowerLevelUserList(self, user_id='',main_list='') -> list:
        try:
            #print('user_id',user_id)
            #print('main_list',main_list)
            hi_user_list_details =TCoreUserDetail.objects.filter(reporting_head_id = str(user_id),cu_is_deleted=False,cu_user__isnull=False).values_list(
                'cu_user_id',flat=True)
            #print('hi_user_list_details1111',hi_user_list_details)
            if hi_user_list_details.count() > 0 :
                for hi_user_details in hi_user_list_details:
                    main_list.append(hi_user_details)
                    self.getLowerLevelUserList(str(hi_user_details),main_list)
            return main_list
        except Exception as e:
            raise e

    @response_modify_decorator_list_or_get_before_execution_for_onoff_pagination
    def get(self, request, *args, **kwargs):
        #print('self',self.response)
        return response  

class EmployeeListWOPaginationView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = User.objects.filter(is_active=True)
    serializer_class =EmployeeListSerializer
    def get_queryset(self):
        team_approval_flag = self.request.query_params.get('team_approval_flag', None)
        search_sort_flag = True
        if team_approval_flag == '1':
            login_user_details = self.request.user
            print('login_user_details',login_user_details)
            #print('login_user_details',login_user_details.is_superuser)
            if login_user_details.is_superuser == False:
                users_list_under_the_login_user = TCoreUserDetail.objects.filter(
                    reporting_head = login_user_details,
                    cu_is_deleted = False
                ).annotate(
                first_name = F('cu_user__first_name'),
                last_name=F('cu_user__last_name'),
                ).values('id','cu_user','first_name','last_name')
                print('users_list_under_the_login_user',users_list_under_the_login_user)
                if users_list_under_the_login_user:
                    return users_list_under_the_login_user
                else:
                    return list()
            else:
                return super().get_queryset()
        else:
            return super().get_queryset()

    @response_modify_decorator_get_after_execution
    def get(self, request, *args, **kwargs):
        department= self.request.query_params.get('department', None)
        print('department',department)
        dept_list=None
        if department:
            dept_list=department.split(",")
            print('dept_list',dept_list)
        response=super(EmployeeListWOPaginationView,self).get(self, request, args, kwargs)
        # print('response',response.data) 
        dept_det=[]   
        if dept_list:
            for data in response.data:
                dept=TCoreUserDetail.objects.filter(cu_user_id=data['id'],
                                            department__in=dept_list,
                                            cu_is_deleted=False)
                print('dept',dept)
                for data in dept:
                    dept_dict={
                        "id":data.id,
                        "cu_user":data.cu_user.id,
                        "first_name":data.cu_user.first_name,
                        "last_name":data.cu_user.last_name
                    }
                    dept_det.append(dept_dict)
                print('dept_det',dept_det)
            return Response(dept_det)         
        else:
            return response
class EmployeeListForHrView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = User.objects.filter(is_active=True).order_by('-id')
    serializer_class =EmployeeListWithoutDetailsSerializer
    pagination_class = CSPageNumberPagination

    def intersection(dept_list, date_list): 
        return list(set(dept_list) & set(date_list))

    def get_queryset(self):
        login_user = self.request.user.id
        # self.queryset = self.queryset.filter(~Q(pk=login_user),
        # pk__in=(TMasterModuleRoleUser.objects.filter(mmr_type='3')))
        self.queryset = self.queryset.filter(~Q(pk=login_user))
        filter = {}
        joining_date_filter={}
        date_filter={}
        total_filter={}
        #name = self.request.query_params.get('name', None)
        field_name = self.request.query_params.get('field_name', None)
        order_by = self.request.query_params.get('order_by', None)
        department= self.request.query_params.get('department', None)
        from_date = self.request.query_params.get('from_date', None)
        to_date = self.request.query_params.get('to_date', None)

        if department and from_date and to_date:
            print('department',department)
            department = department.split(',')
            department_ids=TCoreUserDetail.objects.filter(department__in=department,cu_is_deleted=False)
            dept_list=[]
            for d_i in department_ids:
                user_id=d_i.cu_user.id
                dept_list.append(user_id)
            print('dept_list',dept_list)
            from_object =datetime.datetime.strptime(from_date, '%Y-%m-%d')
            to_object =datetime.datetime.strptime(to_date, '%Y-%m-%d')
            joining_date_filter['joining_date__date__gte']= from_object
            joining_date_filter['joining_date__date__lte']= to_object + timedelta(days=1)
            date_ids=TCoreUserDetail.objects.filter(cu_is_deleted=False,**joining_date_filter)
            date_list=[]
            for d_i in date_ids:
                emp_id=d_i.cu_user.id
                date_list.append(emp_id)
            print('date_list',date_list)

            total_list=list(set(dept_list) & set(date_list))
            print('total_list',total_list)
            total_filter['id__in']=total_list
            
        
        # if department or (from_date and to_date):
        elif department:
            department=department.split(',')
            department_ids=TCoreUserDetail.objects.filter(department__in=department,cu_is_deleted=False).values_list('cu_user',flat=True)
            # return self.queryset.filter(id__in=department_ids)
            print('department_ids',department_ids)
            filter['id__in']=department_ids
            
        elif from_date and to_date:
            from_object =datetime.datetime.strptime(from_date, '%Y-%m-%d')
            to_object =datetime.datetime.strptime(to_date, '%Y-%m-%d')
            joining_date_filter['joining_date__date__gte']= from_object
            joining_date_filter['joining_date__date__lte']= to_object + timedelta(days=1)
            date_ids=TCoreUserDetail.objects.filter(cu_is_deleted=False,**joining_date_filter).values_list('cu_user',flat=True)
            date_filter['id__in']=date_ids
        
        if field_name and order_by:
            if field_name == 'cu_emp_code' and order_by == 'asc':
                user_total_experience_details = TCoreUserDetail.objects.filter(
                    cu_is_deleted=False).order_by('cu_emp_code')
                total_experience_details_list = []
                for u_g in user_total_experience_details:
                    total_experience_details_id = u_g.cu_user.id
                    total_experience_details_list.append(total_experience_details_id)
                #print('current_ctc_details_list', total_experience_details_list)
                clauses = ' '.join(
                    ['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(total_experience_details_list)])
                ordering = 'CASE %s END' % clauses
                queryset = self.queryset.filter(pk__in=total_experience_details_list,**filter,**date_filter,**total_filter).extra(
                    select={'ordering': ordering}, order_by=('ordering',))           
                #print('queryset', queryset)
                return queryset
            if field_name == 'cu_emp_code' and order_by == 'desc':
                # print('user_department',order_by)
                user_total_experience_details = TCoreUserDetail.objects.filter(
                    cu_is_deleted=False).order_by('-cu_emp_code')
                #print('user_current_ctc_details_asc', user_total_experience_details)
                total_experience_details_list = []
                for u_g in user_total_experience_details:
                    total_experience_details_id = u_g.cu_user.id
                    total_experience_details_list.append(total_experience_details_id)
                #print('current_ctc_details_list', total_experience_details_list)
                clauses = ' '.join(
                    ['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(total_experience_details_list)])
                ordering = 'CASE %s END' % clauses
                queryset = self.queryset.filter(pk__in=total_experience_details_list,**filter,**date_filter,**total_filter).extra(
                    select={'ordering': ordering}, order_by=('ordering',))
                # print('queryset', queryset)
                return queryset
                
                
            if field_name == 'cu_punch_id' and order_by == 'asc':
                user_total_experience_details = TCoreUserDetail.objects.filter(
                    cu_is_deleted=False).order_by('cu_punch_id')
                total_experience_details_list = []
                for u_g in user_total_experience_details:
                    total_experience_details_id = u_g.cu_user.id
                    total_experience_details_list.append(total_experience_details_id)
                #print('current_ctc_details_list', total_experience_details_list)
                clauses = ' '.join(
                    ['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(total_experience_details_list)])
                ordering = 'CASE %s END' % clauses
                queryset = self.queryset.filter(pk__in=total_experience_details_list,**filter,**date_filter,**total_filter).extra(
                    select={'ordering': ordering}, order_by=('ordering',))
                #print('queryset', queryset)
                return queryset
            if field_name == 'cu_punch_id' and order_by == 'desc':
                # print('user_department',order_by)
                user_total_experience_details = TCoreUserDetail.objects.filter(
                    cu_is_deleted=False).order_by('-cu_punch_id')
                #print('user_current_ctc_details_asc', user_total_experience_details)
                total_experience_details_list = []
                for u_g in user_total_experience_details:
                    total_experience_details_id = u_g.cu_user.id
                    total_experience_details_list.append(total_experience_details_id)
                #print('current_ctc_details_list', total_experience_details_list)
                clauses = ' '.join(
                    ['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(total_experience_details_list)])
                ordering = 'CASE %s END' % clauses
                queryset = self.queryset.filter(pk__in=total_experience_details_list,**filter,**date_filter,**total_filter).extra(
                    select={'ordering': ordering}, order_by=('ordering',))
                #print('queryset', queryset)
                return queryset
            if field_name == 'sap_personnel_no' and order_by == 'asc':
                user_total_experience_details = TCoreUserDetail.objects.filter(
                    cu_is_deleted=False).order_by('sap_personnel_no')
                total_experience_details_list = []
                for u_g in user_total_experience_details:
                    total_experience_details_id = u_g.cu_user.id
                    total_experience_details_list.append(total_experience_details_id)
                #print('current_ctc_details_list', total_experience_details_list)
                clauses = ' '.join(
                    ['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(total_experience_details_list)])
                ordering = 'CASE %s END' % clauses
                queryset = self.queryset.filter(pk__in=total_experience_details_list,**filter,**date_filter,**total_filter).extra(
                    select={'ordering': ordering}, order_by=('ordering',))
                #print('queryset', queryset)
                return queryset
            if field_name == 'sap_personnel_no' and order_by == 'desc':
                # print('user_department',order_by)
                user_total_experience_details = TCoreUserDetail.objects.filter(
                    cu_is_deleted=False).order_by('-sap_personnel_no')
                #print('user_current_ctc_details_asc', user_total_experience_details)
                total_experience_details_list = []
                for u_g in user_total_experience_details:
                    total_experience_details_id = u_g.cu_user.id
                    total_experience_details_list.append(total_experience_details_id)
                #print('current_ctc_details_list', total_experience_details_list)
                clauses = ' '.join(
                    ['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(total_experience_details_list)])
                ordering = 'CASE %s END' % clauses
                queryset = self.queryset.filter(pk__in=total_experience_details_list,**filter,**date_filter,**total_filter).extra(
                    select={'ordering': ordering}, order_by=('ordering',))
                #print('queryset', queryset)
                return queryset
            if field_name == 'joining_date' and order_by == 'asc':
                user_total_experience_details = TCoreUserDetail.objects.filter(
                    cu_is_deleted=False).order_by('joining_date')
                total_experience_details_list = []
                for u_g in user_total_experience_details:
                    total_experience_details_id = u_g.cu_user.id
                    total_experience_details_list.append(total_experience_details_id)
                #print('current_ctc_details_list', total_experience_details_list)
                clauses = ' '.join(
                    ['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(total_experience_details_list)])
                ordering = 'CASE %s END' % clauses
                queryset = self.queryset.filter(pk__in=total_experience_details_list,**filter,**date_filter,**total_filter).extra(
                    select={'ordering': ordering}, order_by=('ordering',))
                #print('queryset', queryset)
                return queryset
            if field_name == 'joining_date' and order_by == 'desc':
                # print('user_department',order_by)
                user_total_experience_details = TCoreUserDetail.objects.filter(
                    cu_is_deleted=False).order_by('-joining_date')
                #print('user_current_ctc_details_asc', user_total_experience_details)
                total_experience_details_list = []
                for u_g in user_total_experience_details:
                    total_experience_details_id = u_g.cu_user.id
                    total_experience_details_list.append(total_experience_details_id)
                #print('current_ctc_details_list', total_experience_details_list)
                clauses = ' '.join(
                    ['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(total_experience_details_list)])
                ordering = 'CASE %s END' % clauses
                queryset = self.queryset.filter(pk__in=total_experience_details_list,**filter,**date_filter,**total_filter).extra(
                    select={'ordering': ordering}, order_by=('ordering',))
                #print('queryset', queryset)
                return queryset
            if field_name =='designation' and order_by =='asc':
                #print('user_grade',order_by)
                user_designation = TCoreUserDetail.objects.filter(
                    cu_is_deleted=False).order_by('designation__cod_name')
                #print('user_designation_desc',user_designation)
                designation_list=[]
                for u_g in user_designation:
                    designation_id=u_g.cu_user.id
                    designation_list.append(designation_id)
                #print('designation_list',designation_list)
                clauses = ' '.join(['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(designation_list)])
                ordering = 'CASE %s END' % clauses
                queryset =  self.queryset.filter(pk__in=designation_list,**filter,**date_filter,**total_filter).extra(select={'ordering': ordering}, order_by=('ordering',))
                #print('queryset',queryset)
                return queryset
            if field_name =='designation' and order_by =='desc':
                #print('user_grade',order_by)
                user_designation = TCoreUserDetail.objects.filter(
                    cu_is_deleted=False).order_by('-designation__cod_name')
                #print('user_designation_desc',user_designation)
                designation_list=[]
                for u_g in user_designation:
                    designation_id=u_g.cu_user.id
                    designation_list.append(designation_id)
                #print('designation_list',designation_list)
                clauses = ' '.join(['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(designation_list)])
                ordering = 'CASE %s END' % clauses
                queryset =  self.queryset.filter(pk__in=designation_list,**filter,**date_filter,**total_filter).extra(select={'ordering': ordering}, order_by=('ordering',))
                #print('queryset',queryset)
                return queryset
            if field_name =='reporting_head' and order_by =='asc':
                #print('user_grade',order_by)
                user_designation = TCoreUserDetail.objects.filter(
                    cu_is_deleted=False).order_by('reporting_head_id__first_name')
                #print('user_designation_desc',user_designation)
                designation_list=[]
                for u_g in user_designation:
                    designation_id=u_g.cu_user.id
                    designation_list.append(designation_id)
                #print('designation_list',designation_list)
                clauses = ' '.join(['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(designation_list)])
                ordering = 'CASE %s END' % clauses
                queryset =  self.queryset.filter(pk__in=designation_list,**filter,**date_filter,**total_filter).extra(select={'ordering': ordering}, order_by=('ordering',))
                #print('queryset',queryset)
                return queryset
            if field_name =='reporting_head' and order_by =='desc':
                #print('user_grade',order_by)
                user_designation = TCoreUserDetail.objects.filter(
                    cu_is_deleted=False).order_by('-reporting_head_id__first_name')
                #print('user_designation_desc',user_designation)
                designation_list=[]
                for u_g in user_designation:
                    designation_id=u_g.cu_user.id
                    designation_list.append(designation_id)
                #print('designation_list',designation_list)
                clauses = ' '.join(['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(designation_list)])
                ordering = 'CASE %s END' % clauses
                queryset =  self.queryset.filter(pk__in=designation_list,**filter,**date_filter,**total_filter).extra(select={'ordering': ordering}, order_by=('ordering',))
                #print('queryset',queryset)
                return queryset
            if field_name =='hod' and order_by =='asc':
                #print('user_grade',order_by)
                user_designation = TCoreUserDetail.objects.filter(
                    cu_is_deleted=False).order_by('hod_id__first_name')
                #print('user_designation_desc',user_designation)
                designation_list=[]
                for u_g in user_designation:
                    designation_id=u_g.cu_user.id
                    designation_list.append(designation_id)
                #print('designation_list',designation_list)
                clauses = ' '.join(['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(designation_list)])
                ordering = 'CASE %s END' % clauses
                queryset =  self.queryset.filter(pk__in=designation_list,**filter,**date_filter,**total_filter).extra(select={'ordering': ordering}, order_by=('ordering',))
                #print('queryset',queryset)
                return queryset
            if field_name =='hod' and order_by =='desc':
                #print('user_grade',order_by)
                user_designation = TCoreUserDetail.objects.filter(
                    cu_is_deleted=False).order_by('-hod_id__first_name')
                #print('user_designation_desc',user_designation)
                designation_list=[]
                for u_g in user_designation:
                    designation_id=u_g.cu_user.id
                    designation_list.append(designation_id)
                #print('designation_list',designation_list)
                clauses = ' '.join(['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(designation_list)])
                ordering = 'CASE %s END' % clauses
                queryset =  self.queryset.filter(pk__in=designation_list,**filter,**date_filter,**total_filter).extra(select={'ordering': ordering}, order_by=('ordering',))
                #print('queryset',queryset)
                return queryset
       
        elif filter :
            return self.queryset.filter(**filter)
        elif date_filter:
            return self.queryset.filter(**date_filter)
        elif total_filter:
            return self.queryset.filter(**total_filter)
        else:
            user_total_experience_details = TCoreUserDetail.objects.filter(
                    cu_is_deleted=False).order_by('-joining_date')
            total_experience_details_list = []
            for u_g in user_total_experience_details:
                total_experience_details_id = u_g.cu_user.id
                total_experience_details_list.append(total_experience_details_id)
            #print('current_ctc_details_list', total_experience_details_list)
            clauses = ' '.join(
                ['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(total_experience_details_list)])
            ordering = 'CASE %s END' % clauses
            queryset = self.queryset.filter(pk__in=total_experience_details_list).extra(
                select={'ordering': ordering}, order_by=('ordering',))           
            #print('queryset', queryset)
            return queryset

                       

    @response_modify_decorator_list_or_get_after_execution_for_pagination
    def get(self, request, *args, **kwargs):
        response=super(EmployeeListForHrView,self).get(self, request, args, kwargs)
        for data in response.data['results']:
            hr_details=TCoreUserDetail.objects.filter(cu_user=data['id'],cu_is_deleted=False).values(
                    'cu_emp_code','sap_personnel_no','cu_punch_id','joining_date','cu_phone_no',
                    'department__id','department__cd_name','reporting_head__id','designation__id','designation__cod_name',
                    'hod__id'
                    )
            if hr_details:
                data['name']=userdetails(data['id'])
                data['emp_code']=hr_details[0]['cu_emp_code'] 
                data['cu_punch_id']=hr_details[0]['cu_punch_id'] 
                data['sap_personnel_no']=hr_details[0]['sap_personnel_no'] 
                data['joining_date']=hr_details[0]['joining_date'] 
                data['cu_phone_no']=hr_details[0]['cu_phone_no']
                data['department_id']=hr_details[0]['department__id'] 
                data['department_name']=hr_details[0]['department__cd_name'] 
                data['designation__id']=hr_details[0]['designation__id'] 
                data['designation__cod_name']=hr_details[0]['designation__cod_name'] 
                data['reporting_head__id']=hr_details[0]['reporting_head__id'] 
                data['reporting_head__name']=userdetails(data['reporting_head__id'])
                data['hod__id']=hr_details[0]['hod__id']
                data['hod__name']=userdetails(data['hod__id'])
                
        return response 

      
class DocumentAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = HrmsDocument.objects.filter(is_deleted=False)
    serializer_class =DocumentAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('user','tab_name','field_label')
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response

class DocumentDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = HrmsDocument.objects.all()
    serializer_class =DocumentDeleteSerializer

class HrmsEmployeeProfileDocumentAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = HrmsDynamicSectionFieldLabelDetailsWithDoc.objects.filter(is_deleted=False)
    serializer_class = HrmsEmployeeProfileDocumentAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('user','tab_name','field_label')
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response

class HrmsEmployeeProfileDocumentDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = HrmsDynamicSectionFieldLabelDetailsWithDoc.objects.all()
    serializer_class =HrmsEmployeeProfileDocumentDeleteSerializer

class HrmsEmployeeAcademicQualificationAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = HrmsUserQualification.objects.filter(is_deleted=False)
    serializer_class =HrmsEmployeeAcademicQualificationAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('user','qualification')
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response

class HrmsEmployeeAcademicQualificationDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = HrmsUserQualification.objects.all()
    serializer_class =HrmsEmployeeAcademicQualificationDeleteSerializer

class HrmsEmployeeAcademicQualificationDocumentAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = HrmsUserQualificationDocument.objects.filter(is_deleted=False)
    serializer_class =HrmsEmployeeAcademicQualificationDocumentAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('user_qualification',)
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response

class HrmsEmployeeAcademicQualificationDocumentDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = HrmsUserQualificationDocument.objects.all()
    serializer_class =HrmsEmployeeAcademicQualificationDocumentDeleteSerializer

class EmployeeAddByCSVorExcelView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    @response_modify_decorator_post  
    def post(self, request, format=None):
        
        '''
            Modify as per details 05.02.2020
        '''
        try:
            import random
            document = request.data['document']
            # print('document',type(document))
            # print('document_name',document)
            logdin_user_id = self.request.user.id
            print('logdin_user_id',logdin_user_id)
            user_list = []
            user_duplicate_list=[]
            total_result={}
            data = pd.read_excel(document,converters={
                'official_email_id':str,
                'punch_id':str,'emp_code':str,
                'username':str,'joining_date':str,
                'module_name':str,'sap_personnel_no':str,'job_location_state':str,'phone_no':str}) #read excel
            data.dropna(axis = 0, how ='all', inplace = True) #Remove blank rows with all nun column
            data = data.loc[:, ~data.columns.str.contains('^Unnamed')] #Remove blank unnamed column
            data = data.replace(np.nan,'',regex=True) # for replace blank value with nan

            #print('data',data)
            
            # data1=pd.DataFrame(data)
            #print('data1',data)
            filter_t_core_user={}
            filter_grade={}
            user_blank_list=[]
            leave_filter={}
            with transaction.atomic():
                for index, row in data.iterrows():
                    #pass
                    #return Response({})
                    if row['first_name']!='' and row['last_name']!='':
                        #print('row',row)
                        if  row['punch_id'] == '' or  row['emp_code'] == '' or row['joining_date'] == '' or row['module_name'] == '':
                            user_blank_dict={
                                'cu_emp_code':row['emp_code'],
                                'cu_punch_id':row['punch_id'],
                                'module_name':row['module_name'],
                                'joining_date':row['joining_date'],
                                'first_name':row['first_name'],
                                'last_name':row['last_name']
                            }
                            user_blank_list.append(user_blank_dict)
                            
                        else:
                            #print('sddsdsds')
                            #print('row',row['module_name'])
                            company_det=TCoreCompany.objects.filter(coc_name=(row['company_name']).lower(),coc_is_deleted=False)
                            if company_det:
                                for c_d in company_det: 
                                    filter_t_core_user['company_id']=c_d.id
                            else:
                                filter_t_core_user['company_id']=None
                                
                            department_det=TCoreDepartment.objects.filter(cd_name=(row['department_name']).lower(),cd_is_deleted=False)
                            if department_det:
                                for d_t in department_det:
                                    filter_t_core_user['department_id']=d_t.id
                            else:
                                filter_t_core_user['department_id']=None
                                                    
                            designation_det=TCoreDesignation.objects.filter(cod_name=(row['designation_name']).lower(),cod_is_deleted=False)
                            if designation_det:
                                for desig in designation_det:
                                    filter_t_core_user['designation_id']=desig.id
                                    filter_grade['mmr_designation_id']=desig.id
                            else:
                                filter_t_core_user['designation_id']=None
                                filter_grade['mmr_designation_id']=None


                            grade_det=TCoreGrade.objects.filter(cg_name=(row['grade_name']).lower(),cg_is_deleted=False)
                            if grade_det:
                                for g_t in grade_det:
                                    filter_t_core_user['employee_grade_id']=g_t.id
                            else:
                                filter_t_core_user['employee_grade_id']=None

                            
                            salary_type=row['salary_type'] if row['salary_type'] else ''
                            # print('salary_type',type(salary_type))
                            salary_type_det=TCoreSalaryType.objects.filter(st_name=salary_type,st_is_deleted=False)
                            if salary_type_det:
                                for s_t in salary_type_det:
                                    filter_t_core_user['salary_type_id']=s_t.id
                            else:
                                filter_t_core_user['salary_type_id']=None
                            
                            if row['job_location_state']:
                                job_location_state_det =TCoreState.objects.filter(
                                    cs_state_name=row['job_location_state'],cs_is_deleted=False)
                                if job_location_state_det:
                                    job_location_state_det = TCoreState.objects.get(
                                    cs_state_name=row['job_location_state'],cs_is_deleted=False)
                                    filter_t_core_user['job_location_state']=job_location_state_det

                            else:
                                filter_t_core_user['job_location_state']=None


                            gender=row['gender'] if row['gender'] else None
                            if gender:
                                if row['gender'].lower()=='male':
                                    filter_t_core_user['cu_gender']='male'
                                elif row['gender'].lower()=='female':
                                    filter_t_core_user['cu_gender']='female'
                        
                            cu_phone_no=row['phone_no'] if row['phone_no'] else ''

                            #print('date_of_birth',len(row['date_of_birth']),type(row['date_of_birth']))

                            # if len(row['date_of_birth']) == 0:
                            #     cu_dob = None
                            # else: 
                            #     cu_dob=datetime.datetime.strptime(row['date_of_birth'],"%Y-%m-%d %H:%M:%S").date()
                            
                            
                            #initial_ctc = row['initial_ctc'] if row['initial_ctc'] else Decimal(0.0)
                            #current_ctc= row['current_ctc'] if  row['current_ctc'] else Decimal(0.0)
                            cost_centre = row['cost_centre'] if row['cost_centre'] else ''
                            #address = row['address'] if row['address'] else ''
                            source=row['source'] if row['source'] else None
                            source_name=row['source_name'] if row['source_name'] else None
                            total_experience=  row['total_experience'] if  row['total_experience'] else Decimal(0.0)
                            job_location = row['job_location'] if row['job_location'] else ''
                            granted_cl= row['granted_cl'] if  row['granted_cl'] else 10
                            granted_el= row['granted_el'] if  row['granted_el'] else 15
                            granted_sl= row['granted_sl'] if  row['granted_sl'] else 7
                            joining_date=row['joining_date'] 
                            joined_date = datetime.datetime.strptime(joining_date,"%Y-%m-%d %H:%M:%S").date()
                            joined_year=joined_date.year
                            pf_number = row['pf_number'] if row['pf_number'] else ''
                            esic_number = row['esic_number'] if row['esic_number'] else ''
                        

                            daily_loginTime=row['daily_loginTime'] if row['daily_loginTime'] else "10:00:00"
                            daily_logoutTime=row['daily_logoutTime'] if row['daily_logoutTime'] else "19:00:00"
                            lunch_start=row['lunch_start'] if row['lunch_start'] else "13:30:00"
                            lunch_end=row['lunch_end'] if row['lunch_end'] else "14:00:00"
                            worst_late=row['worst_late'] if row['worst_late'] else "14:00:00"


                            print('before_check')
                            if TCoreUserDetail.objects.filter((
                                Q(cu_punch_id=row['punch_id']) |
                                Q(cu_emp_code=row['emp_code'])) & Q(cu_is_deleted=False)).count() == 0:
                                print('under')
                                username_generate = row['first_name']+row['last_name']
                                print('username_generate',username_generate)
                                check_user_exist = User.objects.filter(username = username_generate)
                                print('check_user_exist',check_user_exist)
                                if check_user_exist:
                                    username_generate = username_generate+str(random.randint(1,6))
                                
                                print('username_generate',username_generate)
                                user=User.objects.create(first_name=row['first_name'],
                                                    last_name=row['last_name'],
                                                    username=username_generate,
                                                    email=row['official_email_id']
                                                    )
                                '''
                                    Modified by Rupam Hazra to set default password
                                '''
                                password = 'Shyam@123'
                                user.set_password(password)
                                user.save()
                                #print('user',user.id)
                                data_dict = {
                                'id': user.id,
                                'first_name':user.first_name,
                                'last_name':user.last_name,
                                'username':user.username,
                                'email':user.email
                                }
                                #print('data_dict',data_dict)
                                user_detail = TCoreUserDetail.objects.create(cu_user=user,
                                                                    cu_phone_no=cu_phone_no,
                                                                    cu_alt_email_id = row['official_email_id'],
                                                                    password_to_know=password,
                                                                    cu_emp_code=row['emp_code'],
                                                                    cu_punch_id=row['punch_id'],
                                                                    #cu_dob=cu_dob,
                                                                    sap_personnel_no=row['sap_personnel_no'],
                                                                    #initial_ctc=initial_ctc,
                                                                    #current_ctc=current_ctc,
                                                                    cost_centre=cost_centre,
                                                                    #address=address,
                                                                    source=source,
                                                                    source_name=source_name,
                                                                    total_experience=total_experience,
                                                                    job_location=job_location,
                                                                    pf_no=pf_number,
                                                                    esic_no=esic_number,
                                                                    granted_cl=granted_cl,
                                                                    granted_el=granted_el,
                                                                    granted_sl=granted_sl,
                                                                    joining_date=joining_date,
                                                                    daily_loginTime=daily_loginTime,
                                                                    daily_logoutTime=daily_logoutTime,
                                                                    lunch_start=lunch_start,
                                                                    lunch_end=lunch_end,
                                                                    worst_late=worst_late,
                                                                    **filter_t_core_user,
                                                                    cu_created_by_id=logdin_user_id
                                                                    )            
                                #print('user_detail',user_detail)                
                                data_dict['cu_emp_code']= user_detail.cu_emp_code
                                data_dict['cu_punch_id']=user_detail.cu_punch_id
                                data_dict['sap_personnel_no']=user_detail.sap_personnel_no
                                data_dict['cu_phone_no']= user_detail.cu_phone_no if user_detail.cu_phone_no else None
                                data_dict['joining_date']= user_detail.joining_date if user_detail.joining_date else None
                                data_dict['daily_loginTime']= user_detail.daily_loginTime if user_detail.daily_loginTime else None
                                data_dict['daily_logoutTime']= user_detail.daily_logoutTime if user_detail.daily_logoutTime else None
                                data_dict['lunch_start']= user_detail.lunch_start if user_detail.lunch_start else None
                                data_dict['lunch_end']= user_detail.lunch_end if user_detail.lunch_end else None
                                data_dict['worst_late']= user_detail.worst_late if user_detail.worst_late else None
                                # data_dict['initial_ctc']=user_detail.initial_ctc if user_detail.initial_ctc else None
                                # data_dict['current_ctc']=user_detail.current_ctc if user_detail.current_ctc else None
                                # data_dict['cost_centre']=user_detail.cost_centre if user_detail.cost_centre else None
                                # data_dict['address']=user_detail.address if user_detail.address else None
                                # data_dict['source']=user_detail.source if user_detail.source else None
                                # data_dict['total_experience']=user_detail.total_experience if user_detail.total_experience else None
                                # data_dict['job_location']=user_detail.job_location if user_detail.job_location else None
                                # data_dict['job_location_state']=user_detail.job_location_state if user_detail.job_location_state else None
                                # data_dict['granted_cl']=user_detail.granted_cl if user_detail.granted_cl else None
                                # data_dict['granted_el']=user_detail.granted_el if user_detail.granted_el else None
                                # data_dict['granted_sl']=user_detail.granted_sl if user_detail.granted_sl else None
                                # data_dict['company_id']=user_detail.company.id if user_detail.company else None
                                # data_dict['company_name']=user_detail.company.coc_name if user_detail.company else None
                                # data_dict['designation_id']=user_detail.designation.id if user_detail.designation else None
                                # data_dict['designation_name']=user_detail.designation.cod_name if user_detail.designation else None
                                # data_dict['department_id']=user_detail.department.id if user_detail.department else None
                                # data_dict['department_name']=user_detail.department.cd_name if user_detail.department else None
                                # data_dict['grade']=user_detail.employee_grade.id if user_detail.employee_grade else None
                                # data_dict['grade_name']=user_detail.employee_grade.cg_name if user_detail.employee_grade else None 
                                # data_dict['cu_gender'] =user_detail.cu_gender if user_detail.cu_gender else None
                                #print('data_dict111',data_dict)

                                '''
                                    For multiple modules
                                '''
                                #print('module_name',row['module_name'])
                                modules = row['module_name'].split(',')
                                #print('modules',modules)
                                for module in modules:
                                    if module == 'HRMS' : 
                                        module = 'ATTENDANCE & HRMS'

                                    module_det=TCoreModule.objects.filter(cm_name=module,cm_is_deleted=False)
                                    #print('module_det',module_det)
                                    if module_det:
                                        for m_d in module_det:
                                            filter_grade['mmr_module_id']=m_d.id
                                    else:
                                        filter_grade['mmr_module_id']=None

                                    role_user=TMasterModuleRoleUser.objects.create(
                                                                            mmr_user = user,
                                                                            mmr_type=3,
                                                                            **filter_grade,
                                                                            mmr_created_by_id =logdin_user_id
                                                                            )

                                data_dict['module_id']=role_user.mmr_module.id
                                data_dict['module_name']=role_user.mmr_module.cm_name
                                data_dict['mmr_type']=role_user.mmr_type

                                #print('data_dict',data_dict)
                                                        
                                user_list.append(data_dict)
                                
                                total_month_grace=AttendenceMonthMaster.objects.filter(month_start__date__lte=joined_date,
                                            month_end__date__gte=joined_date,is_deleted=False).values('grace_available',
                                                                                    'year_start_date',
                                                                                    'year_end_date',
                                                                                    'month',
                                                                                    'month_start',
                                                                                    'month_end'
                                                                                    )
                                if total_month_grace:
                                    year_start_date=total_month_grace[0]['year_start_date'].date()
                                    year_end_date=total_month_grace[0]['year_end_date'].date()
                                    total_days=(year_end_date - joined_date).days
                                    # print('total_days',total_days)
                                    calculated_cl=round((total_days/365)* int(granted_cl))
                                    leave_filter['cl']=calculated_cl
                                    calculated_el=round((total_days/365)* int(granted_el))
                                    leave_filter['el']=calculated_el
                                    if granted_sl:
                                        calculated_sl=round((total_days/365)* int(granted_sl))
                                        # print('calculated_sl',calculated_sl)
                                        leave_filter['sl']=calculated_sl
                                    else:
                                        leave_filter['sl']=None

                                    month_start_date=total_month_grace[0]['month_start'].date()
                                    month_end_date=total_month_grace[0]['month_end'].date()
                                    # print('month_start_date',month_start_date,month_end_date)
                                    month_days=(month_end_date-month_start_date).days
                                    # print('month_days',month_days)
                                    remaining_days=(month_end_date-joined_date).days
                                    # print('remaining_days',remaining_days)
                                    available_grace = round((remaining_days/month_days)*int(total_month_grace[0]['grace_available']))
                                    # print('available_grace',available_grace)
                
                                    if year_start_date<joined_date:
                                        JoiningApprovedLeave.objects.get_or_create(employee=user,
                                                                            year=joined_year,
                                                                            month=total_month_grace[0]['month'],
                                                                            **leave_filter,
                                                                            first_grace=available_grace,
                                                                            created_by_id=logdin_user_id,
                                                                            owned_by_id=logdin_user_id
                                                                            )
                                
                                if row['official_email_id']:
                    
                                    #============= Mail Send ==============#

                                    # Send mail to employee with login details
                                    mail_data = {
                                                "name": user.first_name+ '' + user.last_name,
                                                "user": username_generate,
                                                "pass": password
                                        }
                                    #print('mail_data',mail_data)
                                    mail_class = GlobleMailSend('EMP001', [row['official_email_id']])
                                    mail_thread = Thread(target = mail_class.mailsend, args = (mail_data,))
                                    mail_thread.start()

                                # Send mail to who added the employee
                                t_core_user = TCoreUserDetail.objects.filter(cu_user=self.request.user)
                                if t_core_user:
                                    add_cu_alt_email_id = t_core_user[0]
                                    if add_cu_alt_email_id.cu_alt_email_id:
                                        mail_data = {
                                                    "name": self.request.user.first_name+ ' ' + self.request.user.last_name,
                                                    "user": username_generate,
                                                    "pass": password
                                            }
                                        #print('mail_data',mail_data)
                                        mail_class = GlobleMailSend('EMPA001', [add_cu_alt_email_id.cu_alt_email_id])
                                        mail_thread = Thread(target = mail_class.mailsend, args = (mail_data,))
                                        mail_thread.start()
                            else:
                                print('duplicate')
                                duplicate_data={
                                    'first_name':row['first_name'],
                                    'last_name':row['last_name'],
                                    'cu_emp_code':row['emp_code'],
                                    'cu_punch_id':row['punch_id'],
                                    'sap_personnel_no':row['sap_personnel_no'],
                                    'module_name':row['module_name'],
                                    'joining_date':row['joining_date']
                                }
                                user_duplicate_list.append(duplicate_data)
                            
                        total_result['user_duplicate_list']=user_duplicate_list
                        total_result['user_added_list']=user_list
                        total_result['user_not_added_list_due_to_required_fields']=user_blank_list

            return Response(total_result)
  
        except Exception as e:
            raise e
            # raise APIException({'msg':settings.MSG_ERROR,
            #                     'error':e,
            #                     "request_status": 0
            #                     })

#:::::::::::::::::::::: HRMS NEW REQUIREMENT:::::::::::::::::::::::::::#
class HrmsNewRequirementAddView(generics.ListCreateAPIView, mixins.UpdateModelMixin):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = HrmsNewRequirement.objects.filter(is_deleted=False)
    serializer_class = HrmsNewRequirementAddSerializer
    # pagination_class = OnOffPagination

    def get_queryset(self):
        req_id = self.request.query_params.get('req_id', None)
        queryset = self.queryset.filter(id = req_id,tab_status__gte=2)

        return queryset
    # @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        # page_size = self.request.query_params.get('page_size', None)
        response=super(HrmsNewRequirementAddView,self).get(self, request, args, kwargs)
        data_dict={}
        print("response",response.data)

        def userdetails(user):
            print(type(user))
            if isinstance(user,(int)):
                name = User.objects.filter(id =user)
                for i in name:
                    print("i",i)
                    f_name_l_name = i.first_name +" "+ i.last_name
                    print("f_name_l_name",f_name_l_name)
            elif isinstance(user,(str)):
                print(user ,"str")
                name = User.objects.filter(username=user)
                for i in name:
                    print("i",i)
                    f_name_l_name = i.first_name +" "+ i.last_name
                    print("f_name_l_name",f_name_l_name)
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
                desg_data = TCoreDesignation.objects.filter(id = designation )
                if desg_data:
                    for desg in desg_data:
                        return desg.cod_name
                else:
                    return None


        def display(data):
            age_group_data=  HrmsNewRequirement.objects.filter(id=response.data[0]['id'],
                    desired_age_group=data)
            for age_group in age_group_data:
                return age_group.get_desired_age_group_display()

        def department(department):
            if isinstance(department,(str)):
                desg_data  = TCoreUserDetail.objects.filter(cu_user__username =department)
                if desg_data:
                    for desg in desg_data:
                        return desg.department.cd_name
                else:
                    return None
            elif isinstance(department,(int)):
                desg_data = TCoreDepartment.objects.filter(id = department )
                if desg_data:
                    for desg in desg_data:
                        return desg.cd_name
                else:
                    return None

        for data in response.data:

            response.data[0]['desired_age_group'] = display(data['desired_age_group'])
            data_dict['reporting_to_name'] = userdetails(data['reporting_to'])
            data_dict['issuing_department_name']=department(data['issuing_department'])
            data_dict['proposed_designation_name']=designation(data['proposed_designation'])
            # {
            #     'issuing_department_name':department(data['issuing_department']),
            #     'proposed_designation_name':designation(data['proposed_designation'])
            # }
            data_dict['raised_by_data']={
                "mrf_raised_by":userdetails(data['created_by']),
                "date":data['created_at'],
                "designation":designation(data['created_by']),
                "department":department(data['created_by'])
            }
            data_dict['recommended_by_data']={
                "recommended_by":userdetails(data['reporting_to']),
                "date":data['created_at'],
                "designation":designation(data['created_by']),
                "department":department(data['created_by'])
            }
            section_name = self.request.query_params.get('section_name', None)
            if section_name:
                permission_details=[]
                section_details=TCoreOther.objects.get(cot_name__iexact=section_name)
                approval_master_details = PmsApprovalPermissonMatser.objects.filter(section=section_details.id)
                # print("approval_master_details",approval_master_details)
                log_details=HrmsNewRequirementLog.objects.\
                        filter(master_hnr=response.data[0]['id']).\
                            values('id','level_approval','approval_permission_user_level','tag_name','created_at')
                # print('log_details',log_details)
                amd_list=[]
                l_d_list=[]
                for l_d in log_details:
                    # if l_d['tag_name']=='approval':
                    l_d_list.append(l_d['approval_permission_user_level'])

                for a_m_d in approval_master_details:
                    if l_d_list:
                        if a_m_d.id in l_d_list:
                            l_d=log_details.get(approval_permission_user_level=a_m_d.id)
                            f_name = a_m_d.approval_user.first_name if a_m_d.approval_user else ''
                            l_name = a_m_d.approval_user.last_name if a_m_d.approval_user else ''
                            # var=a_m_d.permission_level
                            # res = re.sub("\D", "", var)
                            permission_dict={
                                "user_level":a_m_d.permission_level,
                                "approval":l_d['level_approval'],
                                # "permission_num":int(res),
                                "tag_name":l_d['tag_name'],
                                "approved_date":l_d['created_at'],
                                "user_details":{
                                    "id":a_m_d.approval_user.id if a_m_d.approval_user else None,
                                    "email":a_m_d.approval_user.email if a_m_d.approval_user else None,
                                    "name":  f_name +' '+l_name,
                                    "username":a_m_d.approval_user.username,
                                    "department":department(a_m_d.approval_user.id),
                                    "designation":designation(a_m_d.approval_user.id)
                                    }
                            }


                        else:
                            f_name = a_m_d.approval_user.first_name if a_m_d.approval_user else ''
                            l_name = a_m_d.approval_user.last_name if a_m_d.approval_user else ''
                            # var=a_m_d.permission_level
                            # res = re.sub("\D", "", var)
                            permission_dict={
                                "user_level":a_m_d.permission_level,
                                # "permission_num":int(res),
                                "approval":None,
                                "tag_name":None,
                                "approved_date":None,
                                "user_details":{
                                    "id":a_m_d.approval_user.id if a_m_d.approval_user else None,
                                    "email":a_m_d.approval_user.email if a_m_d.approval_user else None,
                                    "name":  f_name +' '+l_name,
                                    "username":a_m_d.approval_user.username,
                                    "department":department(a_m_d.approval_user.id),
                                    "designation":designation(a_m_d.approval_user.id)
                                    }
                            }

                        permission_details.append(permission_dict)
                    else:
                        f_name = a_m_d.approval_user.first_name if a_m_d.approval_user else ''
                        l_name = a_m_d.approval_user.last_name if a_m_d.approval_user else ''
                        # var=a_m_d.permission_level
                        # res = re.sub("\D", "", var)
                        permission_dict={
                                "user_level":a_m_d.permission_level,
                                # "permission_num":int(res),
                                "approval":None,
                                "tag_name":None,
                                "approved_date":None,
                                "user_details":{
                                    "id":a_m_d.approval_user.id if a_m_d.approval_user else None,
                                    "email":a_m_d.approval_user.email if a_m_d.approval_user else None,
                                    "name":  f_name +' '+l_name,
                                    "username":a_m_d.approval_user.username,
                                    "department":department(a_m_d.approval_user.id),
                                    "designation":designation(a_m_d.approval_user.id)
                                    }
                            }
                        permission_details.append(permission_dict)

            data_dict['approved_by_data']=permission_details

            # print("data_dict",data_dict)
        
        response.data[0].update(data_dict)
        data_sp_dict = {}
        data_sp_dict['result'] = response.data[0]
        if response.data:
            data_sp_dict['request_status'] = 1
            data_sp_dict['msg'] = settings.MSG_SUCCESS
        elif len(response.data) == 0:
            data_sp_dict['request_status'] = 1
            data_sp_dict['msg'] = settings.MSG_NO_DATA
        else:
            data_sp_dict['request_status'] = 0
            data_sp_dict['msg'] = settings.MSG_ERROR
        response.data = data_sp_dict
        return response

    def put(self, request, *args, **kwargs):
        updated_by=request.user
        created_by=request.user
        # print(updated_by)

        req_id = self.request.query_params.get('req_id', None)
        approval_tag = self.request.query_params.get('approval_tag', None)
        approval_permission_user_level = request.data['approval_permission_user_level']

        if approval_tag.lower() == 'approval':

            level_approval= request.data['level_approval']

            updating_table = HrmsNewRequirement.objects.filter(id=req_id).update(
                approval_permission_user_level=approval_permission_user_level,
                level_approval=level_approval,updated_by=updated_by
            )
            data = HrmsNewRequirement.objects.filter(id=req_id)
            for obj in data.values():
                print(obj)
                log_create = HrmsNewRequirementLog.objects.create(
                    master_hnr_id=obj['id'],
                    issuing_department_id=obj['issuing_department_id'],
                    date = obj['date'],
                    type_of_vacancy=obj['type_of_vacancy'],
                    type_of_requirement=obj['type_of_requirement'],
                    reason = obj['reason'],
                    number_of_position=obj['number_of_position'],
                    proposed_designation_id=obj['proposed_designation_id'],
                    location=obj['location'],
                    substantiate_justification=['substantiate_justification'],
                    document=obj['document'],
                    desired_qualification=obj['desired_qualification'],
                    desired_experience=obj['desired_experience'],
                    desired_age_group=obj['desired_age_group'],
                    tab_status=obj['tab_status'],
                    gender=obj['gender'],
                    reporting_to_id=obj['reporting_to_id'],
                    number_of_subordinates=obj['number_of_subordinates'],
                    ctc = obj['ctc'],
                    required_skills=obj['required_skills'],
                    level_approval=obj['level_approval'],
                    tag_name = approval_tag.lower(),
                    created_by=created_by,
                    approval_permission_user_level_id=obj['approval_permission_user_level_id']


                )

            return Response(request.data)

        elif approval_tag.lower() == 'recieved':

            reciever_approval= request.data['reciever_approval']
            reciever_remarks= request.data['reciever_remarks']
            if reciever_approval == 1 :
                updating_table = HrmsNewRequirement.objects.filter(id=req_id).update(
                    approval_permission_user_level=approval_permission_user_level,
                    reciever_approval=reciever_approval,updated_by=updated_by,
                    reciever_remarks=reciever_remarks,tab_status=3
                )
            else:
                updating_table = HrmsNewRequirement.objects.filter(id=req_id).update(
                    approval_permission_user_level=approval_permission_user_level,
                    reciever_approval=reciever_approval,updated_by=updated_by,
                    reciever_remarks=reciever_remarks
                )

            data = HrmsNewRequirement.objects.filter(id=req_id)
            for obj in data.values():
                print(obj)
                log_create = HrmsNewRequirementLog.objects.create(
                    master_hnr_id=obj['id'],
                    issuing_department_id=obj['issuing_department_id'],
                    date = obj['date'],
                    type_of_vacancy=obj['type_of_vacancy'],
                    type_of_requirement=obj['type_of_requirement'],
                    reason = obj['reason'],
                    number_of_position=obj['number_of_position'],
                    proposed_designation_id=obj['proposed_designation_id'],
                    location=obj['location'],
                    substantiate_justification=obj['substantiate_justification'],
                    document=obj['document'],
                    desired_qualification=obj['desired_qualification'],
                    desired_experience=obj['desired_experience'],
                    desired_age_group=obj['desired_age_group'],
                    tab_status=obj['tab_status'],
                    gender=obj['gender'],
                    reporting_to_id=obj['reporting_to_id'],
                    number_of_subordinates=obj['number_of_subordinates'],
                    ctc = obj['ctc'],
                    required_skills=obj['required_skills'],
                    level_approval=obj['reciever_approval'],
                    tag_name = approval_tag.lower(),
                    reciever_remarks=reciever_remarks,
                    created_by=created_by,
                    approval_permission_user_level_id=obj['approval_permission_user_level_id']


                )

            return Response(request.data)

#:::::::::::::::::::::: HRMS INTERVIEW TYPE:::::::::::::::::::::::::::#
class InterviewTypeAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = HrmsInterviewType.objects.filter(is_deleted=False)
    serializer_class = InterviewTypeAddSerializer

    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response

class InterviewTypeEditView(generics.RetrieveUpdateAPIView):
	permission_classes = [IsAuthenticated]
	authentication_classes = [TokenAuthentication]
	queryset = HrmsInterviewType.objects.all()
	serializer_class = InterviewTypeEditSerializer

class InterviewTypeDeleteView(generics.RetrieveUpdateAPIView):
	permission_classes = [IsAuthenticated]
	authentication_classes = [TokenAuthentication]
	queryset = HrmsInterviewType.objects.all()
	serializer_class = InterviewTypeDeleteSerializer

#:::::::::::::::::::::: HRMS INTERVIEW LEVEL:::::::::::::::::::::::::::#
class InterviewLevelAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = HrmsInterviewLevel.objects.filter(is_deleted=False)
    serializer_class = InterviewLevelAddSerializer

    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response

class InterviewLevelEditView(generics.RetrieveUpdateAPIView):
	permission_classes = [IsAuthenticated]
	authentication_classes = [TokenAuthentication]
	queryset = HrmsInterviewLevel.objects.all()
	serializer_class = InterviewLevelEditSerializer

class InterviewLevelDeleteView(generics.RetrieveUpdateAPIView):
	permission_classes = [IsAuthenticated]
	authentication_classes = [TokenAuthentication]
	queryset = HrmsInterviewLevel.objects.all()
	serializer_class = InterviewLevelDeleteSerializer

#:::::::::::::::::::::: HRMS SCHEDULE INTERVIEW :::::::::::::::::::::::::::#

class ScheduleInterviewAddView(generics.ListCreateAPIView,mixins.UpdateModelMixin):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = HrmsScheduleInterview.objects.filter(is_deleted=False)
    serializer_class = ScheduleInterviewAddSerializer

    @response_modify_decorator_post
    def post(self, request, *args, **kwargs):
        # print('request',request.data)
        contact_no=request.data['contact_no']
        print('contact_no',contact_no)
        if HrmsScheduleInterview.objects.filter(contact_no=contact_no).count() > 0:
            custom_exception_message(self,'Contact no')
        return super().post(request, *args, **kwargs)


    @response_modify_decorator_update
    def put(self, request, *args, **kwargs):
        try:
            updated_by=request.user
            sed_id = self.request.query_params.get('sed_id', None)
            req_id = self.request.query_params.get('req_id', None)
            action_approval = request.data.get('action_approval')
            print("action_approval",action_approval)

            with transaction.atomic():
                # no_of_pos = HrmsNewRequirement.objects.get(id=req_id).number_of_position
                # unique_appoval = HrmsScheduleInterview.objects.filter(requirement=req_id,action_approval=1).annotate(Count('candidate_name',
                #                      distinct=True)).count()
                # print("no_of_pos",no_of_pos,"unique_appoval",unique_appoval)
                # if no_of_pos != unique_appoval:
                HrmsScheduleInterview.objects.filter(id=sed_id).update(
                    action_approval = action_approval
                )
                HrmsNewRequirement.objects.filter(id=req_id).update(tab_status=5)
                    # no_pos = HrmsNewRequirement.objects.get(id=req_id).number_of_position
                    # unique_appoval_count = HrmsScheduleInterview.objects.filter(requirement=req_id,action_approval=1).annotate(Count('candidate_name',
                    #                  distinct=True)).count()
                    # print("no_of_pos",no_pos,"unique_appoval",unique_appoval_count)
                #     if no_pos == unique_appoval_count:
                #         HrmsNewRequirement.objects.filter(id=req_id).update(tab_status=5)
                #         HrmsScheduleInterview.objects.filter(requirement=req_id).exclude(action_approval=1).update(action_approval=2)
                # else:
                #     custom_exception_message(self,None,"Number of position is Fullfilled")


                return request
        except Exception as e:
            raise e

class RescheduleInterviewAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = HrmsScheduleAnotherRoundInterview.objects.filter(is_deleted=False)
    serializer_class =  RescheduleInterviewAddSerializer



class InterviewStatusAddView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = HrmsScheduleAnotherRoundInterview.objects.all()
    serializer_class = InterviewStatusAddSerializer

class InterviewStatusListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = HrmsScheduleInterview.objects.filter(is_deleted=False)
    serializer_class = InterviewStatusListSerializer

    def get_queryset(self):
        approved = self.request.query_params.get('approved', None)
        req_id = self.request.query_params.get('req_id', None)
        cad_id = self.request.query_params.get('cad_id', None)
        if approved:
            if approved.lower() == "yes":
                queryset=self.queryset.filter(requirement=req_id,is_deleted=False,action_approval=1)
        elif cad_id:
            queryset=self.queryset.filter(id=cad_id,requirement=req_id,is_deleted=False)

        else:
            queryset=self.queryset.filter(requirement=req_id,is_deleted=False)

        return queryset

    @response_modify_decorator_get_after_execution
    def get(self, request, *args, **kwargs):
        approved = self.request.query_params.get('approved', None)
        interview_details=self.get_queryset()
        print('interview_details',interview_details)
        interview_details_list=[]
        if interview_details:
            for i_d in interview_details:
                schedule_another_det=HrmsScheduleAnotherRoundInterview.objects.filter(schedule_interview=i_d,
                                                                                    is_deleted=False
                                                                                    )
                interview_rounds_list=[]
                for s_a_d in schedule_another_det:
                    round_details={
                        'id':s_a_d.id,
                        'planned_date_of_interview':s_a_d.planned_date_of_interview,
                        'planned_time_of_interview':s_a_d.planned_time_of_interview,
                        'actual_date_of_interview':s_a_d.actual_date_of_interview,
                        'actual_time_of_interview':s_a_d.actual_time_of_interview,
                        'type_of_interview':s_a_d.type_of_interview.id,
                        'interview_type_name':s_a_d.type_of_interview.name,
                        'level_of_interview':s_a_d.level_of_interview.id,
                        'interview_level_name':s_a_d.level_of_interview.name,
                        'interview_status':s_a_d.interview_status,
                        'interview_status_name':s_a_d.get_interview_status_display(),
                        'is_resheduled':s_a_d.is_resheduled
                    }
                    interview_rounds_list.append(round_details)

                    interviewers=HrmsScheduleInterviewWith.objects.filter(interview=s_a_d,is_deleted=False)
                    print('interviewers',interviewers)
                    interviewers_list=[]
                    int_dict={}
                    section_name = self.request.query_params.get('section_name', None)
                    if section_name:
                        permission_details=[]
                        section_details=TCoreOther.objects.get(cot_name__iexact=section_name)
                        approval_master_details = PmsApprovalPermissonMatser.objects.filter(section=section_details.id)
                        # print("approval_master_details",approval_master_details)
                        log_details=HrmsScheduleInterviewLog.objects.\
                                filter(hsi_master=i_d.id).\
                                    values('id','level_approval','approval_permission_user_level','created_at')
                        # print('log_details',log_details)
                        amd_list=[]
                        l_d_list=[]
                        for l_d in log_details:
                            # if l_d['tag_name']=='approval':
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
                                        "approval":l_d['level_approval'],
                                        "permission_num":int(res),
                                        # "tag_name":l_d['tag_name'],
                                        "approved_date":l_d['created_at'],
                                        "user_details":{
                                            "id":a_m_d.approval_user.id if a_m_d.approval_user else None,
                                            "email":a_m_d.approval_user.email if a_m_d.approval_user else None,
                                            "name":  f_name +' '+l_name,
                                            "username":a_m_d.approval_user.username,
                                            "department":department(a_m_d.approval_user.id),
                                            "designation":designation(a_m_d.approval_user.id)
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
                                        # "tag_name":None,
                                        "approved_date":None,
                                        "user_details":{
                                            "id":a_m_d.approval_user.id if a_m_d.approval_user else None,
                                            "email":a_m_d.approval_user.email if a_m_d.approval_user else None,
                                            "name":  f_name +' '+l_name,
                                            "username":a_m_d.approval_user.username,
                                            "department":department(a_m_d.approval_user.id),
                                            "designation":designation(a_m_d.approval_user.id)
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
                                        # "tag_name":None,
                                        "approved_date":None,
                                        "user_details":{
                                            "id":a_m_d.approval_user.id if a_m_d.approval_user else None,
                                            "email":a_m_d.approval_user.email if a_m_d.approval_user else None,
                                            "name":  f_name +' '+l_name,
                                            "username":a_m_d.approval_user.username,
                                            "department":department(a_m_d.approval_user.id),
                                            "designation":designation(a_m_d.approval_user.id)
                                            }
                                    }
                                permission_details.append(permission_dict)

                    # data_dict['approved_by_data']=permission_details
                    if interviewers:
                        for i_t in interviewers:
                            int_dict={
                                'id':i_t.id,
                                'interview':i_t.interview.id,
                                'user':i_t.user.id,
                                'first_name':i_t.user.first_name,
                                'last_name':i_t.user.last_name,
                            }
                            interviewers_list.append(int_dict)
                    round_details['interviewers']=interviewers_list

                    upload_feedback=HrmsScheduleInterviewFeedback.objects.filter(interview=s_a_d,is_deleted=False)
                    feedback_dict={}
                    if upload_feedback:
                        for u_f in upload_feedback:
                            upload_feedback=request.build_absolute_uri(u_f.upload_feedback.url) if u_f.upload_feedback else None
                            feedback_dict={
                                'id':u_f.id,
                                'interview':u_f.interview.id,
                                'upload_feedback':upload_feedback
                            }
                    round_details['feedback']=feedback_dict

                    resume=request.build_absolute_uri(i_d.resume.url) if i_d.resume else None
                    if approved and approved.lower() == "yes":
                        interview_dict={
                            'id':i_d.id,
                            'candidate_name':i_d.candidate_name,
                            'contact_no':i_d.contact_no,
                            'email':i_d.email,
                            'note':i_d.note,
                            'resume':resume,
                            "interview_rounds":interview_rounds_list,
                            'notice_period':i_d.notice_period,
                            'expected_ctc':i_d.expected_ctc,
                            'current_ctc':i_d.current_ctc,
                            'action_approval':i_d.get_action_approval_display(),
                            'approved_by_data':permission_details
                        }
                    else:
                        interview_dict={
                            'id':i_d.id,
                            'candidate_name':i_d.candidate_name,
                            'contact_no':i_d.contact_no,
                            'email':i_d.email,
                            'note':i_d.note,
                            'resume':resume,
                            "interview_rounds":interview_rounds_list,
                            'action_approval':i_d.get_action_approval_display(),
                            'approved_by_data':permission_details
                        }
                interview_details_list.append(interview_dict)

        return Response(interview_details_list)

class CandidatureUpdateEditView(generics.RetrieveUpdateAPIView):
	permission_classes = [IsAuthenticated]
	authentication_classes = [TokenAuthentication]
	queryset = HrmsScheduleInterview.objects.filter(is_deleted=False)
	serializer_class = CandidatureUpdateEditSerializer

class CandidatureApproveEditView(generics.RetrieveUpdateAPIView):
	permission_classes = [IsAuthenticated]
	authentication_classes = [TokenAuthentication]
	queryset = HrmsScheduleInterview.objects.filter(is_deleted=False)
	serializer_class = CandidatureApproveEditSerializer

class OpenAndClosedRequirementListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = HrmsNewRequirement.objects.filter(is_deleted=False).order_by('-id')
    serializer_class =OpenAndClosedRequirementListSerializer
    pagination_class = CSPageNumberPagination
    def get_queryset(self):
        filter={}
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        department=self.request.query_params.get('department', None)
        designation=self.request.query_params.get('designation', None)
        if self.queryset.count():
            if start_date and end_date:
                start_object =datetime.datetime.strptime(start_date, '%Y-%m-%d')
                end_object = datetime.datetime.strptime(end_date, '%Y-%m-%d')
                filter['date__date__gte']= start_object
                filter['date__date__lte']= end_object + timedelta(days=1)
            if department:
                department=department.split(',')
                filter['issuing_department__in']=department
                
            if designation:
                designation=designation.split(',')
                filter['proposed_designation__in']=designation

        if filter:
            print('asda',self.queryset.filter(**filter,is_deleted=False))
            return self.queryset.filter(**filter,is_deleted=False)
        else:
            return self.queryset
              
    @response_modify_decorator_list_or_get_after_execution_for_pagination
    def get(self,request, *args, **kwargs):
        type=self.request.query_params.get('type', None)
        response=super(OpenAndClosedRequirementListView,self).get(self, request, args, kwargs)
        # print('response--->',response.data)
        if response.data['results']:
            data_list=[]
            for data in response.data['results']:
                # print('data',data)
                if type.lower() == "open" :
                    if data['tab_status'] <= 6:
                        data_list.append(data)
                                      
                elif type.lower() == "close" :
                    if data['tab_status'] == 6:
                        data_list.append(data)

            response.data['results']=data_list
            return response           
                        
        else:
            return response
                    

class UpcomingAndInterviewHistoryListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = HrmsScheduleInterview.objects.filter(is_deleted=False).order_by('-id')
    serializer_class = UpcomingAndInterviewHistoryListSerializer
    pagination_class = CSPageNumberPagination

    def get_queryset(self):
        filter={}
        planned_start_date= self.request.query_params.get('planned_start_date', None)
        planned_end_date= self.request.query_params.get('planned_end_date', None)
        actual_start_date= self.request.query_params.get('actual_start_date', None)
        actual_end_date= self.request.query_params.get('actual_end_date', None)
        interview_type = self.request.query_params.get('interview_type', None)
        department=self.request.query_params.get('department', None)
        designation=self.request.query_params.get('designation', None)
        search=self.request.query_params.get('search', None)
        field_name = self.request.query_params.get('field_name', None)
        order_by = self.request.query_params.get('order_by', None)

        if field_name and order_by:
            if field_name == 'planned_date_of_interview' and order_by == 'asc':
                another_round=HrmsScheduleAnotherRoundInterview.objects.filter(is_deleted=False
                                    ).order_by('planned_date_of_interview')       
                # print('another_round',another_round)
                another_round_list=[]
                for a_r in another_round:
                    schedule_id=a_r.schedule_interview.id
                    another_round_list.append(schedule_id)
                # print('another_round_list',another_round_list)
                clauses = ' '.join(
                    ['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(another_round_list)])
                ordering = 'CASE %s END' % clauses
                queryset = self.queryset.filter(pk__in=another_round_list).extra(
                    select={'ordering': ordering}, order_by=('ordering',))
                # print('queryset', queryset)
                return queryset
                

            if field_name == 'planned_date_of_interview' and order_by == 'desc':
                another_round=HrmsScheduleAnotherRoundInterview.objects.filter(is_deleted=False
                                    ).order_by('-planned_date_of_interview')       
                # print('another_round',another_round)
                another_round_list=[]
                for a_r in another_round:
                    schedule_id=a_r.schedule_interview.id
                    another_round_list.append(schedule_id)
                # print('another_round_list',another_round_list)
                clauses = ' '.join(
                    ['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(another_round_list)])
                ordering = 'CASE %s END' % clauses
                queryset = self.queryset.filter(pk__in=another_round_list).extra(
                    select={'ordering': ordering}, order_by=('ordering',))
                # print('queryset', queryset)
                return queryset
            if field_name == 'actual_date_of_interview' and order_by == 'asc':
                another_round=HrmsScheduleAnotherRoundInterview.objects.filter(is_deleted=False
                                    ).order_by('actual_date_of_interview')       
                # print('another_round',another_round)
                another_round_list=[]
                for a_r in another_round:
                    schedule_id=a_r.schedule_interview.id
                    another_round_list.append(schedule_id)
                # print('another_round_list',another_round_list)
                clauses = ' '.join(
                    ['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(another_round_list)])
                ordering = 'CASE %s END' % clauses
                queryset = self.queryset.filter(pk__in=another_round_list).extra(
                    select={'ordering': ordering}, order_by=('ordering',))
                # print('queryset', queryset)
                return queryset
                

            if field_name == 'actual_date_of_interview' and order_by == 'desc':
                another_round=HrmsScheduleAnotherRoundInterview.objects.filter(is_deleted=False
                                    ).order_by('-actual_date_of_interview')       
                # print('another_round',another_round)
                another_round_list=[]
                for a_r in another_round:
                    schedule_id=a_r.schedule_interview.id
                    another_round_list.append(schedule_id)
                # print('another_round_list',another_round_list)
                clauses = ' '.join(
                    ['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(another_round_list)])
                ordering = 'CASE %s END' % clauses
                queryset = self.queryset.filter(pk__in=another_round_list).extra(
                    select={'ordering': ordering}, order_by=('ordering',))
                # print('queryset', queryset)
                return queryset
            if field_name == 'date_of_requirement' and order_by == 'asc':
                return self.queryset.all().order_by('requirement__date')

            if field_name == 'date_of_requirement' and order_by == 'desc':
                return self.queryset.all().order_by('-requirement__date')


        if interview_type:
            if interview_type.lower() == "upcoming":
                # queryset=self.queryset.filter(requirement__tab_status__lte=5,action_approval=3,is_deleted=False)
                filter['requirement__tab_status__lte']=5
                filter['action_approval']=3
            elif interview_type.lower() == "history":
                # queryset=self.queryset.filter(action_approval__lte=3,is_deleted=False)
                filter['action_approval__lte']=3
            # return queryset

        if planned_start_date and planned_end_date:
            planned_start_object =datetime.datetime.strptime(planned_start_date, '%Y-%m-%d')
            planned_end_object = datetime.datetime.strptime(planned_end_date, '%Y-%m-%d')
            another_round = HrmsScheduleAnotherRoundInterview.objects.filter(planned_date_of_interview__date__gte=planned_start_object,
                                                                            planned_date_of_interview__date__lte=(planned_end_object+ timedelta(days=1))
                                                                            ).values_list('schedule_interview')
            print('another_round',another_round)
            filter['id__in']= another_round
       

        if actual_start_date and actual_end_date:
            actual_start_object =datetime.datetime.strptime(actual_start_date, '%Y-%m-%d')
            actual_end_object = datetime.datetime.strptime(actual_end_date, '%Y-%m-%d')
            actual_date_id=HrmsScheduleAnotherRoundInterview.objects.filter(actual_date_of_interview__date__gte=actual_start_object,
                                                                            actual_date_of_interview__date__lte=(actual_end_object+ timedelta(days=1))
                                                                            ).values_list('schedule_interview')
            filter['id__in']= actual_date_id

        if department:
            department=department.split(',')
            filter['requirement__issuing_department__in']=department

        if designation:
            designation=designation.split(',')
            filter['requirement__proposed_designation__in']=designation

        if search:
            search=search.split(",")
            for i in search:
                queryset_all = HrmsScheduleInterview.objects.none()  
                queryset=self.queryset.filter(Q(candidate_name__icontains=i) |
                                            Q(contact_no__icontains=i)|Q(email__icontains=i)).order_by('-id')
                queryset_all = (queryset_all|queryset)
            return queryset_all

        if filter:
            return self.queryset.filter(**filter)
        


    @response_modify_decorator_list_or_get_after_execution_for_pagination
    def get(self, request, *args, **kwargs):
        response=super(UpcomingAndInterviewHistoryListView,self).get(self, request, args, kwargs)
        interview_type = self.request.query_params.get('interview_type', None)
        for data in response.data['results']:
            # print('data',data)
            schedule_another_det=HrmsScheduleAnotherRoundInterview.objects.filter(schedule_interview=data['id'],
                                                                                is_deleted=False
                                                                                )
            # print('schedule_another_det',schedule_another_det)
            for s_a_d in schedule_another_det:
                data['type_of_interview']=s_a_d.type_of_interview.id
                data['interview_type_name']=s_a_d.type_of_interview.name
                data['level_of_interview']=s_a_d.level_of_interview.id
                data['interview_level_name']=s_a_d.level_of_interview.name
                interviewers=HrmsScheduleInterviewWith.objects.filter(interview=s_a_d,is_deleted=False)
                interviewers_list=[]
                if interviewers:
                    for i_t in interviewers:
                        int_dict={
                            'id':i_t.id,
                            'interview':i_t.interview.id,
                            'user':i_t.user.id,
                            'first_name':i_t.user.first_name,
                            'last_name':i_t.user.last_name,
                        }
                        interviewers_list.append(int_dict)

                upload_feedback=HrmsScheduleInterviewFeedback.objects.filter(interview=s_a_d,is_deleted=False)
                feedback_list=[]
                feedback_dict={}
                if upload_feedback:
                    for u_f in upload_feedback:
                        upload_feedback=request.build_absolute_uri(u_f.upload_feedback.url) if u_f.upload_feedback else None
                        feedback_dict={
                            'id':u_f.id,
                            'interview':u_f.interview.id,
                            'upload_feedback':upload_feedback
                        }
                        feedback_list.append(feedback_dict)

                if interview_type and interview_type.lower() == "upcoming":
                    data['interview_round_id']=s_a_d.id
                    data['planned_date_of_interview']=s_a_d.planned_date_of_interview
                    data['planned_time_of_interview']=s_a_d.planned_time_of_interview                   
                    data['interviewers']=interviewers_list
                  
                elif interview_type and interview_type.lower() == "history":
                    data['actual_date_of_interview']=s_a_d.actual_date_of_interview
                    data['actual_time_of_interview']=s_a_d.actual_time_of_interview
                    data['interviewers']=interviewers_list
                    data['feedback']=feedback_list
                    data['interview_status']=s_a_d.interview_status
                    data['interview_status_name']=s_a_d.get_interview_status_display()

        return response

class EmployeeActiveInactiveUserView(generics.RetrieveUpdateAPIView):
    """
    send parameter 'is_active'
    View for user update active and in_active
    using user ID
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = EmployeeActiveInactiveUserSerializer
    queryset = User.objects.all()