import smtplib
from email.mime.text import MIMEText

from django.core.management.base import BaseCommand
from customers.models import Mailing, Attempt
import config.settings as settings


class Command(BaseCommand):
    help = 'Позволяет выбрать и отправить нужную рассылку через консоль'

    def handle(self, *args, **kwargs):
        mailings = Mailing.objects.all()
        for mailing in mailings:
            recipients = mailing.recipients.all()
            letter = mailing.letter.topic
            print(f"Рассылка №{mailing.pk}, тема письма {letter}, получатели {[recipient.full_name for recipient in recipients]}")

        answer_user = ""

        mailing_pk = [mailing.pk for mailing in mailings]

        while answer_user not in mailing_pk:
            answer_user = int(input("Введите номер рассылки которую хотите отправить: "))

        mailing_to_send = Mailing.objects.get(pk=answer_user)

        self.send_notification_email(mailing_to_send)

    def send_notification_email(self, mailing):
        subject = mailing.letter.topic
        message = mailing.letter.content
        from_email = settings.EMAIL_HOST_USER

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
