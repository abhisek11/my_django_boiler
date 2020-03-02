from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class AppVersion(models.Model):
    name = models.CharField(max_length=100, blank=True,null=True)
    version = models.CharField(max_length=100, blank=True,null=True)
    is_deleted = models.BooleanField(default=False)
    updated_at=models.DateTimeField(auto_now =True)
    updated_by=models.ForeignKey(User, on_delete=models.CASCADE, related_name='a_updated_by',blank=True,null=True)
    deleted_at=models.DateTimeField(auto_now =True)
    deleted_by=models.ForeignKey(User, on_delete=models.CASCADE, related_name='a_deleted_by',blank=True,null=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'app_version'