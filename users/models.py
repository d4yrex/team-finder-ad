from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import RegexValidator, URLValidator, validate_email
from django.db import models

from .constants import (
    MAX_ABOUT_LENGTH,
    MAX_NAME_LENGTH,
    MAX_PHONE_LENGTH,
    MAX_SURNAME_LENGTH,
)
from .managers import UserManager
from .utils import generate_avatar


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        unique=True,
        validators=[validate_email],
        error_messages={
            "unique": "Пользователь с таким email уже существует",
        },
        verbose_name="Email",
    )
    name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        verbose_name="Имя",
    )
    surname = models.CharField(
        max_length=MAX_SURNAME_LENGTH,
        verbose_name="Фамилия",
    )
    avatar = models.ImageField(
        upload_to="avatars/",
        default="avatars/default.png",
        verbose_name="Аватарка пользователя",
    )
    phone = models.CharField(
        max_length=MAX_PHONE_LENGTH,
        unique=True,
        blank=True,
        null=True,
        validators=[
            RegexValidator(r"^(\+7|8)\d{10}$", "Формат: 8XXXXXXXXXX или +7XXXXXXXXXX")
        ],
        verbose_name="Номер телефона",
    )
    github_url = models.URLField(
        blank=True,
        null=True,
        validators=[
            URLValidator(),
            RegexValidator(
                r"^https?://(www\.)?github\.com/.*$",
                message="Ссылка должна вести на GitHub",
            ),
        ],
        verbose_name="Ссылка на GitHub",
    )
    about = models.TextField(
        max_length=MAX_ABOUT_LENGTH,
        blank=True,
        verbose_name="О себе",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активен",
    )
    is_staff = models.BooleanField(
        default=False,
        verbose_name="Администратор",
    )
    favorites = models.ManyToManyField(
        "projects.Project",
        related_name="interested_users",
        blank=True,
        verbose_name="Избранные проекты",
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["-id"]

    def __str__(self):
        return f"{self.name} {self.surname}"

    def save(self, *args, **kwargs):
        if not self.pk and not self.avatar:
            avatar_content = generate_avatar(self.name[0].upper())
            self.avatar.save(avatar_content.name, avatar_content, save=False)

        if self.phone and self.phone.startswith("8"):
            self.phone = "+7" + self.phone[1:]

        super().save(*args, **kwargs)
