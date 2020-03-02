from django.shortcuts import render
from mailsend.models import *

from django.core.mail import EmailMessage
from django.core.mail import EmailMultiAlternatives
from django.core.mail import EmailMessage
from django.template import Context,Template
# from mail.models import MailTemplate
from django.conf import settings
from email.mime.image import MIMEImage
# permission checking
from rest_framework.permissions import IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import filters
from rest_framework.views import APIView
from threading import Thread  # for threading
import os
from email.mime.text import MIMEText

'''
    This module prepared by @@ Rupam Hazra. Any kind of issues occurred, ask me first !!!
    Version - 2.0
'''

class MailSendApiView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        #print('GetAppVersionView')
        email = request.data['email']
        mail_response = ''

        mail_id = request.data['email']
        # ============= Mail Send ==============#
        if mail_id:
            mail_data = {
                        "subject": "This is test mail",
                       }
            mail_class = GlobleMailSend('TEST001', [mail_id])
            mail_thread = Thread(target = mail_class.mailsend, args = (mail_data,))
            mail_response = mail_thread.start()


        response_dict = {
            "msg":"success"
        }
        return Response(response_dict)

class GlobleMailSend(object):
    """docstring for GlobleMailSend"""
    def __init__(self, code, recipient_list:list):
        super(GlobleMailSend, self).__init__()
        self.code = code
        self.from_email = settings.EMAIL_FROM_C
        self.recipient_list = recipient_list

    def mailsend(self, mail_data:dict,attach=''):
        # print('mail_data111111',mail_data)
        # print('attach',attach)
        # print('attach type',type(attach))
        # print("self.code: ", self.code)
        mail_content = MailTemplate.objects.get(code = self.code)
        subject = mail_content.subject
        template_variable = mail_content.template_variable.split(",")
        html_content = Template(mail_content.html_content)
        match_data_dict = {}
        for data in template_variable:
            if data.strip() in mail_data:
                match_data_dict[data.strip()] = mail_data[data.strip()]
        
        if match_data_dict:
            context_data = Context(match_data_dict)
            #print(type(self.code ))
            # print("self.recipient_list",self.recipient_list)
            html_content = html_content.render(context_data)
            msg = EmailMessage(subject, html_content,self.from_email, self.recipient_list)
            msg.content_subtype = "html"
            if self.code == "PMS-ST-A":
                #print('attach.name',attach.name,attach.read(),attach.content_type)
                if attach:
                    attach = '.'+attach
                    #print('attach',attach)
                    fp = open(attach, 'rb')
                    mime_image = MIMEImage(fp.read())
                    fp.close()
                    mime_image.add_header('Content-ID', '<image>')
                    msg.attach(mime_image)

            ##############################################################################
            '''
                This condition is used only .ics file generate and atteched with mail.
            '''
            if self.code == "ETAP" or self.code == "ETRDC":
                # print('attach.name',attach)
                if attach:
                    part = MIMEText(attach,'calendar')
                    part.add_header('Filename','file.ics') 
                    part.add_header('Content-Disposition','attachment; filename=file.ics') 
                    # print("part",part)
                    msg.attach(part)
            #################################################################################
            msg.send()
        print("mail send Done..... ")
        return True
        




