from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from core.models import *
from django.contrib.auth.models import *
from rest_framework.exceptions import APIException
from django.conf import settings
# from rest_framework.validators import *
from drf_extra_fields.fields import Base64ImageField # for image base 64
from django.db import transaction, IntegrityError
from master.models import TMasterModuleOther,TMasterOtherRole,TMasterOtherUser,TMasterModuleRoleUser

class TCorePermissionsSerializer(serializers.ModelSerializer):
    cp_created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = TCorePermissions
        fields = ('id','name','cp_created_by')


class TCoreModuleSerializer(serializers.ModelSerializer):
    cm_created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = TCoreModule
        fields = ('id','cm_name','cm_icon','cm_desc','cm_url',
                   'cm_created_by', 'cm_is_editable')

class TCoreModuleListSerializer(serializers.ModelSerializer):
    """docstring for ClassName"""
    # cm_icon = Base64ImageField()    
    
    class Meta:
        model = TCoreModule
        fields = ('id','cm_name', 'cm_icon','cm_desc','cm_url')

class TCoreRoleSerializer(serializers.ModelSerializer):
    """docstring for ClassName"""
    cr_created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = TCoreRole
        fields = ('id','cr_name', 'cr_parent_id', 'cr_created_by','cr_is_deleted')

class UnitAddSerializer(serializers.ModelSerializer):
    c_created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    c_owned_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = TCoreUnit
        fields = ('id', 'c_name', 'c_created_by', 'c_owned_by')

#:::::::::::::::: OBJECTS :::::::::::::#

class OtherAddSerializer(serializers.ModelSerializer):
    cot_created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    cot_parent_id = serializers.IntegerField(required=False)
    mmo_module = serializers.CharField(required=False)
    class Meta:
        model = TCoreOther
        fields = ('id','cot_name','description','cot_parent_id','cot_created_by','mmo_module')
    def create(self, validated_data):
        try:
            cot_created_by = validated_data.get('cot_created_by')
            cot_parent_id = validated_data.pop('cot_parent_id') if 'cot_parent_id' in validated_data else 0
            with transaction.atomic():
                cot_save_id = TCoreOther.objects.create(
                    cot_name=validated_data.get('cot_name'),
                    description=validated_data.get('description'),
                    cot_parent_id = cot_parent_id,
                    cot_created_by=cot_created_by,
                )
                master_module = TMasterModuleOther.objects.create(
                    mmo_other = cot_save_id,
                    mmo_module_id = validated_data.get('mmo_module'),

                )
                response = {
                    'id': cot_save_id.id,
                    'cot_name': cot_save_id.cot_name,
                    'description': cot_save_id.description,
                    'mmo_module':master_module.mmo_module,
                    'cot_parent_id':cot_save_id.cot_parent_id
                }
                return response
        except Exception as e:
            raise e

class OtherListSerializer(serializers.ModelSerializer):
    #parent_name = serializers.CharField(required=False)
    class Meta:
        model = TMasterModuleOther
        fields = ('id','mmo_other','mmo_module','is_deleted')

class OtherListForRoleSerializer(serializers.ModelSerializer):
    permission = serializers.CharField(required=False)
    class Meta:
        model = TMasterModuleOther
        fields = ('id','mmo_other','mmo_module','is_deleted','permission')

class OtherEditSerializer(serializers.ModelSerializer):
    cot_updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    cot_parent_id = serializers.IntegerField(required=False)
    mmo_module = serializers.CharField(required=False)
    class Meta:
        model = TCoreOther
        fields = ('id', 'cot_name', 'description', 'cot_parent_id', 'cot_updated_by', 'mmo_module')

    def update(self, instance, validated_data):
        try:
            print('validated_data',validated_data)
            cot_updated_by = validated_data.get('cot_updated_by')
            cot_parent_id = validated_data.pop('cot_parent_id') if 'cot_parent_id' in validated_data else 0
            with transaction.atomic():
                instance.cot_name = validated_data.get('cot_name')
                instance.description = validated_data.get('description')
                instance.cot_parent_id = cot_parent_id
                instance.cot_updated_by = cot_updated_by
                instance.save()

                tMasterModuleOther = TMasterModuleOther.objects.filter(
                    mmo_other=instance.id)
                print('tMasterModuleOther',tMasterModuleOther)
                if tMasterModuleOther:
                    tMasterModuleOther.delete()

                master_module = TMasterModuleOther.objects.create(
                    mmo_other = instance,
                    mmo_module_id = validated_data.get('mmo_module'),
                )
                #print('master_module', master_module)
                response = {
                    'id': instance.id,
                    'cot_name': instance.cot_name,
                    'description': instance.description,
                    'mmo_module':master_module.mmo_module,
                    'cot_parent_id':instance.cot_parent_id
                }
                return response
        except Exception as e:
            raise e

