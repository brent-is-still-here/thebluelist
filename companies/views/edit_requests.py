from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from companies.models import (
    EditRequest
)

@login_required
def edit_requests(request):
    user_requests = EditRequest.objects.filter(submitted_by=request.user)
    return render(request, 'companies/edit_requests.html', {
        'edit_requests': user_requests
    })

