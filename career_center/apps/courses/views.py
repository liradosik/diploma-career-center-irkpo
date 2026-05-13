from django.contrib import messages
from django.core.paginator import Paginator
from django.core.exceptions import ValidationError
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.decorators import role_required
from apps.accounts.models import ActivityLog, User

from .models import Course, CourseRegistration, StudentFavoriteCourse


def _redirect_back(request, fallback_name, **kwargs):
    next_url = request.POST.get('next')
    if next_url:
        return redirect(next_url)
    return redirect(fallback_name, **kwargs)


@role_required(User.Role.STUDENT)
def course_list(request):
    courses = Course.objects.filter(status=Course.Status.ACTIVE).annotate(
        occupied_places_count=Count(
            'registrations',
            filter=Q(registrations__status=CourseRegistration.Status.REGISTERED),
        )
    ).order_by('date')

    q = (request.GET.get('q') or '').strip()
    kind_filter = (request.GET.get('kind') or '').strip()
    format_filter = (request.GET.get('format') or '').strip()
    registration_filter = (request.GET.get('reg_status') or '').strip()

    if q:
        courses = courses.filter(
            Q(title__icontains=q)
            | Q(description__icontains=q)
            | Q(organization__icontains=q)
        )

    if kind_filter:
        courses = courses.filter(kind=kind_filter)

    if format_filter:
        courses = courses.filter(format_type=format_filter)

    registrations = CourseRegistration.objects.filter(student=request.user).select_related('course')
    registration_map = {r.course_id: r for r in registrations}

    favorite_course_ids = set(
        StudentFavoriteCourse.objects.filter(student=request.user).values_list('course_id', flat=True)
    )

    filtered_courses = []

    for course in courses:
        reg = registration_map.get(course.id)
        occupied = course.occupied_places_count
        available = course.format_type == Course.Format.ONLINE or occupied < course.places

        if registration_filter == 'registered' and not (
            reg and reg.status == CourseRegistration.Status.REGISTERED
        ):
            continue

        if registration_filter == 'cancelled' and not (
            reg and reg.status == CourseRegistration.Status.CANCELLED
        ):
            continue

        if registration_filter == 'open' and not available:
            continue

        if registration_filter == 'full' and available:
            continue

        course.occupied_places_count = occupied
        course.available_places_count = max(course.places - occupied, 0)
        filtered_courses.append(course)

    paginator = Paginator(filtered_courses, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    query_params = request.GET.copy()
    query_params.pop('page', None)
    querystring = query_params.urlencode()

    return render(request, 'courses/list.html', {
        'courses': page_obj.object_list,
        'page_obj': page_obj,
        'querystring': querystring,
        'page_start': page_obj.start_index() if page_obj.paginator.count else 0,
        'page_end': page_obj.end_index() if page_obj.paginator.count else 0,

        'registration_map': registration_map,
        'kind_filter': kind_filter,
        'format_filter': format_filter,
        'registration_filter': registration_filter,
        'KIND_CHOICES': Course.Kind.choices,
        'FORMAT_CHOICES': Course.Format.choices,
        'favorite_course_ids': favorite_course_ids,
    })


@role_required(User.Role.STUDENT, User.Role.CURATOR, User.Role.ADMIN)
def course_detail(request, pk):
    course = get_object_or_404(Course.objects.filter(status=Course.Status.ACTIVE).annotate(
        occupied_places_count=Count('registrations', filter=Q(registrations__status=CourseRegistration.Status.REGISTERED))
    ), pk=pk)
    course.available_places_count = max(course.places - course.occupied_places_count, 0)
    registration = None
    if request.user.role == User.Role.STUDENT:
        registration = CourseRegistration.objects.filter(student=request.user, course=course).first()
    is_favorite = request.user.role == User.Role.STUDENT and StudentFavoriteCourse.objects.filter(
        student=request.user,
        course=course,
    ).exists()

    registrations_qs = CourseRegistration.objects.filter(course=course).select_related('student', 'student__study_group')
    registered_count = registrations_qs.filter(status=CourseRegistration.Status.REGISTERED).count()
    cancelled_count = registrations_qs.filter(status=CourseRegistration.Status.CANCELLED).count()

    curator_registrations = []
    curator_not_registered_students = []
    if request.user.role == User.Role.CURATOR:
        curator_group_ids = list(request.user.managed_study_groups.values_list('id', flat=True))
        if curator_group_ids:
            curator_registrations = list(registrations_qs.filter(student__study_group_id__in=curator_group_ids))
            registered_student_ids = {
                reg.student_id for reg in curator_registrations if reg.status == CourseRegistration.Status.REGISTERED
            }
            curator_not_registered_students = list(
                User.objects.filter(
                    role=User.Role.STUDENT,
                    study_group_id__in=curator_group_ids,
                    is_active=True,
                )
                .exclude(id__in=registered_student_ids)
                .select_related('study_group', 'study_group__specialty_ref')
                .order_by('full_name')
            )

    return render(request, 'courses/detail.html', {
        'course': course,
        'registration': registration,
        'course_registrations': list(registrations_qs) if request.user.role == User.Role.ADMIN else [],
        'curator_course_registrations': curator_registrations,
        'curator_not_registered_students': curator_not_registered_students,
        'active_registrations_count': registered_count,
        'cancelled_registrations_count': cancelled_count,
        'free_places_count': max(course.places - registered_count, 0),
        'is_favorite': is_favorite,
    })


@role_required(User.Role.STUDENT)
def register_course(request, pk):
    if request.method != 'POST':
        return redirect('courses:detail', pk=pk)
    course = get_object_or_404(Course, pk=pk, status=Course.Status.ACTIVE)
    if CourseRegistration.objects.filter(student=request.user, course=course, status=CourseRegistration.Status.REGISTERED).exists():
        messages.info(request, 'Вы уже записаны на это событие.')
        return _redirect_back(request, 'courses:detail', pk=pk)

    if course.format_type == Course.Format.OFFLINE and not course.has_available_places:
        messages.error(request, 'На очный курс больше нет мест.')
        return _redirect_back(request, 'courses:detail', pk=pk)

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
    return _redirect_back(request, 'courses:detail', pk=pk)


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
    return _redirect_back(request, 'courses:detail', pk=registration.course_id)


@role_required(User.Role.STUDENT)
def toggle_favorite_course(request, pk):
    course = get_object_or_404(Course, pk=pk, status=Course.Status.ACTIVE)
    if request.method == 'POST':
        favorite, created = StudentFavoriteCourse.objects.get_or_create(student=request.user, course=course)
        if not created:
            favorite.delete()
    return _redirect_back(request, 'courses:detail', pk=pk)
