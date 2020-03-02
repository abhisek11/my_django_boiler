from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from users.models import *
from django.contrib.auth.models import *
from rest_framework.exceptions import APIException
from core.models import *
from master.models import *
from nameparser import HumanName
from mailsend.views import *
from smssend.views import *
from threading import Thread          #for threading
import os
from django.db import transaction, IntegrityError
from django.conf import settings
from django.db.models import F
import datetime
import json

'''
    New Token Authentication [knox]
'''
# from django.contrib.auth import authenticate

# class LoginSerializer(serializers.Serializer):
#     username = serializers.CharField()
#     password = serializers.CharField()

#     def validate(self, data):
#         user = authenticate(**data)
#         if user and user.is_active:
#             return user
#         raise serializers.ValidationError("Incorrect Credentials")

'''
    End
'''

class UserLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username',
            'password',)

class UserDetailsSerializer(serializers.ModelSerializer):
    # cu_user = UserSerializer()
    class Meta:
        model = TCoreUserDetail
        fields = ('id','cu_emp_code','reporting_head','hod','sap_personnel_no','joining_date')

class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False)
    email = serializers.CharField(required=False)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    is_superuser = serializers.BooleanField(required=False)
    is_active = serializers.BooleanField(required=False)
    class Meta:
        model = User
        fields = ('id','first_name', 'last_name', 'username','email', 'is_superuser', 'is_active')


