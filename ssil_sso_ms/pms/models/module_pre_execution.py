from django.db import models
from django.contrib.auth.models import User
from dynamic_media import get_directory_path
from django_mysql.models import EnumField
from validators import validate_file_extension
from core.models import TCoreUnit,TCoreDesignation
import datetime
import time
from pms.models.module_project import *
from pms.models.module_machineries import *

#::::::::::::PMS PRE EXECUTION GUEST HOUSE FINDING:::::::::#
class PmsPreExcutionGuestHouseFinding(models.Model):
    project = models.ForeignKey(PmsProjects, related_name='p_e_g_h_f_project',
                                on_delete=models.CASCADE, blank=True, null=True)
    cost = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    latitude = models.DecimalField(max_digits=40,decimal_places=16, blank=True, null=True)
    longitude = models.DecimalField(max_digits=40,decimal_places=16, blank=True, null=True)
    no_of_rooms  = models.IntegerField(blank=True, null=True)
    capacity = models.IntegerField(blank=True, null=True)
    distence_from_site = models.DecimalField(max_digits=40, decimal_places=16, blank=True, null=True)
    checkin_date = models.DateTimeField(blank=True, null=True)
    checkout_date = models.DateTimeField(blank=True, null=True)
    near_rail_station = models.CharField(max_length=200, blank=True, null=True)
    near_bus_stand = models.CharField(max_length=200, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_g_h_f_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_g_h_f_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_g_h_f_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_pre_excution_guest_house_finding'

#:::::::::::: PMS PRE EXCUTION FURNITURE ::::::::::::::::#
class PmsPreExcutionFurniture(models.Model):
    type_of_guest_house = (
        (1, 'full_furnished'),
        (2, 'semi_furnished'),
        (3, 'un_furnished')
    )
    project = models.ForeignKey(PmsProjects, related_name='p_e_f_project',
                                on_delete=models.CASCADE, blank=True, null=True)
    guest_house_type = models.IntegerField(choices=type_of_guest_house,null=True,blank=True)
    transporation_cost = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_f_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_f_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_f_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_pre_excution_furniture'

#:::::::::::::: PMS PRE EXCUTION FUR M FUR REQUIREMENTS :::::::::::::#
class PmsPreExcutionFurMFurRequirements(models.Model):
    f_requirements = models.ForeignKey(PmsPreExcutionFurniture, related_name='p_e_f_m_f_requirements',
                                on_delete=models.CASCADE, blank=True, null=True)
    type = models.CharField(max_length=200, blank=True, null=True)
    count = models.IntegerField(blank=True, null=True)
    local_rate = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    document_name = models.CharField(max_length=100, blank=True, null=True)
    document = models.FileField(upload_to=get_directory_path,
                                       default=None,
                                       blank=True, null=True,
                                       validators=[validate_file_extension]
                                       )
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_f_m_f_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_f_m_f_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_f_m_f_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_pre_excution_fur_m_fur_requirements'

################################################################################
#:::::::::::::::::::: PMS PRE EXCUTION UTILITIES AND AMINITIES ::::::::::::::::#
################################################################################

#::::::::::::PMS PRE EXCUTION UTILITIES ELECTRICAL::::::::::::::::::::::::::::#

class PmsPreExcutionUtilitiesElectrical(models.Model):
    project = models.ForeignKey(PmsProjects, related_name='p_e_u_e_project',
                                on_delete=models.CASCADE, blank=True, null=True)
    local_connection=models.BooleanField(default=True)
    option=models.CharField(max_length=200, blank=True, null=True)
    n_electric_of_addr=models.TextField(blank=True, null=True)
    latitude =models.DecimalField(max_digits=40,decimal_places=16,blank=True,null=True)
    longitude = models.DecimalField(max_digits=40, decimal_places=16, blank=True, null=True)
    contact_no =models.CharField(max_length=30, blank=True, null=True)
    detailed_procedure=models.TextField(blank=True, null=True)
    requirment_s_date=models.DateTimeField(blank=True, null=True)
    requirment_e_date=models.DateTimeField(blank=True, null=True)
    budgeted_cost =models.DecimalField(max_digits=10,decimal_places=3,blank=True,null=True)
    executed_cost=models.DecimalField(max_digits=10,decimal_places=3,blank=True,null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_u_e_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_u_e_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_u_e_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_pre_excution_utilities_electrical'

#::::::::::::PMS PRE EXCUTION UTILITIES WATER:::::::::::::::::::::::::::::::::::#
class PmsPreExcutionUtilitiesWater(models.Model):
    project = models.ForeignKey(PmsProjects, related_name='p_e_u_w_project',
                                on_delete=models.CASCADE, blank=True, null=True)
    submergible_pump=models.BooleanField(default=True)
    quantity =models.IntegerField(blank=True, null=True)
    depth =models.CharField(max_length=200, blank=True, null=True)
    con_name =models.CharField(max_length=200, blank=True, null=True)
    con_conatct_no=models.CharField(max_length=30, blank=True, null=True)
    con_email_id =models.CharField(max_length=200, blank=True, null=True)
    con_address =models.TextField(blank=True, null=True)
    latitude=models.DecimalField(max_digits=40,decimal_places=16,blank=True,null=True)
    longitude=models.DecimalField(max_digits=40,decimal_places=16,blank=True,null=True)
    requirment_s_date=models.DateTimeField(blank=True, null=True)
    requirment_e_date=models.DateTimeField(blank=True, null=True)
    budgeted_cost =models.DecimalField(max_digits=10,decimal_places=3,blank=True,null=True)
    executed_cost =models.DecimalField(max_digits=10,decimal_places=3,blank=True,null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_u_w_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_u_w_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_u_w_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_pre_excution_utilities_water'

#::::::::::::PMS PRE EXCUTION UTILITIES FUEL:::::::::::::::::::::::::::::::::::::#
class PmsPreExcutionUtilitiesFuel(models.Model):
    project = models.ForeignKey(PmsProjects, related_name='p_e_u_f_project',
                                on_delete=models.CASCADE, blank=True, null=True)
    available=models.BooleanField(default=True)
    type_of_fuel=models.CharField(max_length=200, blank=True, null=True)
    volume_required=models.CharField(max_length=200, blank=True, null=True)
    supplier_name=models.CharField(max_length=200, blank=True, null=True)
    contact_no=models.CharField(max_length=10, blank=True, null=True)
    supplier_address=models.TextField(blank=True,null=True)
    latitude = models.DecimalField(max_digits=40, decimal_places=16, blank=True, null=True)
    longitude = models.DecimalField(max_digits=40, decimal_places=16, blank=True, null=True)
    requirment_s_date=models.DateTimeField(blank=True, null=True)
    requirment_e_date=models.DateTimeField(blank=True, null=True)
    budgeted_cost =models.DecimalField(max_digits=10,decimal_places=3,blank=True,null=True)
    executed_cost =models.DecimalField(max_digits=10,decimal_places=3,blank=True,null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_u_f_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_u_f_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_u_f_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_pre_excution_utilities_fuel'

#:::::::::::::: PMS PRE EXCUTION UTILITIES UTENSILS :::::::::::::::::::::::::::::#
class PmsPreExcutionUtilitiesUtensils(models.Model):
    project = models.ForeignKey(PmsProjects, related_name='p_e_u_u_project',
                                on_delete=models.CASCADE, blank=True, null=True)
    available = models.BooleanField(default=True)
    requirment_s_date = models.DateTimeField(blank=True, null=True)
    requirment_e_date = models.DateTimeField(blank=True, null=True)
    budgeted_cost = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    executed_cost = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_u_u_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_u_u_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_u_u_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_pre_excution_utilities_utensils'

#:::::::::::::: PMS PRE EXCUTION UTILITIES UTENSILS TYPES :::::::::::::::::::::::#
class PmsPreExcutionUtilitiesUtensilsTypes(models.Model):
    project = models.ForeignKey(PmsProjects, related_name='p_e_u_u_t_project',
                                on_delete=models.CASCADE, blank=True, null=True)
    utensils = models.ForeignKey(PmsPreExcutionUtilitiesUtensils, related_name='p_e_u_u_t_utensils',
                                on_delete=models.CASCADE, blank=True, null=True)
    type_of_utensils = models.CharField(max_length=200, blank=True, null=True)
    quantity = models.IntegerField(blank=True, null=True)
    rate = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_u_u_t_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_u_u_t_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_u_u_t_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_pre_excution_utilities_utensils_types'

#:::::::::::::: PMS PRE EXCUTION UTILITIES TIFFIN BOX :::::::::::::::::::::::::::#
class PmsPreExcutionUtilitiesTiffinBox(models.Model):
    project = models.ForeignKey(PmsProjects, related_name='p_e_u_t_b_project',
                                on_delete=models.CASCADE, blank=True, null=True)
    available = models.BooleanField(default=True)
    requirment_s_date = models.DateTimeField(blank=True, null=True)
    requirment_e_date = models.DateTimeField(blank=True, null=True)
    budgeted_cost = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    executed_cost = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_u_t_b_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_u_t_b_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_u_t_b_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_pre_excution_utilities_tiffin_box'

#:::::::::::::: PMS PRE EXCUTION UTILITIES TIFFIN BOX TYPES :::::::::::::::::::::#
class PmsPreExcutionUtilitiesTiffinBoxTypes(models.Model):
    project = models.ForeignKey(PmsProjects, related_name='p_e_u_t_b_t_project',
                                on_delete=models.CASCADE, blank=True, null=True)
    tiffin_box = models.ForeignKey(PmsPreExcutionUtilitiesTiffinBox, related_name='p_e_u_t_b_t_utensils',
                                on_delete=models.CASCADE, blank=True, null=True)
    make_of_tiffin_box = models.CharField(max_length=200, blank=True, null=True)
    quantity = models.IntegerField(blank=True, null=True)
    rate = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_u_t_b_t_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_u_t_b_t_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_u_t_b_t_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_pre_excution_utilities_tiffin_box_types'

#::::::::::::PMS PRE EXCUTION UTILITIES COOK:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::#
class PmsPreExcutionUtilitiesCook(models.Model):
    project = models.ForeignKey(PmsProjects, related_name='p_e_u_c_project',
                                on_delete=models.CASCADE, blank=True, null=True)

    available=models.BooleanField(default=True)
    cook_name=models.CharField(max_length=200, blank=True, null=True)
    cook_conatct_no=models.CharField(max_length=20, blank=True, null=True)
    chargs=models.CharField(max_length=200, blank=True, null=True)
    name_of_agency =models.CharField(max_length=200, blank=True, null=True)
    agency_contact_no =models.CharField(max_length=20, blank=True, null=True)
    agency_addr=models.TextField(blank=True, null=True)
    latitude=models.DecimalField(max_digits=40,decimal_places=16,blank=True,null=True)
    longitude=models.DecimalField(max_digits=40,decimal_places=16,blank=True,null=True)
    requirment_s_date=models.DateTimeField(blank=True, null=True)
    requirment_e_date=models.DateTimeField(blank=True, null=True)
    budgeted_cost =models.DecimalField(max_digits=10,decimal_places=3,blank=True,null=True)
    executed_cost =models.DecimalField(max_digits=10,decimal_places=3,blank=True,null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_u_c_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_u_c_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_u_c_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_pre_excution_utilities_cook'

#::::::::::::PMS PRE EXCUTION UTILITIES DOCUMENT::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::#
class PmsPreExcutionUtilitiesDocument(models.Model):
    project = models.ForeignKey(PmsProjects, related_name='p_e_u_d_project',
                                on_delete=models.CASCADE, blank=True, null=True)
    model_class = models.CharField(max_length=100, blank=True, null=True)
    module_id = models.IntegerField(blank=True, null=True)
    document_name = models.CharField(max_length=100, blank=True, null=True)
    document = models.FileField(upload_to=get_directory_path,
                                default=None,
                                blank=True, null=True,
                                validators=[validate_file_extension]
                                )
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_u_d_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_u_d_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_u_d_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_pre_excution_utilities_document'

###################################################################################
#::::::::::::::::::::::::::: OFFICE SETUP ::::::::::::::::::::::::::::::::::::::::#
###################################################################################

#:::::::::::::::::::::: PMS PRE EXECUTION OFFICE SETUP MASTER:::::::::::::::::::::::::::#
# class PmsPreExecutionOfficeSetupMaster(models.Model):
#     project = models.ForeignKey(PmsProjects, related_name='p_e_o_s_m_project',
#                                 on_delete=models.CASCADE, blank=True, null=True)
#     name=models.CharField(max_length=200, blank=True, null=True)
#     is_deleted = models.BooleanField(default=False)
#     created_by = models.ForeignKey(User, related_name='p_e_o_s_m_created_by',
#                                    on_delete=models.CASCADE, blank=True, null=True)
#     updated_by = models.ForeignKey(User, related_name='p_e_o_s_m_updated_by',
#                                    on_delete=models.CASCADE, blank=True, null=True)
#     owned_by = models.ForeignKey(User, related_name='p_e_o_s_m_owned_by',
#                                  on_delete=models.CASCADE, blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return str(self.id)

#     class Meta:
#         db_table = 'pms_pre_excution_office_set_up_master'

#::::::::::::PMS PRE EXCUTION OFFICE STRUCTURE::::::::::::::::::::::::::::::::::::#

class PmsPreExecutionOfficeStructure(models.Model):
    type_of_office_structure = (
        (1, 'office_container'),
        (2, 'existing_brick_work')

    )
    # office_set_up=models.ForeignKey(PmsPreExecutionOfficeSetupMaster, related_name='p_e_o_s_office_set_up',
                                # on_delete=models.CASCADE, blank=True, null=True)
    project = models.OneToOneField(PmsProjects, related_name='p_e_o_s_project',
                                on_delete=models.CASCADE, blank=True, null=True)
    structure_type = models.IntegerField(choices=type_of_office_structure, null=True, blank=True)
    size=models.IntegerField(blank=True, null=True)
    rate=models.DecimalField(max_digits=10,decimal_places=3,blank=True,null=True)
    agency_name=models.CharField(max_length=100, blank=True, null=True)
    agency_contact_no=models.CharField(max_length=20, blank=True, null=True)
    transportation_cost=models.DecimalField(max_digits=10,decimal_places=3,blank=True,null=True)
    requirment_s_date = models.DateTimeField(blank=True, null=True)
    requirment_e_date = models.DateTimeField(blank=True, null=True)
    budgeted_cost = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    executed_cost = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_o_s_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_o_s_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_o_s_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_pre_excution_office_structure'

#::::::::::::PMS PRE EXCUTION ELECTRIC CONNECTION::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::#

class PmsPreExecutionElectricalConnection(models.Model):
    project = models.OneToOneField(PmsProjects, related_name='p_e_e_c_project',
                                on_delete=models.CASCADE, blank=True, null=True)
    # office_set_up = models.ForeignKey(PmsPreExecutionOfficeSetupMaster, related_name='p_e_e_c_office_set_up',
    #                                   on_delete=models.CASCADE, blank=True, null=True)
    connection_type=models.BooleanField(default=True)
    option=models.CharField(max_length=200, blank=True, null=True)
    nearby_elec_off_address=models.TextField(blank=True,null=True)
    latitude = models.DecimalField(max_digits=40, decimal_places=16, blank=True, null=True)
    longitude = models.DecimalField(max_digits=40, decimal_places=16, blank=True, null=True)
    contact_no=models.CharField(max_length=20, blank=True, null=True)
    detailed_procedure=models.TextField(blank=True,null=True)
    requirment_s_date = models.DateTimeField(blank=True, null=True)
    requirment_e_date = models.DateTimeField(blank=True, null=True)
    budgeted_cost = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    executed_cost = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_e_c_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_e_c_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_e_c_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_pre_excution_electrical_connection'

#::::::::::::PMS PRE EXCUTION WATER CONNECTION::::::::::::::::::::::::::::::::::::::::::::::#

class PmsPreExecutionWaterConnection(models.Model):
    project = models.OneToOneField(PmsProjects, related_name='p_e_w_c_project',
                                on_delete=models.CASCADE, blank=True, null=True)
    # office_set_up = models.ForeignKey(PmsPreExecutionOfficeSetupMaster, related_name='p_e_w_s_office_set_up',
    #                                   on_delete=models.CASCADE, blank=True, null=True)
    submergible_pump_types=models.BooleanField(default=True)
    quantity = models.IntegerField(blank=True, null=True)
    depth = models.CharField(max_length=200, blank=True, null=True)
    contractor_name=models.CharField(max_length=200, blank=True, null=True)
    con_contact_number=models.CharField(max_length=200, blank=True, null=True)
    con_address = models.TextField(blank=True, null=True)
    latitude = models.DecimalField(max_digits=40, decimal_places=16, blank=True, null=True)
    longitude = models.DecimalField(max_digits=40, decimal_places=16, blank=True, null=True)
    email_id=models.CharField(max_length=100, blank=True, null=True)
    requirment_s_date = models.DateTimeField(blank=True, null=True)
    requirment_e_date = models.DateTimeField(blank=True, null=True)
    budgeted_cost = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    executed_cost = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_w_c_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_w_c_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_w_c_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'pms_pre_excution_water_connection'
#::::::::::::PMS PRE EXCUTION INTERNET CONNECTION::::::::::::::::::::::::::::::::::::::::::::::::::#

class PmsPreExecutionInternetConnection(models.Model):
    type_of_internet_connection= (
        (1, 'jio_fi'),
        (2, 'broadband_connection')
    )
    project = models.OneToOneField(PmsProjects, related_name='p_e_i_c_project',
                                on_delete=models.CASCADE, blank=True, null=True)
    # office_set_up = models.ForeignKey(PmsPreExecutionOfficeSetupMaster, related_name='p_e_i_s_office_set_up',
    #                                   on_delete=models.CASCADE, blank=True, null=True)
    connection_type = models.IntegerField(choices=type_of_internet_connection, null=True, blank=True)
    quantity=models.IntegerField(blank=True, null=True)
    model = models.CharField(max_length=200, blank=True, null=True)
    package_availed=models.CharField(max_length=200, blank=True, null=True)
    price_limit=models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)

    supplier_name=models.CharField(max_length=200, blank=True, null=True)
    supplier_ph_no=models.CharField(max_length=20, blank=True, null=True)
    supplier_address=models.TextField(blank=True, null=True)
    service=models.CharField(max_length=200, blank=True, null=True)
    initial_installation_charges=models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    requirment_s_date = models.DateTimeField(blank=True, null=True)
    requirment_e_date = models.DateTimeField(blank=True, null=True)
    budgeted_cost = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    executed_cost = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_i_c_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_i_c_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_w_i_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_pre_excution_internet_connection'

#::::::::::::PMS PRE EXCUTION OFFICE SETUP  FURNITURE::::::::::::::::::::::::::::::::::::::::::::::::::#

class PmsPreExcutionOfficeSetupFurniture(models.Model):
    type_of_furniture = (
        (1, 'file_cabinet'),
        (2, 'table'),
        (3, 'chair')
    )
    project = models.ForeignKey(PmsProjects, related_name='p_e_o_s_f_project',
                                on_delete=models.CASCADE, blank=True, null=True)
    # office_set_up = models.ForeignKey(PmsPreExecutionOfficeSetupMaster, related_name='p_e_o_s_f_office_set_up',
    #                                   on_delete=models.CASCADE, blank=True, null=True)
    furniture_type = models.IntegerField(choices=type_of_furniture, null=True, blank=True)
    brand = models.CharField(max_length=200, blank=True, null=True)
    quantity=models.IntegerField(blank=True, null=True)
    rate= models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    supplier_name = models.CharField(max_length=200, blank=True, null=True)
    supplier_ph_no = models.CharField(max_length=20, blank=True, null=True)
    supplier_address = models.TextField(blank=True, null=True)
    latitude = models.DecimalField(max_digits=40, decimal_places=16, blank=True, null=True)
    longitude = models.DecimalField(max_digits=40, decimal_places=16, blank=True, null=True)
    requirment_s_date = models.DateTimeField(blank=True, null=True)
    requirment_e_date = models.DateTimeField(blank=True, null=True)
    budgeted_cost = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    executed_cost = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_o_s_f_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_o_s_f_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_o_s_f_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_pre_excution_office_setup_furniture'

#::::::::::::PMS PRE EXCUTION OFFICE SETUP COMPUTER::::::::::::::::::::::::::::::::::::::::::::::::::#

class PmsPreExcutionOfficeSetupComputer(models.Model):
    type_of_computer= (
        (1, 'desktop'),
        (2, 'laptop')
    )
    project = models.OneToOneField(PmsProjects, related_name='p_e_o_s_c_project',
                                on_delete=models.CASCADE, blank=True, null=True)
    # office_set_up = models.ForeignKey(PmsPreExecutionOfficeSetupMaster, related_name='p_e_o_s_c_office_set_up',
    #                                   on_delete=models.CASCADE, blank=True, null=True)
    computer_type = models.IntegerField(choices=type_of_computer, null=True, blank=True)
    brand= models.CharField(max_length=200, blank=True, null=True)
    quantity=models.IntegerField(blank=True, null=True)
    rate= models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    supplier_name = models.CharField(max_length=200, blank=True, null=True)
    supplier_ph_no = models.CharField(max_length=20, blank=True, null=True)
    supplier_address = models.TextField(blank=True, null=True)
    latitude = models.DecimalField(max_digits=40, decimal_places=16, blank=True, null=True)
    longitude = models.DecimalField(max_digits=40, decimal_places=16, blank=True, null=True)
    requirment_s_date = models.DateTimeField(blank=True, null=True)
    requirment_e_date = models.DateTimeField(blank=True, null=True)
    budgeted_cost = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    executed_cost = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_o_s_c_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_o_s_c_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_o_s_c_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_pre_excution_office_setup_computer'

#::::::::::::PMS PRE EXCUTION OFFICE SETUP STATIONARY::::::::::::::::::::::::::::::::::::::::::::::::::#

class PmsPreExcutionOfficeSetupStationary(models.Model):
    project = models.OneToOneField(PmsProjects, related_name='p_e_o_s_s_project',
                                on_delete=models.CASCADE, blank=True, null=True)
    # office_set_up = models.ForeignKey(PmsPreExecutionOfficeSetupMaster, related_name='p_e_o_s_s_office_set_up',
    #                                   on_delete=models.CASCADE, blank=True, null=True)
    requirment_s_date = models.DateTimeField(blank=True, null=True)
    requirment_e_date = models.DateTimeField(blank=True, null=True)
    budgeted_cost = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    executed_cost = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_o_s_s_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_o_s_s_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_o_s_s_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_pre_excution_office_setup_stationary'

class PmsPreExcutionOfficeSetupStationaryMStnRequirements(models.Model):
    stn_requirements = models.ForeignKey(PmsPreExcutionOfficeSetupStationary, related_name='p_e_o_s_s_m_s_requirements',
                                       on_delete=models.CASCADE, blank=True, null=True)
    project = models.ForeignKey(PmsProjects, related_name='p_e_o_s_s_m_s_project',
                                on_delete=models.CASCADE, blank=True, null=True)
    item=models.CharField(max_length=200, blank=True, null=True)
    quantity=models.IntegerField(blank=True, null=True)
    rate = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    supplier_name = models.CharField(max_length=200, blank=True, null=True)
    supplier_ph_no = models.CharField(max_length=20, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_o_s_s_m_s_rcreated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_o_s_s_m_s_r_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_o_s_s_m_s_r_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_pre_excution_office_setup_stationary_mstn_requirements'

#::::::::::::PMS PRE EXCUTION OFFICE SETUP TOILET::::::::::::::::::::::::::::::::::::::::::::::::::#
class PmsPreExcutionOfficeSetupToilet(models.Model):
    type_of_toilet = (
        (1, 'brick_wall_toilet'),
        (2, 'bio_toilet')
    )
    project = models.OneToOneField(PmsProjects, related_name='p_e_o_s_t_project',
                                on_delete=models.CASCADE, blank=True, null=True)
    # office_set_up = models.ForeignKey(PmsPreExecutionOfficeSetupMaster, related_name='p_e_o_s_t_office_set_up',
    #                                   on_delete=models.CASCADE, blank=True, null=True)
    toi_available=models.BooleanField(default=True)
    existing_arrangement=models.IntegerField(choices=type_of_toilet, null=True, blank=True)
    details=models.TextField(blank=True,null=True)
    rate = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    requirment_s_date = models.DateTimeField(blank=True, null=True)
    requirment_e_date = models.DateTimeField(blank=True, null=True)
    budgeted_cost = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    executed_cost = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_o_s_t_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_o_s_t_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_o_s_t_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_pre_excution_office_setup_toilet'

#::::::::::::PMS PRE EXCUTION OFFICE SETUP VEHICLE::::::::::::::::::::::::::::::::::::::::::::::::::#
class PmsPreExcutionOfficeSetupVehicle(models.Model):
    type_of_vehicle = (
        (1, 'rental'),
        (2, 'purchase')
    )
    project = models.ForeignKey(PmsProjects, related_name='p_e_o_s_v_project',
                                on_delete=models.CASCADE, blank=True, null=True)
    # office_set_up = models.ForeignKey(PmsPreExecutionOfficeSetupMaster, related_name='p_e_o_s_v_office_set_up',
    #                                   on_delete=models.CASCADE, blank=True, null=True)
    vehicle_type = models.IntegerField(choices=type_of_vehicle, null=True, blank=True)
    vehicle_model=models.CharField(max_length=200, blank=True, null=True)
    vehicle_details=models.TextField(blank=True,null=True)
    vehicle_cost=models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    Rate_per_day=models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    quantity = models.IntegerField(blank=True, null=True)
    owner_name = models.CharField(max_length=200, blank=True, null=True)
    owner_contact_details = models.CharField(max_length=200, blank=True, null=True)
    requirment_s_date = models.DateTimeField(blank=True, null=True)
    requirment_e_date = models.DateTimeField(blank=True, null=True)
    budgeted_cost = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    executed_cost = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_o_s_v_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_o_s_v_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_o_s_v_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_pre_excution_office_setup_vehicle'

class PmsPreExcutionOfficeSetupVehicleDriver(models.Model):
    vehicle_driver = models.ForeignKey(PmsPreExcutionOfficeSetupVehicle, related_name='p_e_o_s_v_d_vehicle_driver',
                                         on_delete=models.CASCADE, blank=True, null=True)
    project = models.ForeignKey(PmsProjects, related_name='p_e_o_s_v_d_project',
                                on_delete=models.CASCADE, blank=True, null=True)
    driver_name=models.CharField(max_length=200, blank=True, null=True)
    driver_contact_details=models.CharField(max_length=20, blank=True, null=True)
    vehicle_numberplate=models.CharField(max_length=100, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_o_s_v_d_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_o_s_v_d_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_o_s_v_d_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_pre_excution_office_setup_vehicle_driver'

#::::::::::::PMS PRE EXECUTION OFFICE SETUP BIKE::::::::::::::::::::::::::::::::::::::::::::::::::#
class PmsPreExecutionOfficeSetupBike(models.Model):
    project = models.OneToOneField(PmsProjects, related_name='p_e_o_s_b_project',
                                on_delete=models.CASCADE, blank=True, null=True)
    # office_set_up = models.ForeignKey(PmsPreExecutionOfficeSetupMaster, related_name='p_e_o_s_b_office_set_up',
    #                                   on_delete=models.CASCADE, blank=True, null=True)
    bike_model=models.CharField(max_length=200, blank=True, null=True)
    bike_details=models.TextField(blank=True,null=True)
    bike_cost=models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    quantity= models.IntegerField(blank=True, null=True)
    requirment_s_date = models.DateTimeField(blank=True, null=True)
    requirment_e_date = models.DateTimeField(blank=True, null=True)
    budgeted_cost = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    executed_cost = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_o_s_b_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_o_s_b_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_o_s_b_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_pre_excution_office_setup_bike'

##################################################################################
# ::::::::::::PMS PRE EXECUTION OFFICE SETUP LABOUR::::::::::::::::::::::::::::::#
##################################################################################

# ::::::::::::PMS PRE EXECUTION OFFICE SETUP LABOUR LABOUR HUTMENT:::::::::::::::::::::::::::::::::#
class PmsPreExecutionOfficeSetupLabourLabourHutment(models.Model):
    type_of_hut = (
        (1, 'brick_work'),
        (2, 'temporary_structure_with_gi_sheet')
    )
    project = models.OneToOneField(PmsProjects, related_name='p_e_o_s_l_h_project',
                                on_delete=models.CASCADE, blank=True, null=True)
    # office_set_up = models.ForeignKey(PmsPreExecutionOfficeSetupMaster, related_name='p_e_o_s_l_h_office_set_up',
    #                                   on_delete=models.CASCADE, blank=True, null=True)
    hut_type = models.IntegerField(choices=type_of_hut, null=True, blank=True)
    area_of_hut=models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    capacity_of_manpower=models.CharField(max_length=200, blank=True, null=True)
    total_cost=models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    contractor_name=models.CharField(max_length=200, blank=True, null=True)
    phone_no=models.CharField(max_length=10, blank=True, null=True)
    address=models.TextField(blank=True,null=True)
    latitude = models.DecimalField(max_digits=40, decimal_places=16, blank=True, null=True)
    longitude = models.DecimalField(max_digits=40, decimal_places=16, blank=True, null=True)
    requirment_s_date = models.DateTimeField(blank=True, null=True)
    requirment_e_date = models.DateTimeField(blank=True, null=True)
    budgeted_cost = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    executed_cost = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_o_s_l_l_h_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_o_s_l_l_h_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_o_s_l_l_h_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_pre_excution_office_setup_labour_labour_hutment'

# ::::::::::::PMS PRE EXECUTION OFFICE SETUP LABOUR TOILET:::::::::::::::::::::::::::::::::::::::#
class PmsPreExecutionOfficeSetupLabourToilet(models.Model):
    type_of_toilet = (
        (1, 'brick_wall_toilet'),
        (2, 'bio_toilet')
    )
    project = models.OneToOneField(PmsProjects, related_name='p_e_o_s_l_t_project',
                                on_delete=models.CASCADE, blank=True, null=True)
    # office_set_up = models.ForeignKey(PmsPreExecutionOfficeSetupMaster, related_name='p_e_o_s_l_t_office_set_up',
    #                                   on_delete=models.CASCADE, blank=True, null=True)
    toi_available=models.BooleanField(default=True)
    existing_arrangement = models.IntegerField(choices=type_of_toilet, null=True, blank=True)
    details=models.TextField(blank=True,null=True)
    rate= models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    requirment_s_date = models.DateTimeField(blank=True, null=True)
    requirment_e_date = models.DateTimeField(blank=True, null=True)
    budgeted_cost = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    executed_cost = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_o_s_l_t_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_o_s_l_t_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_o_s_l_t_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_pre_excution_office_setup_labour_toilet'

# ::::::::::::PMS PRE EXECUTION OFFICE SETUP LABOUR WATER CONNECTION:::::::::::::::::::::::::::::::#
class PmsPreExecutionOfficeSetupLabourWaterConnection(models.Model):
    project = models.OneToOneField(PmsProjects, related_name='p_e_o_s_l_w_c_project',
                                on_delete=models.CASCADE, blank=True, null=True)
    # office_set_up = models.ForeignKey(PmsPreExecutionOfficeSetupMaster, related_name='p_e_o_s_l_w_c_office_set_up',
    #                                   on_delete=models.CASCADE, blank=True, null=True)
    borewell_for_drinking_water = models.BooleanField(default=True)
    quantity=models.IntegerField(blank=True, null=True)
    depth=models.CharField(max_length=200, blank=True, null=True)
    contractor_name = models.CharField(max_length=200, blank=True, null=True)
    con_contact_number = models.CharField(max_length=200, blank=True, null=True)
    con_address = models.TextField(blank=True, null=True)
    latitude = models.DecimalField(max_digits=40, decimal_places=16, blank=True, null=True)
    longitude = models.DecimalField(max_digits=40, decimal_places=16, blank=True, null=True)
    email_id = models.CharField(max_length=100, blank=True, null=True)
    requirment_s_date = models.DateTimeField(blank=True, null=True)
    requirment_e_date = models.DateTimeField(blank=True, null=True)
    budgeted_cost = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    executed_cost = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_o_s_l_w_c_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_o_s_l_w_c_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_o_s_l_w_c_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_pre_excution_office_setup_labour_water_connection'

# ::::::::::::PMS PRE EXECUTION OFFICE SETUP LABOUR ELECTRICAL CONNECTION::::::::::::::::::::::::::::#
class PmsPreExecutionOfficeSetupLabourElectricalConnection(models.Model):
    project = models.OneToOneField(PmsProjects, related_name='p_e_o_s_l_e_c_project',
                                on_delete=models.CASCADE, blank=True, null=True)
    # office_set_up = models.ForeignKey(PmsPreExecutionOfficeSetupMaster, related_name='p_e_o_s_l_e_c_office_set_up',
    #                                   on_delete=models.CASCADE, blank=True, null=True)
    local_connection = models.BooleanField(default=True)
    option = models.CharField(max_length=200, blank=True, null=True)
    nearby_elec_off_address = models.TextField(blank=True, null=True)
    latitude = models.DecimalField(max_digits=40, decimal_places=16, blank=True, null=True)
    longitude = models.DecimalField(max_digits=40, decimal_places=16, blank=True, null=True)
    contact_no = models.CharField(max_length=20, blank=True, null=True)
    detailed_procedure = models.TextField(blank=True, null=True)
    requirment_s_date = models.DateTimeField(blank=True, null=True)
    requirment_e_date = models.DateTimeField(blank=True, null=True)
    budgeted_cost = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    executed_cost = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_o_s_l_e_c_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_o_s_l_e_c_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_o_s_l_e_c_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_pre_excution_office_setup_labour_electrical_connection'

# ::::::::::::PMS PRE EXECUTION OFFICE SETUP RAW MATERIAL YARD/GODOWN/LAB::::::::::::::::::::::::::::#


# ::::::::::::PMS PRE EXECUTION OFFICE SETUP RAW MATERIAL YARD:::::::::::::::::::::::::::::::::#
class PmsPreExecutionOfficeSetupRawMaterialYard(models.Model):
    type_of_land = (
        (1, 'private_land'),
        (2, 'government_land')
    )
    type_of_protection = (
        (1, 'brick_wall'),
        (2, 'temporary_gi_sheets')
    )
    project = models.OneToOneField(PmsProjects, related_name='p_e_o_s_r_m_y_project',
                                on_delete=models.CASCADE, blank=True, null=True)
    # office_set_up = models.ForeignKey(PmsPreExecutionOfficeSetupMaster, related_name='p_e_o_s_r_m_y_office_set_up',
    #                                   on_delete=models.CASCADE, blank=True, null=True)
    land_type = models.IntegerField(choices=type_of_land, null=True, blank=True)
    protection_type = models.IntegerField(choices=type_of_protection, null=True, blank=True)
    area_of_yard= models.CharField(max_length=200, blank=True, null=True)
    rental_charge= models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    area_owner_name= models.CharField(max_length=200, blank=True, null=True)
    area_owner_phone_no= models.CharField(max_length=10, blank=True, null=True)
    area_owner_address= models.TextField(blank=True,null=True)
    latitude = models.DecimalField(max_digits=40, decimal_places=16, blank=True, null=True)
    longitude = models.DecimalField(max_digits=40, decimal_places=16, blank=True, null=True)
    requirment_s_date = models.DateTimeField(blank=True, null=True)
    requirment_e_date = models.DateTimeField(blank=True, null=True)
    budgeted_cost = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    executed_cost = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_o_s_r_m_y_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_o_s_r_m_y_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_o_s_r_m_y_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_pre_excution_office_setup_raw_material_yard'

# ::::::::::::PMS PRE EXECUTION OFFICE SETUP CEMENT GODOWN::::::::::::::::::::::::::::::::::#
class PmsPreExecutionOfficeSetupCementGodown(models.Model):
    type_of_protection = (
        (1, 'brick_wall'),
        (2, 'pre_fabricated_container')
    )
    project = models.OneToOneField(PmsProjects, related_name='p_e_o_s_c_g_d_project',
                                on_delete=models.CASCADE, blank=True, null=True)
    # office_set_up = models.ForeignKey(PmsPreExecutionOfficeSetupMaster, related_name='p_e_o_s_c_g_d_office_set_up',
    #                                   on_delete=models.CASCADE, blank=True, null=True)
    protection_type = models.IntegerField(choices=type_of_protection, null=True, blank=True)
    area_of_go_down = models.CharField(max_length=200, blank=True, null=True)
    rental_cost = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    capacity = models.IntegerField( null=True, blank=True)
    protection_cost = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    requirment_s_date = models.DateTimeField(blank=True, null=True)
    requirment_e_date = models.DateTimeField(blank=True, null=True)
    budgeted_cost = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    executed_cost = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_o_s_c_g_d_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_o_s_c_g_d_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_o_s_c_g_d_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_pre_excution_office_setup_cement_go_down'

# ::::::::::::PMS PRE EXECUTION OFFICE SETUP QA/QC LAB:::::::::::::::::::::::::::::::::::::::::::::::::#
class PmsPreExecutionOfficeSetupLab(models.Model):
    type_of_protection = (
        (1, 'brick_wall'),
        (2, 'pre_fabricated_container')
    )
    project = models.OneToOneField(PmsProjects, related_name='p_e_o_s_l_project',
                                on_delete=models.CASCADE, blank=True, null=True)
    # office_set_up = models.ForeignKey(PmsPreExecutionOfficeSetupMaster, related_name='p_e_o_s_l_office_set_up',
    #                                   on_delete=models.CASCADE, blank=True, null=True)
    protection_type = models.IntegerField(choices=type_of_protection, null=True, blank=True)
    area_of_lab = models.CharField(max_length=200, blank=True, null=True)
    rental_cost = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    capacity = models.CharField(max_length=200, blank=True, null=True)
    protection_cost = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    requirment_s_date = models.DateTimeField(blank=True, null=True)
    requirment_e_date = models.DateTimeField(blank=True, null=True)
    budgeted_cost = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    executed_cost = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_o_s_l_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_o_s_l_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_o_s_l_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_pre_excution_office_setup_lab'

# ::::::::::::PMS PRE EXECUTION OFFICE SETUP SURVEY INSTRUMENT::::::::::::::::::::::::::::::::::::::::#

class PmsPreExecutionOfficeSetupSurveyInstruments(models.Model):
    type_of_survey_instrument = (
        (1, 'required_survey_instruments'),
        (2, 'actual_survey_instruments')
    )
    project = models.ForeignKey(PmsProjects, related_name='p_e_o_s_s_i_project',
                                on_delete=models.CASCADE, blank=True, null=True)
    # office_set_up = models.ForeignKey(PmsPreExecutionOfficeSetupMaster, related_name='p_e_o_s_s_i_office_set_up',
    #                                   on_delete=models.CASCADE, blank=True, null=True)
    survey_instrument_type_tab=models.IntegerField(choices=type_of_survey_instrument, null=True, blank=True)
    requirment_s_date = models.DateTimeField(blank=True, null=True)
    requirment_e_date = models.DateTimeField(blank=True, null=True)
    budgeted_cost = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    executed_cost = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_o_s_s_i_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_o_s_s_i_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_o_s_s_i_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_pre_excution_office_setup_survey_instruments'

class PmsPreExecutionOfficeSetupSurveyInstrumentsType(models.Model):
    survey_instrument =models.ForeignKey(PmsPreExecutionOfficeSetupSurveyInstruments,related_name ='p_e_o_s_s_i_t_survey_instrument',
                                                                            on_delete=models.CASCADE, blank=True, null=True)
    project = models.ForeignKey(PmsProjects, related_name='p_e_o_s_s_i_t_project',
                                on_delete=models.CASCADE, blank=True, null=True)
    type_of_instrument=models.CharField(max_length=200, blank=True, null=True)
    quantity=models.IntegerField(blank=True,null=True)
    total_cost=models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_o_s_s_i_r_s_i_t_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_o_s_s_i_r_s_i_t_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_o_s_s_i_r_s_i_t_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_pre_excution_office_setup_survey_instruments_type'

# ::::::::::::PMS PRE EXECUTION OFFICE SETUP SAFETY PPE's::::::::::::::::::::::::::::::::::::::::::::::#

class PmsPreExecutionOfficeSetupSafetyPPEs(models.Model):
    project = models.ForeignKey(PmsProjects, related_name='p_e_o_s_s_p_project',
                                on_delete=models.CASCADE, blank=True, null=True)
    # office_set_up = models.ForeignKey(PmsPreExecutionOfficeSetupMaster, related_name='p_e_o_s_s_p_office_set_up',
    #                                   on_delete=models.CASCADE, blank=True, null=True)
    requirment_s_date = models.DateTimeField(blank=True, null=True)
    requirment_e_date = models.DateTimeField(blank=True, null=True)
    budgeted_cost = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    executed_cost = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_o_s_s_p_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_o_s_s_p_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_o_s_s_p_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_pre_excution_office_setup_safety_ppes'

class PmsPreExecutionOfficeSetupSafetyPPEsAccessory(models.Model):
    safety_ppe= models.ForeignKey(PmsPreExecutionOfficeSetupSafetyPPEs, related_name='p_e_o_s_s_p_a_safety_ppe',
                                on_delete=models.CASCADE, blank=True, null=True)
    project = models.ForeignKey(PmsProjects, related_name='p_e_o_s_s_p_a_project',
                                on_delete=models.CASCADE, blank=True, null=True)
    safety_accessory=models.CharField(max_length=200, blank=True, null=True)
    quantity=models.IntegerField(blank=True,null=True)
    total_cost=models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_o_s_s_p_a_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_o_s_s_p_a_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_o_s_s_p_a_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_pre_excution_office_setup_safety_ppes_accessory'

# ::::::::::::PMS PRE EXECUTION OFFICE SETUP SECURITY ROOM:::::::::::::::::::::::::::::::::::::#
class PmsPreExecutionOfficeSetupSecurityRoom(models.Model):
    type_of_security_room = (
        (1, 'office_container'),
        (2, 'existing_brick_work')
    )
    project = models.OneToOneField(PmsProjects, related_name='p_e_o_s_s_r_project',
                                on_delete=models.CASCADE, blank=True, null=True)
    # office_set_up = models.ForeignKey(PmsPreExecutionOfficeSetupMaster, related_name='p_e_o_s_s_r_office_set_up',
    #                                   on_delete=models.CASCADE, blank=True, null=True)
    security_room_type = models.IntegerField(choices=type_of_security_room, null=True, blank=True)
    size=models.CharField(max_length=200, blank=True, null=True)
    rate = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    agency_name=models.CharField(max_length=200, blank=True, null=True)
    agency_contact_no=models.CharField(max_length=10, blank=True, null=True)
    transportation_cost = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    requirment_s_date = models.DateTimeField(blank=True, null=True)
    requirment_e_date = models.DateTimeField(blank=True, null=True)
    budgeted_cost = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    executed_cost = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_o_s_s_r_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_o_s_s_r_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_o_s_s_r_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_pre_excution_office_setup_security_room'

# ::::::::::::PMS PRE EXECUTION P&M :::::::::::::::::::::::::::::::::::::#
class PmsPreExecutionMachineryTypeDetails(models.Model):
    type_of_p_and_m = (
        (1, 'purchase'),
        (2, 'rental')
    )
    project = models.ForeignKey(PmsProjects, related_name='p_e_p_a_m_d_project',
                                on_delete=models.CASCADE, blank=True, null=True)
    machinary_type=models.ForeignKey(PmsMachineryType, related_name='p_e_p_a_m_d_machine_type',
                                on_delete=models.CASCADE, blank=True, null=True)

    types= models.IntegerField(choices=type_of_p_and_m, null=True, blank=True)
    model_of_machinery=models.CharField(max_length=200, blank=True, null=True)
    fuel_consumption=models.CharField(max_length=200, blank=True, null=True)
    quantity = models.IntegerField(blank=True, null=True)
    capacity = models.CharField(max_length=200, blank=True, null=True)
    rate_per_product = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    operator_required=models.BooleanField(default=True)
    operator_name=models.CharField(max_length=200, blank=True, null=True)
    operator_contact_no=models.CharField(max_length=10, blank=True, null=True)
    operator_salary=models.CharField(max_length=200, blank=True, null=True)
    requirment_s_date = models.DateTimeField(blank=True, null=True)
    requirment_e_date = models.DateTimeField(blank=True, null=True)
    budgeted_cost = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    executed_cost = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_p_a_m_d_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_p_a_m_d_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_p_a_m_d_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_pre_execution_machinery_type_details'

##################################################################################
# ::::::::::::PMS PRE EXECUTION MANPOWER::::::::::::::::::::::::::::::#
##################################################################################

class PmsPreExecutionManpowerDetails(models.Model):
    project = models.ForeignKey(PmsProjects, related_name='p_e_m_d_project',
                                on_delete=models.CASCADE, blank=True, null=True)
    designation = models.ForeignKey(TCoreDesignation, related_name='p_e_m_d_des',on_delete=models.CASCADE, 
    blank=True, null=True)
    manpower = models.ForeignKey(User, related_name='p_e_m_d_manpower',on_delete=models.CASCADE, 
    blank=True, null=True)
    total_job_experience = models.CharField(max_length=100, blank=True, null=True)
    qualification = models.CharField(max_length=100, blank=True, null=True)
    job_description=models.TextField(blank=True,null=True)
    requirment_s_date = models.DateTimeField(blank=True, null=True)
    requirment_e_date = models.DateTimeField(blank=True, null=True)
    budgeted_salary = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    expected_salary = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_m_d_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_m_d_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_m_d_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_pre_excution_manpower_details'

#::::::::::::::::::::::::::::::::::::::PMS PRE EXECUTION COST ANALYSIS:::::::::::::::::::::::::::::::::#
class PmsPreExecutionCostAnalysis(models.Model):
    type_of_cost = (
        (1, 'local_market_rate'),
        (2, 'cost_analysis_sheet'),
        (3, 'time_schedule_or_work_plan')
    )
    project = models.ForeignKey(PmsProjects, related_name='p_e_c_a_project',
                                on_delete=models.CASCADE, blank=True, null=True)
    analysis_type=models.IntegerField(choices=type_of_cost, null=True, blank=True)
    document_name = models.CharField(max_length=100, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_c_a_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_c_a_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_c_a_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_pre_excution_cost_analysis'

class PmsPreExecutionCostAnalysisDocument(models.Model):
    cost_analysis = models.ForeignKey(PmsPreExecutionCostAnalysis, related_name='p_e_c_a_d_project',
                                      on_delete=models.CASCADE, blank=True, null=True)
    document = models.FileField(upload_to=get_directory_path,
                                default=None,
                                blank=True, null=True,
                                validators=[validate_file_extension]
                                )
    version = models.CharField(max_length=50)
    date = models.DateTimeField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_c_a_d_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_c_a_d_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_c_a_d_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_pre_excution_cost_analysis_document'

#::::::::::::::::::::::::::::::::::::::PMS PRE EXECUTION CONTRACTOR FINALIZATION:::::::::::::::::::::::::::::::::#
class PmsPreExecutionContractorFinalization(models.Model):
    project = models.ForeignKey(PmsProjects, related_name='p_e_c_f_project',
                                on_delete=models.CASCADE, blank=True, null=True)
    machinery = models.ForeignKey(PmsMachineries, related_name='p_e_c_f_machinery',
                                  on_delete=models.CASCADE, blank=True, null=True)
    contractor = models.ForeignKey(PmsExternalUsers, related_name='p_e_c_f_contractor',
                                   on_delete=models.CASCADE, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_c_f_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_c_f_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_c_f_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_pre_excution_contractor_finalization'

#::::::::::::::::::::::::::::::::::::::PMS PRE EXECUTION SITE PUJA:::::::::::::::::::::::::::::::::#
class PmsPreExecutionSitePuja(models.Model):
    project = models.ForeignKey(PmsProjects, related_name='p_e_s_p_project',
                                on_delete=models.CASCADE, blank=True, null=True)
    location = models.TextField(blank=True, null=True)
    latitude = models.DecimalField(max_digits=40, decimal_places=16, blank=True, null=True)
    longitude = models.DecimalField(max_digits=40, decimal_places=16, blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)
    budget = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_s_p_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_s_p_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_s_p_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_pre_excution_site_puja'

#::::::::::::PMS PRE EXECUTION APPROVAL:::::::::#
class PmsPreExecutionApproval(models.Model):
    list_of_tabs=((1,'site_mobilization'),
                  (2,'office_set_up'),
                  (3,'p_and_m'),
                  (4,'manpower'),
                  (5,'cost_analysis'),
                  (6,'contractor_finalization'),
                  (7,'site_puja'))
    type_of_approved_status=((1,'approve'),
                             (2,'reject'),
                             (3,'modification'))
    project = models.ForeignKey(PmsProjects, related_name='p_e_a_project',
                                on_delete=models.CASCADE, blank=True, null=True)
    pre_execution_tabs = models.IntegerField(choices=list_of_tabs, blank=True, null=True)
    approved_status=models.IntegerField(choices=type_of_approved_status,null=True,blank=True)
    request_modification=models.TextField(blank=True,null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_a_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_a_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_a_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_pre_excution_approval'
