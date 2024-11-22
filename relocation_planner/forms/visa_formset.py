from django.forms import inlineformset_factory
from relocation_planner.models import Country, Visa, VisaRequirement
from .edit_visa import EditVisaForm
from .edit_visa_requirement import EditVisaRequirementForm

VisaRequirementFormSet = inlineformset_factory(
    Visa,
    VisaRequirement,
    form=EditVisaRequirementForm,
    extra=0,
    can_delete=True
)

VisaFormSet = inlineformset_factory(
    Country,
    Visa,
    form=EditVisaForm,
    extra=0,
    can_delete=True
)