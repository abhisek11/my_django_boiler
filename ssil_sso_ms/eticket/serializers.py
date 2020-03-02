from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from core.models import *
from django.contrib.auth.models import *
from rest_framework.exceptions import APIException
from django.conf import settings
from eticket.models import *
from django.db.models import When, Case, Value, CharField, IntegerField, F, Q
from users.models import *
from drf_extra_fields.fields import Base64ImageField # for image base 64
from django.db import transaction, IntegrityError
from master.models import TMasterModuleOther,TMasterOtherRole,TMasterOtherUser,TMasterModuleRoleUser
from django.db.models.functions import Concat
from django.db.models import Value
from mailsend.views import *
from threading import Thread  # for threading
import datetime

class EticketReportingHeadAddSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    department_details = serializers.SerializerMethodField()
    # sub_department_name = serializers.SerializerMethodField()
    reporting_head_name = serializers.SerializerMethodField()

    def get_department_details(self,ETICKETReportingHead):
        data={}
        dept = TCoreDepartment.objects.filter(~Q(cd_parent_id=0),pk=ETICKETReportingHead.department.id)
        # print('dept',dept.query)
        # print('deptcheck',dept)
        if dept:
            dept = TCoreDepartment.objects.get(~Q(cd_parent_id=0),pk=ETICKETReportingHead.department.id)
            data = {
            'id':dept.cd_parent_id,
            'name': TCoreDepartment.objects.only('cd_name').get(pk=dept.cd_parent_id).cd_name,
            'child':{
                'id': dept.id,
                'name':dept.cd_name
                }
            } 
        else:
            data = {
            'id':ETICKETReportingHead.department.id,
            'name': TCoreDepartment.objects.only('cd_name').get(pk=ETICKETReportingHead.department.id).cd_name,
            'child':None
            }

        return data
        
    def get_reporting_head_name(self,ETICKETReportingHead):
        print('ETICKETReportingHead.reporting_head',ETICKETReportingHead.reporting_head)
        return User.objects.only('username').get(pk=ETICKETReportingHead.reporting_head.id).username
    
    # def get_sub_department_name(self,ETICKETReportingHead):
    #     return TCoreDepartment.objects.only('cd_name').get(pk=ETICKETReportingHead.sub_department.id).cd_name
    
    class Meta:
        model = ETICKETReportingHead
        fields = ('id','department','department_details','reporting_head','reporting_head_name',
        'is_deleted','created_by')

class EticketReportingHeadEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = ETICKETReportingHead
        fields = ('id','department','reporting_head','is_deleted','updated_by')

class EticketTicketSubjectListByDepartmentAddSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    created_at = serializers.CharField(required=False)
    class Meta:
        model = ETICKETSubjectOfDepartment
        fields = ('__all__')

    def create(self, validated_data):
        subject_against_depatyment = ETICKETSubjectOfDepartment.objects.create(**validated_data)
        return validated_data

class EticketTicketAddSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    status = serializers.CharField(default="Open")
    created_at = serializers.CharField(required=False)
    class Meta:
        model = ETICKETTicket
        fields = ('id','ticket_number','subject','department','priority','details','status',
        'is_deleted','created_by','created_at','assigned_to')

    def create(self, validated_data):
        print('sdddsd')
        department = validated_data.get('department')
        reporting_head_details = ETICKETReportingHead.objects.get(department=department)
        print('reporting_head_details',reporting_head_details)
        validated_data['ticket_number'] = "SSILT" + str(int(time.time()))
        validated_data['assigned_to'] = reporting_head_details.reporting_head
        response_create = ETICKETTicket.objects.create(**validated_data)
        print('request',response_create)
        mail_id = reporting_head_details.reporting_head.email
        # ============= Mail Send ==============#
        if mail_id:
            mail_data = {
                        "name": reporting_head_details.reporting_head.first_name+ ' ' +reporting_head_details.reporting_head.last_name,
                        "ticket_no": response_create.ticket_number,
                        "ticket_sub":response_create.subject.subject,
                        "priority":response_create.priority,
                        'details': response_create.details
                    }
            mail_class = GlobleMailSend('E-T-DEPT', [mail_id])
            mail_thread = Thread(target = mail_class.mailsend, args = (mail_data,))
            mail_thread.start()
        return response_create
        #return super().create(validated_data)

class EticketTicketDocumentAddSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = ETICKETTicketDoc
        fields = ('id','ticket','document','created_by')

class EticketTicketRaisedByMeListSerializer(serializers.ModelSerializer):
    subject = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    person_responsible = serializers.SerializerMethodField()
    assigned_to_department = serializers.SerializerMethodField()
    document_details = serializers.SerializerMethodField()
    comment_details = serializers.SerializerMethodField()

    def get_subject(self,ETICKETTicket):
        return ETICKETTicket.subject.subject

    def get_comment_count(self,ETICKETTicket):
        if ETICKETTicketComment.objects.filter(ticket = ETICKETTicket.id):
            return ETICKETTicketComment.objects.filter(ticket = ETICKETTicket.id).count()
        else:
            return 0
        
    def get_person_responsible(self,ETICKETTicket):
        print('ETICKETTicket.assigned_to',ETICKETTicket.assigned_to)
        if ETICKETTicket.assigned_to:
            return ETICKETTicket.assigned_to.first_name +' '+ETICKETTicket.assigned_to.last_name
        else:
            return None

    def get_assigned_to_department(self,ETICKETTicket):
        if ETICKETTicket.department:
            return ETICKETTicket.department.cd_name
        else:
            return None

    def get_document_details(self, ETICKETTicket):
        document = ETICKETTicketDoc.objects.filter(ticket=ETICKETTicket)
        request = self.context.get('request')
        response_list = []
        for each_document in document:
            file_url = request.build_absolute_uri(each_document.document.url)
            each_data = {
                "id": int(each_document.id),
                "document": file_url,
            }
            #print('each_data',each_data)
            response_list.append(each_data)
        return response_list
    
    def get_comment_details(self, ETICKETTicket):
        comment = ETICKETTicketComment.objects.annotate(
            name=Concat('created_by__first_name',Value(' '),'created_by__last_name')).filter(
                ticket=ETICKETTicket).values('id','ticket','comment',
        'name','created_at')
        return comment

    

    class Meta:
        model = ETICKETTicket
        fields = ('id','ticket_number','subject','department','assigned_to','assigned_to_department',
        'person_responsible','priority','details','status','is_deleted','created_by','created_at',
        'ticket_closed_date','comment_count','document_details','comment_details')

class EticketTicketChangeStatusSerializer(serializers.ModelSerializer):
    #ticket_closed_date = serializers.HiddenField(default=datetime.datetime.now)
    updated_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = ETICKETTicket
        fields = ('id','status','ticket_closed_date','updated_by')

    def update(self, instance, validated_data):
        print('sdddsdd',validated_data)
        if validated_data.get('status').lower() == 'closed':
            print('dgdfg')
            instance.status = validated_data.get('status')
            instance.ticket_closed_date = datetime.datetime.now()
        else:
            instance.status = validated_data.get('status')
        instance.save()

        return instance

