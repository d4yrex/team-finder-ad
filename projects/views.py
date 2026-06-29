from http import HTTPStatus

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from common.utils import paginate

from .constants import PAGINATE_BY
from .forms import ProjectForm
from .models import Project


def project_list(request):
    projects = (
        Project.objects.filter(status=Project.Status.OPEN)
        .select_related("owner")
        .prefetch_related("participants")
        .order_by("-created_at")
    )

    page_obj = paginate(projects, request, PAGINATE_BY)

    return render(request, "projects/project_list.html", {"projects": page_obj})


def project_detail(request, pk):
    project = get_object_or_404(
        Project.objects.select_related("owner").prefetch_related("participants"), pk=pk
    )
    return render(request, "projects/project-details.html", {"project": project})


@login_required
def create_project(request):
    form = ProjectForm(request.POST or None)
    if form.is_valid():
        project = form.save(commit=False)
        project.owner = request.user
        project.save()
        project.participants.add(request.user)
        messages.success(request, "Проект создан")
        return redirect("projects:detail", pk=project.id)

    return render(
        request,
        "projects/create-project.html",
        {
            "form": form,
            "is_edit": False,
        },
    )


@login_required
def edit_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.owner != request.user:
        messages.error(request, "Нет прав")
        return redirect("projects:detail", pk=pk)

    form = ProjectForm(request.POST or None, instance=project)
    if form.is_valid():
        form.save()
        messages.success(request, "Проект обновлен")
        return redirect("projects:detail", pk=pk)

    return render(
        request,
        "projects/create-project.html",
        {
            "form": form,
            "is_edit": True,
            "project": project,
        },
    )


@login_required
@require_POST
def toggle_participate(request, pk):
    project = get_object_or_404(Project, pk=pk)
    is_participant = project.toggle_participant(request.user)
    return JsonResponse({"status": "ok", "is_participant": is_participant})


@login_required
@require_POST
def toggle_favorite(request, pk):
    project = get_object_or_404(Project, pk=pk)
    is_favorited = project.toggle_favorite(request.user)
    return JsonResponse({"status": "ok", "favorited": is_favorited})


@login_required
@require_POST
def complete_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.owner != request.user:
        return JsonResponse(
            {"status": "error", "message": "Нет прав"}, status=HTTPStatus.FORBIDDEN
        )

    if project.status == Project.Status.OPEN:
        project.status = Project.Status.CLOSED
        project.save()
        return JsonResponse({"status": "ok", "project_status": "closed"})

    return JsonResponse(
        {"status": "error", "message": "Уже завершен"}, status=HTTPStatus.BAD_REQUEST
    )


@login_required
def favorites_list(request):
    projects = request.user.favorites.all().order_by("-created_at")
    page_obj = paginate(projects, request, PAGINATE_BY)
    return render(request, "projects/favorite_projects.html", {"projects": page_obj})
