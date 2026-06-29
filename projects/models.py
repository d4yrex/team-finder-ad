from django.db import models
from django.conf import settings
from django.core.validators import URLValidator, RegexValidator


class Project(models.Model):
    class Status(models.TextChoices):
        OPEN = 'open', 'Открыт'
        CLOSED = 'closed', 'Закрыт'

    name = models.CharField(max_length=200,
                            verbose_name='Название проекта',)
    description = models.TextField(blank=True,
                                   verbose_name='Описание',)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_projects',
        verbose_name='Автор',
    )
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name='Дата создания',)
    github_url = models.URLField(
        blank=True,
        null=True,
        validators=[
            URLValidator(),
            RegexValidator(
                r'^https?://(www\.)?github\.com/.*$',
                message='Ссылка должна вести на GitHub',
            )
        ],
        verbose_name='Ссылка на GitHub',
    )
    status = models.CharField(max_length=6,
                              choices=Status.choices,
                              default=Status.OPEN,
                              verbose_name='Статус',)
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='participated_projects',
        blank=True,
        verbose_name='Участники',
    )

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def is_participant(self, user):
        return self.participants.filter(id=user.id).exists()

    def toggle_participant(self, user):
        if self.is_participant(user):
            self.participants.remove(user)
            return False
        self.participants.add(user)
        return True

    def toggle_favorite(self, user):
        if self.interested_users.filter(id=user.id).exists():
            self.interested_users.remove(user)
            return False
        self.interested_users.add(user)
        return True
