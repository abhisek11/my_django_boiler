from django.db import models
from django.contrib.auth.models import User
from dynamic_media import get_directory_path
from django_mysql.models import EnumField
from validators import validate_file_extension
from core.models import TCoreUnit
import datetime
import time

#:::::::::: LOG TABLE ::::::::#
class PmsLog(models.Model):
    module_id = models.BigIntegerField()
    module_table_name = models.TextField(blank=True, null=True)
    action_type = EnumField(choices=['add', 'edit', 'delete'])
    current_module_data = models.TextField(blank=True, null=True)
    updated_module_data = models.TextField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE,blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'pms_log'