class OtherDeleteSerializer(serializers.ModelSerializer):
    cot_updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault(),required=False)
    parent_id = serializers.IntegerField(required=False)
    mmo_module = serializers.CharField(required=False)
    is_deleted = serializers.CharField(required=False)
    class Meta:
        model = TCoreOther
        fields = ('id', 'cot_name', 'description', 'parent_id', 'cot_updated_by',
                  'mmo_module','updated_by','is_deleted')

    def update(self, instance, validated_data):
        try:
            cot_updated_by = validated_data.get('cot_updated_by')
            updated_by = validated_data.get('updated_by')
            instance.cot_is_deleted = True
            instance.cot_updated_by = cot_updated_by
            instance.save()
            #print('instance',instance)
            module_other = TMasterModuleOther.objects.filter(mmo_other=instance)
            #print('ModuleOther',module_other.query)
            for e_module_other in module_other:
                e_module_other.is_deleted = True
                e_module_other.updated_by = updated_by
                e_module_other.save()
            return instance
        except Exception as e:
            raise e

#:::::::::::::::::::::: T CORE DEPARTMENT:::::::::::::::::::::::::::#
class CoreDepartmentAddSerializer(serializers.ModelSerializer):
    cd_created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = TCoreDepartment
        fields = ('id', 'cd_name', 'cd_parent_id','cd_is_deleted', 'cd_created_by', 'cd_created_at', 'cd_updated_at', 'cd_updated_by', 'cd_deleted_at', 'cd_deleted_by')

class CoreDepartmentEditSerializer(serializers.ModelSerializer):
    cd_updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = TCoreDepartment
        fields = ('id', 'cd_name','cd_parent_id','cd_is_deleted', 'cd_created_by', 'cd_created_at', 'cd_updated_at', 'cd_updated_by', 'cd_deleted_at', 'cd_deleted_by')

class CoreDepartmentDeleteSerializer(serializers.ModelSerializer):
    cd_deleted_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = TCoreDepartment
        fields = '__all__'
    def update(self, instance, validated_data):
        instance.cd_is_deleted=True
        instance.cd_deleted_by = validated_data.get('cd_deleted_by')
        instance.save()
        return instance

#:::::::::::::::::::::: T CORE DESIGNATION:::::::::::::::::::::::::::#
class CoreDesignationAddSerializer(serializers.ModelSerializer):
    cod_created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    mmr_module = serializers.SerializerMethodField()
    def get_mmr_module(self,TCoreDesignation):
        module_details = TMasterModuleRoleUser.objects.filter(mmr_designation_id=TCoreDesignation.id)[:0]  
        if module_details:
            return str(TMasterModuleRoleUser.objects.only('mmr_module').get(mmr_designation_id=TCoreDesignation.id).mmr_module)    
        else:
            return None

    class Meta:
        model = TCoreDesignation
        fields = ('id', 'cod_name', 'cod_is_deleted', 'cod_created_by', 'cod_created_at', 
        'cod_updated_at', 'cod_updated_by', 'cod_deleted_at', 'cod_deleted_by','mmr_module')

class CoreDesignationEditSerializer(serializers.ModelSerializer):
    cod_updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = TCoreDesignation
        fields = ('id', 'cod_name', 'cod_is_deleted', 'cod_created_by', 'cod_created_at', 'cod_updated_at', 'cod_updated_by', 'cod_deleted_at', 'cod_deleted_by')

class CoreDesignationDeleteSerializer(serializers.ModelSerializer):
    cod_deleted_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = TCoreDesignation
        fields = '__all__'
    def update(self, instance, validated_data):
        instance.cod_is_deleted=True
        instance.cod_deleted_by = validated_data.get('cod_deleted_by')
        instance.save()
        return instance

#:::::::::::::::::::::: T CORE COMPANY :::::::::::::::::::::::::::::#
class CoreCompanyAddSerializer(serializers.ModelSerializer):
    coc_created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = TCoreCompany
        fields = ('__all__')

class CoreCompanyEditSerializer(serializers.ModelSerializer):
    coc_updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = TCoreCompany
        fields = ('__all__')

class CoreCompanyDeleteSerializer(serializers.ModelSerializer):
    coc_deleted_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = TCoreCompany
        fields = '__all__'
    def update(self, instance, validated_data):
        instance.coc_is_deleted=True
        instance.coc_deleted_by = validated_data.get('coc_deleted_by')
        instance.save()
        return instance

