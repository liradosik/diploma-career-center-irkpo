from django.contrib import messages
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
    try:
        _, created = CourseRegistration.objects.get_or_create(student=request.user, course=course)
        if created:
            messages.success(request, 'Вы записаны на событие.')
        else:
            messages.info(request, 'Вы уже записаны на это событие.')
    except Exception as exc:
        messages.error(request, str(exc))
    return redirect('courses:list')
