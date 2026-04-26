from datetime import date

from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Count, Max, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET

from apps.courses.models import Course, CourseRegistration
from apps.portfolio.models import PortfolioEntry
from apps.vacancies.models import Vacancy, VacancyResponse

from .decorators import role_required
from .forms import (
    AdminCourseForm,
    AdminCuratorCreateForm,
    AdminStudentCreateForm,
    AdminVacancyForm,
    EmailAuthenticationForm,
    StudentProfileForm,
    UserStudentForm,
)
from .models import User


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = EmailAuthenticationForm


class CustomLogoutView(LogoutView):
    pass


def role_redirect(user):
    if user.role == User.Role.STUDENT:
        return reverse('accounts:student_dashboard')
    if user.role == User.Role.CURATOR:
        return reverse('accounts:curator_dashboard')
    return reverse('accounts:admin_dashboard')


@require_GET
def home(request):
    return render(request, 'public/index.html')


def redirect_by_role(request):
    return redirect(role_redirect(request.user))


@role_required(User.Role.STUDENT)
def student_dashboard(request):
    entries_qs = PortfolioEntry.objects.filter(student=request.user)
    recent_entries = entries_qs.order_by('-created_at')[:5]

    registrations = (
        CourseRegistration.objects
        .filter(student=request.user)
        .select_related('course')
        .order_by('-created_at')[:5]
    )

    resume = getattr(request.user, 'resume_settings', None)
    profile = getattr(request.user, 'student_profile', None)
    resume_public_url = ''
    if profile:
        resume_public_url = request.build_absolute_uri(f"/resumes/public/{profile.public_resume_token}/")

    current_course = None
    if request.user.admission_year:
        current_course = max(date.today().year - request.user.admission_year + 1, 1)

    context = {
        'recent_entries': recent_entries,
        'portfolio_total': entries_qs.count(),
        'portfolio_pending': entries_qs.filter(status=PortfolioEntry.Status.PENDING).count(),
        'portfolio_approved': entries_qs.filter(status=PortfolioEntry.Status.APPROVED).count(),
        'resume': resume,
        'resume_is_public': bool(resume and resume.is_public and profile),
        'resume_public_url': resume_public_url,
        'resume_updated_at': resume.updated_at if resume else None,
        'registrations': registrations,
        'current_course': current_course,
    }
    return render(request, 'dashboard/student_dashboard.html', context)


@role_required(User.Role.CURATOR)
def curator_dashboard(request):
    students = User.objects.filter(role=User.Role.STUDENT, curator=request.user)
    student_ids = students.values_list('id', flat=True)

    pending_entries_qs = (
        PortfolioEntry.objects
        .filter(student_id__in=student_ids, status=PortfolioEntry.Status.PENDING)
        .select_related('student')
        .order_by('-created_at')
    )

    students_with_activity = (
        students.annotate(last_activity=Max('portfolio_entries__updated_at'))
        .order_by('-last_activity', 'full_name')[:5]
    )

    context = {
        'students_count': students.count(),
        'pending_count': pending_entries_qs.count(),
        'approved_count': PortfolioEntry.objects.filter(
            student_id__in=student_ids, status=PortfolioEntry.Status.APPROVED
        ).count(),
        'rejected_count': PortfolioEntry.objects.filter(
            student_id__in=student_ids, status=PortfolioEntry.Status.REJECTED
        ).count(),
        'pending_entries': pending_entries_qs[:5],
        'students_with_activity': students_with_activity,
    }
    return render(request, 'curator/dashboard.html', context)


@role_required(User.Role.CURATOR)
def curator_students(request):
    students = (
        User.objects.filter(role=User.Role.STUDENT, curator=request.user)
        .annotate(
            portfolio_total=Count('portfolio_entries'),
            portfolio_pending=Count('portfolio_entries', filter=Q(portfolio_entries__status=PortfolioEntry.Status.PENDING)),
            portfolio_approved=Count('portfolio_entries', filter=Q(portfolio_entries__status=PortfolioEntry.Status.APPROVED)),
            last_activity=Max('portfolio_entries__updated_at'),
        )
        .order_by('full_name')
    )
    return render(request, 'curator/students.html', {'students': students})


