from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from vms.models import *
from django.contrib.auth.models import *
from django.db import transaction, IntegrityError
from drf_extra_fields.fields import Base64ImageField
import os
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from users.models import TCoreUserDetail
from smssend.views import *
from threading import Thread
import re, time, base64
from datetime import datetime
import os

#:::::::::::::::::::::: VMS FLOOR DETAILS MASTER:::::::::::::::::::::::::::#
class FloorDetailsMasterAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = VmsFloorDetailsMaster
        fields = ('id', 'floor_name', 'description', 'is_deleted', 'created_by', 'owned_by')

class FloorDetailsMasterEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = VmsFloorDetailsMaster
        fields = ('id', 'floor_name', 'description', 'is_deleted', 'updated_by')

class FloorDetailsMasterDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = VmsFloorDetailsMaster
        fields = '__all__'
    def update(self, instance, validated_data):
        instance.is_deleted=True
        instance.updated_by = validated_data.get('updated_by')
        instance.save()
        return instance

#:::::::::::::::::::::: VMS CARD DETAILS MASTER:::::::::::::::::::::::::::#
class CardDetailsMasterAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    status = serializers.BooleanField(default=True)
    floor_details =serializers.ListField(required=False)
    card_current_status=serializers.CharField(required=False,default=1)
   
    class Meta:
        model = VmsCardDetailsMaster
        fields = ('id', 'card_no', 'card_friendly_no','card_current_status', 'status', 'report_arise',
                  'created_by', 'owned_by','floor_details')
    def create(self,validated_data):
        try:
            floor_details=validated_data.pop('floor_details') if 'floor_details' in validated_data else ""
            created_by=validated_data.get('created_by')
            owned_by=validated_data.get('owned_by')
            with transaction.atomic():
                card_details=VmsCardDetailsMaster.objects.create(**validated_data)
                # print('card_details',type(card_details))
                floor_details_list=[]
                for f_d in floor_details:
                    floor_data=VmsCardAndFloorMapping.objects.create(card_id=card_details.id,
                                                                    **f_d,
                                                                    created_by=created_by,
                                                                    owned_by=owned_by
                                                                    )
                    floor_data.__dict__.pop('_state') if '_state' in floor_data.__dict__.keys() else floor_data.__dict__
                    floor_details_list.append(floor_data.__dict__)
                card_details.__dict__['floor_details']=floor_details_list
                return card_details.__dict__

        except Exception as e:
            raise e
   
class CardDetailsMasterEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    card_current_status=serializers.CharField(required=False)
    report_arise=serializers.CharField(required=False)
    status=serializers.CharField(required=False)
    class Meta:
        model = VmsCardDetailsMaster
        fields = ('id','card_current_status','report_arise', 'status','updated_by')

##card_current_status: 3
# report_arise: "false"
# status: "false"

#report_arise: "True"

class CardAndFloorEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    floor_details=serializers.ListField(required=False)
    class Meta:
        model = VmsCardDetailsMaster
        fields = ('id','card_no','card_friendly_no','updated_by','floor_details')
    def update(self,instance,validated_data):
        try:
            floor_details=validated_data.pop('floor_details') if 'floor_details' in validated_data else None
            with transaction.atomic():
                instance.card_no=validated_data.get('card_no')
                instance.card_friendly_no=validated_data.get('card_friendly_no')
                instance.updated_by=validated_data.get('updated_by')
                instance.save()
                if floor_details: 
                    pre_floor_det=VmsCardAndFloorMapping.objects.filter(card_id=instance,status=True,is_deleted=False)
                    if pre_floor_det:
                        pre_floor_det.delete()
                    floor_det_list=[]
                    for f_d in floor_details:
                        floor_data=VmsCardAndFloorMapping.objects.create(card_id=str(instance.id),
                                                                        **f_d,
                                                                        updated_by=validated_data.get('updated_by')
                                                                        )
                        floor_data.__dict__.pop('_state')if '_state' in floor_data.__dict__.keys() else floor_data.__dict__
                        floor_det_list.append(floor_data.__dict__)
                    instance.__dict__['floor_details']=floor_det_list
                return instance.__dict__
        except Exception as e:
            raise e 

class CardDetailsMasterDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = VmsCardDetailsMaster
        fields = '__all__'

    def update(self, instance, validated_data):
        try:
            with transaction.atomic():
                instance.is_deleted=True
                instance.status=False
                instance.updated_by = validated_data.get('updated_by')
                instance.save()
                floor_data=VmsCardAndFloorMapping.objects.filter(card_id=instance,status=True,is_deleted=False)
                if floor_data:
                    floor_data.delete()
                return instance
        except Exception as e:
            raise e
class AvailableCardsListSerializer(serializers.ModelSerializer):
    class Meta:
        model = VmsCardDetailsMaster
        fields = '__all__'

