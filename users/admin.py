from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'surname', 'phone', 'is_active', 'is_staff')
    search_fields = ('email', 'name', 'surname')
    filter_horizontal = ('favorites',)
