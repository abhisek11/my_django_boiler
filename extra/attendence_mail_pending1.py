from global_function import userdetails
from attendance.models import *
from datetime import date,time
from datetime import datetime,timedelta
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from etask.models import *
from django.contrib.auth.models import *
from django.db import transaction, IntegrityError
from drf_extra_fields.fields import Base64ImageField
import os
from custom_exception_message import *
from mailsend.views import *
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from users.models import TCoreUserDetail
from smssend.views import *
from threading import Thread
from django.db.models import When, Case, Value, CharField, IntegerField, F, Q

def my_attendence_mail_before_lock_job():
  current_date = datetime.now().date()
  total_month_grace=AttendenceMonthMaster.objects.filter(month_start__date__lte=current_date,
                                        month_end__date__gte=current_date,is_deleted=False).\
                                            values('lock_date__date'
                                        ,'year_start_date','year_end_date','month','month_start__date',
                                        'month_end__date','pending_action_mail__date')
  print("total_month_grace",total_month_grace)
  days_cnt = (total_month_grace[0]['lock_date__date'] - total_month_grace[0]['pending_action_mail__date']).days
#   days=['20','21','22']
  date_generated = [total_month_grace[0]['pending_action_mail__date'] + timedelta(days=x) for x in range(0,days_cnt+1)]

  print("date_day",date_generated)
  if current_date in date_generated:
    print("entered",current_date)
    #local
    user_mail_list=AttendanceApprovalRequest.objects.filter(attendance_date__gte=total_month_grace[0]['month_start__date'],
                                                  attendance_date__lte=total_month_grace[0]['month_end__date'],
                                                  is_deleted=False,is_requested=False,approved_status='regular')\
                                                    .values_list('attendance__employee__email',flat=True).distinct()
    # # live
    # user_mail_list=AttendanceApprovalRequest.objects.filter(attendance_date__gte=total_month_grace[0]['month_start__date'],
    #                                               attendance_date__lte=total_month_grace[0]['month_end__date'],
    #                                               is_deleted=False,is_requested=False,approved_status='regular',attendance__employee=2316,attendance=424636)\
    #                                                 .values_list('attendance__employee__email',flat=True).distinct()
    print("user_mail_list",user_mail_list)
    # ============= Mail Send Step ==============#
    # email = email_list
    # email_list = ['bubai.das@shyamfuture.com','rupam@shyamfuture.com','koushik.goswami@shyamfuture.com']
    # email_admin= 'abhishekrock94@shyamfuture.com'
    print("email",list(user_mail_list))
    
    if user_mail_list:
        # for email in email_list:
        mail_data = {
          'name':None
        }
        print('mail_data',mail_data)
        mail_class = GlobleMailSend('ATP-PM', list(user_mail_list))
        print('mail_class',mail_class)
        mail_thread = Thread(target = mail_class.mailsend, args = (mail_data,None))
        mail_thread.start()
    
    #===============================================#


    return True