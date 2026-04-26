from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.decorators import role_required
from apps.accounts.models import User

from .models import Course, CourseRegistration


@role_required(User.Role.STUDENT)
def course_list(request):
    courses = Course.objects.filter(status=Course.Status.ACTIVE).order_by('date')
    return render(request, 'courses/list.html', {'courses': courses})


@role_required(User.Role.STUDENT)
def register_course(request, pk):
    course = get_object_or_404(Course, pk=pk, status=Course.Status.ACTIVE)
    if CourseRegistration.objects.filter(student=request.user, course=course).exists():
        messages.info(request, 'Вы уже записаны на это событие.')
        return redirect('courses:list')

    if course.format_type == Course.Format.OFFLINE and not course.has_available_places:
        messages.error(request, 'На очный курс больше нет мест.')
        return redirect('courses:list')

    registration = CourseRegistration(student=request.user, course=course)
    try:
        registration.save()
    except ValidationError as exc:
        messages.error(request, '; '.join(exc.messages))
    else:
        messages.success(request, 'Вы записаны на событие.')
    return redirect('courses:list')
