from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("email", "name", "surname", "phone", "is_active", "is_staff")
    search_fields = ("email", "name", "surname")
    filter_horizontal = ("favorites",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            _("Личная информация"),
            {"fields": ("name", "surname", "avatar", "phone", "github_url", "about")},
        ),
        (
            _("Права доступа"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Избранное"), {"fields": ("favorites",)}),
        (_("Даты"), {"fields": ("last_login",)}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "name",
                    "surname",
                    "phone",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
