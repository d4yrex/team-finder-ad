from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import SetPasswordForm
from django.core.exceptions import ValidationError

from .mixins import GitHubURLMixin
from .models import User


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(),
        min_length=8,
    )

    class Meta:
        model = User
        fields = (
            "name",
            "surname",
            "email",
            "password",
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class UserLoginForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)

    def clean(self):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")
        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise ValidationError("Неверный имейл или пароль")
            if not user.is_active:
                raise ValidationError("Пользователь не активен")
            self.cleaned_data["user"] = user
        return self.cleaned_data


class UserProfileForm(forms.ModelForm, GitHubURLMixin):
    class Meta:
        model = User
        fields = (
            "name",
            "surname",
            "avatar",
            "about",
            "phone",
            "github_url",
        )

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if phone:
            phone = "".join(filter(str.isdigit, phone))
            if phone.startswith("8"):
                phone = "+7" + phone[1:]
            elif not phone.startswith("+7"):
                phone = "+7" + phone[-10:]
        return phone


class ChangePasswordForm(SetPasswordForm):
    old_password = forms.CharField(
        label="Старый пароль",
        widget=forms.PasswordInput,
    )

    def clean_old_password(self):
        if not self.user.check_password(self.cleaned_data.get("old_password")):
            raise ValidationError("Неверный старый пароль")
        return self.cleaned_data["old_password"]
