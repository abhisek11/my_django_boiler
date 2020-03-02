from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from hrms.models import *
from django.contrib.auth.models import *
from django.db import transaction, IntegrityError
from drf_extra_fields.fields import Base64ImageField
from master.models import *
import os
from custom_exception_message import *
from datetime import datetime,timedelta
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from users.models import TCoreUserDetail
from smssend.views import *
from threading import Thread
from custom_decorator import *
from rest_framework.authtoken.models import Token
from attendance.models import *
from decimal import Decimal
from core.models import *
from pms.models import *
import re
import random
from mailsend.views import *

from django.contrib.admin.models import LogEntry
#:::::::::::::::::::::: HRMS BENEFITS PROVIDED:::::::::::::::::::::::::::#
class BenefitsProvidedAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = HrmsBenefitsProvided
        fields = ('id', 'benefits_name','created_by', 'owned_by')


class BenefitsProvidedEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = HrmsBenefitsProvided
        fields = ('id', 'benefits_name','updated_by')

class BenefitsProvidedDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = HrmsBenefitsProvided
        fields = '__all__'
    def update(self, instance, validated_data):
        instance.is_deleted=True
        instance.updated_by = validated_data.get('updated_by')
        instance.save()
        return instance

#:::::::::::::::::::::: HRMS QUALIFICATION MASTER:::::::::::::::::::::::::::#
class QualificationMasterAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = HrmsQualificationMaster
        fields = ('id', 'name', 'created_by', 'owned_by')


class QualificationMasterEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = HrmsQualificationMaster
        fields = ('id', 'name', 'updated_by')

class QualificationMasterDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = HrmsQualificationMaster
        fields = '__all__'
    def update(self, instance, validated_data):
        instance.is_deleted=True
        instance.updated_by = validated_data.get('updated_by')
        instance.save()
        return instance

#::::::::::::::::::::::::::::: HRMS EMPLOYEE:::::::::::::::::::::::::::::::::::::::#
class EmployeeAddSerializer(serializers.ModelSerializer):
    '''
        Last modified By Rupam Hazra on [13.02.2020] as per details

        1. "Employee Login ID" remove. It will be auto created
        2. SAP Personnel ID (Optional)
        3. Add official email id (Optional)
        4. Job Location State
        5. Department
        6. Designation
        -----------------------------------------------

        Date of Termination ->Release Date
        Resignation Date:
    '''
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    cu_phone_no = serializers.CharField(required=False)
    cu_punch_id= serializers.CharField(required=False)
    hod=serializers.CharField(required=False)
    grade=serializers.CharField(required=False,allow_null=True)
    cu_emp_code = serializers.CharField(required=False)
    sap_personnel_no=serializers.CharField(required=False,allow_null=True)
    mmr_module_id=serializers.CharField(required=False)
    mmr_type=serializers.CharField(required=False)
    reporting_head=serializers.CharField(required=False)
    cu_profile_img=serializers.FileField(required=False)
    reporting_head_name=serializers.CharField(required=False)
    company=serializers.CharField(required=False)
    cost_centre=serializers.CharField(required=False)
    hod_name=serializers.CharField(required=False)
    grade_name=serializers.CharField(required=False)
    joining_date=serializers.CharField(required=False)
    daily_loginTime=serializers.CharField(default="10:00:00")
    daily_logoutTime=serializers.CharField(default="19:00:00")
    lunch_start=serializers.CharField(default="13:30:00")
    lunch_end=serializers.CharField(default="14:00:00")
    salary_type= serializers.CharField(required=False,allow_null=True)
    cu_alt_email_id = serializers.CharField(required=False,allow_null=True)
    job_location_state = serializers.CharField(required=False)
    department = serializers.CharField(required=False)
    designation = serializers.CharField(required=False)
    class Meta:
        model = User
        fields = ('id','first_name','last_name','cu_phone_no','cu_emp_code','sap_personnel_no',
                'created_by','cu_profile_img','hod','grade','mmr_module_id','mmr_type','reporting_head',
                'reporting_head_name','hod_name','grade_name','joining_date','daily_loginTime','daily_logoutTime',
                'lunch_start','lunch_end','company','cost_centre','cu_punch_id','salary_type',
                'cu_alt_email_id','job_location_state','department','designation')

    def create(self,validated_data):
        try:

            cu_phone_no = validated_data.pop('cu_phone_no')if 'cu_phone_no' in validated_data else ''

            cu_punch_id = validated_data.pop('cu_punch_id')if 'cu_punch_id' in validated_data else ''
            cu_emp_code = validated_data.pop('cu_emp_code') if 'cu_emp_code' in validated_data else ''

            hod = validated_data.pop('hod') if 'hod' in validated_data else ''

            company=validated_data.pop('company') if 'company' in validated_data else ''
            cost_centre=validated_data.pop('cost_centre') if 'cost_centre' in validated_data else ''

            #print('cost_centre',cost_centre)
            #print('grade',type(validated_data.get('grade')),validated_data.get('grade'))
            grade = '' if validated_data.get('grade') == 'null' else validated_data.pop('grade')
            #print('grade',type(grade),grade)
            cu_profile_img=validated_data.pop('cu_profile_img') if 'cu_profile_img' in validated_data else ''
            print('valid111ated_data111',validated_data)

            sap_personnel_no = validated_data.pop('sap_personnel_no')
            sap_personnel_no = None if sap_personnel_no == 'null' else sap_personnel_no

            print('sap_personnel_no',sap_personnel_no,type(sap_personnel_no))
            mmr_module_id= validated_data.pop('mmr_module_id') if 'mmr_module_id' in validated_data else ''
            mmr_type =  validated_data.pop('mmr_type') if 'mmr_type' in validated_data else ''
            reporting_head = validated_data.pop('reporting_head') if 'reporting_head' in validated_data else ''
            joining_date = validated_data.pop('joining_date') if 'joining_date' in validated_data else None
            joining_date = datetime.datetime.strptime(joining_date, "%Y-%m-%dT%H:%M:%S.%fZ")

            salary_type = validated_data.pop('salary_type')
            salary_type = '' if salary_type == 'null' else salary_type


            cu_alt_email_id = validated_data.pop('cu_alt_email_id')
            cu_alt_email_id = None if cu_alt_email_id == 'null' else cu_alt_email_id

            job_location_state=validated_data.pop('job_location_state') if 'job_location_state' in validated_data else ''
            department = validated_data.pop('department')
            designation = validated_data.pop('designation')

            logdin_user_id = self.context['request'].user.id
            role_details_list=[]
            with transaction.atomic():

                username_generate = validated_data.get('first_name') + validated_data.get('last_name')
                check_user_exist = User.objects.filter(username = username_generate)
                if check_user_exist:
                    username_generate = username_generate+str(random.randint(1,6))
                print('username_generate',username_generate)
                print('last_name',type(validated_data.get('last_name')),validated_data.get('last_name'))
                if validated_data.get('last_name') != 'null':
                    last_name_c = validated_data.get('last_name')
                else:
                    last_name_c = ''
                print('last_name_c',last_name_c)
                user=User.objects.create(first_name=validated_data.get('first_name'),
                                        last_name=last_name_c,
                                        username=username_generate,
                                        )
                print('user',user)
                '''
                    Modified by Rupam Hazra to set default password
                '''
                password = 'Shyam@123'
                user.set_password(password)
                user.save()

                user_detail = TCoreUserDetail.objects.create(
                                                            cu_user=user,
                                                           cu_phone_no=cu_phone_no,
                                                           cu_profile_img=cu_profile_img,
                                                           password_to_know=password,
                                                           cu_emp_code=cu_emp_code,
                                                           sap_personnel_no=sap_personnel_no,
                                                           daily_loginTime=validated_data.get('daily_loginTime'),
                                                           daily_logoutTime=validated_data.get('daily_logoutTime'),
                                                           lunch_start=validated_data.get('lunch_start'),
                                                           lunch_end=validated_data.get('lunch_end'),
                                                           hod_id=hod,
                                                           reporting_head_id=reporting_head,
                                                           joining_date= joining_date,
                                                           cu_created_by_id=logdin_user_id,
                                                           employee_grade_id=grade,
                                                           company_id=company,
                                                           cost_centre=cost_centre,
                                                           cu_punch_id=cu_punch_id,
                                                           salary_type_id=salary_type,
                                                           job_location_state_id=job_location_state,
                                                           cu_alt_email_id = cu_alt_email_id,
                                                           department_id = department,
                                                           designation_id = designation,
                                                           granted_cl = float(10),
                                                           granted_el = float(15),
                                                           granted_sl = float(7)
                                                           )
                #print('user_detail',user_detail)
                role_user=TMasterModuleRoleUser.objects.create(mmr_module_id=mmr_module_id,
                                                               mmr_type = mmr_type,
                                                               mmr_user = user,
                                                               mmr_created_by = validated_data['created_by']
                                                              )

                joining_date=joining_date.date()
                #print('joining_date',joining_date)
                joining_year=joining_date.year
                #print('joining_year',joining_year)
                leave_filter={}


                total_month_grace=AttendenceMonthMaster.objects.filter(month_start__date__lte=joining_date,
                                month_end__date__gte=joining_date,is_deleted=False).values('grace_available',
                                                                            'year_start_date',
                                                                            'year_end_date',
                                                                            'month',
                                                                            'month_start',
                                                                            'month_end')
                granted_cl = 10
                granted_el = 15
                granted_sl = 7
                print('total_month_grace',total_month_grace)
                if total_month_grace:
                    year_end_date=total_month_grace[0]['year_end_date'].date()
                    total_days=(year_end_date - joining_date).days
                    print('total_days',total_days)
                    calculated_cl=round((total_days/365)* int(granted_cl))
                    leave_filter['cl']=calculated_cl
                    calculated_el=round((total_days/365)* int(granted_el))
                    leave_filter['el']=calculated_el
                    if granted_sl:
                        calculated_sl=round((total_days/365)* int(granted_sl))
                        print('calculated_sl',calculated_sl)
                        leave_filter['sl']=calculated_sl
                    else:
                        leave_filter['sl']=None

                    month_start_date=total_month_grace[0]['month_start'].date()
                    month_end_date=total_month_grace[0]['month_end'].date()
                    # print('month_start_date',month_start_date,month_end_date)
                    month_days=(month_end_date-month_start_date).days
                    # print('month_days',month_days)
                    remaining_days=(month_end_date-joining_date).days
                    # print('remaining_days',remaining_days)
                    # available_grace=round(total_month_grace[0]['grace_available']/remaining_days)
                    available_grace = round((remaining_days/month_days)*int(total_month_grace[0]['grace_available']))
                    print('available_grace',available_grace)
                    print(total_month_grace[0]['year_start_date'])
                    print(joining_date)
                    if total_month_grace[0]['year_start_date'].date() < joining_date:

                        JoiningApprovedLeave.objects.get_or_create(employee=user,
                                                            year=joining_year,
                                                            month=total_month_grace[0]['month'],
                                                            **leave_filter,
                                                            first_grace=available_grace,
                                                            created_by=user,
                                                            owned_by=user
                                                            )
                        print('sdddsdsdsd11213231')


                if cu_alt_email_id:

                    #============= Mail Send ==============#

                    # Send mail to employee with login details
                    mail_data = {
                                "name": user.first_name+ '' + user.last_name,
                                "user": username_generate,
                                "pass": password
                        }
                    #print('mail_data',mail_data)
                    mail_class = GlobleMailSend('EMP001', [cu_alt_email_id])
                    mail_thread = Thread(target = mail_class.mailsend, args = (mail_data,))
                    mail_thread.start()

                    # Send mail to who added the employee
                    add_cu_alt_email_id = TCoreUserDetail.objects.filter(cu_user=self.context['request'].user)[0]

                    if add_cu_alt_email_id.cu_alt_email_id:
                        mail_data = {
                                    "name": self.context['request'].user.first_name+ ' ' + self.context['request'].user.last_name,
                                    "user": username_generate,
                                    "pass": password
                            }
                        #print('mail_data',mail_data)
                        mail_class = GlobleMailSend('EMPA001', [add_cu_alt_email_id.cu_alt_email_id])
                        mail_thread = Thread(target = mail_class.mailsend, args = (mail_data,))
                        mail_thread.start()

                data = {
                    'id': user.id,
                    'first_name':user.first_name,
                    'last_name':user.last_name,
                    'username':user.username,
                    'cu_emp_code': user_detail.cu_emp_code,

                  }
                print('data',data)
                return data

        except Exception as e:
            raise APIException({
                'request_status': 0,
                'msg': e
            })


