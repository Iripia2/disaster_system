from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from .models import DisasterReport, MediaAttachment, ResponderAssignment, Comment, Location
from .forms import (DisasterReportForm, LocationForm, MediaAttachmentForm,
                    CommentForm, AssignResponderForm, UpdateStatusForm, AnonymousReportForm)
from notifications.models import Notification
from accounts.models import CustomUser


def anonymous_submit_report(request):
    if request.method == 'POST':
        form = AnonymousReportForm(request.POST, request.FILES)
        if form.is_valid():
            location = Location.objects.create(
                address=form.cleaned_data['address'],
                city=form.cleaned_data['city'],
                lga=form.cleaned_data['lga'],
                landmark=''
            )
            report = DisasterReport.objects.create(
                reporter=None,
                category=form.cleaned_data['category'],
                location=location,
                title=form.cleaned_data['title'],
                description=form.cleaned_data['description'],
                severity=form.cleaned_data['severity'],
                status='pending',
                affected_count=form.cleaned_data.get('affected_count') or 0,
                incident_date=form.cleaned_data['incident_date'],
                is_anonymous=True,
            )
            if request.FILES.get('file'):
                MediaAttachment.objects.create(report=report, file=request.FILES['file'], file_type='image')
            admins = CustomUser.objects.filter(role='admin')
            for admin in admins:
                Notification.objects.create(
                    user=admin,
                    report=report,
                    message=f'Anonymous disaster report submitted: "{report.title}"',
                    notif_type='new_report'
                )
            request.session['anonymous_report_id'] = report.id
            return redirect('reports:anonymous_success')
    else:
        form = AnonymousReportForm()

    return render(request, 'reports/anonymous_submit.html', {'form': form})


def anonymous_success(request):
    report_id = request.session.get('anonymous_report_id')
    report = DisasterReport.objects.filter(pk=report_id).first()
    return render(request, 'reports/anonymous_success.html', {'report': report})


@login_required
def submit_report(request):
    if request.method == 'POST':
        report_form = DisasterReportForm(request.POST)
        location_form = LocationForm(request.POST)
        media_form = MediaAttachmentForm(request.POST, request.FILES)

        if report_form.is_valid() and location_form.is_valid():
            # Save location first
            location = location_form.save()
            # Save report
            report = report_form.save(commit=False)
            report.reporter = request.user
            report.location = location
            report.save()
            # Save media if provided
            if request.FILES.get('file'):
                media = media_form.save(commit=False)
                media.report = report
                media.save()
            # Notify all admins
            admins = CustomUser.objects.filter(role='admin')
            for admin in admins:
                Notification.objects.create(
                    user=admin,
                    report=report,
                    message=f'New disaster report submitted: "{report.title}" by {request.user.get_full_name()}',
                    notif_type='new_report'
                )
            messages.success(request, f'Report submitted successfully! Report ID: #{report.id}')
            return redirect('reports:detail', pk=report.id)
        else:
            messages.error(request, 'Please fill in all required fields correctly.')
    else:
        report_form = DisasterReportForm()
        location_form = LocationForm()
        media_form = MediaAttachmentForm()

    return render(request, 'reports/submit_report.html', {
        'report_form': report_form,
        'location_form': location_form,
        'media_form': media_form,
    })


@login_required
def report_list(request):
    user = request.user
    if user.role == 'admin':
        reports = DisasterReport.objects.all()
    elif user.role == 'responder':
        assigned_report_ids = ResponderAssignment.objects.filter(
            responder=user
        ).values_list('report_id', flat=True)
        reports = DisasterReport.objects.filter(id__in=assigned_report_ids)
    else:
        reports = DisasterReport.objects.filter(reporter=user)

    # Filters
    status_filter = request.GET.get('status')
    severity_filter = request.GET.get('severity')
    if status_filter:
        reports = reports.filter(status=status_filter)
    if severity_filter:
        reports = reports.filter(severity=severity_filter)

    return render(request, 'reports/report_list.html', {
        'reports': reports,
        'status_filter': status_filter,
        'severity_filter': severity_filter,
    })


