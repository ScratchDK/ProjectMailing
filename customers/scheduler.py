from django.core.management import call_command
from threading import Thread


def start_scheduler():
    thread = Thread(target=call_command, args=('runapscheduler',), daemon=True)
    thread.start()