class EmployeeEditSerializer(serializers.ModelSerializer):
    ##### Extra Fields for TCoreUserDetails #####################
    cu_phone_no =serializers.CharField(required=False,allow_null=True)
    cu_alt_phone_no =serializers.CharField(required=False,allow_null=True)
    cu_alt_email_id=serializers.CharField(required=False,allow_null=True)
    cu_emp_code =serializers.CharField(required=False,allow_null=True)
    cu_punch_id = serializers.CharField(required=False,allow_null=True)
    cu_profile_img=serializers.ImageField(required=False,allow_null=True)
    sap_personnel_no=serializers.CharField(required=False,allow_null=True)
    initial_ctc=serializers.CharField(required=False,allow_null=True)
    current_ctc=serializers.CharField(required=False,allow_null=True)
    cost_centre=serializers.CharField(required=False,allow_null=True)
    address =serializers.CharField(required=False,allow_null=True)
    blood_group=serializers.CharField(required=False,allow_null=True)
    total_experience=serializers.CharField(required=False,allow_null=True)
    job_description =serializers.CharField(required=False,allow_null=True)
    company=serializers.CharField(required=False,allow_null=True)
    granted_cl=serializers.CharField(required=False,allow_null=True)
    granted_sl=serializers.CharField(required=False,allow_null=True)
    granted_el=serializers.CharField(required=False,allow_null=True)
    hod = serializers.CharField(required=False,allow_null=True)
    reporting_head = serializers.CharField(required=False)
    designation = serializers.CharField(required=False,allow_null=True)
    department = serializers.CharField(required=False,allow_null=True)
    daily_loginTime=serializers.CharField(required=False,allow_null=True)
    daily_logoutTime=serializers.CharField(required=False,allow_null=True)
    lunch_start=serializers.CharField(required=False,allow_null=True)
    lunch_end=serializers.CharField(required=False,allow_null=True)
    saturday_off=serializers.DictField(required=False)
    salary_type= serializers.CharField(required=False,allow_null=True)
    is_confirm =  serializers.BooleanField(required=False)
    termination_date =serializers.CharField(required=False)
    ##### Extra Fields for another tables #####################
    employee_grade = serializers.CharField(required=False,allow_null=True)
    mmr_module_id =serializers.CharField(required=False,allow_null=True)
    mmr_type=serializers.CharField(required=False,allow_null=True)
    benefit_provided = serializers.ListField(required=False,allow_null=True)
    other_facilities = serializers.ListField(required=False,allow_null=True)

    '''
        Added by Rupam Hazra [13.02.2020] as per details confirmation
    '''
    job_location = serializers.CharField(required = False, allow_null=True)
    job_location_state = serializers.CharField(required=False,allow_null=True)
    source = serializers.CharField(required = False, allow_null=True)
    source_name = serializers.CharField(required = False, allow_null=True)
    bank_account = serializers.CharField(required = False, allow_null=True)
    ifsc_code = serializers.CharField(required = False, allow_null=True)
    branch_name = serializers.CharField(required = False, allow_null=True)
    pincode = serializers.CharField(required = False, allow_null=True)
    emergency_contact_no = serializers.CharField(required = False,allow_null=True)
    father_name = serializers.CharField(required = False,allow_null=True)
    pan_no = serializers.CharField(required = False,allow_null=True)
    aadhar_no = serializers.CharField(required = False,allow_null=True)
    uan_no = serializers.CharField(required = False,allow_null=True)
    pf_no = serializers.CharField(required = False,allow_null=True)
    esic_no = serializers.CharField(required = False,allow_null=True)
    marital_status = serializers.CharField(required = False,allow_null=True)
    salary_per_month=serializers.CharField(required = False,allow_null=True)
    cu_dob = serializers.CharField(required=False,allow_null=True)
    resignation_date = serializers.CharField(required=False,allow_null=True)
    cu_gender = serializers.CharField(required=False,allow_null=True)

    class Meta:
        model = User
        fields=('id','first_name','last_name','email',
        'employee_grade','department','cu_profile_img','termination_date',
        'reporting_head','designation','benefit_provided','other_facilities','is_confirm',
        'hod','blood_group','company','granted_cl','granted_sl','granted_el','salary_type',
        'job_description','total_experience','address','cost_centre','saturday_off','cu_punch_id',
        'current_ctc','initial_ctc','sap_personnel_no','cu_emp_code','cu_alt_email_id','cu_alt_phone_no',
        'cu_phone_no','mmr_module_id',"mmr_type",'daily_loginTime','daily_logoutTime','lunch_start','lunch_end',
        'cu_dob','job_location','job_location_state','source','source_name','bank_account','ifsc_code','branch_name',
        'pincode','emergency_contact_no','father_name','pan_no','aadhar_no','uan_no','pf_no','esic_no',
        'marital_status','salary_per_month','resignation_date','cu_gender')




    def update(self,instance,validated_data):
        try:
            print('validated_data',validated_data)
            list_type = self.context['request'].query_params.get('list_type', None)
            logdin_user_id = self.context['request'].user.id
            blood_group=validated_data.get('blood_group') if validated_data.get('blood_group') else ""
            total_experience=validated_data.get('total_experience') if validated_data.get('total_experience') else ""
            address=validated_data.get('address') if validated_data.get('address') else ""
            cu_profile_img=validated_data.get('cu_profile_img') if validated_data.get('cu_profile_img') else ""
            cu_alt_phone_no=validated_data.get('cu_alt_phone_no') if validated_data.get('cu_alt_phone_no') else ""
            cu_alt_email_id= validated_data.get('cu_alt_email_id') if  validated_data.get('cu_alt_email_id') else ""
            cu_emp_code=validated_data.get('cu_emp_code') if validated_data.get('cu_emp_code') else ""
            cu_punch_id = validated_data.get('cu_punch_id') if validated_data.get('cu_punch_id') else ""
            job_description=validated_data.get('job_description') if validated_data.get('job_description') else ""
            cu_phone_no=validated_data.get('cu_phone_no') if validated_data.get('cu_phone_no') else ""
            company=validated_data.get('company') if validated_data.get('company') else ""
            hod=validated_data.get('hod') if validated_data.get('hod') else ""
            reporting_head=validated_data.get('reporting_head') if validated_data.get('reporting_head') else ""
            department=validated_data.get('department') if validated_data.get('department') else ""
            designation=validated_data.get('designation') if validated_data.get('designation') else ""
            current_ctc=validated_data.get('current_ctc') if validated_data.get('current_ctc') else ""
            initial_ctc=validated_data.get('initial_ctc') if validated_data.get('initial_ctc') else ""
            sap_personnel_no= None if validated_data.get('sap_personnel_no') == 'null' else validated_data.get('sap_personnel_no')
            cost_centre=validated_data.get('cost_centre') if validated_data.get('cost_centre') else ""
            granted_cl=validated_data.get('granted_cl') if validated_data.get('granted_cl') else 0.0
            granted_el=validated_data.get('granted_el') if validated_data.get('granted_el') else 0.0
            granted_sl=validated_data.get('granted_sl') if validated_data.get('granted_sl') else 0.0
            daily_loginTime=validated_data.get('daily_loginTime') if validated_data.get('daily_loginTime') else None
            daily_logoutTime=validated_data.get('daily_logoutTime') if validated_data.get('daily_logoutTime') else None
            lunch_start=validated_data.get('lunch_start') if validated_data.get('lunch_start') else None
            lunch_end=validated_data.get('lunch_end') if validated_data.get('lunch_end') else None
            saturday_off=validated_data.get('saturday_off') if validated_data.get('saturday_off') else None
            salary_type = validated_data.get('salary_type') if validated_data.get('salary_type') else None
            is_confirm = validated_data.get('is_confirm')
            termination_date=validated_data.get('termination_date') if validated_data.get('termination_date') else None


            '''
                Added by Rupam Hazra [13.02.2020] as perdetails
            '''
            # job_location=validated_data.get('job_location') if validated_data.get('job_location') else None
            job_location_state = validated_data.get('job_location_state') if validated_data.get('job_location_state') else None
            # source=validated_data.get('source') if validated_data.get('source') else None
            # source_name=validated_data.get('source_name') if validated_data.get('source_name') else None
            # bank_account=validated_data.get('bank_account') if validated_data.get('bank_account') else None
            # ifsc_code=validated_data.get('ifsc_code') if validated_data.get('ifsc_code') else None
            # branch_name=validated_data.get('branch_name') if validated_data.get('branch_name') else None
            # pincode=validated_data.get('pincode') if validated_data.get('pincode') else None
            # emergency_contact_no=validated_data.get('emergency_contact_no') if validated_data.get('emergency_contact_no') else None
            # father_name=validated_data.get('father_name') if validated_data.get('father_name') else None
            # pan_no=validated_data.get('pan_no') if validated_data.get('pan_no') else None
            # aadhar_no=validated_data.get('aadhar_no') if validated_data.get('aadhar_no') else None
            # uan_no=validated_data.get('uan_no') if validated_data.get('uan_no') else None
            # pf_no=validated_data.get('pf_no') if validated_data.get('pf_no') else None
            # esic_no=validated_data.get('esic_no') if validated_data.get('esic_no') else None
            # marital_status=validated_data.get('marital_status') if validated_data.get('marital_status') else None
            # salary_per_month=validated_data.get('salary_per_month') if validated_data.get('salary_per_month') else None

            resignation_date= validated_data.get('resignation_date') if validated_data.get('resignation_date') else None

            print('resignation_date',resignation_date,type(resignation_date))
            with transaction.atomic():
                if list_type == "personal": ### Checking for Personal
                    '''
                        Reason : Adding many fields on Employee Edit
                        Author : Rupam Hazra
                        Date : 19/02/2020
                        Line Number : 582
                    '''
                    cu_dob = None if validated_data.get('cu_dob')== 'null' else validated_data.get('cu_dob')
                    bank_account = None if validated_data.get('bank_account') == 'null' else validated_data.get('bank_account')
                    ifsc_code = None if validated_data.get('ifsc_code') == 'null' else validated_data.get('ifsc_code')
                    branch_name = None if validated_data.get('branch_name') == 'null' else validated_data.get('branch_name')
                    cu_gender = None if validated_data.get('cu_gender') == 'null' else validated_data.get('cu_gender')
                    state = None if validated_data.get('state') == 'null' else validated_data.get('state')
                    pincode = None if validated_data.get('pincode') == 'null' else validated_data.get('pincode')
                    emergency_contact_no = None if validated_data.get('emergency_contact_no') == 'null' else validated_data.get('emergency_contact_no')
                    father_name = None if validated_data.get('father_name') == 'null' else validated_data.get('father_name')
                    pan_no = None if validated_data.get('pan_no') == 'null' else validated_data.get('pan_no')
                    aadhar_no = None if validated_data.get('aadhar_no') == 'null' else validated_data.get('aadhar_no')
                    uan_no = None if validated_data.get('uan_no') == 'null' else validated_data.get('uan_no')
                    marital_status = None if validated_data.get('marital_status') == 'null' else validated_data.get('marital_status')

                    instance.first_name = validated_data['first_name']
                    instance.last_name = validated_data['last_name']
                    instance.email = validated_data['email']
                    instance.save()

                    user_details=TCoreUserDetail.objects.filter(cu_user=instance.id,cu_is_deleted=False)
                    for det in user_details:
                        det.blood_group = blood_group
                        det.total_experience = total_experience
                        det.cu_phone_no = cu_phone_no
                        det.cu_emp_code=cu_emp_code
                        det.address = address
                        det.cu_updated_by_id=logdin_user_id
                        det.job_location_state_id=job_location_state
                        det.cu_alt_email=cu_alt_email_id
                        existing_image='./media/' + str(det.cu_profile_img)
                        if cu_profile_img:
                            if os.path.isfile(existing_image):
                                os.remove(existing_image)
                            det.cu_profile_img = cu_profile_img
                            # print('det.cu_profile_img',det.cu_profile_img)
                        det.save()
                        instance.__dict__['cu_profile_img'] = det.cu_profile_img



                    instance.__dict__['cu_phone_no'] = cu_phone_no
                    instance.__dict__['cu_emp_code'] = cu_emp_code
                    instance.__dict__['address'] = address
                    instance.__dict__['blood_group'] = blood_group
                    instance.__dict__['total_experience'] = total_experience
                    instance.__dict__['cu_alt_email_id'] = cu_alt_email_id
                    instance.__dict__['job_location_state'] = job_location_state

                elif list_type == "role": ### Checking for Role

                    instance.first_name = validated_data['first_name']
                    instance.last_name = validated_data['last_name']
                    instance.save()

                    # print("termination_date",termination_date )
                    if termination_date:
                        # print("hsgdhhfgs", datetime.datetime.strptime(termination_date, "%Y-%m-%dT%H:%M:%S.%fZ"))
                        termination_date = datetime.datetime.strptime(termination_date, "%Y-%m-%dT%H:%M:%S.%fZ")
                    if resignation_date:
                        resignation_date = datetime.datetime.strptime(resignation_date, "%Y-%m-%dT%H:%M:%S.%fZ")

                    TCoreUserDetail.objects.filter(cu_user=instance.id,cu_is_deleted=False).update(
                        cu_alt_phone_no = cu_alt_phone_no,
                        cu_alt_email_id = cu_alt_email_id,
                        cu_emp_code =cu_emp_code,
                        company = company,
                        job_description = job_description,
                        hod=hod,
                        reporting_head_id=reporting_head,
                        department_id=department,
                        designation_id=designation,
                        cu_updated_by=logdin_user_id,
                        employee_grade = validated_data['employee_grade'],
                        termination_date= termination_date,
                        resignation_date=resignation_date
                    )

                    '''
                        [  Removed By Rupam Hazra 22.01.2020 line 351-364 ]
                    '''
                    # if TMasterModuleRoleUser.objects.filter(mmr_user=instance,mmr_is_deleted=False):
                    #     TMasterModuleRoleUser.objects.filter(mmr_user=instance,mmr_is_deleted=False).update(
                    #                                                             mmr_module_id=validated_data['mmr_module_id'],
                    #                                                             mmr_type=validated_data['mmr_type'],
                    #                                                             mmr_updated_by=logdin_user_id
                    #                                                             )
                    # else:
                    #     TMasterModuleRoleUser.objects.create(
                    #         mmr_user=instance,
                    #         mmr_module_id=validated_data['mmr_module_id'],
                    #         mmr_type=validated_data['mmr_type'],
                    #         mmr_designation_id=designation,
                    #         mmr_created_by_id=logdin_user_id
                    #         )

                    core_details=TCoreUserDetail.objects.filter(cu_user=instance.id,cu_is_deleted=False).values(
                        'reporting_head','cu_alt_phone_no', 'cu_emp_code', 'cu_alt_email_id','designation','department','job_description',
                        'hod','company','termination_date')
                    instance.__dict__['cu_alt_phone_no'] =core_details[0]['cu_alt_phone_no'] if core_details[0]['cu_alt_phone_no'] else ''
                    instance.__dict__['cu_alt_email_id'] = core_details[0]['cu_alt_email_id'] if core_details[0]['cu_alt_email_id'] else ''
                    instance.__dict__['cu_emp_code'] = core_details[0]['cu_emp_code'] if core_details[0]['cu_emp_code'] else ''
                    instance.__dict__['employee_grade'] = validated_data['employee_grade']
                    instance.__dict__['designation'] = core_details[0]['designation'] if core_details[0]['designation'] else ''
                    instance.__dict__['department'] = core_details[0]['department']  if core_details[0]['department'] else ''
                    instance.__dict__['job_description'] = core_details[0]['job_description'] if core_details[0]['job_description'] else ''
                    instance.__dict__['hod'] = core_details[0]['hod'] if core_details[0]['hod'] else ''
                    instance.__dict__['reporting_head'] = core_details[0]['reporting_head'] if core_details[0]['reporting_head'] else ''
                    instance.__dict__['company'] = core_details[0]['company'] if core_details[0]['company'] else ''
                    instance.__dict__['mmr_module_id'] = validated_data['mmr_module_id']
                    instance.__dict__['mmr_type'] = validated_data['mmr_type']
                    instance.__dict__['termination_date'] =core_details[0]['termination_date'] if core_details[0]['termination_date'] else None

                elif list_type == "professional": ### Checking for Professional
                    '''
                        Reason : Adding many fields on Employee Edit
                        Author : Rupam Hazra
                        Date : 19/02/2020
                        Line Number : 582
                    '''



                    instance.first_name = validated_data['first_name']
                    instance.last_name = validated_data['last_name']
                    instance.save()

                    TCoreUserDetail.objects.filter(cu_user=instance.id,cu_is_deleted=False).update(
                        current_ctc = current_ctc,
                        cu_emp_code = cu_emp_code,
                        cu_punch_id = cu_punch_id,
                        initial_ctc = initial_ctc,
                        sap_personnel_no = sap_personnel_no,
                        cost_centre =cost_centre,
                        granted_cl= granted_cl,
                        granted_el= granted_el,
                        granted_sl= granted_sl,
                        daily_loginTime=datetime.datetime.strptime(daily_loginTime,"%H:%M:%S"),
                        daily_logoutTime=datetime.datetime.strptime(daily_logoutTime,"%H:%M:%S"),
                        lunch_start=datetime.datetime.strptime(lunch_start,"%H:%M:%S"),
                        lunch_end=datetime.datetime.strptime(lunch_end,"%H:%M:%S"),
                        salary_type=salary_type,
                        is_confirm=is_confirm,
                        cu_updated_by=logdin_user_id
                    )
                    if saturday_off:
                        prev_sat_data=AttendenceSaturdayOffMaster.objects.filter(employee=instance,is_deleted=False)
                        # print('prev_sat_data',prev_sat_data)
                        if prev_sat_data:
                            for p_s in prev_sat_data:
                                p_s.first=saturday_off['first']
                                p_s.second=saturday_off['second']
                                p_s.third=saturday_off['third']
                                p_s.fourth=saturday_off['fourth']
                                p_s.all_s_day=saturday_off['all_s_day']
                                p_s.updated_by_id=logdin_user_id
                                p_s.save()
                            AttendenceSaturdayOffLogMaster.objects.create(employee=instance,
                                                                         **saturday_off,
                                                                         updated_by_id=logdin_user_id,
                                                                        )
                        else:
                            saturday_data=AttendenceSaturdayOffMaster.objects.create(employee=instance,
                                                                                    **saturday_off,
                                                                                    created_by_id=logdin_user_id,
                                                                                    owned_by_id=logdin_user_id
                                                                                    )

                            # print('saturday_data',saturday_data)
                            AttendenceSaturdayOffLogMaster.objects.create(employee=instance,
                                                                         **saturday_off,
                                                                         created_by_id=logdin_user_id,
                                                                         owned_by_id=logdin_user_id
                                                                        )

                    leave_filter={}
                    '''
                        Reason : Change functionality adn add this code employee add portion
                        Author : Rupam Hazra
                        Date : 19/02/2020
                        Line Number : 657 - 706
                    '''
                    # joining_date_details=TCoreUserDetail.objects.filter(cu_user=instance.id,cu_is_deleted=False).values('joining_date')
                    # if joining_date_details:
                    #     joining_date=joining_date_details[0]['joining_date'].date()
                    #     joining_year=joining_date.year
                    #     # print('joining_year',joining_year)


                    #     total_month_grace=AttendenceMonthMaster.objects.filter(month_start__date__lte=joining_date,
                    #                     month_end__date__gte=joining_date,is_deleted=False).values('grace_available',
                    #                                                              'year_start_date',
                    #                                                              'year_end_date',
                    #                                                              'month',
                    #                                                              'month_start',
                    #                                                              'month_end'
                    #                                                              )
                    #     if total_month_grace:
                    #         year_end_date=total_month_grace[0]['year_end_date'].date()
                    #         total_days=(year_end_date - joining_date).days
                    #         # print('total_days',total_days)
                    #         calculated_cl=round((total_days/365)* int(granted_cl))
                    #         leave_filter['cl']=calculated_cl
                    #         calculated_el=round((total_days/365)* int(granted_el))
                    #         leave_filter['el']=calculated_el
                    #         if granted_sl:
                    #             calculated_sl=round((total_days/365)* int(granted_sl))
                    #             # print('calculated_sl',calculated_sl)
                    #             leave_filter['sl']=calculated_sl
                    #         else:
                    #             leave_filter['sl']=None

                    #         month_start_date=total_month_grace[0]['month_start'].date()
                    #         month_end_date=total_month_grace[0]['month_end'].date()
                    #         # print('month_start_date',month_start_date,month_end_date)
                    #         month_days=(month_end_date-month_start_date).days
                    #         # print('month_days',month_days)
                    #         remaining_days=(month_end_date-joining_date).days
                    #         # print('remaining_days',remaining_days)
                    #         # available_grace=round(total_month_grace[0]['grace_available']/remaining_days)
                    #         available_grace = round((remaining_days/month_days)*int(total_month_grace[0]['grace_available']))
                    #         # print('available_grace',available_grace)

                    #         if total_month_grace[0]['year_start_date']<joining_date_details[0]['joining_date']:
                    #             JoiningApprovedLeave.objects.get_or_create(employee_id=instance.id,
                    #                                                 year=joining_year,
                    #                                                 month=total_month_grace[0]['month'],
                    #                                                 **leave_filter,
                    #                                                 first_grace=available_grace,
                    #                                                 created_by_id=logdin_user_id,
                    #                                                 owned_by_id=logdin_user_id
                    #                                                 )


                    instance.__dict__['cu_emp_code'] =cu_emp_code
                    instance.__dict__['cu_punch_id'] =cu_punch_id
                    instance.__dict__['current_ctc'] = current_ctc
                    instance.__dict__['initial_ctc'] = initial_ctc
                    instance.__dict__['sap_personnel_no'] = sap_personnel_no
                    instance.__dict__['cost_centre'] = cost_centre
                    instance.__dict__['granted_cl'] = granted_cl
                    instance.__dict__['granted_el'] = granted_el
                    instance.__dict__['granted_sl'] = granted_sl
                    instance.__dict__['daily_loginTime'] = daily_loginTime
                    instance.__dict__['daily_logoutTime'] = daily_logoutTime
                    instance.__dict__['lunch_start'] = lunch_start
                    instance.__dict__['lunch_end'] = lunch_end
                    instance.__dict__['saturday_off'] = saturday_off
                    instance.__dict__['salary_type'] = salary_type
                    instance.__dict__['is_confirm'] = is_confirm

                    benefit_provided_details = validated_data.pop('benefit_provided') if 'benefit_provided' in validated_data else None
                    if benefit_provided_details:
                        benefits = HrmsUsersBenefits.objects.filter(user=instance,is_deleted=False)
                        if benefits:
                            benefits.delete()

                        benefits_list = []
                        for get_benefit in benefit_provided_details:
                            create_benefit = HrmsUsersBenefits.objects.create(
                                user_id = str(instance.id),
                                benefits_id = get_benefit['benefits'],
                                allowance=get_benefit['allowance'],
                                created_by_id = logdin_user_id
                            )
                            create_benefit.__dict__.pop('_state') if '_state' in create_benefit.__dict__.keys() else create_benefit.__dict__
                            benefits_list.append(create_benefit.__dict__)
                        instance.__dict__['benefit_provided'] = benefits_list
                    elif benefit_provided_details is None:
                        benefits = HrmsUsersBenefits.objects.filter(user=instance,is_deleted=False)
                        if benefits:
                            benefits.delete()
                    else:
                        instance.__dict__['benefit_provided'] = None

                    other_facilities_details = validated_data.pop('other_facilities') if 'other_facilities' in validated_data else None
                    if other_facilities_details:
                        facilities = HrmsUsersOtherFacilities.objects.filter(user=instance,is_deleted=False)
                        if facilities:
                            facilities.delete()
                        facility_list = []
                        for get_facility in other_facilities_details:
                            create_facilities = HrmsUsersOtherFacilities.objects.create(
                                user_id = str(instance.id),
                                other_facilities= get_facility['facilities'],
                                created_by_id = logdin_user_id
                            )
                            create_facilities.__dict__.pop('_state') if '_state' in create_facilities.__dict__.keys() else create_facilities.__dict__
                            facility_list.append(create_facilities.__dict__)
                        instance.__dict__['other_facilities'] = facility_list
                    elif other_facilities_details is None:
                        facilities = HrmsUsersOtherFacilities.objects.filter(user=instance,is_deleted=False)
                        if facilities:
                            facilities.delete()
                    else:
                        instance.__dict__['other_facilities'] = None

                return instance.__dict__
        except Exception as e:
            raise e


