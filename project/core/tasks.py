from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.management import call_command

logger = get_task_logger(__name__)


@shared_task
def sample_task():
    """ This is a sample task which runs in a certain
    interval

    Returns:

    """
    call_command("daily_sync", )
