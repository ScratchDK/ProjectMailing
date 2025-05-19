from django import forms
from .models import Mailing, Recipient, Letter


class MailingForm(forms.ModelForm):
    class Meta:
        model = Mailing
        fields = ['first_mailing', 'end_mailing', 'status', 'letter', 'recipients']
        widgets = {
            'first_mailing': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_mailing': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'recipients': forms.CheckboxSelectMultiple(),
        }
        labels = {
            'first_mailing': 'Дата и время начала рассылки',
            'end_mailing': 'Дата и время окончания рассылки',
            'status': 'Статус',
            'letter': 'Письмо',
            'recipients': 'Получатели',
        }


class RecipientForm(forms.ModelForm):
    class Meta:
        model = Recipient
        fields = ['email', 'full_name', 'comment']
        labels = {
            'email': 'Адрес электронной почты',
            'full_name': 'Ф.И.О.',
            'comment': 'Комментарий',
        }


class LetterForm(forms.ModelForm):
    class Meta:
        model = Letter
        fields = ['topic', 'content']
        labels = {
            'topic': 'Тема письма',
            'content': 'Содержание письма',
        }
