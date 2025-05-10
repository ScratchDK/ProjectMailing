import users.views as views
from django.urls import path
from users.apps import UsersConfig
from django.contrib.auth import views as auth_views

app_name = UsersConfig.name

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('update_profile/<int:id>/', views.ProfileUpdateView.as_view(), name='update_profile'),
    path('confirm-email/<str:token>/', views.confirm_email, name='confirm-email'),
    path('welcome/', views.welcome, name='welcome'),
    path('users_list/', views.UserListView.as_view(), name='users_list'),

    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='users/password_reset.html'
    ), name='password_reset'),

    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='users/password_reset_done.html',
    ), name='password_reset_done'),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='users/password_reset_confirm.html',
    ), name='password_reset_confirm'),

    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='users/password_reset_complete.html',
    ), name='password_reset_complete'),
]