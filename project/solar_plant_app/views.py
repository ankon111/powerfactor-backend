from django.db import IntegrityError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Plant
from .serializers import PlantSerializer
from .tasks import sync_data


class PlantApiView(APIView):

    def get(self, request, *args, **kwargs):
        """ Fetch all plant data

        Args:
            request:
            *args:
            **kwargs:

        Returns:

        """
        plants = Plant.objects.all()
        serializer = PlantSerializer(plants, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """This method is responsible for creating plant
        data.

        Args:
            request:
            *args:
            **kwargs:

        Returns:

        """
        data = {
            'name': request.data.get('name')
        }

        serializer = PlantSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            sync_data.delay(serializer.data['id'])
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PlantDetailsView(APIView):

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

    def get(self, request, plant_id, *args, **kwargs):
        """ Fetch a specific plant data based on plant id

        Args:
            request:
            plant_id:
            *args:
            **kwargs:

        Returns:

        """
        plant_instance = self.get_object(plant_id)
        if not plant_instance:
            return Response(
                {"results": "Object with plant id does not exists"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = PlantSerializer(plant_instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, plant_id, *args, **kwargs):
        """ Updates the plant item with given plant_id if exists

        Args:
            request:
            plant_id:
            *args:
            **kwargs:

        Returns:

        """
        plant_instance = self.get_object(plant_id)
        if not plant_instance:
            return Response(
                {"results": "Object with plant id does not exists"},
                status=status.HTTP_400_BAD_REQUEST
            )
        data = {
            'name': request.data.get('name')
        }
        serializer = PlantSerializer(instance=plant_instance, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, plant_id, *args, **kwargs):
        """ Deletes the plant item with given plant_id if exists
        but if the data sync is going on then the system won't able to dlete
        until the sync finished and in that case the system sends a message
        for trying again later

        Args:
            request:
            plant_id:
            *args:
            **kwargs:

        Returns:

        """
        plant_instance = self.get_object(plant_id)
        if not plant_instance:
            return Response(
                {"results": "Object with plant id does not exists"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            plant_instance.delete()
        except IntegrityError as ex: # noqa
            return Response(
                {
                    "results": "Data sync is running. Please try again later!"
                },
                status=status.HTTP_200_OK
            )

        return Response(
            {"results": "Object deleted!"},
            status=status.HTTP_200_OK
        )
