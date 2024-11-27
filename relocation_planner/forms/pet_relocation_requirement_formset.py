from django.forms import inlineformset_factory
from relocation_planner.models import Country, PetRelocationRequirement
from relocation_planner.forms.edit_pet_relocation_data import EditPetRelocationRequirementForm

PetRelocationRequirementFormSet = inlineformset_factory(
    Country,
    PetRelocationRequirement,
    form=EditPetRelocationRequirementForm,
    extra=0,
    can_delete=True
)