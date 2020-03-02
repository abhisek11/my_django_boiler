from global_function import userdetails
from attendance.models import *
from datetime import date,time
from datetime import datetime,timedelta
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from etask.models import *
from master.models import *
from users.models import TCoreUserDetail
from master.models import TMasterModuleRole
from django.contrib.auth.models import *
from django.db import transaction, IntegrityError
from drf_extra_fields.fields import Base64ImageField
import os
from django.db.models import Sum
from custom_exception_message import *
from mailsend.views import *
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from users.models import TCoreUserDetail
from smssend.views import *
from threading import Thread
from django.db.models import When, Case, Value, CharField, IntegerField, F, Q



def leave_calulate(employee_id,total_month_grace):
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


def my_attendence_lock_job():
    print("LOG ENTRY FOR LOCK OF ATTENDENCE ON " ,datetime.now())
    try:
        date_object = datetime.now().date()
        current_date = datetime.now().date()
        current_month = current_date.month
        total_month_grace=AttendenceMonthMaster.objects.filter(month=current_month,is_deleted=False).values('lock_date__date'
                                                ,'year_start_date','year_end_date','month','month_start__date','month_end__date')
        # print("total_month_grace",total_month_grace)
        with transaction.atomic():
            if current_date == total_month_grace[0]['lock_date__date']:
                # user_details = TCoreUserDetail.objects.filter((~Q(cu_user__in=TMasterModuleRoleUser.objects.filter(Q(mmr_type=1)|
                #                                         Q(mmr_type=6)|Q(mmr_is_deleted=True)).values_list('mmr_user',flat=True))),
                #                                         (~Q(cu_punch_id__in=['PMSSITE000','#N/A',''])),
                #                                         cu_is_deleted=False).values_list('cu_user',flat=True).distinct()
                user_details=TMasterModuleRoleUser.objects.\
                        filter(~Q(mmr_user_id__in=(TCoreUserDetails.objects.filter(cu_punch_id__in=('10111032','10011271','10111036','00000160','00000171','00000022','00000168','00000163','00000161','00000016','00000018','00000162'))))
                            Q(mmr_type=3),Q(mmr_is_deleted=False),
                            Q(mmr_module__cm_name='ATTENDANCE & HRMS')).values_list('mmr_user',flat=True).distinct()
            
                print('user_details',user_details)
                for employee_id in user_details:
                    
                    '''
                        For Testing Pupose leave check before OD Approval
                    '''
                    total_grace_finalbefore = leave_calulate(employee_id,total_month_grace)
                    print("loop before od ",total_grace_finalbefore)
                    # print("employee_id",employee_id)
                    attendence_ids=AttendanceApprovalRequest.objects.filter(attendance_date__gte=total_month_grace[0]['month_start__date'],
                                                        attendance_date__lte=total_month_grace[0]['month_end__date'],is_late_conveyance=False,
                                                        is_requested=False,is_deleted=False,attendance__employee=employee_id).values_list('attendance',flat=True).distinct()
                    # print("attendence_ids",attendence_ids)
                    #OD AUTO APPROVAL
                    od_app_req_id=AttendanceApprovalRequest.objects.filter((Q(request_type='POD')|Q(request_type='FOD')),attendance__employee=employee_id
                                                                            ,is_requested=True,approved_status='pending').values_list('id',flat=True).distinct()
                    for app_req_id in list(od_app_req_id):
                        total_grace_final = leave_calulate(employee_id,total_month_grace)
                        print("Inside loop od grace",total_grace_final)
                        duration_length=AttendanceApprovalRequest.objects.get(id=app_req_id,
                                                                    is_requested=True).duration
                        if duration_length < 240:
                            if total_grace_final['cl_balance'] > 0.0:

                                update_auto = AttendanceApprovalRequest.objects.filter(id=app_req_id,is_late_conveyance=False,
                                                                        is_requested=True).\
                                                                            update(leave_type_changed_period='HD',leave_type_changed='CL',
                                                                            approved_status='approved',remarks='AUTO OD CONVERTED TO LEAVE & APPROVED')
                            elif total_grace_final['el_balance'] > 0.0:

                                update_auto = AttendanceApprovalRequest.objects.filter(id=app_req_id,is_late_conveyance=False,
                                                                        is_requested=True).\
                                                                            update(leave_type_changed_period='HD',leave_type_changed='EL',
                                                                            approved_status='approved',remarks='AUTO OD CONVERTED TO LEAVE & APPROVED')
                            else:

                                update_auto =AttendanceApprovalRequest.objects.filter(id=app_req_id,is_late_conveyance=False,
                                                                        is_requested=True).\
                                                                            update(leave_type_changed_period='HD',leave_type_changed='AB',
                                                                            approved_status='approved',remarks='AUTO OD CONVERTED TO LEAVE & APPROVED')
                        else:
                            if total_grace_final['cl_balance'] > 0.5:

                                update_auto =AttendanceApprovalRequest.objects.filter(id=app_req_id,is_late_conveyance=False,
                                                                        is_requested=True).\
                                                                            update(leave_type_changed_period='FD',leave_type_changed='CL',
                                                                            approved_status='approved',remarks='AUTO OD CONVERTED TO LEAVE & APPROVED')
                            elif total_grace_final['el_balance'] > 0.5:

                                update_auto = AttendanceApprovalRequest.objects.filter(id=app_req_id,is_late_conveyance=False,
                                                                        is_requested=True).\
                                                                            update(leave_type_changed_period='FD',leave_type_changed='EL',
                                                                            approved_status='approved',remarks='AUTO OD CONVERTED TO LEAVE & APPROVED')
                            else:

                                update_auto = AttendanceApprovalRequest.objects.filter(id=app_req_id,is_late_conveyance=False,
                                                                        is_requested=True).\
                                                                            update(leave_type_changed_period='FD',leave_type_changed='AB',
                                                                            approved_status='approved',remarks='AUTO OD CONVERTED TO LEAVE & APPROVED')                       
                
                    total_grace_final2 = leave_calulate(employee_id,total_month_grace)
                    print("after od leave calculate",total_grace_final2) 
                    for att_id in list(attendence_ids):
                        total_grace_final2 = leave_calulate(employee_id,total_month_grace)
                        print("Inside loop not requested grace",total_grace_final2)
                        duration_length=AttendanceApprovalRequest.objects.filter(attendance=att_id,is_late_conveyance=False,
                                                                    checkin_benchmark=False,is_requested=False).aggregate(Sum('duration'))['duration__sum']
                        print('duration_length',duration_length,'att_id',att_id)
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
                    total_grace_final2 = leave_calulate(employee_id,total_month_grace)
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

        return True

    except Exception as e:
        raise e


