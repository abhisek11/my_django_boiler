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
from datetime import datetime
from holidays.models import *
import collections
from rest_framework.exceptions import APIException
import pandas as pd
import numpy as np
from django_filters.rest_framework import DjangoFilterBackend
from master.serializers import UserModuleWiseListSerializer
from master.models import TMasterModuleRole
from users.models import TCoreUserDetail
from custom_decorator import *
from rest_framework.parsers import FileUploadParser
import os
from pms.custom_filter import *

#::::::::::::PMS PRE EXECUTION GUEST HOUSE FINDING:::::::::#
class PreExecutionGuestHouseFindingAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionGuestHouseFinding.objects.filter(is_deleted=False)
    serializer_class = PreExecutionGuestHouseFindingAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project',)
    @response_modify_decorator_get_single
    def get(self, request, *args, **kwargs):
        return response
class PreExecutionGuestHouseFindingEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionGuestHouseFinding.objects.all()
    serializer_class =PreExecutionGuestHouseFindingEditSerializer

#::::::::::::PMS PRE EXECUTION FURNITURE :::::::::#
class PreExecutionFurnitureAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionFurniture.objects.filter(is_deleted=False)
    serializer_class = PreExecutionFurnitureAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project',)
    @response_modify_decorator_get_single
    def get(self, request, *args, **kwargs):
        return response
class PreExecutionFurnitureEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionFurniture.objects.all()
    serializer_class=PreExecutionFurnitureEditSerializer
class PreExecutionFurnitureRequirementsAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionFurMFurRequirements.objects.filter(is_deleted=False)
    serializer_class = PreExecutionFurnitureRequirementsAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('f_requirements__project',)
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
class PreExecutionFurnitureRequirementsEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionFurMFurRequirements.objects.all()
    serializer_class = PreExecutionFurnitureRequirementsEditSerializer
class PreExecutionFurnitureRequirementsDocumentEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionFurMFurRequirements.objects.all()
    serializer_class = PreExecutionFurnitureRequirementsDocumentEditSerializer
class PreExecutionFurnitureRequirementsDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionFurMFurRequirements.objects.all()
    serializer_class =PreExecutionFurnitureRequirementsDeleteSerializer


#::::::::::::PMS PRE EXCUTION UTILITIES ELECTRICAL::::::::::::::::::::::::::::::::::::::::::::::::::::#
class PreExcutionUtilitiesElectricalAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesElectrical.objects.filter(is_deleted=False)
    serializer_class = PreExcutionUtilitiesElectricalAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project',)

    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
class PreExcutionUtilitiesElectricalEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesElectrical.objects.all()
    serializer_class = PreExcutionUtilitiesElectricalEditSerializer

    def get(self, request, *args, **kwargs):
        responce = super(PreExcutionUtilitiesElectricalEditView, self).get(self, args, kwargs)
        project_id = responce.data["project"]
        tab_doc_d = PmsPreExcutionUtilitiesDocument.objects.filter(project=project_id,model_class='PmsPreExcutionUtilitiesElectrical').values(
            'id', 'project', 'module_id', 'document_name', 'document', 'created_by', 'owned_by')
        doc_detail = []
        if tab_doc_d:
            for tab_doc in tab_doc_d:
                doc_detail.append(tab_doc)
        else:
            doc_detail = []
        responce.data['electrical_document']=doc_detail
        return responce
class PreExcutionUtilitiesElectricalDocumentAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.filter(is_deleted=False)
    serializer_class = PreExcutionUtilitiesElectricalDocumentAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project',)
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
class PreExcutionUtilitiesElectricalDocumentEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.all()
    serializer_class = PreExcutionUtilitiesElectricalDocumentEditSerializer
class PreExcutionUtilitiesElectricalDocumentDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.all()
    serializer_class =PreExcutionUtilitiesElectricalDocumentDeleteSerializer

#:::::::::::::::::::::: PMS PRE EXCUTION UTILITIES WATER:::::::::::::::::::::::::::#
class PreExcutionUtilitiesWaterAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesWater.objects.filter(is_deleted=False)
    serializer_class = PreExcutionUtilitiesWaterAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project',)
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
class PreExcutionUtilitiesWaterEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesWater.objects.all()
    serializer_class = PreExcutionUtilitiesWaterEditSerializer

    def get(self, request, *args, **kwargs):
        responce = super(PreExcutionUtilitiesWaterEditView, self).get(self, args, kwargs)
        project_id = responce.data["project"]
        tab_doc_d = PmsPreExcutionUtilitiesDocument.objects.filter(project=project_id,model_class='PmsPreExcutionUtilitiesWater').values(
            'id', 'project', 'module_id', 'document_name', 'document', 'created_by', 'owned_by')
        print("tab_doc_d",tab_doc_d)
        doc_detail = []
        if tab_doc_d:
            for tab_doc in tab_doc_d:
                doc_detail.append(tab_doc)
        else:
            doc_detail = []
        responce.data['water_document']=doc_detail
        return responce
class PreExcutionUtilitiesWaterDocumentAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.filter(is_deleted=False)
    serializer_class = PreExcutionUtilitiesWaterDocumentAddSerializer
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
class PreExcutionUtilitiesWaterDocumentEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.all()
    serializer_class = PreExcutionUtilitiesWaterDocumentEditSerializer
class PreExcutionUtilitiesWaterDocumentDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.all()
    serializer_class =PreExcutionUtilitiesWaterDocumentDeleteSerializer

#:::::::::::::::::::::: PMS PRE EXCUTION UTILITIES FUEL:::::::::::::::::::::::::::#
class PreExcutionUtilitiesFuelAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesFuel.objects.filter(is_deleted=False)
    serializer_class = PreExcutionUtilitiesFuelAddSerializer
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
class PreExcutionUtilitiesFuelEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesFuel.objects.all()
    serializer_class = PreExcutionUtilitiesFuelEditSerializer

    def get(self, request, *args, **kwargs):
        responce = super(PreExcutionUtilitiesFuelEditView, self).get(self, args, kwargs)
        project_id = responce.data["project"]
        tab_doc_d = PmsPreExcutionUtilitiesDocument.objects.filter(project=project_id,model_class='PmsPreExcutionUtilitiesFuel').values(
            'id', 'project', 'module_id', 'document_name', 'document', 'created_by', 'owned_by')
        doc_detail = []
        if tab_doc_d:
            for tab_doc in tab_doc_d:
                doc_detail.append(tab_doc)
        else:
            doc_detail = []
        responce.data['fuel_document']=doc_detail
        return responce
class PreExcutionUtilitiesFuelDocumentAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.filter(is_deleted=False)
    serializer_class = PreExcutionUtilitiesFuelDocumentAddSerializer
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
class PreExcutionUtilitiesFuelDocumentEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.all()
    serializer_class = PreExcutionUtilitiesFuelDocumentEditSerializer
class PreExcutionUtilitiesFuelDocumentDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.all()
    serializer_class =PreExcutionUtilitiesFuelDocumentDeleteSerializer
 #:::::::::::::: PMS PRE EXCUTION UTILITIES UTENSILS ::::::::::::::::::::::::::::::::::#
class PreExcutionUtilitiesUtensilsAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesUtensils.objects.filter(is_deleted=False)
    serializer_class = PreExcutionUtilitiesUtensilsAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project',)
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
class PreExcutionUtilitiesUtensilsEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesUtensils.objects.all()
    serializer_class=PreExcutionUtilitiesUtensilsEditSerializer
class PreExcutionUtilitiesUtensilsDocumentAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.filter(is_deleted=False)
    serializer_class = PreExcutionUtilitiesUtensilsDocumentAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project',)
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
class PreExcutionUtilitiesUtensilsDocumentEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.all()
    serializer_class = PreExcutionUtilitiesUtensilsDocumentEditSerializer
class PreExcutionUtilitiesUtensilsDocumentDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.all()
    serializer_class = PreExcutionUtilitiesUtensilsDocumentDeleteSerializer