@login_required
def report_detail(request, pk):
    report = get_object_or_404(DisasterReport, pk=pk)
    comments = report.comments.all()
    assignments = report.assignments.all()
    comment_form = CommentForm()
    assign_form = AssignResponderForm()
    update_status_form = UpdateStatusForm()

    if request.method == 'POST':
        if 'add_comment' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.report = report
                comment.user = request.user
                comment.is_official = request.user.role in ['admin', 'responder']
                comment.save()
                messages.success(request, 'Comment added.')
                return redirect('reports:detail', pk=pk)

        elif 'assign_responder' in request.POST and request.user.role == 'admin':
            assign_form = AssignResponderForm(request.POST)
            if assign_form.is_valid():
                assignment = assign_form.save(commit=False)
                assignment.report = report
                assignment.assigned_by = request.user
                assignment.save()
                report.status = 'active'
                report.save()
                # Notify responder
                Notification.objects.create(
                    user=assignment.responder,
                    report=report,
                    message=f'You have been assigned to handle: "{report.title}"',
                    notif_type='assignment'
                )
                messages.success(request, f'Responder assigned successfully.')
                return redirect('reports:detail', pk=pk)

        elif 'update_status' in request.POST and request.user.role in ['admin', 'responder']:
            assignment = assignments.filter(responder=request.user).first()
            if assignment:
                update_status_form = UpdateStatusForm(request.POST, instance=assignment)
                if update_status_form.is_valid():
                    updated = update_status_form.save(commit=False)
                    if updated.status == 'resolved':
                        updated.resolved_at = timezone.now()
                        report.status = 'resolved'
                        report.save()
                        # Notify reporter
                        Notification.objects.create(
                            user=report.reporter,
                            report=report,
                            message=f'Your report "{report.title}" has been resolved.',
                            notif_type='resolved'
                        )
                    updated.save()
                    messages.success(request, 'Status updated successfully.')
                    return redirect('reports:detail', pk=pk)

    return render(request, 'reports/report_detail.html', {
        'report': report,
        'comments': comments,
        'assignments': assignments,
        'comment_form': comment_form,
        'assign_form': assign_form,
        'update_status_form': update_status_form,
    })


def public_feed_data(request):
    reports = DisasterReport.objects.select_related('category', 'location').order_by('-reported_at')
    status_filter = request.GET.get('status')
    if status_filter:
        reports = reports.filter(status=status_filter)
    search = request.GET.get('search', '').strip()
    if search:
        reports = reports.filter(title__icontains=search) | reports.filter(description__icontains=search) | reports.filter(location__lga__icontains=search) | reports.filter(location__city__icontains=search) | reports.filter(category__name__icontains=search)
    items = []
    for report in reports:
        items.append({
            'id': report.id,
            'title': report.title,
            'category_name': report.category.name if report.category else 'Uncategorized',
            'category_icon': report.category.icon if report.category else 'bi-exclamation-triangle',
            'location': f"{report.location.lga}, {report.location.city}" if report.location else 'Unknown',
            'severity': report.severity,
            'severity_display': report.get_severity_display(),
            'status': report.status,
            'status_display': report.get_status_display(),
            'affected_count': report.affected_count,
            'reported_at': report.reported_at.isoformat(),
            'reporter_name': report.get_reporter_name(),
            'is_anonymous': report.is_anonymous,
            'is_recent': (timezone.now() - report.reported_at).total_seconds() < 3600,
            'detail_url': f"/reports/{report.id}/",
        })
    return JsonResponse({'reports': items})


@login_required
def delete_report(request, pk):
    report = get_object_or_404(DisasterReport, pk=pk)
    if request.user == report.reporter or request.user.role == 'admin':
        report.delete()
        messages.success(request, 'Report deleted successfully.')
    return redirect('reports:list')
