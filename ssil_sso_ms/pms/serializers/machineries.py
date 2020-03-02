from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from pms.models import *
from django.contrib.auth.models import *
import time
from django.db import transaction, IntegrityError
from drf_extra_fields.fields import Base64ImageField
import os
from rest_framework.exceptions import APIException
import datetime
from core.models import TCoreUnit
from rest_framework.response import Response
from pms.custom_filter import custom_filter
import pandas as pd
import numpy as np
import xlrd
from pms.custom_delete import *
from django.db.models import Q
import re

#:::::::::::::::::  MECHINE WORKING CATEGORY :::::::::::#
class MachineriesWorkingCategoryAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsMachineriesWorkingCategory
        fields = ('id', 'name', 'created_by', 'owned_by')
class MachineriesWorkingCategoryEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsMachineriesWorkingCategory
        fields = ('id', 'name', 'updated_by')
class MachineriesWorkingCategoryDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsMachineriesWorkingCategory
        fields = '__all__'

    def update(self, instance, validated_data):
        instance.is_deleted = True
        instance.updated_by = validated_data.get('updated_by')
        instance.save()
        return instance

#:::::::::::::::::  MECHINARY MASTER :::::::::::::::#
class MachineriesAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    rental_details=serializers.DictField(required=False)
    owner_details=serializers.DictField(required=False)
    owner_emi_details=serializers.DictField(required=False)
    contract_details =serializers.DictField(required=False)
    lease_details=serializers.DictField(required=False)
    code = serializers.CharField(required=False,allow_null=True)
    class Meta:
        model = PmsMachineries

        fields = (
        'id','code','equipment_name', 'equipment_category', 'equipment_type', 'owner_type',
        'equipment_make',
        'equipment_model_no', 'equipment_registration_no',
        'equipment_chassis_serial_no',
        'equipment_engine_serial_no', 'equipment_power', 'measurement_by',
        'measurement_quantity',
        'fuel_consumption', 'remarks', 'created_by', 'owned_by', 'rental_details',
        'owner_details',
        'owner_emi_details', 'contract_details','lease_details')

    def create(self, validated_data):
        try:
            #print('validated_data',validated_data)
            owner = validated_data.pop('owner_details') if 'owner_details' in validated_data else ""
            if 'is_emi_available' in owner and owner["is_emi_available"]:
                owner_emi = owner['owner_emi_details']
            contract = validated_data.pop('contract_details') if 'contract_details' in validated_data else ""
            lease=validated_data.pop('lease_details') if 'lease_details' in validated_data else ""
            rent = validated_data.pop('rental_details') if 'rental_details' in validated_data else ""
            owner_type = validated_data.get('owner_type')
            owned_by = validated_data.get('owned_by')
            created_by = validated_data.get('created_by')

            #print('owner["is_emi_available"]',owner["is_emi_available"])
            with transaction.atomic():
                machinary = PmsMachineries.objects.create(**validated_data)
                response = {
                    'id': machinary.id,
                    'equipment_name': machinary.equipment_name,
                    'equipment_category': machinary.equipment_category,
                    'equipment_type': machinary.equipment_type,
                    'owner_type': machinary.owner_type,
                    'equipment_make': machinary.equipment_make,
                    'equipment_model_no': machinary.equipment_model_no,
                    'equipment_registration_no': machinary.equipment_registration_no,
                    'equipment_chassis_serial_no': machinary.equipment_chassis_serial_no,
                    'equipment_engine_serial_no': machinary.equipment_engine_serial_no,
                    'equipment_power': machinary.equipment_power,
                    'measurement_by': machinary.measurement_by,
                    'measurement_quantity': machinary.measurement_quantity,
                    'fuel_consumption': machinary.fuel_consumption,
                    'remarks': machinary.remarks
                    }

                if owner_type == 1:
                    vendor=None if rent['vendor'] == ('null' or '') else rent['vendor']
                    rent_amount='' if rent['rent_amount'] == ('null' or '') else rent['rent_amount']
                    type_of_rent=None if rent['type_of_rent'] == ('null' or '') else rent['type_of_rent']
                    machinary_rental_details = PmsMachinaryRentedDetails.objects.create(
                                                                        equipment=machinary,
                                                                        vendor_id=vendor,
                                                                        rent_amount=rent_amount,
                                                                        type_of_rent_id=type_of_rent,
                                                                        owned_by = owned_by,
                                                                        created_by=created_by
                                                                        )
                    print('machinary_rental_details',machinary_rental_details)
                    rental_details_dict = {}
                    rental_details_dict["id"]=machinary_rental_details.id
                    rental_details_dict["equipment"]=machinary_rental_details.equipment.id
                    rental_details_dict["vendor"]=machinary_rental_details.vendor.id if machinary_rental_details.vendor else None
                    rental_details_dict["type_of_rent"]=machinary_rental_details.type_of_rent.id if machinary_rental_details.type_of_rent else None
                    rental_details_dict["rent_amount"]=machinary_rental_details.rent_amount
                    response["rental_details"] = rental_details_dict
                elif owner_type == 2:
                    # purchase_date=None if owner['purchase_date'] == ('null' or '') else datetime.datetime.strptime(owner['purchase_date'],"%Y-%m-%dT%H:%M:%S.%fZ")
                    if owner['purchase_date']:
                        purchase_date=datetime.datetime.strptime(owner['purchase_date'],"%Y-%m-%dT%H:%M:%S.%fZ")
                        print('purchase_date',purchase_date)
                    elif owner['purchase_date'] == '':
                        purchase_date=None
                    else:
                        purchase_date=None
                    price=None if owner['price'] == ('null' or '') else owner['price']
                    is_emi_available=''if owner['is_emi_available'] == ('null' or '') else owner['is_emi_available']
                    machinary_owner_details=PmsMachinaryOwnerDetails.objects.create(
                                                                    equipment=machinary,
                                                                    purchase_date=purchase_date,
                                                                    price = price,
                                                                    is_emi_available=is_emi_available,
                                                                    owned_by=owned_by,
                                                                    created_by=created_by
                                                                    )
                    owner_details_dict = {}
                    owner_details_dict["id"] = machinary_owner_details.id
                    owner_details_dict["equipment"] = machinary_owner_details.equipment.id if machinary_owner_details.equipment else None
                    owner_details_dict["purchase_date"] = machinary_owner_details.purchase_date
                    owner_details_dict["price"] = machinary_owner_details.price
                    owner_details_dict["is_emi_available"] = machinary_owner_details.is_emi_available

                    if 'is_emi_available' in owner and owner["is_emi_available"]:
                        amount=''if owner_emi['amount'] == ('null' or '') else owner_emi['amount']
                        # start_date=None if owner_emi['start_date'] == ('null' or '') else datetime.datetime.strptime(owner_emi['start_date'],"%Y-%m-%dT%H:%M:%S.%fZ")
                        if owner_emi['start_date']:
                            start_date=datetime.datetime.strptime(owner_emi['start_date'],"%Y-%m-%dT%H:%M:%S.%fZ")
                            print('start_date',start_date)
                        elif owner_emi['start_date'] == '':
                            start_date=None
                        else:
                            start_date=None

                        no_of_total_installment='' if owner_emi['no_of_total_installment'] == ('null' or '') else owner_emi['no_of_total_installment']
                        machinary_owner_emi_details=PmsMachinaryOwnerEmiDetails.objects.create(
                                                equipment=machinary,
                                                equipment_owner_details=machinary_owner_details,
                                                amount=amount,
                                                start_date=start_date,
                                                no_of_total_installment=no_of_total_installment,
                                                owned_by=owned_by,
                                                created_by=created_by
                                                )
                        owner_emi_details = {}
                        owner_emi_details["id"] = machinary_owner_emi_details.id
                        owner_emi_details["equipment"] = machinary_owner_emi_details.equipment.id if machinary_owner_emi_details.equipment else None
                        owner_emi_details["equipment_owner_details"] = machinary_owner_emi_details.equipment_owner_details.id if machinary_owner_emi_details.equipment_owner_details else None
                        owner_emi_details["amount"] = machinary_owner_emi_details.amount
                        owner_emi_details["start_date"] = machinary_owner_emi_details.start_date
                        owner_emi_details["no_of_total_installment"] = machinary_owner_emi_details.no_of_total_installment
                        #owner_emi_details["no_of_remain_installment"] = machinary_owner_emi_details.no_of_remain_installment
                        if owner_emi_details:
                            owner_details_dict["owner_emi_details"] = owner_emi_details
                    response["owner_details"] = owner_details_dict
                elif owner_type == 3:
                    # print("contract['contractor_id']: ", contract['contractor'])
                    contractor=None if contract['contractor'] == ('null' or '') else contract['contractor']
                    machinary_contract_details = PmsMachinaryContractDetails.objects.create(
                                                                equipment=machinary,
                                                                contractor_id=contractor,
                                                                owned_by=owned_by,
                                                                created_by=created_by
                                                            )
                    # print('query: ', machinary_contract_details.query)
                    contract_details = {}
                    contract_details["id"] = machinary_contract_details.id
                    contract_details["equipment"] = machinary_contract_details.equipment.id if  machinary_contract_details.equipment else None
                    contract_details["contractor"] = machinary_contract_details.contractor.id if machinary_contract_details.contractor else None

                    response["contract_details"] = contract_details
                elif owner_type == 4:
                    vendor=None if lease['vendor'] == ('null' or '') else lease['vendor']
                    lease_amount=None if lease['lease_amount'] == ('null' or '') else lease['lease_amount']
                    # start_date=None if lease['start_date'] == ('null' or '') else datetime.datetime.strptime(owner['start_date'],"%Y-%m-%dT%H:%M:%S.%fZ")  
                    if lease['start_date']:
                        start_date=datetime.datetime.strptime(lease['start_date'],"%Y-%m-%dT%H:%M:%S.%fZ")
                        print('start_date',start_date)
                    elif lease['start_date'] == '':
                        start_date=None
                    else:
                        start_date=None               
                    lease_period=None if lease['lease_period'] == ('null' or '') else lease['lease_period']
                    machinary_lease_details=PmsMachinaryLeaseDetails.objects.create(equipment=machinary,
                                                                                    vendor_id=vendor,
                                                                                    lease_amount=lease_amount,
                                                                                    start_date=start_date,
                                                                                    lease_period=lease_period,
                                                                                    owned_by=owned_by,
                                                                                    created_by=created_by
                                                                                    )
                    lease_details={}
                    lease_details["id"] = machinary_lease_details.id
                    lease_details["vendor"] = machinary_lease_details.vendor.id if machinary_lease_details.vendor else None
                    lease_details["lease_amount"] = machinary_lease_details.lease_amount 
                    lease_details["start_date"] = machinary_lease_details.start_date
                    lease_details["lease_period"] = machinary_lease_details.lease_period
                    response["lease_details"] = lease_details
                else:
                    pass
            return response
        except Exception as e:
            raise e
class MachineriesEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    equipment_category_details = serializers.DictField(required=False,allow_null=True)
    document_details = serializers.ListField(required=False,allow_null=True)
    rental_details = serializers.DictField(required=False,allow_null=True)
    lease_details=serializers.DictField(required=False,allow_null=True)
    owner_details = serializers.DictField(required=False,allow_null=True)
    owner_emi_details = serializers.DictField(required=False,allow_null=True)
    contract_details = serializers.DictField(required=False,allow_null=True)
    previous_owner_type = serializers.IntegerField(required=False,allow_null=True)
    prev_emi_av = serializers.CharField(required=False,allow_null=True)
    code = serializers.CharField(required=False,allow_null=True)
    class Meta:
        model=PmsMachineries
        fields=('id','code','equipment_name', 'equipment_category', 'equipment_type', 'owner_type', 'equipment_make',
                'equipment_model_no', 'equipment_registration_no', 'equipment_chassis_serial_no',
                'equipment_engine_serial_no', 'equipment_power', 'measurement_by', 'measurement_quantity',
                'fuel_consumption', 'remarks', 'updated_by',
                'contract_details','owner_details','rental_details','owner_emi_details','lease_details',
                'equipment_category_details','document_details','previous_owner_type','prev_emi_av')

    def update(self, instance, validated_data):
        owner = validated_data.pop('owner_details') if 'owner_details' in validated_data else ""
        if 'is_emi_available' in owner and owner["is_emi_available"]:
            owner_emi = owner['owner_emi_details']
            # is_emi_available = True
        # else:
        #     is_emi_available = False

        contract = validated_data.pop('contract_details') if 'contract_details' in validated_data else ""
        rent = validated_data.pop('rental_details') if 'rental_details' in validated_data else ""
        lease=validated_data.pop('lease_details') if 'lease_details' in validated_data else ""
        owner_type = validated_data.get('owner_type')
        previous_owner_type = validated_data.pop('previous_owner_type')

        # instance.code = validated_data.get('code', instance.code)
        instance.code = validated_data.get('code', instance.code)
        instance.equipment_name = validated_data.get("equipment_name",instance.equipment_name)
        instance.equipment_category = validated_data.get("equipment_category",instance.equipment_category)
        instance.equipment_type = validated_data.get("equipment_type",instance.equipment_type)
        instance.owner_type = validated_data.get("owner_type",instance.owner_type)
        instance.equipment_make = validated_data.get("equipment_make",instance.equipment_make)
        instance.equipment_model_no = validated_data.get("equipment_model_no",instance.equipment_model_no)
        instance.equipment_registration_no = validated_data.get("equipment_registration_no", instance.equipment_registration_no)
        instance.equipment_chassis_serial_no = validated_data.get("equipment_chassis_serial_no", instance.equipment_chassis_serial_no)
        instance.equipment_engine_serial_no = validated_data.get("equipment_engine_serial_no", instance.equipment_engine_serial_no)
        instance.equipment_power = validated_data.get("equipment_power", instance.equipment_power)
        instance.measurement_by = validated_data.get("measurement_by", instance.measurement_by)
        instance.measurement_quantity = validated_data.get("measurement_quantity", instance.measurement_quantity)
        instance.fuel_consumption = validated_data.get("fuel_consumption", instance.fuel_consumption)
        instance.remarks = validated_data.get("remarks", instance.remarks)
        instance.updated_by = validated_data.get("updated_by", instance.updated_by)
        instance.save()
        response = {
            'id': instance.id,
            'code':instance.code,
            'equipment_name': instance.equipment_name,
            'equipment_category': instance.equipment_category,
            'equipment_type': instance.equipment_type,
            'owner_type': instance.owner_type,
            'equipment_make': instance.equipment_make,
            'equipment_model_no': instance.equipment_model_no,
            'equipment_registration_no': instance.equipment_registration_no,
            'equipment_chassis_serial_no': instance.equipment_chassis_serial_no,
            'equipment_engine_serial_no': instance.equipment_engine_serial_no,
            'equipment_power': instance.equipment_power,
            'measurement_by': instance.measurement_by,
            'measurement_quantity': instance.measurement_quantity,
            'fuel_consumption': instance.fuel_consumption,
            'remarks': instance.remarks
        }

        if previous_owner_type == 1:
            PmsMachinaryRentedDetails.objects.filter(equipment=instance).delete()
        elif previous_owner_type == 2:
            PmsMachinaryOwnerDetails.objects.filter(equipment=instance).delete()
        elif  previous_owner_type == 3:
            PmsMachinaryContractDetails.objects.filter(equipment=instance).delete()
        else:
            PmsMachinaryLeaseDetails.objects.filter(equipment=instance).delete()

        if owner_type == 1:
            vendor =None if rent['vendor'] == ('null' or '') else rent['vendor']
            rent_amount ='' if rent['rent_amount'] == ('null' or '') else rent['rent_amount']
            type_of_rent =None if rent['type_of_rent'] == ('null' or '') else rent['type_of_rent']
            machinary_rental_details = PmsMachinaryRentedDetails.objects.create(
                equipment=instance,
                vendor_id=vendor,
                rent_amount=rent_amount,
                type_of_rent_id=type_of_rent,
                owned_by=instance.updated_by,
                created_by=instance.updated_by
            )
            print('machinary_rental_details', machinary_rental_details)
            rental_details_dict = {}
            rental_details_dict["id"] = machinary_rental_details.id
            rental_details_dict["equipment"] = machinary_rental_details.equipment.id if machinary_rental_details.equipment else None
            rental_details_dict["vendor"] = machinary_rental_details.vendor.id if machinary_rental_details.vendor else None
            rental_details_dict["type_of_rent"] = machinary_rental_details.type_of_rent.id if machinary_rental_details.type_of_rent else None
            rental_details_dict["rent_amount"] = machinary_rental_details.rent_amount
            response["rental_details"] = rental_details_dict
        elif owner_type == 2:
            # purchase_date=None if owner['purchase_date'] == ('null' or '') else datetime.datetime.strptime(owner['purchase_date'],"%Y-%m-%dT%H:%M:%S.%fZ")
            if owner['purchase_date']:
                purchase_date=datetime.datetime.strptime(owner['purchase_date'],"%Y-%m-%dT%H:%M:%S.%fZ")
                print('purchase_date',purchase_date)
            elif owner['purchase_date'] == '':
                purchase_date=None
            else:
                purchase_date=None

            if owner['price']:
                price=owner['price']
            elif owner['price'] == '':
                price=None
            else:
                price=None
            # price ='' if owner['price'] == ('null' or '') else owner['price']
            is_emi_available=''if owner['is_emi_available'] == ('null' or '') else owner['is_emi_available']
            machinary_owner_details = PmsMachinaryOwnerDetails.objects.create(
                equipment=instance,
                purchase_date=purchase_date,
                price=price,
                is_emi_available=is_emi_available,
                owned_by=instance.updated_by,
                created_by=instance.updated_by
            )
            owner_details_dict = {}
            owner_details_dict["id"] = machinary_owner_details.id
            owner_details_dict["equipment"] = machinary_owner_details.equipment.id if machinary_owner_details.equipment else None
            owner_details_dict["purchase_date"] = machinary_owner_details.purchase_date
            owner_details_dict["price"] = machinary_owner_details.price
            owner_details_dict["is_emi_available"] = machinary_owner_details.is_emi_available
            if owner!="" and owner["prev_emi_av"] == "yes":
                PmsMachinaryOwnerEmiDetails.objects.filter(equipment=instance).delete()
                if 'is_emi_available' in owner and owner["is_emi_available"]:
                    # amount=''if owner_emi['amount'] == ('null' or '') else owner_emi['amount']
                    if owner_emi['amount']:
                        amount=owner_emi['amount']
                        print('amount',amount)
                    elif owner_emi['amount'] == '':
                        amount=None
                    else:
                        amount=None
                        print('amount',amount)
                    # start_date=None if owner_emi['start_date'] == ('null' or '') else datetime.datetime.strptime(owner_emi['start_date'],"%Y-%m-%dT%H:%M:%S.%fZ")
                    if owner_emi['start_date']:
                        start_date=datetime.datetime.strptime(owner_emi['start_date'],"%Y-%m-%dT%H:%M:%S.%fZ")
                        print('start_date',start_date)
                    elif owner_emi['start_date'] == '':
                        start_date=None
                    else:
                        start_date=None
                        print('start_date',start_date)
                    no_of_total_installment='' if owner_emi['no_of_total_installment'] == ('null' or '') else owner_emi['no_of_total_installment']
                    machinary_owner_emi_details = PmsMachinaryOwnerEmiDetails.objects.create(
                        equipment=instance,
                        equipment_owner_details=machinary_owner_details,
                        amount=amount,
                        start_date=start_date,
                        no_of_total_installment=no_of_total_installment,
                        # no_of_remain_installment=owner_emi['purchase_date'],
                        owned_by=instance.updated_by,
                        created_by=instance.updated_by,
                    )
                    owner_emi_details = {}
                    owner_emi_details["id"] = machinary_owner_emi_details.id
                    owner_emi_details["equipment"] = machinary_owner_emi_details.equipment.id if machinary_owner_emi_details.equipment else None
                    owner_emi_details["equipment_owner_details"] = machinary_owner_emi_details.equipment_owner_details.id if machinary_owner_emi_details.equipment_owner_details else None
                    owner_emi_details["amount"] = machinary_owner_emi_details.amount
                    owner_emi_details["start_date"] = machinary_owner_emi_details.start_date
                    owner_emi_details["no_of_total_installment"] = machinary_owner_emi_details.no_of_total_installment
                    # owner_emi_details["no_of_remain_installment"] = machinary_owner_emi_details.no_of_remain_installment
                    if owner_emi_details:
                        owner_details_dict["owner_emi_details"] = owner_emi_details
                response["owner_details"] = owner_details_dict
            else:
                if 'is_emi_available' in owner and owner["is_emi_available"]:
                    # amount=''if owner_emi['amount'] == ('null' or '') else owner_emi['amount']
                    if owner_emi['amount']:
                        amount=owner_emi['amount']
                        print('amount',amount)
                    elif owner_emi['amount'] == '':
                        amount=None
                    else:
                        amount=None
                        print('amount',amount)
                    # start_date=None if owner_emi['start_date'] == ('null' or '') else datetime.datetime.strptime(owner_emi['start_date'],"%Y-%m-%dT%H:%M:%S.%fZ")
                    if owner_emi['start_date']:
                        start_date=datetime.datetime.strptime(owner_emi['start_date'],"%Y-%m-%dT%H:%M:%S.%fZ")
                        print('start_date',start_date)
                    elif owner_emi['start_date'] == '':
                        start_date=None
                    else:
                        start_date=None
                        print('start_date',start_date)
                    no_of_total_installment='' if owner_emi['no_of_total_installment'] == ('null' or '') else owner_emi['no_of_total_installment']
                    machinary_owner_emi_details = PmsMachinaryOwnerEmiDetails.objects.create(
                        equipment=instance,
                        equipment_owner_details=machinary_owner_details,
                        amount=amount,
                        start_date=start_date,
                        no_of_total_installment=no_of_total_installment,
                        owned_by=instance.updated_by,
                        created_by=instance.updated_by
                    )
                    owner_emi_details = {}
                    owner_emi_details["id"] = machinary_owner_emi_details.id
                    owner_emi_details["equipment"] = machinary_owner_emi_details.equipment.id if machinary_owner_emi_details.equipment else None
                    owner_emi_details["equipment_owner_details"] = machinary_owner_emi_details.equipment_owner_details.id if machinary_owner_emi_details.equipment_owner_details else None
                    owner_emi_details["amount"] = machinary_owner_emi_details.amount
                    owner_emi_details["start_date"] = machinary_owner_emi_details.start_date
                    owner_emi_details["no_of_total_installment"] = machinary_owner_emi_details.no_of_total_installment
                    # owner_emi_details["no_of_remain_installment"] = machinary_owner_emi_details.no_of_remain_installment
                    if owner_emi_details:
                        owner_details_dict["owner_emi_details"] = owner_emi_details
                response["owner_details"] = owner_details_dict
        elif owner_type == 3:
            contractor=None if contract == "" else contract['contractor']
            machinary_contract_details = PmsMachinaryContractDetails.objects.create(
                equipment=instance,
                contractor_id=contractor,
                owned_by=instance.updated_by,
                created_by=instance.updated_by
            )
            # print('query: ', machinary_contract_details.query)
            contract_details = {}
            contract_details["id"] = machinary_contract_details.id
            contract_details["equipment"] = machinary_contract_details.equipment.id if machinary_contract_details.equipment else None
            contract_details["contractor"] = machinary_contract_details.contractor.id if  machinary_contract_details.contractor else None
            response["contract_details"] = contract_details
        else:
            print("lease",lease)
            if lease!="":
                vendor = lease['vendor'] if "vendor" in  lease.keys() else None
                lease_amount = lease['lease_amount'] if "lease_amount" in  lease.keys() else None
                start_date = datetime.datetime.strptime(lease['start_date'],"%Y-%m-%dT%H:%M:%S.%fZ") if "start_date" in lease.keys() and lease['start_date'] is not None else None                 
                lease_period = lease['lease_period'] if "lease_period" in  lease.keys() else None
                machinary_lease_details=PmsMachinaryLeaseDetails.objects.create(equipment=instance,
                                                                                        vendor_id=vendor,
                                                                                        lease_amount=lease_amount,
                                                                                        start_date=start_date,
                                                                                        lease_period=lease_period,
                                                                                        owned_by=instance.updated_by,
                                                                                        created_by=instance.updated_by
                                                                                        )
                lease_details={}
                lease_details["id"] = machinary_lease_details.id
                lease_details["vendor"] = machinary_lease_details.vendor.id if  machinary_lease_details.vendor else None
                lease_details["lease_amount"] = machinary_lease_details.lease_amount
                lease_details["start_date"] = machinary_lease_details.start_date
                lease_details["lease_period"] = machinary_lease_details.lease_period
                response["lease_details"] = lease_details


        return response