class PreExcutionUtilitiesUtensilsTypesListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesUtensilsTypes.objects.filter(is_deleted=False)
    serializer_class = PreExcutionUtilitiesUtensilsTypesListSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project',)
    def get(self, request, *args, **kwargs):
        response = super(PreExcutionUtilitiesUtensilsTypesListView, self).get(request, *args, **kwargs)
        data_dict = {}
        data_dict['result'] = response.data
        for data in response.data:
            # print('data',data)
            document_details = list()
            utensils_document = PmsPreExcutionUtilitiesDocument.objects.filter(
                model_class="PmsPreExcutionUtilitiesUtensilsTypes",
                module_id=int(data['id']),
                is_deleted=False)
            print('utensils_document',utensils_document)
            for document in utensils_document:
                data1={
                    "id":int(document.id),
                    "project":int(document.project.id),
                    "module_id":document.module_id,
                    "model_class": document.model_class,
                    "document_name":document.document_name,
                    "document":request.build_absolute_uri(document.document.url),
                }
                document_details.append(data1)
            data['utensils_document_details']=document_details
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
class PreExcutionUtilitiesUtensilsTypesEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesUtensilsTypes.objects.all()
    serializer_class = PreExcutionUtilitiesUtensilsTypesEditSerializer
class PreExcutionUtilitiesUtensilsTypesDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesUtensilsTypes.objects.all()
    serializer_class =PreExcutionUtilitiesUtensilsTypesDeleteSerializer
#:::::::::::::: PMS PRE EXCUTION UTILITIES TIFFIN BOX :::::::::::::::::::::::::::::::::::::::::::::::::#
class PreExcutionUtilitiesTiffinBoxAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesTiffinBox.objects.filter(is_deleted=False)
    serializer_class =PreExcutionUtilitiesTiffinBoxAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project',)
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
class PreExcutionUtilitiesTiffinBoxEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesTiffinBox.objects.filter(is_deleted=False)
    serializer_class = PreExcutionUtilitiesTiffinBoxEditSerializer
class PreExcutionUtilitiesTiffinBoxDocumentAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.filter(is_deleted=False)
    serializer_class = PreExcutionUtilitiesTiffinBoxDocumentAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project',)
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
class PreExcutionUtilitiesTiffinBoxDocumentEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.all()
    serializer_class = PreExcutionUtilitiesTiffinBoxDocumentEditSerializer
class PreExcutionUtilitiesTiffinBoxDocumentDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.all()
    serializer_class = PreExcutionUtilitiesTiffinBoxDocumentDeleteSerializer
class PreExcutionUtilitiesTiffinBoxTypesListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesTiffinBoxTypes.objects.filter(is_deleted=False)
    serializer_class = PreExcutionUtilitiesTiffinBoxTypesListSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project',)

    def get(self, request, *args, **kwargs):
        response = super(PreExcutionUtilitiesTiffinBoxTypesListView, self).get(request, *args, **kwargs)
        data_dict={}
        data_dict['result']=response.data
        for data in response.data:
            print('data',data)
            document_details = list()
            tiffin_box_document = PmsPreExcutionUtilitiesDocument.objects.filter(
                model_class="PmsPreExcutionUtilitiesTiffinBoxTypes",
                module_id=int(data['id']),
                is_deleted=False)
            print('tiffin_box_document',tiffin_box_document)
            for document in tiffin_box_document:
                data1={
                    "id":int(document.id),
                    "project":int(document.project.id),
                    "module_id":document.module_id,
                    "model_class":document.model_class,
                    "document_name":document.document_name,
                    "document":request.build_absolute_uri(document.document.url),
                }
                document_details.append(data1)
            data['tiffin_box_document_details']=document_details
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
class PreExcutionUtilitiesTiffinBoxTypesEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesTiffinBoxTypes.objects.all()
    serializer_class =PreExcutionUtilitiesTiffinBoxTypesEditSerializer
class PreExcutionUtilitiesTiffinBoxTypesDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesTiffinBoxTypes.objects.all()
    serializer_class =PreExcutionUtilitiesTiffinBoxTypesDeleteSerializer
#:::::::::::::::::::::: PMS PRE EXCUTION UTILITIES COOK:::::::::::::::::::::::::::::::::::::::::::::::::::::::::#
class PreExcutionUtilitiesCookAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesCook.objects.all()
    serializer_class = PreExcutionUtilitiesCookAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project',)
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
class PreExcutionUtilitiesCookEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesCook.objects.all()
    serializer_class = PreExcutionUtilitiesCookEditSerializer
#:::::::::::::::::::::: PMS PRE EXECUTION OFFICE SETUP MASTER::::::::::::::::::::::::::::::::::::::::::::::::::::::#
# class PreExecutionOfficeSetupMasterAddView(generics.ListCreateAPIView):
#     permission_classes = [IsAuthenticated]
#     authentication_classes = [TokenAuthentication]
#     queryset = PmsPreExecutionOfficeSetupMaster.objects.filter(is_deleted=False)
#     serializer_class = PreExecutionOfficeSetupMasterAddSerializer
# class PreExecutionOfficeSetupMasterEditView(generics.RetrieveUpdateAPIView):
#     permission_classes = [IsAuthenticated]
#     authentication_classes = [TokenAuthentication]
#     queryset = PmsPreExecutionOfficeSetupMaster.objects.all()
#     serializer_class = PreExecutionOfficeSetupMasterEditSerializer
# class PreExecutionOfficeSetupMasterDeleteView(generics.RetrieveUpdateAPIView):
#     permission_classes = [IsAuthenticated]
#     authentication_classes = [TokenAuthentication]
#     queryset = PmsPreExecutionOfficeSetupMaster.objects.all()
#     serializer_class = PreExecutionOfficeSetupMasterDeleteSerializer
#::::::::::::PMS PRE EXCUTION OFFICE STRUCTURE:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::#
class PreExecutionOfficeStructureAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExecutionOfficeStructure.objects.filter(is_deleted=False)
    serializer_class = PreExecutionOfficeStructureAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project',)
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
class PreExecutionOfficeStructureEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExecutionOfficeStructure.objects.all()
    serializer_class =  PreExecutionOfficeStructureEditSerializer
class PreExecutionOfficeStructureDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExecutionOfficeStructure.objects.all()
    serializer_class =  PreExecutionOfficeStructureDeleteSerializer
class PreExecutionOfficeStructureDocumentAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.filter(is_deleted=False)
    serializer_class =  PreExecutionOfficeStructureDocumentAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project',)
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
class PreExecutionOfficeStructureDocumentEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.all()
    serializer_class = PreExecutionOfficeStructureDocumentEditSerializer
class PreExecutionOfficeStructureDocumentDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.all()
    serializer_class = PreExecutionOfficeStructureDocumentDeleteSerializer

#:::::::::::::::::::::: PMS PRE EXECUTION ELECTRICAL CONNECTION:::::::::::::::::::::::::::#
class PreExecutionElectricalConnectionAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExecutionElectricalConnection.objects.filter(is_deleted=False)
    serializer_class = PreExecutionElectricalConnectionAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project',)
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
class PreExecutionElectricalConnectionEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExecutionElectricalConnection.objects.all()
    serializer_class = PreExecutionElectricalConnectionEditSerializer

    def get(self, request, *args, **kwargs):
        responce = super(PreExecutionElectricalConnectionEditView, self).get(self, args, kwargs)
        project_id = responce.data["project"]
        tab_doc_d = PmsPreExcutionUtilitiesDocument.objects.filter(project=project_id,model_class='PmsPreExecutionElectricalConnection').values(
            'id', 'project', 'module_id', 'model_class', 'document_name', 'document', 'created_by', 'owned_by')
        doc_detail = []
        if tab_doc_d:
            for tab_doc in tab_doc_d:
                doc_detail.append(tab_doc)
        else:
            doc_detail = []
        responce.data['document_details']=doc_detail
        return responce
class PreExecutionElectricalConnectionDocumentAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.filter(is_deleted=False)
    serializer_class =  PreExecutionElectricalConnectionDocumentAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project',)
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
class PreExecutionElectricalConnectionDocumentEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.all()
    serializer_class = PreExecutionElectricalConnectionDocumentEditSerializer
class PreExecutionElectricalConnectionDocumentDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.all()
    serializer_class = PreExecutionElectricalConnectionDocumentDeleteSerializer
#:::::::::::::::::::::: PMS PRE EXECUTION WATER CONNECTION:::::::::::::::::::::::::::#
class PreExecutionWaterConnectionAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExecutionWaterConnection.objects.filter(is_deleted=False)
    serializer_class = PreExecutionWaterConnectionAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project',)
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
class PreExecutionWaterConnectionEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExecutionWaterConnection.objects.all()
    serializer_class = PreExecutionWaterConnectionEditSerializer

    def get(self, request, *args, **kwargs):
        responce = super(PreExecutionWaterConnectionEditView, self).get(self, args, kwargs)
        project_id = responce.data["project"]
        tab_doc_d = PmsPreExcutionUtilitiesDocument.objects.filter(project=project_id,model_class='PmsPreExecutionWaterConnection').values(
            'id', 'project', 'module_id', 'model_class', 'document_name', 'document', 'created_by', 'owned_by')
        doc_detail = []
        if tab_doc_d:
            for tab_doc in tab_doc_d:
                doc_detail.append(tab_doc)
        else:
            doc_detail = []
        responce.data['document_details']=doc_detail
        return responce
class PreExecutionWaterConnectionDocumentAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.filter(is_deleted=False)
    serializer_class =  PreExecutionWaterConnectionDocumentAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project',)
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
class PreExecutionWaterConnectionDocumentEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.all()
    serializer_class = PreExecutionWaterConnectionDocumentEditSerializer
class PreExecutionWaterConnectionDocumentDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.all()
    serializer_class = PreExecutionWaterConnectionDocumentDeleteSerializer
#:::::::::::::::::::::: PMS PRE EXECUTION INTERNET CONNECTION:::::::::::::::::::::::::::#
class PreExecutionInternetConnectionAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExecutionInternetConnection.objects.filter(is_deleted=False)
    serializer_class = PreExecutionInternetConnectionAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project',)
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
class PreExecutionInternetConnectionEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExecutionInternetConnection.objects.all()
    serializer_class = PreExecutionInternetConnectionEditSerializer

    def get(self, request, *args, **kwargs):
        responce = super(PreExecutionInternetConnectionEditView, self).get(self, args, kwargs)
        project_id = responce.data["project"]
        tab_doc_d = PmsPreExcutionUtilitiesDocument.objects.filter(project=project_id,model_class='PmsPreExecutionInternetConnection').values(
            'id', 'project', 'module_id', 'model_class', 'document_name', 'document', 'created_by', 'owned_by')
        doc_detail = []
        if tab_doc_d:
            for tab_doc in tab_doc_d:
                doc_detail.append(tab_doc)
        else:
            doc_detail = []
        responce.data['document_details']=doc_detail
        return responce
class PreExecutionInternetConnectionDocumentAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.filter(is_deleted=False)
    serializer_class =  PreExecutionInternetConnectionDocumentAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project',)
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
class PreExecutionInternetConnectionDocumentEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.all()
    serializer_class = PreExecutionInternetConnectionDocumentEditSerializer
class PreExecutionInternetConnectionDocumentDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.all()
    serializer_class = PreExecutionInternetConnectionDocumentDeleteSerializer
#:::::::::::::::::::::: PMS PRE EXCUTION OFFICE SETUP FURNITURE:::::::::::::::::::::::::::#
class PreExcutionOfficeSetupFurnitureAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionOfficeSetupFurniture.objects.filter(is_deleted=False)
    serializer_class = PreExcutionOfficeSetupFurnitureAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project','furniture_type')
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
class PreExcutionOfficeSetupFurnitureEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionOfficeSetupFurniture.objects.all()
    serializer_class = PreExcutionOfficeSetupFurnitureEditSerializer

    def get(self, request, *args, **kwargs):
        responce = super(PreExcutionOfficeSetupFurnitureEditView, self).get(self, args, kwargs)
        project_id = responce.data["project"]
        tab_doc_d = PmsPreExcutionUtilitiesDocument.objects.filter(project=project_id,model_class='PmsPreExcutionOfficeSetupFurniture').values(
            'id', 'project', 'module_id', 'model_class', 'document_name', 'document', 'created_by', 'owned_by')
        doc_detail = []
        if tab_doc_d:
            for tab_doc in tab_doc_d:
                doc_detail.append(tab_doc)
        else:
            doc_detail = []
        responce.data['document_details']=doc_detail
        return responce
class PreExcutionOfficeSetupFurnitureDocumentAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.filter(is_deleted=False)
    serializer_class =  PreExcutionOfficeSetupFurnitureDocumentAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project',)
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
class PreExcutionOfficeSetupFurnitureDocumentEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.all()
    serializer_class = PreExcutionOfficeSetupFurnitureDocumentEditSerializer
class PreExcutionOfficeSetupFurnitureDocumentDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.all()
    serializer_class = PreExcutionOfficeSetupFurnitureDocumentDeleteSerializer
#:::::::::::::::::::::: PMS PRE EXCUTION OFFICE SETUP COMPUTER:::::::::::::::::::::::::::#
class PreExcutionOfficeSetupComputerAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionOfficeSetupComputer.objects.filter(is_deleted=False)
    serializer_class = PreExcutionOfficeSetupComputerAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project',)
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
class PreExcutionOfficeSetupComputerEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionOfficeSetupComputer.objects.all()
    serializer_class = PreExcutionOfficeSetupComputerEditSerializer

    def get(self, request, *args, **kwargs):
        responce = super(PreExcutionOfficeSetupComputerEditView, self).get(self, args, kwargs)
        project_id = responce.data["project"]
        tab_doc_d = PmsPreExcutionUtilitiesDocument.objects.filter(project=project_id,model_class='PmsPreExcutionOfficeSetupComputer').values(
            'id', 'project', 'module_id', 'model_class', 'document_name', 'document', 'created_by', 'owned_by')
        doc_detail = []
        if tab_doc_d:
            for tab_doc in tab_doc_d:
                doc_detail.append(tab_doc)
        else:
            doc_detail = []
        responce.data['document_details']=doc_detail
        return responce
class PreExcutionOfficeSetupComputerDocumentAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.filter(is_deleted=False)
    serializer_class =  PreExcutionOfficeSetupComputerDocumentAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project',)
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
class PreExcutionOfficeSetupComputerDocumentEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.all()
    serializer_class = PreExcutionOfficeSetupComputerDocumentEditSerializer
class PreExcutionOfficeSetupComputerDocumentDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.all()
    serializer_class = PreExcutionOfficeSetupComputerDocumentDeleteSerializer
#::::::::::::PMS PRE EXCUTION OFFICE SETUP STATIONARY::::::::::::::::::::::::::::::::::::::::::::::::::#
class PreExecutionOfficeSetupStationaryAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionOfficeSetupStationary.objects.filter(is_deleted=False)
    serializer_class =PreExecutionOfficeSetupStationaryAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project',)
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
class PreExecutionOfficeSetupStationaryEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionOfficeSetupStationary.objects.filter(is_deleted=False)
    serializer_class = PreExecutionOfficeSetupStationaryEditSerializer
class PreExecutionOfficeSetupStationaryRequirementsDocumentAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.filter(is_deleted=False)
    serializer_class =PreExecutionOfficeSetupStationaryRequirementsDocumentAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project',)
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
class PreExecutionOfficeSetupStationaryRequirementsDocumentEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.all()
    serializer_class = PreExecutionOfficeSetupStationaryRequirementsDocumentEditSerializer
