from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from master.models import *
from core.models import *
from core.serializers import *
from users.serializers import *
from django.contrib.auth.models import *
from rest_framework.exceptions import APIException
from django.conf import settings
import random
import string
from django.db.models import Q

class UserListSerializer(serializers.ModelSerializer):
    mmr_role = TCoreRoleSerializer()
    mmr_module = TCoreModuleSerializer()
    mmr_permissions = TCorePermissionsSerializer()
    mmr_user = UserSerializer()
    # mmr_user = UserDetailsSerializer(many=True, read_only=True)


    class Meta:
        model = TMasterModuleRoleUser        
        # fields = ('id','mmr_module', 'mmr_permissions','mmr_role','mmr_user', 'user_details')
        fields = ('id', 'mmr_module', 'mmr_permissions', 'mmr_role', 'mmr_user')

class ModuleRoleSerializer(serializers.ModelSerializer):
    mmro_role = TCoreRoleSerializer()
    mmro_created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    module_name = serializers.SerializerMethodField()

    def get_module_name(self,TMasterModuleRole):
        return TCoreModule.objects.only('cm_name').get(pk=TMasterModuleRole.mmro_module.id).cm_name
        
    class Meta:
        model = TMasterModuleRole       
        fields = ('id','mmro_module','module_name','mmro_created_by','mmro_role',)
    def create(self, validated_data):
        try:
            data = {}
            logdin_user_id = self.context['request'].user.id
            role_dict = validated_data.pop('mmro_role')

            print('validated_data: ', validated_data)
            role = TCoreRole.objects.create(**role_dict, cr_created_by_id=logdin_user_id)
            if role:
                module_role_data = TMasterModuleRole.objects.create(
                    mmro_module = validated_data['mmro_module'], 
                    mmro_role=role,
                    mmro_created_by = validated_data['mmro_created_by'],
                    )
                data['id'] = module_role_data.pk
                data['mmro_module'] = module_role_data.mmro_module
                data['mmro_role'] = module_role_data.mmro_role
                data['mmro_created_by'] = module_role_data.mmro_created_by

            return data
        except Exception as e:
            # raise e
            raise serializers.ValidationError({'request_status': 0, 'msg': 'error', 'error': e})

class AssignPermissonToRoleAddSerializer(serializers.ModelSerializer):
    #mor_updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    mor_created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    mor_other_permisson_details =serializers.ListField()
    class Meta:
        model = TMasterOtherRole
        fields = ('id', 'mor_module','mor_other_permisson_details','mor_role','mor_created_by')
    def create(self, validated_data):
        try:
            print('validated_data',validated_data)

            mor_module = validated_data.get('mor_module')
            mor_role = validated_data.get('mor_role')
            mor_other_permisson_details = validated_data.get('mor_other_permisson_details')
            for e_mor_other_permisson_details in mor_other_permisson_details:
                tMasterOtherRole = TMasterOtherRole.objects.filter(
                    mor_role=validated_data.get('mor_role'),
                    mor_other = e_mor_other_permisson_details['mor_other'],
                    mor_module=mor_module
                )
                print(type(e_mor_other_permisson_details['mor_permisson']))
                if tMasterOtherRole:
                    print('TMasterModuleRoleUser', tMasterOtherRole)
                    # tMasterOtherRole.mor_role = validated_data.get('mor_role')
                    # tMasterOtherRole.mor_other_id = e_mor_other_permisson_details['mor_other']
                    # tMasterOtherRole.mor_permissions_id = e_mor_other_permisson_details['mor_permisson']
                    # tMasterOtherRole.mor_module = mor_module
                    # tMasterOtherRole.mor_updated_by = validated_data.get('mor_created_by')
                    if e_mor_other_permisson_details['mor_permisson']==0 or e_mor_other_permisson_details['mor_permisson']==4:
                        mor_permisson_v = None
                    else:
                        mor_permisson_v = e_mor_other_permisson_details['mor_permisson']
                    tMasterOtherRole.update(
                        mor_role=validated_data.get('mor_role'),
                        mor_other_id=e_mor_other_permisson_details['mor_other'],
                        mor_permissions_id=mor_permisson_v,
                        mor_module=mor_module,
                        mor_created_by=validated_data.get('mor_created_by')
                    )
                else:
                    if e_mor_other_permisson_details['mor_permisson']==0 or e_mor_other_permisson_details['mor_permisson']==4:
                        mor_permisson_v = None
                    else:
                        mor_permisson_v = e_mor_other_permisson_details['mor_permisson']
                    TMasterOtherRole.objects.create(
                        mor_role=validated_data.get('mor_role'),
                        mor_other_id=e_mor_other_permisson_details['mor_other'],
                        mor_permissions_id=mor_permisson_v,
                        mor_module=mor_module,
                        mor_created_by=validated_data.get('mor_created_by')
                    )
                        #print('e_TMasterModuleRoleUser1111')
            return validated_data
        except Exception as e:
            # raise e
            raise serializers.ValidationError({'request_status': 0, 'msg': 'error', 'error': e})

