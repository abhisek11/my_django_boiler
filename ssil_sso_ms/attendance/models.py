from django.db import models
from django.contrib.auth.models import User
from dynamic_media import get_directory_path
from django_mysql.models import EnumField
from validators import validate_file_extension
from core.models import TCoreUnit
import datetime
import time
from pms.models.module_tender import *
from pms.models.module_project import *
# Create your models here.

class DeviceMaster(models.Model):
    device_no = models.IntegerField(null=True, blank=True, unique=True)
    device_name = models.CharField(max_length=30,blank=True, null=True)
    is_exit = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='device_master_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='device_master_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='device_master_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'device_master'

class AttendenceMonthMaster(models.Model):
    year_start_date = models.DateTimeField(blank=True, null=True)
    year_end_date = models.DateTimeField(blank=True, null=True)
    month = models.IntegerField(null=True, blank=True)
    month_start = models.DateTimeField(blank=True, null=True)
    month_end = models.DateTimeField(blank=True, null=True)
    grace_available = models.IntegerField(null=True, blank=True)
    lock_date = models.DateTimeField(blank=True, null=True)
    pending_action_mail = models.DateTimeField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='att_month_master_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='att_month_master_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='att_month_master_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'attendence_month_master'

class AttendenceSaturdayOffMaster(models.Model):
    employee=models.ForeignKey(User,related_name='att_sat_off_master_employee_id',
                                   on_delete=models.CASCADE,blank=True,null=True)
    first = models.BooleanField(default=False)
    second = models.BooleanField(default=False)
    third = models.BooleanField(default=False)
    fourth = models.BooleanField(default=False)
    all_s_day = models.BooleanField(default=False)

    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='att_sat_off_master_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='att_sat_off_master_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='att_sat_off_master_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'attendence_saturday_off_master'
class AttendenceSaturdayOffLogMaster(models.Model):
    employee=models.ForeignKey(User,related_name='att_sat_off_log_master_employee_id',
                                   on_delete=models.CASCADE,blank=True,null=True)
    first = models.BooleanField(default=False)
    second = models.BooleanField(default=False)
    third = models.BooleanField(default=False)
    fourth = models.BooleanField(default=False)
    all_s_day = models.BooleanField(default=False)

    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='att_sat_off_log_master_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='att_sat_off_log_master_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='att_sat_off_log_master_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'attendence_saturday_off_log_master'
class AttendanceSpecialdayMaster(models.Model):
    type_choice=((1,'Full Day'),
                (2,'Late Entry'),
                (3,'Early Exit'),
                (4,'Early and Late')
                )
    day_start_time = models.DateTimeField(blank=True, null=True)
    day_end_time = models.DateTimeField(blank=True, null=True)
    full_day= models.DateTimeField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    day_type=models.IntegerField(choices=type_choice, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='att_sp_day_master_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='att_sp_day_master_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='att_sp_day_master_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'attendence_special_day_master'


class VehicleTypeMaster(models.Model):
    name = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True, null=True)    
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='v_t_m_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='v_t_m_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='v_t_m_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'vehicle_type_master'

class JoiningApprovedLeave(models.Model):
    employee = models.ForeignKey(User, related_name='employee_joining_approved_leave',
                                   on_delete=models.CASCADE, blank=True, null=True)
    year = models.IntegerField(null=True, blank=True)
    cl = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)
    el = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)
    sl = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)
    ab = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)
    month = models.IntegerField(null=True, blank=True)
    first_grace = models.IntegerField(null=True, blank=True)

    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='joining_app_leave_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='joining_app_leave_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='joining_app_leave_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'joining_approved_leave'