class UserCreateSerializer(serializers.ModelSerializer):
    """ 
    This Serializer is for Adding User , 
    TCoreUserDetail and TMasterModuleRoleUser table, 
    with the permission id 
    """
    reporting_head = serializers.CharField(required=False,allow_null=True)
    employee_grade = serializers.CharField(required=False,allow_null=True)
    hod = serializers.CharField(required=False,allow_null=True)
    sap_personnel_no = serializers.CharField(required=False,allow_null=True)
    joining_date = serializers.CharField(required=False,allow_null=True)
    cu_phone_no = serializers.CharField(required=False,allow_null=True)
    cu_emp_code = serializers.CharField(required=False,allow_null=True)
    email = serializers.CharField(allow_null=True)
    role_module_details = serializers.ListField(required=False)
    mmr_updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    cu_profile_img=serializers.FileField(required=False)
    class Meta:
        model = User
        fields = ('id','username','email','first_name','last_name','cu_phone_no', 'cu_emp_code',
        'role_module_details','mmr_updated_by','reporting_head','employee_grade',
        'hod','sap_personnel_no','joining_date','cu_profile_img')

    def create(self, validated_data):
        try:
            print('validated_data',validated_data)
            print("validated_data.get('joining_date')", type(validated_data.get('joining_date')),validated_data.get('joining_date'))
            if validated_data.get('joining_date') == "null":
                joining_date = None
            else:
                joining_date = datetime.datetime.strptime(validated_data.get('joining_date'), "%Y-%m-%dT%H:%M:%S.%fZ") 
            
            print('joining_date',joining_date)
            logdin_user_id = self.context['request'].user.id
            #print("logdin_user_id: ", logdin_user_id)
            phone_no = validated_data.pop('cu_phone_no')
            print('phone_no',phone_no,type(phone_no))
            #cu_emp_code = validated_data.pop('cu_emp_code') if 'cu_emp_code' in validated_data else ''
            role_module_details = validated_data.pop('role_module_details')
            email = '' if validated_data['email'] == 'null' else validated_data['email']
            username = validated_data['username']

            with transaction.atomic():
                user_details_count = TCoreUserDetail.objects.filter(cu_user__username=username).count()
                if user_details_count:
                    raise APIException("Username already exist")
            
                #password = User.objects.make_random_password()
                password = "Shyam@123"
                #print('password: ', password)
                user = User.objects.create(
                    username=validated_data['username'],
                    email=email,
                    first_name = validated_data['first_name'],
                    last_name = validated_data['last_name'],
                    password = password
                )
                print('user_save: ', user)
                if user:
                    userdetail_save = TCoreUserDetail.objects.create(
                        cu_user=user,
                        cu_emp_code = '' if validated_data.get('cu_emp_code') == 'null' else validated_data.get('cu_emp_code'),
                        reporting_head_id = '' if validated_data.get('reporting_head') == 'null' else validated_data.get('reporting_head'),
                        hod_id = '' if validated_data.get('hod') == 'null' else validated_data.get('hod'),
                        sap_personnel_no = '' if validated_data.get('sap_personnel_no') == 'null' else validated_data.get('sap_personnel_no'),
                        joining_date= joining_date,
                        cu_phone_no=str(phone_no),
                        password_to_know=password,
                        cu_created_by_id=logdin_user_id,
                        cu_profile_img=validated_data.get('cu_profile_img'),
                        employee_grade_id = '' if validated_data.get('employee_grade') == 'null' else validated_data.get('employee_grade'),
                        )
                    print('userdetail_save',userdetail_save)
                    if userdetail_save:
                        if role_module_details:
                            #role_module_details[0] ths is for multipart/form-data
                            role_module_details = json.loads(role_module_details[0])
                            # print('role_module_details',role_module_details)
                           
                            for e_role_module_details in role_module_details:
                                #print('e_role_module_details',e_role_module_details)
                                role_id = e_role_module_details['role_id']
                                mmr_module_id = e_role_module_details['mmr_module_id']
                                mmr_type = e_role_module_details['mmr_type']
                                TMasterModuleRoleUser.objects.create(
                                    mmr_module_id=mmr_module_id,
                                    mmr_role_id=role_id,
                                    mmr_type = 3,
                                    mmr_user = user,
                                    mmr_created_by = validated_data['mmr_updated_by']
                                )
                                #print('12121212')
                                '''
                                    Assign role objects permission to User 
                                '''
                                tMasterOtherRole = TMasterOtherRole.objects.filter(
                                    mor_role_id=role_id,
                                    mor_module_id = mmr_module_id
                                    )
                                for e_tMasterOtherRole in tMasterOtherRole:
                                    TMasterOtherUser.objects.create(
                                        mou_user = user,
                                        mou_other = e_tMasterOtherRole.mor_other,
                                        mou_permissions = e_tMasterOtherRole.mor_permissions,
                                        mou_module_id = mmr_module_id,
                                        mou_created_by = validated_data['mmr_updated_by']
                                    )
                                    #print('rupam')
                    # data = {
                    #     'id': user.id,
                    #     'name': user.first_name + ' ' + user.last_name,
                    #     'email':user.email,
                    #     'first_name':user.first_name,
                    #     'last_name':user.last_name,
                    #     'username':user.username,
                    #     'cu_emp_code': validated_data.get('cu_emp_code'),
                    #     'cu_phone_no': validated_data.get('cu_phone_no')
                    # }

                    # ============= Mail Send ==============#
                    # if email:
                    #     mail_data = {
                    #                 "name": user.first_name+ '' + user.last_name,
                    #                 "user": username,
                    #                 "pass": password
                    #         }
                    #     print('mail_data',mail_data)
                    #     mail_class = GlobleMailSend('FP001', [email])
                    #     mail_thread = Thread(target = mail_class.mailsend, args = (mail_data,))
                    #     mail_thread.start()
                    # ============= SMS Send ==============#

                    # if cu_phone_no:
                    #     message_data = {
                    #     "user" : user.first_name+ '' + user.last_name,    
                    #     "pass": password 
                    #     }
                    #     sms_class = GlobleSmsSend('wellcom001',[cu_phone_no])
                    #     sms_thread = Thread(target = sms_class.sms_send, args = (message_data,))
                    #     sms_thread.start()

            return validated_data
        except Exception as e:
            raise e
            # raise APIException({'request_status': 0, 'msg': e})

