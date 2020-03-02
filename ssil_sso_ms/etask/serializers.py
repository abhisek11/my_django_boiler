from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from etask.models import *
from django.contrib.auth.models import *
from django.db import transaction, IntegrityError
from drf_extra_fields.fields import Base64ImageField
import os
import datetime
from custom_exception_message import *
from mailsend.views import *
from threading import Thread   
from datetime import datetime
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from users.models import TCoreUserDetail
from smssend.views import *
from threading import Thread
from django.db.models import When, Case, Value, CharField, IntegerField, F, Q
from global_function import department,designation,userdetails,getHostWithPort,raw_query_extract


class EtaskTaskAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    user_cc = serializers.ListField(required=False)
    assignto = serializers.ListField(required=False)
    reporting_date = serializers.ListField(required=False)
    is_forcefully = serializers.BooleanField(required=False)
    followup_date = serializers.DateTimeField(required=False)
    class Meta:
        model = EtaskTask
        fields = '__all__'
        extra_fields = ('user_cc','assignto','reporting_date')
    
    def create(self,validated_data):
        try:
            with transaction.atomic():
                created_by = validated_data.get('created_by')
                owned_by = validated_data.get('owned_by')
                is_forcefully = validated_data.pop('is_forcefully') if 'is_forcefully' in validated_data.keys() else False
                followup_date = validated_data.pop('followup_date') if 'followup_date' in validated_data.keys() else None
                # followup_date = datetime.strptime(validated_data.pop('followup_date'), "%Y-%m-%dT%H:%M:%S.%fZ") if 'followup_date' in validated_data else None
                print("followup_date",followup_date)
                user_cc = validated_data.pop('user_cc') if 'user_cc' in validated_data else ""
                # assignto = validated_data.pop('assignto') if 'assignto' in validated_data else ""
                reporting_date = validated_data.pop('reporting_date') if 'reporting_date' in validated_data else ""

                print("validated_data['task_categories']", validated_data['start_date'])

                if validated_data['task_type']==3:
                    start_date_data = validated_data['start_date'].date()
                    end_date_data = validated_data['end_date'].date()
                    if EtaskTask.objects.filter(start_date__date__lte=start_date_data,end_date__date__gte=end_date_data,
                        id=validated_data['parent_id']):
                        print("PROPER TIME")
                    else:
                        raise APIException({'msg':'Please put Task date in between parent task date range',
                                    "request_status": 0
                                    })


                if validated_data['task_categories']==1:
                    validated_data["owner"]=created_by
                    validated_data["assign_by"]= created_by
                    validated_data["assign_to"]= created_by
                elif validated_data['task_categories']==2:
                    validated_data["assign_by"]=validated_data['owner']
                    validated_data["assign_to"]=created_by
                elif validated_data['task_categories']==3:
                    validated_data["assign_by"]=created_by
                    validated_data['owner']=created_by              

            ### Etask Created modified By Manas Paul,[ get_or_create --> create ], Cause Tak Subject can not possible to create same Subject ###
            ### Changing approved by Tonmoy Sardar ###
                if validated_data["assign_to"] and reporting_date != "" and is_forcefully is False:
                    for report_dt in reporting_date:
                        reporting_date_data = datetime.strptime(report_dt['reporting_date'], "%Y-%m-%dT%H:%M:%S.%fZ")
                        if EtaskTask.objects.filter(Q(Q(task_status=1)|Q(task_status=3)),
                                                            Q(Q(assign_to_id=validated_data["assign_to"])|
                                                            Q(sub_assign_to_user_id=validated_data["assign_to"])),
                                                            id__in=list(ETaskReportingDates.objects.filter(task_type=1,reporting_status=2,
                                                            reporting_date=reporting_date_data).values_list('task',flat=True))):
                            '''
                                "request_status": 2 >> User define exception or condition checking by front end
                            '''
                            reporting_date_formet = reporting_date_data.strftime("%m/%d/%Y, %I:%M:%S %p")
                            raise APIException({'msg': reporting_date_formet+' is already blocked on your Calendar',
                                                "request_status": 2
                                                })
                    

                task_create = EtaskTask.objects.create(         
                    **validated_data
                )
                EtaskTask.objects.filter(id=task_create.id).update(task_code_id="TSK"+str(task_create.id))
                print("task_create.id",task_create.id)

                if followup_date:
                    print("followup_date",followup_date)
                    if validated_data['task_categories']==1:
                        EtaskFollowUP.objects.get_or_create(task=task_create,assign_to=created_by,follow_up_task=validated_data['task_subject'],
                                                            follow_up_date=followup_date,created_by=created_by)
                    else:
                        if 'assign_to' in validated_data:
                            EtaskFollowUP.objects.get_or_create(task=task_create,follow_up_task=validated_data['task_subject'],
                                                                assign_to=validated_data["assign_to"],follow_up_date=followup_date,created_by=validated_data["assign_to"])
                        if 'owner' in validated_data:
                            EtaskFollowUP.objects.get_or_create(task=task_create,follow_up_task=validated_data['task_subject'],
                                                                assign_to=validated_data['owner'],follow_up_date=followup_date,created_by=validated_data['owner'])
                
                usercc_list = []
                for u_cc in user_cc:
                    ucc_details,created_1 = EtaskUserCC.objects.get_or_create(
                        task = task_create, ** u_cc, created_by=created_by , owned_by = owned_by
                    )
                    ucc_details.__dict__.pop('_state') if "_state" in ucc_details.__dict__.keys() else ucc_details.__dict__
                    usercc_list.append(ucc_details.__dict__)
              
                reporting_date_list = []
                print("task_create",task_create.__dict__['id'])
                # print("r_date['reporting_date']",r_date['reporting_date'])
                reporting_date_str = """"""
                r_time = ''
                ics_data = """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN\n"""
                user_name = userdetails(int(task_create.__dict__['assign_to_id']))
                count_id = 0
                for r_date in reporting_date:
                    rdate_details,created = ETaskReportingDates.objects.get_or_create(
                        task_type=1,
                        task = task_create.__dict__['id'],
                        reporting_date = datetime.strptime(r_date['reporting_date'], "%Y-%m-%dT%H:%M:%S.%fZ"),
                        created_by=created_by,
                        owned_by=owned_by
                    )
                    # print('rdate_details',rdate_details,type(rdate_details))
                    reporting_log,created=ETaskReportingActionLog.objects.get_or_create(
                                                                                        task_id = task_create.__dict__['id'],
                                                                                        reporting_date_id =str(rdate_details),
                                                                                        updated_date=datetime.now().date(),
                                                                                        status=2,
                                                                                        created_by=created_by,
                                                                                        owned_by=owned_by
                                                                                    )
                    # print('reporting_log',reporting_log)

                    rdate_details.__dict__.pop('_state') if "_state" in rdate_details.__dict__.keys() else rdate_details.__dict__
                    reporting_date_list.append(rdate_details.__dict__)
                    ###################################################
                    count_id += 1
                    # reporting_date_str += datetime.strptime(x['reporting_date'], "%m/%d/%Y, %I:%M:%S %p")+'\n'
                    reporting_date_str += str(count_id)+'. '+rdate_details.__dict__['reporting_date'].strftime("%m/%d/%Y, %I:%M:%S %p")+" "
                    r_time = rdate_details.__dict__['reporting_date'].strftime("%Y%m%dT%H%M%S")
                    ics_data +=   """BEGIN:VEVENT
SUMMARY:Reporting of {rep_sub}
DTSTART;TZID=Asia/Kolkata:{r_time}
LOCATION:Shyam Tower,Kolkata-700091
DESCRIPTION: Reporting dates.
STATUS:CONFIRMED
SEQUENCE:3
BEGIN:VALARM
TRIGGER:-PT10M
DESCRIPTION:Pickup Reminder
ACTION:DISPLAY
END:VALARM
END:VEVENT\n""".replace("{r_time}",r_time).replace("{rep_sub}",task_create.__dict__['task_subject'])


                
                ##############################################################
                #DTEND;TZID=Asia/Kolkata:{r_time}
                ics_data += "END:VCALENDAR"
                print("reporting_date_str",reporting_date_str)
                user_email = User.objects.get(id=task_create.__dict__['assign_to_id']).email
                print("user_email",user_email)
                
                if user_email:
                    mail_data = {
                                "recipient_name" : user_name,        ## modified by manas Paul 21jan20
                                "task_subject": task_create.__dict__['task_subject'],
                                "reporting_date": reporting_date_str,
                            }
                    # print('mail_data',mail_data)
                    # print('mail_id-->',mail)
                    # print('mail_id-->',[mail])
                    # mail_class = GlobleMailSend('ETAP', email_list)
                    mail_class = GlobleMailSend('ETRDC', [user_email])
                    print('mail_class',mail_class)
                    mail_thread = Thread(target = mail_class.mailsend, args = (mail_data,ics_data))
                    print('mail_thread-->',mail_thread)
                    mail_thread.start()

                ######################################  

                validated_data['user_cc']=usercc_list
                # validated_data['assignto']=assignto_list
                validated_data['reporting_date']=reporting_date_list
                return validated_data

        except Exception as e:
            raise e
            # raise APIException({'request_status': 0, 'msg': e})

class EtaskTaskRepostSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = EtaskTask
        fields = '__all__'


class EtaskTaskEditSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    user_cc = serializers.ListField(required=False)
    assignto = serializers.ListField(required=False)
    reporting_date = serializers.ListField(required=False)
    reporting_date_new = serializers.ListField(required=False)
    is_forcefully = serializers.BooleanField(required=False)
    followup_date = serializers.DateTimeField(required=False)
    class Meta:
        model = EtaskTask
        fields = '__all__'
        extra_fields = ('user_cc','assignto','reporting_date','reporting_date_new')
    
    def update(self,instance,validated_data):
        try:
            with transaction.atomic():
                created_by = validated_data.get('created_by')
                owned_by = validated_data.get('owned_by')
                updated_by = validated_data.get('updated_by')
                
                is_forcefully = validated_data.pop('is_forcefully') if 'is_forcefully' in validated_data.keys() else False
                followup_date = validated_data.pop('followup_date') if 'followup_date' in validated_data.keys() else None
                # followup_date = datetime.strptime(validated_data.pop('followup_date'), "%Y-%m-%dT%H:%M:%S.%fZ") if 'followup_date' in validated_data else None
                #print("followup_date",followup_date)
                user_cc = validated_data.pop('user_cc') if 'user_cc' in validated_data else ""
                # assignto = validated_data.pop('assignto') if 'assignto' in validated_data else ""
                reporting_date = validated_data.pop('reporting_date') if 'reporting_date' in validated_data else ""

                #print("validated_data['task_categories']", validated_data['start_date'])

                if validated_data['task_type']==3:
                    start_date_data = validated_data['start_date'].date()
                    end_date_data = validated_data['end_date'].date()
                    if EtaskTask.objects.filter(
                        start_date__date__lte=start_date_data,
                        end_date__date__gte=end_date_data,
                        id=validated_data['parent_id']):
                        print("PROPER TIME")
                    else:
                        raise APIException({'msg':'Please put Task date in between parent task date range',
                                    "request_status": 0
                                    })


                if validated_data['task_categories']==1:
                    validated_data["owner"]=updated_by
                    validated_data["assign_by"]= updated_by
                    validated_data["assign_to"]= updated_by

                elif validated_data['task_categories']==2:
                    validated_data["assign_by"]=validated_data['owner']
                    validated_data["assign_to"]=updated_by

                elif validated_data['task_categories']==3: # task_categories - assign_to
                    validated_data["assign_by"]=updated_by
                    validated_data['owner']=updated_by  
                    EtaskTaskEditLog.objects.create(
                        **validated_data
                    )          

            ### Etask Created modified By Manas Paul,[ get_or_create --> create ], Cause Tak Subject can not possible to create same Subject ###
            ### Changing approved by Tonmoy Sardar ###
                if validated_data["assign_to"] and reporting_date != "" and is_forcefully is False:
                    #print('validated_data["assign_to"]',validated_data["assign_to"])
                    for report_dt in reporting_date:
                        reporting_date_data = datetime.strptime(report_dt['reporting_date'], "%Y-%m-%dT%H:%M:%S.%fZ")
                        print('reporting_date_data',reporting_date_data)
                        if EtaskTask.objects.filter(Q(Q(task_status=1)|Q(task_status=3)),
                                                            Q(Q(assign_to_id=validated_data["assign_to"])|
                                                            Q(sub_assign_to_user_id=validated_data["assign_to"])),
                                                            id__in=list(ETaskReportingDates.objects.filter(task_type=1,reporting_status=2,
                                                            reporting_date=reporting_date_data).values_list('task',flat=True))):
                            '''
                                "request_status": 2 >> User define exception or condition checking by front end
                            '''
                            reporting_date_formet = reporting_date_data.strftime("%m/%d/%Y, %I:%M:%S %p")
                            raise APIException({'msg': reporting_date_formet+' is already blocked on your Calendar',
                                                "request_status": 2
                                                })
                    

                # task_create = EtaskTask.objects.create(         
                #     **validated_data
                # )
                print('task filtrer....',EtaskTask.objects.filter(pk=instance.id))
                task_update1 = EtaskTask.objects.filter(         
                   pk=instance.id
                ).update(**validated_data)

                #EtaskTask.objects.filter(id=task_create.id).update(task_code_id="TSK"+str(task_create.id))
                print("task_update.id",task_update1,type(task_update1))
                task_update = EtaskTask.objects.get(pk=task_update1)
                
                if followup_date:
                    print("followup_date",followup_date)
                    if validated_data['task_categories']==1:
                        EtaskFollowUP.objects.filter(task=instance).delete()
                        EtaskFollowUP.objects.create(task=instance,assign_to=created_by,follow_up_task=validated_data['task_subject'],
                                                            follow_up_date=followup_date,created_by=created_by)
                    else:
                        if 'assign_to' in validated_data:
                            EtaskFollowUP.objects.filter(task=instance).delete()
                            EtaskFollowUP.objects.create(task=instance,follow_up_task=validated_data['task_subject'],
                                                                assign_to=validated_data["assign_to"],follow_up_date=followup_date,created_by=validated_data["assign_to"])
                        
                            
                        if 'owner' in validated_data:
                            EtaskFollowUP.objects.filter(task=instance).delete()
                            EtaskFollowUP.objects.create(task=instance,follow_up_task=validated_data['task_subject'],
                                                                assign_to=validated_data['owner'],follow_up_date=followup_date,created_by=validated_data['owner'])
                
                usercc_list = []
                for u_cc in user_cc:
                    
                    EtaskUserCC.objects.filter(task = instance).delete()
                    ucc_details= EtaskUserCC.objects.create(task=instance,
                         ** u_cc, created_by=created_by , owned_by = owned_by
                    )
                    ucc_details.__dict__.pop('_state') if "_state" in ucc_details.__dict__.keys() else ucc_details.__dict__
                    usercc_list.append(ucc_details.__dict__)
                
                reporting_date_list = []
                #print("task_create",task_create.__dict__['id'])
                reporting_date_str = """"""
                r_time = ''
                ics_data = """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN\n"""
                user_name = userdetails(int(task_update.__dict__['assign_to_id']))
                count_id = 0
                ETaskReportingDates.objects.filter(task = task_update.__dict__['id']).delete()
                ETaskReportingActionLog.objects.filter(task = task_update.__dict__['id']).delete()
                for r_date in reporting_date:
                    rdate_details,created = ETaskReportingDates.objects.get_or_create(
                        task_type=1,
                        task = task_update.__dict__['id'],
                        reporting_date = datetime.strptime(r_date['reporting_date'], "%Y-%m-%dT%H:%M:%S.%fZ"),
                        created_by=created_by,
                        owned_by=owned_by
                    )
                    # print('rdate_details',rdate_details,type(rdate_details))

                    reporting_log, created=ETaskReportingActionLog.objects.get_or_create(task_id = task_update.__dict__['id'],
                                                                                        reporting_date_id =str(rdate_details),
                                                                                        updated_date=datetime.now().date(),
                                                                                        status=2,
                                                                                        created_by=created_by,
                                                                                        owned_by=owned_by
                                                                                    )
                    # print('reporting_log',reporting_log)

                    rdate_details.__dict__.pop('_state') if "_state" in rdate_details.__dict__.keys() else rdate_details.__dict__
                    reporting_date_list.append(rdate_details.__dict__)
                    ###################################################
                    count_id += 1
                    # reporting_date_str += datetime.strptime(x['reporting_date'], "%m/%d/%Y, %I:%M:%S %p")+'\n'
                    reporting_date_str += str(count_id)+'. '+rdate_details.__dict__['reporting_date'].strftime("%m/%d/%Y, %I:%M:%S %p")+" "
                    r_time = rdate_details.__dict__['reporting_date'].strftime("%Y%m%dT%H%M%S")
                    ics_data +=   """BEGIN:VEVENT
SUMMARY:Reporting of {rep_sub}
DTSTART;TZID=Asia/Kolkata:{r_time}
LOCATION:Shyam Tower,Kolkata-700091
DESCRIPTION: Reporting dates.
STATUS:CONFIRMED
SEQUENCE:3
BEGIN:VALARM
TRIGGER:-PT10M
DESCRIPTION:Pickup Reminder
ACTION:DISPLAY
END:VALARM
END:VEVENT\n""".replace("{r_time}",r_time).replace("{rep_sub}",task_update.__dict__['task_subject'])


                
                ##############################################################
                #DTEND;TZID=Asia/Kolkata:{r_time}
                ics_data += "END:VCALENDAR"
                print("reporting_date_str",reporting_date_str)
                user_email = User.objects.get(id=task_update.__dict__['assign_to_id']).email
                print("user_email",user_email)
                
                # if user_email:
                #     mail_data = {
                #                 "recipient_name" : user_name,        ## modified by manas Paul 21jan20
                #                 "task_subject": task_create.__dict__['task_subject'],
                #                 "reporting_date": reporting_date_str,
                #             }
                #     # print('mail_data',mail_data)
                #     # print('mail_id-->',mail)
                #     # print('mail_id-->',[mail])
                #     # mail_class = GlobleMailSend('ETAP', email_list)
                #     mail_class = GlobleMailSend('ETRDC', [user_email])
                #     print('mail_class',mail_class)
                #     mail_thread = Thread(target = mail_class.mailsend, args = (mail_data,ics_data))
                #     print('mail_thread-->',mail_thread)
                #     mail_thread.start()

                ######################################  

                validated_data['user_cc']=usercc_list
                # validated_data['assignto']=assignto_list
                validated_data['reporting_date']=reporting_date_list
                return validated_data

        except Exception as e:
            raise e
            # raise APIException({'request_status': 0, 'msg': e})

class EtaskTaskDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = EtaskTask
        fields = '__all__'
    def update(self,instance,validated_data):
        try:
            updated_by=validated_data.get('updated_by')
            with transaction.atomic():
                instance.is_deleted=True
                instance.updated_by=updated_by
                instance.save()
                user_cc=EtaskUserCC.objects.filter(task=instance,is_deleted=False).update(is_deleted=True,updated_by_id=updated_by)
                reporting_dates=ETaskReportingDates.objects.filter(task=str(instance),task_type=1,is_deleted=False).update(is_deleted=True,updated_by_id=updated_by)
                reporting_action_log=ETaskReportingActionLog.objects.filter(task=instance,is_deleted=False).update(is_deleted=True,updated_by_id=updated_by)
                comments=ETaskComments.objects.filter(task=instance,is_deleted=False)
                if comments:
                    for e_c in comments:
                        e_c.is_deleted=True
                        e_c.updated_by=updated_by
                        e_c.save()
                        # print('advance_comment',e_c.advance_comment)
                        cost_details=EtaskIncludeAdvanceCommentsCostDetails.objects.filter(etcomments_id=e_c.id,is_deleted=False).update(is_deleted=True,updated_by_id=updated_by)
                        other_details=EtaskIncludeAdvanceCommentsOtherDetails.objects.filter(etcomments_id=e_c.id,is_deleted=False).update(is_deleted=True,updated_by_id=updated_by)
                        document_details=EtaskIncludeAdvanceCommentsDocuments.objects.filter(etcomments_id=e_c.id,is_deleted=False).update(is_deleted=True,updated_by_id=updated_by)
                
                return instance
        except Exception as e:
            raise e

class EtaskParentTaskListSerializer(serializers.ModelSerializer):
    class Meta:
        model = EtaskTask
        fields = ('id','task_subject','start_date','end_date')

class EtaskMyTaskListSerializer(serializers.ModelSerializer):
    class Meta:
        model = EtaskTask
        fields = ('id','parent_id','task_subject','task_description','start_date','end_date','task_status','completed_date',
                    'task_code_id','closed_date','extended_date','assign_by','assign_to','sub_assign_to_user','get_task_status_display') #,'assign_by_name','sub_task_list','sub_assign_to_name')

class EtaskCompletedTaskListSerializer(serializers.ModelSerializer):
    class Meta:
        model = EtaskTask
        fields = ('id','parent_id','task_subject','task_description','start_date','end_date','task_status','completed_date',
                    'task_code_id','extended_date','assign_by','assign_to','sub_assign_to_user') #,'sub_assign_to_user','assign_to_name','sub_task_list','sub_assign_to_name')


class EtaskClosedTaskListSerializer(serializers.ModelSerializer):
    class Meta:
        model = EtaskTask
        fields = ('id','task_code_id','parent_id','task_subject','task_description','start_date','end_date','task_status','closed_date',
                    'extended_date','assign_by','assign_to','sub_assign_to_user','get_task_status_display') #,'assign_to_name','sub_task_list', 'sub_assign_to_name','assign_by_name')

    

class EtaskOverdueTaskListSerializer(serializers.ModelSerializer):
    class Meta:
        model = EtaskTask
        fields = ('id','task_code_id','parent_id','task_subject','task_description','start_date','end_date','task_status','completed_date',
                    'extended_date','assign_by','assign_to','sub_assign_to_user','sub_assign_to_user') #,'assign_to_name','sub_task_list','sub_assign_to_name','assign_by_name','overdue_by_day')
   

class EtasktaskListSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = EtaskTask
        fields = ('id','parent_id','task_subject')


class EtaskTaskStatusListSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    
    class Meta:
        model = EtaskTask
        fields = '__all__'


class ETaskAllTasklistSerializer(serializers.ModelSerializer):
    parent_task=serializers.SerializerMethodField(required=False)
    sub_data = EtaskTask.objects.filter(parent_id=0,is_deleted=False)
    task_type_name=serializers.CharField(source='get_task_type_display')
    recurrance_frequency_name=serializers.CharField(source='get_recurrance_frequency_display')
    task_status_name=serializers.CharField(source='get_task_status_display')
    assign_by_name = serializers.SerializerMethodField()
    assign_to_name= serializers.SerializerMethodField()
    sub_assign_to_user_name= serializers.SerializerMethodField()

    class Meta:
        model = EtaskTask
        fields = ('__all__')

    def get_parent_task(self,EtaskTask):
        if EtaskTask.parent_id:
            if EtaskTask.parent_id !=0:
                if self.sub_data.filter(id=EtaskTask.parent_id).values('id','task_subject'):
                    parent_data=self.sub_data.filter(id=EtaskTask.parent_id).values('id','task_subject')[0]
                    return parent_data

    def user_name(self, user_id):
        name = None
        full_name = ""
        name = User.objects.get(id=user_id)
        if name:
            full_name =  name.__dict__['first_name']+" "+name.__dict__['last_name']
        return full_name

    def get_assign_by_name(self,EtaskTask):
        name = None
        full_name = ""
        if EtaskTask.assign_by:
            name = User.objects.get(id=EtaskTask.assign_by.id)
            if name:
                full_name =  name.__dict__['first_name']+" "+name.__dict__['last_name']
                # print("full_name",full_name)
            return full_name

    def get_sub_assign_to_user_name(self,EtaskTask):
        name=None
        full_name=""
        if EtaskTask.sub_assign_to_user:
            name=User.objects.get(id=EtaskTask.sub_assign_to_user.id)
            if name:
                full_name= name.__dict__['first_name']+" "+name.__dict__['last_name']
                return full_name

    def get_assign_to_name(self,EtaskTask):
        name=None
        full_name=""
        if EtaskTask.assign_to:
            name =User.objects.get(id=EtaskTask.assign_to.id)
            if name:
                full_name=name.__dict__['first_name']+" "+name.__dict__['last_name']
                return full_name

class ETaskUpcomingCompletionListSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = EtaskTask
        fields = '__all__'

class EtaskTaskCompleteViewSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    # completed_date = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = EtaskTask
        fields = '__all__'
    def update(self, instance, validated_data):
        try:
            with transaction.atomic():
                current_date = datetime.now()
                end_date = instance.end_date.date()
                # print('end_date-->',end_date)
                updated_by = validated_data.get('updated_by')
                # print('parent_id',instance.parent_id)
                flag=False
                if instance.parent_id == 0:
                    child_task=EtaskTask.objects.filter(parent_id=str(instance),is_deleted=False).values('task_status')
                    if child_task:
                        # print('child_task',child_task)         
                        for c_t in child_task:
                            # print('c_t',c_t['task_status'])
                            if c_t['task_status'] != 2:
                                flag=True
                        # return flag
                        print('flag',flag)
                    else:
                        instance.task_status=2
                        instance.completed_date = current_date
                        instance.completed_by=updated_by
                        instance.is_closure=True
                        instance.updated_by = updated_by
                        instance.save()
                        reporting_status = ETaskReportingDates.objects.filter(task_type=1,
                                                                        task=instance.id,
                                                                        reporting_date__date=end_date).values('reporting_status')
                        # print('reporting_status->',reporting_status)
                        if reporting_status:
                            if int(reporting_status[0]['reporting_status']) == 0 or int(reporting_status[0]['reporting_status']) == 2 :
                                etask_reporting_dates = ETaskReportingDates.objects.filter(task_type=1,task=instance.id,is_deleted=False)

                                # print('etask_reporting_dates-->',etask_reporting_dates)
                                if etask_reporting_dates:
                                    for e_r in etask_reporting_dates:
                                        e_r.reporting_status=3
                                        e_r.actual_reporting_date = current_date
                                        e_r.updated_by = updated_by
                                        e_r.save()
                                        action_log=ETaskReportingActionLog.objects.create(task_id = instance.id,
                                                                            reporting_date_id=e_r.id,
                                                                            status = 3,
                                                                            updated_by = updated_by
                                                                            )
                                        # print('action_log-->',action_log)
                            else:
                                etask_reporting_dates = ETaskReportingDates.objects.filter(task_type=1,task=instance.id,is_deleted=False)

                                # print('etask_reporting_dates-->',etask_reporting_dates)
                                if etask_reporting_dates:
                                    action_log=ETaskReportingActionLog.objects.create(task_id = instance.id,
                                                                        status = 4,
                                                                        updated_by = updated_by
                                                                        )
                                    # print('action_log-->',action_log)
                        return instance
                    
                if flag == False or instance.parent_id != 0:
                    instance.task_status=2
                    instance.completed_date = current_date
                    instance.completed_by=updated_by
                    instance.is_closure=True
                    instance.updated_by = updated_by
                    instance.save()
                    reporting_status = ETaskReportingDates.objects.filter(task_type=1,
                                                                        task=instance.id,
                                                                        reporting_date__date=end_date).values('reporting_status')
                    # print('reporting_status->',reporting_status[0]['reporting_status'])
                    if reporting_status:
                        if int(reporting_status[0]['reporting_status']) == 0 or int(reporting_status[0]['reporting_status']) == 2 :
                            etask_reporting_dates = ETaskReportingDates.objects.filter(task_type=1,task=instance.id,is_deleted=False)

                            # print('etask_reporting_dates-->',etask_reporting_dates)
                            if etask_reporting_dates:
                                for e_r in etask_reporting_dates:
                                    e_r.reporting_status=3
                                    e_r.actual_reporting_date = current_date
                                    e_r.updated_by = updated_by
                                    e_r.save()
                                    action_log=ETaskReportingActionLog.objects.create(task_id = instance.id,
                                                                        reporting_date_id=e_r.id,
                                                                        status = 3,
                                                                        updated_by = updated_by
                                                                        )
                                    # print('action_log-->',action_log)
                        else:
                            etask_reporting_dates = ETaskReportingDates.objects.filter(task_type=1,task=instance.id,is_deleted=False)

                            # print('etask_reporting_dates-->',etask_reporting_dates)
                            if etask_reporting_dates:
                                action_log=ETaskReportingActionLog.objects.create(task_id = instance.id,
                                                                    status = 4,
                                                                    updated_by = updated_by
                                                                    )
                                # print('action_log-->',action_log)
                    return instance
                else:
                    raise APIException("Child task is not completed."
                                )
        except Exception as e:
            raise e
            # raise APIException({'msg':e,
            #                     "request_status": 0
            #                     })

        

class EtaskMyTaskTodaysPlannerListSerializer(serializers.ModelSerializer):

    class Meta:
        model = EtaskTask
        fields = ('id','parent_id','task_subject','task_description','start_date','end_date','task_status','completed_date',
                    'closed_date','extended_date','assign_by','assign_to','sub_assign_to_user','get_task_status_display')

class EtaskEndDateExtensionRequestSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = EtaskTask
        fields = ('id','requested_end_date','requested_comment','updated_by','requested_by')
    def update(self, instance, validated_data):
        instance.requested_end_date = validated_data['requested_end_date']
        instance.requested_comment = validated_data['requested_comment']
        instance.requested_by=validated_data.get('updated_by')
        instance.updated_by = validated_data.get('updated_by')
        instance.save()
        return instance

class EtaskExtensionsListSerializer(serializers.ModelSerializer):
    parent_task=serializers.SerializerMethodField(required=False)
    sub_data = EtaskTask.objects.filter(parent_id=0,is_deleted=False)
    task_type_name=serializers.CharField(source='get_task_type_display')
    recurrance_frequency_name=serializers.CharField(source='get_recurrance_frequency_display')
    task_status_name=serializers.CharField(source='get_task_status_display')
    task_priority_name=serializers.CharField(source='get_task_priority_display')
    assign_by_name = serializers.SerializerMethodField()
    assign_to_name= serializers.SerializerMethodField()
    sub_assign_to_user_name= serializers.SerializerMethodField()
    reporting_dates = serializers.SerializerMethodField()
    class Meta:
        model= EtaskTask
        fields='__all__'

    def get_parent_task(self,EtaskTask):
        if EtaskTask.parent_id:
            if EtaskTask.parent_id !=0:
                if self.sub_data.filter(id=EtaskTask.parent_id).values('id','task_subject','task_description'):
                    parent_data=self.sub_data.filter(id=EtaskTask.parent_id).values('id','task_subject','task_description')[0]
                    return parent_data

    def user_name(self, user_id):
        name = None
        full_name = ""
        name = User.objects.get(id=user_id)
        if name:
            full_name =  name.__dict__['first_name']+" "+name.__dict__['last_name']
        return full_name

    def get_assign_by_name(self,EtaskTask):
        name = None
        full_name = ""
        if EtaskTask.assign_by:
            name = User.objects.get(id=EtaskTask.assign_by.id)
            if name:
                full_name =  name.__dict__['first_name']+" "+name.__dict__['last_name']
                # print("full_name",full_name)
            return full_name

    def get_sub_assign_to_user_name(self,EtaskTask):
        name=None
        full_name=""
        if EtaskTask.sub_assign_to_user:
            name=User.objects.get(id=EtaskTask.sub_assign_to_user.id)
            if name:
                full_name= name.__dict__['first_name']+" "+name.__dict__['last_name']
                return full_name

    def get_assign_to_name(self,EtaskTask):
        name=None
        full_name=""
        if EtaskTask.assign_to:
            name =User.objects.get(id=EtaskTask.assign_to.id)
            if name:
                full_name=name.__dict__['first_name']+" "+name.__dict__['last_name']
                return full_name
    def get_reporting_dates(self,EtaskTask):
        if EtaskTask.id:
            report_date_list = []
            report_date=ETaskReportingDates.objects.filter(task_type=1,task=EtaskTask.id,is_deleted=False)
            # print("report_date",report_date)
            if report_date:
                for dt in report_date:
                    dt_dict={
                        'id':dt.id,
                        'reporting_date':dt.reporting_date,
                        'reporting_status':dt.reporting_status,
                        'reporting_status_name':dt.get_reporting_status_display()
                       
                    }
                    report_date_list.append(dt_dict)
                                   
                return report_date_list
            else:
                return []

class EtaskExtensionsRejectSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model=EtaskTask
        fields=('id','is_reject','updated_by')
    def update(self,instance,validated_data):
        instance.is_reject=True
        instance.updated_by=validated_data.get('updated_by')
        instance.save()
        return instance

class EtaskTaskDateExtendedViewSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = EtaskTask
        fields = '__all__'
    def update(self, instance, validated_data):
        instance.extended_date = validated_data['extended_date']
        instance.updated_by = validated_data.get('updated_by')
        instance.save()
        return instance

class EtaskTaskDateExtendedWithDelaySerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = EtaskTask
        fields = '__all__'
    def update(self, instance, validated_data):
        instance.extend_with_delay = True
        instance.extended_date = validated_data['extended_date']
        instance.updated_by = validated_data.get('updated_by')
        instance.save()
        return instance

class EtaskTaskReopenAndExtendWithDelaySerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = EtaskTask
        fields = '__all__'
    def update(self, instance, validated_data):
        instance.extend_with_delay = True
        instance.extended_date = validated_data['extended_date']
        instance.completed_date=None
        instance.task_status=1
        instance.updated_by = validated_data.get('updated_by')
        instance.save()
        return instance

class EtaskTaskStartDateShiftSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    shift_date=serializers.DateTimeField(required=False)
    class Meta:
        model = EtaskTask
        fields = ('id','start_date','end_date','updated_by','shift_date','extended_date')
       
    def update(self, instance, validated_data):
        shift_date=validated_data.get('shift_date') 
        print('shift_date',shift_date)
        print('extended_date',instance.extended_date)
        if instance.extended_date:
            if shift_date.date()<=instance.extended_date.date():
                instance.start_date=shift_date
                instance.updated_by = validated_data.get('updated_by')
                instance.save()
                return instance
        elif shift_date.date()<=instance.end_date.date():
            instance.start_date=shift_date
            instance.updated_by = validated_data.get('updated_by')
            instance.save()
            return instance
        else:
            raise APIException({'msg':'Please Give Shift Date Before The Task End Date',
                        "request_status": 0
                        })



class EtaskAllTypeTaskCountViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = EtaskTask
        fields = '__all__'

class EtaskTaskCCListviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = EtaskUserCC
        fields = '__all__'

class EtaskTaskTransferredListviewSerializer(serializers.ModelSerializer):
    task_status_name=serializers.CharField(source='get_task_status_display')
    class Meta:
        model = EtaskTask
        fields = '__all__'

class ETaskCommentsSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    cost_details=serializers.ListField(required=False)
    other_details=serializers.ListField(required=False)
    
    class Meta:
        model=ETaskComments
        fields='__all__'
        extra_fields=('cost_details','other_details')

    def create(self,validated_data):
        try:
            loggedin_user=self.context['request'].user.id
            print('loggedin_user',loggedin_user)
            cost_details=validated_data.pop('cost_details')if 'cost_details' in validated_data else ""
            other_details=validated_data.pop('other_details')if 'other_details' in validated_data else "" 
            created_by=validated_data.get('created_by')
            owned_by=validated_data.get('owned_by')
            cost_details_list=[]
            other_details_list=[]
            comment_save_send = self.context['request'].query_params.get('comment_save_send',None)
            print('comment_save_send',comment_save_send)
            with transaction.atomic():
                e_task_comments=ETaskComments.objects.create(**validated_data)
                # print("e_task_comments-->",e_task_comments)
                users_list=EtaskTask.objects.filter(id=str(validated_data.get('task')),is_deleted=False).values('assign_by','assign_to')
                # print('assign_by',users_list[0]['assign_by'])
                user_cat_list=users_list.values('task_categories','sub_assign_to_user')
                # print('user_cat_list',user_cat_list,user_cat_list[0]['task_categories'])
                email_list=[]
                if user_cat_list[0]['task_categories'] == 1:
                    comment_view=ETaskCommentsViewers.objects.create(etcomments=e_task_comments,
                                                                user_id=users_list[0]['assign_by'],
                                                                task=validated_data.get('task'),                          
                                                                created_by=created_by,
                                                                owned_by=owned_by
                                                                )
                    # print('comment_view',comment_view)
                    if loggedin_user == users_list[0]['assign_by']:
                        viewer=ETaskCommentsViewers.objects.filter(etcomments=e_task_comments,user_id=users_list[0]['assign_by'],
                                                                    task=validated_data.get('task')).update(is_view=True)

                    assign_by_mail_id = TCoreUserDetail.objects.filter(cu_user_id=users_list[0]['assign_by'],cu_is_deleted=False).values('cu_alt_email_id')
                    email_list.append(assign_by_mail_id[0]['cu_alt_email_id'])
                    print('email_list1',email_list)
                    if comment_save_send == 'send':
                        mail_data = {
                                "name": userdetails(users_list[0]['assign_by']),
                                "comment_sub": validated_data.get('comments'),
                                "commented_by": userdetails(users_list[0]['assign_by'])
                                    }
                        # print('mail_data',mail_data)
                        mail_class = GlobleMailSend('ET-COMMENT', email_list)
                        mail_thread = Thread(target = mail_class.mailsend, args = (mail_data,))
                        mail_thread.start()
                else:
                    for user in users_list:
                        print('user',user)
                        for k,v in user.items():
                            print('v',v,type(v))
                            comment_view=ETaskCommentsViewers.objects.create(etcomments=e_task_comments,
                                                                user_id=v,
                                                                task=validated_data.get('task'),                                                         
                                                                created_by=created_by,
                                                                owned_by=owned_by
                                                                )
                            # print('comment_view',comment_view)
                            if loggedin_user == v:
                                viewer=ETaskCommentsViewers.objects.filter(etcomments=e_task_comments,user_id=v,
                                                                    task=validated_data.get('task')).update(is_view=True)
                            if loggedin_user != v:
                                mail_id = TCoreUserDetail.objects.filter(cu_user_id=v,cu_is_deleted=False).values('cu_alt_email_id')
                                email_list.append(mail_id[0]['cu_alt_email_id'])
                                print('email_list2',email_list)
                                if comment_save_send == 'send':
                                    mail_data = {
                                            "name": userdetails(v),
                                            "comment_sub": validated_data.get('comments'),
                                            "commented_by": userdetails(loggedin_user)
                                                }
                                    # print('mail_data',mail_data)
                                    mail_class = GlobleMailSend('ET-COMMENT', email_list)
                                    mail_thread = Thread(target = mail_class.mailsend, args = (mail_data,))
                                    mail_thread.start()
                sub_assign_email_list=[]
                if user_cat_list[0]['sub_assign_to_user']:
                    sub_comment_view=ETaskCommentsViewers.objects.create(etcomments=e_task_comments,
                                                                user_id=user_cat_list[0]['sub_assign_to_user'],
                                                                task=validated_data.get('task'),                          
                                                                created_by=created_by,
                                                                owned_by=owned_by
                                                                )
                    # print('sub_comment_view',sub_comment_view)
                    if loggedin_user == user_cat_list[0]['sub_assign_to_user']:
                        viewer=ETaskCommentsViewers.objects.filter(etcomments=e_task_comments,user_id=user_cat_list[0]['sub_assign_to_user'],
                                                                    task=validated_data.get('task')).update(is_view=True)

                    assign_by_mail_id = TCoreUserDetail.objects.filter(cu_user_id=users_list[0]['assign_by'],cu_is_deleted=False).values('cu_alt_email_id')
                    sub_assign_email_list.append(assign_by_mail_id[0]['cu_alt_email_id'])
                    print('sub_assign_email_list',sub_assign_email_list)
                    if comment_save_send == 'send':
                        mail_data = {
                                "name": userdetails(users_list[0]['assign_by']),
                                "comment_sub": validated_data.get('comments'),
                                "commented_by": userdetails(user_cat_list[0]['sub_assign_to_user'])
                                    }
                        # print('mail_data',mail_data)
                        mail_class = GlobleMailSend('ET-COMMENT', sub_assign_email_list)
                        mail_thread = Thread(target = mail_class.mailsend, args = (mail_data,))
                        mail_thread.start()            
                for c_d in cost_details:
                    cost_data=EtaskIncludeAdvanceCommentsCostDetails.objects.create(etcomments=e_task_comments,
                                                                                                  **c_d,
                                                                                                  created_by=created_by,
                                                                                                  owned_by=owned_by
                                                                                                    )
                    cost_data.__dict__.pop('_state') if "_state" in cost_data.__dict__.keys() else cost_data.__dict__
                    cost_details_list.append(cost_data.__dict__)
                # print('cost_details_list-->',cost_details_list)

                for o_d in other_details:
                    others_data=EtaskIncludeAdvanceCommentsOtherDetails.objects.create(etcomments=e_task_comments,
                                                                                                    **o_d,
                                                                                                    created_by=created_by,
                                                                                                    owned_by=owned_by
                                                                                                    )
                    others_data.__dict__.pop('_state')if '_state' in others_data.__dict__.keys() else others_data.__dict__
                    other_details_list.append(others_data.__dict__)
                # print('other_details_list-->',other_details_list)

                e_task_comments.__dict__['cost_details']=cost_details_list
                e_task_comments.__dict__['other_details']=other_details_list
                return e_task_comments
               
        except Exception as e:
            raise e

class ETaskCommentsViewersSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model=ETaskCommentsViewers
        fields='__all__'
    def create(self,validated_data):
        comment_id=self.context['request'].query_params.get('comment_id')
        print('task_id',comment_id,type(comment_id))
        user_id=self.context['request'].query_params.get('user_id')
        print('user_id',user_id)
        comment_viewers=ETaskCommentsViewers.objects.filter(etcomments=comment_id,user=user_id,is_deleted=False).update(is_view=True)
        print('comment_viewers',comment_viewers,type(comment_viewers))
        return comment_viewers

class ETaskUnreadCommentsSerializer(serializers.ModelSerializer):
    task_status_name=serializers.CharField(source='get_task_status_display')
    class Meta:
        model=EtaskTask
        fields='__all__'




class ETaskCommentsAdvanceAttachmentAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model=EtaskIncludeAdvanceCommentsDocuments
        fields='__all__'

class EtasCommentsListSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=ETaskComments
        fields='__all__'

#::::::::::::::::::::::::: TASK COMMENTS:::::::::::::::::::::::::::#
class ETaskFollowupCommentsSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    cost_details=serializers.ListField(required=False)
    other_details=serializers.ListField(required=False)
    
    class Meta:
        model=FollowupComments
        fields='__all__'
        extra_fields=('cost_details','other_details')

    def create(self,validated_data):
        try:
            cost_details=validated_data.pop('cost_details')if 'cost_details' in validated_data else ""
            other_details=validated_data.pop('other_details')if 'other_details' in validated_data else "" 
            created_by=validated_data.get('created_by')
            owned_by=validated_data.get('owned_by')
            cost_details_list=[]
            other_details_list=[]
            
            with transaction.atomic():
                followup_comments=FollowupComments.objects.create(**validated_data)

                # print("followup_comments-->",followup_comments)
                
                for c_d in cost_details:
                    cost_data=FollowupIncludeAdvanceCommentsCostDetails.objects.create(flcomments=followup_comments,
                                                                                                  **c_d,
                                                                                                  created_by=created_by,
                                                                                                  owned_by=owned_by
                                                                                                    )
                    cost_data.__dict__.pop('_state') if "_state" in cost_data.__dict__.keys() else cost_data.__dict__
                    cost_details_list.append(cost_data.__dict__)
                # print('cost_details_list-->',cost_details_list)

                for o_d in other_details:
                    others_data=FollowupIncludeAdvanceCommentsOtherDetails.objects.create(flcomments=followup_comments,
                                                                                                    **o_d,
                                                                                                    created_by=created_by,
                                                                                                    owned_by=owned_by
                                                                                                    )
                    others_data.__dict__.pop('_state')if '_state' in others_data.__dict__.keys() else others_data.__dict__
                    other_details_list.append(others_data.__dict__)
                # print('other_details_list-->',other_details_list)

                followup_comments.__dict__['cost_details']=cost_details_list
                followup_comments.__dict__['other_details']=other_details_list
                return followup_comments
               
        except Exception as e:
            raise e

class ETaskFollowupCommentsAdvanceAttachmentAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model=FollowupIncludeAdvanceCommentsDocuments
        fields='__all__'

class EtasCommentsListSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=ETaskComments
        fields='__all__'



class ETaskSubAssignSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    # sub_assign=serializers.ListField(required=False)
    class Meta:
        model=EtaskTask
        fields=('id','sub_assign_to_user','updated_by')
    def update(self, instance, validated_data):
        cur_date = datetime.now().date()
        try:
            # sub_assign=validated_data.pop('sub_assign') if 'sub_assign'in validated_data else ""
            
            updated_by=validated_data.get('updated_by')
            with transaction.atomic():
                #======================= log ====================================#
                if instance.sub_assign_to_user:
                    assign_from = instance.sub_assign_to_user
                else:
                    assign_from = instance.assign_to
                sub_assign_log = EtaskTaskSubAssignLog.objects.create(task_id=instance.id,assign_from=assign_from,
                                                                    sub_assign=validated_data['sub_assign_to_user'],
                                                                    created_by=updated_by,owned_by=updated_by)
                ###################################################################
                instance.sub_assign_to_user= validated_data['sub_assign_to_user']
                instance.updated_by=updated_by
                instance.save()
                ####################################################################
                reporting_date = ETaskReportingDates.objects.filter(task=instance.id,task_type=1,reporting_status=2,
                                        reporting_date__date__gt=cur_date).values('reporting_date')
                print("reporting_date",reporting_date)
                reporting_date_list = []
                # print("task_create",task_create.__dict__['id'])
                # print("r_date['reporting_date']",r_date['reporting_date'])
                reporting_date_str = """"""
                r_time = ''
                ics_data = """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN\n"""
                print("validated_data['sub_assign_to_user']",instance.sub_assign_to_user)
                user_name = userdetails(instance.sub_assign_to_user.id)
                count_id = 0
                for r_date in reporting_date:
                    print("r_date['reporting_date']",r_date['reporting_date'])
                    count_id += 1
                    reporting_date_str += str(count_id)+'. '+r_date['reporting_date'].strftime("%m/%d/%Y, %I:%M:%S %p")+" "
                    r_time = r_date['reporting_date'].strftime("%Y%m%dT%H%M%S")
                    ics_data +=   """BEGIN:VEVENT
SUMMARY:Reporting of {rep_sub}
DTSTART;TZID=Asia/Kolkata:{r_time}
LOCATION:Shyam Tower,Kolkata-700091
DESCRIPTION: Reporting dates.
STATUS:CONFIRMED
SEQUENCE:3
BEGIN:VALARM
TRIGGER:-PT10M
DESCRIPTION:Pickup Reminder
ACTION:DISPLAY
END:VALARM
END:VEVENT\n""".replace("{r_time}",r_time).replace("{rep_sub}",instance.task_subject)

                #DTEND;TZID=Asia/Kolkata:{r_time}
                ics_data += "END:VCALENDAR"
                print("reporting_date_str",reporting_date_str)
                user_email = User.objects.get(id= instance.sub_assign_to_user.id).email
                print("user_email",user_email)
                
                if user_email:
                    mail_data = {
                                "recipient_name" : user_name,        ## modified by manas Paul 21jan20
                                "task_subject": instance.task_subject,
                                "reporting_date": reporting_date_str,
                            }
                    # print('mail_data',mail_data)
                    # print('mail_id-->',mail)
                    # print('mail_id-->',[mail])
                    # mail_class = GlobleMailSend('ETAP', email_list)
                    mail_class = GlobleMailSend('ETRDC', [user_email])
                    print('mail_class',mail_class)
                    mail_thread = Thread(target = mail_class.mailsend, args = (mail_data,ics_data))
                    print('mail_thread-->',mail_thread)
                    mail_thread.start()

                ######################################  

                return instance     
        except Exception as e:
            raise e
        
class EtaskAddFollowUpSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    # reporting_dates = serializers.ListField(required=False)
    class Meta:
        model=EtaskFollowUP
        fields='__all__'
        # extra_fields = 'reporting_dates'

    def create(self,validated_data):
        try:
            created_by = validated_data.get('created_by')
            # print('created_by',created_by,type(created_by))
            owned_by = validated_data.get('owned_by')
           
            with transaction.atomic():
                # reporting_dates = validated_data.pop('reporting_dates') if 'reporting_dates' in validated_data else ''

                create_followup = EtaskFollowUP.objects.create(**validated_data)

                print('create_followup-->',create_followup.__dict__)
                
                # reporting_dates = validated_data['reporting_dates'] 
                # print('reporting_dates from user-->',reporting_dates)

                # report_date_list = []

                # for r_dates in reporting_dates:
                #     etask_report_date,create = ETaskReportingDates.objects.get_or_create(
                #         task_type = 2,
                #         task = str(create_followup),
                #         reporting_date = datetime.strptime(r_dates['r_dates'],"%Y-%m-%dT%H:%M:%S.%fZ"),
                #         created_by=created_by,
                #         owned_by=owned_by
                #     )
                #     report_date_list.append(etask_report_date.__dict__)
                #     etask_report_date.__dict__.pop('_state') if '_state' in etask_report_date.__dict__.keys() else etask_report_date.__dict__
                #     print('etask_report_date-->',etask_report_date.__dict__)
                # validated_data['reporting_dates'] = report_date_list
                return create_followup
        except Exception as e:
            raise e

class EtaskFollowUpListSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=EtaskFollowUP
        fields='__all__'
    

class EtaskFollowUpCompleteViewSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = EtaskFollowUP
        fields = '__all__'
    def update(self, instance, validated_data):
        instance.followup_status='completed'
        instance.completed_date = validated_data.get('completed_date')
        instance.updated_by = validated_data.get('updated_by')
        instance.save()
        return instance

class EtaskFollowUpDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = EtaskFollowUP
        fields = ('id','is_deleted','updated_by')

    def update(self, instance, validated_data):
        try:
            with transaction.atomic():
                # reporting_dates = ETaskReportingDates.objects.filter(
                #     task=instance.id,
                #     is_deleted=False)
                # for r_dates in reporting_dates:
                #     print('r_dates_PRE_Status',r_dates.is_deleted)
                #     r_dates.is_deleted = True
                #     r_dates.updated_by =  validated_data.get('updated_by')
                #     print('r_dates_status', r_dates.is_deleted)
                #     r_dates.save()
                instance.updated_by = validated_data.get('updated_by')
                instance.is_deleted = True
                instance.save()
                # instance.__dict__['reporting_dates'] = reporting_dates
            return instance
        except Exception as e:
            raise e

class EtaskFollowUpEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    # reporting_dates = serializers.ListField(required=False)

    class Meta:
        model = EtaskFollowUP
        fields = '__all__'
        # extra_fields = 'reporting_dates'

    def update(self,instance, validated_data):
        try:
            # reporting_dates = validated_data.pop('reporting_dates')if 'reporting_dates' in validated_data else ''
            updated_by = validated_data.get('updated_by')
            with transaction.atomic():

                instance.follow_up_task = validated_data['follow_up_task']
                instance.assign_for = validated_data['assign_for']
                instance.follow_up_date = validated_data['follow_up_date'] 
                # instance.end_date = validated_data['end_date']
                # instance.follow_up_time = validated_data['follow_up_time']
                instance.updated_by=updated_by
                instance.save()

                # existing_reporting_date=ETaskReportingDates.objects.filter(
                #         task_type=2,task=instance.id,is_deleted=False)
                # if existing_reporting_date:
                #     existing_reporting_date.delete()

                # r_dates_list = []
                # for r_date in reporting_dates:
                #     r_dates_details = ETaskReportingDates.objects.create(
                #             task_type=2,
                #             task=instance.id,
                #             reporting_date= datetime.strptime(r_date['r_dates'],"%Y-%m-%dT%H:%M:%S.%fZ"),
                #             created_by=updated_by,
                #             owned_by=updated_by)
                #     r_dates_details.__dict__.pop('_state') if '_state' in r_dates_details.__dict__.keys() else r_dates_details.__dict__
                #     r_dates_list.append(r_dates_details.__dict__)
               
                # instance.__dict__['reporting_dates'] = r_dates_list
                return instance.__dict__
                
        except Exception as e:
            raise e

class EtaskFollowUpRescheduleSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = EtaskFollowUP
        fields = ('id','follow_up_date','updated_by')  

class ETaskAssignToListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TCoreUserDetail
        fields = ('id','cu_user','reporting_head',) 

class ETaskAppointmentAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    internal_invite = serializers.ListField(required=False)
    external_invite = serializers.ListField(required=False)
    class Meta:
        model=EtaskAppointment
        fields='__all__'

    def create(self,validated_data):
        try:
            owned_by = validated_data.get('owned_by')
            created_by = validated_data.get('created_by')
            request = self.context.get('request')
            with transaction.atomic():
                email_list =[]
                internal_invite=validated_data.pop('internal_invite') if 'internal_invite' in validated_data else ""
                external_invite=validated_data.pop('external_invite') if 'external_invite' in validated_data else ""
                sd_date = validated_data.pop('start_date')
                ed_date = validated_data.pop('end_date')
                print('start_date',sd_date,'enddate',ed_date)
                start_date =datetime.strptime(datetime.strftime(sd_date,"%Y-%m-%dT%H:%M:%S"),"%Y-%m-%dT%H:%M:%S")
                end_date = datetime.strptime(datetime.strftime(ed_date,"%Y-%m-%dT%H:%M:%S"),"%Y-%m-%dT%H:%M:%S")
                print("start_date",start_date,type(start_date))
                print("validated_data",validated_data)
                apointment_create = EtaskAppointment.objects.create(Appointment_status='ongoing',start_date=start_date,
                                                                    end_date=end_date,**validated_data)

                internal_invite_list = [EtaskInviteEmployee.objects.create(appointment=apointment_create,**int_invite) 
                                        for int_invite in internal_invite]
                external_invite_list = [EtaskInviteExternalPeople.objects.create(appointment=apointment_create,**ext_invite) 
                                        for ext_invite in external_invite]

                user_dict = {
                    "user_full_name" : userdetails(validated_data['created_by'].id),
                    "email_id" : User.objects.get(id=validated_data['created_by'].id).email
                }
                email_list.append(user_dict)
                user_dict = {}

                for invites in internal_invite:
                    user_email = User.objects.get(id=invites['user_id']).email

                    ## modified by manas Paul 21jan20
                    user_dict = {
                        "user_full_name" : userdetails(invites['user_id']),
                        "email_id" : user_email
                    }
                    email_list.append(user_dict)
                    user_dict = {}

                for invites in external_invite:
                    ## modified by manas Paul 21jan20
                    user_dict = {
                        "user_full_name" :invites['external_people'],
                        "email_id" : invites['external_email']
                    }
                    email_list.append(user_dict)
                    user_dict = {}
                
                print("email_list",email_list)
             

                # ============= Mail Send Step ==============#
                # email = email_list
                # email_list = ['bubai.das@shyamfuture.com','rupam@shyamfuture.com','koushik.goswami@shyamfuture.com']
                # email_admin= 'abhishekrock94@shyamfuture.com'
                # print("email",email_list) 

                #==============================================#
                s_date = start_date.strftime("%Y%m%dT%H%M%S")
                e_date = start_date.strftime("%Y%m%dT%H%M%S")
                ics_data = """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
BEGIN:VEVENT
SUMMARY:Appointment of {app_sub}
DTSTART;TZID=Asia/Kolkata:{s_date}
DTEND;TZID=Asia/Kolkata:{e_date}
LOCATION:Shyam Tower,Kolkata-700091
DESCRIPTION: Appointment.
STATUS:CONFIRMED
SEQUENCE:3
BEGIN:VALARM
TRIGGER:-PT10M
DESCRIPTION:Pickup Reminder
ACTION:DISPLAY
END:VALARM
END:VEVENT
END:VCALENDAR""".replace("{s_date}",s_date).replace("{e_date}",e_date).replace("{app_sub}",validated_data.get('appointment_subject'))

                #===============================================#
                
                if email_list:
                    # for email in email_list:
                    for mail in email_list: ## modified by manas Paul 21jan20
                        mail_data = {
                                    "recipient_name" : mail['user_full_name'],        ## modified by manas Paul 21jan20
                                    "taskSubject": validated_data.get('appointment_subject'),
                                    "location":validated_data.get('location'),
                                    "start_date":start_date,
                                    "end_date":end_date,
                                    "start_time":validated_data.get('start_time'),
                                    "end_time":validated_data.get('end_time'),
                            }
                        # print('mail_data',mail_data)
                        # print('mail_id-->',mail)
                        # print('mail_id-->',[mail])
                        # mail_class = GlobleMailSend('ETAP', email_list)
                        mail_class = GlobleMailSend('ETAP', [mail['email_id']])
                        # print('mail_class',mail_class)
                        mail_thread = Thread(target = mail_class.mailsend, args = (mail_data,ics_data))
                        # print('mail_thread-->',mail_thread)
                        mail_thread.start()
                
                #===============================================#
           
                # print("internal_invite_list",internal_invite_list,'external_invite_list',external_invite_list)
                validated_data['id']= apointment_create.id
                validated_data['start_date']=start_date
                validated_data['end_date']=end_date
                validated_data['Appointment_status']='ongoing'
                validated_data['internal_invite']=internal_invite
                validated_data['external_invite']=external_invite

                return validated_data  

        except Exception as e:
            raise e 

class ETaskAppointmentUpdateSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    internal_invite = serializers.ListField(required=False)
    external_invite = serializers.ListField(required=False)
    class Meta:
        model=EtaskAppointment
        fields='__all__'
    
    def update(self, instance, validated_data):
        email_list = []
        internal_emails =[]
        external_emails = []
        appointment_subject = validated_data.pop('appointment_subject') if 'appointment_subject' in validated_data else ""
        location = validated_data.pop('location') if 'location' in validated_data else ""
        sd_date = validated_data.pop('start_date') if 'start_date' in validated_data else ""
        ed_date = validated_data.pop('end_date') if 'end_date' in validated_data else ""
        start_time= validated_data.pop('start_time') if 'start_time' in validated_data else ""
        end_time= validated_data.pop('end_time') if 'end_time' in validated_data else ""
        internal_invite = validated_data.pop('internal_invite') if 'internal_invite' in validated_data else ""
        external_invite = validated_data.pop('external_invite') if 'external_invite' in validated_data else ""
        start_date =datetime.strptime(datetime.strftime(sd_date,"%Y-%m-%dT%H:%M:%S"),"%Y-%m-%dT%H:%M:%S")
        end_date = datetime.strptime(datetime.strftime(ed_date,"%Y-%m-%dT%H:%M:%S"),"%Y-%m-%dT%H:%M:%S")
        for invites in internal_invite:
            user_email = User.objects.get(id=invites['user_id']).email
            internal_emails.append(user_email)
        for invites in external_invite:
            external_emails.append(invites['external_email'])

        #previous detials 
        previous_invites_email = EtaskInviteEmployee.objects.filter(appointment=instance.id).values_list('user__email',flat=True)
        previous_external_emails = EtaskInviteExternalPeople.objects.filter(appointment=instance.id).values_list('external_email',flat=True)
        print("previous_email_list",list(previous_invites_email),list(previous_external_emails))
        print("new_email_list",internal_emails,external_emails)
        deleted_internal_invites = list(set(previous_invites_email)-set(internal_emails))
        added_internal_invites = list(set(internal_emails)-set(previous_invites_email))
        external_deleted_internal_invites = list(set(previous_external_emails)-set(external_emails))
        external_added_internal_invites = list(set(external_emails)-set(previous_external_emails))
        print("deleted_internal_invites",deleted_internal_invites,external_deleted_internal_invites)
        print("added_internal_invites",added_internal_invites,external_added_internal_invites)
        all_remaining_invites = list(set(internal_emails+external_emails)-set(added_internal_invites+external_added_internal_invites))
        print("all_new_invites",all_remaining_invites)
        
        if instance.location != location or instance.start_date != start_date \
            or instance.end_date != end_date or instance.start_time != start_time or instance.end_time != end_time:
            EtaskAppointment.objects.filter(id=instance.id).update(location=location,start_date=start_date,
                        end_date=end_date,start_time=start_time,end_time=end_time)
            # ============= Mail Send Step ==============#
            # email = email_list
            # email_list = ['bubai.das@shyamfuture.com','rupam@shyamfuture.com','koushik.goswami@shyamfuture.com']
            # email_admin= 'abhishekrock94@shyamfuture.com'
            print("email",email_list) 
            
            if all_remaining_invites:
                # for email in email_list:
                mail_data = {
                            "appointmentsubject":appointment_subject,
                            "location":location,
                            "start_date":start_date,
                            "end_date":end_date,
                            "start_time":start_time,
                            "end_time":end_time,

                    }
                print('mail_data',mail_data)
                mail_class = GlobleMailSend('ETAP-SU', all_remaining_invites)
                print('mail_class',mail_class)
                mail_thread = Thread(target = mail_class.mailsend, args = (mail_data,None))
                mail_thread.start()
                
                #===============================================#
        
        if deleted_internal_invites or external_deleted_internal_invites:
            EtaskInviteEmployee.objects.filter(appointment=instance.id,user__email__in=deleted_internal_invites).update(is_deleted=True)
            EtaskInviteExternalPeople.objects.filter(appointment=instance.id,external_email__in=external_deleted_internal_invites).update(is_deleted=True)

            email_list_deleted_appo = deleted_internal_invites + external_deleted_internal_invites
            if email_list_deleted_appo:
                # for email in email_list:
                mail_data = {
                            "appointmentsubject":appointment_subject,
                            "location":location,

                    }
                print('mail_data',mail_data)
                mail_class = GlobleMailSend('ETAP-CA', email_list_deleted_appo)
                print('mail_class',mail_class)
                mail_thread = Thread(target = mail_class.mailsend, args = (mail_data,None))
                mail_thread.start()
                
                #===============================================#
        if added_internal_invites or external_added_internal_invites:
            user_id = User.objects.filter(email__in=added_internal_invites).values_list('id',flat=True)
            for x in list(user_id):
                EtaskInviteEmployee.objects.create(appointment_id=instance.id,user_id=x)
            for x in external_added_internal_invites:
                name = [ n['external_people'] for n in external_invite if n['external_email'] == x ]
                EtaskInviteExternalPeople.objects.create(appointment_id=instance.id,external_email=x,external_people=name[0])
            
            email_list_added_appo = added_internal_invites + external_added_internal_invites
            # ============= Mail Send Step ==============#
            # email = email_list
            # email_list = ['bubai.das@shyamfuture.com','rupam@shyamfuture.com','koushik.goswami@shyamfuture.com']
            # email_admin= 'abhishekrock94@shyamfuture.com'
            print("email",email_list_added_appo) 
            
            if email_list_added_appo:
                # for email in email_list:
                mail_data = {
                        "taskSubject":appointment_subject,
                        "location":location,
                        "start_date":start_date,
                        "end_date":end_date,
                        "start_time":start_time,
                        "end_time":end_time,

                    }
                print('mail_data',mail_data)
                mail_class = GlobleMailSend('ETAP', email_list_added_appo)
                print('mail_class',mail_class)
                mail_thread = Thread(target = mail_class.mailsend, args = (mail_data,None))
                mail_thread.start()
            
                #===============================================#
            validated_data['appointment_subject']=appointment_subject
            validated_data['location']=location
            validated_data['start_date']=start_date
            validated_data['end_date']=end_date
            validated_data['start_time']=start_time
            validated_data['end_time']=end_time
            validated_data['internal_invite']=internal_invite
            validated_data['external_invite']=external_invite
        return validated_data





class ETaskAppointmentCalanderSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    internal_invite = serializers.ListField(required=False)
    external_invite = serializers.ListField(required=False)
    class Meta:
        model=EtaskAppointment
        fields='__all__'

#::::::::::::::::::::::::: TASK COMMENTS:::::::::::::::::::::::::::#
class ETaskAppointmentCommentsSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    cost_details=serializers.ListField(required=False)
    other_details=serializers.ListField(required=False)
    
    class Meta:
        model=AppointmentComments
        fields='__all__'
        extra_fields=('cost_details','other_details')

    def create(self,validated_data):
        try:
            cost_details=validated_data.pop('cost_details')if 'cost_details' in validated_data else ""
            other_details=validated_data.pop('other_details')if 'other_details' in validated_data else "" 
            created_by=validated_data.get('created_by')
            owned_by=validated_data.get('owned_by')
            cost_details_list=[]
            other_details_list=[]
            
            with transaction.atomic():
                appointment_comments=AppointmentComments.objects.create(**validated_data)

                # print("appointment_comments-->",appointment_comments)
                
                for c_d in cost_details:
                    cost_data=AppointmentIncludeAdvanceCommentsCostDetails.objects.create(apcomments=appointment_comments,
                                                                                                  **c_d,
                                                                                                  created_by=created_by,
                                                                                                  owned_by=owned_by
                                                                                                    )
                    cost_data.__dict__.pop('_state') if "_state" in cost_data.__dict__.keys() else cost_data.__dict__
                    cost_details_list.append(cost_data.__dict__)
                # print('cost_details_list-->',cost_details_list)

                for o_d in other_details:
                    others_data=AppointmentIncludeAdvanceCommentsOtherDetails.objects.create(apcomments=appointment_comments,
                                                                                                    **o_d,
                                                                                                    created_by=created_by,
                                                                                                    owned_by=owned_by
                                                                                                    )
                    others_data.__dict__.pop('_state')if '_state' in others_data.__dict__.keys() else others_data.__dict__
                    other_details_list.append(others_data.__dict__)
                # print('other_details_list-->',other_details_list)

                appointment_comments.__dict__['cost_details']=cost_details_list
                appointment_comments.__dict__['other_details']=other_details_list
                return appointment_comments
               
        except Exception as e:
            raise e

class ETaskAppointmentCommentsAdvanceAttachmentAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model=AppointmentIncludeAdvanceCommentsDocuments
        fields='__all__'

class EtasCommentsListSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=AppointmentComments
        fields='__all__'



class ETaskReportsSerializer(serializers.ModelSerializer):
    assign_by_name = serializers.SerializerMethodField()
    sub_data = EtaskTask.objects.filter(parent_id=0,is_deleted=False)
    parent_task=serializers.SerializerMethodField(required=False)
    reporting_dates=serializers.SerializerMethodField()
    class Meta:
        model=EtaskTask
        fields=('id','task_code_id','parent_id','task_subject','task_description','start_date','end_date','task_status','completed_date',
                    'extended_date','assign_by','assign_by_name','assign_to','sub_assign_to_user',
                    'reporting_dates','parent_task')
    def user_name(self, user_id):
        name = None
        full_name = ""
        name = User.objects.get(id=user_id)
        if name:
            full_name =  name.__dict__['first_name']+" "+name.__dict__['last_name']
        return full_name

    def get_assign_by_name(self,EtaskTask):
        name = None
        full_name = ""
        if EtaskTask.assign_by:
            name = User.objects.get(id=EtaskTask.assign_by.id)
            if name:
                full_name =  name.__dict__['first_name']+" "+name.__dict__['last_name']
                # print("full_name",full_name)
            return full_name
    def get_reporting_dates(self,EtaskTask):
        if EtaskTask.id:
            report_date_list = []
            report_date=ETaskReportingDates.objects.filter(task_type=1,task=EtaskTask.id,is_deleted=False)
            # print("report_date",report_date)
            current_date=datetime.now().date()
            if report_date:
                for dt in report_date:
                    pre_report= dt.reporting_date.date()
                    # print('pre_report',pre_report)
                    if dt.reporting_status==2:
                        days_count=(current_date-pre_report).days
                        print('days_count',days_count)
                    else:
                        days_count = 0
                    dt_dict={
                        'id':dt.id,
                        'reporting_date':dt.reporting_date,
                        'reporting_status':dt.reporting_status,
                        'reporting_status_name':dt.get_reporting_status_display(),
                        'crossed_by':days_count
                    }
                    report_date_list.append(dt_dict)
                
                    
                return report_date_list
            else:
                return []
   
    def get_parent_task(self,EtaskTask):
        if EtaskTask.parent_id:
            # id_data = EtaskTask.get('parent_id')
            # print("id_data",id_data)
            # print('sad',EtaskTask.parent_id)
            if  EtaskTask.parent_id !=0:
                if self.sub_data.filter(id=EtaskTask.parent_id).values('id','task_subject'):
                    parent_data=self.sub_data.filter(id=EtaskTask.parent_id).values('id','task_subject')[0]
                    # print('parent_data',parent_data)
                    return parent_data
        

class EtaskUpcommingReportingListSerializer(serializers.ModelSerializer):

    class Meta:
        model = EtaskTask
        fields = '__all__'

class EtaskReportingDateReportedSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    completed_status = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = ETaskReportingDates
        fields = '__all__'
    def update(self, instance, validated_data):
        current_date = datetime.now()
        # print('current_date-->',current_date)
        updated_by = validated_data.get('updated_by')
        instance.task_type = 1
        instance.task_status=1
        instance.reporting_status = 1
        instance.actual_reporting_date = current_date
        instance.updated_by = updated_by
        instance.save()
        prev_action= ETaskReportingActionLog.objects.filter(
            task_id = instance.task,
            reporting_date_id = instance.id,
            is_deleted=False
            ).update(is_deleted=True)
        reporting_log = ETaskReportingActionLog.objects.create(
            task_id = instance.task,
            reporting_date_id = instance.id,
            status = 1,
            updated_by = updated_by
            )
        # print('reporting_log-->',reporting_log)
        return instance

############################################################################
class EtaskReportingDateShiftViewSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    shift_dates = serializers.ListField(required=False)
    class Meta:
        model = ETaskReportingDates
        fields = ('id','updated_by','shift_dates')
        # extra_fields = ('shift_date',)
    # def update(self,instance,validated_data):
    #     try:
    #         with transaction.atomic():
    #             print('validated_data',validated_data.get('updated_by'))
    #             current_date=datetime.now().date()
    #             if instance.reporting_date.date()>current_date:
    #                 instance.reporting_date=validated_data.get('reporting_date')
    #                 instance.updated_by=validated_data.get('updated_by')
    #                 instance.save()
    #                 ETaskReportingActionLog.objects.filter(reporting_date=instance,is_deleted=False).update(updated_by_id=validated_data.get('updated_by'),is_deleted=True)
    #                 ETaskReportingActionLog.objects.create(reporting_date=instance,
    #                                                         status=2,
    #                                                         task_id=instance.task,
    #                                                         updated_date=datetime.now(),
    #                                                         updated_by=validated_data.get('updated_by')
    #                                                         )
    #             return instance.__dict__
    #     except Exception as e:
    #         raise e
    def create(self,validated_data):
        try:
            # print('validated_data',validated_data)
            task_id=self.context['request'].query_params.get('task_id', None)
            # print('task_id',task_id)
            shift_dates = validated_data.get('shift_dates')if 'shift_dates' in validated_data else ""
            updated_by = validated_data.get('updated_by')
            with transaction.atomic():
                # reporting_dates_details = ETaskReportingDates.objects.filter(task_type=1,task=task_id,is_deleted=False)
                # reporting_action_log=ETaskReportingActionLog.objects.filter(task_id=task_id,is_deleted=False)
                # if reporting_dates_details and reporting_action_log:
                #     reporting_dates_details.delete()
                #     reporting_action_log.delete()
                current_date=datetime.now().date()
                for r_dates in shift_dates:
                    reporting_date_create = ETaskReportingDates.objects.filter(id=r_dates['id'],
                                                                               task=task_id,
                                                                               task_type=1,
                                                                               is_deleted=False
                                                                                ).values('reporting_date','reporting_status','updated_by')
                                                                               
                    # print('reporting_date_create',type(reporting_date_create[0]['reporting_status']))
                    if reporting_date_create[0]['reporting_date'].date() >= current_date and reporting_date_create[0]['reporting_status'] == 2:
                        reporting_date_create = ETaskReportingDates.objects.filter(id=r_dates['id'],
                                                                               task=task_id,
                                                                               task_type=1,
                                                                               is_deleted=False
                                                                                ).update(reporting_date=datetime.strptime(r_dates['reporting_date'], "%Y-%m-%dT%H:%M:%S.%fZ"),
                                                                                      updated_by=updated_by
                                                                                  ) 
                                                                                                                                                                                     
                        reporting_action_log=ETaskReportingActionLog.objects.filter(task_id=task_id,
                                                                                    reporting_date_id=r_dates['id'],
                                                                                    is_deleted=False
                                                                                    ).update(is_deleted=True, updated_by=updated_by)
                        reporting_action_log=ETaskReportingActionLog.objects.create(task_id=task_id,
                                                                                reporting_date_id=r_dates['id'],
                                                                                updated_date=datetime.now().date(),
                                                                                status=2,
                                                                                updated_by=updated_by
                                                                                )
                return validated_data
        except Exception as e:
            raise e
############################################################################
        
class ETaskAdminTaskReportSerializer(serializers.ModelSerializer):
    parent_task=serializers.SerializerMethodField(required=False)
    sub_data = EtaskTask.objects.filter(parent_id=0,is_deleted=False)
    task_type_name=serializers.CharField(source='get_task_type_display')
    recurrance_frequency_name=serializers.CharField(source='get_recurrance_frequency_display')
    task_status_name=serializers.CharField(source='get_task_status_display')
    assign_by_name = serializers.SerializerMethodField()
    assign_to_name= serializers.SerializerMethodField()
    sub_assign_to_user_name= serializers.SerializerMethodField()
    class Meta:
        model=EtaskTask
        fields='__all__'
    def get_parent_task(self,EtaskTask):
        if EtaskTask.parent_id:
            if EtaskTask.parent_id !=0:
                if self.sub_data.filter(id=EtaskTask.parent_id).values('id','task_subject'):
                    parent_data=self.sub_data.filter(id=EtaskTask.parent_id).values('id','task_subject')[0]
                    return parent_data
    def user_name(self, user_id):
        name = None
        full_name = ""
        name = User.objects.get(id=user_id)
        if name:
            full_name =  name.__dict__['first_name']+" "+name.__dict__['last_name']
        return full_name
    def get_assign_by_name(self,EtaskTask):
        name = None
        full_name = ""
        if EtaskTask.assign_by:
            name = User.objects.get(id=EtaskTask.assign_by.id)
            if name:
                full_name =  name.__dict__['first_name']+" "+name.__dict__['last_name']
                # print("full_name",full_name)
            return full_name
    def get_sub_assign_to_user_name(self,EtaskTask):
        name=None
        full_name=""
        if EtaskTask.sub_assign_to_user:
            name=User.objects.get(id=EtaskTask.sub_assign_to_user.id)
            if name:
                full_name= name.__dict__['first_name']+" "+name.__dict__['last_name']
                return full_name

    def get_assign_to_name(self,EtaskTask):
        name=None
        full_name=""
        if EtaskTask.assign_to:
            name =User.objects.get(id=EtaskTask.assign_to.id)
            if name:
                full_name=name.__dict__['first_name']+" "+name.__dict__['last_name']
                return full_name

class ETaskAdminAppointmentReportSerializer(serializers.ModelSerializer):
    appointment_status_name=serializers.CharField(source='get_Appointment_status_display')
    class Meta:
        model=EtaskAppointment
        fields='__all__'

                
class ETaskAllCommentsSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    cost_details=serializers.ListField(required=False)
    other_details=serializers.ListField(required=False)
    id_tfa=serializers.IntegerField(required=False)
    
    class Meta:
        model=None
        fields='__all__'
        extra_fields=('cost_details','other_details')

    def create(self,validated_data):
        comment_section = self.context['request'].query_params.get('comment_section',None)
        print(comment_section)
        if comment_section.lower() =='task':
            task = validated_data.pop('id_tfa')if 'id_tfa' in validated_data else ""
            cost_details=validated_data.pop('cost_details')if 'cost_details' in validated_data else ""
            other_details=validated_data.pop('other_details')if 'other_details' in validated_data else "" 
            created_by=validated_data.get('created_by')
            
            owned_by=validated_data.get('owned_by')
            cost_details_list=[]
            other_details_list=[]
            
            with transaction.atomic():
                print("task",task)
                e_task_comments=ETaskComments.objects.create(task_id=task,**validated_data)

                print("e_task_comments-->",e_task_comments)
                
                for c_d in cost_details:
                    cost_data=EtaskIncludeAdvanceCommentsCostDetails.objects.create(etcomments=e_task_comments,
                                                                                                **c_d,
                                                                                                created_by=created_by,
                                                                                                owned_by=owned_by
                                                                                                    )
                    cost_data.__dict__.pop('_state') if "_state" in cost_data.__dict__.keys() else cost_data.__dict__
                    cost_details_list.append(cost_data.__dict__)
                print('cost_details_list-->',cost_details_list)

                for o_d in other_details:
                    others_data=EtaskIncludeAdvanceCommentsOtherDetails.objects.create(etcomments=e_task_comments,
                                                                                                    **o_d,
                                                                                                    created_by=created_by,
                                                                                                    owned_by=owned_by
                                                                                                    )
                    others_data.__dict__.pop('_state')if '_state' in others_data.__dict__.keys() else others_data.__dict__
                    other_details_list.append(others_data.__dict__)
                print('other_details_list-->',other_details_list)

                e_task_comments.__dict__['cost_details']=cost_details_list
                e_task_comments.__dict__['other_details']=other_details_list

                # ============= Mail Send ============== #
                comment_save_send = self.context['request'].query_params.get('comment_save_send',None)
                # comments_detail = ETaskComments.objects.filter(task_id=task)
                # print('comments_detail-->',comments_detail)
                assign_to_email = TCoreUserDetail.objects.filter(cu_user=EtaskTask.objects.only('assign_to').get(id=task).assign_to)
                print('assign_to_email-->',assign_to_email)
                # email_list = []                

                if assign_to_email and comment_save_send == 'send':

                    print('Email Send Process Started')

                    task_owner_email = list(set(TCoreUserDetail.objects.filter(cu_alt_email_id__isnull=False,cu_user=EtaskTask.objects.only('owner').get(id=task).assign_to
                                                                        ).values_list('cu_alt_email_id',flat=True)))
                    print('task_owner_email-->',task_owner_email)
                    # task_owner_email = ['nuralam.islam@shyamfuture.com']      
                    task_cc_id_list =  list(set(EtaskUserCC.objects.filter(task=task,is_deleted=False).values_list('user',flat=True)))
                    print('task_cc_id_list-->',task_cc_id_list)
                    
                    task_cc_list = []
                    for u_list in task_cc_id_list:
                        user_id = TCoreUserDetail.objects.filter(cu_alt_email_id__isnull=False,cu_user=u_list,cu_is_deleted=False).values('cu_alt_email_id')
                        # print('user_id-->',user_id[0]['cu_alt_email_id'])
                        task_cc_list.append(user_id[0]['cu_alt_email_id'])

                    print('task_cc_list-->',task_cc_list)

                    commented_by = userdetails(created_by.id)
                    comment_subject = validated_data['comments']
                    
                    email = list(set(assign_to_email.values_list('cu_alt_email_id',flat=True)))
                    print('email-->',email)
                    email_list = task_owner_email + email + task_cc_list
                    print('task_owner_email-->',email_list)
                    # full_name = EtaskTask.objects.only('assign_to_id').get(id=task).assign_to_id
                    full_name = userdetails(EtaskTask.objects.only('assign_to_id').get(id=task).assign_to_id)
                    print('full_name-->',full_name)

                    ###### Main mail Send Block ######

                    if email_list:
                        mail_data = {
                                    "name": full_name,
                                    "comment_sub": comment_subject,
                                    "commented_by": commented_by
                            }
                        print('mail_data',mail_data)
                        mail_class = GlobleMailSend('ET-COMMENT', email_list)
                        mail_thread = Thread(target = mail_class.mailsend, args = (mail_data,))
                        mail_thread.start()

                    #################################

                return e_task_comments

        elif comment_section.lower() =='followup':
            print("validated_data",validated_data)
            followup = validated_data.pop('id_tfa') if 'id_tfa' in validated_data else ""
            cost_details=validated_data.pop('cost_details')if 'cost_details' in validated_data else ""
            other_details=validated_data.pop('other_details')if 'other_details' in validated_data else "" 
            
            print("followup",followup)
            created_by=validated_data.get('created_by')
            owned_by=validated_data.get('owned_by')
            cost_details_list=[]
            other_details_list=[]
            
            with transaction.atomic():
                print("entered")
                followup_comments=FollowupComments.objects.create(followup_id=followup,**validated_data)

                # print("followup_comments-->",followup_comments)
                
                for c_d in cost_details:
                    cost_data=FollowupIncludeAdvanceCommentsCostDetails.objects.create(flcomments=followup_comments,
                                                                                                **c_d,
                                                                                                created_by=created_by,
                                                                                                owned_by=owned_by
                                                                                                    )
                    cost_data.__dict__.pop('_state') if "_state" in cost_data.__dict__.keys() else cost_data.__dict__
                    cost_details_list.append(cost_data.__dict__)
                # print('cost_details_list-->',cost_details_list)

                for o_d in other_details:
                    others_data=FollowupIncludeAdvanceCommentsOtherDetails.objects.create(flcomments=followup_comments,
                                                                                                    **o_d,
                                                                                                    created_by=created_by,
                                                                                                    owned_by=owned_by
                                                                                                    )
                    others_data.__dict__.pop('_state')if '_state' in others_data.__dict__.keys() else others_data.__dict__
                    other_details_list.append(others_data.__dict__)
                # print('other_details_list-->',other_details_list)

                followup_comments.__dict__['cost_details']=cost_details_list
                followup_comments.__dict__['other_details']=other_details_list
                return followup_comments
        
        elif comment_section.lower() =='appointment':
            try:
                print("val",validated_data)
                appointment = validated_data.pop('id_tfa') if 'id_tfa' in validated_data else ""
                cost_details=validated_data.pop('cost_details')if 'cost_details' in validated_data else ""
                other_details=validated_data.pop('other_details')if 'other_details' in validated_data else "" 
                created_by=validated_data.get('created_by')
                owned_by=validated_data.get('owned_by')
                cost_details_list=[]
                other_details_list=[]
                
                with transaction.atomic():
                    
                    appointment_comments=AppointmentComments.objects.create(appointment_id=appointment,**validated_data)

                    print("appointment_comments-->",appointment_comments.__dict__)
                    appointment_subject=EtaskAppointment.objects.only('appointment_subject').get(id=appointment,is_deleted=False).appointment_subject
                    
                    for c_d in cost_details:
                        cost_data=AppointmentIncludeAdvanceCommentsCostDetails.objects.create(apcomments=appointment_comments,
                                                                                                    **c_d,
                                                                                                    created_by=created_by,
                                                                                                    owned_by=owned_by
                                                                                                        )
                        cost_data.__dict__.pop('_state') if "_state" in cost_data.__dict__.keys() else cost_data.__dict__
                        cost_details_list.append(cost_data.__dict__)
                    # print('cost_details_list-->',cost_details_list)

                    for o_d in other_details:
                        others_data=AppointmentIncludeAdvanceCommentsOtherDetails.objects.create(apcomments=appointment_comments,
                                                                                                        **o_d,
                                                                                                        created_by=created_by,
                                                                                                        owned_by=owned_by
                                                                                                        )
                        others_data.__dict__.pop('_state')if '_state' in others_data.__dict__.keys() else others_data.__dict__
                        other_details_list.append(others_data.__dict__)
                    # print('other_details_list-->',other_details_list)

                    appointment_comments.__dict__['cost_details']=cost_details_list
                    appointment_comments.__dict__['other_details']=other_details_list

                    # ============= Mail Send ============== # 
                    comment_save_send = self.context['request'].query_params.get('comment_save_send',None)
                    if comment_save_send == 'send':

                        internal_invites = EtaskInviteEmployee.objects.filter((Q(user__email__isnull=False) & ~Q(user__email="")),
                                                    appointment_id=appointment).values_list('user__email',flat=True)
                        print('internal_invites',internal_invites)
                        external_invites = EtaskInviteExternalPeople.objects.filter((Q(external_email__isnull=False) & ~Q(external_email=""))
                                                                ,appointment_id=appointment).values_list('external_email',flat=True)
                        print('external_invites',external_invites)
                        total_emailid = list(set(list(internal_invites)+list(external_invites)))

                        if total_emailid:
                            mail_data = {
                                    "appointment_subject":appointment_subject,
                                    "appointment_comment":appointment_comments.__dict__['comments']
                                   
                            }
                            # if appointment_comments.__dict__['advance_comment'] == True:
                            #     mail_data["cost_details"]=cost_data.__dict__['cost_details']
                            #     mail_data["cost"]=cost_data.__dict__['cost']
                            #     mail_data["other_details"]=others_data.__dict__['other_details']
                            #     mail_data["value"]=others_data.__dict__['value']

                            print('mail_data',mail_data)
                            mail_class = GlobleMailSend('ET-APPONTMANET-COMMENT', total_emailid)
                            mail_thread = Thread(target = mail_class.mailsend, args = (mail_data,))
                            mail_thread.start()

                    return appointment_comments
                
            except Exception as e:
                raise e
       

class ETaskAllCommentsDocumentSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())    
    class Meta:
        model=None
        fields='__all__'

class ETaskAppointmentCancelSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = EtaskAppointment
        fields = '__all__'
    def update(self, instance, validated_data):
        cancelling_user = self.context['request'].user.first_name + " " +  self.context['request'].user.last_name
        internal_invites = EtaskInviteEmployee.objects.filter((Q(user__email__isnull=False) & ~Q(user__email="")),
                                                    appointment=instance.id).values_list('user__email',flat=True)
        external_invites = EtaskInviteExternalPeople.objects.filter((Q(external_email__isnull=False) & ~Q(external_email=""))
                                                ,appointment=instance.id).values_list('external_email',flat=True)
        total_cancle_emailid = list(set(list(internal_invites)+list(external_invites)))
        
        #update section 
        # EtaskInviteEmployee.objects.filter(appointment=instance.id).update(is_deleted=True)
        # EtaskInviteExternalPeople.objects.filter(appointment=instance.id).update(is_deleted=True)
        instance.Appointment_status = 'cancelled'
        # instance.is_deleted = True
        instance.save()




        # etask_appointment_creator = EtaskAppointment.objects.filter(id=instance.id,Appointment_status='ongoing',is_deleted=False)

        # print('etask_appointment_creator-->',etask_appointment_creator)

        # if etask_appointment_creator :            

        #     print('Email Send Process Started')

                        
        #     appintment_owner_email = list(set(TCoreUserDetail.objects.filter(cu_user__in=etask_appointment_creator.values_list('created_by',flat=True)
        #                                                                     ).values_list('cu_alt_email_id',flat=True)))
            
        #     # list(set(TCoreUserDetail.objects.filter(cu_alt_email_id__isnull=False,
        #     #                                         cu_user__in=TCoreUserDetail.objects.filter(cu_user=EtaskTask.objects.only('assign_by').get(id=task).assign_to
        #     #                                                     ).values_list('reporting_head',flat=True)).values_list('cu_alt_email_id',flat=True)))
        #     print('appintment_owner_email-->',appintment_owner_email)
        #     # task_owner_email = ['nuralam.islam@shyamfuture.com']    

        #     # etask_invite_employee_list = EtaskInviteEmployee.objects.filter(appointment=instance,is_deleted=False)
        #     # print('etask_invite_employee_list-->',etask_invite_employee_list)  
        #     invited_employee_list =  list(set(EtaskInviteEmployee.objects.filter(appointment=instance,is_deleted=False).values_list('user',flat=True)))
        #     print('invited_employee_list-->',invited_employee_list)
        #     task_cc_list = []
        #     if invited_employee_list:
        #         for u_list in invited_employee_list:
        #             user_id = TCoreUserDetail.objects.filter(cu_user=u_list,cu_is_deleted=False).values('cu_alt_email_id')
        #             # print('user_id-->',user_id[0]['cu_alt_email_id'])
        #             task_cc_list.append(user_id[0]['cu_alt_email_id'])

        #         print('task_cc_list-->',task_cc_list)
            
        #     etask_invite_external_people = EtaskInviteExternalPeople.objects.filter(appointment=instance,is_deleted=False)
        #     etask_invite_external_people_list = []
        #     if etask_invite_external_people:
        #         etask_invite_external_people_list = list(set(etask_invite_external_people.values_list('external_email',flat=True)))

        #     # cancelled_by = userdetails(created_by.id)
        #     # comment_subject = validated_data['comments']

        #     email_list = task_owner_email + task_cc_list + etask_invite_external_people_list
        #     print('task_owner_email-->',email_list)
        #     # full_name = EtaskTask.objects.only('assign_to_id').get(id=task).assign_to_id
        #     # full_name = userdetails(EtaskTask.objects.only('assign_to_id').get(id=task).assign_to_id)
        #     # print('full_name-->',full_name)

        #     ###### Main mail Send Block ######

        if total_cancle_emailid:
            mail_data = {
                        "appointment_subject":instance.appointment_subject,
                        "cancelled_by": cancelling_user
                }
            print('mail_data',mail_data)
            mail_class = GlobleMailSend('ET-APPONTMANET-CANCEL', total_cancle_emailid)
            mail_thread = Thread(target = mail_class.mailsend, args = (mail_data,))
            mail_thread.start()

        #################################


        return instance


class ETaskTeamOngoingTaskSerializer(serializers.ModelSerializer):
    parent_task=serializers.SerializerMethodField(required=False)
    sub_data = EtaskTask.objects.filter(parent_id=0,is_deleted=False)
    assign_to_name= serializers.SerializerMethodField()
    sub_assign_to_user_name= serializers.SerializerMethodField()
    class Meta:
        model=EtaskTask
        # fields='__all__' ## Modified By Manas Paul and below fields also.
        fields = ('id','parent_id','task_subject','task_description','start_date','end_date','task_status','completed_date','task_priority','extend_with_delay',
                    'task_code_id','closed_date','extended_date','assign_by','assign_to','sub_assign_to_user','get_task_status_display',
                    'sub_assign_to_user_name','parent_task','assign_to_name','sub_assign_to_user_name')
    def get_parent_task(self,EtaskTask):
        if EtaskTask.parent_id:
            if EtaskTask.parent_id !=0:
                if self.sub_data.filter(id=EtaskTask.parent_id).values('id','task_subject'):
                    parent_data=self.sub_data.filter(id=EtaskTask.parent_id).values('id','task_subject')[0]
                    return parent_data
    def user_name(self, user_id):
        name = None
        full_name = ""
        name = User.objects.get(id=user_id)
        if name:
            full_name =  name.__dict__['first_name']+" "+name.__dict__['last_name']
        return full_name
    def get_assign_to_name(self,EtaskTask):
        name=None
        full_name=""
        if EtaskTask.assign_to:
            name =User.objects.get(id=EtaskTask.assign_to.id)
            if name:
                full_name=name.__dict__['first_name']+" "+name.__dict__['last_name']
                return full_name
    def get_sub_assign_to_user_name(self,EtaskTask):
        name=None
        full_name=""
        if EtaskTask.sub_assign_to_user:
            name=User.objects.get(id=EtaskTask.sub_assign_to_user.id)
            if name:
                full_name= name.__dict__['first_name']+" "+name.__dict__['last_name']
                return full_name
class ETaskTeamCompletedTaskSerializer(serializers.ModelSerializer):
    parent_task=serializers.SerializerMethodField(required=False)
    sub_data = EtaskTask.objects.filter(parent_id=0,is_deleted=False)
    assign_to_name= serializers.SerializerMethodField()
    sub_assign_to_user_name= serializers.SerializerMethodField()
    class Meta:
        model=EtaskTask
        fields='__all__'
    def get_parent_task(self,EtaskTask):
        if EtaskTask.parent_id:
            if EtaskTask.parent_id !=0:
                if self.sub_data.filter(id=EtaskTask.parent_id).values('id','task_subject'):
                    parent_data=self.sub_data.filter(id=EtaskTask.parent_id).values('id','task_subject')[0]
                    return parent_data
    def user_name(self, user_id):
        name = None
        full_name = ""
        name = User.objects.get(id=user_id)
        if name:
            full_name =  name.__dict__['first_name']+" "+name.__dict__['last_name']
        return full_name
    def get_assign_to_name(self,EtaskTask):
        name=None
        full_name=""
        if EtaskTask.assign_to:
            name =User.objects.get(id=EtaskTask.assign_to.id)
            if name:
                full_name=name.__dict__['first_name']+" "+name.__dict__['last_name']
                return full_name
    def get_sub_assign_to_user_name(self,EtaskTask):
        name=None
        full_name=""
        if EtaskTask.sub_assign_to_user:
            name=User.objects.get(id=EtaskTask.sub_assign_to_user.id)
            if name:
                full_name= name.__dict__['first_name']+" "+name.__dict__['last_name']
                return full_name
