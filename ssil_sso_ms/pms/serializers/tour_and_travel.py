from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from pms.models import *
from pms.serializers import *
import time
import datetime
from multiplelookupfields import MultipleFieldLookupMixin
from rest_framework.views import APIView
from django.conf import settings
from rest_framework import filters
import calendar
from holidays.models import *
import collections
from rest_framework.exceptions import APIException
from django_filters.rest_framework import DjangoFilterBackend
from master.serializers import UserModuleWiseListSerializer
from master.models import TMasterModuleRole
from users.models import TCoreUserDetail
from custom_decorator import *
import os
from pms.custom_filter import *
from decimal import *


class TourAndTravelExpenseAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    travel_stage_status=serializers.CharField(default=2)
    daily_expenses=serializers.ListField(required=False)
    vendor_or_employee_details=serializers.ListField(required=False)
    bill_received=serializers.ListField(required=False)
    flight_booking_quotations=serializers.ListField(required=False)
    final_booking_details=serializers.ListField(required=False)
    employee_name=serializers.SerializerMethodField(required=False)
    def get_employee_name(self,PmsTourAndTravelExpenseMaster):
        if PmsTourAndTravelExpenseMaster.employee: 
            emp_name = User.objects.filter(id=PmsTourAndTravelExpenseMaster.employee.id)
            for e_n in emp_name:
                first_name=e_n.first_name
                last_name=e_n.last_name
                full_name=first_name+""+last_name
            return full_name
      
    class Meta:
        model = PmsTourAndTravelExpenseMaster
        fields = '__all__'
        extra_fields=('daily_expenses','vendor_or_employee_details','bill_received','flight_booking_quotations','final_booking_details','employee_name')

    def create(self, validated_data):
        try:
            daily_expenses=validated_data.pop('daily_expenses') if 'daily_expenses' in validated_data else ""
            vendor_or_employee_details=validated_data.pop('vendor_or_employee_details') if 'vendor_or_employee_details' in validated_data else ""
            bill_received=validated_data.pop('bill_received')if 'bill_received' in validated_data else ""
            flight_booking_quotations=validated_data.pop('flight_booking_quotations')if 'flight_booking_quotations' in validated_data else ""
            final_booking_details=validated_data.pop('final_booking_details')if 'final_booking_details' in validated_data else ""
            owned_by = validated_data.get('owned_by')
            created_by = validated_data.get('created_by')
            daily_ex_list=[]
            v_e_details_list=[]
            bill_received_list=[]
            flight_booking_quotations_list=[]
            final_booking_details_list=[]
            with transaction.atomic():
                travel_master,created=PmsTourAndTravelExpenseMaster.objects.get_or_create(**validated_data)
                # print('travel_master',travel_master)
                all_other_expenses= Decimal(0.0)
                all_limit_exc_by =  Decimal(0.0)
                all_expense = Decimal(0.0)
                all_flight_fare = Decimal(0.0)
                all_total_cost = Decimal(0.0)
                all_total = Decimal(0.0)
                all_advance_amount = Decimal(0.0)
                for d_e in daily_expenses:
                    all_other_expenses += Decimal(d_e['other_expenses'])
                    daily_ex_data,created=PmsTourAndTravelEmployeeDailyExpenses.objects.get_or_create(expenses_master=travel_master,
                                                                                                    date=datetime.datetime.strptime(d_e['date'], "%Y-%m-%dT%H:%M:%S.%fZ"),
                                                                                                    description=d_e['description'],
                                                                                                    fare=d_e['fare'],
                                                                                                    local_conveyance=d_e['local_conveyance'],
                                                                                                    lodging_expenses=d_e['lodging_expenses'],
                                                                                                    fooding_expenses=d_e['fooding_expenses'],
                                                                                                    da=d_e['da'],
                                                                                                    other_expenses=d_e['other_expenses'],
                                                                                                    created_by=created_by,
                                                                                                    owned_by=owned_by,    
                                                                                                    )
                    daily_ex_data.__dict__.pop('_state') if "_state" in daily_ex_data.__dict__.keys() else daily_ex_data.__dict__
                    # print('daily_ex_data',daily_ex_data)
                    daily_ex_list.append(daily_ex_data.__dict__)
                print('all_other_expenses',all_other_expenses)
                
                for v_e in vendor_or_employee_details:
                    vendor_or_emp_data,created=PmsTourAndTravelVendorOrEmployeeDetails.objects.get_or_create(expenses_master=travel_master,
                                                                                                    **v_e,
                                                                                                    created_by=created_by,
                                                                                                    owned_by=owned_by
                                                                                                        )  
                    # print('vendor_or_emp_data',vendor_or_emp_data)
                    vendor_or_emp_data.__dict__.pop('_state') if '_state' in  vendor_or_emp_data.__dict__.keys() else vendor_or_emp_data.__dict__
                    v_e_details_list.append(vendor_or_emp_data.__dict__)

                
               
                for b_r in bill_received:
                    all_limit_exc_by += Decimal(b_r['limit_exceeded_by'])
                    all_expense +=Decimal(b_r['total_expense'])
                    all_advance_amount += Decimal(b_r['advance_amount'])
                    bill_received_data,created=PmsTourAndTravelBillReceived.objects.get_or_create(expenses_master=travel_master,
                                                                                                    date=datetime.datetime.strptime(b_r['date'], "%Y-%m-%dT%H:%M:%S.%fZ"),
                                                                                                    parking_expense=b_r['parking_expense'],
                                                                                                    posting_expense=b_r['posting_expense'],
                                                                                                    employee_or_vendor_type=b_r['employee_or_vendor_type'],
                                                                                                    empolyee_or_vendor_id=b_r['empolyee_or_vendor_id'],
                                                                                                    less_amount=b_r['less_amount'],
                                                                                                    cgst=b_r['cgst'],
                                                                                                    sgst=b_r['sgst'],
                                                                                                    igst=b_r['igst'],
                                                                                                    document_number=b_r['document_number'],
                                                                                                    net_expenditure=b_r['net_expenditure'],
                                                                                                    advance_amount=b_r['advance_amount'],
                                                                                                    fare_and_conveyance=b_r['fare_and_conveyance'],
                                                                                                    lodging_fooding_and_da=b_r['lodging_fooding_and_da'],
                                                                                                    expense_mans_per_day=b_r['expense_mans_per_day'],
                                                                                                    total_expense=b_r['total_expense'],
                                                                                                    limit_exceeded_by=b_r['limit_exceeded_by'],
                                                                                                    remarks=b_r['remarks'],
                                                                                                    created_by=created_by,
                                                                                                    owned_by=owned_by)
                    # print('bill_received_data',bill_received_data)
                    bill_received_data.__dict__.pop('_state') if '_state' in bill_received_data.__dict__.keys() else bill_received_data.__dict__


                    bill_received_list.append(bill_received_data.__dict__)
                # print('all_limit_exc_by',all_limit_exc_by)
                # print('all_expense',all_expense)
                

                for f_b in flight_booking_quotations:
                    all_flight_fare += Decimal(f_b['airline_fare'])
                    flight_booking_data,created=PmsTourAndTravelWorkSheetFlightBookingQuotation.objects.get_or_create(expenses_master=travel_master,
                                                                                                    **f_b,
                                                                                                    created_by=created_by,
                                                                                                    owned_by=owned_by)
                    # print('flight_booking_data',flight_booking_data)
                    flight_booking_data.__dict__.pop('_state') if '_state' in  flight_booking_data.__dict__.keys() else flight_booking_data.__dict__
                    flight_booking_quotations_list.append(flight_booking_data.__dict__)
                # print('all_flight_fare',all_flight_fare)

                for f_b_d in final_booking_details:
                    all_total_cost += Decimal(f_b_d['total_cost'])
                    final_booking_data,created=PmsTourAndTravelFinalBookingDetails.objects.get_or_create(expenses_master=travel_master,
                                                                                                    **f_b_d,
                                                                                                    created_by=created_by,
                                                                                                    owned_by=owned_by   )  
                    # print('final_booking_data',final_booking_data)     
                    final_booking_data.__dict__.pop('_state') if '_state' in  final_booking_data.__dict__.keys() else final_booking_data.__dict__  
                    final_booking_details_list.append(final_booking_data.__dict__)
                # print('all_total_cost',all_total_cost)

                all_total = all_other_expenses + all_expense + all_total_cost
                # print('all_total',all_total)
                travel_master.__dict__['total_expense']= all_total
                travel_master.__dict__['limit_exceed_by']= all_limit_exc_by
                travel_master.__dict__['total_flight_fare']= all_flight_fare
                travel_master.__dict__['advance']= all_advance_amount
                travel_master.save()

                travel_master.__dict__['daily_expenses']=daily_ex_list
                travel_master.__dict__['vendor_or_employee_details']=v_e_details_list
                travel_master.__dict__['bill_received']=bill_received_list
                travel_master.__dict__['flight_booking_quotations']= flight_booking_quotations_list 
                travel_master.__dict__['final_booking_details']=final_booking_details_list

                return travel_master

        except Exception as e:
            raise e
            # raise APIException({'request_status': 0,
            #                     'error': e,
            #                     'msg': settings.MSG_ERROR})
