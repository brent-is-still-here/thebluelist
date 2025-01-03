from django.contrib import messages
from django.db import transaction
from django.forms import modelformset_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from .forms.edit_country import EditCountryForm
from .forms.pet_relocation_requirement_formset import PetRelocationRequirementFormSet
from .forms.visa_formset import VisaFormSet, VisaRequirementFormSet
from .models import (
    Country,
    Language,
    Visa,
    VisaRequirement,
    PetRelocationRequirement,
    AnimalSpecies
)

import uuid

import logging
logger = logging.getLogger(__name__)

class LandingView(View):
    def get(self, request):
        return render(request, "relocation_planner/landing.html")

class BrowseView(View):
    def get(self, request):
        countries = Country.objects.all().order_by('name')
        return render(request, "relocation_planner/browse.html", {
            "countries": countries
        })

class CountryDetailView(View):
    def get(self, request, slug):
        country = get_object_or_404(
            Country.objects.prefetch_related(
                'common_languages',
                'visa_list',
                'visa_list__requirement_list',
                'pet_requirement_list',
                'pet_requirement_list__animal'
            ).select_related('business_language'),
            slug=slug
        )
        return render(request, "relocation_planner/country_detail.html", {
            "country": country
        })

class EditCountryView(View):
    template_name = "relocation_planner/edit_country.html"

    def get_visa_requirement_formsets(self, visas):
        requirement_formsets = {}
        for visa in visas:
            visa_id = visa.id if visa.id else f'new_{uuid.uuid4().hex}'
            prefix = f'visa_{visa_id}_requirements'
            formset = VisaRequirementFormSet(
                instance=visa,
                prefix=prefix
            )
            requirement_formsets[visa_id] = formset
        return requirement_formsets

    def get(self, request, slug=None):
        country = get_object_or_404(Country, slug=slug) if slug else None
        country_form = EditCountryForm(instance=country)
        visa_formset = VisaFormSet(instance=country if country else None, prefix='visas')
        requirement_formsets = self.get_visa_requirement_formsets(
            country.visa_list.all() if country else []
        )
        pet_requirement_formset = PetRelocationRequirementFormSet(
            instance=country if country else None, 
            prefix='pet_requirements'
        )

        context = {
            "country": country,
            "country_form": country_form,
            "visa_formset": visa_formset,
            "requirement_formsets": requirement_formsets,
            "pet_requirement_formset": pet_requirement_formset,
        }
        return render(request, self.template_name, context)

    def post(self, request, slug=None):
        print("POST received")
        print("POST data keys:", request.POST.keys())

        country = get_object_or_404(Country, slug=slug) if slug else None
        country_form = EditCountryForm(request.POST, instance=country)
        visa_formset = VisaFormSet(request.POST, instance=country if country else None, prefix='visas')
        pet_requirement_formset = PetRelocationRequirementFormSet(
            request.POST, 
            instance=country if country else None,
            prefix='pet_requirements'
        )

        # First validate the main forms
        country_form_valid = country_form.is_valid()
        visa_formset_valid = visa_formset.is_valid()
        pet_requirement_valid = pet_requirement_formset.is_valid()

        print(f"Country form valid: {country_form_valid}")
        print(f"Visa formset valid: {visa_formset_valid}")
        print(f"Pet requirement formset valid: {pet_requirement_valid}")

        if not visa_formset_valid:
            print(f"Visa formset errors: {visa_formset.errors}")
        if not pet_requirement_valid:
            print(f"Pet requirement formset errors: {pet_requirement_formset.errors}")

        # Process and validate visa requirements if main forms are valid
        requirement_formsets = {}
        visa_requirements_valid = True

        if country_form_valid and visa_formset_valid and pet_requirement_valid:
            # Save the country first to ensure it exists for relationships
            country = country_form.save()

            # Process each visa and its requirements
            for visa_form in visa_formset.forms:
                if not visa_form.cleaned_data.get('DELETE', False):
                    # Save the visa first
                    visa = visa_form.save(commit=False)
                    visa.country = country
                    visa.save()

                    # Now handle requirements for this visa
                    visa_id = str(visa.id) if visa.id else f'new_{uuid.uuid4().hex}'
                    prefix = f'visa_{visa_id}_requirements'

                    print(f"Looking for requirements with prefix: {prefix}")
                    requirement_keys = [k for k in request.POST.keys() if k.startswith(prefix)]
                    print(f"Found requirement keys: {requirement_keys}")

                    if requirement_keys:
                        requirement_formset = VisaRequirementFormSet(
                            request.POST,
                            instance=visa,
                            prefix=prefix
                        )

                        if requirement_formset.is_valid():
                            print(f"Processing requirements for visa {visa_id}")
                            # Save requirements
                            requirements = requirement_formset.save(commit=False)
                            for requirement in requirements:
                                requirement.visa = visa
                                requirement.save()
                            
                            # Handle deletions
                            for obj in requirement_formset.deleted_objects:
                                obj.delete()
                        else:
                            print(f"Requirement formset errors for visa {visa_id}: {requirement_formset.errors}")
                            visa_requirements_valid = False
                else:
                    # Handle visa deletion
                    if visa_form.instance.pk:
                        visa_form.instance.delete()

            # Process pet requirements if everything else is valid
            if visa_requirements_valid:
                for req_form in pet_requirement_formset.forms:
                    if not req_form.cleaned_data.get('DELETE', False):
                        requirement = req_form.save(commit=False)
                        requirement.country = country
                        requirement.save()
                    else:
                        if req_form.instance.pk:
                            req_form.instance.delete()

                return redirect("relocation_planner:country_detail", slug=country.slug)

        # If we get here, something failed validation
        if not requirement_formsets:
            requirement_formsets = self.get_visa_requirement_formsets(
                [form.instance for form in visa_formset.forms if form.instance.pk and not form.cleaned_data.get('DELETE', False)]
            )

        context = {
            "country": country,
            "country_form": country_form,
            "visa_formset": visa_formset,
            "requirement_formsets": requirement_formsets,
            "pet_requirement_formset": pet_requirement_formset,
        }
        return render(request, self.template_name, context)

class AssessmentView(View):
    def get(self, request):
        return render(request, "relocation_planner/assessment.html")

    def post(self, request):
        try:
            # Get user preferences
            healthcare_required = request.POST.get('healthcare_required') == 'on'
            cost_of_living_max = request.POST.get('cost_of_living_max')
            quality_of_life_min = request.POST.get('quality_of_life_min')
            
            # Filter countries based on preferences
            countries = Country.objects.all()
            
            if healthcare_required:
                countries = countries.filter(has_universal_healthcare=True)
            
            if cost_of_living_max:
                countries = countries.filter(cost_of_living_index__lte=cost_of_living_max)
                
            if quality_of_life_min:
                countries = countries.filter(quality_of_life_index__gte=quality_of_life_min)
            
            return render(request, "relocation_planner/assessment_results.html", {
                "countries": countries
            })
            
        except Exception as e:
            logger.error(f"Error in assessment: {str(e)}")
            messages.error(request, "An error occurred during assessment. Please try again.")
            return redirect("relocation_planner:assessment")

class AssessmentResultsView(View):
    def get(self, request):
        return render(request, "relocation_planner/assessment_results.html", {
            "countries": []
        })