from django.shortcuts import render

from smssend.models import *
from urllib.request import Request, urlopen
import urllib
import json
from django.conf import settings
import requests

from django.template import Context,Template

'''
    This module prepared by @@ Rupam Hazra. Any kind of issues occurred, ask me first !!!
    Version - 1.0
'''

class GlobleSmsSend(object):
    """docstring for ClassName"""
    def __init__(self, code, recipient_list:list):
        super(GlobleSmsSend, self).__init__()
        self.code = code
        self.recipient_list = recipient_list

    def sms_send(self, sms_data:dict):
        #print("self.code: ", self.code)
        sms_content = SmsContain.objects.get(code = self.code)

        contain_variable = sms_content.contain_variable.split(",")
        #print("contain_variable: ", contain_variable)

        txt_content = Template(sms_content.txt_content)
        #print('txt_content',txt_content)

        match_data_dict = {}
        for data in contain_variable:
            if data.strip() in sms_data:
                match_data_dict[data.strip()] = sms_data[data.strip()]

        if match_data_dict:
            context_data = Context(match_data_dict)
            txt_content = txt_content.render(context_data)

        for contact_no in self.recipient_list:
            headers = {
                    "authorization": "Bearer "+settings.SMS_API_KEY,
                    "cache-control": "no-cache",
                    "content-type": "application/x-www-form-urlencoded"
                }
            #print('headers',headers)    
            payload = {
                'sender_id': settings.SMS_SENDER, 
                'message': txt_content,
                'mobile_no': contact_no
                }

            response = requests.post(settings.SMS_URL, data=payload, headers=headers,verify=False)
            json_raw_response = response.content.decode('utf-8')
            json_decode_response = json.loads(json_raw_response)
            print('response: ',json_decode_response)
        
        print("SMS send Done..... ")
        return True

class GlobleSmsSendTxtLocal(object):
    def __init__(self,code,recipient_list:list):
        super(GlobleSmsSendTxtLocal, self).__init__()
        self.code = code
        self.recipient_list = recipient_list

    def sendSMS(self,sms_data:dict,type):
        sms_content = SmsContain.objects.get(code = self.code)
        contain_variable = sms_content.contain_variable.split(",")
        txt_content = Template(sms_content.txt_content)
        match_data_dict = {}
        for data in contain_variable:
            if data.strip() in sms_data:
                match_data_dict[data.strip()] = sms_data[data.strip()]

        if match_data_dict:
            context_data = Context(match_data_dict)
            txt_content = txt_content.render(context_data)


        print('type',type)
        print('txt_content',txt_content)
        if type == 'whatsapp':
            messages = {
                'send_channel':"whatsapp",
                'messages':[
                    {
                        'number':9038698174,
                        'template':{}
                    }
                ]
               
            }
            print('json.loads(messages)',json.dumps(messages))
            data =  urllib.parse.urlencode({
                'send_channel':'whatsapp',
                'apikey': settings.TXT_LOCAL_SMS_API_KEY, 
                'numbers': self.recipient_list,
                'messages' : json.dumps(messages),
                #'sender': 'SSILRM',
                'test':True
                })
            data = data.encode('utf-8')
            request = urllib.request.Request("https://api.textlocal.in/bulk_json/")
            f = urllib.request.urlopen(request, data)
            fr = f.read()
            print('fr',fr)

        elif type == 'sms':
            data =  urllib.parse.urlencode({
                'apikey': settings.TXT_LOCAL_SMS_API_KEY, 
                'numbers': self.recipient_list,
                'message' : txt_content,
                'sender': 'SSILRM',
                })
            data = data.encode('utf-8')
            request = urllib.request.Request("https://api.textlocal.in/send/?")
            f = urllib.request.urlopen(request, data)
            fr = f.read()
            print('fr',fr)
       

