from django.db import models
from django.contrib.auth.models import User
from dynamic_media import get_directory_path
from django_mysql.models import EnumField
from validators import validate_file_extension
from core.models import TCoreUnit
import datetime
import time
from pms.models.module_tender import *

#::::::::::::::::  PROJECTS :::::::::::::::::::::::::::#
def unique_rand_project():
    while True:
        code = "P" + str(int(time.time()))
        if not PmsProjects.objects.filter(project_g_id=code).exists():
            return code
class PmsProjects(models.Model):
    type_of_state = ((1, 'pre_execution'),
                     (2, 'execution'),
                     (3, 'post_execution'),
                     (4, 'completed'),
                     (5, 'cancelled')
                     )

    name= models.CharField(max_length=200,blank=True,null=True)
    project_g_id = models.CharField(max_length=50, unique=True,
                                    default=unique_rand_project)
    state = models.IntegerField(choices=type_of_state, default=1)
    tender=models.ForeignKey(PmsTenders,
                               related_name='p_tender_id',
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True
                               )
    site_location = models.ForeignKey(PmsSiteProjectSiteManagement,
                               related_name='p_s_management_id',
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True
                               )
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    status = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_projects'

#:::::::::::::::: PROJECTS USER MAPPING :::::::::::#
class PmsProjectUserMapping(models.Model):
    project = models.ForeignKey(PmsProjects, related_name='project_user',
                                on_delete=models.CASCADE, blank=True, null=True)
    user = models.ForeignKey(User, related_name='project_user_mapping_user',
                             on_delete=models.CASCADE, blank=True, null=True)
    start_date = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    expire_date = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    status = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='p_u_m_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='p_u_m_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='p_u_m_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_project_user_mapping'



#:::::::::::::::: PROJECTS MACHINARY MAPPING :::::::::::#
class PmsProjectsMachinaryMapping(models.Model):
    project = models.ForeignKey(PmsProjects,related_name='m_p_id',
                                on_delete=models.CASCADE,blank=True,null=True)
    machinary = models.ForeignKey(PmsMachineries,
                               related_name='m_machinary_id',
                               on_delete=models.CASCADE,blank=True,null=True
                               )
    machinary_s_d_req = models.DateTimeField(blank=True, null=True)
    machinary_e_d_req = models.DateTimeField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='m_m_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='m_m_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='m_m_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_projects_machinary_mapping'