from pms import views
from django.conf.urls import url, include
from rest_framework import routers
from django.urls import path

from rest_framework.authtoken import views as rest_framework_views


urlpatterns = [
    #:::::::::: TENDER AND TENDER DOCUMENTS  ::::::::#
    path('tenders_add/', views.TendersAddView.as_view()),
    path('tenders_edit/<pk>/', views.TenderEditView.as_view()),
    path('tenders_delete/<pk>/', views.TenderDeleteByIdView.as_view()),
    path('tender_doc_by_tender_id/<tender_id>/', views.TenderDocsByTenderIdView.as_view()),
    path('tenders_doc_add/', views.TenderDocsAddView.as_view()),
    path('tenders_doc_edit/<pk>/', views.TenderDocsEditView.as_view()),
    path('tenders_doc_delete/<pk>/', views.TenderDocsDeleteByIdView.as_view()),
    path('tenders_list/', views.TendersListView.as_view()),
    path('tenders_list_count/', views.TendersListCountView.as_view()),
    path('projects_list_wp/', views.ProjectsListWPView.as_view()),
    path('tenders_archive/<pk>/', views.TendersArchiveView.as_view()),
    path('tenders_archive_list/', views.TendersArchiveListView.as_view()),
          
    #::::::::::::::: TENDER  ELIGIBILITY :::::::::::::::#
    path('tender_eligibility_fields_list/<tender_id>/<eligibility_type>/',
         views.PmsTenderEligibilityFieldsByTypeListView.as_view()),
    path('tender_eligibility_fields_add/', views.PmsTenderEligibilityAdd.as_view()),
    path('tender_eligibility_fields_edit_by_id/<pk>/', views.PmsTenderEligibilityFieldsByTypeEdit.as_view()),
    path('tender_not_eligibility_reason_add/<tender_id>/<type>/', views.PmsTenderNotEligibilityReasonAdd.as_view()),

    #::::::::::::::: TENDER  BIDDER TYPE :::::::::::::::#
    path('partners_add/', views.PartnersAddView.as_view()),
    path('partners_edit/<pk>/', views.PartnersEditView.as_view()),
    path('partners_delete/<pk>/', views.PartnersDeleteView.as_view()),
    path('tender_bidder_details_by_tender_id/<tender_id>/', views.TendorBidderTypeByTenderIdView.as_view()),
    path('tender_bidder_type_add/', views.TendorBidderTypeAddView.as_view()),
    path('tender_bidder_type_edit/<pk>/', views.TendorBidderTypeEditView.as_view()),
    path('tender_bidder_type_delete/<pk>/', views.TendorBidderTypeDeleteView.as_view()),

    #::::::::::::::::::: TENDER APPROVAL :::::::::::::#
    path('tender_approval_add_or_update/<tender_id>/', views.TenderApprovalAddOrUpdateView.as_view()),
    path('tender_details_for_approval/<tender_id>/', views.TenderDetailsForApprovalView.as_view()),

    #::::::::::::::: TENDER SURVEY SITE PHOTOS :::::::::::::::#
    path('tender_survey_site_photos_add/', views.TenderSurveySitePhotosAddView.as_view()),
    path('tender_survey_site_photos_edit/<pk>/', views.TenderSurveySitePhotosEditView.as_view()),
    path('tender_survey_site_photos_list/<tender_id>/', views.TenderSurveySitePhotosListView.as_view()),
    path('tender_survey_site_photos_delete/<pk>/', views.TenderSurveySitePhotosDeleteView.as_view()),

    #:::::::::::::::::::::: MATERIAL TYPE MASTER:::::::::::::::::::::::::::#
#     path('material_type_master_add/', views.MaterialTypeMasterAddView.as_view()),
#     path('material_type_master_edit/<pk>/', views.MaterialTypeMasterEditView.as_view()),
#     path('material_type_master_delete/<pk>/', views.MaterialTypeMasterDeleteView.as_view()),

    #::::::::::: TENDER SURVEY METERIAL ::::::::::::::::::::#
    path('materials_add/', views.MaterialsAddView.as_view()),
    path('asset_excel_file_add/',views.AssetsExcelFileAddView.as_view()),
    path('consumables_excel_file_add/',views.ConsumablesExcelFileAddView.as_view()),
    path('electrical_excel_file_add/',views.ElectricalExcelFileAddView.as_view()),
    path('spares_excel_file_add/',views.SparesExcelFileAddView.as_view()),
    path('general_tools_excel_file_add/',views.GeneralToolsExcelFileAddView.as_view()),
    path('safety_excel_file_add/',views.SafetyExcelFileAddView.as_view()),
    path('fuel_and_lub_excel_file_add/',views.FuelandLubExcelFileAddView.as_view()),
    path('raw_material_excel_file_add/',views.RawMaterialExcelFileAddView.as_view()),
    path('materials_edit/<pk>/', views.MaterialsEditView.as_view()),
    path('materials_delete/<pk>/', views.MaterialsDeleteView.as_view()),
    path('materials_list/', views.MaterialsListView.as_view()),
    
    #::::::::::: TENDER SURVEY COORDINATES ::::::::::::::::::::#
    path('tender_survey_location_add/', views.TenderSurveyLocationAddView.as_view()),
    path('tender_survey_location_list/<tender_id>/', views.TenderSurveyLocationListView.as_view()),
    path('tender_survey_location_edit/<pk>/', views.TenderSurveyLocationEditView.as_view()),
    path('tender_survey_location_delete/<pk>/', views.TenderSurveyLocationDeleteView.as_view()),

    #::::::::: TENDER SURVEY COORDINATES MATERIALS EXTERNAL USER MAPPING::::::::::#
    path('tender_survey_materials_external_user_mapping_list/',
         views.TenderSurveyMaterialsExternalUserMappingListView.as_view()),
    path('tender_survey_materials_external_user_mapping_add/',
         views.TenderSurveyMaterialsExternalUserMappingAddView.as_view()),
    path('tender_survey_materials_external_user_mapping_add_f_android/',
             views.TenderSurveyMaterialsExternalUserMappingAddFAndroidView.as_view()),
    path('tender_survey_materials_external_user_mapping_delete/<pk>/', views.TenderSurveyMaterialsExternalUserMappingDeleteView.as_view()),
    path('tender_survey_materials_external_user_mapping_document_add/',views.TenderSurveyMaterialsExternalUserMappingDocumentAddView.as_view()),

    #:::::::::: TENDER SURVEY RESOURCE ESTABLISHMENT :::::::::::#
    path('tender_survey_resource_establishment_add/', views.TenderSurveyResourceEstablishmentAddView.as_view()),
    path('tender_survey_resource_establishment_edit/<pk>/', views.TenderSurveyResourceEstablishmentEditView.as_view()),
    path('tender_survey_resource_establishment_delete/<pk>/', views.TenderSurveyResourceEstablishmentDeleteView.as_view()),
    path('tender_survey_resource_establishment_document_add/',views.TenderSurveyResourceEstablishmentDocumentAddView.as_view()),
    path('tender_survey_resource_establishment_document_edit/<pk>/',views.TenderSurveyResourceEstablishmentDocumentEditView.as_view()),
    path('tender_survey_resource_establishment_document_delete/<pk>/',views.TenderSurveyResourceEstablishmentDocumentDeleteView.as_view()),

    #:::: TENDER SURVEY RESOURCE HYDROLOGICAL :::::::#
    path('tender_survey_resource_hydrological_add/',views.TenderSurveyResourceHydrologicalAddView.as_view()),
    path('tender_survey_resource_hydrological_edit/<pk>/',views.TenderSurveyResourceHydrologicalEditView.as_view()),
    path('tender_survey_resource_hydrological_delete/<pk>/',views.TenderSurveyResourceHydrologicalDeleteView.as_view()),
    path('tender_survey_resource_hydrological_document_add/',views.TenderSurveyResourceHydrologicalDocumentAddView.as_view()),
    path('tender_survey_resource_hydrological_document_edit/<pk>/',views.TenderSurveyResourceHydrologicalDocumentEditView.as_view()),
    path('tender_survey_resource_hydrological_document_delete/<pk>/',views.TenderSurveyResourceHydrologicalDocumentDeleteView.as_view()),

    #:::: TENDER SURVEY RESOURCE CONTRACTORS / VENDORS  CONTRACTOR WORK TYPE:::::::#
    path('tender_survey_resource_contractors_o_vendors_contarctor_w_type_add/',views.TenderSurveyResourceContractorsOVendorsContractorWTypeAddView.as_view()),
    path('tender_survey_resource_contractors_o_vendors_contarctor_w_type_edit/<pk>/',views.TenderSurveyResourceContractorsOVendorsContractorWTypeEditView.as_view()),
    path('tender_survey_resource_contractors_o_vendors_contarctor_w_type_delete/<pk>/',views.TenderSurveyResourceContractorsOVendorsContractorWTypeDeleteView.as_view()),
    path('tender_survey_resource_contractors_o_vendors_contarctor_w_type_document_add/',views.TenderSurveyResourceContractorsOVendorsContractorWTypeDocumentAddView.as_view()),
    path('tender_survey_resource_contractors_o_vendors_contarctor_w_type_document_edit/<pk>/',views.TenderSurveyResourceContractorsOVendorsContractorWTypeDocumentEditView.as_view()),
    path('tender_survey_resource_contractors_o_vendors_contarctor_w_type_document_delete/<pk>/',views.TenderSurveyResourceContractorsOVendorsContractorWTypeDocumentDeleteView.as_view()),

    #:::::::::::::::::::::: Machinary Type :::::::::::::::::::::::::#
    path('machinery_type_add/',views.MachineryTypeAddView.as_view()),
    path('machinery_type_edit/<pk>/',views.MachineryTypeEditView.as_view()),
    path('machinery_type_delete/<pk>/',views.MachineryTypeDeleteView.as_view()),

    #:::: TENDER SURVEY RESOURCE CONTRACTORS / VENDORS  P & M ::::::#
    path('tender_survey_resource_contractors_o_vendors_machinery_type_ex_de_add/',views.TenderSurveyResourceContractorsOVendorsMachineryTypeExDeAddView.as_view()),
    path('tender_survey_resource_contractors_o_vendors_machinery_type_de_add/',views.TenderSurveyResourceContractorsOVendorsMachineryTypeDeAddView.as_view()),
    path('machinary_type_list_by_tender/<tender>/',views.MachinaryTypeListByTenderView.as_view()),
    path('tender_survey_resource_contractors_o_vendors_machinery_type_de_edit/<pk>/',views.TenderSurveyResourceContractorsOVendorsMachineryTypeDeEditView.as_view()),
    path('tender_survey_resource_contractors_o_vendors_machinery_type_de_delete/<pk>/',views.TenderSurveyResourceContractorsOVendorsMachineryTypeDeDeleteView.as_view()),
    path('tender_survey_resource_contractors_o_vendors_machinery_type_de_document_add/', views.TenderSurveyResourceContractorsOVendorsMachineryTypeDeDocumentAddView.as_view()),
    path('tender_survey_resource_contractors_o_vendors_machinery_type_de_document_edit/<pk>/', views.TenderSurveyResourceContractorsOVendorsMachineryTypeDeDocumentEditView.as_view()),
    path('tender_survey_resource_contractors_o_vendors_machinery_type_de_document_delete/<pk>/', views.TenderSurveyResourceContractorsOVendorsMachineryTypeDeDocumentDeleteView.as_view()),

    #:::: TENDER SURVEY RESOURCE CONTACT DETAILS AND DESIGNATION :::::::#
    path('tender_survey_resource_contact_designation_add/',views.TenderSurveyResourceContactDesignationAddView.as_view()),
    path('tender_survey_resource_contact_details_add/',views.TenderSurveyResourceContactDetailsAddView.as_view()),
    path('tender_survey_resource_contact_details_edit/<pk>/',views.TenderSurveyResourceContactDetailsEditView.as_view()),
    path('tender_survey_resource_contact_details_delete/<pk>/',views.TenderSurveyResourceContactDetailsDeleteView.as_view()),

    #::::::::::: TENDER INITIAL COSTING ::::::::::::::::::::#
    path('tender_initial_costing_upload_file/', views.TenderInitialCostingUploadFileView.as_view()),
    path('tender_initial_costing_add/', views.TenderInitialCostingAddView.as_view()),
    path('tender_initial_costing_details/<tender_id>/', views.TenderInitialCostingDetailsView.as_view()),

    #:::::::::: Pms Tender Tab For Eligibility Documents ::::::::::::::::#
    path('tender_eligibility_field_document_add/<pk>/', views.TenderEligibilityFieldDocumentAdd.as_view()),
    path('tender_check_tab_document_upload_add/<tender_id>/', views.TenderCheckTabDocumentUploadAddView.as_view()),
    path('tender_eligibility_tab_document_add/<tender_id>/<eligibility_type>/', views.TenderTabDocumentDocumentsAddView.as_view()),
    path('tender_eligibility_tab_document_list/', views.TenderTabDocumentDocumentsListView.as_view()),
    path('tender_eligibility_with_price_tab_document_list/', views.TenderTabDocumentsListView.as_view()),


    path('tender_eligibility_tab_document_edit/<pk>/', views.TenderTabDocumentDocumentsEditView.as_view()),
    path('tender_eligibility_tab_document_delete/<pk>/', views.TenderTabDocumentDocumentsDeleteView.as_view()),

    #:::::::::::::::::::Pms Tender TabDocumentsPrice :::::::::::::::::::::::::#
    path('tender_tab_document_price_add/', views.TenderTabDocumentPriceAddView.as_view()),
    path('tender_tab_document_price_edit/<pk>/', views.TenderTabDocumentPriceEditView.as_view()),
    path('tender_tab_document_price_delete/<pk>/', views.TenderTabDocumentPriceDeleteView.as_view()),

    #:::::::::::::::::::Pms Tender Status :::::::::::::::::::::::::#
    path('tender_status_add_or_update/', views.TenderStatusAddOrUpdateView.as_view()),
    path('tender_stat_participents_f_view/',views.TenderStatParticipentsUploadFView.as_view()),
    path('tender_stat_comparison_f_view/',views.TenderStatComparisonUploadFView.as_view()),
    path('tender_stat_document_add/', views.TenderStatDocumentAddView.as_view()),
    path('tender_stat_document_edit/<pk>/', views.TenderStatDocumentEditView.as_view()),
    path('tender_stat_document_delete/<pk>/', views.TenderStatDocumentDeleteView.as_view()),

    # Tender Type List 
    path('tender_type_master_add/', views.TenderTpeMasterAddView.as_view()),
]

