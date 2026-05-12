from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from apps.accounts.decorators import role_required
from apps.accounts.models import StudentProfile, User
from apps.portfolio.models import PortfolioEntry

from .forms import ResumeSettingsForm
from .models import ResumeSettings

ALLOWED_RESUME_TEMPLATES = {'classic', 'compact', 'modern', 'academic'}
ALLOWED_RESUME_FONT_SIZES = {'small', 'standard', 'large'}


def _normalize_font_size(font_size):
    if font_size in ALLOWED_RESUME_FONT_SIZES:
        return font_size
    return 'standard'

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
    raw_selected_sections = getattr(resume, 'selected_sections', None)
    selected_sections = section_defaults if raw_selected_sections is None else raw_selected_sections
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
            settings_obj = form.save(commit=False)

            checked_sections = request.POST.getlist('selected_sections')
            raw_order = request.POST.get('section_order', '')
            section_order = [item for item in raw_order.split(',') if item]

            if section_order:
                ordered_selected_sections = [key for key in section_order if key in checked_sections]
                settings_obj.selected_sections = ordered_selected_sections
            else:
                settings_obj.selected_sections = checked_sections

            settings_obj.save()
    else:
        form = ResumeSettingsForm(instance=settings_obj)

    entries, grouped_entries, about_text, selected_sections = _resume_payload(request.user, settings_obj, profile)

    resume_template = _normalize_template(getattr(settings_obj, 'template', 'classic'))
    resume_font_size = _normalize_font_size(getattr(settings_obj, 'font_size', 'standard'))

    section_choices = ResumeSettingsForm.SECTION_CHOICES
    saved_order = list(getattr(settings_obj, 'selected_sections', None) or [])

    ordered_section_choices = []
    used_keys = set()

    for key in saved_order:
        for choice_key, choice_label in section_choices:
            if choice_key == key and choice_key not in used_keys:
                ordered_section_choices.append((choice_key, choice_label))
                used_keys.add(choice_key)

    for choice_key, choice_label in section_choices:
        if choice_key not in used_keys:
            ordered_section_choices.append((choice_key, choice_label))

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
            'ordered_section_choices': ordered_section_choices,
            'has_resume_data': has_base_data or bool(entries),
            'about_text': about_text,
            'resume_template': resume_template,
            'resume_font_size': resume_font_size,
        },
    )


def public_resume(request, token):
    profile = get_object_or_404(StudentProfile, public_resume_token=token)
    resume = getattr(profile.user, 'resume_settings', None)
    if not resume:
        return render(
            request,
            'resumes/public.html',
            {
                'is_unavailable': True,
                'unavailable_reason': 'not_created',
                'student': profile.user,
            },
            status=404,
        )
    if not resume.is_public:
        return render(
            request,
            'resumes/public.html',
            {
                'is_unavailable': True,
                'unavailable_reason': 'private',
                'student': profile.user,
            },
            status=404,
        )
    entries, grouped_entries, about_text, selected_sections = _resume_payload(profile.user, resume, profile)
    resume_template = _normalize_template(getattr(resume, 'template', 'classic'))
    resume_font_size = _normalize_font_size(getattr(resume, 'font_size', 'standard'))
    has_resume_data = any([profile.user.full_name, getattr(resume, 'title', ''), about_text, entries])
    is_owner_view = request.user.is_authenticated and request.user.id == profile.user_id
    if request.GET.get('download') == 'pdf':
        html = render(request, 'resumes/public.html', {
            'student': profile.user, 'profile': profile, 'resume': resume, 'entries': entries,
            'grouped_entries': grouped_entries, 'about_text': about_text, 'has_resume_data': has_resume_data,
            'selected_sections': selected_sections, 'is_owner_view': is_owner_view, 'is_pdf_mode': True,
            'resume_template': resume_template,
            'resume_font_size': resume_font_size,
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
            'resume_font_size': resume_font_size,
        },
    )