class UserNewCreateSerializer(serializers.ModelSerializer):
    """ 
    This Serializer is for Adding User , 
    TCoreUserDetail and TMasterModuleRoleUser table, 
    with the permission id 
    """
    # name = serializers.CharField(required=False)
    #cu_super_set = serializers.CharField(required=False)

    cu_phone_no = serializers.CharField(required=False)
    cu_emp_code = serializers.CharField(required=False, allow_blank=True)
    role_module_details = serializers.ListField(required=False)
    mmr_updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = User
        fields = ('id','username','email','first_name','last_name','cu_phone_no', 'cu_emp_code','role_module_details','mmr_updated_by')

    def create(self, validated_data):
        try:
            print('validated_data',validated_data)
            logdin_user_id = self.context['request'].user.id
            #print("logdin_user_id: ", logdin_user_id)
            cu_phone_no = validated_data.pop('cu_phone_no')
            cu_emp_code = validated_data.pop('cu_emp_code') if 'cu_emp_code' in validated_data else ''
            #print("cu_emp_code: ", cu_emp_code)
            role_module_details = validated_data.pop('role_module_details')
            email = validated_data['email']
            username = validated_data['username']
            #with transaction.atomic():
                
                # if cu_phone_no:
                #     message_data = {
                #     "username": username,
                #     "password": 'Xcdew123',
                #     "cu_phone_no":cu_phone_no
                #     }
                #     sms_class = GlobleSmsSend(message_data)
                #     sms_thread = Thread(target = sms_class.sms_send, args = (message_data,))
                #     sms_thread.start()

                # user_details_count = TCoreUserDetail.objects.filter(cu_phone_no=cu_phone_no).count()
                # if user_details_count:
                #     raise APIException("phone no already exist")
               
                # user = User.objects.create(
                #     username=validated_data['username'],
                #     email=email,
                #     first_name = validated_data['first_name'],
                #     last_name = validated_data['last_name']
                # )
                # password = User.objects.make_random_password()
                # user.set_password(password)
                # user.save()
                #print('password: ', password)

                # userdetail = TCoreUserDetail.objects.create(
                #     cu_user=user,
                #     cu_phone_no=cu_phone_no,
                #     cu_created_by_id=logdin_user_id)
                # if cu_emp_code:
                #     userdetail.cu_emp_code = cu_emp_code
                #     userdetail.save()
            a = ['Ravi', 'vikash',   'rabindra', 'kushal',   'sandeep', 'subhendu', 'pranab',   'vikram',   'dinesh',   'shyamal',  'ankita',   'sujay',    'ajay', 'manoj',    
                'sayan',    'abul', 'manish1',  'saikat',   'thani',    'rahul',    'ARINDAM',  'HEMANT',   'SHAILENDRA',   
                'MRINAL',   'RUKHSAR',  'VIKASHKUMAR',  'SOURAV_DEV',   'VADIRAJ',  'SAIRAM',   'bindu_prakash_jena',  
                 'ankita_dasgupta',  'mousumisarkar',    'sangitadey',   'PulomaChatterjee', 'PayalMukherjee',   'dhrubojit',    
                 'AnutoshMaity', 'nandankumar',  'AntaripaMondal',   'DebjitKar',    'DipanwitaSen', 'NupurPoddar',  
                 'AshishLundia', 'BiswajitRay',  'VikashPoddar', 'VivekKumarSahu',   'KritiBhattacharjee',   'SamarDas', 
                 'SanchitaDey',  'SunandaMukherjee', 'SurenBasak',   'ShariqueAli',  'SuchismitaKundu',  'MONIKANABISWAS',   
                 'SomaDas',  'PrinsKumar',   'DhruvGoel',    'UrvashiBisht', 'ManishSharma', 'AnishDutta',   'IranJyotiSharma',  
                 'SatyamChaturvedi', 'AnupKumarVishwakarma', 'PrakashManiTripathi',  'SunilKumarDubey',  'SantoshKumarOjha', 
                 'AtulSharma',   'AnimeshMandal']
            #a = ['manish']
            count = 0
            for a1 in a:

                userdetail = User.objects.filter(username__iexact=a1)

                if userdetail: 
                    userdetail = User.objects.get(username__iexact=a1)
                    print('userdetail',userdetail)
                    count = count + 1
                    ad = TMasterModuleRoleUser.objects.create(
                        mmr_module_id=9,
                        mmr_role_id='',
                        mmr_type = 3,
                        mmr_user = userdetail,
                        mmr_created_by = validated_data['mmr_updated_by']
                    )
                    print('ad',ad)

            data = {
                'id': user.id,
                'name': user.first_name + ' ' + user.last_name,
                'email':user.email,
                'first_name':user.first_name,
                'last_name':user.last_name,
                'username':user.username,
                'cu_emp_code': userdetail.cu_emp_code,
                'cu_phone_no': userdetail.cu_phone_no
            }

                # ============= Mail Send ==============#
                # if email:
                #     mail_data = {
                #                 "name": user.first_name+ '' + user.last_name,
                #                 "user": username,
                #                 "pass": password
                #         }
                #     print('mail_data',mail_data)
                #     mail_class = GlobleMailSend('FP001', [email])
                #     mail_thread = Thread(target = mail_class.mailsend, args = (mail_data,))
                #     mail_thread.start()
                # ============= SMS Send ==============#
                # if cu_phone_no:
                #     message_data = {
                #     "cu_phone_no":cu_phone_no,
                #     "message": 'Congratulations! You have been successfully registered. Here is your login credentials%nusername : '+username+'%npassword : '+password, 
                #     }
                #     sms_class = GlobleSmsSend(message_data)
                #     sms_thread = Thread(target = sms_class.sms_send, args = (message_data,))
                #     sms_thread.start()
               

            return data
        except Exception as e:
            # raise e
            raise APIException({'request_status': 0, 'msg': e})

