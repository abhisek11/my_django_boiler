from django.db import models
from django.contrib.auth.models import User
from dynamic_media import get_directory_path
from validators import validate_file_extension
import datetime
import time
from core.models import TCoreDepartment

# Create your models here.

'''
    ETICKETDepartmentHead is for reporting head for Eticket.
    Don't mesh up the with table name it is modified as per discussion.
    It is not related to original hod for core user details table.
'''
# class ETICKETDepartmentHead(models.Model):
#     department = models.ForeignKey(TCoreDepartment, related_name='eticket_d_department',
#                                    on_delete=models.CASCADE, blank=True, null=True)
#     department_head = models.ForeignKey(User, related_name='eticket_d_department_head',
#                                         on_delete=models.CASCADE, blank=True, null=True)
#     is_deleted = models.BooleanField(default=False)
#     created_by = models.ForeignKey(User, related_name='eticket_d_created_by',
#                                    on_delete=models.CASCADE, blank=True, null=True)
#     updated_by = models.ForeignKey(User, related_name='eticket_d_updated_by',
#                                    on_delete=models.CASCADE, blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return str(self.id)

#     class Meta:
#         db_table = 'eticket_department_head'

class ETICKETReportingHead(models.Model):
    department = models.ForeignKey(TCoreDepartment, related_name='eticket_r_department',
                                   on_delete=models.CASCADE, blank=True, null=True)
    # sub_department = models.ForeignKey(TCoreDepartment, related_name='eticket_r_sub_department',
    #                                on_delete=models.CASCADE, blank=True, null=True)
    reporting_head = models.ForeignKey(User, related_name='eticket_r_reporting_head',
                                        on_delete=models.CASCADE, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='eticket_r_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='eticket_r_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'eticket_reporting_head'


class ETICKETSubjectOfDepartment(models.Model):
    department = models.ForeignKey(TCoreDepartment, related_name='eticket_department_subject',on_delete=models.CASCADE, 
    blank=True, null=True)
    subject = models.TextField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='eticket_department_created_by', on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, related_name='eticket_department_updated_by', 
    on_delete=models.CASCADE,blank=True, null=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'eticket_subject_of_department'

class ETICKETTicket(models.Model):
    priority_choice = (
        ('High', 'High'),
        ('Low', 'Low'),
        ('Medium', 'Medium'),
    )

    status_choice = (
        ('Open', 'Open'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Closed', 'Closed'),
    )

    ticket_number = models.CharField(max_length=15, blank=True, null=True)
    subject = models.ForeignKey(ETICKETSubjectOfDepartment, related_name='eticket_t_subject',
                                    on_delete=models.CASCADE, blank=True, null=True)
    department = models.ForeignKey(TCoreDepartment, related_name='eticket_t_department',
                                   on_delete=models.CASCADE, blank=True, null=True)
    priority = models.CharField(max_length=10,choices=priority_choice, null=True, blank=True)
    details = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=11,choices=status_choice, null=True, blank=True)
    ticket_closed_date = models.DateTimeField(blank=True, null=True)
    assigned_to = models.ForeignKey(User, related_name='eticket_t_assigned_to',
                                    on_delete=models.CASCADE, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='eticket_t_created_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='eticket_t_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'eticket_ticket'

class ETICKETTicketDoc(models.Model):
    ticket = models.ForeignKey(ETICKETTicket, related_name='eticket_doc_t_id',
                               on_delete=models.CASCADE, blank=True, null=True)
    document = models.FileField(upload_to=get_directory_path, default=None,
                                blank=True, null=True, validators=[validate_file_extension])
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        User, related_name='eticket_doc_created_by', on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, related_name='eticket_doc_updated_by', on_delete=models.CASCADE,
                                   blank=True, null=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'eticket_ticket_document'

class ETICKETTicketComment(models.Model):
    ticket = models.ForeignKey(ETICKETTicket, related_name='eticket_c_id',
                               on_delete=models.CASCADE, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        User, related_name='eticket_c_created_by', on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, related_name='eticket_c_updated_by', on_delete=models.CASCADE,
                                   blank=True, null=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'eticket_ticket_comment'



