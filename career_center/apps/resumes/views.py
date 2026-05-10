from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from apps.accounts.decorators import role_required
from apps.accounts.models import StudentProfile, User
from apps.portfolio.models import PortfolioEntry

from .forms import ResumeSettingsForm
from .models import ResumeSettings

ALLOWED_RESUME_TEMPLATES = {'classic', 'compact', 'modern', 'academic'}


def _normalize_template(template_code):
    if template_code in ALLOWED_RESUME_TEMPLATES:
        return template_code
    return 'classic'


def _resume_payload(student, resume, profile):
    entries = list(
        PortfolioEntry.objects.filter(student=student, status=PortfolioEntry.Status.APPROVED)
        .prefetch_related('attachments')
        .order_by('-date', '-created_at')
    )
    about_text = ((getattr(resume, 'about', '') or '') or getattr(profile, 'about', '') or '').strip()
    section_defaults = ['contacts', 'education', 'skills', 'projects', 'achievements', 'certificates', 'recommendations']
    selected_sections = (getattr(resume, 'selected_sections', None) or section_defaults)
    grouped = {
        'skills': [e for e in entries if e.type == 'skill'],
        'projects': [e for e in entries if e.type == 'project'],
        'achievements': [e for e in entries if e.type == 'academic'],
        'certificates': [e for e in entries if e.type in {'creative', 'sport', 'social'}],
        'recommendations': [e for e in entries if e.type == 'recommendation'],
    }
    return entries, grouped, about_text, selected_sections


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
    entries, grouped_entries, about_text, selected_sections = _resume_payload(request.user, settings_obj, profile)
    resume_template = _normalize_template(getattr(settings_obj, 'template', 'classic'))
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
            'grouped_entries': grouped_entries,
            'selected_sections': selected_sections,
            'has_resume_data': has_base_data or bool(entries),
            'about_text': about_text,
            'resume_template': resume_template,
        },
    )


def public_resume(request, token):
    profile = get_object_or_404(StudentProfile, public_resume_token=token)
    resume = getattr(profile.user, 'resume_settings', None)
    if not resume or not resume.is_public:
        return render(request, 'resumes/public.html', {'is_unavailable': True, 'student': profile.user}, status=404)
    entries, grouped_entries, about_text, selected_sections = _resume_payload(profile.user, resume, profile)
    resume_template = _normalize_template(getattr(resume, 'template', 'classic'))
    has_resume_data = any([profile.user.full_name, getattr(resume, 'title', ''), about_text, entries])
    is_owner_view = request.user.is_authenticated and request.user.id == profile.user_id
    if request.GET.get('download') == 'pdf':
        html = render(request, 'resumes/public.html', {
            'student': profile.user, 'profile': profile, 'resume': resume, 'entries': entries,
            'grouped_entries': grouped_entries, 'about_text': about_text, 'has_resume_data': has_resume_data,
            'selected_sections': selected_sections, 'is_owner_view': is_owner_view, 'is_pdf_mode': True,
            'resume_template': resume_template,
        }).content
        response = HttpResponse(html, content_type='text/html; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename=\"resume-{profile.user_id}.html\"'
        return response
    return render(
        request,
        'resumes/public.html',
        {
            'student': profile.user,
            'profile': profile,
            'resume': resume,
            'entries': entries,
            'grouped_entries': grouped_entries,
            'about_text': about_text,
            'has_resume_data': has_resume_data,
            'selected_sections': selected_sections,
            'is_owner_view': is_owner_view,
            'resume_template': resume_template,
        },
    )
