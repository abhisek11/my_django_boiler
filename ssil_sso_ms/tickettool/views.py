from django.shortcuts import render
from rest_framework import generics
from django.views.generic import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from tickettool.models import *
from tickettool.serializers import *
from django.conf import settings
from custom_decorator import *

from pagination import CSLimitOffestpagination,CSPageNumberPagination
from rest_framework import filters
from rest_framework.exceptions import APIException



class SupportTypeAdd(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = SupportType.objects.all()
    serializer_class = SupportTypeAddSerializer

    @response_modify_decorator_list
    def list(self, request, *args, **kwargs):
        # print(response)
        return response

class TicketAdd(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = Ticket.objects.all()
    serializer_class = TicketAddSerializer
    
    @response_modify_decorator_post_for_ticketingtool
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    @response_modify_decorator_list
    def list(self, request, *args, **kwargs):
        # print(response)
        return response

class TicketList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = Ticket.objects.all()
    serializer_class = TicketListSerializer
    
    @response_modify_decorator_list
    def list(self, request, *args, **kwargs):
        # print(response)
        return response