#:::::::::::::::::::::: VMS VISITOR DETAILS:::::::::::::::::::::::::::#
class VisitorDetailsAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    status = serializers.BooleanField(default=True)
    picture = Base64ImageField(required=False)
    class Meta:
        model = VmsVisitorDetails
        fields = ('id', 'name', 'phone_no', 'email', 'address', 'picture', 'organization', 'status', 'created_by', 
        'owned_by')


class VisitorDetailsListSerializer(serializers.ModelSerializer):
    visit_details = serializers.SerializerMethodField()

    class Meta:
        model = VmsVisitorDetails
        fields = ('id', 'name', 'phone_no', 'email', 'address', 'picture', 'organization', 'status', 'visit_details')

    def get_visit_details(self, VmsVisitorDetails):
        visit_data_dict = {}
        meeting_complete = []
        meeting_on_going ={"login_time": None}
        drop_off = []

        visit_data = VmsVisit.objects.filter(visitor=VmsVisitorDetails.id)
        # print("visit_data",visit_data)

        for data in visit_data:
            data.__dict__.pop('_state') if '_state' in data.__dict__.keys() else data
            print("data",data.__dict__)

            visitor_type=VmsVisitorTypeMaster.objects.only('id').get(name='drop-off').id
            print('visitor_type',type(visitor_type),visitor_type)

            if data.__dict__['visitor_type_id'] == visitor_type:
                # print("Drop-off")
                drop_off.append(data.__dict__)            
           
            elif data.__dict__['visitor_type_id'] != visitor_type and data.__dict__['logout_time'] is None:
                # print("meeting and logged in")
                meeting_on_going["login_time"]=data.__dict__['login_time']
                meeting_on_going["card"]=data.__dict__['card_id']
                meeting_on_going["purpose"]=data.__dict__['purpose']
                meeting_on_going["floor_access"] = []
                meeting_on_going["visit_to"]=[]
                if data.__dict__['card_id']:
                    meeting_on_going["card_no"]=VmsCardDetailsMaster.objects.only('card_no').get(id=data.__dict__['card_id']).card_no
                    floor_access=VmsCardAndFloorMapping.objects.filter(card_id=data.__dict__['card_id']).values('floor__floor_name')
                    if floor_access:
                        meeting_on_going["floor_access"] = [x['floor__floor_name'] for x in floor_access]
                visit_to = VmsEmployeeVisitor.objects.filter(visit_id=data.__dict__['id']).values('visit_to','visit_to__first_name','visit_to__last_name')
                print('visit_to',visit_to)

                if visit_to:
                    meeting_on_going["visit_to"] = [{'name':y['visit_to__first_name']+' '+y['visit_to__last_name'],'id':y['visit_to']} for y in visit_to]

            elif data.__dict__['visitor_type_id'] != visitor_type and data.__dict__['logout_time'] is not None:
                # print("meeeyting  and   log out")
                meeting_complete.append(data.__dict__)

        visit_data_dict['drop_off_details'] = drop_off
        visit_data_dict['meeting_on_going_details'] = meeting_on_going
        visit_data_dict['meeting_complete_details'] = meeting_complete

        if visit_data_dict:
            return visit_data_dict
        else:
            return {}

class VisitorDetailsListForVisitorEntrySerializer(serializers.ModelSerializer):
    #visit_details = serializers.SerializerMethodField()

    class Meta:
        model = VmsVisitorDetails
        fields = ('id', 'name', 'phone_no', 'email', 'address', 'picture', 'organization', 'status',)

   
class VisitorDetailsEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    status=serializers.BooleanField(default=True)
    picture = Base64ImageField(required=False)
    class Meta:
        model = VmsVisitorDetails
        fields = ('id', 'name', 'phone_no', 'email', 'address', 'picture', 'organization', 'status', 'updated_by')

    def update(self, instance, validated_data):
        import os
        import datetime
        try:
            # print('validated_data::',validated_data)
            instance.name = validated_data.get('name')
            instance.phone_no = validated_data.get('phone_no')
            instance.email = validated_data.get('email')
            instance.address = validated_data.get('address')
            instance.organization = validated_data.get('organization')
            instance.status = validated_data.get('status')
            instance.updated_by = validated_data.get('updated_by')
            picture = validated_data.get("picture") if "picture" in validated_data else None
            if picture:
                existing_logo = './media/' + str(instance.picture)
                print('existing_logo',existing_logo)
                instance.picture = validated_data.get('picture', instance.picture)
                if validated_data.get('picture') and os.path.isfile(existing_logo):
                    os.remove(existing_logo)
            instance.save()

        except Exception as e:
            raise e
        return instance
    

class VisitorDetailsDeactivateSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = VmsVisitorDetails
        fields = '__all__'
    def update(self, instance, validated_data):
        visit = VmsVisit.objects.filter(visitor=instance,is_deleted=False,login_time__isnull=False,logout_time__isnull=True)
        if visit:
            raise APIException({'msg': 'Already Logged-in',
                                'request_status':0
        })
        else:
            instance.status=False
            instance.updated_by = validated_data.get('updated_by')
            instance.save()
            return instance

class OrganizationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = VmsVisitorDetails
        fields = ('organization',)

#:::::::::::::::::::: USER DETAILS :::::::::::::::::::::::::#
class UserDetailsListSerializer(serializers.ModelSerializer):

    class Meta:
        model = TCoreUserDetail
        fields = '__all__'

#:::::::::::::::::::::: VMS VISITOR TYPE MASTER:::::::::::::::::::::::::::#
class VisitorTypeMasterAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    status= serializers.BooleanField(default=True)
    class Meta:
        model = VmsVisitorTypeMaster
        fields = ('id', 'name','parent_id', 'status', 'created_by', 'owned_by')


class VisitorTypeMasterEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = VmsVisitorTypeMaster
        fields = ('id', 'name','parent_id','status', 'updated_by')

class VisitorTypeMasterDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = VmsVisitorTypeMaster
        fields = '__all__'
    def update(self, instance, validated_data):
        instance.is_deleted=True
        instance.status=False
        instance.updated_by = validated_data.get('updated_by')
        instance.save()
        return instance

#:::::::::::::::::::::: VMS VISIT:::::::::::::::::::::::::::#
class VisitAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    visiting = serializers.CharField(required=False)
    floor=serializers.CharField(required=False)
    class Meta:
        model = VmsVisit
        fields = ('id', 'visitor_type', 'visitor', 'card', 'purpose', 'login_time', 'logout_time',
                  'drop_off_time', 'created_by', 'owned_by', 'visiting','floor')

    def create(self, validated_data):

        # ============= SMS Send ==============#
        # visiting = validated_data.pop('visiting')
        # visit_to = visiting.split(",")
        # emp_mob_no=TCoreUserDetail.objects.filter(
        #     cu_user__in=visit_to,cu_is_deleted=False).values_list('cu_phone_no',flat=True)
        #print('emp_mob_no',emp_mob_no)
        # if emp_mob_no:
        #     for e_emp_mob_no in emp_mob_no:
        #         message_data = {
        #             "name":"Rupam",
        #             "purpose_of_visit": validated_data.get('purpose')
        #         }
        #         sms_class = GlobleSmsSendTxtLocal('VMSNV',[e_emp_mob_no])
        #         sms_thread = Thread(target = sms_class.sendSMS, args = (message_data,'whatsapp'))
        #         sms_thread.start()
       


        visiting = None
        floor = None
        visit_to = None
        emp_mob_no = None
        if 'visiting' in validated_data.keys():
            visiting = validated_data.pop('visiting')
        if 'floor'in validated_data.keys() :
            floor= validated_data.pop('floor')
        with transaction.atomic():
            drop_off_type=VmsVisitorTypeMaster.objects.only('id').get(name='drop-off').id
            # print('visitor_type',visitor_type)
            if str(validated_data.get('visitor_type'))==str(drop_off_type):
                visit_data, created = VmsVisit.objects.get_or_create(drop_off_time=timezone.now(),**validated_data)
            else:
                exist_visit = VmsVisit.objects.filter(visitor_id=validated_data['visitor'],login_time__isnull=False,
                                                    logout_time__isnull = True)
                if exist_visit:
                    raise APIException({'msg': 'Visitor already Logged In. Please Logout','request_status':0})
                else:
                    # print("gjhgjhg",validated_data)
                    visit_data,created = VmsVisit.objects.get_or_create(login_time=timezone.now(),**validated_data)
                    print('visit_data',visit_data)
                    if 'card' in validated_data.keys():
                        card_data = VmsCardDetailsMaster.objects.filter(id=validated_data['card'].id).update(card_current_status=2)

            if visit_data:
                # print("visit_data",visit_data.__dict__)     
                if visiting:
                    visit_to = visiting.split(",")
                    e_v_add = VmsEmployeeVisitor.objects.bulk_create([VmsEmployeeVisitor(visit=visit_data,visit_to_id=int(i),created_by=validated_data['created_by'],
                                    owned_by=validated_data['owned_by']) for i in visit_to])
                    validated_data['visiting'] = visiting
             
                if floor:          
                    floor_list=floor.split(",")
                    floor_add=VmsFloorVisitor.objects.bulk_create([VmsFloorVisitor(visit=visit_data,floor_id=int(j),created_by=validated_data['created_by'],
                                                                    owned_by=validated_data['owned_by']) for j in floor_list])
                    validated_data['floor']= floor

                if visit_to:   
                    emp_mob_no=TCoreUserDetail.objects.filter(cu_user__in=visit_to,cu_is_deleted=False).values('cu_phone_no')
                    print('emp_mob_no',emp_mob_no)
                    if emp_mob_no:
                        print('visitor',validated_data.get('visitor'))
                        visitor_d = VmsVisitorDetails.objects.filter(pk=str(validated_data.get('visitor'))).values('name')[0]
                        print('visitor_d', visitor_d)
                        for e_emp_mob_no in emp_mob_no:
                            message_data = {
                                "name": visitor_d['name'],
                                "purpose_of_visit": validated_data.get('purpose')
                            }
                            sms_class = GlobleSmsSendTxtLocal('VMSNV',[e_emp_mob_no['cu_phone_no']])
                            sms_thread = Thread(target = sms_class.sendSMS, args = (message_data,'sms'))
                            sms_thread.start()
                   
                
        return validated_data

