from django.shortcuts import get_object_or_404, render

from apps.accounts.decorators import role_required
from apps.accounts.models import StudentProfile, User
from apps.portfolio.models import PortfolioEntry

from .forms import ResumeSettingsForm
from .models import ResumeSettings


@role_required(User.Role.STUDENT)
def builder(request):
    settings_obj, _ = ResumeSettings.objects.get_or_create(student=request.user)
    if request.method == 'POST':
        form = ResumeSettingsForm(request.POST, instance=settings_obj)
        if form.is_valid():
            form.save()
    else:
        form = ResumeSettingsForm(instance=settings_obj)
    entries = PortfolioEntry.objects.filter(student=request.user, status=PortfolioEntry.Status.APPROVED)
    return render(request, 'resumes/builder.html', {'form': form, 'entries': entries, 'resume': settings_obj})


def public_resume(request, token):
    profile = get_object_or_404(StudentProfile, public_resume_token=token)
    resume = getattr(profile.user, 'resume_settings', None)
    entries = PortfolioEntry.objects.filter(student=profile.user, status=PortfolioEntry.Status.APPROVED)
    return render(request, 'resumes/public.html', {'student': profile.user, 'profile': profile, 'resume': resume, 'entries': entries})