class ETaskTeamClosedTaskSerializer(serializers.ModelSerializer):
    parent_task=serializers.SerializerMethodField(required=False)
    sub_data = EtaskTask.objects.filter(parent_id=0,is_deleted=False)
    assign_to_name= serializers.SerializerMethodField()
    sub_assign_to_user_name= serializers.SerializerMethodField()
    reporting_dates=serializers.SerializerMethodField()
    task_priority_name=serializers.CharField(source='get_task_priority_display')
    class Meta:
        model=EtaskTask
        fields='__all__'
    def get_parent_task(self,EtaskTask):
        if EtaskTask.parent_id:
            if EtaskTask.parent_id !=0:
                if self.sub_data.filter(id=EtaskTask.parent_id).values('id','task_subject','task_description'):
                    parent_data=self.sub_data.filter(id=EtaskTask.parent_id).values('id','task_subject','task_description')[0]
                    return parent_data
    def user_name(self, user_id):
        name = None
        full_name = ""
        name = User.objects.get(id=user_id)
        if name:
            full_name =  name.__dict__['first_name']+" "+name.__dict__['last_name']
        return full_name
    def get_assign_to_name(self,EtaskTask):
        name=None
        full_name=""
        if EtaskTask.assign_to:
            name =User.objects.get(id=EtaskTask.assign_to.id)
            if name:
                full_name=name.__dict__['first_name']+" "+name.__dict__['last_name']
                return full_name
    def get_sub_assign_to_user_name(self,EtaskTask):
        name=None
        full_name=""
        if EtaskTask.sub_assign_to_user:
            name=User.objects.get(id=EtaskTask.sub_assign_to_user.id)
            if name:
                full_name= name.__dict__['first_name']+" "+name.__dict__['last_name']
                return full_name
    def get_reporting_dates(self,EtaskTask):
        if EtaskTask.id:
            report_date_list = []
            report_date=ETaskReportingDates.objects.filter(task_type=1,task=EtaskTask.id,is_deleted=False)
            # print("report_date",report_date)
            if report_date:
                for dt in report_date:
                    dt_dict={
                        'id':dt.id,
                        'reporting_date':dt.reporting_date,
                        'reporting_status':dt.reporting_status,
                        'reporting_status_name':dt.get_reporting_status_display()
                       
                    }
                    report_date_list.append(dt_dict)
                                   
                return report_date_list
            else:
                return []
class ETaskTeamOverdueTaskSerializer(serializers.ModelSerializer):
    parent_task=serializers.SerializerMethodField(required=False)
    sub_data = EtaskTask.objects.filter(parent_id=0,is_deleted=False)
    assign_to_name= serializers.SerializerMethodField()
    sub_assign_to_user_name= serializers.SerializerMethodField()
    class Meta:
        model=EtaskTask
        fields='__all__'
    def get_parent_task(self,EtaskTask):
        if EtaskTask.parent_id:
            if EtaskTask.parent_id !=0:
                if self.sub_data.filter(id=EtaskTask.parent_id).values('id','task_subject'):
                    parent_data=self.sub_data.filter(id=EtaskTask.parent_id).values('id','task_subject')[0]
                    return parent_data
    def user_name(self, user_id):
        name = None
        full_name = ""
        name = User.objects.get(id=user_id)
        if name:
            full_name =  name.__dict__['first_name']+" "+name.__dict__['last_name']
        return full_name
    def get_assign_to_name(self,EtaskTask):
        name=None
        full_name=""
        if EtaskTask.assign_to:
            name =User.objects.get(id=EtaskTask.assign_to.id)
            if name:
                full_name=name.__dict__['first_name']+" "+name.__dict__['last_name']
                return full_name
    def get_sub_assign_to_user_name(self,EtaskTask):
        name=None
        full_name=""
        if EtaskTask.sub_assign_to_user:
            name=User.objects.get(id=EtaskTask.sub_assign_to_user.id)
            if name:
                full_name= name.__dict__['first_name']+" "+name.__dict__['last_name']
                return full_name

class ETaskGetDetailsCommentsSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    
    class Meta:
        model=None
        fields='__all__'
class EtaskTaskCloseSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = EtaskTask
        fields = '__all__'
    def update(self, instance, validated_data):
        current_date = datetime.now()
        updated_by = validated_data.get('updated_by')
        instance.task_status=4
        # instance.is_closure=True
        instance.closed_date = current_date
        instance.updated_by = updated_by
        instance.save()
        return instance

class ETaskMassTaskCloseSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    closed_task=serializers.ListField(required=False)
    class Meta:
        model = EtaskTask
        fields = ('id','updated_by','closed_task')
    def create(self,validated_data):
        try:
            updated_by = validated_data.get('updated_by')
            # print('closed_task', validated_data.get('closed_task'))
            for data in validated_data.get('closed_task'):
                cur_date =datetime.now()
                all_closed_task = EtaskTask.objects.filter(id=data['id'],is_deleted=False).update(task_status=4,
                                                                        updated_by=updated_by,closed_date=cur_date)
                
            return validated_data
        except Exception as e:
            raise e

class EmployeeListWithoutDetailsForETaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields=('id','first_name','last_name')

class EtaskTodayAppointmentListSerializer(serializers.ModelSerializer):
    appointment = serializers.CharField(required=False)
    class Meta:
        model=EtaskInviteEmployee
        fields='__all__'
        

class UpcomingTaskPerUserSerializer(serializers.ModelSerializer):
    parent_task=serializers.SerializerMethodField(required=False)
    sub_data = EtaskTask.objects.filter(parent_id=0,is_deleted=False)
    task_type_name=serializers.CharField(source='get_task_type_display')
    recurrance_frequency_name=serializers.CharField(source='get_recurrance_frequency_display')
    task_status_name=serializers.CharField(source='get_task_status_display')
    assign_by_name = serializers.SerializerMethodField()
    assign_to_name= serializers.SerializerMethodField()
    sub_assign_to_user_name= serializers.SerializerMethodField()
    reporting_date=serializers.SerializerMethodField()
    class Meta:
        model = EtaskTask
        fields = ('__all__')

    def get_parent_task(self,EtaskTask):
        if EtaskTask.parent_id:
            if EtaskTask.parent_id !=0:
                if self.sub_data.filter(id=EtaskTask.parent_id).values('id','task_subject'):
                    parent_data=self.sub_data.filter(id=EtaskTask.parent_id).values('id','task_subject')[0]
                    return parent_data

    def user_name(self, user_id):
        name = None
        full_name = ""
        name = User.objects.get(id=user_id)
        if name:
            full_name =  name.__dict__['first_name']+" "+name.__dict__['last_name']
        return full_name

    def get_assign_by_name(self,EtaskTask):
        name = None
        full_name = ""
        if EtaskTask.assign_by:
            name = User.objects.get(id=EtaskTask.assign_by.id)
            if name:
                full_name =  name.__dict__['first_name']+" "+name.__dict__['last_name']
                # print("full_name",full_name)
            return full_name

    def get_sub_assign_to_user_name(self,EtaskTask):
        name=None
        full_name=""
        if EtaskTask.sub_assign_to_user:
            name=User.objects.get(id=EtaskTask.sub_assign_to_user.id)
            if name:
                full_name= name.__dict__['first_name']+" "+name.__dict__['last_name']
                return full_name

    def get_assign_to_name(self,EtaskTask):
        name=None
        full_name=""
        if EtaskTask.assign_to:
            name =User.objects.get(id=EtaskTask.assign_to.id)
            if name:
                full_name=name.__dict__['first_name']+" "+name.__dict__['last_name']
                return full_name

    def get_reporting_date(self,EtaskTask):
        if EtaskTask.id:
            report_date_list = []
            report_date=ETaskReportingDates.objects.filter(task_type=1,task=EtaskTask.id,is_deleted=False)
            # print("report_date",report_date)
            current_date=datetime.now().date()
            if report_date:
                for dt in report_date:
                    pre_report= dt.reporting_date.date()
                    # print('pre_report',pre_report)
                    if pre_report>current_date:                     
                        dt_dict={
                            'id':dt.id,
                            'reporting_date':dt.reporting_date,
                        }
                        report_date_list.append(dt_dict)                             
                return report_date_list
            else:
                return []

class UpcomingTaskReportingPerUserSerializer(serializers.ModelSerializer):
    parent_task=serializers.SerializerMethodField(required=False)
    sub_data = EtaskTask.objects.filter(parent_id=0,is_deleted=False)
    task_type_name=serializers.CharField(source='get_task_type_display')
    recurrance_frequency_name=serializers.CharField(source='get_recurrance_frequency_display')
    task_status_name=serializers.CharField(source='get_task_status_display')
    assign_by_name = serializers.SerializerMethodField()
    assign_to_name= serializers.SerializerMethodField()
    sub_assign_to_user_name= serializers.SerializerMethodField()
    reporting_date=serializers.SerializerMethodField()
    class Meta:
        model = EtaskTask
        fields = ('__all__')

    def get_parent_task(self,EtaskTask):
        if EtaskTask.parent_id:
            if EtaskTask.parent_id !=0:
                if self.sub_data.filter(id=EtaskTask.parent_id).values('id','task_subject'):
                    parent_data=self.sub_data.filter(id=EtaskTask.parent_id).values('id','task_subject')[0]
                    return parent_data

    def user_name(self, user_id):
        name = None
        full_name = ""
        name = User.objects.get(id=user_id)
        if name:
            full_name =  name.__dict__['first_name']+" "+name.__dict__['last_name']
        return full_name

    def get_assign_by_name(self,EtaskTask):
        name = None
        full_name = ""
        if EtaskTask.assign_by:
            name = User.objects.get(id=EtaskTask.assign_by.id)
            if name:
                full_name =  name.__dict__['first_name']+" "+name.__dict__['last_name']
                # print("full_name",full_name)
            return full_name

    def get_sub_assign_to_user_name(self,EtaskTask):
        name=None
        full_name=""
        if EtaskTask.sub_assign_to_user:
            name=User.objects.get(id=EtaskTask.sub_assign_to_user.id)
            if name:
                full_name= name.__dict__['first_name']+" "+name.__dict__['last_name']
                return full_name

    def get_assign_to_name(self,EtaskTask):
        name=None
        full_name=""
        if EtaskTask.assign_to:
            name =User.objects.get(id=EtaskTask.assign_to.id)
            if name:
                full_name=name.__dict__['first_name']+" "+name.__dict__['last_name']
                return full_name

    def get_reporting_date(self,EtaskTask):
        if EtaskTask.id:
            report_date_list = []
            report_date=ETaskReportingDates.objects.filter(task_type=1,task=EtaskTask.id,is_deleted=False)
            # print("report_date",report_date)
            current_date=datetime.now().date()
            if report_date:
                for dt in report_date:
                    pre_report= dt.reporting_date.date()
                    # print('pre_report',pre_report)
                    if pre_report>current_date:                     
                        dt_dict={
                            'id':dt.id,
                            'reporting_date':dt.reporting_date,
                        }
                        report_date_list.append(dt_dict)                             
                return report_date_list
            else:
                return []

#::::::::::::::::DEFAULT REPORTING DATES:::::::::::::::::::::::::::::::::::::#
class ETaskDefaultReportingDatesSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    monthly_data = serializers.ListField(required=False)
    class Meta:
        model = EtaskMonthlyReportingDate
        fields = ('id','employee','created_by','owned_by','monthly_data')
        #extra_fields = ('monthly_data',)  
    def create(self, validated_data):
        try:
            user=self.context['request'].user
            print('user',user,type(user))
            print('is_superuser',user.is_superuser)
            users_list=(list(TCoreUserDetail.objects.filter((Q(reporting_head=user)|Q(hod=user)),cu_is_deleted=False).values_list('cu_user',flat=True)))
            print('users_list',users_list)
            if user.is_superuser==False:
                if users_list:
                    with transaction.atomic():
                        monthly_data = validated_data.get('monthly_data') if 'monthly_data' in validated_data else []
                        print('monthly_data',monthly_data)                 
                        for data in monthly_data:
                            filter={}
                            search_filter={}
                            filter['employee_id']=data['employee']
                            search_filter['employee_id']=data['employee']
                            field_label_value = data['field_label_value'] if 'field_label_value' in data   else []
                            if field_label_value:
                                for f_l in field_label_value:
                                    filter['field_label']=f_l['field_label']
                                    filter['field_value']=f_l['field_value']
                                    search_filter['field_value']=f_l['field_value']
                                    print('count', EtaskMonthlyReportingDate.objects.filter(**search_filter,is_deleted=False).count())
                                    if EtaskMonthlyReportingDate.objects.filter(**search_filter,is_deleted=False).count()==0:
                                        monthly_reporting_dates=EtaskMonthlyReportingDate.objects.create(**filter,created_by=user,owned_by=user)
                        return validated_data
                else:
                    return []
            else:
                return []
        except Exception as e:
            raise e
class ETaskAnotherDefaultReportingDatesSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = EtaskMonthlyReportingDate
        fields = '__all__'
    def create(self,validated_data):
        try:
            employee_id=self.context['request'].query_params.get('employee',None)
            print('employee_id',employee_id)
            loggedin_user=self.context['request'].user
            field_label=validated_data.get('field_label') if 'field_label' in validated_data else ''
            field_value=validated_data.get('field_value') if 'field_value' in validated_data else ''
            another_date=EtaskMonthlyReportingDate.objects.create(employee_id=employee_id,
                                                                    field_label=field_label,
                                                                    field_value=field_value,
                                                                    created_by=loggedin_user,
                                                                    owned_by=loggedin_user
                                                                )
            
            another_date.__dict__.pop('_state') if '_state' in another_date.__dict__ else another_date.__dict__
            print('another_date',another_date.__dict__,type(another_date))
            return another_date

        except Exception as e:
            raise e
class ETaskDefaultReportingDatesUpdateSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = EtaskMonthlyReportingDate
        fields = '__all__'
    def update(self,instance,validated_data):
        field_label=validated_data.get('field_label') if 'field_label' in validated_data else ''
        field_value=validated_data.get('field_value') if 'field_value' in validated_data else ''
        instance.field_label=field_label
        instance.field_value=field_value
        instance.updated_by=validated_data.get('updated_by')
        instance.save()
        return instance

class ETaskDefaultReportingDatesDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = EtaskMonthlyReportingDate
        fields = '__all__'
    def update(self,instance,validated_data):
        instance.is_deleted=True
        instance.updated_by=validated_data.get('updated_by')
        instance.save()
        return instance


#:::::::::::::::::::::::::::::::::::::: TODAY LIST -NEW ::::::::::::::::::::::::::::::::::::::::::::#
class TodayTaskDetailsPerUserSerializer(serializers.ModelSerializer):
    parent_task=serializers.SerializerMethodField(required=False)
    sub_data = EtaskTask.objects.filter(parent_id=0,is_deleted=False)
    task_type_name=serializers.CharField(source='get_task_type_display')
    recurrance_frequency_name=serializers.CharField(source='get_recurrance_frequency_display')
    task_status_name=serializers.CharField(source='get_task_status_display')
    task_priority_name=serializers.CharField(source='get_task_priority_display')
    # assign_by_name = serializers.SerializerMethodField()
    assign_to_name= serializers.SerializerMethodField()
    # sub_assign_to_user_name= serializers.SerializerMethodField()
    reporting_dates=serializers.SerializerMethodField()
    class Meta:
        model = EtaskTask
        fields = ('__all__')

    def get_parent_task(self,EtaskTask):
        if EtaskTask.parent_id:
            if EtaskTask.parent_id !=0:
                if self.sub_data.filter(id=EtaskTask.parent_id).values('id','task_subject','task_description'):
                    parent_data=self.sub_data.filter(id=EtaskTask.parent_id).values('id','task_subject','task_description')[0]
                    return parent_data
    
    def get_assign_to_name(self,EtaskTask):
        name=None
        full_name=""
        if EtaskTask.assign_to:
            name =User.objects.get(id=EtaskTask.assign_to.id)
            if name:
                full_name=name.__dict__['first_name']+" "+name.__dict__['last_name']
                return full_name

    def get_reporting_dates(self,EtaskTask):
        if EtaskTask.id:
            report_date_list = []
            report_date=ETaskReportingDates.objects.filter(task_type=1,task=EtaskTask.id,is_deleted=False)
            # print("report_date",report_date)
            current_date=datetime.now().date()
            if report_date:
                for dt in report_date:
                    pre_report= dt.reporting_date.date()
                    # print('pre_report',pre_report)
                    # if pre_report>current_date:                     
                    dt_dict={
                        'id':dt.id,
                        'reporting_date':dt.reporting_date,
                        'reporting_status':dt.get_reporting_status_display()
                    }
                    report_date_list.append(dt_dict)                             
                return report_date_list
            else:
                return []


