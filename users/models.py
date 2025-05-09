from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    COUNTRIES_CHOICES = [
        ("Russia", "Россия"),
        ("Belarus", "Беларусь"),
        ("Kazakhstan", "Казахстан"),
    ]

    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    avatar = models.ImageField(upload_to='users/images/', blank=True, null=True)
    countries = models.CharField(max_length=20, choices=COUNTRIES_CHOICES, null=True, blank=True)
    # Токен для потверждения почты при регестрации и для восстановления пароля
    confirmation_token = models.CharField(max_length=32, blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email
