from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from pms.models import *
from pms.serializers import *
import time
from multiplelookupfields import MultipleFieldLookupMixin
from rest_framework.views import APIView
from django.conf import settings
from pagination import CSLimitOffestpagination,CSPageNumberPagination
from rest_framework import filters
import calendar
from datetime import datetime,timedelta
from holidays.models import *
import collections
from rest_framework.exceptions import APIException
import pandas as pd
import numpy as np
from django_filters.rest_framework import DjangoFilterBackend
from master.serializers import UserModuleWiseListSerializer
from master.models import TMasterModuleRole
from users.models import TCoreUserDetail , TMasterModuleRole , TCoreRole, TMasterModuleRoleUser
from custom_decorator import *
from rest_framework.parsers import FileUploadParser
import os
from pms.custom_filter import *
from django.db.models import Q

#:::::::::::: ATTENDENCE ::::::::::::::::::::::::::::#
class AttendanceLoginView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsAttendance.objects.all()
    serializer_class = PmsAttendanceAddSerializer

    def post(self, request, *args, **kwargs):
        response = super(AttendanceLoginView, self).post(request,args,kwargs)
        try:
            response.data['msg'] = settings.MSG_SUCCESS
            response.data['request_status'] = 1
        except Exception as e:
            response.data['msg'] = settings.MSG_ERROR
            response.data['request_status'] = 0

        return response
# class AttendanceNewAddView(generics.ListCreateAPIView):
#     permission_classes = [IsAuthenticated]
#     authentication_classes = [TokenAuthentication]
#     queryset = PmsAttendance.objects.all()
#     serializer_class = AttendanceNewAddSerializer


class AttendanceAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsAttendance.objects.all()
    serializer_class = AttendanceAddSerializer

    def post(self, request, *args,**kwargs):
        # print("request",request.user.email)
        # response = super(AttendanceAddView, self).post(request, args, kwargs)
        login_date =datetime.strptime(request.data['login_time'],'%Y-%m-%dT%H:%M:%S').date()
        # print("login_date",login_date)
        attandance_data = custom_filter(
                self,
                PmsAttendance,
                filter_columns={"login_time__date": login_date, "employee__username":request.user.username}, #modified by Rupam
                fetch_columns=['id', 'type', 'employee', 'user_project', 'date', 'login_time', 'login_latitude', 'login_longitude',
                  'login_address','logout_time', 'logout_latitude', 'logout_longitude', 'logout_address', 'approved_status',
                  'justification','created_by', 'owned_by'],
                single_row=True
                          )
        #print("req",request.user)
        # print("login_time_data",attandance_data)

        project_user_mapping = PmsProjectUserMapping.objects.filter(user=request.user, status=True).order_by('-id').values('project')
        print("project_user_mapping",project_user_mapping)
        if project_user_mapping:
            project = project_user_mapping[0]['project']
            request.data['user_project_id'] = project
            #print('project',project)
            project_site = PmsProjects.objects.filter(pk=project).values('id','site_location','site_location__geo_fencing_area')
            #print('project_site_details',project_site)
            if project_site:
                for e_project_site in project_site:
                    geofence = e_project_site['site_location__geo_fencing_area']
                    #print('geofence',geofence)
                    multi_lat_long=PmsSiteProjectSiteManagementMultipleLongLat.objects.filter(
                    project_site_id=e_project_site['site_location']).values()
                    #print('multi_lat_long',multi_lat_long)

            else:
                multi_lat_long = list()
                pass
           
            
        else:
            multi_lat_long = list()
            geofence = ''
            
        if attandance_data:

            # print("attandance_data",attandance_data)
            if attandance_data:
                if attandance_data['logout_time'] is None:
                    # print("attandance_data",attandance_data['logout_time'])
                    return Response({'result':attandance_data,
                                     'request_status': 1,
                                     'msg': settings.MSG_SUCCESS
                                     })
                else:
                    return Response({'request_status': 0,
                                     'msg': "You are not able to login for today"
                                     })
        else:

            attendance_add, created = PmsAttendance.objects.get_or_create(employee=request.user,created_by=request.user,
                                                                          owned_by=request.user,**request.data)
            # print("attendance_add",attendance_add.__dict__)
            attendance_add.__dict__.pop('_state') if "_state" in attendance_add.__dict__.keys() else attendance_add.__dict__
            attendance_add.__dict__['user_project_details'] = multi_lat_long
            attendance_add.__dict__['geo_fencing_area'] = geofence

            return Response({'result':attendance_add.__dict__,
                             'request_status': 1,
                             'msg': settings.MSG_SUCCESS
                             })
# class AttendanceOfflineAddView(generics.ListCreateAPIView):
#     permission_classes = [IsAuthenticated]
#     authentication_classes = [TokenAuthentication]
#     queryset = PmsAttendance.objects.all()
#     serializer_class = AttendanceOfflineAddSerializer

#     def post(self, request, *args,**kwargs):
#         # print("request",request.user.email)
#         # response = super(AttendanceAddView, self).post(request, args, kwargs)
#         login_date =datetime.strptime(request.data['login_time'],'%Y-%m-%dT%H:%M:%S').date()
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

#         project_user_mapping = PmsProjectUserMapping.objects.filter(user=request.user, status=True).order_by('-id').values('project')
#         # print("project_user_mapping",project_user_mapping)
#         if project_user_mapping:
#             project = project_user_mapping[0]['project']
#             request.data['user_project_id'] = project

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
#             return Response({'result':attendance_add.__dict__,
#                              'request_status': 1,
#                              'msg': settings.MSG_SUCCESS
#                              })



class AttendanceListByEmployeeView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    # pagination_class = CSPageNumberPagination
    queryset = PmsAttendance.objects.all()
    serializer_class = AttendanceListSerializer
    filter_backends = (filters.OrderingFilter, filters.SearchFilter,)
    search_fields = ('date', 'employee', 'employee__username', 'login_time', 'logout_time', 'type')
    ordering = ('-created_at',)

    def get_queryset(self):
        employee_id = self.kwargs["employee_id"]
        year = int(self.request.query_params['year']) if 'year' in self.request.query_params else int(
            datetime.today().date().strftime("%Y"))
        month = int(self.request.query_params['month']) if 'month' in self.request.query_params else int(
            datetime.today().date().strftime("%m"))
        return self.queryset.filter(employee_id= employee_id, created_at__year = year, created_at__month=month,is_deleted=False)

    def get_holidays_list(self):
        holidays_list = HolidaysList.objects.filter(status=True)
        holidays_dict = {}
        for data in holidays_list:
            dt_str = data.holiday_date.strftime('%Y-%m-%d')
            holidays_dict[dt_str] = data.holiday_name
        return holidays_dict

    def list(self, request, *args, **kwargs):
        try:
            holidays_dict = self.get_holidays_list()
            # print("holidays_dict: ", holidays_dict)
            current_date = datetime.today().date()
            year = int(self.request.query_params['year']) if 'year' in self.request.query_params else int(current_date.strftime("%Y"))
            month = int(self.request.query_params['month']) if 'month' in self.request.query_params else int(current_date.strftime("%m"))

            response = super(AttendanceListByEmployeeView, self).list(request, args, kwargs)
            results_data_listofdict = response.data
            # print("results_data_listofdict, ", results_data_listofdict)
            month_date_list = self.get_month_dates(year, month)
            absent_date_list = []
            present_date_list = [oddata['date'][0:10] for oddata in results_data_listofdict]
            # print("present_date_list>>>>>", present_date_list)

            for date in month_date_list:
                if date not in present_date_list:
                    # print("date.....>>>",date)
                    present_date = datetime.strptime(date, '%Y-%m-%d').date()
                    rest_day = current_date - present_date
                    if rest_day.days >= 0:
                        absent_date_list.append(date)

            for od in results_data_listofdict:
                # print("od['id']",od['id'])
                deviation_details = PmsAttandanceDeviation.objects.filter(attandance=od['id'])
                # print("deviation",deviation_details)
                login_time = PmsAttendance.objects.only('login_time').get(id=od['id']).login_time
                logout_time = PmsAttendance.objects.only('logout_time').get(id=od['id']).logout_time
                total_time = timedelta(hours=00, minutes=00, seconds=00)

                if login_time and logout_time:
                    login_time_timedelta = timedelta(hours=login_time.hour, minutes=login_time.minute,
                                                     seconds=login_time.second)
                    logout_time_timedelta = timedelta(hours=logout_time.hour, minutes=logout_time.minute,
                                                      seconds=logout_time.second)
                    total_time = logout_time_timedelta - login_time_timedelta
                # print("total_time", total_time)

                total_deviation_time = timedelta(hours=00, minutes=00, seconds=00)

                if deviation_details:
                    for deviation in deviation_details:
                        deviation_time = datetime.strptime(deviation.deviation_time, "%H:%M:%S").time()
                        deviation_time_timedelta= timedelta(hours=deviation_time.hour, minutes=deviation_time.minute, seconds=deviation_time.second)
                        total_deviation_time = total_deviation_time + deviation_time_timedelta
                    # print("total_deviation_time",str(total_deviation_time))
                    od['is_deviation'] = 1
                else:
                    od['is_deviation'] = 0

                working_time = total_time - total_deviation_time
                # print("working_time", str(working_time))
                # print("working_time", working_time.seconds)
                if working_time.seconds > 36000:
                    od['is_ten_hrs'] = 1
                else:
                    od['is_ten_hrs'] = 0


                week_day = datetime.strptime(od['date'], '%Y-%m-%dT%H:%M:%S').strftime('%A')
                od['date'] = datetime.strptime(od['date'], '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%d')
                od['week_day'] = week_day
                od['present'] = 1
                od['holiday'] = 0

            for absent_date in absent_date_list:
                ab_week_day = datetime.strptime(absent_date, '%Y-%m-%d').strftime('%A')
                data_dict = {
                    "type": 1,
                    "employee": self.kwargs["employee_id"],
                    "user_project": "",
                    "date": absent_date,
                    "login_time": "",
                    "logout_time": "",
                    "approved_status": 0,
                    "justification": "Auto genareted absent",
                    "week_day": ab_week_day,
                    "present": 0,
                    "holiday": 0
                }
                if absent_date in holidays_dict.keys():
                    data_dict["holiday"] = 1
                    data_dict["justification"] = holidays_dict[absent_date]



                results_data_listofdict.append(data_dict)

            response_data_dict = collections.OrderedDict()
            response_data_dict['count'] = len(results_data_listofdict)
            response_data_dict['results'] = results_data_listofdict
            response_data_dict['request_status'] = 1
            response_data_dict['msg'] = settings.MSG_SUCCESS
            # print(response_data_dict)
            return Response(self.list_synchronization(response_data_dict))
        except Exception as e:
            raise APIException({'request_status': 0, 'msg': e})

    def list_synchronization(self, list_data: list)-> list:
        data = pd.DataFrame(list_data["results"])
        data = data.replace(np.nan, 0, regex=True)
        data.sort_values("date", axis = 0, ascending = True, inplace = True,)
        col_list = data.columns.values
        row_list = data.values.tolist()
        total_result = list()
        for row in row_list:
            data_dict = dict(zip(col_list,row))
            total_result.append(data_dict)
        list_data["results"] = total_result
        return list_data


    def get_month_dates(self, year, month)-> list:
        date_list = []
        cal = calendar.Calendar()
        for cal_date in cal.itermonthdates(year, month):
            if cal_date.month == month:
                cal_d = cal_date.strftime('%Y-%m-%d')

                date_list.append(cal_d)
        return date_list
