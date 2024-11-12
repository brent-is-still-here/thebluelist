# online_security/management/commands/populate_security_data.py
from django.core.management.base import BaseCommand
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from django.urls import path
from django.conf import settings
from django.db import transaction
from online_security.models import Category, Recommendation, Solution
import json
import logging
import os

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Populates the security database with predefined data from local JSON file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before importing',
        )

    def handle(self, *args, **options):
        data_file_path = os.path.join(settings.BASE_DIR, 'data', 'security_data.json')
        
        try:
            # Read data from local file
            with open(data_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            with transaction.atomic():
                # Clear existing data if requested
                if options['clear']:
                    self.stdout.write('Clearing existing data...')
                    Category.objects.all().delete()
                    self.stdout.write('Existing data cleared.')

                # Process categories and their nested data
                for category_data in data['categories']:
                    try:
                        category = self.create_category(category_data)
                        self.process_recommendations(category, category_data.get('recommendations', []))
                    except Exception as e:
                        logger.error(f"Error processing category {category_data.get('name', 'Unknown')}: {str(e)}")
                        raise

            self.stdout.write(
                self.style.SUCCESS('Successfully populated security data from local file')
            )
            
        except FileNotFoundError:
            error_msg = f'Data file not found at {data_file_path}'
            logger.error(error_msg)
            self.stderr.write(self.style.ERROR(error_msg))
        except json.JSONDecodeError as e:
            error_msg = f'Failed to parse JSON data: {str(e)}'
            logger.error(error_msg)
            self.stderr.write(self.style.ERROR(error_msg))
        except Exception as e:
            error_msg = f'An error occurred: {str(e)}'
            logger.error(error_msg)
            self.stderr.write(self.style.ERROR(error_msg))

    def create_category(self, category_data):
        """Create or update a category"""
        category, created = Category.objects.update_or_create(
            name=category_data['name'],
            defaults={
                'description': category_data['description'],
                'importance': category_data['importance'],
                'order': category_data.get('order', 0)
            }
        )
        action = 'Created' if created else 'Updated'
        self.stdout.write(f'{action} category: {category.name}')
        return category

    def create_recommendation(self, recommendation_data, category):
        """Create or update a recommendation"""
        recommendation, created = Recommendation.objects.update_or_create(
            name=recommendation_data['name'],
            defaults={
                'description': recommendation_data['description'],
                'importance': recommendation_data['importance'],
                'order': recommendation_data.get('order', 0)
            }
        )
        recommendation.categories.add(category)
        action = 'Created' if created else 'Updated'
        self.stdout.write(f'{action} recommendation: {recommendation.name}')
        return recommendation

    def create_solution(self, solution_data, recommendation):
        """Create or update a solution"""
        solution, created = Solution.objects.update_or_create(
            name=solution_data['name'],
            defaults={
                'description': solution_data['description'],
                'type': solution_data['type'],
                'cost': solution_data.get('cost'),
                'cost_duration': solution_data.get('cost_duration'),
                'implementation_difficulty': solution_data.get('implementation_difficulty'),
                'learning_curve': solution_data.get('learning_curve'),
                'implementation_time': solution_data.get('implementation_time'),
                'supported_platforms': solution_data.get('supported_platforms', []),
                'download_link': solution_data.get('download_link'),
                'order': solution_data.get('order', 0)
            }
        )
        solution.recommendations.add(recommendation)
        action = 'Created' if created else 'Updated'
        self.stdout.write(f'{action} solution: {solution.name}')
        return solution

    def process_recommendations(self, category, recommendations_data):
        """Process all recommendations for a category"""
        for recommendation_data in recommendations_data:
            try:
                recommendation = self.create_recommendation(recommendation_data, category)
                self.process_solutions(recommendation, recommendation_data.get('solutions', []))
            except Exception as e:
                logger.error(f"Error processing recommendation {recommendation_data.get('name', 'Unknown')}: {str(e)}")
                raise

    def process_solutions(self, recommendation, solutions_data):
        """Process all solutions for a recommendation"""
        for solution_data in solutions_data:
            try:
                self.create_solution(solution_data, recommendation)
            except Exception as e:
                logger.error(f"Error processing solution {solution_data.get('name', 'Unknown')}: {str(e)}")
                raise


# Admin integration
class SecurityDataAdmin:
    @method_decorator(staff_member_required)
    def populate_security_data_view(self, request):
        from django.core.management import call_command
        try:
            # Get clear parameter from request
            clear_existing = request.GET.get('clear', '').lower() == 'true'
            
            # Call command with appropriate options
            call_command('populate_security_data', clear=clear_existing)
            return HttpResponse('Security data populated successfully!')
        except Exception as e:
            return HttpResponse(f'Error populating security data: {str(e)}', status=500)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'populate-security-data/',
                self.admin_site.admin_view(self.populate_security_data_view),
                name='populate_security_data',
            ),
        ]
        return custom_urls + urls