class PreExecutionOfficeSetupStationaryRequirementsDocumentDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.all()
    serializer_class = PreExecutionOfficeSetupStationaryRequirementsDocumentDeleteSerializer
class PreExecutionOfficeSetupStationaryRequirementsListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionOfficeSetupStationaryMStnRequirements.objects.filter(is_deleted=False)
    serializer_class = PreExecutionOfficeSetupStationaryRequirementsListSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project',)
    def get(self, request, *args, **kwargs):
        response = super(PreExecutionOfficeSetupStationaryRequirementsListView, self).get(request, *args, **kwargs)
        data_dict={}
        data_dict['result']=response.data
        for data in response.data:
            print('data',data)
            document_details = list()
            tiffin_box_document = PmsPreExcutionUtilitiesDocument.objects.filter(
                model_class="PmsPreExcutionOfficeSetupStationaryMStnRequirements",
                module_id=int(data['id']),
                is_deleted=False)

            for document in tiffin_box_document:
                data1={
                    "id":int(document.id),
                    "project":int(document.project.id),
                    "module_id":document.module_id,
                    "model_class":document.model_class,
                    "document_name":document.document_name,
                    "document":request.build_absolute_uri(document.document.url),
                }
                document_details.append(data1)
            data['stationary_requirements_document_details']=document_details
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
class PreExecutionOfficeSetupStationaryRequirementsEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionOfficeSetupStationaryMStnRequirements.objects.all()
    serializer_class = PreExecutionOfficeSetupStationaryRequirementsEditSerializer
class PreExecutionOfficeSetupStationaryRequirementsDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionOfficeSetupStationaryMStnRequirements.objects.all()
    serializer_class = PreExecutionOfficeSetupStationaryRequirementsDeleteSerializer

#:::::::::::::::::::::: PMS PRE EXCUTION OFFICE SETUP TOILET:::::::::::::::::::::::::::#
class PreExcutionOfficeSetupToiletAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionOfficeSetupToilet.objects.filter(is_deleted=False)
    serializer_class = PreExcutionOfficeSetupToiletAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project',)
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
class PreExcutionOfficeSetupToiletEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionOfficeSetupToilet.objects.all()
    serializer_class = PreExcutionOfficeSetupToiletEditSerializer

    def get(self, request, *args, **kwargs):
        responce = super(PreExcutionOfficeSetupToiletEditView, self).get(self, args, kwargs)
        project_id = responce.data["project"]
        tab_doc_d = PmsPreExcutionUtilitiesDocument.objects.filter(project=project_id,model_class='PmsPreExcutionOfficeSetupToilet').values(
            'id', 'project', 'module_id', 'model_class', 'document_name', 'document', 'created_by', 'owned_by')
        doc_detail = []
        if tab_doc_d:
            for tab_doc in tab_doc_d:
                doc_detail.append(tab_doc)
        else:
            doc_detail = []
        responce.data['document_details']=doc_detail
        return responce
class PreExcutionOfficeSetupToiletDocumentAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.filter(is_deleted=False)
    serializer_class =  PreExcutionOfficeSetupToiletDocumentAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project',)
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
class PreExcutionOfficeSetupToiletDocumentEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.all()
    serializer_class = PreExcutionOfficeSetupToiletDocumentEditSerializer
class PreExcutionOfficeSetupToiletDocumentDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.all()
    serializer_class = PreExcutionOfficeSetupToiletDocumentDeleteSerializer

#:::::::::::::::::::::: PMS PRE EXCUTION OFFICE SETUP VEHICLE:::::::::::::::::::::::::::#
class PreExcutionOfficeSetupVehicleAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionOfficeSetupVehicle.objects.filter(is_deleted=False)
    serializer_class = PreExcutionOfficeSetupVehicleAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project',)
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return vehicle_data
class PreExcutionOfficeSetupVehicleEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionOfficeSetupVehicle.objects.filter(is_deleted=False)
    serializer_class = PreExcutionOfficeSetupVehicleEditSerializer
class PreExcutionOfficeSetupVehicleDocumentAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.filter(is_deleted=False)
    serializer_class =  PreExcutionOfficeSetupVehicleDocumentAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project',)
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
class PreExcutionOfficeSetupVehicleDocumentEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.all()
    serializer_class = PreExcutionOfficeSetupVehicleDocumentEditSerializer
class PreExcutionOfficeSetupVehicleDocumentDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.all()
    serializer_class = PreExcutionOfficeSetupVehicleDocumentDeleteSerializer
class PreExcutionOfficeSetupVehicleDriverListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionOfficeSetupVehicleDriver.objects.filter(is_deleted=False)
    serializer_class = PreExcutionOfficeSetupVehicleDriverListSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project',)
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
class PreExcutionOfficeSetupVehicleDriverEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionOfficeSetupVehicleDriver.objects.all()
    serializer_class = PreExcutionOfficeSetupVehicleDriverEditSerializer
class PreExcutionOfficeSetupVehicleDriverDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionOfficeSetupVehicleDriver.objects.all()
    serializer_class = PreExcutionOfficeSetupVehicleDriverDeleteSerializer

#:::::::::::::::::::::: PMS PRE EXECUTION OFFICE SETUP BIKE:::::::::::::::::::::::::::#
class PreExecutionOfficeSetupBikeAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExecutionOfficeSetupBike.objects.filter(is_deleted=False)
    serializer_class = PreExecutionOfficeSetupBikeAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project',)
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
class PreExecutionOfficeSetupBikeEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExecutionOfficeSetupBike.objects.all()
    serializer_class = PreExecutionOfficeSetupBikeEditSerializer

    def get(self, request, *args, **kwargs):
        responce = super(PreExecutionOfficeSetupBikeEditView, self).get(self, args, kwargs)
        project_id = responce.data["project"]
        tab_doc_d = PmsPreExcutionUtilitiesDocument.objects.filter(project=project_id,model_class='PmsPreExecutionOfficeSetupBike').values(
            'id', 'project', 'module_id', 'model_class', 'document_name', 'document', 'created_by', 'owned_by')
        doc_detail = []
        if tab_doc_d:
            for tab_doc in tab_doc_d:
                doc_detail.append(tab_doc)
        else:
            doc_detail = []
        responce.data['document_details']=doc_detail
        return responce
class PreExecutionOfficeSetupBikeDocumentAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.filter(is_deleted=False)
    serializer_class =  PreExecutionOfficeSetupBikeDocumentAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project',)
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
class PreExecutionOfficeSetupBikeDocumentEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.all()
    serializer_class = PreExecutionOfficeSetupBikeDocumentEditSerializer
class PreExecutionOfficeSetupBikeDocumentDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.all()
    serializer_class = PreExecutionOfficeSetupBikeDocumentDeleteSerializer

#:::::::::::::::::::::: PMS PRE EXECUTION OFFICE SETUP LABOUR LABOUR HUTMENT:::::::::::::::::::::::::::#
class PreExecutionOfficeSetupLabourLabourHutmentAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExecutionOfficeSetupLabourLabourHutment.objects.filter(is_deleted=False)
    serializer_class = PreExecutionOfficeSetupLabourLabourHutmentAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project',)
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
class PreExecutionOfficeSetupLabourLabourHutmentEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExecutionOfficeSetupLabourLabourHutment.objects.all()
    serializer_class = PreExecutionOfficeSetupLabourLabourHutmentEditSerializer

    def get(self, request, *args, **kwargs):
        responce = super(PreExecutionOfficeSetupLabourLabourHutmentEditView, self).get(self, args, kwargs)
        project_id = responce.data["project"]
        tab_doc_d = PmsPreExcutionUtilitiesDocument.objects.filter(project=project_id,model_class='PmsPreExecutionOfficeSetupLabourLabourHutment').values(
            'id', 'project', 'module_id', 'model_class', 'document_name', 'document', 'created_by', 'owned_by')
        doc_detail = []
        if tab_doc_d:
            for tab_doc in tab_doc_d:
                doc_detail.append(tab_doc)
        else:
            doc_detail = []
        responce.data['document_details']=doc_detail
        return responce
