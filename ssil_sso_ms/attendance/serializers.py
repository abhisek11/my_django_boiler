from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from attendance.models import *
from django.contrib.auth.models import *
from django.db import transaction, IntegrityError
from drf_extra_fields.fields import Base64ImageField
import os
from holidays.models import * 
# import datetime
from django.db.models import Q
from datetime import datetime,timedelta
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from users.models import TCoreUserDetail
from smssend.views import *
from threading import Thread
from attendance.views import *
from django.db.models import Sum
from custom_exception_message import *
from django.db.models import Q
import calendar
from django.db.models import When, Case, Value, CharField, IntegerField, F, Q
from datetime import date,time
from hrms.models import *
from global_function import userdetails,department,designation
from master.models import *
from core.models import *
from attendance import logger

from mailsend.views import *
from smssend.views import *
from threading import Thread



#GLOBAL GRACE FUNCTION

# def GraceCalculation()

#:::::::::::::::::::::: DEVICE MASTER:::::::::::::::::::::::::::#
class DeviceMasterAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = DeviceMaster
        fields = ('id', 'device_no', 'device_name', 'is_exit', 'created_by', 'owned_by')

class DeviceMasterEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = DeviceMaster
        fields = ('id', 'device_no', 'device_name', 'is_exit', 'updated_by')

class DeviceMasterDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = DeviceMaster
        fields = '__all__'
    def update(self, instance, validated_data):
        instance.is_deleted=True
        instance.updated_by = validated_data.get('updated_by')
        instance.save()
        return instance

#:::::::::::::::::::::: ATTENDENCE MONTH MASTER:::::::::::::::::::::::::::#
class AttendenceMonthMasterAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = AttendenceMonthMaster
        fields = ('id', 'year_start_date', 'year_end_date', 'month', 'month_start', 'month_end',
        'lock_date','pending_action_mail','grace_available', 'created_by', 'owned_by')

class AttendenceMonthMasterEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = AttendenceMonthMaster
        fields = ('id', 'year_start_date', 'year_end_date', 'month', 'month_start', 'month_end', 'grace_available', 
        'lock_date','pending_action_mail','updated_by')

class AttendenceMonthMasterDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = AttendenceMonthMaster
        fields = '__all__'
    def update(self, instance, validated_data):
        instance.is_deleted=True
        instance.updated_by = validated_data.get('updated_by')
        instance.save()
        return instance

class AttendencePerDayDocumentAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = AttandancePerDayDocuments
        fields = '__all__'

class AttendenceApprovalRequestEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    # attendence_approvals=serializers.ListField(required=False)

    class Meta:
        model = AttendanceApprovalRequest
        fields = ('__all__')
        # extra_fields=('attendence_approvals')

    def update(self,instance, validated_data):
        # print("instance",instance)
        updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
        
        try:
            updated_by = validated_data.get('updated_by')
            date =self.context['request'].query_params.get('date', None)
            print('date',type(date))
            #################################################################################
            #if you find error in datetime please remove only datetime from "date_object"   #
            #################################################################################
            date_object = datetime.datetime.strptime(date, '%Y-%m-%d').date()
            print('date_object',type(date_object))
            employee_id=self.context['request'].query_params.get('employee_id', None)
            total_grace={}
            data_dict = {}
            with transaction.atomic():
                request_type=validated_data.get('request_type') if validated_data.get('request_type') else ""
                present=AttendanceApprovalRequest.objects.filter(id=instance.id,
                    attendance__is_present=True)
                total_month_grace=AttendenceMonthMaster.objects.filter(month_start__date__lte=date_object,
                                                    month_end__date__gte=date_object,is_deleted=False).values('grace_available',
                                                                                            'year_start_date',
                                                                                            'year_end_date',
                                                                                            'month',
                                                                                            'month_start',
                                                                                            'month_end'
                                                                                            )
                #REQUEST ONLY IF PRESENT AND HAVE DIVIATION
                if present:


                    availed_grace=AttendanceApprovalRequest.objects.filter(Q(attendance__employee=employee_id) &
                                                            Q(duration_start__gte=total_month_grace[0]['month_start']) &
                                                            Q(duration_start__lte=total_month_grace[0]['month_end']) &
                                                            Q(is_requested=True) &
                                                            Q(is_deleted=False)&
                                                            (Q(request_type='GR')|Q(checkin_benchmark=True))
                                                            ).aggregate(Sum('duration'))['duration__sum']
                    
                    print("availed_grace first 1 ",availed_grace)
                    
                    #*****************Request for Grace************************************************************************************
                    print("total_month_grace",total_month_grace)
                    if request_type == 'GR':
                        worst_late_beanchmark=TCoreUserDetail.objects.get(cu_user=employee_id).worst_late
                        print("worst_late_beanchmark",worst_late_beanchmark)

                        duration_start_end=AttendanceApprovalRequest.objects.get(id=instance.id)
                        print("duration_start_end",duration_start_end)
                        core_user_detail=TCoreUserDetail.objects.filter(cu_user=employee_id,cu_is_deleted=False).values('joining_date')
                        print('core_user_detail',core_user_detail)
                        if core_user_detail:
                            if core_user_detail[0]['joining_date']>total_month_grace[0]['year_start_date']:
                                joining_grace=JoiningApprovedLeave.objects.filter(employee=employee_id,is_deleted=False).values('cl',
                                                                                                                                'el',
                                                                                                                                'sl',
                                                                                                                                'year',
                                                                                                                                'month',
                                                                                                                                'first_grace' )

                                if total_month_grace[0]['month']==joining_grace[0]['month']:    #for joining month only
                                    total_grace['total_month_grace']=joining_grace[0]['first_grace']
                                    total_grace['month_start']=core_user_detail[0]['joining_date']

                                    duration_length=AttendanceApprovalRequest.objects.get(id=instance.id,checkin_benchmark=False,is_requested=False)
                                    # if duration_length.duration < 240:
                                    if duration_length.duration <= 150:
                                    # total_grace['grace_balance']=total_grace['total_month_grace'] - availed_grace
                                        if availed_grace is None:
                                            availed_grace=0.0
                                        if (total_grace['total_month_grace']-(float(availed_grace)+float(duration_length.duration))) >= 0.0 :
                                        
                                            justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,checkin_benchmark=False,is_requested=False).\
                                                update(
                                                request_type=request_type,
                                                is_requested=True,
                                                approved_status='pending',
                                                request_date=datetime.date.today(),
                                                justified_at=datetime.date.today(),
                                                justification=validated_data.get('justification'),
                                                justified_by=updated_by)

                                            return validated_data
                                        else:
                                            # raise serializers.ValidationError("Grace limit exceeds")
                                            custom_exception_message(self,None,"Grace limit exceeds")
                                    elif duration_length.duration >150 and duration_length.duration <=240:
                                        # raise serializers.ValidationError("Please apply half day Your diviation exceeds 2.5 Hours")
                                        custom_exception_message(self,None,"Please apply half day Your diviation exceeds 2.5 Hours")
                                    elif duration_length.duration > 240 :
                                        if (duration_start_end.duration_start.time() and duration_start_end.duration_end.time()) < worst_late_beanchmark:
                                            custom_exception_message(self,None,"Please apply half day Your diviation exceeds 2.5 Hours")
                                        elif duration_start_end.duration_start.time() < worst_late_beanchmark and duration_start_end.duration_end.time() > worst_late_beanchmark:
                                            custom_exception_message(self,None,"Please apply full day Your diviation exceeds 4 Hours")
                                        elif (duration_start_end.duration_start.time() and duration_start_end.duration_end.time()) > worst_late_beanchmark:
                                            custom_exception_message(self,None,"Please apply half day Your diviation exceeds 2.5 Hours")
                                        
                                else:
                                    total_grace['total_month_grace']=float(total_month_grace[0]['grace_available']) if float(total_month_grace[0]['grace_available']) else 0.0
                                    duration_length=AttendanceApprovalRequest.objects.get(id=instance.id,checkin_benchmark=False,is_requested=False)
                                    print('availed_grace12333',availed_grace)
                                    if duration_length.duration <= 150:
                                    # total_grace['grace_balance']=total_grace['total_month_grace'] - availed_grace
                                        if availed_grace is None:
                                            availed_grace=0.0
                                        if (total_grace['total_month_grace']-(float(availed_grace)+float(duration_length.duration))) >= 0.0 :
                                        
                                            justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,checkin_benchmark=False,is_requested=False).\
                                                update(
                                                request_type=request_type,
                                                is_requested=True,
                                                approved_status='pending',
                                                request_date=datetime.date.today(),
                                                justified_at=datetime.date.today(),
                                                justification=validated_data.get('justification'),
                                                justified_by=updated_by)

                                            return validated_data
                                        else:
                                            # raise serializers.ValidationError("Grace limit exceeds")
                                            custom_exception_message(self,None,"Grace limit exceeds")
                                    elif duration_length.duration >150 and duration_length.duration <=240:
                                        # raise serializers.ValidationError("Please apply half day Your diviation exceeds 2.5 Hours")
                                        custom_exception_message(self,None,"Please apply half day Your diviation exceeds 2.5 Hours")
                                    elif duration_length.duration > 240 :
                                        if (duration_start_end.duration_start.time() and duration_start_end.duration_end.time()) < worst_late_beanchmark:
                                            custom_exception_message(self,None,"Please apply half day Your diviation exceeds 2.5 Hours")
                                        elif duration_start_end.duration_start.time() < worst_late_beanchmark and duration_start_end.duration_end.time() > worst_late_beanchmark:
                                            custom_exception_message(self,None,"Please apply full day Your diviation exceeds 4 Hours")
                                        elif (duration_start_end.duration_start.time() and duration_start_end.duration_end.time()) > worst_late_beanchmark:
                                            custom_exception_message(self,None,"Please apply half day Your diviation exceeds 2.5 Hours")
                            else:
                                total_grace['total_month_grace']=float(total_month_grace[0]['grace_available']) if float(total_month_grace[0]['grace_available']) else 0.0
                                duration_length=AttendanceApprovalRequest.objects.get(id=instance.id,checkin_benchmark=False,is_requested=False)
                                if duration_length.duration <= 150:
                                # total_grace['grace_balance']=total_grace['total_month_grace'] - availed_grace
                                    if availed_grace is None:
                                        availed_grace=0.0
                                    # print('total_grace',total_grace['total_month_grace'],availed_grace)
                                    if (total_grace['total_month_grace']-(float(availed_grace)+float(duration_length.duration))) > 0.0 :
                                    
                                        justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,checkin_benchmark=False,is_requested=False).\
                                            update(
                                            request_type=request_type,
                                            is_requested=True,
                                            approved_status='pending',
                                            request_date=datetime.date.today(),
                                            justified_at=datetime.date.today(),
                                            justification=validated_data.get('justification'),
                                            justified_by=updated_by)

                                        return validated_data
                                    else:
                                        # raise serializers.ValidationError("Grace limit exceeds")
                                        custom_exception_message(self,None,"Grace limit exceeds")
                                elif duration_length.duration >150 and duration_length.duration <=240:
                                    # raise serializers.ValidationError("Please apply half day Your diviation exceeds 2.5 Hours")
                                    custom_exception_message(self,None,"Please apply half day Your diviation exceeds 2.5 Hours")
                                elif duration_length.duration > 240 :
                                    if (duration_start_end.duration_start.time() and duration_start_end.duration_end.time()) < worst_late_beanchmark:
                                        custom_exception_message(self,None,"Please apply half day Your diviation exceeds 2.5 Hours")
                                    elif duration_start_end.duration_start.time() < worst_late_beanchmark and duration_start_end.duration_end.time() > worst_late_beanchmark:
                                        custom_exception_message(self,None,"Please apply full day Your diviation exceeds 4 Hours")
                                    elif (duration_start_end.duration_start.time() and duration_start_end.duration_end.time()) > worst_late_beanchmark:
                                        custom_exception_message(self,None,"Please apply half day Your diviation exceeds 2.5 Hours")
                    #*****************present but user want to give HD or FD request*********************************************************
                    elif request_type == 'HD' or request_type == 'FD':
                        worst_late_beanchmark=TCoreUserDetail.objects.get(cu_user=employee_id).worst_late
                        duration_start_end=AttendanceApprovalRequest.objects.get(id=instance.id)
                        leave_type=validated_data.get('leave_type')
                        #*************check and calculation of leave counts available****************** 
                        total_paid_leave={}
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

                        attendence_daily_data = AttendanceApprovalRequest.objects.filter(((Q(leave_type_changed_period__isnull=False)&(Q(leave_type_changed_period='FD')|Q(leave_type_changed_period='HD')))|
                                                                                        (Q(leave_type_changed_period__isnull=True)&(Q(request_type='FD')|Q(request_type='HD')))),
                                                                                        attendance__employee=employee_id,is_requested=True).values('duration_start__date').distinct()
                        print("attendence_daily_data",attendence_daily_data)
                        date_list = [x['duration_start__date'] for x in attendence_daily_data.iterator()]
                        print("date_list",date_list)
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

                        availed_cl_data=float(availed_cl)+float(advance_cl)+float(availed_hd_cl/2)
                        availed_el_data=float(availed_el)+float(advance_el)+float(availed_hd_el/2)
                        availed_sl_data=float(availed_sl)+float(availed_hd_sl/2)
                        availed_ab_data=float(availed_ab)+float(advance_ab)+float(availed_hd_ab/2)

                        total_paid_leave['availed_cl']=float(availed_cl)+float(advance_cl)+float(availed_hd_cl/2)
                        total_paid_leave['availed_el']=float(availed_el)+float(advance_el)+float(availed_hd_el/2)
                        total_paid_leave['availed_sl']=float(availed_sl)+float(availed_hd_sl/2)
                        total_paid_leave['availed_ab']=float(availed_ab)+float(advance_ab)+float(availed_hd_ab/2)
                        total_paid_leave['total_availed_leave']=availed_cl_data + availed_el_data + availed_ab_data

                        core_user_detail=TCoreUserDetail.objects.filter(cu_user=employee_id,cu_is_deleted=False).values('joining_date',
                                                                                                                    'granted_cl',
                                                                                                                    'granted_sl',
                                                                                                                    'granted_el'
                                                                                                                    )
                        print('core_user_detail',core_user_detail)
                        if core_user_detail:
                            if core_user_detail[0]['joining_date']>total_month_grace[0]['year_start_date']:
                                print("joining")
                                approved_leave=JoiningApprovedLeave.objects.filter(employee=employee_id,is_deleted=False).values('cl',
                                                                                                                                'el',
                                                                                                                                'sl',
                                                                                                                                'year',
                                                                                                                                'month',
                                                                                                                                'first_grace' 
                                                                                                                     )
                                print("approved_leave",approved_leave)
                                total_paid_leave['granted_cl']=approved_leave[0]['cl'] 
                                total_paid_leave['cl_balance']=float(approved_leave[0]['cl']) -float(availed_cl_data)
                                total_paid_leave['granted_el']=approved_leave[0]['el']
                                total_paid_leave['el_balance']=float(approved_leave[0]['el']) -float(availed_el_data)
                                total_paid_leave['granted_sl']=approved_leave[0]['sl']
                                total_paid_leave['sl_balance']=float(approved_leave[0]['sl']) -float(availed_ab_data)
                                total_paid_leave['total_granted_leave']=float(approved_leave[0]['cl']) + float(approved_leave[0]['el']) + float(approved_leave[0]['sl'])
                                total_paid_leave['total_leave_balances']=float(total_paid_leave['total_granted_leave']) - float(total_paid_leave['total_availed_leave'])
                                print("total_paid_leave",total_paid_leave)
                                #**********HALF DAY OR FULL DAY LEAVE CALCULATION for New  Joining*************************
                                if request_type == 'HD' or request_type == 'FD':
                                    if  leave_type == 'SL' :
                                        
                                        if total_paid_leave['sl_balance']>0.0:
                                            duration_length=AttendanceApprovalRequest.objects.get(id=instance.id,checkin_benchmark=False,is_requested=False)
                                            if request_type == 'HD':
                                                if duration_length.duration <=240 :
                                                    # raise serializers.ValidationError("Please apply half day Your diviation exceeds 2.5 Hours")
                                            
                                                    justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,checkin_benchmark=False,is_requested=False).\
                                                            update(
                                                            request_type=request_type,
                                                            is_requested=True,
                                                            approved_status='pending',
                                                            request_date=datetime.date.today(),
                                                            justified_at=datetime.date.today(),
                                                            justification=validated_data.get('justification'),
                                                            justified_by=updated_by,
                                                            leave_type=validated_data.get('leave_type')
                                                            )

                                                    return validated_data

                                                elif duration_length.duration > 240 :
                                                    if (duration_start_end.duration_start.time() and duration_start_end.duration_end.time()) < worst_late_beanchmark:
                                                        # custom_exception_message(self,None,"Please apply half day Your diviation exceeds 2.5 Hours")
                                                        justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,checkin_benchmark=False,is_requested=False).\
                                                            update(
                                                            request_type=request_type,
                                                            is_requested=True,
                                                            approved_status='pending',
                                                            request_date=datetime.date.today(),
                                                            justified_at=datetime.date.today(),
                                                            justification=validated_data.get('justification'),
                                                            justified_by=updated_by,
                                                            leave_type=validated_data.get('leave_type')
                                                            )

                                                        return validated_data
                                                    elif duration_start_end.duration_start.time() < worst_late_beanchmark and duration_start_end.duration_end.time() > worst_late_beanchmark:
                                                        custom_exception_message(self,None,"Please apply full day Your diviation exceeds 4 Hours")
                                                    elif (duration_start_end.duration_start.time() and duration_start_end.duration_end.time()) > worst_late_beanchmark:
                                                        # custom_exception_message(self,None,"Please apply half day Your diviation exceeds 2.5 Hours")
                                                        justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,checkin_benchmark=False,is_requested=False).\
                                                            update(
                                                            request_type=request_type,
                                                            is_requested=True,
                                                            approved_status='pending',
                                                            request_date=datetime.date.today(),
                                                            justified_at=datetime.date.today(),
                                                            justification=validated_data.get('justification'),
                                                            justified_by=updated_by,
                                                            leave_type=validated_data.get('leave_type')
                                                            )

                                                        return validated_data
                                            elif request_type == 'FD' and total_paid_leave['sl_balance']>0.5:
                                                justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,checkin_benchmark=False,is_requested=False).\
                                                    update(
                                                    request_type=request_type,
                                                    is_requested=True,
                                                    approved_status='pending',
                                                    request_date=datetime.date.today(),
                                                    justified_at=datetime.date.today(),
                                                    justification=validated_data.get('justification'),
                                                    justified_by=updated_by,
                                                    leave_type=validated_data.get('leave_type')
                                                    )

                                                return validated_data
                                            else:
                                                custom_exception_message(self,None,"Not enough sick leave balance")
                                        else:
                                            # raise serializers.ValidationError("Sick leave limit exceeds")
                                            custom_exception_message(self,None,"Sick leave limit exceeds")
                                            
                                    elif leave_type =='CL':

                                        if total_paid_leave['cl_balance']>0.0:
                                            duration_length=AttendanceApprovalRequest.objects.get(id=instance.id,checkin_benchmark=False,is_requested=False)
                                            if request_type == 'HD':
                                                if duration_length.duration <=240:
                                                    justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,is_late_conveyance=False,checkin_benchmark=False,is_requested=False).\
                                                            update(
                                                            request_type=request_type,
                                                            is_requested=True,
                                                            approved_status='pending',
                                                            request_date=datetime.date.today(),
                                                            justified_at=datetime.date.today(),
                                                            justification=validated_data.get('justification'),
                                                            justified_by=updated_by,
                                                            leave_type=validated_data.get('leave_type')
                                                            )

                                                    return validated_data
                                                
                                                elif duration_length.duration > 240 :
                                                    if (duration_start_end.duration_start.time() and duration_start_end.duration_end.time()) < worst_late_beanchmark:
                                                        # custom_exception_message(self,None,"Please apply half day Your diviation exceeds 2.5 Hours")
                                                        justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,checkin_benchmark=False,is_requested=False).\
                                                            update(
                                                            request_type=request_type,
                                                            is_requested=True,
                                                            approved_status='pending',
                                                            request_date=datetime.date.today(),
                                                            justified_at=datetime.date.today(),
                                                            justification=validated_data.get('justification'),
                                                            justified_by=updated_by,
                                                            leave_type=validated_data.get('leave_type')
                                                            )

                                                        return validated_data
                                                    elif duration_start_end.duration_start.time() < worst_late_beanchmark and duration_start_end.duration_end.time() > worst_late_beanchmark:
                                                        custom_exception_message(self,None,"Please apply full day Your diviation exceeds 4 Hours")
                                                    elif (duration_start_end.duration_start.time() and duration_start_end.duration_end.time()) > worst_late_beanchmark:
                                                        # custom_exception_message(self,None,"Please apply half day Your diviation exceeds 2.5 Hours")
                                                        justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,checkin_benchmark=False,is_requested=False).\
                                                            update(
                                                            request_type=request_type,
                                                            is_requested=True,
                                                            approved_status='pending',
                                                            request_date=datetime.date.today(),
                                                            justified_at=datetime.date.today(),
                                                            justification=validated_data.get('justification'),
                                                            justified_by=updated_by,
                                                            leave_type=validated_data.get('leave_type')
                                                            )

                                                        return validated_data
                                            elif request_type == 'FD' and total_paid_leave['cl_balance']>0.5:
                                                justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,checkin_benchmark=False,is_requested=False).\
                                                    update(
                                                    request_type=request_type,
                                                    is_requested=True,
                                                    approved_status='pending',
                                                    request_date=datetime.date.today(),
                                                    justified_at=datetime.date.today(),
                                                    justification=validated_data.get('justification'),
                                                    justified_by=updated_by,
                                                    leave_type=validated_data.get('leave_type')
                                                    )

                                                return validated_data
                                            else:
                                                custom_exception_message(self,None,"Not enough casual leave balance")
                                        else:
                                            # raise serializers.ValidationError("casual leave limit exceeds")
                                            custom_exception_message(self,None,"casual leave limit exceeds")
                                    elif leave_type == 'EL':
                                        if total_paid_leave['el_balance']>0.0:
                                            duration_length=AttendanceApprovalRequest.objects.get(id=instance.id,checkin_benchmark=False,is_requested=False)
                                            if request_type == 'HD':
                                                if duration_length.duration <=240:
                                                    justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,checkin_benchmark=False,is_requested=False).\
                                                            update(
                                                            request_type=request_type,
                                                            is_requested=True,
                                                            approved_status='pending',
                                                            request_date=datetime.date.today(),
                                                            justified_at=datetime.date.today(),
                                                            justification=validated_data.get('justification'),
                                                            justified_by=updated_by,
                                                            leave_type=validated_data.get('leave_type')
                                                            )

                                                    return validated_data
                                                elif duration_length.duration > 240:
                                                    if (duration_start_end.duration_start.time() and duration_start_end.duration_end.time()) < worst_late_beanchmark:
                                                        # custom_exception_message(self,None,"Please apply half day Your diviation exceeds 2.5 Hours")
                                                        justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,checkin_benchmark=False,is_requested=False).\
                                                            update(
                                                            request_type=request_type,
                                                            is_requested=True,
                                                            approved_status='pending',
                                                            request_date=datetime.date.today(),
                                                            justified_at=datetime.date.today(),
                                                            justification=validated_data.get('justification'),
                                                            justified_by=updated_by,
                                                            leave_type=validated_data.get('leave_type')
                                                            )

                                                        return validated_data
                                                    elif duration_start_end.duration_start.time() < worst_late_beanchmark and duration_start_end.duration_end.time() > worst_late_beanchmark:
                                                        custom_exception_message(self,None,"Please apply full day Your diviation exceeds 4 Hours")
                                                    elif (duration_start_end.duration_start.time() and duration_start_end.duration_end.time()) > worst_late_beanchmark:
                                                        # custom_exception_message(self,None,"Please apply half day Your diviation exceeds 2.5 Hours")
                                                        justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,checkin_benchmark=False,is_requested=False).\
                                                            update(
                                                            request_type=request_type,
                                                            is_requested=True,
                                                            approved_status='pending',
                                                            request_date=datetime.date.today(),
                                                            justified_at=datetime.date.today(),
                                                            justification=validated_data.get('justification'),
                                                            justified_by=updated_by,
                                                            leave_type=validated_data.get('leave_type')
                                                            )

                                                        return validated_data
                                            
                                            elif request_type == 'FD' and total_paid_leave['el_balance']>0.5:
                                                justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,checkin_benchmark=False,is_requested=False).\
                                                    update(
                                                    request_type=request_type,
                                                    is_requested=True,
                                                    approved_status='pending',
                                                    request_date=datetime.date.today(),
                                                    justified_at=datetime.date.today(),
                                                    justification=validated_data.get('justification'),
                                                    justified_by=updated_by,
                                                    leave_type=validated_data.get('leave_type')
                                                    )

                                                return validated_data
                                            else:
                                                custom_exception_message(self,None,"Not enough earn leave balance")
                                        else:
                                            # raise serializers.ValidationError("Earned leave limit exceeds")
                                            custom_exception_message(self,None,"Earned leave limit exceeds")
                                            
                                    elif leave_type == 'AB':
                                        justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,checkin_benchmark=False,is_requested=False).\
                                                    update(
                                                    request_type=request_type,
                                                    is_requested=True,
                                                    approved_status='pending',
                                                    request_date=datetime.date.today(),
                                                    justified_at=datetime.date.today(),
                                                    justification=validated_data.get('justification'),
                                                    justified_by=updated_by,
                                                    leave_type=validated_data.get('leave_type')
                                                    )

                                        return validated_data
                            else:
                                total_paid_leave['granted_cl']=core_user_detail[0]['granted_cl']
                                total_paid_leave['cl_balance']=float(core_user_detail[0]['granted_cl']) - float(availed_cl_data)
                                total_paid_leave['granted_el']=core_user_detail[0]['granted_el']
                                total_paid_leave['el_balance']=float(core_user_detail[0]['granted_el']) - float(availed_el_data)
                                total_paid_leave['granted_sl']=core_user_detail[0]['granted_sl']
                                total_paid_leave['sl_balance']=float(core_user_detail[0]['granted_sl']) - float(availed_sl_data)
                                total_paid_leave['total_granted_leave']=float(core_user_detail[0]['granted_cl']) + float(core_user_detail[0]['granted_el']) + float(core_user_detail[0]['granted_sl'])
                                total_paid_leave['total_leave_balances']=float(total_paid_leave['total_granted_leave']) - float(total_paid_leave['total_availed_leave'])
                                print("total_paid_leave",total_paid_leave)
                                #**********HALF DAY OR FULL DAY LEAVE CALCULATION Regular *************************
                                if request_type == 'HD' or request_type == 'FD':
                                    if  leave_type == 'SL' :
                                        
                                        if total_paid_leave['sl_balance']>0.0:
                                            duration_length=AttendanceApprovalRequest.objects.get(id=instance.id,checkin_benchmark=False,is_requested=False)
                                            if request_type == 'HD':
                                                if duration_length.duration <=240 :
                                                    # raise serializers.ValidationError("Please apply half day Your diviation exceeds 2.5 Hours")
                                            
                                                    justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,checkin_benchmark=False,is_requested=False).\
                                                            update(
                                                            request_type=request_type,
                                                            is_requested=True,
                                                            approved_status='pending',
                                                            request_date=datetime.date.today(),
                                                            justified_at=datetime.date.today(),
                                                            justification=validated_data.get('justification'),
                                                            justified_by=updated_by,
                                                            leave_type=validated_data.get('leave_type')
                                                            )

                                                    return validated_data

                                                elif duration_length.duration > 240 :
                                                    if (duration_start_end.duration_start.time() and duration_start_end.duration_end.time()) < worst_late_beanchmark:
                                                        # custom_exception_message(self,None,"Please apply half day Your diviation exceeds 2.5 Hours")
                                                        justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,checkin_benchmark=False,is_requested=False).\
                                                            update(
                                                            request_type=request_type,
                                                            is_requested=True,
                                                            approved_status='pending',
                                                            request_date=datetime.date.today(),
                                                            justified_at=datetime.date.today(),
                                                            justification=validated_data.get('justification'),
                                                            justified_by=updated_by,
                                                            leave_type=validated_data.get('leave_type')
                                                            )

                                                        return validated_data
                                                    elif duration_start_end.duration_start.time() < worst_late_beanchmark and duration_start_end.duration_end.time() > worst_late_beanchmark:
                                                        custom_exception_message(self,None,"Please apply full day Your diviation exceeds 4 Hours")
                                                    elif (duration_start_end.duration_start.time() and duration_start_end.duration_end.time()) > worst_late_beanchmark:
                                                        # custom_exception_message(self,None,"Please apply half day Your diviation exceeds 2.5 Hours")
                                                        justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,checkin_benchmark=False,is_requested=False).\
                                                            update(
                                                            request_type=request_type,
                                                            is_requested=True,
                                                            approved_status='pending',
                                                            request_date=datetime.date.today(),
                                                            justified_at=datetime.date.today(),
                                                            justification=validated_data.get('justification'),
                                                            justified_by=updated_by,
                                                            leave_type=validated_data.get('leave_type')
                                                            )

                                                        return validated_data
                                            elif request_type == 'FD' and total_paid_leave['sl_balance']>0.5:
                                                justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,checkin_benchmark=False,is_requested=False).\
                                                    update(
                                                    request_type=request_type,
                                                    is_requested=True,
                                                    approved_status='pending',
                                                    request_date=datetime.date.today(),
                                                    justified_at=datetime.date.today(),
                                                    justification=validated_data.get('justification'),
                                                    justified_by=updated_by,
                                                    leave_type=validated_data.get('leave_type')
                                                    )
                                                return validated_data
                                            else:
                                                custom_exception_message(self,None,"Not enough sick leave balance")
                                                
                                        else:
                                            # raise serializers.ValidationError("Sick leave limit exceeds")
                                            custom_exception_message(self,None,"Sick leave limit exceeds")
                                            
                                    elif leave_type =='CL':
                                        if total_paid_leave['cl_balance']>0.0:
                                            duration_length=AttendanceApprovalRequest.objects.get(id=instance.id,checkin_benchmark=False,is_requested=False)
                                            if request_type == 'HD':
                                                if  duration_length.duration <=240:
                                                    justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,is_late_conveyance=False,checkin_benchmark=False,is_requested=False).\
                                                            update(
                                                            request_type=request_type,
                                                            is_requested=True,
                                                            approved_status='pending',
                                                            request_date=datetime.date.today(),
                                                            justified_at=datetime.date.today(),
                                                            justification=validated_data.get('justification'),
                                                            justified_by=updated_by,
                                                            leave_type=validated_data.get('leave_type')
                                                            )

                                                    return validated_data
                                                
                                                elif duration_length.duration > 240 :
                                                    if (duration_start_end.duration_start.time() and duration_start_end.duration_end.time()) < worst_late_beanchmark:
                                                        # custom_exception_message(self,None,"Please apply half day Your diviation exceeds 2.5 Hours")
                                                        justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,checkin_benchmark=False,is_requested=False).\
                                                            update(
                                                            request_type=request_type,
                                                            is_requested=True,
                                                            approved_status='pending',
                                                            request_date=datetime.date.today(),
                                                            justified_at=datetime.date.today(),
                                                            justification=validated_data.get('justification'),
                                                            justified_by=updated_by,
                                                            leave_type=validated_data.get('leave_type')
                                                            )

                                                        return validated_data
                                                    elif duration_start_end.duration_start.time() < worst_late_beanchmark and duration_start_end.duration_end.time() > worst_late_beanchmark:
                                                        custom_exception_message(self,None,"Please apply full day Your diviation exceeds 4 Hours")
                                                    elif (duration_start_end.duration_start.time() and duration_start_end.duration_end.time()) > worst_late_beanchmark:
                                                        # custom_exception_message(self,None,"Please apply half day Your diviation exceeds 2.5 Hours")
                                                        justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,checkin_benchmark=False,is_requested=False).\
                                                            update(
                                                            request_type=request_type,
                                                            is_requested=True,
                                                            approved_status='pending',
                                                            request_date=datetime.date.today(),
                                                            justified_at=datetime.date.today(),
                                                            justification=validated_data.get('justification'),
                                                            justified_by=updated_by,
                                                            leave_type=validated_data.get('leave_type')
                                                            )

                                                        return validated_data
                                            elif request_type == 'FD' and total_paid_leave['cl_balance']>0.5:
                                                justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,checkin_benchmark=False,is_requested=False).\
                                                    update(
                                                    request_type=request_type,
                                                    is_requested=True,
                                                    approved_status='pending',
                                                    request_date=datetime.date.today(),
                                                    justified_at=datetime.date.today(),
                                                    justification=validated_data.get('justification'),
                                                    justified_by=updated_by,
                                                    leave_type=validated_data.get('leave_type')
                                                    )

                                                return validated_data
                                            else:
                                                custom_exception_message(self,None,"Not enough casual leave balance")
                                        else:
                                            # raise serializers.ValidationError("casual leave limit exceeds")
                                            custom_exception_message(self,None,"casual leave limit exceeds")
                                    elif leave_type =='EL':
                                        if total_paid_leave['el_balance']>0.0:
                                            duration_length=AttendanceApprovalRequest.objects.get(id=instance.id,checkin_benchmark=False,is_requested=False)
                                            if request_type == 'HD':
                                                if  duration_length.duration <=240:
                                                    justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,checkin_benchmark=False,is_requested=False).\
                                                            update(
                                                            request_type=request_type,
                                                            is_requested=True,
                                                            approved_status='pending',
                                                            request_date=datetime.date.today(),
                                                            justified_at=datetime.date.today(),
                                                            justification=validated_data.get('justification'),
                                                            justified_by=updated_by,
                                                            leave_type=validated_data.get('leave_type')
                                                            )

                                                    return validated_data
                                                elif duration_length.duration > 240:
                                                    if (duration_start_end.duration_start.time() and duration_start_end.duration_end.time()) < worst_late_beanchmark:
                                                        # custom_exception_message(self,None,"Please apply half day Your diviation exceeds 2.5 Hours")
                                                        justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,checkin_benchmark=False,is_requested=False).\
                                                            update(
                                                            request_type=request_type,
                                                            is_requested=True,
                                                            approved_status='pending',
                                                            request_date=datetime.date.today(),
                                                            justified_at=datetime.date.today(),
                                                            justification=validated_data.get('justification'),
                                                            justified_by=updated_by,
                                                            leave_type=validated_data.get('leave_type')
                                                            )

                                                        return validated_data
                                                    elif duration_start_end.duration_start.time() < worst_late_beanchmark and duration_start_end.duration_end.time() > worst_late_beanchmark:
                                                        custom_exception_message(self,None,"Please apply full day Your diviation exceeds 4 Hours")
                                                    elif (duration_start_end.duration_start.time() and duration_start_end.duration_end.time()) > worst_late_beanchmark:
                                                        # custom_exception_message(self,None,"Please apply half day Your diviation exceeds 2.5 Hours")
                                                        justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,checkin_benchmark=False,is_requested=False).\
                                                            update(
                                                            request_type=request_type,
                                                            is_requested=True,
                                                            approved_status='pending',
                                                            request_date=datetime.date.today(),
                                                            justified_at=datetime.date.today(),
                                                            justification=validated_data.get('justification'),
                                                            justified_by=updated_by,
                                                            leave_type=validated_data.get('leave_type')
                                                            )

                                                        return validated_data
                                            
                                            elif request_type == 'FD' and total_paid_leave['el_balance']>0.5:
                                                justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,checkin_benchmark=False,is_requested=False).\
                                                    update(
                                                    request_type=request_type,
                                                    is_requested=True,
                                                    approved_status='pending',
                                                    request_date=datetime.date.today(),
                                                    justified_at=datetime.date.today(),
                                                    justification=validated_data.get('justification'),
                                                    justified_by=updated_by,
                                                    leave_type=validated_data.get('leave_type')
                                                    )

                                                return validated_data
                                        else:
                                            # raise serializers.ValidationError("Earned leave limit exceeds")
                                            custom_exception_message(self,None,"Earned leave limit exceeds")
                                    elif leave_type == 'AB':
                                        justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,checkin_benchmark=False,is_requested=False).\
                                                    update(
                                                    request_type=request_type,
                                                    is_requested=True,
                                                    approved_status='pending',
                                                    request_date=datetime.date.today(),
                                                    justified_at=datetime.date.today(),
                                                    justification=validated_data.get('justification'),
                                                    justified_by=updated_by,
                                                    leave_type=validated_data.get('leave_type')
                                                    )

                                        return validated_data
                    
                    #*****************As the user is already present hence partial OD********************************************************
                    elif request_type == 'OD':          
                        vehicle_type= validated_data.get('vehicle_type') if validated_data.get('vehicle_type') else None
                        from_place= validated_data.get('from_place') if validated_data.get('from_place') else None
                        to_place= validated_data.get('to_place') if validated_data.get('to_place') else None
                        conveyance_expense= validated_data.get('conveyance_expense') if validated_data.get('conveyance_expense') else 0.0
                        conveyance_remarks= validated_data.get('conveyance_purpose') if validated_data.get('conveyance_purpose') else None
                        conveyance_alloted_by= validated_data.get('conveyance_alloted_by') if validated_data.get('conveyance_alloted_by') else None
                        print(vehicle_type,from_place,to_place,conveyance_expense,conveyance_remarks,conveyance_alloted_by)
                        if from_place or to_place or conveyance_remarks:
                            print("aisaichai ")
                            justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,is_requested=False).\
                                update(
                                request_type='POD',
                                is_requested=True,
                                approved_status='pending',
                                request_date=datetime.date.today(),
                                justified_at=datetime.date.today(),
                                justification=validated_data.get('justification'),
                                justified_by=updated_by,
                                is_conveyance=True,
                                conveyance_approval=0,
                                vehicle_type_id=vehicle_type,
                                conveyance_alloted_by_id=conveyance_alloted_by,
                                from_place=from_place,
                                to_place=to_place,
                                conveyance_expense=conveyance_expense,
                                conveyance_purpose=conveyance_remarks
                                )
                            print("justify_attendence",justify_attendence)

                            return validated_data
                        else:
                            justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,checkin_benchmark=False,is_requested=False).\
                                update(
                                request_type='POD',
                                is_requested=True,
                                approved_status='pending',
                                request_date=datetime.date.today(),
                                justified_at=datetime.date.today(),
                                justification=validated_data.get('justification'),
                                justified_by=updated_by,
                                is_conveyance=False,
                                )

                            return validated_data
                    
                    #*****************Request for mispunch************************************************************************************
                    elif request_type == 'MP': 
                        justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,checkin_benchmark=False,is_requested=False).\
                                update(
                                request_type=request_type,
                                is_requested=True,
                                approved_status='pending',
                                request_date=datetime.date.today(),
                                justified_at=datetime.date.today(),
                                justification=validated_data.get('justification'),
                                justified_by=updated_by)

                        return validated_data



            
                    return validated_data
                #REQUEST ONLY IF User ABSENT 
                else:
                    '''
                        Commented By Rupam Hazra 16/01/2020 for half day open for absent and added HD if condition
                    '''
                    # if request_type == 'FD':
                    #     leave_type=validated_data.get('leave_type')
                    #     #*************check and calculation of leave counts available****************** 
                    #     total_paid_leave={}
                    #     advance_leave=EmployeeAdvanceLeaves.objects.filter(Q(employee=employee_id)&
                    #                                        Q(is_deleted=False)&
                    #                                        (Q(approved_status='pending')|Q(approved_status='approved'))
                    #                                       ).values('leave_type','start_date','end_date')
                    #     print('advance_leave',advance_leave)     
                    #     advance_cl=0
                    #     advance_el=0
                    #     advance_ab=0
                    #     day=0
                    #     if advance_leave:
                    #         for leave in advance_leave:
                    #             print('leave',leave)
                    #             start_date=leave['start_date'].date()
                    #             end_date=leave['end_date'].date()+timedelta(days=1)
                    #             print('start_date,end_date',start_date,end_date)
                    #             if date_object < end_date:
                    #                 if date_object < start_date:
                    #                     day=(end_date-start_date).days 
                    #                     print('day',day)
                    #                 elif date_object > start_date:
                    #                     day=(end_date-date_object).days
                    #                     print('day2',day)
                    #                 else:
                    #                     day=(end_date-date_object).days

                    #             if leave['leave_type']=='CL':
                    #                 advance_cl+=day
                    #             elif leave['leave_type']=='EL':
                    #                 advance_el+=day
                    #             elif leave['leave_type']=='AB':
                    #                 advance_ab+=day
                        
                        
                        
                    #     """ 
                    #     LEAVE CALCULATION:-
                    #     1)SINGLE LEAVE CALCULATION
                    #     2)MULTIPLE LEAVE FOR ONE DAY IS AUTO CONVERTED TO ONE TYPE OF LEAVE 
                    #     EDITED BY :- Abhishek.singh@shyamfuture.com
                        
                    #     """ 
                    #     availed_hd_cl=0.0
                    #     availed_hd_el=0.0
                    #     availed_hd_sl=0.0
                    #     availed_hd_ab=0.0
                    #     availed_cl=0.0
                    #     availed_el=0.0
                    #     availed_sl=0.0
                    #     availed_ab=0.0

                    #     attendence_daily_data = AttendanceApprovalRequest.objects.filter(((Q(leave_type_changed_period__isnull=False)&(Q(leave_type_changed_period='FD')|Q(leave_type_changed_period='HD')))|
                    #                                                                     (Q(leave_type_changed_period__isnull=True)&(Q(request_type='FD')|Q(request_type='HD')))),
                    #                                                                     attendance__employee=employee_id,is_requested=True).values('duration_start__date').distinct()
                    #     print("attendence_daily_data",attendence_daily_data)
                    #     date_list = [x['duration_start__date'] for x in attendence_daily_data.iterator()]
                    #     print("date_list",date_list)
                    #     # for data in attendence_daily_data.iterator():
                    #         # print(datetime.now())
                    #     availed_master_wo_reject_fd = AttendanceApprovalRequest.objects.\
                    #             filter((Q(approved_status='pending')|Q(approved_status='approved')|Q(approved_status='reject')),
                    #                     (Q(leave_type__isnull=False)|Q(leave_type_changed_period__isnull=False)),
                    #                     attendance__employee=employee_id,
                    #                     attendance_date__in=date_list,is_requested=True,is_deleted=False).annotate(
                    #                         leave_type_final = Case(
                    #                         When((Q(leave_type_changed_period__isnull=False)&Q(leave_type_changed_period='FD')),then=F('leave_type_changed')),
                    #                         When((Q(leave_type_changed_period__isnull=True)&Q(request_type='FD')),then=F('leave_type')),
                    #                         output_field=CharField()
                    #                     ),
                    #                     leave_type_final_hd = Case(
                    #                         When((Q(leave_type_changed_period__isnull=False)&Q(leave_type_changed_period='HD')),then=F('leave_type_changed')),
                    #                         When((Q(leave_type_changed_period__isnull=True)&Q(request_type='HD')),then=F('leave_type')),
                    #                         output_field=CharField()
                    #                     ),
                    #                     ).values('leave_type_final','leave_type_final_hd','attendance_date').distinct()
                    #     print("availed_master_wo_reject_fd",availed_master_wo_reject_fd)
                    #     if availed_master_wo_reject_fd:

                    #         for data in date_list:
                    #             availed_FD=availed_master_wo_reject_fd.filter(attendance_date=data)
                                
                    #             print("availed_HD",availed_FD)
                    #             if availed_FD.filter(leave_type_final__isnull=False):
                    #                 if availed_FD.values('leave_type_final').count() >1:
                    #                     if availed_FD.filter(leave_type_final='AB'):
                    #                         availed_ab=availed_ab+1.0

                    #                     elif availed_FD.filter(leave_type_final='CL'):
                    #                         availed_cl=availed_cl+1.0
                                                    

                    #                 else:
                    #                     l_type=availed_FD[0]['leave_type_final']
                    #                     if l_type == 'CL':
                    #                         availed_cl=availed_cl+1.0
                    #                     elif l_type == 'EL':
                    #                         availed_el=availed_el+1.0
                    #                     elif l_type == 'SL':
                    #                         availed_sl=availed_sl+1.0
                    #                     elif l_type == 'AB':
                    #                         availed_ab=availed_ab+1.0

                    #             elif availed_FD.filter(leave_type_final_hd__isnull=False):
                    #                 if availed_FD.values('leave_type_final_hd').count() >1:
                    #                     if availed_FD.filter(leave_type_final_hd='AB'):
                    #                         availed_hd_ab=availed_hd_ab+1.0

                    #                     elif availed_FD.filter(leave_type_final_hd='CL'):
                    #                         availed_hd_cl=availed_hd_cl+1.0
                                                    

                    #                 else:
                    #                     l_type=availed_FD[0]['leave_type_final_hd']
                    #                     if l_type == 'CL':
                    #                         availed_hd_cl=availed_hd_cl+1.0
                    #                     elif l_type == 'EL':
                    #                         availed_hd_el=availed_hd_el+1.0
                    #                     elif l_type == 'SL':
                    #                         availed_hd_sl=availed_hd_sl+1.0
                    #                     elif l_type == 'AB':
                    #                         availed_hd_ab=availed_hd_ab+1.0


                    #     availed_cl_data=float(availed_cl)+float(advance_cl)+float(availed_hd_cl/2)
                    #     availed_el_data=float(availed_el)+float(advance_el)+float(availed_hd_el/2)
                    #     availed_sl_data=float(availed_sl)+float(availed_hd_sl/2)
                    #     availed_ab_data=float(availed_ab)+float(advance_ab)+float(availed_hd_ab/2)

                      
                    #     total_paid_leave['availed_cl']=float(availed_cl)+float(advance_cl)+float(availed_hd_cl/2)
                    #     total_paid_leave['availed_el']=float(availed_el)+float(advance_el)+float(availed_hd_el/2)
                    #     total_paid_leave['availed_sl']=float(availed_sl)+float(availed_hd_sl/2)
                    #     total_paid_leave['availed_ab']=float(availed_ab)+float(advance_ab)+float(availed_hd_ab/2)
                    #     total_paid_leave['total_availed_leave']=availed_cl_data + availed_el_data + availed_ab_data

                    #     core_user_detail=TCoreUserDetail.objects.filter(cu_user=employee_id,cu_is_deleted=False).values('joining_date',
                    #                                                                                                 'granted_cl',
                    #                                                                                                 'granted_sl',
                    #                                                                                                 'granted_el'
                    #                                                                                                 )
                    #     print('core_user_detail',core_user_detail)
                    #     if core_user_detail:
                    #         if core_user_detail[0]['joining_date']>total_month_grace[0]['year_start_date']:
                    #             print("joining")
                    #             approved_leave=JoiningApprovedLeave.objects.filter(employee=employee_id,is_deleted=False).values('cl',
                    #                                                                                                             'el',
                    #                                                                                                             'sl',
                    #                                                                                                             'year',
                    #                                                                                                             'month',
                    #                                                                                                             'first_grace' 
                    #                                                                                                             )
                    #             print("approved_leave",approved_leave)
                    #             total_paid_leave['granted_cl']=approved_leave[0]['cl'] 
                    #             total_paid_leave['cl_balance']=float(approved_leave[0]['cl']) -float(availed_cl_data)
                    #             total_paid_leave['granted_el']=approved_leave[0]['el']
                    #             total_paid_leave['el_balance']=float(approved_leave[0]['el']) -float(availed_el_data)
                    #             total_paid_leave['granted_sl']=approved_leave[0]['sl']
                    #             total_paid_leave['sl_balance']=float(approved_leave[0]['sl']) -float(availed_sl_data)
                    #             total_paid_leave['total_granted_leave']=float(approved_leave[0]['cl']) + float(approved_leave[0]['el']) + float(approved_leave[0]['sl'])
                    #             total_paid_leave['total_leave_balances']=float(total_paid_leave['total_granted_leave']) - float(total_paid_leave['total_availed_leave'])
                    #             print("total_paid_leave",total_paid_leave)
                    #             #**********HALF DAY OR FULL DAY LEAVE CALCULATION for New  Joining*************************
                    #             if request_type == 'FD':
                    #                 if leave_type == 'SL' :
                                        
                    #                     if total_paid_leave['sl_balance']>0.5:
                    #                         justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,checkin_benchmark=False,is_requested=False).\
                    #                                 update(
                    #                                 request_type=request_type,
                    #                                 is_requested=True,
                    #                                 approved_status='pending',
                    #                                 request_date=datetime.date.today(),
                    #                                 justified_at=datetime.date.today(),
                    #                                 justification=validated_data.get('justification'),
                    #                                 justified_by=updated_by,
                    #                                 leave_type=validated_data.get('leave_type')
                    #                                 )

                    #                         return validated_data
                    #                     else:
                    #                         # raise serializers.ValidationError("Sick leave limit exceeds")
                    #                         custom_exception_message(self,None,"Not enough Sick leave to apply full day")
                    #                 elif leave_type =='CL':
                    #                     print("na na na ")
                    #                     if total_paid_leave['cl_balance']>0.5:
                    #                         justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,checkin_benchmark=False,is_requested=False).\
                    #                                 update(
                    #                                 request_type=request_type,
                    #                                 is_requested=True,
                    #                                 approved_status='pending',
                    #                                 request_date=datetime.date.today(),
                    #                                 justified_at=datetime.date.today(),
                    #                                 justification=validated_data.get('justification'),
                    #                                 justified_by=updated_by,
                    #                                 leave_type=validated_data.get('leave_type')
                    #                                 )

                    #                         return validated_data
                    #                     else:
                    #                         # raise serializers.ValidationError("casual leave limit exceeds")
                    #                         custom_exception_message(self,None,"Not enough casual leave to apply full day")
                    #                 elif leave_type == 'EL':
                    #                     if total_paid_leave['el_balance']>0.5:
                    #                         justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,checkin_benchmark=False,is_requested=False).\
                    #                                 update(
                    #                                 request_type=request_type,
                    #                                 is_requested=True,
                    #                                 approved_status='pending',
                    #                                 request_date=datetime.date.today(),
                    #                                 justified_at=datetime.date.today(),
                    #                                 justification=validated_data.get('justification'),
                    #                                 justified_by=updated_by,
                    #                                 leave_type=validated_data.get('leave_type')
                    #                                 )

                    #                         return validated_data
                    #                     else:
                    #                         # raise serializers.ValidationError("Earned leave limit exceeds")
                    #                         custom_exception_message(self,None,"Not enough Earned leave to apply full day")
                    #                 elif leave_type == 'AB':
                    #                     justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,checkin_benchmark=False,is_requested=False).\
                    #                                 update(
                    #                                 request_type=request_type,
                    #                                 is_requested=True,
                    #                                 approved_status='pending',
                    #                                 request_date=datetime.date.today(),
                    #                                 justified_at=datetime.date.today(),
                    #                                 justification=validated_data.get('justification'),
                    #                                 justified_by=updated_by,
                    #                                 leave_type=validated_data.get('leave_type')
                    #                                 )

                    #                     return validated_data
                    #         else:
                    #             total_paid_leave['granted_cl']=core_user_detail[0]['granted_cl']
                    #             total_paid_leave['cl_balance']=float(core_user_detail[0]['granted_cl']) - float(availed_cl_data)
                    #             total_paid_leave['granted_el']=core_user_detail[0]['granted_el']
                    #             total_paid_leave['el_balance']=float(core_user_detail[0]['granted_el']) - float(availed_el_data)
                    #             total_paid_leave['granted_sl']=core_user_detail[0]['granted_sl']
                    #             total_paid_leave['sl_balance']=float(core_user_detail[0]['granted_sl']) - float(availed_sl_data)
                    #             total_paid_leave['total_granted_leave']=float(core_user_detail[0]['granted_cl']) + float(core_user_detail[0]['granted_el']) + float(core_user_detail[0]['granted_sl'])
                    #             total_paid_leave['total_leave_balances']=float(total_paid_leave['total_granted_leave']) - float(total_paid_leave['total_availed_leave'])
                    #             print("total_paid_leave",total_paid_leave)
                    #             #**********HALF DAY OR FULL DAY LEAVE CALCULATION Regular *************************
                    #             if request_type == 'FD':
                    #                 if leave_type =='SL':
                    #                     if total_paid_leave['sl_balance']>0.5:
                    #                         justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,checkin_benchmark=False,is_requested=False).\
                    #                                 update(
                    #                                 request_type=request_type,
                    #                                 is_requested=True,
                    #                                 approved_status='pending',
                    #                                 request_date=datetime.date.today(),
                    #                                 justified_at=datetime.date.today(),
                    #                                 justification=validated_data.get('justification'),
                    #                                 justified_by=updated_by,
                    #                                 leave_type=validated_data.get('leave_type')
                    #                                 )

                    #                         return validated_data
                    #                     else:
                    #                         # raise serializers.ValidationError("Sick leave limit exceeds")
                    #                         custom_exception_message(self,None,"Not enough Sick leave to apply full day")
                    #                 elif leave_type =='CL':
                    #                     if total_paid_leave['cl_balance']>0.5:
                    #                         justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,checkin_benchmark=False,is_requested=False).\
                    #                                 update(
                    #                                 request_type=request_type,
                    #                                 is_requested=True,
                    #                                 approved_status='pending',
                    #                                 request_date=datetime.date.today(),
                    #                                 justified_at=datetime.date.today(),
                    #                                 justification=validated_data.get('justification'),
                    #                                 justified_by=updated_by,
                    #                                 leave_type=validated_data.get('leave_type')
                    #                                 )

                    #                         return validated_data
                    #                     else:
                    #                         # raise serializers.ValidationError("casual leave limit exceeds")
                    #                         custom_exception_message(self,None,"Not enough casual leave to apply full day")
                    #                 elif leave_type =='EL':
                    #                     if total_paid_leave['el_balance']>0.5:
                    #                         justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,checkin_benchmark=False,is_requested=False).\
                    #                                 update(
                    #                                 request_type=request_type,
                    #                                 is_requested=True,
                    #                                 approved_status='pending',
                    #                                 request_date=datetime.date.today(),
                    #                                 justified_at=datetime.date.today(),
                    #                                 justification=validated_data.get('justification'),
                    #                                 justified_by=updated_by,
                    #                                 leave_type=validated_data.get('leave_type')
                    #                                 )

                    #                         return validated_data
                    #                     else:
                    #                         # raise serializers.ValidationError("Earned leave limit exceeds")
                    #                         custom_exception_message(self,None,"Not enough Earned leave to apply full day")
                                    
                    #                 elif leave_type == 'AB':
                    #                     justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,checkin_benchmark=False,is_requested=False).\
                    #                                 update(
                    #                                 request_type=request_type,
                    #                                 is_requested=True,
                    #                                 approved_status='pending',
                    #                                 request_date=datetime.date.today(),
                    #                                 justified_at=datetime.date.today(),
                    #                                 justification=validated_data.get('justification'),
                    #                                 justified_by=updated_by,
                    #                                 leave_type=validated_data.get('leave_type')
                    #                                 )

                    #                     return validated_data

                    if request_type == 'HD' or request_type == 'FD':
                        worst_late_beanchmark=TCoreUserDetail.objects.get(cu_user=employee_id).worst_late
                        duration_start_end=AttendanceApprovalRequest.objects.get(id=instance.id)
                        leave_type=validated_data.get('leave_type')
                        #*************check and calculation of leave counts available****************** 
                        total_paid_leave={}
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

                        attendence_daily_data = AttendanceApprovalRequest.objects.filter(((Q(leave_type_changed_period__isnull=False)&(Q(leave_type_changed_period='FD')|Q(leave_type_changed_period='HD')))|
                                                                                        (Q(leave_type_changed_period__isnull=True)&(Q(request_type='FD')|Q(request_type='HD')))),
                                                                                        attendance__employee=employee_id,is_requested=True).values('duration_start__date').distinct()
                        print("attendence_daily_data",attendence_daily_data)
                        date_list = [x['duration_start__date'] for x in attendence_daily_data.iterator()]
                        print("date_list",date_list)
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

                        availed_cl_data=float(availed_cl)+float(advance_cl)+float(availed_hd_cl/2)
                        availed_el_data=float(availed_el)+float(advance_el)+float(availed_hd_el/2)
                        availed_sl_data=float(availed_sl)+float(availed_hd_sl/2)
                        availed_ab_data=float(availed_ab)+float(advance_ab)+float(availed_hd_ab/2)

                        total_paid_leave['availed_cl']=float(availed_cl)+float(advance_cl)+float(availed_hd_cl/2)
                        total_paid_leave['availed_el']=float(availed_el)+float(advance_el)+float(availed_hd_el/2)
                        total_paid_leave['availed_sl']=float(availed_sl)+float(availed_hd_sl/2)
                        total_paid_leave['availed_ab']=float(availed_ab)+float(advance_ab)+float(availed_hd_ab/2)
                        total_paid_leave['total_availed_leave']=availed_cl_data + availed_el_data + availed_ab_data

                        core_user_detail=TCoreUserDetail.objects.filter(cu_user=employee_id,cu_is_deleted=False).values('joining_date',
                                                                                                                    'granted_cl',
                                                                                                                    'granted_sl',
                                                                                                                    'granted_el'
                                                                                                                    )
                        print('core_user_detail',core_user_detail)
                        if core_user_detail:
                            if core_user_detail[0]['joining_date']>total_month_grace[0]['year_start_date']:
                                print("joining")
                                approved_leave=JoiningApprovedLeave.objects.filter(employee=employee_id,is_deleted=False).values('cl',
                                                                                                                                'el',
                                                                                                                                'sl',
                                                                                                                                'year',
                                                                                                                                'month',
                                                                                                                                'first_grace' 
                                                                                                                     )
                                print("approved_leave",approved_leave)
                                total_paid_leave['granted_cl']=approved_leave[0]['cl'] 
                                total_paid_leave['cl_balance']=float(approved_leave[0]['cl']) -float(availed_cl_data)
                                total_paid_leave['granted_el']=approved_leave[0]['el']
                                total_paid_leave['el_balance']=float(approved_leave[0]['el']) -float(availed_el_data)
                                total_paid_leave['granted_sl']=approved_leave[0]['sl']
                                total_paid_leave['sl_balance']=float(approved_leave[0]['sl']) -float(availed_ab_data)
                                total_paid_leave['total_granted_leave']=float(approved_leave[0]['cl']) + float(approved_leave[0]['el']) + float(approved_leave[0]['sl'])
                                total_paid_leave['total_leave_balances']=float(total_paid_leave['total_granted_leave']) - float(total_paid_leave['total_availed_leave'])
                                print("total_paid_leave",total_paid_leave)
                                #**********HALF DAY OR FULL DAY LEAVE CALCULATION for New  Joining*************************
                                if request_type == 'HD' or request_type == 'FD':
                                    if  leave_type == 'SL' :
                                        
                                        if total_paid_leave['sl_balance']>0.0:
                                            duration_length=AttendanceApprovalRequest.objects.get(id=instance.id,checkin_benchmark=False,is_requested=False)
                                            if request_type == 'HD':
                                                if duration_length.duration <=240 :
                                                    # raise serializers.ValidationError("Please apply half day Your diviation exceeds 2.5 Hours")
                                            
                                                    justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,checkin_benchmark=False,is_requested=False).\
                                                            update(
                                                            request_type=request_type,
                                                            is_requested=True,
                                                            approved_status='pending',
                                                            request_date=datetime.date.today(),
                                                            justified_at=datetime.date.today(),
                                                            justification=validated_data.get('justification'),
                                                            justified_by=updated_by,
                                                            leave_type=validated_data.get('leave_type')
                                                            )

                                                    return validated_data

                                                elif duration_length.duration > 240 :
                                                    if (duration_start_end.duration_start.time() and duration_start_end.duration_end.time()) < worst_late_beanchmark:
                                                        # custom_exception_message(self,None,"Please apply half day Your diviation exceeds 2.5 Hours")
                                                        justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,checkin_benchmark=False,is_requested=False).\
                                                            update(
                                                            request_type=request_type,
                                                            is_requested=True,
                                                            approved_status='pending',
                                                            request_date=datetime.date.today(),
                                                            justified_at=datetime.date.today(),
                                                            justification=validated_data.get('justification'),
                                                            justified_by=updated_by,
                                                            leave_type=validated_data.get('leave_type')
                                                            )

                                                        return validated_data
                                                    elif duration_start_end.duration_start.time() < worst_late_beanchmark and duration_start_end.duration_end.time() > worst_late_beanchmark:
                                                        custom_exception_message(self,None,"Please apply full day Your diviation exceeds 4 Hours")
                                                    elif (duration_start_end.duration_start.time() and duration_start_end.duration_end.time()) > worst_late_beanchmark:
                                                        # custom_exception_message(self,None,"Please apply half day Your diviation exceeds 2.5 Hours")
                                                        justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,checkin_benchmark=False,is_requested=False).\
                                                            update(
                                                            request_type=request_type,
                                                            is_requested=True,
                                                            approved_status='pending',
                                                            request_date=datetime.date.today(),
                                                            justified_at=datetime.date.today(),
                                                            justification=validated_data.get('justification'),
                                                            justified_by=updated_by,
                                                            leave_type=validated_data.get('leave_type')
                                                            )

                                                        return validated_data
                                            elif request_type == 'FD' and total_paid_leave['sl_balance']>0.5:
                                                justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,checkin_benchmark=False,is_requested=False).\
                                                    update(
                                                    request_type=request_type,
                                                    is_requested=True,
                                                    approved_status='pending',
                                                    request_date=datetime.date.today(),
                                                    justified_at=datetime.date.today(),
                                                    justification=validated_data.get('justification'),
                                                    justified_by=updated_by,
                                                    leave_type=validated_data.get('leave_type')
                                                    )

                                                return validated_data
                                            else:
                                                custom_exception_message(self,None,"Not enough sick leave balance")
                                        else:
                                            # raise serializers.ValidationError("Sick leave limit exceeds")
                                            custom_exception_message(self,None,"Sick leave limit exceeds")
                                            
                                    elif leave_type =='CL':

                                        if total_paid_leave['cl_balance']>0.0:
                                            duration_length=AttendanceApprovalRequest.objects.get(id=instance.id,checkin_benchmark=False,is_requested=False)
                                            if request_type == 'HD':
                                                if duration_length.duration <=240:
                                                    justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,is_late_conveyance=False,checkin_benchmark=False,is_requested=False).\
                                                            update(
                                                            request_type=request_type,
                                                            is_requested=True,
                                                            approved_status='pending',
                                                            request_date=datetime.date.today(),
                                                            justified_at=datetime.date.today(),
                                                            justification=validated_data.get('justification'),
                                                            justified_by=updated_by,
                                                            leave_type=validated_data.get('leave_type')
                                                            )

                                                    return validated_data
                                                
                                                elif duration_length.duration > 240 :
                                                    if (duration_start_end.duration_start.time() and duration_start_end.duration_end.time()) < worst_late_beanchmark:
                                                        # custom_exception_message(self,None,"Please apply half day Your diviation exceeds 2.5 Hours")
                                                        justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,checkin_benchmark=False,is_requested=False).\
                                                            update(
                                                            request_type=request_type,
                                                            is_requested=True,
                                                            approved_status='pending',
                                                            request_date=datetime.date.today(),
                                                            justified_at=datetime.date.today(),
                                                            justification=validated_data.get('justification'),
                                                            justified_by=updated_by,
                                                            leave_type=validated_data.get('leave_type')
                                                            )

                                                        return validated_data
                                                    elif duration_start_end.duration_start.time() < worst_late_beanchmark and duration_start_end.duration_end.time() > worst_late_beanchmark:
                                                        custom_exception_message(self,None,"Please apply full day Your diviation exceeds 4 Hours")
                                                    elif (duration_start_end.duration_start.time() and duration_start_end.duration_end.time()) > worst_late_beanchmark:
                                                        # custom_exception_message(self,None,"Please apply half day Your diviation exceeds 2.5 Hours")
                                                        justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,checkin_benchmark=False,is_requested=False).\
                                                            update(
                                                            request_type=request_type,
                                                            is_requested=True,
                                                            approved_status='pending',
                                                            request_date=datetime.date.today(),
                                                            justified_at=datetime.date.today(),
                                                            justification=validated_data.get('justification'),
                                                            justified_by=updated_by,
                                                            leave_type=validated_data.get('leave_type')
                                                            )

                                                        return validated_data
                                            elif request_type == 'FD' and total_paid_leave['cl_balance']>0.5:
                                                justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,checkin_benchmark=False,is_requested=False).\
                                                    update(
                                                    request_type=request_type,
                                                    is_requested=True,
                                                    approved_status='pending',
                                                    request_date=datetime.date.today(),
                                                    justified_at=datetime.date.today(),
                                                    justification=validated_data.get('justification'),
                                                    justified_by=updated_by,
                                                    leave_type=validated_data.get('leave_type')
                                                    )

                                                return validated_data
                                            else:
                                                custom_exception_message(self,None,"Not enough casual leave balance")
                                        else:
                                            # raise serializers.ValidationError("casual leave limit exceeds")
                                            custom_exception_message(self,None,"casual leave limit exceeds")
                                    elif leave_type == 'EL':
                                        if total_paid_leave['el_balance']>0.0:
                                            duration_length=AttendanceApprovalRequest.objects.get(id=instance.id,checkin_benchmark=False,is_requested=False)
                                            if request_type == 'HD':
                                                if duration_length.duration <=240:
                                                    justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,checkin_benchmark=False,is_requested=False).\
                                                            update(
                                                            request_type=request_type,
                                                            is_requested=True,
                                                            approved_status='pending',
                                                            request_date=datetime.date.today(),
                                                            justified_at=datetime.date.today(),
                                                            justification=validated_data.get('justification'),
                                                            justified_by=updated_by,
                                                            leave_type=validated_data.get('leave_type')
                                                            )

                                                    return validated_data
                                                elif duration_length.duration > 240:
                                                    if (duration_start_end.duration_start.time() and duration_start_end.duration_end.time()) < worst_late_beanchmark:
                                                        # custom_exception_message(self,None,"Please apply half day Your diviation exceeds 2.5 Hours")
                                                        justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,checkin_benchmark=False,is_requested=False).\
                                                            update(
                                                            request_type=request_type,
                                                            is_requested=True,
                                                            approved_status='pending',
                                                            request_date=datetime.date.today(),
                                                            justified_at=datetime.date.today(),
                                                            justification=validated_data.get('justification'),
                                                            justified_by=updated_by,
                                                            leave_type=validated_data.get('leave_type')
                                                            )

                                                        return validated_data
                                                    elif duration_start_end.duration_start.time() < worst_late_beanchmark and duration_start_end.duration_end.time() > worst_late_beanchmark:
                                                        custom_exception_message(self,None,"Please apply full day Your diviation exceeds 4 Hours")
                                                    elif (duration_start_end.duration_start.time() and duration_start_end.duration_end.time()) > worst_late_beanchmark:
                                                        # custom_exception_message(self,None,"Please apply half day Your diviation exceeds 2.5 Hours")
                                                        justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,checkin_benchmark=False,is_requested=False).\
                                                            update(
                                                            request_type=request_type,
                                                            is_requested=True,
                                                            approved_status='pending',
                                                            request_date=datetime.date.today(),
                                                            justified_at=datetime.date.today(),
                                                            justification=validated_data.get('justification'),
                                                            justified_by=updated_by,
                                                            leave_type=validated_data.get('leave_type')
                                                            )

                                                        return validated_data
                                            
                                            elif request_type == 'FD' and total_paid_leave['el_balance']>0.5:
                                                justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,checkin_benchmark=False,is_requested=False).\
                                                    update(
                                                    request_type=request_type,
                                                    is_requested=True,
                                                    approved_status='pending',
                                                    request_date=datetime.date.today(),
                                                    justified_at=datetime.date.today(),
                                                    justification=validated_data.get('justification'),
                                                    justified_by=updated_by,
                                                    leave_type=validated_data.get('leave_type')
                                                    )

                                                return validated_data
                                            else:
                                                custom_exception_message(self,None,"Not enough earn leave balance")
                                        else:
                                            # raise serializers.ValidationError("Earned leave limit exceeds")
                                            custom_exception_message(self,None,"Earned leave limit exceeds")
                                            
                                    elif leave_type == 'AB':
                                        justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,checkin_benchmark=False,is_requested=False).\
                                                    update(
                                                    request_type=request_type,
                                                    is_requested=True,
                                                    approved_status='pending',
                                                    request_date=datetime.date.today(),
                                                    justified_at=datetime.date.today(),
                                                    justification=validated_data.get('justification'),
                                                    justified_by=updated_by,
                                                    leave_type=validated_data.get('leave_type')
                                                    )

                                        return validated_data
                            else:
                                total_paid_leave['granted_cl']=core_user_detail[0]['granted_cl']
                                total_paid_leave['cl_balance']=float(core_user_detail[0]['granted_cl']) - float(availed_cl_data)
                                total_paid_leave['granted_el']=core_user_detail[0]['granted_el']
                                total_paid_leave['el_balance']=float(core_user_detail[0]['granted_el']) - float(availed_el_data)
                                total_paid_leave['granted_sl']=core_user_detail[0]['granted_sl']
                                total_paid_leave['sl_balance']=float(core_user_detail[0]['granted_sl']) - float(availed_sl_data)
                                total_paid_leave['total_granted_leave']=float(core_user_detail[0]['granted_cl']) + float(core_user_detail[0]['granted_el']) + float(core_user_detail[0]['granted_sl'])
                                total_paid_leave['total_leave_balances']=float(total_paid_leave['total_granted_leave']) - float(total_paid_leave['total_availed_leave'])
                                print("total_paid_leave",total_paid_leave)
                                #**********HALF DAY OR FULL DAY LEAVE CALCULATION Regular *************************
                                if request_type == 'HD' or request_type == 'FD':
                                    if  leave_type == 'SL' :
                                        
                                        if total_paid_leave['sl_balance']>0.0:
                                            duration_length=AttendanceApprovalRequest.objects.get(id=instance.id,checkin_benchmark=False,is_requested=False)
                                            if request_type == 'HD':
                                                if duration_length.duration <=240 :
                                                    # raise serializers.ValidationError("Please apply half day Your diviation exceeds 2.5 Hours")
                                            
                                                    justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,checkin_benchmark=False,is_requested=False).\
                                                            update(
                                                            request_type=request_type,
                                                            is_requested=True,
                                                            approved_status='pending',
                                                            request_date=datetime.date.today(),
                                                            justified_at=datetime.date.today(),
                                                            justification=validated_data.get('justification'),
                                                            justified_by=updated_by,
                                                            leave_type=validated_data.get('leave_type')
                                                            )

                                                    return validated_data

                                                elif duration_length.duration > 240 :
                                                    if (duration_start_end.duration_start.time() and duration_start_end.duration_end.time()) < worst_late_beanchmark:
                                                        # custom_exception_message(self,None,"Please apply half day Your diviation exceeds 2.5 Hours")
                                                        justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,checkin_benchmark=False,is_requested=False).\
                                                            update(
                                                            request_type=request_type,
                                                            is_requested=True,
                                                            approved_status='pending',
                                                            request_date=datetime.date.today(),
                                                            justified_at=datetime.date.today(),
                                                            justification=validated_data.get('justification'),
                                                            justified_by=updated_by,
                                                            leave_type=validated_data.get('leave_type')
                                                            )

                                                        return validated_data
                                                    elif duration_start_end.duration_start.time() < worst_late_beanchmark and duration_start_end.duration_end.time() > worst_late_beanchmark:
                                                        custom_exception_message(self,None,"Please apply full day Your diviation exceeds 4 Hours")
                                                    elif (duration_start_end.duration_start.time() and duration_start_end.duration_end.time()) > worst_late_beanchmark:
                                                        # custom_exception_message(self,None,"Please apply half day Your diviation exceeds 2.5 Hours")
                                                        justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,checkin_benchmark=False,is_requested=False).\
                                                            update(
                                                            request_type=request_type,
                                                            is_requested=True,
                                                            approved_status='pending',
                                                            request_date=datetime.date.today(),
                                                            justified_at=datetime.date.today(),
                                                            justification=validated_data.get('justification'),
                                                            justified_by=updated_by,
                                                            leave_type=validated_data.get('leave_type')
                                                            )

                                                        return validated_data
                                            elif request_type == 'FD' and total_paid_leave['sl_balance']>0.5:
                                                justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,checkin_benchmark=False,is_requested=False).\
                                                    update(
                                                    request_type=request_type,
                                                    is_requested=True,
                                                    approved_status='pending',
                                                    request_date=datetime.date.today(),
                                                    justified_at=datetime.date.today(),
                                                    justification=validated_data.get('justification'),
                                                    justified_by=updated_by,
                                                    leave_type=validated_data.get('leave_type')
                                                    )
                                                return validated_data
                                            else:
                                                custom_exception_message(self,None,"Not enough sick leave balance")
                                                
                                        else:
                                            # raise serializers.ValidationError("Sick leave limit exceeds")
                                            custom_exception_message(self,None,"Sick leave limit exceeds")
                                            
                                    elif leave_type =='CL':
                                        if total_paid_leave['cl_balance']>0.0:
                                            duration_length=AttendanceApprovalRequest.objects.get(id=instance.id,checkin_benchmark=False,is_requested=False)
                                            if request_type == 'HD':
                                                if  duration_length.duration <=240:
                                                    justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,is_late_conveyance=False,checkin_benchmark=False,is_requested=False).\
                                                            update(
                                                            request_type=request_type,
                                                            is_requested=True,
                                                            approved_status='pending',
                                                            request_date=datetime.date.today(),
                                                            justified_at=datetime.date.today(),
                                                            justification=validated_data.get('justification'),
                                                            justified_by=updated_by,
                                                            leave_type=validated_data.get('leave_type')
                                                            )

                                                    return validated_data
                                                
                                                elif duration_length.duration > 240 :
                                                    if (duration_start_end.duration_start.time() and duration_start_end.duration_end.time()) < worst_late_beanchmark:
                                                        # custom_exception_message(self,None,"Please apply half day Your diviation exceeds 2.5 Hours")
                                                        justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,checkin_benchmark=False,is_requested=False).\
                                                            update(
                                                            request_type=request_type,
                                                            is_requested=True,
                                                            approved_status='pending',
                                                            request_date=datetime.date.today(),
                                                            justified_at=datetime.date.today(),
                                                            justification=validated_data.get('justification'),
                                                            justified_by=updated_by,
                                                            leave_type=validated_data.get('leave_type')
                                                            )

                                                        return validated_data
                                                    elif duration_start_end.duration_start.time() < worst_late_beanchmark and duration_start_end.duration_end.time() > worst_late_beanchmark:
                                                        custom_exception_message(self,None,"Please apply full day Your diviation exceeds 4 Hours")
                                                    elif (duration_start_end.duration_start.time() and duration_start_end.duration_end.time()) > worst_late_beanchmark:
                                                        # custom_exception_message(self,None,"Please apply half day Your diviation exceeds 2.5 Hours")
                                                        justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,checkin_benchmark=False,is_requested=False).\
                                                            update(
                                                            request_type=request_type,
                                                            is_requested=True,
                                                            approved_status='pending',
                                                            request_date=datetime.date.today(),
                                                            justified_at=datetime.date.today(),
                                                            justification=validated_data.get('justification'),
                                                            justified_by=updated_by,
                                                            leave_type=validated_data.get('leave_type')
                                                            )

                                                        return validated_data
                                            elif request_type == 'FD' and total_paid_leave['cl_balance']>0.5:
                                                justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,checkin_benchmark=False,is_requested=False).\
                                                    update(
                                                    request_type=request_type,
                                                    is_requested=True,
                                                    approved_status='pending',
                                                    request_date=datetime.date.today(),
                                                    justified_at=datetime.date.today(),
                                                    justification=validated_data.get('justification'),
                                                    justified_by=updated_by,
                                                    leave_type=validated_data.get('leave_type')
                                                    )

                                                return validated_data
                                            else:
                                                custom_exception_message(self,None,"Not enough casual leave balance")
                                        else:
                                            # raise serializers.ValidationError("casual leave limit exceeds")
                                            custom_exception_message(self,None,"casual leave limit exceeds")
                                    elif leave_type =='EL':
                                        if total_paid_leave['el_balance']>0.0:
                                            duration_length=AttendanceApprovalRequest.objects.get(id=instance.id,checkin_benchmark=False,is_requested=False)
                                            if request_type == 'HD':
                                                if  duration_length.duration <=240:
                                                    justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,checkin_benchmark=False,is_requested=False).\
                                                            update(
                                                            request_type=request_type,
                                                            is_requested=True,
                                                            approved_status='pending',
                                                            request_date=datetime.date.today(),
                                                            justified_at=datetime.date.today(),
                                                            justification=validated_data.get('justification'),
                                                            justified_by=updated_by,
                                                            leave_type=validated_data.get('leave_type')
                                                            )

                                                    return validated_data
                                                elif duration_length.duration > 240:
                                                    if (duration_start_end.duration_start.time() and duration_start_end.duration_end.time()) < worst_late_beanchmark:
                                                        # custom_exception_message(self,None,"Please apply half day Your diviation exceeds 2.5 Hours")
                                                        justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,checkin_benchmark=False,is_requested=False).\
                                                            update(
                                                            request_type=request_type,
                                                            is_requested=True,
                                                            approved_status='pending',
                                                            request_date=datetime.date.today(),
                                                            justified_at=datetime.date.today(),
                                                            justification=validated_data.get('justification'),
                                                            justified_by=updated_by,
                                                            leave_type=validated_data.get('leave_type')
                                                            )

                                                        return validated_data
                                                    elif duration_start_end.duration_start.time() < worst_late_beanchmark and duration_start_end.duration_end.time() > worst_late_beanchmark:
                                                        custom_exception_message(self,None,"Please apply full day Your diviation exceeds 4 Hours")
                                                    elif (duration_start_end.duration_start.time() and duration_start_end.duration_end.time()) > worst_late_beanchmark:
                                                        # custom_exception_message(self,None,"Please apply half day Your diviation exceeds 2.5 Hours")
                                                        justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,checkin_benchmark=False,is_requested=False).\
                                                            update(
                                                            request_type=request_type,
                                                            is_requested=True,
                                                            approved_status='pending',
                                                            request_date=datetime.date.today(),
                                                            justified_at=datetime.date.today(),
                                                            justification=validated_data.get('justification'),
                                                            justified_by=updated_by,
                                                            leave_type=validated_data.get('leave_type')
                                                            )

                                                        return validated_data
                                            
                                            elif request_type == 'FD' and total_paid_leave['el_balance']>0.5:
                                                justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,checkin_benchmark=False,is_requested=False).\
                                                    update(
                                                    request_type=request_type,
                                                    is_requested=True,
                                                    approved_status='pending',
                                                    request_date=datetime.date.today(),
                                                    justified_at=datetime.date.today(),
                                                    justification=validated_data.get('justification'),
                                                    justified_by=updated_by,
                                                    leave_type=validated_data.get('leave_type')
                                                    )

                                                return validated_data
                                        else:
                                            # raise serializers.ValidationError("Earned leave limit exceeds")
                                            custom_exception_message(self,None,"Earned leave limit exceeds")
                                    elif leave_type == 'AB':
                                        justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,checkin_benchmark=False,is_requested=False).\
                                                    update(
                                                    request_type=request_type,
                                                    is_requested=True,
                                                    approved_status='pending',
                                                    request_date=datetime.date.today(),
                                                    justified_at=datetime.date.today(),
                                                    justification=validated_data.get('justification'),
                                                    justified_by=updated_by,
                                                    leave_type=validated_data.get('leave_type')
                                                    )

                                        return validated_data
                    
                    
                    
                    elif request_type == 'OD':          
                        vehicle_type= validated_data.get('vehicle_type') if validated_data.get('vehicle_type') else None
                        from_place= validated_data.get('from_place') if validated_data.get('from_place') else None
                        to_place= validated_data.get('to_place') if validated_data.get('to_place') else None
                        conveyance_expense= validated_data.get('conveyance_expense') if validated_data.get('conveyance_expense') else 0.0
                        conveyance_remarks= validated_data.get('conveyance_remarks') if validated_data.get('conveyance_remarks') else None
                        conveyance_alloted_by= validated_data.get('conveyance_alloted_by') if validated_data.get('conveyance_alloted_by') else None

                        if from_place or to_place or conveyance_remarks:
                            justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,is_requested=False).\
                                update(
                                request_type='FOD',
                                is_requested=True,
                                approved_status='pending',
                                request_date=datetime.date.today(),
                                justified_at=datetime.date.today(),
                                justification=validated_data.get('justification'),
                                justified_by=updated_by,
                                is_conveyance=True,
                                vehicle_type_id=vehicle_type,
                                from_place=from_place,
                                to_place=to_place,
                                conveyance_alloted_by_id=conveyance_alloted_by,
                                conveyance_expense=conveyance_expense,
                                conveyance_remarks=conveyance_remarks
                                )

                            return validated_data
                        else:
                            justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,checkin_benchmark=False,is_requested=False).\
                                update(
                                request_type='FOD',
                                is_requested=True,
                                approved_status='pending',
                                request_date=datetime.date.today(),
                                justified_at=datetime.date.today(),
                                justification=validated_data.get('justification'),
                                justified_by=updated_by,
                                is_conveyance=False,
                                )
                            data=AttendanceApprovalRequest.objects.get(id=instance.id)

                            return validated_data
                    
                    
                    
                    #*****************Request for mispunch************************************************************************************
                    elif request_type == 'MP': 
                        justify_attendence=AttendanceApprovalRequest.objects.filter(id=instance.id,checkin_benchmark=False,is_requested=False).\
                                update(
                                request_type=request_type,
                                is_requested=True,
                                approved_status='pending',
                                request_date=datetime.date.today(),
                                justified_at=datetime.date.today(),
                                justification=validated_data.get('justification'),
                                justified_by=updated_by)

                        return validated_data
                    
                    return validated_data

        except Exception as e:
            raise e

class AttendanceGraceLeaveListSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceApprovalRequest
        fields = '__all__'

# class AttendanceGraceLeaveListModifiedSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = AttendanceApprovalRequest
#         fields = '__all__'
                
class AttendanceLateConveyanceApplySerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = AttendanceApprovalRequest
        fields = ('id','vehicle_type','from_place','to_place','conveyance_expense','conveyance_purpose','conveyance_alloted_by','updated_by')

    def update(self,instance,validated_data):
        try:
            # print("instance",instance.__dict__)
            if instance.__dict__['is_late_conveyance'] is True:
                instance.vehicle_type = validated_data.get('vehicle_type')
                instance.from_place = validated_data.get('from_place')
                instance.to_place = validated_data.get('to_place')
                instance.conveyance_expense = validated_data.get('conveyance_expense')
                instance.conveyance_purpose=validated_data.get('conveyance_purpose')
                instance.conveyance_alloted_by=validated_data.get('conveyance_alloted_by')
                instance.conveyance_approval = 0
                instance.updated_by = validated_data.get('updated_by')
                instance.save()
            return instance
        except Exception as e:
            raise e

class AttendanceConveyanceApprovalListSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceApprovalRequest
        fields = ('id','is_conveyance','is_late_conveyance','conveyance_approval','vehicle_type',
        'conveyance_purpose','conveyance_alloted_by','from_place','to_place','conveyance_expense',
        'approved_expenses','conveyance_remarks','attendance','duration_start','duration_end','duration',
        'conveyance_approved_by','updated_by')

    # def create(self,validated_data):
    #     '''
    #         1)Admin can provide mass update by selecting as much request he wanted 
    #     '''
        
    #     updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    #     for data in validated_data:
    #         conveyance_approval= data['conveyance_approval']
    #         approved_expenses=data['approved_expenses']

    #         if conveyance_approval == 3 :
    #             AttendanceApprovalRequest.objects.filter(id=data['req_id']).update(conveyance_approval=conveyance_approval,
    #                                                                     conveyance_approved_by=updated_by,approved_expenses=approved_expenses)
    #         else:
    #             AttendanceApprovalRequest.objects.filter(id=req_id).update(conveyance_approval=conveyance_approval,
    #                                                                         conveyance_approved_by=updated_by)
    #         # print(AttendanceApprovalRequest.)
    #         if AttendanceApprovalRequest:

    #             return Response({'results': {'conveyance_approval': conveyance_approval, },
    #                             'msg': 'success',
    #                             "request_status": 1})
    #         else:
    #             return Response({'results': {'conveyance_approval': conveyance_approval, },
    #                             'msg': 'fail',
    #                             "request_status": 0})


class AttendanceSummaryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = '__all__'

class AttendanceDailyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = '__all__'

#:::::::::::::::::::::::::::ATTENDANCE ADVANCE LEAVE::::::::::::::::::::::::::::#

class AttendanceAdvanceLeaveListSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeAdvanceLeaves
        fields = '__all__'

class AdminAttendanceAdvanceLeavePendingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeAdvanceLeaves
        fields = '__all__'

class AdminAttendanceAdvanceLeaveApprovalSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    advance_leaves_approvals= serializers.ListField(required=False)

    class Meta:
        model = EmployeeAdvanceLeaves
        fields = ('id', 'approved_status', 'remarks','updated_by','advance_leaves_approvals')

    def create(self,validated_data):
        '''
            1)Admin can provide mass update by selecting as much request he wanted 
        '''

        print(validated_data)
        updated_by = validated_data.get('updated_by')
        remarks = validated_data.get('remarks')
        # master_module_role = TMasterModuleRoleUser.objects.get(mmr_module__cm_name__iexact='hrms',mmr_user=self.context['request'].user).mmr_role
        # core_role = TCoreRole.objects.get(id=str(master_module_role)).cr_name
        for data in validated_data.get('advance_leaves_approvals'):
            approved_status= data['approved_status']
            req_type = EmployeeAdvanceLeaves.objects.get(id=data['req_id'])
            EmployeeAdvanceLeaves.objects.filter(id=data['req_id']).update(approved_status=approved_status,
                                                                    updated_by=updated_by,remarks=remarks)
        
            # if core_role.lower() == 'hr admin':
            logger.log(self.context['request'].user,approved_status+" "+req_type.leave_type,
                'Approval','pending',approved_status,'HRMS-TeamAttendance-LeaveApproval') 
            # elif core_role.lower() == 'hr user':
            #     logger.log(self.context['request'].user,AttendenceAction.ACTION_HR,'rejected'+" "+req_type.leave_type,
            #     'Approval','pending',approved_status,'HRMS-TeamAttendance-LeaveApproval')

        data = validated_data

        return data
    
    # def update(self,instance,validated_data):
    #     try:
    #         instance.approved_status = validated_data.get('approved_status')
    #         instance.remarks = validated_data.get('remarks')
    #         instance.updated_by = validated_data.get('updated_by')
    #         instance.save()
    #         return instance
    #     except Exception as e:
    #         raise e

class AttendanceAdvanceLeaveAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = EmployeeAdvanceLeaves
        fields = '__all__'

    def is2ndOr4thSaturday(self,date1):
        # if date1 is string then you convert the string to date object
        dt = datetime.datetime.strptime(date1, '%Y-%m-%d')
        year = dt.year
        month =  dt.month
        # print('year',year)
        # print('month',month)
        month_calender = calendar.monthcalendar(year, month)
        second_fourth_saturday = (1, 3) if month_calender[0][calendar.SATURDAY] else (2, 4)
        return any(dt.day == month_calender[i][calendar.SATURDAY] for i in second_fourth_saturday)
        
    def leaveDaysCountWithOutHoliday(self,date1, date2):
        request_leave_days = (date2 - date1).days + 1
        #print('request_leave_days',request_leave_days)
        holiday_count = 0
        for dt in self.daterange(date1, date2):
            #print(dt.strftime("%A"))
            day = dt.strftime("%A")
            '''
            Modified By :: Rajesh Samui
            Reason :: State Wise Holiday Calculation
            Line :: 2180-2182
            Date :: 10-02-2020
            '''
            #holiday_details = HolidaysList.objects.filter(holiday_date = dt.strftime("%Y-%m-%d"))
            user = self.context['request'].user
            state_obj = TCoreUserDetail.objects.get(cu_user=user).job_location_state
            default_state = TCoreState.objects.filter(cs_state_name__iexact='west bengal').first()
            t_core_state_id = state_obj.id if state_obj else default_state.id
            holiday_details = HolidayStateMapping.objects.filter(Q(holiday__holiday_date=dt.strftime("%Y-%m-%d"))&Q(state__id=t_core_state_id))
            if holiday_details or day == 'Sunday':
                holiday_count = holiday_count + 1
        
        #print('holiday_count',holiday_count)
        days_count = request_leave_days - holiday_count
        #print('days_count',days_count)
        return days_count   

    def daterange(self,date1, date2):
        for n in range(int ((date2 - date1).days)+1):
            yield date1 + timedelta(n)

    def getMonthsAndDaysBetweenDateRange(self,date1, date2):
        month_details = list()
        months = set()
        for dt in self.daterange(date1, date2):
            month_de = dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            month_de = calendar.month_name[datetime.datetime.strptime(month_de,"%Y-%m-%dT%H:%M:%S.%fZ").month]
            months.add(month_de)
        #print('months',months)
        for month in months:
            days = self.getDaysByMonth(month,date1, date2)
            month_details.append({
                'month':month,
                'days':days
            })
        return month_details

    def getDaysByMonth(self,month,date1, date2):
        days = 0
        for dt in self.daterange(date1, date2):
            month_de = dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            month_de = calendar.month_name[datetime.datetime.strptime(month_de,"%Y-%m-%dT%H:%M:%S.%fZ").month]
            day = dt.strftime("%A")
            '''
            Modified By :: Rajesh Samui
            Reason :: State Wise Holiday Calculation
            Line :: 2223-2225
            Date :: 10-02-2020
            '''
            #holiday_details = HolidaysList.objects.filter(holiday_date = dt.strftime("%Y-%m-%d"))
            user = self.context['request'].user
            state_obj = TCoreUserDetail.objects.get(cu_user=user).job_location_state
            default_state = TCoreState.objects.filter(cs_state_name__iexact='west bengal').first()
            t_core_state_id = state_obj.id if state_obj else default_state.id
            holiday_details = HolidayStateMapping.objects.filter(Q(holiday__holiday_date=dt.strftime("%Y-%m-%d"))&Q(state__id=t_core_state_id))
            if not holiday_details or day != 'Sunday':
                if month == month_de:
                    days = days + 1
        return days
        

    def create(self, validated_data):

        '''
            This Method prepared by @@ Rupam Hazra. Any kind of issues occurred, ask me first !!!

            Note :: 
            1) Used Date Format : yyyy-mm-dd
            2) Checking Start Date should not less than today's date!
            3) End Date should be greater than or euqual to start date!
            4) You can't apply 3 CL for same month!
            5) You have already taken 3 CL for same month!
            6) You requested leaves has not been granted, due to insufficient EL/CL
            7) Check 2nd and 4th satuday off by is2ndOr4thSaturday method
            8) Normal Leave Count and Advance Leave Count From Approval Request Table
        '''

        current_date = datetime.date.today()
        #print('current_date ::::',current_date)
        request_datetime = validated_data.get('start_date').strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        request_datetime = datetime.datetime.strptime(request_datetime,"%Y-%m-%dT%H:%M:%S.%fZ").date()


        request_end_datetime = validated_data.get('end_date').strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        request_end_datetime = datetime.datetime.strptime(request_end_datetime,"%Y-%m-%dT%H:%M:%S.%fZ").date()

        #request_how_many_days_cl = 0.0
        #request_how_many_days_el = 0.0
        how_many_days_cl_taken_on_same_month = 0.0
        balance_el = 0.0
        balance_cl = 0.0
        balance_ab = 0.0
        how_many_days_cl_taken = 0.0
        how_many_days_el_taken = 0.0
        how_many_days_ab_taken = 0.0
        
        # leaveDaysCountWithOutHoliday = self.leaveDaysCountWithOutHoliday(
        #     validated_data.get('start_date'),validated_data.get('end_date'))
        # print('leaveDaysCountWithOutHoliday',leaveDaysCountWithOutHoliday)

        request_how_many_days = (validated_data.get('end_date') - validated_data.get('start_date')).days + 1
        print('request_how_many_days',request_how_many_days)

        request_start_date_month = validated_data.get('start_date').strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        request_start_date_month = calendar.month_name[datetime.datetime.strptime(request_start_date_month,"%Y-%m-%dT%H:%M:%S.%fZ").month]
        
        #print('request_start_date_month',request_start_date_month)

        request_end_date_month = validated_data.get('end_date').strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        request_end_date_month = calendar.month_name[datetime.datetime.strptime(request_end_date_month,"%Y-%m-%dT%H:%M:%S.%fZ").month]
        
        #print('request_end_date_month',request_end_date_month)

        if request_datetime < current_date :
            custom_exception_message(self,None,"Start Date should not less than today's date!")
        
        if request_datetime > request_end_datetime:
            custom_exception_message(self,None,"End Date should be greater than or euqual to start date!")


        getMonthsAndDaysBetweenDateRange = self.getMonthsAndDaysBetweenDateRange(validated_data.get('start_date'),validated_data.get('end_date'))
        #print('getMonthsAndDaysBetweenDateRange',getMonthsAndDaysBetweenDateRange)

        if validated_data.get('leave_type') == 'CL':
            '''
                Checking You can't apply 3 CL for same month!
            '''
            for e_getMonthsAndDaysBetweenDateRange in getMonthsAndDaysBetweenDateRange:
                if e_getMonthsAndDaysBetweenDateRange['days'] > 3:
                    custom_exception_message(self,'',"You can't apply 3 CL for same month!")
                

        if validated_data.get('leave_type') == 'CL' and request_start_date_month == request_end_date_month :
            how_many_days_cl_taken_on_same_month = request_how_many_days

        # userdetails from TCoreUserDetail
        empDetails_from_coreuserdetail = TCoreUserDetail.objects.filter(
            cu_user=validated_data.get('employee'))[0]
        #print('empDetails_from_coreuserdetail',empDetails_from_coreuserdetail)
        employee_id = validated_data.get('employee')

        if empDetails_from_coreuserdetail:
            '''
                Normal Leave Count From approval request
            '''
            #starttime = datetime.now()
            availed_hd_cl=0.0
            availed_hd_el=0.0
            availed_hd_sl=0.0
            availed_hd_ab=0.0
            availed_cl=0.0
            availed_el=0.0
            availed_sl=0.0
            availed_ab=0.0
            attendence_daily_data = AttendanceApprovalRequest.objects.filter(((
                Q(leave_type_changed_period__isnull=False)&(Q(leave_type_changed_period='FD')|Q(leave_type_changed_period='HD')))|
                                                                        (Q(leave_type_changed_period__isnull=True)&(Q(request_type='FD')|Q(request_type='HD')))),
                                                                        attendance__employee=employee_id,is_requested=True).values('duration_start__date').distinct()
            #print("attendence_daily_data",attendence_daily_data)
            date_list = [x['duration_start__date'] for x in attendence_daily_data.iterator()]
            #print("date_list",date_list)
            
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
            #print('availed_master_wo_reject_fd',availed_master_wo_reject_fd)
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
                            # elif l_type == 'SL':
                            #     availed_sl=availed_sl+1.0
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
                            # elif l_type == 'SL':
                            #     availed_hd_sl=availed_hd_sl+1.0
                            elif l_type == 'AB':
                                availed_hd_ab=availed_hd_ab+1.0
            
            '''
                Advance Leave Calculation 
            '''

            last_attendence_date = AttendanceApprovalRequest.objects.all().values_list(
                'attendance_date',flat=True).order_by('-attendance_date')[0]
            print('last_attendence_date',last_attendence_date)

            joining_date = empDetails_from_coreuserdetail.joining_date
            #print('joining_date',joining_date)
            attendence_month_masters = AttendenceMonthMaster.objects.filter(
                year_start_date__gt = joining_date,
                year_end_date__lt = joining_date).order_by('-year_start_date')
            #print('attendence_month_masters',attendence_month_masters)

            if attendence_month_masters:
                joining_approved_leaves = JoiningApprovedLeave.objects.filter(
                    employee=validated_data.get('employee'))
                #print('joining_approved_leaves',joining_approved_leaves)
                if joining_approved_leaves:
                    joining_approved_leaves = JoiningApprovedLeave.objects.filter(
                    employee=validated_data.get('employee'))[0]
                    granted_cl = joining_approved_leaves.cl
                    #granted_sl = joining_approved_leaves.sl
                    granted_el = joining_approved_leaves.el
            else:
                granted_cl = empDetails_from_coreuserdetail.granted_cl
                #granted_sl = empDetails_from_coreuserdetail.granted_sl
                granted_el = empDetails_from_coreuserdetail.granted_el

            # total_granted_leave = (granted_cl + granted_sl + granted_el)
            # print('total_granted_leave',total_granted_leave)

            empDetails_from_advance_leave = EmployeeAdvanceLeaves.objects.filter(
                (Q(approved_status = 'pending') | Q(approved_status = 'approved')),
                 employee=validated_data.get('employee'),is_deleted=False,
                 start_date__date__gte = last_attendence_date,
                 end_date__date__gte = last_attendence_date,
                 
                )
            print('empDetails_from_advance_leave',empDetails_from_advance_leave)
            if empDetails_from_advance_leave:

                for e_empDetails_from_advance_leave in empDetails_from_advance_leave:

                    if e_empDetails_from_advance_leave.leave_type == 'CL':
                        '''
                            Checking taken cl not greater than 3 in a month
                        '''
                        start_month_details = calendar.month_name[datetime.datetime.strptime(
                            e_empDetails_from_advance_leave.start_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                            "%Y-%m-%dT%H:%M:%S.%fZ").month]
                        
                        #print('start_month_details',start_month_details)

                        end_month_details = calendar.month_name[datetime.datetime.strptime(
                            e_empDetails_from_advance_leave.end_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                            "%Y-%m-%dT%H:%M:%S.%fZ").month]
                        
                        #print('end_month_details',end_month_details)

                        if (start_month_details == request_start_date_month and start_month_details == request_end_date_month) or(
                            end_month_details == request_start_date_month and end_month_details == request_end_date_month):

                            how_many_days_cl_taken_on_same_month = how_many_days_cl_taken_on_same_month + (e_empDetails_from_advance_leave.end_date - 
                            e_empDetails_from_advance_leave.start_date).days + 1

                        #print('how_many_days_cl_taken_on_same_month:::',how_many_days_cl_taken_on_same_month)
                        how_many_days_cl_taken = how_many_days_cl_taken + (e_empDetails_from_advance_leave.end_date - 
                                e_empDetails_from_advance_leave.start_date).days + 1
                        
                        #print('how_many_days_cl_taken:::::',how_many_days_cl_taken)

                    if e_empDetails_from_advance_leave.leave_type == 'EL':
                        how_many_days_el_taken = how_many_days_el_taken + (e_empDetails_from_advance_leave.end_date - 
                            e_empDetails_from_advance_leave.start_date).days + 1
                        #print('how_many_days_el_taken:::::',how_many_days_el_taken)
                    
                    if e_empDetails_from_advance_leave.leave_type == 'AB':
                        how_many_days_ab_taken = how_many_days_ab_taken + (e_empDetails_from_advance_leave.end_date - 
                            e_empDetails_from_advance_leave.start_date).days + 1
                        #print('how_many_days_ab_taken:::::',how_many_days_ab_taken)

                if how_many_days_cl_taken_on_same_month > 3:
                    custom_exception_message(self,'',"You can't apply 3 CL for same month!")

            '''
                Section for count total cl and el count which means 
                total of advance leaves and approval leave
            '''
            print('how_many_days_cl_taken',how_many_days_cl_taken)
            print('how_many_days_el_taken',how_many_days_el_taken)
            # print('how_many_days_ab_taken',how_many_days_ab_taken)

            print("availed_cl",availed_cl)
            print("availed_el",availed_el)

            total_availed_cl=float(availed_cl)+float(how_many_days_cl_taken)+float(availed_hd_cl/2)
            print("total_availed_cl",total_availed_cl)
            total_availed_el=float(availed_el)+float(how_many_days_el_taken)+float(availed_hd_el/2)
            print("total_availed_el",total_availed_el)

            print('granted_cl',granted_cl)
            print('granted_el',granted_el)

            '''
                Section for count balance cl and el count which means 
                remaining leaves from granted leave - availed leave
            '''

            balance_cl = float(granted_cl) - float(total_availed_cl)
            print('balance_cl',balance_cl)
            balance_el = float(granted_el) - float(total_availed_el)
            print('balance_el',balance_el)

            # availed_sl=float(availed_sl)+float(availed_hd_sl/2)
            # print("availed_sl",availed_sl)
            # availed_ab=float(availed_ab)+float(how_many_days_ab_taken)+float(availed_hd_ab/2)
            # print("availed_ab",availed_ab)
            # total_availed_leave=availed_cl +availed_el + availed_sl
            # print('total_availed_leave',total_availed_leave)

            '''
                Validation on CL or EL modified
            '''

            #holiday_count = 0
            
            if validated_data.get('leave_type') == 'CL':
                #request_how_many_days_cl = request_how_many_days
                # for dt in self.daterange(validated_data.get('start_date'), validated_data.get('end_date')):
                #     #print(dt.strftime("%A"))
                #     day = dt.strftime("%A")
                #     holiday_details = HolidaysList.objects.filter(holiday_date = dt.strftime("%Y-%m-%d"))

                #     if (holiday_details or day == 'Saturday')  and empDetails_from_coreuserdetail.is_saturday_off:
                #         if  day == 'Saturday' and self.is2ndOr4thSaturday(dt.strftime("%Y-%m-%d")) == False:
                #             holiday_count = holiday_count + 1
                #         else:
                #             holiday_count = holiday_count
                    
                # #print('holiday_count',holiday_count)
                # if leaveDaysCountWithOutHoliday > 6 and holiday_count > 0 :
                #     request_how_many_days_cl = leaveDaysCountWithOutHoliday + holiday_count
                # else:
                #     request_how_many_days_cl = leaveDaysCountWithOutHoliday

                #print('request_how_many_days_cl111',request_how_many_days_cl)
                if request_how_many_days > balance_cl:
                    custom_exception_message(self,None,"You requested leaves has not been granted, due to insufficient CL")

            if validated_data.get('leave_type') == 'EL':
                #request_how_many_days_el = request_how_many_days
                # for dt in self.daterange(validated_data.get('start_date'), validated_data.get('end_date')):
                #     #print(dt.strftime("%A"))
                #     day = dt.strftime("%A")
                #     holiday_details = HolidaysList.objects.filter(holiday_date = dt.strftime("%Y-%m-%d"))

                #     if (holiday_details or day == 'Saturday')  and empDetails_from_coreuserdetail.is_saturday_off:
                #         if  day == 'Saturday' and self.is2ndOr4thSaturday(dt.strftime("%Y-%m-%d")) == False:
                #             holiday_count = holiday_count + 1
                #         else:
                #             holiday_count = holiday_count
                    
                # #print('holiday_count',holiday_count)
                # if leaveDaysCountWithOutHoliday > 6 and holiday_count > 0 :
                #     request_how_many_days_el = leaveDaysCountWithOutHoliday + holiday_count
                # else:
                #     request_how_many_days_el = leaveDaysCountWithOutHoliday
                
                # print('request_how_many_days_el',request_how_many_days_el)

                if request_how_many_days > balance_el:
                    custom_exception_message(self,None,"You requested leaves has not been granted, due to insufficient EL")
                
        return super().create(validated_data)

