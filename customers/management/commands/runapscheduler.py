import sys
import time
import logging
from datetime import timedelta

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
    """Проверка новых рассылок каждые 2 минуты"""
    try:
        now = timezone.localtime()
        # Ищем только НОВЫЕ рассылки (статус Created)
        new_mailings = Mailing.objects.filter(
            first_mailing__lte=now,
            end_mailing__gte=now,
            status='Created'
        )

        logger.info(f"Найдено {new_mailings.count()} новых рассылок в {now}")

        scheduler = get_scheduler()

        for mailing in new_mailings:
            mailing.status = 'Launched'
            mailing.save()

            # Планируем первую отправку СРАЗУ
            scheduler.add_job(
                execute_mailing_cycle,
                'date',
                run_date=now,
                args=[mailing],
                id=f'initial_mailing_{mailing.id}',
                replace_existing=True
            )
            logger.info(f"Запланирована начальная отправка для рассылки {mailing.id}")

    except Exception as e:
        logger.error(f"Ошибка проверки новых рассылок: {e}", exc_info=True)


def execute_mailing_cycle(mailing):
    """Выполняет рассылку и планирует следующую через 24 часа"""
    try:
        now = timezone.localtime()

        # Проверяем, что рассылка еще активна
        mailing.refresh_from_db()
        if mailing.end_mailing < now or mailing.status != 'Launched':
            return

        # Отправляем рассылку
        send_mailing(mailing, now)
        logger.info(f"Отправлена рассылка {mailing.id} в {now}")

        # Планируем следующую через 24 часа
        next_run = now + timedelta(hours=24)
        if next_run < mailing.end_mailing:
            scheduler = get_scheduler()
            scheduler.add_job(
                execute_mailing_cycle,
                'date',
                run_date=next_run,
                args=[mailing],
                id=f'mailing_cycle_{mailing.id}_{next_run.timestamp()}',
                replace_existing=True
            )
            logger.info(f"Следующая отправка для {mailing.id} запланирована на {next_run}")
        else:
            mailing.status = 'Completed'
            mailing.save()
            logger.info(f"Рассылка {mailing.id} завершена")

    except Exception as e:
        logger.error(f"Ошибка в цикле рассылки {mailing.id}: {e}", exc_info=True)
        # Пытаемся запланировать повтор через 5 минут при ошибке
        retry_time = timezone.localtime() + timedelta(minutes=5)
        scheduler = get_scheduler()
        scheduler.add_job(
            execute_mailing_cycle,
            'date',
            run_date=retry_time,
            args=[mailing],
            id=f'retry_mailing_{mailing.id}_{retry_time.timestamp()}',
            replace_existing=True
        )


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
        if 'makemigrations' in sys.argv or 'migrate' in sys.argv:
            return

        # Проверка БД
        for i in range(5):
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                break
            except Exception:
                if i == 4:
                    self.stdout.write(self.style.ERROR("Database not available"))
                    return
                time.sleep(2)

        try:
            scheduler = get_scheduler()

            # Проверка новых рассылок каждые 2 минуты
            scheduler.add_job(
                scheduled_check_mailings,
                trigger=CronTrigger(minute="*/2"),
                id="check_new_mailings",
                max_instances=1,
                replace_existing=True,
            )

            # Очистка старых задач
            scheduler.add_job(
                delete_old_job_executions,
                trigger=CronTrigger(day_of_week="mon", hour="00", minute="00"),
                id="cleanup_jobs",
                max_instances=1,
                replace_existing=True,
            )

            # Запуск немедленной проверки при старте
            scheduler.add_job(
                scheduled_check_mailings,
                trigger='date',
                run_date=timezone.localtime() + timedelta(seconds=5),
                id="initial_check",
                max_instances=1
            )

            self.stdout.write(self.style.SUCCESS("Планировщик запущен! Проверка новых каждые 2 мин, отправка каждые 24 часа"))

            while True:
                time.sleep(1)

        except KeyboardInterrupt:
            scheduler.shutdown()
            self.stdout.write(self.style.SUCCESS("Планировщик остановлен"))
        except Exception as e:
            logger.error(f"Ошибка планировщика: {e}", exc_info=True)
            scheduler.shutdown()
            self.stdout.write(self.style.ERROR(f"Ошибка: {e}"))
