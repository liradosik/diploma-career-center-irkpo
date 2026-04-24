from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.decorators import role_required
from apps.accounts.models import User

from .forms import PortfolioEntryForm
from .models import PortfolioEntry


@role_required(User.Role.STUDENT)
def list_entries(request):
    entries = PortfolioEntry.objects.filter(student=request.user).order_by('-date')
    return render(request, 'portfolio/list.html', {'entries': entries})


@role_required(User.Role.STUDENT)
def create_entry(request):
    if request.method == 'POST':
        form = PortfolioEntryForm(request.POST, request.FILES)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.student = request.user
            entry.save()
            return redirect('portfolio:list')
    else:
        form = PortfolioEntryForm()
    return render(request, 'portfolio/form.html', {'form': form})


@role_required(User.Role.STUDENT)
def edit_entry(request, pk):
    entry = get_object_or_404(PortfolioEntry, pk=pk, student=request.user)
    if request.method == 'POST':
        form = PortfolioEntryForm(request.POST, request.FILES, instance=entry)
        if form.is_valid():
            form.save()
            return redirect('portfolio:list')
    else:
        form = PortfolioEntryForm(instance=entry)
    return render(request, 'portfolio/form.html', {'form': form, 'entry': entry})


@role_required(User.Role.CURATOR)
def review_queue(request):
    students = User.objects.filter(role=User.Role.STUDENT, curator=request.user)
    entries = PortfolioEntry.objects.filter(student__in=students, status=PortfolioEntry.Status.PENDING)
    return render(request, 'curator/review_queue.html', {'entries': entries})
