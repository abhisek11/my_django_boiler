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

#:::::::::: TENDER AND TENDER DOCUMENTS  ::::::::#
class TenderEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    site_location_details = serializers.SerializerMethodField(required=False)
    def get_site_location_details(self,PmsTenders):
        if PmsTenders.site_location:
            tender_s_l = custom_filter(
                self, PmsSiteProjectSiteManagement,
                filter_columns={'id': PmsTenders.site_location.id, 'is_deleted': False},
                fetch_columns=['id', 'name', 'address','site_latitude',
                               'site_longitude','type','type__name','description','company_name',
                               'gst_no','geo_fencing_area','created_by', 'owned_by'],
                single_row=True
            )
            return tender_s_l
            
    class Meta:
        model = PmsTenders
        fields = ('id','updated_by','tender_final_date',
                  'tender_opened_on','tender_added_by','tender_received_on',
                  'tender_aasigned_to','site_location','site_location_details','tender_type')
    def update(self, instance, validated_data):
        try:
            with transaction.atomic():
                site_location = validated_data.pop('site_location') if "site_location" in validated_data else ""
                #print('site_location',type(site_location))
                if site_location:
                    instance.site_location = site_location
                    instance.updated_by = validated_data.get('updated_by')
                    instance.save()
                else:
                    instance.updated_by = validated_data.get('updated_by')
                    instance.tender_final_date = validated_data.get('tender_final_date')
                    instance.tender_opened_on = validated_data.get('tender_opened_on')
                    instance.tender_added_by = validated_data.get('tender_added_by')
                    instance.tender_received_on = validated_data.get('tender_received_on')
                    instance.tender_aasigned_to = validated_data.get('tender_aasigned_to')
                    instance.save()
                return instance
        except Exception as e:
            raise e

class TenderDocumentAddSerializer(serializers.ModelSerializer):
    tender_document = serializers.FileField(required=False)
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    tender_documents = serializers.ListField(required=False)
    status = serializers.BooleanField(default=True)
    class Meta:
        model = PmsTenderDocuments
        fields = ('id','tender','document_name','tender_document',
                  'created_by','owned_by','status','tender_documents')

class TenderDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsTenders
        fields = ("id",'updated_by','status','is_deleted')
    def update(self, instance, validated_data):
        delete_details = custom_delete(
            self, instance, validated_data,
            update_extra_columns=['status'],
            extra_model_with_fields=[
                {
                    'model': PmsTenderDocuments,
                    'filter_columns': {
                        'tender': instance
                    },
                    'update_extra_columns': ['status']
                },
            ]
        )
        return delete_details

class TenderDocsEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsTenderDocuments
        fields = ('id','document_name','updated_by')

class TenderDocumentDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsTenderDocuments
        fields = ("id",'updated_by','status','is_deleted')

    def update(self, instance, validated_data):
        try:
            with transaction.atomic():
                instance.updated_by = validated_data.get('updated_by')
                instance.is_deleted = True
                instance.status = False
                instance.save()
                return instance
        except Exception as e:
            raise e

class TendersAddSerializer(serializers.ModelSerializer):
    tender_g_id = serializers.CharField(required=False)
    created_by=serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by=serializers.CharField(default=serializers.CurrentUserDefault())
    status = serializers.BooleanField(default=True)
    class Meta:
        model = PmsTenders
        fields = ('id','tender_g_id',"tender_final_date","tender_opened_on",
                  "tender_added_by",'tender_received_on','tender_aasigned_to','tender_type',
                  'created_by','owned_by','status')
    def create(self, validated_data):
        try:
            tender_id = "T" + str(int(time.time()))
            #print('tender_id', tender_id)
            created_by = validated_data.get('created_by')
            #print('created_by',created_by)
            owned_by = validated_data.get('owned_by')
            with transaction.atomic():
                tender_save_id = PmsTenders.objects.create(
                        tender_g_id=tender_id,
                        tender_final_date=validated_data.get('tender_final_date'),
                        tender_opened_on=validated_data.get('tender_opened_on'),
                        tender_added_by=validated_data.get('tender_added_by'),
                        tender_received_on=validated_data.get('tender_received_on'),
                        tender_aasigned_to=validated_data.get('tender_aasigned_to'),
                        tender_type=validated_data.get('tender_type'),
                        created_by=created_by,
                        owned_by=owned_by
                       )
                response_data={
                    'id':tender_save_id.id,
                    'tender_g_id':tender_save_id.tender_g_id,
                    'tender_final_date': tender_save_id.tender_final_date,
                    'tender_opened_on': tender_save_id.tender_opened_on,
                    'tender_added_by': tender_save_id.tender_added_by,
                    'tender_received_on': tender_save_id.tender_received_on,
                    'tender_aasigned_to': tender_save_id.tender_aasigned_to,
                     'tender_type': tender_save_id.tender_type,
                    'created_by':tender_save_id.created_by,
                    'owned_by':tender_save_id.owned_by,
                    }
                return response_data

        except Exception as e:
            raise e

class TendersListSerializer(serializers.ModelSerializer):
    site_location_name=serializers.SerializerMethodField(required=False)
    tender_type_name=serializers.SerializerMethodField(required=False)
    def get_site_location_name(self,PmsTenders):
        if PmsTenders.site_location:
            return PmsSiteProjectSiteManagement.objects.only('name').get(id=PmsTenders.site_location.id).name
    def get_tender_type_name(self,PmsTenders):
        if PmsTenders.tender_type:
            return PmsTenderTypeMaster.objects.only('name').get(id=PmsTenders.tender_type.id).name
    
    class Meta:
        model = PmsTenders
        fields = '__all__'
        extra_fields=('site_location_name','tender_type_name')

class TendersArchiveSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsTenders
        fields = ('id', 'status', 'updated_by')

    def update(self, instance, validated_data):
        try:
            with transaction.atomic():
                instance.status = False
                instance.updated_by = validated_data.get('updated_by')
                instance.save()
                PmsTenderDocuments.objects.filter(tender=instance).update(status=False,
                                                                          updated_by=instance.updated_by)

                eligibility = PmsTenderEligibility.objects.filter(tender=instance)
                for e_l in eligibility:
                    e_l.status = False
                    e_l.updated_by = instance.updated_by
                    e_l.save()
                    PmsTenderEligibilityFieldsByType.objects.filter(tender=instance,
                                                                    tender_eligibility=e_l.id) \
                        .update(status=False, updated_by=instance.updated_by)

                    tab_document = PmsTenderTabDocuments.objects.filter(tender=instance)
                    for t_d in tab_document:
                        t_d.status = False
                        t_d.updated_by = instance.updated_by
                        t_d.save()
                        if t_d.is_upload_document == True:
                            PmsTenderTabDocumentsDocuments.objects.filter(tender=instance,
                                                                          tender_eligibility=e_l.id) \
                                .update(staus=False, updated_by=instance.updated_by)
                            PmsTenderTabDocumentsPrice.objects.filter(tender=instance).update(status=False,
                                                                                              updated_by=instance.updated_by)

                partners = PmsTenderPartners.objects.filter(tender=instance)
                # print('partners',partners)
                if partners:
                    for p_t in partners:
                        p_t.status = False
                        p_t.updated_by = instance.updated_by
                        p_t.save()
                        bidder_type = PmsTenderBidderType.objects.filter(tender=instance)
                        # print('bidder_type', bidder_type.__dict__)
                        for b_d in bidder_type:
                            # print('b_d', b_d.id)
                            b_d.status = False
                            b_d.updated_by = instance.updated_by
                            b_d.save()
                            if b_d.bidder_type == 'joint_venture':
                                bidder_partner = PmsTenderBidderTypePartnerMapping.objects \
                                    .filter(tender_bidder_type=b_d.id, tender_partner=p_t.id).update(
                                    status=False)
                else:
                    PmsTenderBidderType.objects.filter(tender=instance).update(status=False,
                                                                               updated_by=instance.updated_by)

                PmsTenderSurveySitePhotos.objects.filter(tender=instance).update(status=False,
                                                                                 updated_by=instance.updated_by)

                PmsTenderSurveyCoordinatesSiteCoordinate.objects.filter(tender=instance).update(
                    status=False, updated_by=instance.updated_by)

                tender_s_r_establishment = PmsTenderSurveyResourceEstablishment.objects.filter(
                    tender=instance)
                for t_s_r in tender_s_r_establishment:
                    t_s_r.status = False
                    t_s_r.updated_by = instance.updated_by
                    t_s_r.save()
                    PmsTenderSurveyDocument.objects.filter(tender=instance,
                                                           model_class="PmsTenderSurveyResourceEstablishment",
                                                           module_id=t_s_r.id).update(status=False,
                                                                                      updated_by=instance.updated_by)

                tender_s_r_hydrological = PmsTenderSurveyResourceHydrological.objects.filter(
                    tender=instance)
                for t_s_r in tender_s_r_hydrological:
                    t_s_r.status = False
                    t_s_r.updated_by = instance.updated_by
                    t_s_r.save()
                    PmsTenderSurveyDocument.objects.filter(tender=instance,
                                                           model_class="PmsTenderSurveyResourceHydrological",
                                                           module_id=t_s_r.id).update(status=False,
                                                                                      updated_by=instance.updated_by)

                tender_s_r_contractor = PmsTenderSurveyResourceContractorsOVendorsContractor.objects.filter(
                    tender=instance)
                for t_s_r in tender_s_r_contractor:
                    t_s_r.status = False
                    t_s_r.updated_by = instance.updated_by
                    t_s_r.save()
                    PmsTenderSurveyDocument.objects.filter(tender=instance,
                                                           model_class="PmsTenderSurveyResourceContractorsOVendorsContractor",
                                                           module_id=t_s_r.id).update(status=False,
                                                                                      updated_by=instance.updated_by)

                # tender_s_r_p_m = PmsTenderSurveyResourceContractorsOVendorsMachineryType.objects.filter(
                #     tender=instance)
                # for t_s_r in tender_s_r_p_m:
                #     t_s_r.status = False
                #     t_s_r.updated_by = instance.updated_by
                #     t_s_r.save()
                #     PmsTenderSurveyDocument.objects.filter(tender=instance,
                #                                            model_class="PmsTenderSurveyResourceContractorsOVendorsMachineryType",
                #                                            module_id=t_s_r.id).update(status=False,
                #                                                                       updated_by=instance.updated_by)

                contact_designation = PmsTenderSurveyResourceContactDesignation.objects.filter(
                    tender=instance)
                for c_d in contact_designation:
                    c_d.status = False
                    c_d.updated_by = instance.updated_by
                    c_d.save()
                    contact_details = PmsTenderSurveyResourceContactDetails.objects.filter(tender=instance,
                                                                                           designation=c_d.id)
                    for cc_d in contact_details:
                        cc_d.status = False
                        cc_d.updated_by = instance.updated_by
                        cc_d.save()
                        PmsTenderSurveyResourceContactFieldDetails.objects.filter(contact=cc_d.id).update(
                            status=False,
                            updated_by=instance.updated_by)

                initial_costing = PmsTenderInitialCosting.objects.filter(tender=instance)
                for i_c in initial_costing:
                    i_c.status = False
                    i_c.updated_by = instance.updated_by
                    i_c.save()
                    field_label = PmsTenderInitialCostingExcelFieldLabel.objects.filter(
                        tender_initial_costing=i_c.id)
                    for f_l in field_label:
                        f_l.status = False
                        f_l.updated_by = instance.updated_by
                        f_l.save()
                        PmsTenderInitialCostingExcelFieldValue.objects.filter(tender_initial_costing=i_c.id,
                                                                              initial_costing_field_label=f_l.id) \
                            .update(status=False, updated_by=instance.updated_by)

                PmsTenderApproval.objects.filter(tender=instance).update(status=False,
                                                                         updated_by=instance.updated_by)

                PmsTenderStatus.objects.filter(tender=instance).update(status=False,
                                                                       updated_by=instance.updated_by)

                return instance

        except Exception as e:
            raise e

class TendersArchiveListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PmsTenders
        fields = '__all__'

#:::::::::: TENDER  BIDDER TYPE :::::::::::::::#
class PartnersAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    status = serializers.BooleanField(default=True)
    class Meta:
        model=PmsTenderPartners
        fields='__all__'
class PartnersEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model=PmsTenderPartners
        fields='__all__'
class PartnersDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model=PmsTenderPartners
        fields='__all__'
    def update(self, instance, validated_data):
        instance.updated_by = validated_data.get('updated_by')
        instance.is_deleted = True
        instance.status = False
        instance.save()
        return instance
class TendorBidderTypeAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    status = serializers.BooleanField(default=True)
    partners = serializers.ListField(required=False)
    type_of_partner = serializers.IntegerField(required=False)
    class Meta:
        model=PmsTenderBidderType
        fields=('id','tender','bidder_type','type_of_partner','responsibility',
                'profit_sharing_ratio_actual_amount',
                'profit_sharing_ratio_tender_specific_amount','created_by',
                'owned_by','partners','status')
    def create(self, validated_data):
        try:
            tender_bidder_type_vendor_mapping_list=[]
            with transaction.atomic():
                if validated_data.get('bidder_type') == 'individual':
                    tender_bidder_type = PmsTenderBidderType.objects.create(tender=validated_data.get('tender'),
                                                                            bidder_type=validated_data.get(
                                                                                'bidder_type'),
                                                                            responsibility=validated_data.get(
                                                                                'responsibility'),
                                                                            status=validated_data.get('status'),
                                                                            created_by=validated_data.get('created_by'),
                                                                            owned_by=validated_data.get('owned_by')

                                                                            )
                    response = {
                        'id': tender_bidder_type.id,
                        'tender': tender_bidder_type.tender,
                        'bidder_type': tender_bidder_type.bidder_type,
                        'created_by': tender_bidder_type.created_by,
                        'owned_by': tender_bidder_type.owned_by,
                    }
                    return response
                else:
                    tender_bidder_type=PmsTenderBidderType.objects.create(
                        tender=validated_data.get('tender'),
                        bidder_type=validated_data.get('bidder_type'),
                        type_of_partner=validated_data.get('type_of_partner'),
                        responsibility=validated_data.get('responsibility'),
                        profit_sharing_ratio_actual_amount=validated_data.get('profit_sharing_ratio_actual_amount'),
                        profit_sharing_ratio_tender_specific_amount=validated_data.get('profit_sharing_ratio_tender_specific_amount'),
                        status = validated_data.get('status'),
                        created_by=validated_data.get('created_by'),
                        owned_by=validated_data.get('owned_by'))

                    for partner in validated_data.get('partners'):
                        #print('vendor',vendor)
                        request_dict = {
                                    "tender_bidder_type_id": str(tender_bidder_type),
                                    "tender_partner_id": int(partner),
                                    "status": True,
                                    "created_by": validated_data.get('created_by'),
                                    "owned_by": validated_data.get('owned_by')
                                   }
                        tender_bidder_type_partner_m, created=PmsTenderBidderTypePartnerMapping.objects.get_or_create(**request_dict)
                        tender_bidder_type_vendor_mapping_list.append({
                                "id" : tender_bidder_type_partner_m.tender_partner.id,
                                "name": tender_bidder_type_partner_m.tender_partner.name
                            })
                    #print('tender_bidder_type_vendor_mapping_list',tender_bidder_type_vendor_mapping_list)
                    response={
                        'id':tender_bidder_type.id,
                        'tender':tender_bidder_type.tender,
                        'bidder_type':tender_bidder_type.bidder_type,
                        'type_of_partner':tender_bidder_type.type_of_partner,
                        'responsibility':tender_bidder_type.responsibility,
                        'profit_sharing_ratio_actual_amount':tender_bidder_type.profit_sharing_ratio_actual_amount,
                        'profit_sharing_ratio_tender_specific_amount':tender_bidder_type.profit_sharing_ratio_tender_specific_amount,
                        'created_by':tender_bidder_type.created_by,
                        'owned_by':tender_bidder_type.owned_by,
                        'partners':validated_data.get('partners')

                    }
                    return response
        except Exception as e:
            raise APIException({'request_status': 0, 'msg': e})
class TendorBidderTypeEditSerializer(serializers.ModelSerializer):
    updated_by=serializers.CharField(default=serializers.CurrentUserDefault())
    partners = serializers.ListField(required=True)
    class Meta:
        model=PmsTenderBidderType
        fields = ( 'id', 'bidder_type','type_of_partner', 'responsibility',
                   'profit_sharing_ratio_actual_amount',
                   'profit_sharing_ratio_tender_specific_amount', 'updated_by','partners')

    def update(self, instance, validated_data):
        try:
            tender_bidder_type_partner_mapping_list = []
            with transaction.atomic():
                instance.bidder_type = validated_data.get('bidder_type', instance.bidder_type)
                instance.type_of_partner=validated_data.get('type_of_partner',instance.type_of_partner)
                #print('instance.type_of_partner',instance.type_of_partner)
                instance.responsibility=validated_data.get('responsibility',instance.responsibility)
                instance.profit_sharing_ratio_actual_amount=validated_data.get('profit_sharing_ratio_actual_amount',instance.profit_sharing_ratio_actual_amount)
                instance.profit_sharing_ratio_tender_specific_amount=validated_data.get('profit_sharing_ratio_tender_specific_amount',instance.profit_sharing_ratio_tender_specific_amount)
                instance.updated_by=validated_data.get('updated_by',instance.updated_by)
                instance.save()

                xyz=PmsTenderBidderTypePartnerMapping.objects.filter(tender_bidder_type_id=instance.id).delete()
                #print('xyz',xyz)

                for partner in validated_data.get('partners'):
                    #print('partner',partner)
                    request_dict = {
                        "tender_bidder_type_id": str(instance.id),
                        "tender_partner_id": partner['tender_partner_id'],
                        "status": True,
                        "created_by": validated_data.get('created_by'),
                        "owned_by": validated_data.get('owned_by')
                    }
                    tender_bidder_type_partner_m, created = PmsTenderBidderTypePartnerMapping.objects.get_or_create(
                        **request_dict)
                    tender_bidder_type_partner_mapping_list.append({
                        "id": tender_bidder_type_partner_m.tender_partner.id,
                        "name": tender_bidder_type_partner_m.tender_partner.name
                    })

                response = {
                    'id': instance.id,
                    'tender': instance.tender,
                    'bidder_type': instance.bidder_type,
                    'type_of_partner':  instance.type_of_partner,
                    'responsibility': instance.responsibility,
                    'profit_sharing_ratio_actual_amount':  instance.profit_sharing_ratio_actual_amount,
                    'profit_sharing_ratio_tender_specific_amount':  instance.profit_sharing_ratio_tender_specific_amount,
                    'updated_by': instance.updated_by,
                    'partners': tender_bidder_type_partner_mapping_list

                }
                return response
        except Exception as e:
            raise e
class TendorBidderTypeDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model=PmsTenderBidderType
        fields=('id','type_of_partner', 'responsibility', 'profit_sharing_ratio_actual_amount',
        'profit_sharing_ratio_tender_specific_amount','status','is_deleted',
                'updated_by','created_by','owned_by')

    def update(self, instance, validated_data):
        with transaction.atomic():
            instance.status=False
            instance.is_deleted=True
            instance.save()

            PmsTenderBidderTypeVendorMapping.objects.filter(tender_bidder_type_id=instance.id).update(status=False,is_deleted=True)

            response_data={ 'id':instance.id,
                            'tender': instance.tender,
                            'bidder_type': instance.bidder_type,
                            'type_of_partner': instance.type_of_partner,
                            'responsibility': instance.responsibility,
                            'profit_sharing_ratio_actual_amount': instance.profit_sharing_ratio_actual_amount,
                            'profit_sharing_ratio_tender_specific_amount': instance.profit_sharing_ratio_tender_specific_amount,
                            'created_by':instance.created_by,
                            'updated_by': instance.updated_by,
                            'owned_by': instance.owned_by,
                            'status':instance.status,
                            'is_deleted':instance.is_deleted
            }

            return  response_data


#:::::::::: TENDER  ELIGIBILITY :::::::::::::::#
class PmsTenderEligibilityAddSerializer(serializers.ModelSerializer):
    """Eligibility is added with the required parameters,
     using 2 table 'PmsTenderEligibility' and 'PmsTenderEligibilityFieldsByType'
     uniquely added on 'PmsTenderEligibility',
     transaction is exist,
     APIException is used. """
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    eligibility_type = serializers.CharField(required=True)
    eligibility_status = serializers.BooleanField(required=False)
    eligibility_fields = serializers.ListField(required=True)
    tender_id = serializers.IntegerField(required=True)
    class Meta:
        model = PmsTenderEligibility
        fields = ('id', 'tender_id', 'eligibility_type', 'eligibility_status', 'eligibility_fields', 'created_by')

    def create(self, validated_data):
        self.eligibility_status = True
        try:
            fields_result_list = list()
            current_user = validated_data.get('created_by')
            tender_id = validated_data.pop('tender_id') if "tender_id" in validated_data else 0
            eligibility_type = validated_data.pop('eligibility_type') if "eligibility_type" in validated_data else ""
            ineligibility_reason = validated_data.pop(
                'ineligibility_reason') if "ineligibility_reason" in validated_data else ""
            eligibility_fields = validated_data.pop('eligibility_fields')
            with transaction.atomic():
                if tender_id:
                    tender_eligibility_dict = {}
                    tender_eligibility_dict['tender_id'] = tender_id
                    tender_eligibility_dict['type'] = eligibility_type
                    tender_eligibility_dict['created_by'] = current_user
                    tender_eligibility_dict['owned_by'] = current_user

                    add_tender_eligibility,  created= PmsTenderEligibility.objects.get_or_create(**tender_eligibility_dict)
                    PmsTenderEligibilityFieldsByType.objects.filter(tender_id=tender_id,
                                                                    tender_eligibility_id=add_tender_eligibility.id).delete()
                    for fields_data in eligibility_fields:
                        #print("fields_data: ", fields_data)
                        fields_data['tender_id'] = tender_id
                        fields_data['tender_eligibility'] = add_tender_eligibility
                        fields_data['created_by'] = current_user
                        fields_data['owned_by'] = current_user
                        #print("eligibility_status: ", self.eligibility_status)
                        if not fields_data['eligible']:
                            self.eligibility_status = False



                        add_tender_eligibilityfields_by_type = PmsTenderEligibilityFieldsByType.objects.create(**fields_data)
                        added_fields = {"id": add_tender_eligibilityfields_by_type.id,
                                        "tender_id": add_tender_eligibilityfields_by_type.tender_id,
                                        "tender_eligibility_id": add_tender_eligibilityfields_by_type.tender_eligibility_id,
                                        "field_label": add_tender_eligibilityfields_by_type.field_label,
                                        "field_value": add_tender_eligibilityfields_by_type.field_value,
                                        "eligible": add_tender_eligibilityfields_by_type.eligible
                                        }
                        fields_result_list.append(added_fields)
                    if not self.eligibility_status:
                        PmsTenderEligibility.objects.filter(pk=add_tender_eligibility.id).update(
                            eligibility_status=False)
                    else:
                        PmsTenderEligibility.objects.filter(pk=add_tender_eligibility.id).update(
                            eligibility_status=True)
                    result_dict = {
                        "id": add_tender_eligibility.id,
                       "tender_id": add_tender_eligibility.tender.id,
                        "eligibility_type": add_tender_eligibility.type,
                        "eligibility_status": self.eligibility_status,
                       "eligibility_fields": fields_result_list
                                   }
            return result_dict
        except Exception as e:
            #print("error: ", e)
            raise APIException({'request_status': 0, 'msg': e})
class PmsTenderEligibilityFieldsByTypeEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsTenderEligibilityFieldsByType
        fields = ("id", "tender", "tender_eligibility",
                  "field_label", "field_value", "eligible","document", "updated_by")
class PmsTenderNotEligibilityReasonAddSerializer(serializers.ModelSerializer):
    updated_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsTenderEligibility
        fields = ("id", "tender", "ineligibility_reason",
                  "eligibility_status", "updated_by")
    def update(self, instance, validated_data):
        instance.ineligibility_reason = validated_data.get("ineligibility_reason",instance.ineligibility_reason)
        instance.save()
        return instance

#::::::::::::::: TENDER SURVEY SITE PHOTOS:::::::::::::::#
class TenderSurveySitePhotosAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    status = serializers.BooleanField(default=True)
    class Meta:
        model=PmsTenderSurveySitePhotos
        fields=('id','tender','latitude','longitude','address','additional_notes',
                'document','document_name','status','created_by','owned_by')
    def create(self, validated_data):
        try:
            survey_site_photos=PmsTenderSurveySitePhotos.objects.create(**validated_data)
            response_data={
                'id':survey_site_photos.id,
                'tender':survey_site_photos.tender,
                'latitude':survey_site_photos.latitude,
                'longitude':survey_site_photos.longitude,
                'address':survey_site_photos.address,
                'additional_notes':survey_site_photos.additional_notes,
                'document':survey_site_photos.document,
                'document_name': survey_site_photos.document_name,
                'status':survey_site_photos.status,
                'created_by':survey_site_photos.created_by,
                'owned_by':survey_site_photos.owned_by

            }
            return response_data
        except Exception as e:
            raise e
class TenderSurveySitePhotosEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model=PmsTenderSurveySitePhotos
        fields=('id','tender','latitude','longitude','address','additional_notes',
                'document','document_name','updated_by')
    def update(self, instance, validated_data):
        try:
            with transaction.atomic():
                instance.latitude=validated_data.get('latitude',instance.latitude)
                instance.longitude=validated_data.get('longitude',instance.longitude)
                instance.address=validated_data.get('address',instance.address)
                instance.additional_notes=validated_data.get('additional_notes',instance.additional_notes)
                instance.updated_by=validated_data.get('updated_by',instance.updated_by)
                instance.document_name=validated_data.get('document_name',instance.document_name)
                existing_image='./media/' + str(instance.document)
                if validated_data.get('document'):
                    if os.path.isfile(existing_image):
                        os.remove(existing_image)
                    instance.document = validated_data.get('document', instance.document)
                instance.save()
                return instance
        except Exception as e:
            raise APIException({'request_status': 0, 'msg': e})
class TenderSurveySitePhotosListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PmsTenderSurveySitePhotos
        fields = '__all__'
class TenderSurveySitePhotosDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsTenderSurveySitePhotos
        fields = '__all__'
    def update(self, instance, validated_data):
        try:
            with transaction.atomic():
                instance.status = False
                instance.is_deleted = True
                instance.save()
                return instance
        except Exception as e:
            raise APIException({'request_status': 0, 'msg': e})

#::::::::::::::: TENDER SURVEY COORDINATE :::::::::::::::#
class TenderSurveyMaterialsExternalUserMappingListSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    document_details = serializers.SerializerMethodField()
    mapping_document_details = serializers.SerializerMethodField()
    external_user_name = serializers.SerializerMethodField()
    external_user_contact = serializers.SerializerMethodField()
    def get_document_details(self, PmsExternalUsersExtraDetailsTenderMapping):
        document = PmsExternalUsersDocument.objects.filter(
            external_user_type=PmsExternalUsersExtraDetailsTenderMapping.external_user_type.id,
            external_user=PmsExternalUsersExtraDetailsTenderMapping.external_user.id,
            is_deleted=False)
        request = self.context.get('request')
        response_list = []
        for each_document in document:
            file_url = request.build_absolute_uri(each_document.document.url)
            owned_by = str(each_document.owned_by) if each_document.owned_by else ''
            created_by = str(each_document.created_by) if each_document.created_by else ''
            each_data = {
                "id": int(each_document.id),
                "external_user_type": each_document.external_user_type.id,
                "external_user_type_name": each_document.external_user_type.type_name,
                "external_user": each_document.external_user.id,
                #"external_user_name": each_document.external_user.organisation_name,
                "document_name": each_document.document_name,
                "document": file_url,
                "created_by": created_by,
                "owned_by": owned_by
            }
            print('each_data',each_data)
            response_list.append(each_data)
        return response_list
    def get_mapping_document_details(self, PmsExternalUsersExtraDetailsTenderMapping):
        document = PmsExternalUsersExtraDetailsTenderMappingDocument.objects.filter(
            external_user_mapping=PmsExternalUsersExtraDetailsTenderMapping.id,
            external_user=PmsExternalUsersExtraDetailsTenderMapping.external_user.id,
            is_deleted=False)
        request = self.context.get('request')
        response_list = []
        for each_document in document:
            file_url = request.build_absolute_uri(each_document.document.url)
            owned_by = str(each_document.owned_by) if each_document.owned_by else ''
            created_by = str(each_document.created_by) if each_document.created_by else ''
            each_data = {
                "id": int(each_document.id),
                "external_user_mapping": each_document.id,
                "external_user": each_document.external_user.id,
                "document_name": each_document.document_name,
                "document": file_url,
                "created_by": created_by,
                "owned_by": owned_by
            }
            print('each_data', each_data)
            response_list.append(each_data)
        return response_list
    def get_external_user_name(self,PmsExternalUsersExtraDetailsTenderMapping):
        user_details = PmsExternalUsers.objects.only('contact_person_name').get(
            pk=PmsExternalUsersExtraDetailsTenderMapping.external_user.id).contact_person_name
        return user_details
    def get_external_user_contact(self, PmsExternalUsersExtraDetailsTenderMapping):
        user_details = PmsExternalUsers.objects.only('contact_no').get(
            pk=PmsExternalUsersExtraDetailsTenderMapping.external_user.id).contact_no
        return user_details
    class Meta:
        model=PmsExternalUsersExtraDetailsTenderMapping
        fields='__all__'
        extra_fields = ['document_details','external_user_name']
class TenderSurveyMaterialsExternalUserMappingAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    mapping_details = serializers.ListField(required=False)

    class Meta:
        model=PmsExternalUsersExtraDetailsTenderMapping
        fields=('id','tender','external_user_type','tender_survey_material','created_by',
                'owned_by','mapping_details')

    def create(self, validated_data):
        response1 = list()
        #print('validated_data',validated_data)
        tender_id = validated_data.get('tender')
        external_user_type_id = validated_data.get('external_user_type')
        tender_survey_material_id = validated_data.get('tender_survey_material')
        mapping_details = validated_data.pop('mapping_details')
        exist = PmsExternalUsersExtraDetailsTenderMapping.objects.filter(
            tender=tender_id,
            external_user_type=external_user_type_id,
            tender_survey_material=tender_survey_material_id
        )
        #print('exist', exist)
        if exist:
            exist.delete()

        for each in mapping_details:
            #print('each',each)
            extra_d = PmsExternalUsersExtraDetailsTenderMapping.objects.create(
                tender=tender_id,
                external_user_type= external_user_type_id,
                tender_survey_material = tender_survey_material_id,
                external_user_id = each['external_user'],
                latitude = each['latitude'],
                longitude = each['longitude'],
                address = each['address'],
                created_by = validated_data.get('created_by'),
                owned_by = validated_data.get('owned_by')
            )
            #print('extra_d',extra_d)
            response_d = {
                'id': int(extra_d.id),
                'external_user':extra_d.external_user.id,
                'latitude':extra_d.latitude,
                'longitude':extra_d.longitude,
                'address':extra_d.address
            }
            #print('response_d',response_d)
            response1.append(response_d)
        #print('response1',response1)
        response = {
            'tender': tender_id,
            'external_user_type': external_user_type_id,
            'tender_survey_material': tender_survey_material_id,
            'mapping_details':response1
        }
        return response
class TenderSurveyMaterialsExternalUserMappingAddFAndroidSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    mapping_details = serializers.DictField(required=False)

    class Meta:
        model=PmsExternalUsersExtraDetailsTenderMapping
        fields=('id','tender','external_user_type','tender_survey_material','created_by',
                'owned_by','mapping_details')

    def create(self, validated_data):
        response1 = list()
        print('validated_data',validated_data)
        tender_id = validated_data.get('tender')
        external_user_type_id = validated_data.get('external_user_type')
        tender_survey_material_id = validated_data.get('tender_survey_material')
        mapping_details = validated_data.pop('mapping_details')
        #print('each',each)
        extra_d = PmsExternalUsersExtraDetailsTenderMapping.objects.create(
            tender=tender_id,
            external_user_type= external_user_type_id,
            tender_survey_material = tender_survey_material_id,
            external_user_id = mapping_details['external_user'],
            latitude = mapping_details['latitude'],
            longitude = mapping_details['longitude'],
            address = mapping_details['address'],
            created_by = validated_data.get('created_by'),
            owned_by = validated_data.get('owned_by')
        )
        #print('extra_d',extra_d)
        response_d = {
            'id': int(extra_d.id),
            'external_user':extra_d.external_user.id,
            'latitude':extra_d.latitude,
            'longitude':extra_d.longitude,
            'address':extra_d.address
        }
        #print('response_d',response_d)
        #response1.append(response_d)
        #print('response1',response1)
        response = {
            'tender': tender_id,
            'external_user_type': external_user_type_id,
            'tender_survey_material': tender_survey_material_id,
            'mapping_details':response_d
        }
        return response
class TenderSurveyMaterialsExternalUserMappingDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    is_deleted = serializers.BooleanField(default=True)
    class Meta:
        model=PmsExternalUsersExtraDetailsTenderMapping
        fields='__all__'
        read_only_fields = ('tender', 'external_user_type','external_user',
                            'tender_survey_material','latitude','longitude','address')
class TenderSurveyMaterialsExternalUserMappingDocumentAddSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    owned_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsExternalUsersExtraDetailsTenderMappingDocument
        fields = ("id", "external_user", "external_user_mapping", "document_name", "document", "created_by", "owned_by")
class TenderSurveyLocationAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    status = serializers.BooleanField(default=True)
    class Meta:
        model=PmsTenderSurveyCoordinatesSiteCoordinate
        fields=('id','tender','name','latitude','longitude','address','status',
                'created_by','owned_by')
class TenderSurveyLocationListSerializer(serializers.ModelSerializer):
    class Meta:
        model=PmsTenderSurveyCoordinatesSiteCoordinate
        fields=('id','tender','name','latitude','longitude','address',
                'status','created_by','owned_by')
class TenderSurveyLocationEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model=PmsTenderSurveyCoordinatesSiteCoordinate
        fields=('id','tender','name','latitude','longitude','address','updated_by')
class TenderSurveyLocationDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsTenderSurveyCoordinatesSiteCoordinate
        fields = '__all__'
    def update(self, instance, validated_data):
        try:
            with transaction.atomic():
                instance.status = False
                instance.is_deleted = True
                instance.save()
                response_data = {'id': instance.id,
                                 'tender': instance.tender,
                                 'name':instance.name,
                                 'latitude': instance.latitude,
                                 'longitude': instance.longitude,
                                 'address': instance.address,
                                 'created_by': instance.created_by,
                                 'updated_by': instance.updated_by,
                                 'owned_by': instance.owned_by,
                                 'status': instance.status,
                                 'is_deleted': instance.is_deleted
                                 }
                return response_data
        except Exception as e:
            raise APIException({'request_status': 0, 'msg': e})

#:::::::::::::::::::::: MATERIAL TYPE MASTER:::::::::::::::::::::::::::#
# class MaterialTypeMasterAddSerializer(serializers.ModelSerializer):
#     created_by = serializers.CharField(default=serializers.CurrentUserDefault())
#     owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
#     class Meta:
#         model = MaterialTypeMaster
#         fields = ('id', 'name', 'created_by', 'owned_by')


# class MaterialTypeMasterEditSerializer(serializers.ModelSerializer):
#     updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

#     class Meta:
#         model = MaterialTypeMaster
#         fields = ('id', 'name', 'updated_by')

# class MaterialTypeMasterDeleteSerializer(serializers.ModelSerializer):
#     updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
#     class Meta:
#         model = MaterialTypeMaster
#         fields = '__all__'
#     def update(self, instance, validated_data):
#         instance.is_deleted=True
#         instance.updated_by = validated_data.get('updated_by')
#         instance.save()
#         return instance

#::::::::::: TENDER SURVEY RESOURCE ::::::::::::::::::::#
class MaterialsAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    materials_unit=serializers.ListField(required=False)
    class Meta:
        model=Materials
        fields='__all__'
        extra_fields=('materials_unit',)
        
    def create(self, validated_data):
        try:
            materials_unit=validated_data.pop('materials_unit')if 'materials_unit' in validated_data else ""
            created_by=validated_data.get('created_by')
            owned_by=validated_data.get('owned_by')
            materials_unit_list=list()
            with transaction.atomic():
                material_data = Materials.objects.filter(
                    mat_code = validated_data.get('mat_code'),
                    is_deleted=False
                )
                print('material_data',material_data)
                if not material_data:
                    material_data=Materials.objects.create(**validated_data)

                    for m_u in materials_unit:
                        unit_data,created_2=MaterialsUnitMapping.objects.get_or_create(material=material_data,**m_u,
                                                                                    created_by=created_by,
                                                                                    owned_by=owned_by)
                        unit_data.__dict__.pop('_state') if '_state' in unit_data.__dict__.keys() else unit_data.__dict__
                        materials_unit_list.append(unit_data.__dict__)
                    material_data.__dict__['materials_unit']=materials_unit_list

                    return material_data
                else:
                    raise serializers.ValidationError({
                'request_status':0,
                'msg': 'This mat code already exist'})


        except Exception as e:
            raise e
class MaterialsListSerializer(serializers.ModelSerializer):
    materials_unit_details = serializers.SerializerMethodField(required=False)
    # mat_type_name = serializers.SerializerMethodField(required=False)
    current_stock = serializers.SerializerMethodField()
    # def get_mat_type_name(self,Materials):
    #     if Materials.mat_type:
    #         type_details=MaterialTypeMaster.objects.only('name').get(id=Materials.mat_type.id,is_deleted=False).name
    #         return type_details
    #     else:
    #         return None
 
    def get_materials_unit_details(self, Materials):
        unit_details = MaterialsUnitMapping.objects.filter(material=Materials.id)
        unit_list = list()
        for each_unit in unit_details:
            each_data = {
                'id': each_unit.id,
                "material": each_unit.material.id,
                "unit": each_unit.unit.id,
                "unit_name": each_unit.unit.c_name,
            }
            unit_list.append(each_data)
        return unit_list

    def get_current_stock(self, Materials):
        from datetime import datetime
        item_type_id = PmsExecutionPurchasesRequisitionsTypeMaster.objects.only('id').get(type_name="Materials").id
        print('item_type_id', item_type_id)
        current_stock_d = PmsExecutionUpdatedStock.objects.filter(
            item=Materials.id,
            type_id=item_type_id,
            #uom=MaterialsUnitMapping.objects.only('unit').get(material_id=Materials.id).unit,
            stock_date__date=datetime.date(datetime.now()),
            is_deleted=False)
        if current_stock_d:
            for current_stock in current_stock_d:
                if current_stock:
                    return current_stock.opening_stock
        else:
            return 0

            # return current_stock

    class Meta:
        model = Materials
        fields = '__all__'
        extra_fields = ('materials_unit_details',)
class MaterialsEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    materials_unit=serializers.ListField(required=False)
    class Meta:
        model=Materials
        fields='__all__'
        extra_fields=('materials_unit')
    def update(self, instance, validated_data):
        try:
            with transaction.atomic():
                materials_unit = validated_data.pop('materials_unit') if 'materials_unit' in validated_data else ""
                materials_unit_list=list()
                instance.mat_code = validated_data.get('mat_code')
                instance.type_code = validated_data.get('type_code')
                instance.name = validated_data.get('name')
                instance.description = validated_data.get('description')
                instance.updated_by = validated_data.get('updated_by')
                instance.save()
                unit_details=MaterialsUnitMapping.objects.filter(material=instance)
                # Removed By Rupam [987 - 992]
                # for u_d in unit_details:
                #     # print('u_d',u_d)
                #     if u_d.is_deleted == False:
                #         u_d.is_deleted=True
                #         u_d.save()
                #     # print(u_d.is_deleted)
                
                if unit_details:
                    unit_details.delete()
                # Removed By Rupam [987 - 992]
                for m_u in materials_unit:
                    unit_data= MaterialsUnitMapping.objects.create(material=instance,
                                                                                    **m_u,
                                                                                    created_by=instance.updated_by,
                                                                                    owned_by=instance.updated_by )
                    # print('unit_data', unit_data)


                    unit_data.__dict__.pop('_state') if '_state' in unit_data.__dict__.keys() else unit_data.__dict__
                    materials_unit_list.append(unit_data.__dict__)
                instance.__dict__['materials_unit']=materials_unit_list
                return instance

        except Exception as e:
                raise e
class MaterialsDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    materials_unit=serializers.ListField(required=False)
    class Meta:
        model=Materials
        fields=('id','is_deleted','updated_by','materials_unit')

    def update(self,instance,validated_data):
        try:
            with transaction.atomic():
                instance.is_deleted = True
                instance.updated_by = validated_data.get('updated_by')
                instance.save()
                unit_details = MaterialsUnitMapping.objects.filter(material=instance)
                # print('unit_details',unit_details)
                unit_details_list = list()
                for u_d in unit_details:
                    # print('u_d',u_d.__dict__)
                    #if u_d.is_deleted == False:
                        #u_d.is_deleted = True
                    u_d.delete()
                    u_d.__dict__.pop('_state') if '_state' in u_d.__dict__.keys() else u_d.__dict__
                    unit_details_list.append( u_d.__dict__)
                # print('unit_details_list',unit_details_list)
                instance.__dict__['materials_unit']=unit_details_list
                # print('instance',instance.__dict__)
                return instance

        except Exception as e:
            raise e

#:::::::::: TENDER SURVEY RESOURCE ESTABLISHMENT :::::::::::#
class TenderSurveyResourceEstablishmentAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsTenderSurveyResourceEstablishment
        fields = (
        'id', 'tender', 'name', 'details', 'latitude', 'longitude', 'address', 'status', 'created_by', 'owned_by')
class TenderSurveyResourceEstablishmentEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsTenderSurveyResourceEstablishment
        fields = ('id', 'tender', 'name', 'details', 'latitude', 'longitude', 'address', 'status', 'updated_by')
class TenderSurveyResourceEstablishmentDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsTenderSurveyResourceEstablishment
        fields = '__all__'

    def update(self, instance, validated_data):
        instance.status = False
        instance.is_deleted = True
        instance.updated_by = validated_data.get('updated_by')
        instance.save()
        return instance
class TenderSurveyResourceEstablishmentDocumentAddSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    owned_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    status = serializers.BooleanField(default=True)

    class Meta:
        model = PmsTenderSurveyDocument
        fields = ("id", "tender", "module_id", "document_name", "document", "created_by", "owned_by", 'status')

    def create(self, validated_data):
        resource_establishment_data = PmsTenderSurveyDocument.objects.create(**validated_data,
                                                                             model_class="PmsTenderSurveyResourceEstablishment")

        return resource_establishment_data
class TenderSurveyResourceEstablishmentDocumentEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsTenderSurveyDocument
        fields = ("id", "module_id", "document_name", "document", "updated_by")

    def update(self, instance, validated_data):
        instance.module_id = validated_data.get('module_id')
        instance.document_name = validated_data.get('document_name')
        instance.updated_by = validated_data.get('updated_by')
        existing_image = './media/' + str(instance.document)
        if validated_data.get('document'):
            if os.path.isfile(existing_image):
                os.remove(existing_image)
            instance.document = validated_data.get('document')
        instance.save()
        return instance
class TenderSurveyResourceEstablishmentDocumentDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsTenderSurveyDocument
        fields = '__all__'

    def update(self, instance, validated_data):
        instance.status = False
        #print('   instance.status ', instance.status)
        instance.updated_by = validated_data.get('updated_by')
        instance.is_deleted = True
        instance.save()
        return instance

#:::: TENDER SURVEY RESOURCE HYDROLOGICAL :::::::#
class TenderSurveyResourceHydrologicalAddSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    owned_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    status = serializers.BooleanField(default=True)
    class Meta:
        model = PmsTenderSurveyResourceHydrological
        fields = ("id", 'tender', "name", 'details', 'latitude', 'longitude', 'address', "created_by",
                  "owned_by", 'status')
class TenderSurveyResourceHydrologicalEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsTenderSurveyResourceHydrological
        fields = ("id","name", 'details', 'latitude', 'longitude', 'address', "updated_by"
                  )
class TenderSurveyResourceHydrologicalDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsTenderSurveyResourceHydrological
        fields = '__all__'

    def update(self, instance, validated_data):
        instance.status = False
        instance.is_deleted = True
        instance.updated_by = validated_data.get('updated_by')
        instance.save()
        return instance
class TenderSurveyResourceHydrologicalDocumentAddSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    owned_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    status = serializers.BooleanField(default=True)
    class Meta:
        model = PmsTenderSurveyDocument
        fields = ("id", "tender", "module_id", "document_name",
                  "document", "created_by", "owned_by",'status')

    def create(self, validated_data):
        survey_document_data = PmsTenderSurveyDocument.objects.create(**validated_data,
                                                                      model_class="PmsTenderSurveyResourceHydrological")
        return survey_document_data
class TenderSurveyResourceHydrologicalDocumentEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsTenderSurveyDocument
        fields = ("id", "module_id", "document_name", "document", "updated_by")

    def update(self, instance, validated_data):
        instance.module_id = validated_data.get('module_id')
        instance.document_name = validated_data.get('document_name')
        instance.updated_by = validated_data.get('updated_by')
        existing_image = './media/' + str(instance.document)
        if validated_data.get('document'):
            if os.path.isfile(existing_image):
                os.remove(existing_image)
            instance.document = validated_data.get('document')
        instance.save()
        return instance