class PreExecutionOfficeSetupLabourLabourHutmentDocumentAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.filter(is_deleted=False)
    serializer_class =  PreExecutionOfficeSetupLabourLabourHutmentDocumentAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project',)
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
class PreExecutionOfficeSetupLabourLabourHutmentDocumentEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.all()
    serializer_class = PreExecutionOfficeSetupLabourLabourHutmentDocumentEditSerializer
class PreExecutionOfficeSetupLabourLabourHutmentDocumentDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.all()
    serializer_class = PreExecutionOfficeSetupLabourLabourHutmentDocumentDeleteSerializer

#:::::::::::::::::::::: PMS PRE EXECUTION OFFICE SETUP LABOUR TOILET:::::::::::::::::::::::::::#

class PreExecutionOfficeSetupLabourToiletAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExecutionOfficeSetupLabourToilet.objects.filter(is_deleted=False)
    serializer_class = PreExecutionOfficeSetupLabourToiletAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project',)
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
class PreExecutionOfficeSetupLabourToiletEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExecutionOfficeSetupLabourToilet.objects.all()
    serializer_class = PreExecutionOfficeSetupLabourToiletEditSerializer

    def get(self, request, *args, **kwargs):
        responce = super(PreExecutionOfficeSetupLabourToiletEditView, self).get(self, args, kwargs)
        project_id = responce.data["project"]
        tab_doc_d = PmsPreExcutionUtilitiesDocument.objects.filter(project=project_id,model_class='PmsPreExecutionOfficeSetupLabourToilet').values(
            'id', 'project', 'module_id', 'model_class', 'document_name', 'document', 'created_by', 'owned_by')
        doc_detail = []
        if tab_doc_d:
            for tab_doc in tab_doc_d:
                doc_detail.append(tab_doc)
        else:
            doc_detail = []
        responce.data['document_details']=doc_detail
        return responce
class PreExecutionOfficeSetupLabourToiletDocumentAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.filter(is_deleted=False)
    serializer_class =  PreExecutionOfficeSetupLabourToiletDocumentAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project',)
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
class PreExecutionOfficeSetupLabourToiletDocumentEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.all()
    serializer_class = PreExecutionOfficeSetupLabourToiletDocumentEditSerializer
class PreExecutionOfficeSetupLabourToiletDocumentDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.all()
    serializer_class = PreExecutionOfficeSetupLabourToiletDocumentDeleteSerializer

#:::::::::::::::::::::: PMS PRE EXECUTION OFFICE SETUP LABOUR WATER CONNECTION:::::::::::::::::::::::::::#
class PreExecutionOfficeSetupLabourWaterConnectionAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExecutionOfficeSetupLabourWaterConnection.objects.filter(is_deleted=False)
    serializer_class = PreExecutionOfficeSetupLabourWaterConnectionAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project',)
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
class PreExecutionOfficeSetupLabourWaterConnectionEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExecutionOfficeSetupLabourWaterConnection.objects.all()
    serializer_class = PreExecutionOfficeSetupLabourWaterConnectionEditSerializer

    def get(self, request, *args, **kwargs):
        responce = super(PreExecutionOfficeSetupLabourWaterConnectionEditView, self).get(self, args, kwargs)
        project_id = responce.data["project"]
        tab_doc_d = PmsPreExcutionUtilitiesDocument.objects.filter(project=project_id,model_class='PmsPreExecutionOfficeSetupLabourWaterConnection').values(
            'id', 'project', 'module_id', 'model_class', 'document_name', 'document', 'created_by', 'owned_by')
        doc_detail = []
        if tab_doc_d:
            for tab_doc in tab_doc_d:
                doc_detail.append(tab_doc)
        else:
            doc_detail = []
        responce.data['document_details']=doc_detail
        return responce
class PreExecutionOfficeSetupLabourWaterConnectionDocumentAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.filter(is_deleted=False)
    serializer_class =  PreExecutionOfficeSetupLabourWaterConnectionDocumentAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project',)
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
class PreExecutionOfficeSetupLabourWaterConnectionDocumentEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.all()
    serializer_class = PreExecutionOfficeSetupLabourWaterConnectionDocumentEditSerializer
class PreExecutionOfficeSetupLabourWaterConnectionDocumentDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.all()
    serializer_class = PreExecutionOfficeSetupLabourWaterConnectionDocumentDeleteSerializer

#:::::::::::::::::::::: PMS PRE EXECUTION OFFICE SETUP LABOUR ELECTRICAL CONNECTION:::::::::::::::::::::::::::#
class PreExecutionOfficeSetupLabourElectricalConnectionAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExecutionOfficeSetupLabourElectricalConnection.objects.filter(is_deleted=False)
    serializer_class = PreExecutionOfficeSetupLabourElectricalConnectionAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project',)
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
class PreExecutionOfficeSetupLabourElectricalConnectionEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExecutionOfficeSetupLabourElectricalConnection.objects.all()
    serializer_class = PreExecutionOfficeSetupLabourElectricalConnectionEditSerializer

    def get(self, request, *args, **kwargs):
        responce = super(PreExecutionOfficeSetupLabourElectricalConnectionEditView, self).get(self, args, kwargs)
        project_id = responce.data["project"]
        tab_doc_d = PmsPreExcutionUtilitiesDocument.objects.filter(project=project_id,model_class='PmsPreExecutionOfficeSetupLabourElectricalConnection').values(
            'id', 'project', 'module_id', 'model_class', 'document_name', 'document', 'created_by', 'owned_by')
        doc_detail = []
        if tab_doc_d:
            for tab_doc in tab_doc_d:
                doc_detail.append(tab_doc)
        else:
            doc_detail = []
        responce.data['document_details']=doc_detail
        return responce
class PreExecutionOfficeSetupLabourElectricalConnectionDocumentAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.filter(is_deleted=False)
    serializer_class =  PreExecutionOfficeSetupLabourElectricalConnectionDocumentAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project',)
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
class PreExecutionOfficeSetupLabourElectricalConnectionDocumentEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.all()
    serializer_class = PreExecutionOfficeSetupLabourElectricalConnectionDocumentEditSerializer
class PreExecutionOfficeSetupLabourElectricalConnectionDocumentDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.all()
    serializer_class = PreExecutionOfficeSetupLabourElectricalConnectionDocumentDeleteSerializer

#:::::::::::::::::::::: PMS PRE EXECUTION OFFICE SETUP RAW MATERIAL YARD:::::::::::::::::::::::::::#
class PreExecutionOfficeSetupRawMaterialYardAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExecutionOfficeSetupRawMaterialYard.objects.filter(is_deleted=False)
    serializer_class = PreExecutionOfficeSetupRawMaterialYardAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project',)
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
class PreExecutionOfficeSetupRawMaterialYardEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExecutionOfficeSetupRawMaterialYard.objects.all()
    serializer_class = PreExecutionOfficeSetupRawMaterialYardEditSerializer

    def get(self, request, *args, **kwargs):
        responce = super(PreExecutionOfficeSetupRawMaterialYardEditView, self).get(self, args, kwargs)
        project_id = responce.data["project"]
        tab_doc_d = PmsPreExcutionUtilitiesDocument.objects.filter(project=project_id,model_class='PmsPreExecutionOfficeSetupRawMaterialYard').values(
            'id', 'project', 'module_id', 'model_class', 'document_name', 'document', 'created_by', 'owned_by')
        doc_detail = []
        if tab_doc_d:
            for tab_doc in tab_doc_d:
                doc_detail.append(tab_doc)
        else:
            doc_detail = []
        responce.data['document_details']=doc_detail
        return responce