class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class ForgotPasswordSerializer(serializers.Serializer):
    """
    Serializer for password forgot.
    """
    mail_id = serializers.CharField(required=False)
    cu_phone_no = serializers.CharField(required=False)


class EditUserSerializer(serializers.ModelSerializer):
    cu_updated_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    name = serializers.CharField(required=False)
    cu_user = UserSerializer(read_only=True,required=False)
    email = serializers.CharField(required=False)
    cu_emp_code = serializers.CharField(required=False)
    class Meta:
        model = TCoreUserDetail
        fields = ('id', 'cu_phone_no', 'cu_alt_phone_no', 'cu_profile_img', 'cu_dob', 'name', 'cu_updated_by', 'cu_user',
                  'cu_emp_code', 'email')
        # lookup_field = 'cu_user_id'


    def update(self, instance, validated_data):
        try:
            email = validated_data.pop('email') if "email" in validated_data else ""
            name = HumanName(validated_data.pop('name'))
            first_name = name.first + " " + name.middle
            last_name = name.last

            instance.cu_phone_no = validated_data.get("cu_phone_no", instance.cu_phone_no)
            instance.cu_alt_phone_no = validated_data.get("cu_alt_phone_no", instance.cu_alt_phone_no)

            existing_images = '.' + settings.MEDIA_URL + str(instance.cu_profile_img)
            if validated_data.get('cu_profile_img'):
                print('os.path.isfile(existing_images)::', os.path.isfile(existing_images))
                if os.path.isfile(existing_images):
                    os.remove(existing_images)

                instance.cu_profile_img = validated_data.get("cu_profile_img", instance.cu_profile_img)
            instance.cu_dob = validated_data.get("cu_dob", instance.cu_dob)
            instance.cu_updated_by = validated_data.get("cu_updated_by", instance.cu_updated_by)
            instance.cu_user.first_name = first_name.strip()
            instance.cu_user.last_name = last_name.strip()
            if email and instance.cu_updated_by.is_superuser:
                instance.cu_user.email = email
                instance.cu_user.username = email
                instance.cu_emp_code = validated_data.get("cu_emp_code", instance.cu_emp_code)
            instance.cu_user.save()
            instance.save()

            data_dict = {}
            user_details = TCoreUserDetail.objects.get(pk=instance.id)
            data_dict['id'] = user_details.id
            data_dict['cu_phone_no'] = user_details.cu_phone_no
            data_dict['cu_alt_phone_no'] = user_details.cu_alt_phone_no
            data_dict['cu_profile_img'] = user_details.cu_profile_img
            data_dict['cu_dob'] = user_details.cu_dob
            data_dict['cu_emp_code'] = user_details.cu_emp_code
            data_dict['email'] = user_details.cu_user.email
            data_dict['name'] = user_details.cu_user.first_name + " " + user_details.cu_user.last_name
            return data_dict
        except Exception as e:
            raise APIException({'request_status': 0, 'msg': e})