# ::::::::::::::::::::::Manpower serializer:::::::::::::::::::::::::::::::::::::::::::#
class UserModuleWiseListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TMasterModuleRoleUser
        fields = ('id', 'mmr_module','mmr_role', 'mmr_user')



class UserModuleWiseUserListByDesignationIdSerializer(serializers.ModelSerializer):
    # user_details =serializers.ListField(required=True)
    class Meta:
        model = TMasterModuleRoleUser
        fields = ('id', 'mmr_module','mmr_role', 'mmr_user')


class GradeAddSerializer(serializers.ModelSerializer):
    cg_created_by=serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = TCoreGrade
        fields = ('id','cg_name','cg_created_by','cg_parent_id')


class AssignPermissonToRoleAddNewSerializer(serializers.ModelSerializer):
    #mor_updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    mor_created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    mor_other_permisson_details =serializers.ListField()
    mor_module = serializers.CharField()
    mor_role = serializers.CharField()

    class Meta:
        model = TMasterOtherRole
        fields = ('id', 'mor_module','mor_other_permisson_details','mor_role','mor_created_by')
    def create(self, validated_data):
        try:
            #print('validated_data',validated_data)

            mor_module = TCoreModule.objects.get(cm_name=validated_data.get('mor_module'))
            #print('mor_module',mor_module)
            mor_role = TCoreRole.objects.get(cr_name=validated_data.get('mor_role'))
            #print('mor_role',mor_role)
            

            '''
                Insert Data to TMasterOtherRole
            '''
            mor_other_permisson_details = validated_data.get('mor_other_permisson_details')
            #print('mor_other_permisson_details',mor_other_permisson_details)

            for e_mor_other_permisson_details in mor_other_permisson_details:
                tMasterOtherRole = TMasterOtherRole.objects.filter(
                    mor_role=mor_role,
                    mor_other = e_mor_other_permisson_details['mor_other'],
                    mor_module=mor_module
                )
                #print(type(e_mor_other_permisson_details['mor_permisson']))
                #print('tMasterOtherRole',tMasterOtherRole)
                if tMasterOtherRole:
                    #print('TMasterModuleRoleUser', tMasterOtherRole)
                    if e_mor_other_permisson_details['mor_permisson']==0 or e_mor_other_permisson_details['mor_permisson']==4:
                        mor_permisson_v = None
                    else:
                        mor_permisson_v = e_mor_other_permisson_details['mor_permisson']
                       
                    tMasterOtherRole.update(
                        mor_role=mor_role,
                        mor_other_id=e_mor_other_permisson_details['mor_other'],
                        mor_permissions_id=mor_permisson_v,
                        mor_module=mor_module,
                        mor_created_by=validated_data.get('mor_created_by')
                    )

                    tMasterOtherUser = TMasterOtherUser.objects.filter(
                        mou_other_id = e_mor_other_permisson_details['mor_other'],
                        mou_module=mor_module
                        ).update(mou_permissions_id=mor_permisson_v)
                    print('tMasterOtherUser',tMasterOtherUser)
                
                else:
                    #print('ddddddd',e_mor_other_permisson_details['mor_other'])
                    if e_mor_other_permisson_details['mor_permisson']==0 or e_mor_other_permisson_details['mor_permisson']==4:
                        mor_permisson_v = None
                    else:
                        mor_permisson_v = e_mor_other_permisson_details['mor_permisson']

                    re = TMasterOtherRole.objects.create(
                        mor_role=mor_role,
                        mor_other_id=e_mor_other_permisson_details['mor_other'],
                        mor_permissions_id=mor_permisson_v,
                        mor_module=mor_module,
                        mor_created_by=validated_data.get('mor_created_by')
                    )

                    tMasterOtherUser = TMasterOtherUser.objects.filter(
                        mou_other_id = e_mor_other_permisson_details['mor_other'],
                        mou_module=mor_module
                        )
                    
                    if not tMasterOtherUser:
                        print('else')
                        users = TMasterModuleRoleUser.objects.filter(
                            mmr_role=mor_role,mmr_module=mor_module,).values_list('mmr_user',flat=True)
                        print('user',users)
                        existing_user_tMasterOtherUser = TMasterOtherUser.objects.filter(mou_user__in=users).values_list('mou_user',flat=True).distinct()
                        print('existing_user_tMasterOtherUser',existing_user_tMasterOtherUser)
                        for user in existing_user_tMasterOtherUser:
                            print('user',type(user))
                            TMasterOtherUser.objects.create(
                                mou_user_id=user,
                                mou_other_id=e_mor_other_permisson_details['mor_other'],
                                mou_permissions_id=mor_permisson_v,
                                mou_module=mor_module,
                                mou_created_by=validated_data.get('mor_created_by')
                            )
                        # print('tMasterOtherUser',tMasterOtherUser)

                    #print('re',re)
            
            '''
                Insert Data to TMasterOtherUser
            '''
            
            
            return validated_data
        except Exception as e:
            # raise e
            raise serializers.ValidationError({'request_status': 0, 'msg': 'error', 'error': e})

