from pms import views
from django.conf.urls import url, include
from rest_framework import routers
from django.urls import path
from rest_framework.authtoken import views as rest_framework_views

urlpatterns = [
    #::::::::::  PMS EXECUTION PLANNING AND REPORT ::::::::#
    path('pms_execution_project_planning_add_or_update/',views.ExecutionProjectPlaningAdd.as_view()),
    path('pms_execution_project_planning_view/<project_id>/<site_id>/',views.ExecutionProjectPlaningview.as_view()),
    path('pms_execution_daily_progress_add/', views.ExecutionDailyReportProgressAdd.as_view()),
    path('pms_execution_daily_progress_labour_add/', views.ExecutionDailyReportLabourAdd.as_view()),
    path('pms_execution_daily_progress_pandm_add/', views.ExecutionDailyReportPandMAdd.as_view()),
    path('pms_execution_daily_progress_list/<project_id>/<site_id>/', views.ExecutionDailyReportProgressView.as_view()),
    path('pms_execution_daily_labour_list/<project_id>/<site_id>/', views.ExecutionDailyReportLabourView.as_view()),
    path('pms_execution_daily_pandm_list/<project_id>/<site_id>/', views.ExecutionDailyReportPandMView.as_view()),

    #:::::::::::::::::::::::::::::::::: EXECUTION REQUISITION ::::::::::::::::::::::::::::::::::::::::::::::#
    path('execution_purchases_requisitions_activities_master_add/', views.ExecutionPurchasesRequisitionsActivitiesMasterAddView.as_view()),
    path('execution_purchases_requisitions_activities_master_edit/<pk>/', views.ExecutionPurchasesRequisitionsActivitiesMasterEditView.as_view()),
    path('execution_purchases_requisitions_activities_master_delete/<pk>/', views.ExecutionPurchasesRequisitionsActivitiesMasterDeleteView.as_view()),

    # path('purchase_requisition_site_to_pid/',views.PurchaseRequisitionsSiteToProjectIDListView.as_view()),


    # path('purchase_requisition_add/',views.PurchaseRequisitionsAddView.as_view()),
    # path('purchase_requisition_list/', views.PurchaseRequisitionsDataList.as_view()),

    path('purchase_requisition_add/',views.PurchaseRequisitionsAddView.as_view()),
    path('purchase_requisition_for_android_add/',views.PurchaseRequisitionsForAndroidAddView.as_view()),
    path('purchase_requisition_submit_for_approval/<pk>/',views.PurchaseRequisitionsSubmitApprovalView.as_view()),
    
    path('purchase_requisition_list/<req_id>/', views.PurchaseRequisitionsDataList.as_view()),
    path('purchase_requisition_total_approval_list/', views.PurchaseRequisitionsTotalDataList.as_view()),
    path('purchase_requisition_total_list/', views.PurchaseRequisitionsTotalListView.as_view()),
    path('purchase_requisition_edit/<pk>/', views.PurchaseRequisitionsEditView.as_view()),
    path('purchase_requisition_for_android_edit/<pk>/', views.PurchaseRequisitionsForAndroidEditView.as_view()),
    path('purchase_requisition_for_android_edit_item/',views.PurchaseRequisitionsForAndroidEditItemView.as_view()),

    path('purchase_requisition_not_approved_mobile_list/', views.PurchaseRequisitionsNotApprovalMobileListView.as_view()),
    path('purchase_requisition_after_approved_mobile_list/', views.PurchaseRequisitionsAfterApprovalMobileListView.as_view()),
    
    path('purchase_requisition_delete/<pk>/', views.PurchaseRequisitionsDeleteView.as_view()),
    #:::::::::::::::::::::::::::::::::: EXECUTION REQUISITION APPROVAL::::::::::::::::::::::::::::::::::::::::::::::#
    path('purchase_requisition_approval/',views.PurchaseRequisitionsApproval.as_view()),
    path('purchase_requisition_approval_list/<requisition_id>/<project_id>/<site_id>/', views.PurchaseRequisitionsApprovalList.as_view()),
    path('purchase_requisition_approval_total_list/',views.PurchaseRequisitionsTotalApprovalList.as_view()),
    # #::::::::::::::::::::::::::::::::::::  PMS EXECUTION PURCHASES QUOTATIONS ;:::::::::::::::::::::::::::::#
    # path('purchase_quotations_payment_terms_master_add/', views.ExecutionPurchaseQuotationsPaymentTermsMasterAddView.as_view()),
    # path('purchase_quotations_payment_terms_master_edit/<pk>/', views.ExecutionPurchaseQuotationsPaymentTermsMasterEditView.as_view()),
    # path('purchase_quotations_payment_terms_master_delete/<pk>/', views.ExecutionPurchaseQuotationsPaymentTermsMasterDeleteView.as_view()),
    #
    # path('purchase_quotations_add/', views.ExecutionPurchaseQuotationsAddView.as_view()),
    # path('purchase_quotations_edit/<pk>/', views.ExecutionPurchaseQuotationsEditView.as_view()),
    # path('purchase_quotations_delete/<pk>/', views.ExecutionPurchaseQuotationsDeleteView.as_view()),
    # path('purchase_item_type_list/<req_id>/<type_id>/',views.ExecutionPurchaseItemTypeListView.as_view()),
    #::::::::::::::::::::::::::::::::::::  PMS EXECUTION PURCHASES QUOTATIONS ;:::::::::::::::::::::::::::::#
    path('purchase_quotations_payment_terms_master_add/',
         views.ExecutionPurchaseQuotationsPaymentTermsMasterAddView.as_view()),
    path('purchase_quotations_payment_terms_master_edit/<pk>/',
         views.ExecutionPurchaseQuotationsPaymentTermsMasterEditView.as_view()),
    path('purchase_quotations_payment_terms_master_delete/<pk>/',
         views.ExecutionPurchaseQuotationsPaymentTermsMasterDeleteView.as_view()),

    path('purchase_quotations_approved_item_list/<req_master_id>/',views.ExecutionPurchaseQuotationsApprovedListView.as_view()),
    path('purchase_quotation_approved/<pk>/',views.PurchaseQuotationApprovedView.as_view()),
    path('purchase_quotations_add/', views.ExecutionPurchaseQuotationsAddView.as_view()),
    path('purchase_quotations_item_list/<req_master_id>/<item_id>/<uom_id>/',
         views.ExecutionPurchaseQuotationsItemListView.as_view()),
    path('purchase_quotations_total_list/<req_master_id>/',
         views.ExecutionPurchaseQuotationsItemTotalListView.as_view()),
    path('purchase_quotations_edit/<pk>/', views.ExecutionPurchaseQuotationsEditView.as_view()),
    path('purchase_quotations_delete/<pk>/', views.ExecutionPurchaseQuotationsDeleteView.as_view()),
    path('purchase_quotations_for_approved_list/', views.PurchaseQuotationsForApprovedListView.as_view()),
 
    #::::::::::::::::::::::::::::::::::::  PMS EXECUTION PURCHASES TYPE  ;::::::::::::::::::::::::::::::#
    path('purchases_requisitions_type_master_add/', views.ExecutionPurchasesRequisitionsTypesMasterAddView.as_view()),
    path('purchases_requisitions_type_master_edit/<pk>/', views.ExecutionPurchasesRequisitionsTypesMasterEditView.as_view()),
    path('purchases_requisitions_type_master_delete/<pk>/', views.ExecutionPurchasesRequisitionsTypesMasterDeleteView.as_view()),
    path('purchases_requisitions_type_to_item_code/', views.PurchasesRequisitionsTypeToItemCodeListView.as_view()),
    
    path('purchases_requisitions_type_to_item_code_current_stock/', views.PurchasesRequisitionsTypeToItemCodeCurrentStockListView.as_view()),

    #:::::::::::::::::::::::  PMS EXECUTION PURCHASES COMPARITIVE STATEMENT:::::::::::::::::::::::::::::::::#
    path('execution_purchases_comparitive_statement_add/',
         views.ExecutionPurchasesComparitiveStatementAddView.as_view()),
    path('execution_purchases_comparitive_statement_edit/<pk>/', views.ExecutionPurchasesComparitiveStatementEditView.as_view()),
    path('execution_purchases_comparitive_statement_ord_list/<requisitions_master_id>/<item_id>/<vendor_id>/',
         views.ExecutionPurchasesComparitiveStatementOrdListView.as_view()),
     path('execution_purchases_comparitive_statement_approval/<pk>/', #currently used for approval
          views.ExecutionPurchasesComparitiveStatementApprovalView.as_view()),
    path('execution_purchases_comparitive_statement_document_add/',
         views.ExecutionPurchasesComparitiveStatementDocumentAddView.as_view()),
    path('execution_purchases_comparitive_statement_item_submit_for_approval/<pk>/', 
          views.ExecutionPurchasesComparitiveStatementItemSubmitApprovalView.as_view()),
     path('execution_purchases_comparitive_statement_approval_list/', #currently used for approval
          views.ExecutionPurchasesComparitiveStatementApprovalListView.as_view()),

    # #:::::::::::::::::::::: PMS EXECUTION PURCHASES DELIVERY:::::::::::::::::::::::::::::::::::::::::::::::::#
    # path('execution_purchases_delivery_add/', views.ExecutionPurchasesDeliveryAddView.as_view()),
    # path('execution_purchases_delivery_edit/<pk>/', views.ExecutionPurchasesDeliveryEditView.as_view()),
    # path('execution_purchases_delivery_document_add/', views.ExecutionPurchasesDeliveryDocumentAddView.as_view()),
    # path('execution_purchases_delivery_document_edit/<pk>/',views.ExecutionPurchasesDeliveryDocumentEditView.as_view()),

    #::::::::::::::::::::::::::::::::::::  PMS EXECUTION PURCHASES PO MASTER  ;::::::::::::::::::::::::::::::#
    path('purchases_order_transportcost_master_add/', views.ExecutionPOTransportCostMasterAddView.as_view()),
    path('purchases_order_transportcost_master_edit/<pk>/', views.ExecutionPOTransportCostMasterEditView.as_view()),
    path('purchases_order_transportcost_master_Delete/<pk>/', views.ExecutionPOTransportCostMasterDeleteView.as_view()),
    #::::::::::::::::::::::::::::::::::::  PMS EXECUTION PURCHASES ;::::::::::::::::::::::::::::::#
    path('purchases_purchases_order_list/<req_id>/', views.ExecutionPurchasesPOListView.as_view()),
    path('purchases_purchases_order_add/', views.ExecutionPurchasesPOAddView.as_view()),
    path('purchases_purchases_order_total_list/<req_id>/', views.ExecutionPurchasesPOTotalListView.as_view()),
    # path('purchase_order_quantity_calculation/<req_id>/',views.ExecutionPurchasesPOQuantityCalView.as_view()),
    path('purchases_order_document_add/', views.ExecutionPurchasesPODocumentAddView.as_view()),
    path('purchases_order_document_Edit/<pk>/', views.ExecutionPurchasesPODocumentEditView.as_view()),
    path('purchases_order_document_Delete/<pk>/', views.ExecutionPurchasesPODocumentDeleteView.as_view()),

    #:::::::::::::::::::::: PMS EXECUTION PURCHASES DISPATCH:::::::::::::::::::::::::::#
    path('execution_purchases_dispatch_add/', views.ExecutionPurchasesDispatchAddView.as_view()),
    path('executsite_locationion_purchases_dispatch_edit/<pk>/', views.ExecutionPurchasesDispatchEditView.as_view()),
    path('execution_purchases_dispatch_delete/<pk>/', views.ExecutionPurchasesDispatchDeleteView.as_view()),
    path('execution_purchases_dispatch_list/', views.ExecutionPurchasesDispatchListView.as_view()),
    path('execution_purchases_dispatch_document_add/', views.ExecutionPurchasesDispatchDocumentAddView.as_view()),
    path('execution_purchases_dispatch_document_edit/<pk>/', views.ExecutionPurchasesDispatchDocumentEditView.as_view()),

    #:::::::::::::::::::::: PMS EXECUTION PURCHASES DELIVERY:::::::::::::::::::::::::::#
    path('execution_purchases_delivery_add/', views.ExecutionPurchasesDeliveryAddView.as_view()),
    path('execution_purchases_delivery_edit/<pk>/', views.ExecutionPurchasesDeliveryEditView.as_view()),
    path('execution_purchases_delivery_list/', views.ExecutionPurchasesDeliveryListView.as_view()),
    path('execution_purchases_total_delivery_material_recieved_list/', views.ExecutionPurchasesTotalDeliveryMaterialRecievedListView.as_view()),
    path('execution_purchases_delivery_document_add/', views.ExecutionPurchasesDeliveryDocumentAddView.as_view()),
    path('execution_purchases_delivery_delete/<pk>/', views.ExecutionPurchasesDeliveryDeleteView.as_view()),

    #:::::::::::::::::::::: PMS EXECUTION PURCHASES PAYMENT:::::::::::::::::::::::::::#
    path('execution_purchases_payment_plan_add/', views.ExecutionPurchasesPaymentPlanAddView.as_view()),

    #:::::::::::::::::::::: PMS EXECUTION PURCHASES PAYMENTS MADE:::::::::::::::::::::::::::#
    path('execution_purchases_payments_made_add/', views.ExecutionPurchasesPaymentsMadeAddView.as_view()),
    path('execution_purchases_payments_made_edit/<pk>/', views.ExecutionPurchasesPaymentsMadeEditView.as_view()),
    path('execution_purchases_payments_made_delete/<pk>/', views.ExecutionPurchasesPaymentsMadeDeleteView.as_view()),
    path('execution_purchases_payments_made_document_add/', views.ExecutionPurchasesPaymentsMadeDocumentAddView.as_view()),
    path('execution_purchases_payments_made_document_edit/<pk>/', views.ExecutionPurchasesPaymentsMadeDocumentEditView.as_view()),
    path('execution_purchases_payments_made_document_delete/<pk>/', views.ExecutionPurchasesPaymentsMadeDocumentDeleteView.as_view()),
    path('execution_purchases_payments_made_list/', views.ExecutionPurchasesPaymentsMadeListView.as_view()),
    path('excution_purchases_total_amount_payable_list/', views.ExecutionPurchasesTotalAmountPayableListView.as_view()),

    #:::::::::::::::::::::: PMS EXECUTION STOCK:::::::::::::::::::::::::::#
    path('execution_stock_issue_mode_add/', views.ExecutionStockIssueModeAdd.as_view()),
    path('execution_stock_issue_mode_edit/<pk>/', views.ExecutionStockIssueModeEdit.as_view()),
    path('execution_stock_issue_mode_delete/<pk>/', views.ExecutionStockIssueModeDelete.as_view()),
    path('execution_stock_stock_issue_add/', views.ExecutionStockIssueAddView.as_view()),
    path('execution_stock_stock_mobile_issue_add/', views.ExecutionStockMobileIssueAddView.as_view()),
	path('execution_stock_mobile_issue_edit/<pk>/', views.ExecutionStockMobileIssueEdit.as_view()),
	path('execution_stock_stock_mobile_each_issue_list/<pk>/', views.ExecutionStockEachIssueListView.as_view()),
    path('execution_stock_mobile_issue_delete/<pk>/', views.ExecutionStockMobileIssueDelete.as_view()),
	path('execution_stock_issue_submit_for_approval/<pk>/', views.ExecutionStockIssueSubmitForApprovalView.as_view()),
   
     path('execution_stock_stock_issue_approved/<pk>/', views.ExecutionStockIssueEdit.as_view()),
    path('execution_stock_stock_issue_list/<project_id>/<site_id>/', views.ExecutionStockIssueListView.as_view()),
	path('execution_stock_mobile_approved_stock_issue_list/<project_id>/<site_id>/', views.ExecutionStockIssueApprovedListView.as_view()),
	path('execution_stock_mobile_non_approved_stock_issue_list/<project_id>/<site_id>/', views.ExecutionStockIssueNonApprovedListView.as_view()),
    path('execution_stock_issue_item_list_by_issue_id/', views.ExecutionStockIssueItemListByIssueIdView.as_view()),
    
    path('execution_stock_monthly_stock_report_list/<project_id>/<site_id>/',views.ExecutionStockMonthReportListView.as_view()),
    path('execution_current_stock_report/<project>/<site_location>/', views.ExecutionCurrentStockReportView.as_view()),
    
    path('execution_material_stock_statement/<project>/<site_location>/', views.ExecutionMaterialStockStatementReportView.as_view()),
    
    path('purchases_requisitions_type_to_item_code_for_stock/', views.PurchasesRequisitionsTypeToItemCodeStockListView.as_view()), #author:- Abhisek singh (15/07/19)
    path('kendpusi_closing_stock_excel_file_add/',views.ClosingStockExcelFileAddView.as_view()),
    path('matla_closing_stock_excel_file_add/',views.MatlaClosingStockExcelFileAddView.as_view()),
    path('mejia_closing_stock_excel_file_add/',views.MejiaClosingStockExcelFileAddView.as_view()),
    path('octagon_closing_stock_excel_file_add/',views.OctagonClosingStockExcelFileAddView.as_view()),
    path('rajkharsawan_closing_stock_excel_file_add/',views.RajkharsawanClosingStockExcelFileAddView.as_view()),

    #::::::::::::::::::::::::::::::::::::  PMS EXECUTION ACTICVE PROJECTS LIST AND REPORTS  ;::::::::::::::::::::::::::::::#
    path('execution_active_listandreport_for_external_user/', views.ExecutionActiveListAndReportForExternalUserView.as_view()),
    path('execution_active_listandreport_of_partner/', views.ExecutionActiveListAndReportOfPartnerView.as_view()),

]