class UserModuleSerializer(serializers.ModelSerializer):
    cu_user = UserSerializer()
    class Meta:
        model = TCoreUserDetail
        fields = ('id', 'cu_emp_code', 'cu_phone_no', 'cu_alt_phone_no', 'cu_dob', 'cu_user', 'applications')

class UserPermissionEditSerializer(serializers.ModelSerializer):

    cu_updated_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    name = serializers.CharField(required=False)
    cu_user = UserSerializer(read_only=True,required=False)
    email = serializers.CharField(required=False)
    cu_emp_code = serializers.CharField(required=False)
    module_access = serializers.SerializerMethodField()

    def get_module_access(self,TCoreUserDetail):
        response_data = list()
        tMasterModuleRoleUser = TMasterModuleRoleUser.objects.filter(mmr_user=TCoreUserDetail.cu_user)
        #print('tMasterModuleRoleUser',tMasterModuleRoleUser)
        for e_tMasterModuleRoleUser in tMasterModuleRoleUser:
            if e_tMasterModuleRoleUser.mmr_module:
                module_details = TCoreModule.objects.filter(pk=e_tMasterModuleRoleUser.mmr_module.id).values()[0]
            else:
                module_details = dict()
            if e_tMasterModuleRoleUser.mmr_role:
                role_details = TCoreRole.objects.filter(pk=e_tMasterModuleRoleUser.mmr_role.id).values()[0]
            else:
                role_details = dict()
            response_data.append({
                'module':module_details,
                'role':role_details
            })
        return response_data

    class Meta:
        model = TCoreUserDetail
        fields = ('id', 'cu_phone_no', 'cu_alt_phone_no', 'cu_profile_img', 'cu_dob', 'name', 'cu_updated_by', 'cu_user',
                  'cu_emp_code', 'email','module_access')
        # lookup_field = 'cu_user_id'


    def update(self, instance, validated_data):
        try:
            email = validated_data.pop('email') if "email" in validated_data else ""
            name = HumanName(validated_data.pop('name'))
            first_name = name.first + " " + name.middle
            last_name = name.last

            instance.cu_phone_no = validated_data.get("cu_phone_no", instance.cu_phone_no)
            instance.cu_alt_phone_no = validated_data.get("cu_alt_phone_no", instance.cu_alt_phone_no)

            existing_images = '.' + settings.MEDIA_URL + str(instance.cu_profile_img)
            if validated_data.get('cu_profile_img'):
                print('os.path.isfile(existing_images)::', os.path.isfile(existing_images))
                if os.path.isfile(existing_images):
                    os.remove(existing_images)

                instance.cu_profile_img = validated_data.get("cu_profile_img", instance.cu_profile_img)
            instance.cu_dob = validated_data.get("cu_dob", instance.cu_dob)
            instance.cu_updated_by = validated_data.get("cu_updated_by", instance.cu_updated_by)
            instance.cu_user.first_name = first_name.strip()
            instance.cu_user.last_name = last_name.strip()
            if email and instance.cu_updated_by.is_superuser:
                instance.cu_user.email = email
                instance.cu_user.username = email
                instance.cu_emp_code = validated_data.get("cu_emp_code", instance.cu_emp_code)
            instance.cu_user.save()
            instance.save()

            data_dict = {}
            user_details = TCoreUserDetail.objects.get(pk=instance.id)
            data_dict['id'] = user_details.id
            data_dict['cu_phone_no'] = user_details.cu_phone_no
            data_dict['cu_alt_phone_no'] = user_details.cu_alt_phone_no
            data_dict['cu_profile_img'] = user_details.cu_profile_img
            data_dict['cu_dob'] = user_details.cu_dob
            data_dict['cu_emp_code'] = user_details.cu_emp_code
            data_dict['email'] = user_details.cu_user.email
            data_dict['name'] = user_details.cu_user.first_name + " " + user_details.cu_user.last_name
            return data_dict
        except Exception as e:
            raise APIException({'request_status': 0, 'msg': e})

