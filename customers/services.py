from django.core.mail import send_mail
import config.settings as settings
import logging

logger = logging.getLogger(__name__)


def send_mailing(mailing, now):
    logger.info(f"Время [{now}]], начала отправки рассылки №{mailing.id} по {mailing.recipients.count()} получателям.")

    subject = mailing.letter.topic
    message = mailing.letter.content
    from_email = settings.EMAIL_HOST_USER

    for recipient in mailing.recipients.all():
        try:
            send_mail(
                subject,
                message,
                from_email,
                [recipient.email],
                fail_silently=False,
            )
            logger.info(f"Email sent to {recipient.email}")
        except Exception as e:
            logger.error(f"Failed to send email to {recipient.email}: {e}")
