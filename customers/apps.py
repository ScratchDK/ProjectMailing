import os
import logging
from django.apps import AppConfig

logger = logging.getLogger(__name__)


class CustomersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "customers"

    def ready(self):
        logger.info("App ready called, RUN_MAIN=%s", os.environ.get('RUN_MAIN'))
        if os.environ.get('RUN_MAIN') == 'true':
            from .scheduler import start_scheduler
            start_scheduler()
