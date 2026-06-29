from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Project
from .forms import ProjectForm


def project_list(request):
    projects = Project.objects.filter(status=Project.Status.OPEN).order_by('-created_at')
    paginator = Paginator(projects, 12)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'projects/project_list.html', {'projects': page_obj})

def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    return render(request, 'projects/project-details.html', {'project': project})

@login_required
def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            project.participants.add(request.user)
            messages.success(request, 'Проект создан')
            return redirect('projects:detail', pk=project.id)
    else:
        form = ProjectForm()
    return render(request, 'projects/create-project.html', {'form': form, 'is_edit': False})

@login_required
def edit_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.owner != request.user:
        messages.error(request, 'Нет прав')
        return redirect('projects:detail', pk=pk)
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Проект обновлен')
            return redirect('projects:detail', pk=pk)
    else:
        form = ProjectForm(instance=project)
    return render(request, 'projects/create-project.html', {'form': form, 'is_edit': True, 'project': project})

@login_required
@require_POST
def toggle_participate(request, pk):
    project = get_object_or_404(Project, pk=pk)
    is_participant = project.toggle_participant(request.user)
    return JsonResponse({'status': 'ok', 'is_participant': is_participant})

@login_required
@require_POST
def toggle_favorite(request, pk):
    project = get_object_or_404(Project, pk=pk)
    is_favorited = project.toggle_favorite(request.user)
    return JsonResponse({'status': 'ok', 'favorited': is_favorited})

@login_required
@require_POST
def complete_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.owner != request.user:
        return JsonResponse({'status': 'error', 'message': 'Нет прав'}, status=403)
    
    if project.status == Project.Status.OPEN:
        project.status = Project.Status.CLOSED
        project.save()
        return JsonResponse({'status': 'ok', 'project_status': 'closed'})
    return JsonResponse({'status': 'error', 'message': 'Уже завершен'}, status=400)

@login_required
def favorites_list(request):
    projects = request.user.favorites.all().order_by('-created_at')
    paginator = Paginator(projects, 12)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'projects/favorite_projects.html', {'projects': page_obj})
