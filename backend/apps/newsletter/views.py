from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .forms import SubscriberForm

@csrf_exempt  # Optional if using AJAX without CSRF token
@require_POST
def subscribe(request):
    form = SubscriberForm(request.POST)
    if form.is_valid():
        form.save()
        return JsonResponse({'success': True, 'message': 'Subscribed successfully!'})
    return JsonResponse({'success': False, 'errors': form.errors})