class OtherAddNewSerializer(serializers.ModelSerializer):
    cot_created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    cot_parent_id = serializers.IntegerField(required=False)
    mmo_module = serializers.CharField(required=False)
    class Meta:
        model = TCoreOther
        fields = ('id','cot_name','description','cot_parent_id','cot_created_by','mmo_module')
    def create(self, validated_data):
        try:
            cot_created_by = validated_data.get('cot_created_by')
            cot_parent_id = validated_data.pop('cot_parent_id') if 'cot_parent_id' in validated_data else 0
            with transaction.atomic():
                cot_save_id = TCoreOther.objects.create(
                    cot_name=validated_data.get('cot_name'),
                    description=validated_data.get('description'),
                    cot_parent_id = cot_parent_id,
                    cot_created_by=cot_created_by,
                )
                module_id = TCoreModule.objects.only('id').get(cm_name=validated_data.get('mmo_module')).id
                print('module_id',module_id)
                master_module = TMasterModuleOther.objects.create(
                    mmo_other = cot_save_id,
                    mmo_module_id = module_id,

                )
                response = {
                    'id': cot_save_id.id,
                    'cot_name': cot_save_id.cot_name,
                    'description': cot_save_id.description,
                    'mmo_module':master_module.mmo_module,
                    'cot_parent_id':cot_save_id.cot_parent_id
                }
                return response
        except Exception as e:
            raise e

class OtherListWithPermissionByRoleModuleNameSerializer(serializers.ModelSerializer):
    mor_permissions_n = serializers.IntegerField(required=False)
    class Meta:
        model = TMasterOtherRole
        fields = ('id','mor_other','mor_module','mor_role','mor_permissions','mor_permissions_n')

class OtherEditNewSerializer(serializers.ModelSerializer):
    cot_updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    cot_parent_id = serializers.IntegerField(required=False)
    class Meta:
        model = TCoreOther
        fields = ('id', 'cot_name', 'description', 'cot_parent_id', 'cot_updated_by')

    def update(self, instance, validated_data):
        try:
            cot_updated_by = validated_data.get('cot_updated_by')
            with transaction.atomic():
                instance.cot_name = validated_data.get('cot_name')
                instance.description = validated_data.get('description')
                instance.cot_updated_by = cot_updated_by
                instance.save()
                response = {
                    'id': instance.id,
                    'cot_name': instance.cot_name,
                    'description': instance.description,
                    'cot_parent_id':instance.cot_parent_id
                }
                return response
        except Exception as e:
            raise e

class OtherListWithPermissionByUserModuleNameSerializer(serializers.ModelSerializer):
    mou_permissions_n = serializers.IntegerField(required=False)
    mor_other = serializers.IntegerField(required=False)
    mor_module = serializers.IntegerField(required=False)
    mor_permissions = serializers.IntegerField(required=False)
    mor_permissions_n = serializers.IntegerField(required=False)

    class Meta:
        model = TMasterOtherUser
        fields = ('id','mou_other','mou_module','mou_permissions',
        'mou_permissions_n','mor_other','mor_module','mor_permissions','mor_permissions_n')

class StatesListAddSerializer(serializers.ModelSerializer):
    cs_created_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = TCoreState
        fields = ('id','cs_state_name','cs_tin_number','cs_state_code','cs_status','cs_created_by')

class StatesListEditSerializer(serializers.ModelSerializer):
    cs_updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = TCoreState
        fields = ('id','cs_state_name','cs_tin_number','cs_state_code','cs_status','cs_updated_by')

class StatesListDeleteSerializer(serializers.ModelSerializer):
    cs_updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = TCoreState
        fields = '__all__'
    def update(self, instance, validated_data):
        instance.cs_is_deleted=True
        instance.cs_status=False
        instance.cs_updated_by = validated_data.get('cs_updated_by')
        instance.save()
        return instance
#:::::::::::::::::::::: T CORE SALARY TYPE:::::::::::::::::::::::::::#
class CoreSalaryTypeAddSerializer(serializers.ModelSerializer):
    st_created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = TCoreSalaryType
        fields = '__all__'


class CoreSalaryTypeEditSerializer(serializers.ModelSerializer):
    st_updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = TCoreSalaryType
        fields = '__all__'

class CoreSalaryTypeDeleteSerializer(serializers.ModelSerializer):
    st_updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    st_deleted_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = TCoreSalaryType
        fields = '__all__'
    def update(self, instance, validated_data):
        instance.is_deleted=True
        instance.st_updated_by = validated_data.get('st_updated_by')
        instance.st_deleted_by = validated_data.get('st_deleted_by')
        instance.save()
        return instance
