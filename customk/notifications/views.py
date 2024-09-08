from django.http import JsonResponse

from .models import PaymentNotification, QuestionNotification


def unread_question_notifications_count(request):
    count = QuestionNotification.objects.filter(is_read=False).count()
    return JsonResponse({"count": count})


def unread_payment_notifications_count(request):
    count = PaymentNotification.objects.filter(is_read=False).count()
    return JsonResponse({"count": count})
