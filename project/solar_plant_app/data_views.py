from datetime import datetime

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Plant, Datapoint


class PlantDataPointsView(APIView):

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
        """ This function handles GET request with query params.
        Basically this method support for fetching data from backend service
        and serve the data as it is, without calculation.

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
        query_set = Datapoint.objects.filter(
            plant=plant_instance.id,
            timestamp__gte=datetime.fromisoformat(from_date),
            timestamp__lte=datetime.fromisoformat(to_date)
        ).values()

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
