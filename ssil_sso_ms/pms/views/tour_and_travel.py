from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from pms.models import *
from pms.serializers import *
from django.conf import settings
from pagination import *
from rest_framework import filters
from datetime import datetime,timedelta
import collections
from rest_framework.exceptions import APIException
from django_filters.rest_framework import DjangoFilterBackend
from master.serializers import UserModuleWiseListSerializer
from master.models import TMasterModuleRole
from users.models import TCoreUserDetail
from custom_decorator import *
from rest_framework.parsers import FileUploadParser
import os
from pms.custom_filter import *
from custom_decorator import *
from decimal import *
from django.db.models import Q
from global_function import userdetails
class TourAndTravelExpenseAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsTourAndTravelExpenseMaster.objects.filter(is_deleted=False)
    serializer_class = TourAndTravelExpenseAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('employee','guest','id')
    @response_modify_decorator_get_after_execution
    def get(self, request, *args, **kwargs):
        response=super(TourAndTravelExpenseAddView,self).get(self, request, args, kwargs)
        # print('response',response.data)
        for data in response.data:
            # print('dd',data['id'])
            daily_expenses=PmsTourAndTravelEmployeeDailyExpenses.objects.filter(expenses_master=data['id'],is_deleted=False)
            daily_expenses_list=[]
            for d_e in daily_expenses:
                daily_travel={
                    'id':d_e.id,
                    'date':d_e.date,
                    'description':d_e.description,
                    'fare':d_e.fare,
                    'local_conveyance':d_e.local_conveyance,
                    'lodging_expenses':d_e.lodging_expenses,
                    'fooding_expenses':d_e.fooding_expenses,
                    'da':d_e.da,
                    'other_expenses':d_e.other_expenses
                }
                daily_expenses_list.append(daily_travel)
            data['daily_expenses']=daily_expenses_list
            vendor_or_emp_det=PmsTourAndTravelVendorOrEmployeeDetails.objects.filter(expenses_master=data['id'],is_deleted=False)
            emp_det_list=[]

            for e_d in vendor_or_emp_det:
                if e_d.employee_or_vendor_type ==1:
                    name = PmsExternalUsers.objects.only('contact_person_name').get(id=e_d.empolyee_or_vendor_id).contact_person_name
                    # print("e_d.employee_or_vendor_type ==1",name)
                elif e_d.employee_or_vendor_type == 2:
                    # user_name = User.objects.filter(id=e_d.empolyee_or_vendor_id).values('first_name','last_name')
                    # print("elif e_d.employee_or_vendor_type == 2:", user_name)
                    # name=user_name[0]['first_name']+" "+user_name[0]['last_name']
                    name=userdetails(e_d.empolyee_or_vendor_id)
                    print('name',name)
                employee_details={
                    'id':e_d.id,
                    'bill_number':e_d.bill_number,
                    'employee_or_vendor_type':e_d.employee_or_vendor_type,
                    'empolyee_or_vendor_id':e_d.empolyee_or_vendor_id,
                    'bill_amount':e_d.bill_amount,
                    'advance_amount':e_d.advance_amount,
                    'empolyee_or_vendor_name':name
                }
               
                emp_det_list.append(employee_details)
            data['vendor_or_employee_details']=emp_det_list
            bill_received=PmsTourAndTravelBillReceived.objects.filter(expenses_master=data['id'],is_deleted=False)
            bill_received_list=[]
            for b_r in bill_received:
                if b_r.employee_or_vendor_type ==1:
                    name = PmsExternalUsers.objects.only('contact_person_name').get(id=b_r.empolyee_or_vendor_id).contact_person_name
                   
                elif b_r.employee_or_vendor_type == 2:
                    # user_name = User.objects.filter(id=b_r.empolyee_or_vendor_id).values('first_name','last_name')
                    # name=user_name[0]['first_name']+" "+user_name[0]['last_name']
                    name=userdetails(b_r.empolyee_or_vendor_id)

                bill_details={
                    'id':b_r.id,
                    'date':b_r.date,
                    'parking_expense':b_r.parking_expense,
                    'posting_expense':b_r.posting_expense,
                    'employee_or_vendor_type':b_r.employee_or_vendor_type,
                    'empolyee_or_vendor_id':b_r.empolyee_or_vendor_id,
                    'empolyee_or_vendor_name':name,
                    'less_amount':b_r.less_amount,
                    'cgst':b_r.cgst,
                    'sgst':b_r.sgst,
                    'igst':b_r.igst,
                    'document_number':b_r.document_number,
                    'cost_center_number':b_r.cost_center_number,
                    'net_expenditure':b_r.net_expenditure,
                    'advance_amount':b_r.advance_amount,
                    'fare_and_conveyance':b_r.fare_and_conveyance,
                    'lodging_fooding_and_da':b_r.lodging_fooding_and_da,
                    'expense_mans_per_day':b_r.expense_mans_per_day,
                    'total_expense':b_r.total_expense,
                    'limit_exceeded_by':b_r.limit_exceeded_by,
                    'remarks':b_r.remarks
                }
                bill_received_list.append(bill_details)
            data['bill_received']=bill_received_list
            flight_booking=PmsTourAndTravelWorkSheetFlightBookingQuotation.objects.filter(expenses_master=data['id'],is_deleted=False)
            flight_booking_list=[]
            for f_b in flight_booking:
                flight_booking_details={
                    'id':f_b.id,
                    'flight_booking_quotation_type':f_b.flight_booking_quotation_type,
                    'date':f_b.date,
                    'sector':f_b.sector,
                    'airline':f_b.airline,
                    'flight_number':f_b.flight_number,
                    'time':f_b.time,
                    'corporate_fare_agent_1':f_b.corporate_fare_agent_1,
                    'corporate_fare_agent_2':f_b.corporate_fare_agent_2,
                    'retail_fare_agent_1':f_b.retail_fare_agent_1,
                    'retail_fare_agent_2':f_b.retail_fare_agent_2,
                    'airline_fare':f_b.airline_fare,
                    'others':f_b.others
                }
                flight_booking_list.append(flight_booking_details)
            data['flight_booking_quotation']=flight_booking_list
            final_booking_details=PmsTourAndTravelFinalBookingDetails.objects.filter(expenses_master=data['id'],is_deleted=False)
            final_booking_list=[]
            for f_b_d in final_booking_details:
                if f_b_d.employee_or_vendor_type ==1:
                    name = PmsExternalUsers.objects.only('contact_person_name').get(id=f_b_d.empolyee_or_vendor_id).contact_person_name
                   
                elif f_b_d.employee_or_vendor_type == 2:
                    # user_name = User.objects.filter(id=f_b_d.empolyee_or_vendor_id).values('first_name','last_name')
                    # name=user_name[0]['first_name']+" "+user_name[0]['last_name']
                    name=userdetails(f_b_d.empolyee_or_vendor_id)

                final_booking={
                    'id':f_b_d.id,
                    'employee_or_vendor_type':f_b_d.employee_or_vendor_type,
                    'empolyee_or_vendor_id':f_b_d.empolyee_or_vendor_id,
                    'empolyee_or_vendor_name':name,
                    'date_of_journey':f_b_d.date_of_journey,
                    'time':f_b_d.time,
                    'flight_no':f_b_d.flight_no,
                    'travel_sector':f_b_d.travel_sector,
                    'number_of_persons':f_b_d.number_of_persons,
                    'rate_per_person':f_b_d.rate_per_person,
                    'total_cost':f_b_d.total_cost
                }
                final_booking_list.append(final_booking)
            data['final_booking_details']=final_booking_list
                
        return response    

