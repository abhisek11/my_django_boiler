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

#:::  ATTENDENCE ::::#
class PmsAttendance(models.Model):
    Type_of_attandance= (
        (1, 'individual'),
        (2, ' labours under individual')
    )
    Type_of_approved = (
        (1, 'pending'),
        (2, 'approved'),
        (3, 'reject'),
        (4, 'regular'),
    )
    type = models.IntegerField(choices=Type_of_attandance, null=True, blank=True)
    employee=models.ForeignKey(User, related_name='attandance_employee_id',
                                   on_delete=models.CASCADE,blank=True,null=True)
    user_project = models.ForeignKey(PmsProjects, related_name='user_project',
                                   on_delete=models.CASCADE, blank=True, null=True)
    date= models.DateTimeField(auto_now_add=False,blank=True, null=True)
    login_time=models.DateTimeField(blank=True, null=True)
    login_latitude = models.CharField(max_length=200, blank=True, null=True)
    login_longitude= models.CharField(max_length=200, blank=True, null=True)
    login_address=models.TextField(blank=True, null=True)
    logout_time=models.DateTimeField(blank=True, null=True)
    logout_latitude = models.CharField(max_length=200, blank=True, null=True)
    logout_longitude = models.CharField(max_length=200, blank=True, null=True)
    logout_address = models.TextField(blank=True, null=True)
    approved_status = models.IntegerField(choices=Type_of_approved,
                                         default=4)
    justification=models.TextField(blank=True, null=True)
    # deviation_time = models.IntegerField(default=0)
    is_deleted= models.BooleanField(default=False)
    created_by =models.ForeignKey(User, related_name='attandance_created_by',
                                   on_delete=models.CASCADE,blank=True,null=True)
    owned_by = models.ForeignKey(User, related_name='attandance_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='attandance_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_attandance'
class PmsAttandanceLog(models.Model):
  Type_of_approved = (
        (1, 'pending'),
        (2, 'approved'),
        (3, 'reject'),
        (4, 'regular'),
    )
  attandance=models.ForeignKey(PmsAttendance,related_name='a_l_attandance_id',
                                 on_delete=models.CASCADE,blank=True,null=True)
  time=models.DateTimeField(blank=True, null=True)
  latitude = models.CharField(max_length=200, blank=True, null=True)
  longitude = models.CharField(max_length=200, blank=True, null=True)
  address = models.TextField(blank=True, null=True)
  approved_status = models.IntegerField(choices=Type_of_approved, default=4)
  justification = models.TextField(blank=True, null=True)
  remarks=models.TextField(blank=True, null=True)
  is_checkout = models.BooleanField(default=False)
  is_deleted = models.BooleanField(default=False)
  created_by = models.ForeignKey(User, related_name='a_l_created_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
  owned_by = models.ForeignKey(User, related_name='a_l_owned_by',
                               on_delete=models.CASCADE, blank=True, null=True)
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
      return str(self.id)

  class Meta:
      db_table = 'pms_attandance_log'
class PmsAttandanceDeviation(models.Model):
    Type_of_approved = (
        (1, 'pending'),
        (2, 'approved'),
        (3, 'reject'),
        (4, 'regular'),
    )
    Type_of_deviation = (('OD', 'official duty'),
                     ('HD', 'half day'),
                     ('FD', 'full day'))
    attandance = models.ForeignKey(PmsAttendance, related_name='a_d_attandance_id',
                                   on_delete=models.CASCADE, blank=True, null=True)
    from_time = models.DateTimeField(blank=True, null=True)
    to_time = models.DateTimeField(blank=True, null=True)
    deviation_time = models.CharField(max_length=10,blank=True, null=True)
    deviation_type = models.CharField(max_length=2,
                                  choices=Type_of_deviation,
                                  default="OD")
    justification = models.TextField(blank=True, null=True)
    approved_status = models.IntegerField(choices=Type_of_approved, default=4)
    remarks = models.TextField(blank=True, null=True)
    justified_by = models.ForeignKey(User, related_name='a_d_justified_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    justified_at = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey(User, related_name='a_d_approved_by',
                                     on_delete=models.CASCADE, blank=True, null=True)
    approved_at = models.DateTimeField(auto_now_add=True)
    owned_by = models.ForeignKey(User, related_name='a_d_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_attandance_deviation'
class PmsEmployeeLeaves(models.Model):
    Type_of_approved = (
        (1, 'pending'),
        (2, 'approved'),
        (3, 'reject'),
        (4, 'regular'),
    )

    Type_of_leave = (('EL', 'earned leave'),
                      ('CL', 'casual leave'),
                     ('AB', 'Absent'))
    employee = models.ForeignKey(User, related_name='leaves_employee_id',
                                 on_delete=models.CASCADE, blank=True, null=True)
    leave_type = models.CharField(max_length=2,
                  choices=Type_of_leave,
                  default="AB")

    start_date= models.DateTimeField(blank=True, null=True)
    end_date= models.DateTimeField(blank=True, null=True)
    reason = models.TextField(blank=True, null=True)
    approved_status = models.IntegerField(choices=Type_of_approved,
                                          default=1)

    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='leave_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='leave_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='leave_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_employee_leaves'

#:::::::::::::::::::::::::::::::::::PMS EMPLOYEE CONVEYANCE:::::::::::::::::::::::::::::::#
class PmsEmployeeConveyance(models.Model):
    Type_of_approved = (
        (1, 'pending'),
        (2, 'approved'),
        (3, 'reject'),
    )
    project = models.ForeignKey(PmsProjects, related_name='employee_conveyance_project',
                                     on_delete=models.CASCADE, blank=True, null=True)
    employee = models.ForeignKey(User, related_name='employee_conveyance_id',
                                 on_delete=models.CASCADE, blank=True, null=True)
    eligibility_per_day = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)
    from_place = models.TextField(blank=True, null=True)
    to_place = models.TextField(blank=True, null=True)
    vechicle_type = models.CharField(max_length=100,blank=True, null=True)
    purpose = models.TextField(blank=True, null=True)
    job_alloted_by = models.ForeignKey(User, related_name='employee_conveyance_job_alloted_by',
                                       on_delete=models.CASCADE, blank=True, null=True)
    ammount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    approved_status = models.IntegerField(choices=Type_of_approved, default=1)

    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='employee_conveyance_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='employee_conveyance_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='employee_conveyance_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_employee_conveyance'


#:::::::::::::::::::::::::::::::::::PMS EMPLOYEE FOODING:::::::::::::::::::::::::::::::#
class PmsEmployeeFooding(models.Model):
    Type_of_approved = (
        (1, 'pending'),
        (2, 'approved'),
        (3, 'reject'),
    )
    attandance = models.ForeignKey(PmsAttendance, related_name='employee_fooding_attandance_id',
                                   on_delete=models.CASCADE, blank=True, null=True)
    ammount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    approved_status = models.IntegerField(choices=Type_of_approved, default=1)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='employee_fooding_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='employee_fooding_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='employee_fooding_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_employee_fooding'