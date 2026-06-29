from django import forms

from users.mixins import GitHubURLMixin

from .models import Project


class ProjectForm(forms.ModelForm, GitHubURLMixin):
    class Meta:
        model = Project
        fields = (
            "name",
            "description",
            "github_url",
            "status",
        )
