from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator

from .models import User
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm, ChangePasswordForm


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('projects:list')
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            login(request, form.cleaned_data['user'])
            return redirect('projects:list')
    else:
        form = UserLoginForm()
    return render(request, 'users/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('projects:list')

def user_detail(request, pk):
    user = get_object_or_404(User, pk=pk)
    return render(request, 'users/user-details.html', {'user': user})

@login_required
def edit_profile(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.user != user:
        messages.error(request, 'У вас нет прав для редактирования этого профиля')
        return redirect('users:detail', pk=pk)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль обновлен')
            return redirect('users:detail', pk=pk)
    else:
        form = UserProfileForm(instance=user)
    return render(request, 'users/edit_profile.html', {'form': form})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Пароль изменен')
            return redirect('users:detail', pk=request.user.id)
    else:
        form = ChangePasswordForm(request.user)
    return render(request, 'users/change_password.html', {'form': form})

def users_list(request):
    users = User.objects.filter(is_active=True).order_by('-id')
    
    if request.user.is_authenticated:
        filter_type = request.GET.get('filter')
        if filter_type == 'favorite_authors':
            users = users.filter(owned_projects__in=request.user.favorites.all()).distinct()
        elif filter_type == 'participated_authors':
            users = users.filter(owned_projects__in=request.user.participated_projects.all()).distinct()
        elif filter_type == 'fans':
            users = users.filter(favorites__in=request.user.owned_projects.all()).distinct()
        elif filter_type == 'participants':
            users = users.filter(participated_projects__in=request.user.owned_projects.all()).distinct()
    
    paginator = Paginator(users, 12)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    return render(request, 'users/participants.html', {
        'participants': page_obj,
        'active_filter': request.GET.get('filter', '')
    })
