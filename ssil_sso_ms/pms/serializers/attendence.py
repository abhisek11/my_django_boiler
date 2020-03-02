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
from core.models import TCoreUnit
from rest_framework.response import Response
from pms.custom_filter import custom_filter
import pandas as pd
import numpy as np
import xlrd
from pms.custom_delete import *
from django.db.models import Q
import re
from pms.serializers.project import *
from geopy.distance import great_circle
from decimal import Decimal
import threading

#:::::::::::: ATTENDENCE ::::::::::::#
class PmsAttendanceAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    employee = serializers.CharField(default=serializers.CurrentUserDefault())
    type = serializers.IntegerField(required=True)
    user_project_id = serializers.IntegerField(required=True)
    date = serializers.DateField(required=True)
    login_time = serializers.TimeField(required=True)
    login_latitude = serializers.CharField(required=True)
    login_longitude = serializers.CharField(required=True)
    login_address = serializers.CharField(required=True)

    class Meta:
        model = PmsAttendance
        fields = (
        'id', 'type', 'employee', 'user_project_id', 'date', 'login_time', 'login_latitude', 'login_longitude',
        'login_address', 'created_by', 'owned_by',)

    def create(self, validated_data):
        try:
            attendance_data = PmsAttendance.objects.create(**validated_data)
            print('attendance_data: ', attendance_data.type)
            return attendance_data
        except Exception as e:
            raise APIException({"msg": e, "request_status": 0})
