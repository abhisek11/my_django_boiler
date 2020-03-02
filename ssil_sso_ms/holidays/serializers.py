from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from attendance.models import *
from holidays.models import *
from django.contrib.auth.models import *
from django.db import transaction, IntegrityError
from drf_extra_fields.fields import Base64ImageField
import os
from holidays.models import * 
# import datetime
from django.db.models import Q
from datetime import datetime,timedelta
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from users.models import TCoreUserDetail
from smssend.views import *
from threading import Thread
from attendance.views import *
from django.db.models import Sum
from custom_exception_message import *
from django.db.models import Q
import calendar
from hrms.models import *


#:::::::::::::::::::::: HOLIDAYS LIST:::::::::::::::::::::::::::#
class HolidaysListAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    status=serializers.BooleanField(default=True)
    class Meta:
        model = HolidaysList
        fields = ('id', 'holiday_name', 'holiday_date', 'status', 'created_by', 'owned_by')


class HolidaysListEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    status=serializers.BooleanField(default=True)
    class Meta:
        model = HolidaysList
        fields = ('id', 'holiday_name', 'holiday_date', 'status', 'updated_by')

class HolidaysListDeleteSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = HolidaysList
        fields = '__all__'
    def update(self, instance, validated_data):
        instance.is_deleted=True
        instance.status=False
        instance.updated_by = validated_data.get('updated_by')
        instance.save()
        return instance

class HolidaysListStateWiseSerializerOld(serializers.ModelSerializer):

    class Meta:
        model = HolidaysList
        fields = ('id', 'holiday_name', 'holiday_date', 'state_name')

class HolidaysListStateWiseSerializer(serializers.ModelSerializer):
    holiday_id = serializers.IntegerField(source='holiday.id', read_only=True)
    holiday_name = serializers.CharField(source='holiday.holiday_name', read_only=True)
    holiday_date = serializers.CharField(source='holiday.holiday_date', read_only=True)
    state_id = serializers.IntegerField(source='state.id', read_only=True)
    cs_state_name = serializers.CharField(source='state.cs_state_name', read_only=True)

    class Meta:
        model = HolidayStateMapping
        fields = ('id', 'holiday_id', 'holiday_name', 'holiday_date', 'state_id', 'cs_state_name')


class StateWiseHolidaysAddSerializer(serializers.Serializer):
    STATES = [(state.id, state.cs_state_name) for state in TCoreState.objects.filter(Q(cs_status=True)&Q(cs_is_deleted=False))]
    states = serializers.MultipleChoiceField(choices=STATES, allow_blank=False)
    holiday_name = serializers.CharField(max_length=255, required=True)
    holiday_date = serializers.DateField()


class HolidaysStateWiseEditSerializer(serializers.ModelSerializer):
    holiday_name = serializers.CharField(source='holiday.holiday_name', read_only=True)
    holiday_date = serializers.CharField(source='holiday.holiday_date', read_only=True)

    class Meta:
        model = HolidayStateMapping
        fields = ('id', 'holiday_name', 'holiday_date')
    
    def update(self, instance, validated_data):
        user = self.context['request'].user
        instance.holiday.holiday_name = self.context['request'].data.get('holiday_name', instance.holiday.holiday_name)
        instance.holiday.holiday_date = self.context['request'].data.get('holiday_date', instance.holiday.holiday_date)
        instance.updated_by = user
        instance.holiday.save()
        instance.save()
        return instance

class StateWiseHolidaysDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = HolidayStateMapping
        fields = '__all__'
    
    def update(self, instance, validated_data):
        user = self.context['request'].user
        instance.is_deleted=True
        instance.updated_by = user
        instance.save()
        return instance

    