class AttendanceApprovalList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    pagination_class = CSPageNumberPagination
    queryset = PmsAttendance.objects.filter(approved_status=1)
    serializer_class = AttendanceApprovalListSerializer

    def get_queryset(self):
        user_name = self.request.query_params.get('user_name', None)

        if user_name:
            if '@' in user_name:
                queryset = self.queryset.filter(is_deleted=False, employee__email__icontains=user_name).order_by('-id')
                return queryset
            else:
                # print("user_name")
                name = user_name.split(" ")
                # print("name", name)
                if name:
                    queryset_all = PmsAttendance.objects.none()
                    # print("len(name)",len(name))
                    for i in name:
                        queryset = self.queryset.filter(Q(is_deleted=False) & Q(approved_status=1) & Q(employee__first_name__icontains=i) |
                                                        Q(employee__last_name__icontains=i)).order_by('-id')
                        queryset_all = (queryset_all|queryset)
                    return queryset_all
        else:
            queryset = self.queryset.filter(is_deleted=False,approved_status=1).order_by('-id')
            return queryset
        
    def list(self, request, *args, **kwargs):
        response = super(AttendanceApprovalList, self).list(request, args, kwargs)
        response.data['request_status'] = 0
        response.data['msg'] = settings.MSG_ERROR
        response.data['per_page_count'] = len(response.data['results'])
        if response.data['results']:
            response.data['request_status'] = 1
            response.data['msg'] = settings.MSG_SUCCESS
        return response
class AttendanceEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsAttendance.objects.filter(is_deleted=False)
    serializer_class = AttendanceSerializer

    def put(self, request,* args, **kwargs):
        response = super(AttendanceEditView, self).put(request, args, kwargs)
        print('request: ', request.data)
        data_dict = {}
        data_dict['result'] = request.data
        if response.data:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_SUCCESS
        # elif len(response.data) == 0:
        #     data_dict['request_status'] = 1
        #     data_dict['msg'] = settings.MSG_NO_DATA
        else:
            data_dict['request_status'] = 0
            data_dict['msg'] = settings.MSG_ERROR

        response.data = data_dict
        return response
class AttendanceLogOutView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsAttendance.objects.filter(is_deleted=False)
    serializer_class = AttendanceLogOutSerializer

    def put(self, request,* args, **kwargs):
        response = super(AttendanceLogOutView, self).put(request, args, kwargs)
        # print('request: ', request.data)
        data_dict = {}
        data_dict['result'] = request.data
        if response.data:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_SUCCESS
        else:
            data_dict['request_status'] = 0
            data_dict['msg'] = settings.MSG_ERROR

        response.data = data_dict
        return response

class AttandanceAllDetailsListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsAttendance.objects.all()
    serializer_class = AttandanceALLDetailsListSerializer
    pagination_class = CSPageNumberPagination

    def get_queryset(self):
        # from django.db.models import Q
        filter = {}
        user_project = self.request.query_params.get('user_project', None)
        employee = self.request.query_params.get('employee', None)
        user_designation = self.request.query_params.get('user_designation', None)

        user_first_name = self.request.query_params.get('user_first_name', None)
        user_last_name = self.request.query_params.get('user_last_name', None)
        user_name = self.request.query_params.get('user_name', None)
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        attendance = self.request.query_params.get('attendance', None)
        approved_status = self.request.query_params.get('approved_status', None)
        field_name=self.request.query_params.get('field_name',None)
        order_by = self.request.query_params.get('order_by', None)

        if field_name != "" and order_by != "":
            if field_name == 'sort_first_name' and order_by == 'asc':
                queryset = self.queryset.filter(is_deleted=False).order_by('employee__first_name')
                return queryset
            elif field_name == 'sort_first_name' and order_by == 'desc':
                queryset = self.queryset.filter(is_deleted=False).order_by('-employee__first_name')
                return queryset
            elif field_name == 'sort_created_at' and order_by == 'asc':
                queryset =  self.queryset.filter(is_deleted=False).order_by('created_at')
                return queryset
            elif field_name == 'sort_created_at' and order_by == 'desc':
                queryset = self.queryset.filter(is_deleted=False).order_by('-created_at')
                return queryset
            elif field_name == 'sort_user_project' and order_by == 'asc':
                queryset = self.queryset.filter(is_deleted=False).order_by('user_project')
                return queryset
            elif field_name == 'sort_user_project' and order_by == 'desc':
                queryset = self.queryset.filter(is_deleted=False).order_by('-user_project')
                return queryset

        if user_first_name:
            filter['employee__first_name__icontains'] = user_first_name
        if user_last_name:
            filter['employee__last_name__icontains'] = user_last_name

        if start_date and end_date:
            start_object = datetime.strptime(start_date, '%Y-%m-%d')
            end_object = datetime.strptime(end_date, '%Y-%m-%d')
            filter['created_at__range']=(start_object, end_object)
        if user_project:
            filter['user_project__in']= user_project.split(',')

        if user_designation:
            filter['employee__mmr_user']= user_designation

        if attendance:
            filter['id'] = attendance

        if employee:
            filter['employee'] = employee

        if approved_status:
            filter['approved_status'] = approved_status

        if filter:
            queryset = self.queryset.filter(is_deleted=False,**filter).order_by('-id')
            print("queryset",queryset.query)
            return queryset
        elif user_name:
            if '@' in user_name:
                queryset = self.queryset.filter(is_deleted=False, employee__email__icontains=user_name).order_by('-id')
                return queryset
            else:
                print("user_name")
                name = user_name.split(" ")
                print("name", name)
                if name:
                    queryset_all = PmsAttendance.objects.none()
                    print("len(name)",len(name))
                    for i in name:
                        queryset = self.queryset.filter(Q(is_deleted=False) & Q(employee__first_name__icontains=i) |
                                                        Q(employee__last_name__icontains=i)).order_by('-id')
                        queryset_all = (queryset_all|queryset)
                    return queryset_all
        else:
            queryset = self.queryset.filter(is_deleted=False).order_by('-id')
            return queryset

    def list_synchronization(self, list_data: list)-> list:
        data = pd.DataFrame(list_data)
        data = data.replace(np.nan, 0, regex=True)
        data.sort_values("date", axis = 0, ascending = True, inplace = True,)
        col_list = data.columns.values
        row_list = data.values.tolist()
        total_result = list()
        for row in row_list:
            data_dict = dict(zip(col_list,row))
            total_result.append(data_dict)
        list_data = total_result
        return list_data

    def list(self, request, *args, **kwargs):
        response = super(AttandanceAllDetailsListView, self).list(request,args,kwargs)
        response.data['request_status'] = 0
        response.data['msg'] = settings.MSG_ERROR

        if response.data['results']:
            for data in response.data['results']:
                if data['user_project']:
                    print("data_id",data['user_project']['site_location']['id'])
                    long_lat_data=PmsSiteProjectSiteManagementMultipleLongLat.objects.filter(project_site=data['user_project']['site_location']['id']).values('latitude','longitude')
                    data['user_project']['long_lat_details']=long_lat_data
                    print("data['user_project']",data['user_project'])
                # if not data['user_project']:
                else:
                    data['user_project'] = {}
            response.data['results'] = self.list_synchronization(list(response.data['results']))
            response.data['request_status'] = 1
            response.data['msg'] = settings.MSG_SUCCESS
        return response