class EmployeeListSerializer(serializers.ModelSerializer):
    cu_user = serializers.CharField()
    class Meta:
        model = User
        fields=('id','first_name','last_name','cu_user')

class EmployeeListWithoutDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields=('id','first_name','last_name','email','is_superuser')

class DocumentAddSerializer(serializers.ModelSerializer):
    created_by=serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by=serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = HrmsDocument
        fields=('id','user','tab_name','field_label','document_name','document','created_by','owned_by')

class DocumentDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = HrmsDocument
        fields = '__all__'
    def update(self, instance, validated_data):
        instance.updated_by = validated_data.get('updated_by')
        instance.is_deleted = True
        instance.save()
        return instance
class HrmsEmployeeProfileDocumentAddSerializer(serializers.ModelSerializer):
    created_by=serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by=serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = HrmsDynamicSectionFieldLabelDetailsWithDoc
        fields=('id','user','tab_name','field_label','field_label_value','document_name','document','created_by','owned_by')



class HrmsEmployeeProfileDocumentDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = HrmsDynamicSectionFieldLabelDetailsWithDoc
        fields = '__all__'
    def update(self, instance, validated_data):
        instance.updated_by = validated_data.get('updated_by')
        instance.is_deleted = True
        instance.save()
        return instance