class TourAndTravelVendorOrEmployeeDetailsApprovalView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsTourAndTravelVendorOrEmployeeDetails.objects.filter(is_deleted=False)
    serializer_class = TourAndTravelVendorOrEmployeeDetailsApprovalSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('expenses_master','employee_or_vendor_type')
    # @response_modify_decorator_get
    @response_modify_decorator_get_after_execution
    def get(self, request, *args, **kwargs):
        response=super(TourAndTravelVendorOrEmployeeDetailsApprovalView,self).get(self, request, args, kwargs)
        response_dict={}

        if response.data:
           
            response.data=response.data[0]
            response_dict={
                'expenses_master':response.data['expenses_master'],
                'approved_status':response.data['approved_status'],
                'request_modification':response.data['request_modification'],
                'updated_by':response.data['updated_by']

            }
        
        return Response(response_dict)

class TourAndTravelBillReceivedApprovalView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsTourAndTravelBillReceived.objects.filter(is_deleted=False)
    serializer_class = TourAndTravelBillReceivedApprovalSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('expenses_master','employee_or_vendor_type')
    @response_modify_decorator_get_after_execution
    def get(self, request, *args, **kwargs):
        response=super(TourAndTravelBillReceivedApprovalView,self).get(self, request, args, kwargs)
        response_dict={}

        if response.data:
           
            response.data=response.data[0]
            response_dict={
                'expenses_master':response.data['expenses_master'],
                'approved_status':response.data['approved_status'],
                'request_modification':response.data['request_modification'],
                'updated_by':response.data['updated_by']

            }
        
        return Response(response_dict)
class TourAndTravelFinalBookingDetailsApprovalView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsTourAndTravelFinalBookingDetails.objects.filter(is_deleted=False)
    serializer_class =TourAndTravelFinalBookingDetailsApprovalSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('expenses_master','employee_or_vendor_type')
    @response_modify_decorator_get_after_execution
    def get(self, request, *args, **kwargs):
        response=super(TourAndTravelFinalBookingDetailsApprovalView,self).get(self, request, args, kwargs)
        response_dict={}

        if response.data:
           
            response.data=response.data[0]
            response_dict={
                'expenses_master':response.data['expenses_master'],
                'approved_status':response.data['approved_status'],
                'request_modification':response.data['request_modification'],
                'updated_by':response.data['updated_by']

            }
        
        return Response(response_dict)

