from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from reports.models import DisasterReport, ResponderAssignment, DisasterCategory
from accounts.models import CustomUser
from notifications.models import Notification


def _feed_context():
    return {
        'feed_reports': DisasterReport.objects.select_related('category', 'location').order_by('-reported_at')[:10],
    }


@login_required
def home(request):
    user = request.user
    if user.role == 'admin':
        return admin_dashboard(request)
    elif user.role == 'responder':
        return responder_dashboard(request)
    else:
        return reporter_dashboard(request)


@login_required
def reporter_dashboard(request):
    user = request.user
    my_reports = DisasterReport.objects.filter(reporter=user)
    context = {
        'total_reports': my_reports.count(),
        'pending': my_reports.filter(status='pending').count(),
        'active': my_reports.filter(status='active').count(),
        'resolved': my_reports.filter(status='resolved').count(),
        'recent_reports': my_reports[:5],
        'unread_notifications': user.notifications.filter(is_read=False).count(),
    }
    context.update(_feed_context())
    return render(request, 'dashboard/reporter_dashboard.html', context)


@login_required
def admin_dashboard(request):
    all_reports = DisasterReport.objects.all()
    context = {
        'total_reports': all_reports.count(),
        'pending': all_reports.filter(status='pending').count(),
        'active': all_reports.filter(status='active').count(),
        'resolved': all_reports.filter(status='resolved').count(),
        'critical': all_reports.filter(severity='critical').count(),
        'total_users': CustomUser.objects.count(),
        'total_responders': CustomUser.objects.filter(role='responder').count(),
        'recent_reports': all_reports[:8],
        'unread_notifications': request.user.notifications.filter(is_read=False).count(),
        # Chart data
        'category_labels': list(DisasterCategory.objects.values_list('name', flat=True)),
        'category_counts': [
            DisasterReport.objects.filter(category__name=c).count()
            for c in DisasterCategory.objects.values_list('name', flat=True)
        ],
    }
    context.update(_feed_context())
    return render(request, 'dashboard/admin_dashboard.html', context)


@login_required
def responder_dashboard(request):
    user = request.user
    my_assignments = ResponderAssignment.objects.filter(responder=user)
    context = {
        'total_assigned': my_assignments.count(),
        'pending': my_assignments.filter(status='assigned').count(),
        'active': my_assignments.filter(status__in=['on_route', 'on_scene']).count(),
        'resolved': my_assignments.filter(status='resolved').count(),
        'recent_assignments': my_assignments[:6],
        'unread_notifications': user.notifications.filter(is_read=False).count(),
    }
    context.update(_feed_context())
    return render(request, 'dashboard/responder_dashboard.html', context)