@role_required(User.Role.CURATOR)
def curator_student_detail(request, student_id):
    student = get_object_or_404(User, id=student_id, role=User.Role.STUDENT, curator=request.user)
    entries = PortfolioEntry.objects.filter(student=student).order_by('-created_at')
    resume = getattr(student, 'resume_settings', None)
    profile = getattr(student, 'student_profile', None)
    resume_public_url = ''
    if resume and resume.is_public and profile:
        resume_public_url = request.build_absolute_uri(f"/resumes/public/{profile.public_resume_token}/")

    context = {
        'student': student,
        'profile': profile,
        'entries': entries,
        'portfolio_total': entries.count(),
        'portfolio_pending': entries.filter(status=PortfolioEntry.Status.PENDING).count(),
        'portfolio_approved': entries.filter(status=PortfolioEntry.Status.APPROVED).count(),
        'portfolio_rejected': entries.filter(status=PortfolioEntry.Status.REJECTED).count(),
        'resume_public_url': resume_public_url,
    }
    return render(request, 'curator/student_detail.html', context)


@role_required(User.Role.ADMIN)
def admin_dashboard(request):
    students_total = User.objects.filter(role=User.Role.STUDENT).count()
    curators_total = User.objects.filter(role=User.Role.CURATOR).count()

    vacancies = Vacancy.objects.values('status').annotate(total=Count('id'))
    vacancy_summary = {item['status']: item['total'] for item in vacancies}

    courses = Course.objects.values('status').annotate(total=Count('id'))
    course_summary = {item['status']: item['total'] for item in courses}

    context = {
        'students_total': students_total,
        'curators_total': curators_total,
        'vacancies_active': vacancy_summary.get(Vacancy.Status.ACTIVE, 0),
        'courses_active': course_summary.get(Course.Status.ACTIVE, 0),
        'registrations_total': CourseRegistration.objects.count(),
        'responses_total': VacancyResponse.objects.count(),
        'vacancy_summary': {
            'active': vacancy_summary.get(Vacancy.Status.ACTIVE, 0),
            'hidden': vacancy_summary.get(Vacancy.Status.HIDDEN, 0),
            'archive': vacancy_summary.get(Vacancy.Status.ARCHIVE, 0),
        },
        'course_summary': {
            'active': course_summary.get(Course.Status.ACTIVE, 0),
            'hidden': course_summary.get(Course.Status.HIDDEN, 0),
            'archive': course_summary.get(Course.Status.ARCHIVE, 0),
        },
        'latest_vacancies': Vacancy.objects.order_by('-created_at')[:5],
        'latest_courses': Course.objects.order_by('-created_at')[:5],
        'latest_students': User.objects.filter(role=User.Role.STUDENT).order_by('-date_joined')[:5],
    }
    return render(request, 'adminpanel/dashboard.html', context)


@role_required(User.Role.ADMIN)
def admin_students(request):
    form = AdminStudentCreateForm()
    if request.method == 'POST':
        form = AdminStudentCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Студент создан.')
            return redirect('accounts:admin_students')

    students = (
        User.objects.filter(role=User.Role.STUDENT)
        .select_related('curator')
        .annotate(portfolio_total=Count('portfolio_entries'))
        .order_by('full_name')
    )

    q = request.GET.get('q', '').strip()
    group = request.GET.get('group', '').strip()
    curator = request.GET.get('curator', '').strip()
    specialty = request.GET.get('specialty', '').strip()

    if q:
        students = students.filter(Q(full_name__icontains=q) | Q(email__icontains=q))
    if group:
        students = students.filter(group__icontains=group)
    if curator:
        students = students.filter(curator_id=curator)
    if specialty:
        students = students.filter(specialty__icontains=specialty)

    filter_curators = User.objects.filter(role=User.Role.CURATOR).order_by('full_name')

    return render(
        request,
        'adminpanel/students.html',
        {'students': students, 'form': form, 'filter_curators': filter_curators},
    )


