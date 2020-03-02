from pms import views
from django.conf.urls import url, include
from rest_framework import routers
from django.urls import path
from rest_framework.authtoken import views as rest_framework_views

urlpatterns = [
#::::::::::::PMS PRE EXECUTION GUEST HOUSE FINDING::::::::::::::::::::::::::::::#
    path('pre_execution_guest_house_finding_add/', views.PreExecutionGuestHouseFindingAddView.as_view()),
    path('pre_execution_guest_house_finding_edit/<pk>/', views.PreExecutionGuestHouseFindingEditView.as_view()),

    #:::::::::::: PMS PRE EXCUTION FURNITURE :::::::::::::::::::::::::::::::::::::#
    path('pre_execution_furniture_add/', views.PreExecutionFurnitureAddView.as_view()),
    path('pre_execution_furniture_edit/<pk>/', views.PreExecutionFurnitureEditView.as_view()),
    path('pre_execution_furniture_requirements_add/', views.PreExecutionFurnitureRequirementsAddView.as_view()),
    path('pre_execution_furniture_requirements_edit/<pk>/', views.PreExecutionFurnitureRequirementsEditView.as_view()),
    path('pre_execution_furniture_requirements_document_edit/<pk>/', views.PreExecutionFurnitureRequirementsDocumentEditView.as_view()),
    path('pre_execution_furniture_requirements_delete/<pk>/', views.PreExecutionFurnitureRequirementsDeleteView.as_view()),

    #::::::::::::PMS PRE EXCUTION UTILITIES ELECTRICAL::::::::::::::::::::::::::::::::::#
    path('pre_excution_utilities_electrical_add/', views.PreExcutionUtilitiesElectricalAddView.as_view()),
    path('pre_excution_utilities_electrical_edit/<pk>/', views.PreExcutionUtilitiesElectricalEditView.as_view()),
    path('pre_excution_utilities_electrical_document_add/',views.PreExcutionUtilitiesElectricalDocumentAddView.as_view()),
    path('pre_excution_utilities_electrical_document_edit/<pk>/',views.PreExcutionUtilitiesElectricalDocumentEditView.as_view()),
    path('pre_excution_utilities_electrical_document_delete/<pk>/', views.PreExcutionUtilitiesElectricalDocumentDeleteView.as_view()),

    #:::::::::::::::::::::: PMS PRE EXCUTION UTILITIES WATER:::::::::::::::::::::::::::::::#
    path('pre_excution_utilities_water_add/', views.PreExcutionUtilitiesWaterAddView.as_view()),
    path('pre_excution_utilities_water_edit/<pk>/', views.PreExcutionUtilitiesWaterEditView.as_view()),
    path('pre_excution_utilities_water_document_add/', views.PreExcutionUtilitiesWaterDocumentAddView.as_view()),
    path('pre_excution_utilities_water_document_edit/<pk>/', views.PreExcutionUtilitiesWaterDocumentEditView.as_view()),
    path('pre_excution_utilities_water_document_delete/<pk>/', views.PreExcutionUtilitiesWaterDocumentDeleteView.as_view()),

    #:::::::::::::::::::::: PMS PRE EXCUTION UTILITIES FUEL:::::::::::::::::::::::::::::::::#
    path('pre_excution_utilities_fuel_add/', views.PreExcutionUtilitiesFuelAddView.as_view()),
    path('pre_excution_utilities_fuel_edit/<pk>/', views.PreExcutionUtilitiesFuelEditView.as_view()),
    path('pre_excution_utilities_fuel_document_add/', views.PreExcutionUtilitiesFuelDocumentAddView.as_view()),
    path('pre_excution_utilities_fuel_document_edit/<pk>/', views.PreExcutionUtilitiesFuelDocumentEditView.as_view()),
    path('pre_excution_utilities_fuel_document_delete/<pk>/',views.PreExcutionUtilitiesFuelDocumentDeleteView.as_view()),

    #:::::::::::::: PMS PRE EXCUTION UTILITIES UTENSILS ::::::::::::::::::::::::::::::::::#
    path('pre_excution_utilities_utensils_add/', views.PreExcutionUtilitiesUtensilsAddView.as_view()),
    path('pre_excution_utilities_utensils_edit/<pk>/', views.PreExcutionUtilitiesUtensilsEditView.as_view()),
    path('pre_excution_utilities_utensils_document_add/', views.PreExcutionUtilitiesUtensilsDocumentAddView.as_view()),
    path('pre_excution_utilities_utensils_document_edit/<pk>/', views.PreExcutionUtilitiesUtensilsDocumentEditView.as_view()),
    path('pre_excution_utilities_utensils_document_delete/<pk>/', views.PreExcutionUtilitiesUtensilsDocumentDeleteView.as_view()),
    path('pre_excution_utilities_utensils_types_list/', views.PreExcutionUtilitiesUtensilsTypesListView.as_view()),
    path('pre_excution_utilities_utensils_types_edit/<pk>/', views.PreExcutionUtilitiesUtensilsTypesEditView.as_view()),
    path('pre_excution_utilities_utensils_types_delete/<pk>/', views.PreExcutionUtilitiesUtensilsTypesDeleteView.as_view()),

    #:::::::::::::: PMS PRE EXCUTION UTILITIES TIFFIN BOX ::::::::::::::::::::::::::::::::::#
    path('pre_excution_utilities_tiffin_box_add/', views.PreExcutionUtilitiesTiffinBoxAddView.as_view()),
    path('pre_excution_utilities_tiffin_box_edit/<pk>/', views.PreExcutionUtilitiesTiffinBoxEditView.as_view()),
    path('pre_excution_utilities_tiffin_box_document_add/', views.PreExcutionUtilitiesTiffinBoxDocumentAddView.as_view()),
    path('pre_excution_utilities_tiffin_box_document_edit/<pk>/', views.PreExcutionUtilitiesTiffinBoxDocumentEditView.as_view()),
    path('pre_excution_utilities_tiffin_box_document_delete/<pk>/', views.PreExcutionUtilitiesTiffinBoxDocumentDeleteView.as_view()),
    path('pre_excution_utilities_tiffin_box_types_list/', views.PreExcutionUtilitiesTiffinBoxTypesListView.as_view()),
    path('pre_excution_utilities_tiffin_box_types_edit/<pk>/', views.PreExcutionUtilitiesTiffinBoxTypesEditView.as_view()),
    path('pre_excution_utilities_tiffin_box_types_delete/<pk>/', views.PreExcutionUtilitiesTiffinBoxTypesDeleteView.as_view()),

    #:::::::::::::::::::::: PMS PRE EXCUTION UTILITIES COOK:::::::::::::::::::::::::::::::::::#
    path('pre_excution_utilities_cook_add/', views.PreExcutionUtilitiesCookAddView.as_view()),
    path('pre_excution_utilities_cook_edit/<pk>/', views.PreExcutionUtilitiesCookEditView.as_view()),

    #:::::::::::::::::::::: PMS PRE EXECUTION OFFICE SETUP MASTER:::::::::::::::::::::::::::::::::::::::::::::::::::#
    # path('pre_excution_office_set_up_master_add/', views.PreExecutionOfficeSetupMasterAddView.as_view()),
    # path('pre_excution_office_set_up_master_edit/<pk>/', views.PreExecutionOfficeSetupMasterEditView.as_view()),
    # path('pre_excution_office_set_up_master_delete/<pk>/', views.PreExecutionOfficeSetupMasterDeleteView.as_view()),

    #::::::::::::PMS PRE EXCUTION OFFICE STRUCTURE::::::::::::::::::::::::::::::::::::::#
    path('pre_execution_office_structure_add/', views.PreExecutionOfficeStructureAddView.as_view()),
    path('pre_execution_office_structure_edit/<pk>/', views.PreExecutionOfficeStructureEditView.as_view()),
    path('pre_execution_office_structure_delete/<pk>/', views.PreExecutionOfficeStructureDeleteView.as_view()),
    path('pre_execution_office_structure_document_add/', views.PreExecutionOfficeStructureDocumentAddView.as_view()),
    path('pre_execution_office_structure_document_edit/<pk>/', views.PreExecutionOfficeStructureDocumentEditView.as_view()),
    path('pre_execution_office_structure_document_delete/<pk>/', views.PreExecutionOfficeStructureDocumentDeleteView.as_view()),

	#:::::::::::::::::::::: PMS PRE EXECUTION ELECTRICAL CONNECTION:::::::::::::::::::::::::::::::::#
    path('pre_excution_electrical_connection_add/', views.PreExecutionElectricalConnectionAddView.as_view()),
    path('pre_excution_electrical_connection_edit/<pk>/', views.PreExecutionElectricalConnectionEditView.as_view()),
    path('pre_excution_electrical_connection_document_add/', views.PreExecutionElectricalConnectionDocumentAddView.as_view()),
    path('pre_excution_electrical_connection_document_edit/<pk>/', views.PreExecutionElectricalConnectionDocumentEditView.as_view()),
    path('pre_excution_electrical_connection_document_delete/<pk>/', views.PreExecutionElectricalConnectionDocumentDeleteView.as_view()),

    #:::::::::::::::::::::: PMS PRE EXECUTION WATER CONNECTION::::::::::::::::::::::::::::::::::::#
    path('pre_excution_water_connection_add/', views.PreExecutionWaterConnectionAddView.as_view()),
    path('pre_excution_water_connection_edit/<pk>/', views.PreExecutionWaterConnectionEditView.as_view()),
    path('pre_excution_water_connection_document_add/', views.PreExecutionWaterConnectionDocumentAddView.as_view()),
    path('pre_excution_water_connection_document_edit/<pk>/', views.PreExecutionWaterConnectionDocumentEditView.as_view()),
    path('pre_excution_water_connection_document_delete/<pk>/', views.PreExecutionWaterConnectionDocumentDeleteView.as_view()),

    #:::::::::::::::::::::: PMS PRE EXECUTION INTERNET CONNECTION:::::::::::::::::::::::::::::::::#
    path('pre_excution_internet_connection_add/', views.PreExecutionInternetConnectionAddView.as_view()),
    path('pre_excution_internet_connection_edit/<pk>/', views.PreExecutionInternetConnectionEditView.as_view()),
    path('pre_excution_internet_connection_document_add/', views.PreExecutionInternetConnectionDocumentAddView.as_view()),
    path('pre_excution_internet_connection_document_edit/<pk>/', views.PreExecutionInternetConnectionDocumentEditView.as_view()),
    path('pre_excution_internet_connection_document_delete/<pk>/', views.PreExecutionInternetConnectionDocumentDeleteView.as_view()),

    #:::::::::::::::::::::: PMS PRE EXCUTION OFFICE SETUP FURNITURE::::::::::::::::::::::::::::::::::::#
    path('pre_excution_office_setup_furniture_add/', views.PreExcutionOfficeSetupFurnitureAddView.as_view()),
    path('pre_excution_office_setup_furniture_edit/<pk>/', views.PreExcutionOfficeSetupFurnitureEditView.as_view()),
    path('pre_excution_office_setup_furniture_document_add/', views.PreExcutionOfficeSetupFurnitureDocumentAddView.as_view()),
    path('pre_excution_office_setup_furniture_document_edit/<pk>/', views.PreExcutionOfficeSetupFurnitureDocumentEditView.as_view()),
    path('pre_excution_office_setup_furniture_document_delete/<pk>/', views.PreExcutionOfficeSetupFurnitureDocumentDeleteView.as_view()),

    #:::::::::::::::::::::: PMS PRE EXCUTION OFFICE SETUP COMPUTER:::::::::::::::::::::::::::::::::::::::#
    path('pre_excution_office_setup_computer_add/', views.PreExcutionOfficeSetupComputerAddView.as_view()),
    path('pre_excution_office_setup_computer_edit/<pk>/', views.PreExcutionOfficeSetupComputerEditView.as_view()),
    path('pre_excution_office_setup_computer_document_add/', views.PreExcutionOfficeSetupComputerDocumentAddView.as_view()),
    path('pre_excution_office_setup_computer_document_edit/<pk>/', views.PreExcutionOfficeSetupComputerDocumentEditView.as_view()),
    path('pre_excution_office_setup_computer_document_delete/<pk>/', views.PreExcutionOfficeSetupComputerDocumentDeleteView.as_view()),

    #::::::::::::PMS PRE EXCUTION OFFICE SETUP STATIONARY:::::::::::::::::::::::::::::::::::#
    path('pre_excution_office_setup_stationary_add/', views.PreExecutionOfficeSetupStationaryAddView.as_view()),
    path('pre_excution_office_setup_stationary_edit/<pk>/', views.PreExecutionOfficeSetupStationaryEditView.as_view()),
    path('pre_excution_office_setup_stationary_requirements_document_add/', views.PreExecutionOfficeSetupStationaryRequirementsDocumentAddView.as_view()),
    path('pre_excution_office_setup_stationary_requirements_document_edit/<pk>/', views.PreExecutionOfficeSetupStationaryRequirementsDocumentEditView.as_view()),
    path('pre_excution_office_setup_stationary_requirements_document_delete/<pk>/', views.PreExecutionOfficeSetupStationaryRequirementsDocumentDeleteView.as_view()),
    path('pre_excution_office_setup_stationary_requirements_list/', views.PreExecutionOfficeSetupStationaryRequirementsListView.as_view()),
    path('pre_excution_office_setup_stationary_requirements_edit/<pk>/', views.PreExecutionOfficeSetupStationaryRequirementsEditView.as_view()),
    path('pre_excution_office_setup_stationary_requirements_delete/<pk>/', views.PreExecutionOfficeSetupStationaryRequirementsDeleteView.as_view()),

    #:::::::::::::::::::::: PMS PRE EXCUTION OFFICE SETUP TOILET:::::::::::::::::::::::::::::::#
    path('pre_excution_office_setup_toilet_add/', views.PreExcutionOfficeSetupToiletAddView.as_view()),
    path('pre_excution_office_setup_toilet_edit/<pk>/', views.PreExcutionOfficeSetupToiletEditView.as_view()),
    path('pre_excution_office_setup_toilet_document_add/', views.PreExcutionOfficeSetupToiletDocumentAddView.as_view()),
    path('pre_excution_office_setup_toilet_document_edit/<pk>/', views.PreExcutionOfficeSetupToiletDocumentEditView.as_view()),
    path('pre_excution_office_setup_toilet_document_delete/<pk>/', views.PreExcutionOfficeSetupToiletDocumentDeleteView.as_view()),

    #:::::::::::::::::::::: PMS PRE EXCUTION OFFICE SETUP VEHICLE:::::::::::::::::::::::::::#
    path('pre_excution_office_setup_vehicle_add/', views.PreExcutionOfficeSetupVehicleAddView.as_view()),
    path('pre_excution_office_setup_vehicle_edit/<pk>/', views.PreExcutionOfficeSetupVehicleEditView.as_view()),
    path('pre_excution_office_setup_vehicle_document_add/', views.PreExcutionOfficeSetupVehicleDocumentAddView.as_view()),
    path('pre_excution_office_setup_vehicle_document_edit/<pk>/',views.PreExcutionOfficeSetupVehicleDocumentEditView.as_view()),
    path('pre_excution_office_setup_vehicle_document_delete/<pk>/',views.PreExcutionOfficeSetupVehicleDocumentDeleteView.as_view()),
    path('pre_excution_office_setup_vehicle_driver_list/',views.PreExcutionOfficeSetupVehicleDriverListView.as_view()),
    path('pre_excution_office_setup_vehicle_driver_edit/<pk>/',views.PreExcutionOfficeSetupVehicleDriverEditView.as_view()),
    path('pre_excution_office_setup_vehicle_driver_delete/<pk>/',views.PreExcutionOfficeSetupVehicleDriverDeleteView.as_view()),

	#:::::::::::::::::::::: PMS PRE EXECUTION OFFICE SETUP BIKE:::::::::::::::::::::::::#
    path('pre_excution_office_setup_bike_add/', views.PreExecutionOfficeSetupBikeAddView.as_view()),
    path('pre_excution_office_setup_bike_edit/<pk>/', views.PreExecutionOfficeSetupBikeEditView.as_view()),
    path('pre_excution_office_setup_bike_document_add/', views.PreExecutionOfficeSetupBikeDocumentAddView.as_view()),
    path('pre_excution_office_setup_bike_document_edit/<pk>/', views.PreExecutionOfficeSetupBikeDocumentEditView.as_view()),
    path('pre_excution_office_setup_bike_document_delete/<pk>/', views.PreExecutionOfficeSetupBikeDocumentDeleteView.as_view()),

    #:::::::::::::::::::::: PMS PRE EXECUTION OFFICE SETUP LABOUR LABOUR HUTMENT:::::::::::::::::::::::::::#
    path('pre_excution_office_setup_labour_labour_hutment_add/', views.PreExecutionOfficeSetupLabourLabourHutmentAddView.as_view()),
    path('pre_excution_office_setup_labour_labour_hutment_edit/<pk>/', views.PreExecutionOfficeSetupLabourLabourHutmentEditView.as_view()),
    path('pre_excution_office_setup_labour_labour_hutment_document_add/', views.PreExecutionOfficeSetupLabourLabourHutmentDocumentAddView.as_view()),
    path('pre_excution_office_setup_labour_labour_hutment_document_edit/<pk>/', views.PreExecutionOfficeSetupLabourLabourHutmentDocumentEditView.as_view()),
    path('pre_excution_office_setup_labour_labour_hutment_document_delete/<pk>/', views.PreExecutionOfficeSetupLabourLabourHutmentDocumentDeleteView.as_view()),

    #:::::::::::::::::::::: PMS PRE EXECUTION OFFICE SETUP LABOUR TOILET:::::::::::::::::::::::::::#
    path('pre_excution_office_setup_labour_toilet_add/', views.PreExecutionOfficeSetupLabourToiletAddView.as_view()),
    path('pre_excution_office_setup_labour_toilet_edit/<pk>/', views.PreExecutionOfficeSetupLabourToiletEditView.as_view()),
    path('pre_excution_office_setup_labour_toilet_document_add/', views.PreExecutionOfficeSetupLabourToiletDocumentAddView.as_view()),
    path('pre_excution_office_setup_labour_toilet_document_edit/<pk>/', views.PreExecutionOfficeSetupLabourToiletDocumentEditView.as_view()),
    path('pre_excution_office_setup_labour_toilet_document_delete/<pk>/', views.PreExecutionOfficeSetupLabourToiletDocumentDeleteView.as_view()),

    #:::::::::::::::::::::: PMS PRE EXECUTION OFFICE SETUP LABOUR WATER CONNECTION:::::::::::::::::::::::::::#
    path('pre_excution_office_setup_labour_water_connection_add/', views.PreExecutionOfficeSetupLabourWaterConnectionAddView.as_view()),
    path('pre_excution_office_setup_labour_water_connection_edit/<pk>/', views.PreExecutionOfficeSetupLabourWaterConnectionEditView.as_view()),
    path('pre_excution_office_setup_labour_water_connection_document_add/', views.PreExecutionOfficeSetupLabourWaterConnectionDocumentAddView.as_view()),
    path('pre_excution_office_setup_labour_water_connection_document_edit/<pk>/', views.PreExecutionOfficeSetupLabourWaterConnectionDocumentEditView.as_view()),
    path('pre_excution_office_setup_labour_water_connection_document_delete/<pk>/', views.PreExecutionOfficeSetupLabourWaterConnectionDocumentDeleteView.as_view()),

    #:::::::::::::::::::::: PMS PRE EXECUTION OFFICE SETUP LABOUR ELECTRICAL CONNECTION:::::::::::::::::::::::::::#
    path('pre_excution_office_setup_labour_electrical_connection_add/', views.PreExecutionOfficeSetupLabourElectricalConnectionAddView.as_view()),
    path('pre_excution_office_setup_labour_electrical_connection_edit/<pk>/', views.PreExecutionOfficeSetupLabourElectricalConnectionEditView.as_view()),
    path('pre_excution_office_setup_labour_electrical_connection_document_add/', views.PreExecutionOfficeSetupLabourElectricalConnectionDocumentAddView.as_view()),
    path('pre_excution_office_setup_labour_electrical_connection_document_edit/<pk>/', views.PreExecutionOfficeSetupLabourElectricalConnectionDocumentEditView.as_view()),
    path('pre_excution_office_setup_labour_electrical_connection_document_delete/<pk>/', views.PreExecutionOfficeSetupLabourElectricalConnectionDocumentDeleteView.as_view()),

    #:::::::::::::::::::::: PMS PRE EXECUTION OFFICE SETUP RAW MATERIAL YARD:::::::::::::::::::::::::::#
    path('pre_excution_office_setup_raw_material_yard_add/', views.PreExecutionOfficeSetupRawMaterialYardAddView.as_view()),
    path('pre_excution_office_setup_raw_material_yard_edit/<pk>/', views.PreExecutionOfficeSetupRawMaterialYardEditView.as_view()),
    path('pre_excution_office_setup_raw_material_yard_document_add/', views.PreExecutionOfficeSetupRawMaterialYardDocumentAddView.as_view()),
    path('pre_excution_office_setup_raw_material_yard_document_edit/<pk>/', views.PreExecutionOfficeSetupRawMaterialYardDocumentEditView.as_view()),
    path('pre_excution_office_setup_raw_material_yard_document_delete/<pk>/', views.PreExecutionOfficeSetupRawMaterialYardDocumentDeleteView.as_view()),

    #:::::::::::::::::::::: PMS PRE EXECUTION OFFICE SETUP CEMENT GODOWN:::::::::::::::::::::::::::::::#
    path('pre_excution_office_setup_cement_go_down_add/', views.PreExecutionOfficeSetupCementGodownAddView.as_view()),
    path('pre_excution_office_setup_cement_go_down_edit/<pk>/', views.PreExecutionOfficeSetupCementGodownEditView.as_view()),
    path('pre_excution_office_setup_cement_go_down_document_add/', views.PreExecutionOfficeSetupCementGodownDocumentAddView.as_view()),
    path('pre_excution_office_setup_cement_go_down_document_edit/<pk>/', views.PreExecutionOfficeSetupCementGodownDocumentEditView.as_view()),
    path('pre_excution_office_setup_cement_go_down_document_delete/<pk>/', views.PreExecutionOfficeSetupCementGodownDocumentDeleteView.as_view()),

    #:::::::::::::::::::::: PMS PRE EXECUTION OFFICE SETUP LAB:::::::::::::::::::::::::::#
    path('pre_excution_office_setup_lab_add/', views.PreExecutionOfficeSetupLabAddView.as_view()),
    path('pre_excution_office_setup_lab_edit/<pk>/', views.PreExecutionOfficeSetupLabEditView.as_view()),
    path('pre_excution_office_setup_lab_document_add/', views.PreExecutionOfficeSetupLabDocumentAddView.as_view()),
    path('pre_excution_office_setup_lab_document_edit/<pk>/', views.PreExecutionOfficeSetupLabDocumentEditView.as_view()),
    path('pre_excution_office_setup_lab_document_delete/<pk>/', views.PreExecutionOfficeSetupLabDocumentDeleteView.as_view()),

    #:::::::::::::PMS PRE EXECUTION OFFICE SETUP SURVEY INSTRUMENT:::::::::::::::::::::::::#
    path('pre_excution_office_setup_survey_instrument_add/', views.PreExecutionOfficeSetupSurveyInstrumentAddView.as_view()),
    path('pre_excution_office_setup_survey_instrument_edit/<pk>/', views.PreExecutionOfficeSetupSurveyInstrumentEditView.as_view()),
    path('pre_excution_office_setup_survey_instrument_types_document_add/', views.PreExecutionOfficeSetupSurveyInstrumentTypesDocumentAddView.as_view()),
    path('pre_excution_office_setup_survey_instrument_types_document_edit/<pk>/', views.PreExecutionOfficeSetupSurveyInstrumentTypesDocumentEditView.as_view()),
    path('pre_excution_office_setup_survey_instrument_types_document_delete/<pk>/', views.PreExecutionOfficeSetupSurveyInstrumentTypesDocumentDeleteView.as_view()),
    path('pre_excution_office_setup_survey_instrument_types_list/', views.PreExecutionOfficeSetupSurveyInstrumentTypesListView.as_view()),
    path('pre_excution_office_setup_survey_instrument_types_edit/<pk>/', views.PreExecutionOfficeSetupSurveyInstrumentTypesEditView.as_view()),
    path('pre_excution_office_setup_survey_instrument_types_delete/<pk>/', views.PreExecutionOfficeSetupSurveyInstrumentTypesDeleteView.as_view()),

    #:::::::::::::PMS PRE EXECUTION OFFICE SETUP SAFTEY PPE's:::::::::::::::::::::::::::::::::#
    path('pre_excution_office_setup_safety_ppes_add/', views.PreExecutionOfficeSetupSafetyPPEsAddView.as_view()),
    path('pre_excution_office_setup_safety_ppes_edit/<pk>/', views.PreExecutionOfficeSetupSafetyPPEsEditView.as_view()),
    path('pre_excution_office_setup_safety_ppes_document_add/', views.PreExecutionOfficeSetupSafetyPPEsDocumentAddView.as_view()),
    path('pre_excution_office_setup_safety_ppes_document_edit/<pk>/', views.PreExecutionOfficeSetupSafetyPPEsDocumentEditView.as_view()),
    path('pre_excution_office_setup_safety_ppes_document_delete/<pk>/', views.PreExecutionOfficeSetupSafetyPPEsDocumentDeleteView.as_view()),
    path('pre_excution_office_setup_safety_ppes_accessory_list/', views.PreExecutionOfficeSetupSafetyPPEsAccessoryListView.as_view()),
    path('pre_excution_office_setup_safety_ppes_accessory_edit/<pk>/', views.PreExecutionOfficeSetupSafetyPPEsAccessoryEditView.as_view()),
    path('pre_excution_office_setup_safety_ppes_accessory_delete/<pk>/', views.PreExecutionOfficeSetupSafetyPPEsAccessoryDeleteView.as_view()),

	#:::::::::::::::::::::: PMS PRE EXECUTION OFFICE SETUP SECURITY ROOM::::::::::::::::::::::::::::::::::#
    path('pre_excution_office_setup_security_room_add/', views.PreExecutionOfficeSetupSecurityRoomAddView.as_view()),
    path('pre_excution_office_setup_security_room_edit/<pk>/', views.PreExecutionOfficeSetupSecurityRoomEditView.as_view()),
    path('pre_excution_office_setup_security_room_document_add/', views.PreExecutionOfficeSetupSecurityRoomDocumentAddView.as_view()),
    path('pre_excution_office_setup_security_room_document_edit/<pk>/', views.PreExecutionOfficeSetupSecurityRoomDocumentEditView.as_view()),
    path('pre_excution_office_setup_security_room_document_delete/<pk>/', views.PreExecutionOfficeSetupSecurityRoomDocumentDeleteView.as_view()),

	#:::::::::::::::::::::: PMS PRE EXECUTION P AND M DETAILS::::::::::::::::::::::::::::#
    path('pre_excution_p_and_m_machinery_type_ex_details_add/', views.PreExecutionPAndMMachineryTypeExDetailsAddView.as_view()),
    path('pre_excution_p_and_m_machinery_type_details_add/', views.PreExecutionPAndMMachineryTypeDetailsAddView.as_view()),
    path('machinary_type_list_by_project/<project>/',views.MachinaryTypeListByProjectView.as_view()),
    path('pre_excution_p_and_m_details_edit/<pk>/', views.PreExecutionPAndMDetailsEditView.as_view()),
    path('pre_excution_p_and_m_details_document_add/', views.PreExecutionPAndMDetailsDocumentAddView.as_view()),
    path('pre_excution_p_and_m_details_document_edit/<pk>/', views.PreExecutionPAndMDetailsDocumentEditView.as_view()),
    path('pre_excution_p_and_m_details_document_delete/<pk>/', views.PreExecutionPAndMDetailsDocumentDeleteView.as_view()),

    #:::::::::::::::::::::::::::::::::: PMS PRE EXECUTION MANPOWER ::::::::::::::::::::::::::#
    
    path('pre_excution_manpower_requirement_add/', views.PreExecutionManpowerRequirementAddView.as_view()),
    path('pre_excution_manpower_requirement_edit/<pk>/', views.PreExecutionManpowerRequirementEditView.as_view()),
    path('pre_excution_manpower_requirement_delete/<pk>/', views.PreExecutionManpowerRequirementDeleteView.as_view()),
    path('pre_excution_manpower_details_document_add/', views.PreExecutionManpowerDetailsDocumentAddView.as_view()),
    path('pre_excution_manpower_details_document_edit/<pk>/', views.PreExecutionManpowerDetailsDocumentEditView.as_view()),
    path('pre_excution_manpower_details_document_delete/<pk>/', views.PreExecutionManpowerDetailsDocumentDeleteView.as_view()),\

    #::::::::::::::::::::::::::::::::::::::PMS PRE EXECUTION COST ANALYSIS:::::::::::::::::::::::::::::::::#
    path('pre_excution_cost_analysis_add/', views.PreExecutionCostAnalysisAddView.as_view()),

	#:::::::::::::::::::::: PMS PRE EXECUTION CONTRACTOR FINALIZATION:::::::::::::::::::::::::::#
    path('pre_excution_contractor_finalization_add/', views.PreExecutionContractorFinalizationAddView.as_view()),
    path('pre_excution_contractor_finalization_edit/<pk>/', views.PreExecutionContractorFinalizationEditView.as_view()),
    path('pre_excution_contractor_finalization_delete/<pk>/', views.PreExecutionContractorFinalizationDeleteView.as_view()),
    path('pre_excution_contractor_finalization_list/', views.PreExecutionContractorFinalizationListView.as_view()),
    #:::::::::::::::::::::::::::::::::: PMS PRE EXECUTION SITE PUJA::::::::::::::::::::::::#
    path('pre_excution_site_puja_add/', views.PreExecutionSitePujaAddView.as_view()),
    path('pre_excution_site_puja_edit/<pk>/', views.PreExecutionSitePujaEditView.as_view()),
    path('pre_excution_site_puja_delete/<pk>/', views.PreExecutionSitePujaDeleteView.as_view()),
    #::::::::::::::::::::::::PMS PRE EXECUTION APPROVAL::::::::::::::::::::::::::::::::::::::::::::::::::::::::#
    path('pre_execution_approval_add_or_update/<project_id>/', views.PreExecutionApprovalAddOrUpdateView.as_view())
    
]