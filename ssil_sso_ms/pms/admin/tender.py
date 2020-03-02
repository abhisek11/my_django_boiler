from django.contrib import admin
from pms.models.module_tender import *

@admin.register(PmsTenderTypeMaster)
class PmsTenderTypeMaster(admin.ModelAdmin):
    list_display = [field.name for field in PmsTenderTypeMaster._meta.fields]

@admin.register(PmsTenders)
class PmsTenders(admin.ModelAdmin):
    list_display = [field.name for field in PmsTenders._meta.fields]

@admin.register(PmsTenderDocuments)
class PmsTenderDocuments(admin.ModelAdmin):
    list_display = [field.name for field in PmsTenderDocuments._meta.fields]

@admin.register(PmsTenderEligibility)
class PmsTenderEligibility(admin.ModelAdmin):
    list_display = [field.name for field in PmsTenderEligibility._meta.fields]

@admin.register(PmsTenderEligibilityFieldsByType)
class PmsTenderEligibilityFieldsByType(admin.ModelAdmin):
    list_display = [field.name for field in PmsTenderEligibilityFieldsByType._meta.fields]

@admin.register(PmsTenderPartners)
class PmsTenderPartners(admin.ModelAdmin):
    list_display = [field.name for field in PmsTenderPartners._meta.fields]

@admin.register(PmsTenderBidderType)
class PmsTenderBidderType(admin.ModelAdmin):
    list_display = [field.name for field in PmsTenderBidderType._meta.fields]

@admin.register(PmsTenderBidderTypePartnerMapping)
class PmsTenderBidderTypePartnerMapping(admin.ModelAdmin):
    list_display = [field.name for field in PmsTenderBidderTypePartnerMapping._meta.fields]

@admin.register(PmsTenderSurveySitePhotos)
class PmsTenderSurveySitePhotos(admin.ModelAdmin):
    list_display = [field.name for field in PmsTenderSurveySitePhotos._meta.fields]

@admin.register(PmsTenderSurveyCoordinatesSiteCoordinate)
class PmsTenderSurveyCoordinatesSiteCoordinate(admin.ModelAdmin):
    list_display = [field.name for field in PmsTenderSurveyCoordinatesSiteCoordinate._meta.fields]

# @admin.register(MaterialTypeMaster)
# class MaterialTypeMaster(admin.ModelAdmin):
#     list_display = [field.name for field in MaterialTypeMaster._meta.fields]

@admin.register(Materials)
class Materials(admin.ModelAdmin):
    list_display = [field.name for field in Materials._meta.fields]
    
@admin.register(MaterialsUnitMapping)
class MaterialsUnitMapping(admin.ModelAdmin):
    list_display = [field.name for field in MaterialsUnitMapping._meta.fields]

@admin.register(PmsTenderSurveyResourceMaterial)
class PmsTenderSurveyResourceMaterial(admin.ModelAdmin):
    list_display = [field.name for field in PmsTenderSurveyResourceMaterial._meta.fields]

@admin.register(PmsTenderSurveyResourceEstablishment)
class PmsTenderSurveyResourceEstablishment(admin.ModelAdmin):
    list_display = [field.name for field in PmsTenderSurveyResourceEstablishment._meta.fields]

@admin.register(PmsTenderSurveyDocument)
class PmsTenderSurveyDocument(admin.ModelAdmin):
    list_display = [field.name for field in PmsTenderSurveyDocument._meta.fields]

@admin.register(PmsTenderSurveyResourceHydrological)
class PmsTenderSurveyResourceHydrological(admin.ModelAdmin):
    list_display = [field.name for field in PmsTenderSurveyResourceHydrological._meta.fields]

@admin.register(PmsTenderSurveyResourceContractorsOVendorsContractor)
class PmsTenderSurveyResourceContractorsOVendorsContractor(admin.ModelAdmin):
    list_display = [field.name for field in PmsTenderSurveyResourceContractorsOVendorsContractor._meta.fields]

@admin.register(PmsTenderMachineryTypeDetails)
class PmsTenderMachineryTypeDetails(admin.ModelAdmin):
    list_display = [field.name for field in PmsTenderMachineryTypeDetails._meta.fields]

@admin.register(PmsTenderSurveyResourceContactDesignation)
class PmsTenderSurveyResourceContactDesignation(admin.ModelAdmin):
    list_display = [field.name for field in PmsTenderSurveyResourceContactDesignation._meta.fields]

@admin.register(PmsTenderSurveyResourceContactDetails)
class PmsTenderSurveyResourceContactDetails(admin.ModelAdmin):
    list_display = [field.name for field in PmsTenderSurveyResourceContactDetails._meta.fields]

@admin.register(PmsTenderInitialCosting)
class PmsTenderInitialCosting(admin.ModelAdmin):
    list_display = [field.name for field in PmsTenderInitialCosting._meta.fields]

@admin.register(PmsTenderInitialCostingExcelFieldLabel)
class PmsTenderInitialCostingExcelFieldLabel(admin.ModelAdmin):
    list_display = [field.name for field in PmsTenderInitialCostingExcelFieldLabel._meta.fields]

@admin.register(PmsTenderInitialCostingExcelFieldValue)
class PmsTenderInitialCostingExcelFieldValue(admin.ModelAdmin):
    list_display = [field.name for field in PmsTenderInitialCostingExcelFieldValue._meta.fields]

@admin.register(PmsTenderTabDocuments)
class PmsTenderTabDocuments(admin.ModelAdmin):
    list_display = [field.name for field in PmsTenderTabDocuments._meta.fields]

@admin.register(PmsTenderTabDocumentsDocuments)
class PmsTenderTabDocumentsDocuments(admin.ModelAdmin):
    list_display = [field.name for field in PmsTenderTabDocumentsDocuments._meta.fields]

@admin.register(PmsTenderTabDocumentsPrice)
class PmsTenderTabDocumentsPrice(admin.ModelAdmin):
    list_display = [field.name for field in PmsTenderTabDocumentsPrice._meta.fields]

@admin.register(PmsTenderApproval)
class PmsTenderApproval(admin.ModelAdmin):
    list_display = [field.name for field in PmsTenderApproval._meta.fields]

@admin.register(PmsTenderStatus)
class PmsTenderStatus(admin.ModelAdmin):
    list_display = [field.name for field in PmsTenderStatus._meta.fields]

@admin.register(PmsSiteProjectSiteManagementMultipleLongLat)
class PmsSiteProjectSiteManagementMultipleLongLat(admin.ModelAdmin):
    list_display = [field.name for field in PmsSiteProjectSiteManagementMultipleLongLat._meta.fields]