class PreExecutionOfficeSetupRawMaterialYardDocumentAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.filter(is_deleted=False)
    serializer_class =  PreExecutionOfficeSetupRawMaterialYardDocumentAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project',)
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
class PreExecutionOfficeSetupRawMaterialYardDocumentEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.all()
    serializer_class = PreExecutionOfficeSetupRawMaterialYardDocumentEditSerializer
class PreExecutionOfficeSetupRawMaterialYardDocumentDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.all()
    serializer_class = PreExecutionOfficeSetupRawMaterialYardDocumentDeleteSerializer

#:::::::::::::::::::::: PMS PRE EXECUTION OFFICE SETUP CEMENT GODOWN:::::::::::::::::::::::::::#
class PreExecutionOfficeSetupCementGodownAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExecutionOfficeSetupCementGodown.objects.filter(is_deleted=False)
    serializer_class = PreExecutionOfficeSetupCementGodownAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project',)
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
class PreExecutionOfficeSetupCementGodownEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExecutionOfficeSetupCementGodown.objects.all()
    serializer_class = PreExecutionOfficeSetupCementGodownEditSerializer

    def get(self, request, *args, **kwargs):
        responce = super(PreExecutionOfficeSetupCementGodownEditView, self).get(self, args, kwargs)
        project_id = responce.data["project"]
        tab_doc_d = PmsPreExcutionUtilitiesDocument.objects.filter(project=project_id,model_class='PmsPreExecutionOfficeSetupCementGodown').values(
            'id', 'project', 'module_id', 'model_class', 'document_name', 'document', 'created_by', 'owned_by')
        doc_detail = []
        if tab_doc_d:
            for tab_doc in tab_doc_d:
                doc_detail.append(tab_doc)
        else:
            doc_detail = []
        responce.data['document_details']=doc_detail
        return responce
class PreExecutionOfficeSetupCementGodownDocumentAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.filter(is_deleted=False)
    serializer_class =  PreExecutionOfficeSetupCementGodownDocumentAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project',)
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
class PreExecutionOfficeSetupCementGodownDocumentEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.all()
    serializer_class = PreExecutionOfficeSetupCementGodownDocumentEditSerializer
class PreExecutionOfficeSetupCementGodownDocumentDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.all()
    serializer_class = PreExecutionOfficeSetupCementGodownDocumentDeleteSerializer

#:::::::::::::::::::::: PMS PRE EXECUTION OFFICE SETUP LAB:::::::::::::::::::::::::::#
class PreExecutionOfficeSetupLabAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExecutionOfficeSetupLab.objects.filter(is_deleted=False)
    serializer_class = PreExecutionOfficeSetupLabAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project',)
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
class PreExecutionOfficeSetupLabEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExecutionOfficeSetupLab.objects.all()
    serializer_class = PreExecutionOfficeSetupLabEditSerializer

    def get(self, request, *args, **kwargs):
        responce = super(PreExecutionOfficeSetupLabEditView, self).get(self, args, kwargs)
        project_id = responce.data["project"]
        tab_doc_d = PmsPreExcutionUtilitiesDocument.objects.filter(project=project_id,model_class='PmsPreExecutionOfficeSetupLab').values(
            'id', 'project', 'module_id', 'model_class', 'document_name', 'document', 'created_by', 'owned_by')
        doc_detail = []
        if tab_doc_d:
            for tab_doc in tab_doc_d:
                doc_detail.append(tab_doc)
        else:
            doc_detail = []
        responce.data['document_details']=doc_detail
        return responce
class PreExecutionOfficeSetupLabDocumentAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.filter(is_deleted=False)
    serializer_class =  PreExecutionOfficeSetupLabDocumentAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project',)
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
class PreExecutionOfficeSetupLabDocumentEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.all()
    serializer_class = PreExecutionOfficeSetupLabDocumentEditSerializer
class PreExecutionOfficeSetupLabDocumentDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.all()
    serializer_class = PreExecutionOfficeSetupLabDocumentDeleteSerializer

# ::::::::::::PMS PRE EXECUTION OFFICE SETUP SURVEY INSTRUMENT:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::#
class PreExecutionOfficeSetupSurveyInstrumentAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExecutionOfficeSetupSurveyInstruments.objects.filter(is_deleted=False)
    serializer_class =PreExecutionOfficeSetupSurveyInstrumentAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project','survey_instrument_type_tab')
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
class PreExecutionOfficeSetupSurveyInstrumentEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExecutionOfficeSetupSurveyInstruments.objects.filter(is_deleted=False)
    serializer_class =PreExecutionOfficeSetupSurveyInstrumentEditSerializer
class PreExecutionOfficeSetupSurveyInstrumentTypesDocumentAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.filter(is_deleted=False)
    serializer_class = PreExecutionOfficeSetupSurveyInstrumentTypesDocumentAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project',)
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
class PreExecutionOfficeSetupSurveyInstrumentTypesDocumentEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.all()
    serializer_class = PreExecutionOfficeSetupSurveyInstrumentTypesDocumentEditSerializer
class PreExecutionOfficeSetupSurveyInstrumentTypesDocumentDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.all()
    serializer_class = PreExecutionOfficeSetupSurveyInstrumentTypesDocumentDeleteSerializer
class PreExecutionOfficeSetupSurveyInstrumentTypesListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExecutionOfficeSetupSurveyInstrumentsType.objects.filter(is_deleted=False)
    serializer_class =PreExecutionOfficeSetupSurveyInstrumentTypesListSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project','survey_instrument__survey_instrument_type_tab')
    def get(self, request, *args, **kwargs):
        response = super(PreExecutionOfficeSetupSurveyInstrumentTypesListView, self).get(request, *args, **kwargs)
        data_dict={}
        data_dict['result']=response.data
        for data in response.data:
            print('data',data)
            document_details = list()
            tiffin_box_document = PmsPreExcutionUtilitiesDocument.objects.filter(
                model_class="PmsPreExecutionOfficeSetupSurveyInstrumentsType",
                module_id=int(data['id']),
                is_deleted=False)

            for document in tiffin_box_document:
                data1={
                    "id":int(document.id),
                    "project":int(document.project.id),
                    "module_id":document.module_id,
                    "model_class":document.model_class,
                    "document_name":document.document_name,
                    "document":request.build_absolute_uri(document.document.url),
                    'is_deleted':document.is_deleted
                }
                document_details.append(data1)
            data['document_details']=document_details
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
class PreExecutionOfficeSetupSurveyInstrumentTypesEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExecutionOfficeSetupSurveyInstrumentsType.objects.all()
    serializer_class = PreExecutionOfficeSetupSurveyInstrumentTypesEditSerializer
class PreExecutionOfficeSetupSurveyInstrumentTypesDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExecutionOfficeSetupSurveyInstrumentsType.objects.all()
    serializer_class = PreExecutionOfficeSetupSurveyInstrumentTypesDeleteSerializer

#:::::::::::::PMS PRE EXECUTION OFFICE SETUP SAFTEY PPE's:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::#
class PreExecutionOfficeSetupSafetyPPEsAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExecutionOfficeSetupSafetyPPEs.objects.filter(is_deleted=False)
    serializer_class = PreExecutionOfficeSetupSafetyPPEsAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project',)
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return ppes_data
class PreExecutionOfficeSetupSafetyPPEsEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExecutionOfficeSetupSafetyPPEs.objects.filter(is_deleted=False)
    serializer_class = PreExecutionOfficeSetupSafetyPPEsEditSerializer
class PreExecutionOfficeSetupSafetyPPEsDocumentAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.filter(is_deleted=False)
    serializer_class = PreExecutionOfficeSetupSafetyPPEsDocumentAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project',)
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
class PreExecutionOfficeSetupSafetyPPEsDocumentEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.all()
    serializer_class = PreExecutionOfficeSetupSafetyPPEsDocumentEditSerializer
