from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.decorators import role_required
from apps.accounts.models import ActivityLog, User

from .models import Course, CourseRegistration


@role_required(User.Role.STUDENT)
def course_list(request):
    courses = Course.objects.filter(status=Course.Status.ACTIVE).annotate(
        occupied_places_count=Count('registrations', filter=Q(registrations__status=CourseRegistration.Status.REGISTERED))
    ).order_by('date')
    q = (request.GET.get('q') or '').strip()
    kind_filter = (request.GET.get('kind') or '').strip()
    format_filter = (request.GET.get('format') or '').strip()
    registration_filter = (request.GET.get('reg_status') or '').strip()
    if q:
        courses = courses.filter(Q(title__icontains=q) | Q(description__icontains=q) | Q(organization__icontains=q))
    if kind_filter:
        courses = courses.filter(kind=kind_filter)
    if format_filter:
        courses = courses.filter(format_type=format_filter)
    registrations = CourseRegistration.objects.filter(student=request.user).select_related('course')
    registration_map = {r.course_id: r for r in registrations}
    filtered_courses = []
    for course in courses:
        reg = registration_map.get(course.id)
        occupied = course.occupied_places_count
        available = course.format_type == Course.Format.ONLINE or occupied < course.places
        if registration_filter == 'registered' and not (reg and reg.status == CourseRegistration.Status.REGISTERED):
            continue
        if registration_filter == 'cancelled' and not (reg and reg.status == CourseRegistration.Status.CANCELLED):
            continue
        if registration_filter == 'open' and not available:
            continue
        if registration_filter == 'full' and available:
            continue
        course.occupied_places_count = occupied
        course.available_places_count = max(course.places - occupied, 0)
        filtered_courses.append(course)
    return render(request, 'courses/list.html', {
        'courses': filtered_courses,
        'registration_map': registration_map,
        'kind_filter': kind_filter,
        'format_filter': format_filter,
        'registration_filter': registration_filter,
        'KIND_CHOICES': Course.Kind.choices,
        'FORMAT_CHOICES': Course.Format.choices,
    })


@role_required(User.Role.STUDENT)
def course_detail(request, pk):
    course = get_object_or_404(Course.objects.filter(status=Course.Status.ACTIVE).annotate(
        occupied_places_count=Count('registrations', filter=Q(registrations__status=CourseRegistration.Status.REGISTERED))
    ), pk=pk)
    course.available_places_count = max(course.places - course.occupied_places_count, 0)
    registration = CourseRegistration.objects.filter(student=request.user, course=course).first()
    return render(request, 'courses/detail.html', {'course': course, 'registration': registration})


@role_required(User.Role.STUDENT)
def register_course(request, pk):
    course = get_object_or_404(Course, pk=pk, status=Course.Status.ACTIVE)
    if CourseRegistration.objects.filter(student=request.user, course=course, status=CourseRegistration.Status.REGISTERED).exists():
        messages.info(request, 'Вы уже записаны на это событие.')
        return redirect('courses:detail', pk=pk)

    if course.format_type == Course.Format.OFFLINE and not course.has_available_places:
        messages.error(request, 'На очный курс больше нет мест.')
        return redirect('courses:detail', pk=pk)

    registration, _ = CourseRegistration.objects.get_or_create(student=request.user, course=course)
    registration.status = CourseRegistration.Status.REGISTERED
    try:
        registration.save()
    except ValidationError as exc:
        messages.error(request, '; '.join(exc.messages))
    else:
        ActivityLog.objects.create(
            student=request.user,
            event_type=ActivityLog.EventType.COURSE_REGISTERED,
            title=f'Записался на курс: {course.title}',
            description=f'{course.get_kind_display()} • {course.date}',
            related_model='courses.Course',
            related_object_id=course.id,
        )
        messages.success(request, 'Вы записаны на событие.')
    return redirect('courses:detail', pk=pk)


@role_required(User.Role.STUDENT)
def cancel_registration(request, pk):
    registration = get_object_or_404(CourseRegistration, pk=pk, student=request.user)
    if request.method == 'POST' and registration.status == CourseRegistration.Status.REGISTERED:
        registration.status = CourseRegistration.Status.CANCELLED
        registration.save(update_fields=['status'])
        ActivityLog.objects.create(
            student=request.user,
            event_type=ActivityLog.EventType.COURSE_CANCELLED,
            title=f'Отменил запись на курс: {registration.course.title}',
            description=f'{registration.course.get_kind_display()} • {registration.course.date}',
            related_model='courses.Course',
            related_object_id=registration.course_id,
        )
        messages.success(request, 'Запись на событие отменена.')
    return redirect('courses:detail', pk=registration.course_id)
