from django import forms
from django.core.exceptions import ValidationError
from pack_planner.validators import validate_file_extension, validate_json_structure
import json

class AssessmentForm(forms.Form):
    # Family Composition
    adults = forms.IntegerField(
        label="Number of Adults",
        min_value=1, max_value=10,
        initial=1,
        help_text="Enter the number of adults in your party.",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    children = forms.IntegerField(
        label="Number of Children",
        min_value=0, max_value=10,
        initial=0,
        required=False,
        help_text="Enter the number of children (if any).",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    # Special Considerations
    has_elderly = forms.BooleanField(
        label="Include Elderly Family Members",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    has_disabled = forms.BooleanField(
        label="Include Family Members with Disabilities",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    # Pets Section
    has_pets = forms.BooleanField(
        label="We have pets",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'has-pets-checkbox'})
    )
    pet_types = forms.MultipleChoiceField(
        label="Type of Pets",
        choices=[
            ('dogs', 'Dogs'),
            ('cats', 'Cats'),
            ('birds', 'Birds'),
            ('other', 'Other Small Animals')
        ],
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input', 'id': 'pet-types'})
    )

    # Transportation Mode
    transport_type = forms.ChoiceField(
        label="Primary Mode of Transportation",
        choices=[
            ('walking', 'Walking/On Foot'),
            ('bicycle', 'Bicycle'),
            ('car', 'Personal Vehicle'),
            ('public', 'Public Transportation')
        ],
        initial='car',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def clean(self):
        """
        Custom validation to ensure consistency between fields.
        For example, if `has_pets` is False, `pet_types` should not have any values.
        """
        cleaned_data = super().clean()
        has_pets = cleaned_data.get('has_pets')
        pet_types = cleaned_data.get('pet_types')

        if not has_pets and pet_types:
            self.add_error('pet_types', "You cannot select pet types if you don't have pets.")

        return cleaned_data

class DataUploadForm(forms.Form):
    file = forms.FileField(
        label='Select JSON File',
        help_text='File must be in the correct JSON format',
        validators=[lambda value: validate_file_extension(value)]
    )
    UPLOAD_TYPES = [
        ('full', 'Full Data Replace'),
        ('update', 'Update Existing Data'),
        ('add', 'Add New Data Only')
    ]
    upload_type = forms.ChoiceField(
        choices=UPLOAD_TYPES,
        initial='add',
        help_text='Choose how to handle existing data'
    )

    def clean_file(self):
        file = self.cleaned_data['file']
        try:
            # Validate JSON structure
            data = json.load(file)
            validate_json_structure(data)
            file.seek(0)  # Reset file pointer
            return file
        except json.JSONDecodeError:
            raise forms.ValidationError("Invalid JSON file")
        except ValidationError as e:
            raise forms.ValidationError(str(e))
