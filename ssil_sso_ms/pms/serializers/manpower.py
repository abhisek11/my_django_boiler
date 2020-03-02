from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from pms.models import *
from django.contrib.auth.models import *
import time
from django.db import transaction, IntegrityError
from drf_extra_fields.fields import Base64ImageField
import os
from rest_framework.exceptions import APIException
import datetime
from master.models import TMasterModuleRoleUser
from core.models import TCoreDesignation
from rest_framework.response import Response
from pms.custom_filter import custom_filter
import pandas as pd
import numpy as np
import xlrd
from pms.custom_delete import *
from django.db.models import Q
import re

class UserModuleWiseDesignationListSerializer(serializers.ModelSerializer):
    mmr_designation_name = serializers.SerializerMethodField(required=False)
    def get_mmr_designation_name(self,TMasterModuleRoleUser):
        designation_details = TCoreDesignation.objects.filter(pk=TMasterModuleRoleUser.mmr_designation)
        print('designation_details',designation_details)
        if not designation_details:
            print('designation_details1111')
            return None
            
        else: 
            print('not designation_details')
            designation = str(TCoreDesignation.objects.only('cod_name').get(pk=TMasterModuleRoleUser.mmr_designation).cod_name)
            print('designation',designation) 
            
    class Meta:
        model = TMasterModuleRoleUser
        fields = ('id','mmr_designation','mmr_module','mmr_designation_name')