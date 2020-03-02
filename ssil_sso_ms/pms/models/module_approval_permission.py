from django.db import models
from django.contrib.auth.models import User
from dynamic_media import get_directory_path
from validators import validate_file_extension
import datetime
import time
from core.models import TCoreOther

#::::: PMS SECTION MASTER:::::::::::::::#

#::::: PMS SECTION PERMISSION LEVEL MASTER:::::::::::::::#
class PmsApprovalPermissonLavelMatser(models.Model):
    section = models.OneToOneField(TCoreOther, related_name='p_a_p_l_m_section_name',
                                   on_delete=models.CASCADE, blank=True, null=True)
    permission_level = models.IntegerField(blank=True,null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_a_p_l_m_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_a_p_l_m_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_a_p_l_m_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_approval_permission_lavel_master'

#::::: PMS APPROVAL PERMISSION MASTER:::::::::::::::#
class PmsApprovalPermissonMatser(models.Model):
    section = models.ForeignKey(TCoreOther, related_name='p_a_p_m_section',on_delete=models.CASCADE, blank=True, null=True)
    permission_level = models.CharField(max_length=20, blank=True, null=True)
    approval_user = models.ForeignKey(User, related_name='p_a_p_m_user',on_delete=models.CASCADE, blank=True, null=True) 
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_a_p_m_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_a_p_m_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_a_p_m_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_approval_permission_master'

