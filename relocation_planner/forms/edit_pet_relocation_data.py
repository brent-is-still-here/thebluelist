from django import forms
from relocation_planner.models import PetRelocationRequirement

class EditPetRelocationRequirementForm(forms.ModelForm):
    class Meta:
        model = PetRelocationRequirement
        fields = ["animal", "type", "name", "description", "duration"]