class PreExecutionOfficeSetupSafetyPPEsDocumentDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.all()
    serializer_class = PreExecutionOfficeSetupSafetyPPEsDocumentDeleteSerializer
class PreExecutionOfficeSetupSafetyPPEsAccessoryListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExecutionOfficeSetupSafetyPPEsAccessory.objects.filter(is_deleted=False)
    serializer_class = PreExecutionOfficeSetupSafetyPPEsAccessoryListSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project',)

    def get(self, request, *args, **kwargs):
        response = super(PreExecutionOfficeSetupSafetyPPEsAccessoryListView, self).get(request, *args, **kwargs)
        data_dict={}
        data_dict['result']=response.data
        for data in response.data:
            print('data',data)
            document_details = list()
            ppes_accessory_document = PmsPreExcutionUtilitiesDocument.objects.filter(
                model_class="PmsPreExecutionOfficeSetupSafetyPPEsAccessory",
                module_id=int(data['id']),
                is_deleted=False)
            print('ppes_accessory_document',ppes_accessory_document)
            for document in ppes_accessory_document:
                data1={
                    "id":int(document.id),
                    "project":int(document.project.id),
                    "module_id":document.module_id,
                    "model_class":document.model_class,
                    "document_name":document.document_name,
                    "document":request.build_absolute_uri(document.document.url),
                }
                document_details.append(data1)
            data['ppes_accessory_document_details']=document_details
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
class PreExecutionOfficeSetupSafetyPPEsAccessoryEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExecutionOfficeSetupSafetyPPEsAccessory.objects.all()
    serializer_class = PreExecutionOfficeSetupSafetyPPEsAccessoryEditSerializer
class PreExecutionOfficeSetupSafetyPPEsAccessoryDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExecutionOfficeSetupSafetyPPEsAccessory.objects.all()
    serializer_class =PreExecutionOfficeSetupSafetyPPEsAccessoryDeleteSerializer

#:::::::::::::::::::::: PMS PRE EXECUTION OFFICE SETUP SECURITY ROOM:::::::::::::::::::::::::::#
class PreExecutionOfficeSetupSecurityRoomAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExecutionOfficeSetupSecurityRoom.objects.filter(is_deleted=False)
    serializer_class = PreExecutionOfficeSetupSecurityRoomAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project',)
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
class PreExecutionOfficeSetupSecurityRoomEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExecutionOfficeSetupSecurityRoom.objects.all()
    serializer_class = PreExecutionOfficeSetupSecurityRoomEditSerializer

    def get(self, request, *args, **kwargs):
        responce = super(PreExecutionOfficeSetupSecurityRoomEditView, self).get(self, args, kwargs)
        project_id = responce.data["project"]
        tab_doc_d = PmsPreExcutionUtilitiesDocument.objects.filter(project=project_id,model_class='PmsPreExecutionOfficeSetupSecurityRoom').values(
            'id', 'project', 'module_id', 'model_class', 'document_name', 'document', 'created_by', 'owned_by')
        doc_detail = []
        if tab_doc_d:
            for tab_doc in tab_doc_d:
                doc_detail.append(tab_doc)
        else:
            doc_detail = []
        responce.data['document_details']=doc_detail
        return responce
class PreExecutionOfficeSetupSecurityRoomDocumentAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.filter(is_deleted=False)
    serializer_class =  PreExecutionOfficeSetupSecurityRoomDocumentAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project',)
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
class PreExecutionOfficeSetupSecurityRoomDocumentEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.all()
    serializer_class = PreExecutionOfficeSetupSecurityRoomDocumentEditSerializer
class PreExecutionOfficeSetupSecurityRoomDocumentDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.all()
    serializer_class = PreExecutionOfficeSetupSecurityRoomDocumentDeleteSerializer


#:::::::::::::::::::::: PMS PRE EXECUTION P AND M DETAILS::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::#
class PreExecutionPAndMMachineryTypeExDetailsAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExecutionMachineryTypeDetails.objects.filter(is_deleted=False)
    serializer_class = PreExecutionPAndMMachineryTypeExDetailsAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project','machinary_type')
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
class PreExecutionPAndMMachineryTypeDetailsAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExecutionMachineryTypeDetails.objects.filter(is_deleted=False)
    serializer_class = PreExecutionPAndMMachineryTypeDetailsAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project','machinary_type')
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response

class MachinaryTypeListByProjectView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsMachineryType.objects.filter(is_deleted=False,is_default=True)
    serializer_class = MachinaryTypeListByProjectSerializer

    @response_modify_decorator_get_after_execution
    def get(self, request,*args,**kwargs):
        project=self.kwargs.get('project')
        # print("project",type(project))
        pre_ex_list = []
        tender_list = []
        type_list = []
        response=super(self.__class__, self).get(self, request, *args,**kwargs)
        pre_ex_details = PmsPreExecutionMachineryTypeDetails.objects.filter(project=project,is_deleted=False).values()
        pre_ex_mac_list = [pre_ex_data['machinary_type_id'] for pre_ex_data in pre_ex_details]
        # print("pre_ex_list",pre_ex_list)
        tender_details = PmsTenderMachineryTypeDetails.objects.filter(tender=str(PmsProjects.objects.get(id=project,is_deleted=False))).values()
        tender_mac_list = [ten_data['machinary_type_id'] for ten_data in tender_details]
        # print("tender_details",tender_details)
        for type_data in response.data:
            if type_data['id'] in pre_ex_mac_list:
                for pre_ex in pre_ex_details:
                    if pre_ex['machinary_type_id']==type_data['id']:
                        pre_ex['name']=type_data['name']
                        pre_ex['description']=type_data['description']
                        pre_ex_list.append(pre_ex)

                # print("pre_ex_list",pre_ex_list)
            elif type_data['id'] in tender_mac_list:
                for tender in tender_details:
                    if tender['machinary_type_id']==type_data['id']:
                        tender['name']=type_data['name']
                        tender['description']=type_data['description']
                        tender['types']=None
                        tender['model_of_machinery']=None
                        tender['fuel_consumption']=None
                        tender['quantity']=None
                        tender['capacity']=None
                        tender['rate_per_product']=None
                        tender['operator_required']=None
                        tender['operator_name']=None
                        tender['operator_contact_no']=None
                        tender['operator_salary']=None
                        tender['requirment_s_date']=None
                        tender['requirment_e_date']=None
                        tender['budgeted_cost']=None
                        tender['executed_cost']=None         
                        # print("tender",tender)
                        tender_list.append(tender)
                # print("tender_list",tender_list)
            else:
                # print("type_data",type_data)
                type_data['machinary_type_id']=type_data['id']
                type_data['types']=None
                type_data['model_of_machinery']=None
                type_data['fuel_consumption']=None
                type_data['quantity']=None
                type_data['capacity']=None
                type_data['rate_per_product']=None
                type_data['operator_required']=None
                type_data['operator_name']=None
                type_data['operator_contact_no']=None
                type_data['operator_salary']=None
                type_data['requirment_s_date']=None
                type_data['requirment_e_date']=None
                type_data['budgeted_cost']=None
                type_data['executed_cost']=None
                type_list.append(type_data)
            
        total_list = pre_ex_list+tender_list+type_list

        return Response(total_list)



class PreExecutionPAndMDetailsEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExecutionMachineryTypeDetails.objects.all()
    serializer_class = PreExecutionPAndMDetailsEditSerializer

    def get(self, request, *args, **kwargs):
        responce = super(PreExecutionPAndMDetailsEditView, self).get(self, args, kwargs)
        project_id = responce.data["project"]
        tab_doc_d = PmsPreExcutionUtilitiesDocument.objects.filter(project=project_id,model_class='PmsPreExecutionPAndMDetails').values(
            'id', 'project', 'module_id', 'model_class', 'document_name', 'document', 'created_by', 'owned_by')
        doc_detail = []
        if tab_doc_d:
            for tab_doc in tab_doc_d:
                doc_detail.append(tab_doc)
        else:
            doc_detail = []
        responce.data['document_details']=doc_detail
        return responce
class PreExecutionPAndMDetailsDocumentAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.filter(is_deleted=False)
    serializer_class =  PreExecutionPAndMDetailsDocumentAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project',)
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
class PreExecutionPAndMDetailsDocumentEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.all()
    serializer_class = PreExecutionPAndMDetailsDocumentEditSerializer
class PreExecutionPAndMDetailsDocumentDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.all()
    serializer_class = PreExecutionPAndMDetailsDocumentDeleteSerializer
# # :::::::::::::::::::::::::::::::::: PMS PRE EXECUTION MANPOWER::::::::::::::::::::::::::::::::::::::::::::::#
# class PreExecutionManpowerMasterAddView(generics.ListCreateAPIView):
#     permission_classes = [IsAuthenticated]
#     authentication_classes = [TokenAuthentication]
#     queryset = PmsPreExecutionManpowerMaster.objects.filter(is_deleted=False)
#     serializer_class = PreExecutionManpowerMasterAddSerializer
#     filter_backends = (DjangoFilterBackend,)
#     filterset_fields = ('project',)
#     @response_modify_decorator_get
#     def get(self, request, *args, **kwargs):
#         return response
# class PreExecutionManpowerMasterEditView(generics.RetrieveUpdateAPIView):
# 	permission_classes = [IsAuthenticated]
# 	authentication_classes = [TokenAuthentication]
# 	queryset = PmsPreExecutionManpowerMaster.objects.all()
# 	serializer_class = PreExecutionManpowerMasterEditSerializer
# class PreExecutionManpowerMasterDeleteView(generics.RetrieveUpdateAPIView):
# 	permission_classes = [IsAuthenticated]
# 	authentication_classes = [TokenAuthentication]
# 	queryset = PmsPreExecutionManpowerMaster.objects.all()
# 	serializer_class = PreExecutionManpowerMasterDeleteSerializer



class PreExecutionManpowerRequirementAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExecutionManpowerDetails.objects.filter(is_deleted=False)
    serializer_class = PreExecutionManpowerRequirementAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project','manpower','designation')
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response

class PreExecutionManpowerRequirementEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExecutionManpowerDetails.objects.filter(is_deleted=False)
    serializer_class = PreExecutionManpowerRequirementEditSerializer

class PreExecutionManpowerRequirementDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExecutionManpowerDetails.objects.all()
    serializer_class =PreExecutionManpowerRequirementDeleteSerializer

class PreExecutionManpowerDetailsDocumentAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.filter(is_deleted=False)
    serializer_class = PreExecutionManpowerDetailsDocumentAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project',)
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response

class PreExecutionManpowerDetailsDocumentEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.all()
    serializer_class = PreExecutionManpowerDetailsDocumentEditSerializer

class PreExecutionManpowerDetailsDocumentDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExcutionUtilitiesDocument.objects.all()
    serializer_class = PreExecutionManpowerDetailsDocumentDeleteSerializer


#::::::::::::::::::::::::::::::::::::::PMS PRE EXECUTION COST ANALYSIS:::::::::::::::::::::::::::::::::#
class PreExecutionCostAnalysisAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExecutionCostAnalysis.objects.all()
    serializer_class = PreExecutionCostAnalysisAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project','analysis_type')
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response

#:::::::::::::::::::::: PMS PRE EXECUTION CONTRACTOR FINALIZATION:::::::::::::::::::::::::::#
class PreExecutionContractorFinalizationAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExecutionContractorFinalization.objects.filter(is_deleted=False)
    serializer_class = PreExecutionContractorFinalizationAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project',)
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
class PreExecutionContractorFinalizationEditView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExecutionContractorFinalization.objects.all()
    serializer_class = PreExecutionContractorFinalizationEditSerializer

    def get(self, request, *args, **kwargs):
        responce = super(PreExecutionContractorFinalizationEditView, self).get(self, args, kwargs)
        project_id = responce.data["project"]
        tab_doc_d = PmsPreExcutionUtilitiesDocument.objects.filter(project=project_id,model_class='PmsPreExecutionContractorFinalization').values(
            'id', 'project', 'module_id', 'model_class', 'document_name', 'document', 'created_by', 'owned_by')
        doc_detail = []
        if tab_doc_d:
            for tab_doc in tab_doc_d:
                doc_detail.append(tab_doc)
        else:
            doc_detail = []
        responce.data['document_details']=doc_detail
        return responce
class PreExecutionContractorFinalizationDeleteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExecutionContractorFinalization.objects.all()
    serializer_class = PreExecutionContractorFinalizationDeleteSerializer
class PreExecutionContractorFinalizationListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExecutionContractorFinalization.objects.all()
    serializer_class = PreExecutionContractorFinalizationListSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project','machinery')
    def get(self, request, *args, **kwargs):
        response = super(PreExecutionContractorFinalizationListView, self).get(self, request, *args, **kwargs)
        machinery_data = list()
        machinery_data_set = set()
        data_dict={}
        for data in response.data:
            machinery_data_set.add(data['machinery'])
        for machinery_id in machinery_data_set:
            contractor_data = list()
            machinery_details = custom_filter(
                self, PmsMachineries,
                filter_columns={
                    'id': machinery_id, 'is_deleted': False
                },
                fetch_columns=[ 'id','equipment_name', 'equipment_category','equipment_type', 'owner_type', 'equipment_make','equipment_model_no',
                'equipment_chassis_serial_no','equipment_engine_serial_no', 'equipment_registration_no','equipment_power',
                'measurement_by', 'measurement_quantity','fuel_consumption', 'remarks', 'is_deleted', 'created_by','owned_by',
                'updated_by', 'created_at', 'updated_at'],
                single_row = True
            )
            contractor_id = PmsPreExecutionContractorFinalization.objects.filter(is_deleted=False, machinery=machinery_id).values('contractor')
            for contractor_data_id in contractor_id:
                contractor_details=PmsExternalUsers.objects.get(id=contractor_data_id['contractor'],is_deleted=False)
                contractor_details.__dict__.pop('_state') if "_state" in contractor_details.__dict__.keys() else contractor_details.__dict__
                contractor_data.append(contractor_details.__dict__)
            machinery_details['contractor_details'] = contractor_data
            machinery_data.append(machinery_details)

        if machinery_data:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_SUCCESS
        elif len(machinery_data) == 0:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_NO_DATA
        else:
            data_dict['request_status'] = 0
            data_dict['msg'] = settings.MSG_ERROR
        data_dict['results']=machinery_data
        return Response(data_dict)

#:::::::::::::::::::::::::::::::::: PMS PRE EXECUTION SITE PUJA::::::::::::::::::::::::::::::::::::::::::::::#
class PreExecutionSitePujaAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExecutionSitePuja.objects.filter(is_deleted=False)
    serializer_class = PreExecutionSitePujaAddSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project',)
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response
class PreExecutionSitePujaEditView(generics.RetrieveUpdateAPIView):
	permission_classes = [IsAuthenticated]
	authentication_classes = [TokenAuthentication]
	queryset = PmsPreExecutionSitePuja.objects.all()
	serializer_class = PreExecutionSitePujaEditSerializer
class PreExecutionSitePujaDeleteView(generics.RetrieveUpdateAPIView):
	permission_classes = [IsAuthenticated]
	authentication_classes = [TokenAuthentication]
	queryset = PmsPreExecutionSitePuja.objects.all()
	serializer_class = PreExecutionSitePujaDeleteSerializer

#::::::::::::::::::::::::PMS PRE EXECUTION APPROVAL:::::::::::::::#
class PreExecutionApprovalAddOrUpdateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = PmsPreExecutionApproval.objects.all()
    serializer_class =PreExecutionApprovalEditSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project','pre_execution_tabs')
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return response


