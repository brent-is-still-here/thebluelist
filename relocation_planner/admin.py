from django.contrib import admin
from .models import (
    Country, 
    Language, 
    Visa, 
    VisaRequirement, 
    AnimalSpecies, 
    PetRelocationRequirement
)

# Inline admin classes for nested relationships
class VisaRequirementInline(admin.TabularInline):
    model = VisaRequirement
    extra = 1

class VisaInline(admin.StackedInline):
    model = Visa
    extra = 1
    inlines = [VisaRequirementInline]
    show_change_link = True

class PetRelocationRequirementInline(admin.TabularInline):
    model = PetRelocationRequirement
    extra = 1

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'business_language', 'cost_of_living_index', 'quality_of_life_index')
    list_filter = ('has_universal_healthcare', 'business_language')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('common_languages',)
    inlines = [VisaInline, PetRelocationRequirementInline]

@admin.register(Visa)
class VisaAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'duration')
    list_filter = ('country',)
    search_fields = ('name', 'country__name')
    inlines = [VisaRequirementInline]

@admin.register(VisaRequirement)
class VisaRequirementAdmin(admin.ModelAdmin):
    list_display = ('name', 'visa')
    list_filter = ('visa__country',)
    search_fields = ('name', 'description', 'visa__name')

@admin.register(AnimalSpecies)
class AnimalSpeciesAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(PetRelocationRequirement)
class PetRelocationRequirementAdmin(admin.ModelAdmin):
    list_display = ('name', 'animal', 'type', 'country')
    list_filter = ('animal', 'type', 'country')
    search_fields = ('name', 'description', 'country__name')

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)