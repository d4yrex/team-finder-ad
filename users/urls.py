from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("list/", views.users_list, name="list"),
    path("<int:pk>/", views.user_detail, name="detail"),
    path("<int:pk>/edit/", views.edit_profile, name="edit"),
    path("change-password/", views.change_password, name="change_password"),
]
