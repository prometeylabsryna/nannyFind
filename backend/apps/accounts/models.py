from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


class PlatformUserManager(UserManager):
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("role", User.Role.ADMIN)
        extra_fields.setdefault("status", User.Status.ACTIVE)
        return super().create_superuser(username, email, password, **extra_fields)


class User(AbstractUser):
    class Role(models.TextChoices):
        PARENT = "parent", "Батьки"
        NANNY = "nanny", "Няня"
        ADMIN = "admin", "Адміністратор"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        PENDING = "pending", "Pending"
        BLOCKED = "blocked", "Blocked"

    email = models.EmailField("Email", unique=True)
    phone = models.CharField("Телефон", max_length=32, blank=True)
    role = models.CharField(
        "Роль",
        max_length=16,
        choices=Role.choices,
        default=Role.PARENT,
    )
    status = models.CharField(
        "Статус",
        max_length=16,
        choices=Status.choices,
        default=Status.PENDING,
    )
    oauth_provider = models.CharField("OAuth провайдер", max_length=32, blank=True)
    oauth_uid = models.CharField("OAuth UID", max_length=255, blank=True)

    objects = PlatformUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        verbose_name = "Користувач"
        verbose_name_plural = "Користувачі"
        indexes = [
            models.Index(fields=["role", "status"]),
            models.Index(fields=["oauth_provider", "oauth_uid"]),
        ]

    def __str__(self):
        return self.email

    @property
    def is_parent(self):
        return self.role == self.Role.PARENT

    @property
    def is_nanny(self):
        return self.role == self.Role.NANNY

    @property
    def is_platform_admin(self):
        return self.role == self.Role.ADMIN or self.is_staff
