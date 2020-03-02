from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from tickettool.models import *
from tickettool.serializers import *
from rest_framework import serializers
from django.db import transaction
from django.conf import settings
# from pagination import CSLimitOffestpagination,CSPageNumberPagination
from rest_framework import filters
from mailsend.views import *
from threading import Thread    
from rest_framework.exceptions import APIException
# from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

class SupportTypeAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = SupportType
        fields = ('__all__')
    
    def create(self,validated_data):
        try:
            owned_by = validated_data.get('owned_by')
            created_by = validated_data.get('created_by')
            with transaction.atomic():
                support_data, created1 = SupportType.objects.get_or_create(**validated_data)
                return support_data

        except Exception as e:
            raise e


class TicketAddSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Ticket
        fields = ('__all__')
    
    def create(self,validated_data):
        try:
            owned_by = validated_data.get('owned_by')
            created_by = validated_data.get('created_by')
            
            with transaction.atomic():
                request = self.context.get('request')
                # image_data=validated_data.pop('image')
                # print(image_data)
                # if image_data:
                ticket_data, created1 = Ticket.objects.get_or_create(**validated_data)
                
                print(ticket_data.__dict__)
                email=ticket_data.__dict__['submitter_email']
                email_admin= 'tonmoy@shyamfuture.com'
                # email_admin= 'abhishekrock94@shyamfuture.com'
                print("email",email) 
                # ============= Mail Send Step ==============#
                user_name= User.objects.get(email=email)
                print(user_name.first_name)
                if user_name:
                    mail_data = {
                                "name":(user_name.first_name).capitalize() + ' ' +(user_name.last_name).capitalize(),
                                "ticket_no":ticket_data.__dict__['ticket_g_id'],
                        }
                    print('mail_data',mail_data)
                    mail_class = GlobleMailSend('PMS-ST', [email])
                    mail_thread = Thread(target = mail_class.mailsend, args = (mail_data,None))
                    mail_thread.start()

                from urllib.parse import urlparse
                path_url=request.build_absolute_uri(ticket_data.image.url)
                media_path = urlparse(path_url)
                #print("media_path",media_path.path)
                if email_admin:
                    mail_data = {
                                
                                "ticket_no":ticket_data.__dict__['ticket_g_id'],
                                "ticket_content":ticket_data.__dict__['description'],
                        }
                    print('mail_data',mail_data)
                    mail_class = GlobleMailSend('PMS-ST-A', [email_admin])
                    mail_thread = Thread(target = mail_class.mailsend, args = (mail_data,media_path.path))
                    mail_thread.start()
                return ticket_data

        except Exception as e:
            raise e

class TicketListSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(default=serializers.CurrentUserDefault())
    owned_by = serializers.CharField(default=serializers.CurrentUserDefault())
    updated_by = serializers.CharField(default=serializers.CurrentUserDefault())
    
    class Meta:
        model = Ticket
        fields = ('__all__')
    

