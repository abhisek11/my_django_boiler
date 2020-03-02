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
from pms.models.module_approval_permission import *

#::::::::::  PMS EXECUTION PURCHASES REQUISITIONS ACTIVITIES MASTER ;::::::::#
class PmsExecutionPurchasesRequisitionsActivitiesMaster(models.Model):
    code = models.CharField(max_length=200,blank=True,null=True)
    description = models.CharField(max_length=200, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_p_r_a_m_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_p_r_a_m_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_p_r_a_m_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'pms_execution_purchases_requisitions_activities_master'
#::::::::::  PMS EXECUTION PLANNING AND REPORT TABLE ::::::::#
# PROJECT PLANNING
class PmsExecutionProjectPlaningMaster(models.Model):
    project = models.ForeignKey(PmsProjects, related_name='p_e_pp_project_id',
                                on_delete=models.CASCADE, blank=True, null=True)
    site_location = models.ForeignKey(PmsSiteProjectSiteManagement, related_name='p_e_pp_site_location',
                                      on_delete=models.CASCADE, blank=True, null=True)
    name_of_work = models.TextField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_pp_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_pp_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_pp_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_execution_project_planning_master'


class PmsExecutionProjectPlaningFieldLabel(models.Model):
    project_planning = models.ForeignKey(PmsExecutionProjectPlaningMaster,
                                         related_name='p_e_fl_project_planing_id',
                                         on_delete=models.CASCADE,
                                         blank=True,
                                         null=True
                                         )
    field_label = models.CharField(max_length=100, blank=True, null=True)
    status = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_fl_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_fl_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_fl_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_execution_project_planning_field_label'


class PmsExecutionProjectPlaningFieldValue(models.Model):
    project_planning = models.ForeignKey(PmsExecutionProjectPlaningMaster,
                                         related_name='p_e_fv_project_planing_id',
                                         on_delete=models.CASCADE,
                                         blank=True,
                                         null=True
                                         )
    initial_field_label = models.ForeignKey(PmsExecutionProjectPlaningFieldLabel,
                                            related_name='p_e_fv_label_id',
                                            on_delete=models.CASCADE,
                                            blank=True,
                                            null=True
                                            )
    field_value = models.CharField(max_length=100, blank=True, null=True)
    status = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_fv_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_fv_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_fv_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_execution_project_planning_field_value'

#::::::::::::::::::::::::DAILY DATA TABLES::::::::::::::::::::::::::#
class PmsExecutionDailyProgress(models.Model):
    type_of_report = (
        (1, 'PROGRESS_REPORT'),
        (2, 'LABOUR_REPORT'),
        (3, 'PANDM_REPORT')
    )
    type_of_report = models.IntegerField(choices=type_of_report, null=True, blank=True)
    project_id = models.ForeignKey(PmsProjects, related_name='p_e_pr_project_id',
                                   on_delete=models.CASCADE, blank=True, null=True)
    site_location = models.ForeignKey(PmsSiteProjectSiteManagement, related_name='p_e_pr_site_location',
                                      on_delete=models.CASCADE, blank=True, null=True)
    date_entry = models.DateTimeField(blank=True, null=True)
    weather = models.CharField(max_length=200, blank=True, null=True)
    date_of_completion = models.DateTimeField(blank=True, null=True)
    milestone_to_be_completed = models.TextField(blank=True,null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_pr_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_pr_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_pr_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_execution_daily_progress'

#:::::::::::::::::::::::::::DAILY DATA TABLES PROGRESS::::::::::::::::#
class PmsExecutionDailyProgressProgress(models.Model):
    daily_progress = models.ForeignKey(PmsExecutionDailyProgress, related_name='daily_progress',
                                       on_delete=models.CASCADE, blank=True, null=True)

    activity =  models.ForeignKey(PmsExecutionPurchasesRequisitionsActivitiesMaster, related_name='pedp_activity',
                                   on_delete=models.CASCADE, blank=True, null=True)
    description = models.TextField(blank=True,null=True)
    uom = models.ForeignKey(TCoreUnit, related_name='pedp_uom',
                                     on_delete=models.CASCADE, blank=True, null=True)
    planned_start_time=models.TimeField(blank=True, null=True)
    planned_end_time=models.TimeField(blank=True, null=True)
    actual_start_time=models.TimeField(blank=True, null=True)
    actual_end_time=models.TimeField(blank=True, null=True)
    planned_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    archieved_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    assigned_to = models.ForeignKey(User, related_name='pedp_assigned_to',
                                   on_delete=models.CASCADE, blank=True, null=True)
    contractors_name = models.ForeignKey(PmsExternalUsers, related_name='pedp_contractors_name',
                                on_delete=models.CASCADE, blank=True, null=True)
    remarks = models.TextField(blank=True,null=True)
    major_achivements = models.TextField(blank=True, null=True)
    # status = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='pedp_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='pedp_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='pedp_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_execution_daily_progress_progress'


#::::::::::::::::::::::::::LABOUR REPORT::::::::::::::::::::::::#
class PmsExecutionDailyProgressLabourReport(models.Model):
    labour_report = models.ForeignKey(PmsExecutionDailyProgress, related_name='p_e_pr_p_labour_id',
                                      on_delete=models.CASCADE, blank=True, null=True)
    name_of_contractor = models.ForeignKey(PmsExternalUsers, related_name='p_e_pr_p_contractors_name',
                                on_delete=models.CASCADE, blank=True, null=True)
    number_skilled = models.IntegerField(null=True, blank=True)
    number_unskilled = models.IntegerField(null=True, blank=True)
    activity =  models.ForeignKey(PmsExecutionPurchasesRequisitionsActivitiesMaster, related_name='p_e_pr_p_activity',
                                   on_delete=models.CASCADE, blank=True, null=True)
    details_activity = models.TextField(blank=True, null=True)
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    remarks = models.TextField(blank=True,null=True)
    status = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_pr_p_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_pr_p_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_pr_p_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_execution_daily_progress_labour_report'

# PLANNED AND MACHINERY ;::::::::#
class PmsExecutionDailyProgressPandM(models.Model):
    plan_machine_report = models.ForeignKey(PmsExecutionDailyProgress, related_name='p_e_pr_p_pm_id',
                                            on_delete=models.CASCADE, blank=True, null=True)
    activity =  models.ForeignKey(PmsExecutionPurchasesRequisitionsActivitiesMaster, related_name='p_e_pr_p_pm_activity',
                                   on_delete=models.CASCADE, blank=True, null=True)
    details_of_activity = models.TextField(blank=True, null=True)
    machinery_used = models.ForeignKey(PmsMachineries, related_name='p_e_pr_machinery_id',
                                       on_delete=models.CASCADE, blank=True, null=True)
    used_by = models.CharField(max_length=200, blank=True, null=True)
    unit_details = models.ForeignKey(TCoreUnit, related_name='p_e_pr_p_unit_id',
                                     on_delete=models.CASCADE, blank=True, null=True)
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    unit_from = models.DecimalField(max_digits=8, decimal_places=2,blank=True, null=True)
    unit_to = models.DecimalField(max_digits=8, decimal_places=2,blank=True, null=True) 
    remarks = models.TextField(blank=True,null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_pr_pm_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_pr_pm_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_pr_pm_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_execution_daily_progress_plant_nd_machinery'




#:::::::::::::::::::::::::::::: PMS EXECUTION PURCHASES REQUISITIONS TYPE MASTER ;:::::::::::::::::::::::::::::
class PmsExecutionPurchasesRequisitionsTypeMaster(models.Model):
    type_name = models.CharField(max_length=100, blank=True, null=True)
    code = models.CharField(max_length=50, blank=True, null=True)

    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_p_r_t_m_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_p_r_t_m_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_p_r_t_m_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_execution_purchases_requisitions_type_master'

#::::::::::::::::::::::::::::::::: PMS EXECUTION PURCHASES REQUISITIONS MASTER ;::::::::::::::::::::::::::::::::::#
class PmsExecutionPurchasesRequisitionsMaster(models.Model):
    # status_type = (
    #     (0, 'Starting'),
    #     (1, 'Pending'),
    #     (2, 'Approved'),
    #     (3, 'Processing'),
    #     (4, 'Delivery'),
    #     (5, 'Payment'),
    #     (6, 'completed'),
    #     (7, 'cancled'),
    #     (8, 'Quotation Approval Pending'),
    #     (9, 'Quotation Approval Approved')
    # )

    status_type = (
        (0, 'Starting'),
        (1, 'Pending'),
        (2, 'Approved'),
        (3, 'Quotation_Approval_Pending'),
        (4, 'Quotation_Approval_Approved'),
        (5, 'PO'),
        (6, 'Dispach'),
        (7, 'Delivery'),
        (8, 'Payment'),
        (9, 'Completed'),
        (10, 'Cancled')
    )
    # completed_status_type = (
    #     (1, 'PO_Completed'),
    #     (2, 'Dispatch_Completed'),
    #     (3, 'Delivery_Completed'),
    #     (4, 'Payment_Completed'),
    #     (5, 'comparitive_statement_completed')
    # )
    completed_status_type = (
        (1, 'comparitive_statement_completed'),
        (2, 'PO_Completed'),
        (3, 'Dispatch_Completed'),
        (4, 'Delivery_Completed'),
        (5, 'Payment_Completed'),
    )
    mr_date = models.DateTimeField(blank=True, null=True)
    site_location = models.ForeignKey(PmsSiteProjectSiteManagement, related_name='p_e_p_r_m_site_location',
                                      on_delete=models.CASCADE, blank=True, null=True)
    project = models.ForeignKey(PmsProjects, related_name='p_e_p_r_m_project_id',
                                on_delete=models.CASCADE, blank=True, null=True)
    type = models.ForeignKey(PmsExecutionPurchasesRequisitionsTypeMaster, related_name='p_e_p_r_m_type',
                                      on_delete=models.CASCADE, blank=True, null=True)
    status = models.IntegerField(choices=status_type, null=True, blank=True, default=0)
    completed_status = models.IntegerField(choices=completed_status_type, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_p_r_m_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_p_r_m_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_p_r_m_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_execution_purchases_requisitions_master'

#::::::::::  PMS EXECUTION PURCHASES REQUISITIONS  ;::::::::#
class PmsExecutionPurchasesRequisitions(models.Model):
    # term_type = (
    #     (1, 'Short Term'),
    #     (2, 'Long Term')
    # )
    requisitions_master = models.ForeignKey(PmsExecutionPurchasesRequisitionsMaster, related_name='p_e_p_r_master',
                                            on_delete=models.CASCADE, blank=True, null=True)
    item = models.IntegerField(blank=True,null=True)
    # terms =  models.IntegerField(choices=term_type, null=True, blank=True)
    hsn_sac_code= models.CharField(max_length=100, blank=True,null=True)
    uom = models.ForeignKey(TCoreUnit, related_name='p_e_p_r_unit',
                            on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=3,blank=True, null=True)
    current_stock = models.DecimalField(max_digits=10, decimal_places=3,blank=True, null=True)
    procurement_site = models.DecimalField(max_digits=10, decimal_places=3,blank=True, null=True)
    procurement_ho = models.DecimalField(max_digits=10, decimal_places=3,blank=True, null=True)
    required_by = models.CharField(max_length=100, blank=True,null=True)
    required_on = models.DateTimeField(blank=True, null=True)
    remarks = models.TextField(blank=True,null=True)
    is_approved = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_p_r_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_p_r_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_p_r_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    


    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'pms_execution_purchases_requisitions'

#::::::::::  PMS EXECUTION PURCHASES REQUISITIONS MAPPING WITH ACTIVITIES ;::::::::#
class PmsExecutionPurchasesRequisitionsMapWithActivities(models.Model):
    requisitions = models.ForeignKey(PmsExecutionPurchasesRequisitions, related_name='p_e_p_r_m_p_w_a_requisitions',
                                   on_delete=models.CASCADE, blank=True, null=True)
    activity =  models.ForeignKey(PmsExecutionPurchasesRequisitionsActivitiesMaster, related_name='p_e_p_r_m_p_w_a_activity',
                                   on_delete=models.CASCADE, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_p_r_m_p_w_a_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_p_r_m_p_w_a_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_p_r_m_p_w_a_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'pms_execution_purchases_requisitions_map_with_activities'

#:::::::::::::::  PMS EXECUTION PURCHASES QUOTATIONS PAYMENT TERMS MASTER ;:::::::::::::#
class PmsExecutionPurchasesQuotationsPaymentTermsMaster(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_p_q_p_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_p_q_p_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_p_q_p_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'pms_execution_purchases_quotations_payment_terms_master'

#::::::::::  PMS EXECUTION PURCHASES QUOTATIONS ;::::::::::#
class PmsExecutionPurchasesQuotations(models.Model):

    # requisitions = models.ForeignKey(PmsExecutionPurchasesRequisitions, related_name='p_e_p_r_requisitions',
    #                                on_delete=models.CASCADE, blank=True, null=True)
    requisitions_master = models.ForeignKey(PmsExecutionPurchasesRequisitionsMaster, related_name='p_e_p_r_requisitions',
        on_delete=models.CASCADE, blank=True, null=True)
    vendor = models.ForeignKey(PmsExternalUsers, related_name='p_e_p_q_vendors',
                                on_delete=models.CASCADE, blank=True, null=True)
    payment_terms = models.ForeignKey(PmsExecutionPurchasesQuotationsPaymentTermsMaster,
                                      related_name='p_e_p_q_payment_terms',
                                      on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.DecimalField(max_digits=12, decimal_places=5,blank=True,null=True,default=0.0)
    unit = models.ForeignKey(TCoreUnit, related_name='p_e_p_q_unit',
                                on_delete=models.CASCADE, blank=True, null=True)
    price = models.FloatField(blank=True, null=True)
    delivery_date = models.DateTimeField(blank=True, null=True)
    remarks= models.TextField(blank=True,null=True)
    document_name = models.CharField(max_length=50,blank=True,null=True)
    document = models.FileField(upload_to=get_directory_path,
                                         default=None,
                                         blank=True, null=True,
                                         validators=[validate_file_extension]
                                         )
    discount = models.DecimalField(max_digits=12, decimal_places=5, blank=True, null=True)
    final_price = models.DecimalField(max_digits=20, decimal_places=5, blank=True, null=True)
    item = models.IntegerField(blank=True, null=True)
    # type = models.CharField(max_length=50,blank=True,null=True)
    # quotation_approved= models.BooleanField(default=False) #Added By Koushik 8.01.2020#
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_p_q_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_p_q_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_p_q_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'pms_execution_purchases_quotations'


#:::::::::::::::::::::::  PMS EXECUTION PURCHASES COMPARITIVE STATEMENT::::::::::::::::::::::::::::::::::::::::::::::#
class PmsExecutionPurchasesComparitiveStatement(models.Model):
    requisitions_master = models.ForeignKey(PmsExecutionPurchasesRequisitionsMaster, related_name='p_e_p_c_s_requisitions',
                                            on_delete=models.CASCADE, blank=True, null=True)
    vendor = models.ForeignKey(PmsExternalUsers, related_name='p_e_p_c_s_vendors', on_delete=models.CASCADE,
                               blank=True, null=True)
    item = models.IntegerField(blank=True, null=True)
    uom = models.ForeignKey(TCoreUnit, related_name='p_e_p_c_s_uom',
                                on_delete=models.CASCADE, blank=True, null=True)
    discount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    final_price = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    price_basis = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    make = models.TextField(blank=True, null=True)
    base_price = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    packaging_and_forwarding = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    freight_up_to_site = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    cgst = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    sgst = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    igst = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    payment_terms = models.ForeignKey(PmsExecutionPurchasesQuotationsPaymentTermsMaster,
                                      related_name='p_e_p_c_s_payment_terms',
                                      on_delete=models.CASCADE, blank=True, null=True)
    approval_permission_user_level =  models.ForeignKey(PmsApprovalPermissonMatser, related_name='p_e_p_c_s_permission_id',
                                   on_delete=models.CASCADE, blank=True, null=True)

    delivery_time = models.IntegerField(blank=True, null=True)
    total_order_value = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    net_landed_cost = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    inco_terms = models.CharField(max_length=200,blank=True,null=True)
    warranty_guarantee = models.CharField(max_length=200,blank=True,null=True)
    is_approved = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_p_c_s_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_p_c_s_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_p_c_s_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'pms_execution_purchases_comparitive_statement'

class PmsExecutionPurchasesComparitiveStatementLog(models.Model):
    requisitions_master = models.ForeignKey(PmsExecutionPurchasesRequisitionsMaster, related_name='p_e_p_c_s_l_requisitions',
                                            on_delete=models.CASCADE, blank=True, null=True)
    vendor = models.ForeignKey(PmsExternalUsers, related_name='p_e_p_c_s_l_vendors', on_delete=models.CASCADE,
                               blank=True, null=True)
    item = models.IntegerField(blank=True, null=True)
    uom = models.ForeignKey(TCoreUnit, related_name='p_e_p_c_s_l_uom',
                                on_delete=models.CASCADE, blank=True, null=True)
    discount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    final_price = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    price_basis = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    make = models.TextField(blank=True, null=True)
    base_price = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    packaging_and_forwarding = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    freight_up_to_site = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    cgst = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    sgst = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    igst = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    payment_terms = models.ForeignKey(PmsExecutionPurchasesQuotationsPaymentTermsMaster,
                                      related_name='p_e_p_c_s_l_payment_terms',
                                      on_delete=models.CASCADE, blank=True, null=True)
    approval_permission_user_level =  models.ForeignKey(PmsApprovalPermissonMatser, related_name='p_e_p_c_s_l_permission_id',
                                   on_delete=models.CASCADE, blank=True, null=True)

    delivery_time = models.IntegerField(blank=True, null=True)
    total_order_value = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    net_landed_cost = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    inco_terms = models.CharField(max_length=200,blank=True,null=True)
    warranty_guarantee = models.CharField(max_length=200,blank=True,null=True)
    is_approved = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_p_c_s_l_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_p_c_s_l_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_p_c_s_l_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'pms_execution_purchases_comparitive_statement_log'

#::::::::::::PMS EXECUTION PURCHASES COMPARITIVE STATEMENT DOCUMENT::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::#
class PmsExecutionPurchasesComparitiveStatementDocument(models.Model):
    comparitive_statement = models.ForeignKey(PmsExecutionPurchasesComparitiveStatement, related_name='p_e_p_c_s_d_comparitive_statement',
                                on_delete=models.CASCADE, blank=True, null=True)
    document_name = models.CharField(max_length=100, blank=True, null=True)
    document = models.FileField(upload_to=get_directory_path,
                                default=None,
                                blank=True, null=True,
                                validators=[validate_file_extension])
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_p_c_s_d_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_p_c_s_d_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_p_c_s_d_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_excution_purchases_comparitive_statement_document'


###################################################################################################
#:::::::::::::::::::::::::  PMS EXECUTION PURCHASES PO MASTER ;::::::::::::::::::::::::::::#
class PmsExecutionPurchasesPOMaster(models.Model):
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_p_po_m_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_p_po_m_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_p_po_m_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'pms_execution_purchases_po_master'


#:::::::::::  PMS EXECUTION PURCHASES PO MASTER  ;::::::::::#
class PmsExecutionPurchasesPOTransportCostMaster(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    code = models.CharField(max_length=100, blank=True, null=True)
    type_desc = models.TextField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_p_po_t_m_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_p_po_t_m_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_p_po_t_m_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'pms_execution_purchases_po_transport_cost_master'

#::::::::::::::::::::::::::::::::::::  PMS EXECUTION PURCHASES PO  ;::::::::::::::::::::::::::::::#
class PmsExecutionPurchasesPO (models.Model):
    requisitions_master = models.ForeignKey(PmsExecutionPurchasesRequisitionsMaster, related_name='p_e_p_po_master',
                                            on_delete=models.CASCADE, blank=True, null=True)
    vendor =  models.ForeignKey(PmsExternalUsers, related_name='p_e_p_po_vendors',
                                on_delete=models.CASCADE, blank=True, null=True)
    date_of_po = models.DateTimeField(blank=True, null=True)
    po_no = models.CharField(max_length=200, blank=True, null=True)
    po_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    transport_cost_type = models.ForeignKey(PmsExecutionPurchasesPOTransportCostMaster, related_name='p_e_p_po_transport_cost',
                                       on_delete=models.CASCADE, blank=True, null=True)
    transport_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_p_po_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    approval_permission_user_level =  models.ForeignKey(PmsApprovalPermissonMatser, related_name='p_e_p_po_permission_id',
                                   on_delete=models.CASCADE, blank=True, null=True)

    owned_by = models.ForeignKey(User, related_name='p_e_p_po_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_p_po_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'pms_execution_purchases_po'


class PmsExecutionPurchasesPOLog (models.Model):
    requisitions_master = models.ForeignKey(PmsExecutionPurchasesRequisitionsMaster, related_name='p_e_p_po_l_master',
                                            on_delete=models.CASCADE, blank=True, null=True)
    vendor =  models.ForeignKey(PmsExternalUsers, related_name='p_e_p_po_l_vendors',
                                on_delete=models.CASCADE, blank=True, null=True)
    date_of_po = models.DateTimeField(blank=True, null=True)
    po_no = models.CharField(max_length=200, blank=True, null=True)
    po_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    transport_cost_type = models.ForeignKey(PmsExecutionPurchasesPOTransportCostMaster, related_name='p_e_p_po_l_transport_cost',
                                       on_delete=models.CASCADE, blank=True, null=True)
    transport_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_p_po_l_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    approval_permission_user_level =  models.ForeignKey(PmsApprovalPermissonMatser, related_name='p_e_p_po_l_permission_id',
                                   on_delete=models.CASCADE, blank=True, null=True)

    owned_by = models.ForeignKey(User, related_name='p_e_p_po_l_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_p_po_l_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'pms_execution_purchases_po_log'


class PmsExecutionPurchasesPOItemsMAP(models.Model):
    purchase_order = models.ForeignKey(PmsExecutionPurchasesPO, related_name='p_e_p_po_i_m_master',
                                       on_delete=models.CASCADE, blank=True, null=True)
    item = models.IntegerField(blank=True, null=True)
    quantity = models.IntegerField(blank=True, null=True)
    uom = models.ForeignKey(TCoreUnit, related_name='p_e_p_po_i_m_unit_id',
                            on_delete=models.CASCADE, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_p_po_i_m_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_p_po_i_m_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_p_po_i_m_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_execution_purchases_po_item_map'

#:::::::::::  PMS EXECUTION PURCHASES PO DOCUMENT ;::::::::::#
class PmsExecutionPurchasesPODocument(models.Model):
    purchase_order = models.ForeignKey(PmsExecutionPurchasesPO, related_name='p_e_p_po_d_po_no',
                               on_delete=models.CASCADE, blank=True, null=True)
    document_name = models.CharField(max_length=100, blank=True, null=True)
    document = models.FileField(upload_to=get_directory_path,
                                default=None,
                                blank=True, null=True,
                                validators=[validate_file_extension]
                                )
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_p_po_d_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_p_po_d_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_p_po_d_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'pms_execution_purchases_po_document'

#:::::::::::::::::::::::  PMS EXECUTION PURCHASES REQUISITION APPROVAL::::::::::::::::::::::::::::::::::::::::::::::#
class PmsExecutionPurchasesRequisitionsApproval(models.Model):
    approval_type = (
        (0, 'Reject'),
        (1, 'Approve'),
        (2, 'Modification'))
    requisitions_master = models.ForeignKey(PmsExecutionPurchasesRequisitionsMaster, related_name='p_e_p_r_approval',
                                  on_delete=models.CASCADE, blank=True, null=True)
    site_location = models.ForeignKey(PmsSiteProjectSiteManagement, related_name='p_e_p_r_a_site_location',
                                      on_delete=models.CASCADE, blank=True, null=True)
    project = models.ForeignKey(PmsProjects, related_name='p_e_p_r_a_project_id',
                                   on_delete=models.CASCADE, blank=True, null=True)
    item = models.IntegerField(blank=True, null=True)
    type = models.ForeignKey(PmsExecutionPurchasesRequisitionsTypeMaster, related_name='p_e_p_r_a_type',
                                    on_delete=models.CASCADE, blank=True, null=True)
    uom = models.ForeignKey(TCoreUnit, related_name='p_e_p_r_a_unit_id',
                            on_delete=models.CASCADE, blank=True, null=True)
    initial_estimate=models.CharField(max_length=100, blank=True,null=True)
    as_per_drawing=models.CharField(max_length=100, blank=True,null=True)
    #current_stock=models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_p_r_a_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_p_r_a_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_p_r_a_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # l1_approval= models.BooleanField(default=False)
    arm_approval = models.IntegerField(choices=approval_type, null=True, blank=True)
    approval_permission_user_level =  models.ForeignKey(PmsApprovalPermissonMatser, related_name='p_e_p_r_a_permission_id',
                                   on_delete=models.CASCADE, blank=True, null=True)

    approved_quantity = models.CharField(max_length=100, blank=True, null=True)
    available_quantity = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    quotation_approved= models.BooleanField(default=False) #Added By Koushik 8.01.2020#
    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'pms_execution_purchases_requisitions_approval'

class PmsExecutionPurchasesRequisitionsApprovalLogTable(models.Model):
    approval_type = (
        (0, 'Reject'),
        (1, 'Approve'),
        (2, 'Modification'))
    requisitions_master = models.ForeignKey(PmsExecutionPurchasesRequisitionsMaster, related_name='p_e_p_r_lt_approval',
                                  on_delete=models.CASCADE, blank=True, null=True)
    site_location = models.ForeignKey(PmsSiteProjectSiteManagement, related_name='p_e_p_r_a_lt_site_location',
                                      on_delete=models.CASCADE, blank=True, null=True)
    project = models.ForeignKey(PmsProjects, related_name='p_e_p_r_a_lt_project_id',
                                   on_delete=models.CASCADE, blank=True, null=True)
    item = models.IntegerField(blank=True, null=True)
    type = models.ForeignKey(PmsExecutionPurchasesRequisitionsTypeMaster, related_name='p_e_p_r_a_lt_type',
                                    on_delete=models.CASCADE, blank=True, null=True)
    uom = models.ForeignKey(TCoreUnit, related_name='p_e_p_r_a_lt_unit_id',
                            on_delete=models.CASCADE, blank=True, null=True)
    # initial_estimate=models.CharField(max_length=100, blank=True,null=True)
    # as_per_drawing=models.CharField(max_length=100, blank=True,null=True)
    arm_approval = models.IntegerField(choices=approval_type, null=True, blank=True)
    approval_permission_user_level =  models.ForeignKey(PmsApprovalPermissonMatser, related_name='p_e_p_r_a_lt_permission_id',
                                   on_delete=models.CASCADE, blank=True, null=True)

    approved_quantity = models.CharField(max_length=100, blank=True, null=True)
    available_quantity = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)

    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_p_r_a_lt_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_p_r_a_lt_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_p_r_a_lt_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'pms_execution_purchases_requisitions_approval_log_table'


#:::::::::::::::::::::::::::::::::PMS EXECUTION PURCHASES DISPATCH::::::::::::::::::::::::::::::::::::::::::::::::::::#
class PmsExecutionPurchasesDispatch(models.Model):
    requisitions_master = models.ForeignKey(PmsExecutionPurchasesRequisitionsMaster, related_name='p_e_p_disp_requisitions_master',
                                            on_delete=models.CASCADE, blank=True, null=True)
    dispatch_item = models.IntegerField(blank=True,null=True)
    quantity = models.IntegerField(blank=True,null=True)
    uom = models.ForeignKey(TCoreUnit, related_name='p_e_p_disp_unit_id',
                                     on_delete=models.CASCADE, blank=True, null=True)
    vendor =  models.ForeignKey(PmsExternalUsers, related_name='p_e_p_disp_vendors',
                                on_delete=models.CASCADE, blank=True, null=True)
    po_no = models.CharField(max_length=200, blank=True, null=True)
    date_of_dispatch = models.DateTimeField(blank=True, null=True)
    dispatch_cost = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_p_disp_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_p_disp_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_p_disp_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'pms_execution_purchases_dispatch'

class PmsExecutionPurchasesDispatchDocument(models.Model):
    dispatch = models.ForeignKey(PmsExecutionPurchasesDispatch, related_name='p_e_p_disp_d_comparitive_statement',
                                on_delete=models.CASCADE, blank=True, null=True)
    document_name = models.CharField(max_length=100, blank=True, null=True)
    document = models.FileField(upload_to=get_directory_path,
                                default=None,
                                blank=True, null=True,
                                validators=[validate_file_extension])
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_p_disp_d_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_p_disp_d_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_p_disp_d_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_excution_purchases_dispatch_document'

#:::::::::::::::::::::::::::::PMS EXECUTION PURCHASES DELIVERY::::::::::::::::::::::::::::::::::::::::::::::::::::#
class PmsExecutionPurchasesDelivery(models.Model):
    requisitions_master = models.ForeignKey(PmsExecutionPurchasesRequisitionsMaster, related_name='p_e_p_delivery_requisitions_master',
                                            on_delete=models.CASCADE, blank=True, null=True)
    received_item = models.IntegerField(blank=True,null=True)
    received_quantity = models.IntegerField(blank=True,null=True)
    uom = models.ForeignKey(TCoreUnit, related_name='p_e_p_delivery_unit_id',
                                     on_delete=models.CASCADE, blank=True, null=True)
    vendor =  models.ForeignKey(PmsExternalUsers, related_name='p_e_p_delivery_vendors',
                                on_delete=models.CASCADE, blank=True, null=True)
    po_no = models.CharField(max_length=200, blank=True, null=True)
    date_of_delivery = models.DateTimeField(blank=True, null=True)
    grn_no = models.CharField(max_length=20,blank=True,null=True)
    e_way_bill_no = models.CharField(max_length=20,blank=True,null=True)
    return_and_issue = models.CharField(max_length=200,blank=True,null=True)
    return_cost = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    compensation = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    date_of_receipt = models.DateTimeField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_p_delivery_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_p_delivery_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_p_delivery_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'pms_execution_purchases_delivery'

class PmsExecutionPurchasesDeliveryDocument(models.Model):
    delivery = models.ForeignKey(PmsExecutionPurchasesDelivery, related_name='p_e_p_delivery_d_comparitive_statement',
                                on_delete=models.CASCADE, blank=True, null=True)
    document_name = models.CharField(max_length=100, blank=True, null=True)
    document = models.FileField(upload_to=get_directory_path,
                                default=None,
                                blank=True, null=True,
                                validators=[validate_file_extension])
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_p_delivery_d_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_p_delivery_d_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_p_delivery_d_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_excution_purchases_delivery_document'

#:::::::::::::::::::::::::::::::::PMS EXECUTION PURCHASES PAYMENT::::::::::::::::::::::::::::::::::::::::::::::::::::#
class PmsExecutionPurchasesTotalAmountPayable(models.Model):
    requisitions_master = models.ForeignKey(PmsExecutionPurchasesRequisitionsMaster,
                                            related_name='p_e_p_t_a_p_requisitions_master',
                                            on_delete=models.CASCADE, blank=True, null=True)
    vendor = models.ForeignKey(PmsExternalUsers, related_name='p_e_p_t_a_p_vendors',
                               on_delete=models.CASCADE, blank=True, null=True)
    item = models.IntegerField(blank=True, null=True)
    quantity = models.IntegerField(blank=True, null=True)
    uom = models.ForeignKey(TCoreUnit, related_name='p_e_p_t_a_p_unit_id',
                            on_delete=models.CASCADE, blank=True, null=True)
    price = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    payment_terms = models.ForeignKey(PmsExecutionPurchasesQuotationsPaymentTermsMaster,
                                      related_name='p_e_p_t_a_p_payment_terms',
                                      on_delete=models.CASCADE, blank=True, null=True)
    po_no = models.CharField(max_length=30,null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_p_t_a_p_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_p_t_a_p_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_p_t_a_p_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_excution_purchases_total_amount_payable'
class PmsExecutionPurchasesTotalTransportCostPayable(models.Model):
    requisitions_master = models.ForeignKey(PmsExecutionPurchasesRequisitionsMaster,
                                            related_name='p_e_p_t_t_c_p_requisitions_master',
                                            on_delete=models.CASCADE, blank=True, null=True)
    total_transport_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_p_t_t_c_p_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_p_t_t_c_p_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_p_t_t_c_p_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_excution_purchases_total_transport_cost_payable'
class PmsExecutionPurchasesPaymentPlan(models.Model):
    requisitions_master = models.ForeignKey(PmsExecutionPurchasesRequisitionsMaster,
                                            related_name='p_e_p_payment_plan_requisitions_master',
                                            on_delete=models.CASCADE, blank=True, null=True)
    due_amount = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    due_date = models.DateTimeField(blank=True, null=True)
    vendor = models.ForeignKey(PmsExternalUsers, related_name='p_e_p_payment_plan_vendor',
                               on_delete=models.CASCADE, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_p_payment_plan_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_p_payment_plan_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_p_payment_plan_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_excution_purchases_payment_plan'
class PmsExecutionPurchasesPaymentsMade(models.Model):
    requisitions_master = models.ForeignKey(PmsExecutionPurchasesRequisitionsMaster,
                                            related_name='p_e_p_p_m_requisitions_master',
                                            on_delete=models.CASCADE, blank=True, null=True)
    payment_amount=models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    payment_date=models.DateTimeField(blank=True, null=True)
    invoice_number=models.CharField(max_length=30,null=True, blank=True)
    transaction_id=models.CharField(max_length=30,null=True, blank=True)
    vendor=models.ForeignKey(PmsExternalUsers, related_name='p_e_p_p_m_vendor',
                               on_delete=models.CASCADE, blank=True, null=True)
    po_no = models.CharField(max_length=30, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_p_p_m_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_p_p_m_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_p_p_m_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_excution_purchases_payments_made'
class PmsExecutionPurchasesPaymentsMadeDocument(models.Model):
    purchases_made= models.ForeignKey(PmsExecutionPurchasesPaymentsMade,
                                            related_name='p_e_p_p_m_d_purchases_made',
                                            on_delete=models.CASCADE, blank=True, null=True)
    document_name = models.CharField(max_length=100, blank=True, null=True)
    document = models.FileField(upload_to=get_directory_path,
                                default=None,
                                blank=True, null=True,
                                validators=[validate_file_extension])
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_p_p_m_d_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_p_p_m_d_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_p_p_m_d_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_excution_purchases_payments_made_document'

#::::::::::::::::::::::::::::Pms Execution Stock:::::::::::::::::::::::::::#
class PmsExecutionStockIssueMaster(models.Model):

    status_choice=(
        (1,'Starting'),
        (2,'Pending'),
        (3,'Completed'),
    )
    issue_approval_type = (
        (0, 'Reject'),
        (1, 'Approve'),
        
        )
    issue_stage_status=models.IntegerField(choices=status_choice, null=True, blank=True,default=1)
    project_id = models.ForeignKey(PmsProjects, related_name='p_e_s_i_m_project_id',
                                   on_delete=models.CASCADE, blank=True, null=True)
    site_location = models.ForeignKey(PmsSiteProjectSiteManagement, related_name='p_e_s_i_m_site_location',
                                      on_delete=models.CASCADE, blank=True, null=True)
    issue_date = models.DateTimeField(blank=True, null=True)
    issue_slip_no=models.CharField(max_length=100, blank=True,null=True)
    name_of_contractor=models.ForeignKey(PmsExternalUsers, related_name='p_e_s_i_m_name_of_contractor',
                                   on_delete=models.CASCADE, blank=True, null=True)
    type = models.ForeignKey(PmsExecutionPurchasesRequisitionsTypeMaster, related_name='p_e_s_i_m_type',
                                    on_delete=models.CASCADE, blank=True, null=True)
    no_of_items=models.IntegerField(null=True, blank=True)
    requested_by = models.ForeignKey(User, related_name='p_e_s_i_m_requested_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    authorized_by = models.ForeignKey(User, related_name='p_e_s_i_m_authorized_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    recieved_by = models.ForeignKey(User, related_name='p_e_s_i_m_recieved_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    store_keeper = models.ForeignKey(User, related_name='p_e_s_i_m_store_keeper',
                                   on_delete=models.CASCADE, blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    issue_approval = models.IntegerField(choices=issue_approval_type, null=True, blank=True,default=0)
    approval_permission_user_level =  models.ForeignKey(PmsApprovalPermissonMatser, 
                related_name='p_e_s_i_m_permission_id',on_delete=models.CASCADE, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_s_i_m_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_s_i_m_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_s_i_m_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_execution_stock_issue_master'

class PmsExecutionStockIssueMasterLogTable(models.Model):
    status_choice=(
        (1,'Starting'),
        (2,'Pending'),
        (3,'Completed'),
    )
    issue_approval_type = (
        (0, 'Reject'),
        (1, 'Approve'),
        
        )
    issue_master = models.ForeignKey(PmsExecutionStockIssueMaster, related_name='p_e_s_i_m_lt_issue_master',
                                  on_delete=models.CASCADE, blank=True, null=True)
    issue_stage_status=models.IntegerField(choices=status_choice, null=True, blank=True,default=1)
    project_id = models.ForeignKey(PmsProjects, related_name='p_e_s_i_m_lt_project_id',
                                   on_delete=models.CASCADE, blank=True, null=True)
    site_location = models.ForeignKey(PmsSiteProjectSiteManagement, related_name='p_e_s_i_m_lt_site_location',
                                      on_delete=models.CASCADE, blank=True, null=True)
    issue_date = models.DateTimeField(blank=True, null=True)
    issue_slip_no=models.CharField(max_length=100, blank=True,null=True)
    name_of_contractor=models.ForeignKey(PmsExternalUsers, related_name='p_e_s_i_m_lt_name_of_contractor',
                                   on_delete=models.CASCADE, blank=True, null=True)
    type = models.ForeignKey(PmsExecutionPurchasesRequisitionsTypeMaster, related_name='p_e_s_i_m_lt_type',
                                    on_delete=models.CASCADE, blank=True, null=True)
    no_of_items=models.IntegerField(null=True, blank=True)
    requested_by = models.ForeignKey(User, related_name='p_e_s_i_m_lt_requested_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    authorized_by = models.ForeignKey(User, related_name='p_e_s_i_m_lt_authorized_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    recieved_by = models.ForeignKey(User, related_name='p_e_s_i_m_lt_recieved_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    store_keeper = models.ForeignKey(User, related_name='p_e_s_i_m_lt_store_keeper',
                                   on_delete=models.CASCADE, blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    issue_approval = models.IntegerField(choices=issue_approval_type, null=True, blank=True,default=0)
    approval_permission_user_level =  models.ForeignKey(PmsApprovalPermissonMatser, 
                related_name='p_e_s_i_m_lt_permission_id',on_delete=models.CASCADE, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_s_i_m_lt_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_s_i_m_lt_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_s_i_m_lt_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'pms_execution_stock_issue_master_log_table'

class PmsExecutionIssueMode(models.Model):
    name=models.CharField(max_length=100, blank=True,null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_i_m_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_i_m_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_i_m_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_execution_issue_mode'

class PmsExecutionStockIssue(models.Model):

    issue_master=models.ForeignKey(PmsExecutionStockIssueMaster, related_name='p_e_s_i_issue_master',
                                   on_delete=models.CASCADE, blank=True, null=True)
    # material_code= models.ForeignKey(Materials, related_name='p_e_s_i_material_code',
    #                                on_delete=models.CASCADE, blank=True, null=True)
    type_item_id =models.IntegerField(blank=True,null=True)
    description=models.CharField(max_length=250, blank=True,null=True)
    wbs_number=models.CharField(max_length=100, blank=True,null=True)
    unit=models.ForeignKey(TCoreUnit, related_name='p_e_s_i_unit_id',
                                     on_delete=models.CASCADE, blank=True, null=True)

    quantity=models.CharField(max_length=250, blank=True,null=True)
    mode= models.ForeignKey(PmsExecutionIssueMode, related_name='p_e_s_i_mode',
                                 on_delete=models.CASCADE, blank=True, null=True)
    remarks=models.CharField(max_length=250, blank=True,null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_s_i_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_s_i_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_s_i_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_execution_stock_issue'


class PmsExecutionStock(models.Model):
    which_requisition_tab = models.CharField(max_length=100, blank=True, null=True)
    project = models.ForeignKey(PmsProjects, related_name='p_e_s_project_id',
                                   on_delete=models.CASCADE, blank=True, null=True)
    site_location = models.ForeignKey(PmsSiteProjectSiteManagement, related_name='p_e_s_site_location',
                                      on_delete=models.CASCADE, blank=True, null=True)
    opening_stock=models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True)
    recieved_stock=models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    issued_stock=models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    closing_stock=models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock_date=models.DateTimeField(auto_now_add=True)
    uom=models.ForeignKey(TCoreUnit, related_name='p_e_s_uom',
                                     on_delete=models.CASCADE, blank=True, null=True)

    purpose=models.CharField(max_length=100, blank=True,null=True)
    type = models.ForeignKey(PmsExecutionPurchasesRequisitionsTypeMaster, related_name='p_e_s_type',
                                    on_delete=models.CASCADE, blank=True, null=True)
    requisition=models.ForeignKey(PmsExecutionPurchasesRequisitionsMaster, related_name='p_e_s_approval',
                                  on_delete=models.CASCADE, blank=True, null=True)
    item=models.IntegerField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_s_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_s_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_s_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_execution_stock'

class PmsExecutionUpdatedStock(models.Model):
    project = models.ForeignKey(PmsProjects, related_name='p_e_s_u_project_id',
                                   on_delete=models.CASCADE, blank=True, null=True)
    site_location = models.ForeignKey(PmsSiteProjectSiteManagement, related_name='p_e_s_u_site_location',
                                      on_delete=models.CASCADE, blank=True, null=True)
    opening_stock=models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    recieved_stock=models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    issued_stock=models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    closing_stock=models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock_date=models.DateTimeField(auto_now_add=True)
    uom=models.ForeignKey(TCoreUnit, related_name='p_e_s_u_uom',
                                     on_delete=models.CASCADE, blank=True, null=True)

    purpose=models.CharField(max_length=100, blank=True,null=True)
    type = models.ForeignKey(PmsExecutionPurchasesRequisitionsTypeMaster, related_name='p_e_s_u_type',
                                    on_delete=models.CASCADE, blank=True, null=True)
    requisition=models.ForeignKey(PmsExecutionPurchasesRequisitionsMaster, related_name='p_e_s_u_approval',
                                  on_delete=models.CASCADE, blank=True, null=True)
    item=models.IntegerField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_e_s_u_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_e_s_u_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_e_s_u_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'pms_execution_updated_stock'


