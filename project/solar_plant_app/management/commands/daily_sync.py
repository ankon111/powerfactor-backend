import os
import time
import requests
import json

from datetime import timedelta, datetime
from django.core.management import BaseCommand
from tenacity import retry, wait_fixed, stop_after_attempt

from solar_plant_app.models import Plant, Datapoint
from solar_plant_app.serializers import DataPointSerializer
from core.settings import MONITORING_SERVICE_API


class Command(BaseCommand):
    help = "Sync Database"

    def add_arguments(self, parser):
        parser.add_argument('--plant_id', type=int)

    def handle(self, *args, **options):
        """ This method is used for handling django commands. in our case
        this is Sync Database. Details of the database sync is given below:
        The database is synced (task is triggered) in one of two ways:
        1. Once a solar plant id is created
        2. In a daily interval (periodic task)
        In this process the logic is following:
        * If the sync is triggered by plant id creation then we will sync the data
        only for the specific plant that is just created. First we sync for immediate date,
        which is yesterdays data and then we sync the database for one or more years based on
        the `SYNC_EVERY_RUN` param. e.g if SYNC_EVERY_RUN is 2 then this will sync two years of data
        from the oldest date that exist for specific that plant id. How many years of previous data
        we will save in our backend that is also parameterized by `SYNC_UNTIL_YEAR`
        * For periodic task all the logics are same except this runs for all plants.

        Args:
            *args:
            **options:

        Returns:

        """
        plant_id = options.get('plant_id', None)

        if plant_id is None:
            plant_instance_list = Plant.objects.all()
        else:
            plant_instance_list = Plant.objects.filter(id=plant_id)

        # This will sync data only from yesterday which will execute daily
        yesterday = datetime.now() - timedelta(1)
        from_date = yesterday.date().isoformat()
        to_date = datetime.now().date().isoformat()

        for plant_instance in plant_instance_list:
            self.sync_database(from_date=from_date, to_date=to_date, plant_instance=plant_instance)

            # This will sync up to n years of data
            oldest_date = Datapoint.objects.order_by('timestamp').filter(
                plant_id=plant_instance.id).first().timestamp

            # We will keep the last 10 years of data and that also depends on our decision
            SYNC_UNTIL_YEAR = int(os.environ.get('SYNC_UNTIL_YEAR'))
            # In every run sync last 1 year data for a plant
            SYNC_EVERY_RUN = int(os.environ.get('SYNC_EVERY_RUN'))

            if oldest_date and datetime.now().year - SYNC_UNTIL_YEAR <= oldest_date.year:
                for year in range(oldest_date.year - SYNC_EVERY_RUN, oldest_date.year + 1):
                    from_date = datetime(year, 1, 1).date().isoformat()
                    # if the year is current year then we will sync from beginning of the year
                    # until the day before yesterday as we already sync the data of yesterday
                    if year >= datetime.now().year:
                        to_date = (datetime.now() - timedelta(days=2)).date().isoformat()
                    else:
                        to_date = datetime(year, 12, 31).date().isoformat()
                    # Year by year sync
                    self.sync_database(from_date=from_date, to_date=to_date, plant_instance=plant_instance)

    def sync_database(self, from_date, to_date, plant_instance):
        """Fetch data from external service and save the data into our existing
        backend service

        Args:
            from_date:
            to_date:
            plant_instance:

        Returns:

        """
        start_time = time.time()
        params = {
            'plant-id': plant_instance.id,
            'from': from_date,
            'to': to_date
        }
        data = None
        # Fetch data from monitoring service with retry mechanism
        # to ensure that data is available
        try:
            data = self.fetch_data_from_monitoring_service(params=params)
        except Exception as ex: # noqa
            self.stdout.write("Retry failed...")

        if data:
            data_point_list = DataPointSerializer.map_plant_data_points(plant=plant_instance,
                                                                        data_list=data)
            serializer = DataPointSerializer(data=data_point_list, many=True)
            if serializer.is_valid():
                serializer.create(validated_data=data_point_list)

        end_time = time.time() - start_time
        self.stdout.write(f"The Database synced successfully in from {from_date} to {to_date}")
        self.stdout.write(f"The Database synced in {end_time} seconds")

    @retry(wait=wait_fixed(2), stop=stop_after_attempt(7))
    def fetch_data_from_monitoring_service(self, params):
        """ This method call an external API, in our case it's monitoring
        api and fetch data. Retry mechanism is implemented as the monitoring
        service is not available all the time. Each failed request is retried in every 2s for
        seven times.

        Args:
            params:

        Returns:

        """
        data = requests.get(url=MONITORING_SERVICE_API, params=params)
        data = json.loads(data.text)
        if data and 'error' not in data:
            return data
        else:
            self.stdout.write("Retrying.....")
            raise IOError("Retrying! something breaks in monitoring service...")
