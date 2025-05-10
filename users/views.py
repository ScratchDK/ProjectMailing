from django.contrib import messages
from django.contrib.auth import login, get_user_model
from django.contrib.auth.views import LoginView, LogoutView
from django.core.mail import send_mail
from django.shortcuts import redirect, render, reverse, get_object_or_404
from django.urls import reverse_lazy
from django.utils.crypto import get_random_string
from django.views.generic import CreateView, UpdateView, ListView

import config.settings as settings

from .forms import CustomUserCreationForm, ProfileUpdateForm
from .models import CustomUser


def welcome(request):
    return render(request, 'users/welcome.html')


def confirm_email(request, token):
    User = get_user_model()
    user = get_object_or_404(User, confirmation_token=token)

    # Активируем пользователя
    user.is_active = True
    user.confirmation_token = None  # Удаляем токен, так как он больше не нужен
    user.save()

    # Авторизуем пользователя
    login(request, user)

    messages.success(request, 'Ваш email успешно подтвержден!')
    return redirect('customers:mailing_list')


class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    success_url = reverse_lazy('customers:mailing_list')


class CustomLogoutView(LogoutView):
    next_page = 'users:welcome'


class RegisterView(CreateView):
    template_name = 'users/register.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('customers:mailing_list')

    def form_valid(self, form):
        # Создаем пользователя, но не сохраняем в базу
        user = form.save(commit=False)
        user.is_active = False  # Делаем пользователя неактивным до подтверждения

        # Генерируем токен подтверждения
        confirmation_token = get_random_string(32)
        user.confirmation_token = confirmation_token  # Добавьте это поле в вашу модель пользователя

        # Сохраняем пользователя с токеном (но is_active=False)
        user.save()

        # Отправляем письмо с подтверждением
        self.send_confirmation_email(user)

        # Сообщаем пользователю о необходимости подтверждения
        messages.info(self.request, 'Пожалуйста, проверьте вашу почту для завершения регистрации.')
        return redirect('customers:mailing_list')  # Перенаправляем на домашнюю страницу

    def send_confirmation_email(self, user):
        confirmation_link = self.request.build_absolute_uri(
            reverse('users:confirm-email', kwargs={'token': user.confirmation_token})
        )

        subject = 'Подтвердите вашу регистрацию'
        message = f'Для завершения регистрации перейдите по ссылке: {confirmation_link}'
        recipient_list = [user.email]
        from_email = settings.EMAIL_HOST_USER

        send_mail(subject, message, from_email, recipient_list)


class ProfileUpdateView(UpdateView):
    model = CustomUser
    pk_url_kwarg = 'id'
    form_class = ProfileUpdateForm
    template_name = "users/update_profile.html"
    success_url = reverse_lazy('catalog:home')


class UserListView(ListView):
    model = CustomUser
    template_name = 'users/users_list.html'
    context_object_name = 'users'

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        user_id = request.POST.get('user_id')

        if action == "deactivate":
            user = CustomUser.objects.get(pk=user_id)
            user.is_active = False
            user.save()

        elif action == "activate":
            user = CustomUser.objects.get(pk=user_id)
            user.is_active = True
            user.save()

        return redirect("users:users_list")