class HrmsEmployeeAcademicQualificationAddSerializer(serializers.ModelSerializer):
    created_by=serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by=serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = HrmsUserQualification
        fields='__all__'

class HrmsEmployeeAcademicQualificationDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = HrmsUserQualification
        fields = '__all__'
    def update(self, instance, validated_data):
        instance.updated_by = validated_data.get('updated_by')
        instance.is_deleted = True
        instance.save()
        qualification_doc=HrmsUserQualificationDocument.objects.filter(user_qualification=instance,is_deleted=False)
        if qualification_doc:
            for q_d in qualification_doc:
                existing_image='./media/' + str(q_d.document)
                print('existing_image',existing_image)
                if os.path.isfile(existing_image):
                    os.remove(existing_image)
            qualification_doc.delete()
        return instance

class HrmsEmployeeAcademicQualificationDocumentAddSerializer(serializers.ModelSerializer):
    created_by=serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by=serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = HrmsUserQualificationDocument
        fields='__all__'

class HrmsEmployeeAcademicQualificationDocumentDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = HrmsUserQualificationDocument
        fields = '__all__'
    def update(self, instance, validated_data):
        instance.updated_by = validated_data.get('updated_by')
        instance.is_deleted = True
        instance.save()
        return instance

#:::::::::::::::::::::: HRMS NEW REQUIREMENT:::::::::::::::::::::::::::#
class HrmsNewRequirementAddSerializer(serializers.ModelSerializer):
    created_by=serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by=serializers.CharField(default=serializers.CurrentUserDefault())
    raised_by_data = serializers.DictField(required =False)
    class Meta:
        model = HrmsNewRequirement
        fields=('__all__')
        extra_fields= ('raised_by_data')

    def create(self,validated_data):
        print(validated_data)
        # for key,value in validated_data.items():
        #     if key == 'raised_by_data':


        validated_data.pop('raised_by_data')

        requirement_data= HrmsNewRequirement.objects.create(**validated_data,tab_status=2)
        return requirement_data

