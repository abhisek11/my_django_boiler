from celery import shared_task
import time
from smssend.views import GlobleSmsSendTxtLocal
from mailsend.views import GlobleMailSend


@shared_task
def hello(sleep_time):
    time.sleep(sleep_time)
    print('Hello there! ',sleep_time)
    return {'test': 'hello there!!!'}

@shared_task
def unjustified_sms_alert_to_all_employee_task(*args, **kwargs):
    task_response = dict()
    try:
        #print('all_employee_mail_kwargs:', kwargs)
        last_justification_date = kwargs['last_justification_date']
        user_phone_no = kwargs['user_phone_no']
        unjustified_attendance_requests = kwargs['unjustified_attendance_requests']
        '''
            Description: Sms alert for all employees for unjustified request(Grace, HD, FD, MM, etc.).
            Name: Unjustified Request Alert For Employees
            Code: AT-URAFE
            Subject: Alert!!! Unjustified Requests
            Txt content:
                You have total {{ unjustified_attendance_requests }} unjustified requests left. Please justify your attendance deviation 
                with a proper remarks before {{ last_justification_date }}.
            Contain variable:  unjustified_attendance_requests, last_justification_date
        '''
        
        message_data = {
            'unjustified_attendance_requests': unjustified_attendance_requests,
            'last_justification_date': last_justification_date
        }
        
        sms_class = GlobleSmsSendTxtLocal('AT-URAFE',[user_phone_no])
        print('sms_class:',sms_class)
        print('user.cu_alt_phone_no:', user_phone_no)
        sms_response = sms_class.sendSMS(message_data,'sms')
        print('sms_response:',sms_response)
        task_response['phone'] = user_phone_no
        task_response['unjustified_attendance_requests_count'] = len(unjustified_attendance_requests)
        task_response['status'] = 'Success'
    except Exception as e:
        print(str(e))
        task_response['status'] = 'Error'
        task_response['message'] = str(e)

    return task_response

@shared_task
def unjustified_mail_alert_to_all_employee_task(*args, **kwargs):
    task_response = dict()
    try:
        last_justification_date = kwargs['last_justification_date']
        user_email = kwargs['user_email']
        unjustified_attendance_requests = kwargs['unjustified_attendance_requests']
        '''
            Description: Mail alert for all employees for unjustified request(Grace, HD, FD, MM, etc.).
            Name: Unjustified Request Alert For Employees
            Code: AT-URAFE
            Subject: Alert!!! Unjustified Requests
            Html content: 
                You have total {{ unjustified_attendance_requests }} unjustified requests left. Please justify your attendance 
                deviation with a proper remarks before {{ last_justification_date }}.

                Date            Duration Deviation(minutes)
                2019-12-19      34
                2019-12-21      78

            Template variable: unjustified_attendance_requests, last_justification_date
        '''
        
        mail_data = {
            'last_justification_date': last_justification_date,
            'unjustified_attendance_requests': unjustified_attendance_requests
        }
        mail_class = GlobleMailSend('AT-URAFE', [user_email])
        print('mail_class:', mail_class)
        print('user.cu_alt_email_id', user_email)
        mail_response = mail_class.mailsend(mail_data)
        print('mail_response:', mail_response)
        # mail_thread = Thread(target = mail_class.mailsend, args = (mail_data,))
        # mail_thread.start()

        task_response['mail'] = user_email
        task_response['unjustified_attendance_requests_count'] = len(unjustified_attendance_requests)
        task_response['status'] = 'Success'
    except Exception as e:
        print(str(e))
        task_response['status'] = 'Error'
        task_response['message'] = str(e)

    return task_response

@shared_task
def pending_sms_alert_to_reporting_head(*args, **kwargs):
    task_response = dict()
    try:
        reporting_head_phone = kwargs['reporting_head_phone']
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
        Code: AT-PRAAFRH
        Subject: Alert!!! Pending Approval Request
        Txt content:
            You have total {{ pending_approval_requests }} pending approval requests left of your team members. 
            Please approve/reject/release the pending request from team attendance with a proper remarks before {{ last_approval_date }}.
        Contain variable:  pending_approval_requests, last_approval_date
        '''
        
        message_data = {
            'pending_approval_requests': pending_approval_requests,
            'last_approval_date': last_approval_date
        }
        sms_class = GlobleSmsSendTxtLocal('AT-PRAAFRH',[reporting_head_phone])
        print('sms_class:',sms_class)
        print('reporting_head_phone:', reporting_head_phone)
        sms_response = sms_class.sendSMS(message_data,'sms')
        print('sms_response:', sms_response)
        # sms_thread = Thread(target = sms_class.sendSMS, args = (message_data,'sms'))
        # sms_thread.start()
        
        task_response['phone'] = reporting_head_phone
        task_response['pending_approval_requests_count'] = len(pending_approval_requests)
        task_response['status'] = 'Success'
    except Exception as e:
        print(str(e))
        task_response['status'] = 'Error'
        task_response['message'] = str(e)

    return task_response

@shared_task
def pending_mail_alert_to_reporting_head(*args, **kwargs):
    task_response = dict()
    try:
        reporting_head_email = kwargs['reporting_head_email']
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
        
        '''
        Description: 
            Mail alert for Reporting Head to approve/reject/release the pending requests(Grace, HD, FD, MM, etc.) 
            requested by team members.
        Name: Pending Approval Request Alert For  Reporting Head
        Code: AT-PRAAFRH
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
        mail_class = GlobleMailSend('AT-PRAAFRH', [reporting_head_email])
        print('mail_class:', mail_class)
        print('reporting_head_email:', reporting_head_email)
        mail_response = mail_class.mailsend(mail_data)
        print('mail_response:', mail_response)
        # mail_thread = Thread(target = mail_class.mailsend, args = (mail_data,))
        # mail_thread.start()
        
        task_response['mail'] = reporting_head_email
        task_response['pending_approval_requests_count'] = len(pending_approval_requests)
        task_response['status'] = 'Success'
    except Exception as e:
        print(str(e))
        task_response['status'] = 'Error'
        task_response['message'] = str(e)

    return task_response
    