class ModuleRoleNewSerializer(serializers.ModelSerializer):
    mmro_role = TCoreRoleSerializer()
    mmro_created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    mmro_module = serializers.CharField()
        
    class Meta:
        model = TMasterModuleRole       
        fields = ('id','mmro_module','mmro_created_by','mmro_role',)
    def create(self, validated_data):
        try:
            data = {}
            logdin_user_id = self.context['request'].user.id
            role_dict = validated_data.pop('mmro_role')
            mmro_module = TCoreModule.objects.get(cm_name=validated_data.get('mmro_module'))
            #print('validated_data: ', validated_data)
            role = TCoreRole.objects.create(**role_dict, cr_created_by_id=logdin_user_id)
            if role:
                module_role_data = TMasterModuleRole.objects.create(
                    mmro_module = mmro_module, 
                    mmro_role=role,
                    mmro_created_by = validated_data['mmro_created_by'],
                    )
            return module_role_data
        except Exception as e:
            # raise e
            raise serializers.ValidationError({'request_status': 0, 'msg': 'error', 'error': e})


class AssignPermissonToUserAddNewSerializer(serializers.ModelSerializer):
    mou_created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    mou_other_permisson_details =serializers.ListField()
    mou_role = serializers.CharField(required=False)

    class Meta:
        model = TMasterOtherUser
        fields = ('id', 'mou_module','mou_role','mou_other_permisson_details','mou_user','mou_created_by')
    def create(self, validated_data):
        try:
            #print('validated_data',validated_data)
            mou_module = validated_data.get('mou_module')
            mou_user = validated_data.get('mou_user')
            #mou_role = validated_data.get('mou_role')
            #print('mou_role',mou_role)
            
            mou_other_permisson_details = validated_data.get('mou_other_permisson_details')
            #print('mou_other_permisson_details',mou_other_permisson_details)

            for e_mou_other_permisson_details in mou_other_permisson_details:
                tMasterOtherUser = TMasterOtherUser.objects.filter(
                    mou_user=mou_user,
                    mou_other = e_mou_other_permisson_details['mou_other'],
                    mou_module=mou_module
                )
                #print(type(e_mou_other_permisson_details['mou_permisson']))
                print('tMasterOtherRole',tMasterOtherUser)
                if tMasterOtherUser:
                    #print('TMasterModuleRoleUser', tMasterOtherUser)
                    if e_mou_other_permisson_details['mou_permisson']==0 or e_mou_other_permisson_details['mou_permisson']==4:
                        mou_permisson_v = None
                    else:
                        mou_permisson_v = e_mou_other_permisson_details['mou_permisson']
                    tMasterOtherUser.update(
                        mou_user=mou_user,
                        mou_other_id=e_mou_other_permisson_details['mou_other'],
                        mou_permissions_id=mou_permisson_v,
                        mou_module=mou_module,
                        mou_created_by=validated_data.get('mou_created_by')
                    )
                else:
                    #print('ddddddd',e_mou_other_permisson_details['mou_other'])
                    if e_mou_other_permisson_details['mou_permisson']==0 or e_mou_other_permisson_details['mou_permisson']==4:
                        mou_permisson_v = None
                    else:
                        mou_permisson_v = e_mou_other_permisson_details['mou_permisson']

                    re = TMasterOtherUser.objects.create(
                        mou_user=mou_user,
                        mou_other_id=e_mou_other_permisson_details['mou_other'],
                        mou_permissions_id=mou_permisson_v,
                        mou_module=mou_module,
                        mou_created_by=validated_data.get('mou_created_by')
                    )
                    #print('re',re)
            return validated_data
        except Exception as e:
            # raise e
            raise serializers.ValidationError({'request_status': 0, 'msg': 'error', 'error': e})
