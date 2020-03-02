from django.shortcuts import render
from rest_framework import generics
from eticket.serializers import *
from rest_framework.response import Response
from rest_framework import filters
from rest_framework.permissions import IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from pagination import CSLimitOffestpagination, CSPageNumberPagination,OnOffPagination
from django_filters.rest_framework import DjangoFilterBackend
from master.models import TMasterOtherRole, TMasterModuleRoleUser
import collections
from rest_framework import mixins
from custom_decorator import *
from rest_framework.views import APIView
from django.db.models import When, Case, Value, CharField, IntegerField, F, Q
from mailsend.views import *
from threading import Thread  # for threading
import datetime
from users.serializers import UserSerializer

class EticketReportingHeadAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    pagination_class =OnOffPagination
    queryset = ETICKETReportingHead.objects.filter(is_deleted=False).order_by('-id')
    serializer_class = EticketReportingHeadAddSerializer
    filter_backends = [filters.OrderingFilter]
    # ordering_fields = ['department', 'reporting_head']

    def get_queryset(self):

        id = self.request.query_params.get('id',None)
        ordering = self.request.query_params.get('ordering', None)
        # order_by = self.request.query_params.get('order_by', None)
        sort_field = '-id'
        if ordering:      
            if ordering =='department':
                sort_field='department'
            if ordering =='-department':
                sort_field='-department'
            if ordering =='reporting_head':
                sort_field='reporting_head'
            if ordering =='-reporting_head':
                sort_field='-reporting_head'

        if id:
            return  ETICKETReportingHead.objects.filter(id = id).order_by(sort_field)
        else:
            return  ETICKETReportingHead.objects.order_by(sort_field)
    

    @response_modify_decorator_post
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    

    
    @response_modify_decorator_list_or_get_before_execution_for_onoff_pagination
    def get(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class EticketReportingHeadEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = ETICKETReportingHead.objects.all()
    serializer_class = EticketReportingHeadEditSerializer

    @response_modify_decorator_post
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

class EticketTicketSubjectListByDepartmentAddView(generics.ListCreateAPIView,mixins.UpdateModelMixin):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = ETICKETSubjectOfDepartment.objects.all()
    pagination_class = OnOffPagination
    serializer_class = EticketTicketSubjectListByDepartmentAddSerializer
    filter_backends = (filters.SearchFilter,)
    # ordering_fields = ['department']

    def get_queryset(self):
        id = self.request.query_params.get('id',None)
        ordering = self.request.query_params.get('ordering', None)
        # order_by = self.request.query_params.get('order_by', None)
        sort_field = '-id'
        if ordering:      
            if ordering =='department':
                sort_field='department'
            if ordering =='-department':
                sort_field='-department'
        return self.queryset.order_by(sort_field)
    
    def get(self, request, *args, **kwargs):
        id = self.request.query_params.get('id', None)
        print('id',id)
        if id is None:
            response = super(self.__class__, self).list(self, request, args, kwargs)
            response1 = response.data['results'] if 'results' in response.data else response.data

            for data in response1:
                dept = TCoreDepartment.objects.filter(~Q(cd_parent_id=0),pk=data['department'])
                # print('dept',dept.query)
                # print('deptcheck',dept)
                if dept:
                    dept = TCoreDepartment.objects.get(~Q(cd_parent_id=0),pk=data['department'])
                    data['department_details'] = {
                    'id':dept.cd_parent_id,
                    'name': TCoreDepartment.objects.only('cd_name').get(pk=dept.cd_parent_id).cd_name,
                    'child':{
                        'id': dept.id,
                        'name':dept.cd_name
                        }
                    } 
                else:
                    data['department_details'] = {
                    'id':data['department'],
                    'name': TCoreDepartment.objects.only('cd_name').get(pk=data['department']).cd_name,
                    'child':None
                    }
                    
            data_dict = {}
            if 'results' in response.data:
                data_dict = response.data
            else:
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
        else:
            data_dict = dict()
            response = ETICKETSubjectOfDepartment.objects.filter(id = id)
            #print('response',response)
            if response:
                response = response.values()[0]
                print('response',response['department_id'])
                dept = TCoreDepartment.objects.filter(~Q(cd_parent_id=0),id=response['department_id'])
                print('dept',dept.query)
                if dept:
                    dept = dept.values()[0]
                    response['department_details'] = {
                        'id':dept['cd_parent_id'],
                        'name': TCoreDepartment.objects.only('cd_name').get(pk=dept['cd_parent_id']).cd_name,
                        'child':{
                            'id': dept['id'],
                            'name':dept['cd_name']
                            }
                    } 

                else:
                    print('response',response)
                    dept = TCoreDepartment.objects.get(pk=response['department_id'])
                    response['department_details'] = {
                        'id':dept.id,
                        'name': dept.cd_name,
                        'child':None
                    } 
               

            #print('response',response)
            if response:
                data_dict['request_status'] = 1
                data_dict['msg'] = settings.MSG_SUCCESS
                data_dict['results'] = response
            else:
                data_dict['request_status'] = 1
                data_dict['msg'] = settings.MSG_NO_DATA
                data_dict['results'] = ""

            return Response(data_dict)

    @response_modify_decorator_post
    def post(self, request, *args, **kwargs):
        response = super().post(request,*args,**kwargs)
        return response
    
    def put(self, request, *args, **kwargs):
        updated_by=request.user
        print(updated_by)

        id = self.request.query_params.get('id', None)
        department = request.data['department']
        subject = request.data['subject']
        update_sub_dep = ETICKETSubjectOfDepartment.objects.filter(id = id).update(department=department,
                                                                subject=subject,updated_by=updated_by)


        return Response({'results': request.data,
                             'msg': 'success',
                             "request_status": 1})

class EticketTicketAddView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = ETICKETTicket.objects.all()
    serializer_class = EticketTicketAddSerializer
    filter_backends = (filters.SearchFilter,)

    @response_modify_decorator_post
    def post(self, request, *args, **kwargs):
        response = super().post(request,*args,**kwargs)
        return response

class EticketTicketDocumentAddView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = ETICKETTicketDoc.objects.all()
    serializer_class = EticketTicketDocumentAddSerializer

    @response_modify_decorator_post
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class EticketTicketRaisedByMeListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    pagination_class = OnOffPagination
    queryset = ETICKETTicket.objects.all()
    serializer_class = EticketTicketRaisedByMeListSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = '__all__'
    
    def get_queryset(self):
        current_user = self.request.user
        print('current_user',current_user)
        userid_by_filter = self.request.query_params.get('userId',None)
        print('userid_by_filter',userid_by_filter)
        if userid_by_filter:
            return self.queryset.filter(created_by_id=userid_by_filter)
        else:
            return self.queryset.filter(created_by=current_user)
    
    @response_modify_decorator_list_or_get_before_execution_for_onoff_pagination
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class EticketTicketChangeStatusView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = ETICKETTicket.objects.all()
    serializer_class = EticketTicketChangeStatusSerializer

    @response_modify_decorator_post
    def update(self, request, *args, **kwargs):
        response = super().update(request,*args,**kwargs)
        #print('request.data',self.kwargs)
        ticket_id = self.kwargs['pk']
        print('ticket_id',type(ticket_id))
        ticket_details = ETICKETTicket.objects.get(pk= self.kwargs['pk'])
        print('ticket_details',ticket_details)
        mail_id = ticket_details.created_by.email
        
        # ============= Mail Send ==============#
        if mail_id:
            mail_data = {
                        "name": ticket_details.created_by.first_name+ ' ' +ticket_details.created_by.last_name,
                        "ticket_no": ticket_details.ticket_number,
                        "ticket_sub":ticket_details.subject,
                        "priority":ticket_details.priority,
                        "details": ticket_details.details,
                        "status": ticket_details.status,
                    }
            mail_class = GlobleMailSend('E-T-DEPT-Status', [mail_id])
            mail_thread = Thread(target = mail_class.mailsend, args = (mail_data,))
            mail_thread.start()
        return response

class EticketTicketAssignedToMeListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    pagination_class = OnOffPagination
    queryset = ETICKETTicket.objects.all()
    serializer_class = EticketTicketAssignedToMeListSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = '__all__'

    def get_queryset(self):
        current_user = self.request.user
        print("current_user",current_user)
        userid_by_filter = self.request.query_params.get('userId',None)
        print('current_user',current_user)
        reporting_head_details = ETICKETReportingHead.objects.filter(reporting_head = current_user)
        print('reporting_head_details',reporting_head_details)
        if reporting_head_details:
            reporting_head_details = ETICKETReportingHead.objects.get(reporting_head = current_user)[0]
            print('userid_by_filter',userid_by_filter)
            if userid_by_filter:
                return self.queryset.filter(Q(assigned_to_id=userid_by_filter)|Q(assigned_to_id__in=
            TCoreUserDetail.objects.filter(department=reporting_head_details.department).values_list('cu_user_id',flat=True)))
            else:  
                dept = TCoreDepartment.objects.filter(~Q(cd_parent_id=0),pk=reporting_head_details.department.id)
                if dept:
                    dept = TCoreDepartment.objects.get(~Q(cd_parent_id=0),pk=reporting_head_details.department.id)
                    return self.queryset.filter(
                        assigned_to_id__in=TCoreUserDetail.objects.filter(
                            department=dept.cd_parent_id).values_list('cu_user_id',flat=True))
                else:
                    return self.queryset.filter(
                        assigned_to_id__in=TCoreUserDetail.objects.filter(
                            department=reporting_head_details.department).values_list('cu_user_id',flat=True))

        else:
            #print('userid_by_filter',userid_by_filter)
            if userid_by_filter:
                return self.queryset.filter(Q(assigned_to_id=userid_by_filter)|Q(assigned_to_id__in=
            TCoreUserDetail.objects.filter(hod_id=userid_by_filter).values_list('cu_user_id',flat=True)))
            else:   
                return self.queryset.filter(
                        Q(assigned_to=current_user)|
                        Q(assigned_to__in=TCoreUserDetail.objects.filter(hod=current_user).values_list(
                            'cu_user_id',flat=True)))


    @response_modify_decorator_list_or_get_before_execution_for_onoff_pagination
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class EticketTicketCommentAddView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = ETICKETTicketComment.objects.all()
    serializer_class = EticketTicketCommentAddSerializer

    @response_modify_decorator_post
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class EticketTicketChangePersonResponsibleView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = ETICKETTicket.objects.all()
    serializer_class = EticketTicketChangePersonResponsibleSerializer

    @response_modify_decorator_post
    def update(self, request, *args, **kwargs):

        response = super().update(request,*args,**kwargs)
        assigned_to = request.data['assigned_to']
        assigned_to_details = User.objects.get(
            pk=assigned_to)
        mail_id = assigned_to_details.email
        print('mail_id',mail_id)
        print('datetime',datetime.datetime.now())

        ticket_details = ETICKETTicket.objects.filter(assigned_to=assigned_to).order_by('-id')
        if ticket_details:
            ticket_details = ETICKETTicket.objects.filter(assigned_to=assigned_to).order_by('-id')[0]
        print('ticket_details',ticket_details)
        # ============= Mail Send ==============#
        if mail_id:
            mail_data = {
                        "name": assigned_to_details.first_name+ ' ' +assigned_to_details.last_name,
                        "ticket_no": ticket_details.ticket_number,
                        "ticket_sub":ticket_details.subject,
                        "priority":ticket_details.priority,
                        'details': ticket_details.details
                    }
            mail_class = GlobleMailSend('E-T-DEPT-User', [mail_id])
            mail_thread = Thread(target = mail_class.mailsend, args = (mail_data,))
            mail_thread.start()

        return response

class EticketTicketListByStatusView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    pagination_class = OnOffPagination
    queryset = ETICKETTicket.objects.all()
    serializer_class = EticketTicketRaisedByMeListSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = '__all__'

    def get_queryset(self):
        
        status_details = self.kwargs
        #print('status_details',status_details)
        if status_details['status'].lower() == 're-open':
            return self.queryset.filter(ticket_closed_date__isnull=False,status='Open')
        elif status_details['status'].lower() == 'open':
            return self.queryset.filter(ticket_closed_date__isnull=True,status=status_details['status'])
        else:
            return self.queryset.filter(status=status_details['status'])
    
    @response_modify_decorator_list_or_get_before_execution_for_onoff_pagination
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class EticketTicketSubjectListByDepartmentView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    pagination_class = OnOffPagination
    queryset = ETICKETSubjectOfDepartment.objects.all()
    serializer_class = EticketTicketSubjectListByDepartmentSerializer
    #filter_backends = (filters.SearchFilter,)
    def get_queryset(self):
        department_id = self.kwargs['department_id']
        return self.queryset.filter(department_id=department_id)
    
    @response_modify_decorator_list_or_get_before_execution_for_onoff_pagination
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class EticketUserListUnderLoginUserView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    pagination_class = OnOffPagination

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return self.queryset.filter(is_active=True)
        else:
            user_ids = TCoreUserDetail.objects.filter(
                        hod=user).values_list('cu_user',flat=True)
            if user_ids:
                return self.queryset.filter(pk__in=user_ids)
            else:
                
                is_reporting_head_check = ETICKETReportingHead.objects.filter(reporting_head = user)
                if is_reporting_head_check:
                    is_reporting_head = ETICKETReportingHead.objects.get(reporting_head = user)
                    dept = TCoreDepartment.objects.filter(~Q(cd_parent_id=0),pk=is_reporting_head.department.id)
                    if dept:
                        dept = TCoreDepartment.objects.get(~Q(cd_parent_id=0),pk=is_reporting_head.department.id)
                        user_ids = TCoreUserDetail.objects.filter(
                            department=dept.cd_parent_id).values_list('cu_user',flat=True)
                    else:
                        user_ids = TCoreUserDetail.objects.filter(
                            department=is_reporting_head.department).values_list('cu_user',flat=True)

                    return self.queryset.filter(pk__in=user_ids)
                else:
                    return list()

    @response_modify_decorator_list_or_get_before_execution_for_onoff_pagination
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
 