class AttandanceAllDetailsListByPermissonView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsAttendance.objects.order_by('-date')
    serializer_class = AttandanceALLDetailsListByPermissonSerializer
    pagination_class = CSPageNumberPagination

    # For permisson lavel check modified by @Rupam
    def get_queryset(self):
        
        #print('sdsddsddd')
        module_id = self.request.GET.get('module_id', None)
        #print('module_id',type(module_id))
        if module_id:
            login_user_details = self.request.user
            #print('login_user_details',login_user_details.id)
            if login_user_details.is_superuser == False:

                '''
                    Added By Rupam Hazra 27.01.2020 from 563-660 for user type = module admin
                '''
                which_type_of_user = TMasterModuleRoleUser.objects.filter(
                    mmr_module_id= module_id,
                    mmr_user=login_user_details,
                    mmr_is_deleted=False
                ).values_list('mmr_type',flat=True)[0]

                # print('which_type_of_user',which_type_of_user,type(which_type_of_user))
                # time.sleep(10)

                if which_type_of_user == 2: #[module admin]
                    queryset = PmsAttendance.objects.filter(is_deleted=False)
                    if queryset:
                        print('queryset1111...else', queryset)
                        filter = {}
                        user_project = self.request.query_params.get('user_project', None)
                        employee = self.request.query_params.get('employee', None)
                        user_designation = self.request.query_params.get('user_designation', None)
                        user_first_name = self.request.query_params.get('user_first_name', None)
                        user_last_name = self.request.query_params.get('user_last_name', None)
                        user_name = self.request.query_params.get('user_name', None)
                        start_date = self.request.query_params.get('start_date', None)
                        end_date = self.request.query_params.get('end_date', None)
                        attendance = self.request.query_params.get('attendance', None)
                        approved_status = self.request.query_params.get('approved_status', None)
                        field_name = self.request.query_params.get('field_name', None)
                        order_by = self.request.query_params.get('order_by', None)

                        if field_name != "" and order_by != "":
                            if field_name == 'sort_first_name' and order_by == 'asc':
                                queryset = queryset.filter(is_deleted=False).order_by('employee__first_name')
                                return queryset
                            elif field_name == 'sort_first_name' and order_by == 'desc':
                                queryset = queryset.filter(is_deleted=False).order_by('-employee__first_name')
                                return queryset
                            elif field_name == 'sort_created_at' and order_by == 'asc':
                                queryset = queryset.filter(is_deleted=False).order_by('created_at')
                                return queryset
                            elif field_name == 'sort_created_at' and order_by == 'desc':
                                queryset = queryset.filter(is_deleted=False).order_by('-created_at')
                                return queryset
                            elif field_name == 'sort_user_project' and order_by == 'asc':
                                queryset = queryset.filter(is_deleted=False).order_by('user_project')
                                return queryset
                            elif field_name == 'sort_user_project' and order_by == 'desc':
                                queryset = queryset.filter(is_deleted=False).order_by('-user_project')
                                return queryset

                        if user_first_name:
                            filter['employee__first_name__icontains'] = user_first_name
                        if user_last_name:
                            filter['employee__last_name__icontains'] = user_last_name

                        if start_date and end_date:
                            end_date = end_date + 'T23:59:59'
                            start_object = datetime.strptime(start_date, '%Y-%m-%d')
                            end_object = datetime.strptime(end_date, '%Y-%m-%dT%H:%M:%S')
                            filter['created_at__range'] = (start_object, end_object)
                        if user_project:
                            filter['user_project__in'] = user_project.split(',')

                        if user_designation:
                            filter['employee__mmr_user'] = user_designation

                        if attendance:
                            filter['id'] = attendance

                        if employee:
                            filter['employee'] = employee

                        if approved_status:
                            filter['approved_status'] = approved_status

                        if filter:
                            print("filter",filter)
                            queryset = queryset.filter(is_deleted=False, **filter).order_by('-date')
                            # print("queryset",queryset.query)
                            return queryset
                        elif user_name:
                            if '@' in user_name:
                                queryset = queryset.filter(is_deleted=False, employee__email__icontains=user_name).order_by(
                                    '-id')
                                return queryset
                            else:
                                # print("user_name")
                                name = user_name.split(" ")
                                # print("name", name)
                                if name:
                                    queryset_all = PmsAttendance.objects.none()
                                    # print("len(name)",len(name))
                                    for i in name:
                                        queryset = queryset.filter(
                                            Q(is_deleted=False) & Q(employee__first_name__icontains=i) |
                                            Q(employee__last_name__icontains=i)).order_by('-date')
                                        queryset_all = (queryset_all | queryset)
                                    return queryset_all
                        else:
                            queryset = queryset.filter(is_deleted=False).order_by('-date')
                            return queryset
                else:
                    users_list_under_the_login_user = list()
                    for a in TCoreUserDetail.objects.raw(
                        'SELECT * FROM t_core_user_details AS tcud'+
                        ' JOIN t_master_module_role_user AS tmmru ON tmmru.mmr_user_id=tcud.cu_user_id'+
                        ' WHERE tmmru.mmr_module_id=%s'+
                        ' AND tcud.reporting_head_id=%s'+' AND tcud.cu_is_deleted=0',[module_id,login_user_details.id]
                        ):
                        users_list_under_the_login_user.append(a.cu_user_id)
                    
                    #print('users_list_under_the_login_user',users_list_under_the_login_user)
                    if users_list_under_the_login_user:
                        queryset = PmsAttendance.objects.filter(
                                    employee_id__in=users_list_under_the_login_user,
                                    is_deleted = False
                                    )
                        #print('attedence_details',queryset)
                        if queryset:
                            filter = {}
                            user_project = self.request.query_params.get('user_project', None)
                            employee = self.request.query_params.get('employee', None)
                            user_designation = self.request.query_params.get('user_designation', None)
                            user_first_name = self.request.query_params.get('user_first_name', None)
                            user_last_name = self.request.query_params.get('user_last_name', None)
                            user_name = self.request.query_params.get('user_name', None)
                            start_date = self.request.query_params.get('start_date', None)
                            end_date = self.request.query_params.get('end_date', None)
                            attendance = self.request.query_params.get('attendance', None)
                            approved_status = self.request.query_params.get('approved_status', None)
                            field_name=self.request.query_params.get('field_name',None)
                            order_by = self.request.query_params.get('order_by', None)

                            if field_name != "" and order_by != "":
                                if field_name == 'sort_first_name' and order_by == 'asc':
                                    queryset = queryset.filter(is_deleted=False).order_by('employee__first_name')
                                    return queryset
                                elif field_name == 'sort_first_name' and order_by == 'desc':
                                    queryset = queryset.filter(is_deleted=False).order_by('-employee__first_name')
                                    return queryset
                                elif field_name == 'sort_created_at' and order_by == 'asc':
                                    queryset = queryset.filter(is_deleted=False).order_by('created_at')
                                    return queryset
                                elif field_name == 'sort_created_at' and order_by == 'desc':
                                    queryset = queryset.filter(is_deleted=False).order_by('-created_at')
                                    return queryset
                                elif field_name == 'sort_user_project' and order_by == 'asc':
                                    queryset = queryset.filter(is_deleted=False).order_by('user_project')
                                    return queryset
                                elif field_name == 'sort_user_project' and order_by == 'desc':
                                    queryset = queryset.filter(is_deleted=False).order_by('-user_project')
                                    return queryset


                            if user_first_name:
                                filter['employee__first_name__icontains'] = user_first_name
                            if user_last_name:
                                filter['employee__last_name__icontains'] = user_last_name

                            if start_date and end_date:
                                end_date = end_date+'T23:59:59'
                                start_object = datetime.strptime(start_date, '%Y-%m-%d')
                                end_object = datetime.strptime(end_date, '%Y-%m-%dT%H:%M:%S')
                                filter['created_at__range']=(start_object, end_object)
                            if user_project:
                                filter['user_project__in']= user_project.split(',')

                            if user_designation:
                                filter['employee__mmr_user']= user_designation

                            if attendance:
                                filter['id'] = attendance

                            if employee:
                                filter['employee'] = employee

                            if approved_status:
                                filter['approved_status'] = approved_status

                            if filter:
                                queryset = queryset.filter(is_deleted=False,**filter).order_by('-date')
                                #print("queryset",queryset.query)
                                return queryset
                            elif user_name:
                                if '@' in user_name:
                                    queryset = queryset.filter(is_deleted=False, employee__email__icontains=user_name).order_by('-date')
                                    return queryset
                                else:
                                    #print("user_name")
                                    name = user_name.split(" ")
                                    #print("name", name)
                                    if name:
                                        queryset_all = PmsAttendance.objects.none()
                                        #print("len(name)",len(name))
                                        for i in name:
                                            queryset = queryset.filter(Q(is_deleted=False) & Q(employee__first_name__icontains=i) |
                                                                            Q(employee__last_name__icontains=i)).order_by('-date')
                                            queryset_all = (queryset_all|queryset)
                                        return queryset_all
                            else:
                                queryset = queryset.filter(is_deleted=False).order_by('-date')
                                return queryset
                        else:
                            #print('fgdfggfdgdffggf')
                            return queryset
                    else:
                        return list()
            else:
                queryset = PmsAttendance.objects.filter(is_deleted=False)
                if queryset:
                    print('queryset1111...else', queryset)
                    filter = {}
                    user_project = self.request.query_params.get('user_project', None)
                    employee = self.request.query_params.get('employee', None)
                    user_designation = self.request.query_params.get('user_designation', None)
                    user_first_name = self.request.query_params.get('user_first_name', None)
                    user_last_name = self.request.query_params.get('user_last_name', None)
                    user_name = self.request.query_params.get('user_name', None)
                    start_date = self.request.query_params.get('start_date', None)
                    end_date = self.request.query_params.get('end_date', None)
                    attendance = self.request.query_params.get('attendance', None)
                    approved_status = self.request.query_params.get('approved_status', None)
                    field_name = self.request.query_params.get('field_name', None)
                    order_by = self.request.query_params.get('order_by', None)

                    if field_name != "" and order_by != "":
                        if field_name == 'sort_first_name' and order_by == 'asc':
                            queryset = queryset.filter(is_deleted=False).order_by('employee__first_name')
                            return queryset
                        elif field_name == 'sort_first_name' and order_by == 'desc':
                            queryset = queryset.filter(is_deleted=False).order_by('-employee__first_name')
                            return queryset
                        elif field_name == 'sort_created_at' and order_by == 'asc':
                            queryset = queryset.filter(is_deleted=False).order_by('created_at')
                            return queryset
                        elif field_name == 'sort_created_at' and order_by == 'desc':
                            queryset = queryset.filter(is_deleted=False).order_by('-created_at')
                            return queryset
                        elif field_name == 'sort_user_project' and order_by == 'asc':
                            queryset = queryset.filter(is_deleted=False).order_by('user_project')
                            return queryset
                        elif field_name == 'sort_user_project' and order_by == 'desc':
                            queryset = queryset.filter(is_deleted=False).order_by('-user_project')
                            return queryset

                    if user_first_name:
                        filter['employee__first_name__icontains'] = user_first_name
                    if user_last_name:
                        filter['employee__last_name__icontains'] = user_last_name

                    if start_date and end_date:
                        end_date = end_date + 'T23:59:59'
                        start_object = datetime.strptime(start_date, '%Y-%m-%d')
                        end_object = datetime.strptime(end_date, '%Y-%m-%dT%H:%M:%S')
                        filter['created_at__range'] = (start_object, end_object)
                    if user_project:
                        filter['user_project__in'] = user_project.split(',')

                    if user_designation:
                        filter['employee__mmr_user'] = user_designation

                    if attendance:
                        filter['id'] = attendance

                    if employee:
                        filter['employee'] = employee

                    if approved_status:
                        filter['approved_status'] = approved_status

                    if filter:
                        print("filter",filter)
                        queryset = queryset.filter(is_deleted=False, **filter).order_by('-date')
                        # print("queryset",queryset.query)
                        return queryset
                    elif user_name:
                        if '@' in user_name:
                            queryset = queryset.filter(is_deleted=False, employee__email__icontains=user_name).order_by(
                                '-id')
                            return queryset
                        else:
                            # print("user_name")
                            name = user_name.split(" ")
                            # print("name", name)
                            if name:
                                queryset_all = PmsAttendance.objects.none()
                                # print("len(name)",len(name))
                                for i in name:
                                    queryset = queryset.filter(
                                        Q(is_deleted=False) & Q(employee__first_name__icontains=i) |
                                        Q(employee__last_name__icontains=i)).order_by('-date')
                                    queryset_all = (queryset_all | queryset)
                                return queryset_all
                    else:
                        queryset = queryset.filter(is_deleted=False).order_by('-date')
                        return queryset

        else:
            return self.queryset
    
    # End For permisson lavel check modified by @Rupam
    
    def list_synchronization(self, list_data: list)-> list:
        data = pd.DataFrame(list_data)
        data = data.replace(np.nan, 0, regex=True)
        data.sort_values("date", axis = 0, ascending = False, inplace = True,)
        col_list = data.columns.values
        row_list = data.values.tolist()
        total_result = list()
        for row in row_list:
            data_dict = dict(zip(col_list,row))
            total_result.append(data_dict)
        list_data = total_result
        return list_data

    def list(self, request, *args, **kwargs):
        response = super(AttandanceAllDetailsListByPermissonView, self).list(request,args,kwargs)
        response.data['request_status'] = 0
        response.data['msg'] = settings.MSG_ERROR

        if response.data['results']:
            for data in response.data['results']:
                if not data['user_project']:
                    data['user_project'] = {}
            response.data['results'] = self.list_synchronization(list(response.data['results']))
            response.data['request_status'] = 1
            response.data['msg'] = settings.MSG_SUCCESS
        return response

