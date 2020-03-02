from django.contrib import admin
from pms.models.module_pre_execution import *


@admin.register(PmsPreExcutionGuestHouseFinding)
class PmsPreExcutionGuestHouseFinding(admin.ModelAdmin):
    list_display = [field.name for field in PmsPreExcutionGuestHouseFinding._meta.fields]

@admin.register(PmsPreExcutionFurniture)
class PmsPreExcutionFurniture(admin.ModelAdmin):
    list_display = [field.name for field in PmsPreExcutionFurniture._meta.fields]

@admin.register(PmsPreExcutionFurMFurRequirements)
class PmsPreExcutionFurMFurRequirements(admin.ModelAdmin):
    list_display = [field.name for field in PmsPreExcutionFurMFurRequirements._meta.fields]

@admin.register(PmsPreExcutionUtilitiesElectrical)
class PmsPreExcutionUtilitiesElectrical(admin.ModelAdmin):
    list_display = [field.name for field in PmsPreExcutionUtilitiesElectrical._meta.fields]

@admin.register(PmsPreExcutionUtilitiesWater)
class PmsPreExcutionUtilitiesWater(admin.ModelAdmin):
    list_display = [field.name for field in PmsPreExcutionUtilitiesWater._meta.fields]

@admin.register(PmsPreExcutionUtilitiesFuel)
class PmsPreExcutionUtilitiesFuel(admin.ModelAdmin):
    list_display = [field.name for field in PmsPreExcutionUtilitiesFuel._meta.fields]

@admin.register(PmsPreExcutionUtilitiesUtensils)
class PmsPreExcutionUtilitiesUtensils(admin.ModelAdmin):
    list_display = [field.name for field in PmsPreExcutionUtilitiesUtensils._meta.fields]

@admin.register(PmsPreExcutionUtilitiesUtensilsTypes)
class PmsPreExcutionUtilitiesUtensilsTypes(admin.ModelAdmin):
    list_display = [field.name for field in PmsPreExcutionUtilitiesUtensilsTypes._meta.fields]

@admin.register(PmsPreExcutionUtilitiesTiffinBox)
class PmsPreExcutionUtilitiesTiffinBox(admin.ModelAdmin):
    list_display = [field.name for field in PmsPreExcutionUtilitiesTiffinBox._meta.fields]

@admin.register(PmsPreExcutionUtilitiesTiffinBoxTypes)
class PmsPreExcutionUtilitiesTiffinBoxTypes(admin.ModelAdmin):
    list_display = [field.name for field in PmsPreExcutionUtilitiesTiffinBoxTypes._meta.fields]

@admin.register(PmsPreExcutionUtilitiesCook)
class PmsPreExcutionUtilitiesCook(admin.ModelAdmin):
    list_display = [field.name for field in PmsPreExcutionUtilitiesCook._meta.fields]

@admin.register(PmsPreExcutionUtilitiesDocument)
class PmsPreExcutionUtilitiesDocument(admin.ModelAdmin):
    list_display = [field.name for field in PmsPreExcutionUtilitiesDocument._meta.fields]

@admin.register(PmsPreExecutionOfficeStructure)
class PmsPreExecutionOfficeStructure(admin.ModelAdmin):
    list_display = [field.name for field in PmsPreExecutionOfficeStructure._meta.fields]

@admin.register(PmsPreExecutionElectricalConnection)
class PmsPreExecutionElectricalConnection(admin.ModelAdmin):
    list_display = [field.name for field in PmsPreExecutionElectricalConnection._meta.fields]

@admin.register(PmsPreExecutionWaterConnection)
class PmsPreExecutionWaterConnection(admin.ModelAdmin):
    list_display = [field.name for field in PmsPreExecutionWaterConnection._meta.fields]

@admin.register(PmsPreExecutionInternetConnection)
class PmsPreExecutionInternetConnection(admin.ModelAdmin):
    list_display = [field.name for field in PmsPreExecutionInternetConnection._meta.fields]

@admin.register(PmsPreExcutionOfficeSetupFurniture)
class PmsPreExcutionOfficeSetupFurniture(admin.ModelAdmin):
    list_display = [field.name for field in PmsPreExcutionOfficeSetupFurniture._meta.fields]

@admin.register(PmsPreExcutionOfficeSetupComputer)
class PmsPreExcutionOfficeSetupComputer(admin.ModelAdmin):
    list_display = [field.name for field in PmsPreExcutionOfficeSetupComputer._meta.fields]

@admin.register(PmsPreExcutionOfficeSetupStationary)
class PmsPreExcutionOfficeSetupStationary(admin.ModelAdmin):
    list_display = [field.name for field in PmsPreExcutionOfficeSetupStationary._meta.fields]

@admin.register(PmsPreExcutionOfficeSetupStationaryMStnRequirements)
class PmsPreExcutionOfficeSetupStationaryMStnRequirements(admin.ModelAdmin):
    list_display = [field.name for field in PmsPreExcutionOfficeSetupStationaryMStnRequirements._meta.fields]

@admin.register(PmsPreExcutionOfficeSetupToilet)
class PmsPreExcutionOfficeSetupToilet(admin.ModelAdmin):
    list_display = [field.name for field in PmsPreExcutionOfficeSetupToilet._meta.fields]

@admin.register(PmsPreExcutionOfficeSetupVehicle)
class PmsPreExcutionOfficeSetupVehicle(admin.ModelAdmin):
    list_display = [field.name for field in PmsPreExcutionOfficeSetupVehicle._meta.fields]

