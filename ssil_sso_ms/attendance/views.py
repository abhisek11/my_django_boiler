from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from attendance.models import *
from attendance.serializers import *
from holidays.models import *
from master.models import *
from core.models import *
# from vms.vms_pagination import CSLimitOffestpagination,CSPageNumberVmsPagination
from rest_framework.views import APIView
from django.conf import settings
from rest_framework import filters
from datetime import datetime,timedelta,date
import collections
from rest_framework.exceptions import APIException
from rest_framework import mixins
from master.serializers import UserModuleWiseListSerializer
from master.models import TMasterModuleRole
from users.models import TCoreUserDetail
from django.db.models import Sum
from custom_decorator import *
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
import calendar
import pandas as pd
import numpy as np
import xlrd
from custom_decorator import *
from pagination import CSLimitOffestpagination,CSPageNumberPagination
from hrms.models import *
from datetime import datetime
from datetime import date,time
# import datetime
from rest_framework.parsers import MultiPartParser
from django.core.files.storage import FileSystemStorage
import shutil
import platform
import re
from django.db.models import When, Case, Value, CharField, IntegerField, F, Q
from pandas import DataFrame
import os.path
from os import path
from SSIL_SSO_MS.settings import BASE_DIR
from attendance import logger
from global_function import department,designation,userdetails,getHostWithPort,raw_query_extract
import time
from functools import reduce
from attendance.tasks import ( hello, unjustified_sms_alert_to_all_employee_task, unjustified_mail_alert_to_all_employee_task, 
                                pending_sms_alert_to_reporting_head, pending_mail_alert_to_reporting_head,)


# Create your views here.
############GLOBAL LOG VIEW ###############################################################
'''Author:- Abhisek Singh 
   Description:- Generate log for all the activities 
'''
# def activity_view(request):
#     # Authentication check.
#     authentication_result = views.authentication_check(request, [Account.ACCOUNT_ADMIN])
#     if authentication_result is not None: return authentication_result
#     # Get the template data from the session
#     template_data = views.parse_session(request, {'query': Action.objects.all().order_by('-timePerformed')})
#     # Proceed with the rest of the view
#     if 'sort' in request.GET:
#         if request.GET['sort'] == 'description':
#             template_data['query'] = Action.objects.all().order_by('description', '-timePerformed')
#         if request.GET['sort'] == 'user':
#             template_data['query'] = Action.objects.all().order_by('user__username', '-timePerformed')
#         if request.GET['sort'] == 'type':
#             template_data['query'] = Action.objects.all().order_by('type', 'description', '-timePerformed')
#     return render(request, 'healthnet/admin/activity.html', template_data)
#################################################################################################
#:::::::::::::::::::::: DEVICE MASTER:::::::::::::::::::::::::::#
class DeviceMasterAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = DeviceMaster.objects.filter(is_deleted=False)
    serializer_class = DeviceMasterAddSerializer

    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response

class DeviceMasterEditView(generics.RetrieveUpdateAPIView):
	permission_classes = [IsAuthenticated]
	authentication_classes = [TokenAuthentication]
	queryset = DeviceMaster.objects.filter(is_deleted=False)
	serializer_class = DeviceMasterEditSerializer

class DeviceMasterDeleteView(generics.RetrieveUpdateAPIView):
	permission_classes = [IsAuthenticated]
	authentication_classes = [TokenAuthentication]
	queryset = DeviceMaster.objects.filter(is_deleted=False)
	serializer_class = DeviceMasterDeleteSerializer

#:::::::::::::::::::::: ATTENDENCE MONTH MASTER:::::::::::::::::::::::::::#
class AttendenceMonthMasterAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = AttendenceMonthMaster.objects.filter(is_deleted=False)
    serializer_class = AttendenceMonthMasterAddSerializer

    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response

class AttendenceMonthMasterEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = AttendenceMonthMaster.objects.filter(is_deleted=False)
    serializer_class = AttendenceMonthMasterEditSerializer

    @response_modify_decorator_update
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
        
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response

class AttendenceMonthMasterDeleteView(generics.RetrieveUpdateAPIView):
	permission_classes = [IsAuthenticated]
	authentication_classes = [TokenAuthentication]
	queryset = AttendenceMonthMaster.objects.filter(is_deleted=False)
	serializer_class = AttendenceMonthMasterDeleteSerializer

#:::::::::::::::::: DOCUMENTS UPLOAD ::::::::::::::::::::::::#
class AttendanceFileUploadOldVersion(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = AttandancePerDayDocuments.objects.filter(is_deleted=False)
    serializer_class = AttendanceFileUploadOldVersionSerializer
    parser_classes = (MultiPartParser,)
    

    def att_create(self, filter: dict):
        logdin_user_id = self.request.user.id
        attendance,create1 = Attendance.objects.get_or_create(created_by_id=logdin_user_id,owned_by_id=logdin_user_id,**filter)
        return attendance
    def request_create(self, filter: dict):
        logdin_user_id = self.request.user.id  #attendance_date
        request,create2 = AttendanceApprovalRequest.objects.get_or_create(created_by_id=logdin_user_id,owned_by_id=logdin_user_id,**filter)
        return request

    def post(self, request, *args, **kwargs):
        response = super().post(request,*args,**kwargs)
        # print("response",response.data['document'])
        print("Please wait...")
        print("processing...")
        os_type = platform.system().lower()
        # print("os_type",os_type)
        if request.is_secure():
            protocol = 'https://'
        else:
            protocol = 'http://'

        host_url = getHostWithPort(request)
        print('host_url',host_url)
        url = response.data['document'].replace(host_url,'./')
        # url = response.data['document'].replace('https://shyamsteel.tech:8002','.')
        # if os_type=="linux":
        #     url = re.sub('^http://(\d+\.)+\d+\:\d{4}','.',response.data['document'])
        # elif os_type=="windows":
        #     # url = url = re.sub('^http://(\d+\.)+\d+\:\d{4}','',response.data['document'])
        #     url = re.sub('^http://(\d+\.)+\d+\:\d{4}\/','',response.data['document'])
        # print("url", url)
        try:
            wb = xlrd.open_workbook(url)
        except xlrd.biffh.XLRDError:
            print("XLRDError occure")
        if wb:
            sh = wb.sheet_by_index(0)
        else:
            print("exit")
            exit()
        a=[]
        for i in range(sh.nrows):
            for j in range(sh.ncols):
                if sh.cell_value(i,j) == 'Date' and sh.cell_value(i,j+1) == 'Time':
                    skip_row=i
                    for i in range(0,skip_row):
                        a.append(i)
                    data = pd.read_excel(url,skiprows=skip_row,converters={'Empid':str})
                    #print(data.head())

        data.dropna(axis = 0, how ='all', inplace = True)  #Remove blank rows with all nun column
        data = data.loc[:, ~data.columns.str.contains('^Unnamed')] #Remove blank unnamed columns

        # avoid_att = TMasterModuleRoleUser.objects.filter((Q(mmr_type=1)|Q(mmr_type=6))&Q(mmr_is_deleted=False)).values_list('mmr_user')
        # print("avoid_att",avoid_att)

        # user_details = TCoreUserDetail.objects.filter((~Q(cu_user__in=TMasterModuleRoleUser.objects.filter(Q(mmr_type=1)|Q(mmr_type=6)|Q(mmr_is_deleted=True)
        #                                                 ).values_list('mmr_user',flat=True))),
        #                                                 (~Q(cu_punch_id__in=['PMSSITE000','#N/A',''])),
        #                                                 (Q(cu_is_deleted=False))).values() ##avoid 'PMSSITE000','#N/A' punch ids
        # print('user_details',len(user_details))
        # user_count = len(user_details) if user_details else 0
        holiday_list = HolidaysList.objects.filter(status=True).values('holiday_date','holiday_name')
        device_details = DeviceMaster.objects.filter(is_exit=True,is_deleted=False).values('id')
        if device_details:
            device_no_list = [x['id'] for x in device_details]
        # print("device_no_list", device_no_list)
        day = data.get('Date')[0]
        # print("dayyy", day)
        # request_checking_flag = 1
        if day:
            today_datetime = datetime.strptime(str(day)+'T'+'12:00:00', "%d/%m/%YT%H:%M:%S")
            print("today_datetime",today_datetime.date())
            date_time_day = today_datetime.date()
            late_convence_limit = today_datetime.replace(hour=20, minute=30)
            # print("late_convence_limit",late_convence_limit)
            '''
                Delete only last Attendance  if these DATE had already in Attendance Date.
            '''
            lase_attendance = Attendance.objects.filter(date__date=date_time_day).order_by('-id')
            if lase_attendance:
                print('delete_data',lase_attendance[0].__dict__['id'])
                AttendanceApprovalRequest.objects.filter(attendance=lase_attendance[0].__dict__['id']).delete()
                AttendanceLog.objects.filter(attendance=lase_attendance[0].__dict__['id']).delete()
                Attendance.objects.filter(id=lase_attendance[0].__dict__['id']).delete()

            '''
                << Avoid attendance >>
                IF User is Demo_user or Super_user
                IF Punch id is ('PMSSITE000','#N/A','')
                IF User had already Attendance for this day.
            '''
            user_details = TCoreUserDetail.objects.filter(~Q(
                    (   
                        Q(cu_user__in=TMasterModuleRoleUser.objects.filter(
                        Q(mmr_type=1)|Q(mmr_type=6)|Q(mmr_is_deleted=True)).values_list('mmr_user',flat=True))
                    )|
                    (Q(cu_punch_id='#N/A'))|
                    (Q(cu_user_id__in=Attendance.objects.filter(date__date=date_time_day).values_list('employee',flat=True)))
                ),
                (Q(joining_date__date__lte=date_time_day)),cu_is_deleted=False).values() ##avoid 'PMSSITE000','#N/A' punch ids

            print('Total_user',len(user_details))
            user_count = len(user_details) if user_details else 0
            # return Response({'result':{'request_status':0,'msg':str(user_details)}})
        else:
            return Response({'result':{'request_status':0,'msg':'Enter proper Excel'}})
        total_month_grace=AttendenceMonthMaster.objects.filter(month_start__date__lte=today_datetime.date(),
                                        month_end__date__gte=today_datetime.date(),is_deleted=False).values('grace_available',
                                                                                 'year_start_date', 'year_end_date', 'month', 
                                                                                 'month_start', 'month_end','grace_available'
                                                                                 )
        # print("total_month_grace",total_month_grace)

        special_day = AttendanceSpecialdayMaster.objects.filter(((Q(day_start_time__date=today_datetime.date())|Q(
            day_end_time__date=today_datetime.date())) & Q(is_deleted=False))).values('day_start_time__time','day_end_time__time','remarks')

        special_full_day = AttendanceSpecialdayMaster.objects.filter(full_day__date=today_datetime.date(),is_deleted=False).values('full_day__date','remarks')
        print("special_full_day",special_full_day)
        print("special_day",special_day)

        for user in user_details:
            user_count = user_count-1
            print("Wait...", user_count)
            att_filter = {}
            req_filter = {}
            pre_att_filter = {}
            pre_req_filter = {}
            late_con_filter = {}
            bench_filter = {}
            pre_att = None

            logout_time = None
            check_out = 0
            # adv_leave_type = None
            user_flag = 0
            cu_punch_id = user['cu_punch_id'] if user['cu_punch_id'] else None
            cu_user_id = int(user['cu_user_id'])

            ###If user has no login/logout/lunch time >> Then fix their time##
            user['daily_loginTime'] = today_datetime.replace(hour=10, minute=00).time() if user['daily_loginTime'] is None else user['daily_loginTime']
            user['daily_logoutTime'] = today_datetime.replace(hour=19, minute=00).time() if user['daily_logoutTime'] is None else user['daily_logoutTime']
            user['lunch_start'] = today_datetime.replace(hour=13, minute=30).time() if user['lunch_start'] is None else user['lunch_start']
            user['lunch_end'] = today_datetime.replace(hour=14, minute=00).time() if user['lunch_end'] is None else user['lunch_end']
            
            ## If Change Login-Logout time (Special Day) ##
            if special_day:
                daily_loginTime = special_day[0]['day_start_time__time'] if special_day[0]['day_start_time__time'] is not None else user['daily_loginTime']
                # daily_logoutTime = special_day[0]['day_end_time__time'] if special_day[0]['day_end_time__time'] is not None else user['daily_logoutTime']
                daily_logoutTime = special_day[0]['day_end_time__time'] if special_day[0]['day_end_time__time'] is not None and \
                                                            special_day[0]['day_end_time__time']<user['daily_logoutTime'] else user['daily_logoutTime']
                pre_att_filter['day_remarks'] = special_day[0]['remarks'] if special_day[0]['remarks'] is not None else ''
            elif today_datetime.weekday()==5:
                daily_loginTime = user['daily_loginTime']
                daily_logoutTime = user['daily_logoutTime'].replace(hour=16, minute=00)
                pre_att_filter['day_remarks'] = 'Present'
            else:
                daily_loginTime = user['daily_loginTime']
                daily_logoutTime = user['daily_logoutTime']
                pre_att_filter['day_remarks'] = 'Present'
            
            ## LUNCH TIME ##
            lunch_start = datetime.combine(today_datetime,user['lunch_start'])
            lunch_end = datetime.combine(today_datetime,user['lunch_end'])

            ## DAILY LOGIN-LOGOUT ##
            # print("daily_loginTime", daily_loginTime, type(daily_loginTime))
            daily_login = datetime.combine(today_datetime,daily_loginTime)
            daily_logout = datetime.combine(today_datetime,daily_logoutTime)

            is_saturday_off = user['is_saturday_off'] 
            att_filter['employee_id']=cu_user_id
            grace_over = False

            joining_date = user['joining_date']
            if total_month_grace:
                grace_available = total_month_grace[0]['grace_available'] if total_month_grace[0]['grace_available'] is not None else 0
                # print("GRACE", grace_available)
                if joining_date >= total_month_grace[0]['month_start'] and joining_date <= total_month_grace[0]['month_end']:
                    total_grace = JoiningApprovedLeave.objects.filter(employee=cu_user_id,is_deleted=False).values('first_grace')
                    grace_available = total_grace[0]['first_grace'] if total_grace[0]['first_grace'] is not None else 0
                    # print("grace_available AAAA", grace_available, cu_user_id)

            availed_grace=AttendanceApprovalRequest.objects.filter(Q(attendance__employee=cu_user_id) &
                                                            Q(duration_start__gte=total_month_grace[0]['month_start']) &
                                                            Q(duration_start__lte=total_month_grace[0]['month_end']) &
                                                            Q(is_requested=True) &
                                                            Q(is_deleted=False)&
                                                            (Q(request_type='GR')|Q(checkin_benchmark=True))
                                                            ).aggregate(Sum('duration'))['duration__sum']
            # print('availed_grace',availed_grace)
            availed_grace = availed_grace if availed_grace else 0
            
            # if grace_available<availed_grace: #nur code 
            #     grace_over = True
            for index, row in data.iterrows():
                #print('row',row)
                # lunch_start = datetime.combine(today_datetime,user['lunch_start'])
                date_time = str(row['Date'])+'T'+str(row['Time'])
                date_time_format = datetime.strptime(date_time, "%d/%m/%YT%H:%M:%S")
                #print('cu_punch_id_type',type(cu_punch_id),cu_punch_id)
                #print('rowEmpid',type(row['Empid']),row['Empid'])
                if cu_punch_id == row['Empid']:
                    user_flag = 1
                    ##################### Added By Rupam #######################
                    deviceMasterDetails = DeviceMaster.objects.filter(device_no=int(row['CID']))
                    if deviceMasterDetails:
                        current_device = DeviceMaster.objects.get(device_no=int(row['CID']))
                        # print("current_device",current_device)
                    ##################### END ###################################
                    pre_att_filter['employee_id'] = cu_user_id
                    # pre_att_filter['day_remarks'] = 'Present'
                    pre_att_filter['is_present'] = True
                    pre_att_filter['date'] = date_time_format
                    pre_att_filter['login_time'] = date_time_format
                    # print("pre_att_filter",pre_att_filter)

                    ##First time log in a Day##Successful
                    if pre_att is None:                    
                        if pre_att_filter:
                            pre_att = self.att_create(pre_att_filter)
                            bench_time = daily_login + timedelta(minutes=30)
                            # print('bench_time',bench_time)

                            ###Check login if After USER Daily login time = Duration### Successful
                            if daily_login<pre_att_filter['login_time']:
                                    bench_filter['attendance']=pre_att
                                    bench_filter['attendance_date'] = daily_login.date()
                                    bench_filter['duration_start']=daily_login
                                    bench_filter['duration_end']=pre_att_filter['login_time']
                                    bench_filter['duration'] = round(((bench_filter['duration_end']-bench_filter['duration_start']).seconds)/60)
                                    bench_filter['punch_id'] = cu_punch_id
                                    if grace_available<availed_grace + float(bench_filter['duration']): #abhisek code 
                                        grace_over = True
                                    if bench_time>pre_att_filter['login_time'] and grace_over is False:
                                        bench_filter['checkin_benchmark']=True
                                        bench_filter['is_requested']=True
                                        # bench_filter['is_requested']=True
                                        # bench_filter['request_type']='GR'
                                    else:
                                        bench_filter['checkin_benchmark']=False

                                    if bench_filter['duration']>0:
                                        bench_req = self.request_create(bench_filter)

                    ##After Daily Attendance## Successful
                    if pre_att:
                        att_log_create, create1 = AttendanceLog.objects.get_or_create(
                            attendance=pre_att,
                            employee_id=cu_user_id,
                            time=date_time_format,
                            device_no=current_device
                        )

                        logout_time = date_time_format
                        duration_count = 0
                        if check_out == 0 and current_device.__dict__['id'] in device_no_list and date_time_format<daily_logout:
                            # print("if current_device in device_no_list:")
                            check_out = 1
                            pre_req_filter['attendance'] = pre_att
                            pre_req_filter['punch_id'] = cu_punch_id
                            pre_req_filter['duration_start'] = date_time_format
                        elif check_out == 1 and current_device not in device_no_list and date_time_format<daily_login:
                            check_out = 0
                            pre_req_filter = {}
                        elif check_out == 1 and current_device not in device_no_list and date_time_format>daily_login:
                            check_out = 0
                            if date_time_format>daily_logout:
                                pre_req_filter['duration_end'] = daily_logout
                            else:
                                pre_req_filter['duration_end'] = date_time_format

                            if pre_req_filter['duration_start']<daily_login:
                                pre_req_filter['duration_start'] = daily_login
                            # else:
                            #     pre_req_filter['duration_end'] = date_time_format

                            if bench_time>pre_req_filter['duration_end'] and grace_over is False:
                                pre_req_filter['checkin_benchmark']=True
                                pre_req_filter['is_requested']=True


                            if lunch_end < pre_req_filter['duration_start']:
                                duration_count = round(((pre_req_filter['duration_end']-pre_req_filter['duration_start']).seconds)/60)
                            elif lunch_start > pre_req_filter['duration_end']:
                                duration_count = round(((pre_req_filter['duration_end']-pre_req_filter['duration_start']).seconds)/60)
                            elif lunch_start > pre_req_filter['duration_start'] and lunch_end < pre_req_filter['duration_end']:
                                duration_count = round(((lunch_start - pre_req_filter['duration_start'] + pre_req_filter['duration_end'] - lunch_end).seconds)/60)
                            elif lunch_start > pre_req_filter['duration_start'] and lunch_end > pre_req_filter['duration_end']:
                                duration_count = round(((lunch_start - pre_req_filter['duration_start']).seconds)/60)
                            elif lunch_end < pre_req_filter['duration_end'] and lunch_start < pre_req_filter['duration_start']:
                                duration_count = round(duration_count + ((pre_req_filter['duration_end']-lunch_end).seconds)/60)

                            # print("duration_count",duration_count, pre_req_filter)
                            if duration_count>0:
                                pre_req_filter['duration']=duration_count
                                pre_req_filter['attendance_date'] = pre_req_filter['duration_start'].date()
                                pre_req = self.request_create(pre_req_filter)
                                pre_req_filter = {}
                                #print("pre_req",pre_req)


            if logout_time and pre_att:
                # print('pre_att',pre_att.id)
                pre_att_update = Attendance.objects.filter(pk=pre_att.id).update(logout_time=logout_time)
                ### IF Late convence ### Successful Testing
                if daily_logoutTime < logout_time.time():
                    late_con_filter['attendance'] = pre_att
                    late_con_filter['punch_id'] = cu_punch_id
                    late_con_filter['attendance_date']=daily_logout.date()
                    late_con_filter['duration_start']=daily_logout
                    late_con_filter['duration_end']=logout_time
                    late_con_filter['duration'] = round(((late_con_filter['duration_end']-late_con_filter['duration_start']).seconds)/60)
                    late_con_filter['is_late_conveyance']=True
                    # if late_con_filter['duration']>10: #If late conveyance grater then 10 Minutes.
                    '''
                        As per requirement and discussion with Tonmay Da(10.12.2019):
                        LATE CONVENCE always count after 08:30 PM 
                    '''
                    if late_convence_limit>=late_con_filter['duration_start'] and late_convence_limit<late_con_filter['duration_end']\
                         and late_con_filter['duration']>0:
                        # print("late_con_filter",late_con_filter)
                        late_req = self.request_create(late_con_filter)
                        # print("late_req",late_req)
                
                ###If Logout less then User's Daily log out### Successful Testing
                elif daily_logoutTime > logout_time.time():
                    late_con_filter['attendance']=pre_att
                    late_con_filter['punch_id'] = cu_punch_id
                    late_con_filter['attendance_date']=daily_logout.date()
                    late_con_filter['duration_start']=logout_time
                    late_con_filter['duration_end']=daily_logout
                    late_con_filter['duration'] = round(((late_con_filter['duration_end']-late_con_filter['duration_start']).seconds)/60)
                    late_con_filter['is_late_conveyance']=False
                    # late_con_filter['request_type']='GR'
                    if late_con_filter['duration']>0:
                        # print("late_con_filter",late_con_filter)
                        late_req = self.request_create(late_con_filter)
                        # print("late_req",late_req)

        ## IF User Absent ###
            if user_flag==0:
                # print("ABSENT")
                is_required = False
                # print("user",cu_user_id)
                adv_leave_type = None
                leave = EmployeeAdvanceLeaves.objects.filter(
                    Q(start_date__date__lte=date_time_day)&Q(end_date__date__gte=date_time_day)&Q(employee_id=cu_user_id)&  #changes by abhisek 21/11/19
                    (Q(approved_status='pending')|Q(approved_status='approved'))).values('leave_type','reason')
                # print("leave",leave)
                '''
                Modified By :: Rajesh Samui
                Reason :: State Wise Holiday Calculation
                Line :: 490-502
                Date :: 10-02-2020
                '''
                #holiday = HolidaysList.objects.filter(status=True,holiday_date=date_time_day).values('holiday_name')
                state_obj = TCoreUserDetail.objects.get(cu_user__id=cu_user_id).job_location_state
                default_state = TCoreState.objects.filter(cs_state_name__iexact='west bengal').first()
                t_core_state_id = state_obj.id if state_obj else default_state.id
                holiday = HolidayStateMapping.objects.filter(Q(holiday__holiday_date=date_time_day)&Q(state__id=t_core_state_id)).values('holiday__holiday_name')

                # print(state_obj)
                # print(t_core_user_state_code)
                # print(holiday)
                # print(holiday[0]["holiday__holiday_name"])


                if leave:
                    adv_leave_type = leave[0]['leave_type']
                    # print("leave_type",leave[0]['leave_type'])
                    att_filter['day_remarks']=leave[0]['leave_type']
                    is_required = True
                elif holiday:
                    holiday_name = holiday[0]["holiday__holiday_name"]
                    att_filter['day_remarks']=holiday[0]["holiday__holiday_name"]
                elif special_full_day:
                    # special_full_day_name = special_full_day[0]["full_day__date"]
                    att_filter['day_remarks']=special_full_day[0]["remarks"]
                elif date_time_day.weekday()==6:
                    # print("Sunday")
                    att_filter['day_remarks']="Sunday"
                elif date_time_day.weekday()==5:
                    saturday_off_list = AttendenceSaturdayOffMaster.objects.filter(employee_id=cu_user_id,is_deleted=False).values(
                       'first', 'second', 'third', 'fourth', 'all_s_day').order_by('-id')

                    if saturday_off_list:
                        if saturday_off_list[0]['all_s_day'] is True:
                            # if user['is_saturday_off'] is True:
                            att_filter['day_remarks']='Saturday'

                        else:
                            week_date = date_time_day.day
                            # print("week_date",  week_date)
                            month_calender = calendar.monthcalendar(date_time_day.year, date_time_day.month)
                            saturday_list = (0,1,2,3) if month_calender[0][calendar.SATURDAY] else (1,2,3,4)

                            if saturday_off_list[0]['first'] is True and int(week_date)==int(month_calender[saturday_list[0]][calendar.SATURDAY]):
                                att_filter['day_remarks']='Saturday'
                            elif saturday_off_list[0]['second'] is True and int(week_date)==int(month_calender[saturday_list[1]][calendar.SATURDAY]):
                                att_filter['day_remarks']='Saturday'
                            elif saturday_off_list[0]['third'] is True and int(week_date)==int(month_calender[saturday_list[2]][calendar.SATURDAY]):
                                att_filter['day_remarks']='Saturday'
                            elif saturday_off_list[0]['fourth'] is True and int(week_date)==int(month_calender[saturday_list[3]][calendar.SATURDAY]):
                                att_filter['day_remarks']='Saturday'
                            else:
                                #print("Not Present")
                                is_required = True
                                att_filter['day_remarks']="Not Present"
                                    
                    else:
                        is_required = True
                        att_filter['day_remarks']="Not Present"
                    # print("Saturday")

                else:
                    is_required = True
                    att_filter['day_remarks']="Not Present"
                if att_filter:
                    date = date_time[0:10]+'T'+str(daily_loginTime)
                    date_time_date =datetime.strptime(date, "%d/%m/%YT%H:%M:%S")
                    #print("date_time_format",date_time_date)
                    att_filter['date']=date_time_date
                    #print("att_filter",att_filter)

                    abs_att = self.att_create(att_filter)
                    #print("att_filter",abs_att)
                    if is_required is True:
                        req_filter['attendance']= abs_att
                        req_filter['attendance_date'] = daily_login.date()
                        req_filter['duration_start'] = daily_login
                        req_filter['duration_end'] = daily_logout
                        req_filter['duration'] = round(((req_filter['duration_end']-req_filter['duration_start']).seconds)/60)

                        if adv_leave_type:
                            req_filter['request_type']='FD'
                            req_filter['leave_type'] = adv_leave_type
                            req_filter['approved_status'] = 'approved'
                            req_filter['is_requested'] = True
                            req_filter['justification'] = leave[0]['reason']

                        if req_filter:
                            req_filter['punch_id'] = cu_punch_id
                            abs_req = self.request_create(req_filter)
                            # print("abs_req",abs_req, req_filter)


        return Response({'result':{'request_status':1,'msg':'Successful'}})

#########

class AttendanceFileUploadForNewUser(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = AttandancePerDayDocuments.objects.filter(is_deleted=False)
    serializer_class = AttendanceFileUploadSerializer
    parser_classes = (MultiPartParser,)
    

    def att_create(self, filter: dict):
        logdin_user_id = self.request.user.id
        attendance,create1 = Attendance.objects.get_or_create(created_by_id=logdin_user_id,owned_by_id=logdin_user_id,**filter)
        return attendance
    def request_create(self, filter: dict):
        logdin_user_id = self.request.user.id  #attendance_date
        request,create2 = AttendanceApprovalRequest.objects.get_or_create(created_by_id=logdin_user_id,owned_by_id=logdin_user_id,**filter)
        return request

    def post(self, request, *args, **kwargs):
        response = super().post(request,*args,**kwargs)
        # print("response",response.data['document'])
        print("Please wait...")
        print("processing...")
        os_type = platform.system().lower()
        # print("os_type",os_type)
        if request.is_secure():
            protocol = 'https://'
        else:
            protocol = 'http://'

        host_url = getHostWithPort(request)
        print('host_url',host_url)
        url = response.data['document'].replace(host_url,'./')
        # if os_type=="linux":
        #     url = re.sub('^http://(\d+\.)+\d+\:\d{4}','.',response.data['document'])
        # elif os_type=="windows":
        #     # url = url = re.sub('^http://(\d+\.)+\d+\:\d{4}','',response.data['document'])
        #     url = re.sub('^http://(\d+\.)+\d+\:\d{4}\/','',response.data['document'])
        print("url", url)
        try:
            wb = xlrd.open_workbook(url)
        except xlrd.biffh.XLRDError:
            print("XLRDError occure")
        if wb:
            sh = wb.sheet_by_index(0)
        else:
            print("exit")
            exit()
        a=[]
        for i in range(sh.nrows):
            for j in range(sh.ncols):
                if sh.cell_value(i,j) == 'Date' and sh.cell_value(i,j+1) == 'Time':
                    skip_row=i
                    for i in range(0,skip_row):
                        a.append(i)
                    data = pd.read_excel(url,skiprows=skip_row,converters={'Empid':str})
                    #print(data.head())

        data.dropna(axis = 0, how ='all', inplace = True)  #Remove blank rows with all nun column
        data = data.loc[:, ~data.columns.str.contains('^Unnamed')] #Remove blank unnamed columns

        # avoid_att = TMasterModuleRoleUser.objects.filter((Q(mmr_type=1)|Q(mmr_type=6))&Q(mmr_is_deleted=False)).values_list('mmr_user')
        # print("avoid_att",avoid_att)

        # user_details = TCoreUserDetail.objects.filter((~Q(cu_user__in=TMasterModuleRoleUser.objects.filter(Q(mmr_type=1)|Q(mmr_type=6)|Q(mmr_is_deleted=True)
        #                                                 ).values_list('mmr_user',flat=True))),
        #                                                 (~Q(cu_punch_id__in=['PMSSITE000','#N/A',''])),
        #                                                 (Q(cu_is_deleted=False))).values() ##avoid 'PMSSITE000','#N/A' punch ids
        # print('user_details',len(user_details))
        # user_count = len(user_details) if user_details else 0
        holiday_list = HolidaysList.objects.filter(status=True).values('holiday_date','holiday_name')
        device_details = DeviceMaster.objects.filter(is_exit=True,is_deleted=False).values('id')
        if device_details:
            device_no_list = [x['id'] for x in device_details]
        # print("device_no_list", device_no_list)
        day = data.get('Date')[0]
        # print("dayyy", day)
        # request_checking_flag = 1
        if day:
            today_datetime = datetime.strptime(str(day)+'T'+'12:00:00', "%d/%m/%YT%H:%M:%S")
            print("today_datetime",today_datetime.date())
            date_time_day = today_datetime.date()
            late_convence_limit = today_datetime.replace(hour=20, minute=30)
            # print("late_convence_limit",late_convence_limit)
            '''
                Delete only last Attendance  if these DATE had already in Attendance Date.
            '''
            # lase_attendance = Attendance.objects.filter(date__date=date_time_day).order_by('-id')
            # if lase_attendance:
            #     print('delete_data',lase_attendance[0].__dict__['id'])
            #     AttendanceApprovalRequest.objects.filter(attendance=lase_attendance[0].__dict__['id']).delete()
            #     AttendanceLog.objects.filter(attendance=lase_attendance[0].__dict__['id']).delete()
            #     Attendance.objects.filter(id=lase_attendance[0].__dict__['id']).delete()

            '''
                << Avoid attendance >>
                IF User is Demo_user or Super_user
                IF Punch id is ('PMSSITE000','#N/A','')
                IF User had already Attendance for this day.
            '''
            # punch_id_list = []
            user_details = TCoreUserDetail.objects.filter(~Q(
                    (   
                        Q(cu_user__in=TMasterModuleRoleUser.objects.filter(
                        Q(mmr_type=1)|Q(mmr_type=6)|Q(mmr_is_deleted=True)).values_list('mmr_user',flat=True))
                    )|
                    (Q(cu_punch_id='#N/A'))|
                    (Q(cu_user_id__in=Attendance.objects.filter(date__date=date_time_day).values_list('employee',flat=True)))
                ),
                (
                    Q(
                        Q(termination_date__isnull=False)&Q(
                            Q(
                                Q(termination_date__year=today_datetime.year)&Q(termination_date__month=today_datetime.month)
                            )|
                            Q(termination_date__date__gte=date_time_day)
                        )
                    )|
                    Q(Q(termination_date__isnull=True))
                ),
                (Q(joining_date__date__lte=date_time_day)),cu_is_deleted=False).values() ##avoid 'PMSSITE000','#N/A' punch ids

            # punch_id_list = [x['cu_punch_id'] for x in user_details]

            print('Total_user',len(user_details))
            # print('hdfhoihgfoishgoishgois',TCoreUserDetail.objects.filter(Q(cu_punch_id__in=['PMSSITE000','#N/A'])|
            #                                                             Q(cu_punch_id__exact="")).count())
            user_count = len(user_details) if user_details else 0
            # return Response({'result':{'request_status':user_count,'punch_id_list':punch_id_list,'msg':str(user_details)}})
        else:
            return Response({'result':{'request_status':0,'msg':'Enter proper Excel'}})
        total_month_grace=AttendenceMonthMaster.objects.filter(month_start__date__lte=today_datetime.date(),
                                        month_end__date__gte=today_datetime.date(),is_deleted=False).values('grace_available',
                                                                                 'year_start_date', 'year_end_date', 'month', 
                                                                                 'month_start', 'month_end','grace_available'
                                                                                 )
        # print("total_month_grace",total_month_grace)

        special_day = AttendanceSpecialdayMaster.objects.filter(((Q(day_start_time__date=today_datetime.date())|Q(
            day_end_time__date=today_datetime.date())) & Q(is_deleted=False))).values('day_start_time__time','day_end_time__time','remarks')

        special_full_day = AttendanceSpecialdayMaster.objects.filter(full_day__date=today_datetime.date(),is_deleted=False).values('full_day__date','remarks')
        # holiday = HolidaysList.objects.filter(status=True,holiday_date=date_time_day).values('holiday_name')
        

        # print('holiday',holiday)
        # print("special_full_day",special_full_day)
        # print("special_day",special_day)
        # ##########
        # no_request = False
        # day_remarks = ''
        # if holiday:
        #     # holiday_name = holiday[0]["holiday_name"]
        #     day_remarks = holiday[0]["holiday_name"]
        #     no_request = True
        # elif special_full_day:
        #     # special_full_day_name = special_full_day[0]["full_day__date"]
        #     day_remarks = special_full_day[0]["remarks"]
        #     no_request = True
        # elif date_time_day.weekday()==6:
        #     # print("Sunday")
        #     day_remarks = "Sunday"
        #     no_request = True


        ##########
        for user in user_details:
            user_count = user_count-1
            print("Wait...", user_count)
            att_filter = {}
            req_filter = {}
            pre_att_filter = {}
            pre_req_filter = {}
            late_con_filter = {}
            bench_filter = {}
            saturday_off_list = None
            pre_att = None
            saturday_off = False

            logout_time = None
            check_out = 0
            # adv_leave_type = None
            user_flag = 0
            cu_punch_id = user['cu_punch_id'] if user['cu_punch_id'] else None
            cu_user_id = int(user['cu_user_id'])

            #################
            '''
            Modified By :: Rajesh Samui
            Reason :: State Wise Holiday Calculation
            Description :: Comment out line 725-745 because holiday is now state wise and user dependent.
            Line :: 777-798
            Date :: 10-02-2020
            '''
            # holiday = HolidaysList.objects.filter(status=True,holiday_date=date_time_day).values('holiday_name')
            state_obj = TCoreUserDetail.objects.get(cu_user__id=cu_user_id).job_location_state
            default_state = TCoreState.objects.filter(cs_state_name__iexact='west bengal').first()
            t_core_state_id = state_obj.id if state_obj else default_state.id
            holiday = HolidayStateMapping.objects.filter(Q(holiday__holiday_date=date_time_day)&Q(state__id=t_core_state_id)).values('holiday__holiday_name')

            print('holiday',holiday)
            print("special_full_day",special_full_day)
            print("special_day",special_day)

            # print(state_obj)
            # print(t_core_state_id)
            # print(holiday)

            ##########
            no_request = False
            day_remarks = ''
            if holiday:
                # holiday_name = holiday[0]["holiday_name"]
                day_remarks = holiday[0]["holiday__holiday_name"]
                no_request = True
            elif special_full_day:
                # special_full_day_name = special_full_day[0]["full_day__date"]
                day_remarks = special_full_day[0]["remarks"]
                no_request = True
            elif date_time_day.weekday()==6:
                # print("Sunday")
                day_remarks = "Sunday"
                no_request = True

            #################
            if date_time_day.weekday()==5 and no_request is False:
                saturday_off_list = AttendenceSaturdayOffMaster.objects.filter(employee_id=cu_user_id,is_deleted=False).values(
                    'first', 'second', 'third', 'fourth', 'all_s_day').order_by('-id')

                print("saturday_off_list",date_time_day.weekday(), saturday_off_list)

                if saturday_off_list:
                    if saturday_off_list[0]['all_s_day'] is True:
                        # if user['is_saturday_off'] is True:
                        day_remarks = 'Saturday'
                        saturday_off = True

                    else:
                        week_date = date_time_day.day
                        # print("week_date",  week_date)
                        month_calender = calendar.monthcalendar(date_time_day.year, date_time_day.month)
                        saturday_list = (0,1,2,3) if month_calender[0][calendar.SATURDAY] else (1,2,3,4)

                        if saturday_off_list[0]['first'] is True and int(week_date)==int(month_calender[saturday_list[0]][calendar.SATURDAY]):
                            day_remarks='Saturday'
                            saturday_off = True
                        elif saturday_off_list[0]['second'] is True and int(week_date)==int(month_calender[saturday_list[1]][calendar.SATURDAY]):
                            day_remarks='Saturday'
                            saturday_off = True
                        elif saturday_off_list[0]['third'] is True and int(week_date)==int(month_calender[saturday_list[2]][calendar.SATURDAY]):
                            day_remarks='Saturday'
                            saturday_off = True
                        elif saturday_off_list[0]['fourth'] is True and int(week_date)==int(month_calender[saturday_list[3]][calendar.SATURDAY]):
                            day_remarks='Saturday'
                            saturday_off = True

                    # print("Saturday")

            #################

            ###If user has no login/logout/lunch time >> Then fix their time##
            user['daily_loginTime'] = today_datetime.replace(hour=10, minute=00).time() if user['daily_loginTime'] is None else user['daily_loginTime']
            user['daily_logoutTime'] = today_datetime.replace(hour=19, minute=00).time() if user['daily_logoutTime'] is None else user['daily_logoutTime']
            user['lunch_start'] = today_datetime.replace(hour=13, minute=30).time() if user['lunch_start'] is None else user['lunch_start']
            user['lunch_end'] = today_datetime.replace(hour=14, minute=00).time() if user['lunch_end'] is None else user['lunch_end']
            
            ## If Change Login-Logout time (Special Day) ##
            if special_day:
                daily_loginTime = special_day[0]['day_start_time__time'] if special_day[0]['day_start_time__time'] is not None else user['daily_loginTime']
                # daily_logoutTime = special_day[0]['day_end_time__time'] if special_day[0]['day_end_time__time'] is not None else user['daily_logoutTime']
                daily_logoutTime = special_day[0]['day_end_time__time'] if special_day[0]['day_end_time__time'] is not None and \
                                                                            special_day[0]['day_end_time__time']<user['daily_logoutTime'] else user['daily_logoutTime']
                print("daily_logoutTime",daily_logoutTime)
                pre_att_filter['day_remarks'] = special_day[0]['remarks'] if special_day[0]['remarks'] is not None else ''
            elif today_datetime.weekday()==5:
                daily_loginTime = user['daily_loginTime']
                daily_logoutTime = user['saturday_logout'] if user['saturday_logout'] is not None else user['daily_logoutTime'].replace(hour=16, minute=00)
                pre_att_filter['day_remarks'] = 'Present'

            else:
                daily_loginTime = user['daily_loginTime']
                daily_logoutTime = user['daily_logoutTime']
                pre_att_filter['day_remarks'] = 'Present'
            
            ## LUNCH TIME ##
            lunch_start = datetime.combine(today_datetime,user['lunch_start'])
            lunch_end = datetime.combine(today_datetime,user['lunch_end'])

            ## DAILY LOGIN-LOGOUT ##
            # print("daily_loginTime", daily_loginTime, type(daily_loginTime))
            daily_login = datetime.combine(today_datetime,daily_loginTime)
            daily_logout = datetime.combine(today_datetime,daily_logoutTime)

            is_saturday_off = user['is_saturday_off'] 
            att_filter['employee_id'] = cu_user_id
            grace_over = False

            joining_date = user['joining_date']
            if total_month_grace:
                grace_available = total_month_grace[0]['grace_available'] if total_month_grace[0]['grace_available'] is not None else 0
                print("GRACE", grace_available)
                if joining_date >= total_month_grace[0]['month_start'] and joining_date <= total_month_grace[0]['month_end']:
                    total_grace = JoiningApprovedLeave.objects.filter(employee=cu_user_id,is_deleted=False).values('first_grace')
                    grace_available = total_grace[0]['first_grace'] if total_grace[0]['first_grace'] is not None else 0
                    print("grace_available AAAA", grace_available, cu_user_id)

            availed_grace=AttendanceApprovalRequest.objects.filter(Q(attendance__employee=cu_user_id) &
                                                            Q(duration_start__gte=total_month_grace[0]['month_start']) &
                                                            Q(duration_start__lte=total_month_grace[0]['month_end']) &
                                                            Q(is_requested=True) &
                                                            Q(is_deleted=False)&
                                                            (Q(request_type='GR')|Q(checkin_benchmark=True))
                                                            ).aggregate(Sum('duration'))['duration__sum']
            print('availed_grace',availed_grace)
            availed_grace = availed_grace if availed_grace else 0
            
            # if grace_available<availed_grace: #nur code 
            #     grace_over = True
            for index, row in data.iterrows():
                #print('row',row)
                # lunch_start = datetime.combine(today_datetime,user['lunch_start'])
                date_time = str(row['Date'])+'T'+str(row['Time'])
                date_time_format = datetime.strptime(date_time, "%d/%m/%YT%H:%M:%S")
                #print('cu_punch_id_type',type(cu_punch_id),cu_punch_id)
                #print('rowEmpid',type(row['Empid']),row['Empid'])
                if cu_punch_id == row['Empid']:
                    user_flag = 1
                    ##################### Added By Rupam #######################
                    deviceMasterDetails = DeviceMaster.objects.filter(device_no=int(row['CID']))
                    if deviceMasterDetails:
                        current_device = DeviceMaster.objects.get(device_no=int(row['CID']))
                        # print("current_device",current_device)
                    ##################### END ###################################
                    pre_att_filter['employee_id'] = cu_user_id
                    # pre_att_filter['day_remarks'] = 'Present'
                    pre_att_filter['is_present'] = True
                    pre_att_filter['date'] = date_time_format
                    pre_att_filter['login_time'] = date_time_format
                    # print("pre_att_filter",pre_att_filter)

                    ##First time log in a Day##Successful
                    if pre_att is None:                      
                        if pre_att_filter:
                            pre_att = self.att_create(pre_att_filter)
                            bench_time = daily_login + timedelta(minutes=30)
                            # print('bench_time',bench_time)
                            # if saturday_off is False and no_request is False:

                            ###Check login if After USER Daily login time = Duration### Successful
                            if daily_login<pre_att_filter['login_time'] and saturday_off is False and no_request is False:
                                    bench_filter['attendance']=pre_att
                                    bench_filter['attendance_date'] = daily_login.date()
                                    bench_filter['duration_start']=daily_login
                                    bench_filter['duration_end']=pre_att_filter['login_time']
                                    bench_filter['duration'] = round(((bench_filter['duration_end']-bench_filter['duration_start']).seconds)/60)
                                    bench_filter['punch_id'] = cu_punch_id
                                    if grace_available<availed_grace + float(bench_filter['duration']): #abhisek code 
                                        grace_over = True
                                    if bench_time>pre_att_filter['login_time'] and grace_over is False:
                                        bench_filter['checkin_benchmark']=True
                                        bench_filter['is_requested']=True
                                        # bench_filter['is_requested']=True
                                        # bench_filter['request_type']='GR'
                                    else:
                                        bench_filter['checkin_benchmark']=False

                                    if bench_filter['duration']>0:
                                        bench_req = self.request_create(bench_filter)

                    ##After Daily Attendance## Successful
                    if pre_att:
                        att_log_create, create1 = AttendanceLog.objects.get_or_create(
                            attendance=pre_att,
                            employee_id=cu_user_id,
                            time=date_time_format,
                            device_no=current_device
                        )

                        logout_time = date_time_format
                        duration_count = 0
                        if saturday_off is False and no_request is False:
                            if check_out == 0 and current_device.__dict__['id'] in device_no_list and date_time_format<daily_logout:
                                # print("if current_device in device_no_list:")
                                check_out = 1
                                pre_req_filter['attendance'] = pre_att
                                pre_req_filter['punch_id'] = cu_punch_id
                                pre_req_filter['duration_start'] = date_time_format
                            elif check_out == 1 and current_device not in device_no_list and date_time_format<daily_login:
                                check_out = 0
                                pre_req_filter = {}
                            elif check_out == 1 and current_device not in device_no_list and date_time_format>daily_login:
                                check_out = 0
                                if date_time_format>daily_logout:
                                    pre_req_filter['duration_end'] = daily_logout
                                else:
                                    pre_req_filter['duration_end'] = date_time_format

                                if pre_req_filter['duration_start']<daily_login:
                                    pre_req_filter['duration_start'] = daily_login
                                # else:
                                #     pre_req_filter['duration_end'] = date_time_format

                                # if bench_time>pre_req_filter['duration_end'] and grace_over is False:
                                #     pre_req_filter['checkin_benchmark']=True
                                #     pre_req_filter['is_requested']=True


                                if lunch_end < pre_req_filter['duration_start']:
                                    duration_count = round(((pre_req_filter['duration_end']-pre_req_filter['duration_start']).seconds)/60)
                                elif lunch_start > pre_req_filter['duration_end']:
                                    duration_count = round(((pre_req_filter['duration_end']-pre_req_filter['duration_start']).seconds)/60)
                                elif lunch_start > pre_req_filter['duration_start'] and lunch_end < pre_req_filter['duration_end']:
                                    duration_count = round(((lunch_start - pre_req_filter['duration_start'] + pre_req_filter['duration_end'] - lunch_end).seconds)/60)
                                elif lunch_start > pre_req_filter['duration_start'] and lunch_end > pre_req_filter['duration_end']:
                                    duration_count = round(((lunch_start - pre_req_filter['duration_start']).seconds)/60)
                                elif lunch_end < pre_req_filter['duration_end'] and lunch_start < pre_req_filter['duration_start']:
                                    duration_count = round(duration_count + ((pre_req_filter['duration_end']-lunch_end).seconds)/60)

                                # print("duration_count",duration_count, pre_req_filter)
                                if duration_count>0:
                                    pre_req_filter['duration']=duration_count
                                    pre_req_filter['attendance_date'] = pre_req_filter['duration_start'].date()
                                    pre_req = self.request_create(pre_req_filter)
                                    pre_req_filter = {}
                                    #print("pre_req",pre_req)


            if logout_time and pre_att:
                # print('pre_att',pre_att.id)
                pre_att_update = Attendance.objects.filter(pk=pre_att.id).update(logout_time=logout_time)
                if saturday_off is False and no_request is False:
                    ### IF Late convence ### Successful Testing
                    if daily_logoutTime < logout_time.time():
                        late_con_filter['attendance'] = pre_att
                        late_con_filter['punch_id'] = cu_punch_id
                        late_con_filter['attendance_date']=daily_logout.date()
                        late_con_filter['duration_start']=daily_logout
                        late_con_filter['duration_end']=logout_time
                        late_con_filter['duration'] = round(((late_con_filter['duration_end']-late_con_filter['duration_start']).seconds)/60)
                        late_con_filter['is_late_conveyance']=True
                        # if late_con_filter['duration']>10: #If late conveyance grater then 10 Minutes.
                        '''
                            As per requirement and discussion with Tonmay Da(10.12.2019):
                            LATE CONVENCE always count after 08:30 PM 
                        '''
                        if late_convence_limit>=late_con_filter['duration_start'] and late_convence_limit<late_con_filter['duration_end']\
                            and late_con_filter['duration']>0:
                            # print("late_con_filter",late_con_filter)
                            late_req = self.request_create(late_con_filter)
                            # print("late_req",late_req)
                    
                    ###If Logout less then User's Daily log out### Successful Testing
                    elif daily_logoutTime > logout_time.time():
                        late_con_filter['attendance']=pre_att
                        late_con_filter['punch_id'] = cu_punch_id
                        late_con_filter['attendance_date']=daily_logout.date()
                        late_con_filter['duration_start']=logout_time
                        late_con_filter['duration_end']=daily_logout
                        late_con_filter['duration'] = round(((late_con_filter['duration_end']-late_con_filter['duration_start']).seconds)/60)
                        late_con_filter['is_late_conveyance']=False
                        # late_con_filter['request_type']='GR'
                        if late_con_filter['duration']>0:
                            # print("late_con_filter",late_con_filter)
                            late_req = self.request_create(late_con_filter)
                            # print("late_req",late_req)

        ## IF User Absent ###
            if user_flag==0:
                # print("ABSENT")
                is_required = False
                # print("user",cu_user_id)
                adv_leave_type = None
                leave = EmployeeAdvanceLeaves.objects.filter(
                    Q(start_date__date__lte=date_time_day)&Q(end_date__date__gte=date_time_day)&Q(employee_id=cu_user_id)&  #changes by abhisek 21/11/19
                    (Q(approved_status='pending')|Q(approved_status='approved'))).values('leave_type','reason')
                # print("leave",leave)
                # holiday = HolidaysList.objects.filter(status=True,holiday_date=date_time_day).values('holiday_name')

                if leave:
                    adv_leave_type = leave[0]['leave_type']
                    # print("leave_type",leave[0]['leave_type'])
                    att_filter['day_remarks']=leave[0]['leave_type']
                    is_required = True
                elif saturday_off is True or no_request is True:
                    att_filter['day_remarks'] = day_remarks
                    print("att_filter",att_filter, saturday_off, no_request)
                else:
                    is_required = True
                    att_filter['day_remarks']="Not Present"

                if att_filter:
                    date = date_time[0:10]+'T'+str(daily_loginTime)
                    date_time_date =datetime.strptime(date, "%d/%m/%YT%H:%M:%S")
                    #print("date_time_format",date_time_date)
                    att_filter['date'] = date_time_date
                    #print("att_filter",att_filter)

                    abs_att = self.att_create(att_filter)
                    # print("att_filter",abs_att, is_required)
                    if is_required is True:
                        req_filter['attendance']= abs_att
                        req_filter['attendance_date'] = daily_login.date()
                        req_filter['duration_start'] = daily_login
                        req_filter['duration_end'] = daily_logout
                        req_filter['duration'] = round(((req_filter['duration_end']-req_filter['duration_start']).seconds)/60)

                        if adv_leave_type:
                            req_filter['request_type']='FD'
                            req_filter['leave_type'] = adv_leave_type
                            req_filter['approved_status'] = 'approved'
                            req_filter['is_requested'] = True
                            req_filter['justification'] = leave[0]['reason']

                        if req_filter:
                            # print("req_filter,",req_filter)
                            req_filter['punch_id'] = cu_punch_id
                            abs_req = self.request_create(req_filter)
                            # print("abs_req",abs_req, req_filter)


        return Response({'result':{'request_status':1,'msg':'Successful'}})


#:::::::::::::::::: DOCUMENTS UPLOAD MODIFICATION::::::::::::::::::::::::#
class AttendanceFileUpload(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = AttandancePerDayDocuments.objects.filter(is_deleted=False)
    serializer_class = AttendanceFileUploadSerializer
    parser_classes = (MultiPartParser,)
    

    def att_create(self, filter: dict):
        logdin_user_id = self.request.user.id
        attendance,create1 = Attendance.objects.get_or_create(created_by_id=logdin_user_id,owned_by_id=logdin_user_id,**filter)
        return attendance
    def request_create(self, filter: dict):
        logdin_user_id = self.request.user.id  #attendance_date
        request,create2 = AttendanceApprovalRequest.objects.get_or_create(created_by_id=logdin_user_id,owned_by_id=logdin_user_id,**filter)
        return request

    def post(self, request, *args, **kwargs):
        response = super().post(request,*args,**kwargs)
        # print("response",response.data['document'])
        print("Please wait...")
        print("processing...")
        #########################################################################################
        '''
            Always enter a .xlsx file.
            This code avoid Unnamed rows.
            File must have 
        '''
        if request.is_secure():
            protocol = 'https://'
        else:
            protocol = 'http://'

        host_url = getHostWithPort(request)
        print('host_url',host_url)
        url = response.data['document'].replace(host_url,'./')
        # print("url", url)
        try:
            wb = xlrd.open_workbook(url)
        except xlrd.biffh.XLRDError:
            print("XLRDError occure")
        if wb:
            sh = wb.sheet_by_index(0)
        else:
            print("exit")
            exit()

        '''
        Skip the first few rows and read the excel after this rows in pandas
        '''
        a=[]
        for i in range(sh.nrows):
            for j in range(sh.ncols):
                if sh.cell_value(i,j) == 'Date' and sh.cell_value(i,j+1) == 'Time':
                    skip_row=i
                    for i in range(0,skip_row):
                        a.append(i)
                    data = pd.read_excel(url,skiprows=skip_row,converters={'Empid':str})
                    #print(data.head())

        data.dropna(axis = 0, how ='all', inplace = True)  #Remove blank rows with all nun column
        data = data.loc[:, ~data.columns.str.contains('^Unnamed')] #Remove blank unnamed columns
        #############################################################################################
        '''
            Exit device list & device_id in list form
        '''
        device_details = DeviceMaster.objects.filter(is_exit=True,is_deleted=False).values('id')
        if device_details:
            device_no_list = [x['id'] for x in device_details]
        # print("device_no_list", device_no_list)
        ##############################################################################################
        day = data.get('Date')[0]
        # print("dayyy", day)
        if day:
            today_datetime = datetime.strptime(str(day)+'T'+'12:00:00', "%d/%m/%YT%H:%M:%S")
            print("today_datetime",today_datetime)
            date_time_day = today_datetime.date()
            late_convence_limit = today_datetime.replace(hour=20, minute=30)
            # print("late_convence_limit",late_convence_limit)
            '''
                Delete only last Attendance  if these DATE had already in Attendance Date.
            '''
            lase_attendance = Attendance.objects.filter(date__date=date_time_day).order_by('-id')
            if lase_attendance:
                print('delete_data',lase_attendance[0].__dict__['id'])
                AttendanceApprovalRequest.objects.filter(attendance=lase_attendance[0].__dict__['id']).delete()
                AttendanceLog.objects.filter(attendance=lase_attendance[0].__dict__['id']).delete()
                Attendance.objects.filter(id=lase_attendance[0].__dict__['id']).delete()

            '''
                << Avoid attendance >>
                IF User is Demo_user or Super_user
                IF Punch id is ('PMSSITE000','#N/A','')
                IF User had already Attendance for this day.
            '''
            # logic??? what is the filter logic for except avoid attendence?
            '''
                1. Check If the user is terminated and termination date entered before termination date. 
                2. Check if the user joining date is less than entered date.
            '''
            user_details = TCoreUserDetail.objects.filter(~Q(
                    (   
                        Q(cu_user__in=TMasterModuleRoleUser.objects.filter(
                        Q(mmr_type=1)|Q(mmr_type=6)|Q(mmr_is_deleted=True)).values_list('mmr_user',flat=True))
                    )|
                    (Q(cu_punch_id='#N/A'))|
                    (Q(cu_user_id__in=Attendance.objects.filter(date__date=date_time_day).values_list('employee',flat=True)))
                ),
                (
                    Q(
                        Q(termination_date__isnull=False)&Q(
                            Q(
                                Q(termination_date__year=today_datetime.year)&Q(termination_date__month=today_datetime.month)
                            )|
                            Q(termination_date__date__gte=date_time_day)
                        )
                    )|
                    Q(Q(termination_date__isnull=True))
                ),
                (Q(joining_date__date__lte=date_time_day)),cu_is_deleted=False).values() ##avoid 'PMSSITE000','#N/A' punch ids

            print('Total_user',len(user_details))
            time.sleep(10) # logic??? Wait to check the user_count.
            user_count = len(user_details) if user_details else 0
            #user_check_list = [x['cu_user_id']  for x in user_details]

            #return Response({'result':{'request_status':user_check_list,'msg':str(user_details)}})
        else:
            return Response({'result':{'request_status':0,'msg':'Enter proper Excel'}})

        # logic??? What is the significance of AttendenceMonthMaster model and what is the logic of filtering? why lte and gte?
        '''
        Get the current month of AttendenceMonthMaster record.
        '''
        total_month_grace=AttendenceMonthMaster.objects.filter(month_start__date__lte=today_datetime.date(),
                                        month_end__date__gte=today_datetime.date(),is_deleted=False).values('grace_available',
                                                                                 'year_start_date', 'year_end_date', 'month', 
                                                                                 'month_start', 'month_end','grace_available'
                                                                                 )
        # print("total_month_grace",total_month_grace)

        # logic??? What is the significance of AttendanceSpecialdayMaster model and what is the logic of filtering?
        '''
        filtering the AttendanceSpecialdayMaster based on start time and end time and fullday if declare spacial day.
        '''
        special_day = AttendanceSpecialdayMaster.objects.filter(((Q(day_start_time__date=today_datetime.date())|Q(
            day_end_time__date=today_datetime.date())) & Q(is_deleted=False))).values('day_start_time__time','day_end_time__time','remarks')

        special_full_day = AttendanceSpecialdayMaster.objects.filter(full_day__date=today_datetime.date(),is_deleted=False).values('full_day__date','remarks')
        # holiday = HolidaysList.objects.filter(status=True,holiday_date=date_time_day).values('holiday_name')

        # print('holiday',holiday)
        # print("special_full_day",special_full_day)
        # print("special_day",special_day)
        # ##########
        # no_request = False
        # day_remarks = ''
        # if holiday:
        #     # holiday_name = holiday[0]["holiday_name"]
        #     day_remarks = holiday[0]["holiday_name"]
        #     no_request = True
        # elif special_full_day:
        #     # special_full_day_name = special_full_day[0]["full_day__date"]
        #     day_remarks = special_full_day[0]["remarks"]
        #     no_request = True
        # elif date_time_day.weekday()==6:
        #     # print("Sunday")
        #     day_remarks = "Sunday"
        #     no_request = True


        ##########
        for user in user_details:
            user_count = user_count-1
            print("Wait...", user_count)
            att_filter = {}
            req_filter = {}
            pre_att_filter = {}
            pre_req_filter = {}
            late_con_filter = {}
            bench_filter = {}
            saturday_off_list = None
            pre_att = None
            saturday_off = False

            logout_time = None
            check_out = 0
            # adv_leave_type = None
            user_flag = 0
            cu_punch_id = user['cu_punch_id'] if user['cu_punch_id'] else None
            cu_user_id = int(user['cu_user_id'])

            #################
            '''
            Modified By :: Rajesh Samui
            Reason :: State Wise Holiday Calculation
            Description :: Comment out line 1238-1257 because holiday is now state wise and user dependent.
            Line :: 1289-1318
            Date :: 10-02-2020
            '''
            #holiday = HolidaysList.objects.filter(status=True,holiday_date=date_time_day).values('holiday_name')
            state_obj = TCoreUserDetail.objects.get(cu_user__id=cu_user_id).job_location_state
            default_state = TCoreState.objects.filter(cs_state_name__iexact='west bengal').first()
            t_core_state_id = state_obj.id if state_obj else default_state.id
            holiday = HolidayStateMapping.objects.filter(Q(holiday__holiday_date=date_time_day)&Q(state__id=t_core_state_id)).values('holiday__holiday_name')


            print('holiday',holiday)
            print("special_full_day",special_full_day)
            print("special_day",special_day)

            # print(state_obj)
            # print(t_core_state_id)
            # print(holiday)

            ##########
            no_request = False
            day_remarks = ''
            if holiday:
                # holiday_name = holiday[0]["holiday_name"]
                day_remarks = holiday[0]["holiday__holiday_name"]
                no_request = True
            elif special_full_day:
                # special_full_day_name = special_full_day[0]["full_day__date"]
                day_remarks = special_full_day[0]["remarks"]
                no_request = True
            elif date_time_day.weekday()==6:
                # print("Sunday")
                day_remarks = "Sunday"
                no_request = True

            #################
            if date_time_day.weekday()==5 and no_request is False:
                ## logic??? difference between AttendenceSaturdayOffMaster? meaning of all_s_day?
                '''
                    filtering the AttendenceSaturdayOffMaster to get the off saturday.
                    all_s_day :: All Saturday off
                '''
                saturday_off_list = AttendenceSaturdayOffMaster.objects.filter(employee_id=cu_user_id,is_deleted=False).values(
                    'first', 'second', 'third', 'fourth', 'all_s_day').order_by('-id')

                print("saturday_off_list",date_time_day.weekday(), saturday_off_list)

                if saturday_off_list:
                    if saturday_off_list[0]['all_s_day'] is True:
                        # if user['is_saturday_off'] is True:
                        day_remarks = 'Saturday'
                        saturday_off = True

                    else:
                        week_date = date_time_day.day
                        # print("week_date",  week_date)
                        month_calender = calendar.monthcalendar(date_time_day.year, date_time_day.month)
                        saturday_list = (0,1,2,3) if month_calender[0][calendar.SATURDAY] else (1,2,3,4)

                        if saturday_off_list[0]['first'] is True and int(week_date)==int(month_calender[saturday_list[0]][calendar.SATURDAY]):
                            day_remarks='Saturday'
                            saturday_off = True
                        elif saturday_off_list[0]['second'] is True and int(week_date)==int(month_calender[saturday_list[1]][calendar.SATURDAY]):
                            day_remarks='Saturday'
                            saturday_off = True
                        elif saturday_off_list[0]['third'] is True and int(week_date)==int(month_calender[saturday_list[2]][calendar.SATURDAY]):
                            day_remarks='Saturday'
                            saturday_off = True
                        elif saturday_off_list[0]['fourth'] is True and int(week_date)==int(month_calender[saturday_list[3]][calendar.SATURDAY]):
                            day_remarks='Saturday'
                            saturday_off = True

                    # print("Saturday")

            #################

            ###If user has no login/logout/lunch time >> Then fix their time##
            user['daily_loginTime'] = today_datetime.replace(hour=10, minute=00).time() if user['daily_loginTime'] is None else user['daily_loginTime']
            user['daily_logoutTime'] = today_datetime.replace(hour=19, minute=00).time() if user['daily_logoutTime'] is None else user['daily_logoutTime']
            user['lunch_start'] = today_datetime.replace(hour=13, minute=30).time() if user['lunch_start'] is None else user['lunch_start']
            user['lunch_end'] = today_datetime.replace(hour=14, minute=00).time() if user['lunch_end'] is None else user['lunch_end']
            
            ## If Change Login-Logout time (Special Day) ##
            if special_day:
                daily_loginTime = special_day[0]['day_start_time__time'] if special_day[0]['day_start_time__time'] is not None else user['daily_loginTime']
                # daily_logoutTime = special_day[0]['day_end_time__time'] if special_day[0]['day_end_time__time'] is not None else user['daily_logoutTime']
                daily_logoutTime = special_day[0]['day_end_time__time'] if special_day[0]['day_end_time__time'] is not None and \
                                                                            special_day[0]['day_end_time__time']<user['daily_logoutTime'] else user['daily_logoutTime']
                print("daily_logoutTime",daily_logoutTime)
                pre_att_filter['day_remarks'] = special_day[0]['remarks'] if special_day[0]['remarks'] is not None else ''
            elif today_datetime.weekday()==5:
                daily_loginTime = user['daily_loginTime']
                daily_logoutTime = user['saturday_logout'] if user['saturday_logout'] is not None else user['daily_logoutTime'].replace(hour=16, minute=00)
                pre_att_filter['day_remarks'] = 'Present'

            else:
                daily_loginTime = user['daily_loginTime']
                daily_logoutTime = user['daily_logoutTime']
                pre_att_filter['day_remarks'] = 'Present'
            
            ## LUNCH TIME ##
            lunch_start = datetime.combine(today_datetime,user['lunch_start'])
            lunch_end = datetime.combine(today_datetime,user['lunch_end'])

            ## DAILY LOGIN-LOGOUT ##
            # print("daily_loginTime", daily_loginTime, type(daily_loginTime))
            daily_login = datetime.combine(today_datetime,daily_loginTime)
            daily_logout = datetime.combine(today_datetime,daily_logoutTime)

            is_saturday_off = user['is_saturday_off'] 
            att_filter['employee_id'] = cu_user_id
            grace_over = False

            joining_date = user['joining_date']
            if total_month_grace:
                grace_available = total_month_grace[0]['grace_available'] if total_month_grace[0]['grace_available'] is not None else 0
                print("GRACE", grace_available)
                if joining_date >= total_month_grace[0]['month_start'] and joining_date <= total_month_grace[0]['month_end']:
                    total_grace = JoiningApprovedLeave.objects.filter(employee=cu_user_id,is_deleted=False).values('first_grace')
                    grace_available = total_grace[0]['first_grace'] if total_grace[0]['first_grace'] is not None else 0
                    print("grace_available AAAA", grace_available, cu_user_id)

            availed_grace=AttendanceApprovalRequest.objects.filter(Q(attendance__employee=cu_user_id) &
                                                            Q(duration_start__gte=total_month_grace[0]['month_start']) &
                                                            Q(duration_start__lte=total_month_grace[0]['month_end']) &
                                                            Q(is_requested=True) &
                                                            Q(is_deleted=False)&
                                                            (Q(request_type='GR')|Q(checkin_benchmark=True))
                                                            ).aggregate(Sum('duration'))['duration__sum']
            print('availed_grace',availed_grace)
            availed_grace = availed_grace if availed_grace else 0
            
            # if grace_available<availed_grace: #nur code 
            #     grace_over = True
            for index, row in data.iterrows():
                #print('row',row)
                # lunch_start = datetime.combine(today_datetime,user['lunch_start'])
                date_time = str(row['Date'])+'T'+str(row['Time'])
                date_time_format = datetime.strptime(date_time, "%d/%m/%YT%H:%M:%S")
                #print('cu_punch_id_type',type(cu_punch_id),cu_punch_id)
                #print('rowEmpid',type(row['Empid']),row['Empid'])
                if cu_punch_id == row['Empid']:
                    user_flag = 1
                    ##################### Added By Rupam #######################
                    deviceMasterDetails = DeviceMaster.objects.filter(device_no=int(row['CID']))
                    if deviceMasterDetails:
                        current_device = DeviceMaster.objects.get(device_no=int(row['CID']))
                        # print("current_device",current_device)
                    ##################### END ###################################
                    pre_att_filter['employee_id'] = cu_user_id
                    # pre_att_filter['day_remarks'] = 'Present'
                    pre_att_filter['is_present'] = True
                    pre_att_filter['date'] = date_time_format
                    pre_att_filter['login_time'] = date_time_format
                    # print("pre_att_filter",pre_att_filter)

                    ##First time log in a Day##Successful
                    if pre_att is None:                      
                        if pre_att_filter:
                            pre_att = self.att_create(pre_att_filter)
                            bench_time = daily_login + timedelta(minutes=30)
                            # print('bench_time',bench_time)
                            # if saturday_off is False and no_request is False:

                            ###Check login if After USER Daily login time = Duration### Successful
                            if daily_login<pre_att_filter['login_time'] and saturday_off is False and no_request is False:
                                    bench_filter['attendance']=pre_att
                                    bench_filter['attendance_date'] = daily_login.date()
                                    bench_filter['duration_start']=daily_login
                                    bench_filter['duration_end']=pre_att_filter['login_time']
                                    bench_filter['duration'] = round(((bench_filter['duration_end']-bench_filter['duration_start']).seconds)/60)
                                    bench_filter['punch_id'] = cu_punch_id
                                    if grace_available<availed_grace + float(bench_filter['duration']): #abhisek code 
                                        grace_over = True
                                    if bench_time>pre_att_filter['login_time'] and grace_over is False:
                                        bench_filter['checkin_benchmark']=True
                                        bench_filter['is_requested']=True
                                        # bench_filter['is_requested']=True
                                        # bench_filter['request_type']='GR'
                                    else:
                                        bench_filter['checkin_benchmark']=False

                                    if bench_filter['duration']>0:
                                        bench_req = self.request_create(bench_filter)

                    ##After Daily Attendance## Successful
                    if pre_att:
                        att_log_create, create1 = AttendanceLog.objects.get_or_create(
                            attendance=pre_att,
                            employee_id=cu_user_id,
                            time=date_time_format,
                            device_no=current_device
                        )

                        logout_time = date_time_format
                        duration_count = 0
                        # logic??? What is check_out? Explain 3 conditions.
                        '''

                            1. 1st time checkout for exist device.
                            2. If date_time_format is less than daily_login.
                            3. between login and logout
                        '''
                        if saturday_off is False and no_request is False:
                            if check_out == 0 and current_device.__dict__['id'] in device_no_list and date_time_format<daily_logout:
                                # print("if current_device in device_no_list:")
                                check_out = 1
                                pre_req_filter['attendance'] = pre_att
                                pre_req_filter['punch_id'] = cu_punch_id
                                pre_req_filter['duration_start'] = date_time_format
                            elif check_out == 1 and current_device not in device_no_list and date_time_format<daily_login:
                                check_out = 0
                                pre_req_filter = {}
                            elif check_out == 1 and current_device not in device_no_list and date_time_format>daily_login:
                                check_out = 0
                                if date_time_format>daily_logout:
                                    pre_req_filter['duration_end'] = daily_logout
                                else:
                                    pre_req_filter['duration_end'] = date_time_format

                                if pre_req_filter['duration_start']<daily_login:
                                    pre_req_filter['duration_start'] = daily_login
                                # else:
                                #     pre_req_filter['duration_end'] = date_time_format

                                # if bench_time>pre_req_filter['duration_end'] and grace_over is False:
                                #     pre_req_filter['checkin_benchmark']=True
                                #     pre_req_filter['is_requested']=True

                                '''
                                    Deviation duration calculation.
                                '''
                                if lunch_end < pre_req_filter['duration_start']:
                                    duration_count = round(((pre_req_filter['duration_end']-pre_req_filter['duration_start']).seconds)/60)
                                elif lunch_start > pre_req_filter['duration_end']:
                                    duration_count = round(((pre_req_filter['duration_end']-pre_req_filter['duration_start']).seconds)/60)
                                elif lunch_start > pre_req_filter['duration_start'] and lunch_end < pre_req_filter['duration_end']:
                                    duration_count = round(((lunch_start - pre_req_filter['duration_start'] + pre_req_filter['duration_end'] - lunch_end).seconds)/60)
                                elif lunch_start > pre_req_filter['duration_start'] and lunch_end > pre_req_filter['duration_end']:
                                    duration_count = round(((lunch_start - pre_req_filter['duration_start']).seconds)/60)
                                elif lunch_end < pre_req_filter['duration_end'] and lunch_start < pre_req_filter['duration_start']:
                                    duration_count = round(duration_count + ((pre_req_filter['duration_end']-lunch_end).seconds)/60)

                                # print("duration_count",duration_count, pre_req_filter)
                                if duration_count>0:
                                    pre_req_filter['duration']=duration_count
                                    pre_req_filter['attendance_date'] = pre_req_filter['duration_start'].date()
                                    pre_req = self.request_create(pre_req_filter)
                                    pre_req_filter = {}
                                    #print("pre_req",pre_req)
            '''
                To calculate if user can apply for late convence and create approval request based on that.
            '''
            if logout_time and pre_att:
                # print('pre_att',pre_att.id)
                pre_att_update = Attendance.objects.filter(pk=pre_att.id).update(logout_time=logout_time)
                if saturday_off is False and no_request is False:
                    ### IF Late convence ### Successful Testing
                    if daily_logoutTime < logout_time.time():
                        late_con_filter['attendance'] = pre_att
                        late_con_filter['punch_id'] = cu_punch_id
                        late_con_filter['attendance_date']=daily_logout.date()
                        late_con_filter['duration_start']=daily_logout
                        late_con_filter['duration_end']=logout_time
                        late_con_filter['duration'] = round(((late_con_filter['duration_end']-late_con_filter['duration_start']).seconds)/60)
                        late_con_filter['is_late_conveyance']=True
                        # if late_con_filter['duration']>10: #If late conveyance grater then 10 Minutes.
                        '''
                            As per requirement and discussion with Tonmay Da(10.12.2019):
                            LATE CONVENCE always count after 08:30 PM 
                        '''
                        if late_convence_limit>=late_con_filter['duration_start'] and late_convence_limit<late_con_filter['duration_end']\
                            and late_con_filter['duration']>0:
                            # print("late_con_filter",late_con_filter)
                            late_req = self.request_create(late_con_filter)
                            # print("late_req",late_req)
                    
                    ###If Logout less then User's Daily log out### Successful Testing
                    elif daily_logoutTime > logout_time.time():
                        late_con_filter['attendance']=pre_att
                        late_con_filter['punch_id'] = cu_punch_id
                        late_con_filter['attendance_date']=daily_logout.date()
                        late_con_filter['duration_start']=logout_time
                        late_con_filter['duration_end']=daily_logout
                        late_con_filter['duration'] = round(((late_con_filter['duration_end']-late_con_filter['duration_start']).seconds)/60)
                        late_con_filter['is_late_conveyance']=False
                        # late_con_filter['request_type']='GR'
                        if late_con_filter['duration']>0:
                            # print("late_con_filter",late_con_filter)
                            late_req = self.request_create(late_con_filter)
                            # print("late_req",late_req)

        ## IF User Absent ###
            if user_flag==0:
                # print("ABSENT")
                is_required = False
                # print("user",cu_user_id)
                adv_leave_type = None
                leave = EmployeeAdvanceLeaves.objects.filter(
                    Q(start_date__date__lte=date_time_day)&Q(end_date__date__gte=date_time_day)&Q(employee_id=cu_user_id)&  #changes by abhisek 21/11/19
                    (Q(approved_status='pending')|Q(approved_status='approved'))).values('leave_type','reason')
                # print("leave",leave)
                # holiday = HolidaysList.objects.filter(status=True,holiday_date=date_time_day).values('holiday_name')

                if leave:
                    adv_leave_type = leave[0]['leave_type']
                    # print("leave_type",leave[0]['leave_type'])
                    att_filter['day_remarks']=leave[0]['leave_type']
                    is_required = True
                elif saturday_off is True or no_request is True:
                    att_filter['day_remarks'] = day_remarks
                    print("att_filter",att_filter, saturday_off, no_request)
                else:
                    is_required = True
                    att_filter['day_remarks']="Not Present"

                if att_filter:
                    date = date_time[0:10]+'T'+str(daily_loginTime)
                    date_time_date =datetime.strptime(date, "%d/%m/%YT%H:%M:%S")
                    #print("date_time_format",date_time_date)
                    att_filter['date'] = date_time_date
                    #print("att_filter",att_filter)

                    abs_att = self.att_create(att_filter)
                    print("att_filter",abs_att, is_required)
                    if is_required is True:
                        req_filter['attendance']= abs_att
                        req_filter['attendance_date'] = daily_login.date()
                        req_filter['duration_start'] = daily_login
                        req_filter['duration_end'] = daily_logout
                        req_filter['duration'] = round(((req_filter['duration_end']-req_filter['duration_start']).seconds)/60)

                        if adv_leave_type:
                            req_filter['request_type']='FD'
                            req_filter['leave_type'] = adv_leave_type
                            req_filter['approved_status'] = 'approved'
                            req_filter['is_requested'] = True
                            req_filter['justification'] = leave[0]['reason']

                        if req_filter:
                            print("req_filter,",req_filter)
                            req_filter['punch_id'] = cu_punch_id
                            abs_req = self.request_create(req_filter)
                            # abs_check = self.absent_checking(req_filter)
                            # print("abs_req",abs_req, req_filter)


        return Response({'result':{'request_status':1,'msg':'Successful'}})

#########

class AttendencePerDayDocumentAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = AttandancePerDayDocuments.objects.filter(is_deleted=False)
    serializer_class = AttendencePerDayDocumentAddSerializer

# class AttendenceJoiningApprovedLeaveAddView(generics.ListCreateAPIView):
#     permission_classes = [IsAuthenticated]
#     authentication_classes = [TokenAuthentication]
#     queryset = JoiningApprovedLeave.objects.filter(is_deleted=False)
#     serializer_class = AttendenceJoiningApprovedLeaveAddSerializer

#     @response_modify_decorator_get
#     def get(self, request, *args, **kwargs):
#         return response

class AttendanceGraceLeaveListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = AttendanceApprovalRequest.objects.filter(is_deleted=False)
    serializer_class = AttendanceGraceLeaveListSerializer

    def get(self, request, *args, **kwargs):
        response=super(AttendanceGraceLeaveListView,self).get(self, request, args, kwargs)
        date =self.request.query_params.get('date', None)
        print('date',type(date))
        date_object = datetime.strptime(date, '%Y-%m-%d').date()
        print('date_object',date_object)
        employee_id=self.request.query_params.get('employee_id', None)
        total_grace={}
        data_dict = {}
        is_previous=self.request.query_params.get('is_previous', None)

        aa = datetime.now()

        total_month_grace=AttendenceMonthMaster.objects.filter(month_start__date__lte=date_object,
                                        month_end__date__gte=date_object,is_deleted=False).values('grace_available',
                                                                                 'year_start_date',
                                                                                 'year_end_date',
                                                                                 'month',
                                                                                 'month_start',
                                                                                 'month_end')
        if is_previous == "true":
            print('sada',type(total_month_grace[0]['month_start']))
            date_object= total_month_grace[0]['month_start'].date()- timedelta(days=1)  
            total_month_grace=AttendenceMonthMaster.objects.filter(month_start__date__lte=date_object,
                                        month_end__date__gte=date_object,is_deleted=False).values('grace_available',
                                                                                 'year_start_date',
                                                                                 'year_end_date',
                                                                                 'month',
                                                                                 'month_start',
                                                                                 'month_end')
                                                                                
        print('total_month_grace',total_month_grace)
        total_grace['month_start']=total_month_grace[0]['month_start']
        total_grace['month_end']=total_month_grace[0]['month_end']
        total_grace['year_start']=total_month_grace[0]['year_start_date']
        total_grace['year_end']=total_month_grace[0]['year_end_date']
        print("total_month_grace",total_grace)

        if total_month_grace:
            total_grace['total_month_grace']=total_month_grace[0]['grace_available'] if total_month_grace[0]['grace_available'] else None

        # for data in response.data:
        availed_grace=AttendanceApprovalRequest.objects.filter(Q(attendance__employee=employee_id) &
                                                            Q(duration_start__gte=total_month_grace[0]['month_start']) &
                                                            Q(duration_start__lte=total_month_grace[0]['month_end']) &
                                                            Q(is_requested=True) &
                                                            Q(is_deleted=False)&
                                                            (Q(request_type='GR')|Q(checkin_benchmark=True))
                                                            ).aggregate(Sum('duration'))['duration__sum']

        total_grace['availed_grace']=availed_grace if availed_grace else 0
        total_grace['grace_balance']=total_month_grace[0]['grace_available'] - total_grace['availed_grace']

        advance_leave=EmployeeAdvanceLeaves.objects.filter(Q(employee=employee_id)&
                                                           Q(is_deleted=False)&
                                                           (Q(approved_status='pending')|Q(approved_status='approved'))
                                                          ).values('leave_type','start_date','end_date')
        print('advance_leave',advance_leave)     
        advance_cl=0
        advance_el=0
        advance_ab=0
        day=0
        if advance_leave:
            for leave in advance_leave:
                print('leave',leave)
                start_date=leave['start_date'].date()
                end_date=leave['end_date'].date()+timedelta(days=1)
                print('start_date,end_date',start_date,end_date)
                if date_object < end_date:
                    if date_object < start_date:
                        day=(end_date-start_date).days 
                        print('day',day)
                    elif date_object > start_date:
                        day=(end_date-date_object).days
                        print('day2',day)
                    else:
                        day=(end_date-date_object).days

                if leave['leave_type']=='CL':
                    advance_cl+=day
                elif leave['leave_type']=='EL':
                    advance_el+=day
                elif leave['leave_type']=='AB':
                    advance_ab+=day
              
            print('advance_el',advance_el)
            print('advance_cl',advance_cl)

        print("datetime_start", datetime.now()-aa)

        leave_attendence_id_data=[]
        availed_leave=[]
        availed_data=AttendanceApprovalRequest.objects.\
            filter((Q(request_type='HD')|Q(request_type='FD')),(Q(approved_status='pending')|Q(approved_status='approved')),attendance__employee=employee_id,
            is_requested=True,is_deleted=False).values('request_type','leave_type',
            'leave_type_changed_period','leave_type_changed','attendance')

        for x in availed_data:
            if x['attendance'] not in leave_attendence_id_data:
                leave_attendence_id_data.append(x['attendance'])
                availed_leave.append(x)

        print("leave_attendence_id_data",leave_attendence_id_data)
        print("actual_data",availed_leave)

        availed_cl=0
        availed_el=0
        availed_sl=0
        availed_ab=0
        type_leave = ''
        availed = 0
        if availed_leave:
            for leave in availed_leave:
                if leave['leave_type_changed_period']=='HD' and leave['leave_type_changed'] is not None:
                    availed = 0.5
                    type_leave = leave['leave_type_changed']
                elif leave['leave_type_changed_period']=='FD' and leave['leave_type_changed'] is not None:
                    availed = 1
                    type_leave = leave['leave_type_changed']
                elif leave['request_type']=='FD' and leave['leave_type'] is not None:
                    availed = 1
                    type_leave = leave['leave_type']
                elif leave['request_type']=='HD' and leave['leave_type'] is not None:
                    availed = 0.5
                    type_leave = leave['leave_type']

                if type_leave == 'CL':
                    availed_cl+=availed
                elif type_leave == 'EL':
                    availed_el+=availed
                elif type_leave == 'SL':
                    availed_sl=availed_sl + availed
                elif type_leave == 'AB':
                    availed_ab+=availed
                availed=0

        availed_cl=float(availed_cl)+float(advance_cl)
        availed_el=float(availed_el)+float(advance_el)
        availed_ab =float(availed_ab)+float(advance_ab)

        total_grace['availed_cl']=availed_cl
        total_grace['availed_el']=availed_el
        total_grace['availed_sl']=availed_sl
        total_grace['availed_ab']=availed_ab
        total_grace['total_availed_leave']=float(availed_cl) + float(availed_el) + float(availed_sl)

        core_user_detail=TCoreUserDetail.objects.filter(cu_user=employee_id,cu_is_deleted=False).values('joining_date',
                                                                                                    'granted_cl',
                                                                                                    'granted_sl',
                                                                                                    'granted_el'
                                                                                                    )
        print('core_user_detail',core_user_detail)
        if core_user_detail:
            if core_user_detail[0]['joining_date']>total_month_grace[0]['year_start_date']:
                approved_leave=JoiningApprovedLeave.objects.filter(employee=employee_id,is_deleted=False).values('cl',
                                                                                                                 'el',
                                                                                                                 'sl',
                                                                                                                 'year',
                                                                                                                 'month',
                                                                                                                 'first_grace'
                                                                                                                 )
                if approved_leave:
                    total_grace['granted_cl']=approved_leave[0]['cl']
                    total_grace['cl_balance']=float(approved_leave[0]['cl'] if approved_leave[0]['cl'] else 0.0) -float(availed_cl)
                    total_grace['granted_el']=approved_leave[0]['el']
                    total_grace['el_balance']=float(approved_leave[0]['el'] if approved_leave[0]['el'] else 0.0 ) -float(availed_el)
                    total_grace['granted_sl']=approved_leave[0]['sl']
                    total_grace['sl_balance']=float( approved_leave[0]['sl'] if approved_leave[0]['sl'] else 0.0 ) -float(availed_sl)
                    total_grace['total_granted_leave']=float(approved_leave[0]['cl'] if approved_leave[0]['cl'] else 0.0) + float(approved_leave[0]['el'] if approved_leave[0]['el'] else 0.0) + float(approved_leave[0]['sl'] if approved_leave[0]['sl'] else 0.0)
                    total_grace['total_leave_balances']=float(total_grace['total_granted_leave']) - float(total_grace['total_availed_leave'])
                    if total_month_grace[0]['month']==approved_leave[0]['month']:    #for joining month only
                        total_grace['total_month_grace']=approved_leave[0]['first_grace']
                        total_grace['month_start']=core_user_detail[0]['joining_date']
                        total_grace['grace_balance']=total_grace['total_month_grace'] - total_grace['availed_grace']
            else:
                total_grace['granted_cl']=core_user_detail[0]['granted_cl']
                total_grace['cl_balance']=float(core_user_detail[0]['granted_cl']) - float(availed_cl)
                total_grace['granted_el']=core_user_detail[0]['granted_el']
                total_grace['el_balance']=float(core_user_detail[0]['granted_el']) - float(availed_el)
                total_grace['granted_sl']=core_user_detail[0]['granted_sl']
                total_grace['sl_balance']=float(core_user_detail[0]['granted_sl']) - float(availed_sl)
                total_grace['total_granted_leave']=float(core_user_detail[0]['granted_cl']) + float(core_user_detail[0]['granted_el']) + float(core_user_detail[0]['granted_sl'])
                total_grace['total_leave_balances']=float(total_grace['total_granted_leave']) - float(total_grace['total_availed_leave'])

        data_dict['result'] = total_grace
        
        print("total_time", datetime.now()-aa)

        if total_grace:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_SUCCESS
        elif len(total_grace) == 0:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_NO_DATA
        else:
            data_dict['request_status'] = 0
            data_dict['msg'] = settings.MSG_ERROR
        total_grace = data_dict
        return Response(total_grace)


class AttendanceGraceLeaveListModifiedView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = AttendanceApprovalRequest.objects.filter(is_deleted=False)
    # serializer_class = AttendanceGraceLeaveListModifiedSerializer

   

    def get(self, request, *args, **kwargs):
        # response=super(AttendanceGraceLeaveListModifiedView,self).get(self, request, args, kwargs)
        #date =self.request.query_params.get('date', None)
        # print('date',type(date))
        #date_object = datetime.strptime(date, '%Y-%m-%d').date()
        date_object = datetime.now().date()
        #print('date_object',date_object)
        employee_id=self.request.query_params.get('employee_id', None)
        total_grace={}
        data_dict = {}
        is_previous=self.request.query_params.get('is_previous', None)

        aa = datetime.now()
        total_month_grace=AttendenceMonthMaster.objects.filter(month_start__date__lte=date_object,
                                        month_end__date__gte=date_object,is_deleted=False).values('grace_available',
                                                                                 'year_start_date',
                                                                                 'year_end_date',
                                                                                 'month',
                                                                                 'month_start',
                                                                                 'month_end')
        if is_previous == "true":
            #print('sada',type(total_month_grace[0]['month_start']))
            '''
                Changed by Rupam Hazra due to same variable date_object
            '''
            date_object_previous= total_month_grace[0]['month_start'].date()- timedelta(days=1)  
            total_month_grace=AttendenceMonthMaster.objects.filter(month_start__date__lte=date_object_previous,
                                        month_end__date__gte=date_object_previous,is_deleted=False).values('grace_available',
                                                                                 'year_start_date',
                                                                                 'year_end_date',
                                                                                 'month',
                                                                                 'month_start',
                                                                                 'month_end')
                                                                                
        #print('total_month_grace',total_month_grace)
        total_grace['month_start']=total_month_grace[0]['month_start']
        total_grace['month_end']=total_month_grace[0]['month_end']
        total_grace['year_start']=total_month_grace[0]['year_start_date']
        total_grace['year_end']=total_month_grace[0]['year_end_date']
        #print("total_month_grace",total_grace)

        if total_month_grace:
            total_grace['total_month_grace']=total_month_grace[0]['grace_available'] if total_month_grace[0]['grace_available'] else 0

        # for data in response.data:
        availed_grace = AttendanceApprovalRequest.objects.filter(Q(attendance__employee=employee_id) &
                                                                Q(duration_start__gte=total_month_grace[0]['month_start']) &
                                                                Q(duration_start__lte=total_month_grace[0]['month_end']) &
                                                                Q(is_requested=True) & Q(is_deleted=False) &
                                                                (Q(request_type='GR')|Q(checkin_benchmark=True))
                                                                ).aggregate(Sum('duration'))['duration__sum']

        total_grace['availed_grace']=availed_grace if availed_grace else 0
        total_grace['grace_balance']=total_month_grace[0]['grace_available'] - total_grace['availed_grace']


        advance_leave=EmployeeAdvanceLeaves.objects.filter(Q(employee=employee_id)&
                                                           Q(is_deleted=False)&
                                                           (Q(approved_status='pending')|Q(approved_status='approved'))
                                                          ).values('leave_type','start_date','end_date')
        #print('advance_leave',advance_leave)     
        advance_cl=0
        advance_el=0
        advance_ab=0
        day=0

        date =self.request.query_params.get('employee', None)

        


        if advance_leave:
            for leave in advance_leave.iterator():
                #print('leave',leave)
                start_date=leave['start_date'].date()
                end_date=leave['end_date'].date()+timedelta(days=1)
                #print('start_date,end_date',start_date,end_date)
                if date_object < end_date:
                    if date_object < start_date:
                        day=(end_date-start_date).days 
                        #print('day',day)
                    elif date_object > start_date:
                        day=(end_date-date_object).days
                        #print('day2',day)
                    else:
                        day=(end_date-date_object).days

                if leave['leave_type']=='CL':
                    advance_cl+=day
                    #print('advance_cl_1',advance_cl)
                elif leave['leave_type']=='EL':
                    advance_el+=day
                    #print('advance_el_2',advance_el)
                elif leave['leave_type']=='AB':
                    advance_ab+=day

        

        print('advance_cl',advance_cl)
        print('advance_el',advance_el)


        
        """ 
        LEAVE CALCULATION:-
        1)SINGLE LEAVE CALCULATION
        2)MULTIPLE LEAVE FOR ONE DAY IS AUTO CONVERTED TO ONE TYPE OF LEAVE 
        EDITED BY :- Abhishek.singh@shyamfuture.com
        
        """ 
        #starttime = datetime.now()
        availed_hd_cl=0.0
        availed_hd_el=0.0
        availed_hd_sl=0.0
        availed_hd_ab=0.0
        availed_cl=0.0
        availed_el=0.0
        availed_sl=0.0
        availed_ab=0.0

        attendence_daily_data = AttendanceApprovalRequest.objects.filter(((Q(leave_type_changed_period__isnull=False)&(Q(leave_type_changed_period='FD')|Q(leave_type_changed_period='HD')))|
                                                                        (Q(leave_type_changed_period__isnull=True)&(Q(request_type='FD')|Q(request_type='HD')))),
                                                                        attendance__employee=employee_id,is_requested=True).values('duration_start__date').distinct()
        #print("attendence_daily_data",attendence_daily_data)
        date_list = [x['duration_start__date'] for x in attendence_daily_data.iterator()]
        #print("date_list",date_list)
        # for data in attendence_daily_data.iterator():
            # print(datetime.now())
        availed_master_wo_reject_fd = AttendanceApprovalRequest.objects.\
                filter((Q(approved_status='pending')|Q(approved_status='approved')|Q(approved_status='reject')),
                        (Q(leave_type__isnull=False)|Q(leave_type_changed_period__isnull=False)),
                        attendance__employee=employee_id,
                        attendance_date__in=date_list,is_requested=True,is_deleted=False).annotate(
                            leave_type_final = Case(
                            When((Q(leave_type_changed_period__isnull=False)&Q(leave_type_changed_period='FD')),then=F('leave_type_changed')),
                            When((Q(leave_type_changed_period__isnull=True)&Q(request_type='FD')),then=F('leave_type')),
                            output_field=CharField()
                        ),
                        leave_type_final_hd = Case(
                            When((Q(leave_type_changed_period__isnull=False)&Q(leave_type_changed_period='HD')),then=F('leave_type_changed')),
                            When((Q(leave_type_changed_period__isnull=True)&Q(request_type='HD')),then=F('leave_type')),
                            output_field=CharField()
                        ),
                        ).values('leave_type_final','leave_type_final_hd','attendance_date').distinct()
        #print("availed_master_wo_reject_fd",availed_master_wo_reject_fd)
        if availed_master_wo_reject_fd:

            for data in date_list:
                availed_FD=availed_master_wo_reject_fd.filter(attendance_date=data)
                
                #print("availed_HD",availed_FD)
                if availed_FD.filter(leave_type_final__isnull=False):
                    if availed_FD.values('leave_type_final').count() >1:
                        if availed_FD.filter(leave_type_final='AB'):
                            availed_ab=availed_ab+1.0

                        elif availed_FD.filter(leave_type_final='CL'):
                            availed_cl=availed_cl+1.0
                                    

                    else:
                        l_type=availed_FD[0]['leave_type_final']
                        if l_type == 'CL':
                            availed_cl=availed_cl+1.0
                        elif l_type == 'EL':
                            availed_el=availed_el+1.0
                        elif l_type == 'SL':
                            availed_sl=availed_sl+1.0
                        elif l_type == 'AB':
                            availed_ab=availed_ab+1.0

                elif availed_FD.filter(leave_type_final_hd__isnull=False):
                    if availed_FD.values('leave_type_final_hd').count() >1:
                        if availed_FD.filter(leave_type_final_hd='AB'):
                            availed_hd_ab=availed_hd_ab+1.0

                        elif availed_FD.filter(leave_type_final_hd='CL'):
                            availed_hd_cl=availed_hd_cl+1.0
                                    

                    else:
                        l_type=availed_FD[0]['leave_type_final_hd']
                        if l_type == 'CL':
                            availed_hd_cl=availed_hd_cl+1.0
                        elif l_type == 'EL':
                            availed_hd_el=availed_hd_el+1.0
                        elif l_type == 'SL':
                            availed_hd_sl=availed_hd_sl+1.0
                        elif l_type == 'AB':
                            availed_hd_ab=availed_hd_ab+1.0
        

        

        print("availed_cl",availed_cl)
        print("availed_el",availed_el)

        print('availed_hd_cl',availed_hd_cl/2)
        print('availed_hd_el',availed_hd_el/2)

        total_grace['availed_cl']=float(availed_cl)+float(advance_cl)+float(availed_hd_cl/2)
        print("total_grace['availed_cl']",total_grace['availed_cl'])
        total_grace['availed_el']=float(availed_el)+float(advance_el)+float(availed_hd_el/2)
        print("total_grace['availed_el']",total_grace['availed_el'])
        total_grace['availed_sl']=float(availed_sl)+float(availed_hd_sl/2)
        #print("total_grace['availed_sl']",total_grace['availed_sl'])
        total_grace['availed_ab']=float(availed_ab)+float(advance_ab)+float(availed_hd_ab/2)
        #print("total_grace['availed_ab']",total_grace['availed_ab'])


        total_grace['total_availed_leave']=total_grace['availed_cl'] +total_grace['availed_el'] + total_grace['availed_sl']

        core_user_detail=TCoreUserDetail.objects.filter(cu_user=employee_id,cu_is_deleted=False).values('joining_date',
                                                                                                    'granted_cl',
                                                                                                    'granted_sl',
                                                                                                    'granted_el',
                                                                                                    'is_confirm',
                                                                                                    'salary_type__st_name'
                                                                                                    )
        #print('core_user_detail',core_user_detail)

        if core_user_detail:
            if core_user_detail[0]['salary_type__st_name']=='13' and core_user_detail[0]['is_confirm'] is False:
                total_grace['is_confirm'] = False
            else:
                total_grace['is_confirm'] = True
            if core_user_detail[0]['joining_date']>total_month_grace[0]['year_start_date']:
                approved_leave=JoiningApprovedLeave.objects.filter(employee=employee_id,is_deleted=False).values('cl', 'el', 'sl',
                                                                                                                 'year', 'month',
                                                                                                                 'first_grace')
                if approved_leave:
                    total_grace['granted_cl']=approved_leave[0]['cl']
                    total_grace['cl_balance']=float(approved_leave[0]['cl'] if approved_leave[0]['cl'] else 0.0) - float(total_grace['availed_cl'])
                    total_grace['granted_el']=approved_leave[0]['el']
                    total_grace['el_balance']=float(approved_leave[0]['el'] if approved_leave[0]['el'] else 0.0 ) - float(total_grace['availed_el'])
                    total_grace['granted_sl']=approved_leave[0]['sl']
                    total_grace['sl_balance']=float( approved_leave[0]['sl'] if approved_leave[0]['sl'] else 0.0 ) - float(total_grace['availed_sl'])
                    total_grace['total_granted_leave']=float(approved_leave[0]['cl'] if approved_leave[0]['cl'] else 0.0) + float(approved_leave[0]['el'] if approved_leave[0]['el'] else 0.0) + float(approved_leave[0]['sl'] if approved_leave[0]['sl'] else 0.0)
                    total_grace['total_leave_balances']=float(total_grace['total_granted_leave']) - float(total_grace['total_availed_leave'])
                    if total_month_grace[0]['month']==approved_leave[0]['month']:    #for joining month only
                        total_grace['total_month_grace']=approved_leave[0]['first_grace']
                        total_grace['month_start']=core_user_detail[0]['joining_date']
                        total_grace['grace_balance']=total_grace['total_month_grace'] - total_grace['availed_grace']
            else:
                total_grace['granted_cl']=core_user_detail[0]['granted_cl']
                total_grace['cl_balance']=float(core_user_detail[0]['granted_cl']) -  float(total_grace['availed_cl'])
                total_grace['granted_el']=core_user_detail[0]['granted_el']
                total_grace['el_balance']=float(core_user_detail[0]['granted_el']) - float(total_grace['availed_el'])
                total_grace['granted_sl']=core_user_detail[0]['granted_sl']
                total_grace['sl_balance']=float(core_user_detail[0]['granted_sl']) - float(total_grace['availed_sl'])
                total_grace['total_granted_leave']=float(core_user_detail[0]['granted_cl']) + float(core_user_detail[0]['granted_el']) + float(core_user_detail[0]['granted_sl'])
                total_grace['total_leave_balances']=float(total_grace['total_granted_leave']) - float(total_grace['total_availed_leave'])

        data_dict['result'] = total_grace
        time_last = datetime.now()-aa
        #print("time_last",time_last)
        # data_dict['result'] = "Successful"
        if total_grace:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_SUCCESS
        elif len(total_grace) == 0:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_NO_DATA
        else:
            data_dict['request_status'] = 0
            data_dict['msg'] = settings.MSG_ERROR
        total_grace = data_dict
        return Response(total_grace)

class AttendanceLateConveyanceApplyView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = AttendanceApprovalRequest.objects.filter(is_deleted=False)
    serializer_class = AttendanceLateConveyanceApplySerializer

    # @response_modify_decorator_get
    # def get(self, request, *args, **kwargs):
    #     return response

    def get(self,request,*args, **kwargs):
        attandance_id = self.kwargs['pk']
        attendance_approval_request = AttendanceApprovalRequest.objects.filter(attendance=attandance_id,is_deleted=False,is_late_conveyance=True)
        data = {}
        data_dict = {}
        conveyance_data_dict = {}
        if attendance_approval_request:
            print('attendance_approval_request',attendance_approval_request)
            conveyance_data_list = []
            for conveyance_data in attendance_approval_request:
                first_name=conveyance_data.conveyance_alloted_by.first_name if conveyance_data.conveyance_alloted_by.first_name  else None
                last_name=conveyance_data.conveyance_alloted_by.last_name if conveyance_data.conveyance_alloted_by.last_name  else None
                data = {
                    'id' : conveyance_data.id,
                    'vehicle_type' : conveyance_data.vehicle_type.name if conveyance_data.vehicle_type else '',
                    'vehicle_type_desctiption' : conveyance_data.vehicle_type.description if conveyance_data.vehicle_type else '',
                    'vehicle_type_id' : conveyance_data.vehicle_type.id if conveyance_data.vehicle_type else '',
                    'conveyance_purpose':conveyance_data.conveyance_purpose,
                    'conveyance_alloted_by':conveyance_data.conveyance_alloted_by.id,
                    'conveyance_alloted_by_name':first_name +" "+ last_name,
                    'from_place' : conveyance_data.from_place,
                    'to_place' : conveyance_data.to_place,
                    'conveyance_expense' : conveyance_data.conveyance_expense
                }
                print('data',data)
                conveyance_data_list.append(data)
            print('conveyance_data_list',conveyance_data_list)
            data_dict['result'] = conveyance_data_list
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

class AttendanceAdvanceLeaveListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EmployeeAdvanceLeaves.objects.filter(is_deleted=False)
    serializer_class = AttendanceAdvanceLeaveListSerializer
    pagination_class = CSPageNumberPagination

    def get_queryset(self):
        cur_date = datetime.now().date()
        total_month_grace=AttendenceMonthMaster.objects.filter(month_start__date__lte=cur_date,
                                        month_end__date__gte=cur_date,is_deleted=False).values(
                                                                                 'year_start_date__date',
                                                                                 'year_end_date__date')

        emp_id = self.request.query_params.get('emp_id', None)
        if self.queryset.count():
            if total_month_grace:
                #print("total_month_grace",total_month_grace)
                return self.queryset.filter(((Q(start_date__date__gte=total_month_grace[0]['year_start_date__date'])&
                                            Q(end_date__date__lte=total_month_grace[0]['year_end_date__date']))|
                                            (Q(start_date__date__lte=total_month_grace[0]['year_start_date__date'])&
                                            Q(end_date__date__gte=total_month_grace[0]['year_start_date__date']))|
                                            (Q(start_date__date__lte=total_month_grace[0]['year_end_date__date'])&
                                            Q(end_date__date__gte=total_month_grace[0]['year_end_date__date']))
                                            ),employee_id=emp_id)
            else:
                return self.queryset.filter(((Q(start_date__date__gte=cur_date)&Q(end_date__date__lte=cur_date))|
                                            (Q(start_date__date__lte=cur_date)&Q(end_date__date__gte=cur_date))|
                                            (Q(start_date__date__lte=cur_date)&Q(end_date__date__gte=cur_date))
                                            ),employee_id=emp_id)
        else:
            return self.queryset

    @response_modify_decorator_list_or_get_after_execution_for_pagination
    def get(self, request, *args, **kwargs):
        response=super(AttendanceAdvanceLeaveListView,self).get(self, request, args, kwargs)
        for data in response.data['results']:
            #print(data['approved_status'])
            data['approved_status']=data['approved_status'].capitalize()
        return response
class AttendanceAdvanceLeaveReportView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = AttendanceAdvanceLeaveListSerializer
    pagination_class = CSPageNumberPagination
    queryset = EmployeeAdvanceLeaves.objects.filter(Q(is_deleted=False) & 
                                                    (Q(approved_status='approved')|Q(approved_status='reject'))
                                                   )
    def get_queryset(self):

        team_approval_flag = self.request.query_params.get('team_approval_flag', None)
        search_sort_flag = True
        if team_approval_flag == '1':
            login_user_details = self.request.user
            #print('login_user_details',login_user_details)
            #print('login_user_details',login_user_details.is_superuser)
            if login_user_details.is_superuser == False:
                users_list_under_the_login_user = TCoreUserDetail.objects.filter(
                    reporting_head = login_user_details,
                    cu_is_deleted = False
                ).values_list('cu_user')
                #print('users_list_under_the_login_user',users_list_under_the_login_user)
                if users_list_under_the_login_user:
                    attendence_id_list = EmployeeAdvanceLeaves.objects.filter(
                                employee__in=users_list_under_the_login_user,
                                is_deleted = False
                                )
                    print('attedence_details',attendence_id_list)
                    if attendence_id_list:
                        search_sort_flag = True
                        self.queryset = attendence_id_list
                    else:
                        search_sort_flag = False
                        self.queryset = self.queryset
                else:
                    search_sort_flag = False
                    self.queryset = []
                
            else:
                search_sort_flag = True
                self.queryset = self.queryset   

        if search_sort_flag:
            filter={}
            search = self.request.query_params.get('search', None)
            leave_type=self.request.query_params.get('leave_type', None)
            approved_type=self.request.query_params.get('approved_type', None)
            field_name = self.request.query_params.get('field_name', None)
            order_by = self.request.query_params.get('order_by', None)
            from_date = self.request.query_params.get('from_date', None)
            to_date = self.request.query_params.get('to_date', None)
            queryset_all = EmployeeAdvanceLeaves.objects.none()
            sort_field='-id'
            dept_filter = self.request.query_params.get('dept_filter', None)

            if field_name and order_by:
                if field_name =='start_date' and order_by=='asc':
                    sort_field='start_date'
                    # return self.queryset.filter(is_deleted=False).order_by('start_date')
                elif field_name =='start_date' and order_by=='desc':
                    sort_field='-start_date'
                    # return self.queryset.filter(is_deleted=False).order_by('-start_date')
                elif field_name =='end_date' and order_by=='asc':
                    sort_field='end_date'
                    # return self.queryset.filter(is_deleted=False).order_by('end_date')
                elif field_name =='end_date' and order_by=='desc':
                    sort_field='-end_date'
                    # return self.queryset.filter(is_deleted=False).order_by('-end_date')
                elif field_name =='date_of_application' and order_by=='asc':
                    sort_field='created_at'
                    # return self.queryset.filter(is_deleted=False).order_by('created_at')
                elif field_name =='date_of_application' and order_by=='desc':
                    sort_field='-created_at'
                    # return self.queryset.filter(is_deleted=False).order_by('-created_at')
            if self.queryset.count():
                if dept_filter:
                    dept_list = dept_filter.split(',')
                    emp_list = TCoreUserDetail.objects.filter(department__in=dept_list).values_list('cu_user',flat=True)
                    filter['employee__in'] = emp_list

                if from_date and to_date:
                    start_object = datetime.strptime(from_date, '%Y-%m-%d').date()
                    filter['start_date__date__gte'] = start_object
                    end_object = datetime.strptime(to_date, '%Y-%m-%d').date()
                    filter['end_date__date__lte'] = end_object + timedelta(days=1)

                if leave_type:
                    leave_type_list=leave_type.split(',')
                    filter['leave_type__in']= leave_type_list
                    # return self.queryset.filter(leave_type__in=leave_type_list)
                if approved_type:
                    approved_type_list=approved_type.split(',')
                    filter['approved_status__in']= approved_type_list
                    # return self.queryset.filter(approved_status__in=approved_type_list)

                    
                if search :
                    search_data = list(map(str,search.split(" ")))
                    print("This is if condition entry")
                    if len(search.split(" "))>0 and len(search.split(" "))<2:
                        print("length 1 hai ")
                        queryset = self.queryset.filter((Q(employee__first_name__icontains=search_data[0])|Q(employee__last_name__icontains=search_data[0])),
                                                        is_deleted=False,**filter).order_by(sort_field)                            
                        queryset_all=(queryset_all|queryset)
                        return queryset_all 

                    elif len(search.split(" "))>1:
                        print("length 2 hai ")
                        queryset = self.queryset.filter((Q(employee__first_name__icontains=search_data[0]) & Q(employee__last_name__icontains=search_data[1])),
                                                        is_deleted=False,**filter).order_by(sort_field)
                        queryset_all=(queryset_all|queryset)
                        return queryset_all 


                else:
                    queryset = self.queryset.filter(is_deleted=False,**filter).order_by(sort_field)
                    return queryset

            else:
                return queryset_all
        else:
            return list()



    @response_modify_decorator_list_or_get_after_execution_for_pagination
    def get(self, request, *args, **kwargs):
        response=super(AttendanceAdvanceLeaveReportView,self).get(self, request, args, kwargs)
        for data in response.data['results']:
            data['employee_name'] = ''
            data['approved_status']=  data['approved_status'].capitalize() if data['approved_status'] else None
            emp_name = User.objects.filter(id=data['employee']).values('first_name','last_name')
            if emp_name:
                first_name=emp_name[0]['first_name'] if emp_name[0]['first_name'] else ""
                last_name=emp_name[0]['last_name'] if emp_name[0]['last_name'] else ""
                data['employee_name'] = first_name + " " + last_name
        return response
class AdminAttendanceAdvanceLeavePendingListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EmployeeAdvanceLeaves.objects.filter(is_deleted=False,approved_status='pending')
    serializer_class = AdminAttendanceAdvanceLeavePendingListSerializer
    pagination_class = CSPageNumberPagination

    def get_queryset(self):

        team_approval_flag = self.request.query_params.get('team_approval_flag', None)
        search_sort_flag = True
        if team_approval_flag == '1':
            login_user_details = self.request.user
            #print('login_user_details',login_user_details)
            #print('login_user_details',login_user_details.is_superuser)
            if login_user_details.is_superuser == False:
                users_list_under_the_login_user = TCoreUserDetail.objects.filter(
                    reporting_head = login_user_details,
                    cu_is_deleted = False
                ).values_list('cu_user')
                #print('users_list_under_the_login_user',users_list_under_the_login_user)
                if users_list_under_the_login_user:
                    attendence_id_list = EmployeeAdvanceLeaves.objects.filter(
                                employee__in=users_list_under_the_login_user,
                                is_deleted = False,approved_status='pending'
                                )
                    print('attedence_details',attendence_id_list)
                    if attendence_id_list:
                        search_sort_flag = True
                        self.queryset = attendence_id_list
                        #self.queryset = self.queryset.filter(attendance__in=attendence_id_list)
                    else:
                        search_sort_flag = False
                        self.queryset = self.queryset
                else:
                    search_sort_flag = False
                    self.queryset = []
                
            else:
                search_sort_flag = True
                self.queryset = self.queryset   


        if search_sort_flag:
            sort_field='-id'
            filter={}
            search = self.request.query_params.get('search', None)
            emp_id = self.request.query_params.get('emp_id', None)
            leave_type=self.request.query_params.get('leave_type', None)
            field_name = self.request.query_params.get('field_name', None)
            order_by = self.request.query_params.get('order_by', None)
            queryset_all = EmployeeAdvanceLeaves.objects.none()
            if self.queryset.count():
                # print('leave_type-->',leave_type)
                if field_name and order_by:
                    if field_name =='start_date' and order_by=='asc':
                        sort_field='start_date'
                        # return self.queryset.filter(is_deleted=False).order_by('start_date')
                    elif field_name =='start_date' and order_by=='desc':
                        sort_field='-start_date'
                        # return self.queryset.filter(is_deleted=False).order_by('-start_date')
                    elif field_name =='end_date' and order_by=='asc':
                        sort_field='end_date'
                        # return self.queryset.filter(is_deleted=False).order_by('end_date')
                    elif field_name =='end_date' and order_by=='desc':
                        sort_field='-end_date'
                        # return self.queryset.filter(is_deleted=False).order_by('-end_date')
                    elif field_name =='sort_applied' and order_by=='asc':
                        sort_field='created_at'
                        # return self.queryset.filter(is_deleted=False).order_by('created_at')
                    elif field_name =='sort_applied' and order_by=='desc':
                        sort_field='-created_at'
                        # return self.queryset.filter(is_deleted=False).order_by('-created_at')
                    

                if leave_type:
                    leave_type_list=leave_type.split(',')
                    filter['leave_type__in']= leave_type_list

                if search :
                    search_data = list(map(str,search.split(" ")))
                    print("This is if condition entry")
                    if len(search.split(" "))>0 and len(search.split(" "))<2:
                        print("length 1 hai ")
                        queryset = self.queryset.filter((Q(employee__first_name__icontains=search_data[0])|Q(employee__last_name__icontains=search_data[0])),
                                                        is_deleted=False,**filter).order_by(sort_field)                            
                        return queryset
                    elif len(search.split(" "))>1:
                        print("length 2 hai ")
                        queryset = self.queryset.filter((Q(employee__first_name__icontains=search_data[0]) & Q(employee__last_name__icontains=search_data[1])),
                                                        is_deleted=False,**filter).order_by(sort_field) 
                        return queryset      

                else:
                    queryset = self.queryset.filter(is_deleted=False,**filter).order_by(sort_field) 
                    return queryset
            else:
                return queryset_all
        else:
            return list()

    @response_modify_decorator_list_or_get_after_execution_for_pagination
    def get(self, request, *args, **kwargs):
        response=super(AdminAttendanceAdvanceLeavePendingListView,self).get(self, request, args, kwargs)
        for data in response.data['results']:
            data['employee_name'] = ''
            data['approved_status']=data['approved_status'].capitalize()
            emp_name = User.objects.filter(id=data['employee']).values('first_name','last_name')
            if emp_name:
                first_name=emp_name[0]['first_name'] if emp_name[0]['first_name'] else ""
                last_name=emp_name[0]['last_name'] if emp_name[0]['last_name'] else ""
                data['employee_name'] = first_name + " " + last_name
        return response

class AdminAttendanceAdvanceLeaveApprovalView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EmployeeAdvanceLeaves.objects.filter(is_deleted=False)
    serializer_class = AdminAttendanceAdvanceLeaveApprovalSerializer

    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
	
class AttendenceApprovalRequestView(generics.RetrieveUpdateAPIView):
	permission_classes = [IsAuthenticated]
	authentication_classes = [TokenAuthentication]
	queryset = AttendanceApprovalRequest.objects.filter(is_deleted=False)
	serializer_class = AttendenceApprovalRequestEditSerializer

class AttendanceConveyanceApprovalListView(generics.ListAPIView, mixins.UpdateModelMixin,
                                            mixins.CreateModelMixin):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = AttendanceApprovalRequest.objects.filter(conveyance_approval=0, is_deleted=False)
    serializer_class = AttendanceConveyanceApprovalListSerializer
    pagination_class = CSPageNumberPagination
    
    
    def get_queryset(self):
        print('sdsdsdsdsds')
        team_approval_flag = self.request.query_params.get('team_approval_flag', None)
        search_sort_flag = True
        if team_approval_flag == '1':
            login_user_details = self.request.user
            print('login_user_details',login_user_details)
            print('login_user_details',login_user_details.is_superuser)
            if login_user_details.is_superuser == False:
                users_list_under_the_login_user = TCoreUserDetail.objects.filter(
                    reporting_head = login_user_details,
                    cu_is_deleted = False
                ).values_list('cu_user')
                print('users_list_under_the_login_user',users_list_under_the_login_user)
                if users_list_under_the_login_user:
                    attendence_id_list = Attendance.objects.filter(
                                employee__in=users_list_under_the_login_user,
                                is_deleted = False
                                ).values_list('id')
                    print('attedence_details',attendence_id_list)
                    if attendence_id_list:
                        
                        print('gfggfgfgf')
                        result = self.queryset.filter(attendance__in=attendence_id_list)
                        print('result',result)
                        if result:
                            search_sort_flag = True
                            self.queryset = result
                        else:
                            search_sort_flag = False
                            #self.queryset = []

                    else:
                        search_sort_flag = False
                        #self.queryset = self.queryset
                else:
                    search_sort_flag = False
                    #self.queryset = self.queryset
                
            else:
                print('sdsds')
                search_sort_flag = True
                print('self.queryset',self.queryset  )
                self.queryset = self.queryset   
        # queryset=self.queryset.filter(status=1)
        if search_sort_flag:
            filter = {}
            sort_field='-id'
            from_date = self.request.query_params.get('from_date', None)
            to_date = self.request.query_params.get('to_date', None)
            department = self.request.query_params.get('department', None)
            designation = self.request.query_params.get('designation', None)
            search = self.request.query_params.get('search', None)
            field_name = self.request.query_params.get('field_name', None)
            order_by = self.request.query_params.get('order_by', None)

            if field_name and order_by:      
                if field_name =='date' and order_by=='asc':
                    sort_field='duration_start__date'
                    # return self.queryset.all().order_by('duration_start__date')
                if field_name =='date' and order_by=='desc':
                    sort_field='-duration_start__date'
                    # return self.queryset.all().order_by('-duration_start__date')
                if field_name =='duration_start' and order_by=='asc':
                    sort_field='duration_start'
                    # return self.queryset.all().order_by('duration_start')
                if field_name =='duration_start' and order_by=='desc':
                    sort_field='-duration_start'
                    # return self.queryset.all().order_by('-duration_start')

                if field_name =='duration_end' and order_by=='asc':
                    sort_field='duration_end'
                    # return self.queryset.all().order_by('duration_end')
                if field_name =='duration_end' and order_by=='desc':
                    sort_field='-duration_end'
                    # return self.queryset.all().order_by('-duration_end')

                if field_name =='duration' and order_by=='asc':
                    sort_field='duration'
                    # return self.queryset.all().order_by('duration')
                if field_name =='duration' and order_by=='desc':
                    sort_field='-duration'
                    # return self.queryset.all().order_by('-duration')
            # if search :
            #     print("This is if condition entry")
            #     for name in search.split(" "):
            #         queryset = self.queryset.filter((Q(attendance__employee__first_name__icontains=name)|Q(attendance__employee__last_name__icontains=name)),
            #                                         conveyance_approval=0,is_deleted=False)
            #     return queryset
            if from_date or to_date or designation or department or search:

                if from_date and to_date:
                    from_object =datetime.strptime(from_date, '%Y-%m-%d')
                    to_object =datetime.strptime(to_date, '%Y-%m-%d')
                    filter['attendance_date__gte']= from_object
                    filter['attendance_date__lte']= to_object + timedelta(days=1)

                if department and designation:
                    desi_dep_id=TCoreUserDetail.objects.filter(designation=designation,department=department).values('cu_user')
                    print(desi_dep_id)
                    filter['attendance__employee__in'] = [x['cu_user'] for x in desi_dep_id ]
                elif department :
                    department_id=TCoreUserDetail.objects.filter(department=department).values('cu_user')
                    print(department_id)
                    filter['attendance__employee__in'] = [x['cu_user'] for x in department_id ]
                    print(filter)
                elif designation:
                    designation_id=TCoreUserDetail.objects.filter(designation=designation).values('cu_user')
                    print(designation_id)
                    filter['attendance__employee__in'] = [x['cu_user'] for x in designation_id ]
                    print(filter)
                

                if search :
                    search_data = list(map(str,search.split(" ")))
                    print("This is if condition entry")
                    if len(search.split(" "))>0 and len(search.split(" "))<2:
                        print("length 1 hai ")
                        queryset = self.queryset.filter((Q(attendance__employee__first_name__icontains=search_data[0])|Q(attendance__employee__last_name__icontains=search_data[0])),
                                                        conveyance_approval=0,is_deleted=False,**filter).order_by(sort_field)                            
                        return queryset
                    elif len(search.split(" "))>1:
                        print("length 2 hai ")
                        queryset = self.queryset.filter((Q(attendance__employee__first_name__icontains=search_data[0]) & Q(attendance__employee__last_name__icontains=search_data[1])),
                                                        conveyance_approval=0,is_deleted=False,**filter).order_by(sort_field)
                        return queryset                

                else:
                    queryset = self.queryset.filter(conveyance_approval=0,is_deleted=False,**filter).order_by(sort_field)
                    return queryset

            else:
                return self.queryset.filter(conveyance_approval=0, is_deleted=False).order_by(sort_field)
        else:
            return list()
    
    @response_modify_decorator_list_or_get_after_execution_for_pagination
    def get(self, request, *args, **kwargs):

        response = super(AttendanceConveyanceApprovalListView, self).get(self, request, *args, **kwargs)
        convay_list = []
        for data in response.data['results']:
            data_dict = {}
            user_name = Attendance.objects.get(id=data['attendance'])
            benifit_id = HrmsBenefitsProvided.objects.get(benefits_name='conveyance')
            alloyance_per_day = HrmsUsersBenefits.objects.filter(user_id=user_name.employee, benefits_id=benifit_id)
            allowance = [x.allowance for x in alloyance_per_day if alloyance_per_day]
            if allowance:
                allowance_money = allowance[0]
            else:
                allowance_money = 0.0
            if data['vehicle_type']:
                vehical_name=VehicleTypeMaster.objects.get(id=data['vehicle_type']).name
            else:
                vehical_name=None
            alloted_by=AttendanceApprovalRequest.objects.get(id=data['id'])
            if alloted_by.conveyance_alloted_by:
                job_alloted_by = alloted_by.conveyance_alloted_by.first_name +" "+ alloted_by.conveyance_alloted_by.last_name
            else:
                job_alloted_by = None
            data_dict = {
                'id': data['id'],
                'name': user_name.employee.first_name + " " + user_name.employee.last_name,
                'eligibility': allowance_money,
                'is_conveyance': data['is_conveyance'],
                'is_late_conveyance': data['is_late_conveyance'],
                'conveyance_approval': data['conveyance_approval'],
                'vehicle_type': vehical_name,
                'conveyance_purpose': data['conveyance_purpose'],
                'conveyance_alloted_by':job_alloted_by,
                'from_place': data['from_place'],
                'to_place': data['to_place'],
                'conveyance_expense': data['conveyance_expense'],
                'approved_expenses': data['approved_expenses'],
                'conveyance_remarks': data['conveyance_remarks'],
                'attendance': data['attendance'],
                'duration_start': data['duration_start'],
                'duration_end': data['duration_end'],
                'duration': data['duration'],
                'conveyance_approved_by':data['conveyance_approved_by']
            }
            convay_list.append(data_dict)
        response.data['results'] = convay_list
        return response

    def put(self, request, *args, **kwargs):
        updated_by=request.user
        print(updated_by)

        req_id = self.request.query_params.get('req_id', None)
        conveyance_approval = request.data['conveyance_approval']

        approved_expenses= request.data['approved_expenses']
        print("req_id", req_id)
        if int(conveyance_approval) == 3 :
            AttendanceApprovalRequest.objects.filter(id=req_id).update(conveyance_approval=conveyance_approval,
                                                                    conveyance_approved_by=updated_by,approved_expenses=approved_expenses)
        else:
            AttendanceApprovalRequest.objects.filter(id=req_id).update(conveyance_approval=conveyance_approval,
                                                                        conveyance_approved_by=updated_by)
        # print(AttendanceApprovalRequest.)
        if AttendanceApprovalRequest:

            return Response({'results': {'conveyance_approval': conveyance_approval, },
                             'msg': 'success',
                             "request_status": 1})
        else:
            return Response({'results': {'conveyance_approval': conveyance_approval, },
                             'msg': 'fail',
                             "request_status": 0})
    def post(self, request, *args, **kwargs):

        updated_by=request.user
        log_before = []
        approve_or_reject =[]

        for data in request.data.get('conveyance_approvals'):
            log_before_query = AttendanceApprovalRequest.objects.filter(id=data.get('req_id')).values('conveyance_approval')
            if log_before_query: log_before.append(log_before_query[0])
            conveyance_approval= data.get('conveyance_approval')
            approved_expenses=data.get('approved_expenses')
            approve_or_reject.append(conveyance_approval)
            print("conveyance_approval",conveyance_approval)
            if int(conveyance_approval) == 3 :
                AttendanceApprovalRequest.objects.filter(id=data.get('req_id')).update(conveyance_approval=conveyance_approval,
                                                                        conveyance_approved_by=updated_by,approved_expenses=approved_expenses)
            else:
                AttendanceApprovalRequest.objects.filter(id=data.get('req_id')).update(conveyance_approval=conveyance_approval,
                                                                            conveyance_approved_by=updated_by)
            # print(AttendanceApprovalRequest.)
            if not AttendanceApprovalRequest:

                return Response({'results': {'conveyance_approval': conveyance_approval, },
                                'msg': 'fail',
                                "request_status": 0})

        ####################LOG PART######################################################## 
        print("log_before",str(log_before))
        # master_module_role = TMasterModuleRoleUser.objects.get(mmr_module__cm_name__iexact='hrms',mmr_user=request.user).mmr_role
        # master_module_role = TMasterModuleRoleUser.objects.get(mmr_user=request.user).mmr_role
        # core_role = TCoreRole.objects.get(id=str(master_module_role)).cr_name
        print(list(set(approve_or_reject)))
        if list(set(approve_or_reject))[0] == 2:
            # if core_role.lower() == 'hr admin':
            logger.log(request.user,'bulk approved Conveyance','conveyance_approval',str(log_before),request.data.get('conveyance_approvals'),'HRMS-AttendenceApproval-ConveyenceApprovals')
            # elif core_role.lower() == 'hr user':
            #     logger.log(request.user,AttendenceAction.ACTION_HR,'bulk approved Conveyance','conveyance_approval',str(log_before),request.data.get('conveyance_approvals'),'HRMS-AttendenceApproval-ConveyenceApprovals')
        elif list(set(approve_or_reject))[0] == 1:
            # if core_role.lower() == 'hr admin':
            logger.log(request.user,'bulk reject Conveyance','conveyance_approval',str(log_before),request.data.get('conveyance_approvals'),'HRMS-AttendenceApproval-ConveyenceApprovals')
            # elif core_role.lower() == 'hr user':
            #     logger.log(request.user,AttendenceAction.ACTION_HR,'bulk reject Conveyance','conveyance_approval',str(log_before),request.data.get('conveyance_approvals'),'HRMS-AttendenceApproval-ConveyenceApprovals')
        return Response({'results': {'conveyance_approvals': request.data.get('conveyance_approvals'), },
                'msg': 'success',
                "request_status": 1})

class AttendanceConveyanceAfterApprovalListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = AttendanceApprovalRequest.objects.filter(conveyance_approval__gt=0, is_deleted=False)
    serializer_class = AttendanceConveyanceApprovalListSerializer
    pagination_class = CSPageNumberPagination
    
    
    def get_queryset(self):
        # queryset=self.queryset.filter(status=1)

        team_approval_flag = self.request.query_params.get('team_approval_flag', None)
        search_sort_flag = True
        if team_approval_flag == '1':
            login_user_details = self.request.user
            #print('login_user_details',login_user_details)
            #print('login_user_details',login_user_details.is_superuser)
            if login_user_details.is_superuser == False:
                users_list_under_the_login_user = TCoreUserDetail.objects.filter(
                    reporting_head = login_user_details,
                    cu_is_deleted = False
                ).values_list('cu_user')
                #print('users_list_under_the_login_user',users_list_under_the_login_user)
                if users_list_under_the_login_user:
                    attendence_id_list = Attendance.objects.filter(
                                employee__in=users_list_under_the_login_user,
                                is_deleted = False
                                ).values_list('id')
                    print('attedence_details',attendence_id_list)
                    if attendence_id_list:
                        
                        self.queryset = self.queryset.filter(attendance__in=attendence_id_list)
                    else:
                        search_sort_flag = False
                        self.queryset = self.queryset
                else:
                    search_sort_flag = False
                    self.queryset = []
                
            else:
                search_sort_flag = True
                self.queryset = self.queryset   

        if search_sort_flag:
            filter = {}
            from_date = self.request.query_params.get('from_date', None)
            to_date = self.request.query_params.get('to_date', None)
            department = self.request.query_params.get('department', None)
            designation = self.request.query_params.get('designation', None)
            search = self.request.query_params.get('search', None)
            field_name = self.request.query_params.get('field_name', None)
            order_by = self.request.query_params.get('order_by', None)
            sort_field='-id'
            if field_name and order_by:      
                if field_name =='date' and order_by=='asc':
                    sort_field='duration_start__date'
                    # return self.queryset.all().order_by('duration_start__date')
                if field_name =='date' and order_by=='desc':
                    sort_field='-duration_start__date'
                    # return self.queryset.all().order_by('-duration_start__date')
                if field_name =='duration_start' and order_by=='asc':
                    sort_field='duration_start'
                    # return self.queryset.all().order_by('duration_start')
                if field_name =='duration_start' and order_by=='desc':
                    sort_field='-duration_start'
                    # return self.queryset.all().order_by('-duration_start')
                if field_name =='duration_end' and order_by=='asc':
                    sort_field='duration_end'
                    # return self.queryset.all().order_by('duration_end')
                if field_name =='duration_end' and order_by=='desc':
                    sort_field='-duration_end'
                    # return self.queryset.all().order_by('-duration_end')
                if field_name =='duration' and order_by=='asc':
                    sort_field='duration'
                    # return self.queryset.all().order_by('duration')
                if field_name =='duration' and order_by=='desc':
                    sort_field='-duration'
                    # return self.queryset.all().order_by('-duration')


            if from_date or to_date or designation or department or search:

                if from_date and to_date:
                    start_object = datetime.strptime(from_date, '%Y-%m-%d').date()
                    filter['duration_start__gte'] = start_object
                    end_object = datetime.strptime(to_date, '%Y-%m-%d').date()
                    filter['duration_start__lte'] = end_object + timedelta(days=1)

                if department and designation:
                    desi_dep_id=TCoreUserDetail.objects.filter(designation=designation,department=department).values('cu_user')
                    print(desi_dep_id)
                    filter['attendance__employee__in'] = [x['cu_user'] for x in desi_dep_id ]
                elif department :
                    department_id=TCoreUserDetail.objects.filter(department=department).values('cu_user')
                    print(department_id)
                    filter['attendance__employee__in'] = [x['cu_user'] for x in department_id ]
                    print(filter)
                elif designation:
                    designation_id=TCoreUserDetail.objects.filter(designation=designation).values('cu_user')
                    print(designation_id)
                    filter['attendance__employee__in'] = [x['cu_user'] for x in designation_id ]
                    print(filter)
                if search :
                    search_data = list(map(str,search.split(" ")))
                    print("This is if condition entry")
                    if len(search.split(" "))>0 and len(search.split(" "))<2:
                        print("length 1 hai ")
                        queryset = self.queryset.filter((Q(attendance__employee__first_name__icontains=search_data[0])|Q(attendance__employee__last_name__icontains=search_data[0])),
                                                        conveyance_approval__gt=0,is_deleted=False,**filter).order_by(sort_field)                            
                        return queryset
                    elif len(search.split(" "))>1:
                        print("length 2 hai ")
                        queryset = self.queryset.filter((Q(attendance__employee__first_name__icontains=search_data[0]) & Q(attendance__employee__last_name__icontains=search_data[1])),
                                                        conveyance_approval__gt=0,is_deleted=False,**filter).order_by(sort_field)
                        return queryset                

                else:
                    queryset = self.queryset.filter(conveyance_approval__gt=0,is_deleted=False,**filter).order_by(sort_field)
                    return queryset

            else:
                return self.queryset.filter(conveyance_approval__gt=0, is_deleted=False).order_by(sort_field)
        else:
            return list()


       


    @response_modify_decorator_list_or_get_after_execution_for_pagination
    def get(self, request, *args, **kwargs):

        response = super(AttendanceConveyanceAfterApprovalListView, self).get(self, request, *args, **kwargs)
        convay_list = []
        for data in response.data['results']:
            data_dict = {}
            user_name = Attendance.objects.get(id=data['attendance'])
            print(user_name.employee.first_name)
            benifit_id = HrmsBenefitsProvided.objects.get(benefits_name='conveyance')
            print(benifit_id)
            alloyance_per_day = HrmsUsersBenefits.objects.filter(user_id=user_name.employee, benefits_id=benifit_id)
            print(alloyance_per_day)
            allowance = [x.allowance for x in alloyance_per_day if alloyance_per_day]
            if allowance:
                allowance_money = allowance[0]
            else:
                allowance_money = 0.0
            if data['vehicle_type']:
                vehical_name=VehicleTypeMaster.objects.get(id=data['vehicle_type']).name
            else:
                vehical_name=None

            alloted_by=AttendanceApprovalRequest.objects.get(id=data['id'])
            if alloted_by.conveyance_alloted_by:
                job_alloted_by = alloted_by.conveyance_alloted_by.first_name +" "+ alloted_by.conveyance_alloted_by.last_name
            else:
                job_alloted_by = None
            conveyance_approved_by=AttendanceApprovalRequest.objects.get(id=data['id'])
            if conveyance_approved_by.conveyance_approved_by:
                job_conveyance_approved_by = conveyance_approved_by.conveyance_approved_by.first_name +" "+ conveyance_approved_by.conveyance_approved_by.last_name
            else:
                job_conveyance_approved_by = None
            data_dict = {
                'id': data['id'],
                'name': user_name.employee.first_name + " " + user_name.employee.last_name,
                'eligibility': allowance_money,
                'is_conveyance': data['is_conveyance'],
                'is_late_conveyance': data['is_late_conveyance'],
                'conveyance_approval': data['conveyance_approval'],
                'vehicle_type': vehical_name,
                'conveyance_purpose': data['conveyance_purpose'],
                'conveyance_alloted_by': job_alloted_by,
                'from_place': data['from_place'],
                'to_place': data['to_place'],
                'conveyance_expense': data['conveyance_expense'],
                'approved_expenses': data['approved_expenses'],
                'conveyance_remarks': data['conveyance_remarks'],
                'attendance': data['attendance'],
                'duration_start': data['duration_start'],
                'duration_end': data['duration_end'],
                'duration': data['duration'],
                'conveyance_approved_by':job_conveyance_approved_by
            }
            convay_list.append(data_dict)
        response.data['results'] = convay_list
        return response

class AttendanceSummaryListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = Attendance.objects.filter(is_deleted=False).order_by('date')
    serializer_class = AttendanceSummaryListSerializer
    # pagination_class = CSPageNumberPagination

    def get_queryset(self):
        blank_queryset = Attendance.objects.none()
        print('blank_queryset',blank_queryset)
        emp_id = self.request.query_params.get('emp_id', None)
        current_date = self.request.query_params.get('current_date', None)
        month = self.request.query_params.get('month', None)
        year = self.request.query_params.get('year', None)
        filter = {}
        date_range = None
        if self.queryset.count():
            print("self.queryset.count()",self.queryset.count())
            if current_date and emp_id:
                date = datetime.strptime(current_date, "%Y-%m-%d")
                date_range = AttendenceMonthMaster.objects.filter(month_start__date__lte=date,month_end__date__gte=date).values('month_start__date','month_end__date')
                # print("date_range",date_range)
            if month and year and emp_id:
                date_range = AttendenceMonthMaster.objects.filter(month=month,month_end__year=year).values('month_start__date','month_end__date')
                print("date_range",date_range)

            if date_range:
                print("This is if")
                filter['employee']=emp_id
                filter['date__date__gte'] = date_range[0]['month_start__date']
                filter['date__date__lte'] = date_range[0]['month_end__date']

        if filter :
            print('filter',self.queryset.filter(**filter))
            return self.queryset.filter(**filter)
        else:
            # print('else filter',self.queryset)
            return blank_queryset

    @response_modify_decorator_list_after_execution
    def get(self, request, *args, **kwargs):
        print('entry test')
        print(self.queryset)
        response=super(AttendanceSummaryListView,self).get(self, request, args, kwargs)
        print("response.data['results']",response.data)
        # print("response.data['results']",response.data['results'])
        attendance_request_dict = {}
        for data in response.data:
            attendance_request = AttendanceApprovalRequest.objects.filter(attendance=data['id'],is_deleted=False)
            attendance_request_list = []
            conveyance_dict = {}
            conveyance_list = []
            data['is_attendance_request'] = True
            daily_duration = 0
            daily_grace = 0
            cng_leave_type = None
            oth_leave_type = None
            daily_leave_type = None
            daily_leave_period = None
            daily_leave_approval = None
            cng_leave_period = None
            oth_leave_period = None
            day_remarks = None  
            for att_req in attendance_request:
                if att_req.leave_type_changed is not None:
                    day_remarks = 'Leave ('+att_req.leave_type_changed+')'
                elif att_req.leave_type_changed is None and att_req.leave_type is not None:
                    day_remarks = 'Leave ('+att_req.leave_type+')'
                elif att_req.approved_status=='approved' and att_req.request_type =='FOD':
                    day_remarks = 'OD'

                if att_req.leave_type_changed_period=='GR':
                    daily_grace+=att_req.duration
                elif att_req.request_type=='GR':
                    daily_grace+=att_req.duration
                elif att_req.checkin_benchmark == True:
                    daily_grace+=att_req.duration
                if att_req.leave_type_changed:
                    cng_leave_type= att_req.leave_type_changed
                    if att_req.leave_type_changed_period=='FD':
                        cng_leave_period = 1
                    elif att_req.leave_type_changed_period=='HD':
                        cng_leave_period = 0.5
                elif att_req.leave_type:
                    oth_leave_type= att_req.leave_type
                    if att_req.request_type=='FD':
                        oth_leave_period = 1
                    elif att_req.request_type=='HD':
                        oth_leave_period = 0.5

                if cng_leave_type:
                    daily_leave_type=cng_leave_type
                    daily_leave_period=cng_leave_period
                elif oth_leave_type:
                    daily_leave_type=oth_leave_type
                    daily_leave_period=oth_leave_period

                if att_req.approved_status == 'relese' or att_req.approved_status == 'pending' or att_req.is_requested== True:
                    data['is_attendance_request'] = False
                if att_req.is_late_conveyance==False and att_req.checkin_benchmark==False:
                    attendance_request_dict = {
                        'id' : att_req.id,
                        'duration_start' : att_req.duration_start,
                        'duration_end' : att_req.duration_end,
                        'duration' : att_req.duration,
                        'request_type' : att_req.leave_type_changed_period if att_req.leave_type_changed_period else att_req.request_type,
                        'is_requested' : att_req.is_requested,
                        'request_date' : att_req.request_date,
                        'justification' : att_req.justification,
                        'approved_status' : att_req.approved_status,
                        'remarks' : att_req.remarks,
                        'justified_by' : att_req.justified_by_id,
                        'justified_at' : att_req.justified_at,
                        'approved_by' : att_req.approved_by_id,
                        'approved_at' : att_req.approved_at,
                        'leave_type' : att_req.leave_type_changed if att_req.leave_type_changed else att_req.leave_type,
                        'is_late_conveyance' : att_req.is_late_conveyance,
                        'vehicle_type' : att_req.vehicle_type.name if att_req.vehicle_type else '',
                        'vehicle_type_id' : att_req.vehicle_type.id if att_req.vehicle_type else '',
                        'is_conveyance' : att_req.is_conveyance,
                        'from_place' : att_req.from_place,
                        'to_place' : att_req.to_place,
                        'conveyance_expense' : att_req.conveyance_expense,
                        'approved_expenses' : att_req.approved_expenses,
                        'conveyance_remarks' : att_req.conveyance_remarks,
                        'leave_type_changed' : att_req.leave_type_changed,
                        'leave_type_changed_period' : att_req.leave_type_changed_period,
                        'checkin_benchmark' : att_req.checkin_benchmark,
                        'lock_status' : att_req.lock_status
                    }
                    attendance_request_list.append(attendance_request_dict)

                if att_req.vehicle_type and att_req.from_place and att_req.to_place and att_req.conveyance_expense:
                    first_name = att_req.conveyance_alloted_by.first_name if att_req.conveyance_alloted_by else ''
                    last_name = att_req.conveyance_alloted_by.last_name if att_req.conveyance_alloted_by else ''
                    conveyance_dict = {
                        'vehicle_type' : att_req.vehicle_type.name if att_req.vehicle_type else '',
                        'vehicle_type_desctiption' : att_req.vehicle_type.description if att_req.vehicle_type else '',
                        'vehicle_type_id' : att_req.vehicle_type.id if att_req.vehicle_type else '',
                        'from_place' : att_req.from_place,
                        'to_place' : att_req.to_place,
                        'conveyance_expense' : att_req.conveyance_expense,
                        'approved_expenses' : att_req.approved_expenses,
                        'conveyance_remarks' : att_req.conveyance_remarks,
                        'conveyance_purpose' : att_req.conveyance_purpose,
                        'conveyance_alloted_by' : first_name + " " + last_name,
                        'conveyance_approval' : att_req.conveyance_approval,
                        'conveyance_approval_name' :att_req.get_conveyance_approval_display(),
                        'conveyance_durations' : att_req.duration,
                        'duration_start': att_req.duration_start,
                        'duration_end': att_req.duration_end,
                        'is_late_conveyance': att_req.is_late_conveyance
                    }
                    conveyance_list.append(conveyance_dict)


            print("daily_grace", daily_grace)
            data['conveyance_details'] = conveyance_list
            data['daily_grace'] = daily_grace
            data['daily_leave_type'] = daily_leave_type
            data['daily_leave_period'] = daily_leave_period
            data['attendance_request'] = attendance_request_list
            if day_remarks:
                    data['day_remarks'] = day_remarks

        return response

class AttendanceDailyListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = Attendance.objects.filter(is_deleted=False)
    # queryset = Attendance.objects.all()
    serializer_class = AttendanceDailyListSerializer
    # pagination_class = CSPageNumberPagination

    def get_queryset(self):
        emp_id = self.request.query_params.get('emp_id', None)
        current_date = self.request.query_params.get('current_date', None)
        month = self.request.query_params.get('month', None)
        year = self.request.query_params.get('year', None)
        is_previous = self.request.query_params.get('is_previous', None)
        joining_date = None
        filter = {}
        date_range = None

        if self.queryset.count():
            if emp_id:
                filter['employee']=emp_id
                joining_date = TCoreUserDetail.objects.get(cu_user=emp_id).joining_date.date()
                print("joining_date", joining_date)
            if current_date:
                print("current_date",current_date)
                date = datetime.strptime(current_date, "%Y-%m-%d")
                date_range = AttendenceMonthMaster.objects.filter(month_start__date__lte=date,month_end__date__gte=date).values('month_start__date','month_end__date')
                print("date_range",date_range)
                self.date_range_str = date_range[0]['month_start__date']
                self.date_range_end = date.date()

                if is_previous == 'true':
                    # print("is_previous",is_previous)
                    date = date_range[0]['month_start__date'] - timedelta(days=1)
                    # print("date",date)
                    date_range = AttendenceMonthMaster.objects.filter(month_start__date__lte=date,month_end__date__gte=date).values('month_start__date','month_end__date')
                    # print("is_previous_date_range",date_range)
                    self.date_range_str = date_range[0]['month_start__date']
                    self.date_range_end = date_range[0]['month_end__date']
                # print("date_range",date_range)
            elif month and year:
                date_range = AttendenceMonthMaster.objects.filter(month=month,month_end__year=year).values('month_start__date','month_end__date')
                # print("date_range",date_range)
            
            # print("elf.date_range",date_range)
            if date_range:
                filter['date__date__gte'] = date_range[0]['month_start__date']
                filter['date__date__lte'] = date_range[0]['month_end__date']
            if filter:
                return self.queryset.filter(**filter)
            else:
                return self.queryset
        else:
            # print("ELLSSS", self.queryset)
            return self.queryset.filter(is_deleted=False)

    # @response_modify_decorator_list_or_get_after_execution_for_pagination
    @response_modify_decorator_get_after_execution
    def get(self, request, *args, **kwargs):
        emp_id = self.request.query_params.get('emp_id', None)
        current_date = self.request.query_params.get('current_date', None)
        is_previous = self.request.query_params.get('is_previous', None)
        response=super(AttendanceDailyListView,self).get(self, request, args, kwargs)
        # print("response.data['results']",response.data)
        attendance_request_dict = {}
        date_list_data = []

        for data in response.data:
            is_attendance_request = True
            is_late_conveyance = False
            is_late_conveyance_completed = False
            late_conveyance_id = None
          
            # print(self.last_day_of_month(datetime.date(datetime.now().year,datetime.now().month, 1)))
            # print(datetime.now().year)
            date_list_data.append(datetime.strptime(data['date'], "%Y-%m-%dT%H:%M:%S").date())
            
            attendance_request = AttendanceApprovalRequest.objects.filter(attendance=data['id'],is_deleted=False)
            # print("attendance_request",attendance_request)
            attendance_request_list = []
            # print("data",data)
            day_remarks = None
            for att_req in attendance_request:
                if att_req.leave_type_changed is not None:
                    day_remarks = 'Leave ('+att_req.leave_type_changed+')'
                elif att_req.leave_type_changed is None and att_req.leave_type is not None:
                    day_remarks = 'Leave ('+att_req.leave_type+')'
                elif att_req.approved_status=='approved' and att_req.request_type =='FOD':
                    day_remarks = 'OD'

                if att_req.is_late_conveyance == True:
                    is_late_conveyance = True
                    late_conveyance_id = att_req.id
                if att_req.vehicle_type and att_req.from_place and att_req.to_place and att_req.conveyance_expense and att_req.is_late_conveyance == True:
                    is_late_conveyance_completed = True

                if att_req.is_late_conveyance==False and att_req.checkin_benchmark==False:
                    if att_req.approved_status == 'relese' or att_req.is_requested == False:
                        is_attendance_request = False
                    attendance_request_dict = {
                        'id' : att_req.id,
                        'duration_start' : att_req.duration_start,
                        'duration_end' : att_req.duration_end,
                        'duration' : att_req.duration,
                        'request_type' : att_req.leave_type_changed_period if att_req.leave_type_changed_period else att_req.request_type,
                        'is_requested' : att_req.is_requested,
                        'request_date' : att_req.request_date,
                        'justification' : att_req.justification,
                        'approved_status' : att_req.approved_status,
                        'remarks' : att_req.remarks,
                        'justified_by' : att_req.justified_by_id,
                        'justified_at' : att_req.justified_at,
                        'approved_by' : att_req.approved_by_id,
                        'approved_at' : att_req.approved_at,
                        'leave_type' : att_req.leave_type_changed if att_req.leave_type_changed else att_req.leave_type,
                        'is_late_conveyance' : att_req.is_late_conveyance,
                        'vehicle_type' : att_req.vehicle_type.name if att_req.vehicle_type else '',
                        'vehicle_type_id' : att_req.vehicle_type.id if att_req.vehicle_type else '',
                        'is_conveyance' : att_req.is_conveyance,
                        'from_place' : att_req.from_place,
                        'to_place' : att_req.to_place,
                        'conveyance_expense' : att_req.conveyance_expense,
                        'approved_expenses' : att_req.approved_expenses,
                        'conveyance_remarks' : att_req.conveyance_remarks,
                        'leave_type_changed' : att_req.leave_type_changed,
                        'leave_type_changed_period' : att_req.leave_type_changed_period,
                        'checkin_benchmark' : att_req.checkin_benchmark,
                        'lock_status' : att_req.lock_status,
                        'conveyance_purpose' : att_req.conveyance_purpose,
                        'conveyance_alloted_by' : att_req.conveyance_alloted_by.id if att_req.conveyance_alloted_by else '',
                        'conveyance_alloted_by_name' : (att_req.conveyance_alloted_by.first_name if att_req.conveyance_alloted_by else '') + " " +(att_req.conveyance_alloted_by.last_name if att_req.conveyance_alloted_by else '')
                    }                  

                    attendance_request_list.append(attendance_request_dict)
            data['attendance_request'] = attendance_request_list
            data['is_late_conveyance'] = is_late_conveyance
            data['late_conveyance_id'] = late_conveyance_id
            data['is_late_conveyance_completed'] = is_late_conveyance_completed
            data['is_attendance_request'] = is_attendance_request
            if day_remarks:
                data['day_remarks'] = day_remarks

        # if response.data:
        day_list = self.last_day_of_month(self.date_range_str,self.date_range_end)
        # print("date_list_data",date_list_data)
        joining_date = None
        joining_date = TCoreUserDetail.objects.only('joining_date').get(cu_user=emp_id).joining_date.date()
        new_dict = {}
        for day in day_list:
            if day not in date_list_data:
                # print("day", day)
                new_dict={
                    'id' : None,
                    'date' : day.strftime("%Y-%m-%dT%H:%M:%S"),
                    'is_present' : False,
                    "is_attendance_request": False,
                    "day_remarks": "Absent",
                    "attendance_request":[],
                    "is_late_conveyance":False,
                    "is_late_conveyance_completed":False,
                    "is_deleted":False,
                    "login_time": "",
                    "logout_time": ""
                    }
                if joining_date:
                    if joining_date > day:
                        new_dict['day_remarks']="Not Joined"
                    # elif joining_date == day:
                    #     new_dict['day_remarks']="Joining date"
                    
                response.data.append(new_dict)

        response.data = self.list_synchronization(list(response.data))

        return response
    def last_day_of_month(self,sdate, edate):
        days_list = []
        # sdate = date(2008, 8, 15)   # start date
        # edate = date(2008, 9, 15)   # end date
        print("sdate",sdate   , edate)

        delta = edate - sdate       # as timedelta

        for i in range(delta.days + 1):
            day = sdate + timedelta(days=i)
            # print(day)
            days_list.append(day)
        return days_list


    def list_synchronization(self, list_data: list)-> list:
        data = pd.DataFrame(list_data)
        data = data.replace(np.nan, 0, regex=True)
        data.sort_values("date", axis = 0, ascending = True, inplace = True,)
        col_list = data.columns.values
        row_list = data.values.tolist()
        total_result = list()
        for row in row_list:
            data_dict = dict(zip(col_list,row))
            total_result.append(data_dict)
        list_data = total_result
        return list_data

class AttendanceAdvanceLeaveAddView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EmployeeAdvanceLeaves.objects.filter(is_deleted=False)
    serializer_class = AttendanceAdvanceLeaveAddSerializer
    #pagination_class = CSPageNumberPagination

    # def get_queryset(self):
    #     emp_id = self.request.query_params.get('emp_id', None)
    #     if self.queryset.count():
    #         return self.queryset.filter(employee_id=emp_id)
    #     else:
    #         return self.queryset

    # @response_modify_decorator_list_or_get_after_execution_for_pagination
    # def get(self, request, *args, **kwargs):
    #     response=super(AttendanceAdvanceLeaveListView,self).get(self, request, args, kwargs)
    #     for data in response.data['results']:
    #         print(data['approved_status'])
    #         data['approved_status']=data['approved_status'].capitalize()
    #     return response

class ETaskAttendanceApprovalList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = ETaskAttendanceApprovalListSerializer
    pagination_class = CSPageNumberPagination
    queryset = AttendanceApprovalRequest.objects.filter(Q(is_requested=True)&
                                                        Q(lock_status=False)&
                                                        Q(is_deleted=False)&
                                                        Q(is_late_conveyance=False)&
                                                        Q(checkin_benchmark=False)&
                                                        (Q(approved_status='pending')|
                                                        Q(approved_status='relese')))
    
    def get_queryset(self):
        filter={}
        team_approval_flag = self.request.query_params.get('team_approval_flag', None)
        search_sort_flag = True
        if team_approval_flag == '1':
            login_user_details = self.request.user
            #print('login_user_details',login_user_details)
            #print('login_user_details',login_user_details.is_superuser)
            if login_user_details.is_superuser == False:
                users_list_under_the_login_user = TCoreUserDetail.objects.filter(
                    reporting_head = login_user_details,
                    cu_is_deleted = False
                ).values_list('cu_user')
                #print('users_list_under_the_login_user',users_list_under_the_login_user)
                if users_list_under_the_login_user:
                    attendence_id_list = Attendance.objects.filter(
                                employee__in=users_list_under_the_login_user,
                                is_deleted = False
                                ).values_list('id')
                    print('attedence_details',attendence_id_list)
                    if attendence_id_list:
                        
                        self.queryset = self.queryset.filter(attendance__in=attendence_id_list)
                    else:
                        search_sort_flag = False
                        self.queryset = self.queryset
                else:
                    search_sort_flag = False
                    self.queryset = []
                
            else:
                search_sort_flag = True
                self.queryset = self.queryset   

        if search_sort_flag:
            field_name = self.request.query_params.get('field_name', None)
            order_by = self.request.query_params.get('order_by', None)
            search= self.request.query_params.get('search', None)
            request_type=self.request.query_params.get('request_type', None)
        
            if field_name and order_by:      
                if field_name =='date' and order_by=='asc':
                    return self.queryset.all().order_by('duration_start__date')
                if field_name =='date' and order_by=='desc':
                    return self.queryset.all().order_by('-duration_start__date')
                if field_name =='duration_start' and order_by=='asc':
                    return self.queryset.all().order_by('duration_start')
                if field_name =='duration_start' and order_by=='desc':
                    return self.queryset.all().order_by('-duration_start')

                if field_name =='duration_end' and order_by=='asc':
                    return self.queryset.all().order_by('duration_end')
                if field_name =='duration_end' and order_by=='desc':
                    return self.queryset.all().order_by('-duration_end')

                if field_name =='duration' and order_by=='asc':
                    return self.queryset.all().order_by('duration')
                if field_name =='duration' and order_by=='desc':
                    return self.queryset.all().order_by('-duration')
            
            if request_type:
                request_type_list=request_type.split(',')
                '''
                    Added By Rupam Hazra For Android end [29-12-2019] 
                    #Line No - 2719 - 2722
                '''
                if 'OD' in request_type_list:
                    request_type_list.remove('OD')
                    request_type_list.append('POD')
                    request_type_list.append('FOD')
                filter['request_type__in']= request_type_list

            # if leave_type:
            #     leave_type_list=leave_type.split(',')
            #     filter['leave_type__in']= leave_type_list

            if search :
                search_data = list(map(str,search.split(" ")))
                print("This is if condition entry")
                if len(search.split(" "))>0 and len(search.split(" "))<2:
                    print("length 1 hai ")
                    queryset = self.queryset.filter((Q(attendance__employee__first_name__icontains=search_data[0])|Q(attendance__employee__last_name__icontains=search_data[0])),
                                                    is_deleted=False,**filter)                            
                    return queryset
                elif len(search.split(" "))>1:
                    print("length 2 hai ")
                    queryset = self.queryset.filter((Q(attendance__employee__first_name__icontains=search_data[0]) & Q(attendance__employee__last_name__icontains=search_data[1])),
                                                    is_deleted=False,**filter)
                    return queryset                

            else:
                queryset = self.queryset.filter(is_deleted=False,**filter)
                return queryset
           
        else:
            return []
       

    @response_modify_decorator_list_or_get_after_execution_for_pagination
    def get(self, request, *args, **kwargs):
        response=super(ETaskAttendanceApprovalList, self).get(self, request, args, kwargs)
        return response

class ETaskAttendanceApprovaGracelList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = ETaskAttendanceApprovalGraceListSerializer
    pagination_class = CSPageNumberPagination
    queryset = AttendanceApprovalRequest.objects.filter(Q(is_requested=True)&
                                                        Q(lock_status=False)&
                                                        Q(is_deleted=False)&
                                                        Q(is_late_conveyance=False)&
                                                        Q(checkin_benchmark=False)&
                                                        Q(request_type='GR')&
                                                        (Q(approved_status='pending')|
                                                        Q(approved_status='relese')))
    def get_queryset(self):
        filter={}
        team_approval_flag = self.request.query_params.get('team_approval_flag', None)
        search_sort_flag = True
        if team_approval_flag == '1':
            login_user_details = self.request.user
            #print('login_user_details',login_user_details)
            #print('login_user_details',login_user_details.is_superuser)
            if login_user_details.is_superuser == False:
                users_list_under_the_login_user = TCoreUserDetail.objects.filter(
                    reporting_head = login_user_details,
                    cu_is_deleted = False
                ).values_list('cu_user')
                #print('users_list_under_the_login_user',users_list_under_the_login_user)
                if users_list_under_the_login_user:
                    attendence_id_list = Attendance.objects.filter(
                                employee__in=users_list_under_the_login_user,
                                is_deleted = False
                                ).values_list('id')
                    print('attedence_details',attendence_id_list)
                    if attendence_id_list:
                        
                        self.queryset = self.queryset.filter(attendance__in=attendence_id_list)
                    else:
                        search_sort_flag = False
                        self.queryset = self.queryset
                else:
                    search_sort_flag = False
                    self.queryset = []
                
            else:
                search_sort_flag = True
                self.queryset = self.queryset   

        if search_sort_flag:
            field_name = self.request.query_params.get('field_name', None)
            order_by = self.request.query_params.get('order_by', None)
            search= self.request.query_params.get('search', None)
            request_type=self.request.query_params.get('request_type', None)
            sort_field="-id"
        
            if field_name and order_by:      
                if field_name =='date' and order_by=='asc':
                    # return self.queryset.all().order_by('duration_start__date')
                    sort_field='duration_start__date'
                if field_name =='date' and order_by=='desc':
                    sort_field='-duration_start__date'
                    # return self.queryset.all().order_by('-duration_start__date')
                if field_name =='duration_start' and order_by=='asc':
                    sort_field='duration_start'
                    # return self.queryset.all().order_by('duration_start')
                if field_name =='duration_start' and order_by=='desc':
                    sort_field='-duration_start'
                    # return self.queryset.all().order_by('-duration_start')

                if field_name =='duration_end' and order_by=='asc':
                    sort_field='duration_end'
                    # return self.queryset.all().order_by('duration_end')
                if field_name =='duration_end' and order_by=='desc':
                    sort_field='-duration_end'
                    # return self.queryset.all().order_by('-duration_end')

                if field_name =='duration' and order_by=='asc':
                    sort_field='duration'
                    # return self.queryset.all().order_by('duration')
                if field_name =='duration' and order_by=='desc':
                    sort_field='-duration'
                    # return self.queryset.all().order_by('-duration')
            
            # if request_type:
            #     request_type_list=request_type.split(',')
            #     filter['request_type__in']= request_type_list

            # if leave_type:
            #     leave_type_list=leave_type.split(',')
            #     filter['leave_type__in']= leave_type_list

            if search :
                search_data = list(map(str,search.split(" ")))
                print("This is if condition entry")
                if len(search.split(" "))>0 and len(search.split(" "))<2:
                    print("length 1 hai ")
                    queryset = self.queryset.filter((Q(attendance__employee__first_name__icontains=search_data[0])|Q(attendance__employee__last_name__icontains=search_data[0])),
                                                    is_deleted=False,**filter).order_by(sort_field)                            
                    return queryset
                elif len(search.split(" "))>1:
                    print("length 2 hai ")
                    queryset = self.queryset.filter((Q(attendance__employee__first_name__icontains=search_data[0]) & Q(attendance__employee__last_name__icontains=search_data[1])),
                                                    is_deleted=False,**filter).order_by(sort_field)
                    return queryset                
            else:
                queryset = self.queryset.filter(is_deleted=False,**filter).order_by(sort_field)
                return queryset
        else:
            return []
       
  
    @response_modify_decorator_list_or_get_after_execution_for_pagination
    def get(self, request, *args, **kwargs):
        response=super(ETaskAttendanceApprovaGracelList, self).get(self, request, args, kwargs)
        return response

class ETaskAttendanceApprovaWithoutGracelList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = ETaskAttendanceApprovaWithoutGracelSerializer
    pagination_class = CSPageNumberPagination
    queryset = AttendanceApprovalRequest.objects.filter(Q(is_requested=True)&
                                                        Q(lock_status=False)&
                                                        Q(is_deleted=False)&
                                                        Q(is_late_conveyance=False)&
                                                        Q(checkin_benchmark=False)&
                                                        (Q(request_type='HD')|
                                                        Q(request_type='FD')|
                                                        Q(request_type='WO')|
                                                        Q(request_type='OD')|
                                                        Q(request_type='FOD')|
                                                        Q(request_type='POD')|
                                                        Q(request_type='LC'))&
                                                        (Q(approved_status='pending')|
                                                        Q(approved_status='relese')))
    
    def get_queryset(self):
        filter={}
        sort_field="-id"
        team_approval_flag = self.request.query_params.get('team_approval_flag', None)
        search_sort_flag = True
        if team_approval_flag == '1':
            login_user_details = self.request.user
            #print('login_user_details',login_user_details)
            #print('login_user_details',login_user_details.is_superuser)
            if login_user_details.is_superuser == False:
                users_list_under_the_login_user = TCoreUserDetail.objects.filter(
                    reporting_head = login_user_details,
                    cu_is_deleted = False
                ).values_list('cu_user')
                #print('users_list_under_the_login_user',users_list_under_the_login_user)
                if users_list_under_the_login_user:
                    attendence_id_list = Attendance.objects.filter(
                                employee__in=users_list_under_the_login_user,
                                is_deleted = False
                                ).values_list('id')
                    print('attedence_details',attendence_id_list)
                    if attendence_id_list:
                        
                        self.queryset = self.queryset.filter(attendance__in=attendence_id_list)
                    else:
                        search_sort_flag = False
                        self.queryset = self.queryset
                else:
                    search_sort_flag = False
                    self.queryset = []
                
            else:
                search_sort_flag = True
                self.queryset = self.queryset   

        if search_sort_flag:
            field_name = self.request.query_params.get('field_name', None)
            order_by = self.request.query_params.get('order_by', None)
            search= self.request.query_params.get('search', None)
            request_type=self.request.query_params.get('request_type', None)
        
            if field_name and order_by:      
                if field_name =='date' and order_by=='asc':
                    sort_field="duration_start__date"
                    # return self.queryset.all().order_by('duration_start__date')
                if field_name =='date' and order_by=='desc':
                    sort_field="-duration_start__date"
                    # return self.queryset.all().order_by('-duration_start__date')
                if field_name =='duration_start' and order_by=='asc':
                    sort_field="duration_start"
                    # return self.queryset.all().order_by('duration_start')
                if field_name =='duration_start' and order_by=='desc':
                    sort_field="-duration_start"
                    # return self.queryset.all().order_by('-duration_start')

                if field_name =='duration_end' and order_by=='asc':
                    sort_field="duration_end"
                    # return self.queryset.all().order_by('duration_end')
                if field_name =='duration_end' and order_by=='desc':
                    sort_field="-duration_end"
                    # return self.queryset.all().order_by('-duration_end')

                if field_name =='duration' and order_by=='asc':
                    sort_field="duration"
                    # return self.queryset.all().order_by('duration')
                if field_name =='duration' and order_by=='desc':
                    sort_field="-duration"
                    # return self.queryset.all().order_by('-duration')
            
            if request_type:
                request_type_list=request_type.split(',')
                filter['request_type__in']= request_type_list

            # if leave_type:
            #     leave_type_list=leave_type.split(',')
            #     filter['leave_type__in']= leave_type_list

            if search :
                search_data = list(map(str,search.split(" ")))
                print("This is if condition entry")
                if len(search.split(" "))>0 and len(search.split(" "))<2:
                    print("length 1 hai ")
                    queryset = self.queryset.filter((Q(attendance__employee__first_name__icontains=search_data[0])|Q(attendance__employee__last_name__icontains=search_data[0])),
                                                    is_deleted=False,**filter).order_by(sort_field)                            
                    return queryset
                elif len(search.split(" "))>1:
                    print("length 2 hai ")
                    queryset = self.queryset.filter((Q(attendance__employee__first_name__icontains=search_data[0]) & Q(attendance__employee__last_name__icontains=search_data[1])),
                                                    is_deleted=False,**filter).order_by(sort_field)
                    return queryset                

            else:
                queryset = self.queryset.filter(is_deleted=False,**filter).order_by(sort_field)
                return queryset
           
        else:
            return []
       


  
    @response_modify_decorator_list_or_get_after_execution_for_pagination
    def get(self, request, *args, **kwargs):
        response=super(ETaskAttendanceApprovaWithoutGracelList, self).get(self, request, args, kwargs)
        return response

class ETaskAttendanceApprovalView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class =  ETaskAttendanceApprovalSerializer
    queryset = AttendanceApprovalRequest.objects.filter(Q(is_requested=True)&
                                                        Q(lock_status=False)&
                                                        Q(is_deleted=False)&
                                                        (Q(approved_status='pending')|
                                                        Q(approved_status='relese')))

class ETaskAttendanceApprovalModifyView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class =  ETaskAttendanceApprovalModifySerializer
    queryset = AttendanceApprovalRequest.objects.filter(Q(is_requested=True)&
                                                        Q(lock_status=False)&
                                                        Q(is_deleted=False)&
                                                        (Q(approved_status='pending')|
                                                        Q(approved_status='relese')))

class AttendanceApprovalReportView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = ETaskAttendanceApprovalListSerializer
    pagination_class = CSPageNumberPagination
    queryset = AttendanceApprovalRequest.objects.filter(Q(is_requested=True)&
                                                        Q(lock_status=False)&
                                                        Q(is_deleted=False)&
                                                        Q(is_late_conveyance=False)&
                                                        Q(checkin_benchmark=False)&
                                                        (Q(approved_status='approved')|
                                                        Q(approved_status='reject')) &
                                                        (Q(request_type='HD')|
                                                        Q(request_type='FD'))
                                                        )
    def get_queryset(self):
        team_approval_flag = self.request.query_params.get('team_approval_flag', None)
        search_sort_flag = True
        if team_approval_flag == '1':
            login_user_details = self.request.user
            #print('login_user_details',login_user_details)
            #print('login_user_details',login_user_details.is_superuser)
            if login_user_details.is_superuser == False:
                users_list_under_the_login_user = TCoreUserDetail.objects.filter(
                    reporting_head = login_user_details,
                    cu_is_deleted = False
                ).values_list('cu_user')
                #print('users_list_under_the_login_user',users_list_under_the_login_user)
                if users_list_under_the_login_user:
                    attendence_id_list = Attendance.objects.filter(
                                employee__in=users_list_under_the_login_user,
                                is_deleted = False
                                ).values_list('id')
                    print('attedence_details',attendence_id_list)
                    if attendence_id_list:
                        
                        self.queryset = self.queryset.filter(attendance__in=attendence_id_list)
                    else:
                        search_sort_flag = False
                        self.queryset = self.queryset
                else:
                    search_sort_flag = False
                    self.queryset = []
                
            else:
                search_sort_flag = True
                self.queryset = self.queryset   

        if search_sort_flag:
            filter={}
            sort_field='-id'
            search = self.request.query_params.get('search', None)
            request_type=self.request.query_params.get('request_type', None)
            from_date = self.request.query_params.get('from_date', None)
            to_date = self.request.query_params.get('to_date', None)
            leave_type=self.request.query_params.get('leave_type', None)
            approved_type=self.request.query_params.get('approved_type', None)
            field_name = self.request.query_params.get('field_name', None)
            order_by = self.request.query_params.get('order_by', None)
            queryset_all = EmployeeAdvanceLeaves.objects.none()

            dept_filter = self.request.query_params.get('dept_filter', None)

            if field_name and order_by:
                if field_name =='duration_start' and order_by=='asc':
                    sort_field='duration_start'
                    # return self.queryset.filter(is_deleted=False).order_by('duration_start')
                elif field_name =='duration_start' and order_by=='desc':
                    sort_field='-duration_start'
                    # return self.queryset.filter(is_deleted=False).order_by('-duration_start')
                elif field_name =='duration_end' and order_by=='asc':
                    sort_field='duration_end'
                    # return self.queryset.filter(is_deleted=False).order_by('duration_end')
                elif field_name =='duration_end' and order_by=='desc':
                    sort_field='-duration_end'
                    # return self.queryset.filter(is_deleted=False).order_by('-duration_end')
                elif field_name =='date_of_application' and order_by=='asc':
                    sort_field='duration_start__date'
                    # return self.queryset.filter(is_deleted=False).order_by('duration_start__date')
                elif field_name =='date_of_application' and order_by=='desc':
                    sort_field='-duration_start__date'
                    # return self.queryset.filter(is_deleted=False).order_by('-duration_start__date')
                elif field_name =='duration' and order_by=='asc':
                    sort_field='duration'
                    # return self.queryset.filter(is_deleted=False).order_by('duration')
                elif field_name =='duration' and order_by=='desc':
                    sort_field='-duration'
                    # return self.queryset.filter(is_deleted=False).order_by('-duration')

            if self.queryset.count():
                if dept_filter:
                    dept_list = dept_filter.split(',')
                    emp_list = TCoreUserDetail.objects.filter(department__in=dept_list).values_list('cu_user',flat=True)
                    filter['attendance__employee__in'] = emp_list

                if from_date and to_date:
                    start_object = datetime.strptime(from_date, '%Y-%m-%d').date()
                    filter['duration_start__date__gte'] = start_object
                    end_object = datetime.strptime(to_date, '%Y-%m-%d').date()
                    filter['duration_start__date__lte'] = end_object + timedelta(days=1)

                if request_type:
                    request_type_list=request_type.split(',')
                    filter['request_type__in']= request_type_list
                if leave_type:
                    leave_type_list=leave_type.split(',')
                    filter['leave_type__in']= leave_type_list
                if approved_type:
                    approved_type_list=approved_type.split(',')
                    filter['approved_status__in']= approved_type_list
                if search :
                    search_data = list(map(str,search.split(" ")))
                    print("This is if condition entry")
                    if len(search.split(" "))>0 and len(search.split(" "))<2:
                        print("length 1 hai ")
                        queryset = self.queryset.filter((Q(attendance__employee__first_name__icontains=search_data[0])|Q(attendance__employee__last_name__icontains=search_data[0])),
                                                        is_deleted=False,**filter).order_by(sort_field)                            
                        queryset_all=(queryset_all|queryset) 
                        return queryset_all       

                    elif len(search.split(" "))>1:
                        print("length 2 hai ")
                        queryset = self.queryset.filter((Q(attendance__employee__first_name__icontains=search_data[0]) & Q(attendance__employee__last_name__icontains=search_data[1])),
                                                        is_deleted=False,**filter).order_by(sort_field)
                        queryset_all=(queryset_all|queryset) 
                        return queryset_all                
                # if search :
                #     print("This is if condition entry")
                #     for name in search.split(" "):

                #         queryset = self.queryset.filter((Q(attendance__employee__first_name__icontains=name)|Q(attendance__employee__last_name__icontains=name)),
                #                                         is_deleted=False,**filter)
    
                #         queryset_all=(queryset_all|queryset)                     
                #         return queryset_all
                else:
                    queryset = self.queryset.filter(is_deleted=False,**filter).order_by(sort_field)
                    return queryset

            else:
                return queryset_all
        else:
            return list()
    @response_modify_decorator_list_or_get_after_execution_for_pagination
    def get(self, request, *args, **kwargs):
        response=super(AttendanceApprovalReportView, self).get(self, request, args, kwargs)
        return response

class AttendanceVehicleTypeMasterAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = VehicleTypeMaster.objects.filter(is_deleted=False)
    serializer_class = AttendanceVehicleTypeMasterAddSerializer

    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response

class AttendanceVehicleTypeMasterEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = VehicleTypeMaster.objects.filter(is_deleted=False)
    serializer_class = AttendanceVehicleTypeMasterEditSerializer

    # @response_modify_decorator_update
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response

class AttendanceVehicleTypeMasterDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = VehicleTypeMaster.objects.filter(is_deleted=False)
    serializer_class = AttendanceVehicleTypeMasterDeleteSerializer

    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response

class AttendanceAdminSummaryListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = Attendance.objects.filter(is_deleted=False)
    serializer_class = AttendanceAdminSummaryListSerializer
    # pagination_class = CSPageNumberPagination

    def get_queryset(self):
        #print('queryset',self.queryset)
        team_approval_flag = self.request.query_params.get('team_approval_flag', None)
        search_sort_flag = True
        if team_approval_flag == '1':
            login_user_details = self.request.user
            #print('login_user_details',login_user_details)
            #print('login_user_details',login_user_details.is_superuser)
            if login_user_details.is_superuser == False:
                users_list_under_the_login_user = TCoreUserDetail.objects.filter(
                    reporting_head = login_user_details,
                    cu_is_deleted = False
                ).values_list('cu_user')
                #print('users_list_under_the_login_user',users_list_under_the_login_user)
                if users_list_under_the_login_user:
                    attendence= Attendance.objects.filter(
                                employee__in=users_list_under_the_login_user,
                                is_deleted = False
                                )
                    print('attedence_details',attendence)
                    if attendence:
                        search_sort_flag = True
                        self.queryset = attendence
                    else:
                        search_sort_flag = False
                else:
                    search_sort_flag = False
                    
                
            else:
                search_sort_flag = True
                self.queryset = self.queryset   

        if search_sort_flag:
            blank_queryset = Attendance.objects.none()
            print('blank_queryset',blank_queryset)
            emp_id = self.request.query_params.get('emp_id', None)
            current_date = self.request.query_params.get('current_date', None)
            month = self.request.query_params.get('month', None)
            year = self.request.query_params.get('year', None)
            filter = {}
            date_range = None
           
                #print("self.queryset.count()",self.queryset.count())
            if month and year and emp_id:
                date_range = AttendenceMonthMaster.objects.filter(month=month,month_end__year=year).values('month_start__date','month_end__date')
                print("date_range",date_range)

                if date_range:
                    print("This is if")
                    filter['employee']=emp_id
                    filter['date__date__gte'] = date_range[0]['month_start__date']
                    filter['date__date__lte'] = date_range[0]['month_end__date']

            if filter :
                # print('filter',self.queryset.filter(**filter))
                return self.queryset.filter(**filter).order_by('date')
            else:
                # print('else filter',self.queryset)
                return self.queryset.filter(is_deleted=False).order_by('date')
        else:
            return []

    @response_modify_decorator_get_after_execution
    def get(self, request, *args, **kwargs):
        print('entry test')
        print(self.queryset)
        response=super(AttendanceAdminSummaryListView,self).get(self, request, args, kwargs)
        # print("response.data['results']",response.data)
        # print("response.data['results']",response.data['results'])
        attendance_request_dict = {}
        for data in response.data:
            attendance_request = AttendanceApprovalRequest.objects.filter(attendance=data['id'],is_deleted=False)
            attendance_request_list = []
            conveyance_dict = {}
            conveyance_list = []
            data['is_attendance_request'] = True
            daily_duration = 0
            daily_grace = 0
            cng_leave_type = None
            oth_leave_type = None
            daily_leave_type = None
            daily_leave_period = None
            daily_leave_approval = None
            cng_leave_period = None
            oth_leave_period = None
            day_remarks = None
            for att_req in attendance_request:
                if att_req.leave_type_changed is not None:
                    day_remarks = 'Leave ('+att_req.leave_type_changed+')'
                elif att_req.leave_type_changed is None and att_req.leave_type is not None:
                    day_remarks = 'Leave ('+att_req.leave_type+')'
                elif att_req.approved_status=='approved' and att_req.request_type =='FOD':
                    day_remarks = 'OD'


                if att_req.leave_type_changed_period=='GR':
                    daily_grace+=att_req.duration
                elif att_req.request_type=='GR':
                    daily_grace+=att_req.duration
                elif att_req.checkin_benchmark == True:
                    daily_grace+=att_req.duration
                if att_req.leave_type_changed:
                    cng_leave_type= att_req.leave_type_changed
                    if att_req.leave_type_changed_period=='FD':
                        cng_leave_period = 1
                    elif att_req.leave_type_changed_period=='HD':
                        cng_leave_period = 0.5
                elif att_req.leave_type:
                    oth_leave_type= att_req.leave_type
                    if att_req.request_type=='FD':
                        oth_leave_period = 1
                    elif att_req.request_type=='HD':
                        oth_leave_period = 0.5

                if cng_leave_type:
                    daily_leave_type=cng_leave_type
                    daily_leave_period=cng_leave_period
                elif oth_leave_type:
                    daily_leave_type=oth_leave_type
                    daily_leave_period=oth_leave_period

                if att_req.approved_status == 'relese' or att_req.approved_status == 'pending' or att_req.is_requested== True:
                    data['is_attendance_request'] = False
                if att_req.is_late_conveyance==False and att_req.checkin_benchmark==False:
                    attendance_request_dict = {
                        'id' : att_req.id,
                        'duration_start' : att_req.duration_start,
                        'duration_end' : att_req.duration_end,
                        'duration' : att_req.duration,
                        'request_type' : att_req.leave_type_changed_period if att_req.leave_type_changed_period else att_req.request_type,
                        'is_requested' : att_req.is_requested,
                        'request_date' : att_req.request_date,
                        'justification' : att_req.justification,
                        'approved_status' : att_req.approved_status,
                        'remarks' : att_req.remarks,
                        'justified_by' : att_req.justified_by_id,
                        'justified_at' : att_req.justified_at,
                        'approved_by' : att_req.approved_by_id,
                        'approved_at' : att_req.approved_at,
                        'leave_type' : att_req.leave_type_changed if att_req.leave_type_changed else att_req.leave_type,
                        'is_late_conveyance' : att_req.is_late_conveyance,
                        'vehicle_type' : att_req.vehicle_type.name if att_req.vehicle_type else '',
                        'vehicle_type_id' : att_req.vehicle_type.id if att_req.vehicle_type else '',
                        'is_conveyance' : att_req.is_conveyance,
                        'from_place' : att_req.from_place,
                        'to_place' : att_req.to_place,
                        'conveyance_expense' : att_req.conveyance_expense,
                        'approved_expenses' : att_req.approved_expenses,
                        'conveyance_remarks' : att_req.conveyance_remarks,
                        'leave_type_changed' : att_req.leave_type_changed,
                        'leave_type_changed_period' : att_req.leave_type_changed_period,
                        'checkin_benchmark' : att_req.checkin_benchmark,
                        'lock_status' : att_req.lock_status
                    }
                    attendance_request_list.append(attendance_request_dict)

                if att_req.from_place and att_req.to_place:
                    first_name = att_req.conveyance_alloted_by.first_name if att_req.conveyance_alloted_by else ''
                    last_name = att_req.conveyance_alloted_by.last_name if att_req.conveyance_alloted_by else ''
                    conveyance_dict = {
                        'vehicle_type' : att_req.vehicle_type.name if att_req.vehicle_type else '',
                        'vehicle_type_desctiption' : att_req.vehicle_type.description if att_req.vehicle_type else '',
                        'vehicle_type_id' : att_req.vehicle_type.id if att_req.vehicle_type else '',
                        'from_place' : att_req.from_place,
                        'to_place' : att_req.to_place,
                        'conveyance_expense' : att_req.conveyance_expense,
                        'approved_expenses' : att_req.approved_expenses,
                        'conveyance_remarks' : att_req.conveyance_remarks,
                        'conveyance_purpose' : att_req.conveyance_purpose,
                        'conveyance_alloted_by' : first_name + " " + last_name,
                        'conveyance_approval' : att_req.conveyance_approval,
                        'conveyance_approval_name' :att_req.get_conveyance_approval_display(),
                        'conveyance_durations' : att_req.duration,
                        'duration_start': att_req.duration_start,
                        'duration_end': att_req.duration_end,
                        'is_late_conveyance': att_req.is_late_conveyance
                    }
                    conveyance_list.append(conveyance_dict)


            print("daily_grace", daily_grace)
            data['conveyance_details'] = conveyance_list
            data['daily_grace'] = daily_grace
            data['daily_leave_type'] = daily_leave_type
            data['daily_leave_period'] = daily_leave_period
            data['attendance_request'] = attendance_request_list
            if day_remarks:
                data['day_remarks'] = day_remarks

        return response

class AttendanceAdminDailyListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = Attendance.objects.filter(is_deleted=False)
    serializer_class = AttendanceAdminDailyListSerializer
    pagination_class = CSPageNumberPagination

    def get_queryset(self):
        team_approval_flag = self.request.query_params.get('team_approval_flag', None)
        search_sort_flag = True
        if team_approval_flag == '1':
            login_user_details = self.request.user
            #print('login_user_details',login_user_details)
            #print('login_user_details',login_user_details.is_superuser)
            if login_user_details.is_superuser == False:
                users_list_under_the_login_user = TCoreUserDetail.objects.filter(
                    reporting_head = login_user_details,
                    cu_is_deleted = False
                ).values_list('cu_user')
                #print('users_list_under_the_login_user',users_list_under_the_login_user)
                if users_list_under_the_login_user:
                    attendence= Attendance.objects.filter(
                                employee__in=users_list_under_the_login_user,
                                is_deleted = False
                                )
                    print('attedence_details',attendence)
                    if attendence:
                        search_sort_flag = True
                        self.queryset = attendence
                    else:
                        search_sort_flag = False
                else:
                    search_sort_flag = False
                    
                
            else:
                search_sort_flag = True
                self.queryset = self.queryset   


        if search_sort_flag:
            start_date = self.request.query_params.get('start_date', None)
            end_date = self.request.query_params.get('end_date', None)
            search = self.request.query_params.get('search', None)
            leave_type = self.request.query_params.get('leave_type', None)
            field_name = self.request.query_params.get('field_name', None)
            order_by = self.request.query_params.get('order_by', None)
            department = self.request.query_params.get('department', None)
            designation = self.request.query_params.get('designation', None)
            sort_field='-id'
            filter = {}
            date_range = None
            if self.queryset.count():
                print("self.queryset.count()",self.queryset.count())
                if field_name and order_by:
                    if field_name == 'date' and order_by == 'asc':
                        sort_field='date'
                        # return self.queryset.filter(is_deleted=False).order_by('date')
                    elif field_name == 'date' and order_by == 'desc':
                        sort_field='-date'
                        # return self.queryset.filter(is_deleted=False).order_by('-date')
                    elif field_name == 'login_time' and order_by == 'asc':
                        sort_field='login_time'
                        # return self.queryset.filter(is_deleted=False).order_by('login_time')
                    elif field_name == 'login_time' and order_by == 'desc':
                        sort_field='-login_time'
                        # return self.queryset.filter(is_deleted=False).order_by('-login_time')
                    elif field_name == 'logout_time' and order_by == 'asc':
                        sort_field='logout_time'
                        # return self.queryset.filter(is_deleted=False).order_by('logout_time')
                    elif field_name == 'logout_time' and order_by == 'desc':
                        sort_field='-logout_time'
                        # return self.queryset.filter(is_deleted=False).order_by('-logout_time')
                
            if start_date or end_date or designation or department or search:
                if start_date and end_date:
                    start_object = datetime.strptime(start_date, '%Y-%m-%d').date()
                    filter['date__gte'] = start_object
                    end_object = datetime.strptime(end_date, '%Y-%m-%d').date()
                    filter['date__lte'] = end_object + timedelta(days=1)

                if department and designation:
                    desi_dep_id=TCoreUserDetail.objects.filter(designation=designation,department=department).values('cu_user')
                    print(desi_dep_id)
                    filter['employee__in'] = [x['cu_user'] for x in desi_dep_id ]
                elif department :
                    department_id=TCoreUserDetail.objects.filter(department=department).values('cu_user')
                    print(department_id)
                    filter['employee__in'] = [x['cu_user'] for x in department_id ]
                    print(filter)
                elif designation:
                    designation_id=TCoreUserDetail.objects.filter(designation=designation).values('cu_user')
                    print(designation_id)
                    filter['employee__in'] = [x['cu_user'] for x in designation_id ]
                    print(filter)
                
                if search :
                    search_data = list(map(str,search.split(" ")))
                    print("This is if condition entry")
                    if len(search.split(" "))>0 and len(search.split(" "))<2:
                        print("length 1 hai ")
                        queryset = self.queryset.filter((Q(employee__first_name__icontains=search_data[0])|Q(employee__last_name__icontains=search_data[0])),
                                                        is_deleted=False,**filter).order_by(sort_field)                            
                        return queryset
                    elif len(search.split(" "))>1:
                        print("length 2 hai ")
                        queryset = self.queryset.filter((Q(employee__first_name__icontains=search_data[0]) & Q(employee__last_name__icontains=search_data[1])),
                                                        is_deleted=False,**filter).order_by(sort_field) 
                        return queryset      

                # if search :
                #     print("This is if condition entry")
                #     for name in search.split(" "):

                #         queryset = self.queryset.filter((Q(employee__first_name__icontains=name)|Q(employee__last_name__icontains=name)),
                #                                         is_deleted=False,**filter)
                #         # print(queryset.query)                                
                #         return queryset
                else:
                    queryset = self.queryset.filter(is_deleted=False,**filter).order_by(sort_field) 
                    return queryset

            else:
                return self.queryset.filter(is_deleted=False).order_by(sort_field) 
        else:
            return []


    @response_modify_decorator_list_or_get_after_execution_for_pagination
    def get(self, request, *args, **kwargs):
        response=super(AttendanceAdminDailyListView,self).get(self, request, args, kwargs)
        # print("response.data['results']",response.data)
        attendance_request_dict = {}
        for data in response.data['results']:
            data['is_attendance_request'] = True
            is_late_conveyance = False
            is_late_conveyance_completed = False
            late_conveyance_id = None
            conveyance_dict = {}
            conveyance_list = []
            attendance_request = AttendanceApprovalRequest.objects.filter(attendance=data['id'],is_deleted=False)
            # print("attendance_request",attendance_request)
            # print('employee__first_name-->',data['employee'])
            # data['employee_name'] = data['employee']
            emp_name = User.objects.filter(id=data['employee']).values('first_name','last_name')
            if emp_name:
                first_name=emp_name[0]['first_name'] if emp_name[0]['first_name'] else ""
                last_name=emp_name[0]['last_name'] if emp_name[0]['last_name'] else ""
                data['employee_name'] = first_name + " " + last_name

            attendance_request_list = []
            day_remarks = None
            for att_req in attendance_request:
                if att_req.leave_type_changed is not None:
                    day_remarks = 'Leave ('+att_req.leave_type_changed+')'
                elif att_req.leave_type_changed is None and att_req.leave_type is not None:
                    day_remarks = 'Leave ('+att_req.leave_type+')'
                elif att_req.approved_status=='approved' and att_req.request_type =='FOD':
                    day_remarks = 'OD'

                if att_req.approved_status == 'relese' or att_req.approved_status == 'pending' or att_req.is_requested== True:
                    data['is_attendance_request'] = False
                if att_req.is_late_conveyance == True:
                    is_late_conveyance = True
                    late_conveyance_id = att_req.id
                if att_req.from_place and att_req.to_place and att_req.is_late_conveyance == True:
                    is_late_conveyance_completed = True


                benifit_id = HrmsBenefitsProvided.objects.get(benefits_name='conveyance')
                alloyance_per_day = HrmsUsersBenefits.objects.filter(user_id=data['employee'], benefits_id=benifit_id)
                allowance = [x.allowance for x in alloyance_per_day if alloyance_per_day]
                if allowance:
                    allowance_money = allowance[0]
                else:
                    allowance_money = 0.0

                if att_req.is_late_conveyance==False and att_req.checkin_benchmark==False:
                # if att_req.checkin_benchmark==False:
                    attendance_request_dict = {                        
                        'id' : att_req.id,
                        'duration_start' : att_req.duration_start,
                        'eligibility_amount' : allowance_money,
                        'duration_end' : att_req.duration_end,
                        'duration' : att_req.duration,
                        'request_type' : att_req.leave_type_changed_period if att_req.leave_type_changed_period else att_req.request_type,
                        'is_requested' : att_req.is_requested,
                        'request_date' : att_req.request_date,
                        'justification' : att_req.justification,
                        'approved_status' : att_req.approved_status,
                        'remarks' : att_req.remarks,
                        'justified_by' : att_req.justified_by_id,
                        'justified_at' : att_req.justified_at,
                        'approved_by' : att_req.approved_by_id,
                        'approved_at' : att_req.approved_at,
                        'leave_type' : att_req.leave_type_changed if att_req.leave_type_changed else att_req.leave_type,
                        'is_late_conveyance' : att_req.is_late_conveyance,
                        'vehicle_type' : att_req.vehicle_type.name if att_req.vehicle_type else '',
                        'vehicle_type_id' : att_req.vehicle_type.id if att_req.vehicle_type else '',
                        'is_conveyance' : att_req.is_conveyance,
                        'from_place' : att_req.from_place,
                        'to_place' : att_req.to_place,
                        'conveyance_expense' : att_req.conveyance_expense,
                        'approved_expenses' : att_req.approved_expenses,
                        'conveyance_purpose' : att_req.conveyance_purpose,
                        'conveyance_remarks' : att_req.conveyance_remarks,
                        'leave_type_changed' : att_req.leave_type_changed,
                        'leave_type_changed_period' : att_req.leave_type_changed_period,
                        'checkin_benchmark' : att_req.checkin_benchmark,
                        'lock_status' : att_req.lock_status,
                        'conveyance_approval' : att_req.get_conveyance_approval_display(),
                        'conveyance_approved_by' : att_req.conveyance_approved_by.id if att_req.conveyance_approved_by else '',
                        'conveyance_approved_by_name' : (att_req.conveyance_approved_by.first_name if att_req.conveyance_approved_by else '') + " " +(att_req.conveyance_approved_by.last_name if att_req.conveyance_approved_by else ''),
                        'conveyance_alloted_by' : att_req.conveyance_alloted_by.id if att_req.conveyance_alloted_by else '',
                        'conveyance_alloted_by_name' : (att_req.conveyance_alloted_by.first_name if att_req.conveyance_alloted_by else '') + " " +(att_req.conveyance_alloted_by.last_name if att_req.conveyance_alloted_by else '')
                    }
                    attendance_request_list.append(attendance_request_dict)

                if att_req.from_place and att_req.to_place:
                    first_name = att_req.conveyance_alloted_by.first_name if att_req.conveyance_alloted_by else ''
                    last_name = att_req.conveyance_alloted_by.last_name if att_req.conveyance_alloted_by else ''
                    conveyance_dict = {
                        'vehicle_type' : att_req.vehicle_type.name if att_req.vehicle_type else '',
                        'vehicle_type_desctiption' : att_req.vehicle_type.description if att_req.vehicle_type else '',
                        'vehicle_type_id' : att_req.vehicle_type.id if att_req.vehicle_type else '',
                        'from_place' : att_req.from_place,
                        'to_place' : att_req.to_place,
                        'conveyance_expense' : att_req.conveyance_expense,
                        'approved_expenses' : att_req.approved_expenses,
                        'conveyance_remarks' : att_req.conveyance_remarks,
                        'conveyance_purpose' : att_req.conveyance_purpose,
                        'conveyance_alloted_by' : first_name + " " + last_name,
                        'conveyance_approval' : att_req.conveyance_approval,
                        'conveyance_approval_name' :att_req.get_conveyance_approval_display(),
                        'conveyance_durations' : att_req.duration,
                        'duration_start': att_req.duration_start,
                        'duration_end': att_req.duration_end,
                        'is_late_conveyance': att_req.is_late_conveyance
                    }
                    conveyance_list.append(conveyance_dict)

            data['attendance_request'] = attendance_request_list
            data['is_late_conveyance'] = is_late_conveyance
            data['late_conveyance_id'] = late_conveyance_id
            data['is_late_conveyance_completed'] = is_late_conveyance_completed
            data['conveyance_details'] = conveyance_list
            if day_remarks:
                data['day_remarks'] = day_remarks

        return response

class AttendanceLeaveApprovalList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = AttendanceLeaveApprovalListSerializer
    pagination_class = CSPageNumberPagination
    queryset = AttendanceApprovalRequest.objects.filter(Q(is_requested=True)&
                                                        Q(lock_status=False)&
                                                        Q(is_deleted=False)&
                                                        Q(is_late_conveyance=False)&
                                                        Q(checkin_benchmark=False)&
                                                        ~Q(leave_type=None)&
                                                        (Q(approved_status='pending')|
                                                        Q(approved_status='relese')))
    def get_queryset(self):
        #print('self.queryset',self.queryset)
        team_approval_flag = self.request.query_params.get('team_approval_flag', None)
        sort_field='-id'
        search_sort_flag = True
        if team_approval_flag == '1':
            login_user_details = self.request.user
            print('login_user_details',login_user_details)
            print('login_user_details',login_user_details.is_superuser)
            if login_user_details.is_superuser == False:
                #print('check')
                users_list_under_the_login_user = TCoreUserDetail.objects.filter(
                    reporting_head = login_user_details,
                    cu_is_deleted = False
                ).values_list('cu_user')
                print('users_list_under_the_login_user',users_list_under_the_login_user)
                if users_list_under_the_login_user:
                    attendence_id_list = Attendance.objects.filter(
                                employee__in=users_list_under_the_login_user,
                                is_deleted = False
                                ).values_list('id')
                    print('attedence_details',attendence_id_list)
                    if attendence_id_list:
                        
                        result = self.queryset.filter(attendance__in=attendence_id_list)
                        print('result',result)
                        if result:
                            search_sort_flag = True
                            self.queryset = result
                        else:
                            search_sort_flag = False
                            #self.queryset = []
                        #print('self.queryset',self.queryset.query)
                    else:
                        search_sort_flag = False
                        #self.queryset = self.queryset
                else:
                    search_sort_flag = False
                    #self.queryset =  self.queryset
                
            else:
                search_sort_flag = True
                self.queryset = self.queryset  
        if search_sort_flag:     
            print('enter') 
            filter = dict()  
            field_name = self.request.query_params.get('field_name', None)
            order_by = self.request.query_params.get('order_by', None)
            search= self.request.query_params.get('search', None)
            leave_type=self.request.query_params.get('leave_type', None)
        
            if field_name and order_by:      
                if field_name =='date' and order_by=='asc':
                    sort_field='duration_start__date'
                    # return self.queryset.all().order_by('duration_start__date')
                if field_name =='date' and order_by=='desc':
                    sort_field='-duration_start__date'
                    # return self.queryset.all().order_by('-duration_start__date')
                if field_name =='duration_start' and order_by=='asc':
                    sort_field='duration_start'
                    # return self.queryset.all().order_by('duration_start')
                if field_name =='duration_start' and order_by=='desc':
                    sort_field='-duration_start'
                    # return self.queryset.all().order_by('-duration_start')

                if field_name =='duration_end' and order_by=='asc':
                    sort_field='duration_end'
                    # return self.queryset.all().order_by('duration_end')
                if field_name =='duration_end' and order_by=='desc':
                    sort_field='-duration_end'
                    # return self.queryset.all().order_by('-duration_end')

                if field_name =='duration' and order_by=='asc':
                    sort_field='duration'
                    # return self.queryset.all().order_by('duration')
                if field_name =='duration' and order_by=='desc':
                    sort_field='-duration'
                    # return self.queryset.all().order_by('-duration')
            
            
            if leave_type:
                leave_type_list=leave_type.split(',')
                filter['leave_type__in']= leave_type_list

            if search :
                search_data = list(map(str,search.split(" ")))
                print("This is if condition entry")
                if len(search.split(" "))>0 and len(search.split(" "))<2:
                    print("length 1 hai ")
                    queryset = self.queryset.filter((Q(attendance__employee__first_name__icontains=search_data[0])|Q(attendance__employee__last_name__icontains=search_data[0])),
                                                    is_deleted=False,**filter).order_by(sort_field)                            
                    return queryset
                elif len(search.split(" "))>1:
                    print("length 2 hai ")
                    queryset = self.queryset.filter((Q(attendance__employee__first_name__icontains=search_data[0]) & Q(attendance__employee__last_name__icontains=search_data[1])),
                                                    is_deleted=False,**filter).order_by(sort_field)
                    return queryset      
           
            
            else:
                # print('filter',**filter)
                queryset = self.queryset.filter(is_deleted=False,**filter).order_by(sort_field)
                return queryset
        else:
            print('sdsdsdsds')
            return []

    @response_modify_decorator_list_or_get_after_execution_for_pagination
    def get(self, request, *args, **kwargs):
        response=super(AttendanceLeaveApprovalList, self).get(self, request, args, kwargs)
        return response

class AttendanceAdminMispunchCheckerView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = AttendanceAdminMispunchCheckerSerializer
    pagination_class = CSPageNumberPagination
    queryset = AttendanceApprovalRequest.objects.filter(Q(is_requested=True) & Q(lock_status=False) & Q(is_deleted=False)&
                                                        Q(is_late_conveyance=False) & Q(checkin_benchmark=False)&
                                                        Q(request_type='MP')& (Q(approved_status='pending')|Q(approved_status='Approved')|Q(approved_status='Reject')))

    ## If mispunch will be accepted then we need to check the 
     # approved_status and keep only for visual not for use.
    ##

    def get_queryset(self):
        filter={}
        team_approval_flag = self.request.query_params.get('team_approval_flag', None)
        search_sort_flag = True
        if team_approval_flag == '1':
            login_user_details = self.request.user
            #print('login_user_details',login_user_details)
            #print('login_user_details',login_user_details.is_superuser)
            if login_user_details.is_superuser == False:
                users_list_under_the_login_user = TCoreUserDetail.objects.filter(
                    reporting_head = login_user_details,
                    cu_is_deleted = False
                ).values_list('cu_user')
                #print('users_list_under_the_login_user',users_list_under_the_login_user)
                if users_list_under_the_login_user:
                    attendence_id_list = Attendance.objects.filter(
                                employee__in=users_list_under_the_login_user,
                                is_deleted = False
                                ).values_list('id')
                    print('attedence_details',attendence_id_list)
                    if attendence_id_list:
                        
                        self.queryset = self.queryset.filter(attendance__in=attendence_id_list)
                    else:
                        search_sort_flag = False
                        self.queryset = self.queryset
                else:
                    search_sort_flag = False
                    self.queryset = []
                
            else:
                search_sort_flag = True
                self.queryset = self.queryset   

        if search_sort_flag:
            field_name = self.request.query_params.get('field_name', None)
            order_by = self.request.query_params.get('order_by', None)
            search= self.request.query_params.get('search', None)
            request_type=self.request.query_params.get('request_type', None)
            start_date = self.request.query_params.get('start_date', None)
            end_date = self.request.query_params.get('end_date', None)
            users = self.request.query_params.get('users', None)
            approval_type = self.request.query_params.get('approval_type', None)

            if users:
                user_lst = users.split(',')
                filter['attendance__employee__in'] = user_lst
            
            if start_date and end_date:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
                filter['duration_start__date__gte'] = start_date_obj
                filter['duration_end__date__lte'] = end_date_obj

            if approval_type:
                type_list = approval_type.split(',')
                print('approved_status',type_list)
                filter['approved_status__in'] = type_list
        
            if search :
                search_data = list(map(str,search.split(" ")))
                print("This is if condition entry")
                if len(search.split(" "))>0 and len(search.split(" "))<2:
                    print("length 1 hai ")
                    queryset = self.queryset.filter((Q(attendance__employee__first_name__icontains=search_data[0])|Q(attendance__employee__last_name__icontains=search_data[0])),
                                                    is_deleted=False,**filter)                            
                    return queryset
                elif len(search.split(" "))>1:
                    print("length 2 hai ")
                    queryset = self.queryset.filter((Q(attendance__employee__first_name__icontains=search_data[0]) & Q(attendance__employee__last_name__icontains=search_data[1])),
                                                    is_deleted=False,**filter)
                    return queryset                
            else:
                queryset = self.queryset.filter(is_deleted=False,**filter)
                return queryset
        else:
            return []
       
  
    @response_modify_decorator_list_or_get_after_execution_for_pagination
    def get(self, request, *args, **kwargs):
        response=super(AttendanceAdminMispunchCheckerView, self).get(self, request, args, kwargs)
        for data in response.data['results']:
            get_employee = Attendance.objects.filter(id=data['attendance']).values('employee__first_name','employee__last_name')
            print(get_employee[0]['employee__first_name'])
            print(get_employee[0]['employee__last_name'])
            data['employee'] = get_employee[0]['employee__first_name'] + ' ' + get_employee[0]['employee__last_name']
            
        return response

class AttendanceAdminMispunchCheckerCSVReportView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = AttendanceAdminMispunchCheckerCSVReportSerializer
    # pagination_class = CSPageNumberPagination
    queryset = AttendanceApprovalRequest.objects.filter(Q(is_requested=True) & Q(lock_status=False) & Q(is_deleted=False)&
                                                        Q(is_late_conveyance=False) & Q(checkin_benchmark=False)&
                                                        Q(request_type='MP')& (Q(approved_status='pending')|Q(approved_status='Approved')|Q(approved_status='Reject')))

    ## If mispunch will be accepted then we need to check the 
     # approved_status and keep only for visual not for use.
    ##

    def get_queryset(self):
        filter={}
        team_approval_flag = self.request.query_params.get('team_approval_flag', None)
        search_sort_flag = True
        if team_approval_flag == '1':
            login_user_details = self.request.user
            #print('login_user_details',login_user_details)
            #print('login_user_details',login_user_details.is_superuser)
            if login_user_details.is_superuser == False:
                users_list_under_the_login_user = TCoreUserDetail.objects.filter(
                    reporting_head = login_user_details,
                    cu_is_deleted = False
                ).values_list('cu_user')
                #print('users_list_under_the_login_user',users_list_under_the_login_user)
                if users_list_under_the_login_user:
                    attendence_id_list = Attendance.objects.filter(
                                employee__in=users_list_under_the_login_user,
                                is_deleted = False
                                ).values_list('id')
                    print('attedence_details',attendence_id_list)
                    if attendence_id_list:
                        
                        self.queryset = self.queryset.filter(attendance__in=attendence_id_list)
                    else:
                        search_sort_flag = False
                        self.queryset = self.queryset
                else:
                    search_sort_flag = False
                    self.queryset = []
                
            else:
                search_sort_flag = True
                self.queryset = self.queryset   

        if search_sort_flag:
            field_name = self.request.query_params.get('field_name', None)
            order_by = self.request.query_params.get('order_by', None)
            search= self.request.query_params.get('search', None)
            request_type=self.request.query_params.get('request_type', None)
            start_date = self.request.query_params.get('start_date', None)
            end_date = self.request.query_params.get('end_date', None)
            users = self.request.query_params.get('users', None)
            approval_type = self.request.query_params.get('approval_type', None)

            if users:
                user_lst = users.split(',')
                filter['attendance__employee__in'] = user_lst
            
            if start_date and end_date:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
                filter['duration_start__date__gte'] = start_date_obj
                filter['duration_end__date__lte'] = end_date_obj

            if approval_type:
                type_list = approval_type.split(',')
                print('approved_status',type_list)
                filter['approved_status__in'] = type_list
        
            if search :
                search_data = list(map(str,search.split(" ")))
                print("This is if condition entry")
                if len(search.split(" "))>0 and len(search.split(" "))<2:
                    print("length 1 hai ")
                    queryset = self.queryset.filter((Q(attendance__employee__first_name__icontains=search_data[0])|Q(attendance__employee__last_name__icontains=search_data[0])),
                                                    is_deleted=False,**filter)                            
                    return queryset
                elif len(search.split(" "))>1:
                    print("length 2 hai ")
                    queryset = self.queryset.filter((Q(attendance__employee__first_name__icontains=search_data[0]) & Q(attendance__employee__last_name__icontains=search_data[1])),
                                                    is_deleted=False,**filter)
                    return queryset                
            else:
                queryset = self.queryset.filter(is_deleted=False,**filter)
                return queryset
        else:
            return []
       
  
    def get(self, request, *args, **kwargs):
        response=super(AttendanceAdminMispunchCheckerCSVReportView, self).get(self, request, args, kwargs)
        if response.data:
            data_list = []
            for data in response.data:
                get_employee = Attendance.objects.filter(id=data['attendance']).values('employee__first_name','employee__last_name')
                print(get_employee[0]['employee__first_name'])
                print(get_employee[0]['employee__last_name'])
                data['employee'] = get_employee[0]['employee__first_name'] + ' ' + get_employee[0]['employee__last_name']
                print("jgjhghjg",data['duration_start'][:10],data['duration_start'][10:])
                data_list.append([data['employee'],data['attendance'],data['duration_start'][:10],data['duration_start'][11:19],data['duration_end'][11:19],\
                                    data['duration'],data['request_type'],data['justification'],data['remarks'],data['approved_status'],data['created_at'][:10],\
                                    data['created_at'][11:19]])


            ####################
            if os.path.isdir('media/attendance/misspunch_report/document'):
                file_name = 'media/attendance/misspunch_report/document/misspunch_report.csv'
            else:
                os.makedirs('media/attendance/misspunch_report/document')
                file_name = 'media/attendance/misspunch_report/document/misspunch_report.csv'


            final_df = pd.DataFrame(data_list, columns=['Employee Name','Attendance Id','Date','Duration Start','Duration End','Duration(Min.)','Request Type',\
                            'Justification','Remarks','Approved Status','Requested(Date)','Requested(Time)'])

            final_df.index = np.arange(1,len(final_df)+1)
            final_df.to_csv(file_name)
            # print("final_df",final_df)
            if request.is_secure():
                protocol = 'https://'
            else:
                protocol = 'http://'

            url = getHostWithPort(request) + file_name if file_name else None

            return Response(url)
                ####################
        else:
            return Response('No data found')
                    
class AttandanceRequestFreeByHRListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = AttandanceRequestFreeByHRListSerializer
    pagination_class = CSPageNumberPagination
    queryset = AttendanceApprovalRequest.objects.filter(Q(is_requested=True)&
                                                        Q(lock_status=False)&
                                                        Q(is_deleted=False)&
                                                        Q(is_late_conveyance=False)&
                                                        Q(checkin_benchmark=False)&
                                                        (Q(approved_status='approved')|
                                                        Q(approved_status='reject')|
                                                        Q(approved_status='pending')))
    
    def get_queryset(self):
        filter={}
        team_approval_flag = self.request.query_params.get('team_approval_flag', None)
        search_sort_flag = True
        if team_approval_flag == '1':
            login_user_details = self.request.user
            #print('login_user_details',login_user_details)
            #print('login_user_details',login_user_details.is_superuser)
            if login_user_details.is_superuser == False:
                users_list_under_the_login_user = TCoreUserDetail.objects.filter(
                    reporting_head = login_user_details,
                    cu_is_deleted = False
                ).values_list('cu_user')
                #print('users_list_under_the_login_user',users_list_under_the_login_user)
                if users_list_under_the_login_user:
                    attendence_id_list = Attendance.objects.filter(
                                employee__in=users_list_under_the_login_user,
                                is_deleted = False
                                ).values_list('id')
                    print('attedence_details',attendence_id_list)
                    if attendence_id_list:
                        
                        self.queryset = self.queryset.filter(attendance__in=attendence_id_list)
                    else:
                        search_sort_flag = False
                        self.queryset = self.queryset
                else:
                    search_sort_flag = False
                    self.queryset = []
                
            else:
                search_sort_flag = True
                self.queryset = self.queryset   

        if search_sort_flag:
            field_name = self.request.query_params.get('field_name', None)
            order_by = self.request.query_params.get('order_by', None)
            search= self.request.query_params.get('search', None)
            request_type=self.request.query_params.get('request_type', None)
            sort_field="-id"
        
            if field_name and order_by:      
                if field_name =='date' and order_by=='asc':
                    sort_field="duration_start__date"
                    # return self.queryset.all().order_by('duration_start__date')
                if field_name =='date' and order_by=='desc':
                    sort_field="-duration_start__date"
                    # return self.queryset.all().order_by('-duration_start__date')
                if field_name =='duration_start' and order_by=='asc':
                    sort_field="duration_start"
                    # return self.queryset.all().order_by('duration_start')
                if field_name =='duration_start' and order_by=='desc':
                    sort_field="-duration_start"
                    # return self.queryset.all().order_by('-duration_start')

                if field_name =='duration_end' and order_by=='asc':
                    sort_field="duration_end"
                    # return self.queryset.all().order_by('duration_end')
                if field_name =='duration_end' and order_by=='desc':
                    sort_field="-duration_end"
                    # return self.queryset.all().order_by('-duration_end')

                if field_name =='duration' and order_by=='asc':
                    sort_field="duration"
                    # return self.queryset.all().order_by('duration')
                if field_name =='duration' and order_by=='desc':
                    sort_field="-duration"
                    # return self.queryset.all().order_by('-duration')
            
            if request_type:
                request_type_list=request_type.split(',')
                filter['request_type__in']= request_type_list

            # if leave_type:
            #     leave_type_list=leave_type.split(',')
            #     filter['leave_type__in']= leave_type_list

            if search :
                search_data = list(map(str,search.split(" ")))
                print("This is if condition entry")
                if len(search.split(" "))>0 and len(search.split(" "))<2:
                    print("length 1 hai ")
                    queryset = self.queryset.filter((Q(attendance__employee__first_name__icontains=search_data[0])|Q(attendance__employee__last_name__icontains=search_data[0])),
                                                    is_deleted=False,**filter).order_by(sort_field)                            
                    return queryset
                elif len(search.split(" "))>1:
                    print("length 2 hai ")
                    queryset = self.queryset.filter((Q(attendance__employee__first_name__icontains=search_data[0]) & Q(attendance__employee__last_name__icontains=search_data[1])),
                                                    is_deleted=False,**filter).order_by(sort_field)
                    return queryset                

            else:
                queryset = self.queryset.filter(is_deleted=False,**filter).order_by(sort_field) 
                return queryset
           
        else:
            return []
       

    @response_modify_decorator_list_or_get_after_execution_for_pagination
    def get(self, request, *args, **kwargs):
        response=super(AttandanceRequestFreeByHRListView, self).get(self, request, args, kwargs)
        return response

class AttendanceMonthlyHRListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = Attendance.objects.filter(is_deleted=False).order_by('date')
    serializer_class = AttendanceMonthlyHRListSerializer
    # pagination_class = CSPageNumberPagination

    def get_queryset(self):
        blank_queryset = Attendance.objects.none()
        print('blank_queryset',blank_queryset)
        emp_id = self.request.query_params.get('emp_id', None)
        current_date = self.request.query_params.get('current_date', None)
        month = self.request.query_params.get('month', None)
        year = self.request.query_params.get('year', None)
        filter = {}
        date_range = None
        if self.queryset.count():
            print("self.queryset.count()",self.queryset.count())
            if current_date and emp_id:
                date = datetime.strptime(current_date, "%Y-%m-%d")
                date_range = AttendenceMonthMaster.objects.filter(month_start__date__lte=date,month_end__date__gte=date).values('month_start__date','month_end__date')
                # print("date_range",date_range)
            if month and year and emp_id:
                date_range = AttendenceMonthMaster.objects.filter(month=month,month_end__year=year).values('month_start__date','month_end__date')
                print("date_range",date_range)

            if date_range:
                print("This is if")
                filter['employee']=emp_id
                filter['date__date__gte'] = date_range[0]['month_start__date']
                filter['date__date__lte'] = date_range[0]['month_end__date']

        if filter :
            print('filter',self.queryset.filter(**filter))
            return self.queryset.filter(**filter)
        else:
            # print('else filter',self.queryset)
            return blank_queryset

    @response_modify_decorator_list_after_execution
    def get(self, request, *args, **kwargs):
        print('entry test')
        print(self.queryset)
        response=super(AttendanceMonthlyHRListView,self).get(self, request, args, kwargs)
        print("response.data['results']",response.data)
        # print("response.data['results']",response.data['results'])
        attendance_request_dict = {}
        for data in response.data:
            attendance_request = AttendanceApprovalRequest.objects.filter(attendance=data['id'],is_deleted=False)
            attendance_request_list = []
            conveyance_dict = {}
            conveyance_list = []
            data['is_attendance_request'] = True
            daily_duration = 0
            daily_grace = 0
            cng_leave_type = None
            oth_leave_type = None
            daily_leave_type = None
            daily_leave_period = None
            daily_leave_approval = None
            cng_leave_period = None
            oth_leave_period = None
            day_remarks = None
            for att_req in attendance_request:
                if att_req.leave_type_changed is not None:
                    day_remarks = 'Leave ('+att_req.leave_type_changed+')'
                elif att_req.leave_type_changed is None and att_req.leave_type is not None:
                    day_remarks = 'Leave ('+att_req.leave_type+')'
                elif att_req.approved_status=='approved' and att_req.request_type =='FOD':
                    day_remarks = 'OD'

                if att_req.leave_type_changed_period=='GR':
                    daily_grace+=att_req.duration
                elif att_req.request_type=='GR':
                    daily_grace+=att_req.duration
                if att_req.leave_type_changed:
                    cng_leave_type= att_req.leave_type_changed
                    if att_req.leave_type_changed_period=='FD':
                        cng_leave_period = 1
                    elif att_req.leave_type_changed_period=='HD':
                        cng_leave_period = 0.5
                elif att_req.leave_type:
                    oth_leave_type= att_req.leave_type
                    if att_req.request_type=='FD':
                        oth_leave_period = 1
                    elif att_req.request_type=='HD':
                        oth_leave_period = 0.5

                if cng_leave_type:
                    daily_leave_type=cng_leave_type
                    daily_leave_period=cng_leave_period
                elif oth_leave_type:
                    daily_leave_type=oth_leave_type
                    daily_leave_period=oth_leave_period

                if att_req.approved_status == 'relese' or att_req.approved_status == 'pending' or att_req.is_requested== True:
                    data['is_attendance_request'] = False
                if att_req.is_late_conveyance==False and att_req.checkin_benchmark==False:
                    attendance_request_dict = {
                        'id' : att_req.id,
                        'duration_start' : att_req.duration_start,
                        'duration_end' : att_req.duration_end,
                        'duration' : att_req.duration,
                        'request_type' : att_req.leave_type_changed_period if att_req.leave_type_changed_period else att_req.request_type,
                        'is_requested' : att_req.is_requested,
                        'request_date' : att_req.request_date,
                        'justification' : att_req.justification,
                        'approved_status' : att_req.approved_status,
                        'remarks' : att_req.remarks,
                        'justified_by' : att_req.justified_by_id,
                        'justified_at' : att_req.justified_at,
                        'approved_by' : att_req.approved_by_id,
                        'approved_at' : att_req.approved_at,
                        'leave_type' : att_req.leave_type_changed if att_req.leave_type_changed else att_req.leave_type,
                        'is_late_conveyance' : att_req.is_late_conveyance,
                        'vehicle_type' : att_req.vehicle_type.name if att_req.vehicle_type else '',
                        'vehicle_type_id' : att_req.vehicle_type.id if att_req.vehicle_type else '',
                        'is_conveyance' : att_req.is_conveyance,
                        'from_place' : att_req.from_place,
                        'to_place' : att_req.to_place,
                        'conveyance_expense' : att_req.conveyance_expense,
                        'approved_expenses' : att_req.approved_expenses,
                        'conveyance_remarks' : att_req.conveyance_remarks,
                        'leave_type_changed' : att_req.leave_type_changed,
                        'leave_type_changed_period' : att_req.leave_type_changed_period,
                        'checkin_benchmark' : att_req.checkin_benchmark,
                        'lock_status' : att_req.lock_status
                    }
                    attendance_request_list.append(attendance_request_dict)

                if att_req.vehicle_type and att_req.from_place and att_req.to_place and att_req.conveyance_expense:
                    first_name = att_req.conveyance_alloted_by.first_name if att_req.conveyance_alloted_by else ''
                    last_name = att_req.conveyance_alloted_by.last_name if att_req.conveyance_alloted_by else ''
                    conveyance_dict = {
                        'vehicle_type' : att_req.vehicle_type.name if att_req.vehicle_type else '',
                        'vehicle_type_desctiption' : att_req.vehicle_type.description if att_req.vehicle_type else '',
                        'vehicle_type_id' : att_req.vehicle_type.id if att_req.vehicle_type else '',
                        'from_place' : att_req.from_place,
                        'to_place' : att_req.to_place,
                        'conveyance_expense' : att_req.conveyance_expense,
                        'approved_expenses' : att_req.approved_expenses,
                        'conveyance_remarks' : att_req.conveyance_remarks,
                        'conveyance_purpose' : att_req.conveyance_purpose,
                        'conveyance_alloted_by' : first_name + " " + last_name,
                        'conveyance_approval' : att_req.get_conveyance_approval_display()
                    }
                    conveyance_list.append(conveyance_dict)


            print("daily_grace", daily_grace)
            data['conveyance_details'] = conveyance_list
            data['daily_grace'] = daily_grace
            data['daily_leave_type'] = daily_leave_type
            data['daily_leave_period'] = daily_leave_period
            data['attendance_request'] = attendance_request_list
            if day_remarks:
                data['day_remarks'] = day_remarks

        return response

class AttendanceMonthlyHRSummaryListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = Attendance.objects.filter(is_deleted=False)
    serializer_class = AttendanceMonthlyHRListSerializer
    # pagination_class = CSPageNumberPagination

    def get_queryset(self):
        #print('queryset',self.queryset)
        team_approval_flag = self.request.query_params.get('team_approval_flag', None)
        search_sort_flag = True
        if team_approval_flag == '1':
            login_user_details = self.request.user
            #print('login_user_details',login_user_details)
            #print('login_user_details',login_user_details.is_superuser)
            if login_user_details.is_superuser == False:
                users_list_under_the_login_user = TCoreUserDetail.objects.filter(
                    reporting_head = login_user_details,
                    cu_is_deleted = False
                ).values_list('cu_user')
                #print('users_list_under_the_login_user',users_list_under_the_login_user)
                if users_list_under_the_login_user:
                    attendence= Attendance.objects.filter(
                                employee__in=users_list_under_the_login_user,
                                is_deleted = False
                                )
                    print('attedence_details',attendence)
                    if attendence:
                        search_sort_flag = True
                        self.queryset = attendence
                    else:
                        search_sort_flag = False
                else:
                    search_sort_flag = False
                    
                
            else:
                search_sort_flag = True
                self.queryset = self.queryset   

        if search_sort_flag:
            blank_queryset = Attendance.objects.none()
            print('blank_queryset',blank_queryset)
            emp_id = self.request.query_params.get('emp_id', None)
            current_date = self.request.query_params.get('current_date', None)
            month = self.request.query_params.get('month', None)
            year = self.request.query_params.get('year', None)
            filter = {}
            date_range = None
           
                #print("self.queryset.count()",self.queryset.count())
            if month and year and emp_id:
                date_range = AttendenceMonthMaster.objects.filter(month=month,month_end__year=year).values('month_start__date','month_end__date')
                print("date_range",date_range)

                if date_range:
                    print("This is if")
                    filter['employee']=emp_id
                    filter['date__date__gte'] = date_range[0]['month_start__date']
                    filter['date__date__lte'] = date_range[0]['month_end__date']

            if filter :
                print('filter',self.queryset.filter(**filter))
                return self.queryset.filter(**filter).order_by('date')
            else:
                # print('else filter',self.queryset)
                return self.queryset.filter(is_deleted=False).order_by('date')
        else:
            return []

    @response_modify_decorator_get_after_execution
    def get(self, request, *args, **kwargs):
        print('entry test')
        print(self.queryset)
        response=super(AttendanceMonthlyHRSummaryListView,self).get(self, request, args, kwargs)
        # print("response.data['results']",response.data)
        # print("response.data['results']",response.data['results'])
        attendance_request_dict = {}
        for data in response.data:
            attendance_request = AttendanceApprovalRequest.objects.filter(attendance=data['id'],is_deleted=False)
            grace_duration_list = []
            grace_remarks_list = []
            od_duration_list = []
            od_remarks_list = []
            attendance_request_list = []
            conveyance_dict = {}
            conveyance_list = []
            data['is_attendance_request'] = True
            daily_duration = 0
            daily_grace = 0
            cng_leave_type = None
            oth_leave_type = None
            daily_leave_type = None
            daily_leave_period = None
            daily_leave_approval = None
            cng_leave_period = None
            oth_leave_period = None
            day_remarks = None
            for att_req in attendance_request:
                if att_req.leave_type_changed is not None:
                    day_remarks = 'Leave ('+att_req.leave_type_changed+')'
                elif att_req.leave_type_changed is None and att_req.leave_type is not None:
                    day_remarks = 'Leave ('+att_req.leave_type+')'
                elif att_req.approved_status=='approved' and att_req.request_type =='FOD':
                    day_remarks = 'OD'

                if att_req.leave_type_changed_period=='GR':
                    daily_grace+=att_req.duration
                    grace_duration_list.append(att_req.duration)
                    grace_remarks_list.append(att_req.justification)
                elif att_req.request_type=='GR':
                    daily_grace+=att_req.duration
                    grace_duration_list.append(att_req.duration)
                    grace_remarks_list.append(att_req.justification)
                elif att_req.checkin_benchmark == True:
                    daily_grace+=att_req.duration
                if att_req.leave_type_changed:
                    cng_leave_type= att_req.leave_type_changed
                    if att_req.leave_type_changed_period=='FD':
                        cng_leave_period = 1
                    elif att_req.leave_type_changed_period=='HD':
                        cng_leave_period = 0.5
                elif att_req.leave_type:
                    oth_leave_type= att_req.leave_type
                    if att_req.request_type=='FD':
                        oth_leave_period = 1
                    elif att_req.request_type=='HD':
                        oth_leave_period = 0.5
                elif att_req.request_type=='OD':
                    od_duration_list.append(att_req.duration)
                    od_remarks_list.append(att_req.justification)

                if cng_leave_type:
                    daily_leave_type=cng_leave_type
                    daily_leave_period=cng_leave_period
                elif oth_leave_type:
                    daily_leave_type=oth_leave_type
                    daily_leave_period=oth_leave_period

                if att_req.approved_status == 'relese' or att_req.approved_status == 'pending' or att_req.is_requested== True:
                    data['is_attendance_request'] = False
                if att_req.is_late_conveyance==False and att_req.checkin_benchmark==False:
                    attendance_request_dict = {
                        'id' : att_req.id,
                        'duration_start' : att_req.duration_start,
                        'duration_end' : att_req.duration_end,
                        'duration' : att_req.duration,
                        'request_type' : att_req.leave_type_changed_period if att_req.leave_type_changed_period else att_req.request_type,
                        'is_requested' : att_req.is_requested,
                        'request_date' : att_req.request_date,
                        'justification' : att_req.justification,
                        'approved_status' : att_req.approved_status,
                        'remarks' : att_req.remarks,
                        'justified_by' : att_req.justified_by_id,
                        'justified_at' : att_req.justified_at,
                        'approved_by' : att_req.approved_by_id,
                        'approved_at' : att_req.approved_at,
                        'leave_type' : att_req.leave_type_changed if att_req.leave_type_changed else att_req.leave_type,
                        'is_late_conveyance' : att_req.is_late_conveyance,
                        'vehicle_type' : att_req.vehicle_type.name if att_req.vehicle_type else '',
                        'vehicle_type_id' : att_req.vehicle_type.id if att_req.vehicle_type else '',
                        'is_conveyance' : att_req.is_conveyance,
                        'from_place' : att_req.from_place,
                        'to_place' : att_req.to_place,
                        'conveyance_expense' : att_req.conveyance_expense,
                        'approved_expenses' : att_req.approved_expenses,
                        'conveyance_remarks' : att_req.conveyance_remarks,
                        'leave_type_changed' : att_req.leave_type_changed,
                        'leave_type_changed_period' : att_req.leave_type_changed_period,
                        'checkin_benchmark' : att_req.checkin_benchmark,
                        'lock_status' : att_req.lock_status
                    }
                    attendance_request_list.append(attendance_request_dict)

                if att_req.vehicle_type and att_req.from_place and att_req.to_place and att_req.conveyance_expense:
                    first_name = att_req.conveyance_alloted_by.first_name if att_req.conveyance_alloted_by else ''
                    last_name = att_req.conveyance_alloted_by.last_name if att_req.conveyance_alloted_by else ''
                    conveyance_dict = {
                        'vehicle_type' : att_req.vehicle_type.name if att_req.vehicle_type else '',
                        'vehicle_type_desctiption' : att_req.vehicle_type.description if att_req.vehicle_type else '',
                        'vehicle_type_id' : att_req.vehicle_type.id if att_req.vehicle_type else '',
                        'from_place' : att_req.from_place,
                        'to_place' : att_req.to_place,
                        'conveyance_expense' : att_req.conveyance_expense,
                        'approved_expenses' : att_req.approved_expenses,
                        'conveyance_remarks' : att_req.conveyance_remarks,
                        'conveyance_purpose' : att_req.conveyance_purpose,
                        'conveyance_alloted_by' : first_name + " " + last_name,
                        'conveyance_approval' : att_req.conveyance_approval,
                        'conveyance_approval_name' :att_req.get_conveyance_approval_display(),
                        'conveyance_durations' : att_req.duration,
                        'duration_start': att_req.duration_start,
                        'duration_end': att_req.duration_end,
                        'is_late_conveyance': att_req.is_late_conveyance
                    }
                    conveyance_list.append(conveyance_dict)


            print("daily_grace", daily_grace)
            data['conveyance_details'] = conveyance_list
            data['daily_grace'] = daily_grace
            data['daily_leave_type'] = daily_leave_type
            data['daily_leave_period'] = daily_leave_period
            data['attendance_request'] = attendance_request_list
            data['grace_duration_list'] = grace_duration_list
            data['grace_remarks_list'] = grace_remarks_list
            data['od_duration_list'] = od_duration_list
            data['od_remarks_list'] = od_remarks_list
            if day_remarks:
                data['day_remarks'] = day_remarks

        return response

class AttendanceGraceLeaveListForHRModifiedView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = AttendanceApprovalRequest.objects.filter(is_deleted=False)

    def get(self, request, *args, **kwargs):
        date =self.request.query_params.get('date', None)
        print('date',type(date))
        date_object = datetime.strptime(date, '%Y-%m-%d').date()
        print('date_object',date_object)
        employee_id=self.request.query_params.get('employee_id', None)
        total_grace={}
        data_dict = {}
        is_previous=self.request.query_params.get('is_previous', None)

        aa = datetime.now()
        total_month_grace=AttendenceMonthMaster.objects.filter(month_start__date__lte=date_object,
                                        month_end__date__gte=date_object,is_deleted=False).values('grace_available',
                                                                                 'year_start_date',
                                                                                 'year_end_date',
                                                                                 'month',
                                                                                 'month_start',
                                                                                 'month_end')
        if is_previous == "true":
            print('sada',type(total_month_grace[0]['month_start']))
            date_object= total_month_grace[0]['month_start'].date()- timedelta(days=1)  
            total_month_grace=AttendenceMonthMaster.objects.filter(month_start__date__lte=date_object,
                                        month_end__date__gte=date_object,is_deleted=False).values('grace_available',
                                                                                 'year_start_date',
                                                                                 'year_end_date',
                                                                                 'month',
                                                                                 'month_start',
                                                                                 'month_end')
                                                                                
        print('total_month_grace',total_month_grace)
        total_grace['month_start']=total_month_grace[0]['month_start']
        total_grace['month_end']=total_month_grace[0]['month_end']
        total_grace['year_start']=total_month_grace[0]['year_start_date']
        total_grace['year_end']=total_month_grace[0]['year_end_date']
        print("total_month_grace",total_grace)

        if total_month_grace:
            total_grace['total_month_grace']=total_month_grace[0]['grace_available'] if total_month_grace[0]['grace_available'] else 0

        # for data in response.data:
        availed_grace = AttendanceApprovalRequest.objects.filter(Q(attendance__employee=employee_id) &
                                                                Q(duration_start__gte=total_month_grace[0]['month_start']) &
                                                                Q(duration_start__lte=total_month_grace[0]['month_end']) &
                                                                Q(is_requested=True) & Q(is_deleted=False) &
                                                                (Q(request_type='GR')|Q(checkin_benchmark=True))
                                                                ).aggregate(Sum('duration'))['duration__sum']

        total_grace['availed_grace']=availed_grace if availed_grace else 0
        total_grace['grace_balance']=total_month_grace[0]['grace_available'] - total_grace['availed_grace']

        advance_leave=EmployeeAdvanceLeaves.objects.filter(Q(employee=employee_id)&
                                                           Q(is_deleted=False)&
                                                           (Q(approved_status='pending')|Q(approved_status='approved'))
                                                          ).values('leave_type','start_date','end_date')
        print('advance_leave',advance_leave)     
        advance_cl=0
        advance_el=0
        advance_ab=0
        day=0

        ###############################################################################################
        '''
            Advanced Leave Calculation till month.
            If employee's last attendance date less then till month's last date.
            Then calculate CL/EL/AB.
        '''
        last_attendance = Attendance.objects.filter(employee=employee_id).values_list('date__date',flat=True).order_by('-date')[:1]
        print("last_attendance",last_attendance)
        last_attendance = last_attendance[0] if last_attendance else date_object
        
        if last_attendance<total_grace['month_end'].date():
            print("last_attendancehfthtfrhfth",last_attendance)
            adv_str_date = last_attendance+timedelta(days=1)
            adv_end_date = total_grace['month_end'].date()+timedelta(days=1)
            if advance_leave:
                for leave in advance_leave:
                    print('leave',leave)
                    start_date=leave['start_date'].date()
                    end_date=leave['end_date'].date()+timedelta(days=1)
                    print('start_date,end_date',start_date,end_date)

                    if adv_str_date<=start_date and adv_end_date>=start_date:
                        if adv_end_date>=end_date:
                            day = (end_date-start_date).days
                        elif adv_end_date<=end_date:
                            day = (adv_end_date-start_date).days
                    elif adv_str_date>start_date:
                        if adv_end_date<=end_date:
                            day = (adv_end_date-adv_str_date).days
                        elif adv_str_date<=end_date and adv_end_date>=end_date:
                            day = (end_date-adv_str_date).days


                        
                    if leave['leave_type']=='CL':
                        advance_cl+=day
                    elif leave['leave_type']=='EL':
                        advance_el+=day
                    elif leave['leave_type']=='AB':
                        advance_ab+=day

        ############################################################
        # if advance_leave:
        #     for leave in advance_leave:
        #         print('leave',leave)
        #         start_date=leave['start_date'].date()
        #         end_date=leave['end_date'].date()+timedelta(days=1)
        #         print('start_date,end_date',start_date,end_date)
        #         if date_object < end_date:
        #             if date_object < start_date:
        #                 day=(end_date-start_date).days 
        #                 print('day',day)
        #             elif date_object > start_date:
        #                 day=(end_date-date_object).days
        #                 print('day2',day)
        #             else:
        #                 day=(end_date-date_object).days

        #         if leave['leave_type']=='CL':
        #             advance_cl+=day
        #         elif leave['leave_type']=='EL':
        #             advance_el+=day
        #         elif leave['leave_type']=='AB':
        #             advance_ab+=day
        ##################################################################
        ###################################### yearly ############################################
        # yearly_availed_data = AttendanceApprovalRequest.objects.filter(attendance__employee=employee_id,is_requested=True,is_deleted=False,
        #                                                         duration_start__gte=total_month_grace[0]['year_start_date'],
        #                                                         duration_start__lte=total_month_grace[0]['year_end_date'])

        """ 
        LEAVE CALCULATION:-
        1)SINGLE LEAVE CALCULATION
        2)MULTIPLE LEAVE FOR ONE DAY IS AUTO CONVERTED TO ONE TYPE OF LEAVE 
        EDITED BY :- Abhishek.singh@shyamfuture.com
        
        """ 

        availed_hd_cl=0.0
        availed_hd_el=0.0
        availed_hd_sl=0.0
        availed_hd_ab=0.0
        availed_cl=0.0
        availed_el=0.0
        availed_sl=0.0
        availed_ab=0.0

        yearly_attendence_daily_data = AttendanceApprovalRequest.objects.filter(((Q(leave_type_changed_period__isnull=False)&(Q(leave_type_changed_period='FD')|Q(leave_type_changed_period='HD')))|
                                            (Q(leave_type_changed_period__isnull=True)&(Q(request_type='FD')|Q(request_type='HD')))),
                                            attendance__employee=employee_id,is_requested=True,
                                            attendance__date__gte=total_month_grace[0]['year_start_date'],
                                            attendance__date__lte=total_month_grace[0]['month_end']).values('duration_start__date').distinct()
                                            
        print("yearly_attendence_daily_data",yearly_attendence_daily_data)
        yearly_date_list = [x['duration_start__date'] for x in yearly_attendence_daily_data.iterator()]
        print("yearly_date_list",yearly_date_list)
        # for data in attendence_daily_data.iterator():
            # print(datetime.now())
        availed_master_wo_reject_fd = AttendanceApprovalRequest.objects.\
                filter((Q(approved_status='pending')|Q(approved_status='approved')|Q(approved_status='reject')),
                        (Q(leave_type__isnull=False)|Q(leave_type_changed_period__isnull=False)),
                        attendance__employee=employee_id,
                        attendance_date__in=yearly_date_list,is_requested=True,is_deleted=False).annotate(
                            leave_type_final = Case(
                            When((Q(leave_type_changed_period__isnull=False)&Q(leave_type_changed_period='FD')),then=F('leave_type_changed')),
                            When((Q(leave_type_changed_period__isnull=True)&Q(request_type='FD')),then=F('leave_type')),
                            output_field=CharField()
                        ),
                        leave_type_final_hd = Case(
                            When((Q(leave_type_changed_period__isnull=False)&Q(leave_type_changed_period='HD')),then=F('leave_type_changed')),
                            When((Q(leave_type_changed_period__isnull=True)&Q(request_type='HD')),then=F('leave_type')),
                            output_field=CharField()
                        ),
                        ).values('leave_type_final','leave_type_final_hd','attendance_date').distinct()
        print("availed_master_wo_reject_fd",availed_master_wo_reject_fd)
        if availed_master_wo_reject_fd:

            for data in yearly_date_list:
                availed_FD=availed_master_wo_reject_fd.filter(attendance_date=data)
                
                print("availed_HD",availed_FD)
                if availed_FD.filter(leave_type_final__isnull=False):
                    if availed_FD.values('leave_type_final').count() >1:
                        if availed_FD.filter(leave_type_final='AB'):
                            availed_ab=availed_ab+1.0

                        elif availed_FD.filter(leave_type_final='CL'):
                            availed_cl=availed_cl+1.0
                                    
                    else:
                        l_type=availed_FD[0]['leave_type_final']
                        if l_type == 'CL':
                            availed_cl=availed_cl+1.0
                        elif l_type == 'EL':
                            availed_el=availed_el+1.0
                        elif l_type == 'SL':
                            availed_sl=availed_sl+1.0
                        elif l_type == 'AB':
                            availed_ab=availed_ab+1.0

                elif availed_FD.filter(leave_type_final_hd__isnull=False):
                    if availed_FD.values('leave_type_final_hd').count() >1:
                        if availed_FD.filter(leave_type_final_hd='AB'):
                            availed_hd_ab=availed_hd_ab+1.0

                        elif availed_FD.filter(leave_type_final_hd='CL'):
                            availed_hd_cl=availed_hd_cl+1.0
                                    
                    else:
                        l_type=availed_FD[0]['leave_type_final_hd']
                        if l_type == 'CL':
                            availed_hd_cl=availed_hd_cl+1.0
                        elif l_type == 'EL':
                            availed_hd_el=availed_hd_el+1.0
                        elif l_type == 'SL':
                            availed_hd_sl=availed_hd_sl+1.0
                        elif l_type == 'AB':
                            availed_hd_ab=availed_hd_ab+1.0


        total_grace['yearly_availed_cl']=float(availed_cl)+float(advance_cl)+float(availed_hd_cl/2)
        total_grace['yearly_availed_el']=float(availed_el)+float(advance_el)+float(availed_hd_el/2)
        total_grace['yearly_availed_sl']=float(availed_sl)+float(availed_hd_sl/2)
        total_grace['yearly_availed_ab']=float(availed_ab)+float(advance_ab)+float(availed_hd_ab/2)
        total_grace['yearly_total_availed_leave']=total_grace['yearly_availed_cl'] + total_grace['yearly_availed_el'] + total_grace['yearly_availed_sl']
        ############################################################################################################

        ##################################### MONTHLY ##############################################
        monthly_availed_data = AttendanceApprovalRequest.objects.filter(attendance__employee=employee_id,is_requested=True,is_deleted=False,
                                                                duration_start__gte=total_month_grace[0]['month_start'],
                                                                duration_start__lte=total_month_grace[0]['month_end'])
        
        
        """ 
        LEAVE CALCULATION:-
        1)SINGLE LEAVE CALCULATION
        2)MULTIPLE LEAVE FOR ONE DAY IS AUTO CONVERTED TO ONE TYPE OF LEAVE 
        EDITED BY :- Abhishek.singh@shyamfuture.com
        
        """ 
        
        ####Monthly GR request date count##########################
        grace_month_count_total=0
        # attendence_daily_gr_count_data = Attendance.objects.filter(employee=employee_id,date__gte=total_month_grace[0]['month_start'],
        #                                                             date__lte=total_month_grace[0]['month_end'])
        # for data in attendence_daily_gr_count_data:
        #     grace_per_month=AttendanceApprovalRequest.objects.filter(Q(attendance__employee=employee_id)&
        #                                                     Q(is_requested=True)&Q(request_type='GR')&
        #                                                     Q(duration_start__gte=total_month_grace[0]['month_start'])&
        #                                                     Q(duration_start__lte=total_month_grace[0]['month_end'])&
        #                                                     Q(is_deleted=False),attendance_date=data.date.date()
        #                                                     ).values('request_type').distinct().count()
        #     print("grace_per_month",grace_per_month)
        #     grace_month_count_total+=grace_per_month
        #     print('grace_per_month',grace_month_count_total)
        grace_month_count_total = AttendanceApprovalRequest.objects.filter(Q(attendance__employee=employee_id) &
                                                                Q(duration_start__gte=total_month_grace[0]['month_start']) &
                                                                Q(duration_start__lte=total_month_grace[0]['month_end']) &
                                                                Q(is_requested=True) & Q(is_deleted=False) &
                                                                (Q(request_type='GR')|Q(checkin_benchmark=True)) &
                                                                (Q(approved_status='pending')|Q(approved_status='approved'))
                                                                ).aggregate(Sum('duration'))['duration__sum']
        print('grace_month_count_total',grace_month_count_total)
        ####Monthly GR request date count##########################

        monthly_availed_hd_cl=0.0
        monthly_availed_hd_el=0.0
        monthly_availed_hd_sl=0.0
        monthly_availed_hd_ab=0.0
        monthly_availed_cl=0.0
        monthly_availed_el=0.0
        monthly_availed_sl=0.0
        monthly_availed_ab=0.0

        attendence_daily_data = AttendanceApprovalRequest.objects.filter(((Q(leave_type_changed_period__isnull=False)&(Q(leave_type_changed_period='FD')|Q(leave_type_changed_period='HD')))|
                                            (Q(leave_type_changed_period__isnull=True)&(Q(request_type='FD')|Q(request_type='HD')))),
                                            attendance__employee=employee_id,is_requested=True,
                                            attendance__date__gte=total_month_grace[0]['month_start'],
                                            attendance__date__lte=total_month_grace[0]['month_end']).values('duration_start__date').distinct()

        print("attendence_daily_data",attendence_daily_data)
        month_date_list = [x['duration_start__date'] for x in attendence_daily_data.iterator()]
        print("month_date_list",month_date_list)
        # for data in attendence_daily_data.iterator():
            # print(datetime.now())
        availed_master_wo_reject_fd = AttendanceApprovalRequest.objects.\
                filter((Q(approved_status='pending')|Q(approved_status='approved')|Q(approved_status='reject')),
                        (Q(leave_type__isnull=False)|Q(leave_type_changed_period__isnull=False)),
                        attendance__employee=employee_id,
                        attendance_date__in=month_date_list,is_requested=True,is_deleted=False).annotate(
                            leave_type_final = Case(
                            When((Q(leave_type_changed_period__isnull=False)&Q(leave_type_changed_period='FD')),then=F('leave_type_changed')),
                            When((Q(leave_type_changed_period__isnull=True)&Q(request_type='FD')),then=F('leave_type')),
                            output_field=CharField()
                        ),
                        leave_type_final_hd = Case(
                            When((Q(leave_type_changed_period__isnull=False)&Q(leave_type_changed_period='HD')),then=F('leave_type_changed')),
                            When((Q(leave_type_changed_period__isnull=True)&Q(request_type='HD')),then=F('leave_type')),
                            output_field=CharField()
                        ),
                        ).values('leave_type_final','leave_type_final_hd','attendance_date').distinct()
        print("availed_master_wo_reject_fd",availed_master_wo_reject_fd)
        if availed_master_wo_reject_fd:

            for data in month_date_list:
                availed_FD=availed_master_wo_reject_fd.filter(attendance_date=data)
                
                print("availed_HD",availed_FD)
                if availed_FD.filter(leave_type_final__isnull=False):
                    if availed_FD.values('leave_type_final').count() >1:
                        if availed_FD.filter(leave_type_final='AB'):
                            monthly_availed_ab=monthly_availed_ab+1.0

                        elif availed_FD.filter(leave_type_final='CL'):
                            monthly_availed_cl=monthly_availed_cl+1.0
                                    

                    else:
                        l_type=availed_FD[0]['leave_type_final']
                        if l_type == 'CL':
                            monthly_availed_cl=monthly_availed_cl+1.0
                        elif l_type == 'EL':
                            monthly_availed_el=monthly_availed_el+1.0
                        elif l_type == 'SL':
                            monthly_availed_sl=monthly_availed_sl+1.0
                        elif l_type == 'AB':
                            monthly_availed_ab=monthly_availed_ab+1.0

                elif availed_FD.filter(leave_type_final_hd__isnull=False):
                    if availed_FD.values('leave_type_final_hd').count() >1:
                        if availed_FD.filter(leave_type_final_hd='AB'):
                            monthly_availed_hd_ab=monthly_availed_hd_ab+1.0

                        elif availed_FD.filter(leave_type_final_hd='CL'):
                            monthly_availed_hd_cl=monthly_availed_hd_cl+1.0
                                    

                    else:
                        l_type=availed_FD[0]['leave_type_final_hd']
                        if l_type == 'CL':
                            monthly_availed_hd_cl=monthly_availed_hd_cl+1.0
                        elif l_type == 'EL':
                            monthly_availed_hd_el=monthly_availed_hd_el+1.0
                        elif l_type == 'SL':
                            monthly_availed_hd_sl=monthly_availed_hd_sl+1.0
                        elif l_type == 'AB':
                            monthly_availed_hd_ab=monthly_availed_hd_ab+1.0
       

        total_grace['monthly_grace_count']=grace_month_count_total
        total_grace['monthly_availed_cl']=float(monthly_availed_cl)+float(monthly_availed_hd_cl/2)
        total_grace['monthly_availed_el']=float(monthly_availed_el)+float(monthly_availed_hd_el/2)
        total_grace['monthly_availed_sl']=float(monthly_availed_sl)+float(monthly_availed_hd_sl/2)
        total_grace['monthly_availed_ab']=float(monthly_availed_ab)+float(monthly_availed_hd_ab/2)
        total_grace['monthly_total_availed_leave']= total_grace['monthly_availed_cl'] + total_grace['monthly_availed_el'] + total_grace['monthly_availed_sl']

        total_grace['monthly_od_count'] = monthly_availed_data.filter(Q(is_requested=True)& Q(is_deleted=False)&
                                                        (Q(request_type='FOD')|Q(request_type='POD'))&
                                                        (Q(approved_status='pending')|Q(approved_status='approved')
                                                        )).count()

        total_grace['monthly_od_duration'] = monthly_availed_data.filter(Q(is_requested=True)&Q(is_deleted=False)&
                                                        (Q(request_type='FOD')|Q(request_type='POD'))&
                                                        (Q(approved_status='pending')|Q(approved_status='approved')
                                                        )).aggregate(Sum('duration'))['duration__sum']

        ###############

        core_user_detail=TCoreUserDetail.objects.filter(cu_user=employee_id,cu_is_deleted=False).values('joining_date',
                                                                                                    'granted_cl',
                                                                                                    'granted_sl',
                                                                                                    'granted_el'
                                                                                                    )
        print('core_user_detail',core_user_detail)
        if core_user_detail:
            if core_user_detail[0]['joining_date']>total_month_grace[0]['year_start_date']:
                approved_leave=JoiningApprovedLeave.objects.filter(employee=employee_id,is_deleted=False).values('cl', 'el', 'sl',
                                                                                                                 'year', 'month',
                                                                                                                 'first_grace')
                if approved_leave:
                    total_grace['granted_cl']=approved_leave[0]['cl']
                    total_grace['cl_balance']=float(approved_leave[0]['cl'] if approved_leave[0]['cl'] else 0.0) -float(total_grace['yearly_availed_cl'])
                    total_grace['granted_el']=approved_leave[0]['el']
                    total_grace['el_balance']=float(approved_leave[0]['el'] if approved_leave[0]['el'] else 0.0 ) -float(total_grace['yearly_availed_el'])
                    total_grace['granted_sl']=approved_leave[0]['sl']
                    total_grace['sl_balance']=float( approved_leave[0]['sl'] if approved_leave[0]['sl'] else 0.0 ) -float(total_grace['yearly_availed_sl'])
                    total_grace['total_granted_leave']=float(approved_leave[0]['cl'] if approved_leave[0]['cl'] else 0.0) + float(approved_leave[0]['el'] if approved_leave[0]['el'] else 0.0) + float(approved_leave[0]['sl'] if approved_leave[0]['sl'] else 0.0)
                    total_grace['total_leave_balances']=float(total_grace['total_granted_leave']) - float(total_grace['yearly_total_availed_leave'])
                    if total_month_grace[0]['month']==approved_leave[0]['month']:    #for joining month only
                        total_grace['total_month_grace']=approved_leave[0]['first_grace']
                        total_grace['month_start']=core_user_detail[0]['joining_date']
                        total_grace['grace_balance']=total_grace['total_month_grace'] - total_grace['availed_grace']
            else:
                total_grace['granted_cl']=core_user_detail[0]['granted_cl']
                total_grace['cl_balance']=float(core_user_detail[0]['granted_cl']) - float(total_grace['yearly_availed_cl'])
                total_grace['granted_el']=core_user_detail[0]['granted_el']
                total_grace['el_balance']=float(core_user_detail[0]['granted_el']) - float(total_grace['yearly_availed_el'])
                total_grace['granted_sl']=core_user_detail[0]['granted_sl']
                total_grace['sl_balance']=float(core_user_detail[0]['granted_sl']) - float(total_grace['yearly_availed_sl'])
                total_grace['total_granted_leave']=float(core_user_detail[0]['granted_cl']) + float(core_user_detail[0]['granted_el']) + float(core_user_detail[0]['granted_sl'])
                total_grace['total_leave_balances']=float(total_grace['total_granted_leave']) - float(total_grace['yearly_total_availed_leave'])

        data_dict['result'] = total_grace
        time_last = datetime.now()-aa
        print("time_last",time_last)
        # data_dict['result'] = "Successful"
        if total_grace:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_SUCCESS
        elif len(total_grace) == 0:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_NO_DATA
        else:
            data_dict['request_status'] = 0
            data_dict['msg'] = settings.MSG_ERROR
        total_grace = data_dict
        return Response(total_grace)
#:::::::::::::::::::::: ATTENDANCE SPECIALDAY MASTER:::::::::::::::::::::::::::#
class AttendanceSpecialdayMasterAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = AttendanceSpecialdayMaster.objects.filter(is_deleted=False)
    serializer_class = AttendanceSpecialdayMasterAddSerializer
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response

class AttendanceSpecialdayMasterEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = AttendanceSpecialdayMaster.objects.all()
    serializer_class = AttendanceSpecialdayMasterEditSerializer
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response

class AttendanceSpecialdayMasterDeleteView(generics.RetrieveUpdateAPIView):
	permission_classes = [IsAuthenticated]
	authentication_classes = [TokenAuthentication]
	queryset = AttendanceSpecialdayMaster.objects.all()
	serializer_class = AttendanceSpecialdayMasterDeleteSerializer

class AttendanceEmployeeReportView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = TCoreUserDetail.objects.filter(cu_is_deleted=False)
    serializer_class = AttendanceEmployeeReportSerializer

    def get(self, request, *args, **kwargs):
        
        ## decleare the date parameret
        date =self.request.query_params.get('date', None)
        print('date',date)
        
        ## convert date argument to date object
        date_object = datetime.strptime(date, '%Y-%m-%d').date()
        print('date_object',date_object)

        response = super(AttendanceEmployeeReportView,self).get(self, request, args, kwargs)

        ## get month from MonthMaster by date from argument ##
        total_month=AttendenceMonthMaster.objects.filter(month_start__date__lte=date_object,
                                        month_end__date__gte=date_object,is_deleted=False).values('grace_available',
                                                                                 'year_start_date',
                                                                                 'year_end_date',
                                                                                 'month',
                                                                                 'month_start',
                                                                                 'month_end')
        ###### Sunday count in month range ######

        ## Thease prints for month start and month end ##
        print('month_start-->',total_month[0]['month_start'].date())
        print('month_end-->',total_month[0]['month_end'].date())

        sunday_count = 0
        saturday_count = 0
        start_date = total_month[0]['month_start'].date()
        end_date = total_month[0]['month_end'].date()
        print(start_date," ",end_date)
        current_month= ((total_month[0]['month_end'].date()+ timedelta(days=1)) - total_month[0]['month_start'].date()).days
        date_generated = [start_date + timedelta(days=x) for x in range(0, current_month)] 
        # print('current_month-->',current_month)
        for get_day in date_generated:
            if get_day.weekday()==6:
                sunday_count +=1
            if get_day.weekday()==5:
                saturday_count +=1 
        print('sunday_count-->',sunday_count)

        for data in response.data:
            
            ## get the user name and set first_name and last_name in different veriable ##
            user_name = User.objects.filter(id=data['cu_user'],is_active=True).values('first_name','last_name')
            first_name = user_name[0]['first_name'] if user_name[0]['first_name'] else '' 
            last_name = user_name[0]['last_name'] if user_name[0]['last_name'] else ''

            ## get current month filter ##
            monthly_availed_data = AttendanceApprovalRequest.objects.filter(attendance__employee=data['cu_user'],is_requested=True,is_deleted=False,
                                                                duration_start__gte=total_month[0]['month_start'],
                                                                duration_start__lte=total_month[0]['month_end'])

            ## Present Days calculation ##
            atten_count = Attendance.objects.filter(employee=data['cu_user'],is_present=True,is_deleted=False,date__gte=total_month[0]['month_start'].date(),
                                                    date__lte=total_month[0]['month_end'].date()).count()
            ## Print For debugging ##
            print('atten_count-->',atten_count)

            ## Half Day calculation ##
            half_day = monthly_availed_data.filter(Q(is_deleted=False)& Q(attendance__employee=data['cu_user']) & Q(request_type='HD')).count()
            print('half_day-->',half_day)
            half_day =half_day/2

            ### cl,el,sl,ab Full Day count ###
            fd_cl = monthly_availed_data.filter((Q(approved_status='pending')|Q(approved_status='approved')),attendance__employee=data['cu_user'],
                                                                request_type='FD', leave_type='CL',is_requested=True,is_deleted=False).count()
            fd_el = monthly_availed_data.filter((Q(approved_status='pending')|Q(approved_status='approved')),attendance__employee=data['cu_user'],
                                                                request_type='FD', leave_type='EL',is_requested=True,is_deleted=False).count()
            fd_sl = monthly_availed_data.filter((Q(approved_status='pending')|Q(approved_status='approved')),attendance__employee=data['cu_user'],
                                                                request_type='FD', leave_type='SL',is_requested=True,is_deleted=False).count()
            fd_ab = monthly_availed_data.filter((Q(approved_status='pending')|Q(approved_status='approved')),attendance__employee=data['cu_user'],
                                                                request_type='FD', leave_type='AB',is_requested=True,is_deleted=False).count()

            ### cl,el,sl,ab Half Day count ###
            hd_cl = monthly_availed_data.filter((Q(approved_status='pending')|Q(approved_status='approved')),attendance__employee=data['cu_user'],
                                                                request_type='HD', leave_type='CL',is_requested=True,is_deleted=False).count()
            hd_el = monthly_availed_data.filter((Q(approved_status='pending')|Q(approved_status='approved')),attendance__employee=data['cu_user'],
                                                                request_type='HD', leave_type='EL',is_requested=True,is_deleted=False).count()
            hd_sl = monthly_availed_data.filter((Q(approved_status='pending')|Q(approved_status='approved')),attendance__employee=data['cu_user'],
                                                                request_type='HD', leave_type='SL',is_requested=True,is_deleted=False).count()
            hd_ab = monthly_availed_data.filter((Q(approved_status='pending')|Q(approved_status='approved')),attendance__employee=data['cu_user'],
                                                                request_type='HD', leave_type='AB',is_requested=True,is_deleted=False).count()

            ## comment by developer for few days and tesing ##
            # current_month = ((total_month[0]['month_end'].date()+ timedelta(days=1)) - total_month[0]['month_start'].date()).days
            
            ## Holiday count in month range ##
            holyday_count = HolidaysList.objects.filter(status=True,is_deleted=False,holiday_date__gte=total_month[0]['month_start'].date(),
                                                        holiday_date__lte=total_month[0]['month_end'].date()).count()

            ### cl,el,sl,ab Half Day count ###
            cl_taken = float(fd_cl)+float(hd_cl/2)
            el_taken = float(fd_el)+float(hd_el/2)
            sl_taken = float(fd_sl)+float(hd_sl/2)
            ab_taken = float(fd_ab)+float(hd_ab/2)

            ## Present day calculation ##
            present_days = (atten_count-half_day)

            ## total Woring days calculation ##
            total_working_day = (sunday_count + holyday_count + present_days + cl_taken + el_taken + sl_taken) - ab_taken
            
            ## Print fo debuging ##
            print('get_holyday_count-->',holyday_count)          
            print('name : ',first_name+' '+last_name)
            print('total_days_in_month-->',current_month)
            print('user--------->',data['cu_user'])
            print('half_day-->',half_day)
            print('CL_taken-->',cl_taken)
            print('EL_taken-->',el_taken)
            print('SL_taken-->',sl_taken)
            print('AB_taken-->',ab_taken)
            print('total_working_day-->',total_working_day)

            ### Data Binding in JSON ##
            data['cu_user'] = first_name+' '+last_name
            data['sunday'] = sunday_count
            data['present_days'] = present_days
            data['cl_taken'] = cl_taken
            data['el_taken'] = el_taken
            data['sl_taken'] = sl_taken
            data['ab_taken'] = ab_taken
            data['total_days_in_month'] = current_month
            data['holiday'] = holyday_count
            data['total_working_day'] = total_working_day
            
        return response

class logListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = AttendenceAction.objects.all().order_by('-id')
    serializer_class = logListSerializer
    pagination_class = CSPageNumberPagination
    @response_modify_decorator_list_or_get_after_execution_for_pagination
    def get(self, request, *args, **kwargs):
        response=super(logListView,self).get(self, request, args, kwargs)
        for data in response.data['results']:
            data['user_role_details']={
                'user_id':data['user'],
                'user_name':userdetails(data['user']),
                'role':TCoreRole.objects.get(id=str(TMasterModuleRoleUser.objects.get(mmr_module__cm_name__iexact='hrms',mmr_user=request.user).mmr_role)).cr_name ,
                'department': department(data['user']),
                'designation': designation(data['user'])
            }

        return response

#::::::::::::::::::::::::::::::::::::::::: Report :::::::::::::::::::::::::::::::::::::::#
class AttandanceAdminOdMsiReportView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = AttandanceAdminOdMsiReportSerializer

    @response_modify_decorator_list_after_execution
    def get(self, request, *args, **kwargs):
        total_list = []
        year =self.request.query_params.get('year', None)
        month =self.request.query_params.get('month', None)
        month_range = AttendenceMonthMaster.objects.filter(month=month,month_end__year=year).values('month_start__date','month_end__date')
        if month_range:
            month_start = month_range[0]['month_start__date']
            month_end = month_range[0]['month_end__date']
            module_user_list = list(TMasterModuleRoleUser.objects.filter(
                mmr_module__cm_name='ATTENDANCE & HRMS',mmr_type=3).values_list('mmr_user',flat=True))

            print('module_user_list',module_user_list)
            od_emp_list = set(AttendanceApprovalRequest.objects.filter(Q(is_requested=True)& Q(is_deleted=False)&Q(duration_start__date__gte=month_start)&Q(duration_start__date__lte=month_end)&(Q(request_type='FOD')|Q(request_type='POD'))&(Q(approved_status='pending')|Q(approved_status='approved')|Q(approved_status='reject')),attendance__employee__in=od_emp_list).values_list('attendance__employee', flat=True))

            print("get_od_emp_details",od_emp_list)
            od_details = AttendanceApprovalRequest.objects.filter(Q(is_requested=True)& Q(is_deleted=False)&
                                                                    Q(duration_start__date__gte=month_start)&
                                                                    Q(duration_start__date__lte=month_end)&
                                                                    (Q(request_type='FOD')|Q(request_type='POD'))&
                                                                    (Q(approved_status='pending')|Q(approved_status='approved')|
                                                                    Q(approved_status='reject')),attendance__employee__in=od_emp_list)

            if od_emp_list:
                for emp in od_emp_list:
                    data_list = []
                    print("emp",emp)
                    od_duration = od_details.filter(attendance__employee=emp).aggregate(Sum('duration'))['duration__sum']
                    approved_od = od_details.filter(attendance__employee=emp,approved_status='approved').count()
                    pending_od = od_details.filter(attendance__employee=emp,approved_status='pending').count()
                    reject_od = od_details.filter(attendance__employee=emp,approved_status='reject').count()
                    total_od = approved_od + pending_od + reject_od

                    print("khlkhkjg", total_od , approved_od , pending_od , reject_od)

                    # user_details = TCoreUserDetail.objects.filter(cu_user=emp,cu_is_deleted=False).values('cu_user__first_name',
                    #                                                 'cu_user__last_name', 'cu_punch_id', 'hod__first_name','hod__last_name')#reporting_head
                    user_details = TCoreUserDetail.objects.filttotal_lister(cu_user=emp,cu_is_deleted=False).annotate(
                                                                        user_first_name=Case(
                                                                        When(cu_user__first_name__isnull=True, then=Value("")),
                                                                        When(cu_user__first_name__isnull=False, then=F('cu_user__first_name')),
                                                                        output_field=CharField()
                                                                        ),user_last_name=Case(
                                                                        When(cu_user__last_name__isnull=True, then=Value("")),
                                                                        When(cu_user__last_name__isnull=False, then=F('cu_user__last_name')),
                                                                        output_field=CharField()
                                                                        ),reporting_head_first_name=Case(
                                                                        When(reporting_head__first_name__isnull=True, then=Value("")),
                                                                        When(reporting_head__first_name__isnull=False, then=F('reporting_head__first_name')),
                                                                        output_field=CharField()
                                                                        ),reporting_head_last_name=Case(
                                                                        When(reporting_head__last_name__isnull=True, then=Value("")),
                                                                        When(reporting_head__last_name__isnull=False, then=F('reporting_head__last_name')),
                                                                        output_field=CharField()
                                                                        ),hod_first_name=Case(
                                                                        When(hod__first_name__isnull=True, then=Value("")),
                                                                        When(hod__first_name__isnull=False, then=F('hod__first_name')),
                                                                        output_field=CharField()
                                                                        ),hod_last_name=Case(
                                                                        When(hod__last_name__isnull=True, then=Value("")),
                                                                        When(hod__last_name__isnull=False, then=F('hod__last_name')),
                                                                        output_field=CharField()
                                                                        ),cu_emp_code_n=Case(
                                                                        When(cu_emp_code__isnull=True, then=Value("")),
                                                                        When(cu_emp_code__isnull=False, then=F('cu_emp_code')),
                                                                        output_field=CharField()),).values(
                                                                        'user_first_name','user_last_name','reporting_head_first_name','reporting_head_last_name',
                                                                        'hod_first_name','hod_last_name','cu_emp_code_n').order_by('-hod_first_name')
                    print("user_details",  user_details[0])
                    employee_name = user_details[0]['user_first_name']+" "+user_details[0]['user_last_name']
                    reporting_head = user_details[0]['reporting_head_first_name']+" "+user_details[0]['reporting_head_last_name']
                    hod_name = user_details[0]['hod_first_name']+" "+user_details[0]['hod_last_name']
                    # data_dict['employee_name'] = user_details.__dict__['cu_user__first_name']
                    employee_code = user_details[0]['cu_emp_code_n']
                    data_list = [employee_name, reporting_head, hod_name, employee_code, total_od, od_duration, approved_od, pending_od, reject_od]

                    total_list.append(data_list)

        # print('total_list--->',total_list)
        if os.path.isdir('media/attendance/od_mis_report/document'):
            file_name = 'media/attendance/od_mis_report/document/od_mis_report.csv'
        else:
            os.makedirs('media/attendance/od_mis_report/document')
            file_name = 'media/attendance/od_mis_report/document/od_mis_report.csv'
        
        #########################################################
        df = DataFrame(total_list, columns= ['Employee Name', 'Reporting Head', 'HOD Name', 'Employee_code', 'Total Od', 'Total Min', 'Approved', 'Pending', 'Rejected'])
        export_csv = df.to_csv (file_name, index = None, header=True)

        #########################################################
        #url_path = request.build_absolute_uri(file_name) if file_name else None
        #print("url_path",url_path)
        
        '''
            Editied By Rupam Hazra on 2019-12-17
        '''
        #print('host',request.get_host())

        if request.is_secure():
            protocol = 'https://'
        else:
            protocol = 'http://'

        url = getHostWithPort(request) + file_name if file_name else None
        #print('url',url)
        #url = re.search('https://(\d+\.)+\d+\:\d{4}\/',str(url_path)).group()
        #print("url",url)
        #url_path = url+file_name
        # url_path = "http://13.232.240.233:8000/"+file_name
        return Response(url)

class AttandanceAdminOdMsiReportDetailsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = AttandanceAdminOdMsiReportSerializer

    @response_modify_decorator_list_after_execution
    def get(self, request, *args, **kwargs):
        total_list = []
        day_start =self.request.query_params.get('day_start', None)
        day_end =self.request.query_params.get('day_end', None)
        year =self.request.query_params.get('year', None)
        month =self.request.query_params.get('month', None)
        dept_filter = self.request.query_params.get('dept_filter', None)
        emp_list = []
        total_user_list = []
        filter_search = {}
        module_user_list = list(TMasterModuleRoleUser.objects.filter(mmr_module__cm_name='ATTENDANCE & HRMS',mmr_type=3).values_list('mmr_user',flat=True))
        print('module_user_list',module_user_list)

        if dept_filter:
            dept_list = dept_filter.split(',')
            emp_list = list(TCoreUserDetail.objects.filter(department__in=dept_list).values_list('cu_user',flat=True))
            print("emp_list",emp_list)
            # filter_search['attendance__employee__in']=emp_list
            total_user_list = [val for val in module_user_list if val in emp_list]
            filter_search['attendance__employee__in']=total_user_list
        else:
            filter_search['attendance__employee__in'] = module_user_list

        if day_start and day_end:
            month_start = datetime.strptime(day_start,"%Y-%m-%d").date()
            month_end = datetime.strptime(day_end,"%Y-%m-%d").date()

        elif year and month:
            month_range = AttendenceMonthMaster.objects.filter(month=month,month_end__year=year).values('month_start__date','month_end__date')
            if month_range:
                month_start = month_range[0]['month_start__date']
                month_end = month_range[0]['month_end__date']
        if month_start and month_end:       
            od_emp_list = set(AttendanceApprovalRequest.objects.filter(Q(**filter_search)&
                                                                        Q(is_requested=True)& Q(is_deleted=False)&
                                                                        Q(duration_start__date__gte=month_start)&
                                                                        Q(duration_start__date__lte=month_end)&
                                                                        (Q(request_type='FOD')|Q(request_type='POD'))&
                                                                        (Q(approved_status='pending')|Q(approved_status='approved')|
                                                                        Q(approved_status='reject'))).values_list('attendance__employee', 
                                                                        flat=True))

            print("get_od_emp_details",od_emp_list)
            od_details = AttendanceApprovalRequest.objects.filter(Q(**filter_search)&
                                                                    Q(is_requested=True)& Q(is_deleted=False)&
                                                                    Q(duration_start__date__gte=month_start)&
                                                                    Q(duration_start__date__lte=month_end)&
                                                                    (Q(request_type='FOD')|Q(request_type='POD'))&
                                                                    (Q(approved_status='pending')|Q(approved_status='approved')|
                                                                    Q(approved_status='reject')))

            if od_emp_list:
                for emp in od_emp_list:
                    # print("emp",emp)
                    user_details = TCoreUserDetail.objects.filter(cu_user=emp,cu_is_deleted=False).annotate(
                                                                        user_first_name=Case(
                                                                        When(cu_user__first_name__isnull=True, then=Value("")),
                                                                        When(cu_user__first_name__isnull=False, then=F('cu_user__first_name')),
                                                                        output_field=CharField()
                                                                        ),user_last_name=Case(
                                                                        When(cu_user__last_name__isnull=True, then=Value("")),
                                                                        When(cu_user__last_name__isnull=False, then=F('cu_user__last_name')),
                                                                        output_field=CharField()
                                                                        ),reporting_head_first_name=Case(
                                                                        When(reporting_head__first_name__isnull=True, then=Value("")),
                                                                        When(reporting_head__first_name__isnull=False, then=F('reporting_head__first_name')),
                                                                        output_field=CharField()
                                                                        ),reporting_head_last_name=Case(
                                                                        When(reporting_head__last_name__isnull=True, then=Value("")),
                                                                        When(reporting_head__last_name__isnull=False, then=F('reporting_head__last_name')),
                                                                        output_field=CharField()
                                                                        ),hod_first_name=Case(
                                                                        When(hod__first_name__isnull=True, then=Value("")),
                                                                        When(hod__first_name__isnull=False, then=F('hod__first_name')),
                                                                        output_field=CharField()
                                                                        ),hod_last_name=Case(
                                                                        When(hod__last_name__isnull=True, then=Value("")),
                                                                        When(hod__last_name__isnull=False, then=F('hod__last_name')),
                                                                        output_field=CharField()
                                                                        ),sap_personnel_no_n=Case(
                                                                        When(sap_personnel_no__isnull=True, then=Value("")),
                                                                        When(sap_personnel_no__isnull=False, then=F('sap_personnel_no')),
                                                                        output_field=CharField()
                                                                        ),cu_emp_code_n=Case(
                                                                        When(cu_emp_code__isnull=True, then=Value("")),
                                                                        When(cu_emp_code__isnull=False, then=F('cu_emp_code')),
                                                                        output_field=CharField()),).values(
                                                                        'user_first_name','user_last_name','reporting_head_first_name',
                                                                        'reporting_head_last_name','hod_first_name','hod_last_name','sap_personnel_no_n',
                                                                        'cu_emp_code_n').order_by('-hod_first_name')
                    # print("user_details",  user_details)
                    employee_name = user_details[0]['user_first_name']+" "+user_details[0]['user_last_name']
                    reporting_head = user_details[0]['reporting_head_first_name']+" "+user_details[0]['reporting_head_last_name']
                    hod_name = user_details[0]['hod_first_name']+" "+user_details[0]['hod_last_name']
                    # data_dict['employee_name'] = user_details.__dict__['cu_user__first_name']
                    emp_sap_id = user_details[0]['sap_personnel_no_n']
                    emp_code = user_details[0]['cu_emp_code_n']
                    request_list = od_details.filter(attendance__employee=emp)
                    if request_list:
                        for request_data in request_list:
                            data_list = []
                            req_date = request_data.duration_start.date()
                            req_start = request_data.duration_start.time()
                            req_end = request_data.duration_end.time()
                            justification = request_data.justification
                            approved_status = request_data.approved_status

                            data_list = [employee_name, reporting_head, hod_name, emp_code, emp_sap_id, req_date, req_start, req_end, justification, approved_status]

                            total_list.append(data_list)

        # print('total_list--->',total_list)
        if os.path.isdir('media/attendance/od_mis_report/document'):
            file_name = 'media/attendance/od_mis_report/document/od_mis_details_report.csv'
        else:
            os.makedirs('media/attendance/od_mis_report/document')
            file_name = 'media/attendance/od_mis_report/document/od_mis_details_report.csv'
        
        #########################################################
        df = DataFrame(total_list, columns= ['Employee Name', 'Reporting Head','HOD Name','Employee Code','SAP No','Attendance Date','Duration Start','Duration End', 'Justification','Approved Status'])
        export_csv = df.to_csv (file_name, index = None, header=True)

        if request.is_secure():
            protocol = 'https://'
        else:
            protocol = 'http://'

        url = getHostWithPort(request) + file_name if file_name else None
        print('url',url)

        return Response(url)

class AttandanceAdminSAPReportView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    # serializer_class = AttandanceAdminOdMsiReportSerializer

    @response_modify_decorator_list_after_execution
    def get(self, request, *args, **kwargs):
        '''
            If "is_sap = 1" then API returns excel with SAP id otherwise return with Epm_name,code,punch id.
        '''
        total_list = []
        cur_date =self.request.query_params.get('cur_date', None)
        dept_filter =self.request.query_params.get('dept_filter', None)
        is_sap =self.request.query_params.get('is_sap', None)
        year = self.request.query_params.get('year', None)
        month = self.request.query_params.get('month', None)
        emp_list = []
        total_user_list = []
        module_user_list = []
        req_filter = {}
        date_range = []
        header = []
        '''
            This API is use to generate SAP report as .csv file on "Full/Half Day" leave Basic.Conditions are below:-
            'date'-> It is current date value, from front end. Used to get previous month's date range.
            'module_user_list'-> Get 'ATTENDANCE & HRMS' module users as list formet.
        '''
        if cur_date:
            date = datetime.strptime(cur_date, "%Y-%m-%d")
            date_range_first = AttendenceMonthMaster.objects.filter(month_start__date__lte=date,month_end__date__gte=date).values('month_start__date','month_end__date')
            date = date_range_first[0]['month_start__date'] - timedelta(days=1)
            date_range = AttendenceMonthMaster.objects.filter(month_start__date__lte=date,month_end__date__gte=date).values('month_start__date','month_end__date')

        elif year and month:
            date_range = AttendenceMonthMaster.objects.filter(month=month,month_end__year=year).values('month_start__date','month_end__date')


        if date_range:
            print("date_range",date_range)
            req_filter['duration_start__date__gte']=date_range[0]['month_start__date']
            req_filter['duration_start__date__lte']=date_range[0]['month_end__date']
            req_filter['is_requested'] = True
            req_filter['is_deleted'] = False

            # Avoid director punch ids in SAP report.
            director_punch_id = ['10111032','10011271','10111036','00000160','00000171','00000022','00000168','00000163','00000161','00000016','00000018','00000162']
            director_user_id = list(TCoreUserDetail.objects.filter(cu_punch_id__in=director_punch_id).values_list('cu_user',flat=True))
            
            module_user_list = list(TMasterModuleRoleUser.objects.filter(~Q(mmr_user__in=director_user_id),mmr_module__cm_name='ATTENDANCE & HRMS',mmr_type=3).values_list('mmr_user',flat=True))
            print('module_user_list',module_user_list)
            if dept_filter:
                dept_list = dept_filter.split(',')
                emp_list = list(TCoreUserDetail.objects.filter(department__in=dept_list).values_list('cu_user',flat=True))
                print("emp_list",emp_list)
                # req_filter['attendance__employee__in']=emp_list
                total_user_list = [val for val in module_user_list if val in emp_list]
                req_filter['attendance__employee__in']=total_user_list
            else:
                req_filter['attendance__employee__in']=module_user_list
            print(req_filter['attendance__employee__in'])

        if req_filter:
            request_details = AttendanceApprovalRequest.objects.filter(((Q(leave_type_changed_period__isnull=False)&(Q(leave_type_changed_period='FD')|Q(leave_type_changed_period='HD')))|
                                                                        (Q(leave_type_changed_period__isnull=True)&(Q(request_type='FD')|Q(request_type='HD')))),
                                                                        **req_filter)

            # print("request_details",request_details)
            lv_emp_list = set(request_details.filter().values_list('attendance__employee',flat=True))
            if lv_emp_list:
                # print("lv_emp_list",lv_emp_list)
                for employee_id in lv_emp_list:
                    sap_no = None
                    sap_no = TCoreUserDetail.objects.only('sap_personnel_no').get(cu_user=employee_id).sap_personnel_no
                    # user_details = TCoreUserDetail.objects.filter(cu_user=employee_id).values('cu_user__first_name','cu_user__last_name','sap_personnel_no',
                    #                                                                             'cu_emp_code','cu_punch_id')
                    # print("sap_no",sap_no)
                    if sap_no and sap_no!='#N/A':
                        # sap_no = user_details[0]['sap_personnel_no']
                        # user_name = user_details[0]['cu_user__first_name']+" "+user_details[0]['cu_user__last_name']
                        # cu_emp_code = user_details[0]['cu_emp_code']
                        # cu_punch_id = user_details[0]['cu_punch_id']
                        date_list = set(request_details.filter(attendance__employee=employee_id).values_list('duration_start__date',flat=True))
                        availed_master_wo_reject_fd = request_details.\
                        filter((Q(approved_status='pending')|Q(approved_status='approved')|Q(approved_status='reject')),
                                (Q(leave_type__isnull=False)|Q(leave_type_changed_period__isnull=False)),
                                attendance__employee=employee_id,
                                attendance_date__in=date_list,is_requested=True,is_deleted=False).annotate(
                                    leave_type_final = Case(
                                    When((Q(leave_type_changed_period__isnull=False)&Q(leave_type_changed_period='FD')),then=F('leave_type_changed')),
                                    When((Q(leave_type_changed_period__isnull=True)&Q(request_type='FD')),then=F('leave_type')),
                                    output_field=CharField()
                                ),
                                leave_type_final_hd = Case(
                                    When((Q(leave_type_changed_period__isnull=False)&Q(leave_type_changed_period='HD')),then=F('leave_type_changed')),
                                    When((Q(leave_type_changed_period__isnull=True)&Q(request_type='HD')),then=F('leave_type')),
                                    output_field=CharField()
                                ),
                                ).values('leave_type_final','leave_type_final_hd','attendance_date').distinct()
                        # print("availed_master_wo_reject_fd",availed_master_wo_reject_fd)

                        if availed_master_wo_reject_fd:
                            for data in date_list:
                                data_str = data.strftime("%d.%m.%Y")
                                # print("data_str",data_str, type(data_str))
                                subtype = None
                                data_list = []
                                availed_FD=availed_master_wo_reject_fd.filter(attendance_date=data)
                                
                                #print("availed_HD",availed_FD)
                                if availed_FD.filter(leave_type_final__isnull=False):
                                    if availed_FD.values('leave_type_final').count() >1:
                                        if availed_FD.filter(leave_type_final='AB'):
                                            # availed_ab=availed_ab+1.0
                                            subtype = '1050'

                                        elif availed_FD.filter(leave_type_final='CL'):
                                            # availed_cl=availed_cl+1.0
                                            subtype = '1020'
                                                    

                                    else:
                                        l_type=availed_FD[0]['leave_type_final']
                                        if l_type == 'CL':
                                            # availed_cl=availed_cl+1.0
                                            subtype = '1020'
                                        elif l_type == 'EL':
                                            # availed_el=availed_el+1.0
                                            subtype = '1000'
                                        elif l_type == 'SL':
                                            # availed_sl=availed_sl+1.0
                                            subtype = '1010'
                                        elif l_type == 'AB':
                                            # availed_ab=availed_ab+1.0
                                            subtype = '1050'

                                elif availed_FD.filter(leave_type_final_hd__isnull=False):
                                    if availed_FD.values('leave_type_final_hd').count() >1:
                                        if availed_FD.filter(leave_type_final_hd='AB'):
                                            # availed_hd_ab=availed_hd_ab+0.5
                                            subtype = '9050'

                                        elif availed_FD.filter(leave_type_final_hd='CL'):
                                            # availed_hd_cl=availed_hd_cl+0.5
                                            subtype = '9020'
                                                    

                                    else:
                                        l_type=availed_FD[0]['leave_type_final_hd']
                                        if l_type == 'CL':
                                            # availed_hd_cl=availed_hd_cl+0.5
                                            subtype = '9020'

                                        elif l_type == 'EL':
                                            # availed_hd_el=availed_hd_el+0.5
                                            subtype = '9000'
                                        elif l_type == 'SL':
                                            # availed_hd_sl=availed_hd_sl+0.5
                                            subtype = '9010'

                                        elif l_type == 'AB':
                                            # availed_hd_ab=availed_hd_ab+1.0
                                            subtype = '9050'

                                if subtype:
                                    data_list = [sap_no, subtype, data_str, data_str]
                                    # header = ['PERSONNEL NUMBER(SAP ID)',' SUBTYPE',' BEGIN DATE',' ENDDATE']
                                    total_list.append(data_list)
                                # elif subtype:
                                #     data_list = [user_name, cu_emp_code, cu_punch_id, subtype, data_str, data_str]
                                #     header = ['FULL NAME','EMPLOYEE CODE','PUNCH ID',' SUBTYPE',' BEGIN DATE',' ENDDATE']
                                # total_list.append(data_list)


        # print('total_list--->',total_list)
        if os.path.isdir('media/attendance/sap_report/document'):
            file_name = 'media/attendance/sap_report/document/sap_report.csv'
        else:
            os.makedirs('media/attendance/sap_report/document')
            file_name = 'media/attendance/sap_report/document/sap_report.csv'
        
        #########################################################
        df = DataFrame(total_list, columns= ['PERSONNEL NUMBER(SAP ID)',' SUBTYPE',' BEGIN DATE',' ENDDATE'])
        export_csv = df.to_csv (file_name, index = None, header=True)

        if request.is_secure():
            protocol = 'https://'
        else:
            protocol = 'http://'

        url = getHostWithPort(request) + file_name if file_name else None
        print('url',url)

        return Response(url)

class AttandanceUserLeaveReportTillDateView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    # @response_modify_decorator_list_after_execution
    def get(self, request, *args, **kwargs):
        '''
            If "is_sap = 1" then API returns excel with SAP id otherwise return with Epm_name,code,punch id.
        '''
        total_list = []
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        total_user_list = []
        req_filter = {}
        header = []

        if start_date and end_date:
            # print("kjgjkk",datetime.strptime(start_date, "%Y-%m-%d").date())
            req_filter['attendance__date__gte'] = datetime.strptime(start_date, "%Y-%m-%d").date()
            req_filter['attendance__date__lte'] = datetime.strptime(end_date, "%Y-%m-%d").date()

        # user_details = TCoreUserDetail.objects.filter(
        #     cu_user_id__in=list(
        #         Attendance.objects.filter(is_deleted=False).values_list('employee_id',flat=True))
        #         ).values('cu_user_id','cu_punch_id','cu_emp_code','sap_personnel_no','joining_date','granted_cl','granted_sl','granted_el')
        
        '''
            Modified By Rupam Hazra 18.02.2020
        '''
        user_details = TCoreUserDetail.objects.filter(
            cu_user_id__in=(TCoreUserDetail.objects.filter(~Q(cu_punch_id='#N/A')).values_list('cu_user_id',flat=True)),cu_is_deleted=False).values('cu_user_id','cu_punch_id','cu_emp_code','sap_personnel_no',
                'joining_date','granted_cl','granted_sl','granted_el')
        
        
        print("user_details",user_details)
        time.sleep(10)
        for user in user_details:
            data_list = []
            # print("user['cu_user_id']",user['cu_user_id'])
            req_filter['attendance__employee'] = user['cu_user_id']
            req_filter['is_requested']=True
            user_name = userdetails(int(user['cu_user_id']))
            sap_personnel_no = str(user['sap_personnel_no']) if user['sap_personnel_no'] else ''
            punch_id = str(user['cu_punch_id']) if user['cu_punch_id'] else ''
            emp_code = str(user['cu_emp_code']) if user['cu_emp_code'] else ''
            granted_cl = user['granted_cl']
            granted_sl = user['granted_sl']
            granted_el = user['granted_el']
            print("user['joining_date']",user['joining_date'])
            if user['joining_date'].date()>datetime.strptime(start_date, "%Y-%m-%d").date():
                approved_leave=JoiningApprovedLeave.objects.filter(employee=user['cu_user_id'],is_deleted=False).values('cl', 'el', 'sl')
                if approved_leave:
                    granted_cl = approved_leave[0]['cl']
                    granted_sl = approved_leave[0]['sl']
                    granted_el = approved_leave[0]['el']
            availed_hd_cl=0.0
            availed_hd_el=0.0
            availed_hd_sl=0.0
            availed_hd_ab=0.0
            availed_cl=0.0
            availed_el=0.0
            availed_sl=0.0
            availed_ab=0.0

            print("end_date",req_filter)
            daily_data = AttendanceApprovalRequest.objects.filter(((Q(leave_type_changed_period__isnull=False)&
                                                                    (Q(leave_type_changed_period='FD')|Q(leave_type_changed_period='HD')))|
                                                                    (Q(leave_type_changed_period__isnull=True)&(Q(request_type='FD')|Q(request_type='HD')))),
                                                                    **req_filter).values('duration_start__date').distinct()
                                                
            # print("yearly_attendence_daily_data",daily_data)
            yearly_date_list = [x['duration_start__date'] for x in daily_data.iterator()]
            # print("yearly_date_list",yearly_date_list)
            # for data in attendence_daily_data.iterator():
                # print(datetime.now())
            availed_master_wo_reject_fd = AttendanceApprovalRequest.objects.\
                    filter((Q(approved_status='pending')|Q(approved_status='approved')|Q(approved_status='reject')),
                            (Q(leave_type__isnull=False)|Q(leave_type_changed_period__isnull=False)),
                            attendance__employee=user['cu_user_id'],
                            attendance_date__in=yearly_date_list,is_requested=True,is_deleted=False).annotate(
                                leave_type_final = Case(
                                When((Q(leave_type_changed_period__isnull=False)&Q(leave_type_changed_period='FD')),then=F('leave_type_changed')),
                                When((Q(leave_type_changed_period__isnull=True)&Q(request_type='FD')),then=F('leave_type')),
                                output_field=CharField()
                            ),
                            leave_type_final_hd = Case(
                                When((Q(leave_type_changed_period__isnull=False)&Q(leave_type_changed_period='HD')),then=F('leave_type_changed')),
                                When((Q(leave_type_changed_period__isnull=True)&Q(request_type='HD')),then=F('leave_type')),
                                output_field=CharField()
                            ),
                            ).values('leave_type_final','leave_type_final_hd','attendance_date').distinct()
            # print("availed_master_wo_reject_fd",availed_master_wo_reject_fd)
            if availed_master_wo_reject_fd:

                for data in yearly_date_list:
                    availed_FD=availed_master_wo_reject_fd.filter(attendance_date=data)
                    
                    if availed_FD.filter(leave_type_final__isnull=False):
                        if availed_FD.values('leave_type_final').count() >1:
                            if availed_FD.filter(leave_type_final='AB'):
                                availed_ab=availed_ab+1.0

                            elif availed_FD.filter(leave_type_final='CL'):
                                availed_cl=availed_cl+1.0
                                        
                        else:
                            l_type=availed_FD[0]['leave_type_final']
                            if l_type == 'CL':
                                availed_cl=availed_cl+1.0
                            elif l_type == 'EL':
                                availed_el=availed_el+1.0
                            elif l_type == 'SL':
                                availed_sl=availed_sl+1.0
                            elif l_type == 'AB':
                                availed_ab=availed_ab+1.0

                    elif availed_FD.filter(leave_type_final_hd__isnull=False):
                        if availed_FD.values('leave_type_final_hd').count() >1:
                            if availed_FD.filter(leave_type_final_hd='AB'):
                                availed_hd_ab=availed_hd_ab+1.0

                            elif availed_FD.filter(leave_type_final_hd='CL'):
                                availed_hd_cl=availed_hd_cl+1.0
                                        
                        else:
                            l_type=availed_FD[0]['leave_type_final_hd']
                            if l_type == 'CL':
                                availed_hd_cl=availed_hd_cl+1.0
                            elif l_type == 'EL':
                                availed_hd_el=availed_hd_el+1.0
                            elif l_type == 'SL':
                                availed_hd_sl=availed_hd_sl+1.0
                            elif l_type == 'AB':
                                availed_hd_ab=availed_hd_ab+1.0

            yearly_availed_cl = float(availed_cl)+float(availed_hd_cl/2)
            yearly_availed_el = float(availed_el)+float(availed_hd_el/2)
            yearly_availed_sl = float(availed_sl)+float(availed_hd_sl/2)
            # yearly_availed_ab = float(availed_ab)+float(availed_hd_ab/2)

            granted_cl_1 = granted_cl if granted_cl else '0.00'
            yearly_availed_cl_1 = yearly_availed_cl if yearly_availed_cl else '0.00'
            granted_el_1 = granted_el if granted_el else '0.00'
            yearly_availed_el_1 = yearly_availed_el if yearly_availed_el else '0.00'
            granted_sl_1 = granted_sl if granted_sl else '0.00'
            yearly_availed_sl_1 = yearly_availed_sl if yearly_availed_sl else '0.00'

            yearly_balanced_cl = float(granted_cl_1) - float(yearly_availed_cl_1)
            yearly_balanced_el = float(granted_el_1) - float(yearly_availed_el_1)
            yearly_balanced_sl = float(granted_sl_1) - float(yearly_availed_sl_1)
            
            data_list = [user_name,"'"+punch_id,"'"+sap_personnel_no,"'"+emp_code,granted_cl,yearly_availed_cl,yearly_balanced_cl,granted_el,yearly_availed_el,yearly_balanced_el,granted_sl,yearly_availed_sl,yearly_balanced_sl]
            # header = ['PERSONNEL NUMBER(SAP ID)',' SUBTYPE',' BEGIN DATE',' ENDDATE']
            total_list.append(data_list)


        # print('total_list--->',total_list)
        if os.path.isdir('media/attendance/leave_report/document'):
            file_name = 'media/attendance/leave_report/document/leave_report.csv'
        else:
            os.makedirs('media/attendance/leave_report/document')
            file_name = 'media/attendance/leave_report/document/leave_report.csv'
        
        #########################################################
        df = DataFrame(total_list, columns= [' Employee Name ',' Punch Id ',' SAP No ',' Emp Code ',' Granted CL',' Availed CL ',' Balanced CL ',' Granted EL',' Availed EL',' Balanced EL ',' Granted SL',' Availed SL','Balanced SL'])
        export_csv = df.to_csv (file_name, index = None, header=True)

        if request.is_secure():
            protocol = 'https://'
        else:
            protocol = 'http://'

        url = getHostWithPort(request) + file_name if file_name else None
        print('url',url)

        return Response(url)

class AttendanceFileUploadCheck(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = Attendance.objects.filter(is_deleted=False)
    serializer_class = AttendanceFileUploadCheckSerializer
    #parser_classes = (MultiPartParser,)
    
    def att_create(self, filter: dict):
        logdin_user_id = self.request.user.id
        attendance,create1 = Attendance.objects.get_or_create(created_by_id=logdin_user_id,owned_by_id=logdin_user_id,**filter)
        return attendance
    def request_create(self, filter: dict):
        logdin_user_id = self.request.user.id  #attendance_date
        request,create2 = AttendanceApprovalRequest.objects.get_or_create(created_by_id=logdin_user_id,owned_by_id=logdin_user_id,**filter)
        return request

    def post(self, request, *args, **kwargs):
        response = super().post(request,*args,**kwargs)
        # print("response",response.data['document'])
        print("Please wait...")
        print("processing...")
        date_input = request.data['date_input']
        
        from django.db import connection
        print('connection',connection)
        with connection.cursor() as cursor:
            print('cursor',cursor)
            #cursor.execute("SELECT eid AS Empid,event_date AS Date,event_time AS Time,terminal_id AS CID FROM attendence_table where eid='00001063' and event_date like '2019-05-%'")
            cursor.execute('SELECT eid AS Empid,event_date AS Date,event_time AS Time,terminal_id AS CID FROM attendence_table where event_date LIKE %s',[date_input])
            rows = cursor.fetchall()
        print("rows",rows)
        print("rows",len(rows))






        ### IF Demo_user or Super_user >> Avoid attendance ###
        avoid_att = TMasterModuleRoleUser.objects.filter((Q(mmr_type=1)|Q(mmr_type=6))&Q(mmr_is_deleted=False)).values_list('mmr_user')
        print("avoid_att",avoid_att)

        user_details = TCoreUserDetail.objects.filter(~Q(cu_user__in=avoid_att),~Q(cu_punch_id='PMSSITE000'),cu_is_deleted=False).values() ##avoid 'PMSSITE000' punch ids
        #print('user_details',user_details)
        user_count = len(user_details) if user_details else 0
        holiday_list = HolidaysList.objects.filter(status=True).values('holiday_date','holiday_name')
        device_details = DeviceMaster.objects.filter(is_exit=True,is_deleted=False).values('id')
        if device_details:
            device_no_list = [x['id'] for x in device_details]
        # print("device_no_list", device_no_list)
        
        
        
        
        

        day = request.data['date_input']
        # day = rows[0]
        # day = day[1]
        print('day',day)


        # print("dayyy", day)
        if day:
            today_datetime = datetime.strptime(str(day)+'T'+'12:00:00', "%Y-%m-%dT%H:%M:%S")
            print("today_datetime",today_datetime.date())
            date_time_day = today_datetime.date()
        else:
            return Response({'result':{'request_status':0,'msg':'Enter proper Excel'}})
        total_month_grace=AttendenceMonthMaster.objects.filter(month_start__date__lte=today_datetime.date(),
                                        month_end__date__gte=today_datetime.date(),is_deleted=False).values('grace_available',
                                                                                 'year_start_date', 'year_end_date', 'month', 
                                                                                 'month_start', 'month_end','grace_available'
                                                                                 )
        # print("total_month_grace",total_month_grace)

        special_day = AttendanceSpecialdayMaster.objects.filter(((Q(day_start_time__date=today_datetime.date())|Q(
            day_end_time__date=today_datetime.date())) & Q(is_deleted=False))).values('day_start_time__time','day_end_time__time','remarks')

        special_full_day = AttendanceSpecialdayMaster.objects.filter(full_day__date=today_datetime.date(),is_deleted=False).values('full_day__date','remarks')
        #print("special_full_day",special_full_day)
        #print("special_day",special_day)

        for user in user_details:
            print('user',user)
            user_count = user_count-1
            print("Wait...", user_count)
            att_filter = {}
            req_filter = {}
            pre_att_filter = {}
            pre_req_filter = {}
            late_con_filter = {}
            bench_filter = {}
            pre_att = None

            logout_time = None
            check_out = 0
            # adv_leave_type = None
            user_flag = 0
            #cu_punch_id = int(user['cu_punch_id']) if user['cu_punch_id'] else None
            cu_punch_id = user['cu_punch_id'] if user['cu_punch_id'] else None
            print('cu_punch_id',cu_punch_id)
            cu_user_id = int(user['cu_user_id'])

            ###If user has no login/logout/lunch time >> Then fix their time##
            user['daily_loginTime'] = today_datetime.replace(hour=10, minute=00).time() if user['daily_loginTime'] is None else user['daily_loginTime']
            user['daily_logoutTime'] = today_datetime.replace(hour=19, minute=00).time() if user['daily_logoutTime'] is None else user['daily_logoutTime']
            user['lunch_start'] = today_datetime.replace(hour=13, minute=30).time() if user['lunch_start'] is None else user['lunch_start']
            user['lunch_end'] = today_datetime.replace(hour=14, minute=00).time() if user['lunch_end'] is None else user['lunch_end']
            
            ## If Change Login-Logout time (Special Day) ##
            if special_day:
                daily_loginTime = special_day[0]['day_start_time__time'] if special_day[0]['day_start_time__time'] is not None else user['daily_loginTime']
                daily_logoutTime = special_day[0]['day_end_time__time'] if special_day[0]['day_end_time__time'] is not None else user['daily_logoutTime']
                pre_att_filter['day_remarks'] = special_day[0]['remarks'] if special_day[0]['remarks'] is not None else ''
            elif today_datetime.weekday()==5:
                daily_loginTime = user['daily_loginTime']
                daily_logoutTime = user['daily_logoutTime'].replace(hour=16, minute=00)
                pre_att_filter['day_remarks'] = 'Present'
            else:
                daily_loginTime = user['daily_loginTime']
                daily_logoutTime = user['daily_logoutTime']
                pre_att_filter['day_remarks'] = 'Present'
            
            ## LUNCH TIME ##
            lunch_start = datetime.combine(today_datetime,user['lunch_start'])
            lunch_end = datetime.combine(today_datetime,user['lunch_end'])

            ## DAILY LOGIN-LOGOUT ##
            # print("daily_loginTime", daily_loginTime, type(daily_loginTime))
            daily_login = datetime.combine(today_datetime,daily_loginTime)
            daily_logout = datetime.combine(today_datetime,daily_logoutTime)

            is_saturday_off = user['is_saturday_off'] 
            att_filter['employee_id']=cu_user_id
            grace_over = False

            joining_date = user['joining_date']
            if total_month_grace:
                grace_available = total_month_grace[0]['grace_available'] if total_month_grace[0]['grace_available'] is not None else 0
                # print("GRACE", grace_available)
                if joining_date >= total_month_grace[0]['month_start'] and joining_date <= total_month_grace[0]['month_end']:
                    total_grace = JoiningApprovedLeave.objects.filter(employee=cu_user_id,is_deleted=False).values('first_grace')
                    grace_available = total_grace[0]['first_grace'] if total_grace[0]['first_grace'] is not None else 0
                    # print("grace_available AAAA", grace_available, cu_user_id)

            availed_grace=AttendanceApprovalRequest.objects.filter(Q(attendance__employee=cu_user_id) &
                                                            Q(duration_start__gte=total_month_grace[0]['month_start']) &
                                                            Q(duration_start__lte=total_month_grace[0]['month_end']) &
                                                            Q(is_requested=True) &
                                                            Q(is_deleted=False)&
                                                            (Q(request_type='GR')|Q(checkin_benchmark=True))
                                                            ).aggregate(Sum('duration'))['duration__sum']
            # print('availed_grace',availed_grace)
            availed_grace = availed_grace if availed_grace else 0
            
            # if grace_available<availed_grace: #nur code 
            #     grace_over = True
            rows = list(rows)
            for index, row in enumerate(rows):
                #print('index',index)
                #print('row under',row)
                # lunch_start = datetime.combine(today_datetime,user['lunch_start'])


                #print('row[index][1]',row[1])
                #print('row[index][2]',row[2])
                date_time = str(row[1])+'T'+str(row[2])
                print('date_time',date_time)
                date_time_format = datetime.strptime(date_time, "%Y-%m-%dT%H:%M:%S")
                print('row[0]',row[0])
                if cu_punch_id == row[0]:
                    user_flag = 1
                    ##################### Added By Rupam #######################
                    deviceMasterDetails = DeviceMaster.objects.filter(device_no=int(row[3]))
                    if deviceMasterDetails:
                        current_device = DeviceMaster.objects.get(device_no=int(row[3]))
                        # print("current_device",current_device)
                    ##################### END ###################################
                    pre_att_filter['employee_id'] = cu_user_id
                    # pre_att_filter['day_remarks'] = 'Present'
                    pre_att_filter['is_present'] = True
                    pre_att_filter['date'] = date_time_format
                    pre_att_filter['login_time'] = date_time_format
                    print("pre_att_filter",pre_att_filter)


                    ##First time log in a Day##Successful
                    if pre_att is None:                      
                        if pre_att_filter:
                            print('pre_att')
                            pre_att = self.att_create(pre_att_filter)
                            bench_time = daily_login + timedelta(minutes=30)
                            # print('bench_time',bench_time)

                            ###Check login if After USER Daily login time = Duration### Successful
                            if daily_login<pre_att_filter['login_time']:
                                    bench_filter['attendance']=pre_att
                                    bench_filter['attendance_date'] = daily_login.date()
                                    bench_filter['duration_start']=daily_login
                                    bench_filter['duration_end']=pre_att_filter['login_time']
                                    bench_filter['duration'] = round(((bench_filter['duration_end']-bench_filter['duration_start']).seconds)/60)
                                    if grace_available<availed_grace + float(bench_filter['duration']): #abhisek code 
                                        grace_over = True
                                    if bench_time>pre_att_filter['login_time'] and grace_over is False:
                                        bench_filter['checkin_benchmark']=True
                                        bench_filter['is_requested']=True
                                        # bench_filter['is_requested']=True
                                        # bench_filter['request_type']='GR'
                                    else:
                                        bench_filter['checkin_benchmark']=False

                                    if bench_filter['duration']>0:
                                        bench_req = self.request_create(bench_filter)

                    ##After Daily Attendance## Successful
                    if pre_att:
                        print('logggggg')
                        att_log_create, create1 = AttendanceLog.objects.get_or_create(
                            attendance=pre_att,
                            employee_id=cu_user_id,
                            time=date_time_format,
                            device_no=current_device
                        )

                        logout_time = date_time_format
                        duration_count = 0
                        if check_out == 0 and current_device.__dict__['id'] in device_no_list and date_time_format<daily_logout:
                            # print("if current_device in device_no_list:")
                            check_out = 1
                            pre_req_filter['attendance'] = pre_att
                            pre_req_filter['duration_start'] = date_time_format
                        elif check_out == 1 and current_device not in device_no_list and date_time_format<daily_login:
                            check_out = 0
                            pre_req_filter = {}
                        elif check_out == 1 and current_device not in device_no_list and date_time_format>daily_login:
                            check_out = 0
                            if date_time_format>daily_logout:
                                pre_req_filter['duration_end'] = daily_logout
                            else:
                                pre_req_filter['duration_end'] = date_time_format

                            if pre_req_filter['duration_start']<daily_login:
                                pre_req_filter['duration_start'] = daily_login
                            # else:
                            #     pre_req_filter['duration_end'] = date_time_format

                            if bench_time>pre_req_filter['duration_end'] and grace_over is False:
                                pre_req_filter['checkin_benchmark']=True
                                pre_req_filter['is_requested']=True


                            if lunch_end < pre_req_filter['duration_start']:
                                duration_count = round(((pre_req_filter['duration_end']-pre_req_filter['duration_start']).seconds)/60)
                            elif lunch_start > pre_req_filter['duration_end']:
                                duration_count = round(((pre_req_filter['duration_end']-pre_req_filter['duration_start']).seconds)/60)
                            elif lunch_start > pre_req_filter['duration_start'] and lunch_end < pre_req_filter['duration_end']:
                                duration_count = round(((lunch_start - pre_req_filter['duration_start'] + pre_req_filter['duration_end'] - lunch_end).seconds)/60)
                            elif lunch_start > pre_req_filter['duration_start'] and lunch_end > pre_req_filter['duration_end']:
                                duration_count = round(((lunch_start - pre_req_filter['duration_start']).seconds)/60)
                            elif lunch_end < pre_req_filter['duration_end'] and lunch_start < pre_req_filter['duration_start']:
                                duration_count = round(duration_count + ((pre_req_filter['duration_end']-lunch_end).seconds)/60)

                            # print("duration_count",duration_count, pre_req_filter)
                            if duration_count>0:
                                pre_req_filter['duration']=duration_count
                                pre_req_filter['attendance_date'] = pre_req_filter['duration_start'].date()
                                pre_req = self.request_create(pre_req_filter)
                                #print("pre_req",pre_req)


            if logout_time and pre_att:
                # print('pre_att',pre_att.id)
                pre_att_update = Attendance.objects.filter(pk=pre_att.id).update(logout_time=logout_time)
                ### IF Late convence ### Successful Testing
                if daily_logoutTime < logout_time.time():
                    late_con_filter['attendance']=pre_att
                    late_con_filter['attendance_date']=daily_logout.date()
                    late_con_filter['duration_start']=daily_logout
                    late_con_filter['duration_end']=logout_time
                    late_con_filter['duration'] = round(((late_con_filter['duration_end']-late_con_filter['duration_start']).seconds)/60)
                    late_con_filter['is_late_conveyance']=True
                    if late_con_filter['duration']>10: #If late conveyance grater then 10 Minutes. 
                        # print("late_con_filter",late_con_filter)
                        late_req = self.request_create(late_con_filter)
                        # print("late_req",late_req)
                
                ###If Logout less then User's Daily log out### Successful Testing
                elif daily_logoutTime > logout_time.time():
                    late_con_filter['attendance']=pre_att
                    late_con_filter['attendance_date']=daily_logout.date()
                    late_con_filter['duration_start']=logout_time
                    late_con_filter['duration_end']=daily_logout
                    late_con_filter['duration'] = round(((late_con_filter['duration_end']-late_con_filter['duration_start']).seconds)/60)
                    late_con_filter['is_late_conveyance']=False
                    # late_con_filter['request_type']='GR'
                    if late_con_filter['duration']>0:
                        # print("late_con_filter",late_con_filter)
                        late_req = self.request_create(late_con_filter)
                        # print("late_req",late_req)

        ## IF User Absent ###
            if user_flag==0:
                # print("ABSENT")
                is_required = False
                # print("user",cu_user_id)
                adv_leave_type = None
                leave = EmployeeAdvanceLeaves.objects.filter(
                    Q(start_date__date__lte=date_time_day)&Q(end_date__date__gte=date_time_day)&Q(employee_id=cu_user_id)&  #changes by abhisek 21/11/19
                    (Q(approved_status='pending')|Q(approved_status='approved'))).values('leave_type','reason')
                # print("leave",leave)
                '''
                Modified By :: Rajesh Samui
                Reason :: State Wise Holiday Calculation
                Line :: 6553-6567
                Date :: 10-02-2020
                '''
                # holiday = HolidaysList.objects.filter(status=True,holiday_date=date_time_day).values('holiday_name')
                state_obj = TCoreUserDetail.objects.get(cu_user__id=cu_user_id).job_location_state
                default_state = TCoreState.objects.filter(cs_state_name__iexact='west bengal').first()
                t_core_state_id = state_obj.id if state_obj else default_state.id
                holiday = HolidayStateMapping.objects.filter(Q(holiday__holiday_date=date_time_day)&Q(state__id=t_core_state_id)).values('holiday__holiday_name')



                if leave:
                    adv_leave_type = leave[0]['leave_type']
                    # print("leave_type",leave[0]['leave_type'])
                    att_filter['day_remarks']=leave[0]['leave_type']
                    is_required = True
                elif holiday:
                    holiday_name = holiday[0]["holiday__holiday_name"]
                    att_filter['day_remarks']=holiday[0]["holiday__holiday_name"]
                elif special_full_day:
                    # special_full_day_name = special_full_day[0]["full_day__date"]
                    att_filter['day_remarks']=special_full_day[0]["remarks"]
                elif date_time_day.weekday()==6:
                    # print("Sunday")
                    att_filter['day_remarks']="Sunday"
                elif date_time_day.weekday()==5:
                    saturday_off_list = AttendenceSaturdayOffMaster.objects.filter(employee_id=cu_user_id,is_deleted=False).values(
                       'first', 'second', 'third', 'fourth', 'all_s_day').order_by('-id')

                    if saturday_off_list:
                        if saturday_off_list[0]['all_s_day'] is True:
                            # if user['is_saturday_off'] is True:
                            att_filter['day_remarks']='Saturday'

                        else:
                            week_date = date_time_day.day
                            # print("week_date",  week_date)
                            month_calender = calendar.monthcalendar(date_time_day.year, date_time_day.month)
                            saturday_list = (0,1,2,3) if month_calender[0][calendar.SATURDAY] else (1,2,3,4)

                            if saturday_off_list[0]['first'] is True and int(week_date)==int(month_calender[saturday_list[0]][calendar.SATURDAY]):
                                att_filter['day_remarks']='Saturday'
                            elif saturday_off_list[0]['second'] is True and int(week_date)==int(month_calender[saturday_list[1]][calendar.SATURDAY]):
                                att_filter['day_remarks']='Saturday'
                            elif saturday_off_list[0]['third'] is True and int(week_date)==int(month_calender[saturday_list[2]][calendar.SATURDAY]):
                                att_filter['day_remarks']='Saturday'
                            elif saturday_off_list[0]['fourth'] is True and int(week_date)==int(month_calender[saturday_list[3]][calendar.SATURDAY]):
                                att_filter['day_remarks']='Saturday'
                            else:
                                #print("Not Present")
                                is_required = True
                                att_filter['day_remarks']="Not Present"
                                    
                    else:
                        is_required = True
                        att_filter['day_remarks']="Not Present"
                    # print("Saturday")

                else:
                    is_required = True
                    att_filter['day_remarks']="Not Present"
                if att_filter:
                    date = date_time[0:10]+'T'+str(daily_loginTime)
                    date_time_date =datetime.strptime(date, "%Y-%m-%dT%H:%M:%S")
                    #print("date_time_format",date_time_date)
                    att_filter['date']=date_time_date
                    #print("att_filter",att_filter)

                    abs_att = self.att_create(att_filter)
                    #print("att_filter",abs_att)
                    if is_required is True:
                        req_filter['attendance']= abs_att
                        req_filter['attendance_date'] = daily_login.date()
                        req_filter['duration_start'] = daily_login
                        req_filter['duration_end'] = daily_logout
                        req_filter['duration'] = round(((req_filter['duration_end']-req_filter['duration_start']).seconds)/60)

                        if adv_leave_type:
                            req_filter['request_type']='FD'
                            req_filter['leave_type'] = adv_leave_type
                            req_filter['approved_status'] = 'approved'
                            req_filter['is_requested'] = True
                            req_filter['justification'] = leave[0]['reason']

                        if req_filter:
                            abs_req = self.request_create(req_filter)
                            # print("abs_req",abs_req, req_filter)


        return Response({'result':{'request_status':1,'msg':'Successful'}})


class AttendanceFileUploadCheckPunchOldData(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = Attendance.objects.filter(is_deleted=False)
    # serializer_class = AttendanceFileUploadCheckSerializer
    #parser_classes = (MultiPartParser,)
    
    def att_create(self, filter: dict):
        logdin_user_id = self.request.user.id
        attendance,create1 = Attendance.objects.get_or_create(created_by_id=logdin_user_id,owned_by_id=logdin_user_id,**filter)
        return attendance
    def request_create(self, filter: dict):
        logdin_user_id = self.request.user.id  #attendance_date
        request,create2 = AttendanceApprovalRequest.objects.get_or_create(created_by_id=logdin_user_id,owned_by_id=logdin_user_id,**filter)
        return request

    def post(self, request, *args, **kwargs):
        # response = super().post(request,*args,**kwargs)
        # print("response",response.data['document'])
        print("Please wait...")
        print("processing...")
        # date_input = request.data['date_input']
        day_start = request.data['day_start']
        day_end = request.data['day_end']
        punch_ids = request.data['punch_ids']
        date_list = []
        punch_list = []
        if day_start and day_end and punch_ids:
            punch_list = punch_ids.split(',')
            day_start = datetime.strptime(day_start, "%Y-%m-%d").date()
            day_end = datetime.strptime(day_end, "%Y-%m-%d").date()
            print("day_start", day_start, day_end)

            
            while day_end>=day_start:
                date_list.append(day_start)
                day_start+=timedelta(days=1)

            # print("date_list",date_list)
        
        if punch_list and date_list:
            device_details = DeviceMaster.objects.filter(is_exit=True,is_deleted=False).values('id')
            if device_details:
                device_no_list = [x['id'] for x in device_details]
            print("device_no_list", device_no_list)

            from django.db import connection
            print('connection',connection)
            with connection.cursor() as cursor:
                print('cursor',cursor)

                for punch_id in punch_list:
                    for date_input in date_list:    
                        print('date_input--punch_id', date_input, punch_id)    
                        cursor.execute('SELECT eid AS Empid,event_date AS Date,event_time AS Time,terminal_id AS CID FROM attendence_table where event_date LIKE %s AND eid = %s',[date_input,punch_id])
                        rows = cursor.fetchall()
                        # print("rows",rows)
                        # print("rows",len(rows))
                        # return Response({'result':{'request_status':0,'msg':'Enter proper Excel'}})


                        ### IF Demo_user or Super_user >> Avoid attendance ###
                        # avoid_att = TMasterModuleRoleUser.objects.filter((Q(mmr_type=1)|Q(mmr_type=6))&Q(mmr_is_deleted=False)).values_list('mmr_user')
                        # print("avoid_att",avoid_att)

                        user_details = TCoreUserDetail.objects.filter(cu_punch_id=punch_id).values()
                        #print('user_details',user_details)
                        user_count = len(user_details) if user_details else 0
                        holiday_list = HolidaysList.objects.filter(status=True).values('holiday_date','holiday_name')            
                        
                        
                        day = date_input
                        # day = rows[0]
                        # day = day[1]
                        print('day',day)


                        # print("dayyy", day)
                        if day:
                            today_datetime = datetime.strptime(str(day)+'T'+'12:00:00', "%Y-%m-%dT%H:%M:%S")
                            print("today_datetime",today_datetime)
                            date_time_day = today_datetime.date()
                            late_convence_limit = today_datetime.replace(hour=20, minute=30)
                            # print("late_convence_limit",late_convence_limit)
                            # return Response({'result':{'request_status':0,'msg':'Enter proper Excel'}})
                        else:
                            return Response({'result':{'request_status':0,'msg':'Enter proper Excel'}})
                        total_month_grace=AttendenceMonthMaster.objects.filter(month_start__date__lte=today_datetime.date(),
                                        month_end__date__gte=today_datetime.date(),is_deleted=False).values('grace_available',
                                                                                 'year_start_date', 'year_end_date', 'month', 
                                                                                 'month_start', 'month_end','grace_available'
                                                                                 )
                        # print("total_month_grace",total_month_grace)

                        special_day = AttendanceSpecialdayMaster.objects.filter(((Q(day_start_time__date=today_datetime.date())|Q(
                            day_end_time__date=today_datetime.date())) & Q(is_deleted=False))).values('day_start_time__time','day_end_time__time','remarks')

                        special_full_day = AttendanceSpecialdayMaster.objects.filter(full_day__date=today_datetime.date(),is_deleted=False).values('full_day__date','remarks')
                        # holiday = HolidaysList.objects.filter(status=True,holiday_date=date_time_day).values('holiday_name')

                        # print('holiday',holiday)
                        # print("special_full_day",special_full_day)
                        # print("special_day",special_day)
                        # ##########
                        # no_request = False
                        # day_remarks = ''
                        # if holiday:
                        #     # holiday_name = holiday[0]["holiday_name"]
                        #     day_remarks = holiday[0]["holiday_name"]
                        #     no_request = True
                        # elif special_full_day:
                        #     # special_full_day_name = special_full_day[0]["full_day__date"]
                        #     day_remarks = special_full_day[0]["remarks"]
                        #     no_request = True
                        # elif date_time_day.weekday()==6:
                        #     # print("Sunday")
                        #     day_remarks = "Sunday"
                        #     no_request = True

                        for user in user_details:
                            user_count = user_count-1
                            print("Wait...", user_count)
                            att_filter = {}
                            req_filter = {}
                            pre_att_filter = {}
                            pre_req_filter = {}
                            late_con_filter = {}
                            bench_filter = {}
                            saturday_off_list = None
                            pre_att = None
                            saturday_off = False

                            logout_time = None
                            check_out = 0
                            # adv_leave_type = None
                            user_flag = 0
                            cu_punch_id = user['cu_punch_id'] if user['cu_punch_id'] else None
                            cu_user_id = int(user['cu_user_id'])

                            #################
                            '''
                            Modified By :: Rajesh Samui
                            Reason :: State Wise Holiday Calculation
                            Description :: Commented out line 6739-6758
                            Line :: 6788-6807
                            Date :: 10-02-2020
                            '''
                            # holiday = HolidaysList.objects.filter(status=True,holiday_date=date_time_day).values('holiday_name')
                            state_obj = TCoreUserDetail.objects.get(cu_user__id=cu_user_id).job_location_state
                            default_state = TCoreState.objects.filter(cs_state_name__iexact='west bengal').first()
                            t_core_state_id = state_obj.id if state_obj else default_state.id
                            holiday = HolidayStateMapping.objects.filter(
                                Q(holiday__holiday_date=date_time_day)&Q(state__id=t_core_state_id)).values('holiday__holiday_name')

                            # print(state_obj)
                            # print(t_core_user_state_code)
                            # print(holiday)


                            print('holiday',holiday)
                            print("special_full_day",special_full_day)
                            print("special_day",special_day)
                            ##########
                            no_request = False
                            day_remarks = ''
                            if holiday:
                                # holiday_name = holiday[0]["holiday_name"]
                                day_remarks = holiday[0]["holiday__holiday_name"]
                                no_request = True
                            elif special_full_day:
                                # special_full_day_name = special_full_day[0]["full_day__date"]
                                day_remarks = special_full_day[0]["remarks"]
                                no_request = True
                            elif date_time_day.weekday()==6:
                                # print("Sunday")
                                day_remarks = "Sunday"
                                no_request = True

                            #################
                            if date_time_day.weekday()==5 and no_request is False:
                                saturday_off_list = AttendenceSaturdayOffMaster.objects.filter(employee_id=cu_user_id,is_deleted=False).values(
                                    'first', 'second', 'third', 'fourth', 'all_s_day').order_by('-id')

                                print("saturday_off_list",date_time_day.weekday(), saturday_off_list)

                                if saturday_off_list:
                                    if saturday_off_list[0]['all_s_day'] is True:
                                        # if user['is_saturday_off'] is True:
                                        day_remarks = 'Saturday'
                                        saturday_off = True

                                    else:
                                        week_date = date_time_day.day
                                        # print("week_date",  week_date)
                                        month_calender = calendar.monthcalendar(date_time_day.year, date_time_day.month)
                                        saturday_list = (0,1,2,3) if month_calender[0][calendar.SATURDAY] else (1,2,3,4)

                                        if saturday_off_list[0]['first'] is True and int(week_date)==int(month_calender[saturday_list[0]][calendar.SATURDAY]):
                                            day_remarks='Saturday'
                                            saturday_off = True
                                        elif saturday_off_list[0]['second'] is True and int(week_date)==int(month_calender[saturday_list[1]][calendar.SATURDAY]):
                                            day_remarks='Saturday'
                                            saturday_off = True
                                        elif saturday_off_list[0]['third'] is True and int(week_date)==int(month_calender[saturday_list[2]][calendar.SATURDAY]):
                                            day_remarks='Saturday'
                                            saturday_off = True
                                        elif saturday_off_list[0]['fourth'] is True and int(week_date)==int(month_calender[saturday_list[3]][calendar.SATURDAY]):
                                            day_remarks='Saturday'
                                            saturday_off = True

                                    # print("Saturday")

                            #################

                            ###If user has no login/logout/lunch time >> Then fix their time##
                            user['daily_loginTime'] = today_datetime.replace(hour=10, minute=00).time() if user['daily_loginTime'] is None else user['daily_loginTime']
                            user['daily_logoutTime'] = today_datetime.replace(hour=19, minute=00).time() if user['daily_logoutTime'] is None else user['daily_logoutTime']
                            user['lunch_start'] = today_datetime.replace(hour=13, minute=30).time() if user['lunch_start'] is None else user['lunch_start']
                            user['lunch_end'] = today_datetime.replace(hour=14, minute=00).time() if user['lunch_end'] is None else user['lunch_end']
                            
                            ## If Change Login-Logout time (Special Day) ##
                            if special_day:
                                daily_loginTime = special_day[0]['day_start_time__time'] if special_day[0]['day_start_time__time'] is not None else user['daily_loginTime']
                                # daily_logoutTime = special_day[0]['day_end_time__time'] if special_day[0]['day_end_time__time'] is not None else user['daily_logoutTime']
                                daily_logoutTime = special_day[0]['day_end_time__time'] if special_day[0]['day_end_time__time'] is not None and \
                                                                                            special_day[0]['day_end_time__time']<user['daily_logoutTime'] else user['daily_logoutTime']
                                print("daily_logoutTime",daily_logoutTime)
                                pre_att_filter['day_remarks'] = special_day[0]['remarks'] if special_day[0]['remarks'] is not None else ''
                            elif today_datetime.weekday()==5:
                                daily_loginTime = user['daily_loginTime']
                                daily_logoutTime = user['saturday_logout'] if user['saturday_logout'] is not None else user['daily_logoutTime'].replace(hour=16, minute=00)
                                pre_att_filter['day_remarks'] = 'Present'

                            else:
                                daily_loginTime = user['daily_loginTime']
                                daily_logoutTime = user['daily_logoutTime']
                                pre_att_filter['day_remarks'] = 'Present'
                            
                            ## LUNCH TIME ##
                            lunch_start = datetime.combine(today_datetime,user['lunch_start'])
                            lunch_end = datetime.combine(today_datetime,user['lunch_end'])

                            ## DAILY LOGIN-LOGOUT ##
                            # print("daily_loginTime", daily_loginTime, type(daily_loginTime))
                            daily_login = datetime.combine(today_datetime,daily_loginTime)
                            daily_logout = datetime.combine(today_datetime,daily_logoutTime)

                            is_saturday_off = user['is_saturday_off'] 
                            att_filter['employee_id'] = cu_user_id
                            grace_over = False

                            joining_date = user['joining_date']
                            if total_month_grace:
                                grace_available = total_month_grace[0]['grace_available'] if total_month_grace[0]['grace_available'] is not None else 0
                                print("GRACE", grace_available)
                                if joining_date >= total_month_grace[0]['month_start'] and joining_date <= total_month_grace[0]['month_end']:
                                    total_grace = JoiningApprovedLeave.objects.filter(employee=cu_user_id,is_deleted=False).values('first_grace')
                                    grace_available = total_grace[0]['first_grace'] if total_grace[0]['first_grace'] is not None else 0
                                    print("grace_available AAAA", grace_available, cu_user_id)

                            availed_grace=AttendanceApprovalRequest.objects.filter(Q(attendance__employee=cu_user_id) &
                                                                            Q(duration_start__gte=total_month_grace[0]['month_start']) &
                                                                            Q(duration_start__lte=total_month_grace[0]['month_end']) &
                                                                            Q(is_requested=True) &
                                                                            Q(is_deleted=False)&
                                                                            (Q(request_type='GR')|Q(checkin_benchmark=True))
                                                                            ).aggregate(Sum('duration'))['duration__sum']
                            print('availed_grace',availed_grace)
                            availed_grace = availed_grace if availed_grace else 0

                            print("date_input",user['daily_loginTime'],date_input )
                            rows = list(rows) if len(rows)>0 else [['0000000',str(date_input),str(user['daily_loginTime'])]]

                            # for index, row in enumerate(rows):
                            for row in rows:
                                print('row[index][1]',row[1])
                                print('row[index][2]',row[2])
                                date_time = str(row[1])+'T'+str(row[2])
                                print('date_time',date_time)
                                date_time_format = datetime.strptime(date_time, "%Y-%m-%dT%H:%M:%S")
                                print('row[0]',row[0])
                                if cu_punch_id == row[0]:
                                    user_flag = 1
                                    ##################### Added By Rupam #######################
                                    deviceMasterDetails = DeviceMaster.objects.filter(device_no=int(row[3]))
                                    if deviceMasterDetails:
                                        current_device = DeviceMaster.objects.get(device_no=int(row[3]))
                                        # print("current_device",current_device)
                                    ##################### END ###################################
                                    pre_att_filter['employee_id'] = cu_user_id
                                    # pre_att_filter['day_remarks'] = 'Present'
                                    pre_att_filter['is_present'] = True
                                    pre_att_filter['date'] = date_time_format
                                    pre_att_filter['login_time'] = date_time_format
                                    # print("pre_att_filter",pre_att_filter)

                                    ##First time log in a Day##Successful
                                    if pre_att is None:                      
                                        if pre_att_filter:
                                            pre_att = self.att_create(pre_att_filter)
                                            bench_time = daily_login + timedelta(minutes=30)
                                            # print('bench_time',bench_time)
                                            # if saturday_off is False and no_request is False:

                                            ###Check login if After USER Daily login time = Duration### Successful
                                            if daily_login<pre_att_filter['login_time'] and saturday_off is False and no_request is False:
                                                    bench_filter['attendance']=pre_att
                                                    bench_filter['attendance_date'] = daily_login.date()
                                                    bench_filter['duration_start']=daily_login
                                                    bench_filter['duration_end']=pre_att_filter['login_time']
                                                    bench_filter['duration'] = round(((bench_filter['duration_end']-bench_filter['duration_start']).seconds)/60)
                                                    bench_filter['punch_id'] = cu_punch_id
                                                    if grace_available<availed_grace + float(bench_filter['duration']): #abhisek code 
                                                        grace_over = True
                                                    if bench_time>pre_att_filter['login_time'] and grace_over is False:
                                                        bench_filter['checkin_benchmark']=True
                                                        bench_filter['is_requested']=True
                                                        # bench_filter['is_requested']=True
                                                        # bench_filter['request_type']='GR'
                                                    else:
                                                        bench_filter['checkin_benchmark']=False

                                                    if bench_filter['duration']>0:
                                                        bench_req = self.request_create(bench_filter)

                                    ##After Daily Attendance## Successful
                                    if pre_att:
                                        att_log_create, create1 = AttendanceLog.objects.get_or_create(
                                            attendance=pre_att,
                                            employee_id=cu_user_id,
                                            time=date_time_format,
                                            device_no=current_device
                                        )

                                        logout_time = date_time_format
                                        duration_count = 0
                                        if saturday_off is False and no_request is False:
                                            if check_out == 0 and current_device.__dict__['id'] in device_no_list and date_time_format<daily_logout:
                                                # print("if current_device in device_no_list:")
                                                check_out = 1
                                                pre_req_filter['attendance'] = pre_att
                                                pre_req_filter['punch_id'] = cu_punch_id
                                                pre_req_filter['duration_start'] = date_time_format
                                            elif check_out == 1 and current_device not in device_no_list and date_time_format<daily_login:
                                                check_out = 0
                                                pre_req_filter = {}
                                            elif check_out == 1 and current_device not in device_no_list and date_time_format>daily_login:
                                                check_out = 0
                                                if date_time_format>daily_logout:
                                                    pre_req_filter['duration_end'] = daily_logout
                                                else:
                                                    pre_req_filter['duration_end'] = date_time_format

                                                if pre_req_filter['duration_start']<daily_login:
                                                    pre_req_filter['duration_start'] = daily_login
                                                # else:
                                                #     pre_req_filter['duration_end'] = date_time_format

                                                # if bench_time>pre_req_filter['duration_end'] and grace_over is False:
                                                #     pre_req_filter['checkin_benchmark']=True
                                                #     pre_req_filter['is_requested']=True


                                                if lunch_end < pre_req_filter['duration_start']:
                                                    duration_count = round(((pre_req_filter['duration_end']-pre_req_filter['duration_start']).seconds)/60)
                                                elif lunch_start > pre_req_filter['duration_end']:
                                                    duration_count = round(((pre_req_filter['duration_end']-pre_req_filter['duration_start']).seconds)/60)
                                                elif lunch_start > pre_req_filter['duration_start'] and lunch_end < pre_req_filter['duration_end']:
                                                    duration_count = round(((lunch_start - pre_req_filter['duration_start'] + pre_req_filter['duration_end'] - lunch_end).seconds)/60)
                                                elif lunch_start > pre_req_filter['duration_start'] and lunch_end > pre_req_filter['duration_end']:
                                                    duration_count = round(((lunch_start - pre_req_filter['duration_start']).seconds)/60)
                                                elif lunch_end < pre_req_filter['duration_end'] and lunch_start < pre_req_filter['duration_start']:
                                                    duration_count = round(duration_count + ((pre_req_filter['duration_end']-lunch_end).seconds)/60)

                                                # print("duration_count",duration_count, pre_req_filter)
                                                if duration_count>0:
                                                    pre_req_filter['duration']=duration_count
                                                    pre_req_filter['attendance_date'] = pre_req_filter['duration_start'].date()
                                                    pre_req = self.request_create(pre_req_filter)
                                                    pre_req_filter = {}
                                                    #print("pre_req",pre_req)


                            if logout_time and pre_att:
                                # print('pre_att',pre_att.id)
                                pre_att_update = Attendance.objects.filter(pk=pre_att.id).update(logout_time=logout_time)
                                if saturday_off is False and no_request is False:
                                    ### IF Late convence ### Successful Testing
                                    if daily_logoutTime < logout_time.time():
                                        late_con_filter['attendance'] = pre_att
                                        late_con_filter['punch_id'] = cu_punch_id
                                        late_con_filter['attendance_date']=daily_logout.date()
                                        late_con_filter['duration_start']=daily_logout
                                        late_con_filter['duration_end']=logout_time
                                        late_con_filter['duration'] = round(((late_con_filter['duration_end']-late_con_filter['duration_start']).seconds)/60)
                                        late_con_filter['is_late_conveyance']=True
                                        # if late_con_filter['duration']>10: #If late conveyance grater then 10 Minutes.
                                        '''
                                            As per requirement and discussion with Tonmay Da(10.12.2019):
                                            LATE CONVENCE always count after 08:30 PM 
                                        '''
                                        if late_convence_limit>=late_con_filter['duration_start'] and late_convence_limit<late_con_filter['duration_end']\
                                            and late_con_filter['duration']>0:
                                            # print("late_con_filter",late_con_filter)
                                            late_req = self.request_create(late_con_filter)
                                            # print("late_req",late_req)
                                    
                                    ###If Logout less then User's Daily log out### Successful Testing
                                    elif daily_logoutTime > logout_time.time():
                                        late_con_filter['attendance']=pre_att
                                        late_con_filter['punch_id'] = cu_punch_id
                                        late_con_filter['attendance_date']=daily_logout.date()
                                        late_con_filter['duration_start']=logout_time
                                        late_con_filter['duration_end']=daily_logout
                                        late_con_filter['duration'] = round(((late_con_filter['duration_end']-late_con_filter['duration_start']).seconds)/60)
                                        late_con_filter['is_late_conveyance']=False
                                        # late_con_filter['request_type']='GR'
                                        if late_con_filter['duration']>0:
                                            # print("late_con_filter",late_con_filter)
                                            late_req = self.request_create(late_con_filter)
                                            # print("late_req",late_req)

                        ## IF User Absent ###
                            if user_flag==0:
                                # print("ABSENT")
                                is_required = False
                                # print("user",cu_user_id)
                                adv_leave_type = None
                                leave = EmployeeAdvanceLeaves.objects.filter(
                                    Q(start_date__date__lte=date_time_day)&Q(end_date__date__gte=date_time_day)&Q(employee_id=cu_user_id)&  #changes by abhisek 21/11/19
                                    (Q(approved_status='pending')|Q(approved_status='approved'))).values('leave_type','reason')
                                # print("leave",leave)
                                # holiday = HolidaysList.objects.filter(status=True,holiday_date=date_time_day).values('holiday_name')

                                if leave:
                                    adv_leave_type = leave[0]['leave_type']
                                    # print("leave_type",leave[0]['leave_type'])
                                    att_filter['day_remarks']=leave[0]['leave_type']
                                    is_required = True
                                elif saturday_off is True or no_request is True:
                                    att_filter['day_remarks'] = day_remarks
                                    print("att_filter",att_filter, saturday_off, no_request)
                                else:
                                    is_required = True
                                    att_filter['day_remarks']="Not Present"

                                if att_filter:
                                    date = date_time[0:10]+'T'+str(daily_loginTime)
                                    date_time_date =datetime.strptime(date, "%d/%m/%YT%H:%M:%S")
                                    #print("date_time_format",date_time_date)
                                    att_filter['date'] = date_time_date
                                    #print("att_filter",att_filter)

                                    abs_att = self.att_create(att_filter)
                                    print("att_filter",abs_att, is_required)
                                    if is_required is True:
                                        req_filter['attendance']= abs_att
                                        req_filter['attendance_date'] = daily_login.date()
                                        req_filter['duration_start'] = daily_login
                                        req_filter['duration_end'] = daily_logout
                                        req_filter['duration'] = round(((req_filter['duration_end']-req_filter['duration_start']).seconds)/60)

                                        if adv_leave_type:
                                            req_filter['request_type']='FD'
                                            req_filter['leave_type'] = adv_leave_type
                                            req_filter['approved_status'] = 'approved'
                                            req_filter['is_requested'] = True
                                            req_filter['justification'] = leave[0]['reason']

                                        if req_filter:
                                            print("req_filter,",req_filter)
                                            req_filter['punch_id'] = cu_punch_id
                                            abs_req = self.request_create(req_filter)
                                            # abs_check = self.absent_checking(req_filter)
                                            # print("abs_req",abs_req, req_filter)



                            #         ##First time log in a Day##Successful
                            #         if pre_att is None:                      
                            #             if pre_att_filter:
                            #                 print('pre_att')
                            #                 pre_att = self.att_create(pre_att_filter)
                            #                 bench_time = daily_login + timedelta(minutes=30)
                            #                 # print('bench_time',bench_time)

                            #                 ###Check login if After USER Daily login time = Duration### Successful
                            #                 if daily_login<pre_att_filter['login_time']:
                            #                         bench_filter['attendance']=pre_att
                            #                         bench_filter['attendance_date'] = daily_login.date()
                            #                         bench_filter['duration_start']=daily_login
                            #                         bench_filter['duration_end']=pre_att_filter['login_time']
                            #                         bench_filter['duration'] = round(((bench_filter['duration_end']-bench_filter['duration_start']).seconds)/60)
                            #                         if grace_available<availed_grace + float(bench_filter['duration']): #abhisek code 
                            #                             grace_over = True
                            #                         if bench_time>pre_att_filter['login_time'] and grace_over is False:
                            #                             bench_filter['checkin_benchmark']=True
                            #                             bench_filter['is_requested']=True
                            #                             # bench_filter['is_requested']=True
                            #                             # bench_filter['request_type']='GR'
                            #                         else:
                            #                             bench_filter['checkin_benchmark']=False

                            #                         if bench_filter['duration']>0:
                            #                             bench_req = self.request_create(bench_filter)

                            #         ##After Daily Attendance## Successful
                            #         if pre_att:
                            #             print('logggggg')
                            #             att_log_create, create1 = AttendanceLog.objects.get_or_create(
                            #                 attendance=pre_att,
                            #                 employee_id=cu_user_id,
                            #                 time=date_time_format,
                            #                 device_no=current_device
                            #             )

                            #             logout_time = date_time_format
                            #             duration_count = 0
                            #             if check_out == 0 and current_device.__dict__['id'] in device_no_list and date_time_format<daily_logout:
                            #                 # print("if current_device in device_no_list:")
                            #                 check_out = 1
                            #                 pre_req_filter['attendance'] = pre_att
                            #                 pre_req_filter['duration_start'] = date_time_format
                            #             elif check_out == 1 and current_device not in device_no_list and date_time_format<daily_login:
                            #                 check_out = 0
                            #                 pre_req_filter = {}
                            #             elif check_out == 1 and current_device not in device_no_list and date_time_format>daily_login:
                            #                 check_out = 0
                            #                 if date_time_format>daily_logout:
                            #                     pre_req_filter['duration_end'] = daily_logout
                            #                 else:
                            #                     pre_req_filter['duration_end'] = date_time_format

                            #                 if pre_req_filter['duration_start']<daily_login:
                            #                     pre_req_filter['duration_start'] = daily_login
                            #                 # else:
                            #                 #     pre_req_filter['duration_end'] = date_time_format

                            #                 if bench_time>pre_req_filter['duration_end'] and grace_over is False:
                            #                     pre_req_filter['checkin_benchmark']=True
                            #                     pre_req_filter['is_requested']=True


                            #                 if lunch_end < pre_req_filter['duration_start']:
                            #                     duration_count = round(((pre_req_filter['duration_end']-pre_req_filter['duration_start']).seconds)/60)
                            #                 elif lunch_start > pre_req_filter['duration_end']:
                            #                     duration_count = round(((pre_req_filter['duration_end']-pre_req_filter['duration_start']).seconds)/60)
                            #                 elif lunch_start > pre_req_filter['duration_start'] and lunch_end < pre_req_filter['duration_end']:
                            #                     duration_count = round(((lunch_start - pre_req_filter['duration_start'] + pre_req_filter['duration_end'] - lunch_end).seconds)/60)
                            #                 elif lunch_start > pre_req_filter['duration_start'] and lunch_end > pre_req_filter['duration_end']:
                            #                     duration_count = round(((lunch_start - pre_req_filter['duration_start']).seconds)/60)
                            #                 elif lunch_end < pre_req_filter['duration_end'] and lunch_start < pre_req_filter['duration_start']:
                            #                     duration_count = round(duration_count + ((pre_req_filter['duration_end']-lunch_end).seconds)/60)

                            #                 # print("duration_count",duration_count, pre_req_filter)
                            #                 if duration_count>0:
                            #                     pre_req_filter['duration']=duration_count
                            #                     pre_req_filter['attendance_date'] = pre_req_filter['duration_start'].date()
                            #                     pre_req = self.request_create(pre_req_filter)
                            #                     #print("pre_req",pre_req)


                            # if logout_time and pre_att:
                            #     # print('pre_att',pre_att.id)
                            #     pre_att_update = Attendance.objects.filter(pk=pre_att.id).update(logout_time=logout_time)
                            #     ### IF Late convence ### Successful Testing
                            #     if daily_logoutTime < logout_time.time():
                            #         late_con_filter['attendance']=pre_att
                            #         late_con_filter['attendance_date']=daily_logout.date()
                            #         late_con_filter['duration_start']=daily_logout
                            #         late_con_filter['duration_end']=logout_time
                            #         late_con_filter['duration'] = round(((late_con_filter['duration_end']-late_con_filter['duration_start']).seconds)/60)
                            #         late_con_filter['is_late_conveyance']=True
                            #         if late_con_filter['duration']>10: #If late conveyance grater then 10 Minutes. 
                            #             # print("late_con_filter",late_con_filter)
                            #             late_req = self.request_create(late_con_filter)
                            #             # print("late_req",late_req)
                                
                            #     ###If Logout less then User's Daily log out### Successful Testing
                            #     elif daily_logoutTime > logout_time.time():
                            #         late_con_filter['attendance']=pre_att
                            #         late_con_filter['attendance_date']=daily_logout.date()
                            #         late_con_filter['duration_start']=logout_time
                            #         late_con_filter['duration_end']=daily_logout
                            #         late_con_filter['duration'] = round(((late_con_filter['duration_end']-late_con_filter['duration_start']).seconds)/60)
                            #         late_con_filter['is_late_conveyance']=False
                            #         # late_con_filter['request_type']='GR'
                            #         if late_con_filter['duration']>0:
                            #             # print("late_con_filter",late_con_filter)
                            #             late_req = self.request_create(late_con_filter)
                            #             # print("late_req",late_req)

                            # ## IF User Absent ###
                            # if user_flag==0:
                            #     # print("ABSENT")
                            #     is_required = False
                            #     # print("user",cu_user_id)
                            #     adv_leave_type = None
                            #     leave = EmployeeAdvanceLeaves.objects.filter(
                            #         Q(start_date__date__lte=date_time_day)&Q(end_date__date__gte=date_time_day)&Q(employee_id=cu_user_id)&  #changes by abhisek 21/11/19
                            #         (Q(approved_status='pending')|Q(approved_status='approved'))).values('leave_type','reason')
                            #     # print("leave",leave)
                            #     holiday = HolidaysList.objects.filter(status=True,holiday_date=date_time_day).values('holiday_name')

                            #     if leave:
                            #         adv_leave_type = leave[0]['leave_type']
                            #         # print("leave_type",leave[0]['leave_type'])
                            #         att_filter['day_remarks']=leave[0]['leave_type']
                            #         is_required = True
                            #     elif holiday:
                            #         holiday_name = holiday[0]["holiday_name"]
                            #         att_filter['day_remarks']=holiday[0]["holiday_name"]
                            #     elif special_full_day:
                            #         # special_full_day_name = special_full_day[0]["full_day__date"]
                            #         att_filter['day_remarks']=special_full_day[0]["remarks"]
                            #     elif date_time_day.weekday()==6:
                            #         # print("Sunday")
                            #         att_filter['day_remarks']="Sunday"
                            #     elif date_time_day.weekday()==5:
                            #         saturday_off_list = AttendenceSaturdayOffMaster.objects.filter(employee_id=cu_user_id,is_deleted=False).values(
                            #         'first', 'second', 'third', 'fourth', 'all_s_day').order_by('-id')

                            #         if saturday_off_list:
                            #             if saturday_off_list[0]['all_s_day'] is True:
                            #                 # if user['is_saturday_off'] is True:
                            #                 att_filter['day_remarks']='Saturday'

                            #             else:
                            #                 week_date = date_time_day.day
                            #                 # print("week_date",  week_date)
                            #                 month_calender = calendar.monthcalendar(date_time_day.year, date_time_day.month)
                            #                 saturday_list = (0,1,2,3) if month_calender[0][calendar.SATURDAY] else (1,2,3,4)

                            #                 if saturday_off_list[0]['first'] is True and int(week_date)==int(month_calender[saturday_list[0]][calendar.SATURDAY]):
                            #                     att_filter['day_remarks']='Saturday'
                            #                 elif saturday_off_list[0]['second'] is True and int(week_date)==int(month_calender[saturday_list[1]][calendar.SATURDAY]):
                            #                     att_filter['day_remarks']='Saturday'
                            #                 elif saturday_off_list[0]['third'] is True and int(week_date)==int(month_calender[saturday_list[2]][calendar.SATURDAY]):
                            #                     att_filter['day_remarks']='Saturday'
                            #                 elif saturday_off_list[0]['fourth'] is True and int(week_date)==int(month_calender[saturday_list[3]][calendar.SATURDAY]):
                            #                     att_filter['day_remarks']='Saturday'
                            #                 else:
                            #                     #print("Not Present")
                            #                     is_required = True
                            #                     att_filter['day_remarks']="Not Present"
                                                    
                            #         else:
                            #             is_required = True
                            #             att_filter['day_remarks']="Not Present"
                            #         # print("Saturday")

                            #     else:
                            #         is_required = True
                            #         att_filter['day_remarks']="Not Present"
                            #     if att_filter:
                            #         date = date_time[0:10]+'T'+str(daily_loginTime)
                            #         date_time_date =datetime.strptime(date, "%Y-%m-%dT%H:%M:%S")
                            #         #print("date_time_format",date_time_date)
                            #         att_filter['date']=date_time_date
                            #         #print("att_filter",att_filter)

                            #         abs_att = self.att_create(att_filter)
                            #         #print("att_filter",abs_att)
                            #         if is_required is True:
                            #             req_filter['attendance']= abs_att
                            #             req_filter['attendance_date'] = daily_login.date()
                            #             req_filter['duration_start'] = daily_login
                            #             req_filter['duration_end'] = daily_logout
                            #             req_filter['duration'] = round(((req_filter['duration_end']-req_filter['duration_start']).seconds)/60)

                            #             if adv_leave_type:
                            #                 req_filter['request_type']='FD'
                            #                 req_filter['leave_type'] = adv_leave_type
                            #                 req_filter['approved_status'] = 'approved'
                            #                 req_filter['is_requested'] = True
                            #                 req_filter['justification'] = leave[0]['reason']

                            #             if req_filter:
                            #                 abs_req = self.request_create(req_filter)
                            #                 # print("abs_req",abs_req, req_filter)


            return Response({'result':{'request_status':1,'msg':'Successful'}})
        else:
            Response({'result':{'request_status':0,'msg':'punch_list or date range error'}})


#:::::::::::::::::: DOCUMENTS UPLOAD FOR USER  ::::::::::::::::::::::::#
class AttendanceUserAttendanceUploadByLogData(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    # queryset = AttandancePerDayDocuments.objects.filter(is_deleted=False)

    def att_create(self, filter: dict):
        logdin_user_id = self.request.user.id
        attendance= Attendance.objects.create(created_by_id=logdin_user_id,owned_by_id=logdin_user_id,**filter)
        return attendance
    def request_create(self, filter: dict):
        logdin_user_id = self.request.user.id  #attendance_date
        request= AttendanceApprovalRequest.objects.create(created_by_id=logdin_user_id,owned_by_id=logdin_user_id,**filter)
        return request

    def post(self, request, *args, **kwargs):
        # response = super().post(request,*args,**kwargs)
        # print("response",response.data['document'])
        print("request", request.data['emp_list'])
        emp_list = request.data['emp_list'].split(',') # Enter user_id list in this list
        last_date = datetime.strptime(request.data['last_date'],"%Y-%m-%d")
        print("emp_list",emp_list, last_date)
        print("Please wait...")
        user_details = TCoreUserDetail.objects.filter(cu_user__in=emp_list,cu_is_deleted=False).values()
        print('user_details',len(user_details))
        user_count = len(user_details) if user_details else 0
        holiday_list = HolidaysList.objects.filter(status=True).values('holiday_date','holiday_name')
        device_no_list = DeviceMaster.objects.filter(is_exit=True,is_deleted=False).values_list('id',flat=True)
        # if device_details:
        #     device_no_list = [x['id'] for x in device_details]
        print("device_no_list", device_no_list)

        for user in user_details:
            user_count = user_count-1
            print("Wait...", user_count)
            att_by_day = Attendance.objects.filter(employee=user['cu_user_id'],date__date__lte=last_date.date()).order_by('date').values()
            print("att_by_day", att_by_day)
        #     ######
            for per_day in att_by_day:
                with transaction.atomic():
                    print(user_count, "per_day", per_day['date'])
                    today_datetime = per_day['date']
                    date_time_day = today_datetime.date()
                    total_month_grace=AttendenceMonthMaster.objects.filter(month_start__date__lte=today_datetime.date(),
                                    month_end__date__gte=today_datetime.date(),is_deleted=False).values('grace_available',
                                                                                'year_start_date', 'year_end_date', 'month', 
                                                                                'month_start', 'month_end','grace_available'
                                                                                )
                    # print("total_month_grace",total_month_grace)

                    # special_day = AttendanceSpecialdayMaster.objects.filter(((Q(day_start_time__date=today_datetime.date())|Q(
                    #     day_end_time__date=today_datetime.date())) & Q(is_deleted=False))).values('day_start_time__time','day_end_time__time','remarks')

                    # special_full_day = AttendanceSpecialdayMaster.objects.filter(full_day__date=today_datetime.date(),is_deleted=False).values('full_day__date','remarks')
                    # print("special_full_day",special_full_day)
                    # print("special_day",special_day)
                    special_day = AttendanceSpecialdayMaster.objects.filter(((Q(day_start_time__date=today_datetime.date())|Q(
                        day_end_time__date=today_datetime.date())) & Q(is_deleted=False))).values('day_start_time__time','day_end_time__time','remarks')

                    special_full_day = AttendanceSpecialdayMaster.objects.filter(full_day__date=today_datetime.date(),is_deleted=False).values('full_day__date','remarks')
                    '''
                    Modified By :: Rajesh Samui
                    Reason :: State Wise Holiday Calculation
                    Line :: 7393-7411
                    Date :: 10-02-2020
                    '''
                    # holiday = HolidaysList.objects.filter(status=True,holiday_date=date_time_day).values('holiday_name')
                    state_obj = TCoreUserDetail.objects.get(cu_user__id=cu_user_id).job_location_state
                    default_state = TCoreState.objects.filter(cs_state_name__iexact='west bengal').first()
                    t_core_state_id = state_obj.id if state_obj else default_state.id
                    holiday = HolidayStateMapping.objects.filter(Q(holiday__holiday_date=date_time_day)&Q(state__id=t_core_state_id)).values('holiday__holiday_name')

                    # print(state_obj)
                    # print(t_core_user_state_code)
                    # print(holiday)

                    print('holiday',holiday)
                    print("special_full_day",special_full_day)
                    print("special_day",special_day)
                    ##########
                    no_request = False
                    day_remarks = ''
                    if holiday:
                        # holiday_name = holiday[0]["holiday_name"]
                        day_remarks = holiday[0]["holiday__holiday_name"]
                        no_request = True
                    elif special_full_day:
                        # special_full_day_name = special_full_day[0]["full_day__date"]
                        day_remarks = special_full_day[0]["remarks"]
                        no_request = True
                    elif date_time_day.weekday()==6:
                        # print("Sunday")
                        day_remarks = "Sunday"
                        no_request = True

                    # AttendanceApprovalRequest.objects.filter(attendance=per_day['id']).delete()
                    # print("delete_request",delete_request)
                    log_details = AttendanceLog.objects.filter(attendance=per_day['id'],employee=user['cu_user_id']).values()
                    # print("log_details",log_details)

                    #######

                    att_filter = {}
                    req_filter = {}
                    pre_att_filter = {}
                    pre_req_filter = {}
                    late_con_filter = {}
                    bench_filter = {}
                    saturday_off_list = None
                    pre_att = None
                    saturday_off = False

                    logout_time = None
                    check_out = 0
                    # adv_leave_type = None
                    user_flag = 0
                    cu_punch_id = user['cu_punch_id'] if user['cu_punch_id'] else None
                    cu_user_id = int(user['cu_user_id'])

                    #################
                    if date_time_day.weekday()==5 and no_request is False:
                        saturday_off_list = AttendenceSaturdayOffMaster.objects.filter(employee_id=cu_user_id,is_deleted=False).values(
                            'first', 'second', 'third', 'fourth', 'all_s_day').order_by('-id')

                        print("saturday_off_list",date_time_day.weekday(), saturday_off_list)

                        if saturday_off_list:
                            if saturday_off_list[0]['all_s_day'] is True:
                                # if user['is_saturday_off'] is True:
                                day_remarks = 'Saturday'
                                saturday_off = True

                            else:
                                week_date = date_time_day.day
                                # print("week_date",  week_date)
                                month_calender = calendar.monthcalendar(date_time_day.year, date_time_day.month)
                                saturday_list = (0,1,2,3) if month_calender[0][calendar.SATURDAY] else (1,2,3,4)

                                if saturday_off_list[0]['first'] is True and int(week_date)==int(month_calender[saturday_list[0]][calendar.SATURDAY]):
                                    day_remarks='Saturday'
                                    saturday_off = True
                                elif saturday_off_list[0]['second'] is True and int(week_date)==int(month_calender[saturday_list[1]][calendar.SATURDAY]):
                                    day_remarks='Saturday'
                                    saturday_off = True
                                elif saturday_off_list[0]['third'] is True and int(week_date)==int(month_calender[saturday_list[2]][calendar.SATURDAY]):
                                    day_remarks='Saturday'
                                    saturday_off = True
                                elif saturday_off_list[0]['fourth'] is True and int(week_date)==int(month_calender[saturday_list[3]][calendar.SATURDAY]):
                                    day_remarks='Saturday'
                                    saturday_off = True

                            # print("Saturday")

                    #################

                    ###If user has no login/logout/lunch time >> Then fix their time##
                    user['daily_loginTime'] = today_datetime.replace(hour=10, minute=00).time() if user['daily_loginTime'] is None else user['daily_loginTime']
                    user['daily_logoutTime'] = today_datetime.replace(hour=19, minute=00).time() if user['daily_logoutTime'] is None else user['daily_logoutTime']
                    user['lunch_start'] = today_datetime.replace(hour=13, minute=30).time() if user['lunch_start'] is None else user['lunch_start']
                    user['lunch_end'] = today_datetime.replace(hour=14, minute=00).time() if user['lunch_end'] is None else user['lunch_end']
                    
                    ## If Change Login-Logout time (Special Day) ##
                    if special_day:
                        daily_loginTime = special_day[0]['day_start_time__time'] if special_day[0]['day_start_time__time'] is not None else user['daily_loginTime']
                        # daily_logoutTime = special_day[0]['day_end_time__time'] if special_day[0]['day_end_time__time'] is not None else user['daily_logoutTime']
                        daily_logoutTime = special_day[0]['day_end_time__time'] if special_day[0]['day_end_time__time'] is not None and \
                                                                                    special_day[0]['day_end_time__time']<user['daily_logoutTime'] else user['daily_logoutTime']
                        print("daily_logoutTime",daily_logoutTime)
                        pre_att_filter['day_remarks'] = special_day[0]['remarks'] if special_day[0]['remarks'] is not None else ''
                    elif today_datetime.weekday()==5:
                        daily_loginTime = user['daily_loginTime']
                        daily_logoutTime = user['saturday_logout'] if user['saturday_logout'] is not None else user['daily_logoutTime'].replace(hour=16, minute=00)
                        pre_att_filter['day_remarks'] = 'Present'

                    else:
                        daily_loginTime = user['daily_loginTime']
                        daily_logoutTime = user['daily_logoutTime']
                        pre_att_filter['day_remarks'] = 'Present'
                    
                    ## LUNCH TIME ##
                    lunch_start = datetime.combine(today_datetime,user['lunch_start'])
                    lunch_end = datetime.combine(today_datetime,user['lunch_end'])

                    ## DAILY LOGIN-LOGOUT ##
                    # print("daily_loginTime", daily_loginTime, type(daily_loginTime))
                    daily_login = datetime.combine(today_datetime,daily_loginTime)
                    daily_logout = datetime.combine(today_datetime,daily_logoutTime)

                    is_saturday_off = user['is_saturday_off'] 
                    att_filter['employee_id'] = cu_user_id
                    grace_over = False

                    joining_date = user['joining_date']
                    if total_month_grace:
                        grace_available = total_month_grace[0]['grace_available'] if total_month_grace[0]['grace_available'] is not None else 0
                        print("GRACE", grace_available)
                        if joining_date >= total_month_grace[0]['month_start'] and joining_date <= total_month_grace[0]['month_end']:
                            total_grace = JoiningApprovedLeave.objects.filter(employee=cu_user_id,is_deleted=False).values('first_grace')
                            grace_available = total_grace[0]['first_grace'] if total_grace[0]['first_grace'] is not None else 0
                            print("grace_available AAAA", grace_available, cu_user_id)

                    availed_grace=AttendanceApprovalRequest.objects.filter(Q(attendance__employee=cu_user_id) &
                                                                    Q(duration_start__gte=total_month_grace[0]['month_start']) &
                                                                    Q(duration_start__lte=total_month_grace[0]['month_end']) &
                                                                    Q(is_requested=True) &
                                                                    Q(is_deleted=False)&
                                                                    (Q(request_type='GR')|Q(checkin_benchmark=True))
                                                                    ).aggregate(Sum('duration'))['duration__sum']
                    print('availed_grace',availed_grace)
                    availed_grace = availed_grace if availed_grace else 0
                    
                    # if grace_available<availed_grace: #nur code 
                    #     grace_over = True
                    if log_details:
                        user_flag = 1
                        for daily_log in log_details:
                            # print('daily_log',daily_log['time'])
                            # lunch_start = datetime.combine(today_datetime,user['lunch_start'])
                            # date_time = str(row['Date'])+'T'+str(row['Time'])
                            date_time_format = daily_log['time']
                            #print('cu_punch_id_type',type(cu_punch_id),cu_punch_id)
                            #print('rowEmpid',type(row['Empid']),row['Empid'])
                            # if cu_punch_id == row['Empid']:
                            # deviceMasterDetails = DeviceMaster.objects.filter(device_no=int(daily_log['CID']))
                            # if deviceMasterDetails:
                            #     current_device = DeviceMaster.objects.get(device_no=int(daily_log['CID']))
                                # print("current_device",current_device)

                            current_device = daily_log['device_no_id']
                            # print("current_device", current_device , type(current_device))
                            ##################### END ###################################
                            pre_att_filter['employee_id'] = cu_user_id
                            # pre_att_filter['day_remarks'] = 'Present'
                            pre_att_filter['is_present'] = True
                            pre_att_filter['date'] = date_time_format
                            pre_att_filter['login_time'] = date_time_format
                            # print("pre_att_filter",pre_att_filter)

                            ##First time log in a Day##Successful
                            if pre_att is None:                      
                                if pre_att_filter:
                                    pre_att = self.att_create(pre_att_filter)
                                    bench_time = daily_login + timedelta(minutes=30)
                                    # print('bench_time',bench_time)
                                    # if saturday_off is False and no_request is False:

                                    ###Check login if After USER Daily login time = Duration### Successful
                                    if daily_login<pre_att_filter['login_time'] and saturday_off is False and no_request is False:
                                            bench_filter['attendance']=pre_att
                                            bench_filter['attendance_date'] = daily_login.date()
                                            bench_filter['duration_start']=daily_login
                                            bench_filter['duration_end']=pre_att_filter['login_time']
                                            bench_filter['duration'] = round(((bench_filter['duration_end']-bench_filter['duration_start']).seconds)/60)
                                            bench_filter['punch_id'] = cu_punch_id
                                            if grace_available<availed_grace + float(bench_filter['duration']): #abhisek code 
                                                grace_over = True
                                            if bench_time>pre_att_filter['login_time'] and grace_over is False:
                                                bench_filter['checkin_benchmark']=True
                                                bench_filter['is_requested']=True
                                                # bench_filter['is_requested']=True
                                                # bench_filter['request_type']='GR'
                                            else:
                                                bench_filter['checkin_benchmark']=False

                                            if bench_filter['duration']>0:
                                                bench_req = self.request_create(bench_filter)

                            ##After Daily Attendance## Successful
                            if pre_att:
                                att_log_create, create1 = AttendanceLog.objects.get_or_create(
                                    attendance=pre_att,
                                    employee_id=cu_user_id,
                                    time=date_time_format,
                                    device_no=current_device
                                )

                                logout_time = date_time_format
                                duration_count = 0
                                if saturday_off is False and no_request is False:
                                    if check_out == 0 and current_device.__dict__['id'] in device_no_list and date_time_format<daily_logout:
                                        # print("if current_device in device_no_list:")
                                        check_out = 1
                                        pre_req_filter['attendance'] = pre_att
                                        pre_req_filter['punch_id'] = cu_punch_id
                                        pre_req_filter['duration_start'] = date_time_format
                                    elif check_out == 1 and current_device not in device_no_list and date_time_format<daily_login:
                                        check_out = 0
                                        pre_req_filter = {}
                                    elif check_out == 1 and current_device not in device_no_list and date_time_format>daily_login:
                                        check_out = 0
                                        if date_time_format>daily_logout:
                                            pre_req_filter['duration_end'] = daily_logout
                                        else:
                                            pre_req_filter['duration_end'] = date_time_format

                                        if pre_req_filter['duration_start']<daily_login:
                                            pre_req_filter['duration_start'] = daily_login
                                        # else:
                                        #     pre_req_filter['duration_end'] = date_time_format

                                        # if bench_time>pre_req_filter['duration_end'] and grace_over is False:
                                        #     pre_req_filter['checkin_benchmark']=True
                                        #     pre_req_filter['is_requested']=True


                                        if lunch_end < pre_req_filter['duration_start']:
                                            duration_count = round(((pre_req_filter['duration_end']-pre_req_filter['duration_start']).seconds)/60)
                                        elif lunch_start > pre_req_filter['duration_end']:
                                            duration_count = round(((pre_req_filter['duration_end']-pre_req_filter['duration_start']).seconds)/60)
                                        elif lunch_start > pre_req_filter['duration_start'] and lunch_end < pre_req_filter['duration_end']:
                                            duration_count = round(((lunch_start - pre_req_filter['duration_start'] + pre_req_filter['duration_end'] - lunch_end).seconds)/60)
                                        elif lunch_start > pre_req_filter['duration_start'] and lunch_end > pre_req_filter['duration_end']:
                                            duration_count = round(((lunch_start - pre_req_filter['duration_start']).seconds)/60)
                                        elif lunch_end < pre_req_filter['duration_end'] and lunch_start < pre_req_filter['duration_start']:
                                            duration_count = round(duration_count + ((pre_req_filter['duration_end']-lunch_end).seconds)/60)

                                        # print("duration_count",duration_count, pre_req_filter)
                                        if duration_count>0:
                                            pre_req_filter['duration']=duration_count
                                            pre_req_filter['attendance_date'] = pre_req_filter['duration_start'].date()
                                            pre_req = self.request_create(pre_req_filter)
                                            pre_req_filter = {}
                                            #print("pre_req",pre_req)


                    if logout_time and pre_att:
                        # print('pre_att',pre_att.id)
                        pre_att_update = Attendance.objects.filter(pk=pre_att.id).update(logout_time=logout_time)
                        if saturday_off is False and no_request is False:
                            ### IF Late convence ### Successful Testing
                            if daily_logoutTime < logout_time.time():
                                late_con_filter['attendance'] = pre_att
                                late_con_filter['punch_id'] = cu_punch_id
                                late_con_filter['attendance_date']=daily_logout.date()
                                late_con_filter['duration_start']=daily_logout
                                late_con_filter['duration_end']=logout_time
                                late_con_filter['duration'] = round(((late_con_filter['duration_end']-late_con_filter['duration_start']).seconds)/60)
                                late_con_filter['is_late_conveyance']=True
                                # if late_con_filter['duration']>10: #If late conveyance grater then 10 Minutes.
                                '''
                                    As per requirement and discussion with Tonmay Da(10.12.2019):
                                    LATE CONVENCE always count after 08:30 PM 
                                '''
                                if late_convence_limit>=late_con_filter['duration_start'] and late_convence_limit<late_con_filter['duration_end']\
                                    and late_con_filter['duration']>0:
                                    # print("late_con_filter",late_con_filter)
                                    late_req = self.request_create(late_con_filter)
                                    # print("late_req",late_req)
                            
                            ###If Logout less then User's Daily log out### Successful Testing
                            elif daily_logoutTime > logout_time.time():
                                late_con_filter['attendance']=pre_att
                                late_con_filter['punch_id'] = cu_punch_id
                                late_con_filter['attendance_date']=daily_logout.date()
                                late_con_filter['duration_start']=logout_time
                                late_con_filter['duration_end']=daily_logout
                                late_con_filter['duration'] = round(((late_con_filter['duration_end']-late_con_filter['duration_start']).seconds)/60)
                                late_con_filter['is_late_conveyance']=False
                                # late_con_filter['request_type']='GR'
                                if late_con_filter['duration']>0:
                                    # print("late_con_filter",late_con_filter)
                                    late_req = self.request_create(late_con_filter)
                                    # print("late_req",late_req)

                ## IF User Absent ###
                    if user_flag==0:
                        # print("ABSENT")
                        is_required = False
                        # print("user",cu_user_id)
                        adv_leave_type = None
                        leave = EmployeeAdvanceLeaves.objects.filter(
                            Q(start_date__date__lte=date_time_day)&Q(end_date__date__gte=date_time_day)&Q(employee_id=cu_user_id)&  #changes by abhisek 21/11/19
                            (Q(approved_status='pending')|Q(approved_status='approved'))).values('leave_type','reason')
                        # print("leave",leave)
                        # holiday = HolidaysList.objects.filter(status=True,holiday_date=date_time_day).values('holiday_name')

                        if leave:
                            adv_leave_type = leave[0]['leave_type']
                            # print("leave_type",leave[0]['leave_type'])
                            att_filter['day_remarks']=leave[0]['leave_type']
                            is_required = True
                        elif saturday_off is True or no_request is True:
                            att_filter['day_remarks'] = day_remarks
                            print("att_filter",att_filter, saturday_off, no_request)
                        else:
                            is_required = True
                            att_filter['day_remarks']="Not Present"

                        if att_filter:
                            date = date_time[0:10]+'T'+str(daily_loginTime)
                            date_time_date =datetime.strptime(date, "%d/%m/%YT%H:%M:%S")
                            #print("date_time_format",date_time_date)
                            att_filter['date'] = date_time_date
                            #print("att_filter",att_filter)

                            abs_att = self.att_create(att_filter)
                            print("att_filter",abs_att, is_required)
                            if is_required is True:
                                req_filter['attendance']= abs_att
                                req_filter['attendance_date'] = daily_login.date()
                                req_filter['duration_start'] = daily_login
                                req_filter['duration_end'] = daily_logout
                                req_filter['duration'] = round(((req_filter['duration_end']-req_filter['duration_start']).seconds)/60)

                                if adv_leave_type:
                                    req_filter['request_type']='FD'
                                    req_filter['leave_type'] = adv_leave_type
                                    req_filter['approved_status'] = 'approved'
                                    req_filter['is_requested'] = True
                                    req_filter['justification'] = leave[0]['reason']

                                if req_filter:
                                    print("req_filter,",req_filter)
                                    req_filter['punch_id'] = cu_punch_id
                                    abs_req = self.request_create(req_filter)
                                    # abs_check = self.absent_checking(req_filter)
                                    # print("abs_req",abs_req, req_filter)
                                    
                    print("DELETE START FOR :", per_day['id'])
                    AttendanceLog.objects.filter(attendance=per_day['id']).delete()
                    AttendanceApprovalRequest.objects.filter(attendance=per_day['id']).delete()
                    Attendance.objects.filter(id=per_day['id']).delete()
                    print("DELETE COMPLETE", )
        return Response({'result':{'request_status':1,'msg':'Successful'}})

#########

class AttendanceNewUsersJoiningLeaveCalculation(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def post(self, request, *args, **kwargs):
        logdin_user_id = self.request.user.id
        # print('logdin_user_id',logdin_user_id)
        checking_join_date = datetime.strptime(request.data['checking_join_date'],"%Y-%m-%d") #First date of the year
        joining_date_details=TCoreUserDetail.objects.filter(~Q(cu_user__in=JoiningApprovedLeave.objects.filter().values_list('employee',flat=True))&
                                                            Q(joining_date__date__gt=checking_join_date)&~Q(cu_is_deleted=True)
                                                            ).values('joining_date','cu_user','granted_cl','granted_sl','granted_el')
        print('joining_date_details',joining_date_details)
        if joining_date_details:
            for user in joining_date_details:
                print("user",user['cu_user'], user['joining_date'])
                if user['joining_date']:
                    leave_filter = {}
                    joining_date = user['joining_date'].date()
                    joining_year=joining_date.year
                    print('joining_year',joining_date)
                    total_month_grace=AttendenceMonthMaster.objects.filter(month_start__date__lte=joining_date,
                                    month_end__date__gte=joining_date,is_deleted=False).values('grace_available',
                                                                                'year_start_date',
                                                                                'year_end_date',
                                                                                'month',
                                                                                'month_start',
                                                                                'month_end'
                                                                                )
                    if total_month_grace:
                        year_end_date=total_month_grace[0]['year_end_date'].date()
                        total_days=(year_end_date - joining_date).days
                        # print('total_days',total_days)
                        if user['granted_cl']:
                            leave_filter['cl']=round((total_days/365)* int(user['granted_cl']))
                        else:
                            leave_filter['cl']= 0
                        if user['granted_el']:
                            leave_filter['el']=round((total_days/365)* int(user['granted_el']))
                        else:
                            leave_filter['el']= 0
                        if user['granted_sl']:
                            leave_filter['sl']=round((total_days/365)* int(user['granted_sl']))
                            # print('calculated_sl',calculated_sl)
                        else:
                            leave_filter['sl']= 0

                        month_start_date=total_month_grace[0]['month_start'].date()
                        month_end_date=total_month_grace[0]['month_end'].date()
                        # print('month_start_date',month_start_date,month_end_date)
                        month_days=(month_end_date-month_start_date).days
                        # print('month_days',month_days)
                        remaining_days=(month_end_date-joining_date).days
                        # print('remaining_days',remaining_days)
                        # available_grace=round(total_month_grace[0]['grace_available']/remaining_days)
                        available_grace = round((remaining_days/month_days)*int(total_month_grace[0]['grace_available']))
                        # print('available_grace',available_grace)

                        # if total_month_grace[0]['year_start_date']<joining_date_details[0]['joining_date']:
                        JoiningApprovedLeave.objects.get_or_create(employee_id=user['cu_user'],
                                                            year=joining_year,
                                                            month=total_month_grace[0]['month'],
                                                            **leave_filter,
                                                            first_grace=available_grace,
                                                            created_by_id=logdin_user_id,
                                                            owned_by_id=logdin_user_id
                                                            )
                    

        return Response({'result':{'request_status':1,'msg':'Successful'}})



##############CRON TEST VIEW ################################
class AttendanceUserCronMailForPending(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    # queryset = AttandancePerDayDocuments.objects.filter(is_deleted=False)

    def get(self, request, *args, **kwargs):
        data = {}

        # current_date = datetime.now().date()
        current_date = datetime.now().date()
        current_month = current_date.month
        print("current_date",current_date)
        total_month_grace=AttendenceMonthMaster.objects.filter(month=current_month,is_deleted=False).\
                                                    values('lock_date__date'
                                                ,'year_start_date','year_end_date','month','month_start__date',
                                                'month_end__date','pending_action_mail__date')
        print("total_month_grace",total_month_grace)
        days_cnt = (total_month_grace[0]['lock_date__date'] - total_month_grace[0]['pending_action_mail__date']).days
        date_generated = [total_month_grace[0]['pending_action_mail__date'] + timedelta(days=x) for x in range(0,days_cnt)]

        print("date_day",date_generated)
            #working query local and live 
        if current_date in date_generated:
            print("entered",current_date)
            #working query local and live 
            user_list=TMasterModuleRoleUser.objects.\
                        filter(
                            Q(mmr_type=3),Q(mmr_is_deleted=False),
                            Q(mmr_module__cm_name='ATTENDANCE & HRMS')).\
                            values_list('mmr_user',flat=True).distinct()

            print("user_list",user_list.query)
            #email extraction            
            user_mail_list_primary=TMasterModuleRoleUser.objects.\
                        filter(
                            Q(mmr_type=3),Q(mmr_is_deleted=False),
                            Q(mmr_module__cm_name='ATTENDANCE & HRMS'),
                            (Q(mmr_user__email__isnull=False) & ~Q(mmr_user__email=""))).\
                            values('mmr_user__email').distinct()

            user_mail_official = TCoreUserDetail.objects.filter(
                (Q(cu_alt_email_id__isnull=False) & ~Q(cu_alt_email_id="")),cu_user__in=list(user_list)).\
                    values('cu_alt_email_id').distinct()
            print("user_mail_list_primary",user_mail_list_primary)
            print("user_mail_official",user_mail_official)
            umlp = [x['mmr_user__email'] for x in user_mail_list_primary]
            uma = [x['cu_alt_email_id'] for x in user_mail_official]

            user_mail_list = list(set(umlp + uma))
            print("user_mail_list",user_mail_list)

            
            
            emp_mob = TCoreUserDetail.objects.filter(cu_user__in=list(user_list),cu_phone_no__isnull=False).\
                values('cu_phone_no').distinct()
            emp_mob_no = [ x['cu_phone_no'] for x in emp_mob ]

        print("user_mail_list",user_mail_list)
        # ============= Mail Send Step ==============#

        print("email",user_mail_list)
        
        if user_mail_list:
            # for email in email_list:
            mail_data = {
            'name':None
            }
            print('mail_data',mail_data)
            # mail_class = GlobleMailSend('ATP-PM', user_mail_list)
            mail_class = GlobleMailSend('ATP-PM', ['prashant.damani@shyamsteel.com', 'sribesh@shyamsteel.com', 'kalyan.acharya@shyamfuture.com', 'shankar@shyamsteel.com', 'rupam@shyamfuture.com'])
            print('mail_class',mail_class)
            mail_thread = Thread(target = mail_class.mailsend, args = (mail_data,None))
            mail_thread.start()
            
        #===============================================#
        
        # # ============= Sms Send Step ==============#

        #     message_data = {
        #         'name':None
        #     }
        #     sms_class = GlobleSmsSendTxtLocal('ATTPR',emp_mob_no)
        #     # sms_class = GlobleSmsSendTxtLocal('ATTPR',['7595914029'])
        #     sms_thread = Thread(target = sms_class.sendSMS, args = (message_data,'sms'))
        #     sms_thread.start()

        #     #===================================================#
        data['results'] = list(user_mail_list)
        return Response(data)

class AttendanceUserCronMailForPendingRoh(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    # queryset = AttandancePerDayDocuments.objects.filter(is_deleted=False)

    def get(self, request, *args, **kwargs):
        data = {}

        current_date = datetime.now().date()
        current_month = current_date.month
        total_month_grace=AttendenceMonthMaster.objects.filter(month=current_month,is_deleted=False).\
                                                    values('lock_date__date'
                                                ,'year_start_date','year_end_date','month','month_start__date',
                                                'month_end__date','pending_action_mail__date')
        print("total_month_grace",total_month_grace)
        days_cnt = (total_month_grace[0]['lock_date__date'] - total_month_grace[0]['pending_action_mail__date']).days
        date_generated = [total_month_grace[0]['pending_action_mail__date'] + timedelta(days=x) for x in range(0,days_cnt+1)]

        print("date_day",date_generated)
        if current_date in date_generated:
            print("entered",current_date)
            #working query local and live 
            roh_userlist = TCoreUserDetail.objects.values_list('reporting_head',flat=True).distinct()
            print("roh_userlist",roh_userlist)
            user_mail_list=TMasterModuleRoleUser.objects.\
                filter(
                    Q(mmr_type=3),Q(mmr_is_deleted=False),
                    Q(mmr_module__cm_name='ATTENDANCE & HRMS'),
                    (Q(mmr_user__email__isnull=False) & ~Q(mmr_user__email="")),mmr_user__in=list(roh_userlist)).\
                    values_list('mmr_user__email',flat=True).distinct()
            print(user_mail_list.query)
            

            print("user_mail_list",user_mail_list, list(user_mail_list))
                # ============= Mail Send Step ==============#

            print("email",list(user_mail_list))
            if user_mail_list:
                # for email in email_list:
                mail_data = {
                'name':None
                }
                print('mail_data',mail_data)
                mail_class = GlobleMailSend('ATAP-PM', list(user_mail_list))
                print('mail_class',mail_class)
                mail_thread = Thread(target = mail_class.mailsend, args = (mail_data,None))
                mail_thread.start()
        data['results'] = list(user_mail_list)
        return Response(data)


class AttendanceUserCronLock(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def leave_calulate(self,employee_id,total_month_grace):
        total_grace={}
        date_object = datetime.now().date()
        print('employee_id',employee_id)
        advance_leave=EmployeeAdvanceLeaves.objects.filter(Q(employee=employee_id)&
                                                            Q(is_deleted=False)&
                                                            (Q(approved_status='pending')|Q(approved_status='approved'))
                                                            ).values('leave_type','start_date','end_date')
        print('advance_leave',advance_leave)     
        advance_cl=0
        advance_el=0
        advance_ab=0           
        day=0

        # date =self.request.query_params.get('employee', None)
        if advance_leave:
            for leave in advance_leave.iterator():
                #print('leave',leave)
                start_date=leave['start_date'].date()
                end_date=leave['end_date'].date()+timedelta(days=1)
                #print('start_date,end_date',start_date,end_date)
                if date_object < end_date:
                    if date_object < start_date:
                        day=(end_date-start_date).days 
                        #print('day',day)
                    elif date_object > start_date:
                        day=(end_date-date_object).days
                        #print('day2',day)
                    else:
                        day=(end_date-date_object).days

                if leave['leave_type']=='CL':
                    advance_cl+=day
                    #print('advance_cl_1',advance_cl)
                elif leave['leave_type']=='EL':
                    advance_el+=day
                    #print('advance_el_2',advance_el)
                elif leave['leave_type']=='AB':
                    advance_ab+=day

            

        print('advance_cl',advance_cl,type(advance_cl))
        print('advance_el',advance_el,type(advance_el))


        
        """ 
        LEAVE CALCULATION:-
        1)SINGLE LEAVE CALCULATION
        2)MULTIPLE LEAVE FOR ONE DAY IS AUTO CONVERTED TO ONE TYPE OF LEAVE 
        CREATED & EDITED BY :- Abhishek.singh@shyamfuture.com
        
        """ 
        #starttime = datetime.now()
        availed_hd_cl=0.0
        availed_hd_el=0.0
        availed_hd_sl=0.0
        availed_hd_ab=0.0
        availed_cl=0.0
        availed_el=0.0
        availed_sl=0.0
        availed_ab=0.0

        attendence_daily_data = AttendanceApprovalRequest.objects.filter(((Q(leave_type_changed_period__isnull=False)&(Q(leave_type_changed_period='FD')|Q(leave_type_changed_period='HD')))|
                                                                        (Q(leave_type_changed_period__isnull=True)&(Q(request_type='FD')|Q(request_type='HD')))),
                                                                        attendance__employee=employee_id,is_requested=True).values('duration_start__date').distinct()
        print("attendence_daily_data",attendence_daily_data)
        date_list = [x['duration_start__date'] for x in attendence_daily_data.iterator()]
        #print("date_list",date_list)
        # for data in attendence_daily_data.iterator():
            # print(datetime.now())
        availed_master_wo_reject_fd = AttendanceApprovalRequest.objects.\
                filter((Q(approved_status='pending')|Q(approved_status='approved')|Q(approved_status='reject')),
                        (Q(leave_type__isnull=False)|Q(leave_type_changed_period__isnull=False)),
                        attendance__employee=employee_id,
                        attendance_date__in=date_list,is_requested=True,is_deleted=False).annotate(
                            leave_type_final = Case(
                            When((Q(leave_type_changed_period__isnull=False)&Q(leave_type_changed_period='FD')),then=F('leave_type_changed')),
                            When((Q(leave_type_changed_period__isnull=True)&Q(request_type='FD')),then=F('leave_type')),
                            output_field=CharField()
                        ),
                        leave_type_final_hd = Case(
                            When((Q(leave_type_changed_period__isnull=False)&Q(leave_type_changed_period='HD')),then=F('leave_type_changed')),
                            When((Q(leave_type_changed_period__isnull=True)&Q(request_type='HD')),then=F('leave_type')),
                            output_field=CharField()
                        ),
                        ).values('leave_type_final','leave_type_final_hd','attendance_date').distinct()
        print("availed_master_wo_reject_fd",availed_master_wo_reject_fd)
        if availed_master_wo_reject_fd:

            for data in date_list:
                availed_FD=availed_master_wo_reject_fd.filter(attendance_date=data)
                
                #print("availed_HD",availed_FD)
                if availed_FD.filter(leave_type_final__isnull=False):
                    if availed_FD.values('leave_type_final').count() >1:
                        if availed_FD.filter(leave_type_final='AB'):
                            availed_ab=availed_ab+1.0

                        elif availed_FD.filter(leave_type_final='CL'):
                            availed_cl=availed_cl+1.0
                                    

                    else:
                        l_type=availed_FD[0]['leave_type_final']
                        if l_type == 'CL':
                            availed_cl=availed_cl+1.0
                        elif l_type == 'EL':
                            availed_el=availed_el+1.0
                        elif l_type == 'SL':
                            availed_sl=availed_sl+1.0
                        elif l_type == 'AB':
                            availed_ab=availed_ab+1.0

                elif availed_FD.filter(leave_type_final_hd__isnull=False):
                    if availed_FD.values('leave_type_final_hd').count() >1:
                        if availed_FD.filter(leave_type_final_hd='AB'):
                            availed_hd_ab=availed_hd_ab+1.0

                        elif availed_FD.filter(leave_type_final_hd='CL'):
                            availed_hd_cl=availed_hd_cl+1.0
                                    

                    else:
                        l_type=availed_FD[0]['leave_type_final_hd']
                        if l_type == 'CL':
                            availed_hd_cl=availed_hd_cl+1.0
                        elif l_type == 'EL':
                            availed_hd_el=availed_hd_el+1.0
                        elif l_type == 'SL':
                            availed_hd_sl=availed_hd_sl+1.0
                        elif l_type == 'AB':
                            availed_hd_ab=availed_hd_ab+1.0
        

        

        print("availed_cl",availed_cl,type(availed_cl))
        print("availed_el",availed_el,type(availed_el))

        print('availed_hd_cl',availed_hd_cl/2.0,type(availed_hd_cl/2.0))
        print('availed_hd_el',availed_hd_el/2.0,type(availed_hd_el/2.0))

        # if employee_id == '1881':
        #     total_grace['availed_cl']= 20.0
        #     print("total_grace['availed_cl']",total_grace['availed_cl'])

        #     total_grace['availed_el']=0.0
        #     print("total_grace['availed_el']",total_grace['availed_el'])
        #     total_grace['availed_sl']=float(availed_sl)+float(availed_hd_sl/2.0)
        #     print("total_grace['availed_sl']",total_grace['availed_sl'])
        #     total_grace['availed_ab']=float(availed_ab)+float(advance_ab)+float(availed_hd_ab/2.0)
        # else:
        total_grace['availed_cl']= float(availed_cl)+ float(advance_cl) +(float(availed_hd_cl)/2.0)
        print("total_grace['availed_cl']",total_grace['availed_cl'])

        total_grace['availed_el']=float(availed_el)+float(advance_el)+float(availed_hd_el/2.0)
        print("total_grace['availed_el']",total_grace['availed_el'])
        total_grace['availed_sl']=float(availed_sl)+float(availed_hd_sl/2.0)
        print("total_grace['availed_sl']",total_grace['availed_sl'])
        total_grace['availed_ab']=float(availed_ab)+float(advance_ab)+float(availed_hd_ab/2.0)


        # print("total_grace['availed_ab']",total_grace['availed_ab'])

        # total_grace['total_availed_leave']=total_grace['availed_cl'] +total_grace['availed_el'] + total_grace['availed_sl']
        # core_user_detail=TCoreUserDetail.objects.filter(cu_user=employee_id,cu_is_deleted=False).values('joining_date',
        #                                                                                     'granted_cl',
        #                                                                                     'granted_sl',
        #                                                                                     'granted_el',
        #                                                                                     'is_confirm',
        #                                                                                     'salary_type__st_name'
        #                                                                                     )
        core_user_detail=TCoreUserDetail.objects.filter(cu_user=employee_id).values('joining_date',
                                                                                            'granted_cl',
                                                                                            'granted_sl',
                                                                                            'granted_el',
                                                                                            'is_confirm',
                                                                                            'salary_type__st_name'
                                                                                            )

        print('core_user_detail',core_user_detail)

        if core_user_detail:
            if core_user_detail[0]['salary_type__st_name']=='13' and core_user_detail[0]['is_confirm'] is False:
                total_grace['is_confirm'] = False
            else:
                total_grace['is_confirm'] = True
                # print("core_user_detail[0]['joining_date']",core_user_detail[0]['joining_date'],"total_month_grace[0]['year_start_date']",total_month_grace[0]['year_start_date'])
            if core_user_detail[0]['joining_date']>total_month_grace[0]['year_start_date']:
                approved_leave=JoiningApprovedLeave.objects.filter(employee=employee_id,is_deleted=False).values('cl', 'el', 'sl',
                                                                                                                'year', 'month',
                                                                                                                'first_grace')
                if approved_leave:
                    total_grace['granted_cl']=approved_leave[0]['cl']
                    total_grace['cl_balance']=float(approved_leave[0]['cl'] if approved_leave[0]['cl'] else 0.0) - float(total_grace['availed_cl'])
                    total_grace['granted_el']=approved_leave[0]['el']
                    total_grace['el_balance']=float(approved_leave[0]['el'] if approved_leave[0]['el'] else 0.0 ) - float(total_grace['availed_el'])
                    total_grace['granted_sl']=approved_leave[0]['sl']
                    total_grace['sl_balance']=float( approved_leave[0]['sl'] if approved_leave[0]['sl'] else 0.0 ) - float(total_grace['availed_sl'])
                    # total_grace['total_granted_leave']=float(approved_leave[0]['cl'] if approved_leave[0]['cl'] else 0.0) + float(approved_leave[0]['el'] if approved_leave[0]['el'] else 0.0) + float(approved_leave[0]['sl'] if approved_leave[0]['sl'] else 0.0)
                    # total_grace['total_leave_balances']=float(total_grace['total_granted_leave']) - float(total_grace['total_availed_leave'])
                    if total_month_grace[0]['month']==approved_leave[0]['month']:    #for joining month only
                        total_grace['total_month_grace']=approved_leave[0]['first_grace']
                        total_grace['month_start']=core_user_detail[0]['joining_date']
                        # total_grace['grace_balance']=total_grace['total_month_grace'] - total_grace['availed_grace']
            else:

                # total_grace['granted_cl']=core_user_detail[0]['granted_cl']
                print("granted cl",core_user_detail[0]['granted_cl'],type(core_user_detail[0]['granted_cl']))
                print("availed_cl cl",total_grace['availed_cl'],type(total_grace['availed_cl']))
                total_grace['cl_balance']=float(core_user_detail[0]['granted_cl']) -  float(total_grace['availed_cl'])
                total_grace['granted_el']=core_user_detail[0]['granted_el']
                total_grace['el_balance']=float(core_user_detail[0]['granted_el']) - float(total_grace['availed_el'])
                total_grace['granted_sl']=core_user_detail[0]['granted_sl']
                total_grace['sl_balance']=float(core_user_detail[0]['granted_sl']) - float(total_grace['availed_sl'])
                # total_grace['total_granted_leave']=float(core_user_detail[0]['granted_cl']) + float(core_user_detail[0]['granted_el']) + float(core_user_detail[0]['granted_sl'])
                # total_grace['total_leave_balances']=float(total_grace['total_granted_leave']) - float(total_grace['total_availed_leave'])

        return total_grace 


    def get(self, request, *args, **kwargs):
        date_object = datetime.now().date()
        current_date = datetime.now().date()
        current_month = current_date.month
        total_month_grace=AttendenceMonthMaster.objects.filter(month=current_month,is_deleted=False).values('lock_date__date'
                                                ,'year_start_date','year_end_date','month','month_start__date','month_end__date')
        # print("total_month_grace",total_month_grace)
        with transaction.atomic():
            print('lock_date__date',total_month_grace[0]['lock_date__date'])
            if current_date == total_month_grace[0]['lock_date__date']:
               
                # Exclude director's punch id from list
                user_details=TMasterModuleRoleUser.objects.\
                        filter(
                            Q(mmr_user__in=(TCoreUserDetail.objects.filter(~Q(cu_punch_id='#N/A'),user_type__in=('User','Housekeeper'),cu_is_deleted=False).values_list('cu_user',flat=True))),
                            Q(mmr_type=3),
                            Q(mmr_is_deleted=False),
                            Q(mmr_module__cm_name='ATTENDANCE & HRMS')).values_list('mmr_user',flat=True).distinct()
            
                print('user_details',len(user_details))
                for employee_id in user_details:

                    '''
                        For Testing Pupose leave check before OD Approval 7969-7970
                    '''
                    total_grace_finalbefore = self.leave_calulate(employee_id,total_month_grace)
                    print("loop before od ",total_grace_finalbefore)
                    
                    # print("employee_id",employee_id)
                    attendence_ids=AttendanceApprovalRequest.objects.filter(attendance_date__gte=total_month_grace[0]['month_start__date'],
                                                        attendance_date__lte=total_month_grace[0]['month_end__date'],is_late_conveyance=False,
                                                        is_requested=False,is_deleted=False,attendance__employee=employee_id).values_list('attendance',flat=True).distinct()
                    # print("attendence_ids",attendence_ids)
                    


                    #OD AUTO APPROVAL
                    od_app_req_id=AttendanceApprovalRequest.objects.filter(
                        (Q(request_type='POD')|Q(request_type='FOD')),
                        attendance__employee=employee_id,is_requested=True,approved_status='pending').values_list('id',flat=True).distinct()

                    
                    for app_req_id in list(od_app_req_id):

                        
                        AttendanceApprovalRequest.objects.filter(
                            id=app_req_id,
                            is_late_conveyance=False,
                            is_requested=True).update(approved_status='approved',remarks='AUTO OD APPROVED')

                        # total_grace_final = leave_calulate(employee_id,total_month_grace)
                        # print("Inside loop od grace",total_grace_final)
                        # duration_length=AttendanceApprovalRequest.objects.get(id=app_req_id,
                        #                                             is_requested=True).duration
                        # if duration_length < 240:
                        #     if total_grace_final['cl_balance'] > 0.0:

                        #         update_auto = AttendanceApprovalRequest.objects.filter(
                        #             id=app_req_id,is_late_conveyance=False,is_requested=True).\
                        #                                                     update(leave_type_changed_period='HD',leave_type_changed='CL',
                        #                                                     approved_status='approved',remarks='AUTO OD CONVERTED TO LEAVE & APPROVED')
                        #     elif total_grace_final['el_balance'] > 0.0:

                        #         update_auto = AttendanceApprovalRequest.objects.filter(id=app_req_id,is_late_conveyance=False,
                        #                                                 is_requested=True).\
                        #                                                     update(leave_type_changed_period='HD',leave_type_changed='EL',
                        #                                                     approved_status='approved',remarks='AUTO OD CONVERTED TO LEAVE & APPROVED')
                        #     else:

                        #         update_auto =AttendanceApprovalRequest.objects.filter(id=app_req_id,is_late_conveyance=False,
                        #                                                 is_requested=True).\
                        #                                                     update(leave_type_changed_period='HD',leave_type_changed='AB',
                        #                                                     approved_status='approved',remarks='AUTO OD CONVERTED TO LEAVE & APPROVED')
                        # else:
                        #     if total_grace_final['cl_balance'] > 0.5:

                        #         update_auto =AttendanceApprovalRequest.objects.filter(id=app_req_id,is_late_conveyance=False,
                        #                                                 is_requested=True).\
                        #                                                     update(leave_type_changed_period='FD',leave_type_changed='CL',
                        #                                                     approved_status='approved',remarks='AUTO OD CONVERTED TO LEAVE & APPROVED')
                        #     elif total_grace_final['el_balance'] > 0.5:

                        #         update_auto = AttendanceApprovalRequest.objects.filter(id=app_req_id,is_late_conveyance=False,
                        #                                                 is_requested=True).\
                        #                                                     update(leave_type_changed_period='FD',leave_type_changed='EL',
                        #                                                     approved_status='approved',remarks='AUTO OD CONVERTED TO LEAVE & APPROVED')
                        #     else:

                        #         update_auto = AttendanceApprovalRequest.objects.filter(id=app_req_id,is_late_conveyance=False,
                        #                                                 is_requested=True).\
                        #                                                     update(leave_type_changed_period='FD',leave_type_changed='AB',
                        #                                                     approved_status='approved',remarks='AUTO OD CONVERTED TO LEAVE & APPROVED')                       
                
                    
                    # total_grace_final2 = self.leave_calulate(employee_id,total_month_grace)
                    # print("after od leave calculate",total_grace_final2) 

                    for att_id in list(attendence_ids):
                        
                        total_grace_final2 = self.leave_calulate(employee_id,total_month_grace)
                        print('employee_id',employee_id)
                        print("Inside loop not requested grace",total_grace_final2)

                        duration_length=AttendanceApprovalRequest.objects.filter(attendance=att_id,is_late_conveyance=False,
                                                                    checkin_benchmark=False,is_requested=False).aggregate(Sum('duration'))['duration__sum']
                        print('duration_length',duration_length,'att_id',att_id)
                        print('employee_id',employee_id)
                        if duration_length is not None and duration_length < 240:
                            if total_grace_final2['cl_balance'] > 0.0:

                                update_auto = AttendanceApprovalRequest.objects.filter(attendance=att_id,is_late_conveyance=False,
                                                                        checkin_benchmark=False,is_requested=False).\
                                                                            update(request_type='HD',leave_type='CL',justification='AUTO',is_requested=True,
                                                                            approved_status='approved',remarks='AUTO LEAVE APPROVED')
                            elif total_grace_final2['el_balance'] > 0.0:

                                update_auto = AttendanceApprovalRequest.objects.filter(attendance=att_id,is_late_conveyance=False,
                                                                        checkin_benchmark=False,is_requested=False).\
                                                                            update(request_type='HD',leave_type='EL',justification='AUTO',is_requested=True,
                                                                            approved_status='approved',remarks='AUTO LEAVE APPROVED')
                            else:

                                update_auto = AttendanceApprovalRequest.objects.filter(attendance=att_id,is_late_conveyance=False,
                                                                        checkin_benchmark=False,is_requested=False).\
                                                                            update(request_type='HD',leave_type='AB',justification='AUTO',is_requested=True,
                                                                            approved_status='approved',remarks='AUTO LEAVE APPROVED')
                        else:
                            if total_grace_final2['cl_balance'] > 0.5:

                                update_auto = AttendanceApprovalRequest.objects.filter(attendance=att_id,is_late_conveyance=False,
                                                                        checkin_benchmark=False,is_requested=False).\
                                                                            update(request_type='FD',leave_type='CL',justification='AUTO',is_requested=True,
                                                                            approved_status='approved',remarks='AUTO LEAVE APPROVED')
                            elif total_grace_final2['el_balance'] > 0.5:

                                update_auto = AttendanceApprovalRequest.objects.filter(attendance=att_id,is_late_conveyance=False,
                                                                        checkin_benchmark=False,is_requested=False).\
                                                                            update(request_type='FD',leave_type='EL',justification='AUTO',is_requested=True,
                                                                            approved_status='approved',remarks='AUTO LEAVE APPROVED')
                            else:

                                update_auto = AttendanceApprovalRequest.objects.filter(attendance=att_id,is_late_conveyance=False,
                                                                        checkin_benchmark=False,is_requested=False).\
                                                                            update(request_type='FD',leave_type='AB',justification='AUTO',is_requested=True,
                                                                            approved_status='approved',remarks='AUTO LEAVE APPROVED')                        
                    #for checking
                    total_grace_final2 = self.leave_calulate(employee_id,total_month_grace)
                    print("after grace leave calculate",total_grace_final2) 
                    auto_grace_approval =AttendanceApprovalRequest.objects.filter(attendance__employee=employee_id,
                                                                            is_requested=True,request_type='GR',approved_status='pending').\
                                                                                update(approved_status='approved',remarks='AUTO GRACE APPROVED')

                    auto_misspunch_approval =AttendanceApprovalRequest.objects.filter(attendance__employee=employee_id,
                                                                            is_requested=True,request_type='MP',approved_status='pending').\
                                                                                update(approved_status='approved',remarks='AUTO MISSPUNCH APPROVED') 
                    
                print("entered or noyt ")                                                                             
                lock=AttendanceApprovalRequest.objects.filter(attendance_date__gte=total_month_grace[0]['month_start__date'],
                                                        attendance_date__lte=total_month_grace[0]['month_end__date'],
                                                        is_deleted=False).\
                                                            update(lock_status=True)
                print("lock",lock)   

        return Response({})


    # def get(self, request, *args, **kwargs):
    #     date_object = datetime.now().date()
    #     current_date = datetime.now().date()
    #     current_month = current_date.month
    #     total_month_grace=AttendenceMonthMaster.objects.filter(month=current_month,is_deleted=False).values('lock_date__date'
    #                                             ,'year_start_date','year_end_date','month','month_start__date','month_end__date')
    #     # print("total_month_grace",total_month_grace)
    #     #with transaction.atomic():
    #     print('lock_date__date',total_month_grace[0]['lock_date__date'])
    #     if current_date == total_month_grace[0]['lock_date__date']:
    #         # user_details = TCoreUserDetail.objects.filter((~Q(cu_user__in=TMasterModuleRoleUser.objects.filter(Q(mmr_type=1)|
    #         #                                         Q(mmr_type=6)|Q(mmr_is_deleted=True)).values_list('mmr_user',flat=True))),
    #         #                                         (~Q(cu_punch_id__in=['PMSSITE000','#N/A',''])),
    #         #                                         cu_is_deleted=False).values_list('cu_user',flat=True).distinct()
            
    #         # Exclude director's punch id from list
    #         user_details=TMasterModuleRoleUser.objects.\
    #                 filter(
    #                     ~Q(mmr_user__in=(TCoreUserDetail.objects.filter(
    #                         cu_punch_id__in=('10111032','10011271','10111036','00000160','00000171','00000022','00000168','00000163','00000161','00000016','00000018','00000162')).values_list('cu_user',flat=True))),
    #                     Q(mmr_type=3),Q(mmr_is_deleted=False),
    #                     Q(mmr_module__cm_name='ATTENDANCE & HRMS')).values_list('mmr_user',flat=True).distinct()
        
    #         #print('user_details',len(user_details))
    #         for employee_id in user_details:

    #             total_grace_finalbefore = leave_calulate(employee_id,total_month_grace)
    #             print("loop before od ",total_grace_finalbefore)
    #             # print("employee_id",employee_id)
    #             attendence_ids=AttendanceApprovalRequest.objects.filter(attendance_date__gte=total_month_grace[0]['month_start__date'],
    #                                                 attendance_date__lte=total_month_grace[0]['month_end__date'],is_late_conveyance=False,
    #                                                 is_requested=False,is_deleted=False,attendance__employee=employee_id).values_list('attendance',flat=True).distinct()
    #             # print("attendence_ids",attendence_ids)
                


    #             #OD AUTO APPROVAL
    #             od_app_req_id=AttendanceApprovalRequest.objects.filter(
    #                 (Q(request_type='POD')|Q(request_type='FOD')),
    #                 attendance__employee=employee_id,is_requested=True,approved_status='pending').values_list('id',flat=True).distinct()
                
    #             for app_req_id in list(od_app_req_id):
    #                 total_grace_final = leave_calulate(employee_id,total_month_grace)
    #                 print("Inside loop od grace",total_grace_final)
    #                 duration_length=AttendanceApprovalRequest.objects.get(id=app_req_id,
    #                                                             is_requested=True).duration
    #                 if duration_length < 240:
    #                     if total_grace_final['cl_balance'] > 0.0:

    #                         update_auto = AttendanceApprovalRequest.objects.filter(id=app_req_id,is_late_conveyance=False,
    #                                                                 is_requested=True).\
    #                                                                     update(leave_type_changed_period='HD',leave_type_changed='CL',
    #                                                                     approved_status='approved',remarks='AUTO OD CONVERTED TO LEAVE & APPROVED')
    #                     elif total_grace_final['el_balance'] > 0.0:

    #                         update_auto = AttendanceApprovalRequest.objects.filter(id=app_req_id,is_late_conveyance=False,
    #                                                                 is_requested=True).\
    #                                                                     update(leave_type_changed_period='HD',leave_type_changed='EL',
    #                                                                     approved_status='approved',remarks='AUTO OD CONVERTED TO LEAVE & APPROVED')
    #                     else:

    #                         update_auto =AttendanceApprovalRequest.objects.filter(id=app_req_id,is_late_conveyance=False,
    #                                                                 is_requested=True).\
    #                                                                     update(leave_type_changed_period='HD',leave_type_changed='AB',
    #                                                                     approved_status='approved',remarks='AUTO OD CONVERTED TO LEAVE & APPROVED')
    #                 else:
    #                     if total_grace_final['cl_balance'] > 0.5:

    #                         update_auto =AttendanceApprovalRequest.objects.filter(id=app_req_id,is_late_conveyance=False,
    #                                                                 is_requested=True).\
    #                                                                     update(leave_type_changed_period='FD',leave_type_changed='CL',
    #                                                                     approved_status='approved',remarks='AUTO OD CONVERTED TO LEAVE & APPROVED')
    #                     elif total_grace_final['el_balance'] > 0.5:

    #                         update_auto = AttendanceApprovalRequest.objects.filter(id=app_req_id,is_late_conveyance=False,
    #                                                                 is_requested=True).\
    #                                                                     update(leave_type_changed_period='FD',leave_type_changed='EL',
    #                                                                     approved_status='approved',remarks='AUTO OD CONVERTED TO LEAVE & APPROVED')
    #                     else:

    #                         update_auto = AttendanceApprovalRequest.objects.filter(id=app_req_id,is_late_conveyance=False,
    #                                                                 is_requested=True).\
    #                                                                     update(leave_type_changed_period='FD',leave_type_changed='AB',
    #                                                                     approved_status='approved',remarks='AUTO OD CONVERTED TO LEAVE & APPROVED')                       
            
                
    #             total_grace_final2 = leave_calulate(employee_id,total_month_grace)
    #             print("after od leave calculate",total_grace_final2) 
    #             for att_id in list(attendence_ids):
    #                 total_grace_final2 = leave_calulate(employee_id,total_month_grace)
    #                 print("Inside loop not requested grace",total_grace_final2)
    #                 duration_length=AttendanceApprovalRequest.objects.filter(attendance=att_id,is_late_conveyance=False,
    #                                                             checkin_benchmark=False,is_requested=False).aggregate(Sum('duration'))['duration__sum']
    #                 print('duration_length',duration_length,'att_id',att_id)
    #                 if duration_length is not None and duration_length < 240:
    #                     if total_grace_final2['cl_balance'] > 0.0:

    #                         update_auto = AttendanceApprovalRequest.objects.filter(attendance=att_id,is_late_conveyance=False,
    #                                                                 checkin_benchmark=False,is_requested=False).\
    #                                                                     update(request_type='HD',leave_type='CL',justification='AUTO',is_requested=True,
    #                                                                     approved_status='approved',remarks='AUTO LEAVE APPROVED')
    #                     elif total_grace_final2['el_balance'] > 0.0:

    #                         update_auto = AttendanceApprovalRequest.objects.filter(attendance=att_id,is_late_conveyance=False,
    #                                                                 checkin_benchmark=False,is_requested=False).\
    #                                                                     update(request_type='HD',leave_type='EL',justification='AUTO',is_requested=True,
    #                                                                     approved_status='approved',remarks='AUTO LEAVE APPROVED')
    #                     else:

    #                         update_auto = AttendanceApprovalRequest.objects.filter(attendance=att_id,is_late_conveyance=False,
    #                                                                 checkin_benchmark=False,is_requested=False).\
    #                                                                     update(request_type='HD',leave_type='AB',justification='AUTO',is_requested=True,
    #                                                                     approved_status='approved',remarks='AUTO LEAVE APPROVED')
    #                 else:
    #                     if total_grace_final2['cl_balance'] > 0.5:

    #                         update_auto = AttendanceApprovalRequest.objects.filter(attendance=att_id,is_late_conveyance=False,
    #                                                                 checkin_benchmark=False,is_requested=False).\
    #                                                                     update(request_type='FD',leave_type='CL',justification='AUTO',is_requested=True,
    #                                                                     approved_status='approved',remarks='AUTO LEAVE APPROVED')
    #                     elif total_grace_final2['el_balance'] > 0.5:

    #                         update_auto = AttendanceApprovalRequest.objects.filter(attendance=att_id,is_late_conveyance=False,
    #                                                                 checkin_benchmark=False,is_requested=False).\
    #                                                                     update(request_type='FD',leave_type='EL',justification='AUTO',is_requested=True,
    #                                                                     approved_status='approved',remarks='AUTO LEAVE APPROVED')
    #                     else:

    #                         update_auto = AttendanceApprovalRequest.objects.filter(attendance=att_id,is_late_conveyance=False,
    #                                                                 checkin_benchmark=False,is_requested=False).\
    #                                                                     update(request_type='FD',leave_type='AB',justification='AUTO',is_requested=True,
    #                                                                     approved_status='approved',remarks='AUTO LEAVE APPROVED')                        
    #             #for checking
    #             total_grace_final2 = leave_calulate(employee_id,total_month_grace)
    #             print("after grace leave calculate",total_grace_final2) 
    #             auto_grace_approval =AttendanceApprovalRequest.objects.filter(attendance__employee=employee_id,
    #                                                                     is_requested=True,request_type='GR',approved_status='pending').\
    #                                                                         update(approved_status='approved',remarks='AUTO GRACE APPROVED')

    #             auto_misspunch_approval =AttendanceApprovalRequest.objects.filter(attendance__employee=employee_id,
    #                                                                     is_requested=True,request_type='MP',approved_status='pending').\
    #                                                                         update(approved_status='approved',remarks='AUTO MISSPUNCH APPROVED') 
                
    #         print("entered or noyt ")                                                                             
    #         lock=AttendanceApprovalRequest.objects.filter(attendance_date__gte=total_month_grace[0]['month_start__date'],
    #                                                 attendance_date__lte=total_month_grace[0]['month_end__date'],
    #                                                 is_deleted=False).\
    #                                                     update(lock_status=True)
    #         print("lock",lock)   

    #     return Response({})





class AttendanceUserSixDayLeaveCheck(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request, *args, **kwargs):
        from time import sleep
        logdin_user_id = self.request.user.id
        user_id = self.request.query_params.get('user_id', None)

        # current_date = self.request.query_params.get('current_date', None)
        # if current_date:
        #     today_datetime = datetime.strptime(current_date, "%Y-%m-%d")
        # else:
        #     today_datetime = datetime.now()
        # print("today_datetime",today_datetime, type(today_datetime))
        #sleep(2)
        
        start_date = self.request.query_params.get('start_date', None)
        sdate = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = self.request.query_params.get('end_date', None)
        edate = datetime.strptime(end_date, "%Y-%m-%d")

        # def last_day_of_month(self,sdate, edate):
        days_list = []
        user_list =  []
        # sdate = date(2008, 8, 15)   # start date
        # edate = date(2008, 9, 15)   # end date
        print("sdate",sdate   , edate)

        delta = edate - sdate       # as timedelta

        for i in range(delta.days + 1):
            day = sdate + timedelta(days=i)
            # print(day)
            days_list.append(day)
        # return days_list

        print("days_list",days_list)

        

        for today_datetime in days_list:
            date_time_day = today_datetime.date()
            print("date_time_day",date_time_day)
            # sleep(1)
            if user_id:
                user_details = TCoreUserDetail.objects.filter(cu_user_id=user_id).values()
            else:
                user_details = TCoreUserDetail.objects.filter(~Q(
                            (   
                                Q(cu_user__in=TMasterModuleRoleUser.objects.filter(
                                Q(mmr_type=1)|Q(mmr_type=6)|Q(mmr_is_deleted=True)).values_list('mmr_user',flat=True))
                            )|
                            (Q(cu_punch_id='#N/A'))#|
                            # (Q(cu_user_id__in=Attendance.objects.filter(date__date=date_time_day).values_list('employee',flat=True)))
                        ),
                        (
                            Q(
                                Q(termination_date__isnull=False)&Q(
                                    Q(
                                        Q(termination_date__year=today_datetime.year)&Q(termination_date__month=today_datetime.month)
                                    )|
                                    Q(termination_date__date__gte=date_time_day)
                                )
                            )|
                            Q(Q(termination_date__isnull=True))
                        ),
                        (Q(joining_date__date__lte=date_time_day)),cu_is_deleted=False).values() ##avoid 'PMSSITE000','#N/A' punch ids

            print('Total_user',len(user_details))
            #sleep(2)
            user_count = len(user_details)


            for user in user_details:
                print("len(user_details)", user_count,  user['cu_user_id'],  user['cu_punch_id'])
                user_count =user_count-1
                
                # print("user",user)
                date = today_datetime.date()
                cu_user = int(user['cu_user_id'])
                punch_id = user['cu_punch_id']
                # attendance_data = Attendance.objects.filter(date__date=date_time_day,employee=cu_user_id)#.values_list('employee',flat=True)
                is_absent = True
                # requested_list = []
                # not_requested_list = []
                count = 0
                attendance_dtl_list = []
                six_day_count = 0

                while is_absent is True:
                    #sleep(1)
                    # print("kjgjkgk",date, cu_user)
                    attendance_data = Attendance.objects.filter(date__date=date,employee=cu_user).values()
                    req_data = AttendanceApprovalRequest.objects.filter(((Q(leave_type_changed_period__isnull=False)&(Q(leave_type_changed_period='FD')))|
                                                                        (Q(leave_type_changed_period__isnull=True)&(Q(request_type='FD')))),
                                                                        attendance__employee=cu_user,is_requested=True,duration_start__date=date,punch_id=punch_id)
                    
                    not_requested_data = AttendanceApprovalRequest.objects.filter(attendance__employee=cu_user,is_requested=False,duration_start__date=date,punch_id=punch_id).count()
                    if attendance_data:
                        if attendance_data[0]["is_present"] is False:
                            if req_data:
                                is_absent = True
                                count += 1
                                # requested_list.append(date)
                                # print("req_data",req_data)
                                # six_day_count +=1
                            elif not_requested_data==0:
                                is_absent = True
                                count += 1
                                attendance_dtl_list.append(attendance_data[0])
                            else:
                                is_absent = False
                        elif attendance_data[0]["is_present"] is True:
                                print("_present")
                                is_absent = False
                    else:
                        print("No attendance")
                        is_absent = False
                    # if req_data:
                    #     is_absent = True
                    #     count += 1
                    #     # requested_list.append(date)
                    #     print("req_data",req_data)
                    #     six_day_count +=1
                    # else:
                    #     print("Not requested attendance")
                    #     if attendance_data:
                    #         print("not_requested_data",not_requested_data, type(not_requested_data))
                    #         if attendance_data[0]["is_present"] is True:
                    #             print("_present")
                    #             is_absent = False
                    #         elif attendance_data[0]["is_present"] is False and not_requested_data>0:
                    #             is_absent = False
                    #         elif attendance_data[0]["is_present"] is False and not_requested_data==0:
                    #             print("Absent")
                    #             is_absent = True
                    #             count += 1
                    #             attendance_dtl_list.append(attendance_data[0])
                    #             six_day_count +=1

                    #         else:
                    #             print("not_present")
                    #             is_absent = False
                    #     else:
                    #         print("Not requested")
                    #         is_absent = False

                    date = date - timedelta(days=1)
                    print("after while date",date, type(date))
                    print("six_day_count",six_day_count, count)
                    # sleep(2)

                # if six_day_count>6:
                #     user_list.append(user['cu_user_id'])
                #     print("attendance_dtl_listjsgfgsgf",attendance_dtl_list)
                if count>6 and len(attendance_dtl_list)>0:
                    #sleep(2)
                    print("attendance_dtl_list",attendance_dtl_list)
                    user_list.append(user['cu_user_id'])
                    for data in attendance_dtl_list:
                        print("data",data)

                        daily_login = datetime.combine(data['date'],user['daily_loginTime'])
                        daily_logout = datetime.combine(data['date'],user['daily_logoutTime'])
                        duration = round(((daily_logout-daily_login).seconds)/60)
                        AttendanceApprovalRequest.objects.get_or_create(attendance_id=data['id'],duration_start=daily_login,duration_end=daily_logout,
                                                                        duration=duration,attendance_date=daily_login.date(),punch_id=punch_id,
                                                                        created_by_id=logdin_user_id,owned_by_id=logdin_user_id)


        return Response({'result':{'request_status':1,'msg':'Successful','user_list':set(user_list)}})


class QueryPrint(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request, *args, **kwargs):
        data={}
        #WRITE QUERY SECTION##################################################################
        user_list = TMasterModuleRoleUser.objects.\
                    filter(
                        Q(mmr_type=3),Q(mmr_is_deleted=False),
                        Q(mmr_module__cm_name='ATTENDANCE & HRMS')).\
                        values_list('mmr_user',flat=True).distinct()
        q = TCoreUserDetail.objects.filter(cu_punch_id__isnull=False).values('cu_punch_id','cu_user')
        user = [x['cu_user']for x in q]
        for us in user :
            punch_id = q.filter(cu_user=us).values('cu_punch_id')
            query = AttendanceApprovalRequest.objects.filter(attendance__employee=us).update(punch_id=punch_id[0]['cu_punch_id'])
            print("query",query)
        ######################################################################################
        # query_output = raw_query_extract(query) #QUERY EXTRACTION FUNCTION raw_query_extract
        # print("query_output",query_output)
        data['Raw_query_result'] = str(query)
        return Response(data)


class EmailSMSAlertForRequestApproval(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = Attendance.objects.filter(is_deleted=False)
    serializer_class = EmailSMSAlertForRequestApprovalSerializer


    @response_with_status
    def get(self, request, *args, **kwargs):
        last_justification_date = self.request.query_params.get('last_justification_date', None)
        last_approval_date = self.request.query_params.get('last_approval_date', None)
        send_type = self.request.query_params.get('send_type', None)
        data = list()
        if last_justification_date:
            user_details, today_datetime, date_time_day = self.get_all_active_user()

            #::::::::::::::: For All User :::::::::::::::#
            reporting_head_set = set()
            if send_type == 'sms':
                print('user_details',user_details)
                for user in user_details:
                    
                    
                    kwargs['user'] = user
                    kwargs['emp_id'] = user.cu_user.id
                    kwargs['date_time_day'] = date_time_day
                    unjustified_attendance_requests, _ = self.get_unjustified_and_pending_attendance_request(request, *args, **kwargs)

                    #self.send_alert_to_all_employee(last_justification_date=last_justification_date, user=user, unjustified_attendance_requests=unjustified_attendance_requests)
                    if user.cu_alt_phone_no:
                        user_phone_no  = user.cu_alt_phone_no
                    else:
                        user_phone_no = user.cu_phone_no
                    
                    data.append({'user_id':user.cu_user.id, 'user_phone_no': user_phone_no,'len(unjustified_attendance_requests)':len(unjustified_attendance_requests)})

                    if user_phone_no and len(unjustified_attendance_requests):
                        unjustified_sms_alert_to_all_employee_task.delay(last_justification_date=last_justification_date, user_phone_no=user_phone_no, unjustified_attendance_requests=unjustified_attendance_requests)
                    # if user.cu_alt_email_id and len(unjustified_attendance_requests):
                    #     unjustified_mail_alert_to_all_employee_task.delay(last_justification_date=last_justification_date, user_email=user.cu_alt_email_id, unjustified_attendance_requests=unjustified_attendance_requests)
                    

                # print(reporting_head_set)
                #::::::::::::::: For Reporting Head :::::::::::::::#
                users_under_reporting_head_list = self.users_under_reporting_head(user_details)
                for reporting_head, users_under_reporting_head in users_under_reporting_head_list.items():
                    print('reporting_head:', reporting_head)
                    print('users_under_reporting_head:', users_under_reporting_head)

                    pending_approval_requests_list = list()
                    pending_dick = {'grace':0, 'half_day':0, 'full_day':0, 'mispunch':0, 'week_off':0, 'off_duty':0, 'conveyance':0, 'leave':0}
                    for user in users_under_reporting_head:
                        kwargs['user'] = user
                        kwargs['emp_id'] = user.cu_user.id
                        kwargs['date_time_day'] = date_time_day
                        _, pending_approval_requests = self.get_unjustified_and_pending_attendance_request(request, *args, **kwargs)
                        pending_approval_requests_list.extend(pending_approval_requests)
                        grace, half_day, full_day, mispunch, week_off, off_duty, conveyance, leave = self.get_pending_requests_and_leave_count(pending_approval_requests)
                        pending_dick['grace'] = pending_dick['grace'] + grace
                        pending_dick['half_day'] = pending_dick['half_day'] + half_day
                        pending_dick['full_day'] = pending_dick['full_day'] + full_day
                        pending_dick['mispunch'] = pending_dick['mispunch'] + mispunch
                        pending_dick['week_off'] = pending_dick['week_off'] + week_off
                        pending_dick['off_duty'] = pending_dick['off_duty'] + off_duty
                        pending_dick['conveyance'] = pending_dick['conveyance'] + conveyance
                        pending_dick['leave'] = pending_dick['leave'] + leave


                    pending_dick['reporting_head_phone'] = reporting_head.cu_alt_phone_no if reporting_head.cu_alt_phone_no else reporting_head.cu_phone_no
                    pending_dick['reporting_head_email'] = reporting_head.cu_alt_email_id if reporting_head.cu_alt_email_id else reporting_head.cu_user.email
                    pending_dick['pending_approval_requests'] = pending_approval_requests_list
                    pending_dick['last_approval_date'] = last_approval_date
                    # self.send_alert_to_reporting_head(**pending_dick)
                    if pending_dick['reporting_head_phone'] and len(pending_approval_requests_list):
                        pending_sms_alert_to_reporting_head.delay(**pending_dick)
                    # if reporting_head.cu_alt_email_id and len(pending_approval_requests_list):
                    #     pending_mail_alert_to_reporting_head.delay(**pending_dick)
                    
            
            if send_type == 'mail':
                for user in user_details:
                    
                    kwargs['user'] = user
                    kwargs['emp_id'] = user.cu_user.id
                    kwargs['date_time_day'] = date_time_day
                    unjustified_attendance_requests, _ = self.get_unjustified_and_pending_attendance_request(request, *args, **kwargs)

                    if user.cu_alt_email_id:
                        user_email = user.cu_alt_email_id
                    else:
                        user_email = user.cu_user.email
                    #self.send_alert_to_all_employee(last_justification_date=last_justification_date, user=user, unjustified_attendance_requests=unjustified_attendance_requests)
                    

                    # if user.cu_alt_phone_no and len(unjustified_attendance_requests):
                    #     unjustified_sms_alert_to_all_employee_task.delay(last_justification_date=last_justification_date, user_phone_no=user.cu_alt_phone_no, unjustified_attendance_requests=unjustified_attendance_requests)
                    if user_email and len(unjustified_attendance_requests):
                        data.append({'user_id':user.cu_user.id,'last_justification_date':last_justification_date ,'user_email': user_email, "len(unjustified_attendance_requests)":len(unjustified_attendance_requests)})
                        unjustified_mail_alert_to_all_employee_task.delay(last_justification_date=last_justification_date, user_email=user_email, unjustified_attendance_requests=unjustified_attendance_requests)
                    

                # print(reporting_head_set)
                #::::::::::::::: For Reporting Head :::::::::::::::#
                users_under_reporting_head_list = self.users_under_reporting_head(user_details)
                for reporting_head, users_under_reporting_head in users_under_reporting_head_list.items():
                    print('reporting_head:', reporting_head)
                    print('users_under_reporting_head:', users_under_reporting_head)

                    pending_approval_requests_list = list()
                    pending_dick = {'grace':0, 'half_day':0, 'full_day':0, 'mispunch':0, 'week_off':0, 'off_duty':0, 'conveyance':0, 'leave':0}
                    for user in users_under_reporting_head:
                        kwargs['user'] = user
                        kwargs['emp_id'] = user.cu_user.id
                        kwargs['date_time_day'] = date_time_day
                        _, pending_approval_requests = self.get_unjustified_and_pending_attendance_request(request, *args, **kwargs)
                        pending_approval_requests_list.extend(pending_approval_requests)
                        grace, half_day, full_day, mispunch, week_off, off_duty, conveyance, leave = self.get_pending_requests_and_leave_count(pending_approval_requests)
                        pending_dick['grace'] = pending_dick['grace'] + grace
                        pending_dick['half_day'] = pending_dick['half_day'] + half_day
                        pending_dick['full_day'] = pending_dick['full_day'] + full_day
                        pending_dick['mispunch'] = pending_dick['mispunch'] + mispunch
                        pending_dick['week_off'] = pending_dick['week_off'] + week_off
                        pending_dick['off_duty'] = pending_dick['off_duty'] + off_duty
                        pending_dick['conveyance'] = pending_dick['conveyance'] + conveyance
                        pending_dick['leave'] = pending_dick['leave'] + leave

                    pending_dick['reporting_head_phone'] = reporting_head.cu_alt_phone_no if reporting_head.cu_alt_phone_no else reporting_head.cu_phone_no
                    pending_dick['reporting_head_email'] = reporting_head.cu_alt_email_id if reporting_head.cu_alt_email_id else reporting_head.cu_user.email
                    pending_dick['pending_approval_requests'] = pending_approval_requests_list
                    pending_dick['last_approval_date'] = last_approval_date
                    # self.send_alert_to_reporting_head(**pending_dick)
                    # if reporting_head.cu_alt_phone_no and len(pending_approval_requests_list):
                    #     pending_sms_alert_to_reporting_head.delay(**pending_dick)
                    if pending_dick['reporting_head_email'] and len(pending_approval_requests_list):
                        pending_mail_alert_to_reporting_head.delay(**pending_dick)
                    
        return data

    def get_pending_requests_and_leave_count(self,pending_approval_requests):
        grace = len(list(filter(lambda x: (x['is_requested'] and x['approved_status'] == 'pending' and x['request_type'] == 'GR'), pending_approval_requests)))
        half_day = len(list(filter(lambda x: (x['is_requested'] and x['approved_status'] == 'pending' and x['request_type'] == 'HD'), pending_approval_requests)))
        full_day = len(list(filter(lambda x: (x['is_requested'] and x['approved_status'] == 'pending' and x['request_type'] == 'FD'), pending_approval_requests)))
        mispunch = len(list(filter(lambda x: (x['is_requested'] and x['approved_status'] == 'pending' and x['request_type'] == 'MP'), pending_approval_requests)))
        week_off = len(list(filter(lambda x: (x['is_requested'] and x['approved_status'] == 'pending' and x['request_type'] == 'WO'), pending_approval_requests)))
        off_duty = len(list(filter(lambda x: (x['is_requested'] and x['approved_status'] == 'pending' and (x['request_type'] == 'OD' or x['request_type'] == 'FOD' or x['request_type'] == 'POD')), pending_approval_requests)))
        conveyance = len(list(filter(lambda x: (x['is_requested'] and x['approved_status'] == 'pending' and (x['is_late_conveyance'] or x['is_conveyance'])), pending_approval_requests)))
        leave = len(list(filter(lambda x: (x['is_requested'] and x['approved_status'] == 'pending' and (x['leave_type'] == 'EL' or x['leave_type'] == 'CL' or x['leave_type'] == 'SL')), pending_approval_requests)))
        return grace, half_day, full_day, mispunch, week_off, off_duty, conveyance, leave

    def users_under_reporting_head(self,user_details):
        users_under_reporting_head_list = collections.defaultdict(set)
        for user in user_details:
            if user.reporting_head:
                users_under_reporting_head_list[TCoreUserDetail.objects.get(cu_user=user.reporting_head)].add(user)
        return users_under_reporting_head_list

    def get_all_active_user(self):
        today_datetime = datetime.now()
        date_time_day = today_datetime.date()
        user_details = TCoreUserDetail.objects.filter(~Q(
                (   
                    Q(cu_user__in=TMasterModuleRoleUser.objects.filter(
                    Q(mmr_type=1)|Q(mmr_type=6)|Q(mmr_is_deleted=True)).values_list('mmr_user',flat=True))
                )|
                (Q(cu_punch_id='#N/A'))|
                (Q(cu_user_id__in=Attendance.objects.filter(date__date=date_time_day).values_list('employee',flat=True)))
            ),
            (
                Q(
                    Q(termination_date__isnull=False)&Q(
                        Q(
                            Q(termination_date__year=today_datetime.year)&Q(termination_date__month=today_datetime.month)
                        )|
                        Q(termination_date__date__gte=date_time_day)
                    )
                )|
                Q(Q(termination_date__isnull=True))
            ),
            (Q(user_type__in=('User','Housekeeper'))),
            # (Q(cu_user_id='3187')),
            (Q(joining_date__date__lte=date_time_day)),cu_is_deleted=False)

        
        print('Total_user',len(user_details))
        return user_details, today_datetime, date_time_day

    def get_unjustified_and_pending_attendance_request(self, request, *args, **kwargs):
        # print('kwargs:',kwargs)
        self.request.query_params._mutable = True
        self.request.query_params['emp_id'] = kwargs['emp_id']
        self.request.query_params['current_date'] = '2020-02-25' #str(kwargs['date_time_day']) # '2019-12-21'
        self.request.query_params['is_previous'] = False
        self.request.query_params._mutable = False
        
        response = self.get_justifiable_requests(request, args, kwargs)
        request_approval_daily_list = response.data
        filtered_attendance_requests = list()
        for arl in request_approval_daily_list:
            if len(arl['attendance_request']):
                filtered_attendance_requests.extend(arl['attendance_request'])
        #print('User:',kwargs['user'].cu_user.id)
        #print('len of requests approval:', len(filtered_attendance_requests))

        unjustified_attendance_requests = list(filter(lambda x: not x['is_requested'] , filtered_attendance_requests))
        print('len of unjustified requests approval:', len(unjustified_attendance_requests))

        pending_approval_requests = list(filter(lambda x: (x['is_requested'] and x['approved_status'] == 'pending'), filtered_attendance_requests))
        print('len of pending requests approval:', len(pending_approval_requests))
        
        return unjustified_attendance_requests, pending_approval_requests

    def send_alert_to_all_employee(self, *args, **kwargs):
        #print('all_employee_mail_kwargs:', kwargs)
        last_justification_date = kwargs['last_justification_date']
        user = kwargs['user']
        unjustified_attendance_requests = kwargs['unjustified_attendance_requests']
        '''
            Description: Sms alert for all employees for unjustified request(Grace, HD, FD, MM, etc.).
            Name: Unjustified Request Alert For Employees
            Code: URAFE
            Subject: Alert!!! Unjustified Requests
            Txt content:
                You have total {{ unjustified_attendance_requests }} unjustified requests left. Please justify your attendance deviation 
                with a proper remarks before {{ last_justification_date }}.
            Contain variable:  unjustified_attendance_requests, last_justification_date
        '''
        
        if user.cu_alt_phone_no and len(unjustified_attendance_requests):
            message_data = {
                'unjustified_attendance_requests': unjustified_attendance_requests,
                'last_justification_date': last_justification_date
            }
            
            sms_class = GlobleSmsSendTxtLocal('URAFE',[user.cu_alt_phone_no])
            print('sms_class:',sms_class)
            print('user.cu_alt_phone_no:', user.cu_alt_phone_no)
            unjustified_sms_alert_to_all_employee_task.delay(sms_class=sms_class)
            
            # sms_thread = Thread(target = sms_class.sendSMS, args = (message_data,'sms'))
            # sms_thread.start()

        '''
            Description: Mail alert for all employees for unjustified request(Grace, HD, FD, MM, etc.).
            Name: Unjustified Request Alert For Employees
            Code: URAFE
            Subject: Alert!!! Unjustified Requests
            Html content: 
                You have total {{ unjustified_attendance_requests }} unjustified requests left. Please justify your attendance 
                deviation with a proper remarks before {{ last_justification_date }}.

                Date            Duration Deviation(minutes)
                2019-12-19      34
                2019-12-21      78

            Template variable: unjustified_attendance_requests, last_justification_date
        '''
        
        if user.cu_alt_email_id and len(unjustified_attendance_requests):
            mail_data = {
                'last_justification_date': last_justification_date,
                'unjustified_attendance_requests': unjustified_attendance_requests
            }
            mail_class = GlobleMailSend('URAFE', [user.cu_alt_email_id])
            print('mail_class:', mail_class)
            print('user.cu_alt_email_id', user.cu_alt_email_id)
            
            # mail_thread = Thread(target = mail_class.mailsend, args = (mail_data,))
            # mail_thread.start()
            
        
        return

    def send_alert_to_reporting_head(self, *args, **kwargs):
        print('reporting_mail_kwargs:', kwargs)
        reporting_head = kwargs['reporting_head']
        pending_approval_requests = kwargs['pending_approval_requests']
        last_approval_date = kwargs['last_approval_date']
        half_day = kwargs['half_day']
        full_day = kwargs['full_day']
        grace = kwargs['grace']
        mispunch = kwargs['mispunch']
        week_off = kwargs['week_off']
        off_duty = kwargs['off_duty']
        conveyance = kwargs['conveyance']
        leave = kwargs['leave']
        print('pending_approval_requests length:',len(pending_approval_requests))

        '''
        Description: 
            Sms alert for Reporting Head to approve/reject/release the pending requests(Grace, HD, FD, MM, etc.) 
            requested by team members.
        Name: Pending Approval Request Alert For  Reporting Head
        Code: PRAAFRH
        Subject: Alert!!! Pending Approval Request
        Txt content:
            You have total {{ pending_approval_requests }} pending approval requests left of your team members. 
            Please approve/reject/release the pending request from team attendance with a proper remarks before {{ last_approval_date }}.
        Contain variable:  pending_approval_requests, last_approval_date
        '''
        
        if reporting_head.cu_alt_phone_no and len(pending_approval_requests):
            message_data = {
                'pending_approval_requests': pending_approval_requests,
                'last_approval_date': last_approval_date
            }
            sms_class = GlobleSmsSendTxtLocal('PRAAFRH',[reporting_head.cu_alt_phone_no])
            print('sms_class:',sms_class)
            print('reporting_head.cu_alt_phone_no:', reporting_head.cu_alt_phone_no)
            
            # sms_thread = Thread(target = sms_class.sendSMS, args = (message_data,'sms'))
            # sms_thread.start()
            

        '''
        Description: 
            Mail alert for Reporting Head to approve/reject/release the pending requests(Grace, HD, FD, MM, etc.) 
            requested by team members.
        Name: Pending Approval Request Alert For  Reporting Head
        Code: PRAAFRH
        Subject: Alert!!! Pending Approval Request
        Html content: 
            You have total {{ pending_approval_requests }} pending approval requests left of your team members. 
            Please approve/reject/release the pending request from team attendance with a proper remarks before {{ last_approval_date }}.

            Total requests		{{ pending_approval_requests }}
            Half Day			{{ half_day }}
            Full Day			{{ full_day }}
            Grace				{{ grace }}
            Mispunch			{{ mispunch }}
            Week Off			{{ week_off }}
            Off Duty			{{ off_duty }}
            Conveyance		    {{ conveyance }}
            Leave		        {{ leave }}

        Template variable: pending_approval_requests, last_approval_date, half_day,  full_day, grace, mispunch, week_off, off_duty, conveyance, leave
        '''
        
        if reporting_head.cu_alt_email_id and len(pending_approval_requests):
            mail_data = {
                'pending_approval_requests': pending_approval_requests,
                'last_approval_date': last_approval_date,
                'half_day': half_day,
                'full_day': full_day,
                'grace': grace,
                'mispunch': mispunch,
                'week_off': week_off,
                'off_duty': off_duty,
                'conveyance': conveyance,
                'leave': leave
            }
            mail_class = GlobleMailSend('PRAAFRH', [reporting_head.cu_alt_email_id])
            print('mail_class:', mail_class)
            print('reporting_head.cu_alt_email_id:', reporting_head.cu_alt_email_id)
            
            # mail_thread = Thread(target = mail_class.mailsend, args = (mail_data,))
            # mail_thread.start()
            
        
        return

    def get_queryset(self):
        emp_id = self.request.query_params.get('emp_id', None)
        current_date = self.request.query_params.get('current_date', None)
        month = self.request.query_params.get('month', None)
        year = self.request.query_params.get('year', None)
        is_previous = self.request.query_params.get('is_previous', None)
        joining_date = None
        filter = {}
        date_range = None

        if self.queryset.count():
            if emp_id:
                filter['employee']=emp_id
                joining_date = TCoreUserDetail.objects.get(cu_user=emp_id).joining_date.date()
            if current_date:
                date = datetime.strptime(current_date, "%Y-%m-%d")
                date_range = AttendenceMonthMaster.objects.filter(month_start__date__lte=date,month_end__date__gte=date).values('month_start__date','month_end__date')
                self.date_range_str = date_range[0]['month_start__date']
                self.date_range_end = date.date()

                if is_previous == 'true':
                    # print("is_previous",is_previous)
                    date = date_range[0]['month_start__date'] - timedelta(days=1)
                    # print("date",date)
                    date_range = AttendenceMonthMaster.objects.filter(month_start__date__lte=date,month_end__date__gte=date).values('month_start__date','month_end__date')
                    # print("is_previous_date_range",date_range)
                    self.date_range_str = date_range[0]['month_start__date']
                    self.date_range_end = date_range[0]['month_end__date']
                # print("date_range",date_range)
            elif month and year:
                date_range = AttendenceMonthMaster.objects.filter(month=month,month_end__year=year).values('month_start__date','month_end__date')
                # print("date_range",date_range)
            
            # print("elf.date_range",date_range)
            if date_range:
                filter['date__date__gte'] = date_range[0]['month_start__date']
                filter['date__date__lte'] = date_range[0]['month_end__date']
            if filter:
                return self.queryset.filter(**filter)
            else:
                return self.queryset
        else:
            # print("ELLSSS", self.queryset)
            return self.queryset.filter(is_deleted=False)

    def get_justifiable_requests(self, request, *args, **kwargs):
        response=super(EmailSMSAlertForRequestApproval,self).get(self, request, args, kwargs)
        emp_id = self.request.query_params.get('emp_id', None)
        # print("response.data['results']",response.data)
        attendance_request_dict = {}
        date_list_data = []

        for data in response.data:
            is_attendance_request = True
            is_late_conveyance = False
            is_late_conveyance_completed = False
            late_conveyance_id = None
          
            # print(self.last_day_of_month(datetime.date(datetime.now().year,datetime.now().month, 1)))
            # print(datetime.now().year)
            date_list_data.append(datetime.strptime(data['date'], "%Y-%m-%dT%H:%M:%S").date())
            
            attendance_request = AttendanceApprovalRequest.objects.filter(attendance=data['id'],is_deleted=False)
            # print("attendance_request",attendance_request)
            attendance_request_list = []
            # print("data",data)
            day_remarks = None
            for att_req in attendance_request:
                if att_req.leave_type_changed is not None:
                    day_remarks = 'Leave ('+att_req.leave_type_changed+')'
                elif att_req.leave_type_changed is None and att_req.leave_type is not None:
                    day_remarks = 'Leave ('+att_req.leave_type+')'
                elif att_req.approved_status=='approved' and att_req.request_type =='FOD':
                    day_remarks = 'OD'

                if att_req.is_late_conveyance == True:
                    is_late_conveyance = True
                    late_conveyance_id = att_req.id
                if att_req.vehicle_type and att_req.from_place and att_req.to_place and att_req.conveyance_expense and att_req.is_late_conveyance == True:
                    is_late_conveyance_completed = True

                if att_req.is_late_conveyance==False and att_req.checkin_benchmark==False:
                    if att_req.approved_status == 'relese' or att_req.is_requested == False:
                        is_attendance_request = False
                    attendance_request_dict = {
                        'id' : att_req.id,
                        'duration_start' : att_req.duration_start,
                        'duration_end' : att_req.duration_end,
                        'duration' : att_req.duration,
                        'request_type' : att_req.leave_type_changed_period if att_req.leave_type_changed_period else att_req.request_type,
                        'is_requested' : att_req.is_requested,
                        'request_date' : att_req.request_date,
                        'justification' : att_req.justification,
                        'approved_status' : att_req.approved_status,
                        'remarks' : att_req.remarks,
                        'justified_by' : att_req.justified_by_id,
                        'justified_at' : att_req.justified_at,
                        'approved_by' : att_req.approved_by_id,
                        'approved_at' : att_req.approved_at,
                        'leave_type' : att_req.leave_type_changed if att_req.leave_type_changed else att_req.leave_type,
                        'is_late_conveyance' : att_req.is_late_conveyance,
                        'vehicle_type' : att_req.vehicle_type.name if att_req.vehicle_type else '',
                        'vehicle_type_id' : att_req.vehicle_type.id if att_req.vehicle_type else '',
                        'is_conveyance' : att_req.is_conveyance,
                        'from_place' : att_req.from_place,
                        'to_place' : att_req.to_place,
                        'conveyance_expense' : att_req.conveyance_expense,
                        'approved_expenses' : att_req.approved_expenses,
                        'conveyance_remarks' : att_req.conveyance_remarks,
                        'leave_type_changed' : att_req.leave_type_changed,
                        'leave_type_changed_period' : att_req.leave_type_changed_period,
                        'checkin_benchmark' : att_req.checkin_benchmark,
                        'lock_status' : att_req.lock_status,
                        'conveyance_purpose' : att_req.conveyance_purpose,
                        'conveyance_alloted_by' : att_req.conveyance_alloted_by.id if att_req.conveyance_alloted_by else '',
                        'conveyance_alloted_by_name' : (att_req.conveyance_alloted_by.first_name if att_req.conveyance_alloted_by else '') + " " +(att_req.conveyance_alloted_by.last_name if att_req.conveyance_alloted_by else '')
                    }                  

                    attendance_request_list.append(attendance_request_dict)
            data['attendance_request'] = attendance_request_list
            data['is_late_conveyance'] = is_late_conveyance
            data['late_conveyance_id'] = late_conveyance_id
            data['is_late_conveyance_completed'] = is_late_conveyance_completed
            data['is_attendance_request'] = is_attendance_request
            if day_remarks:
                data['day_remarks'] = day_remarks

        # if response.data:
        day_list = self.last_day_of_month(self.date_range_str,self.date_range_end)
        # print("date_list_data",date_list_data)
        joining_date = None
        joining_date = TCoreUserDetail.objects.only('joining_date').get(cu_user=emp_id).joining_date.date()
        new_dict = {}
        for day in day_list:
            if day not in date_list_data:
                # print("day", day)
                new_dict={
                    'id' : None,
                    'date' : day.strftime("%Y-%m-%dT%H:%M:%S"),
                    'is_present' : False,
                    "is_attendance_request": False,
                    "day_remarks": "Absent",
                    "attendance_request":[],
                    "is_late_conveyance":False,
                    "is_late_conveyance_completed":False,
                    "is_deleted":False,
                    "login_time": "",
                    "logout_time": ""
                    }
                if joining_date:
                    if joining_date > day:
                        new_dict['day_remarks']="Not Joined"
                    # elif joining_date == day:
                    #     new_dict['day_remarks']="Joining date"
                    
                response.data.append(new_dict)

        response.data = self.list_synchronization(list(response.data))

        return response
    
    def last_day_of_month(self,sdate, edate):
        days_list = []
        # sdate = date(2008, 8, 15)   # start date
        # edate = date(2008, 9, 15)   # end date
        print("sdate",sdate   , edate)

        delta = edate - sdate       # as timedelta

        for i in range(delta.days + 1):
            day = sdate + timedelta(days=i)
            # print(day)
            days_list.append(day)
        return days_list

    def list_synchronization(self, list_data: list)-> list:
        data = pd.DataFrame(list_data)
        data = data.replace(np.nan, 0, regex=True)
        data.sort_values("date", axis = 0, ascending = True, inplace = True,)
        col_list = data.columns.values
        row_list = data.values.tolist()
        total_result = list()
        for row in row_list:
            data_dict = dict(zip(col_list,row))
            total_result.append(data_dict)
        list_data = total_result
        return list_data


class CwsReportView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = Attendance.objects.filter(is_deleted=False)
    serializer_class = CwsReportSerializer

    @response_with_status
    def get(self, request, *args, **kwargs):
        data = list()

        return data

    def get_queryset(self):
        queryset = self.get_queryset()
        return queryset

    def get_cws_user(self):
        today_datetime = datetime.now()
        date_time_day = today_datetime.date()
        user_details = TCoreUserDetail.objects.filter(~Q(
                (   
                    Q(cu_user__in=TMasterModuleRoleUser.objects.filter(
                    Q(mmr_type=1)|Q(mmr_type=6)|Q(mmr_is_deleted=True)).values_list('mmr_user',flat=True))
                )|
                (Q(cu_punch_id='#N/A'))|
                (Q(cu_user_id__in=Attendance.objects.filter(date__date=date_time_day).values_list('employee',flat=True)))
            ),
            (
                Q(
                    Q(termination_date__isnull=False)&Q(
                        Q(
                            Q(termination_date__year=today_datetime.year)&Q(termination_date__month=today_datetime.month)
                        )|
                        Q(termination_date__date__gte=date_time_day)
                    )
                )|
                Q(Q(termination_date__isnull=True))
            ),
            (Q(user_type='Housekeeper')),
            (Q(joining_date__date__lte=date_time_day)),cu_is_deleted=False)
        return user_details, today_datetime, date_time_day

class AttendanceUsers(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request, *args, **kwargs):
        user_details=TMasterModuleRoleUser.objects.\
                        filter(
                            Q(mmr_user__in=(TCoreUserDetail.objects.filter(~Q(cu_punch_id='#N/A'),user_type__in=('User','Housekeeper'),cu_is_deleted=False).values_list('cu_user',flat=True))),
                            Q(mmr_type=3),
                            Q(mmr_is_deleted=False),
                            Q(mmr_module__cm_name='ATTENDANCE & HRMS')).values_list('mmr_user',flat=True).distinct()
            
        print('user_details',len(user_details))
        return Response({'user_length':len(user_details)})

    