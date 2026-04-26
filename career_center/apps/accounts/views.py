from datetime import date

from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Count, Max, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET

from apps.courses.models import Course, CourseRegistration
from apps.portfolio.models import PortfolioEntry
from apps.vacancies.models import Vacancy, VacancyResponse

from .decorators import role_required
from .forms import EmailAuthenticationForm, StudentProfileForm, UserStudentForm
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
        'resume_updated_at': getattr(resume, "updated_at", None) if resume else None,
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

    offline_courses = Course.objects.filter(format_type=Course.Format.OFFLINE)
    offline_places_total = sum(course.places for course in offline_courses)

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
        'offline_courses_count': offline_courses.count(),
        'offline_places_total': offline_places_total,
        'latest_vacancies': Vacancy.objects.order_by('-created_at')[:5],
        'latest_courses': Course.objects.order_by('-created_at')[:5],
        'latest_students': User.objects.filter(role=User.Role.STUDENT).order_by('-date_joined')[:5],
    }
    return render(request, 'adminpanel/dashboard.html', context)


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
