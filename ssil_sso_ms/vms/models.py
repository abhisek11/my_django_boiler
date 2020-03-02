from django.db import models
from django.contrib.auth.models import User
from dynamic_media import get_directory_path
from validators import validate_file_extension



# Create your models here.

class VmsFloorDetailsMaster(models.Model):
    floor_name = models.CharField(max_length=20, blank=True, null=True)
    description = models.CharField(max_length=100, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='vms_f_d_created_by',
                                   on_delete=models.CASCADE,blank=True,null=True)
    owned_by = models.ForeignKey(User, related_name='vms_f_d_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='vms_f_d_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'vms_floor_details_master'


class VmsCardDetailsMaster(models.Model):
    status_type = (
        (1, 'at reception'),
        (2, 'current in use'),
        (3, 'obsolete'),
    )
    card_no = models.CharField(max_length=20, blank=True, null=True, unique=True)
    card_friendly_no = models.CharField(max_length=10, blank=True, null=True)
    card_current_status = models.IntegerField(choices=status_type, default=1)
    status = models.BooleanField(default=True)
    report_arise = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='vms_c_d_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='vms_c_d_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='vms_c_d_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'vms_card_details_master'

class VmsCardAndFloorMapping(models.Model):
    card=models.ForeignKey(VmsCardDetailsMaster, related_name='vms_c_a_f_m_card',
                                   on_delete=models.CASCADE,blank=True,null=True)
    floor=models.ForeignKey(VmsFloorDetailsMaster, related_name='vms_c_a_f_m_floor',
                                   on_delete=models.CASCADE,blank=True,null=True)
    status = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='vms_c_a_f_m_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='vms_c_a_f_m_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='vms_c_a_f_m_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'vms_card_and_floor_mapping'


class VmsVisitorDetails(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)
    phone_no = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=50, blank=True, null= True)
    address = models.TextField(blank=True, null=True)
    picture = models.ImageField(upload_to=get_directory_path,
                                         default=None,
                                         blank=True, null=True,
                                         )
    organization = models.CharField(max_length=100, blank=True, null=True)
    status = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='vms_v_d_created_by',
                                   on_delete=models.CASCADE,blank=True,null=True)
    owned_by = models.ForeignKey(User, related_name='vms_v_d_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='vms_v_d_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self): 
        return str(self.id)

    class Meta:
        db_table = 'vms_visitor_details'

class VmsVisitorTypeMaster(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)
    parent_id=models.IntegerField(default=0)
    status = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, related_name='vms_v_t_m_created_by', on_delete=models.CASCADE,blank=True,null=True)
    owned_by = models.ForeignKey(User, related_name='vms_v_t_m_owned_by', on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='vms_v_t_m_updated_by', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'vms_visitor_type_master'


class VmsVisit(models.Model):
    visitor_type = models.ForeignKey(VmsVisitorTypeMaster, related_name='vms_visit_visitor_type',
                             on_delete=models.CASCADE,blank=True,null=True)
    visitor = models.ForeignKey(VmsVisitorDetails, related_name='vms_visit_visitor_id',
                                on_delete=models.CASCADE,blank=True,null=True)
    card = models.ForeignKey(VmsCardDetailsMaster, related_name='vms_visit_card_id',
                             on_delete=models.CASCADE,blank=True,null=True)
    purpose = models.CharField(max_length=100, blank=True, null=True)
    login_time = models.DateTimeField(blank=True, null=True)
    logout_time = models.DateTimeField(blank=True, null=True)
    drop_off_time = models.DateTimeField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='vms_visit_created_by',
                                   on_delete=models.CASCADE,blank=True,null=True)
    updated_by = models.ForeignKey(User, related_name='vms_visit_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='vms_visit_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'vms_visit'

class VmsVisitorPunching(models.Model):
    visit = models.ForeignKey(VmsVisit, related_name='vms_v_p_visit_id', on_delete=models.CASCADE,blank=True,null=True)
    gate = models.CharField(max_length=30, blank=True, null=True)
    time = models.DateTimeField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'vms_visitor_punching'

class VmsEmployeeVisitor(models.Model):
    visit = models.ForeignKey(VmsVisit, related_name='vms_e_v_visit_id', on_delete=models.CASCADE,blank=True,null=True)
    visit_to = models.ForeignKey(User,related_name='vms_e_v_visit_to_id',
                             on_delete=models.CASCADE,blank=True,null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='vms_e_v_created_by', on_delete=models.CASCADE,blank=True,null=True)
    owned_by = models.ForeignKey(User, related_name='vms_e_v_owned_by', on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'vms_employee_visitor'

class VmsFloorVisitor(models.Model):
    visit = models.ForeignKey(VmsVisit, related_name='vms_f_v_id', on_delete=models.CASCADE,blank=True,null=True)
    floor = models.ForeignKey(VmsFloorDetailsMaster, related_name='vms_f_v_floor', on_delete=models.CASCADE,blank=True,null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='vms_f_v_created_by', on_delete=models.CASCADE,blank=True,null=True)
    owned_by = models.ForeignKey(User, related_name='vms_f_v_owned_by', on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'vms_floor_visitor'


