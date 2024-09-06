document.addEventListener('DOMContentLoaded', function() {
    const notificationIcon = document.getElementById('notification-icon');
    const notificationBadge = document.getElementById('notification-badge');

    fetch('/v1/notifications/unread_count/')
        .then(response => response.json())
        .then(data => {
            if (data.count > 0) {
                notificationBadge.textContent = '';
                notificationBadge.style.display = 'inline';
                notificationIcon.style.color = 'blue';
            } else {
                notificationBadge.style.display = 'none';
                notificationIcon.style.color = '#000';
            }
        })
        .catch(error => console.error('Error fetching notification count:', error));
});
