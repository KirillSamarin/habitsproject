from django.contrib.auth.models import UserManager, AbstractUser
from django.db import models


class CustomUserManager(UserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    email = models.EmailField(unique=True, verbose_name="email")
    phone_number = models.CharField(max_length=20, null=True, blank=True, verbose_name="номер телефона")
    telegram_chat_id = models.CharField(max_length=64, null=True, blank=True, verbose_name="telegram chat id")
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.email}, {self.first_name}, {self.last_name}"

    class Meta:
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"
