from django.db import models
from django.contrib.auth.models import User


class PmsTourAndTravelExpenseMaster(models.Model):
    
    status_choice=((1,'starting'),
                    (2,'pending'),
                    (3,'completed'),
                    )
    type_of_user=((1,'employee'),
                    (2,'guest'))
    type_of_approved_status=((1,'approve'),
                             (2,'reject'),
                             (3,'modification'))

    travel_stage_status=models.IntegerField(choices=status_choice, null=True, blank=True,default=1) 
    company_name=models.CharField(max_length=200, blank=True, null=True)
    user_type=models.IntegerField(choices=type_of_user,null=True,blank=True) 
    employee= models.ForeignKey(User, related_name='t_a_t_e_m_employee_name',
                                   on_delete=models.CASCADE, blank=True, null=True)
    guest= models.CharField(max_length=200, blank=True, null=True)                              
    journey_number=models.TextField(blank=True, null=True)
    booking_date=models.DateTimeField(blank=True, null=True)
    booking_by=models.CharField(max_length=200, blank=True, null=True)
    place_of_travel=models.CharField(max_length=200, blank=True, null=True)
    from_date=models.DateTimeField(blank=True, null=True)
    to_date=models.DateTimeField(blank=True, null=True)
    non=models.CharField(max_length=200, blank=True, null=True)
    extra_day=models.IntegerField(blank=True, null=True)
    approved_status=models.IntegerField(choices=type_of_approved_status,null=True,blank=True)
    request_modification=models.TextField(blank=True,null=True)
    total_expense= models.DecimalField(max_digits=10,decimal_places=2,blank=True,null=True)
    limit_exceed_by=models.DecimalField(max_digits=10,decimal_places=2,blank=True,null=True)
    total_flight_fare=models.DecimalField(max_digits=10,decimal_places=2,blank=True,null=True)
    advance=models.DecimalField(max_digits=10,decimal_places=2,blank=True,null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='t_a_t_e_m_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='t_a_t_e_m_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='t_a_t_e_m_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'pms_tour_and_travel_expense_master'

class PmsTourAndTravelEmployeeDailyExpenses(models.Model):
    expenses_master = models.ForeignKey(PmsTourAndTravelExpenseMaster,related_name='t_a_t_e_d_e_expenses_master',
                                   on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    fare = models.DecimalField(max_digits=10,decimal_places=2,blank=True,null=True)
    local_conveyance = models.DecimalField(max_digits=10,decimal_places=2,blank=True,null=True)
    lodging_expenses = models.DecimalField(max_digits=10,decimal_places=2,blank=True,null=True)
    fooding_expenses = models.DecimalField(max_digits=10,decimal_places=2,blank=True,null=True)
    da = models.DecimalField(max_digits=10,decimal_places=2,blank=True,null=True)
    other_expenses = models.DecimalField(max_digits=10,decimal_places=2,blank=True,null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='t_a_t_e_d_e_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='t_a_t_e_d_e_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='t_a_t_e_d_e_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'pms_tour_and_travel_employee_daily_expenses'

    
class PmsTourAndTravelVendorOrEmployeeDetails(models.Model):
    type_of_approved_status=((1,'approve'),
                             (2,'reject'),
                             (3,'modification'))
    type_of_vendor_or_employee=((1,'vendor'),
                            (2,'employee'))
    expenses_master = models.ForeignKey(PmsTourAndTravelExpenseMaster,related_name='t_a_t_v_o_e_d_expenses_master',
                                   on_delete=models.CASCADE, blank=True, null=True)
    bill_number = models.CharField(max_length=200, blank=True, null=True)
    employee_or_vendor_type=models.IntegerField(choices=type_of_vendor_or_employee,null=True,blank=True) 
    empolyee_or_vendor_id=models.IntegerField(blank=True,null=True)
    bill_amount = models.DecimalField(max_digits=10,decimal_places=2,blank=True,null=True)
    advance_amount = models.DecimalField(max_digits=10,decimal_places=2,blank=True,null=True)
    approved_status=models.IntegerField(choices=type_of_approved_status,null=True,blank=True)
    request_modification=models.TextField(blank=True,null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='t_a_t_v_o_e_d_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='t_a_t_v_o_e_d_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='t_a_t_v_o_e_d_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'pms_tour_and_travel_vendor_or_employee_details'

class PmsTourAndTravelBillReceived(models.Model):
    type_of_approved_status=((1,'approve'),
                             (2,'reject'),
                             (3,'modification'))
    type_of_vendor_or_employee=((1,'vendor'),
                            (2,'employee'))
    expenses_master = models.ForeignKey(PmsTourAndTravelExpenseMaster,related_name='t_a_t_b_r_expenses_master',
                                   on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)
    parking_expense = models.DecimalField(max_digits=10,decimal_places=2,blank=True,null=True)
    posting_expense = models.DecimalField(max_digits=10,decimal_places=2,blank=True,null=True)
    employee_or_vendor_type=models.IntegerField(choices=type_of_vendor_or_employee,null=True,blank=True) 
    empolyee_or_vendor_id=models.IntegerField(blank=True,null=True)
    less_amount =models.DecimalField(max_digits=10,decimal_places=2,blank=True,null=True)
    cgst = models.DecimalField(max_digits=20,decimal_places=2,blank=True,null=True)
    sgst = models.DecimalField(max_digits=20,decimal_places=2,blank=True,null=True)
    igst =models.DecimalField(max_digits=20,decimal_places=2,blank=True,null=True)
    document_number = models.CharField(max_length=200, blank=True, null=True)
    cost_center_number = models.CharField(max_length=200, blank=True, null=True)
    net_expenditure = models.DecimalField(max_digits=10,decimal_places=2,blank=True,null=True)
    advance_amount=models.DecimalField(max_digits=10,decimal_places=2,blank=True,null=True)
    fare_and_conveyance=models.DecimalField(max_digits=10,decimal_places=2,blank=True,null=True)
    lodging_fooding_and_da=models.DecimalField(max_digits=10,decimal_places=2,blank=True,null=True)
    expense_mans_per_day=models.DecimalField(max_digits=10,decimal_places=2,blank=True,null=True)
    total_expense = models.DecimalField(max_digits=10,decimal_places=2,blank=True,null=True)
    limit_exceeded_by =  models.DecimalField(max_digits=10,decimal_places=2,blank=True,null=True)
    remarks = models.TextField(blank=True, null=True)
    approved_status=models.IntegerField(choices=type_of_approved_status,null=True,blank=True)
    request_modification=models.TextField(blank=True,null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='t_a_t_b_r_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='t_a_t_b_r_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='t_a_t_b_r_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'pms_tour_and_travel_bill_received'

class PmsTourAndTravelWorkSheetFlightBookingQuotation(models.Model):
    type_of_booking_quotations=((1,'onward_journey'),
                            (2,'return_journey'))
    expenses_master = models.ForeignKey(PmsTourAndTravelExpenseMaster,
                                        related_name='t_a_t_w_s_f_b_q_expenses_master',
                                        on_delete=models.CASCADE, blank=True, null=True)
    flight_booking_quotation_type=models.IntegerField(choices=type_of_booking_quotations, null=True, blank=True)
    date = models.DateField(blank=True, null=True)
    sector= models.CharField(max_length=200, blank=True, null=True)
    airline= models.CharField(max_length=200, blank=True, null=True)
    flight_number=models.CharField(max_length=200, blank=True, null=True)
    time=models.TimeField(blank=True, null=True)
    corporate_fare_agent_1=models.DecimalField(max_digits=10,decimal_places=2,blank=True,null=True)
    corporate_fare_agent_2= models.DecimalField(max_digits=10,decimal_places=2,blank=True,null=True)
    retail_fare_agent_1= models.DecimalField(max_digits=10,decimal_places=2,blank=True,null=True)
    retail_fare_agent_2= models.DecimalField(max_digits=10,decimal_places=2,blank=True,null=True)
    airline_fare= models.DecimalField(max_digits=10,decimal_places=2,blank=True,null=True)
    others=models.TextField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='t_a_t_w_s_f_b_q_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='t_a_t_w_s_f_b_q_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='t_a_t_w_s_f_b_q_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'pms_tour_and_travel_work_sheet_flight_booking_quotation'

class PmsTourAndTravelFinalBookingDetails(models.Model):
    type_of_approved_status=((1,'approve'),
                             (2,'reject'),
                             (3,'modification'))
    type_of_vendor_or_employee=((1,'vendor'),
                            (2,'employee'))
    expenses_master = models.ForeignKey(PmsTourAndTravelExpenseMaster,
                                        related_name='t_a_t_f_b_d_expenses_master',
                                        on_delete=models.CASCADE, blank=True, null=True)
    employee_or_vendor_type=models.IntegerField(choices=type_of_vendor_or_employee,null=True,blank=True)
    empolyee_or_vendor_id=models.IntegerField(blank=True,null=True)
    date_of_journey=models.DateField(blank=True, null=True)
    time=models.TimeField(blank=True, null=True)
    flight_no=models.CharField(max_length=200, blank=True, null=True)
    travel_sector=models.CharField(max_length=200, blank=True, null=True)
    number_of_persons=models.IntegerField( blank=True, null=True)
    rate_per_person= models.DecimalField(max_digits=10,decimal_places=2,blank=True,null=True)
    total_cost= models.DecimalField(max_digits=10,decimal_places=2,blank=True,null=True)
    approved_status=models.IntegerField(choices=type_of_approved_status,null=True,blank=True)
    request_modification=models.TextField(blank=True,null=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='t_a_t_f_b_d_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='t_a_t_f_b_d_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='t_a_t_f_b_d_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = 'pms_tour_and_travel_final_booking_details'