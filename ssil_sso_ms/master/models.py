from django.db import models
from django.contrib.auth.models import User
from core.models import * 
import collections

class TMasterModuleOther(models.Model):
    mmo_other = models.ForeignKey(TCoreOther, on_delete=models.CASCADE,related_name='mmo_other')
    mmo_module = models.ForeignKey(TCoreModule, on_delete=models.CASCADE,related_name='mmo_module')
    #mmo_name = models.CharField(max_length=100, blank=True,null=True)
    #parent_id = models.IntegerField(default=0)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='t_m_updated_by', blank=True, null=True)
    class Meta:
        db_table = 't_master_module_other'

    def __str__(self):
        return str(self.id)

class TMasterModuleRole(models.Model):
    """docstring for ClassName"""
    mmro_module = models.ForeignKey(TCoreModule, on_delete=models.CASCADE,related_name='mmr_o_module')
    mmro_role = models.ForeignKey(TCoreRole, on_delete=models.CASCADE,related_name='mmr_o_role',blank=True,null=True,)
    mmro_is_deleted = models.BooleanField(default=False)
    mmro_created_by = models.ForeignKey(User, related_name='mmr_o_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    mmro_updated_by = models.ForeignKey(User, related_name='mmr_o_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    mmro_created_at = models.DateTimeField(auto_now_add=True)
    mmro_updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 't_master_module_role'
    def __str__(self):
        return str(self.id)

class TMasterModuleRoleUser(models.Model):
    """docstring for ClassName"""

    TYPE_CHOICE = (
        (1,'Super User'),
        (2,'Module Admin'),
        (3,'Module User'),
        (4,'Dealer'),
        (5,'CWS'),
        (6,'Demo User')
        )

    mmr_module = models.ForeignKey(TCoreModule, on_delete=models.CASCADE,related_name='mmr_module')
    mmr_role = models.ForeignKey(TCoreRole, on_delete=models.CASCADE,related_name='mmr_role',blank=True,null=True,)
    mmr_type = models.IntegerField(default = 1, choices = TYPE_CHOICE, blank=True,null=True,)
    mmr_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mmr_user',blank=True,null=True)
    mmr_is_deleted = models.BooleanField(default=False)
    mmr_created_by = models.ForeignKey(User, related_name='mmr_r_created_by',on_delete=models.CASCADE,blank=True, null=True)
    mmr_updated_by = models.ForeignKey(User, related_name='mmr_r_updated_by',on_delete=models.CASCADE, blank=True, null=True)
    mmr_created_at = models.DateTimeField(auto_now_add=True)
    mmr_updated_at = models.DateTimeField(auto_now=True)
    mmr_designation = models.ForeignKey(TCoreDesignation, on_delete=models.CASCADE, related_name='mmr_designation',blank=True,null=True)
    class Meta:
        db_table = 't_master_module_role_user'
    def __str__(self):
        return str(self.id)

class TMasterOtherRole(models.Model):
    """
        Used for assigning object permisson to role
    """
    mor_role = models.ForeignKey(TCoreRole, on_delete=models.CASCADE,related_name='mor_r_role',blank=True, null=True)
    mor_other = models.ForeignKey(TCoreOther, on_delete=models.CASCADE,related_name='mor_r_other')
    mor_permissions = models.ForeignKey(TCorePermissions, on_delete=models.CASCADE,
                                        related_name='mor_permissions', blank=True, null=True)
    mor_module = models.ForeignKey(TCoreModule, on_delete=models.CASCADE,related_name='mor_module')
    mor_is_deleted = models.BooleanField(default=False)
    mor_created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mor_r_created_by', blank=True,
                                       null=True)
    mor_created_at = models.DateTimeField(auto_now_add=True)
    mor_updated_at = models.DateTimeField(auto_now=True)
    mor_updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mor_r_updated_by', blank=True,
                                       null=True)
    mor_deleted_at = models.DateTimeField(auto_now=True)
    mor_deleted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mor_r_deleted_by', blank=True,null=True)
    class Meta:
        db_table = 't_master_other_role'
    def __str__(self):
        return str(self.id)

class TMasterOtherUser(models.Model):
    """
        Used for assigning object permisson to user
    """
    mou_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mou_r_user', blank=True, null=True)
    mou_other = models.ForeignKey(TCoreOther, on_delete=models.CASCADE,related_name='mou_r_other')
    mou_permissions = models.ForeignKey(TCorePermissions, on_delete=models.CASCADE,
                                        related_name='mmr_permissions', blank=True, null=True)
    mou_module = models.ForeignKey(TCoreModule, on_delete=models.CASCADE,related_name='mou_module')
    mou_is_deleted = models.BooleanField(default=False)
    mou_created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mou_r_created_by', blank=True,
                                       null=True)
    mou_created_at = models.DateTimeField(auto_now_add=True)
    mou_updated_at = models.DateTimeField(auto_now=True)
    mou_updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mou_r_updated_by', blank=True,
                                       null=True)
    mou_deleted_at = models.DateTimeField(auto_now=True)
    mou_deleted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mou_r_deleted_by', blank=True,null=True)
    class Meta:
        db_table = 't_master_other_user'
    def __str__(self):
        return str(self.id)

class TMasterModulePermissonBlock(models.Model):
    """
        Used for assigning object permisson to user
    """
    mmpb_module = models.ForeignKey(TCoreModule, on_delete=models.CASCADE,related_name='mmpb_c_module')
    user_permission = models.BooleanField(default=False)
    teamlead_permission = models.BooleanField(default=False)
    hr_permission = models.BooleanField(default=False)
    mmpb_created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mmpb_r_created_by', blank=True,
                                       null=True)
    mmpb_created_at = models.DateTimeField(auto_now_add=True)
    mmpb_updated_at = models.DateTimeField(auto_now=True)
    mmpb_updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mmpb_r_updated_by', blank=True,
                                       null=True)
    mmpb_deleted_at = models.DateTimeField(auto_now=True)
    mmpb_deleted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mmpb_r_deleted_by', blank=True,null=True)
    class Meta:
        db_table = 't_master_module_permission_block'
    def __str__(self):
        return str(self.id)
