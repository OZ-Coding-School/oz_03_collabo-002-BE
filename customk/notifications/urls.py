from django.urls import path
from .views import unread_notifications_count

urlpatterns = [
    path('admin/api/unread_notifications_count/', unread_notifications_count, name='unread-notifications-count'),
]