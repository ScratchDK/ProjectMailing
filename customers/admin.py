from django.contrib import admin
from .models import Mailing, Letter, Attempt, Recipient


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ('first_mailing', 'end_mailing', 'status', 'letter')
    list_filter = ('status',)
    search_fields = ('letter', 'recipients',)


@admin.register(Letter)
class LetterAdmin(admin.ModelAdmin):
    list_display = ('topic', 'content')
    search_fields = ('topic', 'content',)


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'comment')
    search_fields = ('full_name', 'email',)


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ('attempt_time', 'status', 'server_response', 'mailing')
