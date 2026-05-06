from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.decorators import role_required
from apps.accounts.models import ActivityLog, User

from .models import Course, CourseRegistration


@role_required(User.Role.STUDENT)
def course_list(request):
    courses = Course.objects.filter(status=Course.Status.ACTIVE).order_by('date')
    registrations = CourseRegistration.objects.filter(student=request.user).select_related('course')
    registration_map = {r.course_id: r for r in registrations}
    return render(request, 'courses/list.html', {'courses': courses, 'registration_map': registration_map})


@role_required(User.Role.STUDENT)
def register_course(request, pk):
    course = get_object_or_404(Course, pk=pk, status=Course.Status.ACTIVE)
    if CourseRegistration.objects.filter(student=request.user, course=course, status=CourseRegistration.Status.REGISTERED).exists():
        messages.info(request, 'Вы уже записаны на это событие.')
        return redirect('courses:list')

    if course.format_type == Course.Format.OFFLINE and not course.has_available_places:
        messages.error(request, 'На очный курс больше нет мест.')
        return redirect('courses:list')

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
    return redirect('courses:list')


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
    return redirect('courses:list')
