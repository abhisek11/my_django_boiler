from django.contrib import admin
from pms.models.module_execution import *

@admin.register(PmsExecutionDailyProgress)
class PmsExecutionDailyProgress(admin.ModelAdmin):
    list_display = [field.name for field in PmsExecutionDailyProgress._meta.fields]

@admin.register(PmsExecutionDailyProgressProgress)
class PmsExecutionDailyProgressProgress(admin.ModelAdmin):
    list_display = [field.name for field in PmsExecutionDailyProgressProgress._meta.fields]

@admin.register(PmsExecutionDailyProgressLabourReport)
class PmsExecutionDailyProgressLabourReport(admin.ModelAdmin):
    list_display = [field.name for field in PmsExecutionDailyProgressLabourReport._meta.fields]
@admin.register(PmsExecutionDailyProgressPandM)
class PmsExecutionDailyProgressPandM(admin.ModelAdmin):
    list_display = [field.name for field in PmsExecutionDailyProgressPandM._meta.fields]
# @admin.register(TCoreUnit)
# class TCoreUnit(admin.ModelAdmin):
#     list_display = [field.name for field in TCoreUnit._meta.fields]

@admin.register(PmsExecutionPurchasesRequisitionsActivitiesMaster)
class PmsExecutionPurchasesRequisitionsActivitiesMaster(admin.ModelAdmin):
    list_display = [field.name for field in PmsExecutionPurchasesRequisitionsActivitiesMaster._meta.fields]

@admin.register(PmsExecutionPurchasesRequisitions)
class PmsExecutionPurchasesRequisitions(admin.ModelAdmin):
    list_display = [field.name for field in PmsExecutionPurchasesRequisitions._meta.fields]

@admin.register(PmsExecutionPurchasesRequisitionsMapWithActivities)
class PmsExecutionPurchasesRequisitionsMapWithActivities(admin.ModelAdmin):
    list_display = [field.name for field in PmsExecutionPurchasesRequisitionsMapWithActivities._meta.fields]

# @admin.register(PmsExecutionPurchasesRequisitionsApproval)
# class PmsExecutionPurchasesRequisitionsApproval(admin.ModelAdmin):
#     list_display = [field.name for field in PmsExecutionPurchasesRequisitionsApproval._meta.fields]

@admin.register(PmsExecutionProjectPlaningMaster)
class PmsExecutionProjectPlaningMaster(admin.ModelAdmin):
    list_display = [field.name for field in PmsExecutionProjectPlaningMaster._meta.fields]

@admin.register(PmsExecutionProjectPlaningFieldLabel)
class PmsExecutionProjectPlaningFieldLabel(admin.ModelAdmin):
    list_display = [field.name for field in PmsExecutionProjectPlaningFieldLabel._meta.fields]

@admin.register(PmsExecutionProjectPlaningFieldValue)
class PmsExecutionProjectPlaningFieldValue(admin.ModelAdmin):
    list_display = [field.name for field in PmsExecutionProjectPlaningFieldValue._meta.fields]

@admin.register(PmsExecutionPurchasesQuotationsPaymentTermsMaster)
class PmsExecutionPurchasesQuotationsPaymentTermsMaster(admin.ModelAdmin):
    list_display = [field.name for field in PmsExecutionPurchasesQuotationsPaymentTermsMaster._meta.fields]

@admin.register(PmsExecutionPurchasesQuotations)
class PmsExecutionPurchasesQuotations(admin.ModelAdmin):
    list_display = [field.name for field in PmsExecutionPurchasesQuotations._meta.fields]

@admin.register(PmsExecutionPurchasesRequisitionsMaster)
class PmsExecutionPurchasesRequisitionsMaster(admin.ModelAdmin):
    list_display = [field.name for field in PmsExecutionPurchasesRequisitionsMaster._meta.fields]

@admin.register(PmsExecutionPurchasesRequisitionsTypeMaster)
class PmsExecutionPurchasesRequisitionsTypeMaster(admin.ModelAdmin):
    list_display = [field.name for field in PmsExecutionPurchasesRequisitionsTypeMaster._meta.fields]

@admin.register(PmsExecutionPurchasesRequisitionsApproval)
class PmsExecutionPurchasesRequisitionsApproval(admin.ModelAdmin):
    list_display = [field.name for field in PmsExecutionPurchasesRequisitionsApproval._meta.fields]

@admin.register(PmsExecutionPurchasesComparitiveStatement)
class PmsExecutionPurchasesComparitiveStatement(admin.ModelAdmin):
    list_display = [field.name for field in PmsExecutionPurchasesComparitiveStatement._meta.fields]

@admin.register(PmsExecutionPurchasesComparitiveStatementDocument)
class PmsExecutionPurchasesComparitiveStatementDocument(admin.ModelAdmin):
    list_display = [field.name for field in PmsExecutionPurchasesComparitiveStatementDocument._meta.fields]

