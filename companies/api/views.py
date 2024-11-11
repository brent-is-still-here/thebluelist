from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from ..models import EditRequest, Business
from .serializers import EditRequestSerializer, BusinessSerializer

class EditRequestViewSet(viewsets.ModelViewSet):
    queryset = EditRequest.objects.all()
    serializer_class = EditRequestSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(submitted_by=self.request.user)
    
    def get_queryset(self):
        # Regular users can only see their own edit requests
        # Admins can see all
        if self.request.user.is_staff:
            return EditRequest.objects.all()
        return EditRequest.objects.filter(submitted_by=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def review(self, request, pk=None):
        edit_request = self.get_object()
        status = request.data.get('status')
        notes = request.data.get('review_notes', '')
        
        if status not in ['approved', 'rejected']:
            return Response({'error': 'Invalid status'}, status=400)
            
        edit_request.status = status
        edit_request.reviewed_by = request.user
        edit_request.review_notes = notes
        edit_request.save()
        
        if status == 'approved':
            # Apply the changes to the business
            self._apply_changes(edit_request)
            
        return Response(EditRequestSerializer(edit_request).data)
    
    def _apply_changes(self, edit_request):
        business = edit_request.business
        # Update the business with the approved changes
        for field in ['name', 'description']:
            if getattr(edit_request, field):
                setattr(business, field, getattr(edit_request, field))
                
        # Update political data
        political_data = business.politicaldata
        for field in ['republican_percentage', 'democrat_percentage', 
                     'trump_donor', 'america_pac_donor', 
                     'total_donations', 'data_source']:
            if getattr(edit_request, field) is not None:
                setattr(political_data, field, getattr(edit_request, field))
        
        business.save()
        political_data.save()