class AttandanceListWithOnlyDeviationByPermissonView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsAttendance.objects.filter(is_deleted=False)#,id__in=
    serializer_class = AttandanceListWithOnlyDeviationByPermissonSerializer
    pagination_class = CSPageNumberPagination
    # For permisson lavel check modified by @Rupam
    def get_queryset(self):
        module_id = self.request.GET.get('module_id', None)
        self.queryset = self.queryset.filter(is_deleted=False,id__in=PmsAttandanceDeviation.objects.all().
                                             values_list('attandance'))
        #print("queryset111",self.queryset)
        if module_id:
            login_user_details = self.request.user
            print('login_user_details',login_user_details.is_superuser)

            if login_user_details.is_superuser == False:

                '''
                    Added By Rupam Hazra 27.01.2020 from 563-660 for user type = module admin
                '''
                which_type_of_user = TMasterModuleRoleUser.objects.filter(
                    mmr_module_id= module_id,
                    mmr_user=login_user_details,
                    mmr_is_deleted=False
                ).values_list('mmr_type',flat=True)[0]

                if which_type_of_user == 2: #[module admin]
                    queryset = self.queryset
                    if queryset:
                        filter = {}
                        user_project = self.request.query_params.get('user_project', None)
                        employee = self.request.query_params.get('employee', None)
                        user_designation = self.request.query_params.get('user_designation', None)
                        user_first_name = self.request.query_params.get('user_first_name', None)
                        user_last_name = self.request.query_params.get('user_last_name', None)
                        user_name = self.request.query_params.get('user_name', None)
                        start_date = self.request.query_params.get('start_date', None)
                        end_date = self.request.query_params.get('end_date', None)
                        attendance = self.request.query_params.get('attendance', None)
                        approved_status = self.request.query_params.get('approved_status', None)
                        field_name = self.request.query_params.get('field_name', None)
                        order_by = self.request.query_params.get('order_by', None)

                        if field_name != "" and order_by != "":
                            if field_name == 'sort_first_name' and order_by == 'asc':
                                queryset = queryset.filter(is_deleted=False).order_by('employee__first_name')
                                return queryset
                            elif field_name == 'sort_first_name' and order_by == 'desc':
                                queryset = queryset.filter(is_deleted=False).order_by('-employee__first_name')
                                return queryset
                            elif field_name == 'sort_created_at' and order_by == 'asc':
                                queryset = queryset.filter(is_deleted=False).order_by('created_at')
                                return queryset
                            elif field_name == 'sort_created_at' and order_by == 'desc':
                                queryset = queryset.filter(is_deleted=False).order_by('-created_at')
                                return queryset
                            elif field_name == 'sort_user_project' and order_by == 'asc':
                                queryset = queryset.filter(is_deleted=False).order_by('user_project')
                                return queryset
                            elif field_name == 'sort_user_project' and order_by == 'desc':
                                queryset = queryset.filter(is_deleted=False).order_by('-user_project')
                                return queryset

                        if user_first_name:
                            filter['employee__first_name__icontains'] = user_first_name
                        if user_last_name:
                            filter['employee__last_name__icontains'] = user_last_name

                        if start_date and end_date:
                            end_date = end_date + 'T23:59:59'
                            start_object = datetime.strptime(start_date, '%Y-%m-%d')
                            end_object = datetime.strptime(end_date, '%Y-%m-%dT%H:%M:%S')
                            filter['created_at__range'] = (start_object, end_object)
                        if user_project:
                            filter['user_project__in'] = user_project.split(',')

                        if user_designation:
                            filter['employee__mmr_user'] = user_designation

                        if attendance:
                            filter['id'] = attendance

                        if employee:
                            filter['employee'] = employee

                        if approved_status:
                            filter['approved_status'] = approved_status

                        if filter:
                            queryset = queryset.filter(is_deleted=False, **filter).order_by('-id')
                            # print("queryset",queryset.query)
                            return queryset
                        elif user_name:
                            if '@' in user_name:
                                queryset = queryset.filter(is_deleted=False, employee__email__icontains=user_name).order_by(
                                    '-id')
                                return queryset
                            else:
                                # print("user_name")
                                name = user_name.split(" ")
                                # print("name", name)
                                if name:
                                    queryset_all = PmsAttendance.objects.none()
                                    # print("len(name)",len(name))
                                    for i in name:
                                        queryset = queryset.filter(
                                            Q(is_deleted=False) & Q(employee__first_name__icontains=i) |
                                            Q(employee__last_name__icontains=i)).order_by('-id')
                                        queryset_all = (queryset_all | queryset)
                                    return queryset_all
                        else:
                            queryset = queryset.filter(is_deleted=False).order_by('-id')
                            return queryset
                    else:
                        return self.queryset
                else:
                    users_list_under_the_login_user = list()
                    for a in TCoreUserDetail.objects.raw(
                        'SELECT * FROM t_core_user_details AS tcud'+
                        ' JOIN t_master_module_role_user AS tmmru ON tmmru.mmr_user_id=tcud.cu_user_id'+
                        ' WHERE tmmru.mmr_module_id=%s'+
                        ' AND tcud.reporting_head_id=%s'+' AND tcud.cu_is_deleted=0',[module_id,login_user_details.id]
                        ):
                        users_list_under_the_login_user.append(a.cu_user_id)
                    
                    print('users_list_under_the_login_user',users_list_under_the_login_user)
                    if users_list_under_the_login_user:
                        queryset = self.queryset.filter(
                                    employee_id__in=users_list_under_the_login_user,
                                    is_deleted = False
                                    )
                        print('queryset',queryset)
                        if queryset:
                            filter = {}
                            user_project = self.request.query_params.get('user_project', None)
                            employee = self.request.query_params.get('employee', None)
                            user_designation = self.request.query_params.get('user_designation', None)
                            user_first_name = self.request.query_params.get('user_first_name', None)
                            user_last_name = self.request.query_params.get('user_last_name', None)
                            user_name = self.request.query_params.get('user_name', None)
                            start_date = self.request.query_params.get('start_date', None)
                            end_date = self.request.query_params.get('end_date', None)
                            attendance = self.request.query_params.get('attendance', None)
                            approved_status = self.request.query_params.get('approved_status', None)
                            field_name=self.request.query_params.get('field_name',None)
                            order_by = self.request.query_params.get('order_by', None)

                            if field_name != "" and order_by != "":
                                if field_name == 'sort_first_name' and order_by == 'asc':
                                    queryset = queryset.filter(is_deleted=False).order_by('employee__first_name')
                                    return queryset
                                elif field_name == 'sort_first_name' and order_by == 'desc':
                                    queryset = queryset.filter(is_deleted=False).order_by('-employee__first_name')
                                    return queryset
                                elif field_name == 'sort_created_at' and order_by == 'asc':
                                    queryset =  queryset.filter(is_deleted=False).order_by('created_at')
                                    return queryset
                                elif field_name == 'sort_created_at' and order_by == 'desc':
                                    queryset = queryset.filter(is_deleted=False).order_by('-created_at')
                                    return queryset
                                elif field_name == 'sort_user_project' and order_by == 'asc':
                                    queryset = queryset.filter(is_deleted=False).order_by('user_project')
                                    return queryset
                                elif field_name == 'sort_user_project' and order_by == 'desc':
                                    queryset = queryset.filter(is_deleted=False).order_by('-user_project')
                                    return queryset
                            if user_first_name:
                                filter['employee__first_name__icontains'] = user_first_name
                            if user_last_name:
                                filter['employee__last_name__icontains'] = user_last_name
                            if start_date and end_date:
                                end_date = end_date+'T23:59:59'
                                start_object = datetime.strptime(start_date, '%Y-%m-%d')
                                end_object = datetime.strptime(end_date, '%Y-%m-%dT%H:%M:%S')
                                filter['created_at__range']=(start_object, end_object)
                            if user_project:
                                filter['user_project__in']= user_project.split(',')
                            if user_designation:
                                filter['employee__mmr_user']= user_designation
                            if attendance:
                                filter['id'] = attendance
                            if employee:
                                filter['employee'] = employee
                            if approved_status:
                                filter['approved_status'] = approved_status
                            if filter:
                                queryset = queryset.filter(is_deleted=False,**filter).order_by('-id')
                                # print("queryset",queryset.query)
                                return queryset
                            elif user_name:
                                if '@' in user_name:
                                    queryset = queryset.filter(is_deleted=False, employee__email__icontains=user_name).order_by('-id')
                                    return queryset
                                else:
                                    #print("user_name")
                                    name = user_name.split(" ")
                                    #print("name", name)
                                    if name:
                                        queryset_all = PmsAttendance.objects.none()
                                        #print("len(name)",len(name))
                                        for i in name:
                                            queryset = queryset.filter(Q(is_deleted=False) & Q(employee__first_name__icontains=i) |
                                                                            Q(employee__last_name__icontains=i)).order_by('-id')
                                            queryset_all = (queryset_all|queryset)
                                        return queryset_all
                            else:
                                queryset = queryset.filter(is_deleted=False).order_by('-id')
                                return queryset
                        else:
                            return queryset
                    else:
                        return list()  
            else:
                #+++++++++++++
                queryset = self.queryset
                if queryset:
                    filter = {}
                    user_project = self.request.query_params.get('user_project', None)
                    employee = self.request.query_params.get('employee', None)
                    user_designation = self.request.query_params.get('user_designation', None)
                    user_first_name = self.request.query_params.get('user_first_name', None)
                    user_last_name = self.request.query_params.get('user_last_name', None)
                    user_name = self.request.query_params.get('user_name', None)
                    start_date = self.request.query_params.get('start_date', None)
                    end_date = self.request.query_params.get('end_date', None)
                    attendance = self.request.query_params.get('attendance', None)
                    approved_status = self.request.query_params.get('approved_status', None)
                    field_name = self.request.query_params.get('field_name', None)
                    order_by = self.request.query_params.get('order_by', None)

                    if field_name != "" and order_by != "":
                        if field_name == 'sort_first_name' and order_by == 'asc':
                            queryset = queryset.filter(is_deleted=False).order_by('employee__first_name')
                            return queryset
                        elif field_name == 'sort_first_name' and order_by == 'desc':
                            queryset = queryset.filter(is_deleted=False).order_by('-employee__first_name')
                            return queryset
                        elif field_name == 'sort_created_at' and order_by == 'asc':
                            queryset = queryset.filter(is_deleted=False).order_by('created_at')
                            return queryset
                        elif field_name == 'sort_created_at' and order_by == 'desc':
                            queryset = queryset.filter(is_deleted=False).order_by('-created_at')
                            return queryset
                        elif field_name == 'sort_user_project' and order_by == 'asc':
                            queryset = queryset.filter(is_deleted=False).order_by('user_project')
                            return queryset
                        elif field_name == 'sort_user_project' and order_by == 'desc':
                            queryset = queryset.filter(is_deleted=False).order_by('-user_project')
                            return queryset

                    if user_first_name:
                        filter['employee__first_name__icontains'] = user_first_name
                    if user_last_name:
                        filter['employee__last_name__icontains'] = user_last_name

                    if start_date and end_date:
                        end_date = end_date + 'T23:59:59'
                        start_object = datetime.strptime(start_date, '%Y-%m-%d')
                        end_object = datetime.strptime(end_date, '%Y-%m-%dT%H:%M:%S')
                        filter['created_at__range'] = (start_object, end_object)
                    if user_project:
                        filter['user_project__in'] = user_project.split(',')

                    if user_designation:
                        filter['employee__mmr_user'] = user_designation

                    if attendance:
                        filter['id'] = attendance

                    if employee:
                        filter['employee'] = employee

                    if approved_status:
                        filter['approved_status'] = approved_status

                    if filter:
                        queryset = queryset.filter(is_deleted=False, **filter).order_by('-id')
                        # print("queryset",queryset.query)
                        return queryset
                    elif user_name:
                        if '@' in user_name:
                            queryset = queryset.filter(is_deleted=False, employee__email__icontains=user_name).order_by(
                                '-id')
                            return queryset
                        else:
                            # print("user_name")
                            name = user_name.split(" ")
                            # print("name", name)
                            if name:
                                queryset_all = PmsAttendance.objects.none()
                                # print("len(name)",len(name))
                                for i in name:
                                    queryset = queryset.filter(
                                        Q(is_deleted=False) & Q(employee__first_name__icontains=i) |
                                        Q(employee__last_name__icontains=i)).order_by('-id')
                                    queryset_all = (queryset_all | queryset)
                                return queryset_all
                    else:
                        queryset = queryset.filter(is_deleted=False).order_by('-id')
                        return queryset
                else:
                    return self.queryset

                #+++++++++++++
        else:
            return self.queryset
    
    # End For permisson lavel check modified by @Rupam
    
    def list_synchronization(self, list_data: list)-> list:
        data = pd.DataFrame(list_data)
        data = data.replace(np.nan, 0, regex=True)
        data.sort_values("date", axis = 0, ascending = True, inplace = True,)
        col_list = data.columns.values
        row_list = data.values.tolist()
        total_result = list()
        for row in row_list:
            data_dict = dict(zip(col_list,row))
            # print("data_dict",data_dict['deviation_details'])
            if len(data_dict['deviation_details'])>0:
                total_result.append(data_dict)
        list_data = total_result
        return list_data
    @response_modify_decorator_list_or_get_after_execution_for_pagination
    def list(self, request, *args, **kwargs):
        response = super(AttandanceListWithOnlyDeviationByPermissonView, self).list(request,args,kwargs)
        if response.data['results']:
            for data in response.data['results']:
                if not data['user_project']:
                    data['user_project'] = {}
            response.data['results'] = self.list_synchronization(list(response.data['results']))
        return response


