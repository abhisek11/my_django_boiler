from django.db import models
from django.contrib.auth.models import User
from dynamic_media import get_directory_path
from master.models import *
from PIL import Image
import collections

class TCoreUserDetail(models.Model):
    USER_TYPE_CHOICE = (
        ('User','User'),
        ('Director','Director'),
        ('Housekeeper','Housekeeper'),
        )
    GENDER_CHOICE = (
        ('male','Male'),
        ('female','Female'),
       )
    blood_group_type=(('A+','A+'),
                      ('A-','A-'),
                      ('B+','B+'),
                      ('B-','B-'),
                      ('O+','O+'),
                      ('O-','O-'),
                      ('AB+','AB+'),
                      ('AB-','AB-')
                    )
    marital_status_type=(('Married','Married'),
                      ('Single','Single'),
                    )
    cu_user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cu_user',blank=True,null=True)
    cu_gender = models.CharField(choices =GENDER_CHOICE,max_length = 10,blank=True,null=True)
    cu_phone_no = models.CharField(max_length = 15, blank=True,null=True) # business contact no
    cu_alt_phone_no = models.CharField(max_length = 15, blank=True,null=True) # personal contact no
    cu_alt_email_id=models.EmailField(max_length=70,blank=True,null=True) # official email id
    cu_punch_id = models.CharField(max_length = 50, blank=True, null=True)
    cu_emp_code = models.CharField(max_length = 50, blank=True, null=True)
    cu_profile_img = models.ImageField(upload_to=get_directory_path, default=None)
    cu_dob = models.DateField(max_length=8, default=None, blank=True,null=True)
    sap_personnel_no=models.CharField(max_length = 200, blank=True, null=True)
    initial_ctc=models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    current_ctc=models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    cost_centre=models.CharField(max_length = 200, blank=True, null=True)
    address = models.TextField(blank=True,null=True)
    blood_group=models.CharField(choices =blood_group_type,max_length = 10,blank=True,null=True)
    total_experience= models.CharField(max_length = 100, blank=True, null=True)
    job_description = models.TextField(blank=True,null=True)
    company=models.ForeignKey(TCoreCompany,on_delete=models.CASCADE,related_name='cu_company',blank=True,null=True)
    hod=models.ForeignKey(User,on_delete=models.CASCADE,related_name='cu_hod',blank=True,null=True)
    reporting_head=models.ForeignKey(User,on_delete=models.CASCADE,related_name='reporting_head',blank=True,null=True)
    department=models.ForeignKey(TCoreDepartment,on_delete=models.CASCADE,related_name='cu_department',blank=True,null=True)
    designation=models.ForeignKey(TCoreDesignation,on_delete=models.CASCADE,related_name='cu_designation',blank=True,null=True)
    password_to_know=models.CharField(max_length = 200, blank=True, null=True)
    granted_cl=models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    granted_sl=models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    granted_el=models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    joining_date = models.DateTimeField(blank=True, null=True)
    termination_date = models.DateTimeField(blank=True, null=True)
    daily_loginTime = models.TimeField(blank=True, null=True)
    daily_logoutTime = models.TimeField(blank=True, null=True)
    saturday_logout= models.TimeField(blank=True, null=True)
    lunch_start = models.TimeField(blank=True, null=True)
    lunch_end = models.TimeField(blank=True, null=True)
    worst_late= models.TimeField(blank=True, null=True)
    is_tech = models.BooleanField(default=False)
    cu_is_deleted = models.BooleanField(default=False)
    cu_change_pass = models.BooleanField(default=True)
    is_saturday_off = models.BooleanField(default=False)
    cu_created_by = models.ForeignKey(User, on_delete=models.CASCADE,related_name='cu_created_by',blank=True,null=True)
    cu_created_at=models.DateTimeField(auto_now_add=True)
    cu_updated_at=models.DateTimeField(auto_now =True)
    cu_updated_by=models.ForeignKey(User, on_delete=models.CASCADE, related_name='cu_updated_by',blank=True,null=True)
    cu_deleted_at=models.DateTimeField(auto_now =True,blank=True,null=True)
    cu_deleted_by= models.ForeignKey(User, on_delete=models.CASCADE, related_name='cu_deleted_by',blank=True,null=True)
    employee_grade = models.ForeignKey(TCoreGrade, on_delete=models.CASCADE, related_name='eg_deleted_by',blank=True,null=True)
    salary_type = models.ForeignKey(TCoreSalaryType, on_delete=models.CASCADE, related_name='cu_salary_type',blank=True,null=True)
    is_confirm = models.BooleanField(default=False)
    job_location = models.CharField(max_length = 50, blank=True, null=True)
    job_location_state = models.ForeignKey(TCoreState, on_delete=models.CASCADE, related_name='job_loc_state',
    blank=True,null=True)
    source = models.CharField(max_length = 50, blank=True, null=True)
    source_name = models.CharField(max_length = 50, blank=True, null=True)
    bank_account = models.CharField(max_length = 15, blank=True, null=True)
    ifsc_code = models.CharField(max_length = 15, blank=True, null=True)
    branch_name = models.CharField(max_length = 30, blank=True, null=True)
    pincode = models.CharField(max_length = 15, blank=True, null=True)
    emergency_contact_no = models.CharField(max_length = 15, blank=True,null=True)
    father_name = models.CharField(max_length = 20, blank=True,null=True)
    pan_no = models.CharField(max_length = 12, blank=True,null=True)
    aadhar_no = models.CharField(max_length = 12, blank=True,null=True)
    uan_no = models.CharField(max_length = 12, blank=True,null=True)
    pf_no = models.CharField(max_length = 25, blank=True,null=True)
    esic_no = models.CharField(max_length = 25, blank=True,null=True)
    marital_status = models.CharField(choices = marital_status_type,max_length = 15,blank=True,null=True)
    salary_per_month=models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    state = models.ForeignKey(TCoreState, on_delete=models.CASCADE, related_name='em_state',
    blank=True,null=True)
    resignation_date = models.DateTimeField(blank=True,null=True)
    user_type = models.CharField(choices = USER_TYPE_CHOICE,max_length = 15,blank=True,null=True)

    def __str__(self):
        return str(self.id)

    

    class Meta:
        db_table = 't_core_user_details'
        #unique_together = ('cu_punch_id', 'cu_phone_no',)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        try:
            if self.id is not None:
                previous = TCoreUserDetail.objects.get(id=self.id)
                super(TCoreUserDetail, self).save(force_insert, force_update)
                size = (256, 256)
                if self.cu_profile_img and self.cu_profile_img != previous.cu_profile_img:
                    print('self.cu_profile_img:', self.cu_profile_img)
                    cu_profile_img = Image.open(self.cu_profile_img.path)
                    print("cu_profile_img size:", cu_profile_img.size)
                    cu_profile_img.thumbnail(size, Image.ANTIALIAS)
                    print("logo 2size:", cu_profile_img.size)
                    cu_profile_img.save(self.cu_profile_img.path)
            else:
                super(TCoreUserDetail, self).save(force_insert, force_update)

        except Exception as e:
            raise e
    def applications(self):
        app_list = []
        try:
            mmr_detalis = TMasterModuleRoleUser.objects.filter(mmr_user_id = self.cu_user_id)
            if mmr_detalis:
                for mmr_data in mmr_detalis:
                    mmr_odict = collections.OrderedDict()
                    #print("mmr_data: ", mmr_data.mmr_permissions)
                    if mmr_data.mmr_type:
                        mmr_odict['mmr_type'] = mmr_data.mmr_type
                    else:
                        mmr_odict['mmr_type'] = None


                    if mmr_data.mmr_module:
                        mmr_odict['mmr_module'] = {"id":mmr_data.mmr_module.id,
                                                   "cm_name":mmr_data.mmr_module.cm_name}
                    else:
                        mmr_odict['mmr_module'] = dict()

                    if mmr_data.mmr_role:
                        mmr_odict['mmr_role'] = {
                                                # "id": mmr_data.mmr_role.id,
                                                "cr_name": mmr_data.mmr_role.cr_name,
                                                 # "cr_parent_id": mmr_data.mmr_role.cr_parent_id
                                                 }
                    else:
                        mmr_odict['mmr_role'] = dict()

                    # if mmr_data.mmr_permissions:
                    #     mmr_odict['mmr_permissions'] = {
                    #         "id": mmr_data.mmr_permissions.id,
                    #         "name": mmr_data.mmr_permissions.name,
                    #         }
                    # else:
                    #     mmr_odict['mmr_permissions'] = dict()
                    app_list.append(mmr_odict)
            else:
                app_list = list()
            return app_list
        except Exception as e:
            raise e

class LoginLogoutLoggedTable(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,blank=True, null=True)
    token=models.CharField(max_length=255, blank=True, null=True)
    ip_address=models.CharField(max_length=255, blank=True, null=True)
    login_time=models.DateTimeField(auto_now_add=True)
    logout_time=models.DateTimeField(auto_now=False, blank=True, null=True)
    browser_name=models.CharField(max_length=255, blank=True, null=True)
    os_name=models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 't_log_signin_signout'

    
