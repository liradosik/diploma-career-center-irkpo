from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.db.models import Q

from apps.accounts.decorators import role_required
from apps.accounts.models import User

from .forms import PortfolioEntryForm
from .models import PortfolioEntry


@role_required(User.Role.STUDENT)
def list_entries(request):
    entries = PortfolioEntry.objects.filter(student=request.user).order_by('-date')
    return render(request, 'portfolio/list.html', {'entries': entries})


@role_required(User.Role.STUDENT)
def create_entry(request):
    if request.method == 'POST':
        form = PortfolioEntryForm(request.POST, request.FILES)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.student = request.user
            entry.status = PortfolioEntry.Status.PENDING
            entry.save()
            return redirect('portfolio:list')
    else:
        form = PortfolioEntryForm()
    return render(request, 'portfolio/form.html', {'form': form})


@role_required(User.Role.STUDENT)
def edit_entry(request, pk):
    entry = get_object_or_404(PortfolioEntry, pk=pk, student=request.user)
    if request.method == 'POST':
        form = PortfolioEntryForm(request.POST, request.FILES, instance=entry)
        if form.is_valid():
            form.save()
            return redirect('portfolio:list')
    else:
        form = PortfolioEntryForm(instance=entry)
    return render(request, 'portfolio/form.html', {'form': form, 'entry': entry})


@role_required(User.Role.CURATOR)
def review_queue(request):
    students = User.objects.filter(role=User.Role.STUDENT).filter(
        Q(study_group__curator=request.user, study_group__is_active=True) |
        Q(study_group__isnull=True, curator=request.user)
    ).exclude(academic_status=User.AcademicStatus.GRADUATED).distinct()
    entries_qs = PortfolioEntry.objects.filter(student__in=students).select_related('student').order_by('-created_at')

    if request.method == 'POST':
        entry_id = request.POST.get('entry_id')
        decision = request.POST.get('decision')
        comment = request.POST.get('curator_comment', '').strip()

        entry = get_object_or_404(entries_qs, id=entry_id)
        can_review = entry.student.academic_status == User.AcademicStatus.STUDYING
        if entry.status == PortfolioEntry.Status.PENDING and can_review and decision in {PortfolioEntry.Status.APPROVED, PortfolioEntry.Status.REJECTED}:
            entry.status = decision
            entry.curator_comment = comment
            entry.reviewed_by = request.user
            entry.reviewed_at = timezone.now()
            entry.save(update_fields=['status', 'curator_comment', 'reviewed_by', 'reviewed_at', 'updated_at'])

        return redirect('portfolio:review_queue')

    status_filter = request.GET.get('status', 'all')
    if status_filter in {PortfolioEntry.Status.PENDING, PortfolioEntry.Status.APPROVED, PortfolioEntry.Status.REJECTED}:
        entries_qs = entries_qs.filter(status=status_filter)
    else:
        status_filter = 'all'

    return render(
        request,
        'curator/review_queue.html',
        {
            'entries': entries_qs[:50],
            'status_filter': status_filter,
        },
    )


@role_required(User.Role.STUDENT)
def delete_entry(request, pk):
    entry = get_object_or_404(PortfolioEntry, pk=pk, student=request.user)
    if request.method == 'POST':
        entry.delete()
    return redirect('portfolio:list')