# class AttendanceLogOutSerializer(serializers.ModelSerializer):
#     updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
#
#     class Meta:
#         model = PmsAttendance
#         fields = ('id', 'logout_time', 'logout_latitude', 'logout_longitude', 'logout_address', 'updated_by')
#
#     def update(self, instance, validated_data):
#         instance.logout_time = validated_data.get("logout_time", instance.logout_time)
#         instance.logout_latitude = validated_data.get("logout_latitude", instance.logout_latitude)
#         instance.logout_longitude = validated_data.get("logout_longitude", instance.logout_longitude)
#         instance.updated_by = validated_data.get("updated_by")
#         instance.save()
#         print("instance.attandance: ", type(instance.id))
#         # log_details = PmsAttandanceLog.objects.filter()
#         self.add_deviations(instance.id, instance.logout_time, instance.updated_by)
#         return instance
#
#     def add_deviations(self, att_id, log_out_time, owned_by):
#         from datetime import timedelta
#         owned_by = owned_by
#         att_id = att_id
#
#         log_details = PmsAttandanceLog.objects.filter(attandance_id=att_id).order_by('id')
#         flag = 0
#         check_len = 0
#         # for log in log_details:
#         #     check_len += 1
#         #     checkout = log.is_checkout
#         #     if checkout == True:
#         #         if flag == 1:
#         #             # if not to_time:
#         #             if check_len == len(log_details):
#         #                 to_time = log_out_time
#         #                 self.calculate_deviation(att_id, from_time, to_time, owned_by)
#         #         else:
#         #             flag= 1
#         #             from_time = log.time
#         #     else:
#         #         if flag == 1:
#         #             flag = 0
#         #             to_time = log.time
#         #             self.calculate_deviation(att_id, from_time, to_time, owned_by)
#         if len(log_details) == 1:
#             for log in log_details:
#                 from_time = log.time
#                 to_time = log_out_time
#                 self.calculate_deviation(att_id, from_time, to_time, owned_by)
#         else:
#             for log in log_details:
#                 check_len += 1
#                 print("check_len: ", check_len)
#                 checkout = log.is_checkout
#                 if checkout == True:
#                     if flag == 1:
#                         # if not to_time:
#                         if check_len == len(log_details):
#                             to_time = log_out_time
#                             print("to_time:", to_time)
#                             self.calculate_deviation(att_id, from_time, to_time, owned_by)
#                     else:
#                         flag = 1
#                         from_time = log.time
#                         print("from_time:", from_time)
#                 else:
#                     if flag == 1:
#                         flag = 0
#                         to_time = log.time
#                         self.calculate_deviation(att_id, from_time, to_time, owned_by)
#
#     def calculate_deviation(self, att_id, from_time, to_time, owned_by):
#         data_dict = {}
#         print("to_time",to_time)
#         print("from_time",from_time)
#         dev_time = (from_time - to_time)
#         print("dev_time",dev_time)
#         time_deviation = (datetime.datetime.min + dev_time).time().strftime('%H:%M:%S')
#         data_dict["attandance_id"] = att_id
#         data_dict["from_time"] = from_time.strftime('%Y-%m-%dT%H:%M:%S')
#         data_dict["to_time"] = to_time.strftime('%Y-%m-%dT%H:%M:%S')
#         data_dict["deviation_time"] = time_deviation
#         data_dict["owned_by"] = owned_by
#         if dev_time.seconds <= 3600 * 5 and dev_time.seconds >= 3600 * 2.5:
#             data_dict["deviation_type"] = "HD"
#         elif dev_time.seconds > 3600 * 5:
#             data_dict["deviation_type"] = "FD"
#         else:
#             data_dict["deviation_type"] = "OD"
#
#         if data_dict:
#             PmsAttandanceDeviation.objects.create(**data_dict)
class AttendanceLogOutSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsAttendance
        fields = ('id', 'logout_time', 'logout_latitude', 'logout_longitude', 'logout_address', 'updated_by')

    def update(self, instance, validated_data):
        instance.logout_time = validated_data.get("logout_time", instance.logout_time)
        instance.logout_latitude = validated_data.get("logout_latitude", instance.logout_latitude)
        instance.logout_longitude = validated_data.get("logout_longitude", instance.logout_longitude)
        instance.logout_address = validated_data.get("logout_address", instance.logout_address)
        instance.updated_by = validated_data.get("updated_by")
        instance.save()
        print("instance.attandance: ", type(instance.id))
        # log_details = PmsAttandanceLog.objects.filter()
        self.add_deviations(instance.id, instance.logout_time, instance.updated_by)
        return instance

    def add_deviations(self, att_id, log_out_time, owned_by):
        from datetime import timedelta
        owned_by = owned_by
        att_id = att_id

        log_details = PmsAttandanceLog.objects.filter(attandance_id=att_id).order_by('id')
        flag = 0
        check_len = 0
        if len(log_details) == 1:
            # print("if len(log_details) == 1")
            for log in log_details:
                # print("log 11",log)
                from_time = log.time
                to_time = log_out_time
                # print("step 1", from_time, to_time)
                self.calculate_deviation(att_id, from_time, to_time, owned_by)
        else:
            # print("else len(log_details) == 1")
            for log in log_details:
                # print("log 22",log)
                check_len += 1
                # print("check_len: ", check_len)
                checkout = log.is_checkout
                # print("checkout :", checkout)
                if checkout == True:
                    # print("if checkout == True:")
                    if flag == 1:
                        # print("if flag == 1:")
                        # if not to_time:
                        if check_len == len(log_details):
                            to_time = log_out_time
                            print("to_time:", to_time)
                            self.calculate_deviation(att_id, from_time, to_time, owned_by)
                    else:
                        # print("else flag == 1:")
                        flag = 1
                        from_time = log.time
                        # print("from_time:", from_time)
                else:
                    # print("else checkout == True:")
                    if flag == 1:
                        flag = 0
                        to_time = log.time
                        # print("to_time", to_time)
                        self.calculate_deviation(att_id, from_time, to_time, owned_by)

    def calculate_deviation(self, att_id, from_time, to_time, owned_by):
        data_dict = {}
        # print("===calculate_deviation===")
        # print("from_time",from_time)
        # print("to_time",to_time)
        dev_time = (to_time - from_time)
        # dev_time = (from_time - to_time)
        # print("dev_time",dev_time)
        time_deviation = (datetime.datetime.min + dev_time).time().strftime('%H:%M:%S')
        data_dict["attandance_id"] = att_id
        data_dict["from_time"] = from_time.strftime('%Y-%m-%dT%H:%M:%S')
        data_dict["to_time"] = to_time.strftime('%Y-%m-%dT%H:%M:%S')
        data_dict["deviation_time"] = time_deviation
        data_dict["owned_by"] = owned_by
        if dev_time.seconds <= 3600 * 5 and dev_time.seconds >= 3600 * 2.5:
            data_dict["deviation_type"] = "HD"
        elif dev_time.seconds > 3600 * 5:
            data_dict["deviation_type"] = "FD"
        else:
            data_dict["deviation_type"] = "OD"

        if data_dict:
            PmsAttandanceDeviation.objects.get_or_create(**data_dict)

class AttendanceAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    employee = serializers.CharField(default=serializers.CurrentUserDefault())
    date = serializers.DateTimeField(required=True)
    login_time = serializers.DateTimeField(required=True)

    # employee_details=serializers.SerializerMethodField()
    # def get_employee_details(self, PmsAttendance):
    #     from users.models import TCoreUserDetail
    #     from users.serializers import UserModuleSerializer, UserSerializer
    #     user_details = TCoreUserDetail.objects.filter(cu_user=PmsAttendance.employee)  # Whatever your query may be
    #     serializer = UserModuleSerializer(instance=user_details, many=True)
    #     return serializer.data
    class Meta:
        model = PmsAttendance
        fields = ('id', 'type', 'employee', 'user_project', 'date', 'login_time', 'login_latitude', 'login_longitude',
                  'login_address',
                  'logout_time', 'logout_latitude', 'logout_longitude', 'logout_address', 'approved_status',
                  'justification',
                  'created_by', 'owned_by')


