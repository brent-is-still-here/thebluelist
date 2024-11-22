from django.urls import path
from .views import (
    LandingView,
    BrowseView,
    CountryDetailView,
    EditCountryView,
    AssessmentView,
    AssessmentResultsView
)

app_name = 'relocation_planner'

urlpatterns = [
    path('', LandingView.as_view(), name='landing'),
    path('browse/', BrowseView.as_view(), name='browse'),
    path('assess/', AssessmentView.as_view(), name='assessment'),
    path('assess/results/', AssessmentResultsView.as_view(), name='assessment_results'),
    # Make sure the add path comes before the detail path to avoid slug conflicts
    path('country/add/', EditCountryView.as_view(), name='add_country'),
    path('country/<slug:slug>/edit/', EditCountryView.as_view(), name='edit_country'),
    path('country/<slug:slug>/', CountryDetailView.as_view(), name='country_detail'),
]