class EditUserNewSerializer(serializers.ModelSerializer):
    cu_phone_no = serializers.CharField(required=False,allow_null=True)
    cu_emp_code = serializers.CharField(required=False,allow_null=True)
    role_module_details = serializers.ListField(required=False)
    mmr_updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    reporting_head = serializers.CharField(required=False,allow_null=True)
    employee_grade = serializers.CharField(required=False,allow_null=True)
    hod = serializers.CharField(required=False,allow_null=True)
    sap_personnel_no = serializers.CharField(required=False,allow_null=True)
    joining_date = serializers.CharField(required=False,allow_null=True)
    cu_profile_img = serializers.FileField(required=False,allow_null=True)
    email = serializers.CharField(allow_null=True)

    class Meta:
        model = User
        fields = ('id','username','email','first_name','last_name','cu_phone_no', 
        'cu_emp_code','role_module_details','mmr_updated_by','reporting_head','employee_grade',
        'hod','sap_personnel_no','joining_date','cu_profile_img')

    def update(self, instance, validated_data):
        try:
            print("validated_data", validated_data)
            role_module_details = validated_data.pop('role_module_details')
            print('role_module_details',role_module_details)
            joining_date = None if validated_data.get('joining_date') == 'null' else datetime.datetime.strptime(validated_data.get('joining_date'), "%Y-%m-%dT%H:%M:%S.%fZ") 
            cu_profile_img = validated_data.get("cu_profile_img") if "cu_profile_img" in validated_data else None
            email = '' if validated_data['email'] == 'null' else validated_data['email']
            phone_no = '' if validated_data['cu_phone_no'] == 'null' else validated_data['cu_phone_no']
            print('phone_no',phone_no)
            
            with transaction.atomic():
                instance.first_name = validated_data.get('first_name')
                instance.last_name = validated_data.get('last_name')
                instance.email = email
                instance.username = validated_data.get('username')
                instance.save()

                user_details_count = TCoreUserDetail.objects.filter(cu_user=instance).count()
                if user_details_count:
                    user_details = TCoreUserDetail.objects.get(cu_user=instance)
                    user_details.cu_emp_code = '' if validated_data.get('cu_emp_code') == 'null' else validated_data.get('cu_emp_code')
                    user_details.cu_phone_no = phone_no
                    user_details.reporting_head_id = '' if validated_data.get('reporting_head') == "null" else str(validated_data.get('reporting_head'))
                    user_details.employee_grade_id = '' if validated_data.get('employee_grade') == "null" else str(validated_data.get('employee_grade'))
                    user_details.hod_id = '' if validated_data.get('hod') == 'null' else str(validated_data.get('hod'))
                    user_details.sap_personnel_no = '' if validated_data.get('sap_personnel_no') == 'null' else validated_data.get('sap_personnel_no')
                    user_details.joining_date =joining_date
                    user_details.cu_updated_by = validated_data['mmr_updated_by']
                    if cu_profile_img:
                        existing_image='./media/' + str(user_details.cu_profile_img)
                        if os.path.isfile(existing_image):
                            os.remove(existing_image)
                        user_details.cu_profile_img = cu_profile_img
                    user_details.save()
                    print('user_details')
                    if role_module_details:
                        print('dsgfdgfdfgg')
                        role_module_details = json.loads(role_module_details[0])
                        print('role_module_details',role_module_details)
                        TMasterModuleRoleUser.objects.filter(
                                    mmr_user = instance,
                                    ).delete()
                        if role_module_details:
                            
                            for e_role_module_details in role_module_details:
                                role_id = e_role_module_details['role_id']
                                mmr_module_id = e_role_module_details['mmr_module_id']
                                mmr_type = int(e_role_module_details['mmr_type'])
                                # p = TMasterModuleRoleUser.objects.filter(
                                #     mmr_module_id=mmr_module_id,
                                #     mmr_role_id = role_id,
                                #     mmr_user = instance,
                                #     ).delete()
                                # print('p',p)
                                TMasterModuleRoleUser.objects.create(
                                    mmr_module_id=mmr_module_id,
                                    mmr_role_id=role_id,
                                    mmr_type = mmr_type,
                                    mmr_user = instance,
                                    mmr_created_by = validated_data['mmr_updated_by']
                                )

                                '''
                                    Assign role objects permission to User 
                                '''
                                # tMasterOtherRole = TMasterOtherRole.objects.filter(
                                #     mor_role_id=role_id,
                                #     mor_module_id = mmr_module_id
                                #     )
                                # for e_tMasterOtherRole in tMasterOtherRole:
                                #     TMasterOtherUser.objects.create(
                                #         mou_user = instance,
                                #         mou_other = e_tMasterOtherRole.mor_other,
                                #         mou_permissions = e_tMasterOtherRole.mor_permissions,
                                #         mou_module_id = mmr_module_id,
                                #         mou_created_by = validated_data['mmr_updated_by']
                                #     )
                       
                            
                else:
                    raise APIException("User does not exist")
                # print('password: ', password)
                return validated_data
        except Exception as e:
            # raise e
            raise APIException({'request_status': 0, 'msg': e})

