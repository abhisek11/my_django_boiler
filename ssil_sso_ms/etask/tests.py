from django.test import TestCase
from django.db import models
from django.contrib.auth.models import User
from dynamic_media import get_directory_path
from validators import validate_file_extension
from etask.models import *


#random task id generation unit test ---Abhisek Singh 

def unique_rand_task():
    while True:
        latest_task = EtaskTask.objects.latest()
        print("latest_task",latest_task)
        # code = "TSK" + str(int(time.time()))
        # if not EtaskTask.objects.filter(task_code_id=code).exists():
        #     return code 