class EticketTicketAssignedToMeListSerializer(serializers.ModelSerializer):
    department_users = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    assigned_to_department = serializers.SerializerMethodField()
    raised_by_name = serializers.SerializerMethodField()
    document_details = serializers.SerializerMethodField()
    comment_details = serializers.SerializerMethodField()
    person_responsible = serializers.SerializerMethodField()
    subject = serializers.SerializerMethodField()

    def get_subject(self,ETICKETTicket):
        return ETICKETTicket.subject.subject

    def get_department_users(self,ETICKETTicket):
        dept = TCoreDepartment.objects.filter(~Q(cd_parent_id=0),pk=ETICKETTicket.department.id)
        if dept:
            dept = TCoreDepartment.objects.get(~Q(cd_parent_id=0),pk=ETICKETTicket.department.id)
            # print("dept",dept)
            result = TCoreUserDetail.objects.annotate(
                name=Concat('cu_user__first_name',Value(' '),'cu_user__last_name')).filter(department=dept.cd_parent_id).values('cu_user','name')
            # print("result parent",result)
            return result
        else:
            # print("ETICKETTicket.department",ETICKETTicket.department)
            result = TCoreUserDetail.objects.annotate(
                name=Concat('cu_user__first_name',Value(' '),'cu_user__last_name')).filter(department=ETICKETTicket.department).values('cu_user','name')
            # print("result wo parent",result)
            return result

    def get_comment_count(self,ETICKETTicket):
        if ETICKETTicketComment.objects.filter(ticket = ETICKETTicket.id):
            return ETICKETTicketComment.objects.filter(ticket = ETICKETTicket.id).count()
        else:
            return 0
    
    def get_person_responsible(self,ETICKETTicket):
        #print('ETICKETTicket.assigned_to',ETICKETTicket.assigned_to)
        request = self.context.get('request')
        if ETICKETTicket.assigned_to != request.user:
            return {
                        'id': ETICKETTicket.assigned_to.id,
                        'name':ETICKETTicket.assigned_to.first_name +' '+ETICKETTicket.assigned_to.last_name
                }
        else:
            return {
                        'id': ETICKETTicket.assigned_to.id,
                        'name':ETICKETTicket.assigned_to.first_name +' '+ETICKETTicket.assigned_to.last_name
                }

    def get_assigned_to_department(self,ETICKETTicket):
        if ETICKETTicket.department:
            return ETICKETTicket.department.cd_name
        else:
            return None

    def get_raised_by_name(self,ETICKETTicket):
        if ETICKETTicket.created_by:
            return ETICKETTicket.created_by.first_name +' '+ETICKETTicket.created_by.last_name
        else:
            return None

    def get_document_details(self, ETICKETTicket):
        document = ETICKETTicketDoc.objects.filter(ticket=ETICKETTicket)
        request = self.context.get('request')
        response_list = []
        for each_document in document:
            file_url = request.build_absolute_uri(each_document.document.url)
            each_data = {
                "id": int(each_document.id),
                "document": file_url,
            }
            #print('each_data',each_data)
            response_list.append(each_data)
        return response_list

    def get_comment_details(self, ETICKETTicket):
        comment = ETICKETTicketComment.objects.annotate(
            name=Concat('created_by__first_name',Value(' '),'created_by__last_name')).filter(
                ticket=ETICKETTicket).values('id','ticket','comment',
        'name','created_at')
        return comment

    class Meta:
        model = ETICKETTicket
        fields = ('id','ticket_number','subject','department','assigned_to','assigned_to_department','raised_by_name',
        'priority','details','status','is_deleted','created_by','created_at','ticket_closed_date','person_responsible',
        'comment_count','document_details','comment_details','department_users')

class EticketTicketCommentAddSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    name = serializers.SerializerMethodField()
    def get_name(self, ETICKETTicketComment):
        if ETICKETTicketComment.created_by:
            return ETICKETTicketComment.created_by.first_name +' '+ETICKETTicketComment.created_by.last_name

        
    class Meta:
        model = ETICKETTicketComment
        fields = ('id','ticket','comment','created_by','created_at','name')

class EticketTicketChangePersonResponsibleSerializer(serializers.ModelSerializer):
    updated_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = ETICKETTicket
        fields = ('id','assigned_to','updated_by')

class EticketTicketSubjectListByDepartmentSerializer(serializers.ModelSerializer):
    #comment_count = serializers.SerializerMethodField()
    # def get_assigned_to_department(self,ETICKETTicket):
    #     if ETICKETTicket.department:
    #         return ETICKETTicket.department.cd_name
    #     else:
    #         return None

    class Meta:
        model = ETICKETSubjectOfDepartment
        fields = ('id','subject','department','is_deleted','created_by','created_at')
