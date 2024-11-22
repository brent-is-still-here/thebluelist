from django.contrib import messages
from django.db import transaction
from django.forms import modelformset_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from .forms.edit_country import EditCountryForm
from .forms.visa_formset import VisaFormSet, VisaRequirementFormSet
from .models import (
    Country,
    Language,
    Visa,
    VisaRequirement,
    PetRelocationRequirement,
    AnimalSpecies
)

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
                'pet_relocation_requirements',
                'pet_relocation_requirements__animal'
            ).select_related('business_language'),
            slug=slug
        )
        return render(request, "relocation_planner/country_detail.html", {
            "country": country
        })

# class EditCountryView(View):
#     def get(self, request, slug=None):
#         logger.debug(f"GET request received for slug: {slug}")
#         try:
#             country = None
#             if slug:
#                 country = get_object_or_404(Country, slug=slug)
            
#             context = {
#                 "country": country,
#                 "languages": Language.objects.all().order_by('name'),
#                 "visas": Visa.objects.all().order_by('name'),
#                 "pet_requirements": PetRelocationRequirement.objects.all().order_by('animal__name', 'type'),
#                 "animals": AnimalSpecies.objects.all().order_by('name'),
#             }
            
#             return render(request, "relocation_planner/edit_country.html", context)
#         except Exception as e:
#             logger.error(f"Error in GET: {str(e)}")
#             raise

#     def post(self, request, slug=None):
#         logger.debug("POST data received:")
#         for key, value in request.POST.items():
#             logger.debug(f"{key}: {value}")

#         try:
#             # Start a transaction since we're handling multiple related models
#             with transaction.atomic():
#                 if slug:
#                     country = get_object_or_404(Country, slug=slug)
#                 else:
#                     country = Country()

#                 # Update basic country fields as before...
#                 country.name = request.POST.get("name")
#                 country.cost_of_living_index = request.POST.get("cost_of_living_index") or None
#                 country.quality_of_life_index = request.POST.get("quality_of_life_index") or None
#                 country.has_universal_healthcare = request.POST.get("has_universal_healthcare") == "on"
#                 country.pet_relocation_info_link = request.POST.get("pet_relocation_info_link", "")
#                 country.business_language_id = request.POST.get("business_language") or None
                
#                 # Set the user who made the changes
#                 if not country.id:
#                     country.created_by = request.user
#                 country.last_modified_by = request.user
                
#                 country.save()

#                 # Update many-to-many relationships
#                 common_languages_ids = request.POST.getlist("common_languages")
#                 country.common_languages.set(common_languages_ids)

#                 # Handle existing visas
#                 visa_ids = request.POST.getlist("visa_ids[]")
#                 existing_visas = set()  # Keep track of visas we're updating
                
#                 for visa_id in visa_ids:
#                     logger.debug(f"Processing visa {visa_id}")

#                     try:
#                         visa = Visa.objects.get(id=visa_id)
#                         existing_visas.add(visa.id)
                        
#                         # Update visa fields
#                         visa.name = request.POST.get(f"visa_name_{visa_id}")
#                         visa.duration = request.POST.get(f"visa_duration_{visa_id}")
#                         visa.description = request.POST.get(f"visa_description_{visa_id}")
#                         visa.information_link = request.POST.get(f"visa_information_link_{visa_id}")
#                         visa.last_modified_by = request.user
#                         visa.save()

#                         # Handle existing requirements
#                         req_ids = request.POST.getlist(f"visa_requirement_ids_{visa_id}[]", [])
#                         logger.debug(f"Found existing requirement IDs: {req_ids}")
#                         existing_reqs = set()

#                         for req_id in req_ids:
#                             try:
#                                 req = VisaRequirement.objects.get(id=req_id)
#                                 existing_reqs.add(req.id)
                                
#                                 req.name = request.POST.get(f"visa_requirement_name_{visa_id}_{req_id}")
#                                 req.description = request.POST.get(f"visa_requirement_description_{visa_id}_{req_id}")
#                                 req.last_modified_by = request.user
#                                 req.save()
#                             except VisaRequirement.DoesNotExist:
#                                 logger.warning(f"Requirement {req_id} not found for visa {visa_id}")

#                         # Handle new requirements for existing visa
#                         # These come from the "Add Requirement" button in the form
#                         requirement_names = request.POST.getlist(f"new_visa_requirement_name_{visa_id}[]", [])
#                         requirement_descriptions = request.POST.getlist(f"new_visa_requirement_description_{visa_id}[]", [])

#                         logger.debug(f"New requirements for visa {visa_id}: Names={requirement_names}, Descriptions={requirement_descriptions}")

#                         for name, description in zip(requirement_names, requirement_descriptions):
#                             if name.strip():  # Only create if name is provided and not just whitespace
#                                 new_req = VisaRequirement.objects.create(
#                                     visa=visa,
#                                     name=name,
#                                     description=description,
#                                     created_by=request.user,
#                                     last_modified_by=request.user
#                                 )
#                                 existing_reqs.add(new_req.id)
#                                 logger.debug(f"Created new requirement: {new_req.id} for visa {visa_id}")

#                         # Clean up removed requirements
#                         visa.requirements.exclude(id__in=existing_reqs).delete()