#:::::::::::::::::::::: HRMS INTERVIEW TYPE:::::::::::::::::::::::::::#
class InterviewTypeAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = HrmsInterviewType
        fields = ('id', 'name', 'created_by', 'owned_by')

class InterviewTypeEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = HrmsInterviewType
        fields = ('id', 'name', 'updated_by')

class InterviewTypeDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = HrmsInterviewType
        fields = '__all__'
    def update(self, instance, validated_data):
        instance.is_deleted=True
        instance.updated_by = validated_data.get('updated_by')
        instance.save()
        return instance

#:::::::::::::::::::::: HRMS INTERVIEW LEVEL:::::::::::::::::::::::::::#
class InterviewLevelAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = HrmsInterviewLevel
        fields = ('id', 'name', 'created_by', 'owned_by')

class InterviewLevelEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = HrmsInterviewLevel
        fields = ('id', 'name', 'updated_by')

class InterviewLevelDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = HrmsInterviewLevel
        fields = '__all__'
    def update(self, instance, validated_data):
        instance.is_deleted=True
        instance.updated_by = validated_data.get('updated_by')
        instance.save()
        return instance

#:::::::::::::::::::::: HRMS SCHEDULE INTERVIEW :::::::::::::::::::::::::::#

class ScheduleInterviewAddSerializer(serializers.ModelSerializer):
    created_by=serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by=serializers.CharField(default=serializers.CurrentUserDefault())
    interview_with=serializers.CharField(required=False)
    interviewers=serializers.ListField(required=False)
    resume=serializers.FileField(required=False,allow_null=True)
    resume_data=serializers.CharField(required=False)
    planned_date_of_interview=serializers.DateTimeField(required=False)
    planned_time_of_interview=serializers.TimeField(required=False)
    type_of_interview=serializers.IntegerField(required=False)
    level_of_interview=serializers.IntegerField(required=False)
    class Meta:
        model = HrmsScheduleInterview
        fields=('id','requirement','candidate_name','contact_no','email','note','resume','resume_data',
                 'planned_date_of_interview','planned_time_of_interview','type_of_interview',
                 'level_of_interview','interview_with','interviewers','created_by','owned_by','action_approval')

    def create(self,validated_data):
        try:

            created_by=validated_data.get('created_by')
            owned_by =validated_data.get('owned_by')
            # is_resheduled=validated_data.get('is_resheduled')
            candidate_name=validated_data.get('candidate_name') if 'candidate_name' in validated_data else None
            contact_no=validated_data.get('contact_no') if 'contact_no' in validated_data else None
            email=validated_data.get('email') if 'email' in validated_data else None
            note=validated_data.get('note') if 'note' in validated_data else None
            resume=validated_data.get('resume') if 'resume' in validated_data else None
            planned_date_of_interview=validated_data.get('planned_date_of_interview') if 'planned_date_of_interview' in validated_data else None
            planned_time_of_interview=validated_data.get('planned_time_of_interview') if 'planned_time_of_interview' in validated_data else None
            type_of_interview=validated_data.get('type_of_interview') if 'type_of_interview' in validated_data else None
            level_of_interview=validated_data.get('level_of_interview') if 'level_of_interview' in validated_data else None
            interview_with = validated_data.get('interview_with') if 'interview_with' in validated_data else None
            # print("interview_with",interview_with)
            with transaction.atomic():
                # print('validated_data',validated_data)
                print('requirement',validated_data.get('requirement'))
                tab_status=HrmsNewRequirement.objects.only('tab_status').get(id=str(validated_data.get('requirement')),
                                                                            is_deleted=False
                                                                            ).tab_status
                print('tab_status',tab_status)
                if tab_status >= 3:
                    if tab_status != 5 and tab_status != 6:
                        HrmsNewRequirement.objects.filter(id=str(validated_data.get('requirement')),
                                                        is_deleted=False).update(tab_status=4)
                    schedule_details,created=HrmsScheduleInterview.objects.get_or_create(
                                                                        requirement_id=str(validated_data.get('requirement')),
                                                                        candidate_name=candidate_name,
                                                                        contact_no=contact_no,
                                                                        email=email,
                                                                        note=note,
                                                                        resume=resume,
                                                                        created_by=created_by,
                                                                        owned_by=owned_by
                                                                        )
                    print('schedule_details',schedule_details.__dict__)
                    print('created',created)

                    schedule_another_details,created=HrmsScheduleAnotherRoundInterview.objects.get_or_create(schedule_interview=schedule_details,
                                                                                                            planned_date_of_interview=planned_date_of_interview,
                                                                                                            planned_time_of_interview=planned_time_of_interview,
                                                                                                            type_of_interview_id=str(type_of_interview),
                                                                                                            level_of_interview_id=str(level_of_interview),
                                                                                                            created_by=created_by,
                                                                                                            owned_by=owned_by
                                                                                                            )
                    print('schedule_another_details',schedule_another_details.__dict__)

                    interviewers_list=[]
                    if interview_with:
                        interviewers= interview_with.split(',')
                        print('interviewers',interviewers)
                        for i_w in interviewers:
                            interview_details,created_1=HrmsScheduleInterviewWith.objects.get_or_create(interview=schedule_another_details,
                                                                                        user_id=int(i_w),
                                                                                        created_by=created_by,
                                                                                        owned_by=owned_by
                                                                                    )
                            print('interview_details',interview_details.__dict__)
                            print('created_1',created_1)

                            interview_details.__dict__.pop('_state') if '_state' in interview_details.__dict__.keys() else interview_details.__dict__
                            interviewers_list.append(interview_details.__dict__)


                    schedule_details.__dict__['interviewers']=interviewers_list
                    schedule_details.__dict__['resume_data']=schedule_details.__dict__['resume']
                    schedule_details.__dict__['requirement']=validated_data.get('requirement')
                    schedule_details.__dict__['planned_date_of_interview']=schedule_another_details.__dict__['planned_date_of_interview']
                    schedule_details.__dict__['planned_time_of_interview']=schedule_another_details.__dict__['planned_time_of_interview']
                    schedule_details.__dict__['type_of_interview']=type_of_interview
                    schedule_details.__dict__['level_of_interview']=level_of_interview
                    return schedule_details.__dict__
                else:
                    return list()
        except Exception as e:
            raise e
