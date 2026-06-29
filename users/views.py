from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from common.utils import paginate

from .constants import PAGINATE_BY
from .forms import (
    ChangePasswordForm,
    UserLoginForm,
    UserProfileForm,
    UserRegistrationForm,
)
from .models import User


def register(request):
    form = UserRegistrationForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("projects:list")
    return render(request, "users/register.html", {"form": form})


def user_login(request):
    form = UserLoginForm(request.POST or None)
    if form.is_valid():
        login(request, form.cleaned_data["user"])
        return redirect("projects:list")
    return render(request, "users/login.html", {"form": form})


def user_logout(request):
    logout(request)
    return redirect("projects:list")


def user_detail(request, pk):
    user = get_object_or_404(User, pk=pk)
    return render(request, "users/user-details.html", {"user": user})


@login_required
def edit_profile(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.user != user:
        messages.error(request, "У вас нет прав для редактирования этого профиля")
        return redirect("users:detail", pk=pk)

    form = UserProfileForm(request.POST or None, request.FILES or None, instance=user)
    if form.is_valid():
        form.save()
        messages.success(request, "Профиль обновлен")
        return redirect("users:detail", pk=pk)

    return render(request, "users/edit_profile.html", {"form": form})


@login_required
def change_password(request):
    form = ChangePasswordForm(request.user, request.POST or None)
    if form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        messages.success(request, "Пароль изменен")
        return redirect("users:detail", pk=request.user.id)
    return render(request, "users/change_password.html", {"form": form})


def users_list(request):
    users = User.objects.filter(is_active=True).order_by("-id")

    if request.user.is_authenticated:
        filter_type = request.GET.get("filter")
        if filter_type == "favorite_authors":
            users = users.filter(
                owned_projects__in=request.user.favorites.all()
            ).distinct()
        elif filter_type == "participated_authors":
            users = users.filter(
                owned_projects__in=request.user.participated_projects.all()
            ).distinct()
        elif filter_type == "fans":
            users = users.filter(
                favorites__in=request.user.owned_projects.all()
            ).distinct()
        elif filter_type == "participants":
            users = users.filter(
                participated_projects__in=request.user.owned_projects.all()
            ).distinct()

    page_obj = paginate(users, request, PAGINATE_BY)

    return render(
        request,
        "users/participants.html",
        {"participants": page_obj, "active_filter": request.GET.get("filter", "")},
    )
