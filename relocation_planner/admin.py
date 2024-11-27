from django.contrib import admin
from .models import AnimalSpecies, PetRelocationRequirement

@admin.register(AnimalSpecies)
class AnimalSpeciesAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(PetRelocationRequirement)
class PetRelocationRequirementAdmin(admin.ModelAdmin):
    list_display = ('name', 'animal', 'type', 'duration')
    list_filter = ('animal', 'type')
    search_fields = ('name', 'description')