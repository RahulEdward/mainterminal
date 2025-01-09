from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    def create_user(self, username, client_id, api_key, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')
        if not client_id:
            raise ValueError('The Client ID field must be set')
        if not api_key:
            raise ValueError('The API Key field must be set')
        
        user = self.model(
            username=username,
            client_id=client_id,
            api_key=api_key,
            **extra_fields
        )
        # Set a default password since it's required by AbstractBaseUser
        user.set_password('defaultpass123')  # This provides a default password
        user.save(using=self._db)
        return user

    def create_superuser(self, username, client_id, api_key, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        return self.create_user(username, client_id, api_key, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name=_("Username")
    )
    client_id = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_("Client ID")
    )
    api_key = models.CharField(
        max_length=100,
        verbose_name=_("API Key")
    )
    access_token = models.CharField(
        max_length=1000,
        null=True,
        blank=True,
        verbose_name=_("Access Token")
    )
    email = models.EmailField(_("email address"), blank=True)
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_("Designates whether this user should be treated as active."),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['client_id', 'api_key']

    class Meta:
        db_table = 'users'
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return f"{self.username} ({self.client_id})"

    def clean(self):
        super().clean()