class TenderSurveyResourceHydrologicalDocumentDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsTenderSurveyDocument
        fields = '__all__'

    def update(self, instance, validated_data):
        instance.status = False
        instance.is_deleted = True
        instance.updated_by = validated_data.get('updated_by')
        instance.save()
        return instance

#:::: TENDER SURVEY RESOURCE CONTRACTORS / VENDORS  CONTRACTOR WORK TYPE:::::::#
class TenderSurveyResourceContractorsOVendorsContractorWTypeAddSerializer(serializers.ModelSerializer):
    status = serializers.BooleanField(default=True)
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsTenderSurveyResourceContractorsOVendorsContractor
        fields = ('id', 'tender','name','details','latitude','longitude',
                  'address', 'status', 'created_by','owned_by')
class TenderSurveyResourceContractorsOVendorsContractorWTypeEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsTenderSurveyResourceContractorsOVendorsContractor
        fields = ('id','name','details','latitude','longitude','address','updated_by')
class TenderSurveyResourceContractorsOVendorsContractorWTypeDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsTenderSurveyResourceContractorsOVendorsContractor
        fields = '__all__'
    def update(self, instance, validated_data):
        instance.status = False
        instance.updated_by = validated_data.get('updated_by')
        instance.is_deleted = True
        instance.save()

        return instance
class TenderSurveyResourceContractorsOVendorsContractorWTypeDocumentAddSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    owned_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsTenderSurveyDocument
        fields = ("id", "tender", "module_id", "document_name", "document",
                  "created_by", "owned_by")
    def create(self, validated_data):
        survey_document_data = PmsTenderSurveyDocument.objects.create(
            **validated_data,model_class="PmsTenderSurveyResourceContractorsOVendorsContractor")
        return survey_document_data
class TenderSurveyResourceContractorsOVendorsContractorWTypeDocumentEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsTenderSurveyDocument
        fields = ("id", "module_id", "document_name", "document","updated_by")
    def update(self, instance, validated_data):
        instance.module_id=validated_data.get('module_id')
        instance.document_name=validated_data.get('document_name')
        instance.updated_by = validated_data.get('updated_by')
        existing_image = './media/' + str(instance.document)
        if validated_data.get('document'):
            if os.path.isfile(existing_image):
                os.remove(existing_image)
            instance.document = validated_data.get('document')
        instance.save()
        return instance
class TenderSurveyResourceContractorsOVendorsContractorWTypeDocumentDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsTenderSurveyDocument
        fields = '__all__'
    def update(self, instance, validated_data):
        instance.status = False
        instance.is_deleted = True
        instance.updated_by = validated_data.get('updated_by')
        instance.save()
        return instance

 #:::::::::::::::::::::: Machinary Type :::::::::::::::::::::::::#
class MachineryTypeAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    is_default = serializers.BooleanField(required=False)
    class Meta:
        model = PmsMachineryType
        fields = ( "id", "name", "description","created_by", "owned_by",'is_default')

class MachineryTypeEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsMachineryType
        fields = ("id", "name", "description","updated_by")
        
class MachineryTypeDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    is_deleted = serializers.BooleanField(default=True)

    class Meta:
        model = PmsMachineryType
        fields = ("id", "updated_by", "is_deleted")

#:::: TENDER SURVEY RESOURCE CONTRACTORS / VENDORS  P & M:::::::#

class TenderSurveyResourceContractorsOVendorsMachineryTypeExDeAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    is_default = serializers.BooleanField(default=False)
    # name = serializers.CharField(required=False)
    # description = serializers.CharField(required=False)
    machinary_name = serializers.CharField(required=False)
    machinary_description = serializers.CharField(required=False)


    class Meta:
        model = PmsTenderMachineryTypeDetails
        fields = ("id", 'tender',"machinary_type",'make','hire', 
        'khoraki', 'latitude','longitude', 'address', "created_by","owned_by",'updated_by',
        'is_default','machinary_name','machinary_description')
    
    def create(self,validated_data):
        try:
            response_m = dict()
            pmsTenderMachineryTypeDetails_e = PmsTenderMachineryTypeDetails.objects.filter(
                    tender=validated_data.get('tender'),
                    machinary_type=validated_data.get('machinary_type')
                )
            #print('pmsTenderMachineryTypeDetails_e',pmsTenderMachineryTypeDetails_e)
            if pmsTenderMachineryTypeDetails_e:
                for e_d in pmsTenderMachineryTypeDetails_e:
                    e_d.make = validated_data.get('make')
                    e_d.hire = validated_data.get('hire')
                    e_d.khoraki = validated_data.get('khoraki')
                    e_d.latitude = validated_data.get('latitude')
                    e_d.longitude = validated_data.get('longitude')
                    e_d.address = validated_data.get('address')
                    e_d.updated_by = validated_data.get('updated_by')
                    e_d.save()
                    response_m['id'] = e_d.id
                    response_m['tender'] = e_d.tender
                    response_m['machinary_type'] = e_d.machinary_type
                    response_m['machinary_name'] = PmsMachineryType.objects.only('name').get(
                        pk=e_d.machinary_type.id).name
                    response_m['machinary_description'] = PmsMachineryType.objects.only('description').get(
                        pk=e_d.machinary_type.id).description
                    response_m['make'] = e_d.make
                    response_m['hire'] = e_d.hire
                    response_m['khoraki'] = e_d.khoraki
                    response_m['latitude'] = e_d.latitude
                    response_m['longitude'] = e_d.longitude
                    response_m['address'] = e_d.address
                    return response_m
            else:
                
                machinery_type_details=PmsTenderMachineryTypeDetails.objects.create(
                    tender=validated_data.get('tender'),
                    machinary_type=validated_data.get('machinary_type'),
                    make=validated_data.get('make'),
                    hire=validated_data.get('hire'),
                    khoraki=validated_data.get('khoraki'),
                    latitude=validated_data.get('latitude'),
                    longitude=validated_data.get('longitude'),
                    address=validated_data.get('address'),
                    created_by=validated_data.get('created_by'),
                    owned_by=validated_data.get('owned_by')
                    )
                return machinery_type_details
        except Exception as e:
            raise e         

class TenderSurveyResourceContractorsOVendorsMachineryTypeDeAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    machinary_type_list = serializers.ListField(required=False)
    is_default = serializers.BooleanField(default=False)
    name = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
    machinary_name = serializers.SerializerMethodField()
    machinary_description = serializers.SerializerMethodField()
    def get_machinary_name(self,PmsTenderMachineryTypeDetails):
        machineryTypeDetails = PmsMachineryType.objects.filter(
            pk=PmsTenderMachineryTypeDetails.machinary_type.id)
        if machineryTypeDetails:
            return PmsMachineryType.objects.only('name').get(
            pk=PmsTenderMachineryTypeDetails.machinary_type.id).name
        else:
            return None
    
    def get_machinary_description(self,PmsTenderMachineryTypeDetails):
        machineryTypeDetails = PmsMachineryType.objects.filter(
            pk=PmsTenderMachineryTypeDetails.machinary_type.id)
        if machineryTypeDetails:
            return PmsMachineryType.objects.only('description').get(
            pk=PmsTenderMachineryTypeDetails.machinary_type.id).description
        else:
            return None

    class Meta:
        model = PmsTenderMachineryTypeDetails
        fields = (
        "id", 'tender',"machinary_type",'name','description','make','hire', 
        'khoraki', 'latitude','longitude', 'address', "created_by","owned_by",
        "machinary_type_list",'is_default','machinary_name','machinary_description')
    
    def create(self,validated_data):
        try:
                with transaction.atomic():
                    machinery_type_data= PmsMachineryType.objects.create(
                        name=validated_data.get('name'), 
                        description=validated_data.get('description'), 
                        is_default = validated_data.get('is_default'),
                        created_by = validated_data.get('created_by'),
                        owned_by = validated_data.get('owned_by')
                        )
                    print("machinery_type_data::::::::",machinery_type_data)
                    machinery_type_details=PmsTenderMachineryTypeDetails.objects.create(
                        tender=validated_data.get('tender'),
                        machinary_type_id=machinery_type_data.id,
                        make=validated_data.get('make'),
                        hire=validated_data.get('hire'),
                        khoraki=validated_data.get('khoraki'),
                        latitude=validated_data.get('latitude'),
                        longitude=validated_data.get('longitude'),
                        address=validated_data.get('address'),
                        created_by = validated_data.get('created_by'),
                        owned_by = validated_data.get('owned_by')
                        )
                    return machinery_type_details
        except Exception as e:
            #print('response.status_code',dir(e))
            print('response.status_code',e.args[0])
            if e.args[0] == 1062:
                raise APIException({
                    'request_status': 0, 
                    'msg': "Duplicate entry machinary name"
                    })    
            else:
                raise APIException({
                    'request_status': 0,
                    'msg': e.args[1]
                })
class MachinaryTypeListByTenderSerializer(serializers.ModelSerializer): 
    name=serializers.SerializerMethodField()
    description=serializers.SerializerMethodField()
    def get_name(self,PmsTenderMachineryTypeDetails):
        return PmsMachineryType.objects.only('name').get(id=PmsTenderMachineryTypeDetails.machinary_type.id).name
    def get_description(self,PmsTenderMachineryTypeDetails):
        return PmsMachineryType.objects.only('description').get(id=PmsTenderMachineryTypeDetails.machinary_type.id).description

    class Meta:
        model=PmsTenderMachineryTypeDetails
        fields=("id","tender","machinary_type",'make',"hire","khoraki","latitude","longitude","address","name","description")


class TenderSurveyResourceContractorsOVendorsMachineryTypeDeEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    description = serializers.CharField(required=False)
    class Meta:
        model = PmsTenderMachineryTypeDetails
        fields = ("id", "machinary_type", 'make',"description",'hire', 'khoraki', 'latitude', 'longitude', 'address',"updated_by")
class TenderSurveyResourceContractorsOVendorsMachineryTypeDeDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    is_deleted = serializers.BooleanField(default=True)
    class Meta:
        model = PmsTenderMachineryTypeDetails
        fields = ("id", "updated_by","is_deleted")
class TenderSurveyResourceContractorsOVendorsMachineryTypeDeDocumentAddSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    owned_by = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsTenderSurveyDocument
        fields = ("id", "tender", "module_id", "document_name", "document", "created_by", "owned_by")

    def create(self, validated_data):
        survey_document_data = PmsTenderSurveyDocument.objects.create(
            **validated_data,
            model_class="PmsTenderMachineryTypeDetails"
        )
        return survey_document_data
class TenderSurveyResourceContractorsOVendorsMachineryTypeDeDocumentEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsTenderSurveyDocument
        fields = ("id", "module_id", "document_name", "document", "updated_by")

    def update(self, instance, validated_data):
        instance.module_id = validated_data.get('module_id')
        instance.document_name = validated_data.get('document_name')
        instance.updated_by = validated_data.get('updated_by')
        existing_image = './media/' + str(instance.document)
        if validated_data.get('document'):
            if os.path.isfile(existing_image):
                os.remove(existing_image)
            instance.document = validated_data.get('document')
        instance.save()
        return instance
class TenderSurveyResourceContractorsOVendorsMachineryTypeDeDocumentDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsTenderSurveyDocument
        fields = '__all__'
    def update(self, instance, validated_data):
        instance.status = False
        instance.is_deleted = True
        instance.updated_by = validated_data.get('updated_by')
        instance.save()
        return instance

