from django.db import models
from django.contrib.auth.models import User
from dynamic_media import get_directory_path
from django_mysql.models import EnumField
from validators import validate_file_extension
from core.models import TCoreUnit
import datetime
import time
from pms.models.module_project import *
from pms.models.module_external_user import PmsExternalUsers

# ::: PMS Machineries Type ::::::::::::::::::#
class PmsMachineryType(models.Model):
    name = models.CharField(max_length=100,blank=True, null=True, unique=True)
    description = models.TextField(blank=True,null=True)
    is_default = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='t_m_t_created_by',
                                   on_delete=models.CASCADE,blank=True,null=True)
    owned_by = models.ForeignKey(User, related_name='t_m_t_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='t_m_t_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'pms_machinery_type'

# ::: PMS Machineries Working Category ::::::::::::::::::#
class PmsMachineriesWorkingCategory(models.Model):
    name = models.CharField(max_length=200, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='machineries_working_category_created_by',
    on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='machineries_working_category_owned_by',
    on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='machineries_working_category_updated_by',
    on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_machineries_working_category'

# ::: PMS Machineries ::::::::::::::::::#
class PmsMachineries(models.Model):
    Type_of_owner = (
    (1, 'rental'),
    (2, 'own'),
    (3, 'contract'),
    (4,'lease')
    )
    Type_of_measurement = (
    (1, 'distance'),
    (2, 'time')
    )
    code = models.CharField(max_length=50, blank=True, null=True)
    equipment_name = models.CharField(max_length=200, blank=True, null=True)
    equipment_category = models.ForeignKey(
        PmsMachineriesWorkingCategory,related_name='equipment_working_category',
    on_delete=models.CASCADE,blank=True,null=True)
    equipment_type = models.ForeignKey(
        PmsMachineryType,related_name='m_equipment_type',
    on_delete=models.CASCADE,blank=True,null=True)
    owner_type = models.IntegerField(choices=Type_of_owner, null=True, blank=True)
    equipment_make = models.CharField(max_length=200, blank=True, null=True)
    equipment_model_no = models.CharField(max_length=200, blank=True, null=True)
    equipment_chassis_serial_no = models.CharField(max_length=100, blank=True, null=True)
    equipment_engine_serial_no = models.CharField(max_length=100, blank=True, null=True)
    equipment_registration_no = models.CharField(max_length=200, blank=True, null=True)
    equipment_power = models.CharField(max_length=200, blank=True, null=True)
    measurement_by = models.IntegerField(choices=Type_of_measurement, null=True, blank=True)
    measurement_quantity = models.CharField(max_length=200, blank=True, null=True)
    fuel_consumption = models.CharField(max_length=100, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='machinery_created_by',
    on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='machinery_owned_by',
    on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='machinery_updated_by',
    on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_machineries'

class PmsMachineriesDetailsDocument(models.Model):
    equipment = models.ForeignKey(PmsMachineries, related_name='equipment_machineries', on_delete=models.CASCADE,
                                  blank=True, null=True)
    document_name = models.CharField(max_length=200, blank=True, null=True)
    document = models.FileField(upload_to=get_directory_path,
                                default=None,
                                blank=True, null=True,
                                validators=[validate_file_extension]
                                )
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='machinery_document_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='machinery_document_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='machinery_document_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_machineries_document'

#::::::::::Pms Machinary Rented Type Master:::::::::::#
class PmsMachinaryRentedTypeMaster(models.Model):
    name = models.CharField(max_length=200, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='machinery_rented_type_master_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='machinery_rented_type_master_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='machinery_rented_type_master_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_machinary_rented_type_master'

#::::::::::::Pms Machinary Rented Details::::::::::#
class PmsMachinaryRentedDetails(models.Model):
    equipment = models.ForeignKey(PmsMachineries, related_name='equipment_machineries_rented_details',
                                  on_delete=models.CASCADE, blank=True, null=True)
    vendor = models.ForeignKey(PmsExternalUsers, related_name='vendors_machineries_rented_details',
                                on_delete=models.CASCADE, blank=True, null=True)
    rent_amount = models.CharField(max_length=200, blank=True, null=True)
    type_of_rent = models.ForeignKey(PmsMachinaryRentedTypeMaster, related_name='machinary_rented_details',
                                     on_delete=models.CASCADE, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='machinery_rented_details_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='machinery_rented_details_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='machinery_rented_details_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_machinary_rented_details'

#:::::::::::::Pms Machinary Owner Details:::::::::::::::::#
class PmsMachinaryOwnerDetails(models.Model):
    equipment = models.ForeignKey(PmsMachineries, related_name='machinary_owner_details',
                                  on_delete=models.CASCADE, blank=True, null=True)
    purchase_date = models.DateTimeField(blank=True, null=True)
    price = models.FloatField(blank=True, null=True)
    is_emi_available = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='machinery_owner_details_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='machinery_owner_details_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='machinery_owner_details_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_machineries_owner_details'

#:::::::::::Pms Machinary Owner EMI Details:::::::::::::::::#
class PmsMachinaryOwnerEmiDetails(models.Model):
    equipment = models.ForeignKey(PmsMachineries, related_name='machinary_owner_emi_details',
                                  on_delete=models.CASCADE, blank=True, null=True)

    equipment_owner_details = models.ForeignKey(PmsMachinaryOwnerDetails,
                                                related_name='machinary_owner_emi_details',
                                                on_delete=models.CASCADE, blank=True, null=True)

    amount = models.FloatField(blank=True, null=True)
    start_date = models.DateTimeField(blank=True, null=True)
    no_of_total_installment = models.IntegerField(null=True, blank=True)
    #no_of_remain_installment = models.IntegerField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='machinery_owner_emi_details_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='machinery_owner_emi_details_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='machinery_owner_emi_details_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_machineries_owner_emi_details'

#:::::::::Pms Machinary Contract Details:::::::::::::::::#
class PmsMachinaryContractDetails(models.Model):
    equipment = models.ForeignKey(PmsMachineries, related_name='machinary_contract_details',
                                  on_delete=models.CASCADE, blank=True, null=True)
    contractor = models.ForeignKey(PmsExternalUsers, related_name='machinary_contract_details_contractor',
                                   on_delete=models.CASCADE, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='machinery_contract_details_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='machinery_contract_details_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='machinery_contract_details_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_machineries_contract_details'

#:::::::::Pms Machinary Lease Details:::::::::::::::::#

class PmsMachinaryLeaseDetails(models.Model):
    equipment = models.ForeignKey(PmsMachineries, related_name='machinary_lease_details',
                                  on_delete=models.CASCADE, blank=True, null=True)
    vendor = models.ForeignKey(PmsExternalUsers, related_name='vendors_machineries_lease_details',
                                on_delete=models.CASCADE, blank=True, null=True)
    lease_amount=models.DecimalField(max_digits=10,decimal_places=2,blank=True,null=True)
    start_date=models.DateTimeField(blank=True, null=True)
    lease_period=models.CharField(max_length=200, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='machinary_lease_details_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='machinary_lease_details_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='machinary_lease_details_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_machineries_lease_details'


#:::::::::::::::: PROJECTS MACHINARY REPORTS :::::::::::#
class PmsProjectsMachinaryReport(models.Model):
    machine = models.ForeignKey(PmsMachineries,related_name='m_r_machinary_id',
                               on_delete=models.CASCADE,blank=True,null=True)
    date = models.DateTimeField(blank=True, null=True)
    opening_balance = models.DecimalField(blank=True, null=True, max_digits=10,decimal_places=5)
    cash_purchase = models.DecimalField(blank=True, null=True,max_digits=10,decimal_places=5)
    diesel_transfer_from_other_site = models.DecimalField(blank=True, null=True,max_digits=10,decimal_places=5)
    total_diesel_available = models.DecimalField(blank=True, null=True, max_digits=10,decimal_places=5)
    total_diesel_consumed = models.DecimalField(blank=True, null=True, max_digits=10,decimal_places=5)
    diesel_balance = models.DecimalField(blank=True, null=True, max_digits=10,decimal_places=5)
    diesel_consumption_by_equipment = models.DecimalField(blank=True, null=True,max_digits=10,decimal_places=5)
    other_consumption = models.DecimalField(blank=True, null=True,max_digits=10,decimal_places=5)
    miscellaneous_consumption = models.DecimalField(blank=True, null=True,max_digits=10,decimal_places=5)
    opening_meter_reading = models.DecimalField(blank=True, null=True,max_digits=10,decimal_places=5)
    closing_meter_reading = models.DecimalField(blank=True, null=True,max_digits=10,decimal_places=5)
    running_km = models.DecimalField(blank=True, null=True,max_digits=10,decimal_places=5)
    running_hours = models.DecimalField(blank=True, null=True,max_digits=10,decimal_places=5)
    purpose = models.TextField(blank=True,null=True)
    last_pm_date = models.DateTimeField(blank=True, null=True)
    next_pm_schedule = models.DateTimeField(blank=True, null=True)
    difference_in_reading = models.DecimalField(blank=True, null=True,max_digits=10,decimal_places=5)
    hsd_average = models.DecimalField(blank=True, null=True,max_digits=10,decimal_places=5)
    standard_avg_of_hours = models.DecimalField(blank=True, null=True,max_digits=10,decimal_places=5)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='m_m_r_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='m_m_r_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='m_m_r_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'pms_machinary_report'