# class AttendanceNewAddSerializer(serializers.ModelSerializer):
#     created_by = serializers.CharField(default=serializers.CurrentUserDefault())
#     owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
#     employee = serializers.CharField(default=serializers.CurrentUserDefault())
#     date = serializers.DateTimeField(required=True)
#     login_time = serializers.DateTimeField(required=True)
#     user_project_details=serializers.ListField(required=False)
#     geo_fencing_area=serializers.CharField(required=False)

#     class Meta:
#         model = PmsAttendance
#         fields = ('__all__')

#     def create(self,validated_data):
#         # print("request",request.user.email)
#         # response = super(AttendanceAddView, self).post(request, args, kwargs)
#         login_date =datetime.strptime(validated_data.get('login_time'),'%Y-%m-%dT%H:%M:%S').date()
#         # print("login_date",login_date)
#         attandance_data = custom_filter(
#                 self,
#                 PmsAttendance,
#                 filter_columns={"login_time__date": login_date, "employee__username":request.user.username}, #modified by Rupam
#                 fetch_columns=['id', 'type', 'employee', 'user_project', 'date', 'login_time', 'login_latitude', 'login_longitude',
#                   'login_address','logout_time', 'logout_latitude', 'logout_longitude', 'logout_address', 'approved_status',
#                   'justification','created_by', 'owned_by'],
#                 single_row=True
#                           )
#         #print("req",request.user)
#         # print("login_time_data",attandance_data)

#         project_user_mapping = PmsProjectUserMapping.objects.filter(user=validated_data.get('user'), status=True).order_by('-id').values('project')
#         # print("project_user_mapping",project_user_mapping)
#         if project_user_mapping:
#             project = project_user_mapping[0]['project']
#             validated_data['user_project_id'] = project

#         if attandance_data:

#             # print("attandance_data",attandance_data)
#             if attandance_data:
#                 if attandance_data['logout_time'] is None:
#                     # print("attandance_data",attandance_data['logout_time'])
#                     return Response({'result':attandance_data,
#                                      'request_status': 1,
#                                      'msg': settings.MSG_SUCCESS
#                                      })
#                 else:
#                     return Response({'request_status': 0,
#                                      'msg': "You are not able to login for today"
#                                      })
#         else:
#             attendance_add, created = PmsAttendance.objects.get_or_create(employee=request.user,created_by=request.user,
#                                                                           owned_by=request.user,**request.data)
#             # print("attendance_add",attendance_add.__dict__)
#             attendance_add.__dict__.pop('_state') if "_state" in attendance_add.__dict__.keys() else attendance_add.__dict__
#             attendance_add.__dict__['project'] = "jkguihij"
#             return Response({'result':attendance_add.__dict__,
#                              'request_status': 1,
#                              'msg': settings.MSG_SUCCESS
#                              })

# class AttendanceOfflineAddSerializer(serializers.ModelSerializer):
#     created_by = serializers.CharField(default=serializers.CurrentUserDefault())
#     owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
#     employee = serializers.CharField(default=serializers.CurrentUserDefault())
#     date = serializers.DateTimeField(required=True)
#     login_time = serializers.DateTimeField(required=True)

#     # employee_details=serializers.SerializerMethodField()
#     # def get_employee_details(self, PmsAttendance):
#     #     from users.models import TCoreUserDetail
#     #     from users.serializers import UserModuleSerializer, UserSerializer
#     #     user_details = TCoreUserDetail.objects.filter(cu_user=PmsAttendance.employee)  # Whatever your query may be
#     #     serializer = UserModuleSerializer(instance=user_details, many=True)
#     #     return serializer.data
#     class Meta:
#         model = PmsAttendance
#         fields = ('id', 'type', 'employee', 'user_project', 'date', 'login_time', 'login_latitude', 'login_longitude',
#                   'login_address',
#                   'logout_time', 'logout_latitude', 'logout_longitude', 'logout_address', 'approved_status',
#                   'justification',
#                   'created_by', 'owned_by',)


class AttendanceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PmsAttendance
        fields = ('id', 'type', 'employee', 'user_project', 'date', 'login_time',
                  'logout_time', 'approved_status', 'justification')
class AttendanceSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsAttendance
        fields = ('id', 'type', 'employee', 'date', 'login_time', 'login_latitude', 'login_longitude', 'login_address',
                  'logout_time', 'logout_latitude', 'logout_longitude', 'logout_address', 'approved_status',
                  'justification', 'updated_by')
class AttendanceApprovalListSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    employee_details = serializers.SerializerMethodField()

    def get_employee_details(self, PmsAttendance):
        from users.models import TCoreUserDetail
        from users.serializers import UserModuleSerializer, UserSerializer
        user_details = TCoreUserDetail.objects.filter(cu_user=PmsAttendance.employee)  # Whatever your query may be
        serializer = UserModuleSerializer(instance=user_details, many=True)
        return serializer.data

    class Meta:
        model = PmsAttendance
        fields = ('id', 'type', 'employee', 'user_project', 'date', 'login_time', 'login_latitude', 'login_longitude',
                  'login_address',
                  'logout_time', 'logout_latitude', 'logout_longitude', 'logout_address', 'approved_status',
                  'justification',
                  'created_by', 'owned_by', 'employee_details')
# class AttandanceALLDetailsListSerializer(serializers.ModelSerializer):
#     employee_details = serializers.SerializerMethodField()
#     deviation_details = serializers.SerializerMethodField()
#     user_project = ProjectDetailsSerializer()
#
#     def get_employee_details(self, PmsAttendance):
#         from users.models import TCoreUserDetail
#         from users.serializers import UserModuleSerializer, UserSerializer
#         user_details = TCoreUserDetail.objects.filter(cu_user=PmsAttendance.employee)  # Whatever your query may be
#         serializer = UserModuleSerializer(instance=user_details, many=True)
#         return serializer.data
#
#     def get_deviation_details(self, PmsAttendance):
#         # print("PmsAttendance: ",PmsAttendance)
#         attendance_deviation = PmsAttandanceDeviation.objects.filter(attandance_id=PmsAttendance.id)
#         serializer = AttandanceDeviationSerializer(instance=attendance_deviation, many=True)
#         # print("serializer.data: ",serializer.data)
#         return serializer.data
#
#     class Meta:
#         model = PmsAttendance
#         fields = ('id', 'user_project', 'date', 'login_time',
#                   'logout_time', 'approved_status', 'justification', 'employee_details', 'deviation_details')
class AttandanceALLDetailsListSerializer(serializers.ModelSerializer):
    employee_details = serializers.SerializerMethodField()
    # log_details = serializers.SerializerMethodField()
    deviation_details = serializers.SerializerMethodField()
    user_project = ProjectDetailsSerializer()

    # def get_log_details(self, PmsAttendance):
    #     # print("PmsAttendance: ",PmsAttendance)
    #     attendance_log = PmsAttandanceLog.objects.filter(attandance_id=PmsAttendance.id)
    #     serializer = AttandanceLogSerializer(instance=attendance_log, many=True)
    #     # print("serializer.data: ",serializer.data)
    #     return serializer.data
    def get_employee_details(self, PmsAttendance):
        from users.models import TCoreUserDetail
        from users.serializers import UserModuleSerializer, UserSerializer
        user_details = TCoreUserDetail.objects.filter(cu_user=PmsAttendance.employee)  # Whatever your query may be
        serializer = UserModuleSerializer(instance=user_details, many=True)
        return serializer.data

    def get_deviation_details(self, PmsAttendance):
        # print("PmsAttendance: ",PmsAttendance)
        attendance_deviation = PmsAttandanceDeviation.objects.filter(attandance_id=PmsAttendance.id)
        serializer = AttandanceDeviationSerializer(instance=attendance_deviation, many=True)
        # print("serializer.data: ",serializer.data)
        return serializer.data

    class Meta:
        model = PmsAttendance
        fields = ('id', 'user_project', 'date', 'login_time',
                  'logout_time', 'approved_status', 'justification', 'employee_details', 'deviation_details')


class AttandanceALLDetailsListByPermissonSerializer(serializers.ModelSerializer):
    employee_details = serializers.SerializerMethodField()
    # log_details = serializers.SerializerMethodField()
    deviation_details = serializers.SerializerMethodField()
    user_project = ProjectDetailsSerializer()

    # def get_log_details(self, PmsAttendance):
    #     # print("PmsAttendance: ",PmsAttendance)
    #     attendance_log = PmsAttandanceLog.objects.filter(attandance_id=PmsAttendance.id)
    #     serializer = AttandanceLogSerializer(instance=attendance_log, many=True)
    #     # print("serializer.data: ",serializer.data)
    #     return serializer.data
    def get_employee_details(self, PmsAttendance):
        from users.models import TCoreUserDetail
        from users.serializers import UserModuleSerializer, UserSerializer
        user_details = TCoreUserDetail.objects.filter(cu_user=PmsAttendance.employee)  # Whatever your query may be
        serializer = UserModuleSerializer(instance=user_details, many=True)
        return serializer.data

    def get_deviation_details(self, PmsAttendance):
        # print("PmsAttendance: ",PmsAttendance)
        attendance_deviation = PmsAttandanceDeviation.objects.filter(attandance_id=PmsAttendance.id)
        serializer = AttandanceDeviationSerializer(instance=attendance_deviation, many=True)
        # print("serializer.data: ",serializer.data)
        return serializer.data

    class Meta:
        model = PmsAttendance
        fields = ('id', 'user_project', 'date', 'login_time',
                  'logout_time', 'approved_status', 'justification', 'employee_details', 'deviation_details')

