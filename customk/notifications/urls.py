from django.urls import path
from .views import unread_notifications_count

urlpatterns = [
    path('unread_count/', unread_notifications_count, name='unread-notifications-count'),
]