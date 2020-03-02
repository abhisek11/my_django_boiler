from pms import url_tender
from pms import url_project
from pms import url_manpower
from pms import url_external_user
from pms import url_attendence
from pms import url_machineries
from pms import url_pre_execution
from pms import url_requisition
from pms import url_approval_permission
from pms import url_tour_and_travel

urlpatterns = url_tender.urlpatterns
urlpatterns += url_project.urlpatterns
urlpatterns += url_manpower.urlpatterns
urlpatterns += url_external_user.urlpatterns
urlpatterns += url_attendence.urlpatterns
urlpatterns += url_machineries.urlpatterns
urlpatterns += url_pre_execution.urlpatterns
urlpatterns += url_requisition.urlpatterns
urlpatterns += url_approval_permission.urlpatterns
urlpatterns += url_tour_and_travel.urlpatterns