class MachineriesListDetailsSerializer(serializers.ModelSerializer):
    equipment_category_details = serializers.SerializerMethodField()
    document_details = serializers.SerializerMethodField(required=False)
    owner_emi_details = serializers.SerializerMethodField(required=False)
    rented_details = serializers.SerializerMethodField(required=False)
    contractor_details = serializers.SerializerMethodField(required=False)
    lease_details = serializers.SerializerMethodField(required=False)
    equipment_type_name= serializers.SerializerMethodField(required=False)
    # machinery_filter = serializers.SerializerMethodField(required=False)
    # def get_machinery_filter(self,PmsProjectsMachinaryMapping):
    def get_equipment_type_name(self,PmsMachineries):
        if PmsMachineries.equipment_type:
            return PmsMachineryType.objects.only('name').get(id=PmsMachineries.equipment_type.id).name

    def get_owner_emi_details(self,PmsMachineries):
        if PmsMachineries.id:
            owner_det = {}
            owner_details=PmsMachinaryOwnerDetails.objects.filter(equipment=PmsMachineries.id)
            if owner_details:
                for o_d in owner_details:
                    owner_det={
                        'id':o_d.id,
                        'purchase_date':o_d.purchase_date,
                        'price':o_d.price,
                        'is_emi_available':o_d.is_emi_available,
                    }
                    if o_d.is_emi_available is True:
                        emi_details=PmsMachinaryOwnerEmiDetails.objects.filter(equipment=PmsMachineries.id,equipment_owner_details=o_d.id)
                        if emi_details:
                            for e_d in emi_details:
                                emi_det={
                                    'id':e_d.id,
                                    'amount':e_d.amount,
                                    'start_date':e_d.start_date,
                                    'no_of_total_installment':e_d.no_of_total_installment
                                }
                            owner_det['emi_details']=emi_det
                return owner_det
    def get_rented_details(self,PmsMachineries):
        if PmsMachineries.id:
            rented_details=PmsMachinaryRentedDetails.objects.filter(equipment=PmsMachineries.id)
            rental_dict={}
            for r_d in rented_details:
                vendor=r_d.vendor.id if r_d.vendor else None
                vendor_name=r_d.vendor.contact_person_name if r_d.vendor else None
                type_of_rent=r_d.type_of_rent.name if r_d.type_of_rent else None
                rental_dict={
                    'id':r_d.id,
                    'rent_amount':r_d.rent_amount,
                    'type_of_rent':type_of_rent,
                    'vendor':vendor,
                    'vendor_name':vendor_name,

                }
            return rental_dict
    def get_contractor_details(self,PmsMachineries):
        if PmsMachineries.id:
            contractor_details=PmsMachinaryContractDetails.objects.filter(equipment=PmsMachineries.id)
            con_dict={}

            for c_d in contractor_details:
                contractor=c_d.contractor.id if c_d.contractor else None
                contractor_name=c_d.contractor.contact_person_name if c_d.contractor else None
                con_dict={
                    'id':c_d.id,
                    'contractor':contractor,
                    'contractor_name':contractor_name
                }
            return con_dict
    def get_lease_details(self,PmsMachineries):
        if PmsMachineries.id:
            lease_details=PmsMachinaryLeaseDetails.objects.filter(equipment=PmsMachineries.id)
            lease_dict={}
            for l_d in lease_details:
                vendor=l_d.vendor.id if l_d.vendor else None
                vendor_name=l_d.vendor.contact_person_name if l_d.vendor else None
                lease_dict={
                    'id':l_d.id,
                    'vendor':vendor,
                    'vendor_name':vendor_name,
                    'lease_amount':l_d.lease_amount,
                    'start_date':l_d.start_date,
                    'lease_period':l_d.lease_period
                }
            return lease_dict

    def get_equipment_category_details(self, PmsMachineries):
        if PmsMachineries.equipment_category:
            equipment = PmsMachineriesWorkingCategory.objects.filter(id=PmsMachineries.equipment_category.id)

            serializer = MachineriesWorkingCategoryAddSerializer(instance=equipment, many=True)
            return serializer.data[0]
    def get_document_details(self, PmsMachineries):
        if PmsMachineries:
            document = PmsMachineriesDetailsDocument.objects.filter(equipment=PmsMachineries, is_deleted=False)
            request = self.context.get('request')
            response_list = []
            for each_document in document:
                file_url = request.build_absolute_uri(each_document.document.url)

                owned_by = str(each_document.owned_by) if each_document.owned_by else ''
                created_by = str(each_document.created_by) if each_document.created_by else ''
                each_data = {
                    "id": int(each_document.id),
                    "equipment": each_document.equipment.id,
                    "document_name": each_document.document_name,
                    "document": file_url,
                    "created_by": created_by,
                    "owned_by": owned_by
                }
                response_list.append(each_data)
            return response_list
    class Meta:
        model = PmsMachineries
        fields = ('id', 'equipment_name', 'equipment_category', 'equipment_category_details', 'equipment_type',
                  'owner_type', 'equipment_make','equipment_type_name',
                  'equipment_model_no', 'equipment_registration_no',
                  'equipment_chassis_serial_no',
                  'equipment_engine_serial_no', 'equipment_power', 'measurement_by',
                  'measurement_quantity', 'fuel_consumption', 'remarks',
                  'document_details','owner_emi_details','rented_details','contractor_details','lease_details')
class MachineriesDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsMachineries
        fields = '__all__'
    def update(self, instance, validated_data):
        instance.is_deleted=True
        instance.updated_by = validated_data.get('updated_by')
        instance.save()
        return instance
class MachineriesDetailsDocumentAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsMachineriesDetailsDocument
        fields = ('id', 'equipment', 'document_name', 'document', 'created_by', 'owned_by')
class MachineriesDetailsDocumentEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsMachineriesDetailsDocument
        fields = ('id', 'equipment', 'document_name', 'updated_by')
class MachineriesDetailsDocumentDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsMachineriesDetailsDocument
        fields = '__all__'

    def update(self, instance, validated_data):
        instance.is_deleted = True
        instance.updated_by = validated_data.get('updated_by')
        instance.save()
        return instance
class MachineriesDetailsDocumentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PmsMachineriesDetailsDocument
        fields = '__all__'

#::::::::::::::::::: Pms Machinary Rented Type Master :::::::::::::#
class MachinaryRentedTypeMasterAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsMachinaryRentedTypeMaster
        fields = ('id', 'name', 'created_by', 'owned_by')
class MachinaryRentedTypeMasterEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsMachinaryRentedTypeMaster
        fields = ('id', 'name', 'updated_by')
class MachinaryRentedTypeMasterDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsMachinaryRentedTypeMaster
        fields = '__all__'
    def update(self, instance, validated_data):
        instance.is_deleted=True
        instance.updated_by = validated_data.get('updated_by')
        instance.save()
        return instance