def my_attendence_mail_before_lock_job():

    '''
        ATTENDENCE REMINDER FOR ALL HRMS & ATTENDENCE USER 
    '''

    current_date = datetime.now().date()
    current_month = current_date.month
    print("current_date",current_date)

    total_month_grace=AttendenceMonthMaster.objects.filter(
        month=current_month,is_deleted=False).values(
        'lock_date__date','year_start_date','year_end_date',
        'month','month_start__date','month_end__date',
        'pending_action_mail__date')

    print("total_month_grace",total_month_grace)
    days_cnt = (total_month_grace[0]['lock_date__date'] - total_month_grace[0]['pending_action_mail__date']).days
    date_generated = [total_month_grace[0]['pending_action_mail__date'] + timedelta(days=x) for x in range(0,days_cnt)]

    print("date_day",date_generated)
    if current_date in date_generated:
        print("entered",current_date)
        #working query local and live 
        user_list=TMasterModuleRoleUser.objects.\
                    filter(
                        Q(mmr_type=3),Q(mmr_is_deleted=False),
                        Q(mmr_module__cm_name='ATTENDANCE & HRMS')).\
                        values_list('mmr_user',flat=True).distinct()
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
        # print("user_mail_list_primary",user_mail_list_primary)
        # print("user_mail_official",user_mail_official)
        umlp = [x['mmr_user__email'] for x in user_mail_list_primary]
        uma = [x['cu_alt_email_id'] for x in user_mail_official]

        user_mail_list = list(set(umlp + uma))
        print("user_mail_list",user_mail_list)

        
        
    #     emp_mob = TCoreUserDetail.objects.filter(cu_user__in=list(user_list),cu_phone_no__isnull=False).\
    #         values('cu_phone_no').distinct()
    #     emp_mob_no = [ x['cu_phone_no'] for x in emp_mob ]

        print("user_mail_list",user_mail_list)

        '''
            MAIL Functionality
        '''

        print("email",user_mail_list)
        if user_mail_list:
            mail_data = {
            'name':None
            }
            print('mail_data',mail_data)
            mail_list=[]
            while len(user_mail_list)>0:
                dummy_mail_list = user_mail_list[0:5]
                user_mail_list = list(set(user_mail_list) - set(dummy_mail_list ))
                print("user_mail_list",user_mail_list)
                mail_class = GlobleMailSend('ATP-PM', dummy_mail_list)
                mail_thread = Thread(target = mail_class.mailsend, args = (mail_data,None))
                mail_thread.start()
        
        '''
            SMS Functionality
        '''
        if emp_mob_no:
            message_data = {
                'name':None
            }
            sms_class = GlobleSmsSendTxtLocal('ATTPR',emp_mob_no)
            sms_thread = Thread(target = sms_class.sendSMS, args = (message_data,'sms'))
            sms_thread.start()

    return True