class RescheduleInterviewAddSerializer(serializers.ModelSerializer):
    created_by=serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by=serializers.CharField(default=serializers.CurrentUserDefault())
    interview_with=serializers.CharField(required=False)
    interviewers=serializers.ListField(required=False)
    class Meta:
        model = HrmsScheduleAnotherRoundInterview
        fields=('id','planned_date_of_interview','planned_time_of_interview','type_of_interview',
        'level_of_interview','interview_status','is_resheduled','created_by','owned_by','interview_with','interviewers')
    def create(self,validated_data):
        try:
            schedule_interview = self.context['request'].query_params.get('schedule_interview', None)
            print('schedule_interview',type(schedule_interview))
            created_by=validated_data.get('created_by')
            owned_by=validated_data.get('owned_by')
            planned_date_of_interview=validated_data.get('planned_date_of_interview') if 'planned_date_of_interview' in validated_data else None
            planned_time_of_interview=validated_data.get('planned_time_of_interview') if 'planned_time_of_interview' in validated_data else None
            type_of_interview=validated_data.get('type_of_interview') if 'type_of_interview' in validated_data else None
            level_of_interview=validated_data.get('level_of_interview') if 'level_of_interview' in validated_data else None
            interview_with = validated_data.get('interview_with') if 'interview_with' in validated_data else None
            with transaction.atomic():
                prev_schedule_interview=HrmsScheduleAnotherRoundInterview.objects.filter(schedule_interview_id=int(schedule_interview),
                                                                                        is_deleted=False)
                print('prev_schedule_interview',prev_schedule_interview)
                if prev_schedule_interview:
                    for p_s_i in prev_schedule_interview:
                        p_s_i.is_resheduled=True
                        p_s_i.save()
                    schedule_another_details,created=HrmsScheduleAnotherRoundInterview.objects.get_or_create(schedule_interview_id=int(schedule_interview),
                                                                                                            planned_date_of_interview=planned_date_of_interview,
                                                                                                            planned_time_of_interview=planned_time_of_interview,
                                                                                                            type_of_interview_id=str(type_of_interview),
                                                                                                            level_of_interview_id=str(level_of_interview),
                                                                                                            created_by=created_by,
                                                                                                            owned_by=owned_by,
                                                                                                            )
                    print('schedule_another_details',schedule_another_details.__dict__)
                    interviewers_list=[]
                    if interview_with:
                        interviewers= interview_with.split(',')
                        print('interviewers',interviewers)
                        for i_w in interviewers:
                            interview_details,created_1=HrmsScheduleInterviewWith.objects.get_or_create(interview=schedule_another_details,
                                                                                        user_id=int(i_w),
                                                                                        created_by=created_by,
                                                                                        owned_by=owned_by
                                                                                    )
                            print('interview_details',interview_details.__dict__)
                            print('created_1',created_1)

                            interview_details.__dict__.pop('_state') if '_state' in interview_details.__dict__.keys() else interview_details.__dict__
                            interviewers_list.append(interview_details.__dict__)

                    schedule_another_details.__dict__['interviewers']=interviewers_list
                    schedule_another_details.__dict__['type_of_interview']=type_of_interview
                    schedule_another_details.__dict__['level_of_interview']=level_of_interview
                    return schedule_another_details.__dict__
        except Exception as e:
            raise e
