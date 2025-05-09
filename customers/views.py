import smtplib
from email.mime.text import MIMEText

import config.settings as settings
from django.shortcuts import redirect
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView
from .forms import MailingForm, LetterForm, RecipientForm
from .models import Mailing, Letter, Recipient, Attempt
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
# from django.core.mail import send_mail
# from django.contrib import messages


class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = 'customers/mailing_list.html'
    context_object_name = 'mailing'


class LetterListView(LoginRequiredMixin, ListView):
    model = Letter
    template_name = 'customers/letter_list.html'
    context_object_name = 'letters'


class RecipientListView(LoginRequiredMixin, ListView):
    model = Recipient
    template_name = 'customers/recipient_list.html'
    context_object_name = 'recipients'


class AttemptListView(LoginRequiredMixin, ListView):
    model = Attempt
    template_name = 'customers/attempt_list.html'
    context_object_name = 'attempts'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        attempts = self.get_queryset().filter(mailing__owner=self.request.user)

        context['total_mailings'] = attempts.count()
        context['successful_mailings'] = attempts.filter(status='Successful').count()
        context['failed_mailings'] = attempts.filter(status='Unsuccessful').count()

        return context


class MailingDetailView(LoginRequiredMixin, DetailView):
    model = Mailing
    pk_url_kwarg = 'id'
    template_name = 'customers/mailing_detail.html'
    context_object_name = 'mailing'

    def get_object(self,  queryset=None):
        return super().get_object(queryset)

    def post(self, *args, **kwargs):
        mailing = self.get_object()

        # recipients = mailing.recipients.all()
        # emails = [recipient.email for recipient in recipients]

        self.send_notification_email(mailing)

        return redirect("customers:mailing_list")

    def send_notification_email(self, mailing):
        subject = mailing.letter.topic
        message = mailing.letter.content
        from_email = settings.EMAIL_HOST_USER
        # recipient_list = emails

        try:
            msg = MIMEText(message)
            msg['Subject'] = subject
            msg['From'] = from_email
            msg['To'] = ', '.join([recipient.email for recipient in mailing.recipients.all()])

            with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
                server.starttls()
                server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)

                server.sendmail(
                    settings.EMAIL_HOST_USER,
                    [recipient.email for recipient in mailing.recipients.all()],
                    msg.as_string()
                )

                Attempt.objects.create(
                    status='Successful',
                    server_response='250 OK',
                    mailing=mailing
                )

        except smtplib.SMTPResponseException as e:
            Attempt.objects.create(
                status='Unsuccessful',
                server_response=f"{e.smtp_code} {e.smtp_error}",
                mailing=mailing
            )

        # send_mail(subject, message, from_email, recipient_list)


class MailingView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'customers/mailing.html'
    success_url = reverse_lazy('customers:mailing_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class LetterView(LoginRequiredMixin, CreateView):
    model = Letter
    fields = ['topic', 'content']
    template_name = 'customers/letter.html'
    success_url = reverse_lazy('customers:mailing_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class RecipientView(LoginRequiredMixin, CreateView):
    model = Recipient
    fields = ['email', 'full_name', 'comment']
    template_name = 'customers/recipient.html'
    success_url = reverse_lazy('customers:mailing_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    model = Mailing
    pk_url_kwarg = 'id'
    form_class = MailingForm
    template_name = "customers/mailing_update.html"
    success_url = reverse_lazy('customers:mailing_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)

    def dispatch(self, request, *args, **kwargs):
        obj = self.model.objects.filter(pk=kwargs['id']).first()

        is_manager = request.user.groups.filter(name='Менеджеры').exists()

        if obj.owner == request.user or is_manager:
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect('customers:mailing_list')


class LetterUpdateView(LoginRequiredMixin, UpdateView):
    model = Letter
    pk_url_kwarg = 'id'
    form_class = LetterForm
    template_name = "customers/letter_update.html"
    success_url = reverse_lazy('customers:mailing_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)

    def dispatch(self, request, *args, **kwargs):
        obj = self.model.objects.filter(pk=kwargs['id']).first()

        is_manager = request.user.groups.filter(name='Менеджеры').exists()

        if obj.owner == request.user or is_manager:
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect('customers:mailing_list')


class RecipientUpdateView(LoginRequiredMixin, UpdateView):
    model = Recipient
    pk_url_kwarg = 'id'
    form_class = RecipientForm
    template_name = "customers/recipient_update.html"
    success_url = reverse_lazy('customers:mailing_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)

    def dispatch(self, request, *args, **kwargs):
        obj = self.model.objects.filter(pk=kwargs['id']).first()

        is_manager = request.user.groups.filter(name='Менеджеры').exists()

        if obj.owner != request.user and not is_manager:
            return redirect('customers:mailing_list')
        return super().dispatch(request, *args, **kwargs)


class LetterDeleteView(LoginRequiredMixin, DeleteView):
    model = Letter
    pk_url_kwarg = 'id'
    template_name = 'customers/delete_product.html'
    success_url = reverse_lazy('customers:letter_list')

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)

    def dispatch(self, request, *args, **kwargs):
        obj = self.model.objects.filter(pk=kwargs['id']).first()

        is_manager = request.user.groups.filter(name='Менеджеры').exists()

        if obj.owner != request.user and not is_manager:
            return redirect('customers:letter_list')
        return super().dispatch(request, *args, **kwargs)