class AttandanceListWithOnlyDeviationByPermissonSerializer(serializers.ModelSerializer):
    employee_details = serializers.SerializerMethodField()
    # log_details = serializers.SerializerMethodField()
    deviation_details = serializers.SerializerMethodField()
    user_project = ProjectDetailsSerializer()

    # def get_log_details(self, PmsAttendance):
    #     # print("PmsAttendance: ",PmsAttendance)
    #     attendance_log = PmsAttandanceLog.objects.filter(attandance_id=PmsAttendance.id)
    #     serializer = AttandanceLogSerializer(instance=attendance_log, many=True)
    #     # print("serializer.data: ",serializer.data)
    #     return serializer.data
    def get_employee_details(self, PmsAttendance):
        from users.models import TCoreUserDetail
        from users.serializers import UserModuleSerializer, UserSerializer
        user_details = TCoreUserDetail.objects.filter(cu_user=PmsAttendance.employee)  # Whatever your query may be
        serializer = UserModuleSerializer(instance=user_details, many=True)
        return serializer.data

    def get_deviation_details(self, PmsAttendance):
        # print("PmsAttendance: ",PmsAttendance)
        attendance_deviation = PmsAttandanceDeviation.objects.filter(attandance_id=PmsAttendance.id)
        serializer = AttandanceDeviationSerializer(instance=attendance_deviation, many=True)
        # print("serializer.data: ",serializer.data)
        return serializer.data

    class Meta:
        model = PmsAttendance
        fields = ('id', 'user_project', 'date', 'login_time',
                  'logout_time', 'approved_status', 'justification', 'employee_details', 'deviation_details')



#:::::::::::: PmsAttandanceLog ::::::::::::#
class AttandanceLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = PmsAttandanceLog
        fields = (
        'id', 'attandance', 'time', 'latitude', 'longitude', 'address', 'approved_status', 'justification', 'remarks',
        'is_checkout')
class AttandanceLogAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    # logdetails = serializers.ListField(required=False)
    # attendence_log_list= serializers.ListField(required=False)

    class Meta:
        model = PmsAttandanceLog
        fields = ('id', 'attandance', 'time', 'latitude', 'longitude', 'address', 'approved_status', 'justification',
                  'is_checkout', 'created_by', 'owned_by')

    def geofencing(self, cur_location, s_location, geo_fencing_area):
        try:

            if geo_fencing_area.endswith("km"):
                geo_fencing_area = re.findall('^\d+', geo_fencing_area)
                geo_fencing_area = int(geo_fencing_area[0]) * 1000

            else:
                geo_fencing_area = re.findall('^\d+', geo_fencing_area)
                geo_fencing_area = int(geo_fencing_area[0])

            distance = great_circle(cur_location, s_location).meters
            print("distance", distance)
            if distance > geo_fencing_area:
                return True
            else:
                return False
        except Exception as e:
            raise e

    def create(self, validated_data):
        try:
            # is_checkout=True
            attandance_id = validated_data.get('attandance')
            current_user = validated_data.get('created_by')
            latitude = validated_data.get('latitude')
            longitude = validated_data.get('longitude')
            cur_location = (latitude, longitude,)
            assign_project = PmsAttendance.objects.only('user_project_id').get(pk=attandance_id.id).user_project_id
            print("current_user: ", current_user)
            print("user_project_id: ", assign_project)
            # log_count = PmsAttandanceLog.objects.filter(attandance_id=attandance_id).count()
            if not assign_project:
                # print('log_count: ', log_count)
                if latitude and longitude:
                    import math
                    lat = float(latitude)
                    lon = float(longitude)
                    print(lat, lon)
                    R = 6378.1  # earth radius
                    # R = 6371  # earth radius
                    distance = 10  # distance in km
                    lat1 = lat - math.degrees(distance / R)
                    lat2 = lat + math.degrees(distance / R)
                    long1 = lon - math.degrees(distance / R / math.cos(math.degrees(lat)))
                    long2 = lon + math.degrees(distance / R / math.cos(math.degrees(lat)))

                    # site_details = PmsSiteProjectSiteManagement.objects.filter(Q(latitude__gte=lat1, latitude__lte=lat2) | Q(longitude__gte=long1, longitude__lte=long2))
                    site_details = PmsSiteProjectSiteManagement.objects.filter(latitude__gte=lat1,
                                                                               latitude__lte=lat2).filter(
                        longitude__gte=long1, longitude__lte=long2)
                    site_id_list = [i.id for i in site_details]
                    print("site_id_list: ", site_id_list)
                    # project_on_sites = PmsProjects.objects.filter(site_location_)
                    project_user_mapping = PmsProjectUserMapping.objects.filter(user=current_user, status=True,
                                                                                project__site_location_id__in=site_id_list)[
                                           :1]
                    # print(project_user_mapping.query)
                    for project in project_user_mapping:
                        print('project_user_mapping: ', project.project_id)
                        site_lat = project.project.site_location.latitude
                        site_long = project.project.site_location.longitude
                        geo_fencing_area = project.project.site_location.geo_fencing_area
                        s_location = (site_lat, site_long,)

                        PmsAttendance.objects.filter(pk=attandance_id.id).update(user_project_id=project.project_id)
            else:
                attandance_details = PmsAttendance.objects.filter(pk=attandance_id.id)
                for project in attandance_details:
                    print('attandance_project_id: ', project.user_project_id)
                    site_lat = project.user_project.site_location.site_latitude
                    site_long = project.user_project.site_location.site_longitude
                    geo_fencing_area = project.user_project.site_location.geo_fencing_area

                    s_location = (site_lat, site_long,)

            try:

                print('s_location',s_location)
                is_checkout = self.geofencing(cur_location, s_location, geo_fencing_area)
            except Exception as e:
                print(e)
                is_checkout = True

            # print("is_checkout: ", is_checkout)
            attandance_log, created = PmsAttandanceLog.objects.get_or_create(**validated_data, is_checkout=is_checkout)
            print("created: ", created)
            return attandance_log

        except Exception as e:
            raise e

class AttandanceLogMultipleAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    logdetails = serializers.ListField(required=False)
    attendence_log_list= serializers.ListField(required=False)

    class Meta:
        model = PmsAttandanceLog
        fields = ('__all__')
        extra_fields = ('logdetails')
    def create(self, validated_data):
        try:
            logdetails = validated_data.pop('logdetails') if 'logdetails' in validated_data else ""
            print(validated_data)
            owned_by = validated_data.get('owned_by')
            created_by = validated_data.get('created_by')
            '''
                Modified by Rupam Hazra [ remove with transaction.atomic()]
            '''
            
            #with transaction.atomic():
                # pedp_data, created1 = PmsExecutionDailyProgress.objects.get_or_create(**validated_data)
            attendence_log_list = []
            print("log_data",logdetails)
            for data in logdetails:
                if data['is_checkout']=='':
                    data['is_checkout']= False
                # print("log_data",data)
                # print("date_of_completion::::::::",pro_data['date_of_completion'],type(pro_data['date_of_completion']))
                log_data, created1 = PmsAttandanceLog.objects.get_or_create(
                    created_by=created_by,
                    owned_by=owned_by,
                    **data
                    )
                log_data.__dict__.pop('_state') if "_state" in log_data.__dict__.keys() else log_data.__dict__
                attendence_log_list.append(log_data.__dict__)
                validated_data['logdetails']=attendence_log_list
                # print("progress_list:::::", type(progress_list[0]['planned_start_date']))
                # pedp_data.__dict__["progress_data"] = progress_list

            return validated_data



        except Exception as e:
            raise e
    


class AttandanceLogEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsAttandanceLog
        fields = ('id', 'justification', 'updated_by')

    def update(self, instance, validated_data):
        instance.justification = validated_data.get("justification", instance.justification)
        instance.updated_by = validated_data.get("updated_by")
        instance.save()
        return instance
class AttandanceLogApprovalEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsAttandanceLog
        fields = ('id', 'approved_status', 'remarks', 'updated_by')

    def put(self, instance, validated_data):
        instance.justification = validated_data.get("approved_status", instance.justification)
        instance.remarks = validated_data.get("remarks", instance.remarks)
        instance.updated_by = validated_data.get("updated_by")
        instance.save()
        return instance


# ---------------------------------- Pms Attandance Deviation------------------------------------
class AttandanceDeviationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PmsAttandanceDeviation
        fields = "__all__"
class AttandanceDeviationJustificationEditSerializer(serializers.ModelSerializer):
    justified_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsAttandanceDeviation
        fields = ('id', 'deviation_type', 'justification', 'justified_by')

    def update(self, instance, validated_data):
        instance.deviation_type = validated_data.get("deviation_type", instance.deviation_type)
        instance.justification = validated_data.get("justification", instance.justification)
        instance.justified_by = validated_data.get("justified_by")
        instance.save()
        return instance