class InterviewStatusAddSerializer(serializers.ModelSerializer):
    updated_by=serializers.CharField(default=serializers.CurrentUserDefault())
    interview_with=serializers.CharField(required=False)
    feedback=serializers.FileField(required=False)
    feedback_data = serializers.DictField(required=False)
    interviewers=serializers.ListField(required=False)
    # actual_date_of_interview=serializers.DateTimeField(required=False)
    # actual_time_of_interview=serializers.TimeField(required=False)
    # type_of_interview=serializers.IntegerField(required=False)
    # level_of_interview=serializers.IntegerField(required=False)
    # interview_status=serializers.IntegerField(required=False)
    class Meta:
        model = HrmsScheduleAnotherRoundInterview
        fields= ('id','actual_date_of_interview','actual_time_of_interview','type_of_interview',
        'level_of_interview','interview_status','interview_with','feedback','updated_by','feedback_data','interviewers')

    def update(self,instance,validated_data):
        try:
            actual_date_of_interview=validated_data.get('actual_date_of_interview') if 'actual_date_of_interview' in validated_data else None
            actual_time_of_interview=validated_data.get('actual_time_of_interview') if 'actual_time_of_interview' in validated_data else None
            type_of_interview=validated_data.get('type_of_interview') if 'type_of_interview' in validated_data else ""
            print('type_of_interview',type_of_interview)
            level_of_interview=validated_data.get('level_of_interview') if 'level_of_interview' in validated_data else ""
            interview_status=validated_data.get('interview_status') if 'interview_status' in validated_data else ""
            interview_with=validated_data.get('interview_with') if 'interview_with' in validated_data else None
            feedback=validated_data.get('feedback') if 'feedback' in validated_data else None

            updated_by=validated_data.get('updated_by')
            # print(instance.__dict__)
            data = {}
            with transaction.atomic():
                # schedule_another_details=HrmsScheduleAnotherRoundInterview.objects.filter(schedule_interview=instance,
                #                                                                             is_deleted=False
                #                                                                         )
                instance.actual_date_of_interview=actual_date_of_interview
                instance.actual_time_of_interview=actual_time_of_interview
                instance.type_of_interview=type_of_interview
                instance.level_of_interview=level_of_interview
                instance.interview_status=interview_status
                instance.updated_by=updated_by
                instance.save()

                if interview_with:
                    interviewers=interview_with.split(',')
                    interviewers_list = []
                    for i_w in interviewers:
                        int_det=HrmsScheduleInterviewWith.objects.filter(interview=instance,user_id=int(i_w),is_deleted=False)
                        print('int_det',int_det)
                        if int_det:
                            int_det.delete()

                        create_interviewers,created = HrmsScheduleInterviewWith.objects.get_or_create(
                            interview =instance,
                            user_id= int(i_w),
                            created_by=updated_by,
                            owned_by=updated_by
                        )
                        print('create_interviewers',create_interviewers)
                        create_interviewers.__dict__.pop('_state') if '_state' in create_interviewers.__dict__.keys() else create_interviewers.__dict__
                        interviewers_list.append(create_interviewers.__dict__)
                    instance.__dict__['interviewers'] = interviewers_list

                if feedback:
                    upload_feedback=HrmsScheduleInterviewFeedback.objects.create(interview=instance,
                                                                                upload_feedback=feedback,
                                                                                created_by=updated_by,
                                                                                owned_by=updated_by
                                                                                )
                    upload_feedback.__dict__.pop('_state') if '_state' in upload_feedback.__dict__.keys() else upload_feedback.__dict__
                    print('upload_feedback',upload_feedback.__dict__)
                    # data =instance.__dict__
                    instance.__dict__['feedback_data']=upload_feedback.__dict__
                    # data['feedback']=upload_feedback.__dict__

                instance.__dict__['type_of_interview'] = type_of_interview
                instance.__dict__['level_of_interview'] = level_of_interview
                instance.__dict__['actual_date_of_interview'] = actual_date_of_interview
                instance.__dict__['actual_time_of_interview'] = actual_time_of_interview
                instance.__dict__['interview_status'] = interview_status
                # print("instance.__dict__",instance.__dict__)
                return instance
        except Exception as e:
            raise e