def attendence_mail_hod_pending_approval_job():
        user_mail_official = TCoreUserDetail.objects.filter(
            (Q(cu_alt_email_id__isnull=False) & ~Q(cu_alt_email_id="")),cu_user__in=list(user_list)).\
                values('cu_alt_email_id').distinct()
        print("user_mail_list_primary",user_mail_list_primary)
        print("user_mail_official",user_mail_official)
        umlp = [x['mmr_user__email'] for x in user_mail_list_primary]
        uma = [x['cu_alt_email_id'] for x in user_mail_official]

        user_mail_list = list(set(umlp + uma))

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
            for mail in user_mail_list:
                mail_class = GlobleMailSend('ATAP-PM', user_mail_list)
                print('mail_class',mail_class)
                mail_thread = Thread(target = mail_class.mailsend, args = (mail_data,None))
                mail_thread.start()
        
        #===============================================#

        # ============= Sms Send Step ==============#

        message_data = {
            'name':None
        }
        sms_class = GlobleSmsSendTxtLocal('ATTAPR',emp_mob_no)
        # sms_class = GlobleSmsSendTxtLocal('ATTPR',['7595914029'])
        sms_thread = Thread(target = sms_class.sendSMS, args = (message_data,'sms'))
        sms_thread.start()


    return True

'''
    @ Added by Rupam Hazra
'''
def my_attendence_pending_mail_on_every_week():

    '''
        ATTENDENCE REMINDER FOR ALL HRMS & ATTENDENCE USER 
    '''
    print('Current Time :: ',datetime.now())
    # current_date = datetime.now().date()
    # current_month = current_date.month
    # print("current_date",current_date)

    # user_list=TMasterModuleRoleUser.objects.filter(
    #                 Q(mmr_type=3),Q(mmr_is_deleted=False),
    #                 Q(mmr_module__cm_name='ATTENDANCE & HRMS')).\
    #                 values_list('mmr_user',flat=True).distinct()
    # #email extraction            
    # user_mail_list_primary=TMasterModuleRoleUser.objects.filter(
    #                 Q(mmr_type=3),Q(mmr_is_deleted=False),
    #                 Q(mmr_module__cm_name='ATTENDANCE & HRMS'),
    #                 (Q(mmr_user__email__isnull=False) & ~Q(mmr_user__email=""))).\
    #                 values('mmr_user__email').distinct()

    # user_mail_official = TCoreUserDetail.objects.filter(
    #     (Q(cu_alt_email_id__isnull=False) & ~Q(cu_alt_email_id="")),cu_user__in=list(user_list)).\
    #         values('cu_alt_email_id').distinct()
    # # print("user_mail_list_primary",user_mail_list_primary)
    # # print("user_mail_official",user_mail_official)
    # umlp = [x['mmr_user__email'] for x in user_mail_list_primary]
    # uma = [x['cu_alt_email_id'] for x in user_mail_official]

    # user_mail_list = list(set(umlp + uma))
    # print("user_mail_list",user_mail_list)
    
    # emp_mob = TCoreUserDetail.objects.filter(cu_user__in=list(user_list),cu_phone_no__isnull=False).\
    #     values('cu_phone_no').distinct()
    # emp_mob_no = [ x['cu_phone_no'] for x in emp_mob ]

    # print("user_mail_list",user_mail_list)

    '''
        MAIL Functionality
    '''
    user_mail_list = ['rupam@shyamfuture.com','bubai.das@shyamfuture.com']
    print("email",user_mail_list)
    if user_mail_list:
        mail_data = {
        'name':None
        }
        print('mail_data',mail_data)
        mail_class = GlobleMailSend('ATP-PM-EW', user_mail_list)
        mail_thread = Thread(target = mail_class.mailsend, args = (mail_data,None))
        mail_thread.start()
        #mail_list=[]
        # while len(user_mail_list)>0:
        #     dummy_mail_list = user_mail_list[0:5]
        #     user_mail_list = list(set(user_mail_list) - set(dummy_mail_list ))
        #     print("user_mail_list",user_mail_list)
        #     mail_class = GlobleMailSend('ATP-PM', dummy_mail_list)
        #     mail_thread = Thread(target = mail_class.mailsend, args = (mail_data,None))
        #     mail_thread.start()
    
    '''
        SMS Functionality
    '''
    # if emp_mob_no:
    #     message_data = {
    #         'name':None
    #     }
    #     sms_class = GlobleSmsSendTxtLocal('ATTPR',emp_mob_no)
    #     sms_thread = Thread(target = sms_class.sendSMS, args = (message_data,'sms'))
    #     sms_thread.start()

    return True

