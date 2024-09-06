from django.http import JsonResponse
from .models import Notification

def unread_notifications_count(request):
    count = Notification.objects.filter(is_read=False).count()
    return JsonResponse({'count': count})