#:::: TENDER SURVEY RESOURCE CONTACT DETAILS AND DESIGNATION :::::::#
class TenderSurveyResourceContactDesignationAddSerializer(serializers.ModelSerializer):
    status = serializers.BooleanField(default=True)
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model=PmsTenderSurveyResourceContactDesignation
        fields=('id','tender','name','status','created_by','owned_by')
class TenderSurveyResourceContactDetailsAddSerializer(serializers.ModelSerializer):
    status = serializers.BooleanField(default=True)
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    field_details = serializers.ListField(required=False)
    # prev_field_details_exist = serializers.CharField(required=False)
    class Meta:
        model = PmsTenderSurveyResourceContactDetails
        # fields = ('id','tender', 'designation', 'field_details',
        #           'status', 'created_by', 'owned_by','prev_field_details_exist')

        fields = ('id', 'tender', 'designation', 'field_details',
                  'status', 'created_by', 'owned_by')
    def create(self, validated_data):
        field_details_l = list()
        created_by = validated_data.get('created_by')
        owned_by = validated_data.get('owned_by')
        field_details = validated_data.pop('field_details')
        # prev_field_details_exist = validated_data.pop('prev_field_details_exist')
        contact_details =  PmsTenderSurveyResourceContactDetails.objects.create(
            **validated_data )
        response = {
            'id': contact_details.id,
            'tender': contact_details.tender,
            'designation': contact_details.designation,
            'status':contact_details.status,
            'created_by':contact_details.created_by.username,
            'owned_by': contact_details.owned_by.username
        }
        for fields_data in field_details:
            f_l = PmsTenderSurveyResourceContactFieldDetails.objects.create(
                contact = contact_details,
                field_label = fields_data['field_label'],
                field_value = fields_data['field_value'],
                field_type = fields_data['field_type'],
                created_by = created_by,
                owned_by = owned_by
                )
            contact_field_details_r_dict = {}
            contact_field_details_r_dict['id'] = f_l.id
            contact_field_details_r_dict['contact'] = f_l.contact.id
            contact_field_details_r_dict['field_label'] = f_l.field_label
            contact_field_details_r_dict['field_value'] = f_l.field_value
            contact_field_details_r_dict['field_type'] = f_l.field_type
            contact_field_details_r_dict['created_by'] = f_l.created_by.username
            contact_field_details_r_dict['owned_by'] = f_l.owned_by.username
            field_details_l.append(contact_field_details_r_dict)
        response['field_details'] = field_details_l

        return response
            # if prev_field_details_exist == 'yes':
            #     r = PmsTenderSurveyResourceContactFieldDetails.objects.filter(
            #         contact_id=contact_details.id)
            #     print('r',r)
            #     contact_field_details_dict = {}
            #
            #     for fields_data in field_details:
            #         contact_field_details_dict['contact'] = contact_details
            #         contact_field_details_dict['field_label'] = fields_data['field_label']
            #         contact_field_details_dict['field_value'] = fields_data['field_value']
            #         contact_field_details_dict['field_type'] = fields_data['field_type']
            #         contact_field_details_dict['created_by'] = created_by
            #         contact_field_details_dict['owned_by'] = owned_by
            #
            #         f_l = PmsTenderSurveyResourceContactFieldDetails.objects.create(**contact_field_details_dict)
            #         contact_field_details_r_dict={
            #             'id':f_l.id,
            #             'contact':f_l.contact.id,
            #             'field_label':f_l.field_label,
            #             'field_value':f_l.field_value,
            #             'field_type':f_l.field_type,
            #             'created_by':f_l.created_by.username,
            #             'owned_by': f_l.owned_by.username
            #         }
            #
            #         field_details_l.append(contact_field_details_r_dict)
            #     print('field_details_l',field_details_l)
            #     response['field_details'] = field_details_l
            # else:
            #     contact_field_details_dict = {}
            #
            #     for fields_data in field_details:
            #         contact_field_details_dict['contact'] = contact_details
            #         contact_field_details_dict['field_label'] = fields_data['field_label']
            #         contact_field_details_dict['field_value'] = fields_data['field_value']
            #         contact_field_details_dict['field_type'] = fields_data['field_type']
            #         contact_field_details_dict['created_by'] = created_by
            #         contact_field_details_dict['owned_by'] = owned_by
            #
            #         f_l = PmsTenderSurveyResourceContactFieldDetails.objects.create(**contact_field_details_dict)
            #         contact_field_details_r_dict = {
            #             'id': f_l.id,
            #             'contact': f_l.contact.id,
            #             'field_label': f_l.field_label,
            #             'field_value': f_l.field_value,
            #             'field_type': f_l.field_type,
            #             'created_by': f_l.created_by.username,
            #             'owned_by': f_l.owned_by.username
            #         }
            #         field_details_l.append(contact_field_details_r_dict)
            #     response['field_details'] = field_details_l
            #print('response',response)
            #response = PmsTenderSurveyResourceContactFieldDetails.objects.filter(contact_id=contact_details.id)
            #return response
class TenderSurveyResourceContactDetailsEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    field_details = serializers.ListField(required=False)
    prev_field_details_exist = serializers.CharField(required=False)
    class Meta:
        model = PmsTenderSurveyResourceContactDetails
        fields = ('id', 'tender','designation', 'field_details','prev_field_details_exist',
                  'updated_by')
    def update(self, instance, validated_data):
        prev_field_details_exist = validated_data.get('prev_field_details_exist')
        field_details = validated_data.get('field_details')
        updated_by = validated_data.get('updated_by')
        response = {
            'id': instance.id,
            'tender': instance.tender,
            'designation': instance.designation,
            'status': instance.status,
            'created_by': instance.created_by.username,
            'owned_by': instance.owned_by.username
        }
        field_details_l = list()
        if prev_field_details_exist == 'yes':
            m = PmsTenderSurveyResourceContactFieldDetails.objects.filter(
                    contact=instance).delete()
            for fields_data in field_details:
                f_l = PmsTenderSurveyResourceContactFieldDetails.objects.create(
                    contact=instance,
                    field_label=fields_data['field_label'],
                    field_value=fields_data['field_value'],
                    field_type=fields_data['field_type'],
                    updated_by=updated_by
                )
                contact_field_details_r_dict = {}
                # contact_field_details_r_dict['id'] = f_l.id
                # contact_field_details_r_dict['contact'] = f_l.contact.id
                contact_field_details_r_dict['field_label'] = f_l.field_label
                contact_field_details_r_dict['field_value'] = f_l.field_value
                contact_field_details_r_dict['field_type'] = f_l.field_type
                contact_field_details_r_dict['updated_by'] = f_l.updated_by.username
                field_details_l.append(contact_field_details_r_dict)
        else:
            for fields_data in field_details:
                f_l = PmsTenderSurveyResourceContactFieldDetails.objects.create(
                    contact=instance,
                    field_label=fields_data['field_label'],
                    field_value=fields_data['field_value'],
                    field_type=fields_data['field_type'],
                    updated_by=updated_by
                )
                contact_field_details_r_dict = {}
                # contact_field_details_r_dict['id'] = f_l.id
                # contact_field_details_r_dict['contact'] = f_l.contact.id
                contact_field_details_r_dict['field_label'] = f_l.field_label
                contact_field_details_r_dict['field_value'] = f_l.field_value
                contact_field_details_r_dict['field_type'] = f_l.field_type
                contact_field_details_r_dict['updated_by'] = f_l.updated_by.username
                field_details_l.append(contact_field_details_r_dict)
        response['field_details'] = field_details_l
        return response
class TenderSurveyResourceContactDetailsDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsTenderSurveyResourceContactDetails
        fields = '__all__'

    def update(self, instance, validated_data):
        #print('update')
        instance.status = False
        instance.is_deleted = True
        instance.updated_by = validated_data.get('updated_by')
        instance.save()
        f_d = PmsTenderSurveyResourceContactFieldDetails.objects.filter(contact=instance)
        for e_f_d in f_d:
            #print('f_d',f_d)
            e_f_d.is_deleted = True
            e_f_d.status = False
            e_f_d.updated_by = validated_data.get('updated_by')
            e_f_d.save()
        return instance

#::::::::::: TENDER INITIAL COSTING ::::::::::::::::::::#
class TenderInitialCostingUploadFileSerializer(serializers.ModelSerializer):
    field_label = serializers.CharField(required=False)
    field_value = serializers.CharField(required=False)
    class Meta:
        model=PmsTenderInitialCosting
        fields=('id','tender','document')
    def create(self, validated_data):
        try:
            #tender_initial_costing=PmsTenderInitialCosting.objects.create(**validated_data)
            import pandas as pd
            import xlrd
            df = pd.read_excel(validated_data.get('document'))
            #print("Column headings:")
            #print(df.columns)
            for j in df.columns:
                #print(df[j])
                # tender_initial_costing_label = PmsTenderInitialCostingExcelFieldLabel.\
                #     objects.create(
                #     tender_initial_costing=PmsTenderInitialCosting.objects.get(pk=1),
                #     field_label=j
                #
                # )
                for i in df.index:
                    # tender_initial_costing_field = PmsTenderInitialCostingExcelFieldValue. \
                    #     objects.create(
                    #     tender_initial_costing=PmsTenderInitialCosting.objects.get(pk=1),
                    #     initial_costing_field_label=tender_initial_costing_label,
                    #     field_value=df[j][i]
                    #
                    # )
                    print(df[j][i])

            response_data={
                'id':tender_initial_costing.id,
                'tender':tender_initial_costing.tender,
                'field_label':df.columns,
                'field_value':'',
                'document': tender_initial_costing.document,
            }
            return response_data
        except Exception as e:
            raise APIException({'request_status': 0, 'msg': e})
class TenderInitialCostingAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    status = serializers.BooleanField(default=True)
    field_label_value = serializers.ListField(required=False)
    class Meta:
        model=PmsTenderInitialCosting
        fields=('id','tender','client','tender_notice_no_bid_id_no','name_of_work',
                'is_approved','received_estimate','quoted_rate','difference_in_budget',
                'document','status','created_by','owned_by','field_label_value')
    def create(self, validated_data):
        try:
            #print('validated_data',validated_data)
            field_label_value = validated_data.pop('field_label_value')
            tender_existing_data = PmsTenderInitialCosting.objects.filter(
                tender=validated_data['tender'])
            #print('tender_existing_data',tender_existing_data)
            if tender_existing_data:
                tender_existing_id = PmsTenderInitialCosting.objects.get(
                tender=validated_data['tender'])
                #print('tender_existing_data11111', tender_existing_id)
                PmsTenderInitialCostingExcelFieldLabel.objects.filter(
                    tender_initial_costing=tender_existing_id.id).delete()
                PmsTenderInitialCostingExcelFieldValue.objects.filter(
                    tender_initial_costing=tender_existing_id.id).delete()
                PmsTenderInitialCosting.objects.filter(
                    tender=tender_existing_id.tender).delete()

                tender_initial_costing = PmsTenderInitialCosting.objects.create(
                    **validated_data)
                for each_field_label_value in field_label_value:
                    tender_initial_costing_label = PmsTenderInitialCostingExcelFieldLabel. \
                        objects.create(
                        tender_initial_costing=PmsTenderInitialCosting.objects.get(pk=tender_initial_costing.id),
                        field_label=each_field_label_value['field_label'],
                        created_by = validated_data.get('created_by'),
                        owned_by=validated_data.get('owned_by'),
                    )
                    for field_value in each_field_label_value['field_value']:
                        tender_initial_costing_field = PmsTenderInitialCostingExcelFieldValue. \
                            objects.create(
                            tender_initial_costing=PmsTenderInitialCosting.objects.get(pk=tender_initial_costing.id),
                            initial_costing_field_label=tender_initial_costing_label,
                            field_value=field_value,
                            created_by=validated_data.get('created_by'),
                            owned_by=validated_data.get('owned_by'),

                        )
            else:
                #print('tender_not_exist')
                tender_initial_costing=PmsTenderInitialCosting.objects.create(
                    **validated_data)
                for each_field_label_value in field_label_value:
                    #print('each_field_label_value',each_field_label_value['field_label'])
                    tender_initial_costing_label = PmsTenderInitialCostingExcelFieldLabel.\
                        objects.create(
                        tender_initial_costing=PmsTenderInitialCosting.objects.get(pk=tender_initial_costing.id),
                        field_label=each_field_label_value['field_label'],
                        created_by = validated_data.get('created_by'),
                        owned_by = validated_data.get('owned_by'),
                    )
                    for field_value in each_field_label_value['field_value']:
                        tender_initial_costing_field = PmsTenderInitialCostingExcelFieldValue. \
                            objects.create(
                            tender_initial_costing=PmsTenderInitialCosting.objects.get(pk=tender_initial_costing.id),
                            initial_costing_field_label=tender_initial_costing_label,
                            field_value=field_value,
                            created_by=validated_data.get('created_by'),
                            owned_by=validated_data.get('owned_by'),

                        )
                    #print(df[j][i])
            response_data={
                'id':tender_initial_costing.id,
                'tender':tender_initial_costing.tender,
                'client': tender_initial_costing.client,
                'tender_notice_no_bid_id_no':tender_initial_costing.tender_notice_no_bid_id_no,
                'name_of_work':tender_initial_costing.name_of_work,
                'is_approved':tender_initial_costing.is_approved,
                'received_estimate': tender_initial_costing.received_estimate,
                'quoted_rate': tender_initial_costing.quoted_rate,
                'difference_in_budget': tender_initial_costing.difference_in_budget,
                'document': tender_initial_costing.document,
                'status':tender_initial_costing.status,
                'created_by':tender_initial_costing.created_by,
                'owned_by':tender_initial_costing.owned_by,
                #'field_label_value':field_label_value
            }
            return response_data
        except Exception as e:
            raise APIException({'request_status': 0, 'msg': e})
class TenderInitialCostingDetailsSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    status = serializers.BooleanField(default=True)
    field_label_value = serializers.ListField(required=False)
    class Meta:
        model = PmsTenderInitialCosting
        fields = ('id', 'tender', 'client', 'tender_notice_no_bid_id_no', 'name_of_work',
                  'is_approved', 'received_estimate', 'quoted_rate', 'difference_in_budget',
                  'document', 'status', 'created_by', 'owned_by', 'field_label_value')

#-------------------------PmsTenderTabDocuments-------------------------------#
class TenderEligibilityFieldDocumentAddSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsTenderEligibilityFieldsByType
        fields = ("id", "tender", "tender_eligibility","document", "updated_by")
class TenderCheckTabDocumentUploadAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    status = serializers.BooleanField(default=True)
    is_upload_document=serializers.BooleanField(default=True)
    reason_for_no_documentation=serializers.CharField(required=False)
    class Meta:
        model = PmsTenderTabDocuments
        fields = ("id", "is_upload_document","tender","reason_for_no_documentation",
                  "created_by", "owned_by", 'status')
    def create(self, validated_data):
        try:
            response = dict()
            #print('validated_data',validated_data)
            exist_tab_document = PmsTenderTabDocuments.objects.filter(tender=validated_data.get('tender'))
            #print('exist_tab_document',exist_tab_document)
            if exist_tab_document:
                #print('exist')
                for e_exist_tab_document in exist_tab_document:
                    e_exist_tab_document.is_upload_document = validated_data.get('is_upload_document')
                    e_exist_tab_document.reason_for_no_documentation = validated_data.get('reason_for_no_documentation')
                    e_exist_tab_document.updated_by = validated_data.get('created_by')
                    e_exist_tab_document.save()
                    response = {
                        'id': e_exist_tab_document.id,
                        'tender': e_exist_tab_document.tender,
                        'is_upload_document':e_exist_tab_document.is_upload_document,
                        'reason_for_no_documentation':e_exist_tab_document.reason_for_no_documentation,
                        'created_by':e_exist_tab_document.created_by,
                        'owned_by':e_exist_tab_document.owned_by
                    }
                return response
            else:
                #print('not exist')
                #PmsTenderTabDocuments.objects.create(**validated_data)
                return PmsTenderTabDocuments.objects.create(**validated_data)

        except Exception as e:
            raise APIException(
                {"msg": e, "request_status": 0}
            )
class TenderTabDocumentDocumentsAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    tender_eligibility = serializers.CharField(required=False)
    tender_eligibility_type = serializers.CharField(required=False)
    class Meta:
        model = PmsTenderTabDocumentsDocuments
        fields = ("id","tender","tender_eligibility","tender_eligibility_type","document_date_o_s",
                  "document_name","tab_document","created_by", "owned_by")
    def create(self, validated_data):
        try:
            #print('validated_data',validated_data)
            el_type = validated_data.pop('tender_eligibility_type')
            el_type_id_d = PmsTenderEligibility.objects.filter(
                type=el_type,tender=validated_data.get('tender'))
            #print('el_type_id_d',el_type_id_d)
            for el_type_id_d in el_type_id_d:
                el_type_id = el_type_id_d.id
            #print('el_type_id', el_type_id)
            return PmsTenderTabDocumentsDocuments.objects.create(
                tender = validated_data.get('tender'),
                tender_eligibility_id = el_type_id,
                document_date_o_s = validated_data.get('document_date_o_s'),
                document_name = validated_data.get('document_name'),
                tab_document = validated_data.get('tab_document'),
                created_by = validated_data.get('created_by'),
                owned_by = validated_data.get('owned_by')
            )
        except Exception as e:
            raise APIException(
                {"msg": e, "request_status": 0}
            )
class TenderTabDocumentDocumentsListSerializer(serializers.ModelSerializer):
    type=serializers.SerializerMethodField(required=False)
    def get_type(self,PmsTenderTabDocumentsDocuments):
        return PmsTenderEligibility.objects.only('type').get(
            id=PmsTenderTabDocumentsDocuments.tender_eligibility.id).type
    class Meta:
        model = PmsTenderTabDocumentsDocuments
        fields = '__all__'
        extra_fields=('type',)

class TenderTabDocumentsListSerializer(serializers.ModelSerializer):
    type=serializers.SerializerMethodField(required=False)
    def get_type(self,PmsTenderTabDocumentsDocuments):
        return PmsTenderEligibility.objects.only('type').get(
            id=PmsTenderTabDocumentsDocuments.tender_eligibility.id).type
    class Meta:
        model = PmsTenderTabDocumentsDocuments
        fields = '__all__'
        extra_fields=('type',)

class TenderTabDocumentDocumentsEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    tender_eligibility = serializers.CharField(required=False)
    tender_eligibility_type = serializers.CharField(required=False)
    class Meta:
        model=PmsTenderTabDocumentsDocuments
        fields = ("id", "tender", "tender_eligibility", "tender_eligibility_type",
                  "document_date_o_s","document_name", "tab_document", "updated_by")
    def update(self, instance, validated_data):
        el_type = validated_data.pop('tender_eligibility_type')
        el_type_id_d = PmsTenderEligibility.objects.filter(
            type=el_type, tender=validated_data.get('tender'))
        # print('el_type_id_d',el_type_id_d)
        if el_type_id_d:
            for el_type_id_d in el_type_id_d:
                el_type_id = el_type_id_d.id
            instance.tender_eligibility_id = el_type_id
            instance.document_date_o_s = validated_data.get('document_date_o_s')
            instance.document_name = validated_data.get('document_name')
            instance.updated_by = validated_data.get('updated_by')
            existing_image = './media/' + str(instance.tab_document)
            print('existing_image',existing_image)
            if validated_data.get('tab_document'):
                if os.path.isfile(existing_image):
                    os.remove(existing_image)
                instance.tab_document = validated_data.get('tab_document')
            instance.save()
        return instance
class TenderTabDocumentDocumentsDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsTenderTabDocumentsDocuments
        fields = '__all__'
    def update(self, instance, validated_data):
        instance.is_deleted = True
        instance.updated_by = validated_data.get('updated_by')
        instance.save()
        return instance

#::::::::::::::::::: TENDER APPROVAL :::::::::::::#
class TenderApprovalAddOrUpdateSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    is_approved = serializers.BooleanField(default=True)
    reject_reason = serializers.CharField(required=False)
    class Meta:
        model = PmsTenderApproval
        fields = ("id", "is_approved", "tender", "reject_reason",
                  "created_by", "owned_by")
    def create(self, validated_data):
        try:
            response = dict()
            # print('validated_data',validated_data)
            exist_tender_approval = PmsTenderApproval.objects.filter(
                tender=validated_data.get('tender'))
            # print('exist_tab_document',exist_tab_document)
            if exist_tender_approval:
                # print('exist')
                for e_exist_tender_approval in exist_tender_approval:
                    e_exist_tender_approval.is_approved = validated_data.get('is_approved')
                    e_exist_tender_approval.reject_reason = validated_data.get(
                        'reject_reason')
                    e_exist_tender_approval.updated_by = validated_data.get('created_by')
                    e_exist_tender_approval.save()
                    response = {
                        'id': e_exist_tender_approval.id,
                        'tender': e_exist_tender_approval.tender,
                        'is_approved': e_exist_tender_approval.is_approved,
                        'reject_reason': e_exist_tender_approval.reject_reason,
                        'created_by': e_exist_tender_approval.created_by,
                        'owned_by': e_exist_tender_approval.owned_by
                    }
                return response
            else:
                # print('not exist')
                # PmsTenderTabDocuments.objects.create(**validated_data)
                return PmsTenderApproval.objects.create(**validated_data)

        except Exception as e:
            raise APIException(
                {"msg": e, "request_status": 0}
            )
