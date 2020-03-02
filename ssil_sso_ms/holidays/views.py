from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from attendance.models import *
from holidays.serializers import *
from holidays.models import *
# from vms.vms_pagination import CSLimitOffestpagination,CSPageNumberVmsPagination
from rest_framework.views import APIView
from django.conf import settings
from rest_framework import filters
from datetime import datetime,timedelta,date
import collections
from rest_framework.exceptions import APIException
from rest_framework import mixins
from master.serializers import UserModuleWiseListSerializer
from master.models import TMasterModuleRole
from users.models import TCoreUserDetail
from django.db.models import Sum
from custom_decorator import *
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
import calendar
import pandas as pd
import numpy as np
import xlrd
from custom_decorator import *
from pagination import CSLimitOffestpagination,CSPageNumberPagination
from hrms.models import *
from datetime import datetime
from rest_framework.parsers import MultiPartParser
from django.core.files.storage import FileSystemStorage
import shutil
import platform
import re
from django.db.models import When, Case, Value, CharField, IntegerField, F, Q
from collections import defaultdict
import itertools




#:::::::::::::::::::::: HOLIDAYS LIST:::::::::::::::::::::::::::#
class HolidaysListAddView(generics.ListCreateAPIView):
	permission_classes = [IsAuthenticated]
	authentication_classes = [TokenAuthentication]
	queryset = HolidaysList.objects.filter(is_deleted=False,holiday_date__year='2020')
	serializer_class = HolidaysListAddSerializer
	@response_modify_decorator_get
	def get(self, request, *args, **kwargs):
		return response

class HolidaysListEditView(generics.RetrieveUpdateAPIView):
	permission_classes = [IsAuthenticated]
	authentication_classes = [TokenAuthentication]
	queryset = HolidaysList.objects.filter(is_deleted=False)
	serializer_class = HolidaysListEditSerializer


class HolidaysListDeleteView(generics.RetrieveUpdateAPIView):
	permission_classes = [IsAuthenticated]
	authentication_classes = [TokenAuthentication]
	queryset = HolidaysList.objects.filter(is_deleted=False)
	serializer_class = HolidaysListDeleteSerializer


class HolidaysListStateWiseViewOld(generics.ListAPIView):
	permission_classes = [IsAuthenticated]
	authentication_classes = [TokenAuthentication]
	queryset = HolidaysList.objects.filter(is_deleted=False)
	serializer_class = HolidaysListStateWiseSerializerOld

	def get(self, request, *args, **kwargs):
		search=self.request.query_params.get('search', None)

		print('search-->',search)


		data = {}		
		data_dict = {}
		list_of_data = []

		get_holiday_list = HolidaysList.objects.filter(Q(is_deleted=False)&
														 (Q(state_name__cs_state_code__icontains=search)|
														  Q(state_name__cs_state_name__icontains=search)|
														  Q(state_name__cs_tin_number__icontains=search))&
													   Q(status=True))

		print('get_holiday_list-->',get_holiday_list)

		for h_list in get_holiday_list:
			data = {
				'holiday_name' : h_list.holiday_name,
				'holiday_date' : h_list.holiday_date,
				'status' : h_list.status,
				'state_name' : h_list.state_name.cs_state_name
			}	
			# print('data-->',data)
			list_of_data.append(data)

		print('list_of_data-->',list_of_data)
		
		
		data_dict['result'] = list_of_data
		if list_of_data:
			data_dict['request_status'] = 1
			data_dict['msg'] = settings.MSG_SUCCESS
		elif len(list_of_data) == 0:
			data_dict['request_status'] = 1
			data_dict['msg'] = settings.MSG_NO_DATA
		else:
			data_dict['request_status'] = 0
			data_dict['msg'] = settings.MSG_ERROR
		return Response(data_dict)


