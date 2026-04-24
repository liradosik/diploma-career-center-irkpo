from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET

from apps.portfolio.models import PortfolioEntry

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
    entries = PortfolioEntry.objects.filter(student=request.user).order_by('-created_at')[:3]
    return render(request, 'dashboard/student_dashboard.html', {'entries': entries})


@role_required(User.Role.CURATOR)
def curator_dashboard(request):
    students = User.objects.filter(role=User.Role.STUDENT, curator=request.user)
    pending_count = PortfolioEntry.objects.filter(student__in=students, status=PortfolioEntry.Status.PENDING).count()
    return render(request, 'curator/dashboard.html', {'students': students, 'pending_count': pending_count})


@role_required(User.Role.ADMIN)
def admin_dashboard(request):
    return render(request, 'adminpanel/dashboard.html')


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