class UpcomingTaskDetailsPerUserSerializer(serializers.ModelSerializer):
    parent_task=serializers.SerializerMethodField(required=False)
    sub_data = EtaskTask.objects.filter(parent_id=0,is_deleted=False)
    task_type_name=serializers.CharField(source='get_task_type_display')
    task_priority_name=serializers.CharField(source='get_task_priority_display')
    recurrance_frequency_name=serializers.CharField(source='get_recurrance_frequency_display')
    task_status_name=serializers.CharField(source='get_task_status_display')
    # assign_by_name = serializers.SerializerMethodField()
    assign_to_name= serializers.SerializerMethodField()
    # sub_assign_to_user_name= serializers.SerializerMethodField()
    reporting_dates=serializers.SerializerMethodField()
    class Meta:
        model = EtaskTask
        fields = ('__all__')

    def get_parent_task(self,EtaskTask):
        if EtaskTask.parent_id:
            if EtaskTask.parent_id !=0:
                if self.sub_data.filter(id=EtaskTask.parent_id).values('id','task_subject','task_description'):
                    parent_data=self.sub_data.filter(id=EtaskTask.parent_id).values('id','task_subject','task_description')[0]
                    return parent_data

    def get_assign_to_name(self,EtaskTask):
        name=None
        full_name=""
        if EtaskTask.assign_to:
            name =User.objects.get(id=EtaskTask.assign_to.id)
            if name:
                full_name=name.__dict__['first_name']+" "+name.__dict__['last_name']
                return full_name

    def get_reporting_dates(self,EtaskTask):
        if EtaskTask.id:
            report_date_list = []
            report_date=ETaskReportingDates.objects.filter(task_type=1,task=EtaskTask.id,is_deleted=False)
            # print("report_date",report_date)
            current_date=datetime.now().date()
            if report_date:
                for dt in report_date:                   
                    dt_dict={
                        'id':dt.id,
                        'reporting_date':dt.reporting_date,
                        'reporting_status':dt.get_reporting_status_display()
                    }
                    report_date_list.append(dt_dict)                             
                return report_date_list
            else:
                return []

class OverdueTaskDetailsPerUserSerializer(serializers.ModelSerializer):
    parent_task=serializers.SerializerMethodField(required=False)
    sub_data = EtaskTask.objects.filter(parent_id=0,is_deleted=False)
    task_type_name=serializers.CharField(source='get_task_type_display')
    task_priority_name=serializers.CharField(source='get_task_priority_display')
    recurrance_frequency_name=serializers.CharField(source='get_recurrance_frequency_display')
    task_status_name=serializers.CharField(source='get_task_status_display')
    # assign_by_name = serializers.SerializerMethodField()
    assign_to_name= serializers.SerializerMethodField()
    # sub_assign_to_user_name= serializers.SerializerMethodField()
    reporting_dates=serializers.SerializerMethodField()
    class Meta:
        model = EtaskTask
        fields = ('__all__')

    def get_parent_task(self,EtaskTask):
        if EtaskTask.parent_id:
            if EtaskTask.parent_id !=0:
                if self.sub_data.filter(id=EtaskTask.parent_id).values('id','task_subject'):
                    parent_data=self.sub_data.filter(id=EtaskTask.parent_id).values('id','task_subject','task_description')[0]
                    return parent_data

    def get_assign_to_name(self,EtaskTask):
        name=None
        full_name=""
        if EtaskTask.assign_to:
            name =User.objects.get(id=EtaskTask.assign_to.id)
            if name:
                full_name=name.__dict__['first_name']+" "+name.__dict__['last_name']
                return full_name

    def get_reporting_dates(self,EtaskTask):
        if EtaskTask.id:
            report_date_list = []
            report_date=ETaskReportingDates.objects.filter(task_type=1,task=EtaskTask.id,is_deleted=False)
            # print("report_date",report_date)
            current_date=datetime.now().date()
            if report_date:
                for dt in report_date:                     
                    dt_dict={
                        'id':dt.id,
                        'reporting_date':dt.reporting_date,
                        'reporting_status':dt.get_reporting_status_display()
                    }
                    report_date_list.append(dt_dict)                             
                return report_date_list
            else:
                return []


class EtaskClosedTaskListSerializer(serializers.ModelSerializer):
    class Meta:
        model = EtaskTask
        fields = ('id','task_code_id','parent_id','task_subject','task_description','start_date','end_date','task_status','closed_date',
                    'extended_date','assign_by','assign_to','sub_assign_to_user','get_task_status_display') #,'assign_to_name','sub_task_list', 'sub_assign_to_name','assign_by_name')

class EtaskTodaysPlannerCountSerializer(serializers.ModelSerializer):
    class Meta:
        model = EtaskTask
        fields = '__all__'

#:::::::::::::::::::::::::::::::::::::: REPORTING ::::::::::::::::::::::::::::::::::::::::::::::::#
class TodayReportingDetailsPerUserSerializer(serializers.ModelSerializer):
    # reporting_dates=serializers.SerializerMethodField()
    class Meta:
        model=EtaskTask
        fields=('id','task_code_id','task_subject','assign_by','assign_to','sub_assign_to_user','owner')
    # def get_reporting_dates(self,EtaskTask):
    #     if EtaskTask.id:
    #         report_date=list(ETaskReportingDates.objects.filter(task_type=1,task=EtaskTask.id,is_deleted=False).values_list('reporting_date',flat=True))
    #         if report_date:
    #             return report_date[0]
    #         else:
    #             return None

class UpcomingReportingDetailsPerUserSerializer(serializers.ModelSerializer):
    reporting_dates=serializers.SerializerMethodField()
    class Meta:
        model=EtaskTask
        fields=('id','task_code_id','task_subject','assign_by','assign_to','sub_assign_to_user','reporting_dates','owner')
    def get_reporting_dates(self,EtaskTask):
        cur_date = datetime.now().date()
        if EtaskTask.id:
            report_date=list(ETaskReportingDates.objects.filter(reporting_date__date__gt=cur_date,task_type=1,task=EtaskTask.id,
                                                                is_deleted=False).values('reporting_date'))
            return report_date

class OverdueReportingDetailsPerUserSerializer(serializers.ModelSerializer):
    reporting_dates=serializers.SerializerMethodField()
    class Meta:
        model=EtaskTask
        fields=('id','task_code_id','task_subject','assign_by','assign_to','sub_assign_to_user','reporting_dates','owner')
    def get_reporting_dates(self,EtaskTask):
        cur_date = datetime.now().date()
        if EtaskTask.id:
            report_date=list(ETaskReportingDates.objects.filter(reporting_date__date__lt=cur_date,task_type=1,task=EtaskTask.id,
                                                                is_deleted=False).values('reporting_date'))
            return report_date

class TodayReportingMarkDateReportedSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    completed_status = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = ETaskReportingDates
        fields = '__all__'
    def update(self, instance, validated_data):
        current_date = datetime.now()
        # print('current_date-->',current_date)
        updated_by = validated_data.get('updated_by')
        instance.task_type = 1
        instance.task_status=1
        instance.reporting_status = 1
        instance.actual_reporting_date = current_date
        instance.updated_by = updated_by
        instance.save()
        prev_action= ETaskReportingActionLog.objects.filter(
            task_id = instance.task,
            reporting_date_id = instance.id,
            is_deleted=False
            ).update(is_deleted=True)
        reporting_log = ETaskReportingActionLog.objects.create(
            task_id = instance.task,
            reporting_date_id = instance.id,
            status = 1,
            updated_by = updated_by
            )
        # print('reporting_log-->',reporting_log)
        return instance
        

class TodayAppointmenDetailsPerUserSerializer(serializers.ModelSerializer):
    # appointment = serializers.CharField(required=False)
    class Meta:
        model=EtaskAppointment
        fields='__all__'


class TodayAppoinmentMarkCompletedSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = EtaskAppointment
        fields = '__all__'
    def update(self, instance, validated_data):
        # print('current_date-->',current_date)
        updated_by = validated_data.get('updated_by')
        instance.Appointment_status = 'completed'
        instance.updated_at = datetime.now()
        instance.updated_by = updated_by
        instance.save()

        return instance
#:::::::::::::::::::::::::::::::::::::: TASK TRANSFER ::::::::::::::::::::::::::::::::::::::::::::::::#
class ETaskMassTaskTransferSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    transferred_task=serializers.ListField(required=False)
    user=serializers.CharField(required=False)
    tranferred_from=serializers.CharField(required=False)
    class Meta:
        model = EtaskTask
        fields = ('id','updated_by','transferred_task','user','tranferred_from')
    def create(self,validated_data):
        try:
            cur_date=datetime.now()
            updated_by = validated_data.get('updated_by')
            transferred_task=validated_data.get('transferred_task')
            print('transferred_task', transferred_task)
            user=validated_data.get('user')
            tranferred_from=validated_data.get('tranferred_from')
            print('user',user,type(user))
            if transferred_task:
                for data in validated_data.get('transferred_task'):
                    #======================= log ====================================#
                    transferred_task_log = EtaskTaskTransferLog.objects.create(task_id=data['id'],transferred_from_id=tranferred_from,
                                                                                transferred_to_id=user,transfer_date=cur_date,
                                                                                created_by=updated_by,owned_by=updated_by)

                    #################################################################
                    all_transferred_task = EtaskTask.objects.filter(id=data['id'],is_deleted=False).update(assign_to=user,date_of_transfer=cur_date,
                                          is_transferred=True,sub_assign_to_user=None,transferred_from=tranferred_from,updated_by=updated_by)
                    print("all_transferred_task",type(all_transferred_task),all_transferred_task)
                    ####################################################################
                    task_details = EtaskTask.objects.get(id=data['id'],is_deleted=False)
                    reporting_date = ETaskReportingDates.objects.filter(task=task_details.id,task_type=1,reporting_status=2,
                                            reporting_date__date__gt=cur_date).values('reporting_date')
                    print("reporting_date",reporting_date)
                    reporting_date_list = []
                    # print("task_create",task_create.__dict__['id'])
                    # print("r_date['reporting_date']",r_date['reporting_date'])
                    reporting_date_str = """"""
                    r_time = ''
                    ics_data = """BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN\n"""
                    print("validated_data['sub_assign_to_user']",task_details.assign_to)
                    user_name = userdetails(task_details.assign_to.id)
                    count_id = 0
                    for r_date in reporting_date:
                        print("r_date['reporting_date']",r_date['reporting_date'])
                        count_id += 1
                        reporting_date_str += str(count_id)+'. '+r_date['reporting_date'].strftime("%m/%d/%Y, %I:%M:%S %p")+" "
                        r_time = r_date['reporting_date'].strftime("%Y%m%dT%H%M%S")
                        ics_data +=   """BEGIN:VEVENT
SUMMARY:Reporting of {rep_sub}
DTSTART;TZID=Asia/Kolkata:{r_time}
LOCATION:Shyam Tower,Kolkata-700091
DESCRIPTION: Reporting dates.
STATUS:CONFIRMED
SEQUENCE:3
BEGIN:VALARM
TRIGGER:-PT10M
DESCRIPTION:Pickup Reminder
ACTION:DISPLAY
END:VALARM
END:VEVENT\n""".replace("{r_time}",r_time).replace("{rep_sub}",task_details.task_subject)

                    #DTEND;TZID=Asia/Kolkata:{r_time}
                    ics_data += "END:VCALENDAR"
                    print("reporting_date_str",reporting_date_str)
                    user_email = User.objects.get(id= task_details.assign_to.id).email
                    print("user_email",user_email)
                    
                    if user_email:
                        mail_data = {
                                    "recipient_name" : user_name,        ## modified by manas Paul 21jan20
                                    "task_subject": task_details.task_subject,
                                    "reporting_date": reporting_date_str,
                                }
                        # print('mail_data',mail_data)
                        # print('mail_id-->',mail)
                        # print('mail_id-->',[mail])
                        # mail_class = GlobleMailSend('ETAP', email_list)
                        mail_class = GlobleMailSend('ETRDC', [user_email])
                        print('mail_class',mail_class)
                        mail_thread = Thread(target = mail_class.mailsend, args = (mail_data,ics_data))
                        print('mail_thread-->',mail_thread)
                        mail_thread.start()

                    ######################################  

            return validated_data
        except Exception as e:
            raise e

class ETaskTeamTransferTasksListSerializer(serializers.ModelSerializer):
    parent_task=serializers.SerializerMethodField(required=False)
    sub_data = EtaskTask.objects.filter(parent_id=0,is_deleted=False)
    task_type_name=serializers.CharField(source='get_task_type_display')
    recurrance_frequency_name=serializers.CharField(source='get_recurrance_frequency_display')
    task_status_name=serializers.CharField(source='get_task_status_display')
    task_priority_name=serializers.CharField(source='get_task_priority_display')
    assign_by_name = serializers.SerializerMethodField()
    assign_to_name= serializers.SerializerMethodField()
    sub_assign_to_user_name= serializers.SerializerMethodField()
    reporting_dates=serializers.SerializerMethodField()
    class Meta:
        model = EtaskTask
        fields = ('__all__')

    def get_parent_task(self,EtaskTask):
        if EtaskTask.parent_id:
            if EtaskTask.parent_id !=0:
                if self.sub_data.filter(id=EtaskTask.parent_id).values('id','task_subject','task_description'):
                    parent_data=self.sub_data.filter(id=EtaskTask.parent_id).values('id','task_subject','task_description')[0]
                    return parent_data

    def user_name(self, user_id):
        name = None
        full_name = ""
        name = User.objects.get(id=user_id)
        if name:
            full_name =  name.__dict__['first_name']+" "+name.__dict__['last_name']
        return full_name

    def get_assign_by_name(self,EtaskTask):
        name = None
        full_name = ""
        if EtaskTask.assign_by:
            name = User.objects.get(id=EtaskTask.assign_by.id)
            if name:
                full_name =  name.__dict__['first_name']+" "+name.__dict__['last_name']
                # print("full_name",full_name)
            return full_name

    def get_sub_assign_to_user_name(self,EtaskTask):
        name=None
        full_name=""
        if EtaskTask.sub_assign_to_user:
            name=User.objects.get(id=EtaskTask.sub_assign_to_user.id)
            if name:
                full_name= name.__dict__['first_name']+" "+name.__dict__['last_name']
                return full_name

    def get_assign_to_name(self,EtaskTask):
        name=None
        full_name=""
        if EtaskTask.assign_to:
            name =User.objects.get(id=EtaskTask.assign_to.id)
            if name:
                full_name=name.__dict__['first_name']+" "+name.__dict__['last_name']
                return full_name

    def get_reporting_dates(self,EtaskTask):
        if EtaskTask.id:
            report_date_list = []
            report_date=ETaskReportingDates.objects.filter(task_type=1,task=EtaskTask.id,is_deleted=False)
            # print("report_date",report_date)
            if report_date:
                for dt in report_date:
                    dt_dict={
                        'id':dt.id,
                        'reporting_date':dt.reporting_date,
                    }
                    report_date_list.append(dt_dict)                             
                return report_date_list
            else:
                return []