#                     except Visa.DoesNotExist:
#                         messages.warning(request, f"Visa with ID {visa_id} not found")

#                 # Handle new visas and their requirements (this part seems to be working)
#                 new_visa_names = request.POST.getlist("new_visa_name[]")
#                 new_visa_durations = request.POST.getlist("new_visa_duration[]")
#                 new_visa_descriptions = request.POST.getlist("new_visa_description[]")
#                 new_visa_links = request.POST.getlist("new_visa_information_link[]")

#                 for i in range(len(new_visa_names)):
#                     if new_visa_names[i]:  # Only create if name is provided
#                         visa = Visa.objects.create(
#                             name=new_visa_names[i],
#                             duration=new_visa_durations[i],
#                             description=new_visa_descriptions[i],
#                             information_link=new_visa_links[i],
#                             created_by=request.user,
#                             last_modified_by=request.user
#                         )
#                         country.visas.add(visa)
#                         existing_visas.add(visa.id)

#                         # Handle requirements for the new visa
#                         new_req_names = request.POST.getlist(f"new_requirement_name_new_{i}[]")
#                         new_req_descriptions = request.POST.getlist(f"new_requirement_description_new_{i}[]")
#                         logger.debug(f"Found new requirements for visa {visa_id}:")
#                         logger.debug(f"Names: {new_req_names}")
#                         logger.debug(f"Descriptions: {new_req_descriptions}")
                        
#                         for name, desc in zip(new_req_names, new_req_descriptions):
#                             if name.strip():  # Only create if name is provided and not just whitespace
#                                 VisaRequirement.objects.create(
#                                     visa=visa,
#                                     name=name,
#                                     description=desc,
#                                     created_by=request.user,
#                                     last_modified_by=request.user
#                                 )

#                 # Clean up visas that were removed
#                 country.visas.exclude(id__in=existing_visas).delete()

#                 messages.success(request, f"Country {'updated' if slug else 'added'} successfully!")
#                 return redirect("relocation_planner:country_detail", slug=country.slug)
                
#         except Exception as e:
#             logger.error(f"Error saving country: {str(e)}")
#             messages.error(request, f"An error occurred: {str(e)}")
#             return self.get(request, slug)

class EditCountryView(View):
    template_name = "relocation_planner/edit_country.html"

    def get_visa_requirement_formsets(self, visas):
        requirement_formsets = {}
        for visa in visas:
            formset = VisaRequirementFormSet(
                instance=visa,
                prefix=f'requirements_{visa.id}' if visa.id else f'requirements_new_{len(requirement_formsets)}'
            )
            requirement_formsets[visa.id if visa.id else f'new_{len(requirement_formsets)}'] = formset
        return requirement_formsets

    def get(self, request, slug=None):
        country = get_object_or_404(Country, slug=slug) if slug else None
        country_form = EditCountryForm(instance=country)
        visa_formset = VisaFormSet(instance=country if country else None, prefix='visas')
        requirement_formsets = self.get_visa_requirement_formsets(
            country.visa_list.all() if country else []
        )

        context = {
            "country": country,
            "country_form": country_form,
            "visa_formset": visa_formset,
            "requirement_formsets": requirement_formsets,
        }
        return render(request, self.template_name, context)

    def post(self, request, slug=None):
        country = get_object_or_404(Country, slug=slug) if slug else None
        country_form = EditCountryForm(request.POST, instance=country)
        visa_formset = VisaFormSet(request.POST, instance=country)

        requirement_formsets = {}
        is_valid = country_form.is_valid() and visa_formset.is_valid()

        # Process existing visas
        if is_valid:
            country = country_form.save()
            visas = visa_formset.save(commit=False)

            # Handle visa deletions
            for obj in visa_formset.deleted_objects:
                obj.delete()

            # Process each visa and its requirements
            for visa_form in visa_formset.forms:
                if not visa_form.cleaned_data.get('DELETE', False):
                    visa = visa_form.save(commit=False)
                    visa.country = country
                    visa.save()

                    # Process requirements for this visa
                    prefix = f'visa_{visa.id}_requirements' if visa.id else f'new_visa_{len(requirement_formsets)}_requirements'
                    requirement_formset = VisaRequirementFormSet(
                        request.POST,
                        instance=visa,
                        prefix=prefix
                    )

                    if requirement_formset.is_valid():
                        requirements = requirement_formset.save(commit=False)
                        for req in requirement_formset.deleted_objects:
                            req.delete()
                        for requirement in requirements:
                            requirement.visa = visa
                            requirement.save()
                    else:
                        is_valid = False
                        requirement_formsets[visa.id if visa.id else f'new_{len(requirement_formsets)}'] = requirement_formset

        if is_valid:
            return redirect("relocation_planner:country_detail", slug=country.slug)

        # If we get here, there was a validation error
        if not requirement_formsets:
            requirement_formsets = self.get_visa_requirement_formsets(
                [form.instance for form in visa_formset.forms if form.instance.pk and not form.cleaned_data.get('DELETE', False)]
            )

        context = {
            "country": country,
            "country_form": country_form,
            "visa_formset": visa_formset,
            "requirement_formsets": requirement_formsets,
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