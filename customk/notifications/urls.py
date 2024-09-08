from django.urls import path

from . import views

urlpatterns = [
    path(
        "unread_question_notifications_count/",
        views.unread_question_notifications_count,
        name="unread_question_notifications_count",
    ),
    path(
        "unread_payment_notifications_count/",
        views.unread_payment_notifications_count,
        name="unread_payment_notifications_count",
    ),
]