#:::::::::::: PmsAttandanceLog ::::::::::::::::::::::::::::#
class AttandanceLogAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsAttandanceLog.objects.filter(is_deleted=False)
    serializer_class = AttandanceLogAddSerializer
    # pagination_class=CSPageNumberPagination
    # filter_backends = (DjangoFilterBackend,)
    # filterset_fields = ('attandance',)
    ##results

    def get_queryset(self):
        filter = {}
        attandance = self.request.query_params.get('attandance', None)
        start_time = self.request.query_params.get('start_time', None)
        end_time = self.request.query_params.get('end_time', None)

        if attandance:
            filter['attandance_id']=attandance
        if start_time and end_time:
            start_object = datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S')
            end_object = datetime.strptime(end_time, '%Y-%m-%dT%H:%M:%S')
            filter['time__gte']=start_object
            filter['time__lte']=end_object

        if filter:
            # print("filter", filter)
            return self.queryset.filter(is_deleted=False,**filter)
        else:
            return self.queryset.none()

    # def list(self, request, *args, **kwargs):
    #     response = super(AttandanceLogAddView, self).list(request,args,kwargs)
    #     print("response", response.data)
    #     # response.data['results'] = response.data
    #     return response
    def list(self, request, *args, **kwargs):
        data_dict = {}
        response = super(AttandanceLogAddView, self).list(request, args, kwargs)
        data_dict['results'] = response.data
        if response.data:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_SUCCESS
        elif len(response.data) == 0:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_NO_DATA
        else:
            data_dict['request_status'] = 0
            data_dict['msg'] = settings.MSG_ERROR
        response.data = data_dict
        return response

class AttandanceLogMultipleAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsAttandanceLog.objects.filter(is_deleted=False)
    serializer_class = AttandanceLogMultipleAddSerializer

    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
class AttendanceLogEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsAttandanceLog.objects.all()
    serializer_class = AttandanceLogEditSerializer
class AttandanceLogApprovalEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsAttandanceLog.objects.all()
    serializer_class = AttandanceLogApprovalEditSerializer

#:::::::::::: Pms Attandance leave ::::::::::::::::::::::::::::#
# class AdvanceLeaveAddView(generics.ListCreateAPIView):
#     permission_classes = [IsAuthenticated]
#     authentication_classes = [TokenAuthentication]
#     pagination_class = CSPageNumberPagination
#     queryset = PmsEmployeeLeaves.objects.all()
#     serializer_class=AdvanceLeavesAddSerializer

class AdvanceLeaveAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    pagination_class = CSPageNumberPagination
    queryset = PmsEmployeeLeaves.objects.all()
    serializer_class=AdvanceLeavesAddSerializer

    def get(self, request, *args, **kwargs):
        response=super(AdvanceLeaveAddView,self).get(request,args,kwargs)
        for data in response.data['results']:
            employee_first_name = User.objects.only('first_name').get(username=data['employee']).first_name
            employee_last_name = User.objects.only('last_name').get(username=data['employee']).last_name
            data['employee_first_name']=employee_first_name
            data['employee_last_name']=employee_last_name
        return response

    def get_queryset(self):
        filter = {}
        user=self.request.user
        print('login_user_details',user.is_superuser)
        print('user',user)
        users_list=(list(TCoreUserDetail.objects.filter(reporting_head=user,cu_is_deleted=False).values_list('cu_user',flat=True)))
        print('users_list',users_list)
        sort_field='-id'
        user_name = self.request.query_params.get('user_name', None)
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        leave_type = self.request.query_params.get('leave_type', None)
        field_name=self.request.query_params.get('field_name',None)
        order_by = self.request.query_params.get('order_by', None)
        employee = self.request.query_params.get('employee', None)

        if field_name != "" and order_by != "":
            if field_name == 'sort_first_name' and order_by == 'asc':
                # queryset = self.queryset.filter(is_deleted=False).order_by('employee__first_name')
                # return queryset
                sort_field='employee__first_name'
            elif field_name == 'sort_first_name' and order_by == 'desc':
                # queryset = self.queryset.filter(is_deleted=False).order_by('-employee__first_name')
                # return queryset
                sort_field='-employee__first_name'
            elif field_name == 'sort_email' and order_by == 'asc':
                # queryset = self.queryset.filter(is_deleted=False).order_by('employee__email')
                # return queryset
                sort_field='employee__email'
            elif field_name == 'sort_email' and order_by == 'desc':
                # queryset = self.queryset.filter(is_deleted=False).order_by('-employee__email')
                # return queryset
                sort_field='-employee__email'
            elif field_name == 'sort_start_date' and order_by == 'asc':
                # queryset =  self.queryset.filter(is_deleted=False).order_by('start_date')
                # return queryset
                sort_field='start_date'
            elif field_name == 'sort_start_date' and order_by == 'desc':
                # queryset = self.queryset.filter(is_deleted=False).order_by('-start_date')
                # return queryset
                sort_field='-start_date'

        if start_date and end_date:
            start_object = datetime.strptime(start_date, '%Y-%m-%d')
            end_object = datetime.strptime(end_date, '%Y-%m-%d')
            filter['start_date__range']=(start_object, end_object)

        if leave_type:
            filter['leave_type'] = leave_type

        if employee:
            filter['employee'] = employee
        if user.is_superuser == False:
            if users_list:
                if filter:
                    queryset = self.queryset.filter(employee__in=users_list,is_deleted=False,**filter).order_by(sort_field)
                    # print("queryset",queryset.query)
                    return queryset
                elif user_name:
                    if '@' in user_name:
                        queryset = self.queryset.filter(is_deleted=False, employee__email__icontains=user_name).order_by(sort_field)
                        return queryset
                    else:
                        # print("user_name")
                        name = user_name.split(" ")
                        # print("name", name)
                        if name:
                            queryset_all = PmsAttendance.objects.none()
                            # print("len(name)",len(name))
                            for i in name:
                                queryset = self.queryset.filter(Q(is_deleted=False) & Q(employee__first_name__icontains=i) |
                                                                Q(employee__last_name__icontains=i)).order_by(sort_field)
                                queryset_all = (queryset_all|queryset)
                            return queryset_all
                else:
                    queryset = self.queryset.filter(employee__in=users_list,is_deleted=False).order_by(sort_field)
                    return queryset
            else:
                return []
        else:
            if filter:
                queryset = self.queryset.filter(is_deleted=False,**filter).order_by(sort_field)
                # print("queryset",queryset.query)
                return queryset
            elif user_name:
                if '@' in user_name:
                    queryset = self.queryset.filter(is_deleted=False, employee__email__icontains=user_name).order_by(sort_field)
                    return queryset
                else:
                    # print("user_name")
                    name = user_name.split(" ")
                    # print("name", name)
                    if name:
                        queryset_all = PmsAttendance.objects.none()
                        # print("len(name)",len(name))
                        for i in name:
                            queryset = self.queryset.filter(Q(is_deleted=False) & Q(employee__first_name__icontains=i) |
                                                            Q(employee__last_name__icontains=i)).order_by(sort_field)
                            queryset_all = (queryset_all|queryset)
                        return queryset_all
            else:
                queryset = self.queryset.filter(is_deleted=False).order_by(sort_field)
                return queryset
            
class AdvanceLeaveEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsEmployeeLeaves.objects.all()
    serializer_class=AdvanceLeaveEditSerializer
    def put(self, request,* args, **kwargs):
        response = super(AdvanceLeaveEditView, self).put(request, args, kwargs)
        # print('request: ', request.data)
        data_dict = {}
        data_dict['result'] = request.data
        if response.data:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_SUCCESS
        else:
            data_dict['request_status'] = 0
            data_dict['msg'] = settings.MSG_ERROR
        response.data = data_dict
        return response
