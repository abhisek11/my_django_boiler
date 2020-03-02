from django.db import models
from django.contrib.auth.models import User
from core.models import *

# Create your models here.
class HolidaysList(models.Model):
    holiday_name = models.CharField(max_length=100, blank=False,null=False)
    holiday_date = models.DateField(blank=False,null=False)
    status = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='h_l_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='h_l_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='h_l_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return '{}, {}'.format(self.holiday_name, self.holiday_date)
    class Meta:
        db_table = 'holidays_list'


class HolidayStateMapping(models.Model):
    holiday = models.ForeignKey(HolidaysList, related_name='hsm_holiday', on_delete=models.CASCADE)
    state = models.ForeignKey(TCoreState, related_name='hsm_state', on_delete=models.CASCADE)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='hsm_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='hsm_owned_by',
                                 on_delete=models.CASCADE, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='hsm_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{}, {}, {}'.format(self.holiday.holiday_name, self.holiday.holiday_date, self.state.cs_state_name)
    class Meta:
        db_table = 'holiday_state_mapping'
