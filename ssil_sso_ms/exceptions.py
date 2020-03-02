from __future__ import unicode_literals

from django.core.exceptions import PermissionDenied
from django.http import Http404
from rest_framework import status, exceptions
from rest_framework.response import Response
#from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ValidationError


def root_simple_error_handler(exc, *args, app_name=''):
    """
    Returns the response that should be used for any given exception.

    By default we handle the REST framework `APIException`, and also
    Django's builtin `Http404` and `PermissionDenied` exceptions.

    Any unhandled exceptions may return `None`, which will cause a 500 error
    to be raised.
    """

    #print('args',args)
    check_exception = 0
    for each_args in args:
        #print('each_args',each_args['view'].__module__)
        if each_args['view'].__module__ == 'hrms.views' or each_args['view'].__module__ == 'pms.views':
            #print('ok')
            check_exception = 1
    if isinstance(exc,ValidationError):
        print('ValidationError',exc)
        print('ValidationError',exc.get_codes())
        #n = dict(exc.detail)
        headers = {}
        if check_exception == 1:
            return Response({'error': exc.detail},status=exc.status_code,headers=headers)
        else:
            return Response(exc.detail,status=exc.status_code,headers=headers)

    elif isinstance(exc, exceptions.APIException):
        print('APIException',exc.get_full_details())
        headers = {}
        if getattr(exc, 'auth_header', None):
            headers['WWW-Authenticate'] = exc.auth_header
        if getattr(exc, 'wait', None):
            headers['X-Throttle-Wait-Seconds'] = '%d' % exc.wait
        print('exc.detail',exc.detail)
        if check_exception == 1:
            return Response({'error': exc.detail},status=exc.status_code,headers=headers)
        else:
            return Response(exc.detail,status=exc.status_code,headers=headers)

    elif isinstance(exc, Http404):
        print('Http404')
        if check_exception == 1:
            return Response({'error': 'Not found'},status=status.HTTP_404_NOT_FOUND)
        else:
            return Response('Not found',status=status.HTTP_404_NOT_FOUND)

    elif isinstance(exc, PermissionDenied):
        print('PermissionDenied')
        if check_exception == 1:
            return Response({'error': 'Permission denied'},
                        status=status.HTTP_403_FORBIDDEN)
        else:
            return Response('Permission denied',status=status.HTTP_403_FORBIDDEN)

    # Note: Unhandled exceptions will raise a 500 error.
    return None
