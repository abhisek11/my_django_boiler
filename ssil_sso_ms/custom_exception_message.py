from rest_framework.exceptions import APIException
def custom_exception_message(self,field_name:str,msg:str=None):
    if msg:
        raise APIException({
                    "error":{
                        'request_status': 0, 
                        'msg': msg
                        }
                    }) 
    else:
        raise APIException({
                    "error":{
                        'request_status': 0, 
                        'msg': field_name + " already exist"
                        }
                    })