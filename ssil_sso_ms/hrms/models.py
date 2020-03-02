from django.db import models
from django.contrib.auth.models import User
from dynamic_media import get_directory_path
from validators import validate_file_extension
from core.models import *
from pms.models import *
# Create your models here.

class HrmsBenefitsProvided(models.Model):
    benefits_name = models.CharField(max_length=200, blank=True, null=True)
    # allowance = models.CharField(max_length=200, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='hr_b_p_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='hr_b_p_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='hr_b_p_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'hrms_benefits_provided'
        
class HrmsUsersBenefits(models.Model):
    user= models.ForeignKey(User,related_name='hr_u_b_user',
                                   on_delete=models.CASCADE, blank=True, null=True)
    benefits= models.ForeignKey(HrmsBenefitsProvided,related_name='hr_u_b_benefits',
                                   on_delete=models.CASCADE, blank=True, null=True)
    allowance = models.CharField(max_length=200, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='hr_u_b_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='hr_u_b_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='hr_u_b_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'hrms_users_benefits'

class HrmsUsersOtherFacilities(models.Model):
    user= models.ForeignKey(User,related_name='hr_u_o_f_user',
                                   on_delete=models.CASCADE, blank=True, null=True)
    other_facilities=models.CharField(max_length=200, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='hr_u_o_f_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='hr_u_o_f_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='hr_u_o_f_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'hrms_users_other_facilities'

class HrmsDocument(models.Model):
    user= models.ForeignKey(User,related_name='hr_d_user',
                                   on_delete=models.CASCADE, blank=True, null=True)
    tab_name= models.CharField(max_length=200, blank=True, null=True)
    field_label=models.CharField(max_length=200, blank=True, null=True)
    document_name= models.CharField(max_length=200, blank=True, null=True)
    document =models.FileField(upload_to=get_directory_path,
                               default=None,
                               blank=True, null=True,
                               validators=[validate_file_extension]
                               )
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='hr_d_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='hr_d_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='hr_d_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'hrms_document'

class HrmsDynamicSectionFieldLabelDetailsWithDoc(models.Model):
    user= models.ForeignKey(User,related_name='hr_d_s_f_l_d_w_d_user',
                                   on_delete=models.CASCADE, blank=True, null=True)
    tab_name= models.CharField(max_length=200, blank=True, null=True)
    field_label=models.CharField(max_length=200, blank=True, null=True)
    field_label_value=models.CharField(max_length = 200, blank=True, null=True)
    document_name= models.CharField(max_length=200, blank=True, null=True)
    document =models.FileField(upload_to=get_directory_path,
                               default=None,
                               blank=True, null=True,
                               validators=[validate_file_extension]
                               )
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='hr_d_s_f_l_d_w_d_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='hr_d_s_f_l_d_w_d_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='hr_d_s_f_l_d_w_d_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'hrms_dynamic_section_field_label_details_with_doc'

class HrmsQualificationMaster(models.Model):
    name=models.CharField(max_length=100, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='hr_q_m_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='hr_q_m_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='hr_q_m_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'hrms_qualification_master'

class HrmsUserQualification(models.Model):
    user=models.ForeignKey(User,related_name='hr_u_q_user',
                                   on_delete=models.CASCADE, blank=True, null=True)
    qualification=models.ForeignKey(HrmsQualificationMaster,related_name='hr_u_q_qualification',
                                   on_delete=models.CASCADE, blank=True, null=True)
    details=models.CharField(max_length=200, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='hr_u_q_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='hr_u_q_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='hr_u_q_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'hrms_user_qualification'

class HrmsUserQualificationDocument(models.Model):
    user_qualification=models.ForeignKey(HrmsUserQualification,related_name='hr_u_q_d_user_qualification',
                                   on_delete=models.CASCADE, blank=True, null=True)
    document=models.FileField(upload_to=get_directory_path,
                               default=None,
                               blank=True, null=True,
                               validators=[validate_file_extension]
                               )
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='hr_u_q_d_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='hr_u_q_d_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='hr_u_q_d_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'hrms_user_qualification_document'


#****************************HRMS RECUREMENTS AND ONBOARDING****************************************#


class HrmsNewRequirement(models.Model):

    tab_choice = (
        (1,'New_Requirement'),
        (2,'Requirement_Approval'),
        (3,'Shedule_Interview'),
        (4,'Interview_Status'),
        (5,'candidature_approval'),
        (6,'Completed')
    )

    vacancy_choice = (
            ('new','New'),
            ('replacement','Replacement')
    )

    requirement_type_choice = (
        ('immediate','Immediate'),
        ('standard','Standard')
    )

    age_group_choice = (
        (1,'18-25'),
        (2,'25-32'),
        (3,'32-40'),
        (4,'above 40+')
    )

    gender_choice = (
        ('male','Male'),
        ('female','Female'),
        ('other','other')
    )

    issuing_department = models.ForeignKey(TCoreDepartment,related_name='hr_n_r_department',
                                   on_delete=models.CASCADE, blank=True, null=True)
    date =  models.DateTimeField(blank=True, null=True)
    closing_date =  models.DateTimeField(blank=True, null=True)
    type_of_vacancy = models.CharField(max_length=15,choices=vacancy_choice, default=None)
    type_of_requirement = models.CharField(max_length=15,choices=requirement_type_choice, default=None)
    reason= models.CharField(max_length=200, blank=True, null=True)
    number_of_position = models.IntegerField(blank=True,null=True)
    proposed_designation = models.ForeignKey(TCoreDesignation,related_name='hr_n_r_designation',
                                   on_delete=models.CASCADE, blank=True, null=True)
    location = models.CharField(max_length=100,blank=True,null=True)
    substantiate_justification = models.CharField(max_length=1000,null=True,blank = True)
    document = models.FileField(upload_to=get_directory_path,
                                default=None,
                                null=True,blank=True,
                                validators=[validate_file_extension])

    desired_qualification = models.CharField(max_length=10,blank=True,null=True)
    desired_experience= models.CharField(max_length=10,blank=True,null=True)
    desired_age_group = models.IntegerField(choices=age_group_choice,null=True,blank=True)
    tab_status = models.IntegerField(choices=tab_choice,null=True,blank=True,default=1)
    gender = models.CharField(max_length=15,choices=gender_choice, default=None)
    reporting_to = models.ForeignKey(User,related_name='hr_n_r_reporting_to',
                                   on_delete=models.CASCADE, blank=True, null=True)

    number_of_subordinates = models.IntegerField(blank=True,null=True)
    ctc = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    required_skills = models.CharField(max_length=200,blank=True,null=True)

    level_approval= models.BooleanField(default=False)
    reciever_approval= models.BooleanField(default=False)
    approval_permission_user_level =  models.ForeignKey(PmsApprovalPermissonMatser, related_name='hr_n_r_permission_id',
                                   on_delete=models.CASCADE, blank=True, null=True)

    reciever_remarks = models.CharField(max_length=100,blank=True,null=True)

    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='hr_n_r_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='hr_n_r_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='hr_n_r_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'hrms_new_requirement'

class HrmsNewRequirementLog(models.Model):

    tab_choice = (
        (1,'New_Requirement'),
        (2,'Requirement_Approval'),
        (3,'Shedule_Interview'),
        (4,'Interview_Status'),
        (5,'candidature_approval'),
        (6,'Completed')
    )

    vacancy_choice = (
            ('new','New'),
            ('replacement','Replacement')
    )

    requirement_type_choice = (
        ('immediate','Immediate'),
        ('standard','Standard')
    )

    age_group_choice = (
        (1,'18-25'),
        (2,'25-32'),
        (3,'32-40'),
        (4,'above 40+')
    )

    gender_choice = (
        ('male','Male'),
        ('female','Female'),
        ('other','other')
    )
    master_hnr = models.ForeignKey(HrmsNewRequirement,related_name='hr_n_r_log_master',
                                   on_delete=models.CASCADE, blank=True, null=True)
    issuing_department = models.ForeignKey(TCoreDepartment,related_name='hr_n_r_log_department',
                                   on_delete=models.CASCADE, blank=True, null=True)
    date =  models.DateTimeField(blank=True, null=True)
    type_of_vacancy = models.CharField(max_length=15,choices=vacancy_choice, default=None)
    type_of_requirement = models.CharField(max_length=15,choices=requirement_type_choice, default=None)
    reason= models.CharField(max_length=200, blank=True, null=True)
    number_of_position = models.IntegerField(blank=True,null=True)
    proposed_designation = models.ForeignKey(TCoreDesignation,related_name='hr_n_r_log_designation',
                                   on_delete=models.CASCADE, blank=True, null=True)
    location = models.CharField(max_length=100,blank=True,null=True)
    substantiate_justification = models.CharField(max_length=1000,null=True,blank = True)
    document = models.FileField(upload_to=get_directory_path,
                                default=None,
                                null=True,blank=True,
                                validators=[validate_file_extension])

    desired_qualification = models.CharField(max_length=10,blank=True,null=True)
    desired_experience= models.CharField(max_length=10,blank=True,null=True)
    desired_age_group = models.IntegerField(choices=age_group_choice,null=True,blank=True)
    tab_status = models.IntegerField(choices=tab_choice,null=True,blank=True,default=1)
    gender = models.CharField(max_length=15,choices=gender_choice, default=None)
    reporting_to = models.ForeignKey(User,related_name='hr_n_r_log_reporting_to',
                                   on_delete=models.CASCADE, blank=True, null=True)

    number_of_subordinates = models.IntegerField(blank=True,null=True)
    ctc = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    required_skills = models.CharField(max_length=200,blank=True,null=True)
    # reciever_approval= models.BooleanField(default=False)
    level_approval= models.BooleanField(default=False)
    approval_permission_user_level =  models.ForeignKey(PmsApprovalPermissonMatser, related_name='hr_n_r_log_permission_id',
                                   on_delete=models.CASCADE, blank=True, null=True)
    # approval_permission_reciver_level =  models.ForeignKey(PmsApprovalPermissonMatser, related_name='hr_n_r_log_permission_rec_id',
    #                             on_delete=models.CASCADE, blank=True, null=True)

    reciever_remarks = models.CharField(max_length=100,blank=True,null=True)
    tag_name = models.CharField(max_length=100,blank=True,null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='hr_n_r_log_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='hr_n_r_log_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='hr_n_r_log_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'hrms_new_requirement_log'


class HrmsInterviewType(models.Model):
    name= models.CharField(max_length=100,blank=True,null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='hr_i_t_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='hr_i_t_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='hr_i_t_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'hrms_interview_type'

class HrmsInterviewLevel(models.Model):
    name= models.CharField(max_length=100,blank=True,null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='hr_i_l_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='hr_i_l_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='hr_i_l_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'hrms_interview_level'

class HrmsScheduleInterview(models.Model):
    action_choice = (
        (1,'approved'),
        (2,'rejected'),
        (3,'OnProcess')
    )
    requirement=models.ForeignKey(HrmsNewRequirement,related_name='hr_s_i_requirement',
                                   on_delete=models.CASCADE, blank=True, null=True)
    candidate_name= models.CharField(max_length=50,blank=True,null=True)
    contact_no= models.CharField(max_length=10,blank=True,null=True,unique=True)
    email= models.EmailField(max_length=70,blank=True,null=True)
    note= models.CharField(max_length=100,blank=True,null=True)
    resume=models.FileField(upload_to=get_directory_path,
                                default=None,
                                null=True,blank=True,
                                validators=[validate_file_extension])
    notice_period = models.CharField(max_length=100,blank=True,null=True)
    expected_ctc = models.IntegerField(blank=True,null=True)
    current_ctc = models.IntegerField(blank=True,null=True)
    action_approval = models.IntegerField(choices=action_choice,null=True,blank=True,default=3)
    level_approval= models.BooleanField(default=False)
    approval_permission_user_level =  models.ForeignKey(PmsApprovalPermissonMatser, related_name='hr_s_i_log_permission_id',
                                   on_delete=models.CASCADE, blank=True, null=True)

    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='hr_s_i_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='hr_s_i_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='hr_s_i_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'hrms_schedule_interview'

class HrmsScheduleAnotherRoundInterview(models.Model):
    status_choice = (
        (1,'Rescheduled'),
        (2,'On Hold'),
        (3,'Completed'),
        (4,'Cancelled'),
        (5,'On Process')
    )
    schedule_interview=models.ForeignKey(HrmsScheduleInterview,related_name='hr_s_a_r_i_schedule_interview',
                                   on_delete=models.CASCADE, blank=True, null=True)
    planned_date_of_interview= models.DateTimeField(blank=True, null=True)
    planned_time_of_interview= models.TimeField(blank=True, null=True)
    actual_date_of_interview= models.DateTimeField(blank=True, null=True)
    actual_time_of_interview= models.TimeField(blank=True, null=True)
    type_of_interview=models.ForeignKey(HrmsInterviewType,related_name='hr_s_a_r_i_type_of_interview',
                                   on_delete=models.CASCADE, blank=True, null=True)
    level_of_interview=models.ForeignKey(HrmsInterviewLevel,related_name='hr_s_a_r_i_level_of_interview',
                                   on_delete=models.CASCADE, blank=True, null=True)
    interview_status= models.IntegerField(choices=status_choice,null=True,blank=True,default=5)
    is_resheduled = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='hr_s_a_r_i_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='hr_s_a_r_i_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='hr_s_a_r_i_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'hrms_schedule_another_round_interview'

class HrmsScheduleInterviewLog(models.Model):
    action_choice = (
        (1,'approved'),
        (2,'rejected'),
        (3,'pending')
    )
    hsi_master=models.ForeignKey(HrmsScheduleInterview,related_name='hr_s_i_log_master',
                                   on_delete=models.CASCADE, blank=True, null=True)
    requirement=models.ForeignKey(HrmsNewRequirement,related_name='hr_s_i_log_requirement',
                                   on_delete=models.CASCADE, blank=True, null=True)
    candidate_name= models.CharField(max_length=50,blank=True,null=True)
    contact_no= models.CharField(max_length=10,blank=True,null=True)
    email= models.EmailField(max_length=70,blank=True,null=True)
    note= models.CharField(max_length=100,blank=True,null=True)
    resume=models.FileField(upload_to=get_directory_path,
                                default=None,
                                null=True,blank=True,
                                validators=[validate_file_extension])
    notice_period = models.CharField(max_length=100,blank=True,null=True)
    expected_ctc = models.IntegerField(blank=True,null=True)
    current_ctc = models.IntegerField(blank=True,null=True)
    action_approval = models.IntegerField(choices=action_choice,null=True,blank=True,default=3)
    level_approval= models.BooleanField(default=False)
    approval_permission_user_level =  models.ForeignKey(PmsApprovalPermissonMatser, related_name='hr_s_i_log_log_permission_id',
                                   on_delete=models.CASCADE, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='hr_s_i_log_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='hr_s_i_log_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='hr_s_i_log_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'hrms_schedule_interview_log'

class HrmsScheduleInterviewWith(models.Model):
    interview=models.ForeignKey(HrmsScheduleAnotherRoundInterview,related_name='hr_s_i_w_interview',
                                   on_delete=models.CASCADE, blank=True, null=True)
    user=models.ForeignKey(User,related_name='hr_s_i_w_user',
                                   on_delete=models.CASCADE, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='hr_s_i_w_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='hr_s_i_w_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='hr_s_i_w_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'hrms_schedule_interview_with'

class HrmsScheduleInterviewFeedback(models.Model):
    interview=models.ForeignKey(HrmsScheduleAnotherRoundInterview,related_name='hr_s_i_f_interview',
                                   on_delete=models.CASCADE, blank=True, null=True)
    upload_feedback=models.FileField(upload_to=get_directory_path,
                                default=None,
                                null=True,blank=True,
                                validators=[validate_file_extension])
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='hr_s_i_f_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='hr_s_i_f_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='hr_s_i_f_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'hrms_schedule_interview_feedback'