from django.shortcuts import get_object_or_404, render

from apps.accounts.decorators import role_required
from apps.accounts.models import StudentProfile, User
from apps.portfolio.models import PortfolioEntry

from .forms import ResumeSettingsForm
from .models import ResumeSettings


def _group_entries(entries):
    grouped = {
        'skills': [e for e in entries if e.type == 'skill'],
        'projects': [e for e in entries if e.type == 'project'],
        'achievements': [e for e in entries if e.type in {'academic', 'creative', 'sport', 'social'}],
        'recommendations': [e for e in entries if e.type == 'recommendation'],
    }
    return grouped


@role_required(User.Role.STUDENT)
def builder(request):
    settings_obj, _ = ResumeSettings.objects.get_or_create(student=request.user)
    profile = getattr(request.user, 'student_profile', None)
    if request.method == 'POST':
        form = ResumeSettingsForm(request.POST, instance=settings_obj)
        if form.is_valid():
            form.save()
    else:
        form = ResumeSettingsForm(instance=settings_obj)
    entries = list(PortfolioEntry.objects.filter(student=request.user, status=PortfolioEntry.Status.APPROVED))
    about_text = (settings_obj.about or (profile.about if profile else '')).strip()
    has_base_data = any(
        [
            request.user.full_name,
            settings_obj.title,
            about_text,
            request.user.specialty,
            request.user.group,
        ]
    )
    return render(
        request,
        'resumes/builder.html',
        {
            'form': form,
            'entries': entries,
            'resume': settings_obj,
            'profile': profile,
            'grouped_entries': _group_entries(entries),
            'has_resume_data': has_base_data or bool(entries),
            'about_text': about_text,
        },
    )


def public_resume(request, token):
    profile = get_object_or_404(StudentProfile, public_resume_token=token)
    resume = getattr(profile.user, 'resume_settings', None)
    entries = list(PortfolioEntry.objects.filter(student=profile.user, status=PortfolioEntry.Status.APPROVED))
    about_text = ((getattr(resume, 'about', '') or '') or profile.about or '').strip()
    has_resume_data = any([profile.user.full_name, getattr(resume, 'title', ''), about_text, entries])
    return render(
        request,
        'resumes/public.html',
        {
            'student': profile.user,
            'profile': profile,
            'resume': resume,
            'entries': entries,
            'grouped_entries': _group_entries(entries),
            'about_text': about_text,
            'has_resume_data': has_resume_data,
        },
    )
