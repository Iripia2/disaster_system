from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Notification


@login_required
def notification_list(request):
    notifications = request.user.notifications.all()
    # Mark all as read
    notifications.update(is_read=True)
    return render(request, 'notifications/notification_list.html', {
        'notifications': notifications,
    })


@login_required
def mark_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk, user=request.user)
    notif.is_read = True
    notif.save()
    if notif.report:
        return redirect('reports:detail', pk=notif.report.id)
    return redirect('notifications:list')