class LeaveListByEmployeeView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    pagination_class = CSPageNumberPagination
    queryset = PmsEmployeeLeaves.objects.all()
    serializer_class = LeaveListByEmployeeSerializer

    def get_queryset(self,*args,**kwargs):
        employee_id=self.kwargs['employee_id']
        # print('employee_id',employee_id)
        return self.queryset.filter(employee=employee_id)

    def list(self, request, *args, **kwargs):
        response = super(LeaveListByEmployeeView, self).list(request, args, kwargs)
        response.data['request_status'] = 0
        response.data['msg'] = settings.MSG_ERROR
        response.data['per_page_count'] = len(response.data['results'])
        if response.data['results']:
            response.data['request_status'] = 1
            response.data['msg'] = settings.MSG_SUCCESS
        return response

#:::::::::::::::::::Pms Attandance Deviation::::::::::::::::::::#
class AttandanceDeviationJustificationEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsAttandanceDeviation.objects.all()
    serializer_class = AttandanceDeviationJustificationEditSerializer
    def put(self, request,* args, **kwargs):
        response = super(AttandanceDeviationJustificationEditView, self).put(request, args, kwargs)
        # print('request: ', request.data)
        data_dict = {}
        data_dict['result'] = request.data
        if response.data:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_SUCCESS
        else:
            data_dict['request_status'] = 0
            data_dict['msg'] = settings.MSG_ERROR
        response.data = data_dict
        return response
class AttandanceDeviationApprovaEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsAttandanceDeviation.objects.all()
    serializer_class = AttandanceDeviationApprovaEditSerializer
class AttandanceDeviationByAttandanceListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsAttandanceDeviation.objects.all()
    serializer_class =AttandanceDeviationByAttandanceListSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('attandance',)
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response

#:::::::::::::::::::::: PMS EMPLOYEE CONVEYANCE:::::::::::::::::::::::::::#
class EmployeeConveyanceAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsEmployeeConveyance.objects.all()
    serializer_class = EmployeeConveyanceAddSerializer
class EmployeeConveyanceEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsEmployeeConveyance.objects.all()
    serializer_class = EmployeeConveyanceEditSerializer

    def put(self, request,* args, **kwargs):
        response = super(EmployeeConveyanceEditView, self).put(request, args, kwargs)
        # print('request: ', request.data)
        data_dict = {}
        data_dict['result'] = request.data
        if response.data:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_SUCCESS
        else:
            data_dict['request_status'] = 0
            data_dict['msg'] = settings.MSG_ERROR
        response.data = data_dict
        return response
class EmployeeConveyanceListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsEmployeeConveyance.objects.filter(is_deleted=False)
    serializer_class = EmployeeConveyanceListSerializer
    pagination_class = CSPageNumberPagination
    def get_queryset(self):
        filter = {}
        project = self.request.query_params.get('project', None)
        employee = self.request.query_params.get('employee', None)
        project_site = self.request.query_params.get('project_site', None)
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        approved_status = self.request.query_params.get('approved_status', None)
        user_name = self.request.query_params.get('user_name', None)
        field_name = self.request.query_params.get('field_name', None)
        order_by = self.request.query_params.get('order_by', None)

        user=self.request.user
        print('login_user_details',user.is_superuser)
        print('user',user)
        users_list=(list(TCoreUserDetail.objects.filter(reporting_head=user,cu_is_deleted=False).values_list('cu_user',flat=True)))
        print('users_list',users_list)
        sort_field='-id'

        if field_name != "" and order_by != "":
            if field_name == 'date' and order_by == 'asc':
                sort_field='date'
                # queryset = self.queryset.filter(is_deleted=False).order_by('date')
                # return queryset
            elif field_name == 'date' and order_by == 'desc':
                sort_field='-date'
                # queryset = self.queryset.filter(is_deleted=False).order_by('-date')
                # return queryset
            if field_name == 'ammount' and order_by == 'asc':
                sort_field='ammount'
                # queryset = self.queryset.filter(is_deleted=False).order_by('ammount')
                # return queryset
            elif field_name == 'ammount' and order_by == 'desc':
                sort_field='-ammount'
                # queryset = self.queryset.filter(is_deleted=False).order_by('-ammount')
                # return queryset
            if field_name == 'eligibility_per_day' and order_by == 'asc':
                sort_field='eligibility_per_day'
                # queryset = self.queryset.filter(is_deleted=False).order_by('eligibility_per_day')
                # return queryset
            elif field_name == 'eligibility_per_day' and order_by == 'desc':
                sort_field='-eligibility_per_day'
                # queryset = self.queryset.filter(is_deleted=False).order_by('-eligibility_per_day')
                # return queryset
        
        if start_date and end_date:
            start_object = datetime.strptime(start_date, '%Y-%m-%d')
            end_object = datetime.strptime(end_date, '%Y-%m-%d')
            filter['date__range']=(start_object, end_object)

        if project:
            filter['project__in'] = project.split(',')

        if employee:
            filter['employee'] = employee

        if approved_status:
            filter['approved_status'] = approved_status

        if project_site:
            filter['project__site_location__in'] = project_site.split(',')

        if user.is_superuser==False:
            if users_list:
                if filter:
                    queryset = self.queryset.filter(employee__in=users_list,is_deleted=False, **filter).order_by(sort_field)
                    # print("queryset", queryset.query)
                    return queryset
                elif user_name:
                    if '@' in user_name:
                        queryset = self.queryset.filter(is_deleted=False, employee__email__icontains=user_name).order_by(sort_field)
                        return queryset
                    else:
                        print("user_name")
                        name = user_name.split(" ")
                        print("name", name)
                        if name:
                            queryset_all = PmsAttendance.objects.none()
                            print("len(name)",len(name))
                            for i in name:
                                queryset = self.queryset.filter(Q(is_deleted=False) & Q(employee__first_name__icontains=i) |
                                                                Q(employee__last_name__icontains=i)).order_by(sort_field)
                                queryset_all = (queryset_all|queryset)
                            return queryset_all
                else:
                    queryset = self.queryset.filter(employee__in=users_list,is_deleted=False).order_by(sort_field)
                    return queryset
            else:
                return []
        else:
            if filter:
                    queryset = self.queryset.filter(is_deleted=False, **filter).order_by(sort_field)
                    # print("queryset", queryset.query)
                    return queryset
            elif user_name:
                if '@' in user_name:
                    queryset = self.queryset.filter(is_deleted=False, employee__email__icontains=user_name).order_by(sort_field)
                    return queryset
                else:
                    print("user_name")
                    name = user_name.split(" ")
                    print("name", name)
                    if name:
                        queryset_all = PmsAttendance.objects.none()
                        print("len(name)",len(name))
                        for i in name:
                            queryset = self.queryset.filter(Q(is_deleted=False) & Q(employee__first_name__icontains=i) |
                                                            Q(employee__last_name__icontains=i)).order_by(sort_field)
                            queryset_all = (queryset_all|queryset)
                        return queryset_all
            else:
                queryset = self.queryset.filter(is_deleted=False).order_by(sort_field)
                return queryset


    def list(self, request, *args, **kwargs):
        response = super(EmployeeConveyanceListView, self).list(request, args, kwargs)
        response.data['request_status'] = 0
        response.data['msg'] = settings.MSG_ERROR

        if response.data['results']:
            for data in response.data['results']:
                if not data['user_project']:
                    data['user_project'] = {}
            # response.data['results'] = self.list_synchronization(list(response.data['results']))
            response.data['request_status'] = 1
            response.data['msg'] = settings.MSG_SUCCESS
        return response
#:::::::::::::::::::::::::::::::::::PMS EMPLOYEE FOODING:::::::::::::::::::::::::::::::#
class EmployeeFoodingAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsEmployeeFooding.objects.filter(is_deleted=False)
    serializer_class = EmployeeFoodingAddSerializer