class TourAndTravelVendorOrEmployeeDetailsApprovalSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    # request_modification=serializers.CharField(required=False)

    class Meta:
        model = PmsTourAndTravelVendorOrEmployeeDetails
        fields = ('id','expenses_master','approved_status','request_modification', 'updated_by')

    def create(self,validated_data):
        try:
            
            with transaction.atomic():
                response_list=[]
                # vendor_or_emp_approval={}
                exist_vendor_or_emp_approval=PmsTourAndTravelVendorOrEmployeeDetails.objects.filter(expenses_master=validated_data.get('expenses_master'))

                if exist_vendor_or_emp_approval:
                    
                    for e_exist_vendor_or_emp_approval in exist_vendor_or_emp_approval:
                        e_exist_vendor_or_emp_approval.approved_status=validated_data.get('approved_status')
                        e_exist_vendor_or_emp_approval.request_modification=validated_data.get('request_modification')
                        e_exist_vendor_or_emp_approval.updated_by=validated_data.get('updated_by')
                        e_exist_vendor_or_emp_approval.save()

                        vendor_or_emp_approval= {
                        'id': e_exist_vendor_or_emp_approval.id,
                        'expenses_master': e_exist_vendor_or_emp_approval.expenses_master.id,
                        'approved_status': e_exist_vendor_or_emp_approval.approved_status,
                        'request_modification': e_exist_vendor_or_emp_approval.request_modification,
                        'updated_by': e_exist_vendor_or_emp_approval.updated_by
                        }
                        # print('vendor_or_emp_approval',vendor_or_emp_approval)
                        response_list.append(vendor_or_emp_approval)
                    
                    return validated_data 
        except Exception as e:
            raise e 
class TourAndTravelBillReceivedApprovalSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    # request_modification=serializers.CharField(required=False)
    class Meta:
        model = PmsTourAndTravelBillReceived
        fields = ('id','expenses_master','approved_status','request_modification','updated_by')
    def create(self,validated_data):
        try:
           
            with transaction.atomic():
                response_list=[]
                exist_bill_received=PmsTourAndTravelBillReceived.objects.filter(expenses_master=validated_data.get('expenses_master'))
                if exist_bill_received:
                    for e_exist_bill_received in exist_bill_received:
                        e_exist_bill_received.approved_status=validated_data.get('approved_status')
                        e_exist_bill_received.request_modification=validated_data.get('request_modification')
                        e_exist_bill_received.updated_by=validated_data.get('updated_by')
                        e_exist_bill_received.save()


                        bill_received_approval={
                            'id': e_exist_bill_received.id,
                            'expenses_master': e_exist_bill_received.expenses_master.id,
                            'approved_status': e_exist_bill_received.approved_status,
                            'request_modification': e_exist_bill_received.request_modification,
                            'updated_by': e_exist_bill_received.updated_by
                            }
                        response_list.append(bill_received_approval)

                    return validated_data
            
        except Exception as e:
            raise e
class TourAndTravelFinalBookingDetailsApprovalSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    # request_modification=serializers.CharField(required=False)
    class Meta:
        model = PmsTourAndTravelFinalBookingDetails
        fields = ('id','expenses_master','approved_status','request_modification','updated_by')
    def create(self,validated_data):
        try:
            response_list=[]
            with transaction.atomic():
                exist_final_booking_details=PmsTourAndTravelFinalBookingDetails.objects.filter(expenses_master=validated_data.get('expenses_master'))
                if exist_final_booking_details:
                    for e_exist_final_booking_details in exist_final_booking_details:
                        e_exist_final_booking_details.approved_status=validated_data.get('approved_status')
                        e_exist_final_booking_details.request_modification=validated_data.get('request_modification')
                        e_exist_final_booking_details.updated_by=validated_data.get('updated_by')
                        e_exist_final_booking_details.save()

                        final_booking_approval={
                            'id': e_exist_final_booking_details.id,
                            'expenses_master': e_exist_final_booking_details.expenses_master.id,
                            'approved_status': e_exist_final_booking_details.approved_status,
                            'request_modification': e_exist_final_booking_details.request_modification,
                            'updated_by':e_exist_final_booking_details.updated_by
                            }
                        response_list.append(final_booking_approval)
                return validated_data
        except Exception as e:
            raise e

class TourAndTravelExpenseMasterApprovalSerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    # request_modification=serializers.CharField(required=False)
    class Meta:
        model = PmsTourAndTravelExpenseMaster
        fields =('id','approved_status','request_modification','updated_by')
    

class TourAndTravelExpenseApprovalListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PmsTourAndTravelExpenseMaster
        fields = ('id','user_type','employee','guest','place_of_travel','total_expense','limit_exceed_by','total_flight_fare','advance','from_date','to_date','approved_status')

