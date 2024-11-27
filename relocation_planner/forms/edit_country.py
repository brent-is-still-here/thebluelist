from django import forms
from relocation_planner.models import Country, Language

class EditCountryForm(forms.ModelForm):
    common_languages = forms.ModelMultipleChoiceField(
        queryset=Language.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = Country
        fields = [
            "name",
            "business_language",
            "common_languages",
            "cost_of_living_index",
            "quality_of_life_index",
            "has_universal_healthcare",
            "pet_relocation_info_link",
        ]
