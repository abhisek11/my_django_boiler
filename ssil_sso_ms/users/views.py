from django.shortcuts import render
from rest_framework import generics
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import Permission
from django.contrib.auth.models import *
from users.models import *
from users.serializers import *
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework import filters

# permission checking
from rest_framework.permissions import IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly
#from rest_framework.authentication import TokenAuthentication, SessionAuthentication
# collections 
import collections
# get_current_site
from django.contrib.sites.shortcuts import get_current_site
from mailsend.views import *
from rest_framework.exceptions import APIException

from threading import Thread  # for threading
from django.conf import settings
from django.db.models import Q
# pagination
from pagination import CSLimitOffestpagination, CSPageNumberPagination, OnOffPagination
from datetime import datetime
from custom_decorator import *
from core.serializers import *

'''
    New Token Authentication [knox]
'''
# from knox.auth import TokenAuthentication
# from rest_framework import permissions
# from knox.models import AuthToken
# from .serializers import LoginSerializer
# class LoginAPIView(generics.GenericAPIView):
#     serializer_class = LoginSerializer

#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.validated_data
#         return Response({
#             "user": UserSerializer(user, context=self.get_serializer_context()).data,
#             "token": AuthToken.objects.create(user)[1]
#         })
'''
    End
'''


class LoginAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        print('login post')
        try:
            error_msg = "Unable to log in with provided credentials .."
            suspended_msg = "user is suspended .."
            success_msg = "Log in Successfully .."
            # ===========================for contact_no=========================== #
            from django.http import QueryDict

            try:
                request_dict = request.data.dict()
            except Exception as e:
                print("error on request_dict 111: ", e)
                request_dict = request.data


            request_dict['username'] = request_dict['username']
            request_dict['password'] = request_dict['password']
            #print('username',request_dict['username'])
            # ===========================for is_active check=========================== #
            user_status = TCoreUserDetail.objects.filter(
                Q(cu_user__username=request_dict['username']) | Q(cu_phone_no=request_dict['username'])).values(
                "cu_user__is_active")
            #print("user_status: ", user_status)
            if user_status:
                for u_data in user_status:
                    # print("u_data: ", u_data)
                    if not u_data['cu_user__is_active']:
                        raise APIException(suspended_msg)
            else:
                raise APIException(error_msg)
            # ===========================for is_active check=========================== # comment by Rupam
            # if request_dict['username'].isnumeric() and len(request_dict['username']) <= 15:
            #     # print("request_dict['username']:::: ", request_dict['username'])
            #     user_details_data = TCoreUserDetail.objects.filter(cu_phone_no=int(request_dict['username'])) \
            #         .values("cu_user__username")
            #     # print("fgdfgdf: ",list(user_details_data)[0]['cu_user__username'])
            #     data = "username={}&password={}".format(str(list(user_details_data)[0]['cu_user__username']),
            #                                             request_dict['password'])
            #     request_dict = QueryDict(data)


            # ===========================for credentials check=========================== #
            try:
                response = super(LoginAuthToken, self).post(request_dict, *args, **kwargs)
            except Exception as error:
                print("error: ", error)
                raise APIException(error_msg)
            # ===========================for credentials check=========================== #
            # ===========================for contact_no=========================== #
            # response = super(LoginAuthToken, self).post(request, *args, **kwargs)
            print("request_qdict: ", request_dict)
            token = Token.objects.get(key=response.data['token'])
            
            user = User.objects.get(id=token.user_id)
            
            update_last_login(None, user)
            serializer = UserLoginSerializer(user, many=True)
            
            mmr_details = TMasterModuleRoleUser.objects.filter(mmr_user=user)
            
            applications = list()
            for mmr_data in mmr_details:
                print('mmr_details111111',mmr_data)
                module_dict = collections.OrderedDict()
                module_dict["id"] = mmr_data.id
                print('module_dict',module_dict)
                #print('type(mmr_data.mmr_type)',type(mmr_data.mmr_type))
                if mmr_data.mmr_type:
                    module_dict["user_type_details"] =  collections.OrderedDict({
                        "id":mmr_data.mmr_type,
                        "name": 'Module Admin' if mmr_data.mmr_type == 2 else 'Module User' if mmr_data.mmr_type == 3 else 'Super User' 
                        })
                else:
                    module_dict["user_type_details"] = collections.OrderedDict({})

                module_dict["module"] = collections.OrderedDict({
                    "id": mmr_data.mmr_module.id,
                    "cm_name": mmr_data.mmr_module.cm_name,
                    "cm_url": mmr_data.mmr_module.cm_url,
                    "cm_icon": "http://" + get_current_site(request).domain + mmr_data.mmr_module.cm_icon.url,
                })
                print('module_dict["module"]',module_dict["module"])
                print('dfdfdfffffffffffffffffffffffffffff')
                print('mmr_data.mmr_module',mmr_data.mmr_type)
                if(mmr_data.mmr_type == 1):
                    module_dict["role"] = collections.OrderedDict({})
        
                else:  
                    print(' mmr_data.mmr_role',  mmr_data.mmr_role)
                    if mmr_data.mmr_role:  
                        module_dict["role"] = collections.OrderedDict({
                            "id": mmr_data.mmr_role.id,
                            "cr_name": mmr_data.mmr_role.cr_name,
                            "cr_parent_id": mmr_data.mmr_role.cr_parent_id,
                        })
                    else:
                        module_dict["role"] = collections.OrderedDict()

                    if mmr_data.mmr_role: 
                        # print('e_tMasterModuleOther_other',type(e_tMasterModuleOther['mmo_other__id']))
                        tMasterOtherRole = TMasterOtherRole.objects.filter(
                            mor_role=mmr_data.mmr_role,
                            mor_is_deleted=False,
                            mor_other__cot_parent_id=0
                            #mor_other_id=e_tMasterModuleOther['mmo_other__id']
                        )
                        print('tMasterOtherRole', tMasterOtherRole)
                        if tMasterOtherRole:
                            tMasterModuleOther_list = list()
                            for e_tMasterOtherRole in tMasterOtherRole:
                                tMasterModuleOther_e_dict = dict()
                                tMasterModuleOther_e_dict['id'] = e_tMasterOtherRole.mor_other.id
                                tMasterModuleOther_e_dict['name'] = e_tMasterOtherRole.mor_other.cot_name
                                tMasterModuleOther_e_dict['parent'] = e_tMasterOtherRole.mor_other.cot_parent_id
                                tMasterModuleOther_e_dict['permission'] = e_tMasterOtherRole.mor_permissions.id if e_tMasterOtherRole.mor_permissions else 0
                                print('mmr_data.mmr_role.id',mmr_data.mmr_role.id)
                                tMasterModuleOther_e_dict['child_details'] = self.getChildOtherListForLogin(
                                    role_id=mmr_data.mmr_role.id,
                                    parent_other_id = e_tMasterOtherRole.mor_other.id )
                                tMasterModuleOther_list.append(tMasterModuleOther_e_dict)
                        else:
                            tMasterModuleOther_list = list()
                            #tMasterModuleOther_e_dict['child_details'] = 1
                        print('tMasterModuleOther_list',tMasterModuleOther_list)
                        #response.data['results'] = tMasterModuleOther_list
                    else:
                        tMasterModuleOther_list = list()
                    module_dict["object_details"] = tMasterModuleOther_list
                    print('module_dict["permissions"]',module_dict["object_details"])
                    applications.append(module_dict)
            if user:
                user_details = TCoreUserDetail.objects.get(cu_user=user)
                profile_pic = "http://" + get_current_site(
                    request).domain + user_details.cu_profile_img.url if user_details.cu_profile_img else ''
                odict = collections.OrderedDict()
                odict['user_id'] = user.pk
                odict['token'] = token.key
                odict['username'] = user.username
                odict['first_name'] = user.first_name
                odict['last_name'] = user.last_name
                odict['email'] = user.email
                odict['is_superuser'] = user.is_superuser
                #odict['cu_super_set'] = user_details.cu_super_set
                odict['cu_phone_no'] = user_details.cu_phone_no
                odict['cu_profile_img'] = profile_pic
                odict['cu_change_pass'] = user_details.cu_change_pass
                odict['module_access'] = applications
                odict['request_status'] = 1
                odict['msg'] = success_msg
                # print("REMOTE_ADDR: ", request.META.get('REMOTE_ADDR'))
                browser, ip, os = self.detectBrowser()
                log = LoginLogoutLoggedTable.objects.create(
                    user=user, token=token.key, ip_address=ip,browser_name=browser, os_name=os)
                print("log: ", log.id)
                return Response(odict)
        except Exception as e:
            print("error:", e)
            raise APIException({'request_status': 0, 'msg': e})

    def detectBrowser(self):
        import httpagentparser
        user_ip = self.request.META.get('REMOTE_ADDR')
        agent = self.request.environ.get('HTTP_USER_AGENT')
        browser = httpagentparser.detect(agent)
        browser_name = agent.split('/')[0] if not "browser" in browser.keys() else browser['browser']['name']
        os = "" if not "os" in browser.keys() else browser['os']['name']
        return browser_name, user_ip, os
    def getChildOtherListForLogin(self,role_id:int,parent_other_id: int = 0) -> list:
        try:
            print('role_id',role_id)
            #permissionList = TCorePermissions.objects.all().values('id', 'name')
            childlist = []
            childlist_data = TCoreOther.objects.filter(cot_parent_id=parent_other_id)
            #print('childlist_data',childlist_data)
            for child in childlist_data:
                data_dict = collections.OrderedDict()
                # print('child::',child)
                data_dict['id'] = child.id
                data_dict['cot_name'] = child.cot_name
                data_dict['description'] = child.description
                data_dict['cot_is_deleted'] = child.cot_is_deleted
                data_dict['cot_parent_id'] = child.cot_parent_id
                # print('child.id',type(child.id))
                tMasterOtherRole = TMasterOtherRole.objects.filter(
                    mor_role_id=role_id,
                    mor_other_id=child.id
                )
                data_dict['parent_permission'] = 0
                # Checking only child Permisson
                if tMasterOtherRole:
                    # print('tMasterOtherRole', tMasterOtherRole)
                    for e_tMasterOtherRole in tMasterOtherRole:
                        data_dict[
                            'permission'] = e_tMasterOtherRole.mor_permissions.id if e_tMasterOtherRole.mor_permissions else 0
                else:
                    data_dict['permission'] = 0
                data_dict['child_details'] = self.getChildOtherListForLogin(
                    role_id=role_id,
                    parent_other_id=child.id,
                )
                # print('data_dict:: ', data_dict)
                childlist.append(data_dict)
            return childlist
        except Exception as e:
            raise e

