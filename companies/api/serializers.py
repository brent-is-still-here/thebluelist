from rest_framework import serializers
from ..models import EditRequest, Business

class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = ['id', 'name', 'slug', 'website', 'description']

class EditRequestSerializer(serializers.ModelSerializer):
    submitted_by = serializers.ReadOnlyField(source='submitted_by.username')
    
    class Meta:
        model = EditRequest
        fields = [
            'id', 'business', 'submitted_by', 'status',
            'name', 'description', 'republican_percentage',
            'democrat_percentage', 'trump_donor',
            'america_pac_donor', 'total_donations',
            'data_source', 'justification', 'supporting_links',
            'created_at', 'reviewed_at', 'reviewed_by',
            'review_notes'
        ]
        read_only_fields = ['status', 'reviewed_at', 'reviewed_by', 'review_notes']