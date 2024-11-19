from django.views.generic import ListView, TemplateView
from django.db.models import Avg, Count
from .models import Country, UserExperience, Rating

class LandingView(TemplateView):
    template_name = 'relocation_planner/landing.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get featured countries - for now, selecting countries with the most data
        # We could modify this logic based on your preferences
        featured_countries = Country.objects.annotate(
            rating_count=Count('rating'),
            experience_count=Count('userexperience'),
            data_richness=Count('rating') + Count('userexperience')
        ).order_by('-data_richness')[:6]  # Adjust number as needed
        
        # Get recent experiences
        recent_experiences = UserExperience.objects.select_related(
            'user', 'country'
        ).order_by('-created_at')[:5]
        
        context.update({
            'featured_countries': featured_countries,
            'recent_experiences': recent_experiences,
        })
        return context

class CountryListView(ListView):
    model = Country
    template_name = 'relocation_planner/country_list.html'
    context_object_name = 'countries'
    paginate_by = 12  # Shows 12 countries per page
    
    def get_queryset(self):
        queryset = Country.objects.annotate(
            avg_rating=Avg('rating__score')
        ).select_related(
            'business_language'
        ).prefetch_related(
            'official_languages'
        )
        
        # Handle search
        search_query = self.request.GET.get('search', '').strip()
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)
        
        return queryset.order_by('name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        return context