@role_required(User.Role.ADMIN)
def admin_student_detail(request, student_id):
    student = get_object_or_404(User, id=student_id, role=User.Role.STUDENT)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'toggle_active':
            student.is_active = not student.is_active
            student.save(update_fields=['is_active'])
            messages.success(request, 'Статус студента обновлён.')
            return redirect('accounts:admin_student_detail', student_id=student.id)
        if action == 'reset_password':
            new_password = request.POST.get('temp_password', '').strip()
            if new_password:
                student.set_password(new_password)
                student.save(update_fields=['password'])
                messages.success(request, 'Пароль студента сброшен.')
            else:
                messages.error(request, 'Введите временный пароль.')
            return redirect('accounts:admin_student_detail', student_id=student.id)

    return render(request, 'adminpanel/student_detail.html', {'student': student})


@role_required(User.Role.ADMIN)
def admin_curators(request):
    form = AdminCuratorCreateForm()
    if request.method == 'POST':
        form = AdminCuratorCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Куратор создан.')
            return redirect('accounts:admin_curators')

    curators = User.objects.filter(role=User.Role.CURATOR).annotate(students_count=Count('students')).order_by('full_name')
    q = request.GET.get('q', '').strip()
    if q:
        curators = curators.filter(Q(full_name__icontains=q) | Q(email__icontains=q))

    return render(request, 'adminpanel/curators.html', {'curators': curators, 'form': form})


@role_required(User.Role.ADMIN)
def admin_curator_detail(request, curator_id):
    curator = get_object_or_404(User, id=curator_id, role=User.Role.CURATOR)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'toggle_active':
            curator.is_active = not curator.is_active
            curator.save(update_fields=['is_active'])
            messages.success(request, 'Статус куратора обновлён.')
            return redirect('accounts:admin_curator_detail', curator_id=curator.id)
        if action == 'reset_password':
            new_password = request.POST.get('temp_password', '').strip()
            if new_password:
                curator.set_password(new_password)
                curator.save(update_fields=['password'])
                messages.success(request, 'Пароль куратора сброшен.')
            else:
                messages.error(request, 'Введите временный пароль.')
            return redirect('accounts:admin_curator_detail', curator_id=curator.id)

    students_count = User.objects.filter(role=User.Role.STUDENT, curator=curator).count()
    return render(request, 'adminpanel/curator_detail.html', {'curator': curator, 'students_count': students_count})


@role_required(User.Role.ADMIN)
def admin_vacancies(request):
    status_filter = request.GET.get('status', 'all')
    q = request.GET.get('q', '').strip()
    format_filter = request.GET.get('format_type', '').strip()
    employment_filter = request.GET.get('employment_type', '').strip()
    direction_filter = request.GET.get('direction', '').strip()

    form = AdminVacancyForm()
    if request.method == 'POST':
        form = AdminVacancyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Вакансия создана.')
            return redirect('accounts:admin_vacancies')

    vacancies = Vacancy.objects.order_by('-created_at')
    if q:
        vacancies = vacancies.filter(Q(title__icontains=q) | Q(company__icontains=q))
    if status_filter in {Vacancy.Status.ACTIVE, Vacancy.Status.HIDDEN, Vacancy.Status.ARCHIVE}:
        vacancies = vacancies.filter(status=status_filter)
    else:
        status_filter = 'all'
    if format_filter:
        vacancies = vacancies.filter(format_type__icontains=format_filter)
    if employment_filter:
        vacancies = vacancies.filter(employment_type__icontains=employment_filter)
    if direction_filter:
        vacancies = vacancies.filter(direction__icontains=direction_filter)

    return render(
        request,
        'adminpanel/vacancies.html',
        {'vacancies': vacancies, 'form': form, 'status_filter': status_filter},
    )


