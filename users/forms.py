from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser
from django import forms


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = (
            'username', 'email', 'countries', 'phone_number', 'avatar', 'password1', 'password2'
        )

        labels = {
            'username': 'Имя пользователя',
            'email': 'Электронная почта',
            'countries': 'Страна проживания',
            'phone_number': 'Телефонный номер',
            'avatar': 'Фото профиля',
            'password1': 'Пароль',
            'password2': 'Потверждение пароля',
        }


class CustomAuthenticationForm(AuthenticationForm):
    pass


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('countries', 'phone_number', 'avatar')

        labels = {
            'countries': 'Страна проживания',
            'phone_number': 'Телефонный номер',
            'avatar': 'Фото профиля',
        }
