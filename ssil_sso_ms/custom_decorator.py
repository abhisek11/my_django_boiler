from django.conf import settings
from rest_framework.response import Response

#::::::::::: RESPONSE MODIFY DECORATOR FOR COMMON :::::::::::#

def response_modify_decorator_list(func):
    def inner(self, request, *args, **kwargs):
        #print("model", self.__module__)
        response = super(self.__class__, self).list(request, args, kwargs)
        #print("before Execution")
        data_dict = {}
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
        response.data = data_dict
        return response
        # getting the returned value
        func(self, request, *args, **kwargs)
    return inner

def response_modify_decorator_get(func):
    def inner(self, request, *args, **kwargs):
        #print("model", self.__module__)
        response = super(self.__class__, self).get(self, request, args, kwargs)
        #print("before Execution")
        data_dict = {}
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
        response.data = data_dict
        return response
        # getting the returned value
        func(self, request, *args, **kwargs)
        #print("after Execution")
        # returning the value to the original frame
    return inner

def response_modify_decorator_get_single(func):
    def inner(self, request, *args, **kwargs):
        #print("model", self.__module__)
        response = super(self.__class__, self).get(self, request, args, kwargs)
        #print("before Execution")
        data_dict = {}
        if response.data:
            data_dict['request_status'] = 1
            data_dict['result'] = response.data[0]
            data_dict['msg'] = settings.MSG_SUCCESS
        elif len(response.data) == 0:
            data_dict['request_status'] = 1
            data_dict['result'] = ""
            data_dict['msg'] = settings.MSG_NO_DATA
        else:
            data_dict['request_status'] = 0
            data_dict['result'] = ""
            data_dict['msg'] = settings.MSG_ERROR

        response.data = data_dict
        return response
        # getting the returned value
        func(self, request, *args, **kwargs)
        #print("after Execution")
        # returning the value to the original frame
    return inner


#::::::::::: RESPONSE MODIFY DECORATOR FOR COMMON AFTER EXECUTION:::::::::::#


def response_modify_decorator_list_after_execution(func):
    def inner(self, request, *args, **kwargs):
        print('Before Execution')
        # getting the returned value
        response = func(self, request, *args, **kwargs)
        # print("model", self.__module__)
        print("after Execution")
        data_dict = {}
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
        response.data = data_dict
        return response
    return inner

def response_modify_decorator_get_after_execution(func):
    def inner(self, request, *args, **kwargs):
        print('Before Execution')
        # getting the returned value
        response = func(self, request, *args, **kwargs)
        # print("model", self.__module__)
        print("after Execution")
        data_dict = {}
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
        response.data = data_dict
        return response
    return inner

def response_modify_decorator_get_single_after_execution(func):
    def inner(self, request, *args, **kwargs):
        #print("model", self.__module__)
        response = func(self, request, *args, **kwargs)
        #print("before Execution")
        data_dict = {}
        if response.data:
            data_dict['request_status'] = 1
            data_dict['results'] = response.data[0]
            data_dict['msg'] = settings.MSG_SUCCESS
        elif len(response.data) == 0:
            data_dict['request_status'] = 1
            data_dict['results'] = ""
            data_dict['msg'] = settings.MSG_NO_DATA
        else:
            data_dict['request_status'] = 0
            data_dict['results'] = ""
            data_dict['msg'] = settings.MSG_ERROR

        response.data = data_dict
        return response
        # getting the returned value
        
        #print("after Execution")
        # returning the value to the original frame
    return inner


#::::::::::: RESPONSE MODIFY DECORATOR FOR PAGINATION AND AFTER EXECUTION :::::::::::#


def response_modify_decorator_list_or_get_after_execution_for_pagination(func):
    def inner(self, request, *args, **kwargs):
        #print("before Execution")
        response = func(self, request, *args, **kwargs)
        #print("after Execution")
        #print('main_d',response.data)
        data_dict = {}
        data_dict = response.data
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
    return inner

def response_modify_decorator_list_or_get_before_execution_for_pagination(func):
    def inner(self, request, *args, **kwargs):
        #print("before Execution")
        response = super(self.__class__, self).get(self, request, args, kwargs)
        
        #print("after Execution")
        #print('main_d',response.data)
        data_dict = {}
        data_dict = response.data
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
        func(self, request, *args, **kwargs)
    return inner

