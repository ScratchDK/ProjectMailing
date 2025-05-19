from django.contrib import admin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'phone_number', 'countries', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'countries')
    search_fields = ('email', 'username', 'phone_number')
    ordering = ('email',)