class AttandanceDeviationApprovaEditSerializer(serializers.ModelSerializer):
    approved_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsAttandanceDeviation
        fields = ('id', 'approved_status', 'remarks', 'approved_by')

    def update(self, instance, validated_data):
        instance.approved_status = validated_data.get("approved_status", instance.approved_status)
        instance.remarks = validated_data.get("remarks", instance.remarks)
        instance.approved_by = validated_data.get("approved_by")
        instance.save()
        return instance

#:::::::::::: PmsAttandanceLeaves ::::::::::::#
# class AdvanceLeavesAddSerializer(serializers.ModelSerializer):
#     employee = serializers.CharField(default=serializers.CurrentUserDefault())
#     created_by = serializers.CharField(default=serializers.CurrentUserDefault())
#     owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
#
#     class Meta:
#         model = PmsEmployeeLeaves
#         fields = (
#         'id', 'employee', 'leave_type', 'approved_status', 'start_date', 'end_date', 'reason', 'created_by', 'owned_by')
class AdvanceLeavesAddSerializer(serializers.ModelSerializer):
    employee = serializers.CharField(default=serializers.CurrentUserDefault())
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    leave_type = serializers.CharField(required=False)
    start_date = serializers.DateTimeField(required=True)
    end_date = serializers.DateTimeField(required=True)
    reason = serializers.CharField(required=False)
    employee_first_name = serializers.CharField(required=False)
    employee_last_name = serializers.CharField(required=False)
    class Meta:
        model = PmsEmployeeLeaves
        fields = (
        'id', 'employee', 'leave_type', 'approved_status', 'start_date', 'end_date', 'reason', 'created_by', 'owned_by',
        'employee_first_name', 'employee_last_name')
    def create(self, validated_data):
        data_dict = {}
        leave_data, created11 = PmsEmployeeLeaves.objects.get_or_create(**validated_data)
        employee_first_name = User.objects.only('first_name').get(id=leave_data.__dict__['employee_id']).first_name
        employee_last_name = User.objects.only('last_name').get(id=leave_data.__dict__['employee_id']).last_name
        leave_data.__dict__.pop('_state') if "_state" in leave_data.__dict__.keys() else leave_data.__dict__

        data_dict = leave_data.__dict__
        data_dict['employee_first_name']=employee_first_name
        data_dict['employee_last_name']=employee_last_name
        # print("data_dict",data_dict)
        return data_dict

class AdvanceLeaveEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsEmployeeLeaves
        fields = ('id', 'approved_status', 'updated_by')
class LeaveListByEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PmsEmployeeLeaves
        fields = ('id', 'employee', 'leave_type', 'start_date', 'end_date', 'reason',
                  'approved_status')
class AttandanceDeviationByAttandanceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PmsAttandanceDeviation
        fields ='__all__'

#:::::::::::::::::::::: PMS EMPLOYEE CONVEYANCE:::::::::::::::::::::::::::#
class EmployeeConveyanceAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    employee = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsEmployeeConveyance
        fields = ('id', 'project', 'employee', 'eligibility_per_day', 'date', 'from_place', 'to_place', 'vechicle_type',
                  'purpose', 'job_alloted_by', 'approved_status', 'ammount', 'created_by', 'owned_by')

class EmployeeConveyanceEditSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PmsEmployeeConveyance
        fields = ('id', 'approved_status', 'updated_by')


class EmployeeConveyanceListSerializer(serializers.ModelSerializer):
    employee_details = serializers.SerializerMethodField(required=False)
    job_alloted_by_name = serializers.SerializerMethodField(required=False)
    user_project = serializers.SerializerMethodField(required=False)

    def get_employee_details(self, PmsEmployeeConveyance):
        from users.models import TCoreUserDetail
        from users.serializers import UserModuleSerializer, UserSerializer
        user_details = TCoreUserDetail.objects.filter(cu_user=PmsEmployeeConveyance.employee)  # Whatever your query may be
        serializer = UserModuleSerializer(instance=user_details, many=True)
        return serializer.data

    class Meta:
        model = PmsEmployeeConveyance
        fields = ('id', 'project', 'employee', 'eligibility_per_day', 'date', 'from_place', 'to_place', 'vechicle_type',
                  'purpose', 'job_alloted_by', 'approved_status', 'ammount', 'created_by', 'owned_by', 'employee_details',
                  'job_alloted_by_name', 'user_project')

    def get_job_alloted_by_name(self, PmsEmployeeConveyance):
        from users.models import TCoreUserDetail
        from users.serializers import UserModuleSerializer, UserSerializer
        user_details = TCoreUserDetail.objects.filter(cu_user=PmsEmployeeConveyance.job_alloted_by)  # Whatever your query may be.
        serializer = UserModuleSerializer(instance=user_details, many=True)
        name = serializer.data[0]['cu_user']['first_name']+" "+serializer.data[0]['cu_user']['last_name']
        # return serializer.data
        return name

    def get_user_project(self, PmsEmployeeConveyance):
        project = PmsProjects.objects.filter(is_deleted=False,id=PmsEmployeeConveyance.project.id).values('name')
        if project:
            return project[0]['name']
        else:
            None


