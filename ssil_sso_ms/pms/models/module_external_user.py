from django.db import models
from django.contrib.auth.models import User
from dynamic_media import get_directory_path
from django_mysql.models import EnumField
from validators import validate_file_extension
from core.models import *
import datetime
import time

# ::: PMS External Users Type ::::::::::::::::::#
#[vendor,contractor,operator,crusher]#
class PmsExternalUsersType(models.Model):
    type_name = models.CharField(max_length=200, blank=True, null=True)
    type_desc = models.TextField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='external_users_type_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='external_users_type_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='external_users_type_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_external_users_type'

# ::: PMS External Users ::::::::::::::::::#
class PmsExternalUsers(models.Model):
    user_type = models.ForeignKey(PmsExternalUsersType, related_name='external_users_type',
                                  on_delete=models.CASCADE, blank=True, null=True)
    code = models.CharField(max_length=100, blank=True, null=True, unique=True)
    organisation_name = models.CharField(max_length=200, blank=True, null=True)
    contact_no = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(max_length=200,blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    trade_licence_doc = models.FileField(upload_to=get_directory_path,
                                default=None,
                                blank=True, null=True,
                                validators=[validate_file_extension]
                                )
    gst_no = models.CharField(max_length=100, blank=True, null=True)
    gst_doc = models.FileField(upload_to=get_directory_path,
                                         default=None,
                                         blank=True, null=True,
                                         validators=[validate_file_extension]
                                         )
    pan_no = models.CharField(max_length=10, blank=True, null=True)
    pan_doc = models.FileField(upload_to=get_directory_path,
                                         default=None,
                                         blank=True, null=True,
                                         validators=[validate_file_extension]
                                         )
    bank_name =  models.CharField(max_length=100, blank=True, null=True)
    bank_ac_no = models.CharField(max_length=50, blank=True, null=True)
    ifsc_code = models.CharField(max_length=11, blank=True, null=True)
    cancelled_cheque_doc = models.FileField(upload_to=get_directory_path,
                               default=None,
                               blank=True, null=True,
                               validators=[validate_file_extension]
                               )
    adhar_no = models.CharField(max_length=16, blank=True, null=True)
    adhar_doc = models.FileField(upload_to=get_directory_path,
                                            default=None,
                                            blank=True, null=True,
                                            validators=[validate_file_extension]
                                            )
    contact_person_name = models.CharField(max_length=200, blank=True, null=True)
    salary = models.CharField(max_length=80,blank=True, null=True)
    region = models.CharField(max_length=10,blank=True, null=True)
    state =  models.ForeignKey(TCoreState, related_name='external_users_state',
                                   on_delete=models.CASCADE, blank=True, null=True)
    vendor_classified_text = models.CharField(max_length=100,blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='external_users_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='external_users_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='external_users_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'pms_external_users'

class PmsExternalUsersDocument(models.Model):
    external_user_type = models.ForeignKey(PmsExternalUsersType,
                                           related_name='e_u_d_user_type_id',
                                           on_delete=models.CASCADE, blank=True, null=True)
    external_user = models.ForeignKey(PmsExternalUsers, related_name='external_users_document',
                                      on_delete=models.CASCADE, blank=True, null=True)
    document_name = models.CharField(max_length=200, blank=True, null=True)
    document = models.FileField(upload_to=get_directory_path,
                                default=None,
                                blank=True, null=True,
                                validators=[validate_file_extension]
                                )
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='external_users_document_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='external_users_document_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='external_users_document_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'pms_external_users_document'