#:::::::::::::::::  MECHINARY REPORT :::::::::::::::#
class MachineriesReportAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    contractor_o_vendor_details = serializers.SerializerMethodField(required=False)
    machine_name = serializers.SerializerMethodField(required=False)
    owner_type=serializers.SerializerMethodField(required=False)
    def get_owner_type(self,PmsProjectsMachinaryReport):
        if PmsProjectsMachinaryReport.machine:
            machin_d = PmsMachineries.objects.filter(pk=PmsProjectsMachinaryReport.machine.id).values('owner_type')
            if machin_d:
                for e_machin_d in machin_d:
                    return e_machin_d['owner_type']

    def get_machine_name(self,PmsProjectsMachinaryReport):
        if PmsProjectsMachinaryReport.machine:
            machin_d = PmsMachineries.objects.filter(pk=PmsProjectsMachinaryReport.machine.id).values('equipment_name')
            print('machin_d',machin_d)
            if machin_d:
                print('fssdf',machin_d[0]['equipment_name'])
                return machin_d[0]['equipment_name']
    def get_contractor_o_vendor_details(self,PmsProjectsMachinaryReport):
        if PmsProjectsMachinaryReport.machine:
            machinary_d = PmsMachineries.objects.filter(pk=PmsProjectsMachinaryReport.machine.id)
            #print('machinary_d',machinary_d)
            response_d = dict()
            if machinary_d:
                for e_mechine_details in machinary_d:
                    #print('e_mechine_details',e_mechine_details.owner_type)
                    if e_mechine_details.owner_type == 1:
                        # print('xyz',gfsdsdf)
                        machinary_rented_details_queryset = PmsMachinaryRentedDetails.objects.filter(
                            equipment=e_mechine_details.id,
                            is_deleted=False)
                        # print('machinary_rented_details_queryset',machinary_rented_details_queryset)
                        rental_details = dict()
                        for machinary_rent in machinary_rented_details_queryset:
                            rental_details['id'] = machinary_rent.id
                            rental_details['equipment'] = machinary_rent.equipment.id
                            rental_details['vendor'] = machinary_rent.vendor.id
                            rental_details['rent_amount'] = machinary_rent.rent_amount
                            rental_details['type_of_rent'] = machinary_rent.type_of_rent.id
                        if rental_details:
                            response_d["rental_details"] = rental_details
                            m_rented_details_vendor = PmsExternalUsers.objects.filter(
                                pk=machinary_rent.vendor.id, is_deleted=False)
                            #print('m_rented_details_vendor', m_rented_details_vendor)
                            for e_m_rented_details_vendor in m_rented_details_vendor:
                                m_v_details = {'id': e_m_rented_details_vendor.id,
                                            'name': e_m_rented_details_vendor.contact_person_name,
                                            'is_deleted': e_m_rented_details_vendor.is_deleted,
                                            }
                                response_d["rental_details"]['vendor_details'] = m_v_details
                    elif e_mechine_details.owner_type == 2:
                        owner_queryset = PmsMachinaryOwnerDetails.objects.filter(equipment=e_mechine_details.id,
                                                                                is_deleted=False)
                        # print('owner_queryset',owner_queryset)
                        owner_dict = {}
                        for owner in owner_queryset:
                            owner_dict['id'] = owner.id
                            owner_dict['equipment'] = owner.equipment.id
                            owner_dict['purchase_date'] = owner.purchase_date
                            owner_dict['price'] = owner.price
                            owner_dict['is_emi_available'] = owner.is_emi_available
                            if owner.is_emi_available:
                                emi_queryset = PmsMachinaryOwnerEmiDetails.objects.filter(equipment_owner_details=owner,
                                                                                        equipment=e_mechine_details.id,
                                                                                        is_deleted=False)
                                # print('emi_queryset',emi_queryset)
                                emi_dict = {}
                                for emi in emi_queryset:
                                    emi_dict['id'] = emi.id
                                    emi_dict['equipment'] = emi.equipment.id
                                    emi_dict['equipment_owner_details'] = emi.equipment_owner_details.id
                                    emi_dict['amount'] = emi.amount
                                    emi_dict['start_date'] = emi.start_date
                                    emi_dict['no_of_total_installment'] = emi.no_of_total_installment

                                if emi_dict:
                                    owner_dict['owner_emi_details'] = emi_dict
                                    # print('owner_dict',owner_dict)
                        if owner_dict:
                            response_d['owner_details'] = owner_dict
                    elif e_mechine_details.owner_type == 3 :
                        contract_queryset = PmsMachinaryContractDetails.objects.filter(
                            equipment=e_mechine_details.id,is_deleted=False)
                        contract_dict = {}
                        #print('contract_queryset',contract_queryset)
                        for contract in contract_queryset:
                            contract_dict['id'] = contract.id
                            contract_dict['equipment'] = contract.equipment.id
                            contract_dict['contractor_id'] = contract.contractor.id
                            contract_dict['contractor'] = contract.contractor.contact_person_name
                        response_d['contract_details'] = contract_dict
                    else:
                        lease_queryset=PmsMachinaryLeaseDetails.objects.filter(equipment=e_mechine_details.id,is_deleted=False)
                        lease_dict={}
                        for lease in lease_queryset:
                            lease_dict['id']=lease.id
                            lease_dict['vendor']=lease.vendor.id
                            lease_dict['vendor_name']=lease.vendor.contact_person_name
                            lease_dict['lease_amount']=lease.lease_amount
                            lease_dict['start_date']=lease.start_date
                            lease_dict['lease_period']=lease.lease_period
                        response_d['lease_details'] = lease_dict

                return response_d

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.Meta.required:
            self.fields[field].required = True
        for field in self.Meta.allow_null:
            self.fields[field].allow_null = True
    class Meta:
        model = PmsProjectsMachinaryReport
        fields = (
        'id', 'machine','machine_name','date', 'opening_balance', 'cash_purchase',
        'diesel_transfer_from_other_site','total_diesel_available','total_diesel_consumed','diesel_balance',
        'diesel_consumption_by_equipment','other_consumption','miscellaneous_consumption',
        'opening_meter_reading', 'closing_meter_reading','running_km','running_hours', 'purpose',
        'last_pm_date','next_pm_schedule','difference_in_reading','hsd_average','standard_avg_of_hours',
        'created_by', 'owned_by','contractor_o_vendor_details','owner_type')
        required = ('machine','date',)
        allow_null = ('last_pm_date','next_pm_schedule',)
class MachineriesReportEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.Meta.required:
            self.fields[field].required = True
        for field in self.Meta.allow_null:
            self.fields[field].allow_null = True
    class Meta:
        model = PmsProjectsMachinaryReport
        fields = ('id', 'machine', 'date', 'opening_balance', 'cash_purchase',
        'diesel_transfer_from_other_site','total_diesel_available','total_diesel_consumed','diesel_balance',
        'diesel_consumption_by_equipment','other_consumption','miscellaneous_consumption',
        'opening_meter_reading', 'closing_meter_reading','running_km','running_hours', 'purpose',
        'last_pm_date','next_pm_schedule','difference_in_reading','hsd_average',
        'standard_avg_of_hours','updated_by')
        required = ('machine','date',)
        allow_null = ('last_pm_date', 'next_pm_schedule',)
