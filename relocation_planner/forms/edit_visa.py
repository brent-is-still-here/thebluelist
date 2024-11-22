from django import forms
from relocation_planner.models import Visa

class EditVisaForm(forms.ModelForm):
    DELETE = forms.BooleanField(required=False, widget=forms.HiddenInput())
    
    class Meta:
        model = Visa
        fields = ["name", "duration", "description", "information_link"]