class ETaskAttendanceApprovalListSerializer(serializers.ModelSerializer):
    employee_name=serializers.SerializerMethodField(required=False)
    employee_id=serializers.SerializerMethodField(required=False) 
    def get_employee_name(self,AttendanceApprovalRequest):
        if AttendanceApprovalRequest.attendance:
            first_name=AttendanceApprovalRequest.attendance.employee.first_name if AttendanceApprovalRequest.attendance.employee.first_name  else ''
            last_name=AttendanceApprovalRequest.attendance.employee.last_name if AttendanceApprovalRequest.attendance.employee.last_name else ''
            name=first_name+" "+last_name
            return name
    def get_employee_id(self,AttendanceApprovalRequest):
        if AttendanceApprovalRequest.attendance:
            return AttendanceApprovalRequest.attendance.employee.id
    class Meta:
        model = AttendanceApprovalRequest
        fields = '__all__'
        extra_fields=('employee_name','employee_id')

class ETaskAttendanceApprovalGraceListSerializer(serializers.ModelSerializer):
    employee_name=serializers.SerializerMethodField(required=False)
    employee_id=serializers.SerializerMethodField(required=False) 
    def get_employee_name(self,AttendanceApprovalRequest):
        if AttendanceApprovalRequest.attendance:
            first_name=AttendanceApprovalRequest.attendance.employee.first_name if AttendanceApprovalRequest.attendance.employee.first_name  else ''
            last_name=AttendanceApprovalRequest.attendance.employee.last_name if AttendanceApprovalRequest.attendance.employee.last_name else ''
            name=first_name+" "+last_name
            return name
    def get_employee_id(self,AttendanceApprovalRequest):
        if AttendanceApprovalRequest.attendance:
            return AttendanceApprovalRequest.attendance.employee.id
    class Meta:
        model = AttendanceApprovalRequest
        fields = '__all__'
        extra_fields=('employee_name','employee_id')


class ETaskAttendanceApprovaWithoutGracelSerializer(serializers.ModelSerializer):
    employee_name=serializers.SerializerMethodField(required=False)
    employee_id=serializers.SerializerMethodField(required=False) 
    def get_employee_name(self,AttendanceApprovalRequest):
        if AttendanceApprovalRequest.attendance:
            first_name=AttendanceApprovalRequest.attendance.employee.first_name if AttendanceApprovalRequest.attendance.employee.first_name  else ''
            last_name=AttendanceApprovalRequest.attendance.employee.last_name if AttendanceApprovalRequest.attendance.employee.last_name else ''
            name=first_name+" "+last_name
            return name
    def get_employee_id(self,AttendanceApprovalRequest):
        if AttendanceApprovalRequest.attendance:
            return AttendanceApprovalRequest.attendance.employee.id
    class Meta:
        model = AttendanceApprovalRequest
        fields = '__all__'
        extra_fields=('employee_name','employee_id')

class ETaskAttendanceApprovalSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    attendence_approvals=serializers.ListField(required=False)
    
    class Meta:
        model = AttendanceApprovalRequest
        fields = ('id','updated_by','remarks','approved_status','attendence_approvals')
        # extra_fields=('attendence_approvals')

    def create(self,validated_data):
        '''
            ~~~~FEATURES~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            //////////////////////////////////////////////////////////////////////////
            >>>) Admin can provide mass update by selecting as much request he wanted 
                1)Approved
                2)Reject
                3)Release
            1) >>>APPROVED LEAVES,GRACE,MP,OD ON BLUK AS WELL AS SINGLE DATA 
            
            2) >>>REJECT LEAVE AND REQUEST TYPE CALCULATION:-
                1)REJECTED GRACE,OD,MP CALCULATION
                    #IF REQUEST DURATION CROSS 240min REJECTED REQUEST WILL BE 
                        CONVERTED TO "FD" AND "AB"
                    #IF REQUEST DURATION LESS THAN 240min REJECTED REQUEST WILL BE 
                        CONVERTED TO "HD" AND "AB"
                2)REJECTED LEAVES CALCULATION
                    #IF REQUEST LEAVES REJECTED REQUEST(FD,FOD) WILL BE 
                        CONVERTED TO "FD" AND "AB"
                    #IF REQUEST LEAVES REJECTED REQUEST(HD,POD) WILL BE 
                        CONVERTED TO "HD" AND "AB"
                2)MULTIPLE LEAVE FOR ONE DAY IS AUTO CONVERTED TO ONE TYPE OF LEAVE 
            3) >>>RELEASE LEAVE AND REQUEST TYPE 
            
            EDITED BY :- Abhishek.singh@shyamfuture.com
            //////////////////////////////////////////////////////////////////////////
            ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~END~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        '''

        print(validated_data)
        updated_by = validated_data.get('updated_by')
        remarks = validated_data.get('remarks')
        # master_module_role = TMasterModuleRoleUser.objects.get(mmr_module__cm_name__iexact='hrms',mmr_user=self.context['request'].user).mmr_role
        # core_role = TCoreRole.objects.get(id=str(master_module_role)).cr_name
        for data in validated_data.get('attendence_approvals'):
            approved_status= data['approved_status']
            cur_date = datetime.datetime.now()
            
            if approved_status=='approved':
                approved_data = AttendanceApprovalRequest.objects.filter(id=data['req_id']).update(approved_status=approved_status,
                                                                        approved_by=updated_by,remarks=remarks)
                req_type = AttendanceApprovalRequest.objects.get(id=data['req_id']).request_type
                print("approved_data",approved_data,req_type)
                present_data = Attendance.objects.filter(id__in=AttendanceApprovalRequest.objects.filter(
                                        (Q(request_type='MP')|Q(request_type='FOD')),id=data['req_id']).values_list('attendance')
                                        ).update(is_present=True,day_remarks='Present')
                
                # if core_role.lower() == 'hr admin' and approved_data:
                if approved_data:
                    logger.log(self.context['request'].user,'approved'+" "+req_type,
                    'Approval','pending','Approved','HRMS-TeamAttendance -AttendenceApproval') 
                # elif approved_data:
                #     logger.log(self.context['request'].user,AttendenceAction.ACTION_HR,'approved'+" "+req_type,
                #     'Approval','pending','Approved','HRMS-TeamAttendance -AttendenceApproval')

                # if core_role.lower() == 'hr admin' and miss_punch_data:
                #     logger.log(self.context['request'].user,AttendenceAction.ACTION_ADMIN,'approved'+" "+req_type,
                #     'Approval','pending','Approved','HRMS-TeamAttendance -AttendenceApproval')
                # elif core_role.lower() == 'hr user' and miss_punch_data:
                #     logger.log(self.context['request'].user,AttendenceAction.ACTION_HR,'approved'+" "+req_type,
                #     'Approval','pending','Approved','HRMS-TeamAttendance -AttendenceApproval')

            elif approved_status=='reject':
                print("approved_status")
                if AttendanceApprovalRequest.objects.filter(id=data['req_id'],request_type='GR') :
                    # print("grace ")

                    duration_length=AttendanceApprovalRequest.objects.get(id=data['req_id'],is_requested=True)
                    #missing req type
                    prev_cal = AttendanceApprovalRequest.objects.filter(attendance=duration_length.attendance,is_requested=True,approved_status='reject')
                    reject_duration_sum_value = prev_cal.aggregate(Sum('duration'))['duration__sum']
                    rejected_ids = prev_cal.values('id')
                    # print('reject_sum_value',reject_duration_sum_value,'rejected_ids',rejected_ids)
                    # print("prev_cal",prev_cal)
                    # print("duration_length",duration_length)
                    if prev_cal:
                        # print("entered ")
                        ids =[x['id'] for x in rejected_ids] 
                        # print("ids",ids,duration_length.duration + reject_duration_sum_value)
                        if duration_length.duration + reject_duration_sum_value >= 240:
                            AttendanceApprovalRequest.objects.filter(id=data['req_id'],request_type='GR').update(approved_status=approved_status,
                                                                approved_by=updated_by,remarks=remarks,
                                                                leave_type_changed_period='FD',leave_type_changed='AB',approved_at=cur_date)
                            for x in ids:
                                AttendanceApprovalRequest.objects.filter(id=x).update(
                                                                    approved_by=updated_by,
                                                                    leave_type_changed_period='FD',leave_type_changed='AB',approved_at=cur_date)

                        else:
                            AttendanceApprovalRequest.objects.filter(id=data['req_id'],request_type='GR').update(approved_status=approved_status,
                                                                    approved_by=updated_by,remarks=remarks,
                                                                    leave_type_changed_period='HD',leave_type_changed='AB',approved_at=cur_date)
                    else:
                        if duration_length.duration < 240:

                            AttendanceApprovalRequest.objects.filter(id=data['req_id'],request_type='GR').update(approved_status=approved_status,
                                                                    approved_by=updated_by,remarks=remarks,
                                                                    leave_type_changed_period='HD',leave_type_changed='AB',approved_at=cur_date)
                        else:
                            AttendanceApprovalRequest.objects.filter(id=data['req_id'],request_type='GR').update(approved_status=approved_status,
                                                                    approved_by=updated_by,remarks=remarks,
                                                                    leave_type_changed_period='FD',leave_type_changed='AB',approved_at=cur_date)
                elif AttendanceApprovalRequest.objects.filter((Q(request_type='FD')                                           
                                                            |Q(request_type='FOD')),
                                                            id=data['req_id']) :
                    
                    # print("full day ")
                    AttendanceApprovalRequest.objects.filter((Q(request_type='FD')                                                 
                                                            |Q(request_type='FOD'))
                                                            ,id=data['req_id']).\
                                                            update(approved_status=approved_status,approved_by=updated_by,remarks=remarks,
                                                            leave_type_changed_period='FD',leave_type_changed='AB',approved_at=cur_date)

                elif AttendanceApprovalRequest.objects.filter((Q(request_type='HD')|Q(request_type='OD')                    
                                                            |Q(request_type='POD')|Q(request_type='MP')),
                                                            id=data['req_id']) :
                    # print("halfday day ")
                    duration_length=AttendanceApprovalRequest.objects.get(id=data['req_id'],is_requested=True)
                    prev_cal = AttendanceApprovalRequest.objects.filter(attendance=duration_length.attendance,is_requested=True,approved_status='reject')
                    reject_duration_sum_value = prev_cal.aggregate(Sum('duration'))['duration__sum']
                    rejected_ids = prev_cal.values('id')
                    # print('reject_sum_value',reject_duration_sum_value,'rejected_ids',rejected_ids)
                    # print("prev_cal",prev_cal)
                    # print("duration_length",duration_length)
                    if prev_cal:
                        # print("entered ")
                        ids =[x['id'] for x in rejected_ids] 
                        # print("ids",ids)
                        if duration_length.duration + reject_duration_sum_value >= 240:
                            AttendanceApprovalRequest.objects.filter((Q(request_type='HD')|Q(request_type='OD')                
                                                                    |Q(request_type='POD')|Q(request_type='MP'))
                                                                    ,id=data['req_id']).update(approved_status=approved_status,
                                                                approved_by=updated_by,remarks=remarks,
                                                                leave_type_changed_period='FD',leave_type_changed='AB',approved_at=cur_date)
                            for x in ids:
                                AttendanceApprovalRequest.objects.filter(id=x).update(
                                                                    approved_by=updated_by,
                                                                    leave_type_changed_period='FD',leave_type_changed='AB',approved_at=cur_date)
                        else:
                            AttendanceApprovalRequest.objects.filter((Q(request_type='HD')|Q(request_type='OD')                
                                                                    |Q(request_type='POD')|Q(request_type='MP'))
                                                                    ,id=data['req_id']).\
                                                                    update(approved_status=approved_status,approved_by=updated_by,remarks=remarks,
                                                                    leave_type_changed_period='HD',leave_type_changed='AB',approved_at=cur_date)
                    else:
                        # print("duration_length",duration_length)
                        if duration_length.duration < 240:
                            AttendanceApprovalRequest.objects.filter((Q(request_type='HD')|Q(request_type='OD')                
                                                                    |Q(request_type='POD')|Q(request_type='MP'))
                                                                    ,id=data['req_id']).\
                                                                    update(approved_status=approved_status,approved_by=updated_by,remarks=remarks,
                                                                    leave_type_changed_period='HD',leave_type_changed='AB',approved_at=cur_date)
                        else:
                            AttendanceApprovalRequest.objects.filter((Q(request_type='HD')|Q(request_type='OD')                
                                                                    |Q(request_type='POD')|Q(request_type='MP'))
                                                                    ,id=data['req_id']).\
                                                                    update(approved_status=approved_status,approved_by=updated_by,remarks=remarks,
                                                                    leave_type_changed_period='FD',leave_type_changed='AB',approved_at=cur_date)

                req_type = AttendanceApprovalRequest.objects.get(id=data['req_id']).request_type

                # if core_role.lower() == 'hr admin' and approved_data:
                logger.log(self.context['request'].user,'rejected'+" "+req_type,
                    'Approval','pending','Rejected','HRMS-TeamAttendance-AttendenceApproval') 
                # elif core_role.lower() == 'hr user' and approved_data:
                #     logger.log(self.context['request'].user,AttendenceAction.ACTION_HR,'rejected'+" "+req_type,
                #     'Approval','pending','Rejected','HRMS-TeamAttendance-AttendenceApproval')

                # if core_role.lower() == 'hr admin' and miss_punch_data:
                #     logger.log(request.user,AttendenceAction.ACTION_ADMIN,'rejected'+" "+req_type,
                #     'Approval','UnApproved','Approved','HRMS-AttendenceApproval-ConveyenceApprovals')
                # elif core_role.lower() == 'hr user' and approved_data:
                #     logger.log(request.user,AttendenceAction.ACTION_HR,'rejected'+" "+req_type,
                #     'Approval','UnApproved','Approved','HRMS-AttendenceApproval-ConveyenceApprovals')

                ######################### MAIL SEND ################################
                mp_detail = AttendanceApprovalRequest.objects.filter(Q(request_type='MP'), id=data['req_id'])
                od_detail = AttendanceApprovalRequest.objects.filter((Q(request_type='OD')
                                                            |Q(request_type='FOD')|Q(request_type='POD')), id=data['req_id'])
                if mp_detail:
                    print("AAAAA", userdetails(mp_detail.values()[0]['justified_by_id']))
                    full_name = userdetails(mp_detail.values()[0]['justified_by_id'])
                    date = (mp_detail.values()[0]['duration_start']).date()
                    rejected_by = userdetails(updated_by.id)
                    rejected_at = cur_date
                    email = mp_detail.values_list('attendance__employee__email',flat=True)[0]

                    # ============= Mail Send ============== #
                    if email:
                        mail_data = {
                                    "name": full_name,
                                    "date": date,
                                    "rejected_by": rejected_by,
                                    "rejected_date": cur_date.date()
                            }
                        print('mail_data',mail_data)
                        mail_class = GlobleMailSend('MP_reject', [email])
                        mail_thread = Thread(target = mail_class.mailsend, args = (mail_data,))
                        mail_thread.start()

                if od_detail:
                    full_name = userdetails(od_detail.values()[0]['justified_by_id'])
                    date = (od_detail.values()[0]['duration_start']).date()
                    rejected_by = userdetails(updated_by.id)
                    rejected_at = cur_date
                    email = od_detail.values_list('attendance__employee__email',flat=True)[0]

                    # ============= Mail Send ============== #
                    if email:
                        mail_data = {
                                    "name": full_name,
                                    "date": date,
                                    "rejected_by": rejected_by,
                                    "rejected_date": cur_date.date()
                            }
                        print('mail_data',mail_data)
                        mail_class = GlobleMailSend('OD_reject', [email])
                        mail_thread = Thread(target = mail_class.mailsend, args = (mail_data,))
                        mail_thread.start()
                ###########################################

                

            elif approved_status=='relese':
                req_type = AttendanceApprovalRequest.objects.get(id=data['req_id'])
                before_data = req_type.approved_status
                AttendanceApprovalRequest.objects.filter(id=data['req_id']).update(approved_status=approved_status,justification=None,
                                                                        approved_by=updated_by,remarks=remarks,request_type=None,is_requested=False)
        
                # if core_role.lower() == 'hr admin' and approved_data:
                logger.log(self.context['request'].user,'rejected'+" "+req_type.request_type,
                    'Approval',before_data,'Relese','HRMS-TeamAttendance-AttendenceApproval') 
                # elif core_role.lower() == 'hr user' and approved_data:
                #     logger.log(self.context['request'].user,AttendenceAction.ACTION_HR,'rejected'+" "+req_type.request_type,
                #     'Approval',before_data,'Relese','HRMS-TeamAttendance-AttendenceApproval')

        data = validated_data

        return data
    

class ETaskAttendanceApprovalModifySerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    attendence_approvals=serializers.ListField(required=False)
    
    class Meta:
        model = AttendanceApprovalRequest
        fields = ('id','updated_by','remarks','approved_status','attendence_approvals')
        # extra_fields=('attendence_approvals')

    def leave_calulate(self,request_id):
        total_grace={}
        # date_object = datetime.now().date()
        
        ################################

        req_details = AttendanceApprovalRequest.objects.get(id=request_id,is_requested=True)

        # request_month = req_details.duration_start.month
        request_date = req_details.duration_start.date()
        print("request_date",request_date, req_details.duration_start)
        total_month_grace=AttendenceMonthMaster.objects.filter(month_start__date__lte=request_date,
                                        month_end__date__gte=request_date,is_deleted=False).values(
                                        'year_start_date','year_end_date','month','month_start__date','month_end__date')
        # print("total_month_grace",total_month_grace)

        employee_id = req_details.attendance.employee
        print('employee_id',employee_id)

        last_attendance = Attendance.objects.filter(employee=employee_id).values_list('date__date',flat=True).order_by('-date')[:1]
        print("last_attendance",last_attendance)
        last_attendance = last_attendance[0] if last_attendance else date_object
        print('last_attendance',last_attendance)
        date_object = last_attendance
        #################################

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
        core_user_detail=TCoreUserDetail.objects.filter(cu_user=employee_id,cu_is_deleted=False).values('joining_date',
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

    def leave_type_return(self,leave_details,req_type):
        cl_balance = leave_details['cl_balance']
        el_balance = leave_details['el_balance']
        # sl_balance = leave_details['sl_balance']
        is_confirm = leave_details['is_confirm']
        leave_type = None
        if req_type=='HD':
            if cl_balance>=0.5:
                leave_type = 'CL'
            elif is_confirm is True and el_balance>=0.5:
                leave_type = 'EL'
            else:
                leave_type = 'AB'
        elif req_type=='FD':
            if cl_balance>=1.0:
                leave_type = 'CL'
            elif is_confirm is True and el_balance>=1.0:
                leave_type = 'EL'
            else:
                leave_type = 'AB'

        return leave_type

    def create(self,validated_data):
        '''
            ~~~~FEATURES~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            //////////////////////////////////////////////////////////////////////////
            >>>) Admin can provide mass update by selecting as much request he wanted 
                1)Approved
                2)Reject
                3)Release
            1) >>>APPROVED LEAVES,GRACE,MP,OD ON BLUK AS WELL AS SINGLE DATA 
            
            2) >>>REJECT LEAVE AND REQUEST TYPE CALCULATION:-
                1)REJECTED GRACE,OD,MP CALCULATION
                    #IF REQUEST DURATION CROSS 240min REJECTED REQUEST WILL BE 
                        CONVERTED TO "FD" AND "AB"
                    #IF REQUEST DURATION LESS THAN 240min REJECTED REQUEST WILL BE 
                        CONVERTED TO "HD" AND "AB"
                2)REJECTED LEAVES CALCULATION
                    #IF REQUEST LEAVES REJECTED REQUEST(FD,FOD) WILL BE 
                        CONVERTED TO "FD" AND "AB"
                    #IF REQUEST LEAVES REJECTED REQUEST(HD,POD) WILL BE 
                        CONVERTED TO "HD" AND "AB"
                2)MULTIPLE LEAVE FOR ONE DAY IS AUTO CONVERTED TO ONE TYPE OF LEAVE 
            3) >>>RELEASE LEAVE AND REQUEST TYPE 
            
            EDITED BY :- Abhishek.singh@shyamfuture.com
            //////////////////////////////////////////////////////////////////////////
            >>>) As per discussion with Shailendra Sir & Tonmoy Da on 24/01/2020:-
                1)Reject >>1. Grace
                           2. POD/FOD
                           3. MP
                Action:- check LEAVE balance >> CL >> EL & is_confirm >> AB
            ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~END~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        '''

        print(validated_data)
        updated_by = validated_data.get('updated_by')
        remarks = validated_data.get('remarks')
        # master_module_role = TMasterModuleRoleUser.objects.get(mmr_module__cm_name__iexact='hrms',mmr_user=self.context['request'].user).mmr_role
        # core_role = TCoreRole.objects.get(id=str(master_module_role)).cr_name
        for data in validated_data.get('attendence_approvals'):
            approved_status= data['approved_status']
            cur_date = datetime.datetime.now()
            
            if approved_status=='approved':
                approved_data = AttendanceApprovalRequest.objects.filter(id=data['req_id']).update(approved_status=approved_status,
                                                                        approved_by=updated_by,remarks=remarks)
                req_type = AttendanceApprovalRequest.objects.get(id=data['req_id']).request_type
                print("approved_data",approved_data,req_type)
                present_data = Attendance.objects.filter(id__in=AttendanceApprovalRequest.objects.filter(
                                        (Q(request_type='MP')|Q(request_type='FOD')),id=data['req_id']).values_list('attendance')
                                        ).update(is_present=True,day_remarks='Present')
                
                # if core_role.lower() == 'hr admin' and approved_data:
                if approved_data:
                    logger.log(self.context['request'].user,'approved'+" "+req_type,
                    'Approval','pending','Approved','HRMS-TeamAttendance -AttendenceApproval') 
                # elif approved_data:
                #     logger.log(self.context['request'].user,AttendenceAction.ACTION_HR,'approved'+" "+req_type,
                #     'Approval','pending','Approved','HRMS-TeamAttendance -AttendenceApproval')

                # if core_role.lower() == 'hr admin' and miss_punch_data:
                #     logger.log(self.context['request'].user,AttendenceAction.ACTION_ADMIN,'approved'+" "+req_type,
                #     'Approval','pending','Approved','HRMS-TeamAttendance -AttendenceApproval')
                # elif core_role.lower() == 'hr user' and miss_punch_data:
                #     logger.log(self.context['request'].user,AttendenceAction.ACTION_HR,'approved'+" "+req_type,
                #     'Approval','pending','Approved','HRMS-TeamAttendance -AttendenceApproval')

            elif approved_status=='reject':
                print("approved_status")
                leave_details = self.leave_calulate(data['req_id'])
                print("leave_details",leave_details)
                lev_type_FD = self.leave_type_return(leave_details,'FD')
                lev_type_HD = self.leave_type_return(leave_details,'HD')
                print("lev_type",lev_type_FD, 'lev_type_HD', lev_type_HD)
                
                if AttendanceApprovalRequest.objects.filter(id=data['req_id'],request_type='GR'):
                    print("grace ")

                    duration_length=AttendanceApprovalRequest.objects.get(id=data['req_id'],is_requested=True)
                    prev_cal = AttendanceApprovalRequest.objects.filter(attendance=duration_length.attendance,is_requested=True,approved_status='reject')
                    reject_duration_sum_value = prev_cal.aggregate(Sum('duration'))['duration__sum']
                    rejected_ids = prev_cal.values('id')
                    # print('reject_sum_value',reject_duration_sum_value,'rejected_ids',rejected_ids)
                    # print("prev_cal",prev_cal)
                    # print("duration_length",duration_length)
                    if prev_cal:
                        # print("entered ")
                        ids =[x['id'] for x in rejected_ids] 
                        # print("ids",ids,duration_length.duration + reject_duration_sum_value)
                        if duration_length.duration + reject_duration_sum_value >= 240:
                            AttendanceApprovalRequest.objects.filter(id=data['req_id'],request_type='GR').update(approved_status=approved_status,
                                                                approved_by=updated_by,remarks=remarks,
                                                                leave_type_changed_period='FD',leave_type_changed=lev_type_FD,approved_at=cur_date)
                            for x in ids:
                                AttendanceApprovalRequest.objects.filter(id=x).update(
                                                                    approved_by=updated_by,
                                                                    leave_type_changed_period='FD',leave_type_changed=lev_type_FD,approved_at=cur_date)

                        else:
                            AttendanceApprovalRequest.objects.filter(id=data['req_id'],request_type='GR').update(approved_status=approved_status,
                                                                    approved_by=updated_by,remarks=remarks,
                                                                    leave_type_changed_period='HD',leave_type_changed=lev_type_HD,approved_at=cur_date)
                    else:
                        if duration_length.duration < 240:

                            AttendanceApprovalRequest.objects.filter(id=data['req_id'],request_type='GR').update(approved_status=approved_status,
                                                                    approved_by=updated_by,remarks=remarks,
                                                                    leave_type_changed_period='HD',leave_type_changed=lev_type_HD,approved_at=cur_date)
                        else:
                            AttendanceApprovalRequest.objects.filter(id=data['req_id'],request_type='GR').update(approved_status=approved_status,
                                                                    approved_by=updated_by,remarks=remarks,
                                                                    leave_type_changed_period='FD',leave_type_changed=lev_type_FD,approved_at=cur_date)
                # elif AttendanceApprovalRequest.objects.filter((Q(request_type='FD')                                           
                #                                             |Q(request_type='FOD')),
                #                                             id=data['req_id']) :
                    
                #     # print("full day ")
                #     AttendanceApprovalRequest.objects.filter((Q(request_type='FD')                                                 
                #                                             |Q(request_type='FOD'))
                #                                             ,id=data['req_id']).\
                #                                             update(approved_status=approved_status,approved_by=updated_by,remarks=remarks,
                #                                             leave_type_changed_period='FD',leave_type_changed='AB',approved_at=cur_date)

                elif AttendanceApprovalRequest.objects.filter(request_type='FD',id=data['req_id']):
                    
                    # print("full day ")
                    AttendanceApprovalRequest.objects.filter(request_type='FD',id=data['req_id']).\
                                                            update(approved_status=approved_status,approved_by=updated_by,remarks=remarks,
                                                            leave_type_changed_period='FD',leave_type_changed='AB',approved_at=cur_date)

                elif AttendanceApprovalRequest.objects.filter(request_type='FOD',id=data['req_id']) :
                    
                    # print("full day ")
                    AttendanceApprovalRequest.objects.filter(request_type='FOD',id=data['req_id']).\
                                                            update(approved_status=approved_status,approved_by=updated_by,remarks=remarks,
                                                            leave_type_changed_period='FD',leave_type_changed=lev_type_FD,approved_at=cur_date)

                elif AttendanceApprovalRequest.objects.filter((Q(request_type='HD')|Q(request_type='OD')                    
                                                            |Q(request_type='POD')|Q(request_type='MP')),
                                                            id=data['req_id']) :
                    # print("halfday day ")
                    duration_length=AttendanceApprovalRequest.objects.get(id=data['req_id'],is_requested=True)
                    prev_cal = AttendanceApprovalRequest.objects.filter(attendance=duration_length.attendance,is_requested=True,approved_status='reject')
                    reject_duration_sum_value = prev_cal.aggregate(Sum('duration'))['duration__sum']
                    rejected_ids = prev_cal.values('id')
                    # print('reject_sum_value',reject_duration_sum_value,'rejected_ids',rejected_ids)
                    # print("prev_cal",prev_cal)
                    # print("duration_length",duration_length)
                    if prev_cal:
                        # print("entered ")
                        ids =[x['id'] for x in rejected_ids] 
                        # print("ids",ids)
                        if duration_length.duration + reject_duration_sum_value >= 240:
                            AttendanceApprovalRequest.objects.filter((Q(request_type='HD')|Q(request_type='OD')                
                                                                    |Q(request_type='POD')|Q(request_type='MP'))
                                                                    ,id=data['req_id']).update(approved_status=approved_status,
                                                                approved_by=updated_by,remarks=remarks,
                                                                leave_type_changed_period='FD',leave_type_changed=lev_type_FD,approved_at=cur_date)
                            for x in ids:
                                AttendanceApprovalRequest.objects.filter(id=x).update(
                                                                    approved_by=updated_by,
                                                                    leave_type_changed_period='FD',leave_type_changed=lev_type_FD,approved_at=cur_date)
                        else:
                            AttendanceApprovalRequest.objects.filter((Q(request_type='OD')                
                                                                    |Q(request_type='POD')|Q(request_type='MP'))
                                                                    ,id=data['req_id']).\
                                                                    update(approved_status=approved_status,approved_by=updated_by,remarks=remarks,
                                                                    leave_type_changed_period='HD',leave_type_changed=lev_type_HD,approved_at=cur_date)

                            AttendanceApprovalRequest.objects.filter(request_type='HD',id=data['req_id']).\
                                                                    update(approved_status=approved_status,approved_by=updated_by,remarks=remarks,
                                                                    leave_type_changed_period='HD',leave_type_changed='AB',approved_at=cur_date)
                    else:
                        # print("duration_length",duration_length)
                        if duration_length.duration < 240:
                            AttendanceApprovalRequest.objects.filter((Q(request_type='OD')|Q(request_type='POD')|Q(request_type='MP'))
                                                                    ,id=data['req_id']).\
                                                                    update(approved_status=approved_status,approved_by=updated_by,remarks=remarks,
                                                                    leave_type_changed_period='HD',leave_type_changed=lev_type_HD,approved_at=cur_date)

                            AttendanceApprovalRequest.objects.filter(request_type='HD',id=data['req_id']).\
                                                                    update(approved_status=approved_status,approved_by=updated_by,remarks=remarks,
                                                                    leave_type_changed_period='HD',leave_type_changed='AB',approved_at=cur_date)
                        else:
                            AttendanceApprovalRequest.objects.filter((Q(request_type='OD')|Q(request_type='POD')|Q(request_type='MP')),id=data['req_id']).\
                                                                    update(approved_status=approved_status,approved_by=updated_by,remarks=remarks,
                                                                    leave_type_changed_period='FD',leave_type_changed=lev_type_FD,approved_at=cur_date)

                            AttendanceApprovalRequest.objects.filter(request_type='HD',id=data['req_id']).\
                                                                    update(approved_status=approved_status,approved_by=updated_by,remarks=remarks,
                                                                    leave_type_changed_period='FD',leave_type_changed='AB',approved_at=cur_date)

                req_type = AttendanceApprovalRequest.objects.get(id=data['req_id']).request_type

                # if core_role.lower() == 'hr admin' and approved_data:
                logger.log(self.context['request'].user,'rejected'+" "+req_type,
                    'Approval','pending','Rejected','HRMS-TeamAttendance-AttendenceApproval') 
                # elif core_role.lower() == 'hr user' and approved_data:
                #     logger.log(self.context['request'].user,AttendenceAction.ACTION_HR,'rejected'+" "+req_type,
                #     'Approval','pending','Rejected','HRMS-TeamAttendance-AttendenceApproval')

                # if core_role.lower() == 'hr admin' and miss_punch_data:
                #     logger.log(request.user,AttendenceAction.ACTION_ADMIN,'rejected'+" "+req_type,
                #     'Approval','UnApproved','Approved','HRMS-AttendenceApproval-ConveyenceApprovals')
                # elif core_role.lower() == 'hr user' and approved_data:
                #     logger.log(request.user,AttendenceAction.ACTION_HR,'rejected'+" "+req_type,
                #     'Approval','UnApproved','Approved','HRMS-AttendenceApproval-ConveyenceApprovals')

                ######################### MAIL SEND ################################
                mp_detail = AttendanceApprovalRequest.objects.filter(Q(request_type='MP'), id=data['req_id'])
                od_detail = AttendanceApprovalRequest.objects.filter((Q(request_type='OD')
                                                            |Q(request_type='FOD')|Q(request_type='POD')), id=data['req_id'])
                if mp_detail:
                    print("AAAAA", userdetails(mp_detail.values()[0]['justified_by_id']))
                    full_name = userdetails(mp_detail.values()[0]['justified_by_id'])
                    date = (mp_detail.values()[0]['duration_start']).date()
                    rejected_by = userdetails(updated_by.id)
                    rejected_at = cur_date
                    email = mp_detail.values_list('attendance__employee__email',flat=True)[0]

                    # ============= Mail Send ============== #
                    if email:
                        mail_data = {
                                    "name": full_name,
                                    "date": date,
                                    "rejected_by": rejected_by,
                                    "rejected_date": cur_date.date()
                            }
                        print('mail_data',mail_data)
                        mail_class = GlobleMailSend('MP_reject', [email])
                        mail_thread = Thread(target = mail_class.mailsend, args = (mail_data,))
                        mail_thread.start()

                if od_detail:
                    full_name = userdetails(od_detail.values()[0]['justified_by_id'])
                    date = (od_detail.values()[0]['duration_start']).date()
                    rejected_by = userdetails(updated_by.id)
                    rejected_at = cur_date
                    email = od_detail.values_list('attendance__employee__email',flat=True)[0]

                    # ============= Mail Send ============== #
                    if email:
                        mail_data = {
                                    "name": full_name,
                                    "date": date,
                                    "rejected_by": rejected_by,
                                    "rejected_date": cur_date.date()
                            }
                        print('mail_data',mail_data)
                        mail_class = GlobleMailSend('OD_reject', [email])
                        mail_thread = Thread(target = mail_class.mailsend, args = (mail_data,))
                        mail_thread.start()
                ###########################################

                

            elif approved_status=='relese':
                req_type = AttendanceApprovalRequest.objects.get(id=data['req_id'])
                before_data = req_type.approved_status
                AttendanceApprovalRequest.objects.filter(id=data['req_id']).update(approved_status=approved_status,justification=None,
                                                                        approved_by=updated_by,remarks=remarks,request_type=None,is_requested=False)
        
                # if core_role.lower() == 'hr admin' and approved_data:
                logger.log(self.context['request'].user,'rejected'+" "+req_type.request_type,
                    'Approval',before_data,'Relese','HRMS-TeamAttendance-AttendenceApproval') 
                # elif core_role.lower() == 'hr user' and approved_data:
                #     logger.log(self.context['request'].user,AttendenceAction.ACTION_HR,'rejected'+" "+req_type.request_type,
                #     'Approval',before_data,'Relese','HRMS-TeamAttendance-AttendenceApproval')

        data = validated_data

        return data
    


class AttendanceVehicleTypeMasterAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = VehicleTypeMaster
        fields = ('id', 'name', 'description', 'created_by', 'owned_by')

class AttendanceVehicleTypeMasterEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = VehicleTypeMaster
        fields = ('id', 'name', 'description', 'updated_by')

class AttendanceVehicleTypeMasterDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = VehicleTypeMaster
        fields = '__all__'
    def update(self, instance, validated_data):
        instance.is_deleted=True
        instance.updated_by = validated_data.get('updated_by')
        instance.save()
        return instance

class AttendanceAdminSummaryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = '__all__'

class AttendanceAdminDailyListSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Attendance
        fields = '__all__'

class AttendanceFileUploadOldVersionSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = AttandancePerDayDocuments
        fields = '__all__'

    def create(self, validated_data):
        try:
            attendance_file = AttandancePerDayDocuments.objects.create(**validated_data)
            print('attendance_file: ', attendance_file)
            return attendance_file
        except Exception as e:
            raise APIException({"msg": e, "request_status": 0})

class AttendanceFileUploadSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = AttandancePerDayDocuments
        fields = '__all__'

    def create(self, validated_data):
        try:
            attendance_file = AttandancePerDayDocuments.objects.create(**validated_data)
            print('attendance_file: ', attendance_file)
            return attendance_file
        except Exception as e:
            raise APIException({"msg": e, "request_status": 0})

class AttendanceLeaveApprovalListSerializer(serializers.ModelSerializer):
    employee_name=serializers.SerializerMethodField(required=False)
    employee_id=serializers.SerializerMethodField(required=False) 
    def get_employee_name(self,AttendanceApprovalRequest):
        if AttendanceApprovalRequest.attendance:
            first_name=AttendanceApprovalRequest.attendance.employee.first_name if AttendanceApprovalRequest.attendance.employee.first_name  else ''
            last_name=AttendanceApprovalRequest.attendance.employee.last_name if AttendanceApprovalRequest.attendance.employee.last_name else ''
            name=first_name+" "+last_name
            return name
    def get_employee_id(self,AttendanceApprovalRequest):
        if AttendanceApprovalRequest.attendance:
            return AttendanceApprovalRequest.attendance.employee.id
    class Meta:
        model = AttendanceApprovalRequest
        fields = '__all__'
        extra_fields=('employee_name','employee_id')
       

class AttendanceAdminMispunchCheckerSerializer(serializers.ModelSerializer):

    class Meta:
        model = AttendanceApprovalRequest
        fields = ('id','attendance','duration_start','duration_end','duration','request_type','justification','remarks','is_requested','lock_status',
        'is_late_conveyance','checkin_benchmark','approved_status','created_at')

class AttendanceAdminMispunchCheckerCSVReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceApprovalRequest
        fields = ('id','attendance','duration_start','duration_end','duration','request_type','justification','remarks','is_requested','lock_status',
        'is_late_conveyance','checkin_benchmark','approved_status','created_at')


class AttandanceAdminOdMsiReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceApprovalRequest
        fields = '__all__'


class AttandanceRequestFreeByHRListSerializer(serializers.ModelSerializer):
    employee_name=serializers.SerializerMethodField(required=False)
    employee_id=serializers.SerializerMethodField(required=False) 
    def get_employee_name(self,AttendanceApprovalRequest):
        if AttendanceApprovalRequest.attendance:
            first_name=AttendanceApprovalRequest.attendance.employee.first_name if AttendanceApprovalRequest.attendance.employee.first_name  else ''
            last_name=AttendanceApprovalRequest.attendance.employee.last_name if AttendanceApprovalRequest.attendance.employee.last_name else ''
            name=first_name+" "+last_name
            return name
    def get_employee_id(self,AttendanceApprovalRequest):
        if AttendanceApprovalRequest.attendance:
            return AttendanceApprovalRequest.attendance.employee.id
    class Meta:
        model = AttendanceApprovalRequest
        fields = '__all__'
        extra_fields=('employee_name','employee_id')


class AttendanceMonthlyHRListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = '__all__'

class AttendanceMonthlyHRListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = '__all__'

#:::::::::::::::::::::: ATTENDANCE SPECIALDAY MASTER:::::::::::::::::::::::::::#
class AttendanceSpecialdayMasterAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = AttendanceSpecialdayMaster
        fields = ('id', 'day_start_time', 'day_end_time','day_type', 'full_day', 'remarks', 'created_by', 'owned_by')
    def create(self,validated_data):
        try:
            day_start_time=validated_data.get('day_start_time') if 'day_start_time' in validated_data else None
            day_end_time =validated_data.get('day_end_time') if 'day_end_time' in validated_data else None
            day_type =validated_data.get('day_type') if 'day_type' in validated_data else ''
            full_day =validated_data.get('full_day') if 'full_day' in validated_data else None
            remarks=validated_data.get('remarks') if 'remarks' in validated_data else ''
            created_by=validated_data.get('created_by')
            owned_by=validated_data.get('owned_by')
            filter={}
            if day_type == 1:
                filter['full_day']=full_day
            elif day_type == 2:
                filter['day_start_time']=day_start_time
            elif day_type == 3:
                filter['day_end_time']=day_end_time
            elif  day_type == 4:
                filter['day_start_time']=day_start_time
                filter['day_end_time']=day_end_time
            special_day=AttendanceSpecialdayMaster.objects.create(day_type=day_type,
                                                                **filter,
                                                                remarks=remarks,
                                                                created_by=created_by,
                                                                owned_by=owned_by
                                                                    )
            # print('special_day',special_day)
            return special_day

        except Exception as e:
            raise APIException({'msg':settings.MSG_ERROR,
                                'error':e,
                                "request_status": 0
                                })


class AttendanceSpecialdayMasterEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = AttendanceSpecialdayMaster
        fields = ('id', 'day_start_time', 'day_end_time','day_type','full_day', 'remarks', 'updated_by')
    def update(self,instance,validated_data):
        try:
            day_start_time=validated_data.get('day_start_time') if 'day_start_time' in validated_data else None
            day_end_time =validated_data.get('day_end_time') if 'day_end_time' in validated_data else None
            day_type =validated_data.get('day_type') if 'day_type' in validated_data else ''
            full_day =validated_data.get('full_day') if 'full_day' in validated_data else None
            remarks=validated_data.get('remarks') if 'remarks' in validated_data else ''
            updated_by=validated_data.get('updated_by')
            current_date=datetime.datetime.now().date()
            # print('day_start_time',day_start_time.date())
            data={}
            
            if day_type == 1:
                if current_date<=full_day.date():
                    instance.delete()
                    full_day=AttendanceSpecialdayMaster.objects.create(day_type=day_type,
                                                            full_day=full_day,
                                                            remarks=remarks,
                                                            updated_by=updated_by
                                                            )
                    data=full_day
            elif day_type == 2:
                if current_date<=day_start_time.date():
                    instance.delete()
                    day_start=AttendanceSpecialdayMaster.objects.create(day_type=day_type,
                                                            day_start_time=day_start_time,
                                                            remarks=remarks,
                                                            updated_by=updated_by
                                                            )
                    data=day_start
            elif day_type == 3:
                if current_date<=day_end_time.date():
                    instance.delete() 
                    day_end=AttendanceSpecialdayMaster.objects.create(day_type=day_type,
                                                            day_end_time=day_end_time,
                                                            remarks=remarks,
                                                            updated_by=updated_by
                                                            )
                    data=day_end                                        
            elif  day_type == 4:
                if  current_date<=day_start_time.date() or current_date<=day_end_time.date():
                    instance.delete()
                    start_and_end=AttendanceSpecialdayMaster.objects.create(day_type=day_type,
                                                            day_start_time=day_start_time,
                                                            day_end_time=day_end_time,
                                                            remarks=remarks,
                                                            updated_by=updated_by
                                                            )
                    data=start_and_end 
                
            return data

        except Exception as e:
            # raise e
            raise APIException({'msg':settings.MSG_ERROR,
                                'error':e,
                                "request_status": 0
                                })

    

class AttendanceSpecialdayMasterDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = AttendanceSpecialdayMaster
        fields = '__all__'
    def update(self, instance, validated_data):
        instance.is_deleted=True
        instance.updated_by = validated_data.get('updated_by')
        instance.save()
        return instance

class AttendanceEmployeeReportSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = TCoreUserDetail
        fields = ('cu_emp_code','cu_user')

class logListSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendenceAction
        fields= '__all__'

class AttendanceFileUploadCheckSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = Attendance
        fields = '__all__'


class EmailSMSAlertForRequestApprovalSerializer(serializers.ModelSerializer):

    class Meta:
        model = Attendance
        fields = '__all__'


class CwsReportSerializer(serializers.ModelSerializer):

    class Meta:
        model = Attendance
        fields = '__all__'
