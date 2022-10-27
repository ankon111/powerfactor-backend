from datetime import datetime, timedelta

from django.db.models import F, Func, Value, CharField
from django.db.models import Sum
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Plant, Datapoint


class ReportView(APIView):

    def get_object(self, plant_id):
        """Helper method to get the object with given plant_id

        Args:
            plant_id:

        Returns:

        """
        try:
            return Plant.objects.get(id=plant_id)
        except Plant.DoesNotExist:
            return None

    def validation(self, plant_id, from_date, to_date):
        """ This is also an helper method which helps for doing validation.
        This function is seperated by considering that if there are more requests
        added and that may need similar validation.

        Args:
            plant_id:
            from_date:
            to_date:

        Returns:

        """
        if plant_id is None or from_date is None or to_date is None:
            raise Exception("Please provide plant_id, from and to values")

        plant_instance = self.get_object(plant_id)
        if not plant_instance:
            raise Exception("Object with plant id does not exists")

        try:
            datetime.strptime(from_date, '%Y-%m-%d')
            datetime.strptime(to_date, '%Y-%m-%d')
        except ValueError:
            raise Exception("Incorrect data format, should be YYYY-MM-DD")

        if datetime.fromisoformat(from_date) > datetime.fromisoformat(to_date):
            raise Exception("From date can not be greater than to date")

    def get(self, request, *args, **kwargs):
        """This function handles GET request with query params.
        Basically this method support for fetching data from backend service
        and serve the data as hourly sum of energy and irradiation date within
        the date range.

        Args:
            request:
            *args:
            **kwargs:

        Returns:

        """
        plant_id = request.GET.get('plant-id', None)
        from_date = request.GET.get('from', None)
        to_date = request.GET.get('to', None)

        try:
            self.validation(plant_id=plant_id, from_date=from_date, to_date=to_date)
        except Exception as ex:
            return Response(
                {
                    "results": str(ex)
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        plant_instance = self.get_object(plant_id)
        from_date = datetime.fromisoformat(from_date)
        to_date = datetime.fromisoformat(to_date)
        date_range = [(from_date + timedelta(days=x)).strftime(
            "%Y-%m-%d") for x in range((to_date - from_date).days)]

        query_set = Datapoint.objects.all().filter(
            plant=plant_instance.id, timestamp__date__in=date_range).values(
            'timestamp__date').annotate(timestamp=Func(F('timestamp__date'), Value('YYYY-MM-DD'),
                                                       function='to_char', output_field=CharField()),
                                        sum_energy_expected=Sum('energy_expected'),
                                        sum_energy_observed=Sum('energy_observed'),
                                        sum_irradiation_expected=Sum('irradiation_expected'),
                                        sum_irradiation_observed=Sum('irradiation_observed')).values(
            'timestamp', 'sum_energy_expected', 'sum_energy_observed', 'sum_irradiation_expected',
            'sum_irradiation_observed').order_by('timestamp')

        if query_set:
            data = list(query_set)
        else:
            data = "Data is not available!"

        return Response(
            {
                "data": data
            },
            status=status.HTTP_200_OK
        )
