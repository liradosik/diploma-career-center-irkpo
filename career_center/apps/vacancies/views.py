from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.decorators import role_required
from apps.accounts.models import ActivityLog, User

from .models import StudentFavoriteVacancy, Vacancy, VacancyResponse


def _redirect_back(request, fallback_name, **kwargs):
    next_url = request.POST.get('next')
    if next_url:
        return redirect(next_url)
    return redirect(fallback_name, **kwargs)


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
    favorite_vacancy_ids = set(
        StudentFavoriteVacancy.objects.filter(student=request.user).values_list('vacancy_id', flat=True)
    )

    vacancies = vacancies.order_by('-created_at')

    paginator = Paginator(vacancies, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    query_params = request.GET.copy()
    query_params.pop('page', None)
    querystring = query_params.urlencode()

    return render(request, 'vacancies/list.html', {
        'vacancies': page_obj.object_list,
        'page_obj': page_obj,
        'querystring': querystring,
        'page_start': page_obj.start_index() if page_obj.paginator.count else 0,
        'page_end': page_obj.end_index() if page_obj.paginator.count else 0,

        'q': q,
        'format_filter': format_filter,
        'employment_filter': employment_filter,
        'direction_filter': direction_filter,
        'format_options': active_vacancies.values_list('format_type', flat=True).distinct().order_by('format_type'),
        'employment_options': active_vacancies.values_list('employment_type', flat=True).distinct().order_by('employment_type'),
        'direction_options': active_vacancies.values_list('direction', flat=True).distinct().order_by('direction'),

        'responded_vacancy_ids': responded_vacancy_ids,
        'favorite_vacancy_ids': favorite_vacancy_ids,
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
        'is_favorite': StudentFavoriteVacancy.objects.filter(student=request.user, vacancy=vacancy).exists(),
    })


@role_required(User.Role.STUDENT)
def respond(request, pk):
    if request.method != 'POST':
        return redirect('vacancies:detail', pk=pk)

    vacancy = get_object_or_404(Vacancy, pk=pk, status=Vacancy.Status.ACTIVE)
    profile = getattr(request.user, 'student_profile', None)
    resume = getattr(request.user, 'resume_settings', None)
    resume_link = request.build_absolute_uri(f"/resumes/public/{profile.public_resume_token}/") if profile and resume and resume.is_public else ''

    response, created = VacancyResponse.objects.get_or_create(
        student=request.user,
        vacancy=vacancy,
        defaults={'resume_link_snapshot': resume_link},
    )

    if created:
        ActivityLog.objects.create(
            student=request.user,
            event_type=ActivityLog.EventType.VACANCY_APPLIED,
            title=f'Откликнулся на вакансию: {vacancy.title}',
            description=vacancy.company,
            related_model='vacancies.Vacancy',
            related_object_id=vacancy.id,
        )
        messages.success(request, 'Отклик сохранён.')

    else:
        messages.info(request, 'Вы уже откликнулись на эту вакансию.')

    next_url = request.POST.get('next')
    if next_url:
        return redirect(next_url)

    if created:
        return redirect(f"{redirect('vacancies:detail', pk=pk).url}?responded=1")

    return redirect('vacancies:detail', pk=pk)


@role_required(User.Role.STUDENT)
def toggle_favorite(request, pk):
    vacancy = get_object_or_404(Vacancy, pk=pk, status=Vacancy.Status.ACTIVE)
    if request.method == 'POST':
        favorite, created = StudentFavoriteVacancy.objects.get_or_create(student=request.user, vacancy=vacancy)
        if not created:
            favorite.delete()
    return _redirect_back(request, 'vacancies:detail', pk=pk)
