from django import forms

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