#:::::::::::::::::::::::::::::::::::PMS EMPLOYEE FOODING:::::::::::::::::::::::::::::::#
class EmployeeFoodingAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsEmployeeFooding
        fields = ('id', 'attandance', 'approved_status', 'ammount', 'created_by', 'owned_by', 'updated_by')

    def create(self, validated_data):
        fooding_data = PmsEmployeeFooding.objects.filter(is_deleted=False,attandance=validated_data['attandance']).update(
            approved_status=validated_data['approved_status'],ammount=Decimal(100.00) if validated_data['approved_status']==2 else Decimal(0.0),
            updated_by=validated_data['created_by']
        )
        if fooding_data:
            return validated_data
        else:
            fooding_data = PmsEmployeeFooding.objects.create(ammount=Decimal(100.00) 
            if validated_data['approved_status']==2 else Decimal(0.0),**validated_data)
            fooding_data.__dict__.pop('_state') if "_state" in fooding_data.__dict__.keys() else fooding_data.__dict__
            return validated_data

class AttandanceAllDetailsListWithFoodingSerializer(serializers.ModelSerializer):
    employee_details = serializers.SerializerMethodField()
    user_project = ProjectDetailsSerializer()
    fooding_details = serializers.SerializerMethodField()

    def get_employee_details(self, PmsAttendance):
        from users.models import TCoreUserDetail
        from users.serializers import UserModuleSerializer, UserSerializer
        user_details = TCoreUserDetail.objects.filter(cu_user=PmsAttendance.employee)  # Whatever your query may be
        serializer = UserModuleSerializer(instance=user_details, many=True)
        return serializer.data

    def get_fooding_details(self, PmsAttendance):
        fooding = PmsEmployeeFooding.objects.filter(is_deleted=False,attandance_id=PmsAttendance.id)
        if fooding:
            fooding[0].__dict__.pop('_state') if "_state" in fooding[0].__dict__.keys() else fooding[0].__dict__
            return fooding[0].__dict__
        else:
            return {}

    class Meta:
        model = PmsAttendance
        fields = ('id', 'user_project', 'date', 'login_time',
                  'logout_time', 'approved_status', 'justification', 'employee_details', 'fooding_details')

'''
    @@ Added By Rupam Hazra on [10-01-2020] line number 864-868 @@
    
'''
class AttendanceUpdateLogOutTimeFailedOnLogoutSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    class Meta:
        model = PmsAttendance
        fields = ('id', 'logout_time', 'updated_by')

'''
    @@ Added By Rupam Hazra on [10-01-2020] line number 876-926 @@
    
'''
class AttandanceLogMultipleByThreadAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    logdetails = serializers.ListField(required=False)
    attendence_log_list= serializers.ListField(required=False)

    class Meta:
        model = PmsAttandanceLog
        fields = ('__all__')
        extra_fields = ('logdetails')
    def create(self, validated_data):
        try:
            logdetails = validated_data.pop('logdetails') if 'logdetails' in validated_data else ""
            print(validated_data)
            owned_by = validated_data.get('owned_by')
            created_by = validated_data.get('created_by')
            '''
                Modified by Rupam Hazra [ remove with transaction.atomic()]
            '''
            attendence_log_list = []
            print("log_data_count",len(logdetails))
            time.sleep(2)
            ServiceThread(logdetails, owned_by, created_by).start()
            return validated_data

        except Exception as e:
            raise e
    
class ServiceThread(threading.Thread):
    def __init__(self, request_data, owned_by, created_by):
        self.request_data = request_data
        self.owned_by = owned_by
        self.created_by = created_by
        threading.Thread.__init__(self)

    def run (self):
        for data in self.request_data:
            #time.sleep(1)
            if data['is_checkout']=='':
                data['is_checkout']= False
            
            log_data, created1 = PmsAttandanceLog.objects.get_or_create(
            created_by=self.created_by,
            owned_by=self.owned_by,
            **data
            )
            # created1 = PmsAttandanceLog.objects.create(
            # created_by=self.created_by,
            # owned_by=self.owned_by,
            # **data
            # )
            print('created1....')
       