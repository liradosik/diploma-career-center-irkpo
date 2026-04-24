from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.decorators import role_required
from apps.accounts.models import User

from .models import Vacancy, VacancyResponse


@role_required(User.Role.STUDENT)
def vacancy_list(request):
    vacancies = Vacancy.objects.filter(status=Vacancy.Status.ACTIVE)
    q = request.GET.get('q')
    if q:
        vacancies = vacancies.filter(title__icontains=q)
    return render(request, 'vacancies/list.html', {'vacancies': vacancies})


@role_required(User.Role.STUDENT)
def vacancy_detail(request, pk):
    vacancy = get_object_or_404(Vacancy, pk=pk, status=Vacancy.Status.ACTIVE)
    return render(request, 'vacancies/detail.html', {'vacancy': vacancy})


@role_required(User.Role.STUDENT)
def respond(request, pk):
    vacancy = get_object_or_404(Vacancy, pk=pk, status=Vacancy.Status.ACTIVE)
    profile = getattr(request.user, 'student_profile', None)
    resume_link = request.build_absolute_uri(f"/resumes/public/{profile.public_resume_token}/") if profile else ''
    VacancyResponse.objects.get_or_create(student=request.user, vacancy=vacancy, defaults={'resume_link_snapshot': resume_link})
    messages.success(request, 'Отклик сохранен. Используйте контакты работодателя для связи.')
    return redirect('vacancies:detail', pk=pk)
