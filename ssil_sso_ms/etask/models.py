from django.db import models
from django.contrib.auth.models import User
from dynamic_media import get_directory_path
from validators import validate_file_extension
# import uuid
# Create your models here.

class EtaskTask(models.Model):
    # priority_choice=((1,'Low'),
    #                 (2,'Medium'),
    #                 (3,'High')
    #                 )
    priority_choice=((1,'Standard Tasks'),
                    (2,'Priority Tasks')                 
                    )
    task_type_choice=((1,'One Time'),
                       (2,'Profile Job'),
                       (3,'Sub Task')
    )
    task_status_choice=((1,'Ongoing'),
                        (2,'Completed'),
                        (3,'Sub Assign'),
                        (4,'Closed')
    )
    recurrance_frequency_choice=(
                                (1,'Daily'),
                                (2,'Weekely'),
                                (3,'Fortnightly'),
                                (4,'Monthly'),
                                (5,'Quarterly'),
                                (6,'Half-Yearly'),
                                (7,'Annualy')
                                )
    task_choice = ((1,'For Me'),
                    (2,'On behalf of'),
                    (3,'Assign to')
                )
                
    # type=models.ForeignKey(EtaskType,related_name='et_type', on_delete=models.CASCADE, blank=True, null=True )
    task_code_id = models.CharField(max_length=50, unique=True,blank=True,null=True)
    # task_code_id = models.CharField(max_length=50, unique=True,blank=True,null=True)
    parent_id=models.IntegerField(default=0,blank=True, null=True)
    owner = models.ForeignKey(User, related_name='et_owner', on_delete=models.CASCADE, 
                                blank=True, null=True)
    assign_to = models.ForeignKey(User, related_name='et_assign_to', on_delete=models.CASCADE, 
                                    blank=True, null=True)
    assign_by = models.ForeignKey(User, related_name='et_assign_by', on_delete=models.CASCADE, 
                                    blank=True, null=True)
    task_subject = models.CharField(max_length=200, blank=True, null=True)
    task_description = models.TextField(blank=True, null=True)
    task_categories = models.IntegerField(choices=task_choice, null=True, blank=True)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    requested_end_date = models.DateTimeField(blank=True, null=True)
    requested_comment = models.TextField(blank=True, null=True)
    requested_by = models.ForeignKey(User, related_name='et_requested_by', on_delete=models.CASCADE, 
                                    blank=True, null=True)
    is_closure = models.BooleanField(default=False)
    is_reject = models.BooleanField(default=False)
    is_transferred = models.BooleanField(default=False)
    transferred_from= models.ForeignKey(User, related_name='et_transferred_from', on_delete=models.CASCADE, 
                                    blank=True, null=True)
    date_of_transfer = models.DateTimeField(blank=True, null=True)
    completed_date = models.DateTimeField(blank=True, null=True)
    completed_by=models.ForeignKey(User, related_name='et_completed_by', on_delete=models.CASCADE, 
                                    blank=True, null=True)
    closed_date = models.DateTimeField(blank=True, null=True)
    extended_date = models.DateTimeField(blank=True, null=True)
    extend_with_delay=models.BooleanField(default=False)
    task_priority = models.IntegerField(choices=priority_choice, null=True, blank=True)
    task_type = models.IntegerField(choices=task_type_choice, null=True, blank=True)
    task_status = models.IntegerField(choices=task_status_choice, null=True, blank=True,default=1)
    recurrance_frequency = models.IntegerField(choices=recurrance_frequency_choice, null=True, blank=True)
    sub_assign_to_user = models.ForeignKey(User, related_name='et_sub_assign_to_user', on_delete=models.CASCADE, 
                                            blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='et_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='et_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='et_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # objects = TaskManager()

    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'etask_task'

    
    # @staticmethod
    # def get_active():
    #     self.task_code_id = "TSK" + str(self.id)
    #     return Article.objects.filter(isPublished = 1)

    # def get_task_code_id(self, *args, **kwargs):
    #     if self.id:
    #         print("self.id",self.id)
    #         # This is a new ticket as no ID yet exists.
    #         self.task_code_id = "TSK" + str(self.id)

    #     super(EtaskTask, self).save(*args, **kwargs)
 
class EtaskUserCC(models.Model):
    task=models.ForeignKey(EtaskTask,related_name='et_u_cc_task', on_delete=models.CASCADE, 
                            blank=True, null=True )
    user=models.ForeignKey(User, related_name='et_u_cc_user', on_delete=models.CASCADE, 
                    blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='et_u_cc_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='et_u_cc_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='et_u_cc_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'etask_user_cc'

# class EtaskAssignTo(models.Model):
#     task_choice=((1,'For Me'),
#                  (2,'On behalf of'),
#                  (3,'Assign to')
#     )
#     task=models.ForeignKey(EtaskTask,related_name='et_a_t_task', on_delete=models.CASCADE, 
#                             blank=True, null=True )
#     task_categories=models.IntegerField(choices=task_choice, null=True, blank=True)
#     for_me_user=models.ForeignKey(User, related_name='et_a_t_for_me_user', on_delete=models.CASCADE, 
#                     blank=True, null=True)
#     assign_to_user=models.ForeignKey(User, related_name='et_a_t_assign_to_user', on_delete=models.CASCADE, 
#                 blank=True, null=True)
#     on_behalf_of=models.ForeignKey(User, related_name='et_a_t_on_behalf_of', on_delete=models.CASCADE, 
#                 blank=True, null=True)
#     sub_assign_to_user=models.ForeignKey(User, related_name='et_a_t_sub_assign_to_user', on_delete=models.CASCADE, 
#                 blank=True, null=True)
#     is_deleted = models.BooleanField(default=False)
#     created_by = models.ForeignKey(User, related_name='et_a_t_created_by',
#                                    on_delete=models.CASCADE, blank=True, null=True)
#     updated_by = models.ForeignKey(User, related_name='et_a_t_updated_by',
#                                      on_delete=models.CASCADE, blank=True, null=True)
#     owned_by = models.ForeignKey(User, related_name='et_a_t_owned_by',
#                                  on_delete=models.CASCADE, blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return str(self.id)
#     class Meta:
#         db_table = 'etask_assign_to'
    
class ETaskReportingDates(models.Model):
    type_choice=((1,'Tasks'),
                 (2,'Follow Up')
                )
    status_choice=((1,'Reported'),
                   (2,'Not Reported'),
                   (3,'Reported And Completed')
                  )
    task_type = models.IntegerField(choices=type_choice, null=True, blank=True)
    task = models.IntegerField(blank=True, null=True)
    reporting_date = models.DateTimeField(blank=True, null=True)
    actual_reporting_date = models.DateTimeField(blank=True, null=True)
    reporting_status = models.IntegerField(choices=status_choice, null=True, blank=True,default=2)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='et_r_d_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='et_r_d_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='et_r_d_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'etask_reporting_dates'

class ETaskReportingActionLog(models.Model):
    status_choice=((1,'Reported'),
                   (2,'Not Reported'),
                   (3,'Reported And Completed'), # it is used for a task has been completed on reported date.
                   (4,'Task Completed') # It is used for a task has been completed before or after reported date.
                  )
    task= models.ForeignKey(EtaskTask, related_name='et_r_a_l_task',
                                   on_delete=models.CASCADE, blank=True, null=True)
    reporting_date= models.ForeignKey(ETaskReportingDates, related_name='et_r_a_l_reporting_date',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_date= models.DateTimeField(auto_now=True)
    status = models.IntegerField(choices=status_choice, null=True, blank=True)

    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='et_r_a_l_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='et_r_a_l_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='et_r_a_l_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'etask_reporting_action_log'

class EtaskFollowUP(models.Model):

    followup_status_choice=(('pending','Pending'),
                        ('completed','Completed'))

    follow_up_task = models.CharField(max_length=200, blank=True, null=True)
    task= models.ForeignKey(EtaskTask, related_name='et_follow_up_task', #This Field Add For FSD Version.3#
                on_delete=models.CASCADE, blank=True, null=True)
    assign_to = models.ForeignKey(User, related_name='et_follow_up_assign_to', 
                on_delete=models.CASCADE, blank=True, null=True)
    assign_for = models.ForeignKey(User, related_name='et_follow_up_assign_for', 
                on_delete=models.CASCADE, blank=True, null=True)
    follow_up_date = models.DateTimeField(blank=True, null=True)
    # end_date = models.DateTimeField(blank=True, null=True)  #These Fields Remove For FSD Version.3#
    # follow_up_time = models.TimeField(blank=True, null=True)
    followup_status = models.CharField(max_length=10,choices=followup_status_choice, null=True, blank=True, default='pending')
    completed_date = models.DateTimeField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='et_follow_up_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='et_follow_up_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='et_follow_up_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'etask_follow_up'

#::::::::::::: Etask Comments ::::::::::::#
class ETaskComments(models.Model):
    task=models.ForeignKey(EtaskTask,related_name='et_c_task', on_delete=models.CASCADE, 
                            blank=True, null=True )
    comments = models.TextField(blank=True, null=True)
    advance_comment = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='et_c_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='et_c_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='et_c_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'etask_comments'
class ETaskCommentsViewers(models.Model):
    etcomments = models.ForeignKey(ETaskComments,related_name='et_c_v_etcomments', on_delete=models.CASCADE, 
                            blank=True, null=True )
    task = models.ForeignKey(EtaskTask,related_name='et_c_v_task', on_delete=models.CASCADE, 
                            blank=True, null=True)
    user = models.ForeignKey(User, related_name='et_c_v_user',
                                   on_delete=models.CASCADE, blank=True, null=True)
    is_view = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='et_c_v_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='et_c_v_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='et_c_v_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'etask_comments_viewers'
class EtaskIncludeAdvanceCommentsCostDetails(models.Model):
    etcomments=models.ForeignKey(ETaskComments,related_name='et_a_c_c_d_etcomments', on_delete=models.CASCADE, 
                            blank=True, null=True )
    cost_details = models.CharField(max_length=200, blank=True, null=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='et_a_c_c_d_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='et_a_c_c_d_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='et_a_c_c_d_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'etask_include_advance_comments_cost_details'

class EtaskIncludeAdvanceCommentsOtherDetails(models.Model):
    etcomments=models.ForeignKey(ETaskComments,related_name='et_a_c_o_d_etcomments', on_delete=models.CASCADE, 
                            blank=True, null=True )
    other_details = models.CharField(max_length=200, blank=True, null=True)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='et_a_c_o_d_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='et_a_c_o_d_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='et_a_c_o_d_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'etask_include_advance_comments_otehr_details'

class EtaskIncludeAdvanceCommentsDocuments(models.Model):
    etcomments=models.ForeignKey(ETaskComments,related_name='et_a_c_d_etcomments', on_delete=models.CASCADE, 
                            blank=True, null=True )
    document_name = models.CharField(max_length=50,blank=True,null=True)
    document = models.FileField(upload_to=get_directory_path,
                                         default=None,
                                         blank=True, null=True,
                                         validators=[validate_file_extension]
                                         )
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='et_a_c_d_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='et_a_c_d_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='et_a_c_d_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'etask_include_advance_comments_documents'

#::::::::::::: Followup Comments ::::::::::::#
class FollowupComments(models.Model):
    followup=models.ForeignKey(EtaskFollowUP,related_name='fl_c_followup', on_delete=models.CASCADE, 
                            blank=True, null=True )
    comments = models.TextField(blank=True, null=True)
    advance_comment = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='fl_c_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='fl_c_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='fl_c_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'followup_comments'

class FollowupIncludeAdvanceCommentsCostDetails(models.Model):
    flcomments=models.ForeignKey(FollowupComments,related_name='fl_a_c_c_d_flcomments', on_delete=models.CASCADE, 
                            blank=True, null=True )
    cost_details = models.CharField(max_length=200, blank=True, null=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='fl_a_c_c_d_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='fl_a_c_c_d_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='fl_a_c_c_d_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'followup_include_advance_comments_cost_details'

class FollowupIncludeAdvanceCommentsOtherDetails(models.Model):
    flcomments=models.ForeignKey(FollowupComments,related_name='fl_a_c_o_d_flcomments', on_delete=models.CASCADE, 
                            blank=True, null=True )
    other_details = models.CharField(max_length=200, blank=True, null=True)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='fl_a_c_o_d_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='fl_a_c_o_d_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='fl_a_c_o_d_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'followup_include_advance_comments_otehr_details'

class FollowupIncludeAdvanceCommentsDocuments(models.Model):
    flcomments=models.ForeignKey(FollowupComments,related_name='fl_a_c_d_flcomments', on_delete=models.CASCADE, 
                            blank=True, null=True )
    document_name = models.CharField(max_length=50,blank=True,null=True)
    document = models.FileField(upload_to=get_directory_path,
                                         default=None,
                                         blank=True, null=True,
                                         validators=[validate_file_extension]
                                         )
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='fl_a_c_d_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='fl_a_c_d_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='fl_a_c_d_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'followup_include_advance_comments_documents'




#################APPOINTMENT#################################################################

class EtaskAppointment(models.Model):
    status_coice = (
        ('ongoing','Ongoing'),
        ('cancelled','Cancelled'),
        ('completed','Completed'),
    )

    appointment_subject = models.CharField(max_length=200,blank=True, null=True)
    location = models.CharField(max_length=200,blank=True,null=True)
    start_date= models.DateTimeField(blank=True,null=True)
    end_date= models.DateTimeField(blank=True,null=True)
    start_time = models.TimeField(blank=True,null=True)
    end_time = models.TimeField(blank=True,null=True)
    Appointment_status = models.CharField(max_length=20,choices=status_coice, null=True, blank=True, default='ongoing')
    is_deleted = models.BooleanField(default=False)
    appointment_overdue = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='appointment_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='appointment_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='appointment_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'etask_appointment'

class EtaskInviteEmployee(models.Model):
    appointment = models.ForeignKey(EtaskAppointment, related_name='invite_appointment', 
                on_delete=models.CASCADE, blank=True, null=True)
    user = models.ForeignKey(User, related_name='invite_user', 
                on_delete=models.CASCADE, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='invite_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='invite_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='invite_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'etask_invite_employee'

class EtaskInviteExternalPeople(models.Model):
    appointment = models.ForeignKey(EtaskAppointment, related_name='invite_ep_appointment', 
                on_delete=models.CASCADE, blank=True, null=True)
    external_people = models.CharField(max_length=200,blank=True,null=True)
    external_email = models.CharField(max_length=200,blank=True,null=True)

    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='invite_ep_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='invite_ep_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='invite_ep_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'etask_invite_external_people'


#:::::::::::::::::: APPOINTMENT COMMENTS :::::::::::::::::::::::::::#

class AppointmentComments(models.Model):
    appointment=models.ForeignKey(EtaskAppointment,related_name='ap_c_appointment', on_delete=models.CASCADE, 
                            blank=True, null=True )
    comments = models.TextField(blank=True, null=True)
    advance_comment = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='ap_c_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='ap_c_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='ap_c_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'appointment_comments'

class AppointmentIncludeAdvanceCommentsCostDetails(models.Model):
    apcomments=models.ForeignKey(AppointmentComments,related_name='ap_a_c_c_d_apcomments', on_delete=models.CASCADE, 
                            blank=True, null=True )
    cost_details = models.CharField(max_length=200, blank=True, null=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='ap_a_c_c_d_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='ap_a_c_c_d_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='ap_a_c_c_d_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'appointment_comments_include_advance_comments_cost_details'

class AppointmentIncludeAdvanceCommentsOtherDetails(models.Model):
    apcomments=models.ForeignKey(AppointmentComments,related_name='ap_a_c_o_d_apcomments', on_delete=models.CASCADE, 
                            blank=True, null=True )
    other_details = models.CharField(max_length=200, blank=True, null=True)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='ap_a_c_o_d_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='ap_a_c_o_d_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='ap_a_c_o_d_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'appointment_comments_include_advance_comments_otehr_details'

class AppointmentIncludeAdvanceCommentsDocuments(models.Model):
    apcomments=models.ForeignKey(AppointmentComments,related_name='ap_a_c_d_apcomments', on_delete=models.CASCADE, 
                            blank=True, null=True )
    document_name = models.CharField(max_length=50,blank=True,null=True)
    document = models.FileField(upload_to=get_directory_path,
                                         default=None,
                                         blank=True, null=True,
                                         validators=[validate_file_extension]
                                         )
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='ap_a_c_d_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='ap_a_c_d_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='ap_a_c_d_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'appointment_comments_include_advance_comments_documents'

class EtaskMonthlyReportingDate(models.Model):
    employee = models.ForeignKey(User,
                                related_name='et_m_r_d_employee',
                                on_delete=models.CASCADE,
                                blank=True,
                                null=True
                                )
    field_label = models.CharField(max_length=100, blank=True, null=True)
    field_value = models.IntegerField(blank=True,null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='et_m_r_d_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='et_m_r_d_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='et_m_r_d_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'etask_monthly_reporting_date'

'''
    Reason - Added for Task Edit 
    Date -  26.02.2020 
    Author - Rupam Hazra
'''
class EtaskTaskEditLog(models.Model):
    priority_choice=((1,'Standard Tasks'),
                    (2,'Priority Tasks')             
                    )
    task_type_choice=((1,'One Time'),
                       (2,'Profile Job'),
                       (3,'Sub Task')
    )
    task_status_choice=((1,'Ongoing'),
                        (2,'Completed'),
                        (3,'Sub Assign'),
                        (4,'Closed')
    )
    recurrance_frequency_choice=(
                                (1,'Daily'),
                                (2,'Weekely'),
                                (3,'Fortnightly'),
                                (4,'Monthly'),
                                (5,'Quarterly'),
                                (6,'Half-Yearly'),
                                (7,'Annualy')
                                )
    task_choice = ((1,'For Me'),
                    (2,'On behalf of'),
                    (3,'Assign to')
                )
                
    task = models.ForeignKey(EtaskTask, related_name='task_edit', on_delete=models.CASCADE, 
                                blank=True, null=True)
    parent_id=models.IntegerField(default=0,blank=True, null=True)
    owner = models.ForeignKey(User, related_name='ete_owner', on_delete=models.CASCADE, 
                                blank=True, null=True)
    assign_to = models.ForeignKey(User, related_name='ete_prev_assign_to', on_delete=models.CASCADE, 
                                    blank=True, null=True)
    assign_by = models.ForeignKey(User, related_name='ete_prev_assign_by', on_delete=models.CASCADE, 
                                    blank=True, null=True)
    task_subject = models.CharField(max_length=200, blank=True, null=True)
    task_description = models.TextField(blank=True, null=True)
    task_categories = models.IntegerField(choices=task_choice, null=True, blank=True)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    requested_end_date = models.DateTimeField(blank=True, null=True)
    requested_comment = models.TextField(blank=True, null=True)
    requested_by = models.ForeignKey(User, related_name='ete_requested_by', on_delete=models.CASCADE, 
                                    blank=True, null=True)
    is_closure = models.BooleanField(default=False)
    is_reject = models.BooleanField(default=False)
    is_transferred = models.BooleanField(default=False)
    transferred_from= models.ForeignKey(User, related_name='ete_transferred_from', on_delete=models.CASCADE, 
                                    blank=True, null=True)
    date_of_transfer = models.DateTimeField(blank=True, null=True)
    completed_date = models.DateTimeField(blank=True, null=True)
    completed_by=models.ForeignKey(User, related_name='ete_completed_by', on_delete=models.CASCADE, 
                                    blank=True, null=True)
    closed_date = models.DateTimeField(blank=True, null=True)
    extended_date = models.DateTimeField(blank=True, null=True)
    extend_with_delay=models.BooleanField(default=False)
    task_priority = models.IntegerField(choices=priority_choice, null=True, blank=True)
    task_type = models.IntegerField(choices=task_type_choice, null=True, blank=True)
    task_status = models.IntegerField(choices=task_status_choice, null=True, blank=True,default=1)
    recurrance_frequency = models.IntegerField(choices=recurrance_frequency_choice, null=True, blank=True)
    sub_assign_to_user = models.ForeignKey(User, related_name='ete_sub_assign_to_user', on_delete=models.CASCADE, 
                                            blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='ete_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='ete_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    task_edited_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'etask_task_edit_log'

class EtaskTaskTransferLog(models.Model):
    task = models.ForeignKey(EtaskTask, related_name='ett_task_transfer', on_delete=models.CASCADE, 
                                blank=True, null=True)
    transferred_from = models.ForeignKey(User, related_name='ett_transferred_from', on_delete=models.CASCADE, 
                                    blank=True, null=True)
    transferred_to = models.ForeignKey(User, related_name='ett_transferred_to', on_delete=models.CASCADE, 
                                    blank=True, null=True)
    transfer_date = models.DateTimeField(blank=True, null=True)

    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='ett_created_by',
                                    on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='ett_owned_by',
                                    on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'etask_task_transfer_log'

class EtaskTaskSubAssignLog(models.Model):
    task = models.ForeignKey(EtaskTask, related_name='etsa_task_sub_assign', on_delete=models.CASCADE, 
                                blank=True, null=True)
    assign_from = models.ForeignKey(User, related_name='etsa_assign_from', on_delete=models.CASCADE, 
                                    blank=True, null=True)
    sub_assign = models.ForeignKey(User, related_name='etsa_sub_assign', on_delete=models.CASCADE, 
                                    blank=True, null=True)

    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='etsa_created_by',
                                    on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='etsa_owned_by',
                                    on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'etask_task_sub_assign_log'