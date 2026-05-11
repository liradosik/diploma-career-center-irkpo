from collections import OrderedDict

from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.accounts.decorators import role_required
from apps.accounts.models import ActivityLog, User

from .forms import PortfolioEntryForm
from .models import PortfolioAttachment, PortfolioEntry


SECTION_DEFINITIONS = OrderedDict(
    [
        ('academic', ('Учебные достижения', ['academic'])),
        ('project', ('Проекты и работы', ['project'])),
        ('skill', ('Навыки', ['skill'])),
        ('certificates', ('Сертификаты и курсы', ['academic'])),
        ('social_creative', ('Общественная и творческая деятельность', ['creative', 'social', 'sport'])),
        ('recommendation', ('Отзывы и рекомендации', ['recommendation'])),
    ]
)


@role_required(User.Role.STUDENT)
def list_entries(request):
    base_qs = PortfolioEntry.objects.filter(student=request.user).prefetch_related('attachments')

    search_query = request.GET.get('q', '').strip()
    selected_type = request.GET.get('type', '').strip()
    selected_status = request.GET.get('status', '').strip()
    selected_sort = request.GET.get('sort', 'newest').strip() or 'newest'

    entries = base_qs

    if search_query:
        entries = entries.filter(
            Q(title__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(link__icontains=search_query)
            | Q(file__icontains=search_query)
            | Q(attachments__file__icontains=search_query)
        ).distinct()

    type_values = {code for code, _label in PortfolioEntryForm.TYPE_CHOICES}
    if selected_type in type_values:
        entries = entries.filter(type=selected_type)

    status_values = {code for code, _label in PortfolioEntry.Status.choices}
    if selected_status in status_values:
        entries = entries.filter(status=selected_status)

    if selected_sort == 'oldest':
        entries = entries.order_by('date', 'title')
    elif selected_sort == 'title':
        entries = entries.order_by('title', '-date')
    else:
        selected_sort = 'newest'
        entries = entries.order_by('-date', '-created_at')

    portfolio_total = base_qs.count()
    portfolio_pending = base_qs.filter(status=PortfolioEntry.Status.PENDING).count()
    portfolio_approved = base_qs.filter(status=PortfolioEntry.Status.APPROVED).count()

    return render(request, 'portfolio/list.html', {
        'entries': entries,
        'selected_type': selected_type,
        'selected_status': selected_status,
        'selected_sort': selected_sort,
        'search_query': search_query,
        'type_choices': PortfolioEntryForm.TYPE_CHOICES,
        'status_choices': PortfolioEntry.Status.choices,
        'portfolio_total': portfolio_total,
        'portfolio_pending': portfolio_pending,
        'portfolio_approved': portfolio_approved,
    })


@role_required(User.Role.STUDENT)
def create_entry(request):
    if request.method == 'POST':
        form = PortfolioEntryForm(request.POST, request.FILES)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.student = request.user
            entry.status = PortfolioEntry.Status.PENDING
            entry.save()
            for file_obj in form.cleaned_data['attachments']:
                PortfolioAttachment.objects.create(entry=entry, file=file_obj)
            ActivityLog.objects.create(student=request.user, event_type=ActivityLog.EventType.PORTFOLIO_CREATED, title=f'Добавлена запись портфолио: {entry.title}', description=entry.type, related_model='portfolio.PortfolioEntry', related_object_id=entry.id)
            ActivityLog.objects.create(student=request.user, event_type=ActivityLog.EventType.PORTFOLIO_PENDING, title=f'Ожидает проверки: {entry.title}', description=entry.type, related_model='portfolio.PortfolioEntry', related_object_id=entry.id)
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
            updated = form.save(commit=False)
            if entry.status in {PortfolioEntry.Status.APPROVED, PortfolioEntry.Status.REJECTED}:
                updated.status = PortfolioEntry.Status.PENDING
                updated.reviewed_by = None
                updated.reviewed_at = None
                ActivityLog.objects.create(student=request.user, event_type=ActivityLog.EventType.PORTFOLIO_PENDING, title=f'Повторная проверка: {updated.title}', description=updated.type, related_model='portfolio.PortfolioEntry', related_object_id=updated.id)
            updated.save()

            delete_ids = request.POST.getlist('delete_attachments')
            if delete_ids:
                PortfolioAttachment.objects.filter(entry=entry, id__in=delete_ids).delete()
            for file_obj in form.cleaned_data['attachments']:
                PortfolioAttachment.objects.create(entry=entry, file=file_obj)
            return redirect('portfolio:list')
    else:
        form = PortfolioEntryForm(instance=entry)
    return render(request, 'portfolio/form.html', {'form': form, 'entry': entry, 'existing_attachments': entry.attachments.all()})

# unchanged below
@role_required(User.Role.CURATOR)
def review_queue(request):
    students = User.objects.filter(role=User.Role.STUDENT).filter(Q(study_group__curator=request.user, study_group__is_active=True) | Q(study_group__isnull=True, curator=request.user)).exclude(academic_status=User.AcademicStatus.GRADUATED).distinct()
    entries_qs = PortfolioEntry.objects.filter(student__in=students).select_related('student').prefetch_related('attachments').order_by('-created_at')

    if request.method == 'POST':
        entry = get_object_or_404(entries_qs, id=request.POST.get('entry_id'))
        decision = request.POST.get('decision')
        comment = request.POST.get('curator_comment', '').strip()
        can_review = entry.student.academic_status == User.AcademicStatus.STUDYING
        if entry.status == PortfolioEntry.Status.PENDING and can_review and decision in {PortfolioEntry.Status.APPROVED, PortfolioEntry.Status.REJECTED}:
            entry.status = decision
            entry.curator_comment = comment
            entry.reviewed_by = request.user
            entry.reviewed_at = timezone.now()
            entry.save(update_fields=['status', 'curator_comment', 'reviewed_by', 'reviewed_at', 'updated_at'])
            event_type = ActivityLog.EventType.PORTFOLIO_APPROVED if decision == PortfolioEntry.Status.APPROVED else ActivityLog.EventType.PORTFOLIO_REJECTED
            ActivityLog.objects.create(student=entry.student, event_type=event_type, title=f'{entry.get_status_display()}: {entry.title}', description=entry.type, related_model='portfolio.PortfolioEntry', related_object_id=entry.id)
        return redirect('portfolio:review_queue')

    status_filter = request.GET.get('status', 'all')
    if status_filter in {PortfolioEntry.Status.PENDING, PortfolioEntry.Status.APPROVED, PortfolioEntry.Status.REJECTED}:
        entries_qs = entries_qs.filter(status=status_filter)
    return render(request, 'curator/review_queue.html', {'entries': entries_qs[:50], 'status_filter': status_filter})


@role_required(User.Role.STUDENT)
def delete_entry(request, pk):
    entry = get_object_or_404(PortfolioEntry, pk=pk, student=request.user)
    if request.method == 'POST':
        entry.delete()
    return redirect('portfolio:list')