'''
    @ Added by Rupam Hazra
'''
def my_attendence_pending_mail_on_every_friday_in_a_week():

    '''
        ATTENDENCE REMINDER FOR ALL HRMS & ATTENDENCE USER 
    '''
    print('Current Time :: ',datetime.now())
    print('===============================')
    # current_date = datetime.now().date()
    # current_month = current_date.month
    # print("current_date",current_date)

    user_list=TMasterModuleRoleUser.objects.filter(
                    Q(mmr_type=3),Q(mmr_is_deleted=False),
                    Q(mmr_module__cm_name='ATTENDANCE & HRMS')).\
                    values_list('mmr_user',flat=True).distinct()
    #email extraction            
    user_mail_list_primary=TMasterModuleRoleUser.objects.filter(
                    Q(mmr_type=3),Q(mmr_is_deleted=False),
                    Q(mmr_module__cm_name='ATTENDANCE & HRMS'),
                    (Q(mmr_user__email__isnull=False) & ~Q(mmr_user__email=""))).\
                    values('mmr_user__email').distinct()

    user_mail_official = TCoreUserDetail.objects.filter(
        (Q(cu_alt_email_id__isnull=False) & ~Q(cu_alt_email_id="")),cu_user__in=list(user_list)).\
            values('cu_alt_email_id').distinct()
    # print("user_mail_list_primary",user_mail_list_primary)
    # print("user_mail_official",user_mail_official)
    umlp = [x['mmr_user__email'] for x in user_mail_list_primary]
    uma = [x['cu_alt_email_id'] for x in user_mail_official]

    user_mail_list = list(set(umlp + uma))
    print("user_mail_list",user_mail_list)
    
    emp_mob = TCoreUserDetail.objects.filter(cu_user__in=list(user_list),cu_phone_no__isnull=False).\
        values('cu_phone_no').distinct()
    emp_mob_no = [ x['cu_phone_no'] for x in emp_mob ]

    print("user_mail_list",user_mail_list)
    print("user_mail_list",len(user_mail_list))

    '''
        MAIL Functionality
    '''
    #user_mail_list = ['rupam@shyamfuture.com']
    
    if user_mail_list:
        mail_data = {
        'name':None
        }
        print('mail_data',mail_data)
        mail_class = GlobleMailSend('ATP-PM-EW', user_mail_list)
        mail_thread = Thread(target = mail_class.mailsend, args = (mail_data,None))
        mail_thread.start()

    '''
        SMS Functionality
    '''
    if emp_mob_no:
        message_data = {
            'name':None
        }
        sms_class = GlobleSmsSendTxtLocal('ATTPR',emp_mob_no)
        sms_thread = Thread(target = sms_class.sendSMS, args = (message_data,'sms'))
        sms_thread.start()

    return True