class AttandanceAllDetailsListWithFoodingView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsAttendance.objects.filter(is_deleted=False)
    serializer_class = AttandanceAllDetailsListWithFoodingSerializer
    pagination_class = CSPageNumberPagination

    def get_queryset(self):
        # from django.db.models import Q
        filter = {}
        user_project = self.request.query_params.get('user_project', None)
        employee = self.request.query_params.get('employee', None)
        user_designation = self.request.query_params.get('user_designation', None)

        user_first_name = self.request.query_params.get('user_first_name', None)
        user_last_name = self.request.query_params.get('user_last_name', None)
        user_name = self.request.query_params.get('user_name', None)
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        attendance = self.request.query_params.get('attendance', None)
        approved_status = self.request.query_params.get('approved_status', None)
        field_name=self.request.query_params.get('field_name',None)
        order_by = self.request.query_params.get('order_by', None)

        user=self.request.user
        print('login_user_details',user.is_superuser)
        print('user',user)
        users_list=(list(TCoreUserDetail.objects.filter(reporting_head=user,cu_is_deleted=False).values_list('cu_user',flat=True)))
        print('users_list',users_list)
        sort_field='-id'

        if field_name !="" and order_by !="":
            print("field_name is not None and order_by is not None")
            if field_name == 'sort_first_name' and order_by == 'asc':
                sort_field='employee__first_name'
                # queryset = self.queryset.filter(is_deleted=False).order_by('employee__first_name')
                # return queryset
            elif field_name == 'sort_first_name' and order_by == 'desc':
                sort_field='-employee__first_name'
                # queryset = self.queryset.filter(is_deleted=False).order_by('-employee__first_name')
                # return queryset
            elif field_name == 'sort_created_at' and order_by == 'asc':
                sort_field='date'
                # queryset =  self.queryset.filter(is_deleted=False).order_by('date')
                # return queryset
            elif field_name == 'sort_created_at' and order_by == 'desc':
                sort_field='-date'
                # queryset = self.queryset.filter(is_deleted=False).order_by('-date')
                # return queryset
            elif field_name == 'sort_user_project' and order_by == 'asc':
                sort_field='user_project'
                # queryset = self.queryset.filter(is_deleted=False).order_by('user_project')
                # return queryset
            elif field_name == 'sort_user_project' and order_by == 'desc':
                sort_field='-user_project'
                # queryset = self.queryset.filter(is_deleted=False).order_by('-user_project')
                # return queryset

        if user_first_name:
            filter['employee__first_name__icontains'] = user_first_name
        if user_last_name:
            filter['employee__last_name__icontains'] = user_last_name

        if start_date and end_date:
            start_object = datetime.strptime(start_date, '%Y-%m-%d')
            end_object = datetime.strptime(end_date, '%Y-%m-%d')
            filter['created_at__range']=(start_object, end_object)
        if user_project:
            filter['user_project__in']= user_project.split(',')

        if user_designation:
            filter['employee__mmr_user']= user_designation

        if attendance:
            filter['id'] = attendance

        if employee:
            filter['employee'] = employee

        if approved_status:
            filter['approved_status'] = approved_status
        if user.is_superuser==False:
            if users_list:
                if filter:
                    queryset = self.queryset.filter(employee__in=users_list,is_deleted=False,**filter).order_by(sort_field)
                    print("queryset",queryset.query)
                    return queryset
                elif user_name:
                    if '@' in user_name:
                        queryset = self.queryset.filter(is_deleted=False, employee__email__icontains=user_name).order_by(sort_field)
                        return queryset
                    else:
                        print("user_name")
                        name = user_name.split(" ")
                        print("name", name)
                        if name:
                            queryset_all = PmsAttendance.objects.none()
                            print("len(name)",len(name))
                            for i in name:
                                queryset = self.queryset.filter(Q(is_deleted=False) & Q(employee__first_name__icontains=i) |
                                                                Q(employee__last_name__icontains=i)).order_by(sort_field)
                                queryset_all = (queryset_all|queryset)
                            return queryset_all
                else:
                    queryset = self.queryset.filter(employee__in=users_list,is_deleted=False).order_by(sort_field)
                    return queryset
            else:
                return []
        else:
            if filter:
                queryset = self.queryset.filter(is_deleted=False,**filter).order_by(sort_field)
                # print("queryset",queryset.query)
                return queryset
            elif user_name:
                if '@' in user_name:
                    queryset = self.queryset.filter(is_deleted=False, employee__email__icontains=user_name).order_by(sort_field)
                    return queryset
                else:
                    print("user_name")
                    name = user_name.split(" ")
                    print("name", name)
                    if name:
                        queryset_all = PmsAttendance.objects.none()
                        print("len(name)",len(name))
                        for i in name:
                            queryset = self.queryset.filter(Q(is_deleted=False) & Q(employee__first_name__icontains=i) |
                                                            Q(employee__last_name__icontains=i)).order_by(sort_field)
                            queryset_all = (queryset_all|queryset)
                        return queryset_all
            else:
                queryset = self.queryset.filter(is_deleted=False).order_by(sort_field)
                return queryset


    def list_synchronization(self, list_data: list)-> list:
        data = pd.DataFrame(list_data)
        data = data.replace(np.nan, 0, regex=True)
        data.sort_values("date", axis = 0, ascending = True, inplace = True,)
        col_list = data.columns.values
        row_list = data.values.tolist()
        total_result = list()
        for row in row_list:
            data_dict = dict(zip(col_list,row))
            total_result.append(data_dict)
        list_data = total_result
        return list_data

    def list(self, request, *args, **kwargs):
        response = super(AttandanceAllDetailsListWithFoodingView, self).list(request,args,kwargs)
        response.data['request_status'] = 0
        response.data['msg'] = settings.MSG_ERROR

        if response.data['results']:
            for data in response.data['results']:
                if not data['user_project']:
                    data['user_project'] = {}
            # response.data['results'] = self.list_synchronization(list(response.data['results']))
            response.data['request_status'] = 1
            response.data['msg'] = settings.MSG_SUCCESS
        return response


#:::::::::::::::::::::::::::::::: ATTENDENCE LIST EXPORT ::::::::::::::::::::::::::::::#
class AttandanceListExportView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsAttendance.objects.all()

    def get(self, request, *args, **kwargs):
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        filter = {}
        if start_date and end_date:
            end_date = end_date + 'T23:59:59'
            start_object = datetime.strptime(start_date, '%Y-%m-%d')
            end_object = datetime.strptime(end_date, '%Y-%m-%dT%H:%M:%S')
            filter['date__range'] = (start_object, end_object)

        else:
            # cur_date = timezone.now().date()###,date__date=timezone.now().date()
            return Response({
                'status': 0,
                'msz':'Enter proper Date range',
                })
        attemdance_data = PmsAttendance.objects.filter(is_deleted=False,**filter).values(
            'id','employee__first_name','employee__last_name','login_time','logout_time','user_project__name','justification','approved_status').order_by('-date')

        data_list = []
        count = 0

        for att_data in attemdance_data:
            # print("data", att_data)
            login_time = att_data['login_time'].strftime("%I:%M:%S %p")
            if att_data['logout_time']:
                logout_time = att_data['logout_time'].strftime("%I:%M:%S %p")
                logout_datetime = att_data['logout_time'].strftime("%d/%m/%Y, %I:%M:%S %p")
            else:
                logout_time = ""
                logout_datetime = ""

            name = ""
            if att_data['employee__first_name']:
                name = att_data['employee__first_name']
                if att_data['employee__first_name']:
                    name += " " + att_data['employee__last_name']

            if att_data['approved_status']==1:
                approved_status = "pending"
            elif att_data['approved_status'] == 2:
                approved_status = "approved"
            elif att_data['approved_status'] == 3:
                approved_status = "reject"
            else:
                approved_status = "regular"

            deviation_data = PmsAttandanceDeviation.objects.filter(attandance=att_data['id']).values('from_time','to_time')
            if deviation_data:
                for dev_data in deviation_data:
                    count += 1
                    # print("dev_data",dev_data)
                    from_time = dev_data['from_time'].strftime("%I:%M:%S %p")
                    to_time = dev_data['to_time'].strftime("%I:%M:%S %p")
                    attemdance_list = [count,att_data['id'],name,login_time,logout_time,logout_datetime,
                        att_data['user_project__name'],att_data['justification'],approved_status,from_time,to_time]

                    # print("attemdance_list",attemdance_list)
                    data_list.append(attemdance_list)
            else:
                count+=1
                attemdance_list = [count,att_data['id'],name,login_time,logout_time,logout_datetime,
                        att_data['user_project__name'],att_data['justification'],approved_status,"",""]

                data_list.append(attemdance_list)

        # print("data_list",data_list)
        if data_list:
            file_path = self.creat_excel(data_list)

        return Response({
            'status': 1,
            'msz':'successful',
            'results': file_path
        })

    def creat_excel(self, data_list):
        import pandas as pd
        path = "/home/nooralam/Desktop/Scores.xlsx"
        table = pd.DataFrame(data_list)
        table.columns = ['Serial no','Attendance id','Employee Name','Login Time','Logout Time','Logout Datetime','Project Name',
                        'Justification','Approved status','From time(Deviation)','To time(Deviation)']
        writer = pd.ExcelWriter(path)
        table.to_excel(writer, 'Scores 1', index=False)
        writer.save()

        return path


'''
    @@ Added By Rupam Hazra on [10-01-2020] line number 1597-1606 @@
    
'''
class AttendanceUpdateLogOutTimeFailedOnLogoutView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsAttendance.objects.filter(is_deleted=False)
    serializer_class = AttendanceUpdateLogOutTimeFailedOnLogoutSerializer

    @response_modify_decorator_update
    def put(self, request,* args, **kwargs):
        return super().update(request, *args, **kwargs)

class AttandanceLogMultipleByThreadAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsAttandanceLog.objects.filter(is_deleted=False)
    serializer_class = AttandanceLogMultipleByThreadAddSerializer

    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response

    @response_modify_decorator_post
    def post(self, request,* args, **kwargs):
        return super().post(request, *args, **kwargs)