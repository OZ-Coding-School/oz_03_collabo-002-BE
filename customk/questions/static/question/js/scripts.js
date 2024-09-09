document.addEventListener('DOMContentLoaded', function() {
    // 질문 알림 관련 요소
    const notificationIcon = document.getElementById('notification-icon');
    const notificationBadge = document.getElementById('notification-badge');

    const paymentIcon = document.getElementById('payment-icon');
    const paymentBadge = document.getElementById('payment-badge');

    fetch('/v1/notifications/unread_question_notifications_count/')
        .then(response => response.json())
        .then(data => {
            if (data.count > 0) {
                notificationBadge.textContent = "";
                notificationBadge.style.display = 'inline';
                notificationIcon.style.color = 'blue';
            } else {
                notificationBadge.style.display = 'none';
                notificationIcon.style.color = '#000';
            }
        })
        .catch(error => console.error('Error fetching question notification count:', error));

    fetch('/v1/notifications/unread_payment_notifications_count/')
        .then(response => response.json())
        .then(data => {
            if (data.count > 0) {
                paymentBadge.textContent = "";
                paymentBadge.style.display = 'inline';
                paymentIcon.style.color = 'green';
            } else {
                paymentBadge.style.display = 'none';
                paymentIcon.style.color = '#000';
            }
        })
        .catch(error => console.error('Error fetching payment notification count:', error));
});