@admin.register(PmsExecutionPurchasesPOTransportCostMaster)
class PmsExecutionPurchasesPOTransportCostMaster(admin.ModelAdmin):
    list_display = [field.name for field in PmsExecutionPurchasesPOTransportCostMaster._meta.fields]

@admin.register(PmsExecutionPurchasesPO)
class PmsExecutionPurchasesPO(admin.ModelAdmin):
    list_display = [field.name for field in PmsExecutionPurchasesPO._meta.fields]

@admin.register(PmsExecutionPurchasesPOItemsMAP)
class PmsExecutionPurchasesPOItemsMAP(admin.ModelAdmin):
    list_display = [field.name for field in PmsExecutionPurchasesPOItemsMAP._meta.fields]

@admin.register(PmsExecutionPurchasesPODocument)
class PmsExecutionPurchasesPODocument(admin.ModelAdmin):
    list_display = [field.name for field in PmsExecutionPurchasesPODocument._meta.fields]

@admin.register(PmsExecutionStock)
class PmsExecutionStock(admin.ModelAdmin):
    list_display = [field.name for field in PmsExecutionStock._meta.fields]

@admin.register(PmsExecutionPurchasesDispatchDocument)
class PmsExecutionPurchasesDispatchDocument(admin.ModelAdmin):
    list_display = [field.name for field in PmsExecutionPurchasesDispatchDocument._meta.fields]

@admin.register(PmsExecutionPurchasesDelivery)
class PmsExecutionPurchasesDelivery(admin.ModelAdmin):
    list_display = [field.name for field in PmsExecutionPurchasesDelivery._meta.fields]

@admin.register(PmsExecutionPurchasesDeliveryDocument)
class PmsExecutionPurchasesDeliveryDocument(admin.ModelAdmin):
    list_display = [field.name for field in PmsExecutionPurchasesDeliveryDocument._meta.fields]

@admin.register(PmsExecutionStockIssueMaster)
class PmsExecutionStockIssueMaster(admin.ModelAdmin):
    list_display = [field.name for field in PmsExecutionStockIssueMaster._meta.fields]

@admin.register(PmsExecutionStockIssue)
class PmsExecutionStockIssue(admin.ModelAdmin):
    list_display = [field.name for field in PmsExecutionStockIssue._meta.fields]

@admin.register(PmsExecutionUpdatedStock)
class PmsExecutionUpdatedStock(admin.ModelAdmin):
    list_display = [field.name for field in PmsExecutionUpdatedStock._meta.fields]

@admin.register(PmsExecutionIssueMode)
class PmsExecutionIssueMode(admin.ModelAdmin):
    list_display = [field.name for field in PmsExecutionIssueMode._meta.fields]

@admin.register(PmsExecutionPurchasesPaymentsMade)
class PmsExecutionPurchasesPaymentsMade(admin.ModelAdmin):
    list_display = [field.name for field in PmsExecutionPurchasesPaymentsMade._meta.fields]

@admin.register(PmsExecutionPurchasesPaymentPlan)
class PmsExecutionPurchasesPaymentPlan(admin.ModelAdmin):
    list_display = [field.name for field in PmsExecutionPurchasesPaymentPlan._meta.fields]

@admin.register(PmsExecutionPurchasesTotalAmountPayable)
class PmsExecutionPurchasesTotalAmountPayable(admin.ModelAdmin):
    list_display = [field.name for field in PmsExecutionPurchasesTotalAmountPayable._meta.fields]

@admin.register(PmsExecutionPurchasesTotalTransportCostPayable)
class PmsExecutionPurchasesTotalTransportCostPayable(admin.ModelAdmin):
    list_display = [field.name for field in PmsExecutionPurchasesTotalTransportCostPayable._meta.fields]

@admin.register(PmsExecutionPurchasesDispatch)
class PmsExecutionPurchasesDispatch(admin.ModelAdmin):
    list_display = [field.name for field in PmsExecutionPurchasesDispatch._meta.fields]

@admin.register(PmsExecutionPurchasesRequisitionsApprovalLogTable)
class PmsExecutionPurchasesRequisitionsApprovalLogTable(admin.ModelAdmin):
    list_display = [field.name for field in PmsExecutionPurchasesRequisitionsApprovalLogTable._meta.fields]


@admin.register(PmsExecutionStockIssueMasterLogTable)
class PmsExecutionStockIssueMasterLogTable(admin.ModelAdmin):
    list_display = [field.name for field in PmsExecutionStockIssueMasterLogTable._meta.fields]

@admin.register(PmsExecutionPurchasesComparitiveStatementLog)
class PmsExecutionPurchasesComparitiveStatementLog(admin.ModelAdmin):
    list_display = [field.name for field in PmsExecutionPurchasesComparitiveStatementLog._meta.fields]


@admin.register(PmsExecutionPurchasesPOLog)
class PmsExecutionPurchasesPOLog(admin.ModelAdmin):
    list_display = [field.name for field in PmsExecutionPurchasesPOLog._meta.fields]



