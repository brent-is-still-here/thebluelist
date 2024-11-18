from django.shortcuts import render

def safety_at_home_landing(request):
    # Define sections with their content
    upcoming_sections = [
        {
            'title': 'Personal Safety & Security',
            'description': 'Learn to protect yourself and your loved ones with comprehensive security measures and best practices.',
            'status': 'coming_soon'
        },
        {
            'title': 'Health & Hygiene',
            'description': 'Essential guidelines for maintaining health and hygiene during challenging times.',
            'status': 'coming_soon'
        },
        {
            'title': 'Communication',
            'description': 'Strategies and tools for staying connected when traditional methods may be compromised.',
            'status': 'coming_soon'
        },
        {
            'title': 'Home Resilience & Sustainability',
            'description': 'Make your home more self-sufficient and resilient to various challenges.',
            'status': 'coming_soon'
        },
        {
            'title': 'Legal & Financial Preparedness',
            'description': 'Protect your rights and assets with proper legal and financial preparation.',
            'status': 'coming_soon'
        },
        {
            'title': 'Mental & Emotional Resilience',
            'description': 'Resources and strategies for maintaining mental and emotional well-being.',
            'status': 'coming_soon'
        },
        {
            'title': 'Neighborhood & Community',
            'description': 'Build stronger community connections for mutual support and resilience.',
            'status': 'coming_soon'
        }
    ]
    
    emergency_sections = [
        {
            'title': 'Go-Bag',
            'description': 'Essential items for immediate evacuation.',
            'status': 'available',
            'url': '/packplanner/'
        },
        {
            'title': '72-Hour Bag',
            'description': 'Comprehensive preparation for extended emergencies.',
            'status': 'coming_soon'
        },
        {
            'title': 'Home Emergency Preparedness',
            'description': 'Making your home ready for various emergency scenarios.',
            'status': 'coming_soon'
        }
    ]
    
    context = {
        'upcoming_sections': upcoming_sections,
        'emergency_sections': emergency_sections
    }
    
    return render(request, 'safety_at_home/landing.html', context)