@admin.register(PmsPreExcutionOfficeSetupVehicleDriver)
class PmsPreExcutionOfficeSetupVehicleDriver(admin.ModelAdmin):
    list_display = [field.name for field in PmsPreExcutionOfficeSetupVehicleDriver._meta.fields]

@admin.register(PmsPreExecutionOfficeSetupBike)
class PmsPreExecutionOfficeSetupBike(admin.ModelAdmin):
    list_display = [field.name for field in PmsPreExecutionOfficeSetupBike._meta.fields]

@admin.register(PmsPreExecutionOfficeSetupLabourLabourHutment)
class PmsPreExecutionOfficeSetupLabourLabourHutment(admin.ModelAdmin):
    list_display = [field.name for field in PmsPreExecutionOfficeSetupLabourLabourHutment._meta.fields]

@admin.register(PmsPreExecutionOfficeSetupLabourToilet)
class PmsPreExecutionOfficeSetupLabourToilet(admin.ModelAdmin):
    list_display = [field.name for field in PmsPreExecutionOfficeSetupLabourToilet._meta.fields]

@admin.register(PmsPreExecutionOfficeSetupLabourWaterConnection)
class PmsPreExecutionOfficeSetupLabourWaterConnection(admin.ModelAdmin):
    list_display = [field.name for field in PmsPreExecutionOfficeSetupLabourWaterConnection._meta.fields]

@admin.register(PmsPreExecutionOfficeSetupLabourElectricalConnection)
class PmsPreExecutionOfficeSetupLabourElectricalConnection(admin.ModelAdmin):
    list_display = [field.name for field in PmsPreExecutionOfficeSetupLabourElectricalConnection._meta.fields]

@admin.register(PmsPreExecutionOfficeSetupRawMaterialYard)
class PmsPreExecutionOfficeSetupRawMaterialYard(admin.ModelAdmin):
    list_display = [field.name for field in PmsPreExecutionOfficeSetupRawMaterialYard._meta.fields]

@admin.register(PmsPreExecutionOfficeSetupCementGodown)
class PmsPreExecutionOfficeSetupCementGodown(admin.ModelAdmin):
    list_display = [field.name for field in PmsPreExecutionOfficeSetupCementGodown._meta.fields]

@admin.register(PmsPreExecutionOfficeSetupLab)
class PmsPreExecutionOfficeSetupLab(admin.ModelAdmin):
    list_display = [field.name for field in PmsPreExecutionOfficeSetupLab._meta.fields]

@admin.register(PmsPreExecutionOfficeSetupSurveyInstruments)
class PmsPreExecutionOfficeSetupSurveyInstruments(admin.ModelAdmin):
    list_display = [field.name for field in PmsPreExecutionOfficeSetupSurveyInstruments._meta.fields]

@admin.register(PmsPreExecutionOfficeSetupSurveyInstrumentsType)
class PmsPreExecutionOfficeSetupSurveyInstrumentsType(admin.ModelAdmin):
    list_display = [field.name for field in PmsPreExecutionOfficeSetupSurveyInstrumentsType._meta.fields]

@admin.register(PmsPreExecutionOfficeSetupSafetyPPEs)
class PmsPreExecutionOfficeSetupSafetyPPEs(admin.ModelAdmin):
    list_display = [field.name for field in PmsPreExecutionOfficeSetupSafetyPPEs._meta.fields]

@admin.register(PmsPreExecutionOfficeSetupSafetyPPEsAccessory)
class PmsPreExecutionOfficeSetupSafetyPPEsAccessory(admin.ModelAdmin):
    list_display = [field.name for field in PmsPreExecutionOfficeSetupSafetyPPEsAccessory._meta.fields]

@admin.register(PmsPreExecutionOfficeSetupSecurityRoom)
class PmsPreExecutionOfficeSetupSecurityRoom(admin.ModelAdmin):
    list_display = [field.name for field in PmsPreExecutionOfficeSetupSecurityRoom._meta.fields]

@admin.register(PmsPreExecutionMachineryTypeDetails)
class PmsPreExecutionMachineryTypeDetails(admin.ModelAdmin):
    list_display = [field.name for field in PmsPreExecutionMachineryTypeDetails._meta.fields]





@admin.register(PmsPreExecutionManpowerDetails)
class PmsPreExecutionManpowerDetails(admin.ModelAdmin):
    list_display = [field.name for field in PmsPreExecutionManpowerDetails._meta.fields]

@admin.register(PmsPreExecutionCostAnalysis)
class PmsPreExecutionCostAnalysis(admin.ModelAdmin):
    list_display = [field.name for field in PmsPreExecutionCostAnalysis._meta.fields]

@admin.register(PmsPreExecutionCostAnalysisDocument)
class PmsPreExecutionCostAnalysisDocument(admin.ModelAdmin):
    list_display = [field.name for field in PmsPreExecutionCostAnalysisDocument._meta.fields]

@admin.register(PmsPreExecutionContractorFinalization)
class PmsPreExecutionContractorFinalization(admin.ModelAdmin):
    list_display = [field.name for field in PmsPreExecutionContractorFinalization._meta.fields]

@admin.register(PmsPreExecutionSitePuja)
class PmsPreExecutionSitePuja(admin.ModelAdmin):
    list_display = [field.name for field in PmsPreExecutionSitePuja._meta.fields]
@admin.register(PmsPreExecutionApproval)
class PmsPreExecutionApproval(admin.ModelAdmin):
    list_display = [field.name for field in PmsPreExecutionApproval._meta.fields]