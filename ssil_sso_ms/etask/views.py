from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from etask.models import *
from etask.serializers import *
from pagination import CSLimitOffestpagination,CSPageNumberPagination,OnOffPagination
from rest_framework.views import APIView
from django.conf import settings
from rest_framework import filters
from datetime import datetime,timedelta,date
import collections
from rest_framework.parsers import FileUploadParser
from django_filters.rest_framework import DjangoFilterBackend
from custom_decorator import *
from rest_framework import mixins
import os
from global_function import userdetails,department,designation
import pandas as pd
import numpy as np
from datetime import datetime
from django.db.models import When, Case, Value, CharField, IntegerField, F, Q
import functools
import operator

# Create your views here.

# class EtaskTypeAddView(generics.ListCreateAPIView):
#     permission_classes = [IsAuthenticated]
#     authentication_classes = [TokenAuthentication]
#     queryset = EtaskType.objects.all()
#     serializer_class = EtaskTypeAddSerializer
    
class EtaskTaskAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskTask.objects.all()
    serializer_class = EtaskTaskAddSerializer
    pagination_class = CSPageNumberPagination

    @response_modify_decorator_post
    def post(self, request, *args, **kwargs):
        return super(EtaskTaskAddView,self).post(request, *args, **kwargs)


    @response_modify_decorator_list_or_get_after_execution_for_pagination
    def get(self, request, *args, **kwargs):
        response = super(EtaskTaskAddView, self).get(self, request, args, kwargs)

        usercc_dict = {}
        assignto_dict = {}
        subtask_dict = {}
        for data in response.data['results']:
            print("if : task_type-->",data['task_type'])
            user_name = User.objects.filter(id=data['owner']).values('first_name','last_name')
            data['owner'] = user_name[0]['first_name'] + " " + user_name[0]['last_name']
            get_sub_task = EtaskTask.objects.filter(parent_id=data['id'])
            et_reporting_dates = ETaskReportingDates.objects.filter(task=data['id'],task_type=1).values('reporting_date')
            data['r_date'] = et_reporting_dates if et_reporting_dates else '[]'

            if data['task_type'] == 3:
                data['sub_task'] = data['task_subject']
                data['sub_task_description'] = data['task_description']
                get_parent_details = EtaskTask.objects.filter(id=data['parent_id'],is_deleted=False)
                for p_details in get_parent_details:
                    data['task_subject'] = p_details.task_subject
                    data['task_description'] = p_details.task_description                    
        return response

class EtaskTaskRepostView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskTask.objects.filter(is_deleted=False)
    serializer_class = EtaskTaskRepostSerializer

    # @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        response = super(EtaskTaskRepostView, self).get(self, request, args, kwargs)   
        # print('response',response.data)    
        user_cc=EtaskUserCC.objects.filter(task_id=response.data['id'],is_deleted=False).values('id','user')
        # print('user_cc',user_cc)
        response.data['user_cc']=[{'id':u_c['id'],'user_id':u_c['user'],'user_name':userdetails(u_c['user'])} for u_c in user_cc]
        response.data['reporting_date_details'] = ETaskReportingDates.objects.filter(task=response.data['id']).values()
        response.data['follow_up_details'] = EtaskFollowUP.objects.filter(task=response.data['id']).values()
        return response



class EtaskTaskEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskTask.objects.filter(is_deleted=False)
    serializer_class = EtaskTaskEditSerializer

    @response_modify_decorator_update
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
        
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
        
class EtaskTaskDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskTask.objects.filter(is_deleted=False)
    serializer_class = EtaskTaskDeleteSerializer

class EtaskParentTaskListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskTask.objects.filter(Q(Q(task_status=1)|Q(task_status=3)),is_deleted=False,parent_id=0)
    serializer_class = EtaskParentTaskListSerializer

    def get_queryset(self):
        user = self.request.user.id
        print('user',user)
        user_list_rh=(list(TCoreUserDetail.objects.filter((Q(hod_id=user)|Q(reporting_head_id=user)),cu_is_deleted=False).values_list('cu_user',flat=True).iterator()))
        user_list_rh.append(user)
        return self.queryset.filter(Q(assign_to__in=user_list_rh)|Q(assign_by__in=user_list_rh)|Q(sub_assign_to_user__in=user_list_rh)|Q(owner__in=user_list_rh))
                                                 
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):      
        return response

class EtaskMyTaskListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskTask.objects.filter(is_deleted=False)#parent_id=0)
    serializer_class = EtaskMyTaskListSerializer
    pagination_class = CSPageNumberPagination

    def get_queryset(self,):
        user = self.request.user.id

        current_date = self.request.query_params.get('current_date', None)
        all_task = self.request.query_params.get('all_task', None)
        


        filter = {}
        sort_field='-id'
        from_date = self.request.query_params.get('from_date', None)
        to_date = self.request.query_params.get('to_date', None)
        assign_by = self.request.query_params.get('assign_by', None)
        search = self.request.query_params.get('search', None)
        field_name = self.request.query_params.get('field_name', None)
        order_by = self.request.query_params.get('order_by', None)


        if current_date:
            cur_date = datetime.strptime(current_date, "%Y-%m-%d")
            print('cur_date-->',cur_date.date())
            all_queryset = self.queryset.filter(Q(task_status=1,is_deleted=False)&
                                   (Q(start_date__date__lte=cur_date)&Q(end_date__date__gte=cur_date)|
                                   Q(end_date__date__lte=cur_date)& Q(extended_date__date__gte=cur_date))&
                                   (Q(assign_to=user)|Q(sub_assign_to_user=user)),**filter).order_by(sort_field)
        elif all_task == 'all':
            print('--ALL--')
            all_queryset = self.queryset.filter((Q(is_deleted=False)&(Q(assign_to=user)|Q(sub_assign_to_user=user))),**filter).order_by(sort_field)
        else:
            all_queryset = self.queryset.filter((Q(task_status=1,is_deleted=False)&(Q(assign_to=user)|Q(sub_assign_to_user=user))),**filter).order_by(sort_field)



        if field_name and order_by:      
            if field_name =='task_code_id' and order_by=='asc':
                sort_field='task_code_id'

            if field_name =='task_code_id' and order_by=='desc':
                sort_field='-task_code_id'

            if field_name =='task_subject' and order_by=='asc':
                sort_field='task_subject'

            if field_name =='task_subject' and order_by=='desc':
                sort_field='-task_subject'

            if field_name =='start_date' and order_by=='asc':
                sort_field='start_date'
                # return self.queryset.all().order_by('duration_end')
            if field_name =='start_date' and order_by=='desc':
                sort_field='-start_date'
                # return self.queryset.all().order_by('-duration_end')

            if field_name =='end_date' and order_by=='asc':
                sort_field='end_date'
                # return self.queryset.all().order_by('duration')
            if field_name =='end_date' and order_by=='desc':
                sort_field='-end_date'
                    # return self.queryset.all().order_by('-duration')
            if field_name =='assign_by' and order_by=='asc':
                sort_field='assign_by'
                # return self.queryset.all().order_by('duration')
            if field_name =='assign_by' and order_by=='desc':
                sort_field='-assign_by'

        if from_date or to_date or assign_by or search:

            if from_date and to_date:
                from_object =datetime.strptime(from_date, '%Y-%m-%d')
                to_object =datetime.strptime(to_date, '%Y-%m-%d')
                filter['end_date__date__gte']= from_object
                filter['end_date__date__lte']= to_object + timedelta(days=1)

            if assign_by:
                filter['assign_by__in'] = list(map(int,assign_by.split(" ")))
            print("filter",filter)
            if search:
                search_data = search
                print('search_data-->',search_data)
                task_code = self.queryset.filter(task_status=1,is_deleted=False,task_code_id__icontains=search_data,**filter).values_list('id',flat=True)
                print('task_code-->',task_code)
                if task_code:
                    return all_queryset.filter(is_deleted=False,id__in=list(task_code),**filter).order_by(sort_field)
                else:
                    id1= self.queryset.filter(Q(task_status=1,is_deleted=False),**filter).values_list('id',flat=True)
                    id2= self.queryset.filter(Q(task_status=1,is_deleted=False),**filter).values_list('parent_id',flat=True)
                    ids=list(id1)+list(id2)
                    print("ids",ids)
                    check_data = EtaskTask.objects.filter((Q(task_subject__icontains=search_data)),id__in=ids).values_list('id',flat=True)
                    print("check_data",check_data)
                    return all_queryset.filter(Q(is_deleted=False),(Q(parent_id__in=list(check_data))|Q(id__in=list(check_data))),**filter).order_by(sort_field)  
                # queryset = all_queryset.filter((Q(task_code_id__icontains=search_data)|Q(task_subject__icontains=search_data)),
                #                                     is_deleted=False,**filter).order_by(sort_field)   
                # if queryset:
                #     return queryset
                # # else:
                #     check_data = EtaskTask.objects.filter(id__in=list(ids),task_subject__icontains=search_data).values_list('id',flat=True)
                #     print("check_data",check_data)
                #     return all_queryset.filter(Q(is_deleted=False) ,(Q(parent_id__in=list(check_data)|Q(id__in=list(check_data))),**filter).order_by(sort_field)                         
            else:
                return all_queryset.filter(is_deleted=False,**filter).order_by(sort_field)    
        else:
            return all_queryset.filter(is_deleted=False,**filter).order_by(sort_field)
  
        # sub_data = set(EtaskTask.objects.filter(~(Q(parent_id=0)),((Q(sub_assign_to_user__isnull=True)&Q(assign_to=user))|
        #                                     (Q(sub_assign_to_user__isnull=False)&Q(sub_assign_to_user=user))),task_status=1,
        #                                     is_deleted=False).values_list('parent_id', flat=True))
        # print("sub_data",sub_data)
        # return self.queryset.filter((((Q(sub_assign_to_user__isnull=True)&Q(assign_to=user))|
        #                                 (Q(sub_assign_to_user__isnull=False)&Q(sub_assign_to_user=user)))&Q(task_status=1))|
        #                                 (Q(id__in=sub_data))).order_by('-id')

        # return self.queryset.filter((((Q(sub_assign_to_user__isnull=True)&Q(assign_to=user))|
        #                                 (Q(sub_assign_to_user__isnull=False)&Q(sub_assign_to_user=user)))&Q(task_status=1))).order_by('-id')




    @response_modify_decorator_list_or_get_after_execution_for_pagination
    def get(self, request, *args, **kwargs):
        response = super(EtaskMyTaskListView, self).get(self, request, args, kwargs)
        user = self.request.user.id
        # print('response.data-->',response.data)

        for data in response.data['results']:
            comments_count = ETaskComments.objects.filter(task=data['id'],is_deleted=False).count()
            data['comments_count'] = comments_count
            # print('comments_count-->',comments_count)
            latest_comments = ETaskComments.objects.filter(task=data['id'],is_deleted=False).values('comments','created_by','created_at')
            # print('latest_comments-->',latest_comments)

            if latest_comments and int(comments_count) > 0 :
                commentns_created_by = User.objects.filter(id=latest_comments[comments_count-1]['created_by'],is_active=True).values('first_name','last_name')
                commentns_created_by_first_name = commentns_created_by[0]['first_name'] if commentns_created_by[0]['first_name'] else ''
                commentns_created_by_last_name = commentns_created_by[0]['last_name'] if commentns_created_by[0]['last_name'] else ''
                data['latest_comments'] = {
                     "comments" : latest_comments[comments_count-1]['comments'],
                     "created_by" : (commentns_created_by_first_name + ' ' + commentns_created_by_last_name),
                     "created_at" : latest_comments[comments_count-1]['created_at']
                 }
            else:
                data['latest_comments'] = None

            assign_by = User.objects.filter(id=data['assign_by'],is_active=True).values('first_name','last_name')
            if assign_by:
                assign_by_first_name = assign_by[0]['first_name'] if assign_by[0]['first_name'] else ''
                assign_by_last_name = assign_by[0]['last_name'] if assign_by[0]['last_name'] else ''
                data['assign_by'] = assign_by_first_name + ' ' +assign_by_last_name

            sub_assign_to_user = User.objects.filter(id=data['sub_assign_to_user'],is_active=True).values('first_name','last_name')
            # print('sub_assign_to_user-->',sub_assign_to_user)
            if user != data['sub_assign_to_user']:
                if sub_assign_to_user:
                    sub_assign_to_user_first_name = sub_assign_to_user[0]['first_name'] if sub_assign_to_user[0]['first_name'] else ''
                    sub_assign_to_user_last_name = sub_assign_to_user[0]['last_name'] if sub_assign_to_user[0]['last_name'] else ''
                    data['sub_assign_to_user_id'] = data['sub_assign_to_user']
                    data['sub_assign_to_user'] = sub_assign_to_user_first_name + ' ' +sub_assign_to_user_last_name
            else:
                data['sub_assign_to_user'] = None
                data['sub_assign_to_user_id'] = None
                data['assign_to'] = user


            if int(data['parent_id']) != 0:
                # parent_id_name = EtaskTask.objects.filter(id=data['id'],task_status=1,is_deleted=False,parent_id=data['parent_id']).values('task_subject')
                parent_id_name = EtaskTask.objects.filter(is_deleted=False,id=data['parent_id']).values('id','task_subject')
                # print('parent_id_name-->',parent_id_name[0]['id'])
                if parent_id_name:
                    data['parent'] = {
                        "id" :  data['parent_id'],
                        "name" :parent_id_name[0]['task_subject']
                    }
            else :
                data['parent'] = None

            reporting_date = ETaskReportingDates.objects.filter(task=data['id'],task_type=1,is_deleted=False)
            reporting_list = []
            for r_date in reporting_date:
                # print('r_date.reporting_date-->',r_date.reporting_date)
                if r_date.reporting_date.date() >datetime.now().date():
                    reporting_dict = {
                        "id" : r_date.id,
                        "reporting_dates" : r_date.reporting_date,
                        "reporting_status":r_date.reporting_status,
                        "reporting_status_name":r_date.get_reporting_status_display(),
                        "crossed_by":0
                    }
                    reporting_list.append(reporting_dict)
                else:
                    reporting_dict = {
                        "id" : r_date.id,
                        "reporting_dates" : r_date.reporting_date,
                        "reporting_status":r_date.reporting_status,
                        "reporting_status_name":r_date.get_reporting_status_display(),
                        "crossed_by":(datetime.now().date()-r_date.reporting_date.date ()).days
                    }
                    reporting_list.append(reporting_dict)


            data['reporting_dates'] = reporting_list

        return response

class EtaskCompletedTaskListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskTask.objects.filter(is_deleted=False)
    serializer_class = EtaskCompletedTaskListSerializer
    pagination_class = CSPageNumberPagination

    def get_queryset(self,):
        user = self.request.user.id
        # sub_data = set(EtaskTask.objects.filter(~(Q(parent_id=0)),((Q(sub_assign_to_user__isnull=True)&Q(assign_to=user))|
        #                                     (Q(sub_assign_to_user__isnull=False)&Q(sub_assign_to_user=user))),task_status=2,
        #                                     is_deleted=False).values_list('parent_id', flat=True))
        # # print("sub_data",sub_data)
        # return self.queryset.filter((((Q(sub_assign_to_user__isnull=True)&Q(assign_to=user))|
        #                                 (Q(sub_assign_to_user__isnull=False)&Q(sub_assign_to_user=user)))&Q(task_status=2))|
        #                                 (Q(id__in=sub_data))).order_by('-id')

        # return self.queryset.filter((((Q(sub_assign_to_user__isnull=True)&Q(assign_to=user))|
        #                                 (Q(sub_assign_to_user__isnull=False)&Q(sub_assign_to_user=user)))&Q(task_status=2))).order_by('-id')

        filter = {}
        sort_field='-id'
        from_date = self.request.query_params.get('from_date', None)
        to_date = self.request.query_params.get('to_date', None)
        assign_by = self.request.query_params.get('assign_by', None)
        search = self.request.query_params.get('search', None)
        field_name = self.request.query_params.get('field_name', None)
        order_by = self.request.query_params.get('order_by', None)



        if field_name and order_by:      
            if field_name =='task_code_id' and order_by=='asc':
                sort_field='task_code_id'

            if field_name =='task_code_id' and order_by=='desc':
                sort_field='-task_code_id'

            if field_name =='task_subject' and order_by=='asc':
                sort_field='task_subject'

            if field_name =='task_subject' and order_by=='desc':
                sort_field='-task_subject'

            if field_name =='start_date' and order_by=='asc':
                sort_field='start_date'
                # return self.queryset.all().order_by('duration_end')
            if field_name =='start_date' and order_by=='desc':
                sort_field='-start_date'
                # return self.queryset.all().order_by('-duration_end')

            if field_name =='end_date' and order_by=='asc':
                sort_field='end_date'
                # return self.queryset.all().order_by('duration')
            if field_name =='end_date' and order_by=='desc':
                sort_field='-end_date'
                    # return self.queryset.all().order_by('-duration')
            if field_name =='assign_by' and order_by=='asc':
                sort_field='assign_by'
                # return self.queryset.all().order_by('duration')
            if field_name =='assign_by' and order_by=='desc':
                sort_field='-assign_by'

        if from_date or to_date or assign_by or search:

            if from_date and to_date:
                from_object =datetime.strptime(from_date, '%Y-%m-%d')
                to_object =datetime.strptime(to_date, '%Y-%m-%d')
                filter['end_date__date__gte']= from_object
                filter['end_date__date__lte']= to_object + timedelta(days=1)

            if assign_by:
                filter['assign_by__in'] = list(map(int,assign_by.split(" ")))
            print("filter",filter)
            if search:
                search_data = search
                print('search_data-->',search_data)
                task_code = self.queryset.filter(task_status=2,is_deleted=False,task_code_id__icontains=search_data,**filter).values_list('id',flat=True)
                print('task_code-->',task_code)
                if task_code:
                    return self.queryset.filter((Q(assign_to=user)|Q(sub_assign_to_user=user)),
                                                (Q(id__in=list(task_code))),task_status=2,is_deleted=False,**filter).order_by(sort_field)
                else:
                    id1= self.queryset.filter((Q(assign_to=user)|Q(sub_assign_to_user=user)),**filter).values_list('id',flat=True)
                    id2= self.queryset.filter(Q(task_status=2)&(Q(assign_to=user)|Q(sub_assign_to_user=user)),**filter).values_list('parent_id',flat=True)
                    ids=list(id1)+list(id2)
                    print("ids",ids)
                    check_data = EtaskTask.objects.filter((Q(task_subject__icontains=search_data)),id__in=ids).values_list('id',flat=True)
                    print("check_data",check_data)
                    return self.queryset.filter((Q(assign_to=user)|Q(sub_assign_to_user=user)),
                                                    (Q(parent_id__in=list(check_data))|Q(id__in=list(check_data))),task_status=2,is_deleted=False,**filter).order_by(sort_field)
            else:
                return self.queryset.filter((Q(assign_to=user)|Q(sub_assign_to_user=user)),
                                                task_status=2,is_deleted=False,**filter).order_by(sort_field)     
        else:
            return self.queryset.filter(Q(task_status=2)&(Q(assign_to=user)|Q(sub_assign_to_user=user)),**filter).order_by(sort_field)

    @response_modify_decorator_list_or_get_after_execution_for_pagination
    def get(self, request, *args, **kwargs):
        response = super(EtaskCompletedTaskListView, self).get(self, request, args, kwargs)

        # print('response-->',response.data)
        user = request.user.id

        print('user-->',user)

        for data in response.data['results']:

            comments_count = ETaskComments.objects.filter(task=data['id'],is_deleted=False).count()
            # print('comments_count-->',comments_count)
            data['comments_count'] = comments_count
            
            sub_assign_to_user = User.objects.filter(id=data['sub_assign_to_user'],is_active=True).values('first_name','last_name')
            # print('sub_assign_to_user-->',sub_assign_to_user)
            if user != data['sub_assign_to_user']:
                if sub_assign_to_user:
                    sub_assign_to_user_first_name = sub_assign_to_user[0]['first_name'] if sub_assign_to_user[0]['first_name'] else ''
                    sub_assign_to_user_last_name = sub_assign_to_user[0]['last_name'] if sub_assign_to_user[0]['last_name'] else ''
                    data['sub_assign_to_user'] = sub_assign_to_user_first_name + ' ' +sub_assign_to_user_last_name
            else:
                data['sub_assign_to_user'] = None
                data['assign_to'] = user


            assign_to = User.objects.filter(id=data['assign_to'],is_active=True).values('first_name','last_name')
            if assign_to:
                assign_to_first_name = assign_to[0]['first_name'] if assign_to[0]['first_name'] else ''
                assign_to_last_name = assign_to[0]['last_name'] if assign_to[0]['last_name'] else ''
                data['assign_to'] = assign_to_first_name + ' ' +assign_to_last_name

            if int(data['parent_id']) != 0:
                # parent_id_name = EtaskTask.objects.filter(id=data['id'],task_status=1,is_deleted=False,parent_id=data['parent_id']).values('task_subject')
                parent_id_name = EtaskTask.objects.filter(is_deleted=False,id=data['parent_id']).values('id','task_subject')
                # print('parent_id_name-->',parent_id_name[0]['id'])
                if parent_id_name:
                    data['parent'] = {
                        "id" :  data['parent_id'],
                        "name" :parent_id_name[0]['task_subject']
                    }
            else :
                data['parent'] = None


        return response

class EtaskClosedTaskListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskTask.objects.filter(is_deleted=False)
    serializer_class = EtaskClosedTaskListSerializer
    pagination_class = CSPageNumberPagination

    def get_queryset(self,):
        user = self.request.user.id
        # sub_data = set(EtaskTask.objects.filter(~(Q(parent_id=0)),((Q(sub_assign_to_user__isnull=True)&Q(assign_to=user))|
        #                                     (Q(sub_assign_to_user__isnull=False)&Q(sub_assign_to_user=user))),task_status=4,
        #                                     is_deleted=False).values_list('parent_id', flat=True))
        # # print("sub_data",sub_data)
        # return self.queryset.filter((((Q(sub_assign_to_user__isnull=True)&Q(assign_to=user))|
        #                                 (Q(sub_assign_to_user__isnull=False)&Q(sub_assign_to_user=user)))&Q(task_status=4))|
        #                                 (Q(id__in=sub_data))).order_by('-id')

        filter = {}
        sort_field='-id'
        from_date = self.request.query_params.get('from_date', None)
        to_date = self.request.query_params.get('to_date', None)
        assign_by = self.request.query_params.get('assign_by', None)
        search = self.request.query_params.get('search', None)
        field_name = self.request.query_params.get('field_name', None)
        order_by = self.request.query_params.get('order_by', None)



        if field_name and order_by:      
            if field_name =='task_code_id' and order_by=='asc':
                sort_field='task_code_id'

            if field_name =='task_code_id' and order_by=='desc':
                sort_field='-task_code_id'

            if field_name =='task_subject' and order_by=='asc':
                sort_field='task_subject'

            if field_name =='task_subject' and order_by=='desc':
                sort_field='-task_subject'

            if field_name =='start_date' and order_by=='asc':
                sort_field='start_date'
                # return self.queryset.all().order_by('duration_end')
            if field_name =='start_date' and order_by=='desc':
                sort_field='-start_date'
                # return self.queryset.all().order_by('-duration_end')

            if field_name =='end_date' and order_by=='asc':
                sort_field='end_date'
                # return self.queryset.all().order_by('duration')
            if field_name =='end_date' and order_by=='desc':
                sort_field='-end_date'
                    # return self.queryset.all().order_by('-duration')
            if field_name =='assign_by' and order_by=='asc':
                sort_field='assign_by'
                # return self.queryset.all().order_by('duration')
            if field_name =='assign_by' and order_by=='desc':
                sort_field='-assign_by'

        if from_date or to_date or assign_by or search:
            if from_date and to_date:
                from_object =datetime.strptime(from_date, '%Y-%m-%d')
                to_object =datetime.strptime(to_date, '%Y-%m-%d')
                filter['end_date__date__gte']= from_object
                filter['end_date__date__lte']= to_object + timedelta(days=1)

            if assign_by:
                filter['assign_by__in'] = list(map(int,assign_by.split(" ")))
            print("filter",filter)
            if search:
                search_data = search
                print('search_data-->',search_data)
                task_code = self.queryset.filter(task_status=4,is_deleted=False,task_code_id__icontains=search_data,**filter).values_list('id',flat=True)
                print('task_code-->',task_code)
                if task_code:
                    return self.queryset.filter(((Q(sub_assign_to_user__isnull=True)&Q(assign_to=user))|
                                                (Q(sub_assign_to_user__isnull=False)&Q(sub_assign_to_user=user)))&
                                                Q(task_status=4,is_deleted=False),
                                                (Q(id__in=list(task_code))),**filter).order_by(sort_field)
                else:
                    id1= self.queryset.filter(((Q(sub_assign_to_user__isnull=True)&Q(assign_to=user))|
                                                    (Q(sub_assign_to_user__isnull=False)&Q(sub_assign_to_user=user)))&
                                                Q(task_status=4,is_deleted=False),**filter).values_list('id',flat=True)
                    id2= self.queryset.filter(((Q(sub_assign_to_user__isnull=True)&Q(assign_to=user))|
                                                    (Q(sub_assign_to_user__isnull=False)&Q(sub_assign_to_user=user)))&
                                                Q(task_status=4,is_deleted=False),**filter).values_list('parent_id',flat=True)
                    ids=list(id1)+list(id2)
                    print("ids",ids)

                    print("ids",ids)
                    check_data = EtaskTask.objects.filter((Q(task_subject__icontains=search_data)),id__in=ids).values_list('id',flat=True)
                    print("check_data",check_data)
                    return  self.queryset.filter(((Q(sub_assign_to_user__isnull=True)&Q(assign_to=user))|
                                                (Q(sub_assign_to_user__isnull=False)&Q(sub_assign_to_user=user)))&
                                                Q(task_status=4,is_deleted=False),
                                                (Q(parent_id__in=list(check_data))|Q(id__in=list(check_data))),**filter).order_by(sort_field) 
            else:
                return self.queryset.filter(((Q(sub_assign_to_user__isnull=True)&Q(assign_to=user))|
                                                (Q(sub_assign_to_user__isnull=False)&Q(sub_assign_to_user=user))),
                                                task_status=4,is_deleted=False,**filter).order_by(sort_field)                      
        else:
            return self.queryset.filter((((Q(sub_assign_to_user__isnull=True)&Q(assign_to=user))|
                                        (Q(sub_assign_to_user__isnull=False)&Q(sub_assign_to_user=user)))&Q(task_status=4)),**filter).order_by(sort_field)


    @response_modify_decorator_list_or_get_after_execution_for_pagination
    def get(self, request, *args, **kwargs):
        response = super(EtaskClosedTaskListView, self).get(self, request, args, kwargs)
        user = request.user.id

        # print('response-->',response.data)

        for data in response.data['results']:
            
            assign_by = User.objects.filter(id=data['assign_by'],is_active=True).values('first_name','last_name')
            if assign_by:
                assign_by_first_name = assign_by[0]['first_name'] if assign_by[0]['first_name'] else ''
                assign_by_last_name = assign_by[0]['last_name'] if assign_by[0]['last_name'] else ''
                data['assign_by'] = assign_by_first_name + ' ' +assign_by_last_name


            sub_assign_to_user = User.objects.filter(id=data['sub_assign_to_user'],is_active=True).values('first_name','last_name')
            # print('sub_assign_to_user-->',sub_assign_to_user)
            if user != data['sub_assign_to_user']:
                if sub_assign_to_user:
                    sub_assign_to_user_first_name = sub_assign_to_user[0]['first_name'] if sub_assign_to_user[0]['first_name'] else ''
                    sub_assign_to_user_last_name = sub_assign_to_user[0]['last_name'] if sub_assign_to_user[0]['last_name'] else ''
                    data['sub_assign_to_user'] = sub_assign_to_user_first_name + ' ' +sub_assign_to_user_last_name
            else:
                data['sub_assign_to_user'] = None
                data['assign_to'] = user
            
            if int(data['parent_id']) != 0:
                # parent_id_name = EtaskTask.objects.filter(id=data['id'],task_status=1,is_deleted=False,parent_id=data['parent_id']).values('task_subject')
                parent_id_name = EtaskTask.objects.filter(task_status=1,is_deleted=False,id=data['parent_id']).values('id','task_subject')
                # print('parent_id_name-->',parent_id_name[0]['id'])
                if parent_id_name:
                    data['parent'] = {
                        "id" :  data['parent_id'],
                        "name" :parent_id_name[0]['task_subject']
                    }
            else :
                data['parent'] = None


            ### Time deviation Calculation
            flag1=flag2=0

            if 'end_date' in data.keys() :
                date = data['end_date'].split('T')[0]
                end_date_object = datetime.strptime(date, '%Y-%m-%d').date()
                flag1 = 1
            else:
                flag1 = 0

            if 'end_date' in data.keys() :
                c_date = data['closed_date'].split('T')[0]
                c_date_object = datetime.strptime(c_date, '%Y-%m-%d').date()
                flag2 = 1
            else:
                flag2 = 0

            if flag1 ==1 and flag2==1:
                deviation = (c_date_object - end_date_object)

                if str(deviation) == '0:00:00':
                    print('deviation--> On Time')
                    data['deviation'] = 'On Time'
                else:
                    print('deviation--> ',str(deviation).split(',')[0])
                    data['deviation'] = str(deviation).split(',')[0]


        return response

class EtaskOverdueTaskListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskTask.objects.filter(is_deleted=False)
    serializer_class = EtaskOverdueTaskListSerializer
    pagination_class = CSPageNumberPagination

    def get_queryset(self,):
        user = self.request.user.id
        cur_date = datetime.now().date()

        filter = {}
        sort_field='-id'
        from_date = self.request.query_params.get('from_date', None)
        to_date = self.request.query_params.get('to_date', None)
        assign_by = self.request.query_params.get('assign_by', None)
        search = self.request.query_params.get('search', None)
        field_name = self.request.query_params.get('field_name', None)
        order_by = self.request.query_params.get('order_by', None)



        if field_name and order_by:      
            if field_name =='task_code_id' and order_by=='asc':
                sort_field='task_code_id'

            if field_name =='task_code_id' and order_by=='desc':
                sort_field='-task_code_id'

            if field_name =='task_subject' and order_by=='asc':
                sort_field='task_subject'

            if field_name =='task_subject' and order_by=='desc':
                sort_field='-task_subject'

            if field_name =='start_date' and order_by=='asc':
                sort_field='start_date'
                # return self.queryset.all().order_by('duration_end')
            if field_name =='start_date' and order_by=='desc':
                sort_field='-start_date'
                # return self.queryset.all().order_by('-duration_end')

            if field_name =='end_date' and order_by=='asc':
                sort_field='end_date'
                # return self.queryset.all().order_by('duration')
            if field_name =='end_date' and order_by=='desc':
                sort_field='-end_date'
                    # return self.queryset.all().order_by('-duration')
            if field_name =='assign_by' and order_by=='asc':
                sort_field='assign_by'
                # return self.queryset.all().order_by('duration')
            if field_name =='assign_by' and order_by=='desc':
                sort_field='-assign_by'

        if from_date or to_date or assign_by or search:

            if from_date and to_date:
                from_object =datetime.strptime(from_date, '%Y-%m-%d')
                to_object =datetime.strptime(to_date, '%Y-%m-%d')
                filter['end_date__date__gte']= from_object
                filter['end_date__date__lte']= to_object + timedelta(days=1)

            if assign_by:
                filter['assign_by__in'] = list(map(int,assign_by.split(" ")))
            print("filter",filter)
            if search:
                search_data = search
                print('search_data-->',search_data)
                task_code = self.queryset.filter(task_status=1,is_deleted=False,task_code_id__icontains=search_data,**filter).values_list('id',flat=True)
                print('task_code-->',task_code)
                if task_code:
                    return self.queryset.filter(Q(is_deleted=False)&(Q(assign_by=user)|Q(assign_to=user)|Q(sub_assign_to_user=user))&
                                            ((Q(extended_date__isnull=False)&Q(extend_with_delay=False)&Q(extended_date__date__lt=cur_date)&Q(task_status=1))|
                                            (Q(extended_date__isnull=True)&Q(end_date__date__lt=cur_date)&Q(task_status=1)))&
                                            (Q(task_code_id__icontains=search_data)|Q(task_subject__icontains=search_data)),
                                            (Q(id__in=list(task_code))),**filter).order_by(sort_field)
                else:
                    id1= self.queryset.filter(Q(is_deleted=False)&(Q(assign_by=user)|Q(assign_to=user)|Q(sub_assign_to_user=user))&
                                                ((Q(extended_date__isnull=False)&Q(extend_with_delay=False)&Q(extended_date__date__lt=cur_date)&Q(task_status=1))|
                                                (Q(extended_date__isnull=True)&Q(end_date__date__lt=cur_date)&Q(task_status=1))),**filter).values_list('id',flat=True)
                    id2= self.queryset.filter(Q(is_deleted=False)&(Q(assign_to=user)|Q(sub_assign_to_user=user))&
                                                ((Q(extended_date__isnull=False)&Q(extend_with_delay=False)&Q(extended_date__date__lt=cur_date)&Q(task_status=1))|
                                                (Q(extended_date__isnull=True)&Q(end_date__date__lt=cur_date)&Q(task_status=1))),**filter).values_list('parent_id',flat=True)
                    ids=list(id1)+list(id2)
                    print("ids",ids)
                    check_data = EtaskTask.objects.filter((Q(task_code_id__icontains=search_data)|Q(task_subject__icontains=search_data)),id__in=ids).values_list('id',flat=True)
                    print("check_data",check_data)
                    return self.queryset.filter(Q(is_deleted=False)&(Q(assign_by=user)|Q(assign_to=user)|Q(sub_assign_to_user=user))&
                                            ((Q(extended_date__isnull=False)&Q(extend_with_delay=False)&Q(extended_date__date__lt=cur_date)&Q(task_status=1))|
                                            (Q(extended_date__isnull=True)&Q(end_date__date__lt=cur_date)&Q(task_status=1)))&
                                            (Q(task_code_id__icontains=search_data)|Q(task_subject__icontains=search_data)),
                                            (Q(parent_id__in=list(check_data))|Q(id__in=list(check_data))),**filter).order_by(sort_field)

            else:
                return self.queryset.filter(Q(is_deleted=False)&(Q(assign_by=user)|Q(assign_to=user)|Q(sub_assign_to_user=user))&
                                            ((Q(extended_date__isnull=False)&Q(extend_with_delay=False)&Q(extended_date__date__lt=cur_date)&Q(task_status=1))|
                                            (Q(extended_date__isnull=True)&Q(end_date__date__lt=cur_date)&Q(task_status=1))),**filter).order_by(sort_field)
        else:

            return self.queryset.filter(Q(is_deleted=False)&(Q(assign_by=user)|Q(assign_to=user)|Q(sub_assign_to_user=user))&
                                            ((Q(extended_date__isnull=False)&Q(extend_with_delay=False)&Q(extended_date__date__lt=cur_date)&Q(task_status=1))|
                                            (Q(extended_date__isnull=True)&Q(end_date__date__lt=cur_date)&Q(task_status=1))),**filter).order_by(sort_field)
        

    @response_modify_decorator_list_or_get_after_execution_for_pagination
    def get(self, request, *args, **kwargs):
        response = super(EtaskOverdueTaskListView, self).get(self, request, args, kwargs)

        user = request.user.id
        cur_date = datetime.now().date()
        # print('cur_date-->',cur_date)

        # print('response-->',response.data)

        for data in response.data['results']:

            comments_count = ETaskComments.objects.filter(task=data['id'],is_deleted=False).count()
            data['comments_count'] = comments_count
            
            assign_by = User.objects.filter(id=data['assign_by'],is_active=True).values('first_name','last_name')
            if assign_by:
                assign_by_first_name = assign_by[0]['first_name'] if assign_by[0]['first_name'] else ''
                assign_by_last_name = assign_by[0]['last_name'] if assign_by[0]['last_name'] else ''
                data['assign_by'] = assign_by_first_name + ' ' +assign_by_last_name

            sub_assign_to_user = User.objects.filter(id=data['sub_assign_to_user'],is_active=True).values('first_name','last_name')
            # print('sub_assign_to_user-->',sub_assign_to_user)
            if user != data['sub_assign_to_user']:
                if sub_assign_to_user:
                    sub_assign_to_user_first_name = sub_assign_to_user[0]['first_name'] if sub_assign_to_user[0]['first_name'] else ''
                    sub_assign_to_user_last_name = sub_assign_to_user[0]['last_name'] if sub_assign_to_user[0]['last_name'] else ''
                    data['sub_assign_to_user'] = sub_assign_to_user_first_name + ' ' +sub_assign_to_user_last_name
            else:
                data['sub_assign_to_user'] = None
                data['assign_to'] = user
            
            if int(data['parent_id']) != 0:
                # parent_id_name = EtaskTask.objects.filter(id=data['id'],task_status=1,is_deleted=False,parent_id=data['parent_id']).values('task_subject')
                parent_id_name = EtaskTask.objects.filter(task_status=1,is_deleted=False,id=data['parent_id']).values('id','task_subject')
                # print('parent_id_name-->',parent_id_name[0]['id'])
                if parent_id_name:
                    data['parent'] = {
                        "id" :  data['parent_id'],
                        "name" :parent_id_name[0]['task_subject']
                    }
            else :
                data['parent'] = None

            ## Commented By manas Paul ##
            # if data['end_date'] is not None and data['extended_date'] is None and datetime.strptime(data['end_date'], '%Y-%m-%dT%H:%M:%S').date() < cur_date:
            #     en_date = data['end_date'].split('T')[0]
            #     end_date = datetime.strptime(en_date, '%Y-%m-%d').date()
            #     data['overdue_by'] = str(cur_date - end_date).split(',')[0]
            # else:
            #     data['overdue_by'] = None  
            if data['extended_date']:
                if data['extended_date'] and datetime.strptime(data['extended_date'], '%Y-%m-%dT%H:%M:%S').date() <= cur_date:
                    e_date = data['extended_date'].split('T')[0]
                    extended_date = datetime.strptime(e_date, '%Y-%m-%d').date()
                    days_extended=(cur_date - extended_date).days
                    # print("days_extended",days_extended)
                    if days_extended >0:
                        data['overdue_by'] = days_extended
                    else:
                        data['overdue_by'] = None
            else:
                if data['end_date'] and datetime.strptime(data['end_date'], '%Y-%m-%dT%H:%M:%S').date() <= cur_date:
                    en_date = data['end_date'].split('T')[0]
                    end_date = datetime.strptime(en_date, '%Y-%m-%d').date()
                    days_extended=(cur_date - end_date).days
                    # print("days_extended",days_extended)
                    if days_extended >0:
                        data['overdue_by'] = days_extended
                    else:
                        data['overdue_by'] = None
            
            reporting_date = ETaskReportingDates.objects.filter(task=data['id'],task_type=1,is_deleted=False)
            reporting_list = []
            for r_date in reporting_date:
                # print('r_date.reporting_date-->',r_date.reporting_date)
                if r_date.reporting_date.date() >datetime.now().date():
                    reporting_dict = {
                        "id" : r_date.id,
                        "reporting_dates" : r_date.reporting_date,
                        "reporting_status":r_date.reporting_status,
                        "reporting_status_name":r_date.get_reporting_status_display(),
                        "crossed_by":0
                    }
                    reporting_list.append(reporting_dict)
                else:
                    reporting_dict = {
                        "id" : r_date.id,
                        "reporting_dates" : r_date.reporting_date,
                        "reporting_status":r_date.reporting_status,
                        "reporting_status_name":r_date.get_reporting_status_display(),
                        "crossed_by":(datetime.now().date()-r_date.reporting_date.date ()).days
                    }
                    reporting_list.append(reporting_dict)


            data['reporting_dates'] = reporting_list


        return response

class EtasktaskListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskTask.objects.all()
    serializer_class = EtasktaskListSerializer

    def get(self, request, *args, **kwargs):
        data_dict = {}
        etask_list = []
        etask_dict = {}
        get_etask_list = EtaskTask.objects.filter(is_deleted=False)
        print("get_etask_list-->",get_etask_list)
        for etlist in get_etask_list:
            etask_dict = {
                'id' : etlist.id,
                'parent_id' : etlist.parent_id,
                'task_subject' : etlist.task_subject
            }
            etask_list.append(etask_dict)        

        data_dict['result'] = etask_list
        if etask_list:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_SUCCESS
        elif len(etask_list) == 0:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_NO_DATA
        else:
            data_dict['request_status'] = 0
            data_dict['msg'] = settings.MSG_ERROR

        return Response(data_dict)

class EtaskTaskStatusListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskTask.objects.filter(is_deleted=False,parent_id=0)
    serializer_class = EtaskTaskStatusListSerializer
    pagination_class = CSPageNumberPagination

    @response_modify_decorator_list_or_get_after_execution_for_pagination
    # @response_modify_decorator_list_or_get_before_execution_for_pagination
    def get(self, request, *args, **kwargs):
        cur_date = datetime.now().date()
        print("cur_date",cur_date)
        req_type = self.request.query_params.get('req_type', None)
        data_dict = {}
        response = super(EtaskTaskStatusListView, self).get(self, request, args, kwargs)
        total_data = []
        single_data = []

        sub_data = EtaskTask.objects.filter(~(Q(parent_id=0)),is_deleted=False)

        for data in response.data['results']:
            single_data = data
            sub_list = []
            print("data",data['end_date'])  #2019-10-30T15:52:39
            print("khfihv",datetime.strptime(data['end_date'],'%Y-%m-%dT%H:%M:%S'))
            if req_type == 'completed':
                complete_data = sub_data.filter(task_status=2,parent_id=data['id']).values()
                single_data['sub_task']=complete_data
                if complete_data:
                    total_data.append(single_data)
                # else:
                #     if data['task_status']==2:
                #         assign_to = EtaskAssignTo.objects.filter(task=data['id']).values('assign_to_user')
                #         print("assign_to",assign_to) ####
                #         single_data = data
                #         total_data.append(single_data)

            elif req_type == 'closed':
                complete_data = sub_data.filter(task_status=4,parent_id=data['id']).values()
                single_data['sub_task']=complete_data
                if complete_data:
                    total_data.append(single_data)
                else:
                    if data['task_status']==4:
                        single_data = data
                        total_data.append(single_data)

            elif req_type == 'overdue':
                new_list = []
                ext_overdue_data = sub_data.filter((Q(extended_date__isnull=False,extended_date__date__lt=cur_date)|
                                                    (Q(extended_date__isnull=True,end_date__date__lt=cur_date))
                                                    ),task_status=1,parent_id=data['id']).values()
                if ext_overdue_data:
                    for i in ext_overdue_data:
                        if i['extended_date'] is not None:
                            i['overdue_by_day']= (cur_date - i['extended_date'].date()).days
                        elif i['end_date'] is not None:
                            i['overdue_by_day']= (cur_date - i['end_date'].date()).days
                        assigned_by = ""
                        name = User.objects.filter(id=i['owner_id']).values('first_name','last_name')
                        if name:
                            assigned_by = name[0]['first_name']+" "+name[0]['last_name']

                        i['assigned_by'] = assigned_by
                        
                single_data['sub_task']=ext_overdue_data
                if ext_overdue_data:
                    total_data.append(single_data)
                else:
                    if data['task_status']==1 and ((data['extended_date'] is not None and\
                         datetime.strptime(data['extended_date'],'%Y-%m-%dT%H:%M:%S').date()<cur_date)or\
                        (data['extended_date'] is None and datetime.strptime(data['end_date'],'%Y-%m-%dT%H:%M:%S').date()<cur_date)):
                        if data['extended_date'] is not None:
                            data['overdue_by_day']= (cur_date - datetime.strptime(data['extended_date'],'%Y-%m-%dT%H:%M:%S').date()).days
                        elif data['end_date'] is not None:
                            data['overdue_by_day']= (cur_date - datetime.strptime(data['end_date'],'%Y-%m-%dT%H:%M:%S').date()).days

                        assigned_by = ""
                        name = User.objects.filter(id=data['owner']).values('first_name','last_name')
                        if name:
                            assigned_by = name[0]['first_name']+" "+name[0]['last_name']
                        data['assigned_by'] = assigned_by
                        single_data = data
                        total_data.append(single_data)


        response.data['results'] = total_data


        # usercc_dict = {}
        # assignto_dict = {}
        # subtask_dict = {}
        # for data in response.data['results']:
        #     print("if : task_type-->",data['task_type'])
        #     user_name = User.objects.filter(id=data['owner']).values('first_name','last_name')
        #     data['owner'] = user_name[0]['first_name'] + " " + user_name[0]['last_name']
        #     # get_sub_task = EtaskTask.objects.filter(parent_id=data['id'])
        #     et_reporting_dates = ETaskReportingDates.objects.filter(task=data['id']).values('reporting_date')
        #     data['r_date'] = et_reporting_dates if et_reporting_dates else '[]'

        #     if data['task_type'] == 3:
        #         data['sub_task'] = data['task_subject']
        #         data['sub_task_description'] = data['task_description']
        #         get_parent_details = EtaskTask.objects.filter(id=data['parent_id'],is_deleted=False)
        #         for p_details in get_parent_details:
        #             data['task_subject'] = p_details.task_subject
        #             data['task_description'] = p_details.task_description                    
        return response

  
class ETaskAllTasklist(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskTask.objects.filter(is_deleted=False)
    serializer_class = ETaskAllTasklistSerializer
    pagination_class = CSPageNumberPagination

    def get_queryset(self):
        user = self.request.user.id
        # print('user',user)
        user_list_rh=(list(TCoreUserDetail.objects.filter((Q(hod_id=user)|Q(reporting_head_id=user)),cu_is_deleted=False).values_list('cu_user',flat=True).iterator()))
        user_list_rh.append(user)
        # print('user_list_rh',user_list_rh)

        filter = {}
        sort_field='-id'
        from_date = self.request.query_params.get('from_date', None)
        to_date = self.request.query_params.get('to_date', None)
        assign_by = self.request.query_params.get('assign_by', None)
        search = self.request.query_params.get('search', None)
        field_name = self.request.query_params.get('field_name', None)
        order_by = self.request.query_params.get('order_by', None)



        if field_name and order_by:      
            if field_name =='task_code_id' and order_by=='asc':
                sort_field='task_code_id'

            if field_name =='task_code_id' and order_by=='desc':
                sort_field='-task_code_id'

            if field_name =='task_subject' and order_by=='asc':
                sort_field='task_subject'

            if field_name =='task_subject' and order_by=='desc':
                sort_field='-task_subject'

            if field_name =='start_date' and order_by=='asc':
                sort_field='start_date'
                # return self.queryset.all().order_by('duration_end')
            if field_name =='start_date' and order_by=='desc':
                sort_field='-start_date'
                # return self.queryset.all().order_by('-duration_end')

            if field_name =='end_date' and order_by=='asc':
                sort_field='end_date'
                # return self.queryset.all().order_by('duration')
            if field_name =='end_date' and order_by=='desc':
                sort_field='-end_date'
                    # return self.queryset.all().order_by('-duration')
            if field_name =='assign_by' and order_by=='asc':
                sort_field='assign_by'
                # return self.queryset.all().order_by('duration')
            if field_name =='assign_by' and order_by=='desc':
                sort_field='-assign_by'

        if from_date or to_date or assign_by or search:

            if from_date and to_date:
                from_object =datetime.strptime(from_date, '%Y-%m-%d')
                to_object =datetime.strptime(to_date, '%Y-%m-%d')
                filter['end_date__date__gte']= from_object
                filter['end_date__date__lte']= to_object + timedelta(days=1)

            if assign_by:
                filter['assign_by__in'] = list(map(int,assign_by.split(" ")))
            print("filter",filter)
            if search:
                search_data = search
                print('search_data-->',search_data)
                task_code = self.queryset.filter(is_deleted=False,task_code_id__icontains=search_data,**filter).values_list('id',flat=True)
                print('task_code-->',task_code)
                if task_code:
                    return self.queryset.filter((Q(assign_to__in=user_list_rh)|Q(assign_by__in=user_list_rh)|Q(sub_assign_to_user__in=user_list_rh)|Q(owner__in=user_list_rh)),
                                                    (Q(id__in=list(task_code))), is_deleted=False,**filter).order_by(sort_field)
                else:
                    id1= self.queryset.filter((Q(assign_to__in=user_list_rh)|Q(assign_by__in=user_list_rh)|Q(sub_assign_to_user__in=user_list_rh)|Q(owner__in=user_list_rh)),
                                                is_deleted=False,**filter).values_list('id',flat=True)
                    id2= self.queryset.filter((Q(assign_to__in=user_list_rh)|Q(assign_by__in=user_list_rh)|Q(sub_assign_to_user__in=user_list_rh)|Q(owner__in=user_list_rh)),
                                                        is_deleted=False,**filter).values_list('parent_id',flat=True)
                    ids=list(id1)+list(id2)
                    print("ids",ids)
                    check_data = EtaskTask.objects.filter(id__in=ids,task_subject__icontains=search_data).values_list('id',flat=True)
                    print("check_data",check_data)
                    return self.queryset.filter((Q(assign_to__in=user_list_rh)|Q(assign_by__in=user_list_rh)|Q(sub_assign_to_user__in=user_list_rh)|Q(owner__in=user_list_rh)),
                                                    (Q(parent_id__in=list(check_data))|Q(id__in=list(check_data))),
                                                        is_deleted=False,**filter).order_by(sort_field)                            
            else:
                queryset = self.queryset.filter((Q(assign_to__in=user_list_rh)|Q(assign_by__in=user_list_rh)|Q(sub_assign_to_user__in=user_list_rh)|Q(owner__in=user_list_rh)),
                                                is_deleted=False,**filter).order_by(sort_field)    
                return queryset                     
        else:
            return self.queryset.filter(Q(assign_to__in=user_list_rh)|Q(assign_by__in=user_list_rh)|Q(sub_assign_to_user__in=user_list_rh)|Q(owner__in=user_list_rh),
                                            **filter).order_by(sort_field)
        # print('result',result)
        # return result
    @response_modify_decorator_list_or_get_after_execution_for_pagination
    def get(self,request,*args,**kwargs):
        response=super(ETaskAllTasklist,self).get(self,request,args,kwargs)
        current_date = datetime.now().date()
        # print('current_date',current_date)
        for data in response.data['results']:
            comments_count = ETaskComments.objects.filter(task=data['id'],is_deleted=False).count()
            data['comments_count'] = comments_count
            #modification by abhisek
            report_date=ETaskReportingDates.objects.filter(task_type=1,task=data['id'],is_deleted=False).values('id','reporting_date')
           #koushik --code 
            # print('report_date',report_date)
            # report_date_list=[]
            # if report_date:
            #     for r_d in report_date:
            #         if r_d.reporting_date.date()<= current_date:
            #             report_data={
            #                 'id':r_d.id,
            #                 'reporting_date':r_d.reporting_date
            #             }
            #             report_date_list.append(report_data)

            data['reporting_dates']=report_date if report_date else []  
            data['task_status_id']=data['task_status']
            data['task_status']=data['task_status_name']
            data['task_overdue_days'] = None
            ids = report_date.filter().values_list('id',flat=True)
            print('ids',ids)
            reporting_action_log_final = []
            # reporting_action_log=ETaskReportingActionLog.objects.filter((Q(reporting_date__in=ids)|Q(reporting_date__isnull=True)),
            reporting_action_log=ETaskReportingActionLog.objects.filter(reporting_date__in=ids,
                                                                    task=data['id'],is_deleted=False).values('task','reporting_date__id',
                                                                    'reporting_date__reporting_date','updated_date','status')
            
            print("reporting_action_log",reporting_action_log)
            for x in reporting_action_log:
                # print('')
                reporting_log_dict={
                    'task':x['task'],
                    'reporting_date__id':x['reporting_date__id'],
                    'reporting_date':x['reporting_date__reporting_date'],
                    'updated_date':x['updated_date'],
                    'reporting_status':ETaskReportingActionLog.status_choice[x['status']-1][1]
                }
                reporting_action_log_final.append(reporting_log_dict)
            print("reporting_action_log",reporting_action_log_final)
            # reporting_action_list=[]                                                      
            # if reporting_action_log:
            #     for r_a in reporting_action_log:
            #         action_data={
            #             'id':r_a.id,
            #             'date_of_update':r_a.updated_date,
            #             'team_update':r_a.get_status_display()
            #         }
            #         reporting_action_list.append(action_data)         
            data['date_of_update_and_team_update']=reporting_action_log_final if reporting_action_log_final else []
            # else:                
            #     data['date_of_update_and_team_update']=[]
            # if data['extended_date']:
            #     e_date = datetime.strptime(datetime.strftime(datetime.strptime(data['extended_date'],"%Y-%m-%dT%H:%M:%S.%f"),"%Y-%m-%dT%H:%M:%S"),"%Y-%m-%dT%H:%M:%S").date()
            # if data['end_date']:
            #     en_date = datetime.strptime(datetime.strftime(datetime.strptime(data['end_date'],"%Y-%m-%dT%H:%M:%S.%f"),"%Y-%m-%dT%H:%M:%S"),"%Y-%m-%dT%H:%M:%S").date()
            # print('aff',type(data['end_date']))
            if data['task_status_name'] == 'Closed':
                data['task_status']=data['task_status_name']
                data['task_overdue_days'] = None

            elif data['task_status_name'] == 'Completed':
                data['task_status']=data['task_status_name']
                reporting_action_log=ETaskReportingActionLog.objects.filter((Q(reporting_date__in=ids)|Q(reporting_date__isnull=True)),
                                                            
                                                            task=data['id'],is_deleted=False).values_list('updated_date',flat=True)
                data['task_completed_date'] = reporting_action_log[0] if reporting_action_log else None
            elif data['extended_date']:
                if data['extended_date'] and datetime.strptime(data['extended_date'],"%Y-%m-%dT%H:%M:%S").date() <= current_date:
                    e_date = data['extended_date'].split('T')[0]
                    extended_date = datetime.strptime(e_date, '%Y-%m-%d').date()
                    days_extended=(current_date - extended_date).days
                    print("days_extended",days_extended)
                    if days_extended >0:
                        data['task_status']="overdue"
                        data['task_overdue_days'] = days_extended
                    else:
                        # print("data['task_status_name']",data['task_status_name'])
                        data['task_status']=data['task_status_name']
                        data['task_overdue_days'] = None
            else:
                if data['end_date'] and datetime.strptime(data['end_date'],"%Y-%m-%dT%H:%M:%S").date() <= current_date:
                    en_date = data['end_date'].split('T')[0]
                    end_date = datetime.strptime(en_date, '%Y-%m-%d').date()
                    days_extended=(current_date - end_date).days
                    print("days_extended",days_extended)
                    if days_extended >0:
                        data['task_status']="overdue"
                        data['task_overdue_days'] = days_extended
                    else:
                        data['task_status']=data['task_status_name']
                        data['task_overdue_days'] = None
            # else:
            #     data['task_status']=data['task_status_name']
                # data['task_overdue_days'] = None
            
        return response

class ETaskUpcomingCompletionListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskTask.objects.filter(is_deleted=False)
    serializer_class = ETaskUpcomingCompletionListSerializer
    pagination_class = CSPageNumberPagination

    def get_queryset(self):
        user = self.request.user.id
        cur_date = datetime.now().date()

        filter = {}
        sort_field='-id'
        from_date = self.request.query_params.get('from_date', None)
        to_date = self.request.query_params.get('to_date', None)
        assign_by = self.request.query_params.get('assign_by', None)
        search = self.request.query_params.get('search', None)
        field_name = self.request.query_params.get('field_name', None)
        order_by = self.request.query_params.get('order_by', None)



        if field_name and order_by:      
            if field_name =='task_code_id' and order_by=='asc':
                sort_field='task_code_id'

            if field_name =='task_code_id' and order_by=='desc':
                sort_field='-task_code_id'

            if field_name =='task_subject' and order_by=='asc':
                sort_field='task_subject'

            if field_name =='task_subject' and order_by=='desc':
                sort_field='-task_subject'

            if field_name =='start_date' and order_by=='asc':
                sort_field='start_date'
                # return self.queryset.all().order_by('duration_end')
            if field_name =='start_date' and order_by=='desc':
                sort_field='-start_date'
                # return self.queryset.all().order_by('-duration_end')

            if field_name =='end_date' and order_by=='asc':
                sort_field='end_date'
                # return self.queryset.all().order_by('duration')
            if field_name =='end_date' and order_by=='desc':
                sort_field='-end_date'
                    # return self.queryset.all().order_by('-duration')
            if field_name =='assign_by' and order_by=='asc':
                sort_field='assign_by'
                # return self.queryset.all().order_by('duration')
            if field_name =='assign_by' and order_by=='desc':
                sort_field='-assign_by'

        if from_date or to_date or assign_by or search:

            if from_date and to_date:
                from_object =datetime.strptime(from_date, '%Y-%m-%d')
                to_object =datetime.strptime(to_date, '%Y-%m-%d')
                filter['end_date__date__gte']= from_object
                filter['end_date__date__lte']= to_object + timedelta(days=1)

            if assign_by:
                filter['assign_by__in'] = list(map(int,assign_by.split(" ")))
            print("filter",filter)
            if search:
                search_data = search

                print('search_data-->',search_data)
                task_code = self.queryset.filter(task_status=1,is_deleted=False,task_code_id__icontains=search_data,**filter).values_list('id',flat=True)
                print('task_code-->',task_code)
                if task_code:
                    return self.queryset.filter(((Q(sub_assign_to_user__isnull=True)&Q(end_date__date__gte=cur_date)&Q(assign_to=user))|
                                            (Q(sub_assign_to_user__isnull=False)&Q(end_date__date__gte=cur_date)&Q(sub_assign_to_user=user)))&
                                            Q(task_status=1,is_deleted=False),
                                            (Q(id__in=list(task_code))),**filter).order_by(sort_field)
                else:
                    id1= self.queryset.filter(((Q(sub_assign_to_user__isnull=True)&Q(end_date__date__gte=cur_date)&Q(assign_to=user))|
                                                    (Q(sub_assign_to_user__isnull=False)&Q(end_date__date__gte=cur_date)&Q(sub_assign_to_user=user)))&
                                                Q(task_status=1,is_deleted=False),**filter).values_list('id',flat=True)
                    id2= self.queryset.filter(((Q(sub_assign_to_user__isnull=True)&Q(end_date__date__gte=cur_date)&Q(assign_to=user))|
                                                    (Q(sub_assign_to_user__isnull=False)&Q(end_date__date__gte=cur_date)&Q(sub_assign_to_user=user)))&
                                                Q(task_status=1,is_deleted=False),**filter).values_list('parent_id',flat=True)
                    ids=list(id1)+list(id2)

                    print("ids",ids)
                    check_data = EtaskTask.objects.filter(id__in=ids,task_subject__icontains=search_data).values_list('id',flat=True)
                    print("check_data",check_data)
                    return self.queryset.filter(((Q(sub_assign_to_user__isnull=True)&Q(end_date__date__gte=cur_date)&Q(assign_to=user))|
                                                (Q(sub_assign_to_user__isnull=False)&Q(end_date__date__gte=cur_date)&Q(sub_assign_to_user=user)))&
                                                Q(task_status=1,is_deleted=False),
                                                (Q(parent_id__in=list(check_data))|Q(id__in=list(check_data))),**filter).order_by(sort_field)

            else:
                return self.queryset.filter(((Q(sub_assign_to_user__isnull=True)&Q(end_date__date__gte=cur_date)&Q(assign_to=user))|
                                                (Q(sub_assign_to_user__isnull=False)&Q(end_date__date__gte=cur_date)&Q(sub_assign_to_user=user))),
                                                task_status=1,is_deleted=False,**filter).order_by(sort_field)                       
        else:
            return self.queryset.filter((((Q(sub_assign_to_user__isnull=True)&Q(end_date__date__gte=cur_date)&Q(assign_to=user))|
                                        (Q(sub_assign_to_user__isnull=False)&Q(end_date__date__gte=cur_date)&Q(sub_assign_to_user=user)))&
                                        Q(task_status=1)),**filter).order_by(sort_field)

    @response_modify_decorator_list_or_get_after_execution_for_pagination
    def get(self, request, *args, **kwargs):
        user = request.user.id

        response = super(ETaskUpcomingCompletionListView, self).get(self, request, args, kwargs)
        print("response",response.data)
        user = request.user.id
        cur_date = datetime.now().date()

        for data in response.data['results']:

            comments_count = ETaskComments.objects.filter(task=data['id'],is_deleted=False).count()
            print("comments_count",comments_count)
            data['comments_count'] = comments_count
            
            assign_by = User.objects.filter(id=data['assign_by'],is_active=True).values('first_name','last_name')
            if assign_by:
                assign_by_first_name = assign_by[0]['first_name'] if assign_by[0]['first_name'] else ''
                assign_by_last_name = assign_by[0]['last_name'] if assign_by[0]['last_name'] else ''
                data['assign_by'] = assign_by_first_name + ' ' +assign_by_last_name

            sub_assign_to_user = User.objects.filter(id=data['sub_assign_to_user'],is_active=True).values('first_name','last_name')
            # print('sub_assign_to_user-->',sub_assign_to_user)
            if user != data['sub_assign_to_user']:
                if sub_assign_to_user:
                    sub_assign_to_user_first_name = sub_assign_to_user[0]['first_name'] if sub_assign_to_user[0]['first_name'] else ''
                    sub_assign_to_user_last_name = sub_assign_to_user[0]['last_name'] if sub_assign_to_user[0]['last_name'] else ''
                    data['sub_assign_to_user'] = sub_assign_to_user_first_name + ' ' +sub_assign_to_user_last_name
            else:
                data['sub_assign_to_user'] = None
                data['assign_to'] = user
            
            if int(data['parent_id']) != 0:
                # parent_id_name = EtaskTask.objects.filter(id=data['id'],task_status=1,is_deleted=False,parent_id=data['parent_id']).values('task_subject')
                parent_id_name = EtaskTask.objects.filter(task_status=1,is_deleted=False,id=data['parent_id']).values('id','task_subject')
                # print('parent_id_name-->',parent_id_name[0]['id'])
                if parent_id_name:
                    data['parent'] = {
                        "id" :  data['parent_id'],
                        "name" :parent_id_name[0]['task_subject']
                    }
            else :
                data['parent'] = None

            date = data['end_date'].split('T')[0]
            end_date_object = datetime.strptime(date, '%Y-%m-%d').date()
            if end_date_object == cur_date:
                data['date_of_completion'] = "0 day left"
            else:
                date_of_completion = end_date_object - cur_date
                data['date_of_completion'] = str(date_of_completion).split(',')[0] + ' left'

            # print('date_of_completion-->',date_of_completion)

            
        
        return response


class EtaskTaskCompleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskTask.objects.filter(is_deleted=False)
    serializer_class = EtaskTaskCompleteViewSerializer

    @response_modify_decorator_update
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

class EtaskMyTaskTodaysPlannerListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskTask.objects.filter(is_deleted=False)#parent_id=0)
    serializer_class = EtaskMyTaskTodaysPlannerListSerializer
    pagination_class = CSPageNumberPagination

    def get_queryset(self,):
        user = self.request.user.id
        cur_date = datetime.now().date()
       
        return self.queryset.filter(Q(task_status=1,is_deleted=False)&
                                   (Q(start_date__date__lte=cur_date)&Q(end_date__date__gte=cur_date)|
                                   Q(end_date__date__lte=cur_date)& Q(extended_date__date__gte=cur_date))&
                                   (Q(assign_to=user)|Q(sub_assign_to_user=user))).order_by('-id')

    @response_modify_decorator_list_or_get_after_execution_for_pagination
    def get(self, request, *args, **kwargs):
        response = super(EtaskMyTaskTodaysPlannerListView, self).get(self, request, args, kwargs)
        user = self.request.user.id
        print('response.data-->',response.data)

        for data in response.data['results']:
            comments_count = ETaskComments.objects.filter(task=data['id'],is_deleted=False).count()
            data['comments_count'] = comments_count

            assign_by = User.objects.filter(id=data['assign_by'],is_active=True).values('first_name','last_name')
            if assign_by:
                assign_by_first_name = assign_by[0]['first_name'] if assign_by[0]['first_name'] else ''
                assign_by_last_name = assign_by[0]['last_name'] if assign_by[0]['last_name'] else ''
                data['assign_by'] = assign_by_first_name + ' ' +assign_by_last_name

            sub_assign_to_user = User.objects.filter(id=data['sub_assign_to_user'],is_active=True).values('first_name','last_name')
            # print('sub_assign_to_user-->',sub_assign_to_user)
            if user != data['sub_assign_to_user']:
                if sub_assign_to_user:
                    sub_assign_to_user_first_name = sub_assign_to_user[0]['first_name'] if sub_assign_to_user[0]['first_name'] else ''
                    sub_assign_to_user_last_name = sub_assign_to_user[0]['last_name'] if sub_assign_to_user[0]['last_name'] else ''
                    data['sub_assign_to_user_id'] = data['sub_assign_to_user']
                    data['sub_assign_to_user'] = sub_assign_to_user_first_name + ' ' +sub_assign_to_user_last_name
            else:
                data['sub_assign_to_user'] = None
                data['sub_assign_to_user_id'] = None
                data['assign_to'] = user


            if int(data['parent_id']) != 0:
                # parent_id_name = EtaskTask.objects.filter(id=data['id'],task_status=1,is_deleted=False,parent_id=data['parent_id']).values('task_subject')
                parent_id_name = EtaskTask.objects.filter(task_status=1,is_deleted=False,id=data['parent_id']).values('id','task_subject')
                # print('parent_id_name-->',parent_id_name[0]['id'])
                if parent_id_name:
                    data['parent'] = {
                        "id" :  data['parent_id'],
                        "name" :parent_id_name[0]['task_subject']
                    }
            else :
                data['parent'] = None

            # reporting_date = ETaskReportingDates.objects.filter(task=data['id'],task_type=1,is_deleted=False,reporting_status=False)
            # reporting_list = []
            # for r_date in reporting_date:
            #     # print('r_date.reporting_date-->',type(r_date.reporting_date))
            #     reporting_dict = {
            #         "id" : r_date.id,
            #         "reporting_dates" : r_date.reporting_date
            #     }
            #     reporting_list.append(reporting_dict)

            # data['reporting_dates'] = reporting_list

        return response

class EtaskEndDateExtensionRequestView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskTask.objects.filter(is_deleted=False)
    serializer_class =  EtaskEndDateExtensionRequestSerializer

    @response_modify_decorator_update
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

class EtaskExtensionsListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskTask.objects.filter(is_deleted=False,is_reject=False,extended_date__isnull=True,requested_end_date__isnull=False)
    serializer_class = EtaskExtensionsListSerializer
    pagination_class = CSPageNumberPagination
    def get_queryset(self):
        # user=self.request.user
        # print('user',user)
        # users_list=(list(TCoreUserDetail.objects.filter((Q(reporting_head=user)|Q(hod=user)),cu_is_deleted=False).values_list('cu_user',flat=True)))
        login_user_details = self.request.user
        login_user = int(self.request.user.id)
        users_list=[login_user]
        is_hod = TCoreUserDetail.objects.filter(
                            hod = login_user_details,cu_is_deleted=False,cu_user__isnull=False)
        #print('is_hod',is_hod)
        hi_user_list_details = ''
        if is_hod:
            department_d = TCoreUserDetail.objects.filter(
                cu_user = login_user_details,cu_is_deleted=False,cu_user__isnull=False).values_list('department',flat=True)
            #print('department_d',department_d)
            if department_d:
                hi_user_list_details = TCoreUserDetail.objects.filter(department__in=department_d).values_list('cu_user',flat=True)
                #print('hi_user_list_details',hi_user_list_details)
                
        else:
            hi_user_list_details = TCoreUserDetail.objects.filter(
                reporting_head = login_user_details,cu_is_deleted=False,cu_user__isnull=False).values_list('cu_user',flat=True)
            #print('hi_user_list_details',list(hi_user_list_details))
            hi_user_details1 = ''
            if hi_user_list_details.count() > 0 :
                for hi_user_details in hi_user_list_details:
                    hi_user_list_details = self.getLowerLevelUserList(str(hi_user_details),list(hi_user_list_details))
                
        print('hi_user_list_details',hi_user_list_details)
        if hi_user_list_details:
            users_list+=hi_user_list_details
            print("users_list",users_list)        
        if users_list:
            users_list.append(self.request.user.id)
            print('users_list',users_list)
            filter = {}
            sort_field='-id'
            from_date = self.request.query_params.get('from_date', None)
            to_date = self.request.query_params.get('to_date', None)
            assign_by = self.request.query_params.get('assign_by', None)
            search = self.request.query_params.get('search', None)
            field_name = self.request.query_params.get('field_name', None)
            order_by = self.request.query_params.get('order_by', None)
            parent_task = self.request.query_params.get('parent_task', None)
            request_by = self.request.query_params.get('request_by', None)

            if parent_task:
                filter['parent_id'] = parent_task

            if request_by:
                filter['requested_by'] = request_by

            if field_name and order_by:      
                if field_name =='task_subject' and order_by=='asc':
                    sort_field='task_subject'
                if field_name =='task_subject' and order_by=='desc':
                    sort_field='-task_subject'

                if field_name =='start_date' and order_by=='asc':
                    sort_field='start_date'                   
                if field_name =='start_date' and order_by=='desc':
                    sort_field='-start_date'
                    
                if field_name =='end_date' and order_by=='asc':
                    sort_field='end_date'                    
                if field_name =='end_date' and order_by=='desc':
                    sort_field='-end_date'
                       
                if field_name =='extension_date' and order_by=='asc':
                    sort_field='requested_end_date'
                if field_name =='extension_date' and order_by=='desc':
                    sort_field='-requested_end_date'

                if field_name =='requested_by' and order_by=='asc':
                    sort_field='requested_by'
                if field_name =='requested_by' and order_by=='desc':
                    sort_field='-requested_by'

               
            if from_date or to_date or assign_by or search:

                if from_date and to_date:
                    from_object =datetime.strptime(from_date, '%Y-%m-%d')
                    to_object =datetime.strptime(to_date, '%Y-%m-%d')
                    filter['end_date__date__gte']= from_object
                    filter['end_date__date__lte']= to_object + timedelta(days=1)

                if assign_by:
                    filter['assign_by__in'] = list(map(int,assign_by.split(" ")))
                
                if search:
                    search_data = search
                    print('search_data-->',search_data)
                    task_code = self.queryset.filter(task_code_id__icontains=search_data,**filter).values_list('id',flat=True)
                    print('task_code-->',task_code)
                    if task_code:
                        return self.queryset.filter((Q(assign_to__in=users_list)|Q(assign_by__in=users_list)|Q(sub_assign_to_user__in=users_list)|Q(owner__in=users_list)),
                                                    (Q(id__in=list(task_code))),**filter).order_by(sort_field)
                    else:
                        id1= self.queryset.filter((Q(assign_to__in=users_list)|Q(assign_by__in=users_list)|Q(sub_assign_to_user__in=users_list)|Q(owner__in=users_list)),
                                                            **filter).values_list('id',flat=True)
                        id2= self.queryset.filter((Q(assign_to__in=users_list)|Q(assign_by__in=users_list)|Q(sub_assign_to_user__in=users_list)|Q(owner__in=users_list)),
                                                           **filter).values_list('parent_id',flat=True)
                        ids=list(id1)+list(id2)
                        print("ids",ids)
                        check_data = EtaskTask.objects.filter(id__in=ids,task_subject__icontains=search_data).values_list('id',flat=True)
                        print("check_data",check_data)
                        return self.queryset.filter((Q(assign_to__in=users_list)|Q(assign_by__in=users_list)|Q(sub_assign_to_user__in=users_list)|Q(owner__in=users_list)),
                                                    (Q(parent_id__in=list(check_data))|Q(id__in=list(check_data))),
                                                    **filter).order_by(sort_field)                 
                    # return queryset
                else:
                    queryset = self.queryset.filter((Q(assign_to__in=users_list)|Q(assign_by__in=users_list)|Q(sub_assign_to_user__in=users_list)|Q(owner__in=users_list)),
                                                    **filter).order_by(sort_field)    
                    return queryset                     
            else:
                return self.queryset.filter((Q(assign_to__in=users_list)|Q(assign_by__in=users_list)|Q(sub_assign_to_user__in=users_list)|Q(owner__in=users_list)),**filter).order_by(sort_field)
                                          
        else:
            return self.queryset.none()


    @response_modify_decorator_list_or_get_after_execution_for_pagination
    def get(self,request,*args,**kwargs):
        response=super(EtaskExtensionsListView,self).get(self,request,args,kwargs)
        for data in response.data['results']:
            data['requested_by_name']=userdetails(data['requested_by'])
        return response

    def getLowerLevelUserList(self, user_id='',main_list='') -> list:
        try:
            #print('user_id',user_id)
            #print('main_list',main_list)
            hi_user_list_details =TCoreUserDetail.objects.filter(reporting_head_id = str(user_id),cu_is_deleted=False,cu_user__isnull=False).values_list(
                'cu_user_id',flat=True)
            #print('hi_user_list_details1111',hi_user_list_details)
            if hi_user_list_details.count() > 0 :
                for hi_user_details in hi_user_list_details:
                    main_list.append(hi_user_details)
                    self.getLowerLevelUserList(str(hi_user_details),main_list)
            return main_list
        except Exception as e:
            raise e

class EtaskExtensionsRejectView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskTask.objects.filter(is_deleted=False,is_reject=False,extended_date__isnull=True)
    serializer_class = EtaskExtensionsRejectSerializer
    
class EtaskTaskDateExtendedView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskTask.objects.filter(is_deleted=False)
    serializer_class = EtaskTaskDateExtendedViewSerializer

    @response_modify_decorator_update
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

class EtaskTaskDateExtendedWithDelayView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskTask.objects.filter(is_deleted=False)
    serializer_class = EtaskTaskDateExtendedWithDelaySerializer

    @response_modify_decorator_update
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

class EtaskTaskReopenAndExtendWithDelayView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskTask.objects.filter(is_deleted=False)
    serializer_class = EtaskTaskReopenAndExtendWithDelaySerializer

    @response_modify_decorator_update
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

class EtaskTaskStartDateShiftView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskTask.objects.filter(is_deleted=False)
    serializer_class = EtaskTaskStartDateShiftSerializer

class EtaskAllTypeTaskCountView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskTask.objects.filter(is_deleted=False)
    serializer_class = EtaskAllTypeTaskCountViewSerializer

    # def get_queryset(self):
    #     user = self.request.user.id
    #     # print('user-->',user)
    #     return self.queryset.filter(assign_to=user,is_deleted=False)

    def get(self, request, *args, **kwargs):
        user = self.request.user.id
        cur_date = datetime.now().date()

        data = {}
        data_dict = {}
        print("user ",user,type(user))
        my_task_count = EtaskTask.objects.filter(assign_to=user,is_deleted=False,task_status=1).count()
        print('my_task_count-->',my_task_count)
        # my_comment_count=ETaskComments.objects.filter(task__in=my_task_count,is_deleted=False).count()
        data['my_task_count'] = my_task_count
        
        over_due_count = EtaskTask.objects.filter((Q(assign_to=user)|Q(sub_assign_to_user=user))&
                                            ((Q(extended_date__isnull=False)&Q(extend_with_delay=False)&Q(extended_date__date__lt=cur_date)&Q(task_status=1))|
                                            (Q(extended_date__isnull=True)&Q(end_date__date__lt=cur_date)&Q(task_status=1))),is_deleted=False).count()

        # over_due_count = EtaskTask.objects.filter(Q(is_deleted=False)&(Q(assign_to=user)|Q(sub_assign_to_user=user))&
        #                                 (Q(extended_date__isnull=False)&Q(extended_date__date__gt=cur_date)&Q(task_status=1))|
        #                                 (Q(extended_date__isnull=True)&Q(end_date__date__lt=cur_date)&Q(task_status=1))).count()
        print('over_due_count-->',over_due_count)
        data['over_due_count'] = over_due_count

        completed_task_count = EtaskTask.objects.filter(Q(task_status=2)&(Q(assign_to=user)|Q(sub_assign_to_user=user))).count()
        print('completed_task_count-->',completed_task_count)
        data['completed_task_count'] = completed_task_count

        closed_task_count = EtaskTask.objects.filter((((Q(sub_assign_to_user__isnull=True)&Q(assign_to=user))|
                                        (Q(sub_assign_to_user__isnull=False)&Q(sub_assign_to_user=user)))&Q(task_status=4))).count()
        print('closed_task_count-->',closed_task_count)
        data['closed_task_count'] = closed_task_count

        followup_count = EtaskFollowUP.objects.filter(followup_status='pending',is_deleted=False,created_by=user).count()
        print('followup_count-->',followup_count)
        data['followup_count'] = followup_count

        users_list=(list(TCoreUserDetail.objects.filter((Q(reporting_head_id=user)|Q(hod_id=user)),cu_is_deleted=False).values_list('cu_user',flat=True)))
        
        team_task_count = EtaskTask.objects.filter((Q(assign_to__in=users_list)|Q(assign_by__in=users_list)|Q(sub_assign_to_user__in=users_list)|Q(owner__in=users_list)),
                                                        is_deleted=False).values_list('id',flat=True)
        print('team_task_count-->',team_task_count)
        team_task_comment_count=ETaskComments.objects.filter(task__in=team_task_count,is_deleted=False).count()

        # my_task_all_count = EtaskTask.objects.filter(assign_to=user,is_deleted=False).count()
        my_task_all_count = EtaskTask.objects.filter(Q(is_deleted=False)&(Q(assign_to=user)|Q(sub_assign_to_user=user))).values_list('id',flat=True)
        print('my_task_all_count-->',my_task_all_count)
        my_task_comment_count=ETaskComments.objects.filter(task__in=my_task_all_count,is_deleted=False).count()
       
        data['comment'] = {
            "my_task_all_count" : my_task_comment_count,
            "team_task_count" : team_task_comment_count
        }

        team_ongoing_task_count = EtaskTask.objects.filter((Q(assign_to__in=users_list)|Q(assign_by__in=users_list)|Q(sub_assign_to_user__in=users_list)|Q(owner__in=users_list)),
                                                        task_status=1,is_deleted=False).count()
        print('team_ongoing_task_count-->',team_ongoing_task_count)
        team_completedtask_count = EtaskTask.objects.filter((Q(assign_to__in=users_list)|Q(assign_by__in=users_list)|Q(sub_assign_to_user__in=users_list)|Q(owner__in=users_list)),
                                                        task_status=2,is_deleted=False).count()
        print('team_completedtask_count-->',team_completedtask_count)
        team_closed_task_count = EtaskTask.objects.filter((Q(assign_to__in=users_list)|Q(assign_by__in=users_list)|Q(sub_assign_to_user__in=users_list)|Q(owner__in=users_list)),
                                            task_status=4,is_deleted=False).count()
        print('team_closed_task_count-->',team_closed_task_count)
        team_overdue_task_count = EtaskTask.objects.filter(Q(Q(assign_to__in=users_list)|Q(assign_by__in=users_list)|Q(sub_assign_to_user__in=users_list)|Q(owner__in=users_list)) &
                                            Q(Q(Q(extended_date__isnull=False)&Q(extended_date__date__lt=cur_date))|
                                            Q(Q(extended_date__isnull=True)&Q(end_date__date__lt=cur_date))),
                                            task_status=1,is_deleted=False).count()
        print('team_overdue_task_count-->',team_overdue_task_count)

        data['team'] = {
            "team_ongoing_task_count" : team_ongoing_task_count,
            "team_completedtask_count" : team_completedtask_count,
            "team_closed_task_count" : team_closed_task_count,
            "team_overdue_task_count" : team_overdue_task_count
        }

        reporting_task_count = EtaskTask.objects.filter(
                                        (Q(sub_assign_to_user__isnull=True)&Q(assign_to=user)),                                       
                                            task_status=1).values_list('id',flat=True)
        # print('reporting_task_count',reporting_task_count,list(reporting_task_count))
        # data['reporting_task_count'] = reporting_task_count
        current_date=datetime.now().date()
        count=0
        if reporting_task_count:
            for r_c in reporting_task_count:
                crossed_reporting_date=ETaskReportingDates.objects.filter(task_type=1,
                                                                        task=r_c,
                                                                        reporting_date__date__lt=current_date,
                                                                        reporting_status=2,
                                                                        is_deleted=False).count()
                print('crossed_reporting_date',crossed_reporting_date) 
                if crossed_reporting_date > 0:
                    count+=1
            print('count',count)
        data['reporting_task_count'] = count

        invite = EtaskInviteEmployee.objects.filter(user=user).values('appointment')
        # print('invite',invite)
        ids = [x['appointment'] for x in invite]
        upcoming_appointment_count = EtaskAppointment.objects.filter((Q(created_by=user)| Q(id__in=ids)),Appointment_status='ongoing').count()
        data['upcoming_appointment_count'] = upcoming_appointment_count
        previous_appointment_count = EtaskAppointment.objects.filter((Q(created_by=user)| Q(id__in=ids))&
                                                                    (Q(Appointment_status='Completed')|Q(Appointment_status='Cancelled'))).count()
        data['previous_appointment_count'] = previous_appointment_count

        data_dict['result'] = data
        if data:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_SUCCESS
        elif len(data) == 0:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_NO_DATA
        else:
            data_dict['request_status'] = 0
            data_dict['msg'] = settings.MSG_ERROR
        data = data_dict

        return Response(data)

                
class EtaskTaskCCListview(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskUserCC.objects.filter(is_deleted=False)
    serializer_class = EtaskTaskCCListviewSerializer
    pagination_class = CSPageNumberPagination

    def get_queryset(self):
        user = self.request.user.id
        # print('user-->',user)
        filter = {}
        sort_field='-id'
        from_date = self.request.query_params.get('from_date', None)
        to_date = self.request.query_params.get('to_date', None)
        assign_by = self.request.query_params.get('assign_by', None)
        assign_to = self.request.query_params.get('assign_to', None)
        search = self.request.query_params.get('search', None)
        field_name = self.request.query_params.get('field_name', None)
        order_by = self.request.query_params.get('order_by', None)
        parent_task = self.request.query_params.get('parent_task', None)
        status = self.request.query_params.get('status', None)

        if parent_task:
            filter['task__parent_id'] = parent_task

        if status:
            filter['task__task_status'] = status

        if field_name and order_by:
            if field_name =='task_code_id' and order_by=='asc':
                sort_field='task__task_code_id'
            if field_name =='task_code_id' and order_by=='desc':
                sort_field='-task__task_code_id'
      
            if field_name =='task_subject' and order_by=='asc':
                sort_field='task__task_subject'
            if field_name =='task_subject' and order_by=='desc':
                sort_field='-task__task_subject'

            if field_name =='start_date' and order_by=='asc':
                sort_field='task__start_date'              
            if field_name =='start_date' and order_by=='desc':
                sort_field='-task__start_date'
                
            if field_name =='end_date' and order_by=='asc':
                sort_field='task__end_date'                
            if field_name =='end_date' and order_by=='desc':
                sort_field='-task__end_date'
                    
            if field_name =='assign_by' and order_by=='asc':
                sort_field='task__assign_by'
            if field_name =='assign_by' and order_by=='desc':
                sort_field='-task__assign_by'

            if field_name =='assign_to' and order_by=='asc':
                sort_field='task__assign_to'
            if field_name =='assign_to' and order_by=='desc':
                sort_field='-task__assign_to'

        if from_date or to_date or assign_by or assign_to or search:
            if from_date and to_date:
                from_object =datetime.strptime(from_date, '%Y-%m-%d')
                to_object =datetime.strptime(to_date, '%Y-%m-%d')
                filter['task__end_date__date__gte']= from_object
                filter['task__end_date__date__lte']= to_object + timedelta(days=1)

            if assign_by:
                filter['task__assign_by__in'] = list(map(int,assign_by.split(" ")))
            
            if assign_to:
                filter['task__assign_to__in'] = list(map(int,assign_to.split(" ")))
            if search:
                # print('search',search)
                task_ids=EtaskTask.objects.filter(Q(Q(task_subject__icontains=search)|Q(task_code_id__icontains=search)),is_deleted=False).values_list('id',flat=True)
                # print('task_ids',task_ids)
                parent_ids=EtaskTask.objects.filter(Q(Q(task_subject__icontains=search)|Q(task_code_id__icontains=search)),is_deleted=False).values_list('parent_id',flat=True)
                # print('parent_ids',parent_ids)
                total_ids=list(task_ids)+list(parent_ids)
                # print('total_ids',total_ids)
                filter['task__in']=total_ids
        if filter:
            return self.queryset.filter(user=user,is_deleted=False,**filter).order_by(sort_field)
        else:
            return self.queryset.filter(user=user,is_deleted=False).order_by(sort_field)


    @response_modify_decorator_list_or_get_after_execution_for_pagination
    def get(self,request,*args,**kwargs):
        user = self.request.user.id
        response=super(EtaskTaskCCListview,self).get(self, request, args, kwargs)
        current_date = datetime.now().date()
        for data in response.data['results']:
            task_list =   EtaskTask.objects.filter(id=data['task'],is_deleted=False)
            # print('task_list-->',task_list)
            total_comments_count = ETaskCommentsViewers.objects.filter(task=data['task'],user_id=user,is_deleted=False).count()
            data['total_comments_count'] = total_comments_count

            user_name = User.objects.filter(id=data['user'],is_active=True).values('first_name','last_name')
            if user_name:
                user_name_first_name = user_name[0]['first_name'] if user_name[0]['first_name'] else ''
                user_name_last_name = user_name[0]['last_name'] if user_name[0]['last_name'] else ''
                data['user_name'] = user_name_first_name + ' ' +user_name_last_name

            task_list_dict = {}
            task_list_list = []

            for task in task_list:

                data['id'] = task.id
                data['parent_id'] = task.parent_id
                data['task_subject'] = task.task_subject
                data['task_description'] = task.task_description
                data['task_categories'] = task.task_categories
                data['start_date'] = task.start_date
                data['end_date'] = task.end_date
                data['completed_date'] = task.completed_date
                data['closed_date'] = task.closed_date
                data['extended_date'] = task.extended_date
                data['task_priority'] = task.task_priority
                data['task_priority_name'] = task.get_task_priority_display()
                data['task_type'] = task.task_type
                data['task_status'] = task.task_status
                data['task_status_name'] = task.get_task_status_display()
                data['owner'] = task.owner_id
                data['assign_to_id'] = task.assign_to_id
                data['assign_by_id'] = task.assign_by_id
                data['task_code_id'] = task.task_code_id
                
                # print('task.id-->',task.id)
                comments_count = ETaskComments.objects.filter(task=task.id,is_deleted=False).count()
                # print('comments_count-->',comments_count)
                data['comments_count'] = comments_count

                assign_by = User.objects.filter(id=task.assign_by_id,is_active=True).values('first_name','last_name')
                if assign_by:
                    assign_by_first_name = assign_by[0]['first_name'] if assign_by[0]['first_name'] else ''
                    assign_by_last_name = assign_by[0]['last_name'] if assign_by[0]['last_name'] else ''
                    data['assign_by'] = assign_by_first_name + ' ' +assign_by_last_name

                assign_to = User.objects.filter(id=task.assign_to_id,is_active=True).values('first_name','last_name')
                if assign_to:
                    assign_to_first_name = assign_to[0]['first_name'] if assign_to[0]['first_name'] else ''
                    assign_to_last_name = assign_to[0]['last_name'] if assign_to[0]['last_name'] else ''
                    data['assign_to'] = assign_to_first_name + ' ' +assign_to_last_name
                

                # print('task.sub_assign_to_user-->',task.sub_assign_to_user_id)
                sub_assign_to_user = User.objects.filter(id=task.sub_assign_to_user_id,is_active=True).values('first_name','last_name')
                if sub_assign_to_user:
                    if user != task.sub_assign_to_user:
                        if sub_assign_to_user:
                            sub_assign_to_user_first_name = sub_assign_to_user[0]['first_name'] if sub_assign_to_user[0]['first_name'] else ''
                            sub_assign_to_user_last_name = sub_assign_to_user[0]['last_name'] if sub_assign_to_user[0]['last_name'] else ''
                            data['sub_assign_to_user_id'] = task.sub_assign_to_user_id
                            data['sub_assign_to_user'] = sub_assign_to_user_first_name + ' ' +sub_assign_to_user_last_name
                            
                    else:
                        data['assign_to'] = user
                else:
                    data['sub_assign_to_user'] = None
                    data['sub_assign_to_user_id'] = None

                print('task.parent_id-->',task.parent_id)
                print('task.id-->',task.id)
                if int(task.parent_id) != 0:
                    # parent_id_name = EtaskTask.objects.filter(id=data['id'],task_status=1,is_deleted=False,parent_id=data['parent_id']).values('task_subject')
                    parent_id_name = EtaskTask.objects.filter(is_deleted=False,id=task.parent_id).values('task_subject',)
                    print('parent_id_name-->',parent_id_name)
                    if parent_id_name:
                        data['parent'] = {
                            "id" :  task.parent_id,
                            "name" :parent_id_name[0]['task_subject']
                        }
                else :
                    data['parent'] = None

                reporting_date = ETaskReportingDates.objects.filter(task=task.id,task_type=1,is_deleted=False,reporting_status=2)
                reporting_list = []
                for r_date in reporting_date:
                    # print('r_date.reporting_date-->',type(r_date.reporting_date))
                    reporting_dict = {
                        "id" : r_date.id,
                        "reporting_date" : r_date.reporting_date
                    }
                    reporting_list.append(reporting_dict)

                data['reporting_dates'] = reporting_list

                # if task.extended_date and task.extended_date.date() <= current_date:
                #     days_extended=(current_date - task.extended_date.date()).days
                #     print("days_extended",days_extended)
                #     if days_extended >0:
                #         data['task_status']="overdue"
                #         data['task_overdue_days'] = days_extended
                #     else:
                #         data['task_status']=task.get_task_status_display()
                #         data['task_overdue_days'] = None
                # elif task.end_date and task.end_date.date() <= current_date:
                #     days_extended=(current_date - task.end_date.date()).days
                #     print("days_extended",days_extended)
                #     if days_extended >0:
                #         data['task_status']="overdue"
                #         data['task_overdue_days'] = days_extended
                #     else:
                #         data['task_status']=task.get_task_status_display()
                #         data['task_overdue_days'] = None
                # else:
                #     data['task_status']=task.get_task_status_display()

               
            
        return response

class EtaskTaskTransferredListview(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskTask.objects.filter(is_deleted=False)
    serializer_class = EtaskTaskTransferredListviewSerializer
    pagination_class = CSPageNumberPagination

    def get_queryset(self):
        user = self.request.user.id

        filter = {}
        sort_field='-id'
        from_date = self.request.query_params.get('from_date', None)
        to_date = self.request.query_params.get('to_date', None)
        assign_by = self.request.query_params.get('assign_by', None)
        search = self.request.query_params.get('search', None)
        field_name = self.request.query_params.get('field_name', None)
        order_by = self.request.query_params.get('order_by', None)



        if field_name and order_by:      
            if field_name =='task_code_id' and order_by=='asc':
                sort_field='task_code_id'

            if field_name =='task_code_id' and order_by=='desc':
                sort_field='-task_code_id'

            if field_name =='task_subject' and order_by=='asc':
                sort_field='task_subject'

            if field_name =='task_subject' and order_by=='desc':
                sort_field='-task_subject'

            if field_name =='start_date' and order_by=='asc':
                sort_field='start_date'
                # return self.queryset.all().order_by('duration_end')
            if field_name =='start_date' and order_by=='desc':
                sort_field='-start_date'
                # return self.queryset.all().order_by('-duration_end')

            if field_name =='end_date' and order_by=='asc':
                sort_field='end_date'
                # return self.queryset.all().order_by('duration')
            if field_name =='end_date' and order_by=='desc':
                sort_field='-end_date'
                    # return self.queryset.all().order_by('-duration')
            if field_name =='assign_by' and order_by=='asc':
                sort_field='assign_by'
                # return self.queryset.all().order_by('duration')
            if field_name =='assign_by' and order_by=='desc':
                sort_field='-assign_by'

        if from_date or to_date or assign_by or search:

            if from_date and to_date:
                from_object =datetime.strptime(from_date, '%Y-%m-%d')
                to_object =datetime.strptime(to_date, '%Y-%m-%d')
                filter['end_date__date__gte']= from_object
                filter['end_date__date__lte']= to_object + timedelta(days=1)

            if assign_by:
                filter['assign_by__in'] = list(map(int,assign_by.split(" ")))
            print("filter",filter)
            if search:
                search_data = search
                print('search_data-->',search_data)

                id1= self.queryset.filter((Q(assign_to=user)|Q(sub_assign_to_user=user))&Q(sub_assign_to_user__isnull=False),
                                         is_deleted=False,**filter).values_list('id',flat=True)
                id2= self.queryset.filter((Q(assign_to=user)|Q(sub_assign_to_user=user))&Q(sub_assign_to_user__isnull=False),
                                         is_deleted=False,**filter).values_list('parent_id',flat=True)
                ids=list(id1)+list(id2)
                print("ids",ids)
                check_data = EtaskTask.objects.filter((Q(task_code_id__icontains=search_data)|Q(task_subject__icontains=search_data)),id__in=ids).values_list('id',flat=True)
                print("check_data",check_data)
                return self.queryset.filter((Q(assign_to=user)|Q(sub_assign_to_user=user))&Q(sub_assign_to_user__isnull=False),
                                            (Q(parent_id__in=list(check_data))|Q(id__in=list(check_data))),
                                            is_deleted=False,**filter).order_by(sort_field)

            else:
                return self.queryset.filter((Q(assign_to=user)|Q(sub_assign_to_user=user))&Q(sub_assign_to_user__isnull=False),
                                                is_deleted=False,**filter).order_by(sort_field)
                # return queryset                     
        else:
            return self.queryset.filter((Q(assign_to=user)|Q(sub_assign_to_user=user))&Q(sub_assign_to_user__isnull=False),
                                        is_deleted=False,**filter).order_by(sort_field)


    @response_modify_decorator_list_or_get_after_execution_for_pagination
    def get(self, request, *args, **kwargs):
        user = request.user.id
        current_date = datetime.now().date()
        response = super(EtaskTaskTransferredListview, self).get(self, request, args, kwargs)
        user = request.user.id
        cur_date = datetime.now().date()

        for data in response.data['results']:

            comments_count = ETaskComments.objects.filter(task=data['id'],is_deleted=False).count()
            data['comments_count'] = comments_count
            data['task_status_id'] = data['task_status']
            
            assign_by = User.objects.filter(id=data['assign_by'],is_active=True).values('first_name','last_name')
            if assign_by:
                assign_by_first_name = assign_by[0]['first_name'] if assign_by[0]['first_name'] else ''
                assign_by_last_name = assign_by[0]['last_name'] if assign_by[0]['last_name'] else ''
                data['assign_by_id'] = data['assign_by']
                data['assign_by'] = assign_by_first_name + ' ' +assign_by_last_name
                

            assign_to = User.objects.filter(id=data['assign_to'],is_active=True).values('first_name','last_name')
            if assign_to:
                assign_to_first_name = assign_to[0]['first_name'] if assign_to[0]['first_name'] else ''
                assign_to_last_name = assign_to[0]['last_name'] if assign_to[0]['last_name'] else ''
                data['assign_to_name'] = assign_to_first_name + ' ' +assign_to_last_name

            sub_assign_to_user = User.objects.filter(id=data['sub_assign_to_user'],is_active=True).values('first_name','last_name')
            # print('sub_assign_to_user-->',sub_assign_to_user)
            if data['sub_assign_to_user']:
                if sub_assign_to_user:
                    sub_assign_to_user_first_name = sub_assign_to_user[0]['first_name'] if sub_assign_to_user[0]['first_name'] else ''
                    sub_assign_to_user_last_name = sub_assign_to_user[0]['last_name'] if sub_assign_to_user[0]['last_name'] else ''
                    data['sub_assign_to_user'] = sub_assign_to_user_first_name + ' ' +sub_assign_to_user_last_name
            else:
                data['sub_assign_to_user'] = None
                # data['assign_to'] = user
            
            if int(data['parent_id']) != 0:
                # parent_id_name = EtaskTask.objects.filter(id=data['id'],task_status=1,is_deleted=False,parent_id=data['parent_id']).values('task_subject')
                parent_id_name = EtaskTask.objects.filter(task_status=1,is_deleted=False,id=data['parent_id']).values('id','task_subject')
                # print('parent_id_name-->',parent_id_name[0]['id'])
                if parent_id_name:
                    data['parent'] = {
                        "id" :  data['parent_id'],
                        "name" :parent_id_name[0]['task_subject']
                    }
            else :
                data['parent'] = None

            report_date=ETaskReportingDates.objects.filter(task_type=1,task=data['id'],is_deleted=False).values('id','reporting_date')
           #koushik --code 
            # print('report_date',report_date)
            # report_date_list=[]
            # if report_date:
            #     for r_d in report_date:
            #         if r_d.reporting_date.date()<= current_date:
            #             report_data={
            #                 'id':r_d.id,
            #                 'reporting_date':r_d.reporting_date
            #             }
            #             report_date_list.append(report_data)

            data['reporting_dates']=report_date if report_date else []  
        
            ids = report_date.filter().values_list('id',flat=True)
            print('ids',ids)
            reporting_action_log_final = []
            # reporting_action_log=ETaskReportingActionLog.objects.filter((Q(reporting_date__in=ids)|Q(reporting_date__isnull=True)),
            reporting_action_log=ETaskReportingActionLog.objects.filter(reporting_date__in=ids,
                                                                    task=data['id'],is_deleted=False).values('task','reporting_date__id',
                                                                    'reporting_date__reporting_date','updated_date','status')
            
            print("reporting_action_log",reporting_action_log)
            for x in reporting_action_log:
                # print('')
                reporting_log_dict={
                    'task':x['task'],
                    'reporting_date__id':x['reporting_date__id'],
                    'reporting_date':x['reporting_date__reporting_date'],
                    'updated_date':x['updated_date'],
                    'reporting_status':ETaskReportingActionLog.status_choice[x['status']-1][1]
                }
                reporting_action_log_final.append(reporting_log_dict)
            print("reporting_action_log",reporting_action_log_final)
            # reporting_action_list=[]                                                      
            # if reporting_action_log:
            #     for r_a in reporting_action_log:
            #         action_data={
            #             'id':r_a.id,
            #             'date_of_update':r_a.updated_date,
            #             'team_update':r_a.get_status_display()
            #         }
            #         reporting_action_list.append(action_data)         
            data['date_of_update_and_team_update']=reporting_action_log_final if reporting_action_log_final else []
            # else:                
            #     data['date_of_update_and_team_update']=[]
            # if data['extended_date']:
            #     e_date = datetime.strptime(datetime.strftime(datetime.strptime(data['extended_date'],"%Y-%m-%dT%H:%M:%S.%f"),"%Y-%m-%dT%H:%M:%S"),"%Y-%m-%dT%H:%M:%S").date()
            # if data['end_date']:
            #     en_date = datetime.strptime(datetime.strftime(datetime.strptime(data['end_date'],"%Y-%m-%dT%H:%M:%S.%f"),"%Y-%m-%dT%H:%M:%S"),"%Y-%m-%dT%H:%M:%S").date()
            print('aff',type(data['end_date']))
            if data['task_status_name'] == 'Completed':
                data['task_status']=data['task_status_name']
                reporting_action_log=ETaskReportingActionLog.objects.filter((Q(reporting_date__in=ids)|Q(reporting_date__isnull=True)),
                                                            
                                                            task=data['id'],is_deleted=False).values_list('updated_date',flat=True)
                data['task_completed_date'] = reporting_action_log[0] if reporting_action_log else None
            
            elif data['extended_date'] and datetime.strptime(data['extended_date'],"%Y-%m-%dT%H:%M:%S").date() <= current_date:
                e_date = data['extended_date'].split('T')[0]
                extended_date = datetime.strptime(e_date, '%Y-%m-%d').date()
                days_extended=(current_date - extended_date).days
                print("days_extended",days_extended)
                if days_extended >0:
                    data['task_status']="overdue"
                    data['task_overdue_days'] = days_extended
                else:
                    data['task_status']=data['task_status_name']
                    data['task_overdue_days'] = None
            elif data['end_date'] and datetime.strptime(data['end_date'],"%Y-%m-%dT%H:%M:%S").date() <= current_date:
                en_date = data['end_date'].split('T')[0]
                end_date = datetime.strptime(en_date, '%Y-%m-%d').date()
                days_extended=(current_date - end_date).days
                print("days_extended",days_extended)
                if days_extended >0:
                    data['task_status']="overdue"
                    data['task_overdue_days'] = days_extended
                else:
                    data['task_status']=data['task_status_name']
                    data['task_overdue_days'] = None
            else:
                data['task_status']=data['task_status_name']
                # data['task_overdue_days'] = None
            

        return response



class ETaskCommentsView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = ETaskComments.objects.filter(is_deleted=False)
    serializer_class = ETaskCommentsSerializer
    @response_modify_decorator_get_after_execution
    def get(self,request,*args,**kwargs):
        response=super(ETaskCommentsView,self).get(self, request, args, kwargs)
        for data in response.data:
            cost_details=EtaskIncludeAdvanceCommentsCostDetails.objects.filter(etcomments=data['id'],is_deleted=False)
            cost_details_list=[]
            for c_d in cost_details:
                cost_data={
                    'id':c_d.id,
                    'cost_details':c_d.cost_details,
                    'cost':c_d.cost
                }
                cost_details_list.append(cost_data)
            data['cost_details']=cost_details_list
            other_details=EtaskIncludeAdvanceCommentsOtherDetails.objects.filter(etcomments=data['id'],is_deleted=False)
            other_details_list=[]
            for o_d in other_details:
                others_data={
                    'id':o_d.id,
                    'other_details':o_d.other_details,
                    'value':o_d.value
                }
                other_details_list.append(others_data)
            data['other_details']=other_details_list
            attachment_details=EtaskIncludeAdvanceCommentsDocuments.objects.filter(etcomments=data['id'],is_deleted=False)
            attachment_list=[]
            for a_d in attachment_details:
                attachments={
                    'id':a_d.id,
                    'document_name':a_d.document_name,
                    'document':request.build_absolute_uri(a_d.document.url)
                }
                attachment_list.append(attachments)
            data['attachments']=attachment_list

        return response

class ETaskCommentsViewersView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = ETaskCommentsViewers.objects.filter(is_deleted=False)
    serializer_class = ETaskCommentsViewersSerializer

class ETaskUnreadCommentsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    # queryset = ETaskCommentsViewers.objects.filter(is_deleted=False)
    queryset = EtaskTask.objects.filter(is_deleted=False)
    serializer_class = ETaskUnreadCommentsSerializer
    pagination_class = CSPageNumberPagination

    def get_queryset(self):
        login_user=self.request.user.id
        user_id=self.kwargs["user_id"]
        cur_date=datetime.now().date()

        if int(login_user)==int(user_id):
            return self.queryset.filter((Q(assign_to_id=user_id)|Q(sub_assign_to_user_id=user_id)|Q(assign_by_id=user_id)),
                                        id__in=list(ETaskCommentsViewers.objects.filter(user=login_user,
                                        is_view=False,is_deleted=False).values_list('task',flat=True)),
                                        is_deleted=False).order_by('-id')

        else:
            return self.queryset.filter((Q(Q(assign_to_id=user_id)|Q(sub_assign_to_user_id=user_id))&Q(assign_by_id=login_user)),
                                        id__in=list(ETaskCommentsViewers.objects.filter(user=login_user,
                                        is_view=False,is_deleted=False).values_list('task',flat=True)),
                                        is_deleted=False).order_by('-id')


    @response_modify_decorator_list_or_get_after_execution_for_pagination
    def get(self, request, *args, **kwargs):
        response=super(ETaskUnreadCommentsView,self).get(self,request,args,kwargs)
        print("response.data['results']",response.data['results'])
        login_user=self.request.user.id
        user_id=self.kwargs["user_id"]
        if response.data:
            for data in response.data['results']:
                data['assign_by_name'] = userdetails(int(data['assign_by']))
                comment = ETaskCommentsViewers.objects.filter(task=data['id'],user=login_user,is_view=False,
                                                            is_deleted=False).values('etcomments__comments',
                                                            'etcomments__id','etcomments__created_by',
                                                            'etcomments__created_at').order_by('-created_at')

                if comment:
                    adv_comments = {}
                    print("comment",comment)
                    data['comment_id'] = comment[0]['etcomments__id']
                    data['commented_by'] = userdetails(int(comment[0]['etcomments__created_by']))
                    data['commented_at'] = comment[0]['etcomments__created_at']
                    data['comment_details'] = comment[0]['etcomments__comments']
                    cost_details=EtaskIncludeAdvanceCommentsCostDetails.objects.filter(etcomments=comment[0]['etcomments__id'],is_deleted=False)
                    cost_details_list=[]
                    if cost_details:
                        for c_d in cost_details:
                            cost_data={
                                'id':c_d.id,
                                'cost_details':c_d.cost_details,
                                'cost':c_d.cost
                            }
                            cost_details_list.append(cost_data)
                        adv_comments['cost_details']=cost_details_list
                    other_details=EtaskIncludeAdvanceCommentsOtherDetails.objects.filter(etcomments=comment[0]['etcomments__id'],is_deleted=False)
                    other_details_list=[]
                    if other_details:
                        for o_d in other_details:
                            others_data={
                                'id':o_d.id,
                                'other_details':o_d.other_details,
                                'value':o_d.value
                            }
                            other_details_list.append(others_data)
                        adv_comments['other_details']=other_details_list
                    attachment_details=EtaskIncludeAdvanceCommentsDocuments.objects.filter(etcomments=comment[0]['etcomments__id'],is_deleted=False)
                    attachment_list=[]
                    if attachment_details:
                        for a_d in attachment_details:
                            attachments={
                                'id':a_d.id,
                                'document_name':a_d.document_name,
                                'document':request.build_absolute_uri(a_d.document.url)
                            }
                            attachment_list.append(attachments)
                        adv_comments['attachments']=attachment_list
                    if adv_comments:
                        data['adv_comments'] = adv_comments
                    else:
                        data['adv_comments'] = None


                #########################################################################################
                # comments_count = ETaskComments.objects.filter(task=data['id'],is_deleted=False).count()
                # data['comments_count'] = comments_count
                # if int(login_user)==int(user_id):
                #     print("login user")
                #     data['assign_by_name'] = userdetails(int(data['assign_by']))
                #     if int(data['assign_to'])==int(login_user) and data['sub_assign_to_user'] is not None:
                #         print("sub_assign_to_user")
                #         data['sub_assign_to_user_name'] = userdetails(int(data['sub_assign_to_user']))
                #     elif data['sub_assign_to_user'] is not None and int(data['sub_assign_to_user'])==int(login_user):
                #         data['assign_by'] = data['assign_to']
                #         data['assign_by_name'] = userdetails(int(data['assign_to']))
                #         data['sub_assign_to_user_name'] = ''
                #     else:
                #         print("not sub_assign_to_user")
                #         data['sub_assign_to_user_name'] = ''
                # else:
                #     print("not a login user")
                #     if data['sub_assign_to_user']:
                #         if int(data['assign_by'])==int(login_user):
                #             data['assign_by_name'] = userdetails(int(data['assign_by']))
                #             data['sub_assign_to_user_name'] = ''
                #         else:
                #             print("convert")
                #             data['assign_by'] = data['assign_to']
                #             data['assign_by_name'] = userdetails(int(data['assign_to']))
                #             data['sub_assign_to_user_name'] = userdetails(int(data['sub_assign_to_user']))
                #             if int(data['assign_to'])==int(login_user):
                #                 data['sub_assign_to_user_name'] = ""
                #     else:
                #         print("not convert")
                #         data['assign_by_name'] = userdetails(int(data['assign_by']))
                #         data['sub_assign_to_user_name'] = ''
 
        return response


class ETaskCommentsAdvanceAttachmentAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskIncludeAdvanceCommentsDocuments.objects.filter(is_deleted=False)
    serializer_class = ETaskCommentsAdvanceAttachmentAddSerializer

class EtasCommentsListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = ETaskComments.objects.filter(is_deleted=False)
    serializer_class = EtasCommentsListSerializer
    pagination_class = CSPageNumberPagination

    def get_queryset(self):
        task_id =self.request.query_params.get('task_id', None)
        return self.queryset.filter(is_deleted=False,task=task_id)

    @response_modify_decorator_list_or_get_after_execution_for_pagination
    def get(self,request,*args,**kwargs):
        login_user = request.user.id
        task_id =request.query_params.get('task_id', None)
        response=super(EtasCommentsListView,self).get(self, request, args, kwargs)
        for data in response.data['results']:
            is_view = ETaskCommentsViewers.objects.filter(etcomments=data['id'],task=task_id,user=login_user,
                                                        is_deleted=False).values('is_view')
            data['is_view'] = is_view[0]['is_view'] if is_view else True
            cost_details=EtaskIncludeAdvanceCommentsCostDetails.objects.filter(etcomments=data['id'],is_deleted=False)
            cost_details_list=[]
            for c_d in cost_details:
                cost_data={
                    'id':c_d.id,
                    'cost_details':c_d.cost_details,
                    'cost':c_d.cost
                }
                cost_details_list.append(cost_data)
            data['cost_details']=cost_details_list
            other_details=EtaskIncludeAdvanceCommentsOtherDetails.objects.filter(etcomments=data['id'],is_deleted=False)
            other_details_list=[]
            for o_d in other_details:
                others_data={
                    'id':o_d.id,
                    'other_details':o_d.other_details,
                    'value':o_d.value
                }
                other_details_list.append(others_data)
            data['other_details']=other_details_list
            attachment_details=EtaskIncludeAdvanceCommentsDocuments.objects.filter(etcomments=data['id'],is_deleted=False)
            attachment_list=[]
            for a_d in attachment_details:
                attachments={
                    'id':a_d.id,
                    'document_name':a_d.document_name,
                    'document':request.build_absolute_uri(a_d.document.url)
                }
                attachment_list.append(attachments)
            data['attachments']=attachment_list
            data['created_by_name']=userdetails(data['created_by'])


        return response



#::::::::::::::::::::::::: Followup COMMENTS:::::::::::::::::::::::::::#

class ETaskFollowupCommentsView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = FollowupComments.objects.filter(is_deleted=False)
    serializer_class = ETaskFollowupCommentsSerializer
    @response_modify_decorator_get_after_execution
    def get(self,request,*args,**kwargs):
        response=super(ETaskFollowupCommentsView,self).get(self, request, args, kwargs)
        for data in response.data:
            if data['advance_comment'] == True:
                cost_details=FollowupIncludeAdvanceCommentsCostDetails.objects.filter(flcomments=data['id'],is_deleted=False)
                cost_details_list=[]
                for c_d in cost_details:
                    cost_data={
                        'id':c_d.id,
                        'cost_details':c_d.cost_details,
                        'cost':c_d.cost
                    }
                    cost_details_list.append(cost_data)
                data['cost_details']=cost_details_list
                other_details=FollowupIncludeAdvanceCommentsOtherDetails.objects.filter(flcomments=data['id'],is_deleted=False)
                other_details_list=[]
                for o_d in other_details:
                    others_data={
                        'id':o_d.id,
                        'other_details':o_d.other_details,
                        'value':o_d.value
                    }
                    other_details_list.append(others_data)
                data['other_details']=other_details_list
                attachment_details=FoloowupIncludeAdvanceCommentsDocuments.objects.filter(flcomments=data['id'],is_deleted=False)
                attachment_list=[]
                for a_d in attachment_details:
                    attachments={
                        'id':a_d.id,
                        'document_name':a_d.document_name,
                        'document':request.build_absolute_uri(a_d.document.url)
                    }
                    attachment_list.append(attachments)
                data['attachments']=attachment_list
            else:
                data['cost_details']= []
                data['other_details']= []
                data['attachments']= []


        return response

class ETaskFollowupCommentsAdvanceAttachmentAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = FollowupIncludeAdvanceCommentsDocuments.objects.filter(is_deleted=False)
    serializer_class = ETaskFollowupCommentsAdvanceAttachmentAddSerializer

class EtasFollowupCommentsListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = FollowupComments.objects.filter(is_deleted=False)
    serializer_class = EtasCommentsListSerializer
    pagination_class = CSPageNumberPagination

    def get_queryset(self):
        followup_id =self.request.query_params.get('followup_id', None)
        return self.queryset.filter(is_deleted=False,followup=followup_id)


    @response_modify_decorator_list_or_get_after_execution_for_pagination
    def get(self,request,*args,**kwargs):
        response=super(EtasFollowupCommentsListView,self).get(self, request, args, kwargs)
        for data in response.data['results']:
            comment_by_name = User.objects.filter(id=data['created_by'],is_active=True).values('first_name','last_name')
            if comment_by_name:
                comment_by_name_first_name = comment_by_name[0]['first_name'] if comment_by_name[0]['first_name'] else ''
                comment_by_name_last_name = comment_by_name[0]['last_name'] if comment_by_name[0]['last_name'] else ''
                data['comment_by_name'] = comment_by_name_first_name + ' ' + comment_by_name_last_name
                data['comment_by_id'] = data['created_by']

            if data['advance_comment'] == True:
                cost_details=FollowupIncludeAdvanceCommentsCostDetails.objects.filter(flcomments=data['id'],is_deleted=False)
                cost_details_list=[]
                for c_d in cost_details:
                    cost_data={
                        'id':c_d.id,
                        'cost_details':c_d.cost_details,
                        'cost':c_d.cost
                    }
                    cost_details_list.append(cost_data)
                data['cost_details']=cost_details_list
                other_details=FollowupIncludeAdvanceCommentsOtherDetails.objects.filter(flcomments=data['id'],is_deleted=False)
                other_details_list=[]
                for o_d in other_details:
                    others_data={
                        'id':o_d.id,
                        'other_details':o_d.other_details,
                        'value':o_d.value
                    }
                    other_details_list.append(others_data)
                data['other_details']=other_details_list
                attachment_details=FollowupIncludeAdvanceCommentsDocuments.objects.filter(flcomments=data['id'],is_deleted=False)
                attachment_list=[]
                for a_d in attachment_details:
                    attachments={
                        'id':a_d.id,
                        'document_name':a_d.document_name,
                        'document':request.build_absolute_uri(a_d.document.url)
                    }
                    attachment_list.append(attachments)
                data['attachments']=attachment_list
            else:
                data['cost_details']= []
                data['other_details']= []
                data['attachments']= []


        return response


####################################################################

class ETaskSubAssignView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskTask.objects.filter(is_deleted=False)
    serializer_class = ETaskSubAssignSerializer

    @response_modify_decorator_update
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

class EtaskAddFollowUpView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskFollowUP.objects.filter(is_deleted=False)
    serializer_class = EtaskAddFollowUpSerializer

    @response_modify_decorator_post
    def post(self, request, *args, **kwargs):
        return super(EtaskAddFollowUpView,self).post(request, *args, **kwargs)

class EtaskFollowUpListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskFollowUP.objects.filter(is_deleted=False)
    serializer_class = EtaskFollowUpListSerializer
    pagination_class = CSPageNumberPagination

    def get_queryset(self):
        filter = {}
        sort_field='-id'
        user_id=self.kwargs["user_id"]
        current_date = self.request.query_params.get('current_date', None)
        start_date = self.request.query_params.get('from_date', None)
        end_date = self.request.query_params.get('to_date', None)
        assign_to = self.request.query_params.get('assign_to', None)
        search = self.request.query_params.get('search', None)
        field_name = self.request.query_params.get('field_name', None)
        order_by = self.request.query_params.get('order_by', None)
       
        if field_name and order_by:      
            if field_name =='follow_up_task' and order_by=='asc':
                sort_field='follow_up_task'
            if field_name =='follow_up_task' and order_by=='desc':
                sort_field='-follow_up_task'

            if field_name =='start_date' and order_by=='asc':
                sort_field='start_date'               
            if field_name =='start_date' and order_by=='desc':
                sort_field='-start_date'
               
            if field_name =='end_date' and order_by=='asc':
                sort_field='end_date'              
            if field_name =='end_date' and order_by=='desc':
                sort_field='-end_date'

            if field_name =='follow_up_time' and order_by=='asc':
                sort_field='follow_up_time'              
            if field_name =='follow_up_time' and order_by=='desc':
                sort_field='-follow_up_time'  

            if field_name =='assign_to' and order_by=='asc':
                sort_field='assign_to'             
            if field_name =='assign_to' and order_by=='desc':
                sort_field='-assign_to'

        if start_date or end_date or assign_to or search:
            if start_date and end_date:
                from_object =datetime.strptime(start_date, '%Y-%m-%d')
                to_object =datetime.strptime(end_date, '%Y-%m-%d')
                filter['end_date__date__gte']= from_object
                filter['end_date__date__lte']= to_object + timedelta(days=1)

            if assign_to:
                filter['assign_to__in'] = list(map(int,assign_to.split(" ")))
           
            if search:
                search_data = search
                filter['follow_up_task__icontains']=search_data
            
        if current_date:
            cur_date = datetime.strptime(current_date, "%Y-%m-%d").date()
            # print('cur_date-->',type(cur_date))
            return self.queryset.filter(followup_status='pending',is_deleted=False,follow_up_date__date=cur_date,
                                        created_by=user_id,**filter).order_by(sort_field)
        else:
            return self.queryset.filter(is_deleted=False,created_by=user_id,**filter).order_by(sort_field)

    @response_modify_decorator_list_or_get_after_execution_for_pagination
    def get(self, request, *args, **kwargs):

        response = super(EtaskFollowUpListView,self).get(self, request, args, kwargs)
        # print("response",response)

        reporting_dict = {}

        follow_up_list = []
        for data in response.data['results']:


            comments_count = FollowupComments.objects.filter(followup=data['id'],is_deleted=False).count()

            data['comments_count'] = comments_count

            # print(data['id'],'<--comments_count-->',comments_count)

            create_by_name = User.objects.filter(id=data['created_by'],is_active=True).values('first_name','last_name')
            
            if create_by_name:
                u_first_name = create_by_name[0]['first_name'] if create_by_name[0]['first_name'] else ''
                u_last_name = create_by_name[0]['last_name'] if create_by_name[0]['last_name'] else ''
                data['created_by_name'] = u_first_name + ' ' +u_last_name

            assign_to_name = User.objects.filter(id=data['assign_to'],is_active=True).values('first_name','last_name')
            
            if assign_to_name:
                assign_to_first_name = assign_to_name[0]['first_name'] if assign_to_name[0]['first_name'] else ''
                assign_to_last_name = assign_to_name[0]['last_name'] if assign_to_name[0]['last_name'] else ''
                data['assign_to_name'] = assign_to_first_name + ' ' +assign_to_last_name

            reporting_date = ETaskReportingDates.objects.filter(task=data['id'],task_type=2,is_deleted=False)

            reporting_list = []
            for r_date in reporting_date:
                # print('r_date.reporting_date-->',type(r_date.reporting_date))
                reporting_dict = {
                    "follow_up_id" : r_date.task,
                    "reporting_date" : r_date.reporting_date
                }
                reporting_list.append(reporting_dict)

            data['reporting_dates'] = reporting_list
            task=EtaskTask.objects.filter(id=data['task'],is_deleted=False).values('task_subject','parent_id')
            if task:
                task_data={}
                task_data['task_subject']=task[0]['task_subject'] if task[0]['task_subject'] else ''

                if int(task[0]['parent_id']) != 0:
                    # parent_id_name = EtaskTask.objects.filter(id=data['id'],task_status=1,is_deleted=False,parent_id=data['parent_id']).values('task_subject')
                    parent_id_name = EtaskTask.objects.filter(is_deleted=False,id=task[0]['parent_id']).values('id','task_subject')
                    # print('parent_id_name-->',parent_id_name[0]['id'])
                    if parent_id_name:
                        task_data['parent'] = {
                            "id" :  task[0]['parent_id'],
                            "name" :parent_id_name[0]['task_subject']
                        }
                else :
                    task_data['parent'] = None
                data['task_name']=task_data
            else:
                data['task_name']=None

        return response
class EtaskTodaysFollowUpListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskFollowUP.objects.filter(is_deleted=False,followup_status='pending')
    serializer_class = EtaskFollowUpListSerializer
    # pagination_class = CSPageNumberPagination

    def get_queryset(self):
        filter = {}
        sort_field='-id'
        user_id=self.kwargs["user_id"]
        current_date = self.request.query_params.get('current_date', None)
        follow_up_date = self.request.query_params.get('follow_up_date', None)
        # end_date = self.request.query_params.get('to_date', None)
        assign_to = self.request.query_params.get('assign_to', None)
        search = self.request.query_params.get('search', None)
        field_name = self.request.query_params.get('field_name', None)
        order_by = self.request.query_params.get('order_by', None)
        todays_date=date.today()
        print('todays_date',todays_date)

        if field_name and order_by:      
            if field_name =='follow_up_task' and order_by=='asc':
                sort_field='follow_up_task'
            if field_name =='follow_up_task' and order_by=='desc':
                sort_field='-follow_up_task'

            if field_name =='follow_up_date' and order_by=='asc':
                sort_field='follow_up_date'               
            if field_name =='follow_up_date' and order_by=='desc':
                sort_field='-follow_up_date'
               
            if field_name =='assign_to' and order_by=='asc':
                sort_field='assign_to'             
            if field_name =='assign_to' and order_by=='desc':
                sort_field='-assign_to'

        if follow_up_date or assign_to or search:
            if follow_up_date:
                from_object =datetime.strptime(follow_up_date, '%Y-%m-%d')
                filter['follow_up_date__date__gte']= from_object
                filter['follow_up_date__date__lte']= from_object + timedelta(days=1)

            if assign_to:
                filter['assign_to__in'] = list(map(int,assign_to.split(" ")))
           
            if search:
                search_data = search
                filter['follow_up_task__icontains']=search_data
            
        if current_date:
            cur_date = datetime.strptime(current_date, "%Y-%m-%d").date()
            # print('cur_date-->',type(cur_date))
            # return self.queryset.filter(Q(Q(Q(assign_for__isnull=False)&Q(assign_for=user_id))|Q(Q(assign_for__isnull=True)&Q(created_by=user_id))),followup_status='pending',is_deleted=False,follow_up_date__date=cur_date,
            #                             **filter).order_by(sort_field)
            return self.queryset.filter(created_by=user_id,followup_status='pending',is_deleted=False,follow_up_date__date=cur_date,
                                        **filter).order_by(sort_field)
        else:
            return self.queryset.filter(created_by=user_id,
                                            follow_up_date__date=todays_date,is_deleted=False,**filter).order_by(sort_field)

    @response_modify_decorator_get_after_execution
    def get(self, request, *args, **kwargs):

        response = super(EtaskTodaysFollowUpListView,self).get(self, request, args, kwargs)
        print("response",response)

        # reporting_dict = {}

        follow_up_list = []
        for data in response.data:


            comments_count = FollowupComments.objects.filter(followup=data['id'],is_deleted=False).count()

            data['comments_count'] = comments_count

            # print(data['id'],'<--comments_count-->',comments_count)

            create_by_name = User.objects.filter(id=data['created_by'],is_active=True).values('first_name','last_name')
            
            if create_by_name:
                u_first_name = create_by_name[0]['first_name'] if create_by_name[0]['first_name'] else ''
                u_last_name = create_by_name[0]['last_name'] if create_by_name[0]['last_name'] else ''
                data['created_by_name'] = u_first_name + ' ' +u_last_name

            assign_to_name = User.objects.filter(id=data['assign_to'],is_active=True).values('first_name','last_name')
            print('assign_to_name',assign_to_name)
            if assign_to_name:
                assign_to_first_name = assign_to_name[0]['first_name'] if assign_to_name[0]['first_name'] else ''
                assign_to_last_name = assign_to_name[0]['last_name'] if assign_to_name[0]['last_name'] else ''
                data['assign_to_name'] = assign_to_first_name + ' ' +assign_to_last_name

            data['assign_for_name']=userdetails(data['assign_for'])
            # reporting_date = ETaskReportingDates.objects.filter(task=data['id'],task_type=2,is_deleted=False)

            # reporting_list = []
            # for r_date in reporting_date:
            #     # print('r_date.reporting_date-->',type(r_date.reporting_date))
            #     reporting_dict = {
            #         "follow_up_id" : r_date.task,
            #         "reporting_date" : r_date.reporting_date
            #     }
            #     reporting_list.append(reporting_dict)

            # data['reporting_dates'] = reporting_list
            task=EtaskTask.objects.filter(id=data['task'],is_deleted=False).values('task_subject','parent_id')
            if task:
                task_data={}
                task_data['task_subject']=task[0]['task_subject'] if task[0]['task_subject'] else ''

                if int(task[0]['parent_id']) != 0:
                    # parent_id_name = EtaskTask.objects.filter(id=data['id'],task_status=1,is_deleted=False,parent_id=data['parent_id']).values('task_subject')
                    parent_id_name = EtaskTask.objects.filter(is_deleted=False,id=task[0]['parent_id']).values('id','task_subject')
                    # print('parent_id_name-->',parent_id_name[0]['id'])
                    if parent_id_name:
                        task_data['parent'] = {
                            "id" :  task[0]['parent_id'],
                            "name" :parent_id_name[0]['task_subject']
                        }
                else :
                    task_data['parent'] = None
                data['task_name']=task_data
            else:
                data['task_name']=None

        return response
class EtaskUpcomingFollowUpListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskFollowUP.objects.filter(is_deleted=False,followup_status='pending')
    serializer_class = EtaskFollowUpListSerializer
    pagination_class = CSPageNumberPagination

    def get_queryset(self):
        filter = {}
        sort_field='-id'
        user_id=self.kwargs["user_id"]
        # current_date = self.request.query_params.get('current_date', None)
        follow_up_date = self.request.query_params.get('follow_up_date', None)
        # end_date = self.request.query_params.get('to_date', None)
        assign_to = self.request.query_params.get('assign_to', None)
        search = self.request.query_params.get('search', None)
        field_name = self.request.query_params.get('field_name', None)
        order_by = self.request.query_params.get('order_by', None)
        todays_date=date.today()
        print('todays_date',todays_date)

        if field_name and order_by:      
            if field_name =='follow_up_task' and order_by=='asc':
                sort_field='follow_up_task'
            if field_name =='follow_up_task' and order_by=='desc':
                sort_field='-follow_up_task'

            if field_name =='follow_up_date' and order_by=='asc':
                sort_field='follow_up_date'               
            if field_name =='follow_up_date' and order_by=='desc':
                sort_field='-follow_up_date'
            
            if field_name =='assign_to' and order_by=='asc':
                sort_field='assign_to'             
            if field_name =='assign_to' and order_by=='desc':
                sort_field='-assign_to'

        if follow_up_date or assign_to or search:
            if follow_up_date:
                from_object =datetime.strptime(follow_up_date, '%Y-%m-%d')
                filter['follow_up_date__date__gte']= from_object
                filter['follow_up_date__date__lte']= from_object + timedelta(days=1)

            if assign_to:
                filter['assign_to__in'] = list(map(int,assign_to.split(" ")))
           
            if search:
                search_data = search
                filter['follow_up_task__icontains']=search_data
            
        # return self.queryset.filter(Q(Q(Q(assign_for__isnull=False)&Q(assign_for=user_id))|Q(Q(assign_for__isnull=True)&Q(created_by=user_id))),follow_up_date__date__gt=todays_date,is_deleted=False,**filter).order_by(sort_field)
        return self.queryset.filter(created_by=user_id,follow_up_date__date__gt=todays_date,is_deleted=False,**filter).order_by(sort_field)

    @response_modify_decorator_list_or_get_after_execution_for_pagination
    def get(self, request, *args, **kwargs):

        response = super(EtaskUpcomingFollowUpListView,self).get(self, request, args, kwargs)
        # print("response",response)

        reporting_dict = {}

        follow_up_list = []
        for data in response.data['results']:


            comments_count = FollowupComments.objects.filter(followup=data['id'],is_deleted=False).count()

            data['comments_count'] = comments_count

            # print(data['id'],'<--comments_count-->',comments_count)

            create_by_name = User.objects.filter(id=data['created_by'],is_active=True).values('first_name','last_name')
            
            if create_by_name:
                u_first_name = create_by_name[0]['first_name'] if create_by_name[0]['first_name'] else ''
                u_last_name = create_by_name[0]['last_name'] if create_by_name[0]['last_name'] else ''
                data['created_by_name'] = u_first_name + ' ' +u_last_name

            assign_to_name = User.objects.filter(id=data['assign_to'],is_active=True).values('first_name','last_name')
            
            if assign_to_name:
                assign_to_first_name = assign_to_name[0]['first_name'] if assign_to_name[0]['first_name'] else ''
                assign_to_last_name = assign_to_name[0]['last_name'] if assign_to_name[0]['last_name'] else ''
                data['assign_to_name'] = assign_to_first_name + ' ' +assign_to_last_name
            else:
                data['assign_to_name'] = ""
            data['assign_for_name']=userdetails(data['assign_for'])
            # reporting_date = ETaskReportingDates.objects.filter(task=data['id'],task_type=2,is_deleted=False)

            # reporting_list = []
            # for r_date in reporting_date:
            #     # print('r_date.reporting_date-->',type(r_date.reporting_date))
            #     reporting_dict = {
            #         "follow_up_id" : r_date.task,
            #         "reporting_date" : r_date.reporting_date
            #     }
            #     reporting_list.append(reporting_dict)

            # data['reporting_dates'] = reporting_list
            task=EtaskTask.objects.filter(id=data['task'],is_deleted=False).values('task_subject','parent_id')
            if task:
                task_data={}
                task_data['task_subject']=task[0]['task_subject'] if task[0]['task_subject'] else ''

                if int(task[0]['parent_id']) != 0:
                    # parent_id_name = EtaskTask.objects.filter(id=data['id'],task_status=1,is_deleted=False,parent_id=data['parent_id']).values('task_subject')
                    parent_id_name = EtaskTask.objects.filter(is_deleted=False,id=task[0]['parent_id']).values('id','task_subject')
                    # print('parent_id_name-->',parent_id_name[0]['id'])
                    if parent_id_name:
                        task_data['parent'] = {
                            "id" :  task[0]['parent_id'],
                            "name" :parent_id_name[0]['task_subject']
                        }
                else :
                    task_data['parent'] = None
                data['task_name']=task_data
            else:
                data['task_name']=None

        return response
class EtaskOverdueFollowUpListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskFollowUP.objects.filter(is_deleted=False,followup_status='pending')
    serializer_class = EtaskFollowUpListSerializer
    pagination_class = CSPageNumberPagination

    def get_queryset(self):
        filter = {}
        sort_field='-id'
        user_id=self.kwargs["user_id"]
        # current_date = self.request.query_params.get('current_date', None)
        follow_up_date = self.request.query_params.get('follow_up_date', None)
        # end_date = self.request.query_params.get('to_date', None)
        assign_to = self.request.query_params.get('assign_to', None)
        search = self.request.query_params.get('search', None)
        field_name = self.request.query_params.get('field_name', None)
        order_by = self.request.query_params.get('order_by', None)
        todays_date=date.today()
        print('todays_date',todays_date)

        if field_name and order_by:      
            if field_name =='follow_up_task' and order_by=='asc':
                sort_field='follow_up_task'
            if field_name =='follow_up_task' and order_by=='desc':
                sort_field='-follow_up_task'

            if field_name =='follow_up_date' and order_by=='asc':
                sort_field='follow_up_date'               
            if field_name =='follow_up_date' and order_by=='desc':
                sort_field='-follow_up_date'
            
            if field_name =='assign_to' and order_by=='asc':
                sort_field='assign_to'             
            if field_name =='assign_to' and order_by=='desc':
                sort_field='-assign_to'

        if follow_up_date or assign_to or search:
            if follow_up_date:
                from_object =datetime.strptime(follow_up_date, '%Y-%m-%d')
                filter['follow_up_date__date__gte']= from_object
                filter['follow_up_date__date__lte']= from_object + timedelta(days=1)

            if assign_to:
                filter['assign_to__in'] = list(map(int,assign_to.split(" ")))
           
            if search:
                search_data = search
                filter['follow_up_task__icontains']=search_data
            
        # return self.queryset.filter(Q(Q(Q(assign_for__isnull=False)&Q(assign_for=user_id))|Q(Q(assign_for__isnull=True)&Q(created_by=user_id))),follow_up_date__date__lt=todays_date,is_deleted=False,**filter).order_by(sort_field)
        return self.queryset.filter(created_by=user_id,follow_up_date__date__lt=todays_date,is_deleted=False,**filter).order_by(sort_field)

    @response_modify_decorator_list_or_get_after_execution_for_pagination
    def get(self, request, *args, **kwargs):

        response = super(EtaskOverdueFollowUpListView,self).get(self, request, args, kwargs)
        # print("response",response)
        todays_date=date.today()
        reporting_dict = {}

        follow_up_list = []
        for data in response.data['results']:


            comments_count = FollowupComments.objects.filter(followup=data['id'],is_deleted=False).count()

            data['comments_count'] = comments_count

            # print(data['id'],'<--comments_count-->',comments_count)

            create_by_name = User.objects.filter(id=data['created_by'],is_active=True).values('first_name','last_name')
            
            if create_by_name:
                u_first_name = create_by_name[0]['first_name'] if create_by_name[0]['first_name'] else ''
                u_last_name = create_by_name[0]['last_name'] if create_by_name[0]['last_name'] else ''
                data['created_by_name'] = u_first_name + ' ' +u_last_name

            assign_to_name = User.objects.filter(id=data['assign_to'],is_active=True).values('first_name','last_name')
            
            if assign_to_name:
                assign_to_first_name = assign_to_name[0]['first_name'] if assign_to_name[0]['first_name'] else ''
                assign_to_last_name = assign_to_name[0]['last_name'] if assign_to_name[0]['last_name'] else ''
                data['assign_to_name'] = assign_to_first_name + ' ' +assign_to_last_name

            data['assign_for_name']=userdetails(data['assign_for'])
            # reporting_date = ETaskReportingDates.objects.filter(task=data['id'],task_type=2,is_deleted=False)

            # reporting_list = []
            # for r_date in reporting_date:
            #     # print('r_date.reporting_date-->',type(r_date.reporting_date))
            #     reporting_dict = {
            #         "follow_up_id" : r_date.task,
            #         "reporting_date" : r_date.reporting_date
            #     }
            #     reporting_list.append(reporting_dict)

            # data['reporting_dates'] = reporting_list
            if data['follow_up_date']:
                print('data',data['follow_up_date'])
                follow_up_date=datetime.strptime(data['follow_up_date'], '%Y-%m-%dT%H:%M:%S.%f').date()
                print('follow_up_date',follow_up_date)
                if follow_up_date < todays_date:
                    days_extended=(todays_date - follow_up_date).days
                    print("days_extended",days_extended)
                    if days_extended ==1:
                        data['overdue_by'] = str(days_extended)+" "+"day"
                    elif days_extended >1:
                        data['overdue_by'] = str(days_extended)+" "+"days"
                    else:
                        data['overdue_by'] = None


            task=EtaskTask.objects.filter(id=data['task'],is_deleted=False).values('task_subject','parent_id')
            if task:
                task_data={}
                task_data['task_subject']=task[0]['task_subject'] if task[0]['task_subject'] else ''

                if int(task[0]['parent_id']) != 0:
                    # parent_id_name = EtaskTask.objects.filter(id=data['id'],task_status=1,is_deleted=False,parent_id=data['parent_id']).values('task_subject')
                    parent_id_name = EtaskTask.objects.filter(is_deleted=False,id=task[0]['parent_id']).values('id','task_subject')
                    # print('parent_id_name-->',parent_id_name[0]['id'])
                    if parent_id_name:
                        task_data['parent'] = {
                            "id" :  task[0]['parent_id'],
                            "name" :parent_id_name[0]['task_subject']
                        }
                else :
                    task_data['parent'] = None
                data['task_name']=task_data
            else:
                data['task_name']=None

        return response

class EtaskFollowUpCompleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskFollowUP.objects.filter(is_deleted=False)
    serializer_class = EtaskFollowUpCompleteViewSerializer

class EtaskFollowUpDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskFollowUP.objects.filter(is_deleted=False)
    serializer_class = EtaskFollowUpDeleteSerializer

    @response_modify_decorator_update
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)


class EtaskFollowUpEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskFollowUP.objects.filter(is_deleted=False,followup_status='pending')
    serializer_class = EtaskFollowUpEditSerializer    

    # @response_modify_decorator_get_single_after_execution
    def get(self, request, *args, **kwargs):
        f_id = self.kwargs['pk']
        print('f_id-->',f_id)
        response = super(EtaskFollowUpEditView,self).get(self, request, args, kwargs)
        # r_date_dict = {}
        data_dict = {}

        # print('response-->',response.data)


        assign_to_name = User.objects.filter(id=response.data['assign_to'],is_active=True).values('first_name','last_name')
            
        if assign_to_name:
            assign_to_first_name = assign_to_name[0]['first_name'] if assign_to_name[0]['first_name'] else ''
            assign_to_last_name = assign_to_name[0]['last_name'] if assign_to_name[0]['last_name'] else ''
            response.data['assign_to_name'] = assign_to_first_name + ' ' +assign_to_last_name

        
        # get_reporting_dates = ETaskReportingDates.objects.filter(task_type=2,task=response.data['id'])
        # r_date_list = []
        # for r_dates in get_reporting_dates:
        #     r_date_dict = {
        #         'id' : r_dates.id,
        #         'followup_id' : response.data['id'],
        #         'reporting_date' : r_dates.reporting_date
        #     }
        #     r_date_list.append(r_date_dict)
        # response.data['reporting_dates'] = r_date_list

        data_dict['result'] = response.data
        if response.data:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_SUCCESS
        elif len(response.data) == 0:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_NO_DATA
        else:
            data_dict['request_status'] = 0
            data_dict['msg'] = settings.MSG_ERROR

        return Response(data_dict)

class EtaskFollowUpRescheduleView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskFollowUP.objects.filter(is_deleted=False)
    serializer_class = EtaskFollowUpRescheduleSerializer             



class ETaskAssignToListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = TCoreUserDetail.objects.filter(cu_is_deleted=False)
    # serializer_class = ETaskAssignToListSerializer

    def get(self, request, *args, **kwargs):
        user_id = request.user.id
        # print('user_id-->',user_id)
        data = {}
        data_dict = {}
        get_user_list = TCoreUserDetail.objects.filter(reporting_head=user_id,cu_is_deleted=False)
        # print('get_user_list-->',get_user_list)
        
        user_list = []
        for u_list in get_user_list:
            f_name = u_list.cu_user.first_name if u_list.cu_user.first_name else ''
            l_name = u_list.cu_user.last_name if u_list.cu_user.last_name else ''

            data = {
                'user_id' : u_list.cu_user.id,
                'user_name' : f_name +' '+l_name,
            }
            user_list.append(data)

        data_dict['result'] = user_list
        if user_list:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_SUCCESS
        elif len(user_list) == 0:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_NO_DATA
        else:
            data_dict['request_status'] = 0
            data_dict['msg'] = settings.MSG_ERROR
        # data = data_dict

        return Response(data_dict)


class ETaskSubAssignToListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request, *args, **kwargs):
        user_id = request.user.id
        # print('user_id-->',user_id)
        data = {}
        data_dict = {}
        user_list = []
        reporting_head = TCoreUserDetail.objects.filter(cu_user=user_id,cu_is_deleted=False).values_list('reporting_head',flat=True)
        print("reporting_head",reporting_head)
        if reporting_head:
            get_user_list = TCoreUserDetail.objects.filter(~Q(cu_user=user_id),reporting_head=reporting_head[0],cu_is_deleted=False)
            print('get_user_list-->',get_user_list)
        
        if get_user_list:
            for u_list in get_user_list:
                f_name = u_list.cu_user.first_name if u_list.cu_user.first_name else ''
                l_name = u_list.cu_user.last_name if u_list.cu_user.last_name else ''

                data = {
                    'user_id' : u_list.cu_user.id,
                    'user_name' : f_name +' '+l_name,
                }
                user_list.append(data)

        data_dict['result'] = user_list
        if user_list:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_SUCCESS
        elif len(user_list) == 0:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_NO_DATA
        else:
            data_dict['request_status'] = 0
            data_dict['msg'] = settings.MSG_ERROR

        return Response(data_dict)

class ETaskAppointmentAddView(generics.ListCreateAPIView,mixins.UpdateModelMixin):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskAppointment.objects.filter(is_deleted=False)
    serializer_class = ETaskAppointmentAddSerializer
    pagination_class = CSPageNumberPagination


    @response_modify_decorator_post
    def post(self, request, *args, **kwargs):
        return super(ETaskAppointmentAddView,self).post(request, *args, **kwargs)

    def get_queryset(self):
        sort_field='-id'
        app_id= self.request.query_params.get('app_id', None)
        appointment_tab = self.request.query_params.get('appointment_tab', None)
        search=self.request.query_params.get('search', None)
        from_date = self.request.query_params.get('from_date', None)
        to_date = self.request.query_params.get('to_date', None)
        field_name = self.request.query_params.get('field_name', None)
        order_by = self.request.query_params.get('order_by', None)
        filter={}
        user = self.request.user.username
        invite = EtaskInviteEmployee.objects.filter(user__username = user).values('appointment')
        ids = [x['appointment'] for x in invite]

        if field_name and order_by:      
            if field_name =='added_by' and order_by=='asc':
                sort_field='created_by_id'

            if field_name =='added_by' and order_by=='desc':
                sort_field='-created_by_id'

            if field_name =='from_date' and order_by=='asc':
                sort_field='start_date'

            if field_name =='from_date' and order_by=='desc':
                sort_field='-start_date'

            if field_name =='to_date' and order_by=='asc':
                sort_field='end_date'
                # return self.queryset.all().order_by('duration_end')
            if field_name =='to_date' and order_by=='desc':
                sort_field='-end_date'
                # return self.queryset.all().order_by('-duration_end')

        if from_date and to_date:
            from_object =datetime.strptime(from_date, '%Y-%m-%d')
            to_object =datetime.strptime(to_date, '%Y-%m-%d')
            filter['end_date__date__gte']= from_object
            filter['end_date__date__lte']= to_object + timedelta(days=1)
            # return self.queryset.filter(**filter)
        if search:
            filter['appointment_subject__icontains']=search

        if appointment_tab =="upcoming":
            if app_id:
                queryset = self.queryset.filter(id=app_id,Appointment_status='ongoing',**filter).order_by(sort_field)
                return queryset
            else:
                queryset = self.queryset.filter((Q(created_by__username=user)|Q(id__in=ids)),Appointment_status='ongoing',**filter).order_by(sort_field) 
                                               
                return queryset
        if appointment_tab =="history":
            if app_id:
                queryset = self.queryset.filter((Q(Appointment_status='Completed')|Q(Appointment_status='Cancelled')),
                                                        id=app_id,**filter).order_by(sort_field)
                return queryset
            else:
                queryset = self.queryset.filter((Q(created_by__username=user)| Q(id__in=ids))& 
                                                (Q(Appointment_status='Completed')|Q(Appointment_status='Cancelled')),
                                                    **filter).order_by(sort_field)
                return queryset

    @response_modify_decorator_list_or_get_after_execution_for_pagination
    def get(self,request,*args,**kwargs):
        # date = self.request.query_params.get('date',None)
        # date_converted_data = datetime.strptime(date,"%Y-%m-%d")
        # print('date_converted_data',date_converted_data)
        # # print(date_converted_data.time())
        # print("date",date,type(date))

        updated_by=request.user
        app_id = self.request.query_params.get('app_id', None)
        action = self.request.query_params.get('action', None)
        if action:
            if action.lower() =='complete':
                if app_id:
                    data = EtaskAppointment.objects.filter(id=app_id)
                    data.update(Appointment_status='completed',updated_by=updated_by)
                    response = data.filter(id=app_id).values()
                # return Response(response)

        response = super(ETaskAppointmentAddView,self).get(self, request, args, kwargs)
        data_list=[]
        for data in response.data['results']:
            # date_end = datetime.strptime(data['end_date'],"%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%dT%H:%M:%S.%f")
            # print(datetime.strptime(data['end_date'],"%Y-%m-%dT%H:%M:%S").date())

            comments_count = AppointmentComments.objects.filter(appointment=data['id'],is_deleted=False).count()
            # print('comments_count-->',comments_count)
            data['comments_count'] = comments_count

            if datetime.strptime(data['end_date'],"%Y-%m-%dT%H:%M:%S").date() <= datetime.now().date():
                if datetime.strptime(data['end_time'],"%H:%M:%S").time() < datetime.now().time():
                    EtaskAppointment.objects.filter(id=data['id'],is_deleted=False).update(appointment_overdue=True)
                    data['appointment_overdue']=True


            internal_invite = EtaskInviteEmployee.objects.filter(appointment=data['id'],is_deleted=False).values('user')
            external_invites = EtaskInviteExternalPeople.objects.filter(appointment=data['id'],is_deleted=False).values('external_people','external_email')
            data['internal_invite']=[{'user_id':user_d['user'],'user_name':userdetails(user_d['user'])} for user_d in internal_invite]
            data['external_invites']=external_invites
            data_list.append(data)
        
        # print(data_list)
        response.data['results']=data_list

        return response

    # def put(self, request, *args, **kwargs):

    #     updated_by=request.user
    #     app_id = self.request.query_params.get('app_id', None)
    #     action = self.request.query_params.get('action', None)
    #     if action.lower() =='complete':
    #         data = EtaskAppointment.objects.filter(id=app_id)
    #         data.update(Appointment_status='completed',updated_by=updated_by)
    #         response = data.filter(id=app_id).values()
    #         return Response(response)
        # if action.lower() =='delete':
        #     data = EtaskAppointment.objects.filter(id=app_id)
        #     data.update(Appointment_status='completed',updated_by=updated_by)
        #     response = data.filter(id=app_id).values()
        #     return Response(response)


class ETaskAppointmentUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskAppointment.objects.filter(is_deleted=False)
    serializer_class = ETaskAppointmentUpdateSerializer
    pagination_class = CSPageNumberPagination

class ETaskAppointmentCalanderView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskAppointment.objects.filter(is_deleted=False)
    serializer_class = ETaskAppointmentCalanderSerializer
    # pagination_class = CSPageNumberPagination

 
    def get_queryset(self):
        year = self.request.query_params.get('year',None)
        # weekly = self.request.query_params.get('weekly',None)
        user_id = self.request.user.id
        user = self.request.user.username
        # current_date = datetime.now().date()
        # seven_days = current_date + timedelta(days=7)
        # print("user",user)
        user_under_rh =[x['cu_user_id'] for x in TCoreUserDetail.objects.filter(reporting_head__username=user).values('cu_user_id').iterator()]
        user_under_rh.append(user_id)
        invite = EtaskInviteEmployee.objects.filter(user__in = user_under_rh).values('appointment')
        ids = [x['appointment'] for x in invite]
        print("ids",list(set(ids)))
        if year:
            # date_converted_data = datetime.strptime(year,"%Y"),"%Y")
            queryset = self.queryset.filter((Q(created_by__in=user_under_rh)| Q(id__in=list(set(ids)))),
                                            Appointment_status='ongoing',
                                            start_date__year=year,end_date__year=year)
        # elif year:
        #     # date_converted_data = datetime.strptime(year,"%Y"),"%Y")
        #     queryset = self.queryset.filter((Q(created_by__in=user_under_rh)| Q(id__in=list(set(ids)))),
        #                                     Appointment_status='ongoing',
        #                                     start_date__year=year,end_date__year=year)

        # else:
        #     queryset = self.queryset.filter((Q(created_by__in=user_under_rh)| Q(id__in=list(set(ids)))),
        #                                     Appointment_status='ongoing',
        #                                     start_date__lte=datetime.now(),end_date__gte=datetime.now())
        return queryset


    @response_modify_decorator_get_after_execution
    def get(self,request,*args,**kwargs):
        response = super(ETaskAppointmentCalanderView,self).get(self, request, args, kwargs)


        return response


class ETaskAppointmentCalanderWeeklyView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskAppointment.objects.filter(is_deleted=False)
    serializer_class = ETaskAppointmentCalanderSerializer
    # pagination_class = CSPageNumberPagination

 
    def get_queryset(self):
        user_id = self.request.user.id
        user = self.request.user.username
        current_date = datetime.now().date()
        seven_days = current_date + timedelta(days=7)
        # print("user",user)
        user_under_rh =[x['cu_user_id'] for x in TCoreUserDetail.objects.filter(reporting_head__username=user).values('cu_user_id').iterator()]
        user_under_rh.append(user_id)
        invite = EtaskInviteEmployee.objects.filter(user__in = user_under_rh).values('appointment')
        ids = [x['appointment'] for x in invite]
        print("ids",list(set(ids)))
        queryset = self.queryset.filter((Q(created_by__in=user_under_rh)| Q(id__in=list(set(ids)))),
                                        Appointment_status='ongoing',
                                        start_date__date__gte=current_date,end_date__date__lte=seven_days)
 
        return queryset


    @response_modify_decorator_get_after_execution
    def get(self,request,*args,**kwargs):
        response = super(ETaskAppointmentCalanderWeeklyView,self).get(self, request, args, kwargs)
        data_list=[]
        user_id = self.request.user.id
        user = self.request.user.username
        current_date = datetime.now().date()
        seven_days = current_date + timedelta(days=7)
        user_under_rh =[x['cu_user_id'] for x in TCoreUserDetail.objects.filter(reporting_head__username=user).values('cu_user_id').iterator()]
        user_under_rh.append(user_id)
        invite = EtaskInviteEmployee.objects.filter(user__in = user_under_rh).values('appointment')
        ids = [x['appointment'] for x in invite]
        print("ids",list(set(ids)))
        date_generated = [current_date + timedelta(days=x) for x in range(0, 7)]
        c=1
        weekly=[]
        
        for date in date_generated:
            day= {}
            print("queryset",self.queryset)
            val = EtaskAppointment.objects.filter((Q(created_by__in=user_under_rh)| Q(id__in=list(set(ids))))
                ,start_date__date__lte=date,end_date__date__gte=date,Appointment_status='ongoing').values()
            print("val",val)
            day["date"]=date
            day["events"]=val
            c=c+1
            weekly.append(day)
        response.data=weekly

        return response


class ETaskAppointmentCommentsView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = AppointmentComments.objects.filter(is_deleted=False)
    serializer_class = ETaskAppointmentCommentsSerializer
    @response_modify_decorator_get_after_execution
    def get(self,request,*args,**kwargs):
        response=super(ETaskAppointmentCommentsView,self).get(self, request, args, kwargs)
        for data in response.data:
            if data['advance_comment'] == True:
                cost_details=AppointmentIncludeAdvanceCommentsCostDetails.objects.filter(apcomments=data['id'],is_deleted=False)
                cost_details_list=[]
                for c_d in cost_details:
                    cost_data={
                        'id':c_d.id,
                        'cost_details':c_d.cost_details,
                        'cost':c_d.cost
                    }
                    cost_details_list.append(cost_data)
                data['cost_details']=cost_details_list
                other_details=AppointmentIncludeAdvanceCommentsOtherDetails.objects.filter(apcomments=data['id'],is_deleted=False)
                other_details_list=[]
                for o_d in other_details:
                    others_data={
                        'id':o_d.id,
                        'other_details':o_d.other_details,
                        'value':o_d.value
                    }
                    other_details_list.append(others_data)
                data['other_details']=other_details_list
                attachment_details=AppointmentIncludeAdvanceCommentsDocuments.objects.filter(apcomments=data['id'],is_deleted=False)
                attachment_list=[]
                for a_d in attachment_details:
                    attachments={
                        'id':a_d.id,
                        'document_name':a_d.document_name,
                        'document':request.build_absolute_uri(a_d.document.url)
                    }
                    attachment_list.append(attachments)
                data['attachments']=attachment_list
            else:
                data['cost_details']= []
                data['other_details']= []
                data['attachments']= []


        return response

class ETaskAppointmentCommentsAdvanceAttachmentAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = AppointmentIncludeAdvanceCommentsDocuments.objects.filter(is_deleted=False)
    serializer_class = ETaskAppointmentCommentsAdvanceAttachmentAddSerializer

class EtaskAppointmentCommentsListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = AppointmentComments.objects.filter(is_deleted=False)
    serializer_class = EtasCommentsListSerializer
    pagination_class = CSPageNumberPagination

    def get_queryset(self):
        appointment_id =self.request.query_params.get('appointment_id', None)
        return self.queryset.filter(is_deleted=False,appointment=appointment_id)


    @response_modify_decorator_list_or_get_after_execution_for_pagination
    def get(self,request,*args,**kwargs):
        response=super(EtaskAppointmentCommentsListView,self).get(self, request, args, kwargs)
        for data in response.data['results']:
            comment_by_name = User.objects.filter(id=data['created_by'],is_active=True).values('first_name','last_name')
            if comment_by_name:
                comment_by_name_first_name = comment_by_name[0]['first_name'] if comment_by_name[0]['first_name'] else ''
                comment_by_name_last_name = comment_by_name[0]['last_name'] if comment_by_name[0]['last_name'] else ''
                data['comment_by_name'] = comment_by_name_first_name + ' ' + comment_by_name_last_name
                data['comment_by_id'] = data['created_by']

            if data['advance_comment'] == True:
                cost_details=AppointmentIncludeAdvanceCommentsCostDetails.objects.filter(apcomments=data['id'],is_deleted=False)
                cost_details_list=[]
                for c_d in cost_details:
                    cost_data={
                        'id':c_d.id,
                        'cost_details':c_d.cost_details,
                        'cost':c_d.cost
                    }
                    cost_details_list.append(cost_data)
                data['cost_details']=cost_details_list
                other_details=AppointmentIncludeAdvanceCommentsOtherDetails.objects.filter(apcomments=data['id'],is_deleted=False)
                other_details_list=[]
                for o_d in other_details:
                    others_data={
                        'id':o_d.id,
                        'other_details':o_d.other_details,
                        'value':o_d.value
                    }
                    other_details_list.append(others_data)
                data['other_details']=other_details_list
                attachment_details=AppointmentIncludeAdvanceCommentsDocuments.objects.filter(apcomments=data['id'],is_deleted=False)
                attachment_list=[]
                for a_d in attachment_details:
                    attachments={
                        'id':a_d.id,
                        'document_name':a_d.document_name,
                        'document':request.build_absolute_uri(a_d.document.url)
                    }
                    attachment_list.append(attachments)
                data['attachments']=attachment_list
            else:
                data['cost_details']= []
                data['other_details']= []
                data['attachments']= []

        return response


####################################################################
class ETaskReportsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskTask.objects.filter(is_deleted=False)
    serializer_class = ETaskReportsSerializer
    pagination_class = CSPageNumberPagination

    def get_queryset(self):
        user=self.request.user.id

        filter = {}
        sort_field='-id'
        from_date = self.request.query_params.get('from_date', None)
        to_date = self.request.query_params.get('to_date', None)
        assign_by = self.request.query_params.get('assign_by', None)
        search = self.request.query_params.get('search', None)
        field_name = self.request.query_params.get('field_name', None)
        order_by = self.request.query_params.get('order_by', None)



        if field_name and order_by:      
            if field_name =='task_code_id' and order_by=='asc':
                sort_field='task_code_id'

            if field_name =='task_code_id' and order_by=='desc':
                sort_field='-task_code_id'

            if field_name =='task_subject' and order_by=='asc':
                sort_field='task_subject'

            if field_name =='task_subject' and order_by=='desc':
                sort_field='-task_subject'

            if field_name =='start_date' and order_by=='asc':
                sort_field='start_date'
                # return self.queryset.all().order_by('duration_end')
            if field_name =='start_date' and order_by=='desc':
                sort_field='-start_date'
                # return self.queryset.all().order_by('-duration_end')

            if field_name =='end_date' and order_by=='asc':
                sort_field='end_date'
                # return self.queryset.all().order_by('duration')
            if field_name =='end_date' and order_by=='desc':
                sort_field='-end_date'
                    # return self.queryset.all().order_by('-duration')
            if field_name =='assign_by' and order_by=='asc':
                sort_field='assign_by'
                # return self.queryset.all().order_by('duration')
            if field_name =='assign_by' and order_by=='desc':
                sort_field='-assign_by'

        if from_date or to_date or assign_by or search:

            if from_date and to_date:
                from_object =datetime.strptime(from_date, '%Y-%m-%d')
                to_object =datetime.strptime(to_date, '%Y-%m-%d')
                filter['end_date__date__gte']= from_object
                filter['end_date__date__lte']= to_object + timedelta(days=1)

            if assign_by:
                filter['assign_by__in'] = list(map(int,assign_by.split(" ")))
            print("filter",filter)
            if search:
                search_data = search
                print('search_data-->',search_data)
                ids= self.queryset.filter(((Q(sub_assign_to_user__isnull=True)&Q(assign_to=user))|
                                                (Q(sub_assign_to_user__isnull=False)&Q(sub_assign_to_user=user)))&
                                            Q(task_status=1,is_deleted=False),**filter).values_list('parent_id',flat=True)
                print("ids",ids)
                return self.queryset.filter(((Q(sub_assign_to_user__isnull=True)&Q(assign_to=user))|
                                                (Q(sub_assign_to_user__isnull=False)&Q(sub_assign_to_user=user)))&
                                                (Q(task_code_id__icontains=search_data)|Q(task_subject__icontains=search_data)),
                                                    task_status=1,is_deleted=False,**filter).order_by(sort_field)                            
                if queryset:
                    return queryset
                else:
                    check_data = EtaskTask.objects.filter(id__in=list(ids),task_subject__icontains=search_data).values_list('id',flat=True)
                    print("check_data",check_data)
                    return self.queryset.filter(((Q(sub_assign_to_user__isnull=True)&Q(assign_to=user))|
                                                (Q(sub_assign_to_user__isnull=False)&Q(sub_assign_to_user=user))),
                                                task_status=1,is_deleted=False,**filter).order_by(sort_field)
            else:
                queryset = self.queryset.filter(((Q(sub_assign_to_user__isnull=True)&Q(assign_to=user))|
                                                (Q(sub_assign_to_user__isnull=False)&Q(sub_assign_to_user=user))),
                                                task_status=1,is_deleted=False,**filter).order_by(sort_field)    
                return queryset                     
        else:
            return self.queryset.filter(((Q(sub_assign_to_user__isnull=True)&Q(assign_to=user))|
                                                (Q(sub_assign_to_user__isnull=False)&Q(sub_assign_to_user=user))),
                                                task_status=1,is_deleted=False,**filter).order_by(sort_field)
                                       
    @response_modify_decorator_list_or_get_after_execution_for_pagination
    def get(self, request, *args, **kwargs):
        response = super(ETaskReportsView, self).get(self, request, args, kwargs)
        user=self.request.user.id
        # print('user',user)
        for data in response.data['results']:
            # print('data',data)
            comments_count = ETaskComments.objects.filter(task=data['id'],is_deleted=False).count()
            data['comments_count'] = comments_count
            sub_assign_to_user = User.objects.filter(id=data['sub_assign_to_user'],is_active=True).values('first_name','last_name')
            # print('sub_assign_to_user-->',sub_assign_to_user)
            if user != data['sub_assign_to_user']:
                if sub_assign_to_user:
                    sub_assign_to_user_first_name = sub_assign_to_user[0]['first_name'] if sub_assign_to_user[0]['first_name'] else ''
                    sub_assign_to_user_last_name = sub_assign_to_user[0]['last_name'] if sub_assign_to_user[0]['last_name'] else ''
                    data['sub_assign_to_user'] = sub_assign_to_user_first_name + ' ' +sub_assign_to_user_last_name
            else:
                data['sub_assign_to_user'] = None
                data['assign_to'] = user
                

        return response


class EtaskUpcommingReportingListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskTask.objects.filter(is_deleted=False)
    serializer_class = EtaskUpcommingReportingListSerializer
    pagination_class = CSPageNumberPagination

    def get_queryset(self):
        user = self.request.user.id
        cur_date = datetime.now().date()

        filter = {}
        sort_field='-id'
        from_date = self.request.query_params.get('from_date', None)
        to_date = self.request.query_params.get('to_date', None)
        assign_by = self.request.query_params.get('assign_by', None)
        search = self.request.query_params.get('search', None)
        field_name = self.request.query_params.get('field_name', None)
        order_by = self.request.query_params.get('order_by', None)



        if field_name and order_by:      
            if field_name =='task_code_id' and order_by=='asc':
                sort_field='task_code_id'

            if field_name =='task_code_id' and order_by=='desc':
                sort_field='-task_code_id'

            if field_name =='task_subject' and order_by=='asc':
                sort_field='task_subject'

            if field_name =='task_subject' and order_by=='desc':
                sort_field='-task_subject'

            if field_name =='start_date' and order_by=='asc':
                sort_field='start_date'
                # return self.queryset.all().order_by('duration_end')
            if field_name =='start_date' and order_by=='desc':
                sort_field='-start_date'
                # return self.queryset.all().order_by('-duration_end')

            if field_name =='end_date' and order_by=='asc':
                sort_field='end_date'
                # return self.queryset.all().order_by('duration')
            if field_name =='end_date' and order_by=='desc':
                sort_field='-end_date'
                    # return self.queryset.all().order_by('-duration')
            if field_name =='assign_by' and order_by=='asc':
                sort_field='assign_by'
                # return self.queryset.all().order_by('duration')
            if field_name =='assign_by' and order_by=='desc':
                sort_field='-assign_by'

        if from_date or to_date or assign_by or search:

            if from_date and to_date:
                from_object =datetime.strptime(from_date, '%Y-%m-%d')
                to_object =datetime.strptime(to_date, '%Y-%m-%d')
                filter['end_date__date__gte']= from_object
                filter['end_date__date__lte']= to_object + timedelta(days=1)

            if assign_by:
                filter['assign_by__in'] = list(map(int,assign_by.split(" ")))
            print("filter",filter)
            if search:
                search_data = search
                print('search_data-->',search_data)
                ids= self.queryset.filter(((Q(sub_assign_to_user__isnull=True)&Q(assign_to=user))|
                                                (Q(sub_assign_to_user__isnull=False)&Q(sub_assign_to_user=user)))&
                                            Q(task_status=1,is_deleted=False,end_date__date__gt=cur_date),**filter).values_list('parent_id',flat=True)
                print("ids",ids)
                queryset =  self.queryset.filter(((Q(sub_assign_to_user__isnull=True)&Q(assign_to=user))|
                                                (Q(sub_assign_to_user__isnull=False)&Q(sub_assign_to_user=user)))&
                                                (Q(task_code_id__icontains=search_data)|Q(task_subject__icontains=search_data))&
                                            Q(task_status=1,is_deleted=False,end_date__date__gt=cur_date),**filter).order_by(sort_field)                            
                if queryset:
                    return queryset
                else:
                    check_data = EtaskTask.objects.filter(id__in=list(ids),task_subject__icontains=search_data).values_list('id',flat=True)
                    print("check_data",check_data)
                    queryset =  self.queryset.filter(((Q(sub_assign_to_user__isnull=True)&Q(assign_to=user))|
                                                (Q(sub_assign_to_user__isnull=False)&Q(sub_assign_to_user=user)))&
                                            Q(task_status=1,is_deleted=False,end_date__date__gt=cur_date),parent_id__in=list(check_data),**filter).order_by(sort_field) 

                    return queryset
                # else:
                #     pan_id = self.queryset.filter(((Q(sub_assign_to_user__isnull=True)&Q(assign_to=user))|
                #                                 (Q(sub_assign_to_user__isnull=False)&Q(sub_assign_to_user=user)))&
                #                             Q(task_status=1,is_deleted=False,end_date__date__gt=cur_date),**filter).values_list('parent_id', flat=True)
                #     print("pan_id",pan_id)
            else:
                queryset = self.queryset.filter(((Q(sub_assign_to_user__isnull=True)&Q(assign_to=user))|
                                                (Q(sub_assign_to_user__isnull=False)&Q(sub_assign_to_user=user)))&
                                                Q(task_status=1,is_deleted=False,end_date__date__gt=cur_date),**filter).order_by(sort_field)    
                return queryset                     
        else:
            return self.queryset.filter((((Q(sub_assign_to_user__isnull=True)&Q(assign_to=user))|
                                        (Q(sub_assign_to_user__isnull=False)&Q(sub_assign_to_user=user)))&
                                         Q(task_status=1,is_deleted=False,end_date__date__gt=cur_date)),**filter).order_by(sort_field)


    @response_modify_decorator_list_or_get_after_execution_for_pagination
    def get(self, request, *args, **kwargs):
        user = request.user.id

        response = super(EtaskUpcommingReportingListView, self).get(self, request, args, kwargs)
        user = request.user.id
        cur_date = datetime.now().date()

        for data in response.data['results']:

            comments_count = ETaskComments.objects.filter(task=data['id'],is_deleted=False).count()
            data['comments_count'] = comments_count
            
            assign_by = User.objects.filter(id=data['assign_by'],is_active=True).values('first_name','last_name')
            if assign_by:
                assign_by_first_name = assign_by[0]['first_name'] if assign_by[0]['first_name'] else ''
                assign_by_last_name = assign_by[0]['last_name'] if assign_by[0]['last_name'] else ''
                data['assign_by'] = assign_by_first_name + ' ' +assign_by_last_name


            sub_assign_to_user = User.objects.filter(id=data['sub_assign_to_user'],is_active=True).values('first_name','last_name')
            # print('sub_assign_to_user-->',sub_assign_to_user)
            if user != data['sub_assign_to_user']:
                if sub_assign_to_user:
                    sub_assign_to_user_first_name = sub_assign_to_user[0]['first_name'] if sub_assign_to_user[0]['first_name'] else ''
                    sub_assign_to_user_last_name = sub_assign_to_user[0]['last_name'] if sub_assign_to_user[0]['last_name'] else ''
                    data['sub_assign_to_user'] = sub_assign_to_user_first_name + ' ' +sub_assign_to_user_last_name
            else:
                data['sub_assign_to_user'] = None
                data['assign_to'] = user
            
            if int(data['parent_id']) != 0:
                # parent_id_name = EtaskTask.objects.filter(id=data['id'],task_status=1,is_deleted=False,parent_id=data['parent_id']).values('task_subject')
                parent_id_name = EtaskTask.objects.filter(task_status=1,is_deleted=False,id=data['parent_id']).values('id','task_subject')
                # print('parent_id_name-->',parent_id_name[0]['id'])
                if parent_id_name:
                    data['parent'] = {
                        "id" :  data['parent_id'],
                        "name" :parent_id_name[0]['task_subject']
                    }
            else :
                data['parent'] = None

            # print('id',data['id'])
            # print('cur_date-->',cur_date)
            reporting_date = ETaskReportingDates.objects.filter(task=data['id'],is_deleted=False,reporting_date__date__gte=cur_date,reporting_status=2)
            # print('reporting_date-->',reporting_date)
            if reporting_date:
                reporting_date_dict = {}
                reporting_date_list = []
                for r_date in reporting_date:
                    reporting_date_left = r_date.reporting_date.date() - cur_date
                    day_left_raw = str(reporting_date_left).split(',')[0] # + ' left'

                    reporting_date_dict = {
                        "id" : r_date.id,
                        "date" : r_date.reporting_date,
                        "left_days" : '0 Day left' if day_left_raw == '0:00:00' else day_left_raw + ' left' ,
                        "reporting_status" : r_date.get_reporting_status_display(),
                    }
                    reporting_date_list.append(reporting_date_dict) 
                    
                    data['reporting_date'] = reporting_date_list
            else:
                data['reporting_date'] = []
            
        return response


class EtaskReportingDateReportedView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = ETaskReportingDates.objects.filter(is_deleted=False)
    serializer_class = EtaskReportingDateReportedSerializer

    @response_modify_decorator_update
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

class EtaskReportingDateShiftView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    # queryset = ETaskReportingDates.objects.filter(is_deleted=False,reporting_status=2)
    queryset=EtaskTask.objects.filter(is_deleted=False)
    serializer_class = EtaskReportingDateShiftViewSerializer

    # @response_modify_decorator_update
    # def update(self, request, *args, **kwargs):
    #     return super().update(request, *args, **kwargs)

class ETaskAdminTaskReportView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskTask.objects.filter(is_deleted=False).order_by('-id')
    serializer_class =  ETaskAdminTaskReportSerializer
    pagination_class = CSPageNumberPagination

    def get_queryset(self):
        filter={}
        employee=self.request.query_params.get('employee',None)
        task_category=self.request.query_params.get('task_category',None)
        task_status=self.request.query_params.get('task_status',None)
        recurrance_frequency=self.request.query_params.get('recurrance_frequency',None)
        start_date=self.request.query_params.get('start_date',None)
        end_date=self.request.query_params.get('end_date',None)
        or_filter = []
        sort_field='-id'
        assign_by = self.request.query_params.get('assign_by', None)
        field_name = self.request.query_params.get('field_name', None)
        order_by = self.request.query_params.get('order_by', None)

        if field_name and order_by:      
            if field_name =='task_code_id' and order_by=='asc':
                sort_field='task_code_id'

            if field_name =='task_code_id' and order_by=='desc':
                sort_field='-task_code_id'

            if field_name =='task_subject' and order_by=='asc':
                sort_field='task_subject'

            if field_name =='task_subject' and order_by=='desc':
                sort_field='-task_subject'

            if field_name =='start_date' and order_by=='asc':
                sort_field='start_date'
                # return self.queryset.all().order_by('duration_end')
            if field_name =='start_date' and order_by=='desc':
                sort_field='-start_date'
                # return self.queryset.all().order_by('-duration_end')

            if field_name =='end_date' and order_by=='asc':
                sort_field='end_date'
                # return self.queryset.all().order_by('duration')
            if field_name =='end_date' and order_by=='desc':
                sort_field='-end_date'
                    # return self.queryset.all().order_by('-duration')
            if field_name =='assign_by' and order_by=='asc':
                sort_field='assign_by'
                # return self.queryset.all().order_by('duration')
            if field_name =='assign_by' and order_by=='desc':
                sort_field='-assign_by'

        user=self.request.user.id
        # print('user',user)
        users_list=(list(TCoreUserDetail.objects.filter((Q(reporting_head_id=user)|Q(hod_id=user)),cu_is_deleted=False).values_list('cu_user',flat=True)))
        # print('users_list',users_list)
        if employee or task_category or task_status or recurrance_frequency or (start_date and end_date):
            if employee:
                # queryset=self.queryset.filter((Q(assign_to_id=employee)|Q(sub_assign_to_user_id=employee)|Q(assign_by_id=employee)))
                # filter["Q('assign_to_id')|Q('sub_assign_to_user_id')|Q('assign_by_id')"]=employee
                # employee = None
                or_filter = [Q(**{'assign_to_id':employee})|Q(**{'sub_assign_to_user_id':employee})|
                        Q(**{'assign_by_id':employee})]
                # print('or_filter',or_filter)
               
            if task_category:
                filter['task_categories']=task_category
                
            if task_status:
                filter['task_status']=task_status

            if recurrance_frequency:
                filter['recurrance_frequency']=recurrance_frequency
               
            if start_date and end_date:
                start_object=datetime.strptime(start_date, '%Y-%m-%d').date()
                end_object=datetime.strptime(end_date, '%Y-%m-%d').date()
                filter['start_date__date__gte']=start_object
                filter['end_date__date__lte']=end_object
            # queryset=self.queryset.filter(Q(assign_to__in=users_list)|Q(assign_by__in=users_list)|Q(sub_assign_to_user__in=users_list)|Q(owner__in=users_list)).order_by('-id')
            if users_list:
                if filter and or_filter:
                    cvb =self.queryset.filter(functools.reduce(operator.or_,or_filter),Q(Q(assign_to__in=users_list)|Q(assign_by__in=users_list)|Q(sub_assign_to_user__in=users_list)|Q(owner__in=users_list)),**filter).order_by(sort_field)
                    # print('cvb',cvb)
                    return cvb
                elif filter:
                    return self.queryset.filter(Q(Q(assign_to__in=users_list)|Q(assign_by__in=users_list)|Q(sub_assign_to_user__in=users_list)|Q(owner__in=users_list)),**filter).order_by(sort_field)
                elif or_filter:
                    return self.queryset.filter(Q(functools.reduce(operator.or_,or_filter)) & Q(Q(assign_to__in=users_list)|Q(assign_by__in=users_list)|Q(sub_assign_to_user__in=users_list)|Q(owner__in=users_list)),**filter).order_by(sort_field)
                else:
                    return self.queryset.filter(Q(assign_to__in=users_list)|Q(assign_by__in=users_list)|Q(sub_assign_to_user__in=users_list)|Q(owner__in=users_list),**filter).order_by(sort_field)


        else:
            return self.queryset.filter(Q(assign_to__in=users_list)|Q(assign_by__in=users_list)|Q(sub_assign_to_user__in=users_list)|Q(owner__in=users_list),**filter).order_by(sort_field)
    
    @response_modify_decorator_list_or_get_after_execution_for_pagination
    def get(self, request, *args, **kwargs):
        response = super(ETaskAdminTaskReportView, self).get(self, request, args, kwargs)
        current_date = datetime.now().date()
        # print('current_date',current_date)
        for data in response.data['results']:
            comments_count = ETaskComments.objects.filter(task=data['id'],is_deleted=False).count()
            data['comments_count'] = comments_count
        
            report_date=ETaskReportingDates.objects.filter(task_type=1,task=data['id'],is_deleted=False).values('id','reporting_date')
           #koushik --code 
            # print('report_date',report_date)
            # report_date_list=[]
            # if report_date:
            #     for r_d in report_date:
            #         if r_d.reporting_date.date()<= current_date:
            #             report_data={
            #                 'id':r_d.id,
            #                 'reporting_date':r_d.reporting_date
            #             }
            #             report_date_list.append(report_data)

            data['reporting_dates']=report_date if report_date else []  
            data['task_status_id']=data['task_status']
            data['task_status']=data['task_status_name']
            data['task_overdue_days'] = None
            ids = report_date.filter().values_list('id',flat=True)
            print('ids',ids)
            reporting_action_log_final = []
            # reporting_action_log=ETaskReportingActionLog.objects.filter((Q(reporting_date__in=ids)|Q(reporting_date__isnull=True)),
            reporting_action_log=ETaskReportingActionLog.objects.filter(reporting_date__in=ids,
                                                                    task=data['id'],is_deleted=False).values('task','reporting_date__id',
                                                                    'reporting_date__reporting_date','updated_date','status')
            
            print("reporting_action_log",reporting_action_log)
            for x in reporting_action_log:
                # print('')
                reporting_log_dict={
                    'task':x['task'],
                    'reporting_date__id':x['reporting_date__id'],
                    'reporting_date':x['reporting_date__reporting_date'],
                    'updated_date':x['updated_date'],
                    'reporting_status':ETaskReportingActionLog.status_choice[x['status']-1][1]
                }
                reporting_action_log_final.append(reporting_log_dict)
            print("reporting_action_log",reporting_action_log_final)
            # reporting_action_list=[]                                                      
            # if reporting_action_log:
            #     for r_a in reporting_action_log:
            #         action_data={
            #             'id':r_a.id,
            #             'date_of_update':r_a.updated_date,
            #             'team_update':r_a.get_status_display()
            #         }
            #         reporting_action_list.append(action_data)         
            data['date_of_update_and_team_update']=reporting_action_log_final if reporting_action_log_final else []
            # else:                
            #     data['date_of_update_and_team_update']=[]
            # if data['extended_date']:
            #     e_date = datetime.strptime(datetime.strftime(datetime.strptime(data['extended_date'],"%Y-%m-%dT%H:%M:%S.%f"),"%Y-%m-%dT%H:%M:%S"),"%Y-%m-%dT%H:%M:%S").date()
            # if data['end_date']:
            #     en_date = datetime.strptime(datetime.strftime(datetime.strptime(data['end_date'],"%Y-%m-%dT%H:%M:%S.%f"),"%Y-%m-%dT%H:%M:%S"),"%Y-%m-%dT%H:%M:%S").date()
            # print('aff',type(data['end_date']))
            if data['task_status_name'] == 'Closed':
                data['task_status']=data['task_status_name']
                data['task_overdue_days'] = None

            elif data['task_status_name'] == 'Completed':
                data['task_status']=data['task_status_name']
                reporting_action_log=ETaskReportingActionLog.objects.filter((Q(reporting_date__in=ids)|Q(reporting_date__isnull=True)),
                                                            
                                                            task=data['id'],is_deleted=False).values_list('updated_date',flat=True)
                data['task_completed_date'] = reporting_action_log[0] if reporting_action_log else None
            elif data['extended_date']:
                if data['extended_date'] and datetime.strptime(data['extended_date'],"%Y-%m-%dT%H:%M:%S").date() <= current_date:
                    e_date = data['extended_date'].split('T')[0]
                    extended_date = datetime.strptime(e_date, '%Y-%m-%d').date()
                    days_extended=(current_date - extended_date).days
                    # print("days_extended",days_extended)
                    if days_extended >0:
                        data['task_status']="overdue"
                        data['task_overdue_days'] = days_extended
                    else:
                        # print("data['task_status_name']",data['task_status_name'])
                        data['task_status']=data['task_status_name']
                        data['task_overdue_days'] = None
            else:
                if data['end_date'] and datetime.strptime(data['end_date'],"%Y-%m-%dT%H:%M:%S").date() <= current_date:
                    en_date = data['end_date'].split('T')[0]
                    end_date = datetime.strptime(en_date, '%Y-%m-%d').date()
                    days_extended=(current_date - end_date).days
                    # print("days_extended",days_extended)
                    if days_extended >0:
                        data['task_status']="overdue"
                        data['task_overdue_days'] = days_extended
                    else:
                        data['task_status']=data['task_status_name']
                        data['task_overdue_days'] = None
        return response
class ETaskAdminAppointmentReportView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskAppointment.objects.filter(is_deleted=False)
    serializer_class =  ETaskAdminAppointmentReportSerializer
    pagination_class = CSPageNumberPagination
    
    def get_queryset(self):
        employee=self.request.query_params.get('employee',None)
        appointment_status=self.request.query_params.get('appointment_status',None)
        # print('appointment_status',appointment_status)
        start_date=self.request.query_params.get('start_date',None)
        end_date=self.request.query_params.get('end_date',None)
        filter={}
        user=self.request.user.id
        # user=employee
        # print('user',user)
        users_list=(list(TCoreUserDetail.objects.filter((Q(reporting_head_id=user)|Q(hod_id=user)),cu_is_deleted=False).values_list('cu_user',flat=True)))
        # print('users_list',users_list)
        invite = EtaskInviteEmployee.objects.filter(user__in = users_list).values('appointment')
        ids = [x['appointment'] for x in invite]
        print("ids",list(set(ids)))
        if employee or appointment_status or (start_date and end_date):
            if employee:
                invite_employee=EtaskInviteEmployee.objects.filter(user_id=employee,is_deleted=False).values_list('appointment',flat=True)
                # print('invite_employee',invite_employee)
                # queryset=self.queryset.filter(id__in=invite_employee)
                filter['id__in']=invite_employee
                
            if appointment_status:
                # return self.queryset.filter(Appointment_status=appointment_status)
                filter['Appointment_status']=appointment_status
                print('Appointment_status-->',filter['Appointment_status'])
            if start_date and end_date:
                start_object=datetime.strptime(start_date, '%Y-%m-%d').date()
                end_object=datetime.strptime(end_date, '%Y-%m-%d').date()
                # queryset=self.queryset.filter(start_date__date__gte=start_object,end_date__date__lte=end_object)
                filter['start_date__date__gte']=start_object
                filter['end_date__date__lte']=end_object
            if filter:
                get_filter =  self.queryset.filter((Q(created_by__in=users_list)| Q(id__in=list(set(ids)))),**filter)
                print('get_filter-->',get_filter)
                return get_filter

            else:
                self.queryset.filter(Q(created_by__in=users_list)| Q(id__in=list(set(ids))))
        else:
            return self.queryset.filter(Q(created_by__in=users_list)| Q(id__in=list(set(ids))))
        
    @response_modify_decorator_list_or_get_after_execution_for_pagination
    def get(self,request,*args,**kwargs):
        response=super(ETaskAdminAppointmentReportView,self).get(self, request, args, kwargs)
        for data in response.data['results']:
            # print('data',type(data['created_by']))
            internal_invite = EtaskInviteEmployee.objects.filter(appointment=data['id']).values('user')
            if internal_invite:
                data['internal_invite']=[{'user_id':user_d['user'],'user_name':userdetails(user_d['user'])} for user_d in internal_invite]
            else:
                data['internal_invite']=[]

            external_invite = EtaskInviteExternalPeople.objects.filter(appointment=data['id']).values('external_people','external_email')
            if external_invite:
                data['external_invite']=external_invite
            else:
                data['external_invite']=[]
                
            if data['created_by']:
                data['created_by_name']=userdetails(data['created_by'])
            else:
                data['created_by_name']=None
            comments_count = AppointmentComments.objects.filter(appointment=data['id'],is_deleted=False).count()
            # print('comments_count',comments_count)
            data['comments_count'] = comments_count

        return response


class ETaskAllCommentListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    pagination_class = CSPageNumberPagination
    # queryset = TCoreUserDetail.objects.filter(cu_is_deleted=False)
    # serializer_class = ETaskAllCommentsSerializer

    def get_queryset(self):
        comment_section = self.request.query_params.get('comment_section',None)
        if comment_section.lower() =='task':
            model = ETaskComments
            task_id =self.request.query_params.get('task_id', None)
            if task_id:
                return model.objects.filter(is_deleted=False,task=task_id).order_by('-id')
            else:
                return model.objects.filter(is_deleted=False).order_by('-id')
        elif comment_section.lower() =='followup':
            model = FollowupComments
            followup_id =self.request.query_params.get('followup_id', None)
            if followup_id:
                return model.objects.filter(is_deleted=False,followup=followup_id).order_by('-id')
            else:
                return model.objects.filter(is_deleted=False).order_by('-id')
        elif comment_section.lower() =='appointment':
            model = AppointmentComments
            appointment_id =self.request.query_params.get('appointment_id', None)
            if appointment_id:
                return model.objects.filter(is_deleted=False,appointment=appointment_id).order_by('-id')
            else:
                return model.objects.filter(is_deleted=False).order_by('-id')              

    def get_serializer_class(self):
        comment_section = self.request.query_params.get('comment_section',None)
        if comment_section.lower() =='task':
            ETaskAllCommentsSerializer.Meta.model = ETaskComments
            return ETaskAllCommentsSerializer
        elif comment_section.lower() =='followup':
            ETaskAllCommentsSerializer.Meta.model = FollowupComments
            return ETaskAllCommentsSerializer
        elif comment_section.lower() =='appointment':
            ETaskAllCommentsSerializer.Meta.model = AppointmentComments
            return ETaskAllCommentsSerializer
    @response_modify_decorator_list_or_get_after_execution_for_pagination
    def get(self,request,*args,**kwargs):
        comment_section = self.request.query_params.get('comment_section',None)
        if comment_section.lower() =='task':
            response=super(ETaskAllCommentListView,self).get(self, request, args, kwargs)
            for data in response.data['results']:
                cost_details=EtaskIncludeAdvanceCommentsCostDetails.objects.filter(etcomments=data['id'],is_deleted=False)
                cost_details_list=[]
                for c_d in cost_details:
                    cost_data={
                        'id':c_d.id,
                        'cost_details':c_d.cost_details,
                        'cost':c_d.cost
                    }
                    cost_details_list.append(cost_data)
                data['cost_details']=cost_details_list
                other_details=EtaskIncludeAdvanceCommentsOtherDetails.objects.filter(etcomments=data['id'],is_deleted=False)
                other_details_list=[]
                for o_d in other_details:
                    others_data={
                        'id':o_d.id,
                        'other_details':o_d.other_details,
                        'value':o_d.value
                    }
                    other_details_list.append(others_data)
                data['other_details']=other_details_list
                attachment_details=EtaskIncludeAdvanceCommentsDocuments.objects.filter(etcomments=data['id'],is_deleted=False)
                attachment_list=[]
                for a_d in attachment_details:
                    attachments={
                        'id':a_d.id,
                        'document_name':a_d.document_name,
                        'document':request.build_absolute_uri(a_d.document.url)
                    }
                    attachment_list.append(attachments)
                data['attachments']=attachment_list

            return response

        elif comment_section.lower() =='followup':
            response=super(ETaskAllCommentListView,self).get(self, request, args, kwargs)
            for data in response.data['results']:
                # print()
                if data['advance_comment'] == True:
                    cost_details=FollowupIncludeAdvanceCommentsCostDetails.objects.filter(flcomments=data['id'],is_deleted=False)
                    cost_details_list=[]
                    for c_d in cost_details:
                        cost_data={
                            'id':c_d.id,
                            'cost_details':c_d.cost_details,
                            'cost':c_d.cost
                        }
                        cost_details_list.append(cost_data)
                    data['cost_details']=cost_details_list
                    other_details=FollowupIncludeAdvanceCommentsOtherDetails.objects.filter(flcomments=data['id'],is_deleted=False)
                    other_details_list=[]
                    for o_d in other_details:
                        others_data={
                            'id':o_d.id,
                            'other_details':o_d.other_details,
                            'value':o_d.value
                        }
                        other_details_list.append(others_data)
                    data['other_details']=other_details_list
                    attachment_details=FollowupIncludeAdvanceCommentsDocuments.objects.filter(flcomments=data['id'],is_deleted=False)
                    attachment_list=[]
                    for a_d in attachment_details:
                        attachments={
                            'id':a_d.id,
                            'document_name':a_d.document_name,
                            'document':request.build_absolute_uri(a_d.document.url)
                        }
                        attachment_list.append(attachments)
                    data['attachments']=attachment_list
                else:
                    data['cost_details']= []
                    data['other_details']= []
                    data['attachments']= []


            return response
        elif comment_section.lower() =='appointment':
            response=super(ETaskAllCommentListView,self).get(self, request, args, kwargs)
            for data in response.data['results']:
                print(data['advance_comment'])
                if data['advance_comment'] == True:
                    cost_details=AppointmentIncludeAdvanceCommentsCostDetails.objects.filter(apcomments=data['id'],is_deleted=False)
                    cost_details_list=[]
                    for c_d in cost_details:
                        cost_data={
                            'id':c_d.id,
                            'cost_details':c_d.cost_details,
                            'cost':c_d.cost
                        }
                        cost_details_list.append(cost_data)
                    data['cost_details']=cost_details_list
                    other_details=AppointmentIncludeAdvanceCommentsOtherDetails.objects.filter(apcomments=data['id'],is_deleted=False)
                    other_details_list=[]
                    for o_d in other_details:
                        others_data={
                            'id':o_d.id,
                            'other_details':o_d.other_details,
                            'value':o_d.value
                        }
                        other_details_list.append(others_data)
                    data['other_details']=other_details_list
                    attachment_details=AppointmentIncludeAdvanceCommentsDocuments.objects.filter(apcomments=data['id'],is_deleted=False)
                    attachment_list=[]
                    for a_d in attachment_details:
                        attachments={
                            'id':a_d.id,
                            'document_name':a_d.document_name,
                            'document':request.build_absolute_uri(a_d.document.url)
                        }
                        attachment_list.append(attachments)
                    data['attachments']=attachment_list
                else:
                    data['cost_details']= []
                    data['other_details']= []
                    data['attachments']= []

            # response.data['results'] = data
            return response


class ETaskAllCommentDocumentListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    # queryset = TCoreUserDetail.objects.filter(cu_is_deleted=False)
    # serializer_class = ETaskAllCommentsSerializer

    def get_queryset(self):
        comment_section = self.request.query_params.get('comment_section',None)
        if comment_section.lower() =='task':
            model = EtaskIncludeAdvanceCommentsDocuments
            return model.objects.filter(is_deleted=False) 
        elif comment_section.lower() =='followup':
            model = FollowupIncludeAdvanceCommentsDocuments
            return model.objects.filter(is_deleted=False)
        elif comment_section.lower() =='appointment':
            model = AppointmentIncludeAdvanceCommentsDocuments
            return model.objects.filter(is_deleted=False)              

    def get_serializer_class(self):
        comment_section = self.request.query_params.get('comment_section',None)
        if comment_section.lower() =='task':
            ETaskAllCommentsDocumentSerializer.Meta.model = EtaskIncludeAdvanceCommentsDocuments
            return ETaskAllCommentsDocumentSerializer
        elif comment_section.lower() =='followup':
            ETaskAllCommentsDocumentSerializer.Meta.model = FollowupIncludeAdvanceCommentsDocuments
            return ETaskAllCommentsDocumentSerializer
        elif comment_section.lower() =='appointment':
            ETaskAllCommentsDocumentSerializer.Meta.model = AppointmentIncludeAdvanceCommentsDocuments
            return ETaskAllCommentsDocumentSerializer

class ETaskAppointmentCancelView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskAppointment.objects.filter(is_deleted=False)
    serializer_class = ETaskAppointmentCancelSerializer

class ETaskTeamOngoingTaskView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskTask.objects.filter(is_deleted=False)
    serializer_class = ETaskTeamOngoingTaskSerializer
    pagination_class = CSPageNumberPagination
    def get_queryset(self):
        user=self.request.user.id
        # print('user',user)
        all_type_task = self.request.query_params.get('all_type_task', None)
        users_list=(list(TCoreUserDetail.objects.filter((Q(reporting_head_id=user)|Q(hod_id=user)),cu_is_deleted=False).values_list('cu_user',flat=True)))
        # print('users_list',users_list)
        if users_list:
            if all_type_task == 'all':

                filter = {}
                sort_field='-id'
                from_date = self.request.query_params.get('from_date', None)
                to_date = self.request.query_params.get('to_date', None)
                assign_by = self.request.query_params.get('assign_by', None)
                search = self.request.query_params.get('search', None)
                field_name = self.request.query_params.get('field_name', None)
                order_by = self.request.query_params.get('order_by', None)

                if field_name and order_by:      
                    if field_name =='task_code_id' and order_by=='asc':
                        sort_field='task_code_id'

                    if field_name =='task_code_id' and order_by=='desc':
                        sort_field='-task_code_id'

                    if field_name =='task_subject' and order_by=='asc':
                        sort_field='task_subject'

                    if field_name =='task_subject' and order_by=='desc':
                        sort_field='-task_subject'

                    if field_name =='start_date' and order_by=='asc':
                        sort_field='start_date'
                        # return self.queryset.all().order_by('duration_end')
                    if field_name =='start_date' and order_by=='desc':
                        sort_field='-start_date'
                        # return self.queryset.all().order_by('-duration_end')

                    if field_name =='end_date' and order_by=='asc':
                        sort_field='end_date'
                        # return self.queryset.all().order_by('duration')
                    if field_name =='end_date' and order_by=='desc':
                        sort_field='-end_date'
                            # return self.queryset.all().order_by('-duration')
                    if field_name =='assign_by' and order_by=='asc':
                        sort_field='assign_by'
                        # return self.queryset.all().order_by('duration')
                    if field_name =='assign_by' and order_by=='desc':
                        sort_field='-assign_by'

                if from_date or to_date or assign_by or search:

                    if from_date and to_date:
                        from_object =datetime.strptime(from_date, '%Y-%m-%d')
                        to_object =datetime.strptime(to_date, '%Y-%m-%d')
                        filter['end_date__date__gte']= from_object
                        filter['end_date__date__lte']= to_object + timedelta(days=1)

                    if assign_by:
                        filter['assign_by__in'] = list(map(int,assign_by.split(" ")))
                    print("filter",filter)
                    if search:
                        search_data = search
                        print('search_data-->',search_data)
                        task_code = self.queryset.filter(is_deleted=False,task_code_id__icontains=search_data,**filter).values_list('id',flat=True)
                        print('task_code-->',task_code)
                        if task_code:
                            return self.queryset.filter((Q(assign_to__in=users_list)|Q(assign_by__in=users_list)|Q(sub_assign_to_user__in=users_list)|Q(owner__in=users_list)),
                                                        (Q(id__in=list(task_code))),is_deleted=False,**filter).order_by(sort_field)
                        else:
                            id1= self.queryset.filter((Q(assign_to__in=users_list)|Q(assign_by__in=users_list)|Q(sub_assign_to_user__in=users_list)|Q(owner__in=users_list)),
                                                        is_deleted=False,**filter).values_list('id',flat=True)
                            id2= self.queryset.filter((Q(assign_to__in=users_list)|Q(assign_by__in=users_list)|Q(sub_assign_to_user__in=users_list)|Q(owner__in=users_list)),
                                                            is_deleted=False,**filter).values_list('parent_id',flat=True)
                            ids=list(id1)+list(id2)
                            print("ids",ids)
                            check_data = EtaskTask.objects.filter(id__in=ids,task_subject__icontains=search_data).values_list('id',flat=True)
                            print("check_data",check_data)
                            return self.queryset.filter((Q(assign_to__in=users_list)|Q(assign_by__in=users_list)|Q(sub_assign_to_user__in=users_list)|Q(owner__in=users_list)),
                                                            (Q(parent_id__in=list(check_data))|Q(id__in=list(check_data))),
                                                                is_deleted=False,**filter).order_by(sort_field)
                        # return queryset
                    else:
                        queryset = self.queryset.filter((Q(assign_to__in=users_list)|Q(assign_by__in=users_list)|Q(sub_assign_to_user__in=users_list)|Q(owner__in=users_list)),
                                                        is_deleted=False,**filter).order_by(sort_field)    
                        return queryset                     
                else:
                    return self.queryset.filter(Q(assign_to__in=users_list)|Q(assign_by__in=users_list)|Q(sub_assign_to_user__in=users_list)|Q(owner__in=users_list)
                                                    ,is_deleted=False,**filter).order_by(sort_field)
            else:
                filter = {}
                sort_field='-id'
                from_date = self.request.query_params.get('from_date', None)
                to_date = self.request.query_params.get('to_date', None)
                assign_by = self.request.query_params.get('assign_by', None)
                search = self.request.query_params.get('search', None)
                field_name = self.request.query_params.get('field_name', None)
                order_by = self.request.query_params.get('order_by', None)

                if field_name and order_by:      
                    if field_name =='task_code_id' and order_by=='asc':
                        sort_field='task_code_id'

                    if field_name =='task_code_id' and order_by=='desc':
                        sort_field='-task_code_id'

                    if field_name =='task_subject' and order_by=='asc':
                        sort_field='task_subject'

                    if field_name =='task_subject' and order_by=='desc':
                        sort_field='-task_subject'

                    if field_name =='start_date' and order_by=='asc':
                        sort_field='start_date'
                        # return self.queryset.all().order_by('duration_end')
                    if field_name =='start_date' and order_by=='desc':
                        sort_field='-start_date'
                        # return self.queryset.all().order_by('-duration_end')

                    if field_name =='end_date' and order_by=='asc':
                        sort_field='end_date'
                        # return self.queryset.all().order_by('duration')
                    if field_name =='end_date' and order_by=='desc':
                        sort_field='-end_date'
                            # return self.queryset.all().order_by('-duration')
                    if field_name =='assign_by' and order_by=='asc':
                        sort_field='assign_by'
                        # return self.queryset.all().order_by('duration')
                    if field_name =='assign_by' and order_by=='desc':
                        sort_field='-assign_by'

                if from_date or to_date or assign_by or search:

                    if from_date and to_date:
                        from_object =datetime.strptime(from_date, '%Y-%m-%d')
                        to_object =datetime.strptime(to_date, '%Y-%m-%d')
                        filter['end_date__date__gte']= from_object
                        filter['end_date__date__lte']= to_object + timedelta(days=1)

                    if assign_by:
                        filter['assign_by__in'] = list(map(int,assign_by.split(" ")))
                    print("filter",filter)
                    if search:
                        search_data = search
                        print('search_data-->',search_data)
                        task_code = self.queryset.filter(task_status=1,is_deleted=False,task_code_id__icontains=search_data,**filter).values_list('id',flat=True)
                        print('task_code-->',task_code)
                        if task_code:
                            return self.queryset.filter((Q(assign_to__in=users_list)|Q(assign_by__in=users_list)|Q(sub_assign_to_user__in=users_list)|Q(owner__in=users_list)),
                                                        (Q(id__in=list(task_code))),task_status=1,is_deleted=False,**filter).order_by(sort_field)
                        else:
                            id1= self.queryset.filter((Q(assign_to__in=users_list)|Q(assign_by__in=users_list)|Q(sub_assign_to_user__in=users_list)|Q(owner__in=users_list)),
                                                        task_status=1,is_deleted=False,**filter).values_list('id',flat=True)
                            id2= self.queryset.filter((Q(assign_to__in=users_list)|Q(assign_by__in=users_list)|Q(sub_assign_to_user__in=users_list)|Q(owner__in=users_list)),
                                                            task_status=1,is_deleted=False,**filter).values_list('parent_id',flat=True)
                            ids=list(id1)+list(id2)
                            print("ids",ids)
                            check_data = EtaskTask.objects.filter(id__in=ids,task_subject__icontains=search_data).values_list('id',flat=True)
                            print("check_data",check_data)
                            return self.queryset.filter((Q(assign_to__in=users_list)|Q(assign_by__in=users_list)|Q(sub_assign_to_user__in=users_list)|Q(owner__in=users_list)),
                                                            (Q(parent_id__in=list(check_data))|Q(id__in=list(check_data))),
                                                                task_status=1,is_deleted=False,**filter).order_by(sort_field)                           
                        # return queryset
                    else:
                        queryset = self.queryset.filter((Q(assign_to__in=users_list)|Q(assign_by__in=users_list)|Q(sub_assign_to_user__in=users_list)|Q(owner__in=users_list)),
                                                        task_status=1,is_deleted=False,**filter).order_by(sort_field)    
                        return queryset                     
                else:
                    return self.queryset.filter(Q(task_status=1)&(Q(assign_to__in=users_list)|Q(assign_by__in=users_list)|Q(sub_assign_to_user__in=users_list)|Q(owner__in=users_list)),
                                                    task_status=1,is_deleted=False,**filter).order_by(sort_field)
            # return queryset
        else:
            return self.queryset.none()
    @response_modify_decorator_list_or_get_after_execution_for_pagination
    def get(self, request, *args, **kwargs):
        response = super(ETaskTeamOngoingTaskView, self).get(self, request, args, kwargs)
        for data in response.data['results']:
            comments_count = ETaskComments.objects.filter(task=data['id'],is_deleted=False).count()
            data['comments_count'] = comments_count
            # print('comments_count-->',comments_count)
            latest_comments = ETaskComments.objects.filter(task=data['id'],is_deleted=False).values('comments','created_by','created_at')
            # print('latest_comments-->',latest_comments)

            if latest_comments and int(comments_count) > 0 :
                commentns_created_by = User.objects.filter(id=latest_comments[comments_count-1]['created_by'],is_active=True).values('first_name','last_name')
                commentns_created_by_first_name = commentns_created_by[0]['first_name'] if commentns_created_by[0]['first_name'] else ''
                commentns_created_by_last_name = commentns_created_by[0]['last_name'] if commentns_created_by[0]['last_name'] else ''
                data['latest_comments'] = {
                     "comments" : latest_comments[comments_count-1]['comments'],
                     "created_by" : (commentns_created_by_first_name + ' ' + commentns_created_by_last_name),
                     "created_at" : latest_comments[comments_count-1]['created_at']
                 }
            else:
                data['latest_comments'] = None

        
            report_date=ETaskReportingDates.objects.filter(task_type=1,task=data['id'],is_deleted=False).values('id','reporting_date')
            data['reporting_dates']=report_date if report_date else []

        return response
class ETaskTeamCompletedTaskView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskTask.objects.filter(is_deleted=False)
    serializer_class =  ETaskTeamCompletedTaskSerializer
    pagination_class = CSPageNumberPagination
    def get_queryset(self):
        user=self.request.user.id
        # print('user',user)
        users_list=(list(TCoreUserDetail.objects.filter((Q(reporting_head_id=user)|Q(hod_id=user)),cu_is_deleted=False).values_list('cu_user',flat=True)))
        # print('users_list',users_list)
        if users_list:

            filter = {}
            sort_field='-id'
            from_date = self.request.query_params.get('from_date', None)
            to_date = self.request.query_params.get('to_date', None)
            assign_by = self.request.query_params.get('assign_by', None)
            search = self.request.query_params.get('search', None)
            field_name = self.request.query_params.get('field_name', None)
            order_by = self.request.query_params.get('order_by', None)


            if field_name and order_by:      
                if field_name =='task_code_id' and order_by=='asc':
                    sort_field='task_code_id'

                if field_name =='task_code_id' and order_by=='desc':
                    sort_field='-task_code_id'

                if field_name =='task_subject' and order_by=='asc':
                    sort_field='task_subject'

                if field_name =='task_subject' and order_by=='desc':
                    sort_field='-task_subject'

                if field_name =='start_date' and order_by=='asc':
                    sort_field='start_date'
                    # return self.queryset.all().order_by('duration_end')
                if field_name =='start_date' and order_by=='desc':
                    sort_field='-start_date'
                    # return self.queryset.all().order_by('-duration_end')

                if field_name =='end_date' and order_by=='asc':
                    sort_field='end_date'
                    # return self.queryset.all().order_by('duration')
                if field_name =='end_date' and order_by=='desc':
                    sort_field='-end_date'
                        # return self.queryset.all().order_by('-duration')
                if field_name =='assign_by' and order_by=='asc':
                    sort_field='assign_by'
                    # return self.queryset.all().order_by('duration')
                if field_name =='assign_by' and order_by=='desc':
                    sort_field='-assign_by'

            if from_date or to_date or assign_by or search:

                if from_date and to_date:
                    from_object =datetime.strptime(from_date, '%Y-%m-%d')
                    to_object =datetime.strptime(to_date, '%Y-%m-%d')
                    filter['end_date__date__gte']= from_object
                    filter['end_date__date__lte']= to_object + timedelta(days=1)

                if assign_by:
                    filter['assign_by__in'] = list(map(int,assign_by.split(" ")))
                print("filter",filter)
                if search:
                    search_data = search
                    print('search_data-->',search_data)
                    task_code = self.queryset.filter(task_status=2,is_deleted=False,task_code_id__icontains=search_data,**filter).values_list('id',flat=True)
                    print('task_code-->',task_code)
                    if task_code:
                        return self.queryset.filter((Q(assign_to__in=users_list)|Q(assign_by__in=users_list)|Q(sub_assign_to_user__in=users_list)|Q(owner__in=users_list)),
                                                    (Q(id__in=list(task_code))),task_status=2,is_deleted=False,**filter).order_by(sort_field)
                    else:
                        id1= self.queryset.filter((Q(assign_to__in=users_list)|Q(assign_by__in=users_list)|Q(sub_assign_to_user__in=users_list)|Q(owner__in=users_list)),
                                                            task_status=2,is_deleted=False,**filter).values_list('id',flat=True)
                        id2= self.queryset.filter((Q(assign_to__in=users_list)|Q(assign_by__in=users_list)|Q(sub_assign_to_user__in=users_list)|Q(owner__in=users_list)),
                                                            task_status=2,is_deleted=False,**filter).values_list('parent_id',flat=True)
                        ids=list(id1)+list(id2)
                        print("ids",ids)
                        check_data = EtaskTask.objects.filter(id__in=ids,task_subject__icontains=search_data).values_list('id',flat=True)
                        print("check_data",check_data)
                        return self.queryset.filter((Q(assign_to__in=users_list)|Q(assign_by__in=users_list)|Q(sub_assign_to_user__in=users_list)|Q(owner__in=users_list)),
                                                    (Q(parent_id__in=list(check_data))|Q(id__in=list(check_data))),
                                                    task_status=2,is_deleted=False,**filter).order_by(sort_field)

                    # return queryset
                else:
                    queryset = self.queryset.filter((Q(assign_to__in=users_list)|Q(assign_by__in=users_list)|Q(sub_assign_to_user__in=users_list)|Q(owner__in=users_list)),
                                                    task_status=2,is_deleted=False,**filter).order_by(sort_field)    
                    return queryset                     
            else:
                return self.queryset.filter((Q(assign_to__in=users_list)|Q(assign_by__in=users_list)|Q(sub_assign_to_user__in=users_list)|Q(owner__in=users_list)),
                                                        task_status=2,is_deleted=False,**filter).order_by(sort_field)
        else:
            return self.queryset.none()
    @response_modify_decorator_list_or_get_after_execution_for_pagination
    def get(self, request, *args, **kwargs):
        response = super(ETaskTeamCompletedTaskView, self).get(self, request, args, kwargs)
        for data in response.data['results']:
            comments_count = ETaskComments.objects.filter(task=data['id'],is_deleted=False).count()
            data['comments_count'] = comments_count
        return response

class ETaskTeamClosedTaskView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskTask.objects.filter(task_status=4,is_deleted=False)
    serializer_class =  ETaskTeamClosedTaskSerializer
    pagination_class = CSPageNumberPagination
    def get_queryset(self):
        user=self.request.user.id
        # print('user',user)
        users_list=(list(TCoreUserDetail.objects.filter((Q(reporting_head_id=user)|Q(hod_id=user)),cu_is_deleted=False).values_list('cu_user',flat=True)))
        # print('users_list',users_list)
        if users_list:

            filter = {}
            sort_field='-id'
            from_date = self.request.query_params.get('from_date', None)
            to_date = self.request.query_params.get('to_date', None)
            assign_by = self.request.query_params.get('assign_by', None)
            search = self.request.query_params.get('search', None)
            field_name = self.request.query_params.get('field_name', None)
            order_by = self.request.query_params.get('order_by', None)


            if field_name and order_by:      
                if field_name =='task_code_id' and order_by=='asc':
                    sort_field='task_code_id'

                if field_name =='task_code_id' and order_by=='desc':
                    sort_field='-task_code_id'

                if field_name =='task_subject' and order_by=='asc':
                    sort_field='task_subject'

                if field_name =='task_subject' and order_by=='desc':
                    sort_field='-task_subject'

                if field_name =='start_date' and order_by=='asc':
                    sort_field='start_date'
                    # return self.queryset.all().order_by('duration_end')
                if field_name =='start_date' and order_by=='desc':
                    sort_field='-start_date'
                    # return self.queryset.all().order_by('-duration_end')

                if field_name =='end_date' and order_by=='asc':
                    sort_field='end_date'
                    # return self.queryset.all().order_by('duration')
                if field_name =='end_date' and order_by=='desc':
                    sort_field='-end_date'
                        # return self.queryset.all().order_by('-duration')
                if field_name =='assign_by' and order_by=='asc':
                    sort_field='assign_by'
                    # return self.queryset.all().order_by('duration')
                if field_name =='assign_by' and order_by=='desc':
                    sort_field='-assign_by'

            if from_date or to_date or assign_by or search:

                if from_date and to_date:
                    from_object =datetime.strptime(from_date, '%Y-%m-%d')
                    to_object =datetime.strptime(to_date, '%Y-%m-%d')
                    filter['end_date__date__gte']= from_object
                    filter['end_date__date__lte']= to_object + timedelta(days=1)

                if assign_by:
                    filter['assign_by__in'] = list(map(int,assign_by.split(" ")))
                print("filter",filter)
                if search:
                    search_data = search
                    print('search_data-->',search_data)
                    task_code = self.queryset.filter(task_status=4,is_deleted=False,task_code_id__icontains=search_data,**filter).values_list('id',flat=True)
                    print('task_code-->',task_code)
                    if task_code:
                        return self.queryset.filter((Q(assign_to__in=users_list)|Q(assign_by__in=users_list)|Q(sub_assign_to_user__in=users_list)|Q(owner__in=users_list)),
                                                    (Q(id__in=list(task_code))),task_status=4,is_deleted=False,**filter).order_by(sort_field)
                    else:
                        id1= self.queryset.filter((Q(assign_to__in=users_list)|Q(assign_by__in=users_list)|Q(sub_assign_to_user__in=users_list)|Q(owner__in=users_list)),
                                                            task_status=4,is_deleted=False,**filter).values_list('id',flat=True)
                        id2= self.queryset.filter((Q(assign_to__in=users_list)|Q(assign_by__in=users_list)|Q(sub_assign_to_user__in=users_list)|Q(owner__in=users_list)),
                                                            task_status=4,is_deleted=False,**filter).values_list('parent_id',flat=True)
                        ids=list(id1)+list(id2)
                        print("ids",ids)
                        check_data = EtaskTask.objects.filter(id__in=ids,task_subject__icontains=search_data).values_list('id',flat=True)
                        print("check_data",check_data)
                        return self.queryset.filter((Q(assign_to__in=users_list)|Q(assign_by__in=users_list)|Q(sub_assign_to_user__in=users_list)|Q(owner__in=users_list)),
                                                    (Q(parent_id__in=list(check_data))|Q(id__in=list(check_data))),
                                                    task_status=4,is_deleted=False,**filter).order_by(sort_field)                 
                    # return queryset
                else:
                    queryset = self.queryset.filter((Q(assign_to__in=users_list)|Q(assign_by__in=users_list)|Q(sub_assign_to_user__in=users_list)|Q(owner__in=users_list)),
                                                    task_status=4,is_deleted=False,**filter).order_by(sort_field)    
                    return queryset                     
            else:
                return self.queryset.filter((Q(assign_to__in=users_list)|Q(assign_by__in=users_list)|Q(sub_assign_to_user__in=users_list)|Q(owner__in=users_list)),
                                            task_status=4,is_deleted=False,**filter).order_by(sort_field)
        else:
            return self.queryset.none()
    @response_modify_decorator_list_or_get_after_execution_for_pagination
    def get(self, request, *args, **kwargs):
        response = super(ETaskTeamClosedTaskView, self).get(self, request, args, kwargs)
        for data in response.data['results']:
            comments_count = ETaskComments.objects.filter(task=data['id'],is_deleted=False).count()
            data['comments_count'] = comments_count
        return response
class ETaskClosuresTaskListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskTask.objects.filter(task_status=2,is_deleted=False,is_closure=True,completed_date__isnull=False)
    serializer_class =  ETaskTeamClosedTaskSerializer
    pagination_class = CSPageNumberPagination
    def get_queryset(self):
        user=self.request.user.id
        # users_list=(list(TCoreUserDetail.objects.filter((Q(reporting_head_id=user)|Q(hod_id=user)),cu_is_deleted=False).values_list('cu_user',flat=True)))  
        login_user_details = self.request.user
        login_user = int(self.request.user.id)
        users_list=[login_user]
        is_hod = TCoreUserDetail.objects.filter(
                            hod = login_user_details,cu_is_deleted=False,cu_user__isnull=False)
        #print('is_hod',is_hod)
        hi_user_list_details = ''
        if is_hod:
            department_d = TCoreUserDetail.objects.filter(
                cu_user = login_user_details,cu_is_deleted=False,cu_user__isnull=False).values_list('department',flat=True)
            #print('department_d',department_d)
            if department_d:
                hi_user_list_details = TCoreUserDetail.objects.filter(department__in=department_d).values_list('cu_user',flat=True)
                #print('hi_user_list_details',hi_user_list_details)
                
        else:
            hi_user_list_details = TCoreUserDetail.objects.filter(
                reporting_head = login_user_details,cu_is_deleted=False,cu_user__isnull=False).values_list('cu_user',flat=True)
            #print('hi_user_list_details',list(hi_user_list_details))
            hi_user_details1 = ''
            if hi_user_list_details.count() > 0 :
                for hi_user_details in hi_user_list_details:
                    hi_user_list_details = self.getLowerLevelUserList(str(hi_user_details),list(hi_user_list_details))
                
        print('hi_user_list_details',hi_user_list_details)
        if hi_user_list_details:
            users_list+=hi_user_list_details
            print("users_list",users_list)
            
        if users_list:
            # users_list.append(user)
            # print('users_list',users_list)
            filter = {}
            sort_field='-id'
            from_date = self.request.query_params.get('from_date', None)
            to_date = self.request.query_params.get('to_date', None)
            assign_by = self.request.query_params.get('assign_by', None)
            search = self.request.query_params.get('search', None)
            field_name = self.request.query_params.get('field_name', None)
            order_by = self.request.query_params.get('order_by', None)
            parent_task = self.request.query_params.get('parent_task', None)
            complete_by = self.request.query_params.get('complete_by', None)
            
            if parent_task:
                filter['parent_id'] = parent_task
            if complete_by:
                filter['completed_by'] = complete_by

            if field_name and order_by:      
                if field_name =='task_code_id' and order_by=='asc':
                    sort_field='task_code_id'
                if field_name =='task_code_id' and order_by=='desc':
                    sort_field='-task_code_id'

                if field_name =='task_subject' and order_by=='asc':
                    sort_field='task_subject'
                if field_name =='task_subject' and order_by=='desc':
                    sort_field='-task_subject'

                if field_name =='start_date' and order_by=='asc':
                    sort_field='start_date'                   
                if field_name =='start_date' and order_by=='desc':
                    sort_field='-start_date'
                    
                if field_name =='end_date' and order_by=='asc':
                    sort_field='end_date'                    
                if field_name =='end_date' and order_by=='desc':
                    sort_field='-end_date'
                       
                if field_name =='completed_date' and order_by=='asc':
                    sort_field='completed_date'
                if field_name =='completed_date' and order_by=='desc':
                    sort_field='-completed_date'

                if field_name =='assign_by' and order_by=='asc':
                    sort_field='assign_by'
                if field_name =='assign_by' and order_by=='desc':
                    sort_field='-assign_by'

                if field_name =='completed_by' and order_by=='asc':
                    sort_field='completed_by'
                if field_name =='completed_by' and order_by=='desc':
                    sort_field='-completed_by'

            if from_date or to_date or assign_by or search:

                if from_date and to_date:
                    from_object =datetime.strptime(from_date, '%Y-%m-%d')
                    to_object =datetime.strptime(to_date, '%Y-%m-%d')
                    filter['end_date__date__gte']= from_object
                    filter['end_date__date__lte']= to_object + timedelta(days=1)

                if assign_by:
                    filter['assign_by__in'] = list(map(int,assign_by.split(" ")))
                
                if search:
                    search_data = search
                    print('search_data-->',search_data)
                    task_code = self.queryset.filter(task_code_id__icontains=search_data,**filter).values_list('id',flat=True)
                    print('task_code-->',task_code)
                    if task_code:
                        return self.queryset.filter((Q(assign_to__in=users_list)|Q(assign_by__in=users_list)|Q(sub_assign_to_user__in=users_list)|Q(owner__in=users_list)),
                                                    (Q(id__in=list(task_code))),**filter).order_by(sort_field)
                    else:
                        id1= self.queryset.filter((Q(assign_to__in=users_list)|Q(assign_by__in=users_list)|Q(sub_assign_to_user__in=users_list)|Q(owner__in=users_list)),
                                                            **filter).values_list('id',flat=True)
                        id2= self.queryset.filter((Q(assign_to__in=users_list)|Q(assign_by__in=users_list)|Q(sub_assign_to_user__in=users_list)|Q(owner__in=users_list)),
                                                           **filter).values_list('parent_id',flat=True)
                        ids=list(id1)+list(id2)
                        print("ids",ids)
                        check_data = EtaskTask.objects.filter(id__in=ids,task_subject__icontains=search_data).values_list('id',flat=True)
                        print("check_data",check_data)
                        return self.queryset.filter((Q(assign_to__in=users_list)|Q(assign_by__in=users_list)|Q(sub_assign_to_user__in=users_list)|Q(owner__in=users_list)),
                                                    (Q(parent_id__in=list(check_data))|Q(id__in=list(check_data))),
                                                    **filter).order_by(sort_field)                 
                    # return queryset
                else:
                    queryset = self.queryset.filter((Q(assign_to__in=users_list)|Q(assign_by__in=users_list)|Q(sub_assign_to_user__in=users_list)|Q(owner__in=users_list)),
                                                    **filter).order_by(sort_field)    
                    return queryset                     
            else:
                return self.queryset.filter((Q(assign_to__in=users_list)|Q(assign_by__in=users_list)|Q(sub_assign_to_user__in=users_list)|Q(owner__in=users_list)),**filter).order_by(sort_field)
                                          
        else:
            return self.queryset.none()
    @response_modify_decorator_list_or_get_after_execution_for_pagination
    def get(self, request, *args, **kwargs):
        response = super(ETaskClosuresTaskListView, self).get(self, request, args, kwargs)
        # user=self.request.user.id
        # print('user',user)
        # users_list=(list(TCoreUserDetail.objects.filter((Q(reporting_head_id=user)|Q(hod_id=user)),cu_is_deleted=False).values_list('cu_user',flat=True))) 
        login_user_details = self.request.user
        login_user = int(self.request.user.id)
        users_list=[login_user]
        is_hod = TCoreUserDetail.objects.filter(
                            hod = login_user_details,cu_is_deleted=False,cu_user__isnull=False)
        #print('is_hod',is_hod)
        hi_user_list_details = ''
        if is_hod:
            department_d = TCoreUserDetail.objects.filter(
                cu_user = login_user_details,cu_is_deleted=False,cu_user__isnull=False).values_list('department',flat=True)
            #print('department_d',department_d)
            if department_d:
                hi_user_list_details = TCoreUserDetail.objects.filter(department__in=department_d).values_list('cu_user',flat=True)
                #print('hi_user_list_details',hi_user_list_details)
                
        else:
            hi_user_list_details = TCoreUserDetail.objects.filter(
                reporting_head = login_user_details,cu_is_deleted=False,cu_user__isnull=False).values_list('cu_user',flat=True)
            #print('hi_user_list_details',list(hi_user_list_details))
            hi_user_details1 = ''
            if hi_user_list_details.count() > 0 :
                for hi_user_details in hi_user_list_details:
                    hi_user_list_details = self.getLowerLevelUserList(str(hi_user_details),list(hi_user_list_details))
                
        print('hi_user_list_details',hi_user_list_details)
        if hi_user_list_details:
            users_list+=hi_user_list_details
            print("users_list",users_list)     
        if users_list:
            # users_list.append(user)      
            for data in response.data['results']:
                data['completed_by_name']=userdetails(data['completed_by'])
                data['assign_by_name']=userdetails(data['assign_by'])
                unread_comments_count = ETaskCommentsViewers.objects.filter(task=data['id'],user__in=users_list,is_view=False,is_deleted=False).count()
                data['unread_comments_count'] = unread_comments_count
        return response
    
    def getLowerLevelUserList(self, user_id='',main_list='') -> list:
        try:
            #print('user_id',user_id)
            #print('main_list',main_list)
            hi_user_list_details =TCoreUserDetail.objects.filter(reporting_head_id = str(user_id),cu_is_deleted=False,cu_user__isnull=False).values_list(
                'cu_user_id',flat=True)
            #print('hi_user_list_details1111',hi_user_list_details)
            if hi_user_list_details.count() > 0 :
                for hi_user_details in hi_user_list_details:
                    main_list.append(hi_user_details)
                    self.getLowerLevelUserList(str(hi_user_details),main_list)
            return main_list
        except Exception as e:
            raise e


class ETaskTeamOverdueTaskView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskTask.objects.filter(task_status=1,is_deleted=False)
    serializer_class =   ETaskTeamOverdueTaskSerializer
    pagination_class = CSPageNumberPagination
    def get_queryset(self):
        user=self.request.user.id
        current_date=datetime.now().date()
        # print('current_date',current_date)
        # print('user',user)
        users_list=(list(TCoreUserDetail.objects.filter((Q(reporting_head_id=user)|Q(hod_id=user)),cu_is_deleted=False).values_list('cu_user',flat=True)))
        # print('users_list',users_list)
        if users_list:

            filter = {}
            sort_field='-id'
            from_date = self.request.query_params.get('from_date', None)
            to_date = self.request.query_params.get('to_date', None)
            assign_by = self.request.query_params.get('assign_by', None)
            search = self.request.query_params.get('search', None)
            field_name = self.request.query_params.get('field_name', None)
            order_by = self.request.query_params.get('order_by', None)



            if field_name and order_by:      
                if field_name =='task_code_id' and order_by=='asc':
                    sort_field='task_code_id'

                if field_name =='task_code_id' and order_by=='desc':
                    sort_field='-task_code_id'

                if field_name =='task_subject' and order_by=='asc':
                    sort_field='task_subject'

                if field_name =='task_subject' and order_by=='desc':
                    sort_field='-task_subject'

                if field_name =='start_date' and order_by=='asc':
                    sort_field='start_date'
                    # return self.queryset.all().order_by('duration_end')
                if field_name =='start_date' and order_by=='desc':
                    sort_field='-start_date'
                    # return self.queryset.all().order_by('-duration_end')

                if field_name =='end_date' and order_by=='asc':
                    sort_field='end_date'
                    # return self.queryset.all().order_by('duration')
                if field_name =='end_date' and order_by=='desc':
                    sort_field='-end_date'
                        # return self.queryset.all().order_by('-duration')
                if field_name =='assign_by' and order_by=='asc':
                    sort_field='assign_by'
                    # return self.queryset.all().order_by('duration')
                if field_name =='assign_by' and order_by=='desc':
                    sort_field='-assign_by'

            if from_date or to_date or assign_by or search:

                if from_date and to_date:
                    from_object =datetime.strptime(from_date, '%Y-%m-%d')
                    to_object =datetime.strptime(to_date, '%Y-%m-%d')
                    filter['end_date__date__gte']= from_object
                    filter['end_date__date__lte']= to_object + timedelta(days=1)

                if assign_by:
                    filter['assign_by__in'] = list(map(int,assign_by.split(" ")))
                print("filter",filter)
                if search:
                    search_data = search
                    print('search_data-->',search_data)
                    task_code = self.queryset.filter(task_status=1,is_deleted=False,task_code_id__icontains=search_data,**filter).values_list('id',flat=True)
                    print('task_code-->',task_code)
                    if task_code:
                        return self.queryset.filter((Q(Q(assign_to__in=users_list)|Q(assign_by__in=users_list)|Q(sub_assign_to_user__in=users_list)|Q(owner__in=users_list)) &
                                                        Q(Q(Q(extended_date__isnull=False)&Q(extended_date__date__lt=current_date))|
                                                        Q(Q(extended_date__isnull=True)&Q(end_date__date__lt=current_date)))),
                                                        (Q(id__in=list(task_code))),task_status=1,is_deleted=False,**filter).order_by(sort_field) 
                    else:
                        id1= self.queryset.filter((Q(assign_to__in=users_list)|Q(assign_by__in=users_list)|Q(sub_assign_to_user__in=users_list)|Q(owner__in=users_list)),
                                            task_status=1,is_deleted=False,**filter).values_list('id',flat=True)
                        id2= self.queryset.filter((Q(assign_to__in=users_list)|Q(assign_by__in=users_list)|Q(sub_assign_to_user__in=users_list)|Q(owner__in=users_list)),
                                                            task_status=1,is_deleted=False,**filter).values_list('parent_id',flat=True)
                        ids=list(id1)+list(id2)
                        print("ids",ids)
                        check_data = EtaskTask.objects.filter(id__in=ids,task_subject__icontains=search_data).values_list('id',flat=True)
                        print("check_data",check_data)

                        return self.queryset.filter((Q(Q(assign_to__in=users_list)|Q(assign_by__in=users_list)|Q(sub_assign_to_user__in=users_list)|Q(owner__in=users_list)) &
                                                        Q(Q(Q(extended_date__isnull=False)&Q(extended_date__date__lt=current_date))|
                                                        Q(Q(extended_date__isnull=True)&Q(end_date__date__lt=current_date)))),
                                                            (Q(parent_id__in=list(check_data))|Q(id__in=list(check_data))), 
                                                                task_status=1,is_deleted=False,**filter).order_by(sort_field)                            
                    # return queryset
                else:
                    return self.queryset.filter((Q(Q(assign_to__in=users_list)|Q(assign_by__in=users_list)|Q(sub_assign_to_user__in=users_list)|Q(owner__in=users_list)) &
                                                    Q(Q(Q(extended_date__isnull=False)&Q(extended_date__date__lt=current_date))|
                                                    Q(Q(extended_date__isnull=True)&Q(end_date__date__lt=current_date)))),
                                                    task_status=1,is_deleted=False,**filter).order_by(sort_field)                   
            else:
                return self.queryset.filter(Q(Q(assign_to__in=users_list)|Q(assign_by__in=users_list)|Q(sub_assign_to_user__in=users_list)|Q(owner__in=users_list)) &
                                            Q(Q(Q(extended_date__isnull=False)&Q(extended_date__date__lt=current_date))|
                                            Q(Q(extended_date__isnull=True)&Q(end_date__date__lt=current_date))),
                                            task_status=1,is_deleted=False,**filter).order_by(sort_field)
                # print('queryset',queryset.query)
                # return queryset
        else:
            return self.queryset.none()
    @response_modify_decorator_list_or_get_after_execution_for_pagination
    def get(self, request, *args, **kwargs):
        response = super(ETaskTeamOverdueTaskView, self).get(self, request, args, kwargs)
        current_date = datetime.now().date()
        # print('current_date',current_date)
        for data in response.data['results']:
            comments_count = ETaskComments.objects.filter(task=data['id'],is_deleted=False).count()
            data['comments_count'] = comments_count
            if data['extended_date']:
                if data['extended_date'] and datetime.strptime(data['extended_date'], '%Y-%m-%dT%H:%M:%S').date() <= current_date:
                    e_date = data['extended_date'].split('T')[0]
                    extended_date = datetime.strptime(e_date, '%Y-%m-%d').date()
                    days_extended=(current_date - extended_date).days
                    # print("days_extended",days_extended)
                    if days_extended >0:
                        data['overdue_by'] = days_extended
                    else:
                        data['overdue_by'] = None
            else:
                if data['end_date'] and datetime.strptime(data['end_date'], '%Y-%m-%dT%H:%M:%S').date() <= current_date:
                    en_date = data['end_date'].split('T')[0]
                    end_date = datetime.strptime(en_date, '%Y-%m-%d').date()
                    days_extended=(current_date - end_date).days
                    # print("days_extended",days_extended)
                    if days_extended >0:
                        data['overdue_by'] = days_extended
                    else:
                        data['overdue_by'] = None

            reporting_date = ETaskReportingDates.objects.filter(task=data['id'],task_type=1,is_deleted=False)
            reporting_list = []
            for r_date in reporting_date:
                # print('r_date.reporting_date-->',r_date.reporting_date)
                if r_date.reporting_date.date() >datetime.now().date():
                    reporting_dict = {
                        "id" : r_date.id,
                        "reporting_dates" : r_date.reporting_date,
                        "reporting_status":r_date.reporting_status,
                        "reporting_status_name":r_date.get_reporting_status_display(),
                        "crossed_by":0
                    }
                    reporting_list.append(reporting_dict)
                else:
                    reporting_dict = {
                        "id" : r_date.id,
                        "reporting_dates" : r_date.reporting_date,
                        "reporting_status":r_date.reporting_status,
                        "reporting_status_name":r_date.get_reporting_status_display(),
                        "crossed_by":(datetime.now().date()-r_date.reporting_date.date ()).days
                    }
                    reporting_list.append(reporting_dict)


            data['reporting_dates'] = reporting_list
            

        return response


class ETaskGetDetailForCommentListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    # pagination_class = CSPageNumberPagination
    # queryset = TCoreUserDetail.objects.filter(cu_is_deleted=False)
    # serializer_class = ETaskAllCommentsSerializer

    def get_queryset(self):
        section = self.request.query_params.get('section',None)
        if section.lower() =='task':
            model = EtaskTask
            task_id =self.request.query_params.get('task_id', None)
            if task_id:
                return model.objects.filter(is_deleted=False,id=task_id)
            else:
                return model.objects.filter(is_deleted=False) 
        elif section.lower() =='followup':
            model = EtaskFollowUP
            followup_id =self.request.query_params.get('followup_id', None)
            if followup_id:
                return model.objects.filter(is_deleted=False,id=followup_id)
            else:
                return model.objects.filter(is_deleted=False)
        elif section.lower() =='appointment':
            model = EtaskAppointment
            appointment_id =self.request.query_params.get('appointment_id', None)
            if appointment_id:
                return model.objects.filter(is_deleted=False,id=appointment_id)
            else:
                return model.objects.filter(is_deleted=False)              

    def get_serializer_class(self):
        section = self.request.query_params.get('section',None)
        if section.lower() =='task':
            ETaskGetDetailsCommentsSerializer.Meta.model = EtaskTask
            return ETaskGetDetailsCommentsSerializer
        elif section.lower() =='followup':
            ETaskGetDetailsCommentsSerializer.Meta.model = EtaskFollowUP
            return ETaskGetDetailsCommentsSerializer
        elif section.lower() =='appointment':
            ETaskGetDetailsCommentsSerializer.Meta.model = EtaskAppointment
            return ETaskGetDetailsCommentsSerializer
    @response_modify_decorator_get_after_execution
    def get(self,request,*args,**kwargs):
        section = self.request.query_params.get('section',None)
        if section.lower() =='task':
            response=super(ETaskGetDetailForCommentListView,self).get(self, request, args, kwargs)
            print("response ",response.data[0]['id'],type(response.data[0]['id']))
            for data in response.data:
                data['task_status_name']=EtaskTask.task_status_choice[data['task_status']-1][1]
                if int(data['parent_id']) != 0:
                    parent_id_name = EtaskTask.objects.filter(id=data['parent_id'],is_deleted=False).values('id','task_subject')
                    # print('parent_id_name-->',parent_id_name[0]['id'])
                    if parent_id_name:
                        data['parent'] = {
                            "id" :  data['parent_id'],
                            "name" :parent_id_name[0]['task_subject']
                        }
                else :
                    data['parent'] = None
                report_date=ETaskReportingDates.objects.filter(task_type=1,task=data['id'],is_deleted=False).values('id','reporting_date','reporting_status')
                # data['reporting_dates'] = report_date if report_date else []
                report_date_list=[]
                if report_date:
                    for x in report_date:
                        # print('')
                        report_date_dict={
                            'id':x['id'],
                            'reporting_date':x['reporting_date'],
                            'reporting_status':x['reporting_status'],
                            'reporting_status_name':ETaskReportingDates.status_choice[x['reporting_status']-1][1]
                        }
                        report_date_list.append(report_date_dict)
                    data['reporting_dates']=report_date_list
                else:
                    data['reporting_dates']=[]
                data['assign_to_name']= userdetails(data['assign_to'])
                data['assign_by_name']= userdetails(data['assign_by'])

            return response

        elif section.lower() =='followup':
            response=super(ETaskGetDetailForCommentListView,self).get(self, request, args, kwargs)
            for data in response.data:
                report_date=ETaskReportingDates.objects.filter(task_type=2,task=data['id'],is_deleted=False).values('id','reporting_date')
                data['reporting_dates'] = report_date if report_date else []
                data['assign_to_name']= userdetails(data['assign_to'])
                
            return response

        elif section.lower() =='appointment':
            response=super(ETaskGetDetailForCommentListView,self).get(self, request, args, kwargs)
            for data in response.data:
                internal_invite = EtaskInviteEmployee.objects.filter(appointment=data['id']).values('user')
                external_invites = EtaskInviteExternalPeople.objects.filter(appointment=data['id']).values('external_people','external_email')
                data['internal_invite']=[{'user_id':user_d['user'],'user_name':userdetails(user_d['user'])} for user_d in internal_invite]
                data['external_invites']=external_invites
            return response

class EtaskTaskCloseView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskTask.objects.filter(is_deleted=False)
    serializer_class = EtaskTaskCloseSerializer

    @response_modify_decorator_update
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)


class ETaskMassTaskCloseView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskTask.objects.filter(is_deleted=False)
    serializer_class = ETaskMassTaskCloseSerializer
    
    @response_modify_decorator_post
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class EmployeeListWithoutDetailsForETaskView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = User.objects.filter(is_superuser=False,is_active=True)
    serializer_class = EmployeeListWithoutDetailsForETaskSerializer
    pagination_class = OnOffPagination

    def get_queryset(self):
        search_key = self.request.query_params.get('search_key', None)
        module= self.request.query_params.get('module', None)
        team_approval_flag = self.request.query_params.get('team_approval_flag', None)
        login_user_details = self.request.user
        # print('login_user_details',login_user_details)

        if login_user_details.is_superuser == False:
            if team_approval_flag == '1' and module is None:
                is_hod = TCoreUserDetail.objects.filter(
                            hod = login_user_details,cu_is_deleted=False,cu_user__isnull=False)
                
                if is_hod:
                    department_d = TCoreUserDetail.objects.filter(
                        cu_user = login_user_details,cu_is_deleted=False,cu_user__isnull=False).values_list('department',flat=True)
                    #print('department_d',department_d)
                    if department_d:
                        hi_user_list_details = TCoreUserDetail.objects.filter(~Q(cu_user=login_user_details),department__in=department_d).values_list('cu_user',flat=True)
                        #print('hi_user_list_details',hi_user_list_details)
                        if search_key:
                            return self.queryset.filter((Q(first_name__icontains=search_key) | Q(last_name__icontains=search_key)),pk__in=hi_user_list_details)
                        else:
                            return self.queryset.filter(pk__in=hi_user_list_details)
                else:
                    hi_user_list_details = TCoreUserDetail.objects.filter(
                                reporting_head = login_user_details,cu_is_deleted=False,cu_user__isnull=False).values_list('cu_user',flat=True)
                    #print('hi_user_list_details',list(hi_user_list_details))
                    hi_user_details1 = ''
                    if hi_user_list_details.count() > 0 :
                        for hi_user_details in hi_user_list_details:
                            hi_user_list_details = self.getLowerLevelUserList(str(hi_user_details),list(hi_user_list_details))
                        #print('hi_user_details1',hi_user_list_details)
                        if search_key:
                            return self.queryset.filter((Q(first_name__icontains=search_key) | Q(last_name__icontains=search_key)),pk__in=hi_user_list_details)
                        else:
                            return self.queryset.filter(pk__in=hi_user_list_details)     


                # if search_key:
                #     queryset = User.objects.filter((Q(first_name__icontains=search_key) | Q(last_name__icontains=search_key)),pk__in=(TCoreUserDetail.objects.filter(Q(reporting_head_id=login_user_details)|Q(hod_id=login_user_details)).values_list('cu_user_id',flat=True)))
                # else:
                #     queryset = User.objects.filter(pk__in=(TCoreUserDetail.objects.filter(Q(reporting_head_id=login_user_details)|Q(hod_id=login_user_details)).values_list('cu_user_id',flat=True)))
                    # print('queryset',queryset)
                #return queryset
        else:
            if search_key:
                queryset=self.queryset.filter((Q(first_name__icontains=search_key) | Q(last_name__icontains=search_key)))
            else:
                queryset=self.queryset.all()                                

            return queryset

    @response_modify_decorator_list_or_get_before_execution_for_onoff_pagination
    def get(self, request, *args, **kwargs):
        #print('self',self.response)
        return response  

    def getLowerLevelUserList(self, user_id='',main_list='') -> list:
        try:
            #print('user_id',user_id)
            #print('main_list',main_list)
            hi_user_list_details =TCoreUserDetail.objects.filter(reporting_head_id = str(user_id),cu_is_deleted=False,cu_user__isnull=False).values_list(
                'cu_user_id',flat=True)
            #print('hi_user_list_details1111',hi_user_list_details)
            if hi_user_list_details.count() > 0 :
                for hi_user_details in hi_user_list_details:
                    main_list.append(hi_user_details)
                    self.getLowerLevelUserList(str(hi_user_details),main_list)
            return main_list
        except Exception as e:
            raise e

class EtaskTodayAppointmentListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskInviteEmployee.objects.filter(is_deleted=False)
    serializer_class = EtaskTodayAppointmentListSerializer
    # pagination_class = CSPageNumberPagination

    def get_queryset(self):
        user = self.request.user.id
        print('user',user)
        cur_date = datetime.now().date()

        sdf= self.queryset.filter((Q(Q(appointment__start_date__date=cur_date)|Q(appointment__end_date__date=cur_date))|Q(Q(appointment__start_date__date__lte=cur_date)&Q(appointment__end_date__date__gte=cur_date))),
                                    user_id=user,appointment__Appointment_status='ongoing').order_by('-id')
        print('sdf',sdf)
        return sdf                               

    @response_modify_decorator_get_after_execution
    def get(self,request,*args,**kwargs):
        response=super(EtaskTodayAppointmentListView,self).get(self,request,args,kwargs)
        # print('response',response.data)
        for data in response.data:
            print('data',data['appointment'])
            # data['created_by_name'] = userdetails( data['created_by'])
            # data['owned_by_name'] = userdetails( data['owned_by'])

            comments_count = AppointmentComments.objects.filter(appointment=data['appointment'],is_deleted=False).count()
            data['comments_count'] = comments_count

            data['user_name'] = userdetails( data['user'])
            appointment_data = EtaskAppointment.objects.filter(id=data['appointment']).values('appointment_subject','start_date','end_date','start_time','end_time','location','created_by','owned_by')
            print('appointment_data-->',appointment_data[0]['appointment_subject'])
            data['appointment_subject'] = appointment_data[0]['appointment_subject']
            data['created_by'] = appointment_data[0]['created_by']
            data['created_by_name'] = userdetails(appointment_data[0]['created_by'])
            data['owned_by'] = appointment_data[0]['owned_by']
            data['owned_by_name'] =  userdetails(appointment_data[0]['owned_by'])
            data['location'] = appointment_data[0]['location']
            data['start_date'] = appointment_data[0]['start_date']
            data['end_date'] = appointment_data[0]['end_date']
            data['start_time'] = appointment_data[0]['start_time']
            data['end_time'] = appointment_data[0]['end_time']
            internal_invite = EtaskInviteEmployee.objects.filter(appointment_id=data['appointment'],is_deleted=False).values('user')
            external_invites = EtaskInviteExternalPeople.objects.filter(appointment_id=data['appointment'],is_deleted=False).values('external_people','external_email')
            data['internal_invite']=[{'user_id':user_d['user'],'user_name':userdetails(user_d['user'])} for user_d in internal_invite]
            data['external_invites']=external_invites
            data['id'] = data['appointment']
            data.pop('appointment')
           

        return response
class EtaskUpcomingAppointmentListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskInviteEmployee.objects.filter(is_deleted=False)
    serializer_class = EtaskTodayAppointmentListSerializer
    pagination_class = CSPageNumberPagination

    def get_queryset(self):
        user = self.request.user.id
        cur_date = datetime.now().date()
        field_name = self.request.query_params.get('field_name', None)
        order_by = self.request.query_params.get('order_by', None)
        if field_name and order_by:      
            if field_name =='added_by' and order_by=='asc':
                return self.queryset.filter(user__id=user,appointment__Appointment_status='ongoing',
                                    appointment__start_date__date__gt=cur_date).order_by('appointment__created_by')

            if field_name =='added_by' and order_by=='desc':
                return self.queryset.filter(user__id=user,appointment__Appointment_status='ongoing',
                                    appointment__start_date__date__gt=cur_date).order_by('-appointment__created_by')
            if field_name =='from_date' and order_by=='asc':
                return self.queryset.filter(user__id=user,appointment__Appointment_status='ongoing',
                                    appointment__start_date__date__gt=cur_date).order_by('appointment__start_date')

            if field_name =='from_date' and order_by=='desc':
                return self.queryset.filter(user__id=user,appointment__Appointment_status='ongoing',
                                    appointment__start_date__date__gt=cur_date).order_by('-appointment__start_date')

            if field_name =='to_date' and order_by=='asc':
                return self.queryset.filter(user__id=user,appointment__Appointment_status='ongoing',
                                    appointment__start_date__date__gt=cur_date).order_by('appointment__end_date')
                
            if field_name =='to_date' and order_by=='desc':
                return self.queryset.filter(user__id=user,appointment__Appointment_status='ongoing',
                                    appointment__start_date__date__gt=cur_date).order_by('-appointment__end_date')
                
        else:
            return self.queryset.filter(user__id=user,appointment__Appointment_status='ongoing',
                                    appointment__start_date__date__gt=cur_date).order_by('-id')

    @response_modify_decorator_list_or_get_after_execution_for_pagination
    def get(self,request,*args,**kwargs):
        response=super(EtaskUpcomingAppointmentListView,self).get(self,request,args,kwargs)
        for data in response.data['results']:

            comments_count = AppointmentComments.objects.filter(appointment=data['appointment'],is_deleted=False).count()
            data['comments_count'] = comments_count

            data['created_by_name'] = userdetails( data['created_by'])
            data['owned_by_name'] = userdetails( data['owned_by'])
            data['user_name'] = userdetails( data['user'])
            appointment_data = EtaskAppointment.objects.filter(id=data['appointment']).values('appointment_subject','start_date','end_date','start_time','end_time','location','created_by','owned_by')
            print('appointment_data-->',appointment_data[0]['appointment_subject'])
            data['appointment_subject'] = appointment_data[0]['appointment_subject']
            data['created_by'] = appointment_data[0]['created_by']
            data['created_by_name'] = userdetails(appointment_data[0]['created_by'])
            data['owned_by'] = appointment_data[0]['owned_by']
            data['owned_by_name'] =  userdetails(appointment_data[0]['owned_by'])
            data['location'] = appointment_data[0]['location']
            data['start_date'] = appointment_data[0]['start_date']
            data['end_date'] = appointment_data[0]['end_date']
            data['start_time'] = appointment_data[0]['start_time']
            data['end_time'] = appointment_data[0]['end_time']
            internal_invite = EtaskInviteEmployee.objects.filter(appointment_id=data['appointment'],is_deleted=False).values('user')
            external_invites = EtaskInviteExternalPeople.objects.filter(appointment_id=data['appointment'],is_deleted=False).values('external_people','external_email')
            data['internal_invite']=[{'user_id':user_d['user'],'user_name':userdetails(user_d['user'])} for user_d in internal_invite]
            data['external_invites']=external_invites
            data['id'] = data['appointment']
            data.pop('appointment')
           
        return response
#::::::::::::::::UPCOMING TASK ALONG WITH TEAM:::::::::::::::::::::::::::::::::::::#
class UpcomingTaskAlongWithTeamView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
                                  
    def get(self, request, *args, **kwargs):
        user=self.request.user.id
        print('user',user)
        cur_date=datetime.now().date()  
        data_dict={}                
        task_details= EtaskTask.objects.filter((Q(assign_to_id=user)|Q(assign_by_id=user)|Q(sub_assign_to_user_id=user)|Q(owner_id=user)),
                                                start_date__date__gt=cur_date,
                                                is_deleted=False,task_status=1).count()
         
        print('task_details',task_details)
        task_dict={
            "id":user,
            "name":userdetails(user),
            "my_task_count":task_details
        }
        data_dict['my_upcoming_task']=task_dict
        user_list=[]
        user_list_rh=(list(TCoreUserDetail.objects.filter((Q(hod_id=user)|Q(reporting_head_id=user)),cu_is_deleted=False).values_list('cu_user',flat=True).iterator()))
        print('user_list_rh',user_list_rh)
        if user_list_rh:
            for u_l_r in user_list_rh:
                user_task_details= EtaskTask.objects.filter((Q(assign_to_id=u_l_r)|Q(assign_by_id=u_l_r)|Q(sub_assign_to_user_id=u_l_r)|Q(owner_id=u_l_r)),
                                                start_date__date__gt=cur_date,
                                                is_deleted=False,task_status=1).count()
                user_details={
                    "id":u_l_r,
                    "name":userdetails(u_l_r),
                    "task_count":user_task_details
                }                
                user_list.append(user_details)
        data_dict['user_list_under_rh']=user_list if user_list else []
        u_dict={}
        u_dict['result']=data_dict
        if data_dict:
            u_dict['request_status']=1
            u_dict['msg']=settings.MSG_SUCCESS
        elif len(data_dict)==0:
            u_dict['request_status']=1
            u_dict['msg']=settings.MSG_NO_DATA
        else:
            u_dict['request_status']=0
            u_dict['msg']=settings.MSG_ERROR
        data_dict=u_dict
                    
        return Response(data_dict)

class UpcomingTaskPerUserView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskTask.objects.filter(is_deleted=False)
    serializer_class = UpcomingTaskPerUserSerializer
    pagination_class = CSPageNumberPagination

    def get_queryset(self):
        user_id=self.kwargs["user_id"]
        print('user_id',user_id)
        cur_date=datetime.now().date()
        sort_field='-id'
        field_name = self.request.query_params.get('field_name', None)
        order_by = self.request.query_params.get('order_by', None)
        from_date = self.request.query_params.get('from_date', None)
        to_date = self.request.query_params.get('to_date', None)
        assign_by = self.request.query_params.get('assign_by', None)
        search = self.request.query_params.get('search', None)
        filter = {}
        if field_name and order_by:      
            if field_name =='task_code_id' and order_by=='asc':
                sort_field='task_code_id'

            if field_name =='task_code_id' and order_by=='desc':
                sort_field='-task_code_id'

            if field_name =='task_subject' and order_by=='asc':
                sort_field='task_subject'

            if field_name =='task_subject' and order_by=='desc':
                sort_field='-task_subject'

            if field_name =='start_date' and order_by=='asc':
                sort_field='start_date'
                
            if field_name =='start_date' and order_by=='desc':
                sort_field='-start_date'
                
            if field_name =='end_date' and order_by=='asc':
                sort_field='end_date'
                
            if field_name =='end_date' and order_by=='desc':
                sort_field='-end_date'
                   
            if field_name =='assign_by' and order_by=='asc':
                sort_field='assign_by'
                
            if field_name =='assign_by' and order_by=='desc':
                sort_field='-assign_by'
                
        # return self.queryset.filter((Q(assign_to_id=user_id)|Q(assign_by_id=user_id)|Q(sub_assign_to_user_id=user_id)|Q(owner_id=user_id)),
        #                             start_date__date__gt=cur_date,
        #                             is_deleted=False,task_status=1).order_by(sort_field)

        if from_date or to_date or assign_by or search:

            if from_date and to_date:
                from_object =datetime.strptime(from_date, '%Y-%m-%d')
                to_object =datetime.strptime(to_date, '%Y-%m-%d')
                filter['end_date__date__gte']= from_object
                filter['end_date__date__lte']= to_object + timedelta(days=1)

            if assign_by:
                filter['assign_by__in'] = list(map(int,assign_by.split(" ")))
           
            if search:           
                task_code = self.queryset.filter(task_status=1,is_deleted=False,task_code_id__icontains=search).values_list('id',flat=True)
                print('task_code-->',task_code)
                if task_code:
                    # return all_queryset.filter(is_deleted=False,id__in=list(task_code),**filter).order_by(sort_field)
                    return self.queryset.filter((Q(assign_to_id=user_id)|Q(assign_by_id=user_id)|Q(sub_assign_to_user_id=user_id)|Q(owner_id=user_id)),
                                    start_date__date__gt=cur_date,id__in=list(task_code),
                                    is_deleted=False,task_status=1,**filter).order_by(sort_field)
                else:
                    id1= self.queryset.filter(Q(task_status=1,is_deleted=False),**filter).values_list('id',flat=True)
                    id2= self.queryset.filter(Q(task_status=1,is_deleted=False),**filter).values_list('parent_id',flat=True)
                    ids=list(id1)+list(id2)
                    print("ids",ids)
                    check_data = EtaskTask.objects.filter((Q(task_subject__icontains=search)),id__in=ids).values_list('id',flat=True)
                    print("check_data",check_data)
                    # return all_queryset.filter(Q(is_deleted=False),(Q(parent_id__in=list(check_data))|Q(id__in=list(check_data))),**filter).order_by(sort_field)  
                    return self.queryset.filter((Q(assign_to_id=user_id)|Q(assign_by_id=user_id)|Q(sub_assign_to_user_id=user_id)|Q(owner_id=user_id)),
                                    (Q(parent_id__in=list(check_data))|Q(id__in=list(check_data))),
                                    start_date__date__gt=cur_date,id__in=list(task_code),
                                    is_deleted=False,task_status=1,**filter).order_by(sort_field)
            else:
                return self.queryset.filter((Q(assign_to_id=user_id)|Q(assign_by_id=user_id)|Q(sub_assign_to_user_id=user_id)|Q(owner_id=user_id)),
                                    start_date__date__gt=cur_date,
                                    is_deleted=False,task_status=1,**filter).order_by(sort_field)
   
        else:
            return  self.queryset.filter((Q(assign_to_id=user_id)|Q(assign_by_id=user_id)|Q(sub_assign_to_user_id=user_id)|Q(owner_id=user_id)),
                                    start_date__date__gt=cur_date,
                                    is_deleted=False,task_status=1).order_by(sort_field)

    @response_modify_decorator_list_or_get_after_execution_for_pagination
    def get(self, request, *args, **kwargs):
        response=super(UpcomingTaskPerUserView,self).get(self,request,args,kwargs)
        for data in response.data['results']:
            comments_count = ETaskComments.objects.filter(task=data['id'],is_deleted=False).count()
            data['comments_count'] = comments_count
        return response

class UpcomingTaskReportingAlongWithTeamView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
                                  
    def get(self, request, *args, **kwargs):
        user=self.request.user.id
        print('user',user)
        cur_date=datetime.now().date()  
        data_dict={}                
        task_details= EtaskTask.objects.filter((Q(assign_to_id=user)|Q(assign_by_id=user)|Q(sub_assign_to_user_id=user)|Q(owner_id=user)),
                                                # start_date__date__gt=cur_date,
                                                Q(Q(task_status=1)|Q(task_status=3)),
                                                id__in=set(ETaskReportingDates.objects.filter(reporting_date__date__gt=cur_date,task_type=1,reporting_status=2
                                                ).values_list('task',flat=True)),
                                                is_deleted=False).count()
         
        print('task_details',task_details)
        task_dict={
            "id":user,
            "name":userdetails(user),
            "my_task_count":task_details
        }

        data_dict['my_upcoming_task']=task_dict
        user_list=[]
        user_list_rh=(list(TCoreUserDetail.objects.filter((Q(hod_id=user)|Q(reporting_head_id=user)),cu_is_deleted=False).values_list('cu_user',flat=True).iterator()))
        print('user_list_rh',user_list_rh)
        if user_list_rh:
            for u_l_r in user_list_rh:
                user_task_details= EtaskTask.objects.filter((Q(assign_to_id=u_l_r)|Q(assign_by_id=u_l_r)|Q(sub_assign_to_user_id=u_l_r)|Q(owner_id=u_l_r)),
                                                Q(Q(task_status=1)|Q(task_status=3)),
                                                id__in=set(ETaskReportingDates.objects.filter(reporting_date__date__gt=cur_date,task_type=1,reporting_status=2
                                                ).values_list('task',flat=True)),
                                                is_deleted=False).count()
                user_details={
                    "id":u_l_r,
                    "name":userdetails(u_l_r),
                    "task_count":user_task_details
                }

                user_list.append(user_details)
        data_dict['user_list_under_rh']=user_list if user_list else []
        u_dict={}
        u_dict['result']=data_dict
        if data_dict:
            u_dict['request_status']=1
            u_dict['msg']=settings.MSG_SUCCESS
        elif len(data_dict)==0:
            u_dict['request_status']=1
            u_dict['msg']=settings.MSG_NO_DATA
        else:
            u_dict['request_status']=0
            u_dict['msg']=settings.MSG_ERROR
        data_dict=u_dict
                    
        return Response(data_dict)

class UpcomingTaskReportingPerUserView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskTask.objects.filter(is_deleted=False)
    serializer_class = UpcomingTaskReportingPerUserSerializer
    pagination_class = CSPageNumberPagination

    def get_queryset(self):
        user_id=self.kwargs["user_id"]
        print('user_id',user_id)
        cur_date=datetime.now().date()
        sort_field='-id'
        field_name = self.request.query_params.get('field_name', None)
        order_by = self.request.query_params.get('order_by', None)
        from_date = self.request.query_params.get('from_date', None)
        to_date = self.request.query_params.get('to_date', None)
        assign_by = self.request.query_params.get('assign_by', None)
        search = self.request.query_params.get('search', None)
        filter = {}

        self.queryset = self.queryset.filter(Q(Q(task_status=1)|Q(task_status=3)),
                                            id__in=set(ETaskReportingDates.objects.filter(reporting_date__date__gt=cur_date,task_type=1,reporting_status=2
                                            ).values_list('task',flat=True)))

        if field_name and order_by:      
            if field_name =='task_code_id' and order_by=='asc':
                sort_field='task_code_id'

            if field_name =='task_code_id' and order_by=='desc':
                sort_field='-task_code_id'

            if field_name =='task_subject' and order_by=='asc':
                sort_field='task_subject'

            if field_name =='task_subject' and order_by=='desc':
                sort_field='-task_subject'

            if field_name =='start_date' and order_by=='asc':
                sort_field='start_date'
                
            if field_name =='start_date' and order_by=='desc':
                sort_field='-start_date'
                
            if field_name =='end_date' and order_by=='asc':
                sort_field='end_date'
                
            if field_name =='end_date' and order_by=='desc':
                sort_field='-end_date'
                   
            if field_name =='assign_by' and order_by=='asc':
                sort_field='assign_by'
                
            if field_name =='assign_by' and order_by=='desc':
                sort_field='-assign_by'
                
        # return self.queryset.filter((Q(assign_to_id=user_id)|Q(assign_by_id=user_id)|Q(sub_assign_to_user_id=user_id)|Q(owner_id=user_id)),
        #                             start_date__date__gt=cur_date,
        #                             is_deleted=False,task_status=1).order_by(sort_field)

        if from_date or to_date or assign_by or search:

            if from_date and to_date:
                from_object =datetime.strptime(from_date, '%Y-%m-%d')
                to_object =datetime.strptime(to_date, '%Y-%m-%d')
                filter['end_date__date__gte']= from_object
                filter['end_date__date__lte']= to_object + timedelta(days=1)

            if assign_by:
                filter['assign_by__in'] = list(map(int,assign_by.split(" ")))
           
            if search:           
                task_code = self.queryset.filter(is_deleted=False,task_code_id__icontains=search).values_list('id',flat=True)
                print('task_code-->',task_code)
                if task_code:
                    # return all_queryset.filter(is_deleted=False,id__in=list(task_code),**filter).order_by(sort_field)
                    return self.queryset.filter((Q(assign_to_id=user_id)|Q(assign_by_id=user_id)|Q(sub_assign_to_user_id=user_id)|Q(owner_id=user_id)),
                                    start_date__date__gt=cur_date,id__in=list(task_code),
                                    is_deleted=False,**filter).order_by(sort_field)
                else:
                    id1= self.queryset.filter(Q(is_deleted=False),**filter).values_list('id',flat=True)
                    id2= self.queryset.filter(Q(is_deleted=False),**filter).values_list('parent_id',flat=True)
                    ids=list(id1)+list(id2)
                    print("ids",ids)
                    check_data = EtaskTask.objects.filter((Q(task_subject__icontains=search)),id__in=ids).values_list('id',flat=True)
                    print("check_data",check_data)
                    # return all_queryset.filter(Q(is_deleted=False),(Q(parent_id__in=list(check_data))|Q(id__in=list(check_data))),**filter).order_by(sort_field)  
                    return self.queryset.filter((Q(assign_to_id=user_id)|Q(assign_by_id=user_id)|Q(sub_assign_to_user_id=user_id)|Q(owner_id=user_id)),
                                    (Q(parent_id__in=list(check_data))|Q(id__in=list(check_data))),
                                    start_date__date__gt=cur_date,id__in=list(task_code),
                                    is_deleted=False,**filter).order_by(sort_field)
            else:
                return self.queryset.filter((Q(assign_to_id=user_id)|Q(assign_by_id=user_id)|Q(sub_assign_to_user_id=user_id)|Q(owner_id=user_id)),
                                    start_date__date__gt=cur_date,
                                    is_deleted=False,**filter).order_by(sort_field)
   
        else:
            return  self.queryset.filter((Q(assign_to_id=user_id)|Q(assign_by_id=user_id)|Q(sub_assign_to_user_id=user_id)|Q(owner_id=user_id)),
                                    start_date__date__gt=cur_date,
                                    is_deleted=False).order_by(sort_field)

    @response_modify_decorator_list_or_get_after_execution_for_pagination
    def get(self, request, *args, **kwargs):
        response=super(UpcomingTaskReportingPerUserView,self).get(self,request,args,kwargs)
        for data in response.data['results']:
            comments_count = ETaskComments.objects.filter(task=data['id'],is_deleted=False).count()
            data['comments_count'] = comments_count
        return response

#::::::::::::::::TODAYS TASK ALONG WITH TEAM:::::::::::::::::::::::::::::::::::::#
class TodaysTaskAlongWithTeamView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
                                  
    def get(self, request, *args, **kwargs):
        user=self.request.user.id
        print('user',user)
        cur_date=datetime.now().date()  
        data_dict={}                
        task_details= EtaskTask.objects.filter((Q(assign_to_id=user)|Q(assign_by_id=user)|Q(sub_assign_to_user_id=user)|Q(owner_id=user)),
                                                (Q(start_date__date__lte=cur_date)&Q(end_date__date__gte=cur_date)|Q(end_date__date__lte=cur_date)&Q(extended_date__date__gte=cur_date)),
                                                is_deleted=False,task_status=1)
         
        print('task_details',task_details,type(task_details))
        task_list=[]
        for t_d in task_details:
            report_date=ETaskReportingDates.objects.filter(task_type=1,task=t_d.id,is_deleted=False).values('id','reporting_date')
            reporting_date=report_date if report_date else []
            assign_to=t_d.assign_to.id if t_d.assign_to else None
            assign_by=t_d.assign_by.id if t_d.assign_by else None
            sub_assign_to_user=t_d.sub_assign_to_user.id if t_d.sub_assign_to_user else None
            owner=t_d.owner.id if t_d.owner else None
            task_data={
                'id':t_d.id,
                'task_code_id':t_d.task_code_id,
                'parent_id':t_d.parent_id,
                'owner':owner,
                'owner_name':userdetails(owner),
                'assign_to':assign_to,
                'assign_to_name':userdetails(assign_to),
                'assign_by':assign_by,
                'assign_by_name':userdetails(assign_by),
                'task_subject':t_d.task_subject,
                'task_description':t_d.task_description,
                'task_categories':t_d.task_categories,
                'task_categories_name':t_d.get_task_categories_display(),
                'start_date':t_d.start_date,
                'end_date':t_d.end_date,
                'completed_date':t_d.completed_date,
                'closed_date':t_d.closed_date,
                'extended_date':t_d.extended_date,
                'extend_with_delay':t_d.extend_with_delay,
                'task_priority':t_d.task_priority,
                'task_priority_name':t_d.get_task_priority_display(),
                'task_type':t_d.task_type,
                'task_type_name':t_d.get_task_type_display(),
                'task_status':t_d.task_status,
                'task_status_name':t_d.get_task_status_display(),
                'recurrance_frequency':t_d.recurrance_frequency,
                'recurrance_frequency_name':t_d.get_recurrance_frequency_display(),
                'sub_assign_to_user':sub_assign_to_user,
                'sub_assign_to_user_name':userdetails(sub_assign_to_user),
                'reporting_date':reporting_date
            }            
            if int(t_d.parent_id) != 0:
                parent_id_name = EtaskTask.objects.filter(task_status=1,is_deleted=False,id=t_d.parent_id).values('id','task_subject')
                if parent_id_name:
                    task_data['parent'] = {
                        "id" :  t_d.parent_id,
                        "name" :parent_id_name[0]['task_subject']
                    }
                else :
                    task_data['parent'] = None
            else:
                task_data['parent'] = None
            task_list.append(task_data)
        data_dict['my_todays_task']=task_list if task_list else []
        user_list=[]
        user_list_rh=(list(TCoreUserDetail.objects.filter((Q(hod_id=user)|Q(reporting_head_id=user)),cu_is_deleted=False).values_list('cu_user',flat=True).iterator()))
        print('user_list_rh',user_list_rh)
        if user_list_rh:
            for u_l_r in user_list_rh:
                user_details={
                    "id":u_l_r,
                    "name":userdetails(u_l_r)
                }
                task_array=[]
                user_task_details= EtaskTask.objects.filter((Q(assign_to_id=u_l_r)|Q(assign_by_id=u_l_r)|Q(sub_assign_to_user_id=u_l_r)|Q(owner_id=u_l_r)),
                                                (Q(start_date__date__lte=cur_date)&Q(end_date__date__gte=cur_date)|Q(end_date__date__lte=cur_date)& Q(extended_date__date__gte=cur_date)),
                                                is_deleted=False,task_status=1)
                for u_t_d in user_task_details:
                    report_date=ETaskReportingDates.objects.filter(task_type=1,task=u_t_d.id,is_deleted=False).values('id','reporting_date')
                    reporting_date=report_date if report_date else []
                    assign_to=u_t_d.assign_to.id if u_t_d.assign_to else None
                    assign_by=u_t_d.assign_by.id if u_t_d.assign_by else None
                    sub_assign_to_user=u_t_d.sub_assign_to_user.id if u_t_d.sub_assign_to_user else None
                    owner=u_t_d.owner.id if u_t_d.owner else None
                    user_task_data={
                        'id':u_t_d.id,
                        'task_code_id':u_t_d.task_code_id,
                        'parent_id':u_t_d.parent_id,
                        'owner':owner,
                        'owner_name':userdetails(owner),
                        'assign_to':assign_to,
                        'assign_to_name':userdetails(assign_to),
                        'assign_by':assign_by,
                        'assign_by_name':userdetails(assign_by),
                        'task_subject':u_t_d.task_subject,
                        'task_description':u_t_d.task_description,
                        'task_categories':u_t_d.task_categories,
                        'task_categories_name':u_t_d.get_task_categories_display(),
                        'start_date':u_t_d.start_date,
                        'end_date':u_t_d.end_date,
                        'completed_date':u_t_d.completed_date,
                        'closed_date':u_t_d.closed_date,
                        'extended_date':u_t_d.extended_date,
                        'extend_with_delay':u_t_d.extend_with_delay,
                        'task_priority':u_t_d.task_priority,
                        'task_priority_name':u_t_d.get_task_priority_display(),
                        'task_type':u_t_d.task_type,
                        'task_type_name':u_t_d.get_task_type_display(),
                        'task_status':u_t_d.task_status,
                        'task_status_name':u_t_d.get_task_status_display(),
                        'recurrance_frequency':u_t_d.recurrance_frequency,
                        'recurrance_frequency_name':u_t_d.get_recurrance_frequency_display(),
                        'sub_assign_to_user':sub_assign_to_user,
                        'sub_assign_to_user_name':userdetails(sub_assign_to_user),
                        'reporting_date':reporting_date
                    }            
                    if int(u_t_d.parent_id) != 0:
                        parent_id_name = EtaskTask.objects.filter(task_status=1,is_deleted=False,id=u_t_d.parent_id).values('id','task_subject')
                        if parent_id_name:
                            user_task_data['parent'] = {
                                "id" :  u_t_d.parent_id,
                                "name" :parent_id_name[0]['task_subject']
                            }
                        else :
                            user_task_data['parent'] = None
                    else:
                        user_task_data['parent'] = None
                    task_array.append(user_task_data)
                user_details['todays_task']=task_array if task_array else []
                user_list.append(user_details)
        data_dict['user_list_under_rh']=user_list if user_list else []
        u_dict={}
        u_dict['result']=data_dict
        if data_dict:
            u_dict['request_status']=1
            u_dict['msg']=settings.MSG_SUCCESS
        elif len(data_dict)==0:
            u_dict['request_status']=1
            u_dict['msg']=settings.MSG_NO_DATA
        else:
            u_dict['request_status']=0
            u_dict['msg']=settings.MSG_ERROR
        data_dict=u_dict
                   
        return Response(data_dict)

class TodaysTaskReportingAlongWithTeamView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
                                  
    def get(self, request, *args, **kwargs):
        user=self.request.user.id
        print('user',user)
        cur_date=datetime.now().date()  
        data_dict={}
        task_details= EtaskTask.objects.filter((Q(assign_to_id=user)|Q(assign_by_id=user)|Q(sub_assign_to_user_id=user)|Q(owner_id=user)),
                                                # (Q(start_date__date__lte=cur_date)&Q(end_date__date__gte=cur_date)|Q(end_date__date__lte=cur_date)&Q(extended_date__date__gte=cur_date)),
                                                Q(Q(task_status=1)|Q(task_status=3)),
                                                id__in=set(ETaskReportingDates.objects.filter(reporting_date__date=cur_date,task_type=1,reporting_status=2).values_list('task',flat=True)),
                                                is_deleted=False)
         
        print('task_details',task_details,type(task_details))
        task_list=[]
        for t_d in task_details:
            report_date=ETaskReportingDates.objects.filter(task_type=1,task=t_d.id,is_deleted=False).values('id','reporting_date')
            reporting_date=report_date if report_date else []
            assign_to=t_d.assign_to.id if t_d.assign_to else None
            assign_by=t_d.assign_by.id if t_d.assign_by else None
            sub_assign_to_user=t_d.sub_assign_to_user.id if t_d.sub_assign_to_user else None
            owner=t_d.owner.id if t_d.owner else None
            task_data={
                'id':t_d.id,
                'task_code_id':t_d.task_code_id,
                'parent_id':t_d.parent_id,
                'owner':owner,
                'owner_name':userdetails(owner),
                'assign_to':assign_to,
                'assign_to_name':userdetails(assign_to),
                'assign_by':assign_by,
                'assign_by_name':userdetails(assign_by),
                'task_subject':t_d.task_subject,
                'task_description':t_d.task_description,
                'task_categories':t_d.task_categories,
                'task_categories_name':t_d.get_task_categories_display(),
                'start_date':t_d.start_date,
                'end_date':t_d.end_date,
                'completed_date':t_d.completed_date,
                'closed_date':t_d.closed_date,
                'extended_date':t_d.extended_date,
                'extend_with_delay':t_d.extend_with_delay,
                'task_priority':t_d.task_priority,
                'task_priority_name':t_d.get_task_priority_display(),
                'task_type':t_d.task_type,
                'task_type_name':t_d.get_task_type_display(),
                'task_status':t_d.task_status,
                'task_status_name':t_d.get_task_status_display(),
                'recurrance_frequency':t_d.recurrance_frequency,
                'recurrance_frequency_name':t_d.get_recurrance_frequency_display(),
                'sub_assign_to_user':sub_assign_to_user,
                'sub_assign_to_user_name':userdetails(sub_assign_to_user),
                'reporting_date':reporting_date
            }            
            if int(t_d.parent_id) != 0:
                parent_id_name = EtaskTask.objects.filter(task_status=1,is_deleted=False,id=t_d.parent_id).values('id','task_subject')
                if parent_id_name:
                    task_data['parent'] = {
                        "id" :  t_d.parent_id,
                        "name" :parent_id_name[0]['task_subject']
                    }
                else :
                    task_data['parent'] = None
            else:
                task_data['parent'] = None
            task_list.append(task_data)
        data_dict['my_todays_task']=task_list if task_list else []
        user_list=[]
        user_list_rh=(list(TCoreUserDetail.objects.filter((Q(hod_id=user)|Q(reporting_head_id=user)),cu_is_deleted=False).values_list('cu_user',flat=True).iterator()))
        print('user_list_rh',user_list_rh)
        if user_list_rh:
            for u_l_r in user_list_rh:
                user_details={
                    "id":u_l_r,
                    "name":userdetails(u_l_r)
                }
                task_array=[]
                user_task_details= EtaskTask.objects.filter((Q(assign_to_id=u_l_r)|Q(assign_by_id=u_l_r)|Q(sub_assign_to_user_id=u_l_r)|Q(owner_id=u_l_r)),
                                                Q(Q(task_status=1)|Q(task_status=3)),
                                                # (Q(start_date__date__lte=cur_date)&Q(end_date__date__gte=cur_date)|Q(end_date__date__lte=cur_date)& Q(extended_date__date__gte=cur_date)),
                                                id__in=set(ETaskReportingDates.objects.filter(reporting_date__date=cur_date,task_type=1,reporting_status=2).values_list('task',flat=True)),
                                                is_deleted=False)
                for u_t_d in user_task_details:
                    report_date=ETaskReportingDates.objects.filter(task_type=1,task=u_t_d.id,is_deleted=False).values('id','reporting_date')
                    reporting_date=report_date if report_date else []
                    assign_to=u_t_d.assign_to.id if u_t_d.assign_to else None
                    assign_by=u_t_d.assign_by.id if u_t_d.assign_by else None
                    sub_assign_to_user=u_t_d.sub_assign_to_user.id if u_t_d.sub_assign_to_user else None
                    owner=u_t_d.owner.id if u_t_d.owner else None
                    user_task_data={
                        'id':u_t_d.id,
                        'task_code_id':u_t_d.task_code_id,
                        'parent_id':u_t_d.parent_id,
                        'owner':owner,
                        'owner_name':userdetails(owner),
                        'assign_to':assign_to,
                        'assign_to_name':userdetails(assign_to),
                        'assign_by':assign_by,
                        'assign_by_name':userdetails(assign_by),
                        'task_subject':u_t_d.task_subject,
                        'task_description':u_t_d.task_description,
                        'task_categories':u_t_d.task_categories,
                        'task_categories_name':u_t_d.get_task_categories_display(),
                        'start_date':u_t_d.start_date,
                        'end_date':u_t_d.end_date,
                        'completed_date':u_t_d.completed_date,
                        'closed_date':u_t_d.closed_date,
                        'extended_date':u_t_d.extended_date,
                        'extend_with_delay':u_t_d.extend_with_delay,
                        'task_priority':u_t_d.task_priority,
                        'task_priority_name':u_t_d.get_task_priority_display(),
                        'task_type':u_t_d.task_type,
                        'task_type_name':u_t_d.get_task_type_display(),
                        'task_status':u_t_d.task_status,
                        'task_status_name':u_t_d.get_task_status_display(),
                        'recurrance_frequency':u_t_d.recurrance_frequency,
                        'recurrance_frequency_name':u_t_d.get_recurrance_frequency_display(),
                        'sub_assign_to_user':sub_assign_to_user,
                        'sub_assign_to_user_name':userdetails(sub_assign_to_user),
                        'reporting_date':reporting_date
                    }            
                    if int(u_t_d.parent_id) != 0:
                        parent_id_name = EtaskTask.objects.filter(task_status=1,is_deleted=False,id=u_t_d.parent_id).values('id','task_subject')
                        if parent_id_name:
                            user_task_data['parent'] = {
                                "id" :  u_t_d.parent_id,
                                "name" :parent_id_name[0]['task_subject']
                            }
                        else :
                            user_task_data['parent'] = None
                    else:
                        user_task_data['parent'] = None
                    task_array.append(user_task_data)
                user_details['todays_task']=task_array if task_array else []
                user_list.append(user_details)
        data_dict['user_list_under_rh']=user_list if user_list else []
        u_dict={}
        u_dict['result']=data_dict
        if data_dict:
            u_dict['request_status']=1
            u_dict['msg']=settings.MSG_SUCCESS
        elif len(data_dict)==0:
            u_dict['request_status']=1
            u_dict['msg']=settings.MSG_NO_DATA
        else:
            u_dict['request_status']=0
            u_dict['msg']=settings.MSG_ERROR
        data_dict=u_dict
                   
        return Response(data_dict)

#::::::::::::::::DEFAULT REPORTING DATES:::::::::::::::::::::::::::::::::::::#
class ETaskDefaultReportingDatesView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = User.objects.filter(is_active=True,is_superuser=False)
    serializer_class = ETaskDefaultReportingDatesSerializer  
    pagination_class = CSPageNumberPagination
    def get_queryset(self):
        login_user_details=self.request.user
        #print('user',login_user_details)
        field_name = self.request.query_params.get('field_name', None)
        order_by = self.request.query_params.get('order_by', None)
        sort_field='-id'

        '''
            Reason : 
            Currently we are displaying the team list according to HOD/Reporting Head. 
            But due to the current changes request on functional doc we have to work on user hierarchy 
            functionality for (Team) checking HOD first then Checking reporting head.
            Author : Rupam Hazra
            Date : 25/02/2020
            Line Number : 6474
        '''
        is_hod = TCoreUserDetail.objects.filter(
                            hod = login_user_details,cu_is_deleted=False,cu_user__isnull=False)
        #print('is_hod',is_hod)
        if is_hod:
            department_d = TCoreUserDetail.objects.filter(
                cu_user = login_user_details,cu_is_deleted=False,cu_user__isnull=False).values_list('department',flat=True)
            #print('department_d',department_d)
            if department_d:
                hi_user_list_details = TCoreUserDetail.objects.filter(department__in=department_d).values_list('cu_user',flat=True)
                #print('hi_user_list_details',hi_user_list_details)
                if field_name and order_by:
                    if field_name == 'employee' and order_by == 'asc':
                        return self.queryset.filter(id__in=hi_user_list_details).order_by('first_name')
                        # sort_field='first_name'
                    elif field_name == 'employee' and order_by == 'desc':
                        return self.queryset.filter(id__in=hi_user_list_details).order_by('-first_name')
                else:
                    return self.queryset.filter(id__in=hi_user_list_details)
        else:
            hi_user_list_details = TCoreUserDetail.objects.filter(
                reporting_head = login_user_details,cu_is_deleted=False,cu_user__isnull=False).values_list('cu_user',flat=True)
            #print('hi_user_list_details',list(hi_user_list_details))
            hi_user_details1 = ''
            if hi_user_list_details.count() > 0 :
                for hi_user_details in hi_user_list_details:
                    hi_user_list_details = self.getLowerLevelUserList(str(hi_user_details),list(hi_user_list_details))
                #print('hi_user_details1',hi_user_list_details)
                if field_name and order_by:
                    if field_name == 'employee' and order_by == 'asc':
                        return self.queryset.filter(id__in=hi_user_list_details).order_by('first_name')
                    elif field_name == 'employee' and order_by == 'desc':
                        return self.queryset.filter(id__in=hi_user_list_details).order_by('-first_name')
                else:
                    return self.queryset.filter(id__in=hi_user_list_details)
            else:
                return self.queryset.none()
       
    def getLowerLevelUserList(self, user_id='',main_list='') -> list:
        try:
            #print('user_id',user_id)
            #print('main_list',main_list)
            hi_user_list_details =TCoreUserDetail.objects.filter(reporting_head_id = str(user_id),cu_is_deleted=False,cu_user__isnull=False).values_list(
                'cu_user_id',flat=True)
            #print('hi_user_list_details1111',hi_user_list_details)
            if hi_user_list_details.count() > 0 :
                for hi_user_details in hi_user_list_details:
                    main_list.append(hi_user_details)
                    self.getLowerLevelUserList(str(hi_user_details),main_list)
            return main_list
        except Exception as e:
            raise e

    @response_modify_decorator_list_or_get_after_execution_for_pagination
    def get(self, request, *args, **kwargs):
        response=super(ETaskDefaultReportingDatesView,self).get(self,request,args,kwargs)
        for data in response.data['results']:
            data['employee']=data['id']
            data['employee_name']=userdetails(data['id'])
            field_lable_value_list=[]
            field_data=EtaskMonthlyReportingDate.objects.filter(employee_id=data['id'],is_deleted=False)
            # print('field_data',field_data)
            for data1 in field_data:
                field_lable_value_dict={
                    'id':data1.id,
                    'field_label':data1.field_label,
                    'field_value':data1.field_value
                }
                field_lable_value_list.append(field_lable_value_dict)
            data['field_label_value']=field_lable_value_list if field_lable_value_list else []
        return response

class ETaskAnotherDefaultReportingDatesView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskMonthlyReportingDate.objects.filter(is_deleted=False)
    serializer_class = ETaskAnotherDefaultReportingDatesSerializer  

class ETaskDefaultReportingDatesUpdateView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskMonthlyReportingDate.objects.filter(is_deleted=False)
    serializer_class = ETaskDefaultReportingDatesUpdateSerializer  

class ETaskDefaultReportingDatesDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskMonthlyReportingDate.objects.filter(is_deleted=False)
    serializer_class = ETaskDefaultReportingDatesDeleteSerializer  

#:::::::::::::::::::::::::::::::::::::: TODAY LIST -NEW ::::::::::::::::::::::::::::::::::::::::::::#
class TodayTaskDetailsPerUserView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskTask.objects.filter(is_deleted=False)
    serializer_class = TodayTaskDetailsPerUserSerializer
    pagination_class = CSPageNumberPagination

    def get_queryset(self):
        login_user=self.request.user.id
        user_id=self.kwargs["user_id"]
        cur_date=datetime.now().date()
        sort_field='-id'
        field_name = self.request.query_params.get('field_name', None)
        order_by = self.request.query_params.get('order_by', None)
        from_date = self.request.query_params.get('from_date', None)
        to_date = self.request.query_params.get('to_date', None)
        assign_by = self.request.query_params.get('assign_by', None)
        search = self.request.query_params.get('search', None)
        filter = {}
        parent_task = self.request.query_params.get('parent_task', None)
        if parent_task:
            filter['parent_id'] = parent_task
        
        if field_name and order_by:      
            if field_name =='task_code_id' and order_by=='asc':
                sort_field='task_code_id'

            if field_name =='task_code_id' and order_by=='desc':
                sort_field='-task_code_id'

            if field_name =='task_subject' and order_by=='asc':
                sort_field='task_subject'

            if field_name =='task_subject' and order_by=='desc':
                sort_field='-task_subject'

            if field_name =='start_date' and order_by=='asc':
                sort_field='start_date'
                
            if field_name =='start_date' and order_by=='desc':
                sort_field='-start_date'
                
            if field_name =='end_date' and order_by=='asc':
                sort_field='end_date'
                
            if field_name =='end_date' and order_by=='desc':
                sort_field='-end_date'
                   
            if field_name =='assign_by' and order_by=='asc':
                sort_field='assign_by'
                
            if field_name =='assign_by' and order_by=='desc':
                sort_field='-assign_by'

        return self.queryset.filter((Q(assign_to_id=user_id)|Q(sub_assign_to_user_id=user_id)),
                                        (Q(Q(extended_date__isnull=False)&Q(extended_date__date=cur_date))|Q(Q(extended_date__isnull=True)&Q(end_date__date=cur_date))),
                                        is_deleted=False,task_status=1,**filter).order_by(sort_field)

    @response_modify_decorator_list_or_get_after_execution_for_pagination
    def get(self, request, *args, **kwargs):
        response=super(TodayTaskDetailsPerUserView,self).get(self,request,args,kwargs)
        login_user=self.request.user.id
        user_id=self.kwargs["user_id"]
        if response.data:
            for data in response.data['results']:
                # comments_count = ETaskComments.objects.filter(task=data['id'],is_deleted=False).count()
                unread_comments_count = ETaskCommentsViewers.objects.filter(task=data['id'],user=user_id,is_view=False,is_deleted=False).count()
                data['unread_comments_count'] = unread_comments_count
                if int(login_user)==int(user_id):
                    print("login user")
                    data['assign_by_name'] = userdetails(int(data['assign_by']))
                    if int(data['assign_to'])==int(login_user) and data['sub_assign_to_user'] is not None:
                        print("sub_assign_to_user")
                        data['sub_assign_to_user_name'] = userdetails(int(data['sub_assign_to_user']))
                    elif data['sub_assign_to_user'] is not None and int(data['sub_assign_to_user'])==int(login_user):
                        data['assign_by'] = data['assign_to']
                        data['assign_by_name'] = userdetails(int(data['assign_to']))
                        data['sub_assign_to_user_name'] = ''
                    else:
                        print("not sub_assign_to_user")
                        data['sub_assign_to_user_name'] = ''
                else:
                    print("not a login user")
                    if data['sub_assign_to_user']:
                        if int(data['assign_by'])==int(login_user):
                            data['assign_by_name'] = userdetails(int(data['assign_by']))
                            data['sub_assign_to_user_name'] = ''
                        else:
                            print("convert")
                            data['assign_by'] = data['assign_to']
                            data['assign_by_name'] = userdetails(int(data['assign_to']))
                            data['sub_assign_to_user_name'] = userdetails(int(data['sub_assign_to_user']))
                            if int(data['assign_to'])==int(login_user):
                                data['sub_assign_to_user_name'] = ""
                    else:
                        print("not convert")
                        data['assign_by_name'] = userdetails(int(data['assign_by']))
                        data['sub_assign_to_user_name'] = ''
 
        return response

class UpcomingTaskDetailsPerUserView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskTask.objects.filter(is_deleted=False)
    serializer_class = UpcomingTaskDetailsPerUserSerializer
    pagination_class = CSPageNumberPagination

    def get_queryset(self):
        login_user=self.request.user.id
        user_id=self.kwargs["user_id"]
        print('user_id',user_id)
        cur_date=datetime.now().date()
        sort_field='-id'
        field_name = self.request.query_params.get('field_name', None)
        order_by = self.request.query_params.get('order_by', None)
        from_date = self.request.query_params.get('from_date', None)
        to_date = self.request.query_params.get('to_date', None)
        assign_by = self.request.query_params.get('assign_by', None)
        search = self.request.query_params.get('search', None)
        filter = {}
        parent_task = self.request.query_params.get('parent_task', None)
        if parent_task:
            filter['parent_id'] = parent_task
        
        if field_name and order_by:      
            if field_name =='task_code_id' and order_by=='asc':
                sort_field='task_code_id'

            if field_name =='task_code_id' and order_by=='desc':
                sort_field='-task_code_id'

            if field_name =='task_subject' and order_by=='asc':
                sort_field='task_subject'

            if field_name =='task_subject' and order_by=='desc':
                sort_field='-task_subject'

            if field_name =='start_date' and order_by=='asc':
                sort_field='start_date'
                
            if field_name =='start_date' and order_by=='desc':
                sort_field='-start_date'
                
            if field_name =='end_date' and order_by=='asc':
                sort_field='end_date'
                
            if field_name =='end_date' and order_by=='desc':
                sort_field='-end_date'
                   
            if field_name =='assign_by' and order_by=='asc':
                sort_field='assign_by'
                
            if field_name =='assign_by' and order_by=='desc':
                sort_field='-assign_by'

        return  self.queryset.filter((Q(assign_to_id=user_id)|Q(sub_assign_to_user_id=user_id)),
                                    (Q(Q(extended_date__isnull=False)&Q(extended_date__date__gt=cur_date))|Q(Q(extended_date__isnull=True)&Q(end_date__date__gt=cur_date))),
                                    is_deleted=False,task_status=1,**filter).order_by(sort_field)
                
    @response_modify_decorator_list_or_get_after_execution_for_pagination
    def get(self, request, *args, **kwargs):
        login_user=self.request.user.id
        user_id=self.kwargs["user_id"]
        response=super(UpcomingTaskDetailsPerUserView,self).get(self,request,args,kwargs)
        for data in response.data['results']:
            # comments_count = ETaskComments.objects.filter(task=data['id'],is_deleted=False).count()
            # data['comments_count'] = comments_count
            unread_comments_count = ETaskCommentsViewers.objects.filter(task=data['id'],user=user_id,is_view=False,is_deleted=False).count()
            data['unread_comments_count'] = unread_comments_count
            if int(login_user)==int(user_id):
                print("login user")
                data['assign_by_name'] = userdetails(int(data['assign_by']))
                if int(data['assign_to'])==int(login_user) and data['sub_assign_to_user'] is not None:
                    print("sub_assign_to_user")
                    data['sub_assign_to_user_name'] = userdetails(int(data['sub_assign_to_user']))
                elif data['sub_assign_to_user'] is not None and int(data['sub_assign_to_user'])==int(login_user):
                    data['assign_by'] = data['assign_to']
                    data['assign_by_name'] = userdetails(int(data['assign_to']))
                    data['sub_assign_to_user_name'] = ''
                else:
                    print("not sub_assign_to_user")
                    data['sub_assign_to_user_name'] = ''
            else:
                print("not a login user")
                if data['sub_assign_to_user']:
                    if int(data['assign_by'])==int(login_user):
                        data['assign_by_name'] = userdetails(int(data['assign_by']))
                        data['sub_assign_to_user_name'] = ''
                    else:
                        print("convert")
                        data['assign_by'] = data['assign_to']
                        data['assign_by_name'] = userdetails(int(data['assign_to']))
                        data['sub_assign_to_user_name'] = userdetails(int(data['sub_assign_to_user']))
                        if int(data['assign_to'])==int(login_user):
                            data['sub_assign_to_user_name'] = ""
                else:
                    print("not convert")
                    data['assign_by_name'] = userdetails(int(data['assign_by']))
                    data['sub_assign_to_user_name'] = ''
 
        return response

class OverdueTaskDetailsPerUserView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskTask.objects.filter(is_deleted=False)
    serializer_class = OverdueTaskDetailsPerUserSerializer
    pagination_class = CSPageNumberPagination

    def get_queryset(self):
        login_user=self.request.user.id
        user_id=self.kwargs["user_id"]
        print('user_id',user_id)
        cur_date=datetime.now().date()
        sort_field='-id'
        field_name = self.request.query_params.get('field_name', None)
        order_by = self.request.query_params.get('order_by', None)
        from_date = self.request.query_params.get('from_date', None)
        to_date = self.request.query_params.get('to_date', None)
        assign_by = self.request.query_params.get('assign_by', None)
        search = self.request.query_params.get('search', None)
        parent_task = self.request.query_params.get('parent_task', None)
        filter = {}
        if parent_task:
            filter['parent_id'] = parent_task
        
        if field_name and order_by:      
            if field_name =='task_code_id' and order_by=='asc':
                sort_field='task_code_id'

            if field_name =='task_code_id' and order_by=='desc':
                sort_field='-task_code_id'

            if field_name =='task_subject' and order_by=='asc':
                sort_field='task_subject'

            if field_name =='task_subject' and order_by=='desc':
                sort_field='-task_subject'

            if field_name =='start_date' and order_by=='asc':
                sort_field='start_date'
                
            if field_name =='start_date' and order_by=='desc':
                sort_field='-start_date'
                
            if field_name =='end_date' and order_by=='asc':
                sort_field='end_date'
                
            if field_name =='end_date' and order_by=='desc':
                sort_field='-end_date'
                   
            if field_name =='assign_by' and order_by=='asc':
                sort_field='assign_by'
                
            if field_name =='assign_by' and order_by=='desc':
                sort_field='-assign_by'
                
        return self.queryset.filter((Q(assign_to_id=user_id)|Q(sub_assign_to_user_id=user_id)),
                                    ((Q(extended_date__isnull=False)&Q(extend_with_delay=False)&Q(extended_date__date__lt=cur_date))|
                                    (Q(extended_date__isnull=True)&Q(end_date__date__lt=cur_date))),
                                    is_deleted=False,task_status=1,**filter).order_by(sort_field)
        

    @response_modify_decorator_list_or_get_after_execution_for_pagination
    def get(self, request, *args, **kwargs):
        login_user=self.request.user.id
        user_id=self.kwargs["user_id"]
        response=super(OverdueTaskDetailsPerUserView,self).get(self,request,args,kwargs)
        cur_date=datetime.now().date()
        for data in response.data['results']:
            # comments_count = ETaskComments.objects.filter(task=data['id'],is_deleted=False).count()
            # data['comments_count'] = comments_count
            unread_comments_count = ETaskCommentsViewers.objects.filter(task=data['id'],user=user_id,is_view=False,is_deleted=False).count()
            data['unread_comments_count'] = unread_comments_count
            if data['extended_date']:
                if data['extended_date'] and datetime.strptime(data['extended_date'], '%Y-%m-%dT%H:%M:%S').date() <= cur_date:
                    e_date = data['extended_date'].split('T')[0]
                    extended_date = datetime.strptime(e_date, '%Y-%m-%d').date()
                    days_extended=(cur_date - extended_date).days
                    print("days_extended",days_extended,type(days_extended))
                    if days_extended==1:
                        data['overdue_by'] = str(days_extended)+" day"
                    elif days_extended >1:
                        data['overdue_by'] = str(days_extended)+" days"
                    else:
                        data['overdue_by'] = None
            else:
                if data['end_date'] and datetime.strptime(data['end_date'], '%Y-%m-%dT%H:%M:%S').date() <= cur_date:
                    en_date = data['end_date'].split('T')[0]
                    end_date = datetime.strptime(en_date, '%Y-%m-%d').date()
                    days_extended=(cur_date - end_date).days
                    print("days_extended",days_extended,type(days_extended))
                    if days_extended ==1:
                        data['overdue_by'] = str(days_extended)+" day"
                    elif days_extended >1:
                        data['overdue_by'] = str(days_extended)+" days"
                    else:
                        data['overdue_by'] = None

            #################################
            if int(login_user)==int(user_id):
                print("login user")
                data['assign_by_name'] = userdetails(int(data['assign_by']))
                if int(data['assign_to'])==int(login_user) and data['sub_assign_to_user'] is not None:
                    print("sub_assign_to_user")
                    data['sub_assign_to_user_name'] = userdetails(int(data['sub_assign_to_user']))
                elif data['sub_assign_to_user'] is not None and int(data['sub_assign_to_user'])==int(login_user):
                    data['assign_by'] = data['assign_to']
                    data['assign_by_name'] = userdetails(int(data['assign_to']))
                    data['sub_assign_to_user_name'] = ''
                else:
                    print("not sub_assign_to_user")
                    data['sub_assign_to_user_name'] = ''
            else:
                print("not a login user")
                if data['sub_assign_to_user']:
                    if int(data['assign_by'])==int(login_user):
                        data['assign_by_name'] = userdetails(int(data['assign_by']))
                        data['sub_assign_to_user_name'] = ''
                    else:
                        print("convert")
                        data['assign_by'] = data['assign_to']
                        data['assign_by_name'] = userdetails(int(data['assign_to']))
                        data['sub_assign_to_user_name'] = userdetails(int(data['sub_assign_to_user']))
                        if int(data['assign_to'])==int(login_user):
                            data['sub_assign_to_user_name'] = ""
                else:
                    print("not convert")
                    data['assign_by_name'] = userdetails(int(data['assign_by']))
                    data['sub_assign_to_user_name'] = ''
 
        return response

class ClosedTaskDetailsPerUserView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskTask.objects.filter(is_deleted=False)
    serializer_class = EtaskClosedTaskListSerializer
    pagination_class = CSPageNumberPagination

    def get_queryset(self,):
        # user = self.kwargs["user_id"]
        login_user=self.request.user.id
        user_id=self.kwargs["user_id"]
        cur_date=datetime.now().date()

        filter = {}
        sort_field='-id'
        from_date = self.request.query_params.get('from_date', None)
        to_date = self.request.query_params.get('to_date', None)
        assign_by = self.request.query_params.get('assign_by', None)
        search = self.request.query_params.get('search', None)
        field_name = self.request.query_params.get('field_name', None)
        order_by = self.request.query_params.get('order_by', None)
        parent_task = self.request.query_params.get('parent_task', None)

        if parent_task:
            filter['parent_id'] = parent_task


        if field_name and order_by:      
            if field_name =='task_code_id' and order_by=='asc':
                sort_field='task_code_id'

            if field_name =='task_code_id' and order_by=='desc':
                sort_field='-task_code_id'

            if field_name =='task_subject' and order_by=='asc':
                sort_field='task_subject'

            if field_name =='task_subject' and order_by=='desc':
                sort_field='-task_subject'

            if field_name =='start_date' and order_by=='asc':
                sort_field='start_date'
                # return self.queryset.all().order_by('duration_end')
            if field_name =='start_date' and order_by=='desc':
                sort_field='-start_date'
                # return self.queryset.all().order_by('-duration_end')

            if field_name =='end_date' and order_by=='asc':
                sort_field='end_date'
                # return self.queryset.all().order_by('duration')
            if field_name =='end_date' and order_by=='desc':
                sort_field='-end_date'
                    # return self.queryset.all().order_by('-duration')
            if field_name =='assign_by' and order_by=='asc':
                sort_field='assign_by'
                # return self.queryset.all().order_by('duration')
            if field_name =='assign_by' and order_by=='desc':
                sort_field='-assign_by'
        
        return self.queryset.filter((Q(assign_to_id=user_id)|Q(sub_assign_to_user_id=user_id)),
                                        is_deleted=False,task_status=4,**filter).order_by(sort_field)
       
    @response_modify_decorator_list_or_get_after_execution_for_pagination
    def get(self, request, *args, **kwargs):
        response = super(ClosedTaskDetailsPerUserView, self).get(self, request, args, kwargs)
        user = request.user.id

        # print('response-->',response.data)
        user_id=self.kwargs["user_id"]
        for data in response.data['results']:
            unread_comments_count = ETaskCommentsViewers.objects.filter(task=data['id'],user=user_id,is_view=False,is_deleted=False).count()
            data['unread_comments_count'] = unread_comments_count
            assign_by = User.objects.filter(id=data['assign_by'],is_active=True).values('first_name','last_name')
            if assign_by:
                assign_by_first_name = assign_by[0]['first_name'] if assign_by[0]['first_name'] else ''
                assign_by_last_name = assign_by[0]['last_name'] if assign_by[0]['last_name'] else ''
                data['assign_by'] = assign_by_first_name + ' ' +assign_by_last_name


            sub_assign_to_user = User.objects.filter(id=data['sub_assign_to_user'],is_active=True).values('first_name','last_name')
            # print('sub_assign_to_user-->',sub_assign_to_user)
            if user != data['sub_assign_to_user']:
                if sub_assign_to_user:
                    sub_assign_to_user_first_name = sub_assign_to_user[0]['first_name'] if sub_assign_to_user[0]['first_name'] else ''
                    sub_assign_to_user_last_name = sub_assign_to_user[0]['last_name'] if sub_assign_to_user[0]['last_name'] else ''
                    data['sub_assign_to_user'] = sub_assign_to_user_first_name + ' ' +sub_assign_to_user_last_name
            else:
                data['sub_assign_to_user'] = None
                data['assign_to'] = user
            
            if int(data['parent_id']) != 0:
                # parent_id_name = EtaskTask.objects.filter(id=data['id'],task_status=1,is_deleted=False,parent_id=data['parent_id']).values('task_subject')
                parent_id_name = EtaskTask.objects.filter(task_status=1,is_deleted=False,id=data['parent_id']).values('id','task_subject')
                # print('parent_id_name-->',parent_id_name[0]['id'])
                if parent_id_name:
                    data['parent'] = {
                        "id" :  data['parent_id'],
                        "name" :parent_id_name[0]['task_subject']
                    }
            else :
                data['parent'] = None


            ### Time deviation Calculation
            flag1=flag2=0

            if 'end_date' in data.keys() :
                date = data['end_date'].split('T')[0]
                end_date_object = datetime.strptime(date, '%Y-%m-%d').date()
                flag1 = 1
            else:
                flag1 = 0

            if 'end_date' in data.keys() :
                c_date = data['closed_date'].split('T')[0]
                c_date_object = datetime.strptime(c_date, '%Y-%m-%d').date()
                flag2 = 1
            else:
                flag2 = 0

            if flag1 ==1 and flag2==1:
                deviation = (c_date_object - end_date_object)

                if str(deviation) == '0:00:00':
                    print('deviation--> On Time')
                    data['deviation'] = 'On Time'
                else:
                    print('deviation--> ',str(deviation).split(',')[0])
                    data['deviation'] = str(deviation).split(',')[0]


        return response
class ETaskTodaysPlannerCountView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskTask.objects.filter(is_deleted=False)
    serializer_class = EtaskTodaysPlannerCountSerializer

    def get(self, request, *args, **kwargs):
        user=self.kwargs['user_id']
        print('user',user,type(user))
        current_date=datetime.now().date()
        print('current_date',current_date)
        current_day=current_date.day
        print('current_day',current_day)
        data = {}
        data_dict = {}
        my_task_count = EtaskTask.objects.filter((Q(assign_to=user)|Q(assign_by=user)|Q(sub_assign_to_user=user)|Q(owner=user)),
                                    end_date__date=current_date,is_deleted=False,task_status=1).count()
        data['todays_task_count']=my_task_count
        reporting_task_count = EtaskTask.objects.filter(
                                        (Q(sub_assign_to_user__isnull=True)&Q(assign_to=user)),                                       
                                            task_status=1).values_list('id',flat=True)
        count=0
        if reporting_task_count:
            for r_c in reporting_task_count:
                crossed_reporting_date=ETaskReportingDates.objects.filter(task_type=1,
                                                                        task=r_c,
                                                                        reporting_date__date=current_date,
                                                                        reporting_status=2,
                                                                        is_deleted=False).count()
                print('crossed_reporting_date',crossed_reporting_date) 
                if crossed_reporting_date > 0:
                    count+=1
            print('count',count)

        default_reporting_date_count=EtaskMonthlyReportingDate.objects.filter(employee=user,field_value=current_day,is_deleted=False).count()

        data['reporting_count'] = count + default_reporting_date_count

        follow_up=EtaskFollowUP.objects.filter(assign_to=user,is_deleted=False,follow_up_date__date=current_date).count()
        data['follow_up_count']=follow_up

        invite = EtaskInviteEmployee.objects.filter(user=user).values('appointment')
        # print('invite',invite)
        ids = [x['appointment'] for x in invite]
        upcoming_appointment_count = EtaskAppointment.objects.filter((Q(created_by=user)| Q(id__in=ids)),Appointment_status='ongoing').count()
        data['todays_appointment_count'] = upcoming_appointment_count 

        data_dict['result'] = data
        if data:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_SUCCESS
        elif len(data) == 0:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_NO_DATA
        else:
            data_dict['request_status'] = 0
            data_dict['msg'] = settings.MSG_ERROR
        data = data_dict

        return Response(data)

#:::::::::::::::::::::::::::::::::::::: REPORTING ::::::::::::::::::::::::::::::::::::::::::::::::#   
class TodayReportingDetailsPerUserView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskTask.objects.filter(is_deleted=False)
    serializer_class = TodayReportingDetailsPerUserSerializer
    # pagination_class = CSPageNumberPagination

    def get_queryset(self):
        login_user=self.request.user.id
        login_user_details = self.request.user
        user = int(self.kwargs["user_id"])
        cur_date = datetime.now().date()        
        is_team=self.request.query_params.get('is_team',None)
        print('is_team',is_team)
        users_list=[login_user]
        is_hod = TCoreUserDetail.objects.filter(
                            hod = login_user_details,cu_is_deleted=False,cu_user__isnull=False)
        #print('is_hod',is_hod)
        hi_user_list_details = ''
        if is_hod:
            department_d = TCoreUserDetail.objects.filter(
                cu_user = login_user_details,cu_is_deleted=False,cu_user__isnull=False).values_list('department',flat=True)
            #print('department_d',department_d)
            if department_d:
                hi_user_list_details = TCoreUserDetail.objects.filter(department__in=department_d).values_list('cu_user',flat=True)
                #print('hi_user_list_details',hi_user_list_details)
                
        else:
            hi_user_list_details = TCoreUserDetail.objects.filter(
                reporting_head = login_user_details,cu_is_deleted=False,cu_user__isnull=False).values_list('cu_user',flat=True)
            #print('hi_user_list_details',list(hi_user_list_details))
            hi_user_details1 = ''
            if hi_user_list_details.count() > 0 :
                for hi_user_details in hi_user_list_details:
                    hi_user_list_details = self.getLowerLevelUserList(str(hi_user_details),list(hi_user_list_details))
                
        print('hi_user_list_details',hi_user_list_details)
        if hi_user_list_details:
            users_list+=hi_user_list_details
            print("users_list",users_list)
        if is_team == 'True':
            return self.queryset.filter(((Q(sub_assign_to_user__isnull=True)&Q(assign_to__in=users_list))|
                                        (Q(sub_assign_to_user__isnull=False)&Q(sub_assign_to_user__in=users_list))),
                                        owner=login_user,
                                        id__in=list(ETaskReportingDates.objects.filter(task_type=1,reporting_status=2,
                                        reporting_date__date=cur_date).values_list('task',flat=True)),
                                        task_status=1,is_deleted=False)          
        elif login_user==user:
            return self.queryset.filter(((Q(sub_assign_to_user__isnull=True)&Q(assign_to=user))|
                                        (Q(sub_assign_to_user__isnull=False)&Q(sub_assign_to_user=user))),
                                        id__in=list(ETaskReportingDates.objects.filter(task_type=1,reporting_status=2,
                                        reporting_date__date=cur_date).values_list('task',flat=True)),
                                        task_status=1,is_deleted=False)
        else:
            return self.queryset.filter(((Q(sub_assign_to_user__isnull=True)&Q(assign_to=user))|
                                        (Q(sub_assign_to_user__isnull=False)&Q(sub_assign_to_user=user))),
                                        owner=login_user,
                                        id__in=list(ETaskReportingDates.objects.filter(task_type=1,reporting_status=2,
                                        reporting_date__date=cur_date).values_list('task',flat=True)),
                                        task_status=1,is_deleted=False)
        
                                
    @response_modify_decorator_get_after_execution
    def get(self, request, *args, **kwargs):
        login_user = self.request.user.id
        user = int(self.kwargs["user_id"])

        response = super(TodayReportingDetailsPerUserView, self).get(self, request, args, kwargs)
        print("response",response.data)
        for data in response.data:
            report_date=ETaskReportingDates.objects.filter(task_type=1,task=data['id'],is_deleted=False
                                                                ).values('id','reporting_date')
            print('report_date',report_date)
            if report_date:
                data['reporting_date']=report_date[0]['reporting_date']
                data['reporting_date_id']=report_date[0]['id']
            if login_user == user:
                name = userdetails(int(data['owner']))
                data["name"] = name
            else:
                name = userdetails(int(user))
                data["name"] = name
        return response
    def getLowerLevelUserList(self, user_id='',main_list='') -> list:
        try:
            #print('user_id',user_id)
            #print('main_list',main_list)
            hi_user_list_details =TCoreUserDetail.objects.filter(reporting_head_id = str(user_id),cu_is_deleted=False,cu_user__isnull=False).values_list(
                'cu_user_id',flat=True)
            #print('hi_user_list_details1111',hi_user_list_details)
            if hi_user_list_details.count() > 0 :
                for hi_user_details in hi_user_list_details:
                    main_list.append(hi_user_details)
                    self.getLowerLevelUserList(str(hi_user_details),main_list)
            return main_list
        except Exception as e:
            raise e

class UpcomingReportingDetailsPerUserView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskTask.objects.filter(is_deleted=False)
    serializer_class = UpcomingReportingDetailsPerUserSerializer
    # pagination_class = CSPageNumberPagination

    def get_queryset(self):
        login_user=self.request.user.id
        login_user_details = self.request.user
        user = int(self.kwargs["user_id"])
        cur_date = datetime.now().date()
        is_team=self.request.query_params.get('is_team',None)
        print('is_team',is_team)
        users_list=[login_user]
        is_hod = TCoreUserDetail.objects.filter(
                            hod = login_user_details,cu_is_deleted=False,cu_user__isnull=False)
        #print('is_hod',is_hod)
        hi_user_list_details = ''
        if is_hod:
            department_d = TCoreUserDetail.objects.filter(
                cu_user = login_user_details,cu_is_deleted=False,cu_user__isnull=False).values_list('department',flat=True)
            #print('department_d',department_d)
            if department_d:
                hi_user_list_details = TCoreUserDetail.objects.filter(department__in=department_d).values_list('cu_user',flat=True)
                #print('hi_user_list_details',hi_user_list_details)
                
        else:
            hi_user_list_details = TCoreUserDetail.objects.filter(
                reporting_head = login_user_details,cu_is_deleted=False,cu_user__isnull=False).values_list('cu_user',flat=True)
            #print('hi_user_list_details',list(hi_user_list_details))
            hi_user_details1 = ''
            if hi_user_list_details.count() > 0 :
                for hi_user_details in hi_user_list_details:
                    hi_user_list_details = self.getLowerLevelUserList(str(hi_user_details),list(hi_user_list_details))
                
        print('hi_user_list_details',hi_user_list_details)
        if hi_user_list_details:
            users_list+=hi_user_list_details
            print("users_list",users_list)
        if is_team == 'True':
            return self.queryset.filter(((Q(sub_assign_to_user__isnull=True)&Q(assign_to__in=users_list))|
                                        (Q(sub_assign_to_user__isnull=False)&Q(sub_assign_to_user__in=users_list))),
                                        owner=login_user,
                                        id__in=list(ETaskReportingDates.objects.filter(task_type=1,reporting_status=2,
                                        reporting_date__date__gt=cur_date).values_list('task',flat=True)),
                                        task_status=1,is_deleted=False)         

        elif login_user==user:
            return self.queryset.filter(((Q(sub_assign_to_user__isnull=True)&Q(assign_to=user))|
                                        (Q(sub_assign_to_user__isnull=False)&Q(sub_assign_to_user=user))),
                                        id__in=list(ETaskReportingDates.objects.filter(task_type=1,reporting_status=2,
                                        reporting_date__date__gt=cur_date).values_list('task',flat=True)),
                                        task_status=1,is_deleted=False)
        else:
            return self.queryset.filter(((Q(sub_assign_to_user__isnull=True)&Q(assign_to=user))|
                                        (Q(sub_assign_to_user__isnull=False)&Q(sub_assign_to_user=user))),
                                        owner=login_user,
                                        id__in=list(ETaskReportingDates.objects.filter(task_type=1,reporting_status=2,
                                        reporting_date__date__gt=cur_date).values_list('task',flat=True)),
                                        task_status=1,is_deleted=False)
                          
    @response_modify_decorator_get_after_execution
    def get(self, request, *args, **kwargs):
        login_user = self.request.user.id
        user = int(self.kwargs["user_id"])

        response = super(UpcomingReportingDetailsPerUserView, self).get(self, request, args, kwargs)
        for data in response.data:
            if login_user == user:
                name = userdetails(int(data['owner']))
                data["name"] = name
            else:
                name = userdetails(int(user))
                data["name"] = name
        return response
    def getLowerLevelUserList(self, user_id='',main_list='') -> list:
        try:
            #print('user_id',user_id)
            #print('main_list',main_list)
            hi_user_list_details =TCoreUserDetail.objects.filter(reporting_head_id = str(user_id),cu_is_deleted=False,cu_user__isnull=False).values_list(
                'cu_user_id',flat=True)
            #print('hi_user_list_details1111',hi_user_list_details)
            if hi_user_list_details.count() > 0 :
                for hi_user_details in hi_user_list_details:
                    main_list.append(hi_user_details)
                    self.getLowerLevelUserList(str(hi_user_details),main_list)
            return main_list
        except Exception as e:
            raise e
class OverdueReportingDetailsPerUserView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskTask.objects.filter(is_deleted=False)
    serializer_class = OverdueReportingDetailsPerUserSerializer
    # pagination_class = CSPageNumberPagination

    def get_queryset(self):
        login_user=self.request.user.id
        user = int(self.kwargs["user_id"])
        cur_date = datetime.now().date()        
        login_user_details = self.request.user
        is_team=self.request.query_params.get('is_team',None)
        print('is_team',is_team)
        users_list=[login_user]
        is_hod = TCoreUserDetail.objects.filter(
                            hod = login_user_details,cu_is_deleted=False,cu_user__isnull=False)
        #print('is_hod',is_hod)
        hi_user_list_details = ''
        if is_hod:
            department_d = TCoreUserDetail.objects.filter(
                cu_user = login_user_details,cu_is_deleted=False,cu_user__isnull=False).values_list('department',flat=True)
            #print('department_d',department_d)
            if department_d:
                hi_user_list_details = TCoreUserDetail.objects.filter(department__in=department_d).values_list('cu_user',flat=True)
                #print('hi_user_list_details',hi_user_list_details)
                
        else:
            hi_user_list_details = TCoreUserDetail.objects.filter(
                reporting_head = login_user_details,cu_is_deleted=False,cu_user__isnull=False).values_list('cu_user',flat=True)
            #print('hi_user_list_details',list(hi_user_list_details))
            hi_user_details1 = ''
            if hi_user_list_details.count() > 0 :
                for hi_user_details in hi_user_list_details:
                    hi_user_list_details = self.getLowerLevelUserList(str(hi_user_details),list(hi_user_list_details))
                
        print('hi_user_list_details',hi_user_list_details)
        if hi_user_list_details:
            users_list+=hi_user_list_details
            print("users_list",users_list)
        if is_team == 'True':
            return self.queryset.filter(((Q(sub_assign_to_user__isnull=True)&Q(assign_to__in=users_list))|
                                        (Q(sub_assign_to_user__isnull=False)&Q(sub_assign_to_user__in=users_list))),
                                        owner=login_user,
                                        id__in=list(ETaskReportingDates.objects.filter(task_type=1,reporting_status=2,
                                        reporting_date__date__lt=cur_date).values_list('task',flat=True)),
                                        task_status=1,is_deleted=False)         

        elif login_user==user:
            return self.queryset.filter(((Q(sub_assign_to_user__isnull=True)&Q(assign_to=user))|
                                        (Q(sub_assign_to_user__isnull=False)&Q(sub_assign_to_user=user))),
                                        id__in=list(ETaskReportingDates.objects.filter(task_type=1,reporting_status=2,
                                        reporting_date__date__lt=cur_date).values_list('task',flat=True)),
                                        task_status=1,is_deleted=False)
        else:
            return self.queryset.filter(((Q(sub_assign_to_user__isnull=True)&Q(assign_to=user))|
                                        (Q(sub_assign_to_user__isnull=False)&Q(sub_assign_to_user=user))),
                                        owner=login_user,
                                        id__in=list(ETaskReportingDates.objects.filter(task_type=1,reporting_status=2,
                                        reporting_date__date__lt=cur_date).values_list('task',flat=True)),
                                        task_status=1,is_deleted=False)

                                       
    # @response_modify_decorator_list_or_get_after_execution_for_pagination
    @response_modify_decorator_get_after_execution
    def get(self, request, *args, **kwargs):
        login_user = self.request.user.id
        user = int(self.kwargs["user_id"])

        response = super(OverdueReportingDetailsPerUserView, self).get(self, request, args, kwargs)
        for data in response.data:
            if login_user == user:
                name = userdetails(int(data['owner']))
                data["name"] = name
            else:
                name = userdetails(int(user))
                data["name"] = name
        return response
    def getLowerLevelUserList(self, user_id='',main_list='') -> list:
        try:
            #print('user_id',user_id)
            #print('main_list',main_list)
            hi_user_list_details =TCoreUserDetail.objects.filter(reporting_head_id = str(user_id),cu_is_deleted=False,cu_user__isnull=False).values_list(
                'cu_user_id',flat=True)
            #print('hi_user_list_details1111',hi_user_list_details)
            if hi_user_list_details.count() > 0 :
                for hi_user_details in hi_user_list_details:
                    main_list.append(hi_user_details)
                    self.getLowerLevelUserList(str(hi_user_details),main_list)
            return main_list
        except Exception as e:
            raise e

class TodayReportingMarkDateReportedView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = ETaskReportingDates.objects.filter(is_deleted=False)
    serializer_class = TodayReportingMarkDateReportedSerializer

    @response_modify_decorator_update
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)


#:::::::::::::::::::::::::::::::::::::: APPOINMENT ::::::::::::::::::::::::::::::::::::::::::::::::#
class TodayAppointmenDetailsPerUserView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    # queryset = EtaskInviteEmployee.objects.filter(is_deleted=False)
    queryset = EtaskAppointment.objects.filter(is_deleted=False)
    serializer_class = TodayAppointmenDetailsPerUserSerializer
    # pagination_class = CSPageNumberPagination

    def get_queryset(self):
        login_user = self.request.user.id
        print('user',login_user)
        cur_date = datetime.now().date()
        user = int(self.kwargs["user_id"])
        if login_user == user:
            return self.queryset.filter(Q(Appointment_status='ongoing'),
                                        (Q(Q(start_date__date__lte=cur_date)&Q(end_date__date__gte=cur_date))),
                                        (Q(id__in=list(EtaskInviteEmployee.objects.filter(user_id=login_user,is_deleted=False).values_list('appointment',flat=True)))|
                                        Q(created_by=login_user)),
                                        # Appointment_status='ongoing'
                                        ).order_by('-id')
            
        else:
            return self.queryset.filter(Q(Appointment_status='ongoing'),
                                        (Q(Q(start_date__date__lte=cur_date)&Q(end_date__date__gte=cur_date))),
                                        (Q(Q(id__in=list(EtaskInviteEmployee.objects.filter(user_id=login_user,is_deleted=False).values_list('appointment',flat=True)))&
                                        Q(created_by=user))|
                                        Q(Q(id__in=list(EtaskInviteEmployee.objects.filter(user_id=user,is_deleted=False).values_list('appointment',flat=True)))&
                                        Q(created_by=login_user))),
                                        # Appointment_status='ongoing'
                                        ).order_by('-id')
            
    @response_modify_decorator_get_after_execution
    def get(self,request,*args,**kwargs):
        response=super(TodayAppointmenDetailsPerUserView,self).get(self,request,args,kwargs)
        # print('response',response.data)
        for data in response.data:
            data['appointment_subject'] = data['appointment_subject']
            data['created_by'] = data['created_by']
            data['created_by_name'] = userdetails(data['created_by'])
            data['location'] = data['location']
            data['start_date'] = data['start_date']
            data['end_date'] = data['end_date']
            data['start_time'] = data['start_time']
            data['end_time'] = data['end_time']
            internal_invite = EtaskInviteEmployee.objects.filter(appointment_id=data['id'],is_deleted=False).values('user')
            external_invites = EtaskInviteExternalPeople.objects.filter(appointment_id=data['id'],is_deleted=False).values('external_people','external_email')
            data['internal_invite']=[{'user_id':user_d['user'],'user_name':userdetails(user_d['user'])} for user_d in internal_invite]
            data['external_invites']=external_invites
                   
        return response

class UpcomingAppointmenDetailsPerUserView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    # queryset = EtaskInviteEmployee.objects.filter(is_deleted=False)
    queryset = EtaskAppointment.objects.filter(is_deleted=False)
    serializer_class = TodayAppointmenDetailsPerUserSerializer
    # pagination_class = CSPageNumberPagination

    def get_queryset(self):
        login_user = self.request.user.id
        cur_date = datetime.now().date()
        user = int(self.kwargs["user_id"])

        if login_user == user:
            return self.queryset.filter((Q(id__in=list(EtaskInviteEmployee.objects.filter(user_id=login_user,is_deleted=False).values_list('appointment',flat=True)))|
                                        Q(created_by=login_user)),
                                        start_date__date__gt=cur_date,
                                        Appointment_status='ongoing').order_by('start_date')
            
        else:
            return self.queryset.filter((Q(Q(id__in=list(EtaskInviteEmployee.objects.filter(user_id=login_user,is_deleted=False).values_list('appointment',flat=True)))&
                                        Q(created_by=user))|
                                        Q(Q(id__in=list(EtaskInviteEmployee.objects.filter(user_id=user,is_deleted=False).values_list('appointment',flat=True)))&
                                        Q(created_by=login_user))),
                                        start_date__date__gt=cur_date,
                                        Appointment_status='ongoing').order_by('start_date')

    @response_modify_decorator_get_after_execution
    def get(self,request,*args,**kwargs):
        response=super(UpcomingAppointmenDetailsPerUserView,self).get(self,request,args,kwargs)
        for data in response.data:
            data['appointment_subject'] = data['appointment_subject']
            data['created_by'] = data['created_by']
            data['created_by_name'] = userdetails(data['created_by'])
            data['location'] = data['location']
            data['start_date'] = data['start_date']
            data['end_date'] = data['end_date']
            data['start_time'] = data['start_time']
            data['end_time'] = data['end_time']
            print("data",data)
            internal_invite = EtaskInviteEmployee.objects.filter(appointment_id=data['id'],is_deleted=False).values('user')
            external_invites = EtaskInviteExternalPeople.objects.filter(appointment_id=data['id'],is_deleted=False).values('external_people','external_email')
            data['internal_invite']=[{'user_id':user_d['user'],'user_name':userdetails(user_d['user'])} for user_d in internal_invite]
            data['external_invites']=external_invites
          
        return response

class OverdueAppointmenDetailsPerUserView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskAppointment.objects.filter(is_deleted=False)
    serializer_class = TodayAppointmenDetailsPerUserSerializer
    # pagination_class = CSPageNumberPagination

    def get_queryset(self):
        login_user = self.request.user.id
        cur_date = datetime.now().date()
        user = int(self.kwargs["user_id"])

        if login_user == user:
            return self.queryset.filter((Q(id__in=list(EtaskInviteEmployee.objects.filter(user_id=login_user,is_deleted=False).values_list('appointment',flat=True)))|
                                        Q(created_by=login_user)),
                                        end_date__date__lt=cur_date,
                                        Appointment_status='ongoing').order_by('-id')
            
        else:
            return self.queryset.filter((Q(Q(id__in=list(EtaskInviteEmployee.objects.filter(user_id=login_user,is_deleted=False).values_list('appointment',flat=True)))&
                                        Q(created_by=user))|
                                        Q(Q(id__in=list(EtaskInviteEmployee.objects.filter(user_id=user,is_deleted=False).values_list('appointment',flat=True)))&
                                        Q(created_by=login_user))),
                                        end_date__date__lt=cur_date,
                                        Appointment_status='ongoing').order_by('-id')

    @response_modify_decorator_get_after_execution
    def get(self,request,*args,**kwargs):
        response=super(OverdueAppointmenDetailsPerUserView,self).get(self,request,args,kwargs)
        for data in response.data:
            data['appointment_subject'] = data['appointment_subject']
            data['created_by'] = data['created_by']
            data['created_by_name'] = userdetails(data['created_by'])
            data['location'] = data['location']
            data['start_date'] = data['start_date']
            data['end_date'] = data['end_date']
            data['start_time'] = data['start_time']
            data['end_time'] = data['end_time']
            # print("data",data)
            internal_invite = EtaskInviteEmployee.objects.filter(appointment_id=data['id'],is_deleted=False).values('user')
            external_invites = EtaskInviteExternalPeople.objects.filter(appointment_id=data['id'],is_deleted=False).values('external_people','external_email')
            data['internal_invite']=[{'user_id':user_d['user'],'user_name':userdetails(user_d['user'])} for user_d in internal_invite]
            data['external_invites']=external_invites
           
        return response

class ClosedAppointmenDetailsPerUserView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskAppointment.objects.filter(is_deleted=False)
    serializer_class = TodayAppointmenDetailsPerUserSerializer
    # pagination_class = CSPageNumberPagination

    def get_queryset(self):
        login_user = self.request.user.id
        cur_date = datetime.now().date()
        user = int(self.kwargs["user_id"])

        if login_user == user:
            return self.queryset.filter((Q(id__in=list(EtaskInviteEmployee.objects.filter(user_id=login_user,is_deleted=False).values_list('appointment',flat=True)))|
                                        Q(created_by=login_user)),
                                        # end_date__date__lt=cur_date,
                                        Appointment_status='completed').order_by('-id')
            
        else:
            return self.queryset.filter((Q(Q(id__in=list(EtaskInviteEmployee.objects.filter(user_id=login_user,is_deleted=False).values_list('appointment',flat=True)))&
                                        Q(created_by=user))|
                                        Q(Q(id__in=list(EtaskInviteEmployee.objects.filter(user_id=user,is_deleted=False).values_list('appointment',flat=True)))&
                                        Q(created_by=login_user))),
                                        # end_date__date__lt=cur_date,
                                        Appointment_status='completed').order_by('-id')

    @response_modify_decorator_get_after_execution
    def get(self,request,*args,**kwargs):
        response=super(ClosedAppointmenDetailsPerUserView,self).get(self,request,args,kwargs)
        for data in response.data:
            data['appointment_subject'] = data['appointment_subject']
            data['created_by'] = data['created_by']
            data['created_by_name'] = userdetails(data['created_by'])
            data['location'] = data['location']
            data['start_date'] = data['start_date']
            data['end_date'] = data['end_date']
            data['start_time'] = data['start_time']
            data['end_time'] = data['end_time']
            print("data",data)
            internal_invite = EtaskInviteEmployee.objects.filter(appointment_id=data['id'],is_deleted=False).values('user')
            external_invites = EtaskInviteExternalPeople.objects.filter(appointment_id=data['id'],is_deleted=False).values('external_people','external_email')
            data['internal_invite']=[{'user_id':user_d['user'],'user_name':userdetails(user_d['user'])} for user_d in internal_invite]
            data['external_invites']=external_invites
           
        return response

class TodayAppoinmentMarkCompletedView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskAppointment.objects.filter(is_deleted=False)
    serializer_class = TodayAppoinmentMarkCompletedSerializer

    @response_modify_decorator_update
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
#:::::::::::::::::::::::::::::::::::::: TASK TRANSFER ::::::::::::::::::::::::::::::::::::::::::::::::#
class ETaskMassTaskTransferView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskTask.objects.filter(is_deleted=False)
    serializer_class = ETaskMassTaskTransferSerializer
    
    @response_modify_decorator_post
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
class ETaskTeamTransferTasksListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskTask.objects.filter(is_deleted=False)
    serializer_class = ETaskTeamTransferTasksListSerializer
    pagination_class = CSPageNumberPagination

    def get_queryset(self):
        user = self.kwargs['user_id']
        print('user',user)
        filter = {}
        sort_field='-id'
        from_date = self.request.query_params.get('from_date', None)
        to_date = self.request.query_params.get('to_date', None)
        search = self.request.query_params.get('search', None)
        field_name = self.request.query_params.get('field_name', None)
        order_by = self.request.query_params.get('order_by', None)
        parent_task = self.request.query_params.get('parent_task', None)
        status = self.request.query_params.get('status', None)

        if field_name and order_by:      
        
            if field_name =='task_subject' and order_by=='asc':
                sort_field='task_subject'
            if field_name =='task_subject' and order_by=='desc':
                sort_field='-task_subject'

            if field_name =='start_date' and order_by=='asc':
                sort_field='start_date'                
            if field_name =='start_date' and order_by=='desc':
                sort_field='-start_date'
                
            if field_name =='end_date' and order_by=='asc':
                sort_field='end_date'               
            if field_name =='end_date' and order_by=='desc':
                sort_field='-end_date'

        if parent_task:
            filter['parent_id'] = parent_task

        if status:
            filter['task_status'] = status
                   
        if from_date or to_date or search:

            if from_date and to_date:
                from_object =datetime.strptime(from_date, '%Y-%m-%d')
                to_object =datetime.strptime(to_date, '%Y-%m-%d')
                filter['end_date__date__gte']= from_object
                filter['end_date__date__lte']= to_object + timedelta(days=1)
   
            if search:
                search_data = search
                print('search_data-->',search_data)

                id1= self.queryset.filter(assign_to=user,is_deleted=False,**filter).values_list('id',flat=True)                                        
                id2= self.queryset.filter(assign_to=user,is_deleted=False,**filter).values_list('parent_id',flat=True)
                                         
                ids=list(id1)+list(id2)
                print("ids",ids)

                check_data = EtaskTask.objects.filter((Q(task_code_id__icontains=search_data)|Q(task_subject__icontains=search_data)),id__in=ids).values_list('id',flat=True)
                print("check_data",check_data)
                return self.queryset.filter((Q(parent_id__in=list(check_data))|Q(id__in=list(check_data))),assign_to=user,is_deleted=False,**filter).order_by(sort_field)
                                            
            else:
                return self.queryset.filter(assign_to=user,is_deleted=False,**filter).order_by(sort_field)                                             
                # return queryset                     
        else:
            return self.queryset.filter(assign_to=user,is_deleted=False,**filter).order_by(sort_field)

    @response_modify_decorator_list_or_get_after_execution_for_pagination
    def get(self, request, *args, **kwargs):      
        response = super(ETaskTeamTransferTasksListView, self).get(self, request, args, kwargs)
        for data in response.data['results']:
            current_date= datetime.now().date()
            if data['extended_date'] and datetime.strptime(data['extended_date'],"%Y-%m-%dT%H:%M:%S").date() <= current_date:
                e_date = data['extended_date'].split('T')[0]
                extended_date = datetime.strptime(e_date, '%Y-%m-%d').date()
                days_extended=(current_date - extended_date).days
                print("days_extended",days_extended)
                if days_extended >0:
                    data['task_status']="overdue"
                    data['task_overdue_days'] = days_extended
                else:
                    data['task_status']=data['task_status_name']
                    data['task_overdue_days'] = None
            elif data['end_date'] and datetime.strptime(data['end_date'],"%Y-%m-%dT%H:%M:%S").date() <= current_date:
                en_date = data['end_date'].split('T')[0]
                end_date = datetime.strptime(en_date, '%Y-%m-%d').date()
                days_extended=(current_date - end_date).days
                print("days_extended",days_extended)
                if days_extended >0:
                    data['task_status']="overdue"
                    data['task_overdue_days'] = days_extended
                else:
                    data['task_status']=data['task_status_name']
                    data['task_overdue_days'] = None
            else:
                data['task_status']=data['task_status_name']
                # data['task_overdue_days'] = None
            
        return response
class ETaskTeamTasksTransferredListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = EtaskTask.objects.filter(is_deleted=False,is_transferred=True)
    serializer_class = ETaskTeamTransferTasksListSerializer
    pagination_class = CSPageNumberPagination

    def get_queryset(self):
        user = self.request.user.id
        print('user',user)
        users_list=(list(TCoreUserDetail.objects.filter((Q(reporting_head_id=user)|Q(hod_id=user)),cu_is_deleted=False).values_list('cu_user',flat=True)))
        print('users_list',users_list)
        filter = {}
        sort_field='-id'
        from_date = self.request.query_params.get('from_date', None)
        to_date = self.request.query_params.get('to_date', None)
        search = self.request.query_params.get('search', None)
        field_name = self.request.query_params.get('field_name', None)
        order_by = self.request.query_params.get('order_by', None)
        parent_task = self.request.query_params.get('parent_task', None)
        transfer_from = self.request.query_params.get('transfer_from', None)
        transferred_to = self.request.query_params.get('transferred_to', None)
        status = self.request.query_params.get('status', None)
        
        if parent_task:
            filter['parent_id'] = parent_task

        if transfer_from:
            filter['transferred_from'] = transfer_from
        
        if transferred_to:
            filter['assign_to'] = transferred_to
            filter['is_transferred'] = True

        if status:
            filter['task_status'] = status
        
        if field_name and order_by:      
        
            if field_name =='task_subject' and order_by=='asc':
                sort_field='task_subject'
            if field_name =='task_subject' and order_by=='desc':
                sort_field='-task_subject'

            if field_name =='start_date' and order_by=='asc':
                sort_field='start_date'                
            if field_name =='start_date' and order_by=='desc':
                sort_field='-start_date'
                
            if field_name =='end_date' and order_by=='asc':
                sort_field='end_date'               
            if field_name =='end_date' and order_by=='desc':
                sort_field='-end_date'
            
            if field_name =='date_of_transfer' and order_by=='asc':
                sort_field='date_of_transfer'               
            if field_name =='date_of_transfer' and order_by=='desc':
                sort_field='-date_of_transfer'
            
        if users_list:           
            if from_date or to_date or search:

                if from_date and to_date:
                    from_object =datetime.strptime(from_date, '%Y-%m-%d')
                    to_object =datetime.strptime(to_date, '%Y-%m-%d')
                    filter['end_date__date__gte']= from_object
                    filter['end_date__date__lte']= to_object + timedelta(days=1)
    
                if search:
                    search_data = search
                    print('search_data-->',search_data)

                    id1= self.queryset.filter(assign_to__in=users_list,is_deleted=False,**filter).values_list('id',flat=True)                                        
                    id2= self.queryset.filter(assign_to__in=users_list,is_deleted=False,**filter).values_list('parent_id',flat=True)
                                            
                    ids=list(id1)+list(id2)
                    print("ids",ids)

                    check_data = EtaskTask.objects.filter((Q(task_code_id__icontains=search_data)|Q(task_subject__icontains=search_data)),id__in=ids).values_list('id',flat=True)
                    print("check_data",check_data)
                    return self.queryset.filter((Q(parent_id__in=list(check_data))|Q(id__in=list(check_data))),assign_to__in=users_list,is_deleted=False,**filter).order_by(sort_field)
                                                
                else:
                    return self.queryset.filter(assign_to__in=users_list,is_deleted=False,**filter).order_by(sort_field)                                             
                    # return queryset                     
            else:
                return self.queryset.filter(assign_to__in=users_list,is_deleted=False,**filter).order_by(sort_field)
        else:
            return []        

    @response_modify_decorator_list_or_get_after_execution_for_pagination
    def get(self, request, *args, **kwargs):      
        response = super(ETaskTeamTasksTransferredListView, self).get(self, request, args, kwargs)
        user = self.request.user.id
        print('user',user)
        users_list=(list(TCoreUserDetail.objects.filter((Q(reporting_head_id=user)|Q(hod_id=user)),cu_is_deleted=False).values_list('cu_user',flat=True)))
        print('users_list',users_list)
        for data in response.data['results']:
            total_comments_count = ETaskCommentsViewers.objects.filter(task=data['id'],user__in=users_list,is_deleted=False).count()
            data['total_comments_count'] = total_comments_count
            current_date= datetime.now().date()
            data['transferred_from_name']=userdetails(data['transferred_from'])

            if data['extended_date'] and datetime.strptime(data['extended_date'],"%Y-%m-%dT%H:%M:%S").date() <= current_date:
                e_date = data['extended_date'].split('T')[0]
                extended_date = datetime.strptime(e_date, '%Y-%m-%d').date()
                days_extended=(current_date - extended_date).days
                print("days_extended",days_extended)
                if days_extended >0:
                    data['task_status']="overdue"
                    data['task_overdue_days'] = days_extended
                else:
                    data['task_status']=data['task_status_name']
                    data['task_overdue_days'] = None
            elif data['end_date'] and datetime.strptime(data['end_date'],"%Y-%m-%dT%H:%M:%S").date() <= current_date:
                en_date = data['end_date'].split('T')[0]
                end_date = datetime.strptime(en_date, '%Y-%m-%d').date()
                days_extended=(current_date - end_date).days
                print("days_extended",days_extended)
                if days_extended >0:
                    data['task_status']="overdue"
                    data['task_overdue_days'] = days_extended
                else:
                    data['task_status']=data['task_status_name']
                    data['task_overdue_days'] = None
            else:
                data['task_status']=data['task_status_name']
                # data['task_overdue_days'] = None
            
        return response


#::::::::::::::::::::::::::::::::::::::::::::: COUNT ::::::::::::::::::::::::::::::::::::::::::::::::::::::#
class TodayCountDetailsPerUserView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request, *args, **kwargs):
        login_user = int(self.request.user.id)       
        user_id = int(self.kwargs["user_id"])
        cur_date=datetime.now().date()
        today_counts = {}
        data_dict = {}
        is_team=self.request.query_params.get('is_team',None)
        print('is_team',is_team)
        login_user_details = self.request.user
        users_list=[login_user]
        is_hod = TCoreUserDetail.objects.filter(
                            hod = login_user_details,cu_is_deleted=False,cu_user__isnull=False)
        #print('is_hod',is_hod)
        hi_user_list_details = ''
        if is_hod:
            department_d = TCoreUserDetail.objects.filter(
                cu_user = login_user_details,cu_is_deleted=False,cu_user__isnull=False).values_list('department',flat=True)
            #print('department_d',department_d)
            if department_d:
                hi_user_list_details = TCoreUserDetail.objects.filter(department__in=department_d).values_list('cu_user',flat=True)
                #print('hi_user_list_details',hi_user_list_details)
                
        else:
            hi_user_list_details = TCoreUserDetail.objects.filter(
                reporting_head = login_user_details,cu_is_deleted=False,cu_user__isnull=False).values_list('cu_user',flat=True)
            #print('hi_user_list_details',list(hi_user_list_details))
            hi_user_details1 = ''
            if hi_user_list_details.count() > 0 :
                for hi_user_details in hi_user_list_details:
                    hi_user_list_details = self.getLowerLevelUserList(str(hi_user_details),list(hi_user_list_details))
                
        print('hi_user_list_details',hi_user_list_details)
        if hi_user_list_details:
            users_list+=hi_user_list_details
            print("users_list",users_list)
        #=============================================================================================================#
        task_count = EtaskTask.objects.filter((Q(assign_to_id=user_id)|Q(sub_assign_to_user_id=user_id)),
                                        (Q(Q(extended_date__isnull=False)&Q(extended_date__date=cur_date))|
                                        Q(Q(extended_date__isnull=True)&Q(end_date__date=cur_date))),
                                        is_deleted=False,task_status=1).count()
        
        today_counts['task_count'] = task_count
        #=============================================================================================================#
        followup_count = EtaskFollowUP.objects.filter(
                                           created_by=user_id,
                                            followup_status='pending',
                                            is_deleted=False,follow_up_date__date=cur_date).count()
        today_counts['followup_count'] = followup_count
        #=============================================================================================================#
        if is_team == 'True':
            reporting_count=EtaskTask.objects.filter(((Q(sub_assign_to_user__isnull=True)&Q(assign_to__in=users_list))|
                                        (Q(sub_assign_to_user__isnull=False)&Q(sub_assign_to_user__in=users_list))),
                                        owner=login_user,
                                        id__in=list(ETaskReportingDates.objects.filter(task_type=1,reporting_status=2,
                                        reporting_date__date=cur_date).values_list('task',flat=True)),
                                        task_status=1,is_deleted=False).count()          
        elif login_user==user_id:
            reporting_count = EtaskTask.objects.filter(((Q(sub_assign_to_user__isnull=True)&Q(assign_to=user_id))|
                                        (Q(sub_assign_to_user__isnull=False)&Q(sub_assign_to_user=user_id))),
                                        id__in=list(ETaskReportingDates.objects.filter(task_type=1,reporting_status=2,
                                        reporting_date__date=cur_date).values_list('task',flat=True)),
                                        task_status=1,is_deleted=False).count()
        else:
            reporting_count = EtaskTask.objects.filter(((Q(sub_assign_to_user__isnull=True)&Q(assign_to=user_id))|
                                        (Q(sub_assign_to_user__isnull=False)&Q(sub_assign_to_user=user_id))),
                                        owner=login_user,
                                        id__in=list(ETaskReportingDates.objects.filter(task_type=1,reporting_status=2,
                                        reporting_date__date=cur_date).values_list('task',flat=True)),
                                        task_status=1,is_deleted=False).count()
        today_counts['reporting_count'] = reporting_count
        #=============================================================================================================#
        if login_user == user_id:
            appinment_count = EtaskAppointment.objects.filter(Q(Appointment_status='ongoing'),
                                        (Q(Q(start_date__date__lte=cur_date)&Q(end_date__date__gte=cur_date))),
                                        (Q(id__in=list(EtaskInviteEmployee.objects.filter(user_id=login_user,
                                        is_deleted=False).values_list('appointment',flat=True)))|
                                        Q(created_by=login_user))).count()
        else:
            appinment_count = EtaskAppointment.objects.filter(Q(Appointment_status='ongoing'),
                                        (Q(Q(start_date__date__lte=cur_date)&Q(end_date__date__gte=cur_date))),
                                        (Q(Q(id__in=list(EtaskInviteEmployee.objects.filter(user_id=login_user,
                                        is_deleted=False).values_list('appointment',flat=True)))&Q(created_by=user_id))|
                                        Q(Q(id__in=list(EtaskInviteEmployee.objects.filter(user_id=user_id,
                                        is_deleted=False).values_list('appointment',flat=True)))&Q(created_by=login_user)))).count()
        today_counts['appinment_count'] = appinment_count
        #=============================================================================================================#
        extensions_count = EtaskTask.objects.filter((Q(assign_to__in=users_list)|Q(assign_by__in=users_list)|Q(sub_assign_to_user__in=users_list)|
                                            Q(owner__in=users_list)),is_deleted=False,is_reject=False,extended_date__isnull=True,
                                            requested_end_date__isnull=False).count()
        today_counts['extensions_count'] = extensions_count
        #=============================================================================================================#
        closures_count = EtaskTask.objects.filter((Q(assign_to__in=users_list)|Q(assign_by__in=users_list)|Q(sub_assign_to_user__in=users_list)|
                                        Q(owner__in=users_list)),task_status=2,is_deleted=False,is_closure=True,completed_date__isnull=False).count()
        today_counts['closures_count'] = closures_count
        #=============================================================================================================#
        if login_user == user_id:
            comments_count = EtaskTask.objects.filter((Q(assign_to_id=user_id)|Q(sub_assign_to_user_id=user_id)|Q(assign_by_id=user_id)),
                                        id__in=list(ETaskCommentsViewers.objects.filter(user=login_user,
                                        is_view=False,is_deleted=False).values_list('task',flat=True)),
                                        is_deleted=False).count()

        else:
            comments_count = EtaskTask.objects.filter((Q(Q(assign_to_id=user_id)|Q(sub_assign_to_user_id=user_id))&Q(assign_by_id=login_user)),
                                        id__in=list(ETaskCommentsViewers.objects.filter(user=login_user,
                                        is_view=False,is_deleted=False).values_list('task',flat=True)),
                                        is_deleted=False).count()
        today_counts['comments_count'] = comments_count
        #=============================================================================================================#
        data_dict['result'] = today_counts
        if today_counts:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_SUCCESS
        elif len(today_counts) == 0:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_NO_DATA
        else:
            data_dict['request_status'] = 0
            data_dict['msg'] = settings.MSG_ERROR

        return Response(data_dict)
    def getLowerLevelUserList(self, user_id='',main_list='') -> list:
        try:
            #print('user_id',user_id)
            #print('main_list',main_list)
            hi_user_list_details =TCoreUserDetail.objects.filter(reporting_head_id = str(user_id),cu_is_deleted=False,cu_user__isnull=False).values_list(
                'cu_user_id',flat=True)
            #print('hi_user_list_details1111',hi_user_list_details)
            if hi_user_list_details.count() > 0 :
                for hi_user_details in hi_user_list_details:
                    main_list.append(hi_user_details)
                    self.getLowerLevelUserList(str(hi_user_details),main_list)
            return main_list
        except Exception as e:
            raise e
class UpcomingCountDetailsPerUserView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request, *args, **kwargs):
        login_user = int(self.request.user.id)
        user_id = int(self.kwargs["user_id"])
        cur_date=datetime.now().date()
        today_counts = {}
        data_dict = {}
        is_team=self.request.query_params.get('is_team',None)
        print('is_team',is_team)
        login_user_details = self.request.user
        users_list=[login_user]
        is_hod = TCoreUserDetail.objects.filter(
                            hod = login_user_details,cu_is_deleted=False,cu_user__isnull=False)
        #print('is_hod',is_hod)
        hi_user_list_details = ''
        if is_hod:
            department_d = TCoreUserDetail.objects.filter(
                cu_user = login_user_details,cu_is_deleted=False,cu_user__isnull=False).values_list('department',flat=True)
            #print('department_d',department_d)
            if department_d:
                hi_user_list_details = TCoreUserDetail.objects.filter(department__in=department_d).values_list('cu_user',flat=True)
                #print('hi_user_list_details',hi_user_list_details)
                
        else:
            hi_user_list_details = TCoreUserDetail.objects.filter(
                reporting_head = login_user_details,cu_is_deleted=False,cu_user__isnull=False).values_list('cu_user',flat=True)
            #print('hi_user_list_details',list(hi_user_list_details))
            hi_user_details1 = ''
            if hi_user_list_details.count() > 0 :
                for hi_user_details in hi_user_list_details:
                    hi_user_list_details = self.getLowerLevelUserList(str(hi_user_details),list(hi_user_list_details))
                
        print('hi_user_list_details',hi_user_list_details)
        if hi_user_list_details:
            users_list+=hi_user_list_details
            print("users_list",users_list)
        #============================================== TASK ===============================================================#
        task_count = EtaskTask.objects.filter((Q(assign_to_id=user_id)|Q(sub_assign_to_user_id=user_id)),
                                    (Q(Q(extended_date__isnull=False)&Q(extended_date__date__gt=cur_date))|Q(Q(extended_date__isnull=True)&Q(end_date__date__gt=cur_date))),
                                    is_deleted=False,task_status=1).count()
        today_counts['task_count'] = task_count
        #=============================================== FOLLOWUP ==============================================================#
        followup_count = EtaskFollowUP.objects.filter(
                                                       created_by=user_id,
                                                        follow_up_date__date__gt=cur_date,is_deleted=False).count()
        today_counts['followup_count'] = followup_count
        #================================================ REPORTING =============================================================#
        if is_team == 'True':
            reporting_count=ETaskReportingDates.objects.filter(
                                        task__in=list(EtaskTask.objects.filter(((Q(sub_assign_to_user__isnull=True)&Q(assign_to__in=users_list))|
                                        (Q(sub_assign_to_user__isnull=False)&Q(sub_assign_to_user__in=users_list))),
                                        owner=login_user,
                                        task_status=1,is_deleted=False).values_list('id',flat=True)),
                                        task_type=1,reporting_status=2,reporting_date__date__gt=cur_date).count() 
        elif login_user==user_id:
            reporting_count = ETaskReportingDates.objects.filter(task__in=list(EtaskTask.objects.filter(
                                        ((Q(sub_assign_to_user__isnull=True)&Q(assign_to=user_id))|
                                        (Q(sub_assign_to_user__isnull=False)&Q(sub_assign_to_user=user_id))),
                                        task_status=1,is_deleted=False).values_list('id',flat=True)),
                                        task_type=1,reporting_status=2,reporting_date__date__gt=cur_date).count()
        else:
            reporting_count = ETaskReportingDates.objects.filter(
                                        task__in=list(EtaskTask.objects.filter(((Q(sub_assign_to_user__isnull=True)&Q(assign_to=user_id))|
                                        (Q(sub_assign_to_user__isnull=False)&Q(sub_assign_to_user=user_id))),
                                        owner=login_user,
                                        task_status=1,is_deleted=False).values_list('id',flat=True)),
                                        task_type=1,reporting_status=2,reporting_date__date__gt=cur_date).count()
        today_counts['reporting_count'] = reporting_count
        #================================================== APPOINMENT ===========================================================#
        if login_user == user_id:
            appinment_count = EtaskAppointment.objects.filter((Q(id__in=list(EtaskInviteEmployee.objects.filter(user_id=login_user,
                                                                is_deleted=False).values_list('appointment',flat=True)))|
                                                                Q(created_by=login_user)),
                                                                start_date__date__gt=cur_date,Appointment_status='ongoing').count()
        else:
            appinment_count = EtaskAppointment.objects.filter((Q(Q(id__in=list(EtaskInviteEmployee.objects.filter(user_id=login_user,
                                                            is_deleted=False).values_list('appointment',flat=True)))&Q(created_by=user_id))|
                                                            Q(Q(id__in=list(EtaskInviteEmployee.objects.filter(user_id=user_id,is_deleted=False
                                                            ).values_list('appointment',flat=True)))&Q(created_by=user_id))),
                                                            start_date__date__gt=cur_date,Appointment_status='ongoing').count()
        today_counts['appinment_count'] = appinment_count
        #=============================================================================================================#
        data_dict['result'] = today_counts
        if today_counts:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_SUCCESS
        elif len(today_counts) == 0:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_NO_DATA
        else:
            data_dict['request_status'] = 0
            data_dict['msg'] = settings.MSG_ERROR

        return Response(data_dict)
    def getLowerLevelUserList(self, user_id='',main_list='') -> list:
        try:
            #print('user_id',user_id)
            #print('main_list',main_list)
            hi_user_list_details =TCoreUserDetail.objects.filter(reporting_head_id = str(user_id),cu_is_deleted=False,cu_user__isnull=False).values_list(
                'cu_user_id',flat=True)
            #print('hi_user_list_details1111',hi_user_list_details)
            if hi_user_list_details.count() > 0 :
                for hi_user_details in hi_user_list_details:
                    main_list.append(hi_user_details)
                    self.getLowerLevelUserList(str(hi_user_details),main_list)
            return main_list
        except Exception as e:
            raise e

class OverDueCountDetailsPerUserView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request, *args, **kwargs):
        login_user = int(self.request.user.id)
        user_id = int(self.kwargs["user_id"])
        cur_date=datetime.now().date()
        today_counts = {}
        data_dict = {}
        is_team=self.request.query_params.get('is_team',None)
        print('is_team',is_team)
        login_user_details = self.request.user
        users_list=[login_user]
        is_hod = TCoreUserDetail.objects.filter(
                            hod = login_user_details,cu_is_deleted=False,cu_user__isnull=False)
        #print('is_hod',is_hod)
        hi_user_list_details = ''
        if is_hod:
            department_d = TCoreUserDetail.objects.filter(
                cu_user = login_user_details,cu_is_deleted=False,cu_user__isnull=False).values_list('department',flat=True)
            #print('department_d',department_d)
            if department_d:
                hi_user_list_details = TCoreUserDetail.objects.filter(department__in=department_d).values_list('cu_user',flat=True)
                #print('hi_user_list_details',hi_user_list_details)
                
        else:
            hi_user_list_details = TCoreUserDetail.objects.filter(
                reporting_head = login_user_details,cu_is_deleted=False,cu_user__isnull=False).values_list('cu_user',flat=True)
            #print('hi_user_list_details',list(hi_user_list_details))
            hi_user_details1 = ''
            if hi_user_list_details.count() > 0 :
                for hi_user_details in hi_user_list_details:
                    hi_user_list_details = self.getLowerLevelUserList(str(hi_user_details),list(hi_user_list_details))
                
        print('hi_user_list_details',hi_user_list_details)
        if hi_user_list_details:
            users_list+=hi_user_list_details
            print("users_list",users_list)

        #============================================== TASK ===============================================================#
        if int(login_user)==int(user_id):
            task_count = EtaskTask.objects.filter((Q(assign_to_id=user_id)|Q(sub_assign_to_user_id=user_id)),
                                                ((Q(extended_date__isnull=False)&Q(extend_with_delay=False)&
                                                Q(extended_date__date__lt=cur_date))|(Q(extended_date__isnull=True)&
                                                Q(end_date__date__lt=cur_date))),is_deleted=False,task_status=1).count()
        else:
            task_count = EtaskTask.objects.filter((Q(Q(assign_to_id=user_id)|Q(sub_assign_to_user_id=user_id))&
                                                Q(Q(assign_by_id=login_user)|Q(assign_to_id=login_user))),
                                                ((Q(extended_date__isnull=False)&Q(extend_with_delay=False)&
                                                Q(extended_date__date__lt=cur_date))|(Q(extended_date__isnull=True)&
                                                Q(end_date__date__lt=cur_date))),is_deleted=False,task_status=1).count()
        today_counts['task_count'] = task_count
        #=============================================== FOLLOWUP ==============================================================#
        followup_count = EtaskFollowUP.objects.filter(
                                                        created_by=user_id,
                                                        follow_up_date__date__lt=cur_date,is_deleted=False
                                                    ).count()
        today_counts['followup_count'] = followup_count
        #================================================ REPORTING =============================================================#
        if is_team == 'True':
            reporting_count=ETaskReportingDates.objects.filter(
                                        task__in=list(EtaskTask.objects.filter(((Q(sub_assign_to_user__isnull=True)&Q(assign_to__in=users_list))|
                                        (Q(sub_assign_to_user__isnull=False)&Q(sub_assign_to_user__in=users_list))),
                                        owner=login_user,
                                        task_status=1,is_deleted=False).values_list('id',flat=True)),
                                        task_type=1,reporting_status=2,reporting_date__date__lt=cur_date).count()
        elif login_user==user_id:
            reporting_count = ETaskReportingDates.objects.filter(task__in=list(EtaskTask.objects.filter(
                                        ((Q(sub_assign_to_user__isnull=True)&Q(assign_to=user_id))|
                                        (Q(sub_assign_to_user__isnull=False)&Q(sub_assign_to_user=user_id))),
                                        task_status=1,is_deleted=False).values_list('id',flat=True)),
                                        task_type=1,reporting_status=2,reporting_date__date__lt=cur_date).count()
        else:
            reporting_count = ETaskReportingDates.objects.filter(task__in=list(EtaskTask.objects.filter(
                                        ((Q(sub_assign_to_user__isnull=True)&Q(assign_to=user_id))|
                                        (Q(sub_assign_to_user__isnull=False)&Q(sub_assign_to_user=user_id))),
                                        owner=login_user,
                                        task_status=1,is_deleted=False).values_list('id',flat=True)),
                                        task_type=1,reporting_status=2,reporting_date__date__lt=cur_date).count()
        today_counts['reporting_count'] = reporting_count
        #================================================== APPOINMENT ===========================================================#
        if login_user == user_id:
            appinment_count = EtaskAppointment.objects.filter((Q(id__in=list(EtaskInviteEmployee.objects.filter(user_id=login_user,
                                                                is_deleted=False).values_list('appointment',flat=True)))|
                                                                Q(created_by=login_user)),end_date__date__lt=cur_date,
                                                                Appointment_status='ongoing').count()
        else:
            appinment_count = EtaskAppointment.objects.filter((Q(Q(id__in=list(EtaskInviteEmployee.objects.filter(user_id=login_user,
                                                                is_deleted=False).values_list('appointment',flat=True)))&
                                                                Q(created_by=user_id))|
                                                                Q(Q(id__in=list(EtaskInviteEmployee.objects.filter(user_id=user_id,
                                                                is_deleted=False).values_list('appointment',flat=True)))&
                                                                Q(created_by=login_user))),end_date__date__lt=cur_date,
                                                                Appointment_status='ongoing').count()
        today_counts['appinment_count'] = appinment_count
        #=============================================================================================================#
        data_dict['result'] = today_counts
        if today_counts:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_SUCCESS
        elif len(today_counts) == 0:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_NO_DATA
        else:
            data_dict['request_status'] = 0
            data_dict['msg'] = settings.MSG_ERROR

        return Response(data_dict)
    def getLowerLevelUserList(self, user_id='',main_list='') -> list:
        try:
            #print('user_id',user_id)
            #print('main_list',main_list)
            hi_user_list_details =TCoreUserDetail.objects.filter(reporting_head_id = str(user_id),cu_is_deleted=False,cu_user__isnull=False).values_list(
                'cu_user_id',flat=True)
            #print('hi_user_list_details1111',hi_user_list_details)
            if hi_user_list_details.count() > 0 :
                for hi_user_details in hi_user_list_details:
                    main_list.append(hi_user_details)
                    self.getLowerLevelUserList(str(hi_user_details),main_list)
            return main_list
        except Exception as e:
            raise e

class ClosedCountDetailsPerUserView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request, *args, **kwargs):
        login_user = int(self.request.user.id)
        user_id = int(self.kwargs["user_id"])
        cur_date=datetime.now().date()
        today_counts = {}
        data_dict = {}

        #============================================== TASK ===============================================================#
        task_count = EtaskTask.objects.filter((Q(assign_to_id=user_id)|Q(sub_assign_to_user_id=user_id)),
                                        is_deleted=False,task_status=4).count()
        today_counts['task_count'] = task_count

        #================================================== APPOINMENT ===========================================================#
        if login_user == user_id:
            appinment_count = EtaskAppointment.objects.filter((Q(id__in=list(EtaskInviteEmployee.objects.filter(user_id=login_user,
                                                                is_deleted=False).values_list('appointment',flat=True)))|
                                                                Q(created_by=login_user)),Appointment_status='completed').count()
        else:
            appinment_count = EtaskAppointment.objects.filter((Q(Q(id__in=list(EtaskInviteEmployee.objects.filter(user_id=login_user,
                                                                is_deleted=False).values_list('appointment',flat=True)))&
                                                                Q(created_by=user_id))|
                                                                Q(Q(id__in=list(EtaskInviteEmployee.objects.filter(user_id=user_id,
                                                                is_deleted=False).values_list('appointment',flat=True)))&
                                                                Q(created_by=login_user))),Appointment_status='completed').count()
        today_counts['appinment_count'] = appinment_count

        #=============================================================================================================#
        data_dict['result'] = today_counts
        if today_counts:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_SUCCESS
        elif len(today_counts) == 0:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_NO_DATA
        else:
            data_dict['request_status'] = 0
            data_dict['msg'] = settings.MSG_ERROR

        return Response(data_dict)

class DashboardCountDetailsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request, *args, **kwargs):
        login_user = int(self.request.user.id)
        login_user_details = self.request.user
        # user_id = int(self.kwargs["user_id"])
        cur_date=datetime.now().date()
        today_counts = {}
        data_dict = {}
        users_list=[login_user]
        is_hod = TCoreUserDetail.objects.filter(
                            hod = login_user_details,cu_is_deleted=False,cu_user__isnull=False)
        #print('is_hod',is_hod)
        hi_user_list_details = ''
        if is_hod:
            department_d = TCoreUserDetail.objects.filter(
                cu_user = login_user_details,cu_is_deleted=False,cu_user__isnull=False).values_list('department',flat=True)
            #print('department_d',department_d)
            if department_d:
                hi_user_list_details = TCoreUserDetail.objects.filter(department__in=department_d).values_list('cu_user',flat=True)
                #print('hi_user_list_details',hi_user_list_details)
                
        else:
            hi_user_list_details = TCoreUserDetail.objects.filter(
                reporting_head = login_user_details,cu_is_deleted=False,cu_user__isnull=False).values_list('cu_user',flat=True)
            #print('hi_user_list_details',list(hi_user_list_details))
            hi_user_details1 = ''
            if hi_user_list_details.count() > 0 :
                for hi_user_details in hi_user_list_details:
                    hi_user_list_details = self.getLowerLevelUserList(str(hi_user_details),list(hi_user_list_details))
                
        print('hi_user_list_details',hi_user_list_details)
        if hi_user_list_details:
            users_list+=hi_user_list_details
            print("users_list",users_list)
        #++++++++++++++++++++++++++++++++++++++++++++ TODAY ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
        #===================================================== task count ========================================================#
        today_task_count = EtaskTask.objects.filter((Q(assign_to_id__in=users_list)|Q(sub_assign_to_user_id__in=users_list)),
                                        (Q(Q(extended_date__isnull=False)&Q(extended_date__date=cur_date))|
                                        Q(Q(extended_date__isnull=True)&Q(end_date__date=cur_date))),
                                        is_deleted=False,task_status=1).count()
        today_counts['today_task_count'] = today_task_count
        #===================================================== followup count ========================================================#
        today_followup_count = EtaskFollowUP.objects.filter(
                                            created_by__in=users_list,
                                            followup_status='pending',
                                            is_deleted=False,follow_up_date__date=cur_date).count()
        today_counts['today_followup_count'] = today_followup_count
        #=================================================== reporting count ==========================================================#
        today_reporting_count = EtaskTask.objects.filter(((Q(sub_assign_to_user__isnull=True)&Q(assign_to__in=users_list))|
                                        (Q(sub_assign_to_user__isnull=False)&Q(sub_assign_to_user__in=users_list))),
                                        #owner=login_user,
                                        id__in=list(ETaskReportingDates.objects.filter(task_type=1,reporting_status=2,
                                        reporting_date__date=cur_date).values_list('task',flat=True)),
                                        task_status=1,is_deleted=False).count()
        today_counts['today_reporting_count'] = today_reporting_count
        #=================================================== appinment count ==========================================================#
        today_appinment_count = EtaskAppointment.objects.filter(Q(Appointment_status='ongoing'),
                                        (Q(Q(start_date__date__lte=cur_date)&Q(end_date__date__gte=cur_date))),
                                        (Q(id__in=list(EtaskInviteEmployee.objects.filter(user_id=login_user,
                                        is_deleted=False).values_list('appointment',flat=True)))|
                                        Q(created_by_id=login_user))).count()
        today_counts['today_appinment_count'] = today_appinment_count
        #===================================================== extensions count ========================================================#
        today_extensions_count = EtaskTask.objects.filter((Q(assign_to__in=users_list)|Q(assign_by__in=users_list)|Q(sub_assign_to_user__in=users_list)|
                                            Q(owner__in=users_list)),is_deleted=False,is_reject=False,extended_date__isnull=True,
                                            requested_end_date__isnull=False).count()
        today_counts['today_extensions_count'] = today_extensions_count
        #=================================================== closures count ========================================================#
        today_closures_count = EtaskTask.objects.filter((Q(assign_to__in=users_list)|Q(assign_by__in=users_list)|Q(sub_assign_to_user__in=users_list)|
                                        Q(owner__in=users_list)),task_status=2,is_deleted=False,is_closure=True,completed_date__isnull=False).count()
        today_counts['today_closures_count'] = today_closures_count
        #================================================== comments count ===========================================================#       
        today_comments_count = EtaskTask.objects.filter((Q(assign_to_id__in=users_list)|Q(sub_assign_to_user_id__in=users_list)|Q(assign_by_id=login_user)),
                                        id__in=list(ETaskCommentsViewers.objects.filter(user=login_user,
                                        is_view=False,is_deleted=False).values_list('task',flat=True)),
                                        is_deleted=False).count()
        today_counts['today_comments_count'] = today_comments_count

        #++++++++++++++++++++++++++++++++++++++++++++ UPCOMING ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
        #============================================== TASK ===============================================================#    
        upcoming_task_count = EtaskTask.objects.filter((Q(assign_to_id__in=users_list)|Q(sub_assign_to_user_id__in=users_list)),
                                        (Q(Q(extended_date__isnull=False)&Q(extended_date__date__gt=cur_date))|
                                        Q(Q(extended_date__isnull=True)&Q(end_date__date__gt=cur_date))),
                                        is_deleted=False,task_status=1).count()
        today_counts['upcoming_task_count'] = upcoming_task_count
        #=============================================== FOLLOWUP ==============================================================#
        upcoming_followup_count = EtaskFollowUP.objects.filter(
                                                        created_by__in=users_list,
                                                        follow_up_date__date__gt=cur_date,is_deleted=False).count()
        today_counts['upcoming_followup_count'] = upcoming_followup_count
        #================================================ REPORTING =============================================================#
        upcoming_reporting_count = ETaskReportingDates.objects.filter(task_type=1,reporting_status=2,reporting_date__date__gt=cur_date,
                                        task__in=list(EtaskTask.objects.filter(Q(Q(sub_assign_to_user__isnull=True)&Q(assign_to__in=users_list))|
                                        Q(Q(sub_assign_to_user__isnull=False)&Q(sub_assign_to_user__in=users_list)),
                                        task_status=1,is_deleted=False).values_list('id',flat=True))
                                        ).count()

        today_counts['upcoming_reporting_count'] = upcoming_reporting_count
        #================================================== APPOINMENT ===========================================================#
        upcoming_appinment_count = EtaskAppointment.objects.filter((Q(id__in=list(EtaskInviteEmployee.objects.filter(user_id=login_user,
                                                                    is_deleted=False).values_list('appointment',flat=True)))|
                                                                    Q(created_by_id=login_user)),
                                                                    start_date__date__gt=cur_date,Appointment_status='ongoing'
                                                                ).count()

        today_counts['upcoming_appinment_count'] = upcoming_appinment_count

        #++++++++++++++++++++++++++++++++++++++++++++ OVERDUE ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
        #============================================== TASK ===============================================================#
        overdue_task_count = EtaskTask.objects.filter((Q(assign_to_id__in=users_list)|Q(sub_assign_to_user_id__in=users_list)),
                                        (Q(Q(extended_date__isnull=False)&Q(extended_date__date__lt=cur_date))|
                                        Q(Q(extended_date__isnull=True)&Q(end_date__date__lt=cur_date))),
                                        is_deleted=False,task_status=1).count()
        today_counts['overdue_task_count'] = overdue_task_count
        #=============================================== FOLLOWUP ==============================================================#
        overdue_followup_count = EtaskFollowUP.objects.filter(
                                                        created_by__in=users_list,
                                                        follow_up_date__date__lt=cur_date,is_deleted=False).count()
        today_counts['overdue_followup_count'] = overdue_followup_count
        #================================================ REPORTING =============================================================#
        overdue_reporting_count = ETaskReportingDates.objects.filter(task_type=1,reporting_status=2,reporting_date__date__lt=cur_date,
                                        task__in=list(EtaskTask.objects.filter(Q(Q(sub_assign_to_user__isnull=True)&Q(assign_to__in=users_list))|
                                        Q(Q(sub_assign_to_user__isnull=False)&Q(sub_assign_to_user__in=users_list)),
                                        task_status=1,is_deleted=False).values_list('id',flat=True))).count()
        today_counts['overdue_reporting_count'] = overdue_reporting_count
        #================================================== APPOINMENT ===========================================================#
        overdue_appinment_count = EtaskAppointment.objects.filter((Q(id__in=list(EtaskInviteEmployee.objects.filter(user_id=login_user,
                                                                    is_deleted=False).values_list('appointment',flat=True)))|
                                                                    Q(created_by_id=login_user)),
                                                                    start_date__date__lt=cur_date,Appointment_status='ongoing'
                                                                ).count()
        today_counts['overdue_appinment_count'] = overdue_appinment_count

        #++++++++++++++++++++++++++++++++++++++++++++ CLOSED ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
        #============================================== TASK ===============================================================#
        closed_task_count = EtaskTask.objects.filter(Q(assign_to_id__in=users_list)|Q(sub_assign_to_user_id__in=users_list)|Q(assign_by_id__in=users_list),
                                                is_deleted=False,task_status=4).count()
        today_counts['closed_task_count'] = closed_task_count

        #================================================== APPOINMENT ===========================================================#
        closed_appinment_count = EtaskAppointment.objects.filter((Q(id__in=list(EtaskInviteEmployee.objects.filter(user_id=login_user,
                                                                    is_deleted=False).values_list('appointment',flat=True)))|
                                                                    Q(created_by_id=login_user)),Appointment_status='completed').count()
        today_counts['closed_appinment_count'] = closed_appinment_count
        #=========================================================================================================================#

        data_dict['result'] = today_counts
        if today_counts:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_SUCCESS
        elif len(today_counts) == 0:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_NO_DATA
        else:
            data_dict['request_status'] = 0
            data_dict['msg'] = settings.MSG_ERROR

        return Response(data_dict)
    def getLowerLevelUserList(self, user_id='',main_list='') -> list:
        try:
            #print('user_id',user_id)
            #print('main_list',main_list)
            hi_user_list_details =TCoreUserDetail.objects.filter(reporting_head_id = str(user_id),cu_is_deleted=False,cu_user__isnull=False).values_list(
                'cu_user_id',flat=True)
            #print('hi_user_list_details1111',hi_user_list_details)
            if hi_user_list_details.count() > 0 :
                for hi_user_details in hi_user_list_details:
                    main_list.append(hi_user_details)
                    self.getLowerLevelUserList(str(hi_user_details),main_list)
            return main_list
        except Exception as e:
            raise e

class TodayTomorrowUpcomingPlannerView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request, *args, **kwargs):
        login_user =self.request.user.id
        print('login_user',login_user)
        cur_date=datetime.now().date()
        print('cur_date',cur_date)
        tomorrow_date=datetime.now().date()+timedelta(1)
        print('tomorrow_date',tomorrow_date)
        overall_dict={}
        data_dict={}
        todays_appointment_list=[]
        todays_appointment=EtaskInviteEmployee.objects.filter((Q(appointment__start_date__date__lte=cur_date)&Q(appointment__end_date__date__gte=cur_date)),
                                                             user_id=login_user,is_deleted=False,appointment__Appointment_status='ongoing').values(
                                                                'appointment__appointment_subject',
                                                                'appointment__start_date',
                                                                'appointment__start_time',
                                                                'appointment__end_time')
        print('todays_appointment',todays_appointment)
        if todays_appointment:
            # print('sub1',todays_appointment[0]['appointment__appointment_subject'])
            for t_a in todays_appointment:
                # print('sub',t_a['appointment__appointment_subject'])
                today_app={
                    'appointment_subject':t_a['appointment__appointment_subject'],
                    'start_date':t_a['appointment__start_date'],
                    'start_time':t_a['appointment__start_time'],
                    'end_time':t_a['appointment__end_time']
                }
                todays_appointment_list.append(today_app)
            overall_dict['todays_appointment']=todays_appointment_list
        else:
            overall_dict['todays_appointment']=[]

        tomorrow_appointment_list=[]
        tomorrow_appointment=EtaskInviteEmployee.objects.filter((Q(appointment__start_date__date__lte=tomorrow_date)&Q(appointment__end_date__date__gte=tomorrow_date)),
                                                             user_id=login_user,is_deleted=False,appointment__Appointment_status='ongoing').values(
                                                                'appointment__appointment_subject',
                                                                'appointment__start_date',
                                                                'appointment__start_time',
                                                                'appointment__end_time')
        print('tomorrow_appointment',tomorrow_appointment)
        if tomorrow_appointment:
            # print('sub1',todays_appointment[0]['appointment__appointment_subject'])
            for t_a in tomorrow_appointment:
                # print('sub',t_a['appointment__appointment_subject'])
                tomorrow_app={
                    'appointment_subject':t_a['appointment__appointment_subject'],
                    'start_date':t_a['appointment__start_date'],
                    'start_time':t_a['appointment__start_time'],
                    'end_time':t_a['appointment__end_time']
                }
                tomorrow_appointment_list.append(tomorrow_app)
            overall_dict['tomorrows_appointment']=tomorrow_appointment_list
        else:
            overall_dict['tomorrows_appointment']=[]

        upcoming_appointment_list=[]
        upcoming_appointment=EtaskInviteEmployee.objects.filter(appointment__start_date__date__gt=cur_date,
                                                             user_id=login_user,is_deleted=False,appointment__Appointment_status='ongoing').values(
                                                                'appointment__appointment_subject',
                                                                'appointment__start_date',
                                                                'appointment__start_time',
                                                                'appointment__end_time',
                                                                'appointment__location',
                                                                )
        print('upcoming_appointment',upcoming_appointment)
        if upcoming_appointment:
            # print('sub1',todays_appointment[0]['appointment__appointment_subject'])
            for t_a in upcoming_appointment:
                # print('sub',t_a['appointment__appointment_subject'])
                upcoming_app={
                    'appointment_subject':t_a['appointment__appointment_subject'],
                    'start_date':t_a['appointment__start_date'],
                    'start_time':t_a['appointment__start_time'],
                    'end_time':t_a['appointment__end_time'],
                    'location':t_a['appointment__location']
                }
                upcoming_appointment_list.append(upcoming_app)
            overall_dict['upcoming_appointment']=upcoming_appointment_list
        else:
            overall_dict['upcoming_appointment']=[]
        
        todays_task=EtaskTask.objects.filter((Q(assign_to_id=login_user)|Q(sub_assign_to_user_id=login_user)),
                                            (Q(Q(extended_date__isnull=False)&Q(extended_date__date=cur_date))|
                                            Q(Q(extended_date__isnull=True)&Q(end_date__date=cur_date))),
                                            task_status=1,is_deleted=False)
        task_list=[]
        for t_d in todays_task:
            task_data={
                'id':t_d.id,
                'task_code_id':t_d.task_code_id,
                'parent_id':t_d.parent_id,
                'task_subject':t_d.task_subject,
                'task_description':t_d.task_description,
            }            
            if int(t_d.parent_id) != 0:
                parent_id_name = EtaskTask.objects.filter(task_status=1,is_deleted=False,id=t_d.parent_id).values('id','task_subject')
                if parent_id_name:
                    task_data['parent'] = {
                        "id" :  t_d.parent_id,
                        "name" :parent_id_name[0]['task_subject']
                    }
                else :
                    task_data['parent'] = None
            else:
                task_data['parent'] = None
            latest_comment=ETaskComments.objects.filter(task_id=t_d.id,is_deleted=False).values('comments','created_at').order_by('-created_at')
            print('latest_comment',latest_comment)
            task_data['last_comment']=latest_comment[0]['comments'] if latest_comment else ""
            task_data['last_comment_date']=latest_comment[0]['created_at'] if latest_comment else None
            task_list.append(task_data)
        overall_dict['todays_task']=task_list if task_list else []

        todays_follow_up=EtaskFollowUP.objects.filter(created_by_id=login_user,followup_status='pending',is_deleted=False,follow_up_date__date=cur_date
                                                    ).values('id','follow_up_task','assign_for')
        print('todays_follow_up',todays_follow_up)
        todays_follow_up_list=[]
        if todays_follow_up:
            for t_f in todays_follow_up:
                follow_up_det={
                    'follow_up_task':t_f['follow_up_task'],
                    'follow_up_with':userdetails(t_f['assign_for'])
                }
                print('follow_up_det',follow_up_det)
                follow_up_comment=FollowupComments.objects.filter(followup_id=t_f['id'],is_deleted=False).values('comments','created_at').order_by('-created_at')
                follow_up_det['last_comment']=follow_up_comment[0]['comments'] if follow_up_comment else ""
                follow_up_det['last_comment_date']=follow_up_comment[0]['created_at'] if follow_up_comment else None

                todays_follow_up_list.append(follow_up_det)
        
        overall_dict['todays_follow_up']=todays_follow_up_list if todays_follow_up_list else []

        data_dict['result'] = overall_dict
        if overall_dict:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_SUCCESS
        elif len(overall_dict) == 0:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_NO_DATA
        else:
            data_dict['request_status'] = 0
            data_dict['msg'] = settings.MSG_ERROR

        return Response(data_dict)