class UsersSignInListCreate(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    # pagination_class =CSPageNumberPagination
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer

class ChangePasswordView(generics.UpdateAPIView):
    """
    For changing password.
    password is changing using login user token.
    needs old password and new password,
    check old password is exiest or not
    if exiest than it works
    """
    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = (IsAuthenticated,)
    authentication_classes = [TokenAuthentication]

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user_data = self.request.user
            mail_id = user_data.email
            print('user',user_data)
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({'request_status': 1, 'msg': "Wrong password..."}, status=status.HTTP_400_BAD_REQUEST)
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            TCoreUserDetail.objects.filter(cu_user=self.request.user, cu_change_pass=True).update(
                cu_change_pass=False,password_to_know = serializer.data.get("new_password"))
            # ============= Mail Send ==============#
            if mail_id:
                mail_data = {
                            "name": user_data.first_name+ '' + user_data.last_name,
                            "password": serializer.data.get("new_password")
                    }
                mail_class = GlobleMailSend('CHP', [mail_id])
                mail_thread = Thread(target = mail_class.mailsend, args = (mail_data,))
                mail_thread.start()
            else:
                # ============= SMS Send ==============#
                cu_phone_no = TCoreUserDetail.objects.only('cu_phone_no').get(cu_user=user_data).cu_phone_no
                print('cu_phone_no',cu_phone_no)
                if cu_phone_no:
                    message_data = {
                        "password": serializer.data.get("new_password") 
                    }
                    sms_class = GlobleSmsSendTxtLocal('FP100',[cu_phone_no])
                    sms_thread = Thread(target = sms_class.sendSMS, args = (message_data,'sms'))
                    sms_thread.start()
            return Response({'request_status': 0, 'msg': "New Password Save Success..."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordWithUsernameView(generics.UpdateAPIView):
    """
    For changing password.
    password is changing using login user token.
    needs old password and new password,
    check old password is exiest or not
    if exiest than it works
    """
    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = (IsAuthenticated,)
    authentication_classes = [TokenAuthentication]

    def update(self, request, *args, **kwargs):
        #self.object = self.get_object()
        #serializer = self.get_serializer(data=request.data)
        username = self.request.data['username']
        #print('username',username)

        user_data = User.objects.get(username = username)
        print('user',user_data)

        new_password = self.request.data['new_password']
        user_data.set_password(new_password) 
        user_data.save()

        TCoreUserDetail.objects.filter(
            cu_user=user_data).update(
            cu_change_pass=False,password_to_know = new_password)

        # if not self.object.check_password(serializer.data.get("old_password")):
        #     return Response({'request_status': 1, 'msg': "Wrong password..."}, status=status.HTTP_400_BAD_REQUEST)
        # self.object.set_password(serializer.data.get("new_password"))
        # self.object.save()
        
        
        return Response({'request_status': 0, 'msg': "New Password Save Success..."}, status=status.HTTP_200_OK)

  


class Logout(APIView):
    """
        View for user logout
        And delete auth_token
        Using by login user token
        """

    def get(self, request, format=None):
        LoginLogoutLoggedTable.objects.filter(user=request.user, token=request.user.auth_token).update(
            logout_time=datetime.now())
        request.user.auth_token.delete()
        return Response({'request_status': 0, 'msg': "Logout Success..."}, status=status.HTTP_200_OK)

class ForgotPasswordView(APIView):
    """
    Forgot password using mail id ,
    randomly set password,
    mail send using thread,
    using post method
    """

    model = User
    permission_classes = []
    authentication_classes = []

    def post(self, request, format=None):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            mail_id = serializer.data.get("mail_id")
            cu_phone_no = serializer.data.get("cu_phone_no")
            password = 'Shyam@123'  # default password
            if mail_id:
                user_details_exiest = TCoreUserDetail.objects.filter(cu_user__email=mail_id)
            if cu_phone_no:
                user_details_exiest = TCoreUserDetail.objects.filter(cu_phone_no=cu_phone_no)
            #print("user_details_exiest",user_details_exiest)
            if user_details_exiest:
                for user_data in user_details_exiest:
                    user_data.cu_change_pass = True
                    user_data.password_to_know = password
                    fast_name = user_data.cu_user.first_name
                    last_name = user_data.cu_user.last_name
                    send_mail_to = user_data.cu_user.email
                    send_sms_to = user_data.cu_phone_no if user_data.cu_phone_no else ""
                    user_data.cu_user.set_password(password)  # set password...
                    user_data.cu_user.save()
                    user_data.save()
                    #print('user_data',user_data.cu_user.password)
                # ============= Mail Send ==============#
                if mail_id:
                    mail_data = {
                                "name": user_data.cu_user.first_name+ '' + user_data.cu_user.last_name,
                                "password": password
                        }
                    mail_class = GlobleMailSend('FP100', [mail_id])
                    mail_thread = Thread(target = mail_class.mailsend, args = (mail_data,))
                    mail_thread.start()
                # ============= SMS Send ==============#
                if cu_phone_no:
                    message_data = {
                        "password": password 
                    }
                    sms_class = GlobleSmsSendTxtLocal('FP100',[cu_phone_no])
                    sms_thread = Thread(target = sms_class.sendSMS, args = (message_data,'sms'))
                    sms_thread.start()
                
                return Response({'request_status': 1, 'msg': "New Password Save Success..."}, status=status.HTTP_200_OK)
            else:
                raise APIException({'request_status': 1, 'msg': "User does not exist."})

        return Response({'request_status': 0, 'msg': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class ActiveInactiveUserView(generics.RetrieveUpdateAPIView):
    """
    send parameter 'is_active'
    View for user update active and in_active
    using user ID
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = UserSerializer
    queryset = User.objects.all()

class EditUserView(generics.RetrieveUpdateAPIView):
    """
    View for user update
    using user ID
    login user and provided user must be same.. or must be admin
    email, cu_emp_code and username only change by admin
    if img is exist and need to update, than, it will be deleted fast and than update
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = EditUserSerializer
    lookup_field = 'cu_user_id'

    def get_queryset(self):
        user_id = self.kwargs["cu_user_id"]
        if str(self.request.user.id) == user_id or self.request.user.is_superuser:
            return TCoreUserDetail.objects.filter(cu_user_id=user_id)
        else:
            raise APIException({'request_status': 0, 'msg': 'Login user is different'})

class ModuleUserList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = TCoreUserDetail.objects.filter(cu_user__is_active=True,cu_user__is_superuser=False).order_by('-cu_user_id')
    serializer_class = UserModuleSerializer
    pagination_class = CSPageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('cu_user__username', 'cu_phone_no','cu_user__email','cu_emp_code',)
    def get_queryset(self):
        try:
            order_by = self.request.query_params.get('order_by', None)
            field_name = self.request.query_params.get('field_name', None)
            if order_by and order_by.lower() == 'desc' and field_name:
                queryset = self.queryset.order_by('-' + field_name)
            elif order_by and order_by.lower() == 'asc' and field_name:
                queryset = self.queryset.order_by(field_name)
            else:
                queryset = self.queryset
            return queryset.filter(~Q(cu_user_id=self.request.user.id))
        except Exception as e:
            # raise e
            raise APIException({'request_status': 0, 'msg': e})


class UserUpdateEmployeeCode(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = TCoreUserDetail.objects.filter(cu_user__is_active=True).order_by('cu_user_id')
    def post(self, request, format=None):
        data = [
        
        
        # {"username":"Ravi","cu_emp_code":"00000161"},
        # {"username":"vikash","cu_emp_code":"00000162"},
        # {"username":"rabindra","cu_emp_code":"00000163"},
        # {"username":"kushal","cu_emp_code":"00000061"},
        # {"username":"pranab","cu_emp_code":"00000104"},
        # {"username":"vikram","cu_emp_code":"10011290"},
        # {"username":"dinesh","cu_emp_code":"00000051"},
        # {"username":"shyamal","cu_emp_code":"00000079"},
        # {"username":"ankita","cu_emp_code":"00000531"},
        # {"username":"sujay","cu_emp_code":"00000040"},
        # {"username":"ajay","cu_emp_code":"00000300"},
        # {"username":"manoj","cu_emp_code":"00000064"},
        # {"username":"sayan","cu_emp_code":"00000636"},
        # {"username":"AVIJIT","cu_emp_code":"00000006"},
        # {"username":"abul","cu_emp_code":"00000039"},
        # {"username":"nikunj","cu_emp_code":"00000022"},
        # {"username":"Rahulg","cu_emp_code":"00000646"},





        # {"username":"sanket","cu_emp_code":"00000017"},
        # {"username":"ajaygupta","cu_emp_code":"00000003"},
        # {"username":"divakar","cu_emp_code":"00000377"},
        # {"username":"abhishekn","cu_emp_code":"00000184"},
        # {"username":"nikunjsharma","cu_emp_code":"00000203"},
        # {"username":"govind","cu_emp_code":"10011271"},
        # {"username":"rahul","cu_emp_code":"00000071"},
        # {"username":"MONICA","cu_emp_code":"00000242"},
        # {"username":"RAGHAV","cu_emp_code":"00000092"},
        # {"username":"SUKET","cu_emp_code":"00000018"},
        # {"username":"RAVIS","cu_emp_code":"00000026"},
        # {"username":"PUJAM","cu_emp_code":"00000637"},
        # {"username":"PRASENJIT","cu_emp_code":"00000281"},
        # {"username":"ANISH","cu_emp_code":"00000670"},
        # {"username":"LALIT","cu_emp_code":"10111036"},
        # {"username":"ARUP","cu_emp_code":"00000395"},
        # {"username":"SRIKANTA","cu_emp_code":"00000234"},
        # {"username":"BISWAJITCH","cu_emp_code":"00000212"},
        # {"username":"KAVITA","cu_emp_code":"00000623"},
        # {"username":"ARUNAVA","cu_emp_code":"00000527"},
        # {"username":"PRAHLAD","cu_emp_code":"00000023"},
        # {"username":"SUBIR_MITRA","cu_emp_code":"00000082"},
        # {"username":"BIPUL_KUMAR_DEY","cu_emp_code":"00000324"},
        # {"username":"CHIRANJIT_ROY","cu_emp_code":"00000452"},
        # {"username":"KAUSHIK_BISWAS","cu_emp_code":"00000059"},
        # {"username":"SUBHENDU_MUKHERJEE","cu_emp_code":"00000176"},
        # {"username":"SOUMEN_DAS","cu_emp_code":"00000320"},
        # {"username":"DIPAK_BARMAN","cu_emp_code":"00000167"},
        # {"username":"ASHIT_NAG","cu_emp_code":"00000166"},
        # {"username":"UTTAM_SARKAR","cu_emp_code":"00000201"},


        # {"username":"HIMADRI_BHOWMICK","cu_emp_code":"00000659"},
        # {"username":"SURAJ_PRAKASH_SHARMA","cu_emp_code":"00000186"},
        # {"username":"KALLOLBANDAPADHAYA","cu_emp_code":"00000056"},
        # {"username":"PALASH_MAZUMDER","cu_emp_code":"00000227"},
        # {"username":"GOUTAM_MITRA","cu_emp_code":"00000359"},
        # {"username":"KISHORkumar","cu_emp_code":"00000606"},
        # {"username":"KANHAIYA_RAJGARHIA","cu_emp_code":"00000641"},
        # {"username":"UP_BHATTACHARYA","cu_emp_code":"00000036"},
        # {"username":"MRINMOY_CHAKRABORTY","cu_emp_code":"00000252"},
        # {"username":"UMA_GHOSH","cu_emp_code":"00000135"},
        # {"username":"bikash_mallick","cu_emp_code":"00000225"},
        # {"username":"sumanta_pramanik","cu_emp_code":"00000144"},
        # {"username":"surajit_sengupta","cu_emp_code":"00000207"},
        # {"username":"anirban_patra","cu_emp_code":"00000666"},
        # {"username":"SOURAV_DEV","cu_emp_code":"00000687"},
        # {"username":"PARTHA_DAS","cu_emp_code":"00000111"},
        # {"username":"RABINDRANATH","cu_emp_code":"00000429"},
        # {"username":"ankit_agarwal","cu_emp_code":"00000376"},
        # {"username":"nilanjan_dasgupta","cu_emp_code":"00000419"},
        # {"username":"MIMI_MAZUMDAR","cu_emp_code":"00000711"},
        # {"username":"ankita_dasgupta","cu_emp_code":"00000720"},
        # {"username":"MAGAN_PATEL","cu_emp_code":"00000062"},
        # {"username":"DIBYENDU_GHOSH","cu_emp_code":"00000694"},
        # {"username":"BRINDABAN_SAHA","cu_emp_code":"00000692"},
        # {"username":"PALASH_JOTDER","cu_emp_code":"00000713"},
        # {"username":"TARAK_NATH_DAS","cu_emp_code":"00000689"},
        # {"username":"INDRAJIT_CHAKRABORTY","cu_emp_code":"00000693"},
        # {"username":"ARITRA_BOSE","cu_emp_code":"00000437"},
        # {"username":"MRINAL_GHOSH","cu_emp_code":"00000435"},
        # {"username":"TARAK_GHOSH","cu_emp_code":"00000710"},
        # {"username":"PRITHWISH_PATRA","cu_emp_code":"00000696"},
        # {"username":"INDRANIL_CHAKRABORTY","cu_emp_code":"00000702"},
        # {"username":"SABYASACHIROY","cu_emp_code":"00000422"},
        # {"username":"RAVI_KUMAR_VERMA","cu_emp_code":"00000539"},
        # {"username":"ARGHA_DEBNATH","cu_emp_code":"00000430"},
        # {"username":"DEBRAJ_MUKHERJEE","cu_emp_code":"00000418"},
        # {"username":"SHYAM_SUNDAR_DAS","cu_emp_code":"00000738"},
        # {"username":"Sonia_Basu","cu_emp_code":"00000736"},
        # {"username":"ANKAN_DAS","cu_emp_code":"00000730"},
        # {"username":"NIMAI_GHOSH","cu_emp_code":"00000734"},
        # {"username":"ANANTA_KUMAR_PAL","cu_emp_code":"00000735"},
        # {"username":"Gobindo_Basak","cu_emp_code":"00000352"},
        # {"username":"MANAS_MUKHERJEE","cu_emp_code":"00000455"},
        # {"username":"ankur_gupta","cu_emp_code":"00000744"},
        # {"username":"Siddharth","cu_emp_code":"00000016"},
        # {"username":"jagat","cu_emp_code":"00000750"},
        # {"username":"amitprosad","cu_emp_code":"00000740"},
        # {"username":"527","cu_emp_code":"00000756"},
        # {"username":"sanjibray","cu_emp_code":"00000755"},
        # {"username":"biswajitsaha","cu_emp_code":"00000767"},
        # {"username":"subhrangsusaha","cu_emp_code":"00000770"},
        # {"username":"sribeshbeltharia","cu_emp_code":"00000761"},
        # {"username":"dipannita","cu_emp_code":"00000772"},
        # {"username":"atanughosh","cu_emp_code":"00000771"},
        # {"username":"soumyadarshichanda","cu_emp_code":"00000778"},


        # {"username":"mousamghatak","cu_emp_code":"00000779"},
        # {"username":"subhaschandradas","cu_emp_code":"00000781"},
        # {"username":"supriyaghosh","cu_emp_code":"00000345"},
        # {"username":"arupghosh","cu_emp_code":"00000005"},
        # {"username":"bhabanibasu","cu_emp_code":"00000008"},
        # {"username":"samratsircar","cu_emp_code":"00000546"},
        # {"username":"ankurdas","cu_emp_code":"00000783"},


        #{"username":"himanshusampat","cu_emp_code":"00000774"},
        
        # {"username":"amitsahu","cu_emp_code":"00000366"},
        # {"username":"balmikiray","cu_emp_code":"00000497"},
        # {"username":"sushantabanerjee","cu_emp_code":"00000303"},
        # {"username":"mithileshpandey","cu_emp_code":"00000782"},
        # {"username":"ashishagarwal","cu_emp_code":"00000776"},
        # {"username":"varunagarwal","cu_emp_code":"00000777"},
        # {"username":"arihantbotara","cu_emp_code":"00000703"},
        # {"username":"bapichakraborty","cu_emp_code":"00000791"},
        # {"username":"abhishekbose","cu_emp_code":"00000215"},
        # {"username":"subhrasengupta","cu_emp_code":"00000518"},
        # {"username":"sujitgain","cu_emp_code":"00000084"},
        # {"username":"anusuyadas","cu_emp_code":"00000516"},
        # {"username":"rajeshyadav","cu_emp_code":"00000522"},
        # {"username":"sanjaylohia","cu_emp_code":"00000789"},
        # {"username":"monishgobindasen","cu_emp_code":"00000769"},
        # {"username":"rajkumarsasmal","cu_emp_code":"00000794"},
        # {"username":"purushottam","cu_emp_code":"00000168"},
        # {"username":"brijesh","cu_emp_code":"10111032"},
        # {"username":"mousumisarkar","cu_emp_code":"00000547"},
        # {"username":"sangitadey","cu_emp_code":"00000073"},



        # {"username":"chandrikaprasad","cu_emp_code":"00000156"},
        # {"username":"sumitrochaterjee","cu_emp_code":"00000722"},
        # {"username":"vijaykumarsharma","cu_emp_code":"00000037"},
        # {"username":"vinaykhaitan","cu_emp_code":"00000189"},
        # {"username":"tusharranjanmukherjee","cu_emp_code":"00000701"},
        # {"username":"AshokKumarGoenka","cu_emp_code":"00000001"},
        # {"username":"MilanKrishnaPal","cu_emp_code":"00000007"},
        # {"username":"GoutamSanfui","cu_emp_code":"00000021"},
        # {"username":"MrinalKantiDas","cu_emp_code":"00000032"},
        # {"username":"ArnabMukherjee","cu_emp_code":"00000046"},
        # {"username":"GoutamSaha","cu_emp_code":"00000063"},
        # {"username":"SanjibSingha","cu_emp_code":"00000076"},
        # {"username":"SaratChandraMazumder","cu_emp_code":"00000077"},
        

        # {"username":"SamirBoyed","cu_emp_code":"00000089"},
        # {"username":"AjoySarkar","cu_emp_code":"00000091"},
        # {"username":"AnupSamajdar","cu_emp_code":"00000094"},
        # {"username":"JyotirmoyBhattacharjee","cu_emp_code":"00000106"},
        # {"username":"PrasantaLaha","cu_emp_code":"00000113"},
        # {"username":"PrasantaRana","cu_emp_code":"00000114"},
        # {"username":"SudiptaPradhan","cu_emp_code":"00000129"},
        # {"username":"DineshChandraSarkar","cu_emp_code":"00000131"},
        # {"username":"SatishKumarJha","cu_emp_code":"00000146"},

        # {"username":"SandipKumarGayen","cu_emp_code":"00000147"},
        # {"username":"AnjanChakraborty","cu_emp_code":"00000150"},
        # {"username":"SupriyaMukherjee","cu_emp_code":"00000158"},
        
        #{"username":"DilipKumarJha","cu_emp_code":"00000195"},
        # {"username":"ArabindoDutta","cu_emp_code":"00000208"},
        # {"username":"JhulanBanerjee","cu_emp_code":"00000209"},
        # {"username":"RadhikaRanjanRahaRoy","cu_emp_code":"00000210"},
        # {"username":"SouravMitra","cu_emp_code":"00000216"},
        # {"username":"SoumenMitra","cu_emp_code":"00000226"},
        # {"username":"ManojSingh","cu_emp_code":"00000254"},

        # {"username":"ManickChandraDey","cu_emp_code":"00000274"},
        # {"username":"InamWaris","cu_emp_code":"00000275"},
        # {"username":"AjoyBanerjee","cu_emp_code":"00000283"},
        # {"username":"BiswajitDas","cu_emp_code":"00000331"},
        # {"username":"PratikKumarAgarwal","cu_emp_code":"00000334"},
        # {"username":"ArunangsuChowdhury","cu_emp_code":"00000368"},
        # {"username":"KuntalDatta","cu_emp_code":"00000369"},
        # {"username":"KartickPrasad","cu_emp_code":"00000372"},
        # {"username":"SunilKumarRoy","cu_emp_code":"00000383"},
        # {"username":"AnunayKumarDatta","cu_emp_code":"00000408"},
        # {"username":"AnudipDutta","cu_emp_code":"00000409"},
        # {"username":"SwapnenduMukherjee","cu_emp_code":"00000415"},



        # {"username":"PradipDas","cu_emp_code":"00000468"},
        # {"username":"AjayKumar","cu_emp_code":"00000471"},
        # {"username":"RupeshKumarMishra","cu_emp_code":"00000472"},
        # {"username":"ArunKumarRoy","cu_emp_code":"00000502"},
        # {"username":"DipanPoddar","cu_emp_code":"00000521"},
        # {"username":"RatanDas","cu_emp_code":"00000525"},
        # {"username":"BappaKundu","cu_emp_code":"00000541"},
        # {"username":"SwapanSarkar","cu_emp_code":"00000550"},
        # {"username":"KeshabDas","cu_emp_code":"00000558"},
        # {"username":"PappuRauth","cu_emp_code":"00000603"},
        # {"username":"RahulKumarSingh","cu_emp_code":"00000607"},
        # {"username":"AjoyAuddy","cu_emp_code":"00000621"},
        # {"username":"ManojKumarBhabhra","cu_emp_code":"00000625"},
        # {"username":"AmitLall","cu_emp_code":"00000639"},
        # {"username":"AshokeKumarBanerjee","cu_emp_code":"00000642"},
        # {"username":"BiswajitChowdhury","cu_emp_code":"00000661"},
        # {"username":"GauravDev","cu_emp_code":"00000669"},
        # {"username":"AtanuNandi","cu_emp_code":"00000676"},
        # {"username":"NishikantaMondal","cu_emp_code":"00000684"},
        # {"username":"RanjanBhaumik","cu_emp_code":"00000698"},
        # {"username":"PrakashMukherjee","cu_emp_code":"00000708"},
        # {"username":"SarmisthaPoddar","cu_emp_code":"00000725"},
        # {"username":"PujaSaha","cu_emp_code":"00000726"},
        # {"username":"GopalKrishnaSurai","cu_emp_code":"00000733"},
        # {"username":"DebashisRoy","cu_emp_code":"00000737"},
        # {"username":"SudiptaSaha","cu_emp_code":"00000746"},
        # {"username":"TarunRoychowdhury","cu_emp_code":"00000747"},
        # {"username":"AshokDas","cu_emp_code":"00000757"},
        # {"username":"SaikatBanerjee","cu_emp_code":"00000762"},
        # {"username":"SwarupMahapatra","cu_emp_code":"00000763"},
        # {"username":"ParijatNaskar","cu_emp_code":"00000766"},
        # {"username":"BalmikiDas","cu_emp_code":"00000904"},
        # {"username":"BiswajeetMondal","cu_emp_code":"00000615"},
        # {"username":"AnilKrishanaMondal","cu_emp_code":"00000906"},


        # {"username":"AbhoySingh","cu_emp_code":"00000407"},
        # {"username":"AnupKumarChakraborty","cu_emp_code":"00000509"},
        # {"username":"AtanuPandit","cu_emp_code":"00000205"},
        # {"username":"BiswajitDas.","cu_emp_code":"00000448"},
        # {"username":"GovindAgarwal","cu_emp_code":"00000185"},
        # {"username":"JaganathBanik","cu_emp_code":"10021004"},
        # {"username":"LalanSingh","cu_emp_code":"10041087"},
        # {"username":"MadhuGoel","cu_emp_code":"10112024"},
        # {"username":"PrabirKumarSarkar","cu_emp_code":"00000202"},
        # {"username":"PrasantaDas","cu_emp_code":"00000440"},
        # {"username":"RajiwRanjan","cu_emp_code":"00000354"},
        # {"username":"SaritaGoel","cu_emp_code":"10141006"},
        # {"username":"ShwetaKhaitan","cu_emp_code":"10111044"},
        # {"username":"ShyamSundarDubey","cu_emp_code":"00000170"},
        # {"username":"SumantaLat","cu_emp_code":"00000130"},
        # {"username":"SwetaGoel","cu_emp_code":"10112023"},
        # {"username":"TulikaBeriwal","cu_emp_code":"10111037"},
        # {"username":"VijaySahani","cu_emp_code":"00000416"},
        # {"username":"VikramGoel","cu_emp_code":"10141005"},
        # {"username":"DhirendraSingh","cu_emp_code":"00000804"},
        # {"username":"PulomaChatterjee","cu_emp_code":"00000802"},
        # {"username":"PayalMukherjee","cu_emp_code":"00000803"},
        # {"username":"SudhirRanjanDas","cu_emp_code":"00000808"},

        # {"username":"sanjay.rungta","cu_emp_code":"00000799"},
        # {"username":"sumitkumarbagaria","cu_emp_code":"00000795"},
        # {"username":"debrajdas","cu_emp_code":"00000811"},
        # {"username":"bitanbiswas","cu_emp_code":"00000812"},
        # {"username":"indrajitdas","cu_emp_code":"00000814"},
        # {"username":"BIKASHKUMARBANERJEE","cu_emp_code":"00000807"},
        # {"username":"SUROJITDAS","cu_emp_code":"00000813"},
        # {"username":"soumenduroy","cu_emp_code":"00000818"},
        # {"username":"nandadulalkoley","cu_emp_code":"00000819"},
        # {"username":"amitkumarsingh","cu_emp_code":"00000816"},
        # {"username":"ALOKESINHA","cu_emp_code":"00000824"},
        # {"username":"SAMRATSENGUPTA","cu_emp_code":"00000825"},
        # {"username":"SUBHRAMALLICK","cu_emp_code":"00000826"},
        # {"username":"nantupaul","cu_emp_code":"00000828"},
        # {"username":"rajibagarwal","cu_emp_code":"00000833"},
        # {"username":"MALAYKUMARMISHRA","cu_emp_code":"00000831"},
        # {"username":"snehaagarwal","cu_emp_code":"00000912"},
        # {"username":"shreyachatterjee","cu_emp_code":"00000840"},
        # {"username":"MonirulIslam","cu_emp_code":"00000834"},
        # {"username":"AnutoshMaity","cu_emp_code":"00000843"},


        # {"username":"SohamDey","cu_emp_code":"00000846"},
        # {"username":"JayKumarPramanik","cu_emp_code":"00000836"},
        # {"username":"GopinathDas","cu_emp_code":"00000913"},
        # {"username":"SriparnaSaha","cu_emp_code":"00000849"},
        # {"username":"MANASMUKHERJEE","cu_emp_code":"00000851"},
        # {"username":"RASUPADAPAL","cu_emp_code":"00000852"},
        # {"username":"Jordan_Marcar","cu_emp_code":"00000850"},
        # {"username":"AntaripaMondal","cu_emp_code":"00000854"},
        # {"username":"DibyenduSaha","cu_emp_code":"00000861"},
        # {"username":"KalyanMistri","cu_emp_code":"00000862"},
        # {"username":"RajneeshTiwari","cu_emp_code":"00000865"},
        # {"username":"ShibaniModi","cu_emp_code":"00000867"},
        # {"username":"BainabBasuDhar","cu_emp_code":"00000868"},
        # {"username":"HemantBothra","cu_emp_code":"00000869"},
        # {"username":"AbhijitPal","cu_emp_code":"00000872"},
        # {"username":"vinodkumarjain","cu_emp_code":"00000876"},


        # {"username":"SouvikMondal","cu_emp_code":"00000873"},
        # {"username":"PrabirBanerjee","cu_emp_code":"00000882"},
        # {"username":"TarakMajumder","cu_emp_code":"00000880"},
        # {"username":"JayantaRay","cu_emp_code":"00000881"},

        # {"username":"RAKESHMAHESHWARI","cu_emp_code":"00000885"},
        # {"username":"SHANKARMUKHERJEE","cu_emp_code":"00000890"},
        # {"username":"SOMNATHMISTRY","cu_emp_code":"00000889"},
        # {"username":"TUHINDAS","cu_emp_code":"00000888"},
        # {"username":"ANKITASETH","cu_emp_code":"00000887"},
        # {"username":"SOUMENSAHA","cu_emp_code":"00001504"},
        # {"username":"JIBANCHANDRACHAKRABORTY","cu_emp_code":"00000892"},
        # {"username":"SOUMITRABISWAS","cu_emp_code":"00000955"},
        # {"username":"SANJAYMAITY","cu_emp_code":"00000951"},
        # {"username":"JARIFUDDINKHAN","cu_emp_code":"00000953"},
        # {"username":"PRIYANKAKEDIA","cu_emp_code":"00000895"},
        # {"username":"PRAKASHPAL","cu_emp_code":"00000960"},
        # {"username":"SUHASMAJUMDER","cu_emp_code":"00000899"},
        # {"username":"AJAYSHANKARRAM","cu_emp_code":"00000900"},
        # {"username":"LAKSHMANBARAI","cu_emp_code":"00000965"},
        # {"username":"SUBRATADE","cu_emp_code":"00000958"},
        # {"username":"GAUTAMDAS","cu_emp_code":"00000706"},
        # {"username":"RAKESHSUROLIA ","cu_emp_code":"00000963"},
        # {"username":"SARWANBERIWAL","cu_emp_code":"00000728"},
        # {"username":"NIKUNJKEDIA","cu_emp_code":"00000775"},
        # {"username":"ASITGOSWAMI","cu_emp_code":"00000941"},
        # {"username":"MUNCHURSARDAR","cu_emp_code":"0000972"},
        # {"username":"ABDULHAMIDSEKH","cu_emp_code":"00000971"},
        # {"username":"SUTIRTHAKUNDU","cu_emp_code":"00000973"},
        # {"username":"ANURAKTISHARMA","cu_emp_code":"00000975"},
        # {"username":"PranKRISHNADas  ","cu_emp_code":"00000970"},
        # {"username":"GOLAMMORTAJAKHAN","cu_emp_code":"00000977"},
        # {"username":"NAINASINGH","cu_emp_code":"00000980"},
        # {"username":"SOUMIPAUL","cu_emp_code":"00000981"},
        # {"username":"PRANKURVARSHNEYA","cu_emp_code":"00000978"},
        # {"username":"ADITIMITRA ","cu_emp_code":"00000984"},
        # {"username":"SANJEEVJHA","cu_emp_code":"00000982"},
        # {"username":"SandeepKumar","cu_emp_code":"00000986"},
        # {"username":"ANILKUMARSINGH ","cu_emp_code":"00000985"},
        # {"username":"SubhasisKumarDey","cu_emp_code":"00000990"},


        # {"username":"AnantSingh","cu_emp_code":"00000994"},
        # {"username":"DipanwitaSen","cu_emp_code":"00000989"},
        # {"username":"AmitavaKundu","cu_emp_code":"00000993"},
        # {"username":"NupurPoddar","cu_emp_code":"00001001"},
        # {"username":"PrasenjitNath","cu_emp_code":"00000999"},
        # {"username":"SupravatHalder","cu_emp_code":"00001003"},
        # {"username":"PritamGhosh","cu_emp_code":"00001005"},
        # {"username":"MdHasanurRahaman","cu_emp_code":"00001006"},
        # {"username":"PuspenduMondal","cu_emp_code":"00001008"},
        # {"username":"PijushSinha","cu_emp_code":"00001010"},
        # {"username":"SahebMitra","cu_emp_code":"00001011"},
        # {"username":"SahidHoda","cu_emp_code":"00001012"},
        # {"username":"PreetamBhattacharjee","cu_emp_code":"00001009"},
        # {"username":"KoushikGoswami","cu_emp_code":"00000998"},
        # {"username":"SUSMITAKARMAKAR","cu_emp_code":"00001014"},
        # {"username":"Anirudh","cu_emp_code":"00001016"},
        # {"username":"Ashish.Agarwal","cu_emp_code":"00001017"},
        # {"username":"SukladeepGhosh","cu_emp_code":"00001015"},
        # {"username":"TonmoySardar","cu_emp_code":"00001019"},
        # {"username":"AlokeKumarRoy","cu_emp_code":"00001021"},
        # {"username":"JoydebDey","cu_emp_code":"00001018"},
        # {"username":"AshishLundia","cu_emp_code":"00001024"},
        # {"username":"BrindaPoddar","cu_emp_code":"00001022"},
        # {"username":"VikashPoddar","cu_emp_code":"00001028"},
        # {"username":"GaneshDas","cu_emp_code":"00001503"},
        # {"username":"PratapMondal","cu_emp_code":"00001502"},
        # {"username":"KritiBhattacharjee","cu_emp_code":"00001038"},
        # {"username":"PlabanChaudhury","cu_emp_code":"00001043"},
        # {"username":"SanandanPaul","cu_emp_code":"00001044"},
        # {"username":"Pijush_ Mondal","cu_emp_code":"00001505"},
        # {"username":"KasturiMukherjee","cu_emp_code":"00001045"},
        # {"username":"SnehasishDas","cu_emp_code":"00001046"},
        # {"username":"SudipRoy","cu_emp_code":"00001041"},
        # {"username":"KamalikaNath ","cu_emp_code":"00001042"},
        # {"username":"RISHAVKUMARMITTAL","cu_emp_code":"00001051"},
        # {"username":"YashwantKumarSomani","cu_emp_code":"00001052"},
        # {"username":"SuprasunDas","cu_emp_code":"00001049"},
        # {"username":"RanajitMajumder","cu_emp_code":"00001050"},
        # {"username":"SubirChandraGoswami","cu_emp_code":"00001053"},


        # {"username":"Mousumi_Sarkar","cu_emp_code":"00001055"},
        # {"username":"SubrataMondal","cu_emp_code":"00001056"},
        # {"username":"AmitDebnath","cu_emp_code":"00001057"},
        # {"username":"ProvasGhosh","cu_emp_code":"00001507"},
        # {"username":"BhaskarSardar","cu_emp_code":"00001508"},
        # {"username":"MithunThakur ","cu_emp_code":"00001065"},
        # {"username":"SouvikPaul","cu_emp_code":"00001064"},
        # {"username":"SkumarRajwarRajbanshi","cu_emp_code":"00001509"},
        # {"username":"PramodKumarSingh","cu_emp_code":"00001070"},
        # {"username":"RupamHazra","cu_emp_code":"00001063"},
        # {"username":"SubrataBala","cu_emp_code":"00001069"},
        # {"username":"abhishek_gupta","cu_emp_code":"00001054"},
        # {"username":"RajeshChourasia","cu_emp_code":"00001506"},
        # {"username":"SombuddhaDe","cu_emp_code":"00001072"},
        # {"username":"SanchitaDey","cu_emp_code":"00001076"},
        # {"username":"BinodJha","cu_emp_code":"00001078"},
        # {"username":"Sudhanshupathak","cu_emp_code":"00001080"},
        # {"username":"AshitSarkar","cu_emp_code":"00001511"},
        # {"username":"AvinandaGhosh","cu_emp_code":"00001090"},
        # {"username":"DebajyotiGoppi","cu_emp_code":"00001091"},
        # {"username":"BaisakhiMitra","cu_emp_code":"00001086"},
        # {"username":"SunandaMukherjee","cu_emp_code":"00001093"},
        # {"username":"ak.singh","cu_emp_code":"00001097"},
        # {"username":"GourabChatterjee","cu_emp_code":"00001100"},
        # {"username":"SurenBasak","cu_emp_code":"00001095"},
        # {"username":"BiprajitGhoshDastidar","cu_emp_code":"00001101"},
        # {"username":"SubhadipHalder","cu_emp_code":"00001103"},
        # {"username":"SusantoMondal","cu_emp_code":"00001106"},
        # {"username":"ROBINGUPTA","cu_emp_code":"00001108"},
        # {"username":"NishaGandhi","cu_emp_code":"00001111"},
        # {"username":"SuchismitaKundu","cu_emp_code":"00001110"},
        # {"username":"SHAYANTANIMITRA","cu_emp_code":"00001104"},
        # {"username":"MONIKANABISWAS","cu_emp_code":"00001112"},
        # {"username":"SudiptaGupta","cu_emp_code":"00001113"},
        # {"username":"AayushAgarwal","cu_emp_code":"00001118"},
        # {"username":"HemantaMondal","cu_emp_code":"00001117"},
        # {"username":"PalashBauri","cu_emp_code":"00001116"},
        # {"username":"SomaDas","cu_emp_code":"00001119"},
        # {"username":"AnilPrasad","cu_emp_code":"00001120"},
        # {"username":"ShuvankarGoutam","cu_emp_code":"00001122"},
        # {"username":"SubhojitChakraborty","cu_emp_code":"00001126"},
        # {"username":"RajaniLakhotia","cu_emp_code":"00001127"},
        # {"username":"JacobPDatta","cu_emp_code":"00001129"},
        # {"username":"TapanAcharjee","cu_emp_code":"00001130"},
        # {"username":"PriyantoDas","cu_emp_code":"00001132"},
        # {"username":"KishoreSaha","cu_emp_code":"00001131"},
        # {"username":"WasimSazzadNayek","cu_emp_code":"00001133"},
        # {"username":"SantanuNaskar","cu_emp_code":"00001135"},
        # {"username":"PriyankaGhosh","cu_emp_code":"00001138"},
        # {"username":"SandipSur","cu_emp_code":"00001136"},
        # {"username":"ArunMandi","cu_emp_code":"00001140"},
        # {"username":"ParthaMondal","cu_emp_code":"00001141"},
        # {"username":"KanhaGupta","cu_emp_code":"00001143"},
        # {"username":"ArpanRoy","cu_emp_code":"00001142"},
        # {"username":"SupratikBhattacharjee","cu_emp_code":"00001146"},
        # {"username":"SubrataHalder","cu_emp_code":"00001147"},
        # {"username":"SanjibKumar","cu_emp_code":"00001148"},
        # {"username":"TamalDas","cu_emp_code":"00001151"},
        # {"username":"IndranilChaudhuri","cu_emp_code":"00001149"},
        # {"username":"KalyanAcharya","cu_emp_code":"00001150"},
        # {"username":"JayantaMaity","cu_emp_code":"00001152"},
        # {"username":"ArpanHazra","cu_emp_code":"00001153"},
        # {"username":"RupeshKumarSingh","cu_emp_code":"00001155"},
        # {"username":"AdityaSarkar","cu_emp_code":"00001145"},
        # {"username":"SubhasisMaji","cu_emp_code":"00001156"},
        # {"username":"SouravTikadar","cu_emp_code":"00001158"},
        # {"username":"ArkoJyotiChanda","cu_emp_code":"00001162"},
        # {"username":"Samir_Samanta","cu_emp_code":"00001163"},
        # {"username":"KaranMukhi","cu_emp_code":"00001161"},
        # {"username":"SrilalMohta","cu_emp_code":"00001160"},
        # {"username":"ParthaMukherjee","cu_emp_code":"00001166"},
        # {"username":"SouvikNandy","cu_emp_code":"00001167"},
        # {"username":"GopalBiswas","cu_emp_code":"00001168"},
        # {"username":"RamKumarMahto","cu_emp_code":"00001169"},
        # {"username":"ArvindSinghNarwariya","cu_emp_code":"100110093"},


        #{"username":"SujoyChakraborty","cu_emp_code":"00001173"},
        
        # {"username":"SovanSen","cu_emp_code":"00001172"},
        # {"username":"SoumikDas","cu_emp_code":"00001175"},
        # {"username":"MokimSekh","cu_emp_code":"00001177"},
        # {"username":"Abhishekrajoriya","cu_emp_code":"100110103"},
        # {"username":"Soumyabhattacharya","cu_emp_code":"00001181"},
        # {"username":"Partharoy","cu_emp_code":"00001178"},
        # {"username":"Roshanjaiswal","cu_emp_code":"00001185"},
        # {"username":"Mohitbhaumick","cu_emp_code":"00001184"},
        # {"username":"Asimbhattacharyya","cu_emp_code":"00001182"},
        # {"username":"Sumankoley","cu_emp_code":"00001187"},
        # {"username":"Shyamaprasadghosh","cu_emp_code":"00001186"},
        # {"username":"AvinashKumarSingh","cu_emp_code":"00001191"},
        # {"username":"DanishRazaAlam","cu_emp_code":"100110132"},
        # {"username":"Sonalisom","cu_emp_code":"00001183"},
        # {"username":"Biswajithazra","cu_emp_code":"00001513"},
        # {"username":"Kanikakanodia","cu_emp_code":"00001190"},
        # {"username":"Prashantdamani","cu_emp_code":"00001193"},
        # {"username":"Samratnaskar","cu_emp_code":"00001188"},
        # {"username":"Pekhammukherjee","cu_emp_code":"00001195"},
        # {"username":"Subhajitadhikary","cu_emp_code":"00001196"},
        # {"username":"Sanjaymittal","cu_emp_code":"00001194"},
        # {"username":"Manjaralam","cu_emp_code":"00001198"},
        # {"username":"Chandrakantadey","cu_emp_code":"00001199"},


        # {"username":"Souravsaha","cu_emp_code":"00001204"},
        # {"username":"Amlanmondal","cu_emp_code":"00001203"},
        # {"username":"VikashKumarSingh","cu_emp_code":"00001202"},
        # {"username":"SubhrakantiGhosh","cu_emp_code":"00001200"},
        # {"username":"Souravdatta","cu_emp_code":"00001201"},
        # {"username":"Rahulpatidar","cu_emp_code":"100110128"},
        # {"username":"Mayankyadav","cu_emp_code":"100110129"},
        # {"username":"ManojKumaDas","cu_emp_code":"100110147"},
        # {"username":"Subirdas","cu_emp_code":"00001192"},
        # {"username":"SouravBikashMondal","cu_emp_code":"00001207"},
        # {"username":"MadhabKumarHazra","cu_emp_code":"00001206"},
        # {"username":"BibhuranjanHalder","cu_emp_code":"00001197"},
        # {"username":"AbhijitDas","cu_emp_code":"00001212"},
        # {"username":"SujashSengupta","cu_emp_code":"00001213"},
        # {"username":"PallabRoy","cu_emp_code":"00001214"},
        # {"username":"DebjitDas","cu_emp_code":"00001216"},
        # {"username":"ShailendraUmale","cu_emp_code":"00001218"},
        # {"username":"rohitkumarshaw","cu_emp_code":"00001215"},
        # {"username":"JayantaSujitDhar","cu_emp_code":"00001220"},
        # {"username":"SanghamitraDasgupta","cu_emp_code":"00001219"},
        # {"username":"SatarupaMitra","cu_emp_code":"00001223"},
        # {"username":"VinayKumarVerma","cu_emp_code":"100110168"},
        # {"username":"AvijitHalder","cu_emp_code":"00001222"},
        # {"username":"HrishikeshBagchi","cu_emp_code":"00001234"},
        # {"username":"NuralamIslam","cu_emp_code":"00001225"},
        # {"username":"PinkuGhoshChowdhury","cu_emp_code":"00001226"},
        # {"username":"AbhijitGhosh","cu_emp_code":"00001227"},
        # {"username":"SubrataGhosh","cu_emp_code":"00001230"},
        # {"username":"TamalChakraborty","cu_emp_code":"00001229"},
        # {"username":"JayantaMandal","cu_emp_code":"00001237"},
        # {"username":"SyedMofizulIslam","cu_emp_code":"00001238"},
        # {"username":"AneekKumarPal","cu_emp_code":"00001240"},
        # {"username":"AnantaSatpati","cu_emp_code":"00001236"},
        # {"username":"KaustavRoyChowdhury","cu_emp_code":"00001239"},
        # {"username":"Surojit_Das","cu_emp_code":"00001235"},
        # {"username":"HaranSeikh","cu_emp_code":"00001232"},
        # {"username":"AshutoshHalder","cu_emp_code":"00001231"},
        # {"username":"AmitSamui","cu_emp_code":"00001242"},
        # {"username":"NidhiDhelia","cu_emp_code":"00001244"},
        # {"username":"DipankarDey","cu_emp_code":"00001247"},
        # {"username":"Diptayan_Mayra","cu_emp_code":"00000964"},
        # {"username":"SanchitaDas","cu_emp_code":"00001246"},
        # {"username":"ArpanNandy","cu_emp_code":"00001243"},
        # {"username":"SangeetaMukherjee","cu_emp_code":"00001248"},
        # {"username":"DebasisRoy","cu_emp_code":"00001249"},
        # {"username":"GaurabKumarShekhar","cu_emp_code":"00001260"},
        # {"username":"ShibuSingha","cu_emp_code":"00001254"},
        # {"username":"SaikatMitra","cu_emp_code":"00001257"},
        # {"username":"SanjeetTiwari","cu_emp_code":"00001256"},
        # {"username":"SurajitRoy","cu_emp_code":"00001255"},
        # {"username":"PlabanMondal","cu_emp_code":"00001253"},
        # {"username":"SouravKundu","cu_emp_code":"00001251"},
        # {"username":"GaneshGhosh","cu_emp_code":"00001250"},
        # {"username":"RituparnaChakraborty","cu_emp_code":"00001264"},


        # {"username":"SudipKumarPaul","cu_emp_code":"00001263"},
        # {"username":"AmitKarmakar","cu_emp_code":"00001262"},
        # {"username":"VijaySinghal","cu_emp_code":"00001267"},
        # {"username":"SarvendraSingh","cu_emp_code":"0000110200"},
        # {"username":"ArghyaKumarKundu","cu_emp_code":"00001268"},
        # {"username":"MahakantoHari","cu_emp_code":"00001514"},
        # {"username":"DebasisMaity","cu_emp_code":"00001265"},
        # {"username":"AmitavaMitra","cu_emp_code":"00001275"},
        # {"username":"UjjalNandi","cu_emp_code":"00001280"},
        # {"username":"SujoyBhuiya","cu_emp_code":"00001276"},
        # {"username":"MangalDas","cu_emp_code":"00001274"},
        # {"username":"AzadSaw","cu_emp_code":"00001269"},
        # {"username":"RakhahariBiswas","cu_emp_code":"00001266"},
        # {"username":"KiranMondal","cu_emp_code":"00001970"},
        # {"username":"papychowdhury","cu_emp_code":"00001279"},
        # {"username":"MadhurimaRoy","cu_emp_code":"00001278"},
        # {"username":"AvijitKumarChoubey","cu_emp_code":"00001283"},
        # {"username":"RahulBiswas","cu_emp_code":"00001281"},
        # {"username":"RajeshPrasad","cu_emp_code":"00001261"},
        # {"username":"PintuGarai","cu_emp_code":"00001273"},
        # {"username":"RakeshKumarYadav","cu_emp_code":"00001284"},
        # {"username":"ChandanChoudhury","cu_emp_code":"00001285"},
        # {"username":"GoutamSarkar","cu_emp_code":"00001287"},
        # {"username":"KoushikMaity","cu_emp_code":"00001288"},
        # {"username":"SurajitMondal","cu_emp_code":"00001291"},
        # {"username":"RajibThakur","cu_emp_code":"00001286"},
        # {"username":"PrateekGupta","cu_emp_code":"00001293"},
        # {"username":"AbhisekSingh","cu_emp_code":"00001294"},
        # {"username":"ArunHari","cu_emp_code":"00001515"},
        # {"username":"SubrataSarkar","cu_emp_code":"00001295"},
        # {"username":"SouravGhosh","cu_emp_code":"00001298"},
        # {"username":"ManasPaul","cu_emp_code":"00001297"},
        # {"username":"ChandanSarkar","cu_emp_code":"00001299"},
        # {"username":"SuswagataSarkar","cu_emp_code":"00001300"},
        # {"username":"SrijitSimlai","cu_emp_code":"00001304"},
        # {"username":"SagnikSinghaRoy","cu_emp_code":"00001290"},
        # {"username":"PradhyumanOjha","cu_emp_code":"00001296"},
        # {"username":"DollGupta","cu_emp_code":"00001302"},
        # {"username":"MainakMaji","cu_emp_code":"00001303"},
        # {"username":"PoojaSaha","cu_emp_code":"00001307"},
        # {"username":"MehediHasanKhan","cu_emp_code":"00001306"},
        # {"username":"RahulSengupta","cu_emp_code":"00001301"},
        # {"username":"AfsarKhan","cu_emp_code":"00001308"},
        # {"username":"TamalSarkar","cu_emp_code":"00001305"},
        # {"username":"AditionKumar","cu_emp_code":"00001310"},
        # {"username":"Manish_Kumar_Singh","cu_emp_code":"00001309"},
        # {"username":"BikramBittar","cu_emp_code":"00001516"},
        # {"username":"KunalDutta","cu_emp_code":"00001313"},
        # {"username":"ArghyaMitra","cu_emp_code":"00001312"},
        # {"username":"MintuDas","cu_emp_code":"00001314"},
        # {"username":"ShyamaliDas","cu_emp_code":"00001317"},
        # {"username":"UditaChowdhary","cu_emp_code":"00001318"},
        # {"username":"PrabirKumarDas","cu_emp_code":"00001316"},
        # {"username":"SwarnenduRoy","cu_emp_code":"00001320"},
        # {"username":"AnilKumarGoenka","cu_emp_code":"00001322"},
        # {"username":"ShashiRanjanPandey","cu_emp_code":"00001315"},
        # {"username":"DebapriyaDas","cu_emp_code":"00001324"},
        # {"username":"RiyaBansal","cu_emp_code":"00001329"},
        # {"username":"Swapan_Banerjee","cu_emp_code":"00001328"},
        # {"username":"Deepak_Kumar","cu_emp_code":"00001327"},
        # {"username":"MithileshKumarPal","cu_emp_code":"00001326"},
        # {"username":"AmritGupta","cu_emp_code":"00001321"},
        # {"username":"RishabhSekhani","cu_emp_code":"00001331"},
        # {"username":"RameshChowhan","cu_emp_code":"00001330"},
        # {"username":"SanjoyGhosh","cu_emp_code":"00001335"},
        # {"username":"SubhomoyKar","cu_emp_code":"00001333"},
        # {"username":"ShashiKumarGupta","cu_emp_code":"00001336"},
        # {"username":"DhiresAcharyya","cu_emp_code":"00001337"},
        # {"username":"SubhenduChatterjee","cu_emp_code":"00001338"},


        # {"username":"Subrata_Ghosh","cu_emp_code":"00001517"},
        # {"username":"BubaiDas","cu_emp_code":"00001325"},
        # {"username":"AnkitMadhogaria","cu_emp_code":"00001340"},
        # {"username":"Ajay_Sharma","cu_emp_code":"00001339"},
        # {"username":"SumanMazumder","cu_emp_code":"00001341"},
        # {"username":"SarjuRouth","cu_emp_code":"00001519"},
        # {"username":"sankarprasadrouth","cu_emp_code":"00001518"},
        # {"username":"Manoj_Kumar_Das","cu_emp_code":"00001343"},
        # {"username":"SupratimDas","cu_emp_code":"00001348"},
        # {"username":"GouravChoudhary","cu_emp_code":"00001344"},
        # {"username":"SutanuChakraborty","cu_emp_code":"00001345"},
        # {"username":"DipanjanDe","cu_emp_code":"00001342"},
        # {"username":"TwinkleBaidya","cu_emp_code":"00001347"},
        # {"username":"AnujAgarwal","cu_emp_code":"00001352"},
        # {"username":"Amit_Kumar_Singh","cu_emp_code":"00001353"},
        # {"username":"ArunashisMondal","cu_emp_code":"00001349"},
        # {"username":"MadhuparnaMitra","cu_emp_code":"00001354"},
        # {"username":"PriyankaGupta","cu_emp_code":"00001357"},
        # {"username":"ArupNath","cu_emp_code":"00001355"},
        # {"username":"RajibChakraborty","cu_emp_code":"00001362"},
        # {"username":"SouvikNath","cu_emp_code":"00001356"},
        # {"username":"AkashDas","cu_emp_code":"00001360"},
        # {"username":"PratickChakraborty","cu_emp_code":"00001358"},
        # {"username":"SuvodeepGupta","cu_emp_code":"00001359"},
        # {"username":"Subrata.Ghosh","cu_emp_code":"00001363"},
        # {"username":"SisirPalit","cu_emp_code":"00001521"},
        # {"username":"AnuradhaTiwari","cu_emp_code":"00001367"},
        # {"username":"ArindamChakrabarty","cu_emp_code":"00001365"},
        # {"username":"AbhishekJain","cu_emp_code":"00001372"},
        # {"username":"SubrataPal","cu_emp_code":"00001369"},
        # {"username":"RiyaGhosh","cu_emp_code":"00001368"},
        # {"username":"ManasBanerjee","cu_emp_code":"00001371"},
        # {"username":"SubhajitSabui","cu_emp_code":"00001370"},
        # {"username":"SurajRajvor","cu_emp_code":"00001373"},
        # {"username":"AvijitRoy","cu_emp_code":"00001366"},
        # {"username":"SumanSheikh","cu_emp_code":"00001364"},
        # {"username":"ShahbazReyazKhan","cu_emp_code":"00001374"},
        # {"username":"JayantMitra","cu_emp_code":"00001377"},
        # {"username":"SourabhSaha","cu_emp_code":"00001378"},
        # {"username":"RajarshiBanerjee","cu_emp_code":"00001375"},
        # {"username":"Surajit.Mandal","cu_emp_code":"00001376"},
        # {"username":"AmarDas","cu_emp_code":"00001522"},
        # {"username":"ShreyaBothra","cu_emp_code":"00001379"},
        # {"username":"DipakBasak","cu_emp_code":"00001523"},
        # {"username":"AsutoshSharma","cu_emp_code":"00001391"},
        # {"username":"JaiprakashSingh","cu_emp_code":"00001392"},
        # {"username":"RajdeepSinha","cu_emp_code":"00001383"},
        # {"username":"BabuaGhorai","cu_emp_code":"00001390"},
        # {"username":"SoumickSett","cu_emp_code":"00001389"},
        # {"username":"PratikMukherjee","cu_emp_code":"00001387"},
        # {"username":"NiteshKumarYadav","cu_emp_code":"00001386"},
        # {"username":"AmirAsad","cu_emp_code":"00001384"},
        # {"username":"GaruravPandey","cu_emp_code":"00001382"},
        # {"username":"GoluTulshyan","cu_emp_code":"00001381"},
        # {"username":"ManabDas","cu_emp_code":"00001380"},
        # {"username":"testuser_shail","cu_emp_code":"00444756"},
        # {"username":"AmitBiswas","cu_emp_code":"00001398"},
        # {"username":"ArpitaGhosh","cu_emp_code":"00001395"},
        # {"username":"RajatSadhukhan","cu_emp_code":"00001394"},
        # {"username":"AvijitMandal","cu_emp_code":"00001397"},
        # {"username":"ManishKumarSrivastava","cu_emp_code":"00001401"},
        # {"username":"ChaitaliBera","cu_emp_code":"00001402"},
        # {"username":"AsifImranDafadar","cu_emp_code":"00001404"},
        # {"username":"RanajoyBhattacharjee","cu_emp_code":"00001403"},
        # {"username":"AnkurPatwari","cu_emp_code":"00001396"},
        # {"username":"AnupamPatra","cu_emp_code":"00001399"},
        # {"username":"PoulomiGhosh","cu_emp_code":"00001400"},
        # {"username":"TanujBhargava","cu_emp_code":"100000110276"},
        # {"username":"ManasMishra","cu_emp_code":"00001407"},
        # {"username":"Sumit_Kumar","cu_emp_code":"00001406"},
        # {"username":"VimalKumarBothra","cu_emp_code":"00001405"},
        # {"username":"MahaswetaMukherjee","cu_emp_code":"00001408"},
        # {"username":"PawanKumarPatwari","cu_emp_code":"00001412"},
        # {"username":"PragatiAgarwal","cu_emp_code":"00001413"},
        # {"username":"SoumyasriJana","cu_emp_code":"00001411"},
        # {"username":"EnakshiGoswami","cu_emp_code":"00001415"},
        # {"username":"Sanjay_Das","cu_emp_code":"00001409"},
        # {"username":"TimonGhosh","cu_emp_code":"00001410"},
        # {"username":"MrityunjayKumarMishra","cu_emp_code":"1000000110275"},
        # {"username":"ChanchalDas","cu_emp_code":"00001414"},
        # {"username":"Biswajit.Das","cu_emp_code":"00001417"},
        # {"username":"KulwinderSinghToor","cu_emp_code":"00001418"},
        # {"username":"KrishnaMurariKumar","cu_emp_code":"00111490"},
        # {"username":"RameshMallick","cu_emp_code":"00001388"},
        # {"username":"TapasMondal","cu_emp_code":"00001525"},
        # {"username":"RajitNayak","cu_emp_code":"00001524"},
        # {"username":"AmitGhosh","cu_emp_code":"00001420"},
        # {"username":"AhadurRahamanReza","cu_emp_code":"00001421"},
        # {"username":"ManojJaiswal","cu_emp_code":"00001422"},
        # {"username":"BikashChandraMondal","cu_emp_code":"00001423"},
        # {"username":"TanushreeRoy","cu_emp_code":"00001424"},
        # {"username":"SaswatiRoy","cu_emp_code":"00001425"},
        # {"username":"PurnenduSengupta","cu_emp_code":"00001429"},
        # {"username":"KiranChhetri","cu_emp_code":"00001428"},
        # {"username":"PrakashManiTripathi","cu_emp_code":"00001430"},
        # {"username":"AmitGhoshDostider","cu_emp_code":"00001520"},
        # {"username":"PrachiMittal","cu_emp_code":"00001431"},
        # {"username":"SubhajitDas","cu_emp_code":"00001432"},
        # {"username":"RanjabatiChatterjee","cu_emp_code":"00001427"},


        # {"username":"RavindraKumarJha","cu_emp_code":"00001171"}, ##nei
        # {"username":"ManishGoel","cu_emp_code":"00000171"}, #nei
        # {"username":"surojitdasgupta","cu_emp_code":"00000087"}, ## nei
        # {"username":"ShouvikMukherjee","cu_emp_code":"00001426"}, ##nei
        # {"username":"SoumyaProbhatRoy","cu_emp_code":"00001433"}, ##nei
        # {"username":"AnkitBajoria","cu_emp_code":"00001434"},
        # {"username":"Animesh.Das","cu_emp_code":"00001435"},
        # {"username":"Joy.Laha","cu_emp_code":"00001437"},
        # {"username":"AtulSharma","cu_emp_code":"00001436"},
        # {"username":"RakeshAgarwal","cu_emp_code":"00001439"},
        # {"username":"AnimeshMandal","cu_emp_code":"00001442"},
        # {"username":"DibakarDas","cu_emp_code":"00001438"},
        # {"username":"SubhankarHalder","cu_emp_code":"00001440"},
        # {"username":"ArijitDe","cu_emp_code":"00001443"},
        # {"username":"AvijitDas","cu_emp_code":"00001441"},
        # {"username":"Ajay_Kumar","cu_emp_code":"1000000110301"},
        # #{"username":"MainakMukherjee","cu_emp_code":"00001444"},
        # {"username":"JitendraKumarJha","cu_emp_code":"00001446"},
        # {"username":"HimanshuSekharSahoo","cu_emp_code":"00001445"},
        # {"username":"Prosenjit_Das","cu_emp_code":"00001448"},
        # {"username":"SubhadeepSengupta","cu_emp_code":"00001450"},
        # {"username":"DibyakantiDasgupta","cu_emp_code":"00001451"},
        # {"username":"ArpitaRoyChowdhury","cu_emp_code":"00001452"}
        ]

        for d in data:
            #print('d',d['username'])
            ud = User.objects.get(username__iexact= d['username'])
            print('ud',ud)
            TCoreUserDetail.objects.filter(cu_user=ud).update(cu_emp_code=d['cu_emp_code'])

class UserPermissionEditView(generics.RetrieveUpdateAPIView):
    """
    View for user update
    using user ID
    login user and provided user must be same.. or must be admin
    email, cu_emp_code and username only change by admin
    if img is exist and need to update, than, it will be deleted fast and than update
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = UserPermissionEditSerializer
    lookup_field = 'cu_user_id'

    def get_queryset(self):
        user_id = self.kwargs["cu_user_id"]
        result = TCoreUserDetail.objects.filter(cu_user_id=user_id)
        #print('result',result)
        return result

class LoginAuthTokenNew(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        try:
            #request = self.context.get('request')
            #print('request',request)
            error_msg = "Unable to log in with provided credentials .."
            suspended_msg = "user is suspended .."
            success_msg = "Log in Successfully .."
            # ===========================for contact_no=========================== #
            from django.http import QueryDict

            try:
                request_dict = request.data.dict()
            except Exception as e:
                print("error on request_dict 111: ", e)
                request_dict = request.data


            request_dict['username'] = request_dict['username']
            request_dict['password'] = request_dict['password']
            #print('username',request_dict['username'])
            # ===========================for is_active check=========================== #
            user_status = TCoreUserDetail.objects.filter(
                Q(cu_user__username=request_dict['username']) | Q(cu_phone_no=request_dict['username'])).values(
                "cu_user__is_active")
            #print("user_status: ", user_status)
            if user_status:
                for u_data in user_status:
                    # print("u_data: ", u_data)
                    if not u_data['cu_user__is_active']:
                        raise APIException(suspended_msg)
            else:
                raise APIException(error_msg)
            # ===========================for is_active check=========================== # comment by Rupam
            # if request_dict['username'].isnumeric() and len(request_dict['username']) <= 15:
            #     # print("request_dict['username']:::: ", request_dict['username'])
            #     user_details_data = TCoreUserDetail.objects.filter(cu_phone_no=int(request_dict['username'])) \
            #         .values("cu_user__username")
            #     # print("fgdfgdf: ",list(user_details_data)[0]['cu_user__username'])
            #     data = "username={}&password={}".format(str(list(user_details_data)[0]['cu_user__username']),
            #                                             request_dict['password'])
            #     request_dict = QueryDict(data)


            # ===========================for credentials check=========================== #
            try:
                response = super(LoginAuthTokenNew, self).post(request_dict, *args, **kwargs)
            except Exception as error:
                print("error: ", error)
                raise APIException(error_msg)
            # ===========================for credentials check=========================== #
            # ===========================for contact_no=========================== #
            # response = super(LoginAuthToken, self).post(request, *args, **kwargs)
            #print("request_qdict: ", request_dict)
            token = Token.objects.get(key=response.data['token'])
            #print("token: ", token)
            user = User.objects.get(id=token.user_id)
            #print("user: ", user)
            update_last_login(None, user)
            serializer = UserLoginSerializer(user, many=True)
            #print('sdsdsdsdsdsdsdsdsdsdsdsdsd')
            mmr_details = TMasterModuleRoleUser.objects.filter(mmr_user=user)
            print('mmr_details',mmr_details)
            applications = list()
            for mmr_data in mmr_details:
                #print('mmr_details111111',mmr_data)
                module_dict = collections.OrderedDict()
                module_dict["id"] = mmr_data.id
                #print('module_dict',module_dict)
                #print('type(mmr_data.mmr_type)',mmr_data.mmr_type)
                if mmr_data.mmr_type:
                    module_dict["user_type_details"] =  collections.OrderedDict({
                        "id":mmr_data.mmr_type,
                        "name": 'Module Admin' if mmr_data.mmr_type == 2 else 'Module User' if mmr_data.mmr_type == 3 else 'Demo User' if mmr_data.mmr_type == 6 else 'Super User'
                        })
                else:
                    module_dict["user_type_details"] = collections.OrderedDict({})

                module_dict["module"] = collections.OrderedDict({
                    "id": mmr_data.mmr_module.id,
                    "cm_name": mmr_data.mmr_module.cm_name,
                    "cm_url": mmr_data.mmr_module.cm_url,
                    "cm_icon": request.build_absolute_uri(mmr_data.mmr_module.cm_icon.url),
                    #"cm_icon": "http://" + get_current_site(request).domain + mmr_data.mmr_module.cm_icon.url,
                })
                #print('module_dict["module"]',module_dict["module"])
                print('dfdfdfffffffffffffffffffffffffffff')
                print('mmr_data.mmr_module',mmr_data.mmr_type)
                if(mmr_data.mmr_type == 1):
                    module_dict["role"] = collections.OrderedDict({})
        
                else:  
                    print(' mmr_data.mmr_role',  mmr_data.mmr_role)
                    if mmr_data.mmr_role:  
                        module_dict["role"] = collections.OrderedDict({
                            "id": mmr_data.mmr_role.id,
                            "cr_name": mmr_data.mmr_role.cr_name,
                            "cr_parent_id": mmr_data.mmr_role.cr_parent_id,
                        })
                    else:
                        module_dict["role"] = collections.OrderedDict()

                    if mmr_data.mmr_role: 
                        # print('e_tMasterModuleOther_other',type(e_tMasterModuleOther['mmo_other__id']))
                        tMasterOtherRole = TMasterOtherUser.objects.filter(
                            #mor_role=mmr_data.mmr_role,
                            mou_user = user,
                            mou_is_deleted=False,
                            mou_other__cot_parent_id=0
                            #mor_other_id=e_tMasterModuleOther['mmo_other__id']
                        )
                        print('tMasterOtherRole', tMasterOtherRole)
                        if tMasterOtherRole:
                            tMasterModuleOther_list = list()
                            for e_tMasterOtherRole in tMasterOtherRole:
                                tMasterModuleOther_e_dict = dict()
                                tMasterModuleOther_e_dict['id'] = e_tMasterOtherRole.mou_other.id
                                tMasterModuleOther_e_dict['name'] = e_tMasterOtherRole.mou_other.cot_name
                                tMasterModuleOther_e_dict['parent'] = e_tMasterOtherRole.mou_other.cot_parent_id
                                tMasterModuleOther_e_dict['permission'] = e_tMasterOtherRole.mou_permissions.id if e_tMasterOtherRole.mou_permissions else 0
                                #print('mmr_data.mmr_role.id',mmr_data.mmr_role.id)
                                tMasterModuleOther_e_dict['child_details'] = self.getChildOtherListForLogin(
                                    role_id=mmr_data.mmr_role.id,
                                    parent_other_id = e_tMasterOtherRole.mou_other.id )
                                tMasterModuleOther_list.append(tMasterModuleOther_e_dict)
                        else:

                            tMasterOtherRole = TMasterOtherRole.objects.filter(
                                                mor_role=mmr_data.mmr_role,
                                                #mou_user = user,
                                                mor_is_deleted=False,
                                                mor_other__cot_parent_id=0
                                                #mor_other_id=e_tMasterModuleOther['mmo_other__id']
                                                )
                            #print('tMasterOtherRole', tMasterOtherRole)
                            if tMasterOtherRole:
                                tMasterModuleOther_list = list()
                                for e_tMasterOtherRole in tMasterOtherRole:
                                    tMasterModuleOther_e_dict = dict()
                                    tMasterModuleOther_e_dict['id'] = e_tMasterOtherRole.mor_other.id
                                    tMasterModuleOther_e_dict['name'] = e_tMasterOtherRole.mor_other.cot_name
                                    tMasterModuleOther_e_dict['parent'] = e_tMasterOtherRole.mor_other.cot_parent_id
                                    tMasterModuleOther_e_dict['permission'] = e_tMasterOtherRole.mor_permissions.id if e_tMasterOtherRole.mor_permissions else 0
                                    #print('mmr_data.mmr_role.id',mmr_data.mmr_role.id)
                                    tMasterModuleOther_e_dict['child_details'] = self.getChildOtherListForRoleLogin(
                                        role_id=mmr_data.mmr_role.id,
                                        parent_other_id = e_tMasterOtherRole.mor_other.id )
                                    tMasterModuleOther_list.append(tMasterModuleOther_e_dict)

                            else:
                                tMasterModuleOther_list = list()
                            #tMasterModuleOther_e_dict['child_details'] = 1
                        #print('tMasterModuleOther_list',tMasterModuleOther_list)
                        #response.data['results'] = tMasterModuleOther_list
                    else:
                        tMasterModuleOther_list= list()
                    module_dict["object_details"] = tMasterModuleOther_list
                    #print('module_dict["permissions"]',module_dict["object_details"])
                    applications.append(module_dict)
            if user:
                user_details = TCoreUserDetail.objects.get(cu_user=user)
                # profile_pic = "http://" + get_current_site(
                #     request).domain + user_details.cu_profile_img.url if user_details.cu_profile_img else ''
                profile_pic = request.build_absolute_uri(user_details.cu_profile_img.url) if user_details.cu_profile_img else ''
                odict = collections.OrderedDict()
                odict['user_id'] = user.pk
                odict['token'] = token.key
                odict['username'] = user.username
                odict['first_name'] = user.first_name
                odict['last_name'] = user.last_name
                odict['email'] = user.email
                odict['job_location_state'] = user_details.job_location_state.id if user_details.job_location_state else None
                odict['is_superuser'] = user.is_superuser
                #odict['cu_super_set'] = user_details.cu_super_set
                odict['cu_phone_no'] = user_details.cu_phone_no
                odict['cu_profile_img'] = profile_pic
                odict['cu_change_pass'] = user_details.cu_change_pass
                odict['module_access'] = applications
                odict['request_status'] = 1
                odict['msg'] = success_msg
                # print("REMOTE_ADDR: ", request.META.get('REMOTE_ADDR'))
                browser, ip, os = self.detectBrowser()
                log = LoginLogoutLoggedTable.objects.create(
                    user=user, token=token.key, ip_address=ip,browser_name=browser, os_name=os)
                print("log: ", log.id)
                return Response(odict)
        except Exception as e:
            print("error:", e)
            raise APIException({'request_status': 0, 'msg': e})

    def detectBrowser(self):
        import httpagentparser
        user_ip = self.request.META.get('REMOTE_ADDR')
        agent = self.request.environ.get('HTTP_USER_AGENT')
        browser = httpagentparser.detect(agent)
        browser_name = agent.split('/')[0] if not "browser" in browser.keys() else browser['browser']['name']
        os = "" if not "os" in browser.keys() else browser['os']['name']
        return browser_name, user_ip, os
    
    def getChildOtherListForLogin(self,role_id:int,parent_other_id: int = 0) -> list:
        try:
            print('role_id',role_id)
            #permissionList = TCorePermissions.objects.all().values('id', 'name')
            childlist = []
            childlist_data = TCoreOther.objects.filter(cot_parent_id=parent_other_id)
            #print('childlist_data',childlist_data)
            for child in childlist_data:
                data_dict = collections.OrderedDict()
                # print('child::',child)
                data_dict['id'] = child.id
                data_dict['cot_name'] = child.cot_name
                data_dict['description'] = child.description
                data_dict['cot_is_deleted'] = child.cot_is_deleted
                data_dict['cot_parent_id'] = child.cot_parent_id
                # print('child.id',type(child.id))
                tMasterOtherRole = TMasterOtherUser.objects.filter(
                    #mou_role_id=role_id,
                    mou_other_id=child.id
                )
                data_dict['parent_permission'] = 0
                # Checking only child Permisson
                if tMasterOtherRole:
                    # print('tMasterOtherRole', tMasterOtherRole)
                    for e_tMasterOtherRole in tMasterOtherRole:
                        data_dict[
                            'permission'] = e_tMasterOtherRole.mou_permissions.id if e_tMasterOtherRole.mou_permissions else 0
                else:
                    data_dict['permission'] = 0
                data_dict['child_details'] = self.getChildOtherListForLogin(
                    role_id=role_id,
                    parent_other_id=child.id,
                )
                # print('data_dict:: ', data_dict)
                childlist.append(data_dict)
            return childlist
        except Exception as e:
            raise e
    
    def getChildOtherListForRoleLogin(self,role_id:int,parent_other_id: int = 0) -> list:
        try:
            print('role_id',role_id)
            #permissionList = TCorePermissions.objects.all().values('id', 'name')
            childlist = []
            childlist_data = TCoreOther.objects.filter(cot_parent_id=parent_other_id)
            #print('childlist_data',childlist_data)
            for child in childlist_data:
                data_dict = collections.OrderedDict()
                # print('child::',child)
                data_dict['id'] = child.id
                data_dict['cot_name'] = child.cot_name
                data_dict['description'] = child.description
                data_dict['cot_is_deleted'] = child.cot_is_deleted
                data_dict['cot_parent_id'] = child.cot_parent_id
                # print('child.id',type(child.id))
                tMasterOtherRole = TMasterOtherRole.objects.filter(
                    mor_role_id=role_id,
                    mor_other_id=child.id
                )
                data_dict['parent_permission'] = 0
                # Checking only child Permisson
                if tMasterOtherRole:
                    # print('tMasterOtherRole', tMasterOtherRole)
                    for e_tMasterOtherRole in tMasterOtherRole:
                        data_dict[
                            'permission'] = e_tMasterOtherRole.mor_permissions.id if e_tMasterOtherRole.mor_permissions else 0
                else:
                    data_dict['permission'] = 0
                data_dict['child_details'] = self.getChildOtherListForRoleLogin(
                    role_id=role_id,
                    parent_other_id=child.id,
                )
                # print('data_dict:: ', data_dict)
                childlist.append(data_dict)
            return childlist
        except Exception as e:
            raise e

class EditUserNewView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    # pagination_class =CSPageNumberPagination
    queryset = User.objects.all()
    serializer_class = EditUserNewSerializer

class EditUserGetNewView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    # pagination_class =CSPageNumberPagination
    queryset = User.objects.all()
    serializer_class = EditUserGetNewSerializer
    
class UserListByDepartmentView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer

    def get_queryset(self):
        #print('self.kwargs',self.kwargs)
        department_details = self.kwargs
        user_ids = TCoreUserDetail.objects.filter(
            department_id=department_details['department_id']).values_list('cu_user',flat=True)
        return self.queryset.filter(pk__in=user_ids)
    
    @response_modify_decorator_get
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
class UserListUnderLoginUserView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    pagination_class = OnOffPagination

    def get_queryset(self):
        head_type = self.request.query_params.get('type',None)
        user = self.request.user
        if user.is_superuser:
            return self.queryset.filter(is_active=True)
        else:
            if head_type:
                if head_type.lower() == 'hod':
                    user_ids = TCoreUserDetail.objects.filter(
                        hod=user).values_list('cu_user',flat=True)
                    return self.queryset.filter(pk__in=user_ids)
                elif head_type.lower() == 'reporting-head':
                    user_ids = TCoreUserDetail.objects.filter(
                        reporting_head=user).values_list('cu_user',flat=True)
                    return self.queryset.filter(pk__in=user_ids)
            else:
                return list()

    @response_modify_decorator_list_or_get_before_execution_for_onoff_pagination
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
 
class HodListWithDepartmentView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = TCoreDepartment.objects.filter(cd_is_deleted=False)
    serializer_class = CoreDepartmentEditSerializer
    pagination_class = OnOffPagination
    
    @response_modify_decorator_list_or_get_after_execution_for_onoff_pagination
    def get(self, request, *args, **kwargs):
        response = super(self.__class__, self).get(self, request, args, kwargs)
        hod_list = TCoreUserDetail.objects.filter(
            cu_is_deleted=False,hod__isnull=False).values_list('hod',flat=True).distinct()
        print('hod_list',hod_list)
        details_list = list()

        if 'results' in response.data:
            data_dict = response.data['results']
        else:
            data_dict = response.data

        for data in data_dict:
            data['department'] = data['cd_name']
            data.pop('cd_name')
            #print('data',type(data['id']))
            department_head_details = ''
            for e_hod in hod_list:
                #print('e_hod',type(e_hod))
                dept = TCoreUserDetail.objects.only('department').get(cu_user=e_hod).department
                if dept is not None:
                    #print('dept',type(dept.id))
                    if dept.id == data['id']:
                        department_head_details = User.objects.get(pk=e_hod)
                        #print('department_head_details',department_head_details)
                        data['first_name'] = department_head_details.first_name
                        data['last_name'] = department_head_details.last_name
                    else:
                        data['first_name'] = ''
                        data['last_name'] = ''
        return response     
   
        