from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.decorators import role_required
from apps.accounts.models import ActivityLog, User

from .models import Vacancy, VacancyResponse


@role_required(User.Role.STUDENT)
def vacancy_list(request):
    vacancies = Vacancy.objects.filter(status=Vacancy.Status.ACTIVE)

    q = (request.GET.get('q') or '').strip()
    format_filter = (request.GET.get('format') or '').strip()
    employment_filter = (request.GET.get('employment') or '').strip()
    direction_filter = (request.GET.get('direction') or '').strip()

    if q:
        vacancies = vacancies.filter(
            Q(title__icontains=q)
            | Q(company__icontains=q)
            | Q(description__icontains=q)
            | Q(direction__icontains=q)
        )

    if format_filter:
        vacancies = vacancies.filter(format_type=format_filter)

    if employment_filter:
        vacancies = vacancies.filter(employment_type=employment_filter)

    if direction_filter:
        vacancies = vacancies.filter(direction=direction_filter)

    active_vacancies = Vacancy.objects.filter(status=Vacancy.Status.ACTIVE)

    responded_vacancy_ids = set(
        VacancyResponse.objects.filter(student=request.user).values_list('vacancy_id', flat=True)
    )

    return render(request, 'vacancies/list.html', {
        'vacancies': vacancies.order_by('-created_at'),
        'q': q,
        'format_filter': format_filter,
        'employment_filter': employment_filter,
        'direction_filter': direction_filter,
        'format_options': active_vacancies.values_list('format_type', flat=True).distinct().order_by('format_type'),
        'employment_options': active_vacancies.values_list('employment_type', flat=True).distinct().order_by('employment_type'),
        'direction_options': active_vacancies.values_list('direction', flat=True).distinct().order_by('direction'),
        'responded_vacancy_ids': responded_vacancy_ids,
    })


@role_required(User.Role.STUDENT)
def vacancy_detail(request, pk):
    vacancy = get_object_or_404(Vacancy, pk=pk, status=Vacancy.Status.ACTIVE)
    response = VacancyResponse.objects.filter(student=request.user, vacancy=vacancy).first()
    profile = getattr(request.user, 'student_profile', None)
    resume = getattr(request.user, 'resume_settings', None)
    resume_public_url = request.build_absolute_uri(f"/resumes/public/{profile.public_resume_token}/") if profile and resume and resume.is_public else ''
    return render(request, 'vacancies/detail.html', {
        'vacancy': vacancy,
        'response': response,
        'resume_public_url': resume_public_url,
        'resume_pdf_url': f'{resume_public_url}?download=pdf' if resume_public_url else '',
        'just_responded': request.GET.get('responded') == '1',
    })


@role_required(User.Role.STUDENT)
def respond(request, pk):
    vacancy = get_object_or_404(Vacancy, pk=pk, status=Vacancy.Status.ACTIVE)
    profile = getattr(request.user, 'student_profile', None)
    resume = getattr(request.user, 'resume_settings', None)
    resume_link = request.build_absolute_uri(f"/resumes/public/{profile.public_resume_token}/") if profile and resume and resume.is_public else ''
    response, created = VacancyResponse.objects.get_or_create(student=request.user, vacancy=vacancy, defaults={'resume_link_snapshot': resume_link})
    if created:
        ActivityLog.objects.create(
            student=request.user,
            event_type=ActivityLog.EventType.VACANCY_APPLIED,
            title=f'Откликнулся на вакансию: {vacancy.title}',
            description=vacancy.company,
            related_model='vacancies.Vacancy',
            related_object_id=vacancy.id,
        )
    if created:
        messages.success(request, 'Отклик сохранён. Свяжитесь с работодателем по контактам ниже.')
        return redirect(f"{redirect('vacancies:detail', pk=pk).url}?responded=1")
    messages.info(request, 'Вы уже откликнулись на эту вакансию.')
    return redirect('vacancies:detail', pk=pk)