class InterviewStatusListSerializer(serializers.ModelSerializer):
    class Meta:
        model = HrmsScheduleInterview
        fields= '__all__'

class CandidatureUpdateEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = HrmsScheduleInterview
        fields = ('id','notice_period','expected_ctc','current_ctc', 'updated_by')

class CandidatureApproveEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = HrmsScheduleInterview
        fields = ('id','updated_by','level_approval','approval_permission_user_level')

    def update(self, instance, validated_data):
        try:
            req_id = self.context['request'].query_params.get('req_id', None)
            section_name = self.context['request'].query_params.get('section_name', None)
            with transaction.atomic():
                approved_data = HrmsScheduleInterview.objects.filter(requirement=req_id)
                check_full = HrmsNewRequirement.objects.get(id=req_id)
                print("check_full.tab_status",check_full.tab_status)
                if check_full.tab_status != 6:

                    approval_data = HrmsScheduleInterview.objects.filter(id=instance.id).update(**validated_data)
                    approved_list = HrmsScheduleInterview.objects.get(id=instance.id)
                    # print('approved_list',approved_list.__dict__)
                    approved_list.__dict__.pop('id')
                    approved_list.__dict__.pop('created_by_id')
                    approved_list.__dict__.pop('owned_by_id')
                    approved_list.__dict__.pop('updated_by_id')
                    approved_list.__dict__.pop('created_at')
                    approved_list.__dict__.pop('updated_at')

                    approved_list.__dict__.pop('_state')
                    print("approved_list.__dict__",approved_list.__dict__)

                    if approved_list:
                        print("entered the condition ")
                        print(instance.id)
                        HrmsScheduleInterviewLog.objects.create(hsi_master_id = instance.id,**(approved_list.__dict__))
                    # print('approved_list',approved_list)
                    count =0
                    no_of_pos = HrmsNewRequirement.objects.get(id=req_id).number_of_position
                    permission_level_value = PmsApprovalPermissonLavelMatser.objects.get(section__cot_name__icontains=section_name).permission_level
                    for data in approved_data:
                        if data.approval_permission_user_level:
                            var=data.approval_permission_user_level.permission_level
                            res = re.sub("\D", "", var)
                            print("res",res,type(res))
                            if int(res) == int(permission_level_value) and data.level_approval == True:
                                count =count+1
                    print("count",count, no_of_pos)
                    if count == no_of_pos:
                        HrmsNewRequirement.objects.filter(id=req_id).update(tab_status=6,closing_date=datetime.now)

                else:
                    custom_exception_message(self,None,"Number of position is Fullfilled")




                return validated_data


        except Exception as e:
            raise e

class OpenAndClosedRequirementListSerializer(serializers.ModelSerializer):
    department_name=serializers.SerializerMethodField(required=False)
    designation_name=serializers.SerializerMethodField(required=False)
    raised_by=serializers.SerializerMethodField(required=False)
    tab_status_name = serializers.CharField(source='get_tab_status_display')
    def get_raised_by(self,HrmsNewRequirement):
        if HrmsNewRequirement.created_by:
            user_detail=User.objects.filter(id=HrmsNewRequirement.created_by.id)
            for u_d in user_detail:
                name=u_d.first_name+" "+u_d.last_name
            return name
    def get_department_name(self,HrmsNewRequirement):
        if HrmsNewRequirement.issuing_department:
            return TCoreDepartment.objects.only('cd_name').get(id=HrmsNewRequirement.issuing_department.id).cd_name
    def get_designation_name(self,HrmsNewRequirement):
        if HrmsNewRequirement.proposed_designation:
            return TCoreDesignation.objects.only('cod_name').get(id=HrmsNewRequirement.proposed_designation.id).cod_name
    class Meta:
        model = HrmsNewRequirement
        fields= '__all__'

class UpcomingAndInterviewHistoryListSerializer(serializers.ModelSerializer):
    tab_status=serializers.SerializerMethodField(required=False)
    date_of_requirement=serializers.SerializerMethodField(required=False)
    department=serializers.SerializerMethodField(required=False)
    designation=serializers.SerializerMethodField(required=False)
    location=serializers.SerializerMethodField(required=False)
    candidature_name = serializers.CharField(source='get_action_approval_display')
    def get_tab_status(self,HrmsScheduleInterview):
        if HrmsScheduleInterview.requirement:
            tab_status=HrmsNewRequirement.objects.filter(id=HrmsScheduleInterview.requirement.id,
                                                                is_deleted=False)
            if tab_status:
                for t_s in tab_status:
                    tab_dict={
                        'tab_status_id':t_s.tab_status,
                        'tab_status_name':t_s.get_tab_status_display()
                    }
                return tab_dict
            else:
                return None
    def get_date_of_requirement(self,HrmsScheduleInterview):
        if HrmsScheduleInterview.requirement:
            return HrmsNewRequirement.objects.only('date').get(id=HrmsScheduleInterview.requirement.id,
                                                                is_deleted=False).date
    def get_department(self,HrmsScheduleInterview):
        if HrmsScheduleInterview.requirement:
            dept_det=HrmsNewRequirement.objects.filter(id=HrmsScheduleInterview.requirement.id,
                                                                is_deleted=False)
            if dept_det:
                for d_d in dept_det:
                    details={
                        'department_id':d_d.issuing_department.id,
                        'department_name':d_d.issuing_department.cd_name
                    }
                return details
            else:
                return None
    def get_designation(self,HrmsScheduleInterview):
        if HrmsScheduleInterview.requirement:
            desig_det=HrmsNewRequirement.objects.filter(id=HrmsScheduleInterview.requirement.id,
                                                                is_deleted=False)
            if desig_det:
                for d_d in desig_det:
                    details={
                        'designation_id':d_d.proposed_designation.id,
                        'designation_name':d_d.proposed_designation.cod_name
                    }
                return details
            else:
                return None
    def get_location(self,HrmsScheduleInterview):
        if HrmsScheduleInterview.requirement:
            return HrmsNewRequirement.objects.only('location').get(id=HrmsScheduleInterview.requirement.id,
                                                                is_deleted=False).location

    class Meta:
        model = HrmsScheduleInterview
        fields= '__all__'

class EmployeeActiveInactiveUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False)
    email = serializers.CharField(required=False)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    is_superuser = serializers.BooleanField(required=False)
    is_active = serializers.BooleanField(required=False)
    class Meta:
        model = User
        fields = ('id','first_name', 'last_name', 'username','email', 'is_superuser', 'is_active')

    def update(self, instance, validated_data):
        try:
            with transaction.atomic():

                instance.is_active = validated_data.get('is_active')
                instance.save()
                print('instance',instance)
                if validated_data.get('is_active'):
                    TCoreUserDetail.objects.filter(cu_user=instance).update(cu_is_deleted=False)
                else:
                    TCoreUserDetail.objects.filter(cu_user=instance).update(cu_is_deleted=True)

                return instance
        except Exception as e:
            raise e