@role_required(User.Role.ADMIN)
def admin_vacancy_detail(request, vacancy_id):
    vacancy = get_object_or_404(Vacancy, id=vacancy_id)
    form = AdminVacancyForm(instance=vacancy)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update':
            form = AdminVacancyForm(request.POST, instance=vacancy)
            if form.is_valid():
                form.save()
                messages.success(request, 'Вакансия обновлена.')
                return redirect('accounts:admin_vacancy_detail', vacancy_id=vacancy.id)
        elif action == 'set_status':
            new_status = request.POST.get('status')
            if new_status in {Vacancy.Status.ACTIVE, Vacancy.Status.HIDDEN, Vacancy.Status.ARCHIVE}:
                vacancy.status = new_status
                vacancy.save(update_fields=['status', 'updated_at'])
                messages.success(request, 'Статус вакансии обновлён.')
                return redirect('accounts:admin_vacancy_detail', vacancy_id=vacancy.id)
        elif action == 'delete':
            vacancy.delete()
            messages.success(request, 'Вакансия удалена.')
            return redirect('accounts:admin_vacancies')

    return render(request, 'adminpanel/vacancy_detail.html', {'vacancy': vacancy, 'form': form})


@role_required(User.Role.ADMIN)
def admin_courses(request):
    status_filter = request.GET.get('status', 'all')
    q = request.GET.get('q', '').strip()
    kind_filter = request.GET.get('kind', '').strip()
    format_filter = request.GET.get('format_type', '').strip()

    form = AdminCourseForm()
    if request.method == 'POST':
        form = AdminCourseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Курс создан.')
            return redirect('accounts:admin_courses')

    courses = Course.objects.annotate(registrations_count=Count('registrations')).order_by('-created_at')
    if q:
        courses = courses.filter(Q(title__icontains=q) | Q(organization__icontains=q))
    if status_filter in {Course.Status.ACTIVE, Course.Status.HIDDEN, Course.Status.ARCHIVE}:
        courses = courses.filter(status=status_filter)
    else:
        status_filter = 'all'
    if kind_filter in {Course.Kind.COURSE, Course.Kind.SEMINAR, Course.Kind.PRACTICE}:
        courses = courses.filter(kind=kind_filter)
    if format_filter in {Course.Format.ONLINE, Course.Format.OFFLINE}:
        courses = courses.filter(format_type=format_filter)

    return render(
        request,
        'adminpanel/courses.html',
        {'courses': courses, 'form': form, 'status_filter': status_filter},
    )


@role_required(User.Role.ADMIN)
def admin_course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    form = AdminCourseForm(instance=course)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update':
            form = AdminCourseForm(request.POST, instance=course)
            if form.is_valid():
                form.save()
                messages.success(request, 'Курс обновлён.')
                return redirect('accounts:admin_course_detail', course_id=course.id)
        elif action == 'set_status':
            new_status = request.POST.get('status')
            if new_status in {Course.Status.ACTIVE, Course.Status.HIDDEN, Course.Status.ARCHIVE}:
                course.status = new_status
                course.save(update_fields=['status', 'updated_at'])
                messages.success(request, 'Статус курса обновлён.')
                return redirect('accounts:admin_course_detail', course_id=course.id)
        elif action == 'delete':
            course.delete()
            messages.success(request, 'Курс удалён.')
            return redirect('accounts:admin_courses')

    registrations_count = CourseRegistration.objects.filter(course=course).count()
    return render(
        request,
        'adminpanel/course_detail.html',
        {'course': course, 'form': form, 'registrations_count': registrations_count},
    )


@role_required(User.Role.ADMIN)
def admin_responses(request):
    responses = VacancyResponse.objects.select_related('student', 'vacancy').order_by('-created_at')
    return render(request, 'adminpanel/responses.html', {'responses': responses})


@role_required(User.Role.ADMIN)
def admin_course_registrations(request):
    registrations = CourseRegistration.objects.select_related('student', 'course').order_by('-created_at')
    return render(request, 'adminpanel/course_registrations.html', {'registrations': registrations})


@role_required(User.Role.STUDENT)
def profile_edit(request):
    profile = getattr(request.user, 'student_profile', None)
    if profile is None:
        from .models import StudentProfile
        profile = StudentProfile.objects.create(user=request.user)

    if request.method == 'POST':
        user_form = UserStudentForm(request.POST, instance=request.user)
        profile_form = StudentProfileForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('accounts:student_dashboard')
    else:
        user_form = UserStudentForm(instance=request.user)
        profile_form = StudentProfileForm(instance=profile)

    return render(request, 'accounts/profile_edit.html', {'user_form': user_form, 'profile_form': profile_form})