class Attendance(models.Model):
    employee=models.ForeignKey(User,related_name='user_att_employee_id',
                                   on_delete=models.CASCADE,blank=True,null=True)
    date= models.DateTimeField(auto_now_add=False,blank=True, null=True)
    login_time = models.DateTimeField(blank=True, null=True)
    login_latitude = models.CharField(max_length=200, blank=True, null=True)
    login_longitude= models.CharField(max_length=200, blank=True, null=True)
    login_address=models.TextField(blank=True, null=True)
    logout_time = models.DateTimeField(blank=True, null=True)
    logout_latitude = models.CharField(max_length=200, blank=True, null=True)
    logout_longitude = models.CharField(max_length=200, blank=True, null=True)
    logout_address = models.TextField(blank=True, null=True)
    is_present = models.BooleanField(default=False)
    day_remarks = models.CharField(max_length=100, blank=True, null=True)
    is_fullday = models.BooleanField(default=False)
    is_deleted= models.BooleanField(default=False)
    created_by =models.ForeignKey(User, related_name='user_att_created_by',
                                   on_delete=models.CASCADE,blank=True,null=True)
    owned_by = models.ForeignKey(User, related_name='user_att_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='user_att_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'attendance'

class AttendanceLog(models.Model):
    attendance = models.ForeignKey(Attendance,related_name='user_att_l_attendance_id',
                                    on_delete=models.CASCADE,blank=True,null=True)
    employee=models.ForeignKey(User,related_name='user_att_l_employee_id',
                                   on_delete=models.CASCADE,blank=True,null=True)
    time = models.DateTimeField(blank=True, null=True)
    device_no = models.ForeignKey(DeviceMaster,related_name='user_att_l_device_no',
                                    on_delete=models.CASCADE,blank=True,null=True)

    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='user_att_l_created_by',
                                    on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='user_att_l_owned_by',
                                on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'attendance_log'

class AttendanceApprovalRequest(models.Model):
    Type_of_approved = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('reject', 'Reject'),
        ('relese', 'Relese'),
        ('regular', 'Regular'),
    )
    conveyance_choice=((0, 'pending'),
                       (1, 'Reject'),
                       (2, 'Approved'),
                       (3, 'Modified')
    )
    Type_of_request = (('HD', 'half day'),
                     ('FD', 'full day'),
                     ('GR', 'grace_period'),
                     ('MP', 'mispunch'),
                     ('WO', 'week off'),
                     ('OD', 'Off duty'),
                     ('FOD', 'full day official duty'),
                     ('POD', 'partly official duty'),
                     ('LC', 'late conveyance'))

    Type_of_leave = (
        ('EL', 'Earned Leave'),
        ('CL', 'Casual Leave'),
        ('SL', 'Sick Leave'),
        ('AB', 'Absent')
    )

    attendance = models.ForeignKey(Attendance, related_name='a_a_r_attendance_id',
                                   on_delete=models.CASCADE, blank=True, null=True)
    duration_start = models.DateTimeField(blank=True, null=True)
    duration_end = models.DateTimeField(blank=True, null=True)
    duration = models.IntegerField(null=True, blank=True)
    request_type = models.CharField(max_length=3,choices=Type_of_request,
                                  blank=True,null=True)
    attendance_date = models.DateField(blank=True, null=True)
    is_requested = models.BooleanField(default=False)
    request_date = models.DateTimeField(blank=True, null=True)
    justification = models.TextField(blank=True, null=True)
    approved_status = models.CharField(max_length=10,choices=Type_of_approved, default='regular')
    remarks = models.TextField(blank=True, null=True)
    justified_by = models.ForeignKey(User, related_name='a_a_r_justified_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    justified_at = models.DateTimeField(blank=True, null=True)
    approved_by = models.ForeignKey(User, related_name='a_a_r_approved_by',
                                     on_delete=models.CASCADE, blank=True, null=True)
    approved_at = models.DateTimeField(blank=True, null=True)
    leave_type = models.CharField(max_length=2,
                                  choices=Type_of_leave,
                                  blank=True,null=True)
    is_conveyance = models.BooleanField(default=False)
    is_late_conveyance = models.BooleanField(default=False)
    conveyance_approval = models.IntegerField(choices=conveyance_choice,null=True,blank=True)
    conveyance_approved_by = models.ForeignKey(User, related_name='c_a_a_r_approved_by',
                                     on_delete=models.CASCADE, blank=True, null=True)
    vehicle_type = models.ForeignKey(VehicleTypeMaster, related_name='a_a_r_vehicle_type',
                                   on_delete=models.CASCADE, blank=True, null=True)
    conveyance_purpose=models.TextField(blank=True, null=True)
    conveyance_alloted_by=models.ForeignKey(User, related_name='a_a_r_conveyance_alloted_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    from_place = models.TextField(blank=True, null=True)
    to_place = models.TextField(blank=True, null=True)
    conveyance_expense = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    approved_expenses = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    conveyance_remarks = models.TextField(blank=True, null=True)
    leave_type_changed = models.CharField(max_length=2,
                                  choices=Type_of_leave,
                                  blank=True,null=True)
    leave_type_changed_period = models.CharField(max_length=3,
                                  choices=Type_of_request,
                                  blank=True,null=True)
    checkin_benchmark = models.BooleanField(default=False)
    lock_status = models.BooleanField(default=False)
    punch_id = models.CharField(max_length = 50, blank=True, null=True)

    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='a_a_r_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='a_a_r_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='a_a_r_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'attendence_approval_request'

class AttandanceApprovalDocuments(models.Model):
    request = models.ForeignKey(AttendanceApprovalRequest, related_name='att_app_doc_req_id',
                               on_delete=models.CASCADE, blank=True, null=True)
    document_name = models.CharField(max_length=50,blank=True,null=True)
    document = models.FileField(upload_to=get_directory_path,
                                         default=None,
                                         blank=True, null=True,
                                         validators=[validate_file_extension]
                                         )
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='att_app_doc_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='att_app_doc_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='att_app_doc_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'attandance_approval_documents'

class EmployeeAdvanceLeaves(models.Model):
    Type_of_approved = (
        ('pending', 'Pending'),
        ('approved','Approved'),
        ('reject', 'Reject'),
        ('relese', 'Relese')
    )

    Type_of_leave = (
        ('CL', 'casual leave'),
        ('EL', 'earned leave'),
        ('AB', 'Absent')
    )
    employee = models.ForeignKey(User, related_name='emp_adv_leaves_employee_id',
                                 on_delete=models.CASCADE, blank=True, null=True)
    leave_type = models.CharField(max_length=2,
                  choices=Type_of_leave,
                  default="AB")

    start_date= models.DateTimeField(blank=True, null=True)
    end_date= models.DateTimeField(blank=True, null=True)
    reason = models.TextField(blank=True, null=True)
    approved_status = models.CharField(max_length=10,choices=Type_of_approved, default='pending')
    remarks = models.TextField(blank=True, null=True)

    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='emp_adv_leaves_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='emp_adv_leaves_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='emp_adv_leaves_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'employee_advance_leaves'

class AttandancePerDayDocuments(models.Model):    
    name= models.CharField(max_length=200, blank=True, null=True)
    document =models.FileField(upload_to=get_directory_path,
                               default=None,
                               blank=True, null=True,
                               validators=[validate_file_extension]
                               ) 
    upload_date = models.DateTimeField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='a_p_d_d_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='a_p_d_d_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='a_p_d_d_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'attandance_per_day_documents'



class AttendenceAction(models.Model):
    ACTION_ADMIN = 0
    ACTION_HR = 1
    ACTION_EMPLOYEE = 2
    ACTION_TYPES = (
        (ACTION_ADMIN, "Hr Admin"),
        (ACTION_HR, "Hr User"),
        (ACTION_EMPLOYEE, "Hr Employee"),
    )

    @staticmethod
    def toAction(key):
        """
        Parses an integer value to a string representing an action.
        :param key: The action number
        :return: The string representation of the name for action
        """
        for item in Action.ACTION_TYPES:
            if item[0] == key:
                return item[1]
        return "None"
    user = models.ForeignKey(User, on_delete = models.CASCADE )
    # role = models.IntegerField(default=0, choices=ACTION_TYPES)
    time_of_action = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=200, blank=True, null=True)
    fields = models.CharField(max_length=200, blank=True, null=True)
    before_content = models.CharField(max_length=2000, blank=True, null=True)
    after_content = models.CharField(max_length=2000, blank=True, null=True)
    section = models.CharField(max_length=500, blank=True, null=True)

    """
    Might have to add this field to specify:
    - where action was committed
    - exclude actions that are done at a attendence for which a specific
      admin is not in control of ?
    """
    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'attendence_action'