class HolidaysStateWiseListAddView(generics.ListCreateAPIView):
	permission_classes = [IsAuthenticated]
	authentication_classes = [TokenAuthentication]
	queryset = HolidayStateMapping.objects.filter(is_deleted=False).order_by('holiday__holiday_date')
	
	@response_with_status
	def get(self, request, *args, **kwargs):
		'''
		For all holiday list :: http://127.0.0.1:8001/holidays_list_state_wise/?year=2020
		For a perticular State :: http://127.0.0.1:8001/holidays_list_state_wise/?state=<state_id>&year=2020
		'''
		data = list()
		state_id=self.request.query_params.get('state', None)
		year=self.request.query_params.get('year', None)
		queryset = self.get_queryset()
		all_states_set = set(TCoreState.objects.filter(
				Q(cs_status=True)&
				Q(cs_is_deleted=False)
			).values_list('id', flat=True))
		if not state_id:
			queryset = queryset.filter(
				Q(holiday__is_deleted=False)&
				Q(holiday__status=True)&
				Q(holiday__holiday_date__year=year))
			serializer = HolidaysListStateWiseSerializer(queryset, many=True)
			grouped = collections.defaultdict(list)
			for item in serializer.data:
				grouped[item['holiday_id']].append({'state_id':item['state_id'],'cs_state_name':item['cs_state_name']})
			
			for holiday in HolidaysList.objects.filter(Q(status=True)&Q(is_deleted=False)&Q(holiday_date__year=year)).order_by('holiday_date'):
				selected_state_id_set = set([item['state_id'] for item in grouped[holiday.id]])
				is_all_state = all_states_set == selected_state_id_set
				data.append({
					'id': holiday.id,
					'holiday_name': holiday.holiday_name,
					'holiday_date': holiday.holiday_date,
					'is_all_state': is_all_state,
					'states': grouped[holiday.id]
				})
		else:
			queryset = queryset.filter(
				Q(holiday__is_deleted=False)&
				Q(holiday__status=True)&
				Q(holiday__holiday_date__year=year)&
				Q(state__id=int(state_id)))
			serializer = HolidaysListStateWiseSerializer(queryset, many=True)
			for holiday in serializer.data:
				data.append({
					'id': holiday['holiday_id'],
					'holiday_name': holiday['holiday_name'],
					'holiday_date': holiday['holiday_date'],
					'states': [{"cs_state_name": holiday['cs_state_name'], "state_id": holiday['state_id']}]
				})
		return data

	@response_with_status
	def post(self, request, *args, **kwargs):
		data = list()
		serializer = StateWiseHolidaysAddSerializer(data=request.data)
		if serializer.is_valid():
			states = serializer.validated_data.get('states')
			holiday_name = serializer.validated_data.get('holiday_name')
			holiday_date = serializer.validated_data.get('holiday_date')

			holiday, isCreated = HolidaysList.objects.get_or_create(holiday_name=holiday_name,holiday_date=holiday_date)
			if isCreated:
				holiday.created_by = request.user
				holiday.owned_by = request.user
			else:
				holiday.is_deleted = False
				holiday.status = True
			holiday.save()

			for state_id in states:
				state_obj = TCoreState.objects.get(id=int(state_id))
				shm_obj, isCreated = HolidayStateMapping.objects.get_or_create(holiday=holiday,state=state_obj)
				if isCreated:
					shm_obj.created_by = request.user
					shm_obj.owned_by = request.user
				else:
					shm_obj.is_deleted = False
				shm_obj.save()

				data.append({
					'id': shm_obj.id,
					'holiday': shm_obj.holiday.holiday_name,
					'state': shm_obj.state.cs_state_name
				})

		return data


class StateWiseHolidaysDeleteView(generics.RetrieveUpdateAPIView):
	permission_classes = [IsAuthenticated]
	authentication_classes = [TokenAuthentication]
	queryset = HolidayStateMapping.objects.filter(is_deleted=False)
	serializer_class = StateWiseHolidaysDeleteSerializer

	@response_modify_decorator_update
	def patch(self,request,*args,**kwargs):
		return super(self.__class__,self).patch(request,*args,**kwargs)


