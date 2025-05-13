import sys
import time
import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler import util
from django.core.management.base import BaseCommand
from django.utils import timezone

from customers.models import Mailing
from customers.services import send_mailing

from django.db import connection


logger = logging.getLogger(__name__)


def scheduled_check_mailings():
    """Основная функция проверки рассылок"""

    try:
        now = timezone.localtime()
        mailings = Mailing.objects.filter(
            first_mailing__lte=now,
            end_mailing__gte=now,
            status='Created'
        )

        logger.info(f"Found {mailings.count()} mailings to process at {now}")

        for mailing in mailings:
            mailing.status = 'Launched'
            mailing.save()
            send_mailing(mailing)

            # Получаем активный scheduler
            scheduler = get_scheduler()
            if scheduler is not None:
                scheduler.add_job(
                    check_mailing_completion,
                    'date',
                    run_date=mailing.end_mailing,
                    args=[mailing.id],
                    id=f'mailing_complete_{mailing.id}',
                    replace_existing=True
                )

    except Exception as e:
        logger.error(f"Error in scheduled_check_mailings: {e}")


def check_mailing_completion(mailing_id):

    now = timezone.localtime()

    try:
        from customers.models import Mailing
        mailing = Mailing.objects.get(id=mailing_id)
        if mailing.status == 'Launched' and mailing.end_mailing >= now:
            mailing.status = 'Completed'
            mailing.save()
    except Exception as e:
        logger.error(f"Error completing mailing {mailing_id}: {e}")


@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    """Очистка старых задач"""
    try:
        DjangoJobExecution.objects.delete_old_job_executions(max_age)
    except Exception as e:
        logger.error(f"Error cleaning old jobs: {e}")


# Глобальная переменная для планировщика
_scheduler = None


def get_scheduler():
    """Получение экземпляра планировщика"""
    global _scheduler
    if _scheduler is None or not _scheduler.running:
        _scheduler = BackgroundScheduler()
        _scheduler.add_jobstore(DjangoJobStore(), "default")
        _scheduler.start()
    return _scheduler


class Command(BaseCommand):
    help = "Starts the APScheduler."

    def handle(self, *args, **options):

        # Пропускаем запуск при выполнении миграций
        if 'makemigrations' in sys.argv or 'migrate' in sys.argv:
            return
        ##########################################################

        max_retries = 5
        retry_delay = 2

        for i in range(max_retries):
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                break
            except Exception:
                if i == max_retries - 1:
                    self.stdout.write(self.style.ERROR("Database not available"))
                    return
                time.sleep(retry_delay)

        try:
            scheduler = get_scheduler()

            # Проверка рассылок каждые 24 часа
            scheduler.add_job(
                scheduled_check_mailings,
                trigger=CronTrigger(hour="*/12"),
                id="check_mailings",
                max_instances=1,
                replace_existing=True,
            )

            # Очистка старых задач раз в неделю
            scheduler.add_job(
                delete_old_job_executions,
                trigger=CronTrigger(day_of_week="mon", hour="00", minute="00"),
                id="delete_old_job_executions",
                max_instances=1,
                replace_existing=True,
            )

            self.stdout.write(self.style.SUCCESS("Scheduler started successfully!"))

            # Бесконечный цикл для поддержания работы планировщика
            while True:
                time.sleep(1)

        except KeyboardInterrupt:
            if scheduler.running:
                scheduler.shutdown()
            self.stdout.write(self.style.SUCCESS("Scheduler stopped gracefully"))
        except Exception as e:
            logger.error(f"Scheduler failed: {e}")
            if '_scheduler' in globals() and _scheduler.running:
                _scheduler.shutdown()
            self.stdout.write(self.style.ERROR(f"Scheduler error: {e}"))