def response_modify_decorator_post(func):
    def inner(self, request, *args, **kwargs):
        #print("model", self.__module__)
        response = func(self, request, *args, **kwargs)
        #print('response',response.data)
        data_dict = {}
        if response.data:
            data_dict['request_status'] = 1
            data_dict['result'] = response.data
            data_dict['msg'] = settings.MSG_SUCCESS
        elif len(response.data) == 0:
            data_dict['request_status'] = 1
            data_dict['result'] = ""
            data_dict['msg'] = settings.MSG_NO_DATA
        else:
            data_dict['request_status'] = 0
            data_dict['result'] = ""
            data_dict['msg'] = settings.MSG_ERROR  
        return Response(data_dict)
    
    return inner

def response_modify_decorator_post_for_ticketingtool(func):
    def inner(self, request, *args, **kwargs):
        #print("model", self.__module__)
        response = func(self, request, *args, **kwargs)
        #print('response',response.data)
        data_dict = {}
        if response.data:
            data_dict['request_status'] = 1
            data_dict['result'] = response.data
            data_dict['msg'] = "Your Support ticket has been generated.Ticket ID is  " + data_dict['result']['ticket_g_id']+" for future reference"
        elif len(response.data) == 0:
            data_dict['request_status'] = 1
            data_dict['result'] = ""
            data_dict['msg'] = settings.MSG_NO_DATA
        else:
            data_dict['request_status'] = 0
            data_dict['result'] = ""
            data_dict['msg'] = settings.MSG_ERROR  
        return Response(data_dict)
    
    return inner

def response_modify_decorator_update(func):
    def inner(self, request, *args, **kwargs):
        #print("model", self.__module__)
        response = func(self, request, *args, **kwargs)
        #print('response',response.data)
        data_dict = {}
        if response.data:
            data_dict['request_status'] = 1
            data_dict['result'] = response.data
            data_dict['msg'] = settings.MSG_SUCCESS
        elif len(response.data) == 0:
            data_dict['request_status'] = 1
            data_dict['result'] = ""
            data_dict['msg'] = settings.MSG_NO_DATA
        else:
            data_dict['request_status'] = 0
            data_dict['result'] = ""
            data_dict['msg'] = settings.MSG_ERROR  
        return Response(data_dict)
    
    return inner


#::::::::: RESPONSE MODIFY DECORATOR FOR ON OR OFF PAGINATION AND AFTER EXECUTION :::::::::#

def response_modify_decorator_list_or_get_after_execution_for_onoff_pagination(func):
    def inner(self, request, *args, **kwargs):
        response = func(self, request, *args, **kwargs)
        data_dict = {}
        #print("after Execution")
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
    return inner

def response_modify_decorator_list_or_get_before_execution_for_onoff_pagination(func):
    def inner(self, request, *args, **kwargs):
        response = super(self.__class__, self).list(self, request, args, kwargs)
        data_dict = {}
        #print("before Execution",response.data)

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
        func(self, request, *args, **kwargs)
    return inner

def response_with_status_get(func): 
    def inner(self, request, *args, **kwargs): 
        serializer = func(self, request, *args, **kwargs)
        data_dict = dict()
        data_dict['results'] = serializer.data
        if serializer.data:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_SUCCESS
        elif len(serializer.data) == 0:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_NO_DATA
        else:
            data_dict['request_status'] = 0
            data_dict['msg'] = settings.MSG_ERROR
        return Response(data_dict)
    return inner

def response_with_status(func): 
    def inner(self, request, *args, **kwargs): 
        result_data = func(self, request, *args, **kwargs)
        data_dict = dict()
        data_dict['results'] = result_data
        if result_data:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_SUCCESS
        elif len(result_data) == 0:
            data_dict['request_status'] = 1
            data_dict['msg'] = settings.MSG_NO_DATA
        else:
            data_dict['request_status'] = 0
            data_dict['msg'] = settings.MSG_ERROR
        return Response(data_dict)
    return inner

