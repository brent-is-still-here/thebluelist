from django import forms
from relocation_planner.models import VisaRequirement

class EditVisaRequirementForm(forms.ModelForm):
    class Meta:
        model = VisaRequirement
        fields = ["name", "description"]
