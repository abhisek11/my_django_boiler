from django.db import models
from django.contrib.auth.models import User
from dynamic_media import get_directory_path
from django_mysql.models import EnumField
from validators import validate_file_extension
from core.models import TCoreUnit
import datetime
import time
from pms.models.module_project import *
from pms.models.module_machineries import *
from pms.models.module_external_user import *
# from pms.models.module_execution import *

#::::: PROJECT SITE MANAGEMENT SITE TYPE :::::::::::::::#
class PmsSiteTypeProjectSiteManagement(models.Model):
    name = models.CharField(max_length=200, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='site_type_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='site_type_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='site_type_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_site_type_project_site_management'

#:::::::::: PROJECT SITE MANAGEMENT SITE :::::::::::#
class PmsSiteProjectSiteManagement(models.Model):
    name = models.CharField(max_length=200, blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    # latitude = models.DecimalField(max_digits=40, decimal_places=16, blank=True, null=True)
    # longitude = models.DecimalField(max_digits=40, decimal_places=16, blank=True, null=True)
    site_latitude=models.DecimalField(max_digits=40, decimal_places=16, blank=True, null=True)
    site_longitude=models.DecimalField(max_digits=40, decimal_places=16, blank=True, null=True)
    office_latitude=models.DecimalField(max_digits=40, decimal_places=16, blank=True, null=True)
    office_longitude=models.DecimalField(max_digits=40, decimal_places=16, blank=True, null=True)
    gest_house_latitude=models.DecimalField(max_digits=40, decimal_places=16, blank=True, null=True)
    gest_house_longitude=models.DecimalField(max_digits=40, decimal_places=16, blank=True, null=True)
    type = models.ForeignKey(PmsSiteTypeProjectSiteManagement, related_name='project_site_management_type',
                             on_delete=models.CASCADE, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    gst_no = models.CharField(max_length=255, blank=True, null=True)
    geo_fencing_area = models.CharField(max_length=255, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='project_site_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='project_site_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='project_site_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_site_project_site_management'

#::::::::::: ADD TENDER TYPE ::::::::::::#
'''
    Model Added and also added the forign key field to PmsTenders
    By Rupam Hazra on 20.01.2020 for tender survey.
'''
class PmsTenderTypeMaster(models.Model):
    name = models.CharField(max_length=100)
    status = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='t_type_created_by',
                                   on_delete=models.CASCADE,blank=True,null=True)
    owned_by = models.ForeignKey(User, related_name='t_type_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='t_type_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'pms_tender_type'

#:::::::::: ADD NEW TENDER TABLE ::::::::#
class PmsTenders(models.Model):
    tender_g_id = models.CharField(max_length=50,unique=True)
    site_location = models.ForeignKey(PmsSiteProjectSiteManagement,
                                      related_name='t_s_s_p_site_id',
                                      on_delete=models.CASCADE,
                                      blank=True,
                                      null=True
                                      )
    tender_final_date = models.DateTimeField(auto_now_add=False,blank=True, null=True)
    tender_opened_on = models.DateTimeField(auto_now_add=False,blank=True, null=True)
    tender_added_by = models.CharField(max_length=100, blank=True, null=True)
    tender_received_on = models.DateTimeField(auto_now_add=False,blank=True, null=True)
    tender_aasigned_to = models.CharField(max_length=100, blank=True, null=True)
    tender_type = models.ForeignKey(PmsTenderTypeMaster,
                                      related_name='t_type_id',
                                      on_delete=models.CASCADE,
                                      blank=True,
                                      null=True
                                      )
    status = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='t_created_by',
                                   on_delete=models.CASCADE,blank=True,null=True)
    owned_by = models.ForeignKey(User, related_name='t_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='t_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'pms_tenders'

#:::::::::: TENDER DOCUMENT TABLE ::::::::#
class PmsTenderDocuments(models.Model):
    tender = models.ForeignKey(PmsTenders,
                               related_name='t_d_tender_id',
                               on_delete=models.CASCADE,
                               blank=True,null=True)
    document_name = models.CharField(max_length=200,blank=True,null=True)
    tender_document = models.FileField(upload_to=get_directory_path,
                                        default=None,
                                        blank=True, null=True,
                                        validators=[validate_file_extension]
                                       )
    status = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='t_d_created_by',
                                   on_delete=models.CASCADE,blank=True,null=True)
    owned_by = models.ForeignKey(User, related_name='t_d_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='t_d_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'pms_tender_documents'

#:::::::::: TENDER  ELIGIBILITY  TABLE ::::::::#
class PmsTenderEligibility(models.Model):
    tender = models.ForeignKey(PmsTenders,
                                  related_name='t_e_tender_id',
                                  on_delete=models.CASCADE,
                                  blank=True,
                                  null=True
                                  )
    type = EnumField(choices=['technical', 'financial', 'special'])
    ineligibility_reason = models.TextField(blank=True, null=True)
    eligibility_status = models.BooleanField(default=True)
    status = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='t_e_created_by',
                                   on_delete=models.CASCADE,blank=True,null=True)
    owned_by = models.ForeignKey(User, related_name='t_e_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='t_e_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'pms_tender_eligibility'
        unique_together = ('type', 'tender')

#:::::::::: TENDER  ELIGIBILITY FIELDS BY TYPE TABLE ::::::::#
class PmsTenderEligibilityFieldsByType(models.Model):
    tender = models.ForeignKey(PmsTenders,
                                  related_name='t_e_f_tender_id',
                                  on_delete=models.CASCADE,
                                  blank=True,
                                  null=True
                                  )
    tender_eligibility = models.ForeignKey(PmsTenderEligibility,
                                  related_name='eligibility_id',
                                  on_delete=models.CASCADE,
                                  blank=True,
                                  null=True
                                  )
    field_label = models.TextField(blank=True, null=True)
    field_value = models.TextField(blank=True, null=True)
    eligible = models.BooleanField(default=True)
    document = models.FileField(upload_to=get_directory_path,
                                default=None,
                                blank=True, null=True,
                                validators=[validate_file_extension]
                                )
    status = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='t_e_f_created_by',
                                   on_delete=models.CASCADE,blank=True,null=True)
    owned_by = models.ForeignKey(User, related_name='t_e_f_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='t_e_f_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'pms_tender_eligibility_fields_by_type'

#:::::::::: TENDER VENDORS TABLE ::::::::#
class PmsTenderPartners(models.Model):
    tender = models.ForeignKey(PmsTenders,
                               related_name='t_v_tender_id',
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True
                               )
    name = models.CharField(max_length=80,blank=True,null=True)
    contact = models.CharField(max_length=30, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    status = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='t_v_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='t_v_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='t_v_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_tender_partners'

#:::::::::: TENDER  BIDDER TYPE TABLE ::::::::#
class PmsTenderBidderType(models.Model):
    type_of_partner = (
        (1, 'lead_partner'),
        (2, 'other_partner')
    )
    tender = models.ForeignKey(PmsTenders,
                                  related_name='t_b_t_tender_id',
                                  on_delete=models.CASCADE,
                                  blank=True,
                                  null=True
                                  )
    bidder_type = EnumField(choices=['joint_venture', 'individual'])
    type_of_partner = models.IntegerField(choices=type_of_partner,null=True,blank=True)
    responsibility = EnumField(choices=['technical', 'financial','technical_and_financial'],null=True,
                                                                    blank=True,)
    profit_sharing_ratio_actual_amount = models.FloatField(null=True, blank=True, default=None)
    profit_sharing_ratio_tender_specific_amount = models.FloatField(null=True,
                                                                    blank=True,
                                                                    default=None)
    status = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='t_b_t_created_by',
                                   on_delete=models.CASCADE,blank=True,null=True)
    owned_by = models.ForeignKey(User, related_name='t_b_t_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='t_b_t_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'pms_tender_bidder_type'

#:::::::::: TENDER  BIDDER TYPE TABLE ::::::::#
class PmsTenderBidderTypePartnerMapping(models.Model):
    tender_bidder_type = models.ForeignKey(PmsTenderBidderType,on_delete=models.CASCADE,
                                  blank=True,null=True)
    tender_partner = models.ForeignKey(PmsTenderPartners,on_delete=models.CASCADE,
                                  blank=True,null=True)
    status = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='t_b_t_v_m_created_by',
                                   on_delete=models.CASCADE,blank=True,null=True)
    owned_by = models.ForeignKey(User, related_name='t_b_t_v_m_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'pms_tender_bidder_type_partner_mapping'

#:::::::::: TENDER APPROVAL ::::::::#
class PmsTenderApproval(models.Model):
    tender = models.ForeignKey(PmsTenders,
                               related_name='t_a_tender_id',
                               on_delete=models.CASCADE,
                               blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    reject_reason = models.TextField(blank=True, null=True)
    status = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='t_a_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='t_a_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='t_a_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_tender_approval'

##################################################################################
########################### SURVEY TAB SECTION ###################################
##################################################################################

#:::::::::: TENDER SURVEY SITE PHOTOS ::::::::#
class PmsTenderSurveySitePhotos(models.Model):
    tender = models.ForeignKey(PmsTenders,
                                  related_name='t_s_s_p_tender_id',
                                  on_delete=models.CASCADE,
                                  blank=True,
                                  null=True
                                  )
    latitude = models.CharField(max_length=200, blank=True, null=True)
    longitude = models.CharField(max_length=200, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    additional_notes = models.TextField(blank=True, null=True)
    document_name = models.CharField(max_length=100, blank=True, null=True)
    document = models.FileField(upload_to=get_directory_path,
                                       default=None,
                                       blank=True, null=True,
                                       validators=[validate_file_extension]
                                       )
    status = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='t_s_s_p_created_by',
                                   on_delete=models.CASCADE,blank=True,null=True)
    owned_by = models.ForeignKey(User, related_name='t_s_s_p_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='t_s_s_p_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'pms_tender_survey_site_photos'

#::: TENDER SURVEY COORDINATES SITE COORDINATE ::::#
class PmsTenderSurveyCoordinatesSiteCoordinate(models.Model):
    tender = models.ForeignKey(PmsTenders,
                                  related_name='t_s_c_s_c_tender_id',
                                  on_delete=models.CASCADE,
                                  blank=True,
                                  null=True
                                  )
    name = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.CharField(max_length=200, blank=True, null=True)
    longitude = models.CharField(max_length=200, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    status = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='t_s_c_s_c_created_by',
                                   on_delete=models.CASCADE,blank=True,null=True)
    owned_by = models.ForeignKey(User, related_name='t_s_c_s_c_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='t_s_c_s_c_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'pms_tender_survey_coordinates_site_coordinate'

#::: TENDER SURVEY MATERIALS ::::#

# class MaterialTypeMaster(models.Model):
#     name=models.CharField(max_length=100, blank=True, null=True)
#     is_deleted = models.BooleanField(default=False)
#     created_by = models.ForeignKey(User, related_name='m_t_m_created_by',
#                                    on_delete=models.CASCADE,blank=True,null=True)
#     owned_by = models.ForeignKey(User, related_name='m_t_m_owned_by',
#                                  on_delete=models.CASCADE, blank=True, null=True)
#     updated_by = models.ForeignKey(User, related_name='m_t_m_updated_by',
#                                    on_delete=models.CASCADE, blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     def __str__(self):
#         return str(self.id)
#     class Meta:
#         db_table = 'pms_material_type_master'

#[this table Common for resource->material,coordinates]
class Materials(models.Model):
    # mat_type= models.ForeignKey(PmsExecutionPurchasesRequisitionsTypeMaster,related_name='t_s_m_mat_type',
    #                                on_delete=models.CASCADE,blank=True,null=True)
    type_code = models.CharField(max_length=100, blank=True, null=True)#Added by Koushik on 2020-01-08#
    mat_code = models.CharField(max_length=50)
    name = models.CharField(max_length=200, blank=True, null=True)
    '''
        Below two field Added By Rupam Hazra on 20.01.2020 for tender servey
    '''
    is_master = models.BooleanField(default=False)
    is_crusher = models.BooleanField(default=False)
    description = models.TextField(blank=True,null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='t_s_m_created_by',
                                   on_delete=models.CASCADE,blank=True,null=True)
    owned_by = models.ForeignKey(User, related_name='t_s_m_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='t_s_m_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'pms_materials'
class MaterialsUnitMapping(models.Model):
    material = models.ForeignKey(Materials, related_name='m_u_m_material',
                                 on_delete=models.CASCADE, blank=True, null=True)
    unit = models.ForeignKey(TCoreUnit, related_name='m_u_m_unit',
                             on_delete=models.CASCADE, blank=True, null=True)
    #is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='m_u_m_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='m_u_m_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='m_u_m_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'pms_materials_unit_mapping'

#::: TENDER SURVEY RESOURCE MATERIAL ::::#
class PmsTenderSurveyResourceMaterial(models.Model):
    tender = models.ForeignKey(PmsTenders,
                                  related_name='t_s_r_m_tender_id',
                                  on_delete=models.CASCADE,
                                  blank=True,
                                  null=True
                                  )
    tender_survey_material = models.ForeignKey(Materials,
                                               related_name='t_s_r_m_material_id',
                                               on_delete=models.CASCADE,
                                               blank=True,
                                               null=True
                                               )
    supplier_name = models.CharField(max_length=100, blank=True, null=True)
    rate = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=3)
    latitude = models.CharField(max_length=200, blank=True, null=True)
    longitude = models.CharField(max_length=200, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    status = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='t_s_r_m_created_by',
                                   on_delete=models.CASCADE,blank=True,null=True)
    owned_by = models.ForeignKey(User, related_name='t_s_r_m_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='t_s_r_m_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'pms_tender_survey_resource_material'
class PmsTenderSurveyResourceMaterialDocument(models.Model):
    survey_resource_material = models.ForeignKey(PmsTenderSurveyResourceMaterial,
                                                 related_name='t_s_r_material_id',
                                                 on_delete=models.CASCADE,
                                                 blank=True,
                                                 null=True
                                                 )
    document_name = models.CharField(max_length=100, blank=True, null=True)
    document = models.FileField(upload_to=get_directory_path,
                                default=None,
                                blank=True, null=True,
                                validators=[validate_file_extension]
                                )

    status = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='t_s_r_m_d_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='t_s_r_m_d_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='t_s_r_m_d_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_tender_survey_resource_material_document'

#::: TENDER SURVEY RESOURCE ESTABLISHMENT ::::#
class PmsTenderSurveyResourceEstablishment(models.Model):
    tender = models.ForeignKey(PmsTenders,
                                  related_name='t_s_r_e_tender_id',
                                  on_delete=models.CASCADE,
                                  blank=True,
                                  null=True
                                  )
    name = models.CharField(max_length=100, blank=True, null=True)
    details = models.TextField(blank=True, null=True)
    latitude = models.CharField(max_length=200, blank=True, null=True)
    longitude = models.CharField(max_length=200, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    status = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='t_s_r_e_created_by',
                                   on_delete=models.CASCADE,blank=True,null=True)
    owned_by = models.ForeignKey(User, related_name='t_s_r_e_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='t_s_r_e_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'pms_tender_survey_resource_establishment'

#::: TENDER SURVEY DOCUMENT COMMON FOR THEREE TAB
# establishment,hydrological data,contractors/vendors ::::#
class PmsTenderSurveyDocument(models.Model):
    tender = models.ForeignKey(PmsTenders,
                               related_name='t_s_d_tender_id',
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True
                               )
    model_class = models.CharField(max_length=100, blank=True, null=True)
    module_id = models.IntegerField(blank=True, null=True)
    document_name = models.CharField(max_length=100,blank=True, null=True)
    document = models.FileField(upload_to=get_directory_path,
                                       default=None,
                                       blank=True, null=True,
                                       validators=[validate_file_extension]
                                       )
    status = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='t_s_d_created_by',
                                   on_delete=models.CASCADE,blank=True,null=True)
    owned_by = models.ForeignKey(User, related_name='t_s_d_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='t_s_d_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'pms_tender_survey_document'

#::: TENDER SURVEY RESOURCE HYDROLOGICAL ::::#
class PmsTenderSurveyResourceHydrological(models.Model):
    tender = models.ForeignKey(PmsTenders,
                                  related_name='t_s_r_h_tender_id',
                                  on_delete=models.CASCADE,
                                  blank=True,
                                  null=True
                                  )
    name = models.CharField(max_length=100,blank=True, null=True)
    details = models.TextField(blank=True, null=True)
    latitude = models.CharField(max_length=200, blank=True, null=True)
    longitude = models.CharField(max_length=200, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    status = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='t_s_r_h_created_by',
                                   on_delete=models.CASCADE,blank=True,null=True)
    owned_by = models.ForeignKey(User, related_name='t_s_r_h_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='t_s_r_h_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'pms_tender_resource_hydrological'

#::: TENDER SURVEY RESOURCE CONTRACTORS OR VENDORS CONTRACTOR ::::#
class PmsTenderSurveyResourceContractorsOVendorsContractor(models.Model):
    tender = models.ForeignKey(PmsTenders,
                                  related_name='t_s_r_c_o_v_c_tender_id',
                                  on_delete=models.CASCADE,
                                  blank=True,
                                  null=True
                                  )
    name = models.CharField(max_length=100,blank=True, null=True)
    details = models.TextField(blank=True, null=True)
    latitude = models.CharField(max_length=200, blank=True, null=True)
    longitude = models.CharField(max_length=200, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    status = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='t_s_r_c_o_v_c_created_by',
                                   on_delete=models.CASCADE,blank=True,null=True)
    owned_by = models.ForeignKey(User, related_name='t_s_r_c_o_v_c_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='t_s_r_c_o_v_c_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'pms_tender_resource_contractors_o_vendors_contractor'

#::: TENDER SURVEY RESOURCE CONTRACTORS OR VENDORS P&M ::::#
class PmsTenderMachineryTypeDetails(models.Model):
    tender = models.ForeignKey(PmsTenders,
                                  related_name='t_s_r_c_o_v_v_tender_id',
                                  on_delete=models.CASCADE,
                                  blank=True,
                                  null=True
                                  )
    machinary_type = models.ForeignKey(PmsMachineryType,
                                  related_name='t_s_r_c_o_v_v_type_id',
                                  on_delete=models.CASCADE,
                                  blank=True,
                                  null=True
                                  )
    make = models.CharField(max_length=100,blank=True, null=True)
    hire = models.TextField(blank=True, null=True)
    khoraki = models.TextField(blank=True, null=True)
    latitude = models.CharField(max_length=200, blank=True, null=True)
    longitude = models.CharField(max_length=200, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='t_s_r_c_o_v_v_created_by',
                                   on_delete=models.CASCADE,blank=True,null=True)
    owned_by = models.ForeignKey(User, related_name='t_s_r_c_o_v_v_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='t_s_r_c_o_v_v_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'pms_tender_machinery_type_details'


#::: TENDER SURVEY RESOURCE CONTACT DESIGNATION ::::#
class PmsTenderSurveyResourceContactDesignation(models.Model):
    tender = models.ForeignKey(PmsTenders,
                                  related_name='t_s_r_c_d_tender_id',
                                  on_delete=models.CASCADE,
                                  blank=True,
                                  null=True
                                  )
    name = models.CharField(max_length=100,blank=True, null=True)
    status = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='t_s_r_c_d_created_by',
                                   on_delete=models.CASCADE,blank=True,null=True)
    owned_by = models.ForeignKey(User, related_name='t_s_r_c_d_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='t_s_r_c_d_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'pms_tender_resource_contact_designation'

#::: TENDER SURVEY RESOURCE CONTACT DETAILS ::::#
class PmsTenderSurveyResourceContactDetails(models.Model):
    tender = models.ForeignKey(PmsTenders,
                               related_name='t_s_r_c_det_tender_id',
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True
                               )
    designation = models.ForeignKey(PmsTenderSurveyResourceContactDesignation,
                                  related_name='t_s_r_c_d_designation_id',
                                  on_delete=models.CASCADE,
                                  blank=True,
                                  null=True
                                  )
    status = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='t_s_r_c_de_created_by',
                                   on_delete=models.CASCADE,blank=True,null=True)
    owned_by = models.ForeignKey(User, related_name='t_s_r_c_de_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='t_s_r_c_de_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'pms_tender_resource_contact_details'

class PmsTenderSurveyResourceContactFieldDetails(models.Model):
    contact = models.ForeignKey(PmsTenderSurveyResourceContactDetails,
                               related_name='t_s_r_c_det_contact_id',
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True
                               )
    field_label = models.TextField(blank=True, null=True)
    field_value = models.TextField(blank=True, null=True)
    field_type = models.CharField(max_length= 100, blank=True, null=True)
    status = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='t_s_r_c_f_created_by',
                                   on_delete=models.CASCADE,blank=True,null=True)
    owned_by = models.ForeignKey(User, related_name='t_s_r_c_f_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='t_s_r_c_f_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'pms_tender_resource_contact_field_details'

#::: TENDER INITIAL COSTING ::::#
class PmsTenderInitialCosting(models.Model):
    tender = models.ForeignKey(PmsTenders,
                               related_name='t_i_c_tender_id',
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True
                               )
    client = models.CharField(max_length=100,blank=True, null=True)
    tender_notice_no_bid_id_no = models.CharField(max_length=100,
                                                  blank=True, null=True)
    name_of_work = models.TextField(blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    received_estimate = models.FloatField(blank=True, null=True)
    quoted_rate = models.FloatField(blank=True, null=True)
    difference_in_budget = models.FloatField(blank=True, null=True)
    document = models.FileField(upload_to=get_directory_path,default=None,
                                blank=True, null=True,
                                validators=[validate_file_extension]
                               )
    status = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='t_i_c_created_by',
                                   on_delete=models.CASCADE,blank=True,null=True)
    owned_by = models.ForeignKey(User, related_name='t_i_c_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='t_i_c_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'pms_tender_initial_costing'

#::: TENDER INITIAL COSTING EXCEL FIELD LABEL ::::#
class PmsTenderInitialCostingExcelFieldLabel(models.Model):
    tender_initial_costing = models.ForeignKey(PmsTenderInitialCosting,
                               related_name='t_i_c_e_f_l_costing_id',
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True
                               )
    field_label = models.CharField(max_length=100,blank=True, null=True)
    status = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='t_i_c_e_f_l_created_by',
                                   on_delete=models.CASCADE,blank=True,null=True)
    owned_by = models.ForeignKey(User, related_name='t_i_c_e_f_l_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='t_i_c_e_f_l_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'pms_tender_initial_costing_excel_field_label'

#::: TENDER INITIAL COSTING EXCEL FIELD VALUE ::::#
class PmsTenderInitialCostingExcelFieldValue(models.Model):
    tender_initial_costing = models.ForeignKey(PmsTenderInitialCosting,
                               related_name='t_i_c_e_f_v_costing_id',
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True
                               )
    initial_costing_field_label = models.ForeignKey(PmsTenderInitialCostingExcelFieldLabel,
                               related_name='t_i_c_e_f_l_label_id',
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True
                               )
    field_value = models.CharField(max_length=100, blank=True, null=True)
    status = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='t_i_c_e_f_v_created_by',
                                   on_delete=models.CASCADE,blank=True,null=True)
    owned_by = models.ForeignKey(User, related_name='t_i_c_e_f_v_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='t_i_c_e_f_v_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'pms_tender_initial_costing_excel_field_value'

#::: TENDER TAB DOCUMENTS ::::#
class PmsTenderTabDocuments(models.Model):
    tender= models.ForeignKey(PmsTenders,
                               related_name='t_t_d_tender_id',
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True
                               )
    is_upload_document = models.BooleanField(default=False)
    reason_for_no_documentation=models.TextField(null=True,blank=True)
    status = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='t_t_d_created_by',
                                   on_delete=models.CASCADE,blank=True,null=True)
    owned_by = models.ForeignKey(User, related_name='t_t_d_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='t_t_d_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'pms_tender_tab_documents'

class PmsTenderTabDocumentsDocuments(models.Model):
    tender = models.ForeignKey(PmsTenders,
                               related_name='t_t_d_d_tender_id',
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True
                               )
    tender_eligibility = models.ForeignKey(PmsTenderEligibility,
                                           related_name='t_t_d_eligibility_id',
                                           on_delete=models.CASCADE,
                                           blank=True,
                                           null=True
                                           )
    document_date_o_s = models.DateTimeField(blank=True, null=True)
    document_name = models.CharField(max_length=200, blank=True, null=True)
    tab_document = models.FileField(upload_to=get_directory_path,
                                    default=None,
                                    blank=True, null=True,
                                    validators=[validate_file_extension]
                                    )
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='t_t_d_d_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='t_t_d_d_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='t_t_d_d_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'pms_tender_tab_document_documents'
#::: TENDER TAB DOCUMENTS PRICE ::::#
class PmsTenderTabDocumentsPrice(models.Model):
    tender= models.ForeignKey(PmsTenders,
                               related_name='t_t_d_p_tender_id',
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True
                               )
    document_date_o_s = models.DateTimeField(blank=True,null=True)
    document_name = models.CharField(max_length=200, blank=True, null=True)
    tab_document = models.FileField(upload_to=get_directory_path,
                                       default=None,
                                       blank=True, null=True,
                                       validators=[validate_file_extension]
                                       )
    status = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='t_t_d_p_created_by',
                                   on_delete=models.CASCADE,blank=True,null=True)
    owned_by = models.ForeignKey(User, related_name='t_t_d_p_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='t_t_d_p_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'pms_tender_tab_documents_price'

#:::::::::::::::: TENDER STATUS :::::::::::#
class PmsTenderStatus(models.Model):
    tender = models.ForeignKey(PmsTenders,
                               related_name='t_s_tender_id',
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True
                               )
    is_awarded = models.BooleanField(default=False)
    date_of_awarding = models.DateTimeField(null=True, blank=True)
    loi_issued_on = models.DateTimeField(null=True, blank=True)
    position = models.CharField(max_length=100, blank=True, null=True)
    reason = models.TextField(blank=True, null=True)
    percentage_of_preference = models.DecimalField(blank=True, null=True,
                                                   max_digits=10, decimal_places=3)
    status = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='t_s_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='t_s_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='t_s_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'pms_tender_status'

#::::::::::::::: TENDER STATUS PARTICIPENTS::::::::#
class PmsTenderStatusParticipentsFieldLabel(models.Model):
    tender_status = models.ForeignKey(PmsTenderStatus,
                                      related_name='t_s_p_f_l_s_id',
                                      on_delete=models.CASCADE,
                                      blank=True,
                                      null=True
                                      )
    field_label = models.CharField(max_length=100, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='t_s_p_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='t_s_p_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_tender_status_participents_field_label'
class PmsTenderStatusParticipentsFieldValue(models.Model):
    tender_status = models.ForeignKey(PmsTenderStatus,
                                      related_name='t_s_p_f_v_status_id',
                                      on_delete=models.CASCADE,
                                      blank=True,
                                      null=True
                                      )
    participents_field_label = models.ForeignKey(PmsTenderStatusParticipentsFieldLabel,
                                                 related_name='t_s_p_f_label_id',
                                                 on_delete=models.CASCADE,
                                                 blank=True,
                                                 null=True
                                                 )
    field_value = models.CharField(max_length=100, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='t_s_p_f_v_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='t_s_p_f_v_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_tender_status_participents_field_value'

#:::::::: TENDER STATUS COMPARISON ::::::::#
class PmsTenderStatusComparisonChartFieldLabel(models.Model):
    tender_status = models.ForeignKey(PmsTenderStatus,
                               related_name='t_s_c_c_f_l_s_id',
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True
                               )
    field_label = models.CharField(max_length=100,blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='t_s_c_c_f_l_created_by',
                                   on_delete=models.CASCADE,blank=True,null=True)
    owned_by = models.ForeignKey(User, related_name='t_s_c_c_f_l_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'pms_tender_status_comparison_chart_field_label'
class PmsTenderStatusComparisonChartFieldValue(models.Model):
    tender_status = models.ForeignKey(PmsTenderStatus,
                               related_name='t_s_c_c_f_v_status_id',
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True
                               )
    status_comparison_field_label = models.ForeignKey(PmsTenderStatusComparisonChartFieldLabel,
                               related_name='t_s_c_c_f_label_id',
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True
                               )
    field_value = models.CharField(max_length=100, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='t_s_c_c_f_v_created_by',
                                   on_delete=models.CASCADE,blank=True,null=True)
    owned_by = models.ForeignKey(User, related_name='t_s_c_c_f_v_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'pms_tender_status_comparison_chart_field_value'

#::::::::::  TENDER STATUS DOCUMENTS TABLE ::::::::#

class PmsTenderStatusDocuments(models.Model):
    tender = models.ForeignKey(PmsTenders,
                               related_name='t_st_d_tender_id',
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True
                               )
    tender_status = models.ForeignKey(PmsTenderStatus,
                                      related_name='t_s_d_status_id',
                                      on_delete=models.CASCADE,
                                      blank=True,
                                      null=True
                                      )
    document_name = models.CharField(max_length=200,blank=True,null=True)
    document = models.FileField(upload_to=get_directory_path,
                                        default=None,
                                        blank=True, null=True,
                                        validators=[validate_file_extension]
                                       )
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='t_s_ds_created_by',
                                   on_delete=models.CASCADE,blank=True,null=True)
    owned_by = models.ForeignKey(User, related_name='t_s_ds_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='t_s_ds_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'pms_tender_status_documents'

class PmsExternalUsersExtraDetailsTenderMapping(models.Model):
    tender = models.ForeignKey(PmsTenders, related_name='e_u_e_t_m_tender_id',
                                  on_delete=models.CASCADE, blank=True, null=True)
    external_user_type = models.ForeignKey(PmsExternalUsersType,
                                           related_name='e_u_e_t_m_user_type_id',
                                      on_delete=models.CASCADE, blank=True, null=True)
    external_user = models.ForeignKey(PmsExternalUsers, related_name='e_u_e_t_m_user_id',
                               on_delete=models.CASCADE, blank=True, null=True)
    tender_survey_material = models.ForeignKey(Materials,
                                               related_name='e_u_e_t_m_material_id',
                                               on_delete=models.CASCADE,blank=True,null=True)
    latitude = models.DecimalField(max_digits=40, decimal_places=16, blank=True, null=True)
    longitude = models.DecimalField(max_digits=40, decimal_places=16, blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='e_u_e_t_m_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='e_u_e_t_m_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='e_u_e_t_m_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_external_users_extra_details_tender_mapping'

class PmsExternalUsersExtraDetailsTenderMappingDocument(models.Model):
    external_user = models.ForeignKey(PmsExternalUsers, related_name='e_u_e_t_m_d_user_id',
                               on_delete=models.CASCADE)
    external_user_mapping = models.ForeignKey(PmsExternalUsersExtraDetailsTenderMapping, related_name='e_u_e_t_m_d_m_user_id',on_delete=models.CASCADE)
    document_name = models.CharField(max_length=200)
    document = models.FileField(upload_to=get_directory_path,default=None,validators=[validate_file_extension])
    is_deleted = models.BooleanField(default=False)
    status = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, related_name='e_u_e_t_m_d_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='e_u_e_t_m_d_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='e_u_e_t_m_d_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'pms_external_users_extra_details_tender_mapping_document'


#:::::::::: PROJECT SITE MANAGEMENT MULTIPLE LONGITUDE AND LATTITUDE :::::::::::#
class PmsSiteProjectSiteManagementMultipleLongLat(models.Model):
    project_site = models.ForeignKey(PmsSiteProjectSiteManagement, 
    related_name='p_s_p_s_m_m_l_l_project_site', on_delete=models.CASCADE, blank=True, null=True)
    # address = models.CharField(max_length=200, blank=True, null=True)
    latitude = models.DecimalField(max_digits=40, decimal_places=16, blank=True, null=True)
    longitude = models.DecimalField(max_digits=40, decimal_places=16, blank=True, null=True)
    # type = models.ForeignKey(PmsSiteTypeProjectSiteManagement, related_name='project_site_management_type',
    #                          on_delete=models.CASCADE, blank=True, null=True)
    # description = models.CharField(max_length=255, blank=True, null=True)
    # company_name = models.CharField(max_length=255, blank=True, null=True)
    # gst_no = models.CharField(max_length=255, blank=True, null=True)
    # geo_fencing_area = models.CharField(max_length=255, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_s_p_s_m_m_l_l_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_s_p_s_m_m_l_l_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_s_p_s_m_m_l_l_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_site_project_site_management_multiple_long_lat'