#:::::::::::::::::::Pms Tender Status :::::::::::::::::::::::::#
class TenderStatusAddOrUpdateSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    is_awarded = serializers.BooleanField(default=True)
    date_of_awarding = serializers.CharField(required=False,allow_null=True)
    loi_issued_on = serializers.CharField(required=False)
    participents_field_label_value = serializers.ListField(required=False)
    comparison_field_label_value = serializers.ListField(required=False)
    position = serializers.CharField(required=False)
    reason = serializers.CharField(required=False)
    percentage_of_preference = serializers.CharField(required=False)
    project_id = serializers.CharField(required=False)
    tender_status = serializers.CharField(required=False)

    class Meta:
        model = PmsTenderStatus
        fields = ("id", "is_awarded", "tender","date_of_awarding","loi_issued_on",
                  "participents_field_label_value","comparison_field_label_value"
                  ,"position","reason","percentage_of_preference","created_by",
                  "owned_by",'tender_status','updated_by','project_id')
    def create(self, validated_data):
        try:
            response = dict()
            exist_tender_awarded = PmsTenderStatus.objects.filter(
                tender=validated_data.get('tender'))
            #print('exist_tender_awarded',exist_tender_awarded)
            is_awarded = validated_data.get('is_awarded')
            p_field_label_value = validated_data.pop('participents_field_label_value')
            c_field_label_value = validated_data.pop('comparison_field_label_value')
            if exist_tender_awarded:
                if is_awarded:
                    #print('is_awarded')
                    for e_exist_tender_awarded in exist_tender_awarded:
                        e_exist_tender_awarded.is_awarded = is_awarded
                        e_exist_tender_awarded.date_of_awarding = datetime.datetime.strptime(validated_data.pop('date_of_awarding'), "%Y-%m-%dT%H:%M:%S.%fZ")
                        e_exist_tender_awarded.loi_issued_on = datetime.datetime.strptime(validated_data.pop('loi_issued_on'), "%Y-%m-%dT%H:%M:%S.%fZ")
                        e_exist_tender_awarded.position = None
                        e_exist_tender_awarded.reason = None
                        e_exist_tender_awarded.percentage_of_preference = None
                        e_exist_tender_awarded.updated_by = validated_data.get('created_by')
                        e_exist_tender_awarded.save()
                    project_details=PmsProjects.objects.create(
                        tender = validated_data.get('tender'),
                        created_by = validated_data.get('created_by'),
                        owned_by = validated_data.get('created_by')
                    )
                    # print(type(project_details.id))
                    project_id=project_details.id
                    response_data = {
                        'tender': e_exist_tender_awarded.tender,
                        'is_awarded': e_exist_tender_awarded.is_awarded,
                        'date_of_awarding': e_exist_tender_awarded.date_of_awarding,
                        'loi_issued_on': e_exist_tender_awarded.loi_issued_on,
                        'created_by': e_exist_tender_awarded.created_by,
                        'owned_by': e_exist_tender_awarded.owned_by,
                        'project_id': project_id,
                    }
                    # print('response_data', response_data)
                else:
                    for e_exist_tender_awarded in exist_tender_awarded:
                        e_exist_tender_awarded.is_awarded = is_awarded
                        e_exist_tender_awarded.date_of_awarding = None
                        e_exist_tender_awarded.loi_issued_on = None
                        e_exist_tender_awarded.position = validated_data.pop('position')
                        e_exist_tender_awarded.reason = validated_data.pop('reason')
                        e_exist_tender_awarded.percentage_of_preference = validated_data.pop('percentage_of_preference')
                        e_exist_tender_awarded.updated_by = validated_data.get('created_by')
                        e_exist_tender_awarded.save()
                    response_data = {
                        'id': e_exist_tender_awarded.id,
                        'tender': e_exist_tender_awarded.tender,
                        'is_awarded': e_exist_tender_awarded.is_awarded,
                        'position': e_exist_tender_awarded.position,
                        'reason': e_exist_tender_awarded.reason,
                        'percentage_of_preference': e_exist_tender_awarded.percentage_of_preference,
                        'created_by': e_exist_tender_awarded.created_by.id,
                        'owned_by': e_exist_tender_awarded.owned_by.id,
                    }

                PmsTenderStatusParticipentsFieldValue.objects.filter(
                    tender_status=e_exist_tender_awarded.id).delete()
                PmsTenderStatusParticipentsFieldLabel.objects.filter(
                    tender_status=e_exist_tender_awarded.id).delete()
                #print('participents delete')

                PmsTenderStatusComparisonChartFieldValue.objects.filter(
                    tender_status=e_exist_tender_awarded.id).delete()
                cf1 = PmsTenderStatusComparisonChartFieldLabel.objects.filter(
                    tender_status=e_exist_tender_awarded.id).delete()
                #print('ComparisonChart delete')

                # **************   Participents *******************#
                for each_field_label_value in p_field_label_value:
                    #print('e_exist_tender_awarded.id', e_exist_tender_awarded.id)
                    p_s_label = PmsTenderStatusParticipentsFieldLabel. \
                        objects.create(
                        tender_status=e_exist_tender_awarded,
                        field_label=each_field_label_value['field_label'],
                        created_by=validated_data.get('created_by'),
                        owned_by=validated_data.get('owned_by'),
                    )
                    #print('p_s_label',p_s_label)
                    for field_value in each_field_label_value['field_value']:
                        PmsTenderStatusParticipentsFieldValue. \
                            objects.create(
                            tender_status=e_exist_tender_awarded,
                            participents_field_label=p_s_label,
                            field_value=field_value,
                            created_by=validated_data.get('created_by'),
                            owned_by=validated_data.get('owned_by'),

                        )
                #print('Participents')
                # ************** Comparison *******************#
                for each_field_label_value in c_field_label_value:
                    p_s_label = PmsTenderStatusComparisonChartFieldLabel. \
                        objects.create(
                        tender_status=e_exist_tender_awarded,
                        field_label=each_field_label_value['field_label'],
                        created_by=validated_data.get('created_by'),
                        owned_by=validated_data.get('owned_by'),
                    )
                    for field_value in each_field_label_value['field_value']:
                        PmsTenderStatusComparisonChartFieldValue. \
                            objects.create(
                            tender_status=e_exist_tender_awarded,
                            status_comparison_field_label=p_s_label,
                            field_value=field_value,
                            created_by=validated_data.get('created_by'),
                            owned_by=validated_data.get('owned_by'),
                        )
                #print('Comparison')

                return response_data
            else:

                #print('validated_data',validated_data)
                pmsTenderStatus = PmsTenderStatus.objects.create(
                    tender = validated_data.get('tender'),
                    is_awarded = True,
                    date_of_awarding = datetime.datetime.strptime(validated_data.get('date_of_awarding'), "%Y-%m-%dT%H:%M:%S.%fZ"),
                    loi_issued_on = datetime.datetime.strptime(validated_data.get('loi_issued_on'), "%Y-%m-%dT%H:%M:%S.%fZ")
                )
                # print('pmsTenderStatus',pmsTenderStatus)

                if is_awarded:
                    project_details=PmsProjects.objects.create(
                        tender=validated_data.get('tender'),
                        created_by=validated_data.get('created_by'),
                        owned_by=validated_data.get('created_by')
                    )
                    # print("projct_details:::::",project_details)
                    project_id = project_details.id
                    response_data = {
                        'id': pmsTenderStatus.id,
                        'tender': pmsTenderStatus.tender,
                        'is_awarded': pmsTenderStatus.is_awarded,
                        #'tender_status': pmsTenderStatus.tender_status,
                        'date_of_awarding': pmsTenderStatus.date_of_awarding,
                        'loi_issued_on': pmsTenderStatus.loi_issued_on,
                        'created_by': pmsTenderStatus.created_by,
                        'owned_by': pmsTenderStatus.owned_by,
                        'project_id':project_id,
                        # 'field_label_value':field_label_value
                    }
                else:
                    response_data = {
                        'id': pmsTenderStatus.id,
                        'tender': pmsTenderStatus.tender,
                        'is_awarded': pmsTenderStatus.is_awarded,
                        'position': pmsTenderStatus.position,
                        'reason': pmsTenderStatus.reason,
                        'percentage_of_preference': pmsTenderStatus.percentage_of_preference,
                        'created_by': pmsTenderStatus.created_by,
                        'owned_by': pmsTenderStatus.owned_by,
                    }
                # **************   Participents *******************#
                for each_field_label_value in p_field_label_value:
                    p_s_label = PmsTenderStatusParticipentsFieldLabel. \
                        objects.create(
                        tender_status=pmsTenderStatus,
                        field_label=each_field_label_value['field_label'],
                        created_by=validated_data.get('created_by'),
                        owned_by=validated_data.get('owned_by'),
                    )
                    for field_value in each_field_label_value['field_value']:
                        PmsTenderStatusParticipentsFieldValue. \
                            objects.create(
                            tender_status=pmsTenderStatus,
                            participents_field_label=p_s_label,
                            field_value=field_value,
                            created_by=validated_data.get('created_by'),
                            owned_by=validated_data.get('owned_by'),

                        )
                #print('Participents')
                # ************** Comparison *******************#
                for each_field_label_value in c_field_label_value:
                    p_s_label = PmsTenderStatusComparisonChartFieldLabel. \
                        objects.create(
                        tender_status=pmsTenderStatus,
                        field_label=each_field_label_value['field_label'],
                        created_by=validated_data.get('created_by'),
                        owned_by=validated_data.get('owned_by'),
                    )
                    for field_value in each_field_label_value['field_value']:
                        PmsTenderStatusComparisonChartFieldValue. \
                            objects.create(
                            tender_status=pmsTenderStatus,
                            status_comparison_field_label=p_s_label,
                            field_value=field_value,
                            created_by=validated_data.get('created_by'),
                            owned_by=validated_data.get('owned_by'),
                        )
                #print('Comparison')
                return response_data

        except Exception as e:
            # raise e
            raise APIException(
                {"msg": e, "request_status": 0}
            )
            
class TenderStatusDocumentAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    tender_status = serializers.CharField(required=False)
    class Meta:
        model = PmsTenderStatusDocuments
        fields = ('id','tender','tender_status', 'document_name', 'document','created_by', 'owned_by')

    def create(self,validated_data):
        try:
            #print('gdfgdfg')
            #print('validated_data', validated_data)
            exist_tender_awarded = PmsTenderStatus.objects.filter(
                tender=validated_data.get('tender'))
            #print('exist_tender_awarded',dir(exist_tender_awarded))
            if exist_tender_awarded :
                validated_data['tender_status'] = PmsTenderStatus.objects.get(tender=validated_data.get('tender'))
                #print('validated_data1', validated_data)
                return PmsTenderStatusDocuments.objects.create(**validated_data)
        except Exception as e:
            raise APIException(
                {"msg": e, "request_status": 0}
            )
class TenderStatusDocumentEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsTenderStatusDocuments
        fields = ('id', 'tender','tender_status', 'document_name','updated_by',)
    def update(self, instance,validated_data):
        exist_tender_awarded = PmsTenderStatus.objects.filter(
            tender=validated_data.get('tender'))
        if exist_tender_awarded:
            instance.document_name = validated_data.get('document_name')
            instance.updated_by = validated_data.get('updated_by')
        return instance
class TenderStatusDocumentDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsTenderStatusDocuments
        fields = '__all__'
    def update(self, instance, validated_data):
        instance.is_deleted = True
        instance.save()
        return instance

#------------------------PmsTenderTabDocumentsPrice----------------------#
class TenderTabDocumentPriceAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    status = serializers.BooleanField(default=True)
    class Meta:
        model=PmsTenderTabDocumentsPrice
        fields=('id','tender','document_date_o_s','document_name','tab_document',
                "created_by", "owned_by", 'status')
class TenderTabDocumentPriceEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsTenderTabDocumentsPrice
        fields = ( 'id','tender','document_date_o_s', 'document_name', 'tab_document','updated_by')
    def update(self, instance, validated_data):
        instance.tender = validated_data.get('tender')
        instance.document_date_o_s = validated_data.get('document_date_o_s')
        instance.document_name = validated_data.get('document_name')
        instance.updated_by = validated_data.get('updated_by')
        existing_image = './media/' + str(instance.tab_document)
        #print('existing_image', existing_image)
        if validated_data.get('tab_document'):
            if os.path.isfile(existing_image):
                os.remove(existing_image)
            instance.tab_document = validated_data.get('tab_document')
        instance.save()
        return instance
class TenderTabDocumentPriceDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsTenderTabDocumentsPrice
        fields = '__all__'
    def update(self, instance, validated_data):
        instance.status = False
        instance.is_deleted = True
        instance.updated_by = validated_data.get('updated_by')
        instance.save()
        return instance

class TenderTpeMasterAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    status = serializers.BooleanField(default=True)
    class Meta:
        model = PmsTenderTypeMaster
        fields = '__all__'
