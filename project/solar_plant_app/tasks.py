from celery import shared_task

from django.core.management import call_command


@shared_task
def sync_data(plant_id):
    kwargs = {
        'plant_id': plant_id
    }
    call_command("daily_sync", **kwargs)
