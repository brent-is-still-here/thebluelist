from django import forms
from relocation_planner.models import PetRelocationRequirement

class EditPetRelocationRequirementForm(forms.ModelForm):
    class Meta:
        model = PetRelocationRequirement
        fields = ["animal", "type", "name", "description", "duration"]
        widgets = {
            'type': forms.Select(attrs={'class': 'w-full border-gray-300 rounded-md'}),
            'animal': forms.Select(attrs={'class': 'w-full border-gray-300 rounded-md'}),
            'name': forms.TextInput(attrs={'class': 'w-full border-gray-300 rounded-md'}),
            'description': forms.Textarea(attrs={'class': 'w-full border-gray-300 rounded-md', 'rows': 3}),
            'duration': forms.TextInput(attrs={'class': 'w-full border-gray-300 rounded-md'}),
        }