class StateWiseHolidaysEditView(generics.RetrieveUpdateAPIView):
	permission_classes = [IsAuthenticated]
	authentication_classes = [TokenAuthentication]
	queryset = HolidaysList.objects.filter(is_deleted=False)
	serializer_class = HolidaysListEditSerializer

	@response_with_status
	def get(self, request, *args, **kwargs):
		data = dict()
		holiday_obj = self.get_object()
		holiday_state = HolidayStateMapping.objects.filter(is_deleted=False).filter(
			Q(holiday=holiday_obj)&
			Q(holiday__is_deleted=False)&
			Q(holiday__status=True)&
			Q(holiday__holiday_date__year=holiday_obj.holiday_date.year)).values('state__id', 'state__cs_state_name')
		data['id'] = holiday_obj.id
		data['holiday_name'] = holiday_obj.holiday_name
		data['holiday_date'] = holiday_obj.holiday_date
		data['states'] = holiday_state
		return data

	@response_with_status
	def patch(self,request,*args,**kwargs):
		data = list()
		serializer = StateWiseHolidaysAddSerializer(data=request.data)
		if serializer.is_valid():
			states = serializer.validated_data.get('states')
			holiday_name = serializer.validated_data.get('holiday_name')
			holiday_date = serializer.validated_data.get('holiday_date')

			holiday = self.get_object()
			holiday.holiday_name = holiday_name
			holiday.holiday_date = holiday_date
			holiday.save()
			HolidayStateMapping.objects.filter(holiday=holiday).delete()
			for state_id in states:
				state_obj = TCoreState.objects.get(id=int(state_id))
				shm_obj, isCreated = HolidayStateMapping.objects.get_or_create(holiday=holiday,state=state_obj)
				if isCreated:
					shm_obj.created_by = request.user
					shm_obj.owned_by = request.user
				else:
					shm_obj.is_deleted = False
				shm_obj.save()

				data.append({
					'id': shm_obj.id,
					'holiday': shm_obj.holiday.holiday_name,
					'state': shm_obj.state.cs_state_name
				})

		return data





class PDFTestView(APIView):
	permission_classes = [IsAuthenticated]
	authentication_classes = [TokenAuthentication]

	def get(self, request, *args, **kwargs):
		import time
		from reportlab.lib.enums import TA_JUSTIFY
		from reportlab.lib.pagesizes import letter
		from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, tables
		from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
		from reportlab.lib.units import inch
		from reportlab.lib import colors

		doc = SimpleDocTemplate("test.pdf",pagesize=letter,
								rightMargin=30,leftMargin=30,
								topMargin=20,bottomMargin=20)
		Story=[]

		# styles=getSampleStyleSheet()
		# styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
		# ptext = '<font size="18">%s</font>' % 'Purchase Requisition:'
		# Story.append(Paragraph(ptext, styles["Normal"]))
		# Story.append(Spacer(1, 12))
		
		# data= [['Project Name: ', ''],
		# 	['Site Location', ''],
		# 	['M.R DATE', ''],
		# 	['Type', ''],
		# 	]
		# STYLE = [
		# 	('GRID',(0,0),(-1,-1),0.5,colors.darkgrey),
		# 	('BACKGROUND',(0,0),(-1,0),colors.grey),
		# 	]
		# t=tables.Table(data,style=STYLE)
		# t.hAlign = 'LEFT'
		# Story.append(t)


		# logo = "logo.png"
		# im = Image(logo, 2*inch)
		# im.hAlign = 'CENTER'
		# Story.append(im)
		
		# styles=getSampleStyleSheet()
		# styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
		# ptext = '<font size="18">%s</font>' % 'Purchase Requisition:'
		# Story.append(Paragraph(ptext, styles["Normal"]))
		# Story.append(Spacer(1, 12))

		# data= [['Project Name: ', ''],
		# 	['Site Location', ''],
		# 	['M.R DATE', ''],
		# 	['Type', ''],
		# 	]
		# STYLE = [
		# 	('GRID',(0,0),(-1,-1),0.5,colors.darkgrey),
		# 	('BACKGROUND',(0,0),(-1,0),colors.grey),
		# 	]
		# t=tables.Table(data,style=STYLE)
		# t.hAlign = 'LEFT'
		# Story.append(t)

		doc.build(Story)
		return Response()