class TourAndTravelExpenseMasterApprovalView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsTourAndTravelExpenseMaster.objects.filter(is_deleted=False)
    serializer_class =TourAndTravelExpenseMasterApprovalSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('user_type',)
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response

class TourAndTravelExpenseApprovalList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    pagination_class = CSPageNumberPagination
    queryset = PmsTourAndTravelExpenseMaster.objects.filter(is_deleted=False).order_by('-id')
    serializer_class = TourAndTravelExpenseApprovalListSerializer

    def get_queryset(self):
        filter = {}
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        from_expense_range=self.request.query_params.get('from_expense_range', None)
        expense_range_to=self.request.query_params.get('expense_range_to', None)
        from_limit_exceeded_range=self.request.query_params.get('from_limit_exceeded_range', None)
        limit_exceeded_range_to=self.request.query_params.get('limit_exceeded_range_to', None)
        search=self.request.query_params.get('search', None)

        field_name=self.request.query_params.get('field_name',None)
        order_by=self.request.query_params.get('order_by',None)

        if field_name and order_by:
            if field_name == 'from_date' and order_by == 'asc':
                return self.queryset.filter(is_deleted=False).order_by('from_date')
            elif field_name == 'from_date' and order_by == 'desc':
                return self.queryset.filter(is_deleted=False).order_by('-from_date')
            elif field_name == 'to_date' and order_by == 'asc':
                return self.queryset.filter(is_deleted=False).order_by('to_date')
            elif field_name == 'to_date' and order_by == 'desc':
                return self.queryset.filter(is_deleted=False).order_by('-to_date')
            elif field_name == 'total_expense' and order_by == 'asc':
                return self.queryset.filter(is_deleted=False).order_by('total_expense')
            elif field_name == 'total_expense' and order_by == 'desc':
                return self.queryset.filter(is_deleted=False).order_by('-total_expense')
            elif field_name == 'limit_exceed_by' and order_by == 'asc':
                return self.queryset.filter(is_deleted=False).order_by('limit_exceed_by')
            elif field_name == 'limit_exceed_by' and order_by == 'desc':
                return self.queryset.filter(is_deleted=False).order_by('-limit_exceed_by')
            elif field_name == 'total_flight_fare' and order_by == 'asc':
                return self.queryset.filter(is_deleted=False).order_by('total_flight_fare')
            elif field_name == 'total_flight_fare' and order_by == 'desc':
                return self.queryset.filter(is_deleted=False).order_by('-total_flight_fare')
            elif field_name == 'advance' and order_by == 'asc':
                return self.queryset.filter(is_deleted=False).order_by('advance')
            elif field_name == 'advance' and order_by == 'desc':
                return self.queryset.filter(is_deleted=False).order_by('-advance')

        if start_date and end_date :
            start_object = datetime.strptime(start_date, '%Y-%m-%d').date()
            filter['from_date__gte'] = start_object
            end_object = datetime.strptime(end_date, '%Y-%m-%d').date()+ timedelta(days=1)
            filter['to_date__lte'] = end_object    
          
        if from_expense_range and expense_range_to:
            filter['total_expense__range']=(from_expense_range,expense_range_to)

        if from_limit_exceeded_range and limit_exceeded_range_to:
            filter['limit_exceed_by__range']=(from_limit_exceeded_range,limit_exceeded_range_to)

        if search:
            queryset_all = PmsTourAndTravelExpenseMaster.objects.none()
            g_query=self.queryset.filter(guest__icontains=search,is_deleted=False)
            queryset_all=(queryset_all|g_query)
            name=search.split(" ")
            # print('name',name)                                                                                                                                                                                                                                                                            
            if name:
                for i in name:
                    queryset = self.queryset.filter(Q(is_deleted=False) & Q(employee__first_name__icontains=i) |
                                                    Q(employee__last_name__icontains=i)).order_by('-id')
                    queryset_all = (queryset_all|queryset)

            return queryset_all

        if filter:
            queryset = self.queryset.filter(**filter)
            # print('queryset',queryset)
            return queryset

        else:
            queryset = self.queryset.filter(is_deleted=False)
            return queryset
    
    def get(self, request, *args, **kwargs):
        response = super(TourAndTravelExpenseApprovalList, self).get(self, request, args, kwargs)
        # print("response.data",response.data)
        for data in response.data['results']:   
            if data['employee'] and data['user_type'] == 1:
                first_name = User.objects.only('first_name').get(id=data['employee']).first_name
                last_name = User.objects.only('last_name').get(id=data['employee']).last_name
                data['name'] = {
                    'id': data['employee'],
                    'name' : str(first_name) + " " + str(last_name)
                }
            if data['user_type'] == 2:
                data['name'] = {
                    'id': "",
                    'name' : data['guest']
                }        
        if response.data['count'] > 0:
            response.data['request_status'] = 0
            response.data['msg'] = settings.MSG_SUCCESS
        else:
            response.data['request_status'] = 1
            response.data['msg'] = settings.MSG_NO_DATA

        return response