class EditUserGetNewSerializer(serializers.ModelSerializer):
    cu_phone_no = serializers.SerializerMethodField()
    cu_emp_code = serializers.SerializerMethodField()
    hod = serializers.SerializerMethodField()
    reporting_head = serializers.SerializerMethodField()
    employee_grade = serializers.SerializerMethodField()
    sap_personnel_no = serializers.SerializerMethodField()
    joining_date = serializers.SerializerMethodField()
    cu_profile_img = serializers.SerializerMethodField(required=False)
    #mmr_updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    role_module_details = serializers.SerializerMethodField()

    def get_role_module_details(self,User):
        module_role_details = TMasterModuleRoleUser.objects.filter(mmr_user__id=User.id).annotate(
                role_id = F('mmr_role'),
                ).values('mmr_type','mmr_module_id','role_id')
        return module_role_details

    def get_cu_phone_no(self,User):
        if TCoreUserDetail.objects.only('cu_phone_no').get(cu_user__id=User.id).cu_phone_no:
            return TCoreUserDetail.objects.only('cu_phone_no').get(cu_user__id=User.id).cu_phone_no
        else:
            return None

    def get_cu_emp_code(self,User):
        if TCoreUserDetail.objects.only('cu_emp_code').get(cu_user__id=User.id).cu_emp_code:
            return TCoreUserDetail.objects.only('cu_emp_code').get(cu_user__id=User.id).cu_emp_code
        else:
            return None

    def get_reporting_head(self,User):
        reporting_head_d =  TCoreUserDetail.objects.only('reporting_head').get(cu_user__id=User.id).reporting_head
        if reporting_head_d:
            return reporting_head_d.id
        else:
            return None
    
    def get_hod(self,User):
        hod_d = TCoreUserDetail.objects.only('hod').get(cu_user__id=User.id).hod
        if hod_d:
            return hod_d.id
        else:
            return None
    
    def get_employee_grade(self,User):
        employee_grade_d = TCoreUserDetail.objects.only('employee_grade').get(cu_user__id=User.id).employee_grade
        if employee_grade_d:
            return employee_grade_d.id
        else:
            return None

    def get_sap_personnel_no(self,User):
        if TCoreUserDetail.objects.only('sap_personnel_no').get(cu_user__id=User.id).sap_personnel_no:
            return TCoreUserDetail.objects.only('sap_personnel_no').get(cu_user__id=User.id).sap_personnel_no
        else:
            return None
    
    def get_joining_date(self,User):
        if TCoreUserDetail.objects.only('joining_date').get(cu_user__id=User.id).joining_date:
            return str(TCoreUserDetail.objects.only('joining_date').get(cu_user__id=User.id).joining_date)
        else:
            return None
    
    def get_cu_profile_img(self,User):
        image_details = TCoreUserDetail.objects.only('cu_profile_img').get(cu_user__id=User.id).cu_profile_img
        print('image_details',image_details)
        if image_details:
            request = self.context.get('request')
            return request.build_absolute_uri(image_details.url)
        else:
            return ''

    class Meta:
        model = User
        fields = ('id','username','email','is_superuser','first_name','last_name','role_module_details',
        'cu_phone_no','cu_emp_code','hod','reporting_head','employee_grade',
        'sap_personnel_no','joining_date','cu_profile_img')