class VisitListSerializer(serializers.ModelSerializer):
    visitor_details = serializers.SerializerMethodField()
    card_details = serializers.SerializerMethodField(required=False)
    visit_to_name = serializers.SerializerMethodField(required=False)
    visitor_type_name=serializers.SerializerMethodField(required=False)
    punch_details=serializers.SerializerMethodField(required=False)

    class Meta:
        model = VmsVisit
        fields = ('id', 'visitor_type', 'visitor', 'card', 'purpose', 'login_time', 'logout_time',
                  'drop_off_time', 'visitor_details', 'created_by', 'owned_by', 'card_details', 
                  'visit_to_name','visitor_type_name', 'punch_details')

    def get_visitor_type_name(self,VmsVisit):
        if VmsVisit.visitor_type:
            return VmsVisitorTypeMaster.objects.only('name').get(id=VmsVisit.visitor_type.id).name
    def get_visitor_details(self, VmsVisit):
        request = self.context.get('request')
        visitor_data = VmsVisitorDetails.objects.get(is_deleted=False,id=VmsVisit.visitor.id)
        visitor_data.__dict__.pop('_state') if '_state' in visitor_data.__dict__.keys() else visitor_data
        if visitor_data.__dict__['picture']:
            visitor_data.__dict__['picture'] = request.build_absolute_uri(visitor_data.picture.url)
        return visitor_data.__dict__

    def get_visit_to_name(self, VmsVisit):
        if VmsVisit.id:
            name = VmsEmployeeVisitor.objects.filter(is_deleted=False,visit=VmsVisit.id).values('visit_to','visit_to__first_name','visit_to__last_name')
            # print("name",name)
            # name_list = [nm['visit_to__first_name'] for nm in name]
            name_list = []

            for nm in name:
                print(nm['visit_to'])
                f_name = nm['visit_to__first_name'] if nm['visit_to__first_name'] else ''
                l_name = nm['visit_to__last_name'] if nm['visit_to__last_name'] else ''
                name = f_name + ' '+ l_name
                name_dict = {
                    'id': nm['visit_to'],
                    'name': name
                }
                name_list.append(name_dict)
            # print("name_list",name_list)
            return name_list
        else:
            return {}

    def get_card_details(self, VmsVisit):
        if VmsVisit.card:
            card_dict = {}
            floor_list = []
            card_dict["card_no"]= VmsVisit.card.card_no
            card_dict["card_friendly_no"]= VmsVisit.card.card_friendly_no
            floor_data = VmsCardAndFloorMapping.objects.filter(is_deleted=False,card=VmsVisit.card.id).values('floor__floor_name')
            if floor_data:
                floor_list = [x['floor__floor_name'] for x in floor_data]

            card_dict["floor_list"]= floor_list
            return card_dict
        else:
            return None

    def get_punch_details(self, VmsVisit):
        punch_data = VmsVisitorPunching.objects.filter(visit=VmsVisit.id).values('id','visit','gate','time')
        return punch_data

class VisitLogoutSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = VmsVisit
        fields = ('id', 'logout_time', 'updated_by')
    def update(self, instance, validated_data):
        if instance.card:
            card_data = VmsCardDetailsMaster.objects.filter(id=instance.card.id).update(card_current_status=1)
        instance.logout_time = timezone.now()
        instance.updated_by = validated_data.get('updated_by')
        instance.save()
        return instance

class VisitEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = VmsVisit
        fields = ('id', 'visitor_type', 'visitor', 'card', 'purpose', 'login_time', 'logout_time',
                  'drop_off_time', 'updated_by')

class VisitDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = VmsVisit
        fields = '__all__'
    def update(self, instance, validated_data):
        instance.is_deleted=True
        instance.updated_by = validated_data.get('updated_by')
        instance.save()
        return instance
