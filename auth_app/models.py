"""Database models for the custom email-based user used by KanMind."""

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class UserManager(BaseUserManager):
    """Manager for the custom ``User`` model that authenticates by email."""

    def create_user(self, email, fullname, password=None, **extra_fields):
        """Create and persist a regular user identified by email and fullname."""
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, fullname=fullname, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, fullname, password=None, **extra_fields):
        """Create a user with staff and superuser flags enabled."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, fullname, password, **extra_fields)


class User(AbstractUser):
    """Custom user model that uses email as the unique login identifier."""

    username = None
    email = models.EmailField(unique=True)
    fullname = models.CharField(max_length=255)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['fullname']

    objects = UserManager()

    def __str__(self):
        """Return the user's fullname for human-readable representations."""
        return self.fullname

